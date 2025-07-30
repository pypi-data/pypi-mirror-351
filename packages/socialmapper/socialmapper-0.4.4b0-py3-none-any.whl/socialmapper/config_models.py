"""
Configuration models for SocialMapper.

This module defines Pydantic models for configuration validation.
"""

from typing import Optional, List
from pydantic import BaseModel, Field

class RunConfig(BaseModel):
    """Configuration model for SocialMapper runs."""
    
    # Core parameters
    geocode_area: Optional[str] = Field(None, description="Area to search within")
    state: Optional[str] = Field(None, description="State name or abbreviation")
    city: Optional[str] = Field(None, description="City name")
    poi_type: Optional[str] = Field(None, description="Type of POI")
    poi_name: Optional[str] = Field(None, description="Name of POI")
    travel_time: int = Field(15, description="Travel time limit in minutes")
    
    # Data parameters
    census_variables: Optional[List[str]] = Field(None, description="List of census variables")
    api_key: Optional[str] = Field(None, description="Census API key")
    custom_coords_path: Optional[str] = Field(None, description="Path to custom coordinates file")
    max_poi_count: Optional[int] = Field(None, description="Maximum number of POIs to process")
    
    # Output parameters
    output_dir: str = Field("output", description="Output directory")
    export_csv: bool = Field(True, description="Export census data to CSV")
    export_maps: bool = Field(False, description="Generate maps")
    
    # Performance optimization parameters
    use_spatial_optimization: bool = Field(True, description="Enable spatial clustering and network sharing")
    use_concurrent_processing: bool = Field(True, description="Enable multiprocessing for isochrone generation")
    max_workers: Optional[int] = Field(None, description="Maximum number of worker processes")
    cluster_radius_km: float = Field(2.0, description="Maximum distance between POIs in same cluster (km)")
    network_reuse_distance_km: float = Field(1.0, description="Maximum distance for network reuse (km)")
    use_batch_processing: bool = Field(True, description="Enable batch processing for reduced network downloads")
    use_resume_capability: bool = Field(False, description="Enable checkpoint/resume for large datasets")
    force_restart: bool = Field(False, description="Force restart even if existing session found")
    
    # Other parameters
    benchmark_performance: bool = Field(False, description="Enable performance benchmarking")

    @validator("custom_coords_path", always=True)
    def at_least_one_input(cls, v, values):
        if not v and not values.get("config_path"):
            raise ValueError("custom_coords_path must be provided")
        return v

    class Config:
        arbitrary_types_allowed = True 