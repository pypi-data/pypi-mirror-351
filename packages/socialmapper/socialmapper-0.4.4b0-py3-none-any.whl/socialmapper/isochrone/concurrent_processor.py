#!/usr/bin/env python3
"""
Concurrent processing module for parallelizing isochrone generation.

This module provides multiprocessing capabilities for CPU-intensive OSMnx operations.
"""

import logging
import multiprocessing as mp
from typing import Dict, List, Any, Optional, Tuple
import geopandas as gpd
import pandas as pd
from functools import partial
import time
import os

from socialmapper.progress import get_progress_bar

logger = logging.getLogger(__name__)

def _process_poi_worker(args: Tuple[Dict[str, Any], int, str, bool, Optional[float], bool]) -> Optional[gpd.GeoDataFrame]:
    """
    Worker function for processing a single POI.
    
    Args:
        args: Tuple of (poi, travel_time_limit, output_dir, save_file, simplify_tolerance, use_parquet)
        
    Returns:
        GeoDataFrame with isochrone or None if error
    """
    poi, travel_time_limit, output_dir, save_file, simplify_tolerance, use_parquet = args
    
    try:
        # Import here to avoid issues with multiprocessing
        from . import create_isochrone_from_poi
        
        result = create_isochrone_from_poi(
            poi=poi,
            travel_time_limit=travel_time_limit,
            output_dir=output_dir,
            save_file=save_file,
            simplify_tolerance=simplify_tolerance,
            use_parquet=use_parquet
        )
        
        # If save_file=True, result is a file path, load it
        if save_file and isinstance(result, str):
            if result.endswith('.parquet'):
                result = gpd.read_parquet(result)
            else:
                result = gpd.read_file(result)
        
        return result
        
    except Exception as e:
        poi_name = poi.get('tags', {}).get('name', poi.get('id', 'unknown'))
        logger.error(f"Error processing POI {poi_name}: {e}")
        return None

def _process_cluster_worker(args: Tuple[List[Dict[str, Any]], int, int]) -> List[gpd.GeoDataFrame]:
    """
    Worker function for processing a cluster of POIs with shared network.
    
    Args:
        args: Tuple of (cluster_pois, travel_time_limit, cluster_id)
        
    Returns:
        List of isochrone GeoDataFrames
    """
    cluster_pois, travel_time_limit, cluster_id = args
    
    try:
        # Import here to avoid issues with multiprocessing
        from .spatial_optimizer import SpatialIsochroneOptimizer
        
        optimizer = SpatialIsochroneOptimizer()
        return optimizer.process_cluster_batch(cluster_pois, travel_time_limit, cluster_id)
        
    except Exception as e:
        logger.error(f"Error processing cluster {cluster_id}: {e}")
        return []

