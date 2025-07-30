#!/usr/bin/env python3
"""
Batch processing module for OSMnx-based isochrone generation.

This module implements true batch processing for multiple POIs using shared networks,
addressing the core efficiency improvement mentioned in the efficiency document.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import geopandas as gpd
import networkx as nx
import osmnx as ox
from shapely.geometry import Point
import pandas as pd
from geopy.distance import geodesic

from socialmapper.progress import get_progress_bar

logger = logging.getLogger(__name__)

class OSMnxBatchProcessor:
    """
    Batch processor for OSMnx-based isochrone generation.
    
    This addresses the core efficiency issue by processing multiple POIs
    against a single downloaded network, eliminating redundant network downloads.
    """
    
    def __init__(self, 
                 max_batch_size: int = 50,
                 network_buffer_km: float = 1.0,
                 cache_networks: bool = True):
        """
        Initialize the batch processor.
        
        Args:
            max_batch_size: Maximum number of POIs to process in one batch
            network_buffer_km: Buffer around POI cluster for network download
            cache_networks: Whether to cache downloaded networks
        """
        self.max_batch_size = max_batch_size
        self.network_buffer_km = network_buffer_km
        self.cache_networks = cache_networks
        self.network_cache = {}
        
    def create_poi_batches(self, pois: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Create batches of POIs for processing.
        
        Args:
            pois: List of POI dictionaries
            
        Returns:
            List of POI batches
        """
        batches = []
        for i in range(0, len(pois), self.max_batch_size):
            batch = pois[i:i + self.max_batch_size]
            batches.append(batch)
        
        logger.info(f"Created {len(batches)} batches from {len(pois)} POIs")
        return batches
    
    def calculate_batch_network_bounds(self, poi_batch: List[Dict[str, Any]], 
                                     travel_time_minutes: int) -> Tuple[float, float, float, float]:
        """
        Calculate the network bounds needed for a batch of POIs.
        
        Args:
            poi_batch: List of POIs in the batch
            travel_time_minutes: Travel time limit in minutes
            
        Returns:
            Tuple of (min_lat, min_lon, max_lat, max_lon)
        """
        lats = [poi['lat'] for poi in poi_batch]
        lons = [poi['lon'] for poi in poi_batch]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Use much smaller buffer - just enough for the travel time
        # Assume average speed of 30 km/h in urban areas
        buffer_km = min(self.network_buffer_km, travel_time_minutes * 0.5)  # Reduced from 0.8
        buffer_degrees = buffer_km / 111.0  # Rough conversion km to degrees
        
        return (
            min_lat - buffer_degrees,
            min_lon - buffer_degrees, 
            max_lat + buffer_degrees,
            max_lon + buffer_degrees
        )
    
    def download_batch_network(self, poi_batch: List[Dict[str, Any]], 
                             travel_time_minutes: int) -> nx.MultiDiGraph:
        """
        Download a single network that covers all POIs in the batch.
        
        Args:
            poi_batch: List of POIs in the batch
            travel_time_minutes: Travel time limit in minutes
            
        Returns:
            OSMnx network graph
        """
        # Calculate network bounds
        min_lat, min_lon, max_lat, max_lon = self.calculate_batch_network_bounds(
            poi_batch, travel_time_minutes
        )
        
        # Create cache key
        cache_key = f"{min_lat:.4f}_{min_lon:.4f}_{max_lat:.4f}_{max_lon:.4f}"
        
        # Check cache
        if self.cache_networks and cache_key in self.network_cache:
            logger.info(f"Using cached network for batch of {len(poi_batch)} POIs")
            return self.network_cache[cache_key]
        
        # Download network using bounding box
        logger.info(f"Downloading network for batch of {len(poi_batch)} POIs "
                   f"(bounds: {min_lat:.4f}, {min_lon:.4f}, {max_lat:.4f}, {max_lon:.4f})")
        
        try:
            # Download network by bounding box
            network = ox.graph_from_bbox(
                bbox=(min_lon, min_lat, max_lon, max_lat),
                network_type='drive',
                simplify=True
            )
            
            # Add speeds and travel times
            network = ox.add_edge_speeds(network, fallback=50)
            network = ox.add_edge_travel_times(network)
            
            # Project to local coordinate system
            network = ox.project_graph(network)
            
            # Cache if enabled
            if self.cache_networks:
                self.network_cache[cache_key] = network
            
            return network
            
        except Exception as e:
            logger.error(f"Failed to download network for batch: {e}")
            raise
    
    def process_poi_batch_against_network(self, 
                                        poi_batch: List[Dict[str, Any]],
                                        network: nx.MultiDiGraph,
                                        travel_time_minutes: int) -> List[gpd.GeoDataFrame]:
        """
        Process a batch of POIs against a single network.
        
        Args:
            poi_batch: List of POIs to process
            network: OSMnx network graph
            travel_time_minutes: Travel time limit in minutes
            
        Returns:
            List of isochrone GeoDataFrames
        """
        results = []
        
        for poi in get_progress_bar(poi_batch, desc="Processing POIs", unit="POI", leave=False):
            try:
                isochrone_gdf = self.create_isochrone_from_network(
                    poi, network, travel_time_minutes
                )
                results.append(isochrone_gdf)
                
            except Exception as e:
                poi_name = poi.get('tags', {}).get('name', poi.get('id', 'unknown'))
                logger.warning(f"Error processing POI {poi_name}: {e}")
                continue
        
        return results
    
    def create_isochrone_from_network(self,
                                    poi: Dict[str, Any],
                                    network: nx.MultiDiGraph,
                                    travel_time_minutes: int) -> gpd.GeoDataFrame:
        """
        Create isochrone for a single POI using the provided network.
        
        Args:
            poi: POI dictionary
            network: OSMnx network graph
            travel_time_minutes: Travel time limit in minutes
            
        Returns:
            GeoDataFrame with isochrone
        """
        latitude = poi['lat']
        longitude = poi['lon']
        poi_name = poi.get('tags', {}).get('name', f"poi_{poi.get('id', 'unknown')}")
        
        # Create point from coordinates
        poi_point = Point(longitude, latitude)
        poi_geom = gpd.GeoSeries([poi_point], crs='EPSG:4326').to_crs(network.graph['crs'])
        poi_proj = poi_geom.geometry.iloc[0]
        
        # Find nearest node
        poi_node = ox.nearest_nodes(network, X=poi_proj.x, Y=poi_proj.y)
        
        # Generate subgraph based on travel time
        subgraph = nx.ego_graph(
            network,
            poi_node,
            radius=travel_time_minutes * 60,  # Convert minutes to seconds
            distance='travel_time'
        )
        
        # Create isochrone from reachable nodes
        node_points = [Point((data['x'], data['y'])) for node, data in subgraph.nodes(data=True)]
        nodes_gdf = gpd.GeoDataFrame(geometry=node_points, crs=network.graph['crs'])
        
        # Use convex hull to create the isochrone polygon
        isochrone = nodes_gdf.unary_union.convex_hull
        
        # Create GeoDataFrame with the isochrone
        isochrone_gdf = gpd.GeoDataFrame(geometry=[isochrone], crs=network.graph['crs'])
        
        # Convert to WGS84 for standard output
        isochrone_gdf = isochrone_gdf.to_crs('EPSG:4326')
        
        # Add metadata
        isochrone_gdf['poi_id'] = poi.get('id', 'unknown')
        isochrone_gdf['poi_name'] = poi_name
        isochrone_gdf['travel_time_minutes'] = travel_time_minutes
        
        return isochrone_gdf
    
    def process_pois_in_batches(self,
                              poi_data: Dict[str, List[Dict[str, Any]]],
                              travel_time_minutes: int) -> List[gpd.GeoDataFrame]:
        """
        Process POIs using true batch processing.
        
        This is the main method that implements the efficiency improvement
        by downloading fewer networks and processing multiple POIs per network.
        
        Args:
            poi_data: Dictionary with 'pois' key containing list of POIs
            travel_time_minutes: Travel time limit in minutes
            
        Returns:
            List of isochrone GeoDataFrames
        """
        pois = poi_data.get('pois', [])
        if not pois:
            raise ValueError("No POIs found in input data")
        
        logger.info(f"Starting batch processing for {len(pois)} POIs")
        start_time = time.time()
        
        # Create batches
        poi_batches = self.create_poi_batches(pois)
        
        all_results = []
        networks_downloaded = 0
        
        for batch_idx, poi_batch in enumerate(poi_batches):
            logger.info(f"Processing batch {batch_idx + 1}/{len(poi_batches)} "
                       f"({len(poi_batch)} POIs)")
            
            # Download single network for entire batch
            try:
                network = self.download_batch_network(poi_batch, travel_time_minutes)
                networks_downloaded += 1
                
                # Process all POIs in batch against this network
                batch_results = self.process_poi_batch_against_network(
                    poi_batch, network, travel_time_minutes
                )
                
                all_results.extend(batch_results)
                
                logger.info(f"Completed batch {batch_idx + 1}/{len(poi_batches)} "
                           f"({len(all_results)}/{len(pois)} total POIs)")
                
            except Exception as e:
                logger.error(f"Failed to process batch {batch_idx + 1}: {e}")
                continue
        
        total_time = time.time() - start_time
        
        # Calculate efficiency metrics
        traditional_networks = len(pois)  # One network per POI traditionally
        actual_networks = networks_downloaded
        network_reduction = (traditional_networks - actual_networks) / traditional_networks * 100
        
        logger.info(f"Batch processing completed in {total_time:.2f}s")
        logger.info(f"Network efficiency: {actual_networks} networks vs {traditional_networks} traditional "
                   f"({network_reduction:.1f}% reduction)")
        logger.info(f"Successfully processed {len(all_results)}/{len(pois)} POIs")
        
        return all_results
    
    def get_efficiency_stats(self) -> Dict[str, Any]:
        """Get efficiency statistics."""
        return {
            'max_batch_size': self.max_batch_size,
            'network_buffer_km': self.network_buffer_km,
            'cached_networks': len(self.network_cache) if self.cache_networks else 0,
            'cache_enabled': self.cache_networks
        }

def create_isochrones_batch_osmnx(poi_data: Dict[str, List[Dict[str, Any]]],
                                travel_time_limit: int,
                                max_batch_size: int = 50,
                                **kwargs) -> List[gpd.GeoDataFrame]:
    """
    Convenience function for batch OSMnx isochrone generation.
    
    Args:
        poi_data: Dictionary with 'pois' key containing list of POIs
        travel_time_limit: Travel time limit in minutes
        max_batch_size: Maximum POIs per batch
        **kwargs: Additional arguments passed to processor
        
    Returns:
        List of isochrone GeoDataFrames
    """
    processor = OSMnxBatchProcessor(max_batch_size=max_batch_size, **kwargs)
    return processor.process_pois_in_batches(poi_data, travel_time_limit) 