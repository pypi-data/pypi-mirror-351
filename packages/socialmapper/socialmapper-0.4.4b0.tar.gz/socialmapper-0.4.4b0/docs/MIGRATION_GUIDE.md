# 🔄 SocialMapper Migration Guide

**Upgrading to SocialMapper 0.4.3+ with modern API and file-based architecture**

This guide helps you migrate from older SocialMapper versions to the latest 0.4.3+ release, which features a modernized API, file-based architecture, and significant performance improvements.

## 📋 What's Changed

### Major Improvements in 0.4.3+

✅ **Simplified API** - Single `query` parameter replaces complex POI specifications  
✅ **File-based architecture** - No more DuckDB dependencies or database issues  
✅ **5-50x performance improvements** - Optimized spatial operations and caching  
✅ **Modern census variables** - Direct ACS variable codes instead of friendly names  
✅ **Enhanced error handling** - Better error messages and automatic fallbacks  
✅ **Cross-platform reliability** - Works identically on Windows, macOS, and Linux  

### Breaking Changes Summary

| Old (0.3.x) | New (0.4.3+) | Reason |
|-------------|---------------|---------|
| `poi_type` + `poi_name` | `query` | Simpler, more flexible |
| `geocode_area` | `location` | Clearer naming |
| `"total_population"` | `"B01003_001E"` | Standard census codes |
| `travel_time` (int) | `travel_times` (list) | Multiple time analysis |
| DuckDB backend | File-based | Better performance, reliability |

---

## 🚀 Quick Migration

### Before (0.3.x)

```python
from socialmapper import run_socialmapper

results = run_socialmapper(
    geocode_area="Austin",
    state="TX",
    poi_type="amenity",
    poi_name="library",
    travel_time=15,
    census_variables=["total_population", "median_household_income"]
)
```

### After (0.4.3+)

```python
import socialmapper

results = socialmapper.run_socialmapper(
    query="library",
    location="Austin, TX",
    travel_times=[15],
    variables=["B01003_001E", "B19013_001E"]
)
```

**That's it!** Your migration is complete. The new version is simpler and more powerful.

---

## 📊 Complete Parameter Migration

### Core Parameters

| Old Parameter | New Parameter | Example Migration |
|---------------|---------------|-------------------|
| `geocode_area="Chicago"` | `location="Chicago, IL"` | Include state for clarity |
| `state="IL"` | *(included in location)* | `location="Chicago, IL"` |
| `poi_type="amenity"` | *(included in query)* | `query="library"` |
| `poi_name="library"` | `query="library"` | Direct specification |
| `travel_time=15` | `travel_times=[15]` | List format for multiple times |

### Advanced Parameters

| Old Parameter | New Parameter | Notes |
|---------------|---------------|-------|
| `use_spatial_optimization=True` | *(automatic)* | Always enabled |
| `use_concurrent_processing=True` | *(automatic)* | Always enabled |
| `max_workers=6` | *(auto-detected)* | Automatically optimized |
| `custom_coords_path="file.csv"` | `custom_coordinates=coords` | Parse with helper function |

### Census Variables Migration

| Old Friendly Name | New Variable Code | Description |
|------------------|-------------------|-------------|
| `"total_population"` | `"B01003_001E"` | Total population |
| `"median_household_income"` | `"B19013_001E"` | Median household income |
| `"median_age"` | `"B01002_001E"` | Median age |
| `"white_population"` | `"B02001_002E"` | White alone |
| `"black_population"` | `"B02001_003E"` | Black or African American |
| `"hispanic_population"` | `"B03003_003E"` | Hispanic or Latino |
| `"median_home_value"` | `"B25077_001E"` | Median home value |
| `"housing_units"` | `"B25001_001E"` | Total housing units |
| `"education_bachelors_plus"` | `"B15003_022E"` | Bachelor's degree |

---

## 🔧 Step-by-Step Migration

### Step 1: Install Latest Version

```bash
# Uninstall old version (optional)
pip uninstall socialmapper

# Install latest version
pip install socialmapper
```

### Step 2: Update Import Statements

**Before:**
```python
from socialmapper import run_socialmapper
from socialmapper.config import setup_logging
```

**After:**
```python
import socialmapper
# Logging is automatic - no setup needed
```

### Step 3: Update Function Calls

Use this conversion template:

```python
# OLD FORMAT (0.3.x)
results = run_socialmapper(
    geocode_area="CITY",
    state="STATE", 
    poi_type="POI_TYPE",
    poi_name="POI_NAME",
    travel_time=TIME,
    census_variables=["friendly_name1", "friendly_name2"]
)

# NEW FORMAT (0.4.3+)
results = socialmapper.run_socialmapper(
    query="POI_NAME",  # or "POI_TYPE=POI_NAME"
    location="CITY, STATE",
    travel_times=[TIME],
    variables=["VARIABLE_CODE1", "VARIABLE_CODE2"]
)
```

