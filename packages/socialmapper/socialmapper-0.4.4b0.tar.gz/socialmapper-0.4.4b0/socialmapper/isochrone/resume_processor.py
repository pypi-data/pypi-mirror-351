#!/usr/bin/env python3
"""
Resume-capable processor for large-scale isochrone generation.

This module implements checkpoint/resume functionality for processing
large datasets that may be interrupted.
"""

import os
import pickle
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import geopandas as gpd
import pandas as pd

from .batch_processor import OSMnxBatchProcessor
from .spatial_optimizer import SpatialIsochroneOptimizer
from socialmapper.progress import get_progress_bar

logger = logging.getLogger(__name__)

class ResumeableProcessor:
    """
    Processor with checkpoint/resume capability for large datasets.
    
    This addresses the need for processing large datasets (like 259,193 parcels)
    with the ability to resume from interruptions.
    """
    
    def __init__(self, 
                 output_dir: str = "output",
                 checkpoint_dir: str = "checkpoints",
                 checkpoint_interval: int = 100):
        """
        Initialize the resumeable processor.
        
        Args:
            output_dir: Directory for final outputs
            checkpoint_dir: Directory for checkpoint files
            checkpoint_interval: Number of POIs between checkpoints
        """
        self.output_dir = Path(output_dir)
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_interval = checkpoint_interval
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_id = None
        self.progress_file = None
        
    def create_processing_session(self, poi_data: Dict[str, List[Dict[str, Any]]], 
                                travel_time_minutes: int) -> str:
        """
        Create a new processing session with unique ID.
        
        Args:
            poi_data: POI data to process
            travel_time_minutes: Travel time limit
            
        Returns:
            Session ID string
        """
        import hashlib
        
        # Create session ID based on data and parameters
        data_hash = hashlib.md5(
            json.dumps(poi_data, sort_keys=True).encode()
        ).hexdigest()[:8]
        
        timestamp = int(time.time())
        self.session_id = f"session_{data_hash}_{travel_time_minutes}min_{timestamp}"
        
        # Create session metadata
        session_metadata = {
            'session_id': self.session_id,
            'total_pois': len(poi_data.get('pois', [])),
            'travel_time_minutes': travel_time_minutes,
            'created_at': timestamp,
            'status': 'created'
        }
        
        # Save session metadata
        session_file = self.checkpoint_dir / f"{self.session_id}_metadata.json"
        with open(session_file, 'w') as f:
            json.dump(session_metadata, f, indent=2)
        
        # Initialize progress tracking
        self.progress_file = self.checkpoint_dir / f"{self.session_id}_progress.json"
        self._save_progress({
            'completed_pois': [],
            'failed_pois': [],
            'completed_count': 0,
            'last_checkpoint': timestamp
        })
        
        logger.info(f"Created processing session: {self.session_id}")
        return self.session_id
    
    def find_existing_session(self, poi_data: Dict[str, List[Dict[str, Any]]], 
                            travel_time_minutes: int) -> Optional[str]:
        """
        Find existing session for the same data and parameters.
        
        Args:
            poi_data: POI data to process
            travel_time_minutes: Travel time limit
            
        Returns:
            Session ID if found, None otherwise
        """
        import hashlib
        
        # Calculate data hash
        data_hash = hashlib.md5(
            json.dumps(poi_data, sort_keys=True).encode()
        ).hexdigest()[:8]
        
        # Look for existing sessions
        pattern = f"session_{data_hash}_{travel_time_minutes}min_*_metadata.json"
        
        for metadata_file in self.checkpoint_dir.glob(pattern):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                if metadata.get('status') != 'completed':
                    session_id = metadata['session_id']
                    logger.info(f"Found existing incomplete session: {session_id}")
                    return session_id
                    
            except Exception as e:
                logger.warning(f"Error reading session metadata {metadata_file}: {e}")
                continue
        
        return None
    
    def load_session_progress(self, session_id: str) -> Dict[str, Any]:
        """
        Load progress for an existing session.
        
        Args:
            session_id: Session ID to load
            
        Returns:
            Progress dictionary
        """
        self.session_id = session_id
        self.progress_file = self.checkpoint_dir / f"{session_id}_progress.json"
        
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                progress = json.load(f)
            
            logger.info(f"Loaded session progress: {progress['completed_count']} POIs completed")
            return progress
        else:
            logger.warning(f"No progress file found for session {session_id}")
            return {
                'completed_pois': [],
                'failed_pois': [],
                'completed_count': 0,
                'last_checkpoint': time.time()
            }
    
    def _save_progress(self, progress: Dict[str, Any]):
        """Save progress to checkpoint file."""
        if self.progress_file:
            with open(self.progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
    
    def _save_checkpoint(self, results: List[gpd.GeoDataFrame], checkpoint_id: int):
        """Save intermediate results to checkpoint file."""
        if not results:
            return
        
        checkpoint_file = self.checkpoint_dir / f"{self.session_id}_checkpoint_{checkpoint_id}.parquet"
        
        # Combine results into single GeoDataFrame
        combined_gdf = gpd.GeoDataFrame(pd.concat(results, ignore_index=True))
        combined_gdf.to_parquet(checkpoint_file)
        
        logger.info(f"Saved checkpoint {checkpoint_id} with {len(results)} results")
    
    def _load_all_checkpoints(self) -> List[gpd.GeoDataFrame]:
        """Load all checkpoint files for the current session."""
        results = []
        
        pattern = f"{self.session_id}_checkpoint_*.parquet"
        checkpoint_files = sorted(self.checkpoint_dir.glob(pattern))
        
        for checkpoint_file in checkpoint_files:
            try:
                gdf = gpd.read_parquet(checkpoint_file)
                results.append(gdf)
                logger.info(f"Loaded checkpoint: {checkpoint_file.name}")
            except Exception as e:
                logger.error(f"Error loading checkpoint {checkpoint_file}: {e}")
        
        return results
    
    def process_with_resume(self,
                          poi_data: Dict[str, List[Dict[str, Any]]],
                          travel_time_minutes: int,
                          use_batch_processing: bool = True,
                          use_spatial_optimization: bool = True,
                          force_restart: bool = False) -> List[gpd.GeoDataFrame]:
        """
        Process POIs with resume capability.
        
        Args:
            poi_data: POI data to process
            travel_time_minutes: Travel time limit
            use_batch_processing: Whether to use batch processing
            use_spatial_optimization: Whether to use spatial optimization
            force_restart: Force restart even if existing session found
            
        Returns:
            List of isochrone GeoDataFrames
        """
        pois = poi_data.get('pois', [])
        if not pois:
            raise ValueError("No POIs found in input data")
        
        # Check for existing session
        existing_session = None if force_restart else self.find_existing_session(poi_data, travel_time_minutes)
        
        if existing_session:
            # Resume existing session
            logger.info(f"Resuming existing session: {existing_session}")
            progress = self.load_session_progress(existing_session)
            
            # Load existing results
            existing_results = self._load_all_checkpoints()
            
            # Filter out completed POIs
            completed_poi_ids = set(progress.get('completed_pois', []))
            remaining_pois = [poi for poi in pois if poi.get('id') not in completed_poi_ids]
            
            logger.info(f"Resuming with {len(remaining_pois)} remaining POIs "
                       f"(already completed: {len(completed_poi_ids)})")
            
        else:
            # Create new session
            logger.info("Starting new processing session")
            self.create_processing_session(poi_data, travel_time_minutes)
            progress = {
                'completed_pois': [],
                'failed_pois': [],
                'completed_count': 0,
                'last_checkpoint': time.time()
            }
            existing_results = []
            remaining_pois = pois
        
        # Process remaining POIs
        if remaining_pois:
            new_results = self._process_pois_with_checkpoints(
                {'pois': remaining_pois}, 
                travel_time_minutes,
                progress,
                use_batch_processing,
                use_spatial_optimization
            )
        else:
            new_results = []
        
        # Combine all results
        all_results = existing_results + new_results
        
        # Mark session as completed
        self._mark_session_completed()
        
        logger.info(f"Processing completed: {len(all_results)} total results")
        return all_results
    
    def _process_pois_with_checkpoints(self,
                                     poi_data: Dict[str, List[Dict[str, Any]]],
                                     travel_time_minutes: int,
                                     progress: Dict[str, Any],
                                     use_batch_processing: bool,
                                     use_spatial_optimization: bool) -> List[gpd.GeoDataFrame]:
        """Process POIs with periodic checkpointing."""
        pois = poi_data.get('pois', [])
        
        # Choose processor
        if use_batch_processing:
            processor = OSMnxBatchProcessor(max_batch_size=50)
            process_func = processor.process_pois_in_batches
        elif use_spatial_optimization:
            processor = SpatialIsochroneOptimizer()
            process_func = processor.optimize_isochrone_generation
        else:
            # Fallback to standard processing
            from . import create_isochrones_from_poi_list
            process_func = lambda data, time_limit: create_isochrones_from_poi_list(
                data, time_limit, save_individual_files=False, combine_results=False
            )
        
        all_results = []
        checkpoint_id = len(progress.get('completed_pois', [])) // self.checkpoint_interval
        
        # Process in chunks for checkpointing
        for i in range(0, len(pois), self.checkpoint_interval):
            chunk_pois = pois[i:i + self.checkpoint_interval]
            chunk_data = {'pois': chunk_pois}
            
            logger.info(f"Processing chunk {i//self.checkpoint_interval + 1} "
                       f"({len(chunk_pois)} POIs)")
            
            try:
                # Process chunk
                chunk_results = process_func(chunk_data, travel_time_minutes)
                
                if isinstance(chunk_results, gpd.GeoDataFrame):
                    chunk_results = [chunk_results]
                
                all_results.extend(chunk_results)
                
                # Update progress
                completed_poi_ids = [poi.get('id') for poi in chunk_pois]
                progress['completed_pois'].extend(completed_poi_ids)
                progress['completed_count'] += len(chunk_pois)
                progress['last_checkpoint'] = time.time()
                
                # Save checkpoint
                self._save_checkpoint(chunk_results, checkpoint_id)
                self._save_progress(progress)
                
                checkpoint_id += 1
                
                logger.info(f"Checkpoint saved: {progress['completed_count']} POIs completed")
                
            except Exception as e:
                logger.error(f"Error processing chunk {i//self.checkpoint_interval + 1}: {e}")
                
                # Mark POIs as failed
                failed_poi_ids = [poi.get('id') for poi in chunk_pois]
                progress['failed_pois'].extend(failed_poi_ids)
                self._save_progress(progress)
                
                continue
        
        return all_results
    
    def _mark_session_completed(self):
        """Mark the current session as completed."""
        if not self.session_id:
            return
        
        metadata_file = self.checkpoint_dir / f"{self.session_id}_metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            metadata['status'] = 'completed'
            metadata['completed_at'] = time.time()
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Session {self.session_id} marked as completed")
    
    def cleanup_session(self, session_id: str):
        """Clean up checkpoint files for a completed session."""
        pattern = f"{session_id}_*"
        files_to_remove = list(self.checkpoint_dir.glob(pattern))
        
        for file_path in files_to_remove:
            try:
                file_path.unlink()
                logger.info(f"Removed checkpoint file: {file_path.name}")
            except Exception as e:
                logger.warning(f"Error removing {file_path}: {e}")
        
        logger.info(f"Cleaned up session: {session_id}")
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all processing sessions."""
        sessions = []
        
        for metadata_file in self.checkpoint_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                sessions.append(metadata)
            except Exception as e:
                logger.warning(f"Error reading {metadata_file}: {e}")
        
        return sorted(sessions, key=lambda x: x.get('created_at', 0), reverse=True)

def process_with_resume(poi_data: Dict[str, List[Dict[str, Any]]],
                       travel_time_minutes: int,
                       output_dir: str = "output",
                       **kwargs) -> List[gpd.GeoDataFrame]:
    """
    Convenience function for resumeable processing.
    
    Args:
        poi_data: POI data to process
        travel_time_minutes: Travel time limit
        output_dir: Output directory
        **kwargs: Additional arguments
        
    Returns:
        List of isochrone GeoDataFrames
    """
    processor = ResumeableProcessor(output_dir=output_dir)
    return processor.process_with_resume(poi_data, travel_time_minutes, **kwargs) 