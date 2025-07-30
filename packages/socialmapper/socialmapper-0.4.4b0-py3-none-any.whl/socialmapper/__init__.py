#!/usr/bin/env python3
"""
SocialMapper: An open-source Python toolkit for understanding community connections 
through mapping demographics and access to points of interest.

This package provides tools for:
- Querying points of interest from OpenStreetMap
- Generating travel time isochrones
- Analyzing census demographics
- Creating interactive maps and visualizations
"""

__version__ = "0.4.4b0"
__author__ = "mihiarc"
__email__ = "mihiarc@example.com"

# Core functionality
from .core import run_socialmapper, parse_custom_coordinates

# File-based modules (replacing DuckDB-based ones)
from .census_file_based import (
    get_file_census_manager,
    get_census_block_groups,
    isochrone_to_block_groups
)

from .neighbors_file_based import (
    get_file_neighbor_manager,
    get_neighboring_states,
    get_neighboring_counties,
    get_geography_from_point,
    get_counties_from_pois
)

# Other core modules
from .query import build_overpass_query, query_overpass, format_results
from .isochrone import create_isochrones_from_poi_list
from .distance import add_travel_distances
from .visualization import generate_maps_for_variables
from .export import export_census_data_to_csv

# Utility functions
from .util import (
    normalize_census_variable,
    get_census_api_key,
    get_readable_census_variables,
    census_code_to_name
)

from .states import (
    normalize_state,
    normalize_state_list,
    StateFormat,
    state_fips_to_name
)

# Progress utilities
from .progress import get_progress_bar

__all__ = [
    # Core functions
    "run_socialmapper",
    "parse_custom_coordinates",
    
    # File-based census and neighbors
    "get_file_census_manager",
    "get_census_block_groups", 
    "isochrone_to_block_groups",
    "get_file_neighbor_manager",
    "get_neighboring_states",
    "get_neighboring_counties", 
    "get_geography_from_point",
    "get_counties_from_pois",
    
    # Core modules
    "build_overpass_query",
    "query_overpass", 
    "format_results",
    "create_isochrones_from_poi_list",
    "add_travel_distances",
    "generate_maps_for_variables",
    "export_census_data_to_csv",
    
    # Utilities
    "normalize_census_variable",
    "get_census_api_key",
    "get_readable_census_variables", 
    "census_code_to_name",
    "normalize_state",
    "normalize_state_list",
    "StateFormat",
    "state_fips_to_name",
    "get_progress_bar"
] 