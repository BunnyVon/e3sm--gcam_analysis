# E3SM Time Series Plotting Script Documentation

## Overview

**Script Name:** `e3sm_plot_time_series.py`

**Purpose:** Creates publication-quality time series plots from E3SM extracted data files with comprehensive support for annual means, seasonal averages, monthly climatologies, ensemble analysis, statistical significance testing, and percent difference comparisons.

**Key Capabilities:**
- Annual and seasonal time series
- Monthly climatology subplots
- Ensemble mean with uncertainty bands
- Statistical significance markers (t-tests)
- Percent difference plots relative to control
- Multiple scenario comparison
- LaTeX formatting support
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
7. [Output Files](#output-files)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Installation & Requirements

### Required Python Libraries

```bash
pip install pandas numpy matplotlib scipy multiprocessing
```

### Required Utility Modules

- `utility_constants` - Physical constants
- `utility_dataframes` - DataFrame operations
- `utility_functions` - General utilities  
- `utility_plots` - Plotting defaults and functions

---

## Basic Usage

### Command Line Execution

```bash
python e3sm_plot_time_series.py config.json
```

**Multiple Configuration Files:**
```bash
python e3sm_plot_time_series.py config1.json config2.json
```

### What the Script Does

1. Reads JSON configuration file(s)
2. Loads time series data files (.dat or .csv)
3. Processes data (temporal aggregation, seasonal means)
4. Creates publication-quality plots
5. Performs statistical testing (t-tests between scenarios)
6. Saves plots as PDF or PNG
7. Outputs p-value files for significance testing

---

## Complete Parameter Reference Table

### Required Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `output_files` | list/nested list | **Yes** | - | Data file paths |
| `output_labels` | list | **Yes** | - | Labels for legend |

### Core Optional Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `variables` | list or `'all'` | No | `'all'` | Variables to plot |
| `plot_type` | string | No | `'ensemble_averages'` | `'ensemble_averages'` or `'direct'` |
| `plot_directory` | string | No | `'./'` | Output directory |
| `start_year` | integer | No | `2015` | First year to plot |
| `end_year` | integer | No | `2100` | Last year to plot |
| `plot_percent_difference` | boolean | No | `false` | Plot % difference vs first file |

### Visual Customization Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `width` | float | No | `10` | Figure width (inches) |
| `height` | float | No | `8` | Figure height (inches) |
| `linewidth` | float | No | `2` | Line width |
| `use_latex` | boolean | No | `false` | Use LaTeX fonts |
| `legend_on` | boolean | No | `true` | Show legend |
| `legend_label_size` | integer | No | `14` | Legend font size |
| `x_limits` | list `[min, max]` | No | `None` | X-axis limits |
| `y_limits` | list `[min, max]` | No | `None` | Y-axis limits |
| `x_scale` | string | No | `'linear'` | X-axis scale (`'linear'` or `'log'`) |
| `y_scale` | string | No | `'linear'` | Y-axis scale (`'linear'` or `'log'`) |
| `x_label_size` | integer | No | `24` | X-axis label font size |
| `y_label_size` | integer | No | `24` | Y-axis label font size |
| `x_tick_label_size` | integer | No | `20` | X-axis tick label font size |
| `y_tick_label_size` | integer | No | `20` | Y-axis tick label font size |
| `plot_colors` | list | No | Matplotlib default | Line colors (hex codes) |
| `linestyle_tuples` | list | No | Matplotlib default | Line styles |
| `produce_png` | boolean | No | `false` | Output PNG instead of PDF |

### Labels and Names

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `plot_name` | dict | No | Auto-generated | Plot filenames per variable |
| `y_label` | dict | No | Auto-generated | Y-axis labels per variable |

### Seasonal Analysis Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `include_seasons` | dict | No | All `false` | Include seasons on main plot |
| `seasons_to_plot_separately` | dict | No | All `false` | Create separate seasonal plots |
| `monthly_aggregation_type` | string/dict | No | `'mean'` | `'mean'` or `'sum'` for monthly data |
| `std_seasons_multiplier` | float | No | `None` | Error bar multiplier for seasons |

**Season Definitions:**
- **MAM:** March-April-May (Northern Hemisphere spring)
- **JJA:** June-July-August (Northern Hemisphere summer)
- **SON:** September-October-November (Northern Hemisphere fall)
- **DJF:** December-January-February (Northern Hemisphere winter)

### Monthly Time Series Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `monthly_time_series_plot` | boolean/dict | No | `false` | Create monthly climatology subplot |
| `monthly_time_series_start_year` | integer | No | `2071` | Start year for monthly plot |
| `monthly_time_series_end_year` | integer | No | `2090` | End year for monthly plot |
| `monthly_time_series_x_limits` | list | No | `None` | X-axis limits for monthly plot |
| `monthly_time_series_y_limits` | list | No | `None` | Y-axis limits for monthly plot |
| `include_monthly_mean_across_all_sets` | boolean | No | `false` | Show ensemble mean on monthly plot |
| `std_monthly_multiplier` | float | No | `1` | Error bar multiplier for monthly data |
| `std_monthly_mean_across_all_sets_multiplier` | float | No | `1` | Error bar multiplier for monthly ensemble mean |

### Statistical Testing Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `p_value_threshold` | float | No | `0.05` | Significance threshold |
| `p_value_file` | string | No | `'p_values.dat'` | Output file for p-values |
| `p_value_file_print_only_if_below_threshold` | boolean | No | `true` | Only print significant p-values |
| `p_value_marker` | string | No | `'o'` | Marker for significant points |
| `p_value_marker_size` | integer | No | `6` | Size of significance markers |
| `include_annual_mean_across_all_sets` | boolean | No | `false` | Plot ensemble mean across all sets |
| `std_annual_multiplier` | float | No | `1` | Error bar multiplier for annual data |
| `std_annual_mean_across_all_sets_multiplier` | float | No | `1` | Error bar multiplier for annual ensemble mean |

### Advanced Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `multiplier` | float/dict | No | `1` | Scale data values |
| `areas_in_thousands_km2` | boolean | No | `true` | Convert area units to thousands km² |
| `error_bars_alpha` | float | No | `0.2` | Transparency of error bands |

---

## Plot Types Explained

### 1. Direct Plots (`plot_type: "direct"`)

**Description:** Plots each file or ensemble member as a separate line

**Configuration:**
```json
{
    "output_files": ["file1.dat", "file2.dat", "file3.dat"],
    "output_labels": ["Scenario A", "Scenario B", "Scenario C"],
    "plot_type": "direct"
}
```

**Result:** 3 distinct lines on plot

**Use When:**
- Comparing individual simulations
- Showing range of ensemble members
- Simple scenario comparison

---

### 2. Ensemble Averages (`plot_type: "ensemble_averages"`)

**Description:** Calculates ensemble mean with uncertainty bands

**Configuration:**
```json
{
    "output_files": [
        ["ctrl_1.dat", "ctrl_2.dat", "ctrl_3.dat"],
        ["scen_1.dat", "scen_2.dat", "scen_3.dat"]
    ],
    "output_labels": ["Control", "Scenario"],
    "plot_type": "ensemble_averages"
}
```

**Result:** 
- 2 lines (ensemble means)
- Shaded uncertainty bands (±1σ)
- Statistical significance markers

**Use When:**
- Presenting ensemble results
- Showing uncertainty
- Statistical comparison needed

---

### 3. Percent Difference Plots

**Description:** Shows % change relative to first file/ensemble

**Configuration:**
```json
{
    "plot_percent_difference": true
}
```

**Formula:**
```
% Difference = (Value - Reference) / Reference × 100
```

**Result:**
- Reference (first file) = 0% or not shown
- Other scenarios show % deviation

**Use When:**
- Highlighting relative changes
- Comparing against baseline
- Emphasizing magnitude of differences

---

## JSON Configuration Examples

### Example 1: Basic Multi-Scenario Plot

```json
{
    "output_files": [
        "./control_time_series.dat",
        "./full_feedback_time_series.dat",
        "./scenario_time_series.dat"
    ],
    "output_labels": ["Control", "Full feedback", "Scenario"],
    "plot_directory": "./plots/",
    "use_latex": true
}
```

**Creates:** Annual time series for all variables

---

### Example 2: Seasonal Analysis

```json
{
    "output_files": ["./control.dat", "./scenario.dat"],
    "output_labels": ["Control", "Scenario"],
    "plot_directory": "./plots/seasonal/",
    "include_seasons": {
        "ZCO2": {"MAM": false, "JJA": true, "SON": false, "DJF": true}
    },
    "seasons_to_plot_separately": {
        "ZCO2": {"MAM": true, "JJA": true, "SON": true, "DJF": true}
    }
}
```

**Creates:**
- Main plot with JJA and DJF lines
- 4 separate seasonal plots (one per season)

---

### Example 3: Ensemble with Uncertainty

```json
{
    "output_files": [
        ["control_1.dat", "control_2.dat", "control_3.dat", "control_4.dat", "control_5.dat"],
        ["scenario_1.dat", "scenario_2.dat", "scenario_3.dat", "scenario_4.dat", "scenario_5.dat"]
    ],
    "output_labels": ["Control", "Scenario"],
    "plot_type": "ensemble_averages",
    "plot_directory": "./plots/ensemble/",
    "p_value_threshold": 0.05
}
```

**Creates:**
- Ensemble mean lines
- ±1σ shaded bands
- Markers where p < 0.05

---

### Example 4: Monthly Climatology

```json
{
    "output_files": ["./control.dat"],
    "output_labels": ["Control"],
    "plot_directory": "./plots/monthly/",
    "monthly_time_series_plot": {"GPP": true, "NPP": true},
    "monthly_time_series_start_year": 2080,
    "monthly_time_series_end_year": 2090,
    "monthly_aggregation_type": {"PRECIP": "sum", "GPP": "sum"}
}
```

**Creates:**
- Annual mean plot (main)
- Monthly climatology subplot (2080-2090 average)

---

### Example 5: Percent Difference

```json
{
    "output_files": [
        "./control.dat",
        "./scenario1.dat",
        "./scenario2.dat"
    ],
    "output_labels": ["Control", "Scenario 1", "Scenario 2"],
    "plot_directory": "./plots/percent_diff/",
    "plot_percent_difference": true,
    "y_limits": {"GPP": [-10, 10], "NBP": [-50, 50]}
}
```

**Creates:**
- Control = 0% (reference)
- Scenario 1 and 2 show % deviation

---

### Example 6: Custom Styling

```json
{
    "output_files": ["./file1.dat", "./file2.dat"],
    "output_labels": ["Simulation A", "Simulation B"],
    "plot_directory": "./plots/custom/",
    "width": 12,
    "height": 6,
    "linewidth": 3,
    "use_latex": true,
    "y_label": {
        "GPP": "Gross Primary Production (Pg C year$^{-1}$)",
        "NBP": "Net Biome Production (Pg C year$^{-1}$)"
    },
    "x_limits": {"GPP": [2015, 2080]},
    "y_limits": {"GPP": [100, 150]},
    "produce_png": true
}
```

**Customizations:**
- Wider figure (12×6 inches)
- Thicker lines (3pt)
- LaTeX formatting
- Custom axis labels
- PNG output

---

## Output Files

### Plot Files

**Naming Convention:**
```
{plot_directory}/time_series_{variable}.pdf
{plot_directory}/time_series_{variable}_MAM.pdf  (seasonal)
{plot_directory}/time_series_{variable}_JJA.pdf
{plot_directory}/time_series_{variable}_SON.pdf
{plot_directory}/time_series_{variable}_DJF.pdf
{plot_directory}/time_series_{variable}_monthly.pdf
```

**Example:**
```
./plots/
├── time_series_GPP.pdf
├── time_series_GPP_MAM.pdf
├── time_series_GPP_JJA.pdf
├── time_series_GPP_SON.pdf
├── time_series_GPP_DJF.pdf
├── time_series_GPP_monthly.pdf
├── time_series_NPP.pdf
└── ...
```

### P-Value Files

**Purpose:** Records statistical significance test results

**Format:**
```
GPP in Scenario 1: 1.2345e-04
GPP in Scenario 2: 3.4567e-02
NBP in Scenario 1: 6.7890e-01
```

**Location:** Specified by `p_value_file` parameter

**Sorted:** Alphabetically after script completion

---

## Best Practices

### 1. Variable Selection

**Plot all variables:**
```json
"variables": "all"
```

**Plot specific variables:**
```json
"variables": ["GPP", "NPP", "NBP", "ER"]
```

**Recommendation:** Start with specific variables for faster testing

---

### 2. Ensemble Analysis

**Good ensemble size:** 5-10 members

**Configuration:**
```json
{
    "output_files": [
        ["ctrl_1.dat", "ctrl_2.dat", "ctrl_3.dat", "ctrl_4.dat", "ctrl_5.dat"],
        ["scen_1.dat", "scen_2.dat", "scen_3.dat", "scen_4.dat", "scen_5.dat"]
    ],
    "plot_type": "ensemble_averages",
    "p_value_threshold": 0.05
}
```

---

### 3. Seasonal Analysis Strategy

**Step 1:** Include key seasons on main plot
```json
"include_seasons": {"GPP": {"JJA": true, "DJF": true}}
```

**Step 2:** Create separate plots for detailed analysis
```json
"seasons_to_plot_separately": {
    "GPP": {"MAM": true, "JJA": true, "SON": true, "DJF": true}
}
```

---

### 4. Monthly Aggregation Type

**Use `"sum"` for:**
- Fluxes (GPP, NPP, NBP, ER)
- Precipitation (PRECIP)
- Any rate variable that should be integrated

**Use `"mean"` for:**
- State variables (temperature, CO₂ concentration)
- Fractions
- Dimensionless variables

**Example:**
```json
"monthly_aggregation_type": {
    "GPP": "sum",
    "NPP": "sum",
    "PRECIP": "sum",
    "TREFHT": "mean",
    "ZCO2": "mean"
}
```

---

### 5. File Organization

```
project/
├── data/
│   ├── control_time_series.dat
│   └── scenario_time_series.dat
├── configs/
│   ├── plot_config_direct.json
│   ├── plot_config_ensemble.json
│   └── plot_config_seasonal.json
└── plots/
    ├── direct/
    ├── ensemble/
    ├── percent_diff/
    └── seasonal/
```

---

## Troubleshooting

### Issue 1: File Not Found

**Error:**
```
FileNotFoundError: control_time_series.dat
```

**Solutions:**
```bash
# Verify file exists
ls -la control_time_series.dat

# Use absolute paths
"output_files": ["/absolute/path/to/file.dat"]
```

---

### Issue 2: Variable Not Found

**Error:**
```
KeyError: 'GPP'
```

**Solution:**
```python
# Check available variables
import pandas as pd
df = pd.read_fwf('time_series.dat')
print(df.columns)
```

---

### Issue 3: LaTeX Not Found

**Error:**
```
RuntimeError: Failed to process string with tex
```

**Solution:**
```json
"use_latex": false
```

Or install LaTeX:
```bash
# Ubuntu/Debian
sudo apt-get install texlive texlive-latex-extra

# macOS
brew install mactex
```

---

### Issue 4: Ensemble Shape Mismatch

**Error:**
```
ValueError: All arrays must be same length
```

**Cause:** Ensemble members have different time ranges

**Solution:** Ensure all files have identical Year columns

---

### Issue 5: Memory Error

**Cause:** Too many variables/files processed simultaneously

**Solutions:**
```json
// Process fewer variables
"variables": ["GPP", "NPP"]

// Or run configurations separately
python script.py config1.json
python script.py config2.json
```

---

## Advanced Features

### Per-Variable Configuration

Most parameters accept dictionaries for per-variable customization:

```json
{
    "variables": ["GPP", "NBP", "TREFHT"],
    "y_limits": {
        "GPP": [100, 180],
        "NBP": [-10, 20],
        "TREFHT": [285, 295]
    },
    "monthly_time_series_plot": {
        "GPP": true,
        "NBP": false,
        "TREFHT": true
    },
    "monthly_aggregation_type": {
        "GPP": "sum",
        "NBP": "sum",
        "TREFHT": "mean"
    }
}
```

---

### Multiple Configurations

**Single JSON with multiple plot sets:**
```json
[
    {
        "output_files": [...],
        "plot_directory": "./plots/set1/"
    },
    {
        "output_files": [...],
        "plot_directory": "./plots/set2/"
    }
]
```

**Result:** All plots generated in one execution

---

## Statistical Testing Details

### Automatic t-tests

**When plot_type = "ensemble_averages":**
- Compares each scenario ensemble to first (control) ensemble
- Tests at each time point (year or month)
- Overall test across entire time period
- Results written to p_value_file

**Markers:**
- Points with p < threshold shown with marker
- Default: circles (`'o'`)
- Color matches scenario line color

**P-value file:**
- Sorted alphabetically
- Records p-values < threshold (if `p_value_file_print_only_if_below_threshold: true`)
- Or all p-values (if `false`)

---

## References

- E3SM Documentation: [https://e3sm.org/](https://e3sm.org/)
- Matplotlib Documentation: [https://matplotlib.org/](https://matplotlib.org/)
- SciPy Stats: [https://docs.scipy.org/doc/scipy/reference/stats.html](https://docs.scipy.org/doc/scipy/reference/stats.html)
- GitHub Repository: [https://github.com/philipmyint/e3sm--gcam_analysis](https://github.com/philipmyint/e3sm--gcam_analysis)

---

## Contact

For questions or issues:
- **Philip Myint**: myint1@llnl.gov
- **Dalei Hao**: dalei.hao@pnnl.gov

---

## Version Information

**Script:** e3sm_plot_time_series.py  
**Documentation Version:** 1.0  
**Last Updated:** January 2026  
**Python Version:** 3.7+  
**Dependencies:** pandas, numpy, matplotlib, scipy

---

*This documentation provides comprehensive guidance for using the `e3sm_plot_time_series.py` script to create publication-quality time series plots from E3SM model output with ensemble analysis and statistical testing.*
