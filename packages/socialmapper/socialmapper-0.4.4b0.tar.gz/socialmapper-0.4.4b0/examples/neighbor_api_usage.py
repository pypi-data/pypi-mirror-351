#!/usr/bin/env python3
"""
Example: Using SocialMapper's Neighbor API

This example demonstrates how to use SocialMapper's neighbor functionality
directly for geographic analysis without running the full SocialMapper workflow.

The neighbor API uses a file-based system for optimal performance and reliability.
"""

import sys
from pathlib import Path

# Add the package to the path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

# Method 1: Through main package
print("=== Method 1: Through Main Package ===")
from socialmapper import get_neighboring_states, get_neighboring_counties, get_geography_from_point

# Get neighboring states for North Carolina (FIPS: 37)
nc_neighbors = get_neighboring_states('37')
print(f"North Carolina neighbors: {nc_neighbors}")

# Get neighboring counties for Wake County, NC (37, 183)
wake_neighbors = get_neighboring_counties('37', '183')
print(f"Wake County neighbors: {wake_neighbors[:5]}...")  # Show first 5

# Point lookup for Raleigh, NC
raleigh_geo = get_geography_from_point(35.7796, -78.6382)
print(f"Raleigh geography: {raleigh_geo}")

print("\n" + "="*60 + "\n")

# Method 2: Direct import from file-based module
print("=== Method 2: Direct Import from File-Based Module ===")
from socialmapper.neighbors_file_based import (
    get_neighboring_states,
    get_neighboring_counties,
    get_geography_from_point,
    get_counties_from_pois
)

# Same functionality, different import path
ca_neighbors = get_neighboring_states('06')  # California
print(f"California neighbors: {ca_neighbors}")

# Batch POI processing
pois = [
    {'lat': 35.7796, 'lon': -78.6382, 'name': 'Raleigh'},
    {'lat': 35.2271, 'lon': -80.8431, 'name': 'Charlotte'},
    {'lat': 36.0726, 'lon': -79.7920, 'name': 'Greensboro'}
]

counties = get_counties_from_pois(pois, include_neighbors=True)
print(f"Counties for NC POIs (with neighbors): {len(counties)} total")
print(f"Sample counties: {counties[:5]}")

print("\n" + "="*60 + "\n")

# Method 3: Dedicated neighbors API module  
print("=== Method 3: Dedicated Neighbors API Module ===")
import socialmapper.neighbors as neighbors

# Clean namespace access
tx_neighbors = neighbors.get_neighboring_states('48')  # Texas
print(f"Texas neighbors: {tx_neighbors}")

# Use convenience functions
nc_neighbors_abbr = neighbors.get_neighboring_states_by_abbr('NC')
print(f"NC neighbors (by abbreviation): {nc_neighbors_abbr}")

# Get database statistics
stats = neighbors.get_statistics()
print(f"Neighbor database stats:")
for key, value in stats.items():
    print(f"  {key}: {value:,}")

print("\n" + "="*60 + "\n")

# Method 4: Advanced usage with file manager
print("=== Method 4: Advanced Usage ===")
from socialmapper.neighbors_file_based import get_file_neighbor_manager

# Get the manager for advanced operations
manager = get_file_neighbor_manager()

# Example: Find all counties that border multiple states
print("Finding counties with cross-state neighbors...")
all_states = ['37', '45', '47']  # NC, SC, TN
cross_state_counties = []

for state in all_states:
    # Get all counties in the state (simplified approach)
    sample_counties = ['001', '003', '005']  # Just a few for demo
    
    for county in sample_counties:
        try:
            county_neighbors = manager.get_neighboring_counties(state, county, include_cross_state=True)
            cross_state_neighbors = [n for n in county_neighbors if n[0] != state]
            
            if cross_state_neighbors:
                cross_state_counties.append((state, county, len(cross_state_neighbors)))
        except:
            pass  # Skip counties that don't exist

if cross_state_counties:
    print("Counties with cross-state neighbors:")
    for state, county, neighbor_count in cross_state_counties[:5]:
        state_name = neighbors.get_state_abbr(state)
        print(f"  {state_name} County {county}: {neighbor_count} cross-state neighbors")

print("\n" + "="*60 + "\n")
print("✅ Neighbor API examples completed successfully!")
print("💡 All methods use the same fast file-based system with zero dependencies") 