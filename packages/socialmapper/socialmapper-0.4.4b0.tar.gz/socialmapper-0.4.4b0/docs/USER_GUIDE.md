# 📖 SocialMapper User Guide

**Complete guide to using SocialMapper for demographic analysis and community mapping**

## 🚀 Quick Start

SocialMapper helps you understand communities by combining:
- **Points of Interest** (restaurants, schools, hospitals) from OpenStreetMap
- **Travel time analysis** (isochrones) 
- **Census demographics** (population, income, age)
- **Interactive maps** and visualizations

### Installation

```bash
pip install socialmapper
```

### 30-Second Example

```python
import socialmapper

# Find libraries in Austin, TX and analyze surrounding demographics
results = socialmapper.run_socialmapper(
    query="library",
    location="Austin, TX", 
    max_results=10,
    travel_times=[10, 20],  # 10 and 20-minute travel times
    variables=["B01003_001E", "B08301_010E"]  # Population, Public Transit
)

# Results include POIs, isochrones, demographics, and maps
print(f"Found {len(results['pois'])} libraries")
print(f"Generated maps in: {results['output_dir']}")
```

## 📋 Table of Contents

1. [Core Concepts](#core-concepts)
2. [Basic Usage Examples](#basic-usage-examples)
3. [Advanced Workflows](#advanced-workflows)
4. [Real-World Use Cases](#real-world-use-cases)
5. [Customization & Configuration](#customization--configuration)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Core Concepts

### What SocialMapper Does

SocialMapper follows a **4-step analytical workflow**:

1. **🔍 Query POIs** - Find points of interest using OpenStreetMap
2. **🕐 Calculate Isochrones** - Determine travel time boundaries  
3. **📊 Get Demographics** - Pull census data for affected areas
4. **🗺️ Generate Maps** - Create interactive visualizations

### Key Components

| Component | Purpose | Example |
|-----------|---------|---------|
| **POI Query** | Find facilities/amenities | "Find all hospitals in Seattle" |
| **Isochrones** | Travel time boundaries | "15-minute walk from each hospital" |
| **Census Data** | Demographics & statistics | "Population density, median income" |
| **Mapping** | Visual analysis | "Interactive map with layers" |

---

## 🔧 Basic Usage Examples

### Example 1: School Access Analysis

**Question**: *"Where are the schools in Portland, and what communities do they serve?"*

```python
import socialmapper

# Find schools and analyze 15-minute walking access
results = socialmapper.run_socialmapper(
    query="school",
    location="Portland, OR",
    max_results=20,
    travel_times=[15],
    travel_mode="walking", 
    variables=[
        "B01003_001E",  # Total population
        "B08013_001E",  # Aggregate travel time to work
        "B25003_002E",  # Owner-occupied housing units
    ],
    output_dir="./school_analysis"
)

print(f"Found {len(results['pois'])} schools")
print(f"Analyzed {len(results['census_data'])} block groups")

# Access individual components
schools = results['pois']
travel_areas = results['isochrones'] 
demographics = results['census_data']
```

### Example 2: Healthcare Access in Rural Areas

**Question**: *"How far do people need to travel to reach hospitals in rural Montana?"*

```python
import socialmapper

# Analyze hospital access with driving times
results = socialmapper.run_socialmapper(
    query="hospital",
    location="Bozeman, MT",
    max_results=15,
    travel_times=[30, 60],  # 30 and 60-minute drives
    travel_mode="driving",
    variables=[
        "B01003_001E",  # Total population
        "B08303_008E",  # 30-44 minutes travel time to work
        "B19013_001E",  # Median household income
        "B25001_001E",  # Total housing units
    ],
    selection_mode="intersect",  # Include all intersecting areas
    output_dir="./rural_healthcare"
)

# Analyze results
print("Healthcare Access Analysis:")
print(f"- {len(results['pois'])} hospitals found")
print(f"- {len(results['isochrones'])} travel zones created")
print(f"- {results['census_data']['B01003_001E'].sum():,} total population analyzed")
```

### Example 3: Public Transit & Libraries

**Question**: *"Which libraries are accessible by public transit, and who uses them?"*

```python
import socialmapper

# Find libraries accessible by transit
results = socialmapper.run_socialmapper(
    query="library",
    location="San Francisco, CA",
    max_results=25,
    travel_times=[20, 45],  # 20 and 45-minute transit trips
    travel_mode="transit",
    variables=[
        "B08301_010E",  # Public transportation
        "B15003_022E",  # Bachelor's degree
        "B01001_002E",  # Male population  
        "B01001_026E",  # Female population
        "B25003_003E",  # Renter-occupied housing
    ],
    output_dir="./library_transit_access"
)

# Analyze transit accessibility
transit_users = results['census_data']['B08301_010E'].sum()
total_pop = results['census_data']['B01003_001E'].sum()
transit_rate = (transit_users / total_pop) * 100

print(f"Transit Analysis:")
print(f"- Libraries accessible by transit: {len(results['pois'])}")
print(f"- Transit usage rate: {transit_rate:.1f}%")
print(f"- College educated: {results['census_data']['B15003_022E'].sum():,}")
```

---

## 🏗️ Advanced Workflows

### Custom Coordinate Analysis

**Use Case**: *"Analyze specific locations I've identified"*

```python
import socialmapper

# Define custom locations (lat, lon, name)
custom_locations = [
    (40.7128, -74.0060, "Manhattan Community Center"),
    (40.6892, -74.0445, "Brooklyn Health Clinic"),
    (40.7589, -73.9851, "Bronx Library Branch")
]

# Convert to custom coordinates format
coordinates = socialmapper.parse_custom_coordinates(custom_locations)

results = socialmapper.run_socialmapper(
    custom_coordinates=coordinates,
    travel_times=[10, 20, 30],
    travel_mode="walking",
    variables=[
        "B01003_001E",  # Population
        "B08303_001E",  # Total commute time
        "B19013_001E",  # Median income
    ],
    output_dir="./custom_locations"
)
```

### Multi-City Comparison

**Use Case**: *"Compare library access across different cities"*

```python
import socialmapper
import pandas as pd

cities = ["Austin, TX", "Portland, OR", "Nashville, TN"]
all_results = {}

for city in cities:
    print(f"Analyzing {city}...")
    
    results = socialmapper.run_socialmapper(
        query="library",
        location=city,
        max_results=15,
        travel_times=[15],
        travel_mode="walking",
        variables=["B01003_001E", "B15003_022E"],  # Pop, College educated
        output_dir=f"./comparison_{city.replace(', ', '_')}"
    )
    
    all_results[city] = results

# Compare results
comparison = []
for city, data in all_results.items():
    comparison.append({
        'city': city,
        'libraries': len(data['pois']),
        'population': data['census_data']['B01003_001E'].sum(),
        'college_educated': data['census_data']['B15003_022E'].sum()
    })

comparison_df = pd.DataFrame(comparison)
print("\nCity Comparison:")
print(comparison_df)
```

### Detailed Demographics Analysis

**Use Case**: *"Deep dive into community characteristics"*

```python
import socialmapper

# Comprehensive demographic analysis
results = socialmapper.run_socialmapper(
    query="community center",
    location="Denver, CO",
    max_results=12,
    travel_times=[10, 20],
    travel_mode="walking",
    variables=[
        # Population by age
        "B01001_003E",  # Male under 5
        "B01001_027E",  # Female under 5  
        "B01001_020E",  # Male 65-66
        "B01001_044E",  # Female 65-66
        
        # Economic indicators
        "B19013_001E",  # Median household income
        "B25064_001E",  # Median gross rent
        "B23025_005E",  # Unemployed
        
        # Transportation
        "B08301_001E",  # Total commuters
        "B08301_010E",  # Public transit
        "B08301_021E",  # Walk to work
    ],
    output_dir="./denver_communities"
)

# Calculate derived metrics
census_data = results['census_data']

# Age analysis
children_under_5 = census_data['B01001_003E'] + census_data['B01001_027E']
seniors_65_plus = census_data['B01001_020E'] + census_data['B01001_044E']
total_pop = census_data['B01003_001E']

# Transportation analysis  
total_commuters = census_data['B08301_001E']
transit_commuters = census_data['B08301_010E']
walk_commuters = census_data['B08301_021E']

print("Community Profile:")
print(f"- Children under 5: {children_under_5.sum():,} ({children_under_5.sum()/total_pop.sum()*100:.1f}%)")
print(f"- Seniors 65+: {seniors_65_plus.sum():,} ({seniors_65_plus.sum()/total_pop.sum()*100:.1f}%)")
print(f"- Transit usage: {transit_commuters.sum()/total_commuters.sum()*100:.1f}%")
print(f"- Walk to work: {walk_commuters.sum()/total_commuters.sum()*100:.1f}%")
```

---

## 🌍 Real-World Use Cases

### Urban Planning: New Park Location

**Scenario**: *"City wants to build a new park - where would it serve the most people?"*

```python
import socialmapper
import numpy as np

# Step 1: Analyze existing parks
existing_parks = socialmapper.run_socialmapper(
    query="park",
    location="Raleigh, NC",
    max_results=30,
    travel_times=[10],  # 10-minute walk
    travel_mode="walking",
    variables=["B01003_001E"],  # Population
    output_dir="./existing_parks"
)

# Step 2: Identify underserved areas by finding gaps
print(f"Current park coverage:")
print(f"- {len(existing_parks['pois'])} parks found")
print(f"- {existing_parks['census_data']['B01003_001E'].sum():,} people within 10min walk")

# Step 3: Analyze proposed locations
proposed_locations = [
    (35.8801, -78.7880, "Proposed Park Site A"),
    (35.8320, -78.7134, "Proposed Park Site B"), 
    (35.8875, -78.6890, "Proposed Park Site C")
]

coordinates = socialmapper.parse_custom_coordinates(proposed_locations)

proposed_analysis = socialmapper.run_socialmapper(
    custom_coordinates=coordinates,
    travel_times=[10],
    travel_mode="walking", 
    variables=["B01003_001E", "B01001_003E", "B01001_027E"],  # Pop, children
    output_dir="./proposed_parks"
)

# Compare proposals
for i, location in enumerate(proposed_locations):
    site_data = proposed_analysis['census_data'][
        proposed_analysis['census_data']['poi_id'] == f"poi_{i}"
    ]
    
    total_pop = site_data['B01003_001E'].sum()
    children = site_data['B01001_003E'].sum() + site_data['B01001_027E'].sum()
    
    print(f"\n{location[2]}:")
    print(f"  - Population served: {total_pop:,}")
    print(f"  - Children under 5: {children:,}")
    print(f"  - Score: {total_pop + (children * 2):,}")  # Weight children 2x
```

### Public Health: Food Desert Analysis

**Scenario**: *"Identify areas with limited access to fresh food"*

```python
import socialmapper

# Analyze grocery store access
grocery_access = socialmapper.run_socialmapper(
    query="grocery OR supermarket",  # Multiple search terms
    location="Detroit, MI",
    max_results=40,
    travel_times=[15, 30],  # Walking and driving times
    travel_mode="walking",
    variables=[
        "B01003_001E",  # Population
        "B19013_001E",  # Median income
        "B08141_002E",  # No vehicle available
        "B01001_020E",  # Seniors (male 65-66)
        "B01001_044E",  # Seniors (female 65-66)
    ],
    output_dir="./food_access_walking"
)

# Also analyze driving access
driving_access = socialmapper.run_socialmapper(
    query="grocery OR supermarket",
    location="Detroit, MI", 
    max_results=40,
    travel_times=[10],  # 10-minute drive
    travel_mode="driving",
    variables=["B01003_001E"],
    output_dir="./food_access_driving"
)

# Identify food deserts (areas with limited walking access)
walking_pop = grocery_access['census_data']['B01003_001E'].sum()
driving_pop = driving_access['census_data']['B01003_001E'].sum()
no_vehicle = grocery_access['census_data']['B08141_002E'].sum()

print("Food Access Analysis:")
print(f"- Stores found: {len(grocery_access['pois'])}")
print(f"- Walking access (15min): {walking_pop:,} people")
print(f"- Driving access (10min): {driving_pop:,} people") 
print(f"- No vehicle available: {no_vehicle:,} households")
print(f"- Potential food desert impact: {driving_pop - walking_pop:,} people")
```

### Education: School Catchment Analysis

**Scenario**: *"Understand which communities each school serves"*

```python
import socialmapper
import folium

# Analyze schools with detailed demographics
school_analysis = socialmapper.run_socialmapper(
    query="elementary school",
    location="Charlotte, NC",
    max_results=25,
    travel_times=[5, 10, 15],  # Multiple walking distances
    travel_mode="walking",
    variables=[
        "B01003_001E",  # Total population
        "B01001_003E",  # Male under 5
        "B01001_027E",  # Female under 5
        "B15003_017E",  # High school graduate
        "B15003_022E",  # Bachelor's degree
        "B19013_001E",  # Median income
        "B25003_002E",  # Owner occupied housing
    ],
    output_dir="./school_catchments"
)

# Analyze each school's catchment area
schools = school_analysis['pois']
census_data = school_analysis['census_data']

print("School Catchment Analysis:")
print(f"Found {len(schools)} elementary schools\n")

for i, school in schools.iterrows():
    # Get census data for this school's catchment
    school_data = census_data[census_data['poi_id'] == f"poi_{i}"]
    
    if len(school_data) > 0:
        total_pop = school_data['B01003_001E'].sum()
        children = school_data['B01001_003E'].sum() + school_data['B01001_027E'].sum()
        median_income = school_data['B19013_001E'].median()
        college_rate = school_data['B15003_022E'].sum() / school_data['B15003_017E'].sum() * 100
        
        print(f"{school['name']}:")
        print(f"  - Catchment population: {total_pop:,}")
        print(f"  - Children under 5: {children:,}")
        print(f"  - Median income: ${median_income:,.0f}")
        print(f"  - College education rate: {college_rate:.1f}%")
        print()
```

---

## ⚙️ Customization & Configuration

### Custom Variables & Analysis

```python
import socialmapper

# Define custom variable sets for different analyses
DEMOGRAPHIC_VARIABLES = [
    "B01003_001E",  # Total population
    "B01001_002E",  # Male
    "B01001_026E",  # Female  
    "B01002_001E",  # Median age
]

ECONOMIC_VARIABLES = [
    "B19013_001E",  # Median household income
    "B25064_001E",  # Median gross rent
    "B23025_005E",  # Unemployed
    "B08303_001E",  # Aggregate travel time to work
]

HOUSING_VARIABLES = [
    "B25001_001E",  # Total housing units
    "B25003_002E",  # Owner-occupied
    "B25003_003E",  # Renter-occupied
    "B25024_002E",  # 1-unit detached
]

# Use different variable sets for different analyses
demographics = socialmapper.run_socialmapper(
    query="community center",
    location="Austin, TX",
    variables=DEMOGRAPHIC_VARIABLES,
    output_dir="./demographics"
)

economics = socialmapper.run_socialmapper(
    query="job center",  
    location="Austin, TX",
    variables=ECONOMIC_VARIABLES,
    output_dir="./economics"
)
```

### Advanced Query Techniques

```python
import socialmapper

# Complex POI queries
results = socialmapper.run_socialmapper(
    # Use OR for multiple amenity types
    query="hospital OR clinic OR urgent care",
    
    # Or use specific tags
    # query="amenity=hospital OR amenity=clinic",
    
    location="Phoenix, AZ",
    max_results=50,
    travel_times=[20, 40],
    travel_mode="driving",
    
    # Selection modes
    selection_mode="intersect",  # "intersect", "contain", or "clip"
    
    variables=["B01003_001E", "B19013_001E"],
    output_dir="./healthcare_phoenix"
)
```

### Performance Optimization

```python
import socialmapper

# For large analyses, optimize performance
results = socialmapper.run_socialmapper(
    query="school",
    location="Los Angeles, CA",
    max_results=100,  # Large dataset
    travel_times=[15],  # Fewer time intervals
    travel_mode="walking",
    
    # Optimize census data retrieval
    variables=["B01003_001E"],  # Fewer variables for speed
    
    # Use caching
    force_refresh=False,  # Use cached data when available
    
    output_dir="./la_schools"
)

print(f"Analysis completed for {len(results['pois'])} schools")
```

---

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 1. No POIs Found

```python
# Problem: Empty results
results = socialmapper.run_socialmapper(
    query="very_specific_amenity",
    location="Small Town, ST"
)
# results['pois'] is empty

# Solutions:
# A) Broaden your search
results = socialmapper.run_socialmapper(
    query="restaurant OR cafe OR food",  # Broader terms
    location="Small Town, ST",
    max_results=50  # Increase search radius
)

# B) Try different location format
results = socialmapper.run_socialmapper(
    query="restaurant",
    location="County Name, State"  # Use county instead of city
)

# C) Check OpenStreetMap data coverage
from socialmapper.query import query_overpass
raw_results = query_overpass("restaurant", "Small Town, ST")
print(f"Raw OSM results: {len(raw_results)}")
```

#### 2. Census API Errors

```python
# Problem: Census data missing
import socialmapper

# Check your API key
from socialmapper.util import get_census_api_key
api_key = get_census_api_key()
print(f"Census API key configured: {api_key is not None}")

# Solution: Set up Census API key
# 1. Get free key from: https://api.census.gov/data/key_signup.html
# 2. Set environment variable: export CENSUS_API_KEY=your_key_here
# 3. Or create .env file with: CENSUS_API_KEY=your_key_here
```

#### 3. Isochrone Generation Issues

```python
# Problem: Travel time calculation fails
import socialmapper

try:
    results = socialmapper.run_socialmapper(
        query="library",
        location="Remote Area, MT",
        travel_times=[30],
        travel_mode="transit"  # May not be available
    )
except Exception as e:
    print(f"Error: {e}")
    
    # Solution: Use different travel mode
    results = socialmapper.run_socialmapper(
        query="library", 
        location="Remote Area, MT",
        travel_times=[30],
        travel_mode="driving"  # More likely to work in rural areas
    )
```

#### 4. Large Dataset Performance

```python
# Problem: Analysis takes too long
import socialmapper

# Optimize for large datasets
results = socialmapper.run_socialmapper(
    query="restaurant",
    location="New York, NY",  # Large city
    max_results=20,  # Limit results
    travel_times=[10],  # Single time interval
    variables=["B01003_001E"],  # Minimal variables
    output_dir="./optimized_analysis"
)
```

### Getting Help

- **Documentation**: Check the [API Reference](./API_REFERENCE.md)
- **Examples**: See more examples in the `/examples` directory
- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/socialmapper/issues)
- **Community**: Join discussions on [GitHub Discussions](https://github.com/yourusername/socialmapper/discussions)

---

## 📚 Next Steps

1. **Try the examples** - Start with Basic Usage Examples
2. **Explore your area** - Run analyses for your city/region
3. **Read the API Reference** - Learn about all available options
4. **Join the community** - Share your analyses and get help

**Ready to start mapping your community? Pick an example above and try it with your own location!** 🗺️✨ 