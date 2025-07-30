# 🔧 SocialMapper API Reference

**Complete reference for all SocialMapper functions, classes, and parameters**

## 📋 Table of Contents

1. [Main API Functions](#main-api-functions)
2. [Core Parameters](#core-parameters)
3. [Census Variables](#census-variables)
4. [Return Values & Data Structures](#return-values--data-structures)
5. [Utility Functions](#utility-functions)
6. [Configuration & Setup](#configuration--setup)
7. [Error Handling](#error-handling)

---

## 🚀 Main API Functions

### `run_socialmapper()`

**Primary analysis function that orchestrates the entire workflow**

```python
socialmapper.run_socialmapper(
    query=None,
    location=None,
    custom_coordinates=None,
    max_results=20,
    travel_times=[15],
    travel_mode="walking",
    variables=None,
    selection_mode="intersect",
    output_dir=None,
    force_refresh=False
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | `None` | OpenStreetMap query (e.g., "library", "hospital OR clinic") |
| `location` | `str` | `None` | Geographic area (e.g., "Austin, TX", "Travis County, TX") |
| `custom_coordinates` | `list` | `None` | List of custom POI coordinates |
| `max_results` | `int` | `20` | Maximum number of POIs to analyze |
| `travel_times` | `list[int]` | `[15]` | Travel times in minutes |
| `travel_mode` | `str` | `"walking"` | Travel mode: "walking", "driving", "cycling", "transit" |
| `variables` | `list[str]` | `None` | Census variable codes (e.g., ["B01003_001E"]) |
| `selection_mode` | `str` | `"intersect"` | Geometry selection: "intersect", "contain", "clip" |
| `output_dir` | `str` | `None` | Output directory path |
| `force_refresh` | `bool` | `False` | Force refresh cached data |

#### Returns

`dict` containing:
- `'pois'`: GeoDataFrame of points of interest
- `'isochrones'`: GeoDataFrame of travel time areas
- `'census_data'`: DataFrame with demographics
- `'summary'`: Dict with analysis summary
- `'output_dir'`: Path to generated outputs

#### Example

```python
import socialmapper

results = socialmapper.run_socialmapper(
    query="library",
    location="Denver, CO",
    travel_times=[10, 20],
    variables=["B01003_001E", "B19013_001E"],
    output_dir="./library_analysis"
)
```

---

## 🔍 Query & Location Functions

### `query_overpass()`

**Query OpenStreetMap for points of interest**

```python
from socialmapper.query import query_overpass

pois = query_overpass(
    query="library",
    location="Seattle, WA",
    max_results=25
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | Required | POI query string |
| `location` | `str` | Required | Geographic area |
| `max_results` | `int` | `50` | Maximum POIs to return |

#### Returns

`GeoDataFrame` with columns:
- `geometry`: Point geometries
- `name`: POI name
- `amenity`: POI type
- `addr:*`: Address components (when available)

### `parse_custom_coordinates()`

**Convert coordinate lists to SocialMapper format**

```python
from socialmapper import parse_custom_coordinates

locations = [
    (40.7128, -74.0060, "Manhattan Site"),
    (40.6892, -74.0445, "Brooklyn Site")
]

coordinates = parse_custom_coordinates(locations)
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `coordinates` | `list[tuple]` | List of (lat, lon, name) tuples |

#### Returns

`list[dict]` formatted for `custom_coordinates` parameter

---

## 🕐 Isochrone Functions

### `calculate_isochrones()`

**Generate travel time boundaries**

```python
from socialmapper.isochrone import calculate_isochrones

isochrones = calculate_isochrones(
    pois=pois_gdf,
    travel_times=[15, 30],
    travel_mode="walking"
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pois` | `GeoDataFrame` | Required | Points of interest |
| `travel_times` | `list[int]` | Required | Travel times in minutes |
| `travel_mode` | `str` | `"walking"` | Travel mode |

#### Travel Modes

| Mode | Description | Use Cases |
|------|-------------|-----------|
| `"walking"` | Pedestrian routes | Local amenities, urban analysis |
| `"driving"` | Car routes | Regional analysis, rural areas |
| `"cycling"` | Bicycle routes | Bike infrastructure analysis |
| `"transit"` | Public transportation | Transit accessibility studies |

#### Returns

`GeoDataFrame` with columns:
- `geometry`: Polygon geometries (travel time areas)
- `poi_id`: Associated POI identifier
- `travel_time`: Travel time in minutes
- `travel_mode`: Mode of transportation

---

## 📊 Census Functions

### `get_census_data()`

**Retrieve demographics for geographic areas**

```python
from socialmapper.census import get_census_data

census_data = get_census_data(
    isochrones=isochrones_gdf,
    variables=["B01003_001E", "B19013_001E"],
    selection_mode="intersect"
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `isochrones` | `GeoDataFrame` | Required | Travel time areas |
| `variables` | `list[str]` | Required | Census variable codes |
| `selection_mode` | `str` | `"intersect"` | Geometry selection method |

#### Selection Modes

| Mode | Description | When to Use |
|------|-------------|-------------|
| `"intersect"` | Include all intersecting block groups | Most comprehensive coverage |
| `"contain"` | Only fully contained block groups | Conservative estimates |
| `"clip"` | Clip demographics to exact boundaries | Most precise (slower) |

---

## 📋 Core Parameters

### Geographic Specification

#### Location Format Examples

| Format | Example | Description |
|--------|---------|-------------|
| City, State | `"Austin, TX"` | Standard city specification |
| County, State | `"Travis County, TX"` | County-level analysis |
| Address | `"1600 Pennsylvania Ave, Washington, DC"` | Specific address |
| Coordinates | `"30.2672,-97.7431"` | Lat, lon coordinates |

### Query Syntax

#### Basic Queries

```python
# Single amenity type
query="library"

# Multiple types with OR
query="hospital OR clinic OR urgent_care"

# Specific tags
query="amenity=hospital"
query="shop=supermarket"
```

#### Advanced Query Examples

```python
# Healthcare facilities
query="amenity=hospital OR amenity=clinic OR amenity=pharmacy"

# Educational institutions
query="amenity=school OR amenity=university OR amenity=library"

# Food access
query="shop=supermarket OR shop=grocery OR shop=convenience"

# Recreation
query="leisure=park OR leisure=playground OR amenity=community_centre"

# Transportation
query="public_transport=station OR amenity=bus_station"
```

### Travel Time Configuration

#### Recommended Travel Times by Mode

| Mode | Typical Range | Use Cases |
|------|---------------|-----------|
| Walking | 5-20 minutes | Local amenities, walkability |
| Cycling | 10-30 minutes | Bike infrastructure, recreation |
| Driving | 15-60 minutes | Regional access, rural areas |
| Transit | 20-45 minutes | Public transportation analysis |

#### Multiple Time Analysis

```python
# Progressive analysis
travel_times=[5, 10, 15, 20]  # Walking zones

# Comparison analysis  
travel_times=[15, 30]  # Short vs medium distance

# Single optimized analysis
travel_times=[15]  # Fastest processing
```

---

## 📊 Census Variables

### Complete Variable Reference

#### Population & Demographics

| Variable Code | Description | Notes |
|---------------|-------------|-------|
| `B01003_001E` | Total population | Most commonly used |
| `B01001_002E` | Male population | |
| `B01001_026E` | Female population | |
| `B01002_001E` | Median age | |
| `B01001_003E` | Male under 5 years | Children analysis |
| `B01001_027E` | Female under 5 years | Children analysis |
| `B01001_020E` | Male 65-66 years | Seniors analysis |
| `B01001_044E` | Female 65-66 years | Seniors analysis |

#### Economic Indicators

| Variable Code | Description | Notes |
|---------------|-------------|-------|
| `B19013_001E` | Median household income | Key economic indicator |
| `B25077_001E` | Median home value | Housing market |
| `B25064_001E` | Median gross rent | Rental market |
| `B23025_005E` | Unemployed | Employment analysis |
| `B08303_001E` | Aggregate travel time to work | Commuting patterns |

#### Education

| Variable Code | Description | Notes |
|---------------|-------------|-------|
| `B15003_022E` | Bachelor's degree | College educated |
| `B15003_023E` | Master's degree | Graduate level |
| `B15003_024E` | Professional degree | Professional education |
| `B15003_025E` | Doctorate degree | PhD level |
| `B15003_017E` | Regular high school diploma | High school completion |

#### Housing

| Variable Code | Description | Notes |
|---------------|-------------|-------|
| `B25001_001E` | Total housing units | Housing supply |
| `B25003_002E` | Owner-occupied housing | Homeownership |
| `B25003_003E` | Renter-occupied housing | Rental housing |
| `B25024_002E` | 1-unit detached | Single family homes |

#### Transportation

| Variable Code | Description | Notes |
|---------------|-------------|-------|
| `B08301_001E` | Total commuters | |
| `B08301_010E` | Public transportation | Transit usage |
| `B08301_021E` | Walked to work | Walking commuters |
| `B08141_002E` | No vehicle available | Car-free households |

#### Race & Ethnicity

| Variable Code | Description | Notes |
|---------------|-------------|-------|
| `B02001_002E` | White alone | |
| `B02001_003E` | Black or African American alone | |
| `B02001_005E` | Asian alone | |
| `B03003_003E` | Hispanic or Latino | |

### Variable Collections for Common Analysis

#### Basic Demographics

```python
BASIC_DEMOGRAPHICS = [
    "B01003_001E",  # Total population
    "B01002_001E",  # Median age
    "B19013_001E",  # Median household income
]
```

#### Family & Children Analysis

```python
FAMILY_VARIABLES = [
    "B01003_001E",  # Total population
    "B01001_003E",  # Male under 5
    "B01001_027E",  # Female under 5
    "B25003_002E",  # Owner-occupied housing
]
```

#### Economic Analysis

```python
ECONOMIC_VARIABLES = [
    "B19013_001E",  # Median household income
    "B25077_001E",  # Median home value
    "B25064_001E",  # Median gross rent
    "B23025_005E",  # Unemployed
]
```

#### Transportation Analysis

```python
TRANSPORTATION_VARIABLES = [
    "B08301_001E",  # Total commuters
    "B08301_010E",  # Public transportation
    "B08301_021E",  # Walked to work
    "B08141_002E",  # No vehicle available
]
```

---

## 📦 Return Values & Data Structures

### Main Results Dictionary

```python
results = {
    'pois': GeoDataFrame,        # Points of interest
    'isochrones': GeoDataFrame,  # Travel time areas
    'census_data': DataFrame,    # Demographics with distances
    'summary': dict,             # Analysis summary
    'output_dir': str           # Output directory path
}
```

### POIs GeoDataFrame

| Column | Type | Description |
|--------|------|-------------|
| `geometry` | Point | POI coordinates |
| `poi_id` | str | Unique identifier |
| `name` | str | POI name |
| `amenity` | str | POI type |
| `latitude` | float | Latitude |
| `longitude` | float | Longitude |

### Isochrones GeoDataFrame

| Column | Type | Description |
|--------|------|-------------|
| `geometry` | Polygon | Travel time area |
| `poi_id` | str | Associated POI |
| `travel_time` | int | Travel time (minutes) |
| `travel_mode` | str | Transportation mode |

### Census Data DataFrame

| Column | Type | Description |
|--------|------|-------------|
| `GEOID` | str | Census block group ID |
| `poi_id` | str | Associated POI |
| `distance_km` | float | Distance to POI |
| `B01003_001E` | int | Variable values (example) |
| ... | ... | Additional census variables |

### Summary Dictionary

```python
summary = {
    'total_pois': int,
    'total_population': int,
    'analysis_area_sq_km': float,
    'travel_modes': list,
    'travel_times': list,
    'census_variables': list
}
```

---

## 🛠️ Utility Functions

### Geographic Utilities

#### `get_neighboring_states()`

```python
from socialmapper import get_neighboring_states

neighbors = get_neighboring_states("37")  # North Carolina
# Returns: ["45", "21", "47", "13"]  # SC, KY, TN, GA
```

#### `get_neighboring_counties()`

```python
from socialmapper import get_neighboring_counties

neighbors = get_neighboring_counties("37183")  # Wake County, NC
# Returns: list of neighboring county FIPS codes
```

### Data Export Functions

#### `export_to_csv()`

```python
from socialmapper.export import export_to_csv

export_to_csv(
    results=results,
    output_dir="./exports",
    include_geometry=False
)
```

#### `export_to_geojson()`

```python
from socialmapper.export import export_to_geojson

export_to_geojson(
    gdf=results['isochrones'],
    filename="travel_areas.geojson"
)
```

### Visualization Functions

#### `create_summary_map()`

```python
from socialmapper.visualization import create_summary_map

map_obj = create_summary_map(
    pois=results['pois'],
    isochrones=results['isochrones'],
    census_data=results['census_data'],
    variable="B01003_001E"
)
```

---

## ⚙️ Configuration & Setup

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CENSUS_API_KEY` | Recommended | Census Bureau API key |
| `SOCIALMAPPER_CACHE_DIR` | Optional | Custom cache directory |

### Cache Configuration

```python
from socialmapper.util import configure_cache

configure_cache(
    cache_dir="./custom_cache",
    max_size_gb=5.0,
    ttl_days=30
)
```

### Setting up Census API Key

```bash
# Option 1: Environment variable
export CENSUS_API_KEY=your_key_here

# Option 2: .env file
echo "CENSUS_API_KEY=your_key_here" > .env

# Option 3: Python
import os
os.environ['CENSUS_API_KEY'] = 'your_key_here'
```

Get your free API key: https://api.census.gov/data/key_signup.html

---

## 🚨 Error Handling

### Common Exceptions

#### `POIQueryError`

```python
from socialmapper.exceptions import POIQueryError

try:
    results = socialmapper.run_socialmapper(
        query="nonexistent_amenity",
        location="Nowhere, XX"
    )
except POIQueryError as e:
    print(f"POI query failed: {e}")
```

#### `IsochroneError`

```python
from socialmapper.exceptions import IsochroneError

try:
    results = socialmapper.run_socialmapper(
        query="library",
        location="Remote Area, MT",
        travel_mode="transit"  # May not be available
    )
except IsochroneError as e:
    print(f"Isochrone generation failed: {e}")
```

#### `CensusDataError`

```python
from socialmapper.exceptions import CensusDataError

try:
    results = socialmapper.run_socialmapper(
        query="library",
        location="Austin, TX",
        variables=["INVALID_VARIABLE"]
    )
except CensusDataError as e:
    print(f"Census data error: {e}")
```

### Error Recovery Patterns

#### Graceful Fallbacks

```python
import socialmapper

def robust_analysis(query, location):
    """Analysis with built-in fallbacks"""
    
    # Try preferred configuration
    try:
        return socialmapper.run_socialmapper(
            query=query,
            location=location,
            travel_mode="transit",
            travel_times=[15, 30]
        )
    except socialmapper.IsochroneError:
        # Fallback to walking
        print("Transit not available, falling back to walking")
        return socialmapper.run_socialmapper(
            query=query,
            location=location,
            travel_mode="walking",
            travel_times=[15]
        )

results = robust_analysis("library", "Rural Town, MT")
```

#### Input Validation

```python
def validate_inputs(query, location, variables):
    """Validate inputs before analysis"""
    
    if not query or not location:
        raise ValueError("Query and location are required")
    
    # Check variable format
    if variables:
        for var in variables:
            if not var.endswith('E'):
                raise ValueError(f"Invalid census variable: {var}")
    
    return True

# Use validation
try:
    validate_inputs("library", "Austin, TX", ["B01003_001E"])
    results = socialmapper.run_socialmapper(...)
except ValueError as e:
    print(f"Input error: {e}")
```

---

## 📊 Performance Guidelines

### Parameter Impact on Performance

| Parameter | Impact | Optimization Tips |
|-----------|--------|-------------------|
| `max_results` | High | Start with 20, increase gradually |
| `travel_times` | Medium | Fewer time intervals = faster |
| `variables` | Medium | Limit to essential variables |
| `selection_mode` | Low | "intersect" fastest, "clip" slowest |
| `travel_mode` | Low | "walking" usually fastest |

### Memory Usage Estimates

| Dataset Size | Memory Usage | Recommended RAM |
|-------------|---------------|-----------------|
| 1-20 POIs | 100-500 MB | 2+ GB |
| 21-50 POIs | 500 MB - 1 GB | 4+ GB |
| 51-100 POIs | 1-2 GB | 8+ GB |
| 100+ POIs | 2+ GB | 16+ GB |

### Performance Optimization

```python
# High-performance configuration
results = socialmapper.run_socialmapper(
    query="school",
    location="Large City, ST",
    max_results=50,
    travel_times=[15],  # Single time interval
    variables=["B01003_001E"],  # Minimal variables
    force_refresh=False  # Use cache when available
)
```

---

## 🔗 Integration Examples

### With Pandas

```python
import pandas as pd
import socialmapper

results = socialmapper.run_socialmapper(...)

# Convert to regular DataFrame
df = pd.DataFrame(results['census_data'])

# Statistical analysis
correlation = df['B01003_001E'].corr(df['distance_km'])
print(f"Population-Distance Correlation: {correlation}")
```

### With GeoPandas

```python
import geopandas as gpd
import socialmapper

results = socialmapper.run_socialmapper(...)

# Spatial operations
isochrones = results['isochrones']
total_area = isochrones.geometry.area.sum()
print(f"Total coverage area: {total_area/1e6:.2f} sq km")
```

### With Matplotlib

```python
import matplotlib.pyplot as plt
import socialmapper

results = socialmapper.run_socialmapper(...)

# Create custom visualization
fig, ax = plt.subplots(figsize=(12, 8))
results['isochrones'].plot(ax=ax, alpha=0.5)
results['pois'].plot(ax=ax, color='red', markersize=50)
plt.title("POI Access Analysis")
plt.show()
```

---

## 📝 Version Compatibility

### Current Version: 0.4.3-beta

#### Breaking Changes from 0.3.x
- `poi_type` and `poi_name` parameters replaced with single `query` parameter
- `geocode_area` parameter renamed to `location`
- Census variable names changed to standard codes (e.g., `"total_population"` → `"B01003_001E"`)

#### Migration Guide

```python
# Old (0.3.x)
results = run_socialmapper(
    poi_type="amenity",
    poi_name="library", 
    geocode_area="Austin, TX",
    census_variables=["total_population"]
)

# New (0.4.3+)
results = run_socialmapper(
    query="library",
    location="Austin, TX",
    variables=["B01003_001E"]
)
```

---

## 📚 Additional Resources

- **User Guide**: [USER_GUIDE.md](./USER_GUIDE.md) - Practical examples and tutorials
- **Performance Guide**: [PERFORMANCE_GUIDE.md](./PERFORMANCE_GUIDE.md) - Optimization strategies
- **Migration Guide**: [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - Upgrading from older versions

---

*Last Updated: 2025-05-31 | SocialMapper v0.4.3-beta* 