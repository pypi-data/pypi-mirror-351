#!/usr/bin/env python3
"""
File-based census module for SocialMapper - DuckDB replacement.

This module provides the same functionality as the DuckDB-based census module
but uses efficient file formats instead of a database:
- GeoParquet for spatial data
- Parquet for census data  
- JSON for metadata and lookup tables
- No database locking issues
- Better cross-platform compatibility
"""

import os
import json
import logging
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
import warnings
from datetime import datetime, timedelta

import pandas as pd
import geopandas as gpd
import requests
from shapely.geometry import Point, Polygon, MultiPolygon

# Import existing utilities
from socialmapper.progress import get_progress_bar
from socialmapper.util import (
    normalize_census_variable,
    get_census_api_key,
    get_readable_census_variables,
    CENSUS_VARIABLE_MAPPING,
    rate_limiter
)
from socialmapper.states import (
    normalize_state,
    normalize_state_list,
    StateFormat,
    state_fips_to_name
)

# Try to import geopy for distance calculations
try:
    from geopy.distance import geodesic
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    logger.warning("geopy not available, distance calculations will be approximate")

# Configure logging
logger = logging.getLogger(__name__)

# Default cache directory
DEFAULT_CACHE_DIR = Path.home() / ".socialmapper" / "cache"

class FileCensusManager:
    """
    File-based census data management system.
    
    This class provides the same interface as CensusDatabase but uses
    efficient file formats instead of DuckDB:
    - GeoParquet for boundaries
    - Parquet for census data
    - JSON for metadata
    """
    
    def __init__(self, cache_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the file-based census manager.
        
        Args:
            cache_dir: Directory for cache files. If None, uses default location.
        """
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.boundaries_dir = self.cache_dir / "boundaries"
        self.census_data_dir = self.cache_dir / "census_data"
        self.metadata_dir = self.cache_dir / "metadata"
        self.neighbors_dir = self.cache_dir / "neighbors"
        
        for dir_path in [self.boundaries_dir, self.census_data_dir, self.metadata_dir, self.neighbors_dir]:
            dir_path.mkdir(exist_ok=True)
        
        logger.info(f"Initialized file-based census manager at {self.cache_dir}")
    
    def get_or_stream_block_groups(self, 
                                   state_fips: Union[str, List[str]], 
                                   force_refresh: bool = False,
                                   api_key: Optional[str] = None) -> gpd.GeoDataFrame:
        """
        Get block groups for states, using cache or streaming from Census API.
        
        Args:
            state_fips: State FIPS code(s)
            force_refresh: Whether to refresh cached data
            api_key: Census API key
            
        Returns:
            GeoDataFrame with block group boundaries
        """
        if isinstance(state_fips, str):
            state_fips = [state_fips]
        
        all_block_groups = []
        
        for state in state_fips:
            # Check cache first
            cache_file = self.boundaries_dir / f"block_groups_{state}.parquet"
            metadata_file = self.metadata_dir / f"block_groups_{state}_metadata.json"
            
            # Try to use cache if not forcing refresh
            if not force_refresh and cache_file.exists():
                # Check if we have valid metadata
                cache_valid = self._is_cache_valid(metadata_file) if metadata_file.exists() else True
                
                if cache_valid:
                    logger.info(f"Loading cached block groups for state {state}")
                    try:
                        gdf = gpd.read_parquet(cache_file)
                        if not gdf.empty:
                            all_block_groups.append(gdf)
                            continue
                    except Exception as e:
                        logger.warning(f"Error loading cached data for state {state}: {e}")
            
            # Fetch from API if cache not available or invalid
            logger.info(f"Fetching block groups for state {state} from Census API")
            gdf = self._fetch_block_groups_from_api(state, api_key)
            
            if not gdf.empty:
                # Cache the data
                self._cache_block_groups(gdf, state)
                all_block_groups.append(gdf)
        
        if not all_block_groups:
            return gpd.GeoDataFrame()
        
        # Combine all states
        combined_gdf = gpd.GeoDataFrame(pd.concat(all_block_groups, ignore_index=True))
        return combined_gdf
    
    def _fetch_block_groups_from_api(self, state_fips: str, api_key: Optional[str] = None) -> gpd.GeoDataFrame:
        """Fetch block groups from Census API with multiple fallback sources."""
        
        # Try cartographic boundary files first (preferred)
        try:
            return self._fetch_from_cartographic_boundaries(state_fips)
        except Exception as e:
            logger.warning(f"Cartographic boundaries failed for state {state_fips}: {e}")
        
        # Try TIGER/Web API with GeoJSON
        try:
            return self._fetch_from_tiger_geojson(state_fips)
        except Exception as e:
            logger.warning(f"TIGER GeoJSON failed for state {state_fips}: {e}")
        
        # Try TIGER/Web API with ESRI JSON (last resort)
        try:
            return self._fetch_from_tiger_esri_json(state_fips)
        except Exception as e:
            logger.error(f"All data sources failed for state {state_fips}: {e}")
            return gpd.GeoDataFrame()
    
    def _fetch_from_cartographic_boundaries(self, state_fips: str) -> gpd.GeoDataFrame:
        """Fetch from Census cartographic boundary files."""
        year = 2021  # Use most recent available
        url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{state_fips}_bg_500k.zip"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_file = temp_path / f"bg_{state_fips}.zip"
            
            # Download with rate limiting
            rate_limiter.wait_if_needed("census")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(zip_file, 'wb') as f:
                f.write(response.content)
            
            # Extract and read
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
            
            # Find the shapefile
            shp_files = list(temp_path.glob("*.shp"))
            if not shp_files:
                raise ValueError("No shapefile found in downloaded archive")
            
            gdf = gpd.read_file(shp_files[0])
            
            # Ensure consistent CRS
            if gdf.crs != 'EPSG:4326':
                gdf = gdf.to_crs('EPSG:4326')
            
            return gdf
    
    def _fetch_from_tiger_geojson(self, state_fips: str) -> gpd.GeoDataFrame:
        """Fetch from TIGER/Web API using GeoJSON format."""
        url = f"https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2021/MapServer/10/query"
        
        params = {
            'where': f"STATE='{state_fips}'",
            'outFields': '*',
            'f': 'geojson',
            'returnGeometry': 'true'
        }
        
        rate_limiter.wait_if_needed("census")
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        
        # Parse GeoJSON
        geojson_data = response.json()
        gdf = gpd.GeoDataFrame.from_features(geojson_data['features'], crs='EPSG:4326')
        
        return gdf
    
    def _fetch_from_tiger_esri_json(self, state_fips: str) -> gpd.GeoDataFrame:
        """Fetch from TIGER/Web API using ESRI JSON format."""
        url = f"https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2021/MapServer/10/query"
        
        params = {
            'where': f"STATE='{state_fips}'",
            'outFields': '*',
            'f': 'json',
            'returnGeometry': 'true'
        }
        
        rate_limiter.wait_if_needed("census")
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        
        esri_data = response.json()
        return self._convert_esri_json_to_geodataframe(esri_data)
    
    def _convert_esri_json_to_geodataframe(self, esri_data: dict) -> gpd.GeoDataFrame:
        """Convert ESRI JSON response to GeoDataFrame."""
        if 'features' not in esri_data or not esri_data['features']:
            return gpd.GeoDataFrame()
        
        features = []
        for feature in esri_data['features']:
            # Extract attributes
            attributes = feature.get('attributes', {})
            
            # Extract geometry
            geom_data = feature.get('geometry', {})
            if 'rings' in geom_data:
                # Polygon geometry
                from shapely.geometry import Polygon
                try:
                    # ESRI JSON uses rings for polygons
                    rings = geom_data['rings']
                    if rings:
                        # First ring is exterior, others are holes
                        exterior = rings[0]
                        holes = rings[1:] if len(rings) > 1 else None
                        geom = Polygon(exterior, holes)
                    else:
                        continue
                except Exception as e:
                    logger.warning(f"Error creating polygon geometry: {e}")
                    continue
            else:
                logger.warning("Unsupported geometry type in ESRI JSON")
                continue
            
            # Create feature dict
            feature_dict = attributes.copy()
            feature_dict['geometry'] = geom
            features.append(feature_dict)
        
        if not features:
            return gpd.GeoDataFrame()
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(features, crs='EPSG:4326')
        
        # Standardize column names
        column_mapping = {
            'STATE': 'STATEFP',
            'COUNTY': 'COUNTYFP', 
            'TRACT': 'TRACTCE',
            'BLKGRP': 'BLKGRPCE'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in gdf.columns and new_col not in gdf.columns:
                gdf[new_col] = gdf[old_col]
        
        # Ensure GEOID is properly formatted
        if 'GEOID' not in gdf.columns:
            if all(col in gdf.columns for col in ['STATEFP', 'COUNTYFP', 'TRACTCE', 'BLKGRPCE']):
                gdf['GEOID'] = (
                    gdf['STATEFP'].astype(str).str.zfill(2) +
                    gdf['COUNTYFP'].astype(str).str.zfill(3) +
                    gdf['TRACTCE'].astype(str).str.zfill(6) +
                    gdf['BLKGRPCE'].astype(str)
                )
        
        return gdf
    
    def _cache_block_groups(self, gdf: gpd.GeoDataFrame, state_fips: str):
        """Cache block groups data to file."""
        try:
            # Save the GeoDataFrame
            cache_file = self.boundaries_dir / f"block_groups_{state_fips}.parquet"
            gdf.to_parquet(cache_file)
            
            # Save metadata
            metadata = {
                'cached_at': datetime.now().isoformat(),
                'record_count': len(gdf),
                'state_fips': state_fips,
                'source': 'census_api'
            }
            metadata_file = self.metadata_dir / f"block_groups_{state_fips}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f)
            
            logger.info(f"Cached {len(gdf)} block groups for state {state_fips}")
            
        except Exception as e:
            logger.error(f"Error caching block groups for state {state_fips}: {e}")
    
    def _is_cache_valid(self, metadata_file: Path, max_age_days: int = 30) -> bool:
        """Check if cache metadata indicates valid cache."""
        try:
            if not metadata_file.exists():
                return False
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            if 'cached_at' not in metadata:
                return False
            
            cached_at = datetime.fromisoformat(metadata['cached_at'])
            age = datetime.now() - cached_at
            
            return age.days < max_age_days
            
        except Exception as e:
            logger.warning(f"Error checking cache validity: {e}")
            return False
    
    def find_intersecting_block_groups(self, 
                                       geometry: Union[gpd.GeoDataFrame, gpd.GeoSeries],
                                       state_fips: Optional[List[str]] = None,
                                       selection_mode: str = "intersect") -> gpd.GeoDataFrame:
        """
        Find block groups that intersect with given geometry.
        
        Args:
            geometry: Geometry to intersect with (isochrones, etc.)
            state_fips: States to search in (if None, inferred from geometry bounds)
            selection_mode: 'intersect', 'contain', or 'clip'
            
        Returns:
            GeoDataFrame with intersecting block groups including distance calculations
        """
        if isinstance(geometry, gpd.GeoDataFrame):
            geom_gdf = geometry
        else:
            geom_gdf = gpd.GeoDataFrame(geometry=geometry)
        
        # Ensure consistent CRS
        if geom_gdf.crs != 'EPSG:4326':
            geom_gdf = geom_gdf.to_crs('EPSG:4326')
        
        # Determine states to search if not provided
        if state_fips is None:
            state_fips = self._infer_states_from_geometry(geom_gdf)
        
        # Get block groups for relevant states
        block_groups_gdf = self.get_or_stream_block_groups(state_fips)
        
        if block_groups_gdf.empty:
            return gpd.GeoDataFrame()
        
        # Ensure consistent CRS for block groups
        if block_groups_gdf.crs != 'EPSG:4326':
            block_groups_gdf = block_groups_gdf.to_crs('EPSG:4326')
        
        # Perform spatial intersection
        intersecting_blocks = []
        
        for idx, geom_row in geom_gdf.iterrows():
            geom = geom_row.geometry
            
            # Find intersecting block groups
            if selection_mode == "intersect":
                mask = block_groups_gdf.intersects(geom)
            elif selection_mode == "contain":
                mask = block_groups_gdf.within(geom)
            elif selection_mode == "clip":
                mask = block_groups_gdf.intersects(geom)
            else:
                raise ValueError(f"Unknown selection_mode: {selection_mode}")
            
            intersecting = block_groups_gdf[mask].copy()
            
            if not intersecting.empty:
                # Add metadata from the geometry (e.g., POI info)
                for col in geom_gdf.columns:
                    if col != 'geometry':
                        intersecting[col] = geom_row[col]
                
                # Calculate distance from geometry centroid to block group centroids
                geom_centroid = geom.centroid
                block_centroids = intersecting.geometry.centroid
                
                # Calculate distances in kilometers using geodesic distance
                distances_km = []
                for centroid in block_centroids:
                    try:
                        if GEOPY_AVAILABLE:
                            dist = geodesic(
                                (geom_centroid.y, geom_centroid.x),
                                (centroid.y, centroid.x)
                            ).kilometers
                        else:
                            # Fallback to simple Euclidean distance (approximate)
                            import math
                            lat1, lon1 = geom_centroid.y, geom_centroid.x
                            lat2, lon2 = centroid.y, centroid.x
                            
                            # Convert to radians
                            lat1_rad = math.radians(lat1)
                            lon1_rad = math.radians(lon1)
                            lat2_rad = math.radians(lat2)
                            lon2_rad = math.radians(lon2)
                            
                            # Haversine formula for approximate distance
                            dlat = lat2_rad - lat1_rad
                            dlon = lon2_rad - lon1_rad
                            a = (math.sin(dlat/2)**2 + 
                                 math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
                            c = 2 * math.asin(math.sqrt(a))
                            dist = 6371 * c  # Earth radius in km
                        
                        distances_km.append(dist)
                    except Exception as e:
                        logger.warning(f"Error calculating distance: {e}")
                        distances_km.append(0.0)
                
                intersecting['distance_km'] = distances_km
                intersecting_blocks.append(intersecting)
        
        if not intersecting_blocks:
            return gpd.GeoDataFrame()
        
        # Combine all intersecting block groups
        result = gpd.GeoDataFrame(pd.concat(intersecting_blocks, ignore_index=True))
        
        return result
    
    def _infer_states_from_geometry(self, geom_gdf: gpd.GeoDataFrame) -> List[str]:
        """Infer state FIPS codes from geometry bounds."""
        # Get bounding box
        bounds = geom_gdf.total_bounds
        min_lon, min_lat, max_lon, max_lat = bounds
        
        # Use a simple lookup or API call to determine states
        # For now, use a basic approach - in production, you might want a more sophisticated method
        from socialmapper.neighbors_file_based import get_geography_from_point
        
        try:
            # Sample a few points to determine states
            center_lat = (min_lat + max_lat) / 2
            center_lon = (min_lon + max_lon) / 2
            
            geo_info = get_geography_from_point(center_lat, center_lon)
            if geo_info and 'state_fips' in geo_info:
                return [geo_info['state_fips']]
        except Exception as e:
            logger.warning(f"Error inferring states from geometry: {e}")
        
        # Fallback: return common states (this is not ideal but prevents errors)
        logger.warning("Could not infer states from geometry, using fallback approach")
        return ['06', '36', '48']  # CA, NY, TX as fallback
    
    def get_census_data(self, 
                        geoids: List[str], 
                        variables: List[str],
                        year: int = 2021,
                        dataset: str = 'acs5') -> pd.DataFrame:
        """
        Get census data for block groups.
        
        Args:
            geoids: List of block group GEOIDs
            variables: List of census variable codes
            year: Census year
            dataset: Census dataset
            
        Returns:
            DataFrame with census data
        """
        # Check cache first
        cache_key = f"{year}_{dataset}_{hash(tuple(sorted(variables)))}"
        cache_file = self.census_data_dir / f"census_data_{cache_key}.parquet"
        
        if cache_file.exists():
            try:
                cached_df = pd.read_parquet(cache_file)
                # Filter to requested GEOIDs
                available_data = cached_df[cached_df['GEOID'].isin(geoids)]
                if len(available_data) == len(geoids):
                    logger.info(f"Using cached census data for {len(geoids)} GEOIDs")
                    return available_data
            except Exception as e:
                logger.warning(f"Error loading cached census data: {e}")
        
        # Fetch from API
        logger.info(f"Fetching census data for {len(geoids)} GEOIDs from Census API")
        data = self._fetch_census_data_from_api(geoids, variables, year, dataset)
        
        # Cache the data
        if not data.empty:
            self._cache_census_data(data, cache_key)
        
        return data
    
    def _fetch_census_data_from_api(self, 
                                    geoids: List[str], 
                                    variables: List[str],
                                    year: int = 2021,
                                    dataset: str = 'acs5') -> pd.DataFrame:
        """Fetch census data from Census API."""
        # This is a simplified version - you'd want to implement the full
        # census data fetching logic from the existing census module
        
        # Normalize variables
        normalized_vars = [normalize_census_variable(var) for var in variables]
        
        # Group by state for API efficiency
        state_groups = {}
        for geoid in geoids:
            state_fips = geoid[:2]
            if state_fips not in state_groups:
                state_groups[state_fips] = []
            state_groups[state_fips].append(geoid)
        
        all_data = []
        
        for state_fips, state_geoids in state_groups.items():
            try:
                # Fetch data for this state
                state_data = self._fetch_state_census_data(state_fips, normalized_vars, year, dataset)
                
                # Filter to requested GEOIDs
                state_data = state_data[state_data['GEOID'].isin(state_geoids)]
                all_data.append(state_data)
                
            except Exception as e:
                logger.error(f"Error fetching census data for state {state_fips}: {e}")
        
        if not all_data:
            return pd.DataFrame()
        
        return pd.concat(all_data, ignore_index=True)
    
    def _fetch_state_census_data(self, 
                                 state_fips: str, 
                                 variables: List[str],
                                 year: int,
                                 dataset: str) -> pd.DataFrame:
        """Fetch census data for a single state."""
        api_key = get_census_api_key()
        if not api_key:
            logger.warning("No Census API key found, returning empty data")
            return pd.DataFrame()
        
        # Ensure NAME is included for better data quality
        api_variables = variables.copy()
        if 'NAME' not in api_variables:
            api_variables.append('NAME')
        
        base_url = f'https://api.census.gov/data/{year}/{dataset}'
        
        params = {
            'get': ','.join(api_variables),
            'for': 'block group:*',
            'in': f'state:{state_fips} county:* tract:*',
            'key': api_key
        }
        
        try:
            rate_limiter.wait_if_needed("census")
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if not data or len(data) < 2:
                logger.warning(f"No data returned for state {state_fips}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data[1:], columns=data[0])
            
            # Create GEOID
            df['GEOID'] = (
                df['state'].str.zfill(2) + 
                df['county'].str.zfill(3) + 
                df['tract'].str.zfill(6) + 
                df['block group']
            )
            
            logger.info(f"Fetched census data for {len(df)} block groups in state {state_fips}")
            return df
            
        except Exception as e:
            logger.error(f"API request failed for state {state_fips}: {e}")
            return pd.DataFrame()
    
    def _cache_census_data(self, data: pd.DataFrame, cache_key: str):
        """Cache census data to file."""
        try:
            cache_file = self.census_data_dir / f"census_data_{cache_key}.parquet"
            data.to_parquet(cache_file)
            logger.info(f"Cached census data with key {cache_key}")
        except Exception as e:
            logger.error(f"Error caching census data: {e}")


# Backward compatibility functions
def get_file_census_manager(cache_dir: Optional[Union[str, Path]] = None) -> FileCensusManager:
    """Get the global file-based census manager instance."""
    global _file_census_manager
    
    if '_file_census_manager' not in globals() or _file_census_manager is None:
        _file_census_manager = FileCensusManager(cache_dir)
    
    return _file_census_manager

def get_census_block_groups(state_fips: Union[str, List[str]], 
                           api_key: Optional[str] = None, 
                           force_refresh: bool = False) -> gpd.GeoDataFrame:
    """
    Get census block groups for states (file-based version).
    
    Args:
        state_fips: State FIPS code(s)
        api_key: Census API key (optional)
        force_refresh: Whether to refresh cached data
        
    Returns:
        GeoDataFrame with block group boundaries
    """
    manager = get_file_census_manager()
    return manager.get_or_stream_block_groups(state_fips, force_refresh, api_key)

def isochrone_to_block_groups(isochrone_gdf: gpd.GeoDataFrame,
                             state_fips: Optional[List[str]] = None,
                             selection_mode: str = "intersect") -> gpd.GeoDataFrame:
    """
    Find block groups that intersect with isochrones (file-based version).
    
    Args:
        isochrone_gdf: GeoDataFrame with isochrone geometries
        state_fips: States to search in
        selection_mode: 'intersect', 'contain', or 'clip'
        
    Returns:
        GeoDataFrame with intersecting block groups
    """
    manager = get_file_census_manager()
    return manager.find_intersecting_block_groups(isochrone_gdf, state_fips, selection_mode)

# Global instance
_file_census_manager = None 