### Step 4: Update Custom Coordinates

**Before:**
```python
# CSV file with custom POIs
results = run_socialmapper(
    custom_coords_path="my_pois.csv",
    travel_time=20,
    census_variables=["total_population"]
)
```

**After:**
```python
# Parse coordinates from list or CSV
custom_sites = [
    (lat1, lon1, "Site 1"),
    (lat2, lon2, "Site 2")
]

coordinates = socialmapper.parse_custom_coordinates(custom_sites)

results = socialmapper.run_socialmapper(
    custom_coordinates=coordinates,
    travel_times=[20],
    variables=["B01003_001E"]
)
```

---

## 🏗️ Real Migration Examples

### Example 1: Library Analysis

**Before (0.3.x):**
```python
from socialmapper import run_socialmapper

results = run_socialmapper(
    geocode_area="Boston",
    state="MA", 
    poi_type="amenity",
    poi_name="library",
    travel_time=15,
    census_variables=[
        "total_population",
        "median_household_income", 
        "education_bachelors_plus"
    ],
    use_spatial_optimization=True,
    max_workers=4
)
```

**After (0.4.3+):**
```python
import socialmapper

results = socialmapper.run_socialmapper(
    query="library",
    location="Boston, MA",
    travel_times=[15],
    variables=[
        "B01003_001E",  # Total population
        "B19013_001E",  # Median household income
        "B15003_022E"   # Bachelor's degree
    ]
    # Optimization is automatic!
)
```

### Example 2: Healthcare Access

**Before (0.3.x):**
```python
results = run_socialmapper(
    geocode_area="Rural County",
    state="Montana",
    poi_type="amenity", 
    poi_name="hospital",
    travel_time=45,
    census_variables=[
        "total_population",
        "median_age",
        "white_population"
    ],
    use_concurrent_processing=True
)
```

**After (0.4.3+):**
```python
results = socialmapper.run_socialmapper(
    query="hospital",
    location="Rural County, MT",
    travel_times=[45],
    travel_mode="driving",  # Better for rural areas
    variables=[
        "B01003_001E",  # Total population
        "B01002_001E",  # Median age  
        "B02001_002E"   # White alone
    ]
)
```

### Example 3: Multiple POI Types

**Before (0.3.x):**
```python
# Required separate calls
hospitals = run_socialmapper(
    geocode_area="Seattle",
    state="WA",
    poi_type="amenity",
    poi_name="hospital",
    travel_time=30
)

clinics = run_socialmapper(
    geocode_area="Seattle", 
    state="WA",
    poi_type="amenity",
    poi_name="clinic",
    travel_time=30
)
```

**After (0.4.3+):**
```python
# Single call with OR query
results = socialmapper.run_socialmapper(
    query="hospital OR clinic",  # Multiple types!
    location="Seattle, WA",
    travel_times=[30],
    variables=["B01003_001E"]
)
```

---

## 📁 Custom Coordinates Migration

### Old CSV Format

**my_pois.csv:**
```csv
poi_id,name,latitude,longitude
1,Main Library,40.7589,-73.9851
2,Branch Library,40.7614,-73.9776
```

**Code (0.3.x):**
```python
results = run_socialmapper(
    custom_coords_path="my_pois.csv",
    travel_time=15
)
```

### New Format

**Option 1: Direct List**
```python
custom_sites = [
    (40.7589, -73.9851, "Main Library"),
    (40.7614, -73.9776, "Branch Library")
]

coordinates = socialmapper.parse_custom_coordinates(custom_sites)

results = socialmapper.run_socialmapper(
    custom_coordinates=coordinates,
    travel_times=[15]
)
```

**Option 2: Load from CSV**
```python
import pandas as pd

# Load your existing CSV
df = pd.read_csv("my_pois.csv")
custom_sites = [(row.latitude, row.longitude, row.name) 
                for _, row in df.iterrows()]

coordinates = socialmapper.parse_custom_coordinates(custom_sites)

results = socialmapper.run_socialmapper(
    custom_coordinates=coordinates,
    travel_times=[15]
)
```

---

## 🎯 Advanced Features Migration

### Performance Configuration

**Before (0.3.x):**
```python
results = run_socialmapper(
    geocode_area="Los Angeles",
    state="CA",
    poi_type="amenity",
    poi_name="school",
    travel_time=20,
    use_spatial_optimization=True,
    use_concurrent_processing=True,
    max_workers=8
)
```

