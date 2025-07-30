#!/usr/bin/env python3
"""
Spatial optimization module for efficient isochrone generation.

This module provides spatial clustering and network sharing optimizations
specifically designed for OSMnx-based isochrone generation.
"""

import os
import pickle
import logging
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import geopandas as gpd
import networkx as nx
import osmnx as ox
from shapely.geometry import Point
from sklearn.cluster import DBSCAN
from geopy.distance import geodesic
import time
from pathlib import Path

from socialmapper.progress import get_progress_bar

logger = logging.getLogger(__name__)

class SpatialIsochroneOptimizer:
    """
    Optimizes isochrone generation through spatial clustering and network sharing.
    """
    
    def __init__(self, 
                 cache_dir: str = "cache/spatial_optimizer",
                 cluster_radius_km: float = 2.0,
                 network_reuse_distance_km: float = 1.0):
        """
        Initialize the spatial optimizer.
        
        Args:
            cache_dir: Directory for caching optimization data
            cluster_radius_km: Maximum distance between POIs in same cluster (km)
            network_reuse_distance_km: Maximum distance for network reuse (km)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cluster_radius_km = cluster_radius_km
        self.network_reuse_distance_km = network_reuse_distance_km
        
        # Network sharing cache
        self.shared_networks = {}
        self.network_centers = []
        
    def create_spatial_clusters(self, pois: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """
        Create spatial clusters of POIs using DBSCAN.
        
        Args:
            pois: List of POI dictionaries with 'lat' and 'lon'
            
        Returns:
            Dictionary mapping cluster_id to list of POIs
        """
        if len(pois) <= 1:
            return {0: pois}
        
        # Extract coordinates
        coords = np.array([[poi['lat'], poi['lon']] for poi in pois])
        
        # Convert cluster radius to approximate degrees
        eps_degrees = self.cluster_radius_km / 111.0  # Rough conversion
        
        # Perform clustering
        clustering = DBSCAN(eps=eps_degrees, min_samples=1).fit(coords)
        
        # Group POIs by cluster
        clusters = {}
        for i, cluster_id in enumerate(clustering.labels_):
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(pois[i])
        
        logger.info(f"Created {len(clusters)} spatial clusters from {len(pois)} POIs")
        return clusters
    
    def find_reusable_network(self, lat: float, lon: float, travel_time_limit: int) -> Optional[Tuple[nx.MultiDiGraph, Point]]:
        """
        Find an existing network that can be reused for this location.
        
        Args:
            lat: Latitude of new POI
            lon: Longitude of new POI
            travel_time_limit: Travel time limit in minutes
            
        Returns:
            Tuple of (network, center_point) if reusable network found, None otherwise
        """
        poi_point = Point(lon, lat)
        
        for network_id, (network, center_point, time_limit) in self.shared_networks.items():
            # Check if travel time limits are compatible
            if time_limit < travel_time_limit:
                continue
                
            # Calculate distance to network center
            center_lat, center_lon = center_point.y, center_point.x
            distance_km = geodesic((lat, lon), (center_lat, center_lon)).kilometers
            
            if distance_km <= self.network_reuse_distance_km:
                logger.info(f"Reusing network {network_id} (distance: {distance_km:.2f}km)")
                return network, center_point
        
        return None
    
    def get_or_create_shared_network(self, 
                                   cluster_pois: List[Dict[str, Any]], 
                                   travel_time_limit: int) -> Tuple[nx.MultiDiGraph, Point]:
        """
        Get or create a shared network for a cluster of POIs.
        
        Args:
            cluster_pois: List of POIs in the cluster
            travel_time_limit: Travel time limit in minutes
            
        Returns:
            Tuple of (network, center_point)
        """
        # Calculate cluster centroid
        lats = [poi['lat'] for poi in cluster_pois]
        lons = [poi['lon'] for poi in cluster_pois]
        center_lat = np.mean(lats)
        center_lon = np.mean(lons)
        center_point = Point(center_lon, center_lat)
        
        # Check if we can reuse an existing network
        reusable = self.find_reusable_network(center_lat, center_lon, travel_time_limit)
        if reusable is not None:
            return reusable
        
        # Calculate required network size
        # Find the maximum distance from center to any POI in cluster
        max_distance_km = 0
        for poi in cluster_pois:
            distance_km = geodesic((center_lat, center_lon), (poi['lat'], poi['lon'])).kilometers
            max_distance_km = max(max_distance_km, distance_km)
        
        # Add buffer for travel time and safety margin
        network_radius_km = max_distance_km + (travel_time_limit * 0.8)  # Assume ~50km/h average speed
        network_radius_m = int(network_radius_km * 1000)
        
        logger.info(f"Downloading shared network for cluster of {len(cluster_pois)} POIs "
                   f"(center: {center_lat:.4f}, {center_lon:.4f}, radius: {network_radius_km:.1f}km)")
        
        # Download network
        from .network_cache import download_network_with_cache
        network = download_network_with_cache(
            lat=center_lat,
            lon=center_lon,
            dist=network_radius_m,
            network_type='drive'
        )
        
        # Store for reuse
        network_id = len(self.shared_networks)
        self.shared_networks[network_id] = (network, center_point, travel_time_limit)
        
        return network, center_point
    
    def create_isochrone_from_shared_network(self,
                                           poi: Dict[str, Any],
                                           network: nx.MultiDiGraph,
                                           travel_time_limit: int) -> gpd.GeoDataFrame:
        """
        Create isochrone from a shared network.
        
        Args:
            poi: POI dictionary
            network: Shared network graph
            travel_time_limit: Travel time limit in minutes
            
        Returns:
            GeoDataFrame with isochrone
        """
        latitude = poi['lat']
        longitude = poi['lon']
        poi_name = poi.get('tags', {}).get('name', f"poi_{poi.get('id', 'unknown')}")
        
        # Prepare network (add speeds and travel times if not already present)
        if 'speed_kph' not in list(network.edges(data=True))[0][2]:
            network = ox.add_edge_speeds(network, fallback=50)
            network = ox.add_edge_travel_times(network)
        
        # Ensure network is projected
        if not ox.projection.is_projected(network.graph['crs']):
            network = ox.project_graph(network)
        
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
            radius=travel_time_limit * 60,  # Convert minutes to seconds
            distance='travel_time'
        )
        
        # Create isochrone
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
        isochrone_gdf['travel_time_minutes'] = travel_time_limit
        
        return isochrone_gdf
    
    def process_cluster_batch(self,
                            cluster_pois: List[Dict[str, Any]],
                            travel_time_limit: int,
                            cluster_id: int) -> List[gpd.GeoDataFrame]:
        """
        Process a cluster of POIs using shared network.
        
        Args:
            cluster_pois: List of POIs in the cluster
            travel_time_limit: Travel time limit in minutes
            cluster_id: Cluster identifier
            
        Returns:
            List of isochrone GeoDataFrames
        """
        logger.info(f"Processing cluster {cluster_id} with {len(cluster_pois)} POIs")
        
        # Get or create shared network for this cluster
        shared_network, center_point = self.get_or_create_shared_network(cluster_pois, travel_time_limit)
        
        # Process each POI using the shared network
        isochrones = []
        for poi in get_progress_bar(cluster_pois, desc=f"Cluster {cluster_id}", unit="POI", leave=False):
            try:
                isochrone_gdf = self.create_isochrone_from_shared_network(
                    poi, shared_network, travel_time_limit
                )
                isochrones.append(isochrone_gdf)
            except Exception as e:
                poi_name = poi.get('tags', {}).get('name', poi.get('id', 'unknown'))
                logger.warning(f"Error processing POI {poi_name} in cluster {cluster_id}: {e}")
                continue
        
        return isochrones
    
    def optimize_isochrone_generation(self,
                                    poi_data: Dict[str, List[Dict[str, Any]]],
                                    travel_time_limit: int) -> List[gpd.GeoDataFrame]:
        """
        Generate isochrones with spatial optimization.
        
        Args:
            poi_data: Dictionary with 'pois' key containing list of POIs
            travel_time_limit: Travel time limit in minutes
            
        Returns:
            List of isochrone GeoDataFrames
        """
        pois = poi_data.get('pois', [])
        if not pois:
            raise ValueError("No POIs found in input data")
        
        logger.info(f"Starting optimized isochrone generation for {len(pois)} POIs")
        start_time = time.time()
        
        # Create spatial clusters
        clusters = self.create_spatial_clusters(pois)
        
        # Process each cluster
        all_isochrones = []
        total_clusters = len(clusters)
        
        for cluster_id, cluster_pois in clusters.items():
            cluster_isochrones = self.process_cluster_batch(
                cluster_pois, travel_time_limit, cluster_id
            )
            all_isochrones.extend(cluster_isochrones)
            
            logger.info(f"Completed cluster {cluster_id + 1}/{total_clusters} "
                       f"({len(all_isochrones)}/{len(pois)} total POIs)")
        
        total_time = time.time() - start_time
        logger.info(f"Optimized isochrone generation completed in {total_time:.2f}s "
                   f"({len(all_isochrones)} isochrones, {len(self.shared_networks)} shared networks)")
        
        return all_isochrones
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        total_nodes = sum(len(net[0].nodes) for net in self.shared_networks.values())
        total_edges = sum(len(net[0].edges) for net in self.shared_networks.values())
        
        return {
            'shared_networks': len(self.shared_networks),
            'total_nodes': total_nodes,
            'total_edges': total_edges,
            'cluster_radius_km': self.cluster_radius_km,
            'network_reuse_distance_km': self.network_reuse_distance_km
        } 