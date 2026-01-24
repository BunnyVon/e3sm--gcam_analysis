# E3SM Spatial Data Plotting Script Documentation

## Overview

**Script Name:** `e3sm_plot_spatial_data.py`

**Purpose:** Creates publication-quality spatial (map) plots from E3SM NetCDF data files with support for absolute differences, percent differences, ensemble analysis, statistical significance testing (stippling), and separate visualizations for control and scenario runs.

**Key Capabilities:**
- Global and regional spatial maps
- Absolute and percent difference plots
- Ensemble mean with statistical significance stippling
- Separate plots for individual datasets
- Support for both ELM (structured grid) and EAM (unstructured grid)
- Customizable colormaps and projections
- Statistical significance testing (t-tests)
- Parallel processing for efficiency

**Authors:** Philip Myint (myint1@llnl.gov) and Dalei Hao (dalei.hao@pnnl.gov)

**Repository:** [E3SM-GCAM Analysis Scripts](https://github.com/philipmyint/e3sm--gcam_analysis)

---

## Table of Contents

1. [Overview](#overview)
2. [Installation & Requirements](#installation--requirements)
3. [Basic Usage](#basic-usage)
4. [Complete Parameter Reference Table](#complete-parameter-reference-table)
5. [Plot Types Explained](#plot-types-explained)
6. [JSON Configuration Examples](#json-configuration-examples)
7. [ELM vs EAM Differences](#elm-vs-eam-differences)
8. [Output Files](#output-files)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Installation & Requirements

### Required Python Libraries

```bash
pip install xarray uxarray cartopy matplotlib scipy numpy pandas multiprocessing
```

### Required Utility Modules

- `utility_constants` - Physical constants
- `utility_dataframes` - DataFrame operations (t-tests)
- `utility_functions` - General utilities
- `utility_plots` - Plotting defaults and functions
- `utility_xarray` - xarray/uxarray operations

### Additional Requirements

- **For EAM plots:** Grid file (unstructured mesh, e.g., `ne30pg2_scrip_c20191218.nc`)
- **For ELM plots:** No additional files needed (structured lat/lon grid)

---

## Basic Usage

### Command Line Execution

```bash
python e3sm_plot_spatial_data.py config.json
```

**Multiple Configuration Files:**
```bash
python e3sm_plot_spatial_data.py elm_config.json eam_config.json
```

### What the Script Does

1. Reads JSON configuration file(s)
2. Loads NetCDF spatial data files
3. Calculates temporal means/differences
4. Performs statistical testing (if ensemble data)
5. Creates spatial maps with:
   - Coastlines
   - Colorbars
   - Statistical annotations
   - Stippling (optional)
6. Saves plots as PDF or PNG
7. Outputs p-value files

---

## Complete Parameter Reference Table

### Required Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `netcdf_files` | string/list/nested list | **Yes** | - | NetCDF file path(s) |
| `plot_directory` | string | No | `'./'` | Output directory for plots |

### Core Optional Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `variables` | list or `'all'` | No | `'all'` | Variables to plot |
| `plot_type` | string | No | `'absolute_difference'` | Plot type (see below) |
| `start_year` | integer | No | `2071` | First year for temporal averaging |
| `end_year` | integer | No | `2090` | Last year for temporal averaging |
| `time_calculation` | string | No | `'mean'` | `'mean'` or `'sum'` for temporal aggregation |
| `grid_file` | string | No | `None` | **Required for EAM**, grid file path |

**Plot Type Options:**
- `'absolute_difference'` - Scenario minus control (default)
- `'percent_difference'` - (Scenario - Control) / Control × 100
- `'separate_plots'` - Individual plots for control and scenario

### Visual Customization Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `width` | float | No | `10` | Figure width (inches) |
| `height` | float | No | `8` | Figure height (inches) |
| `cmap` | string | No | `'bwr'` | Colormap (blue-white-red) |
| `projection` | cartopy projection | No | `Robinson` | Map projection |
| `use_latex` | boolean | No | `false` | Use LaTeX fonts |
| `produce_png` | boolean | No | `false` | Output PNG instead of PDF |
| `title_size` | integer | No | `24` | Title font size |
| `statistics_panel_size` | integer | No | `14` | Statistics text size |

### Colorbar Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `cbar_on` | boolean | No | `true` | Show colorbar |
| `cbar_limits` | list `[min, max]` | No | `None` | Colorbar limits (auto if None) |
| `cbar_label_size` | integer | No | `20` | Colorbar tick label size |
| `cbar_x_offset` | float | No | `0.06` | Colorbar horizontal offset |

### Stippling Parameters (Statistical Significance)

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `stippling_on` | boolean | No | `false` | Enable stippling |
| `stippling_hatches` | string | No | `'xxxx'` | Hatch pattern (e.g., `'///'`, `'xxx'`) |
| `stippling_std_multiple` | float | No | `2` | Std deviation multiple for stippling |

**Stippling Behavior:**
- **Ensemble data (≥2 members per set):** Stipples where p < threshold
- **Single dataset:** Stipples where |value| > mean ± N×std

### Statistical Testing Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `p_value_threshold` | float | No | `0.05` | Significance threshold |
| `p_value_file` | string | No | `'p_values.dat'` | Output file for p-values |
| `p_value_file_print_only_if_below_threshold` | boolean | No | `true` | Only print significant p-values |

### Advanced Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `multiplier` | float/dict | No | `1` | Scale data values |
| `plot_name` | dict | No | Auto-generated | Custom plot filenames per variable |
| `title` | dict | No | Auto-generated | Custom titles per variable |

---

## Plot Types Explained

### 1. Absolute Difference (`plot_type: "absolute_difference"`)

**Description:** Shows scenario minus control in original units

**Configuration:**
```json
{
    "netcdf_files": ["control.nc", "scenario.nc"],
    "plot_type": "absolute_difference"
}
```

**Formula:**
```
Difference = Scenario - Control
```

**Use When:**
- Showing actual magnitude of changes
- Variables where absolute change meaningful
- Comparing against observations

**Example:** GPP change of +2.5 gC/m²/month

---

### 2. Percent Difference (`plot_type: "percent_difference"`)

**Description:** Shows percent change relative to control

**Configuration:**
```json
{
    "netcdf_files": ["control.nc", "scenario.nc"],
    "plot_type": "percent_difference"
}
```

**Formula:**
```
% Difference = (Scenario - Control) / |Control| × 100
```

**Use When:**
- Emphasizing relative changes
- Variables with widely varying magnitudes
- Comparing fractional impacts

**Example:** GPP change of +15% (from 16.67 to 19.17 gC/m²/month)

**Auto-limits:** Sets colorbar to [-100, 100]% if max exceeds 100%

---

### 3. Separate Plots (`plot_type: "separate_plots"`)

**Description:** Creates individual maps for control and scenario

**Configuration:**
```json
{
    "netcdf_files": ["control.nc", "scenario.nc"],
    "plot_type": "separate_plots"
}
```

**Output:**
- `spatial_GPP_set_1.pdf` (control)
- `spatial_GPP_set_2.pdf` (scenario)

**Use When:**
- Presenting absolute values
- Side-by-side comparison in publications
- Showing spatial patterns individually

---

### 4. Ensemble Analysis (Nested Lists)

**Description:** Averages across ensemble members, performs t-tests

**Configuration:**
```json
{
    "netcdf_files": [
        ["ctrl_1.nc", "scen_1.nc"],
        ["ctrl_2.nc", "scen_2.nc"],
        ["ctrl_3.nc", "scen_3.nc"]
    ],
    "plot_type": "absolute_difference",
    "stippling_on": true
}
```

**Processing:**
1. Average across ensemble members for control
2. Average across ensemble members for scenario
3. Calculate difference
4. Perform t-test at each gridcell
5. Stipple where p < 0.05

**Use When:**
- Synthetic ensemble members available
- Need statistical confidence
- Publication-quality significance testing

---

## JSON Configuration Examples

### Example 1: Basic ELM Single File Plot

```json
{
    "netcdf_files": "./control_spatial_data_elm.nc",
    "plot_directory": "./plots/elm_control/",
    "use_latex": true
}
```

**Creates:** Maps for all variables in control file

---

### Example 2: EAM Difference Plot (Requires Grid File)

```json
{
    "netcdf_files": [
        "./control_spatial_data_eam.nc",
        "./scenario_spatial_data_eam.nc"
    ],
    "plot_directory": "./plots/eam_difference/",
    "plot_type": "absolute_difference",
    "grid_file": "./eam_grid_file/ne30pg2_scrip_c20191218.nc",
    "use_latex": true
}
```

**Creates:** Difference maps (scenario - control) for EAM variables

---

### Example 3: Percent Difference

```json
{
    "netcdf_files": ["./control.nc", "./scenario.nc"],
    "plot_directory": "./plots/percent_diff/",
    "plot_type": "percent_difference",
    "cbar_limits": [-50, 50]
}
```

**Creates:** Percent change maps with colorbar from -50% to +50%

---

### Example 4: Ensemble with Stippling

```json
{
    "netcdf_files": [
        ["./ctrl_1.nc", "./scen_1.nc"],
        ["./ctrl_2.nc", "./scen_2.nc"],
        ["./ctrl_3.nc", "./scen_3.nc"],
        ["./ctrl_4.nc", "./scen_4.nc"],
        ["./ctrl_5.nc", "./scen_5.nc"]
    ],
    "plot_directory": "./plots/ensemble_diff/",
    "plot_type": "absolute_difference",
    "stippling_on": true,
    "p_value_threshold": 0.05
}
```

**Creates:** 
- Ensemble mean difference maps
- Stippling where p < 0.05
- P-value file with significance results

---

### Example 5: Separate Control and Scenario Plots

```json
{
    "netcdf_files": ["./control.nc", "./scenario.nc"],
    "plot_directory": "./plots/separate/",
    "plot_type": "separate_plots",
    "cmap": "viridis"
}
```

**Creates:**
- `spatial_GPP_set_1.pdf` (control)
- `spatial_GPP_set_2.pdf` (scenario)

---

### Example 6: Custom Colormap and Time Period

```json
{
    "netcdf_files": ["./control.nc", "./scenario.nc"],
    "plot_directory": "./plots/custom/",
    "plot_type": "absolute_difference",
    "start_year": 2080,
    "end_year": 2090,
    "cmap": "RdBu_r",
    "cbar_limits": [-5, 5],
    "width": 12,
    "height": 8
}
```

**Customizations:**
- 2080-2090 temporal average
- Reversed Red-Blue colormap
- Fixed colorbar limits
- Custom figure size

---

## ELM vs EAM Differences

### ELM (Land Model)

**Grid:** Structured latitude-longitude grid

**Configuration:**
```json
{
    "netcdf_files": "./elm_spatial_data.nc",
    "plot_directory": "./plots/elm/"
}
```

**No grid_file needed** - uses native lat/lon coordinates

**Variables:** GPP, NPP, NBP, ER, TOTECOSYSC, etc.

---

### EAM (Atmosphere Model)

**Grid:** Unstructured spectral element mesh (ne30, ne120, etc.)

**Configuration:**
```json
{
    "netcdf_files": "./eam_spatial_data.nc",
    "plot_directory": "./plots/eam/",
    "grid_file": "./ne30pg2_scrip_c20191218.nc"
}
```

**Requires grid_file** - SCRIP format grid description

**Variables:** PRECC, PRECL, TREFHT, ZCO2, etc.

**Grid Files:**
- ne30: `ne30pg2_scrip_c20191218.nc`
- ne120: `ne120pg2_scrip_c20200803.nc`

---

## Output Files

### Plot Files

**Naming Convention:**
```
{plot_directory}/spatial_{variable}.pdf
{plot_directory}/spatial_{variable}_set_1.pdf  (separate_plots)
{plot_directory}/spatial_{variable}_set_2.pdf  (separate_plots)
```

**Example:**
```
./plots/elm_control/
├── spatial_GPP.pdf
├── spatial_NPP.pdf
├── spatial_NBP.pdf
└── ...
```

### P-Value Files

**Purpose:** Records statistical significance at overall level

**Format:**
```
GPP: 1.2345e-04
NPP: 3.4567e-02
NBP: 6.7890e-01
```

**Location:** `{plot_directory}/p_values.dat`

**Note:** Spatial p-values (at each gridcell) shown via stippling, not in file

---

## Best Practices

### 1. Variable Selection

**Plot all variables:**
```json
"variables": "all"
```

**Plot specific variables:**
```json
"variables": ["GPP", "NPP", "NBP"]
```

**Recommendation:** Start with specific variables for testing

---

### 2. Temporal Averaging Period

**Standard:** 20-year average (2071-2090)
```json
"start_year": 2071,
"end_year": 2090
```

**End-of-century:** 30-year average
```json
"start_year": 2071,
"end_year": 2100
```

**Mid-century:**
```json
"start_year": 2041,
"end_year": 2060
```

---

### 3. Colormap Selection

**Diverging (for differences):**
```json
"cmap": "bwr"       // Blue-White-Red (default)
"cmap": "RdBu_r"    // Red-Blue reversed
"cmap": "PuOr"      // Purple-Orange
```

**Sequential (for absolute values):**
```json
"cmap": "viridis"   // Yellow-Green-Blue
"cmap": "plasma"    // Purple-Red-Yellow
"cmap": "YlGnBu"    // Yellow-Green-Blue
```

**For carbon fluxes (can be negative):** Use diverging
**For temperature (always positive in K):** Can use sequential or diverging

---

### 4. Colorbar Limits Strategy

**Auto-scaling (default):**
```json
"cbar_limits": null
```

**Symmetric (for differences):**
```json
"cbar_limits": [-10, 10]  // Same magnitude ±
```

**Asymmetric:**
```json
"cbar_limits": [-5, 15]  // Different ranges
```

**Recommendation:** 
1. Run once with auto-scaling
2. Check min/max in statistics panel
3. Set symmetric limits for clean visualization

---

### 5. Stippling Usage

**Enable for ensemble data:**
```json
{
    "netcdf_files": [
        ["ctrl_1.nc", "scen_1.nc"],
        ["ctrl_2.nc", "scen_2.nc"],
        ...
    ],
    "stippling_on": true,
    "p_value_threshold": 0.05
}
```

**For single file (std-based):**
```json
{
    "netcdf_files": ["./data.nc"],
    "stippling_on": true,
    "stippling_std_multiple": 2  // ±2σ from mean
}
```

---

### 6. File Organization

```
project/
├── data/
│   ├── control_spatial_data_elm.nc
│   ├── scenario_spatial_data_elm.nc
│   ├── control_spatial_data_eam.nc
│   ├── scenario_spatial_data_eam.nc
│   └── grid_files/
│       └── ne30pg2_scrip_c20191218.nc
├── configs/
│   ├── elm_plots.json
│   └── eam_plots.json
└── plots/
    ├── elm/
    │   ├── control/
    │   ├── scenario/
    │   └── difference/
    └── eam/
        ├── control/
        ├── scenario/
        └── difference/
```

---

## Troubleshooting

### Issue 1: File Not Found

**Error:**
```
FileNotFoundError: control_spatial_data_elm.nc
```

**Solutions:**
```bash
# Verify file exists
ls -la control_spatial_data_elm.nc

# Use absolute paths
"netcdf_files": "/absolute/path/to/file.nc"
```

---

### Issue 2: Grid File Missing (EAM)

**Error:**
```
TypeError: 'NoneType' object is not callable
```

**Cause:** Forgot `grid_file` parameter for EAM data

**Solution:**
```json
{
    "netcdf_files": "./eam_data.nc",
    "grid_file": "./ne30pg2_scrip_c20191218.nc"
}
```

---

### Issue 3: Variable Not Found

**Error:**
```
KeyError: 'GPP'
```

**Solution:**
```python
# Check available variables
import xarray as xr
ds = xr.open_dataset('spatial_data.nc')
print(list(ds.keys()))
```

---

### Issue 4: Memory Error (Large Files)

**Error:**
```
MemoryError: Unable to allocate array
```

**Solutions:**

1. **Process fewer variables:**
```json
"variables": ["GPP", "NPP"]  // Instead of "all"
```

2. **Process one model at a time:**
```bash
# Separate runs
python script.py elm_config.json
python script.py eam_config.json
```

3. **Reduce ensemble size:**
Use fewer synthetic members

---

### Issue 5: Cartopy/Projection Errors

**Error:**
```
AttributeError: module 'cartopy.crs' has no attribute 'Robinson'
```

**Solution:**
```bash
# Reinstall cartopy
pip install --upgrade cartopy

# Or use different projection
"projection": "PlateCarree"  // Instead of Robinson
```

---

### Issue 6: Unstructured Grid Issues (EAM)

**Error:**
```
ValueError: Grid dimensions do not match
```

**Causes:**
- Wrong grid file
- Grid file version mismatch
- Data from different resolution

**Solution:**
- Verify grid file matches simulation resolution (ne30, ne120, etc.)
- Check grid file date matches data generation date

---

## Advanced Features

### Per-Variable Configuration

Most parameters accept dictionaries for per-variable customization:

```json
{
    "variables": ["GPP", "NBP", "TREFHT"],
    "cbar_limits": {
        "GPP": [-5, 5],
        "NBP": [-2, 2],
        "TREFHT": [-3, 3]
    },
    "cmap": {
        "GPP": "RdBu_r",
        "NBP": "PuOr",
        "TREFHT": "coolwarm"
    }
}
```

---

### Custom Projections

Available Cartopy projections:
```json
"projection": "Robinson"      // Default, good for global
"projection": "PlateCarree"   // Equirectangular
"projection": "Mollweide"     // Equal-area
"projection": "Orthographic"  // Globe view
"projection": "NorthPolarStereo"  // Arctic
"projection": "SouthPolarStereo"  // Antarctic
```

**Example for Arctic focus:**
```json
{
    "projection": "NorthPolarStereo",
    "cbar_x_offset": 0.1
}
```

---

### Stippling Patterns

Available hatch patterns:
```json
"stippling_hatches": "///"    // Forward slashes
"stippling_hatches": "\\\\\\\\  // Backslashes  
"stippling_hatches": "xxx"    // X's
"stippling_hatches": "+++"    // Plus signs
"stippling_hatches": "..."    // Dots
```

---

### Time Aggregation

**Mean (default):**
```json
"time_calculation": "mean"
```
Use for: Temperature, CO₂ concentration, state variables

**Sum:**
```json
"time_calculation": "sum"
```
Use for: Fluxes (GPP, NPP, precipitation)

---

## Statistical Details

### T-Test Methodology

**For ensemble data (≥2 members per set):**

1. **At each gridcell:**
   - Control ensemble: [ctrl_1, ctrl_2, ..., ctrl_n]
   - Scenario ensemble: [scen_1, scen_2, ..., scen_n]
   - Two-sample t-test: t = (mean_scen - mean_ctrl) / SE
   - P-value calculated

2. **Stippling applied where p < threshold (default 0.05)**

3. **Overall p-value** (spatial average) written to file

**For single dataset:**
- Stipples where |value - mean| > N×std
- No p-values calculated

---

### Statistics Panel

**Displayed on each map:**
```
Max: 1.23e+01
Mean: 4.56e+00
Median: 3.89e+00
Min: -2.34e-01

Std: 2.67e+00
```

**Location:** Upper right corner

**Use:** Quick assessment of data range and variability

---

## References

- E3SM Documentation: [https://e3sm.org/](https://e3sm.org/)
- Cartopy Documentation: [https://scitools.org.uk/cartopy/](https://scitools.org.uk/cartopy/)
- xarray Documentation: [https://xarray.pydata.org/](https://xarray.pydata.org/)
- uxarray Documentation: [https://uxarray.readthedocs.io/](https://uxarray.readthedocs.io/)
- GitHub Repository: [https://github.com/philipmyint/e3sm--gcam_analysis](https://github.com/philipmyint/e3sm--gcam_analysis)

---

## Contact

For questions or issues:
- **Philip Myint**: myint1@llnl.gov
- **Dalei Hao**: dalei.hao@pnnl.gov

---

## Version Information

**Script:** e3sm_plot_spatial_data.py  
**Documentation Version:** 1.0  
**Last Updated:** January 2026  
**Python Version:** 3.7+  
**Dependencies:** xarray, uxarray, cartopy, matplotlib, scipy, numpy, pandas

---

*This documentation provides comprehensive guidance for using the `e3sm_plot_spatial_data.py` script to create publication-quality spatial maps from E3SM model output with ensemble analysis and statistical significance testing.*
