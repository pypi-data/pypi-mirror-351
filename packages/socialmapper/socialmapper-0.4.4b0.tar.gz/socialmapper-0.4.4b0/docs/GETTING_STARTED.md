# 🚀 Getting Started with SocialMapper

**Your first SocialMapper analysis in 10 minutes**

Welcome to SocialMapper! This guide will walk you through your first community analysis step-by-step. By the end, you'll understand how SocialMapper works and have generated your first interactive maps with demographics.

## 📋 What You'll Learn

1. **Prerequisites** - Ensure you have Python installed
2. **Installation** - Set up SocialMapper in a virtual environment
3. **First Analysis** - Run a complete 5-minute example
4. **Understanding Results** - Interpret your outputs
5. **Next Steps** - Where to go from here

---

## 🔧 Prerequisites

### Check if Python is Already Installed

First, let's see if you already have Python:

```bash
# Check if Python is installed
python --version
# or try:
python3 --version
```

**What you need:**
- **Python 3.11 or 3.12** (SocialMapper requires these versions)
- **pip** (usually comes with Python)

### If Python is Not Installed

**Don't have Python yet?** Here are the best installation guides:

#### 🌟 **Recommended: Official Python Guide**
- **📖 [Python.org Installation Guide](https://www.python.org/downloads/)** - Official, comprehensive instructions for all platforms

#### 🍎 **macOS Users**
```bash
# Option 1: Download from python.org (recommended for beginners)
# Visit: https://www.python.org/downloads/macos/

# Option 2: Using Homebrew (if you have it)
brew install python@3.12

# Option 3: Using pyenv (for multiple Python versions)
# Follow: https://github.com/pyenv/pyenv#installation
```

#### 🪟 **Windows Users**
```bash
# Option 1: Download from python.org (recommended)
# Visit: https://www.python.org/downloads/windows/
# ⚠️ Make sure to check "Add Python to PATH" during installation!

# Option 2: Using Windows Store
# Search "Python" in Microsoft Store

# Option 3: Using Chocolatey (if you have it)
choco install python312
```

#### 🐧 **Linux Users**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
# Note: python3-venv is needed for virtual environments

# CentOS/RHEL/Fedora
sudo dnf install python3.12 python3-pip

# Arch Linux
sudo pacman -S python python-pip

# Check if venv module is available
python3 -m venv --help
```

### Verify Your Installation

After installing Python, verify everything works:

```bash
# Check Python version (should be 3.11 or 3.12)
python --version

# Check pip is available
pip --version

# If "python" doesn't work, try "python3"
python3 --version
pip3 --version
```

**Expected output:**
```
Python 3.12.x
pip 24.x.x from ...
```

### Troubleshooting Python Installation

**Common issues:**

```bash
# "python: command not found" on Windows
# Solution: Reinstall Python and check "Add Python to PATH"

# "python3" works but "python" doesn't on macOS/Linux
# Solution: Use "python3" throughout this guide, or create alias:
alias python=python3

# Multiple Python versions installed
# Solution: Use specific version:
python3.12 --version
```

**Need more help?** Check out:
- 📖 **[Real Python Installation Guide](https://realpython.com/installing-python/)** - Detailed, beginner-friendly
- 🎥 **[Python.org Tutorial](https://docs.python.org/3/tutorial/index.html)** - Official tutorial
- 💬 **[Python Discord](https://discord.gg/python)** - Community help

---

## 🛠️ Installation

### Step 1: Create a Virtual Environment (Recommended)

**Always use a virtual environment** to avoid conflicts with other Python packages:

#### Using Python's built-in venv (Recommended)
```bash
# Create a new virtual environment
python -m venv socialmapper-env
# If "python" doesn't work, try:
# python3 -m venv socialmapper-env

# Activate it (macOS/Linux)
source socialmapper-env/bin/activate

# Activate it (Windows)
socialmapper-env\Scripts\activate

# Verify you're in the virtual environment
which python  # Should show path to your venv
python --version  # Should show Python 3.11 or 3.12
```

#### Using conda (Alternative)

**Why choose conda?** Better for data science work - handles non-Python dependencies (like geospatial libraries), provides pre-compiled packages, and has more robust dependency resolution.

```bash
# Create a new conda environment
conda create -n socialmapper python=3.11

# Activate it
conda activate socialmapper
```

**Don't have conda?** Install it first:
- **🐍 [Miniconda](https://docs.conda.io/en/latest/miniconda.html)** (Recommended - lightweight)
- **🐍 [Anaconda](https://www.anaconda.com/download)** (Full data science distribution)

#### Using uv (Fast Alternative)

**Why choose uv?** Much faster than pip (10-100x speedup), better dependency resolution, and modern user experience. Great if you want the latest Python tooling.

```bash
# Create and activate with uv (if you have it installed)
uv venv socialmapper-env
source socialmapper-env/bin/activate  # macOS/Linux
# or: socialmapper-env\Scripts\activate  # Windows
```

**Don't have uv?** Install this modern, fast Python package manager:
- **⚡ [uv Installation Guide](https://docs.astral.sh/uv/getting-started/installation/)** (Very fast, modern tool)
- **📦 [uv GitHub](https://github.com/astral-sh/uv)** (Open source project)

### Step 2: Install SocialMapper

With your virtual environment activated:

```bash
pip install socialmapper
```

**That's it!** SocialMapper works out of the box.

### Step 3: Get a Census API Key (Optional but Recommended)

While SocialMapper works without an API key, getting one improves performance and removes rate limits.

1. **Get your free key**: Visit https://api.census.gov/data/key_signup.html
2. **Set up the key**:

```bash
# Option 1: Environment variable (recommended)
export CENSUS_API_KEY=your_key_here

# Option 2: Create .env file in your project directory
echo "CENSUS_API_KEY=your_key_here" > .env
```

### Step 4: Verify Installation

**Check that SocialMapper installed correctly:**

#### Option 1: Check version (Recommended)
```bash
# Simple version check
socialmapper --version
```

**Expected output:**
```
SocialMapper 0.4.4b0
```

#### Option 2: Package details
```bash
# Detailed package information
pip show socialmapper
```

**Expected output:**
```
Name: socialmapper
Version: 0.4.4b0
Summary: An open-source Python toolkit...
```

#### If something goes wrong:
```bash
# Not installed? Try installing again
pip install socialmapper

# Wrong environment? Check you're in your venv
which python  # Should show your virtual environment path

# Still issues? List what's installed
pip list | grep social
```

---

## 🔧 Installation Troubleshooting

### General Installation Issues

```bash
# Check you're in the right environment
which python  # Should show virtual environment path
pip list | grep social  # Should show socialmapper if installed

# If you get permission errors (don't use sudo!)
# Make sure you're in a virtual environment first
source socialmapper-env/bin/activate

# If you get "command not found: python"
python3 -m venv socialmapper-env  # Use python3 instead

# If pip is not found
python -m pip install socialmapper

# To upgrade SocialMapper
pip install --upgrade socialmapper

# Clear pip cache if installation seems stuck
pip cache purge
```

### Platform-Specific Issues

```bash
# macOS: If you get SSL certificate errors
/Applications/Python\ 3.12/Install\ Certificates.command

# Windows: If "python" is not recognized
# Reinstall Python from python.org and check "Add Python to PATH"

# Linux: If missing build tools
sudo apt install build-essential python3-dev  # Ubuntu/Debian
sudo dnf groupinstall "Development Tools" python3-devel  # CentOS/RHEL
```

---

## 🎯 Your First Analysis: Libraries in Austin

Let's start with a real example: finding libraries in Austin, TX and understanding who they serve.

**Before you start:** Make sure your virtual environment is activated:
```bash
# Activate your virtual environment
source socialmapper-env/bin/activate  # macOS/Linux
# or: socialmapper-env\Scripts\activate  # Windows

# Verify you're in the right environment
which python  # Should show venv path
```

### Complete Example

Create a new Python file called `first_analysis.py`:

```python
import socialmapper

# Your first SocialMapper analysis!
results = socialmapper.run_socialmapper(
    geocode_area="Austin",
    state="TX",
    poi_type="amenity",
    poi_name="library",
    travel_time=15,  # 15-minute walking distance
    census_variables=[
        "total_population",  # Total population
        "median_household_income",  # Median household income
        "education_bachelors_plus",  # Bachelor's degree or higher
    ],
    output_dir="./my_first_analysis"
)

# Print summary
print("🎉 Analysis Complete!")
print(f"📍 Found {len(results['poi_data']['pois'])} libraries")

# Get census data for summary  
census_data = results['census_data']
if 'Total Population' in census_data.columns:
    total_pop = census_data['Total Population'].sum()
    print(f"👥 Total population analyzed: {total_pop:,}")

if 'Median Household Income' in census_data.columns:
    avg_income = census_data['Median Household Income'].mean()
    print(f"📊 Average income: ${avg_income:,.0f}")

if 'Education: Bachelor\'s Degree Or Higher' in census_data.columns:
    college_educated = census_data['Education: Bachelor\'s Degree Or Higher'].sum()
    print(f"🎓 College educated: {college_educated:,}")

print(f"📁 Output saved to: my_first_analysis")
```

### Run the Analysis

**Make sure your virtual environment is activated first:**

```bash
# Activate if not already active
source socialmapper-env/bin/activate  # macOS/Linux

# Run your analysis
python first_analysis.py
```

**Expected output:**
```
🎉 Analysis Complete!
📍 Found 10 libraries
👥 Total population analyzed: 45,231
📊 Average income: $68,450
🎓 College educated: 12,456
📁 Output saved to: my_first_analysis
```

**That's it!** You've just completed your first community demographic analysis.

---

## 📊 Understanding Your Results

Your analysis generated several outputs. Let's explore what you got:

### 1. Output Directory Structure

```
my_first_analysis/
├── maps/                 # Visual maps (PNG files)
│   ├── summary_map.png   # Main overview map
│   └── demographics_*.png
├── csv/                  # Data tables (CSV files)  
│   ├── pois.csv         # Library locations
│   ├── census_data.csv  # Demographics
│   └── summary.csv      # Key statistics
├── isochrones/          # Travel areas (GeoJSON)
└── census_data/         # Raw geographic data
```

### 2. Key Results in Python

The `results` dictionary contains everything you need:

```python
# Points of Interest (libraries)
libraries = results['pois']
print(f"First library: {libraries.iloc[0]['name']}")

# Travel time areas (15-minute walking zones)
walking_areas = results['isochrones']
print(f"Total coverage area: {walking_areas.geometry.area.sum()/1e6:.2f} sq km")

# Demographics for each area
demographics = results['census_data']
print(f"Highest income area: ${demographics['B19013_001E'].max():,}")
print(f"Most educated area: {demographics['B15003_022E'].max():,} college graduates")
```

### 3. Generated Maps

Open `my_first_analysis/maps/summary_map.png` to see:

- **Red dots**: Library locations
- **Colored areas**: 15-minute walking zones around each library
- **Color coding**: Population density or income levels
- **Legend**: Explains what colors mean

---

## 🔄 Try Different Analyses

Now that you understand the basics, try these variations:

### Example 2: Schools with Driving Access

```python
import socialmapper

# Analyze school access by car
results = socialmapper.run_socialmapper(
    query="school",
    location="Portland, OR",
    travel_times=[20],  # 20-minute drive
    travel_mode="driving",
    variables=[
        "B01003_001E",  # Population
        "B01001_003E",  # Male under 5 (children)
        "B01001_027E",  # Female under 5 (children)
    ],
    output_dir="./school_analysis"
)

# Calculate children served
total_children = results['census_data']['B01001_003E'].sum() + results['census_data']['B01001_027E'].sum()
print(f"Children under 5 near schools: {total_children:,}")
```

### Example 3: Healthcare in Rural Areas

```python
import socialmapper

# Analyze hospital access in rural Montana
results = socialmapper.run_socialmapper(
    query="hospital OR clinic",  # Multiple types
    location="Bozeman, MT",
    travel_times=[30, 60],  # 30 and 60-minute drives
    travel_mode="driving",
    variables=[
        "B01003_001E",  # Population
        "B01001_020E",  # Seniors (male 65-66)
        "B01001_044E",  # Seniors (female 65-66)
    ],
    output_dir="./healthcare_rural"
)

# Analyze senior access
seniors = results['census_data']['B01001_020E'].sum() + results['census_data']['B01001_044E'].sum()
print(f"Seniors within 1 hour of healthcare: {seniors:,}")
```

### Example 4: Custom Locations

```python
import socialmapper

# Analyze specific sites you choose
custom_sites = [
    (40.7128, -74.0060, "Manhattan Community Center"),
    (40.6892, -74.0445, "Brooklyn Health Center")
]

coordinates = socialmapper.parse_custom_coordinates(custom_sites)

results = socialmapper.run_socialmapper(
    custom_coordinates=coordinates,
    travel_times=[10, 20],
    travel_mode="walking",
    variables=["B01003_001E", "B19013_001E"],
    output_dir="./custom_analysis"
)
```

---

## 📈 Advanced Concepts

### Travel Modes

| Mode | Best For | Example Use |
|------|----------|-------------|
| `"walking"` | Local amenities, urban analysis | Libraries, corner stores |
| `"driving"` | Regional access, rural areas | Hospitals, large stores |
| `"cycling"` | Bike infrastructure | Parks, bike lanes |
| `"transit"` | Public transportation | Transit-accessible jobs |

### Census Variables

Common variables you'll use:

| Code | Description | Use For |
|------|-------------|---------|
| `"B01003_001E"` | Total population | General demographics |
| `"B19013_001E"` | Median household income | Economic analysis |
| `"B15003_022E"` | Bachelor's degree+ | Education analysis |
| `"B08301_010E"` | Public transit users | Transportation analysis |
| `"B25003_003E"` | Renter-occupied housing | Housing analysis |

### Multiple Travel Times

```python
# Compare different access levels
travel_times=[5, 10, 15, 20]  # Walking zones
travel_times=[15, 30, 45]     # Driving zones
travel_times=[20, 45]         # Transit zones
```

---

## 🗺️ Understanding the Maps

### Map Components

1. **Points of Interest** (red dots) - The facilities you searched for
2. **Isochrones** (colored areas) - Travel time boundaries
3. **Color coding** - Demographic values (population, income, etc.)
4. **Legend** - Explains color meanings

### Reading the Results

- **Darker colors** usually mean higher values
- **Larger areas** indicate better connectivity/road networks
- **Overlapping areas** show well-served communities
- **Gaps** indicate underserved areas

### Map Files

- `summary_map.png` - Main overview with all layers
- `demographics_*.png` - Individual demographic maps
- Files are print-ready and presentation-ready

---

## 🚧 Common Issues & Solutions

### Issue 1: Python Not Found or Wrong Version

**Problem**: `python: command not found` or wrong Python version

**Solution**: Install or update Python first
```bash
# Check what you have
python --version
python3 --version

# If no Python or wrong version, see Prerequisites section above
# Install Python 3.11 or 3.12 from https://www.python.org/downloads/

# On macOS/Linux, you might need to use python3:
python3 -m venv socialmapper-env
```

### Issue 2: Virtual Environment Not Activated

**Problem**: Package not found or wrong version

**Solution**: Always activate your virtual environment first
```bash
# Check if you're in a virtual environment
which python  # Should show your venv path, not system Python

# If not in venv, activate it
source socialmapper-env/bin/activate  # macOS/Linux
# or: socialmapper-env\Scripts\activate  # Windows

# Then try your command again
python first_analysis.py
```

### Issue 3: No POIs Found

**Problem**: `Found 0 libraries`

**Solutions**:
```python
# Try broader search terms
query="library OR bookstore"

# Try larger area
location="Travis County, TX"  # County instead of city

# Increase search radius
max_results=50
```

### Issue 4: Census Data Missing

**Problem**: Missing demographic values

**Solution**: Set up your Census API key (see Installation step 3)

### Issue 5: Slow Performance

**Problem**: Analysis takes too long

**Solutions**:
```python
# Reduce POIs
max_results=10

# Single travel time
travel_times=[15]

# Fewer variables
variables=["B01003_001E"]  # Just population
```

### Issue 6: Travel Mode Not Available

**Problem**: Transit mode fails in rural areas

**Solution**:
```python
# Use driving instead
travel_mode="driving"
```

### Issue 7: Permission Errors During Installation

**Problem**: Permission denied when installing packages

**Solution**: Never use `sudo pip install`! Use a virtual environment instead:
```bash
# Create and activate virtual environment first
python -m venv socialmapper-env
source socialmapper-env/bin/activate

# Then install normally
pip install socialmapper
```

---

## 🎯 Real-World Applications

### Urban Planning
- **New park locations**: Where would serve the most people?
- **Transit planning**: Where are transit gaps?
- **Equity analysis**: Do all communities have equal access?

### Public Health
- **Healthcare access**: How far do people travel to hospitals?
- **Food deserts**: Where is grocery access limited?
- **Pharmacy access**: Are medications accessible?

### Education
- **School catchments**: Which communities does each school serve?
- **Library access**: Who has access to educational resources?
- **Digital divide**: Where might internet access be limited?

### Business & Research
- **Market analysis**: Where are your customers?
- **Site selection**: Where should you open a new location?
- **Academic research**: Quantify community access patterns

---

## 💡 Best Practices

### Virtual Environment Management

**Always work in a virtual environment:**
```bash
# Starting a new session? Activate your environment first
source socialmapper-env/bin/activate  # macOS/Linux

# Working on multiple projects? Use descriptive names
python -m venv socialmapper-project1-env
python -m venv socialmapper-project2-env

# Done for the day? Deactivate (optional)
deactivate
```

### Project Organization

**Organize your SocialMapper projects:**
```
my-socialmapper-projects/
├── socialmapper-env/          # Your virtual environment
├── library-analysis/
│   ├── first_analysis.py
│   └── my_first_analysis/     # Generated outputs
├── school-access/
│   ├── school_analysis.py
│   └── school_analysis/       # Generated outputs
└── healthcare-rural/
    ├── rural_analysis.py
    └── rural_healthcare/      # Generated outputs
```

### Code Organization

**Structure your analysis scripts:**
```python
# analysis_template.py
import socialmapper

def main():
    """Your analysis function"""
    # Configuration
    QUERY = "library"
    LOCATION = "Austin, TX"
    VARIABLES = ["B01003_001E", "B19013_001E"]
    
    # Analysis
    results = socialmapper.run_socialmapper(
        query=QUERY,
        location=LOCATION,
        travel_times=[15],
        variables=VARIABLES,
        output_dir="./analysis_output"
    )
    
    # Summary
    print(f"Found {len(results['pois'])} {QUERY}s")
    print(f"Population: {results['census_data']['B01003_001E'].sum():,}")
    
    return results

if __name__ == "__main__":
    results = main()
```

---

## 📚 Next Steps

### Immediate Next Steps

**1. Set up your workspace:**
```bash
# Create a dedicated directory for your analyses
mkdir my-socialmapper-projects
cd my-socialmapper-projects

# Your virtual environment is ready to use
source socialmapper-env/bin/activate
```

**2. Try the examples above** with your own city

**3. Explore the generated maps** - understand your community

**4. Read the full guides**:
   - [User Guide](./USER_GUIDE.md) - Comprehensive examples
   - [API Reference](./API_REFERENCE.md) - All functions and parameters

### Learning Path

1. **Beginner**: Start with single POI types and walking access
2. **Intermediate**: Try multiple travel times and driving access
3. **Advanced**: Use custom coordinates and complex demographic analysis
4. **Expert**: Build custom workflows and integrate with other tools

### Development Workflow

**Daily workflow with virtual environments:**
```bash
# 1. Start your session
cd my-socialmapper-projects
source socialmapper-env/bin/activate

# 2. Work on analysis
python my_analysis.py

# 3. Explore results
open analysis_output/maps/summary_map.png

# 4. Optional: deactivate when done
deactivate
```

### Get Help

- **Documentation**: All guides available in `/docs`
- **Examples**: Working examples in `/examples` directory
- **Community**: Join discussions on GitHub
- **Issues**: Report bugs or request features

### Share Your Analysis

- **Export data**: Use CSV files for further analysis
- **Share maps**: PNG files are ready for presentations
- **Publish research**: Cite SocialMapper in academic work
- **Environment**: Share your `requirements.txt` for reproducibility

```bash
# Create requirements file for sharing
pip freeze > requirements.txt

# Others can recreate your environment with:
# pip install -r requirements.txt
```

---

## 🎉 Congratulations!

You've completed your first SocialMapper analysis! You now understand:

✅ How to set up and manage virtual environments  
✅ How to install and configure SocialMapper properly  
✅ How to run basic demographic analyses  
✅ How to interpret results and maps  
✅ Common troubleshooting approaches  
✅ Best practices for project organization  
✅ Real-world applications of community mapping  

**Ready to explore your community? Pick a POI type (schools, hospitals, parks) and a location you care about, then start mapping!** 🗺️✨

### Quick Reference Commands

```bash
# Check Python (do this first!)
python --version  # or: python3 --version

# Create virtual environment
python -m venv socialmapper-env  # or: python3 -m venv socialmapper-env

# Activate environment
source socialmapper-env/bin/activate  # macOS/Linux
# socialmapper-env\Scripts\activate  # Windows

# Install SocialMapper
pip install socialmapper

# Run analysis
python your_analysis.py

# Check what's installed
pip list

# Upgrade SocialMapper
pip install --upgrade socialmapper

# Deactivate when done
deactivate
```

---

*Need help? Check out the [User Guide](./USER_GUIDE.md) for detailed examples or the [API Reference](./API_REFERENCE.md) for comprehensive documentation.* 