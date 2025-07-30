#!/usr/bin/env python3
"""Command-line interface for SocialMapper."""

import argparse
import logging
import sys
import time
import traceback
import os

from . import __version__
from .core import run_socialmapper, setup_directory
from .util import CENSUS_VARIABLE_MAPPING, normalize_census_variable
from .states import normalize_state, StateFormat

# Configure basic logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description=f"SocialMapper v{__version__}: Tool for mapping community resources and demographics"
    )
    
    # Input source group
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--custom-coords", help="Path to custom coordinates file (CSV or JSON)")
    input_group.add_argument("--poi", action="store_true", help="Use direct POI parameters")
    
    # POI parameters (used when --poi is specified)
    poi_group = parser.add_argument_group("POI Parameters (used with --poi)")
    poi_group.add_argument("--geocode-area", help="Area to search within (city/town name)")
    poi_group.add_argument("--city", help="City to search within (defaults to geocode-area if not specified)")
    poi_group.add_argument("--poi-type", help="Type of POI (e.g., 'amenity', 'leisure')")
    poi_group.add_argument("--poi-name", help="Name of POI (e.g., 'library', 'park')")
    poi_group.add_argument("--state", help="State name or abbreviation")
    
    # General parameters
    parser.add_argument("--travel-time", type=int, default=15, help="Travel time in minutes")
    parser.add_argument(
        "--census-variables", 
        nargs="+", 
        default=["total_population"], 
        help="Census variables to retrieve (e.g. total_population median_household_income)"
    )
    parser.add_argument("--api-key", help="Census API key (optional if set as environment variable)")
    parser.add_argument("--list-variables", action="store_true", help="List available census variables and exit")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done without actually doing it")
    
    # Output type controls - only CSV enabled by default
    parser.add_argument(
        "--export-csv", 
        action="store_true", 
        default=True, 
        help="Export census data to CSV format (default: enabled)"
    )
    parser.add_argument(
        "--no-export-csv", 
        action="store_false", 
        dest="export_csv", 
        help="Disable exporting census data to CSV format"
    )
    parser.add_argument(
        "--export-maps", 
        action="store_true", 
        default=False, 
        help="Generate map visualizations (default: disabled)"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Custom output directory for all generated files (default: 'output')"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"SocialMapper {__version__}",
        help="Show version and exit"
    )
    
    # Performance enhancement options
    parser.add_argument(
        "--benchmark",
        action="store_true", 
        default=False,
        help="Enable performance benchmarking and save results"
    )
    
    # Performance optimization arguments
    parser.add_argument("--disable-spatial-optimization", action="store_true", 
                       help="Disable spatial clustering and network sharing optimizations")
    parser.add_argument("--disable-concurrent-processing", action="store_true",
                       help="Disable multiprocessing for isochrone generation")
    parser.add_argument("--max-workers", type=int, 
                       help="Maximum number of worker processes (defaults to CPU count)")
    parser.add_argument("--cluster-radius-km", type=float, default=2.0,
                       help="Maximum distance between POIs in same cluster (km)")
    parser.add_argument("--network-reuse-distance-km", type=float, default=1.0,
                       help="Maximum distance for network reuse (km)")
    parser.add_argument("--disable-batch-processing", action="store_true",
                       help="Disable batch processing for network downloads")
    parser.add_argument("--enable-resume", action="store_true",
                       help="Enable checkpoint/resume capability for large datasets")
    parser.add_argument("--force-restart", action="store_true",
                       help="Force restart even if existing session found")
    
    # Other arguments
    parser.add_argument("--benchmark-performance", action="store_true",
                       help="Enable performance benchmarking and save results")
    parser.add_argument("--max-poi-count", type=int,
                       help="Maximum number of POIs to process (useful for testing)")

    args = parser.parse_args()
    
    # Validate required arguments for POI query mode
    if not args.custom_coords and not all([args.geocode_area, args.poi_type, args.poi_name]):
        parser.error("Either --custom-coords or all of --geocode-area, --poi-type, and --poi-name are required")
    
    return args

def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # If user just wants to list available variables
    if args.list_variables:
        print("\nAvailable Census Variables:")
        print("=" * 50)
        for code, name in sorted(CENSUS_VARIABLE_MAPPING.items()):
            print(f"{name:<25} {code}")
        print("\nUsage example: --census-variables total_population median_household_income")
        sys.exit(0)
        
    # Create the output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Print banner
    print("=" * 80)
    print(f"SocialMapper v{__version__}: End-to-end tool for mapping community resources")
    print("=" * 80)
    
    # If dry-run, just print what would be done and exit
    if args.dry_run:
        print("\n=== DRY RUN - SHOWING PLANNED STEPS ===")
        if args.poi:
            print(f"POI Query: {args.geocode_area} - {args.poi_type} - {args.poi_name}")
        else:
            print(f"Custom coordinates: {args.custom_coords}")
        print(f"Travel time limit: {args.travel_time} minutes")
        print(f"Census variables: {', '.join(args.census_variables)}")
        print(f"Output directory: {args.output_dir}")
        print("\nOutput types to be generated:")
        print(f"  - CSV: {'Yes' if args.export_csv else 'No'}")
        print(f"  - Maps: {'Yes' if args.export_maps else 'No'}")
        print("\nNo operations will be performed.")
        sys.exit(0)
    
    # Execute the full process
    print("\n=== Starting SocialMapper ===")
    start_time = time.time()
    
    try:
        # Execute the full pipeline
        if args.custom_coords:
            # Custom coordinates mode
            result = run_socialmapper(
                custom_coords_path=args.custom_coords,
                travel_time=args.travel_time,
                census_variables=args.census_variables,
                api_key=args.api_key,
                output_dir=args.output_dir,
                export_csv=args.export_csv,
                export_maps=args.export_maps,
                name_field=args.name_field,
                type_field=args.type_field,
                max_poi_count=args.max_poi_count,
                benchmark_performance=args.benchmark_performance,
                use_spatial_optimization=not args.disable_spatial_optimization,
                use_concurrent_processing=not args.disable_concurrent_processing,
                max_workers=args.max_workers,
                use_batch_processing=not args.disable_batch_processing,
                use_resume_capability=args.enable_resume,
                force_restart=args.force_restart
            )
        else:
            # POI query mode
            result = run_socialmapper(
                geocode_area=args.geocode_area,
                state=args.state,
                poi_type=args.poi_type,
                poi_name=args.poi_name,
                travel_time=args.travel_time,
                census_variables=args.census_variables,
                api_key=args.api_key,
                output_dir=args.output_dir,
                export_csv=args.export_csv,
                export_maps=args.export_maps,
                max_poi_count=args.max_poi_count,
                benchmark_performance=args.benchmark_performance,
                use_spatial_optimization=not args.disable_spatial_optimization,
                use_concurrent_processing=not args.disable_concurrent_processing,
                max_workers=args.max_workers,
                use_batch_processing=not args.disable_batch_processing,
                use_resume_capability=args.enable_resume,
                force_restart=args.force_restart
            )
        
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"\n=== SocialMapper Completed in {elapsed:.1f} seconds ===")
        
    except Exception as e:
        print(f"\n=== Error: {str(e)} ===")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 