**After (0.4.3+):**
```python
# All optimizations are automatic and better!
results = socialmapper.run_socialmapper(
    query="school",
    location="Los Angeles, CA", 
    travel_times=[20],
    max_results=100  # Control dataset size for performance
)
```

### Error Handling

**Before (0.3.x):**
```python
try:
    results = run_socialmapper(...)
except Exception as e:
    print(f"Error: {e}")
```

**After (0.4.3+):**
```python
from socialmapper.exceptions import POIQueryError, CensusDataError

try:
    results = socialmapper.run_socialmapper(...)
except POIQueryError as e:
    print(f"POI search failed: {e}")
except CensusDataError as e:
    print(f"Census data error: {e}")
```

---

## 🚨 Common Migration Issues

### Issue 1: Census Variable Names

**Problem:** Old friendly names don't work
```python
# This will fail
variables=["total_population"]
```

**Solution:** Use ACS variable codes
```python
# This works
variables=["B01003_001E"]
```

**Helper:** Use the [migration table](#census-variables-migration) above.

### Issue 2: Single Travel Time

**Problem:** Old single integer doesn't work
```python
# This will fail  
travel_time=15
```

**Solution:** Use list format
```python
# This works
travel_times=[15]
```

### Issue 3: Import Statements

**Problem:** Old import style doesn't work
```python
# This will fail
from socialmapper import run_socialmapper
```

**Solution:** Use new import style
```python
# This works
import socialmapper
results = socialmapper.run_socialmapper(...)
```

### Issue 4: POI Specifications

**Problem:** Separate type/name parameters
```python
# This will fail
poi_type="amenity", poi_name="library"
```

**Solution:** Combined query
```python
# This works
query="library"
# or more specific:
query="amenity=library"
```

---

## ✅ Migration Checklist

Use this checklist to ensure complete migration:

### Code Changes
- [ ] Update import statements to `import socialmapper`
- [ ] Replace `geocode_area` + `state` with `location`
- [ ] Combine `poi_type` + `poi_name` into `query`
- [ ] Change `travel_time` to `travel_times=[time]`
- [ ] Convert census variable names to ACS codes
- [ ] Update custom coordinates format if used
- [ ] Remove manual optimization parameters

### Testing
- [ ] Run migration with small dataset first
- [ ] Verify output format matches expectations
- [ ] Check generated maps load correctly
- [ ] Confirm census data contains expected variables
- [ ] Test error handling with invalid inputs

### Performance
- [ ] Remove manual performance tuning (now automatic)
- [ ] Test large datasets for improved performance
- [ ] Verify no DuckDB files are created
- [ ] Confirm caching works properly

---

## 🎉 Benefits of Migration

After migration, you'll enjoy:

### Immediate Benefits
✅ **Simpler code** - Fewer parameters, clearer syntax  
✅ **Better performance** - 5-50x faster processing  
✅ **More reliable** - No database corruption or locking issues  
✅ **Better error messages** - Clear guidance when issues occur  

### Long-term Benefits
✅ **Future-proof** - Built on modern, stable architecture  
✅ **Cross-platform** - Works identically everywhere  
✅ **Better support** - Active development and community  
✅ **Enhanced features** - Multi-POI queries, multiple travel times  

---

## 🆘 Need Help?

### Quick Help
- **Examples**: See migrated examples in `/examples` directory
- **Documentation**: Full guides available in `/docs`
- **Variable lookup**: Use [census variables table](#census-variables-migration)

### Get Support
- **GitHub Issues**: Report migration problems
- **Discussions**: Ask questions in GitHub Discussions
- **Documentation**: Check [User Guide](./USER_GUIDE.md) and [API Reference](./API_REFERENCE.md)

### Common Resources
- **Variable codes**: [Census API documentation](https://api.census.gov/data/2021/acs/acs5/variables.html)
- **POI queries**: [OpenStreetMap wiki](https://wiki.openstreetmap.org/wiki/Map_Features)
- **Best practices**: [User Guide examples](./USER_GUIDE.md#basic-usage-examples)

---

## 🚀 Next Steps

1. **Complete your migration** using this guide
2. **Test with a small example** to verify everything works
3. **Explore new features** like multi-POI queries and multiple travel times
4. **Read the [User Guide](./USER_GUIDE.md)** for advanced usage patterns
5. **Share your success** and help others migrate!

**Welcome to SocialMapper 0.4.3+ - faster, simpler, and more reliable community mapping!** 🗺️✨

---

*Last Updated: 2025-05-31 | SocialMapper v0.4.3-beta* 