class ConcurrentIsochroneProcessor:
    """
    Processes isochrones using multiprocessing for improved performance.
    """
    
    def __init__(self, max_workers: Optional[int] = None, use_spatial_optimization: bool = True):
        """
        Initialize the concurrent processor.
        
        Args:
            max_workers: Maximum number of worker processes (defaults to CPU count)
            use_spatial_optimization: Whether to use spatial clustering optimization
        """
        self.max_workers = max_workers or min(mp.cpu_count(), 8)  # Cap at 8 to avoid overwhelming
        self.use_spatial_optimization = use_spatial_optimization
        
        logger.info(f"Initialized concurrent processor with {self.max_workers} workers")
    
    def process_pois_parallel(self,
                            poi_data: Dict[str, List[Dict[str, Any]]],
                            travel_time_limit: int,
                            output_dir: str = 'output/isochrones',
                            save_individual_files: bool = False,
                            simplify_tolerance: Optional[float] = None,
                            use_parquet: bool = True) -> List[gpd.GeoDataFrame]:
        """
        Process POIs in parallel without spatial optimization.
        
        Args:
            poi_data: Dictionary with 'pois' key containing list of POIs
            travel_time_limit: Travel time limit in minutes
            output_dir: Directory to save isochrone files
            save_individual_files: Whether to save individual files
            simplify_tolerance: Tolerance for geometry simplification
            use_parquet: Whether to use GeoParquet format
            
        Returns:
            List of isochrone GeoDataFrames
        """
        pois = poi_data.get('pois', [])
        if not pois:
            raise ValueError("No POIs found in input data")
        
        logger.info(f"Processing {len(pois)} POIs with {self.max_workers} workers")
        start_time = time.time()
        
        # Prepare arguments for workers
        worker_args = [
            (poi, travel_time_limit, output_dir, save_individual_files, simplify_tolerance, use_parquet)
            for poi in pois
        ]
        
        # Process in parallel
        results = []
        with mp.Pool(processes=self.max_workers) as pool:
            # Use imap for progress tracking
            for i, result in enumerate(pool.imap(_process_poi_worker, worker_args)):
                if result is not None:
                    results.append(result)
                
                # Progress update every 10 POIs
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(pois)} POIs ({len(results)} successful)")
        
        total_time = time.time() - start_time
        logger.info(f"Parallel processing completed in {total_time:.2f}s "
                   f"({len(results)}/{len(pois)} successful)")
        
        return results
    
    def process_pois_with_spatial_optimization(self,
                                             poi_data: Dict[str, List[Dict[str, Any]]],
                                             travel_time_limit: int) -> List[gpd.GeoDataFrame]:
        """
        Process POIs with spatial clustering and parallel processing.
        
        Args:
            poi_data: Dictionary with 'pois' key containing list of POIs
            travel_time_limit: Travel time limit in minutes
            
        Returns:
            List of isochrone GeoDataFrames
        """
        pois = poi_data.get('pois', [])
        if not pois:
            raise ValueError("No POIs found in input data")
        
        logger.info(f"Processing {len(pois)} POIs with spatial optimization and {self.max_workers} workers")
        start_time = time.time()
        
        # Create spatial clusters
        from .spatial_optimizer import SpatialIsochroneOptimizer
        optimizer = SpatialIsochroneOptimizer()
        clusters = optimizer.create_spatial_clusters(pois)
        
        logger.info(f"Created {len(clusters)} spatial clusters")
        
        # Prepare arguments for cluster workers
        cluster_args = [
            (cluster_pois, travel_time_limit, cluster_id)
            for cluster_id, cluster_pois in clusters.items()
        ]
        
        # Process clusters in parallel
        all_results = []
        with mp.Pool(processes=min(self.max_workers, len(clusters))) as pool:
            for i, cluster_results in enumerate(pool.imap(_process_cluster_worker, cluster_args)):
                all_results.extend(cluster_results)
                logger.info(f"Completed cluster {i + 1}/{len(clusters)} "
                           f"({len(all_results)}/{len(pois)} total POIs)")
        
        total_time = time.time() - start_time
        logger.info(f"Optimized parallel processing completed in {total_time:.2f}s "
                   f"({len(all_results)}/{len(pois)} successful)")
        
        return all_results
    
    def process_pois(self,
                   poi_data: Dict[str, List[Dict[str, Any]]],
                   travel_time_limit: int,
                   output_dir: str = 'output/isochrones',
                   save_individual_files: bool = False,
                   simplify_tolerance: Optional[float] = None,
                   use_parquet: bool = True) -> List[gpd.GeoDataFrame]:
        """
        Process POIs using the best available method.
        
        Args:
            poi_data: Dictionary with 'pois' key containing list of POIs
            travel_time_limit: Travel time limit in minutes
            output_dir: Directory to save isochrone files
            save_individual_files: Whether to save individual files
            simplify_tolerance: Tolerance for geometry simplification
            use_parquet: Whether to use GeoParquet format
            
        Returns:
            List of isochrone GeoDataFrames
        """
        pois = poi_data.get('pois', [])
        
        # Choose processing method based on POI count and settings
        if len(pois) < 10:
            # For small datasets, use simple sequential processing
            logger.info("Using sequential processing for small dataset")
            from . import create_isochrones_from_poi_list
            result = create_isochrones_from_poi_list(
                poi_data=poi_data,
                travel_time_limit=travel_time_limit,
                output_dir=output_dir,
                save_individual_files=save_individual_files,
                combine_results=False,
                simplify_tolerance=simplify_tolerance,
                use_parquet=use_parquet
            )
            return result if isinstance(result, list) else [result]
        
        elif self.use_spatial_optimization and len(pois) >= 20:
            # For larger datasets, use spatial optimization
            return self.process_pois_with_spatial_optimization(poi_data, travel_time_limit)
        
        else:
            # For medium datasets, use simple parallel processing
            return self.process_pois_parallel(
                poi_data=poi_data,
                travel_time_limit=travel_time_limit,
                output_dir=output_dir,
                save_individual_files=save_individual_files,
                simplify_tolerance=simplify_tolerance,
                use_parquet=use_parquet
            )

def create_isochrones_concurrent(poi_data: Dict[str, List[Dict[str, Any]]],
                               travel_time_limit: int,
                               max_workers: Optional[int] = None,
                               use_spatial_optimization: bool = True,
                               **kwargs) -> List[gpd.GeoDataFrame]:
    """
    Convenience function for concurrent isochrone generation.
    
    Args:
        poi_data: Dictionary with 'pois' key containing list of POIs
        travel_time_limit: Travel time limit in minutes
        max_workers: Maximum number of worker processes
        use_spatial_optimization: Whether to use spatial clustering
        **kwargs: Additional arguments passed to processor
        
    Returns:
        List of isochrone GeoDataFrames
    """
    processor = ConcurrentIsochroneProcessor(
        max_workers=max_workers,
        use_spatial_optimization=use_spatial_optimization
    )
    
    return processor.process_pois(poi_data, travel_time_limit, **kwargs) 