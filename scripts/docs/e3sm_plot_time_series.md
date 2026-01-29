# E3SM Time Series Plotting Script Documentation

## Overview

`e3sm_plot_time_series.py` is a Python script for creating publication-quality time series plots from E3SM (Energy Exascale Earth System Model) output data. The script supports individual file comparisons, ensemble averages with uncertainty bands, percent difference calculations, seasonal analysis, and statistical significance testing.

This script is part of the [e3sm--gcam_analysis](https://github.com/philipmyint/e3sm--gcam_analysis) repository, which provides tools for analyzing coupled E3SM-GCAM simulation outputs.

---

## Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Quick Start](#quick-start)
4. [Input File Format](#input-file-format)
5. [Configuration Parameters](#configuration-parameters)
6. [Plot Types](#plot-types)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)
9. [References](#references)

---

## Features

- **Multiple Plot Types:** Individual time series, ensemble averages with uncertainty bands
- **Percent Difference Calculations:** Compare scenarios relative to a control/reference
- **Seasonal Analysis:** Include seasonal averages (MAM, JJA, SON, DJF) on annual plots or as separate plots
- **Monthly Time Series:** Generate monthly climatology plots
- **Statistical Testing:** Automatic t-tests with p-value markers for significance
- **Flexible Configuration:** Per-variable customization of all plot options
- **Parallel Processing:** Multi-core support for faster plot generation
- **Publication Quality:** LaTeX support, customizable colors, line styles, and dimensions

---

## Requirements

### Python Dependencies

```
matplotlib
numpy
pandas
scipy
```

### Additional Files

The script requires these utility modules from the repository:
- `utility_constants.py`
- `utility_dataframes.py`
- `utility_functions.py`
- `utility_plots.py`

---

## Quick Start

### Basic Usage

```bash
python e3sm_plot_time_series.py path/to/config.json
```

### Multiple Configuration Files

```bash
python e3sm_plot_time_series.py config1.json config2.json config3.json
```

### Minimal Configuration Example

```json
[
    {
        "output_files": ["control.dat", "experiment.dat"],
        "output_labels": ["Control", "Experiment"],
        "plot_directory": "./plots/"
    }
]
```

---

## Input File Format

### Data File Structure

The script expects data files (`.dat` or similar) with the following structure:

| Year | Month | Variable1 (units) | Variable2 (units) | ... |
|------|-------|-------------------|-------------------|-----|
| 2015 | 1     | 410.5             | 0.025             | ... |
| 2015 | 2     | 411.2             | 0.031             | ... |
| ...  | ...   | ...               | ...               | ... |

- **Year:** Integer year values
- **Month:** Integer month values (1-12), optional for annual-only data
- **Variables:** Numeric columns with optional units in parentheses in the header

### JSON Configuration Structure

The JSON configuration file contains an array of configuration blocks, where each block specifies options for a set of plots:

```json
[
    {
        "output_files": [...],
        "output_labels": [...],
        "plot_directory": "...",
        ...other options...
    },
    {
        ...another configuration block...
    }
]
```

---

## Configuration Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `output_files` | string, list, or nested list | Path(s) to input data file(s). See [Output Files Format](#output-files-format) for details. |

### Data Selection Parameters

| Parameter | Type | Required | Default | Possible Values | Description |
|-----------|------|----------|---------|-----------------|-------------|
| `output_files` | string/list/nested list | **Yes** | - | Valid file path(s) | Input data file(s) to plot |
| `output_labels` | list | No | File names | List of strings | Labels for each file/file set in the legend |
| `variables` | list or string | No | All variables | List of variable names, single string, or `"all"` | Variables to plot |
| `start_year` | integer | No | `2015` | Any year | First year to include in plots |
| `end_year` | integer | No | `2100` | Any year | Last year to include in plots |
| `multiplier` | number | No | `1` | Any number | Multiplier applied to data values (for unit conversion) |

### Plot Type Parameters

| Parameter | Type | Required | Default | Possible Values | Description |
|-----------|------|----------|---------|-----------------|-------------|
| `plot_type` | string | No | `"ensemble"` | `"ensemble"`, `"individual"` | Type of plot when using nested output_files |
| `plot_percent_difference` | boolean | No | `false` | `true`, `false` | Calculate percent difference relative to first file/set |

### Output Parameters

| Parameter | Type | Required | Default | Possible Values | Description |
|-----------|------|----------|---------|-----------------|-------------|
| `plot_directory` | string | No | `"./"` | Valid directory path | Directory for output plots |
| `plot_name` | string or dict | No | `"time_series_[variable]"` | Filename (without extension) | Name of output plot file |
| `produce_png` | boolean | No | `false` | `true`, `false` | Output PNG instead of PDF |

### Axis Parameters

| Parameter | Type | Required | Default | Possible Values | Description |
|-----------|------|----------|---------|-----------------|-------------|
| `x_limits` | list or dict | No | Auto | `[min, max]` | X-axis limits |
| `y_limits` | list or dict | No | Auto | `[min, max]` | Y-axis limits |
| `x_scale` | string or dict | No | `"linear"` | `"linear"`, `"log"` | X-axis scale |
| `y_scale` | string or dict | No | `"linear"` | `"linear"`, `"log"` | Y-axis scale |
| `y_label` | string or dict | No | Column header | Any string (supports LaTeX) | Y-axis label |

### Figure Dimension Parameters

| Parameter | Type | Required | Default | Possible Values | Description |
|-----------|------|----------|---------|-----------------|-------------|
| `width` | number | No | `10` | Positive number | Figure width in inches |
| `height` | number | No | `8` | Positive number | Figure height in inches |

### Font Size Parameters

| Parameter | Type | Required | Default | Possible Values | Description |
|-----------|------|----------|---------|-----------------|-------------|
| `x_label_size` | number | No | `24` | Positive number | X-axis label font size |
| `y_label_size` | number | No | `24` | Positive number | Y-axis label font size |
| `x_tick_label_size` | number | No | `20` | Positive number | X-axis tick label font size |
| `y_tick_label_size` | number | No | `20` | Positive number | Y-axis tick label font size |
| `legend_label_size` | number | No | `14` | Positive number | Legend text font size |

### Line Style Parameters

| Parameter | Type | Required | Default | Possible Values | Description |
|-----------|------|----------|---------|-----------------|-------------|
| `plot_colors` | list | No | Tableau palette | List of color codes | Colors for each line |
| `linewidth` | number | No | `2` | Positive number | Line thickness |
| `linestyle_tuples` | list | No | Predefined styles | List of linestyle tuples | Line dash patterns |
| `legend_on` | boolean | No | `true` | `true`, `false` | Show/hide legend |

### Error Bar Parameters

| Parameter | Type | Required | Default | Possible Values | Description |
|-----------|------|----------|---------|-----------------|-------------|
| `std_annual_multiplier` | number or null | No | `1` | Number or `null` | Multiplier on std dev for annual error bands (null = no bands) |
| `std_monthly_multiplier` | number or null | No | `1` | Number or `null` | Multiplier on std dev for monthly error bands |
| `std_seasons_multiplier` | number or null | No | `null` | Number or `null` | Multiplier on std dev for seasonal error bands |
| `std_annual_mean_across_all_sets_multiplier` | number or null | No | `1` | Number or `null` | Std dev multiplier for mean across all sets (annual) |
| `std_monthly_mean_across_all_sets_multiplier` | number or null | No | `1` | Number or `null` | Std dev multiplier for mean across all sets (monthly) |
| `error_bars_alpha` | number | No | `0.2` | 0-1 | Opacity of error band fill |

### Statistical Testing Parameters

| Parameter | Type | Required | Default | Possible Values | Description |
|-----------|------|----------|---------|-----------------|-------------|
| `p_value_threshold` | number | No | `0.05` | 0-1 | Significance threshold for t-tests |
| `p_value_marker` | string | No | `"o"` | Matplotlib marker codes | Marker for significant points |
| `p_value_marker_size` | number | No | `6` | Positive number | Size of significance markers |
| `p_value_file` | string | No | `"p_values.dat"` | Filename | File to store p-value results |
| `p_value_file_print_only_if_below_threshold` | boolean | No | `true` | `true`, `false` | Only write significant p-values to file |

### Seasonal Analysis Parameters

| Parameter | Type | Required | Default | Possible Values | Description |
|-----------|------|----------|---------|-----------------|-------------|
| `include_seasons` | dict | No | All `false` | `{"MAM": bool, "JJA": bool, "SON": bool, "DJF": bool}` | Add seasonal lines to annual plot |
| `seasons_to_plot_separately` | dict | No | All `false` | `{"MAM": bool, "JJA": bool, "SON": bool, "DJF": bool}` | Create separate seasonal plot |

### Monthly Time Series Parameters

| Parameter | Type | Required | Default | Possible Values | Description |
|-----------|------|----------|---------|-----------------|-------------|
| `monthly_time_series_plot` | boolean or dict | No | `false` | `true`, `false` | Generate monthly climatology plot |
| `monthly_time_series_start_year` | integer | No | `2071` | Any year | Start year for monthly averaging |
| `monthly_time_series_end_year` | integer | No | `2090` | Any year | End year for monthly averaging |
| `monthly_time_series_x_limits` | list | No | Auto | `[min, max]` | X-axis limits for monthly plot |
| `monthly_time_series_y_limits` | list | No | Auto | `[min, max]` | Y-axis limits for monthly plot |
| `monthly_aggregation_type` | string or dict | No | `"mean"` | `"mean"`, `"sum"` | How to aggregate monthly data to annual |

### Ensemble Analysis Parameters

| Parameter | Type | Required | Default | Possible Values | Description |
|-----------|------|----------|---------|-----------------|-------------|
| `include_annual_mean_across_all_sets` | boolean | No | `false` | `true`, `false` | Add mean line across all file sets |
| `include_monthly_mean_across_all_sets` | boolean | No | `false` | `true`, `false` | Add mean line across all file sets (monthly) |
| `notify_output_files_transposed` | boolean | No | `false` | `true`, `false` | Print message when output_files are transposed |

### Rendering Parameters

| Parameter | Type | Required | Default | Possible Values | Description |
|-----------|------|----------|---------|-----------------|-------------|
| `use_latex` | boolean | No | `false` | `true`, `false` | Use LaTeX for text rendering |
| `areas_in_thousands_km2` | boolean | No | `true` | `true`, `false` | Convert area variables to thousands km² |

---

## Output Files Format

The `output_files` parameter supports multiple formats depending on your analysis needs:

### Format 1: Single File

```json
"output_files": "path/to/file.dat"
```

### Format 2: Multiple Individual Files

```json
"output_files": ["control.dat", "experiment1.dat", "experiment2.dat"]
```
Each file is plotted as a separate line.

### Format 3: Ensemble Files (Organized by File Set - Recommended)

```json
"output_files": [
    ["control.dat", "control_2.dat", "control_3.dat"],
    ["experiment.dat", "experiment_2.dat", "experiment_3.dat"]
],
"output_labels": ["Control", "Experiment"]
```
Each inner list contains all ensemble members for one scenario. The script automatically detects this format and calculates ensemble statistics.

### Format 4: Ensemble Files (Organized by Ensemble Member - Alternative)

```json
"output_files": [
    ["control.dat", "experiment.dat"],
    ["control_2.dat", "experiment_2.dat"],
    ["control_3.dat", "experiment_3.dat"]
],
"output_labels": ["Control", "Experiment"]
```
Each inner list is one ensemble member. The script automatically transposes this to the internal format using `transpose_scenarios_if_needed()`.

**Note:** The `output_labels` parameter helps the script detect which format you're using. Format 3 (organized by file set) is recommended as it's more intuitive.

---

## Plot Types

### Individual Plots (`plot_type: "individual"`)

Each output file is plotted as a separate line. Use this when:
- Comparing individual simulation runs directly
- Not computing ensemble statistics
- Working with non-ensemble data

### Ensemble Plots (`plot_type: "ensemble"`)

Files are grouped into sets (ensembles), and the mean ± standard deviation is calculated for each set. Use this when:
- Comparing ensemble averages between scenarios
- Quantifying uncertainty within scenarios
- Performing statistical significance testing between scenario sets

---

## Examples

The following examples correspond to the configuration blocks in the provided JSON file.

---

### Example 1: Individual Plots with Multiple Scenarios

**Purpose:** Compare multiple individual simulation outputs directly

```json
{
    "output_files": [
        "./../2025_DiVittorio_et_al_e3sm/control_time_series.dat", 
        "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series.dat",
        "./../2025_DiVittorio_et_al_e3sm/ag_scaling_time_series.dat", 
        "./../2025_DiVittorio_et_al_e3sm/carbon_scaling_time_series.dat"
    ],
    "output_labels": ["Control", "Full feedback", "Ag scaling", "Carbon scaling"],
    "plot_directory": "./../2025_DiVittorio_et_al_e3sm/time_series_plots/individual",
    "y_label": {"ZCO2": "CO$_2$ concentration (ppm)", "SFCO2": "CO$_2$ surface flux (Pg C/month)"},
    "monthly_aggregation_type": {"PRECIP": "sum", "NPP": "sum"},
    "x_limits": {"ZCO2": [2015, 2100]},
    "y_limits": {"ZCO2": [400, 700]},
    "use_latex": true,
    "include_seasons": {"ZCO2": {"MAM": false, "JJA": true, "SON": false, "DJF": true}},
    "seasons_to_plot_separately": {"ZCO2": {"MAM": true, "JJA": true, "SON": true, "DJF": true}},
    "monthly_time_series_plot": {"ZCO2": true},
    "monthly_time_series_end_year": 2100
}
```

**Key Features:**
- Four individual scenarios plotted on the same axes
- Custom y-axis labels for specific variables (ZCO2, SFCO2)
- Monthly aggregation type specified per variable (sum for PRECIP and NPP)
- Seasonal overlays on annual plot for ZCO2 (JJA and DJF only)
- Separate seasonal plot for ZCO2 with all four seasons
- Monthly climatology plot enabled for ZCO2
- LaTeX rendering enabled for publication quality

**Result:**
- Annual time series plot with all four scenarios
- Seasonal plot showing MAM, JJA, SON, DJF averages
- Monthly climatology plot showing average monthly cycle

---

### Example 2: Regional Comparison

**Purpose:** Compare global vs. regional (Amazon) data for the same scenario

```json
{
    "output_files": [
        "./../2025_DiVittorio_et_al_e3sm/control_time_series.dat", 
        "./../2025_DiVittorio_et_al_e3sm/control_time_series_amazon.dat"
    ],
    "output_labels": ["Control (Global)", "Control (Amazon)"],
    "plot_directory": "./../2025_DiVittorio_et_al_e3sm/time_series_plots/individual_amazon",
    "y_label": {"ZCO2": "CO$_2$ concentration (ppm)", "SFCO2": "CO$_2$ surface flux (Pg C/month)"},
    "monthly_aggregation_type": {"PRECIP": "sum", "NPP": "sum"},
    "x_limits": {"ZCO2": [2015, 2100]},
    "y_limits": {"ZCO2": [400, 700]},
    "use_latex": true,
    "include_seasons": {"ZCO2": {"MAM": false, "JJA": true, "SON": false, "DJF": true}},
    "seasons_to_plot_separately": {"ZCO2": {"MAM": true, "JJA": true, "SON": true, "DJF": true}},
    "monthly_time_series_plot": {"ZCO2": true},
    "monthly_time_series_end_year": 2100
}
```

**Key Features:**
- Direct comparison between global and regional averages
- Same variable from different spatial domains
- Useful for understanding regional contributions

---

### Example 3: Percent Difference Plots

**Purpose:** Show relative changes compared to control scenario

```json
{
    "output_files": [
        "./../2025_DiVittorio_et_al_e3sm/control_time_series.dat", 
        "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series.dat",
        "./../2025_DiVittorio_et_al_e3sm/ag_scaling_time_series.dat", 
        "./../2025_DiVittorio_et_al_e3sm/carbon_scaling_time_series.dat"
    ],
    "output_labels": ["Control", "Full feedback", "Ag scaling", "Carbon scaling"],
    "plot_directory": "./../2025_DiVittorio_et_al_e3sm/time_series_plots/individual_percent_difference",
    "y_label": {"ZCO2": "CO$_2$ concentration (ppm)", "SFCO2": "CO$_2$ surface flux (Pg C/month)"},
    "monthly_aggregation_type": {"PRECIP": "sum", "NPP": "sum"},
    "x_limits": {"ZCO2": [2015, 2100]},
    "y_limits": {"ZCO2": [-10, 10]},
    "use_latex": true,
    "plot_percent_difference": true,
    "include_seasons": {"ZCO2": {"MAM": false, "JJA": true, "SON": false, "DJF": true}},
    "seasons_to_plot_separately": {"ZCO2": {"MAM": true, "JJA": true, "SON": true, "DJF": true}},
    "monthly_time_series_plot": {"ZCO2": true},
    "monthly_time_series_end_year": 2100
}
```

**Key Features:**
- `plot_percent_difference: true` enables relative change calculation
- First file (Control) serves as the reference baseline
- Y-axis automatically labeled as "% difference"
- Control line is not plotted (would be zero)
- Symmetric y-limits centered on zero

**Result:**
- Each non-control scenario shows percent difference from control
- Positive values indicate increase relative to control
- Negative values indicate decrease relative to control

---

### Example 4: Ensemble Plots

**Purpose:** Compare ensemble averages with uncertainty bands

```json
{
    "output_files": [
        ["./../2025_DiVittorio_et_al_e3sm/control_time_series.dat", 
         "./../2025_DiVittorio_et_al_e3sm/control_time_series_2.dat",
         "./../2025_DiVittorio_et_al_e3sm/control_time_series_3.dat", 
         "./../2025_DiVittorio_et_al_e3sm/control_time_series_4.dat",
         "./../2025_DiVittorio_et_al_e3sm/control_time_series_5.dat"],
        ["./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series.dat", 
         "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_2.dat",
         "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_3.dat", 
         "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_4.dat",
         "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_5.dat"],
        ["./../2025_DiVittorio_et_al_e3sm/ag_scaling_time_series.dat", 
         "./../2025_DiVittorio_et_al_e3sm/ag_scaling_time_series_2.dat",
         "./../2025_DiVittorio_et_al_e3sm/ag_scaling_time_series_3.dat", 
         "./../2025_DiVittorio_et_al_e3sm/ag_scaling_time_series_4.dat",
         "./../2025_DiVittorio_et_al_e3sm/ag_scaling_time_series_5.dat"],
        ["./../2025_DiVittorio_et_al_e3sm/carbon_scaling_time_series.dat", 
         "./../2025_DiVittorio_et_al_e3sm/carbon_scaling_time_series_2.dat",
         "./../2025_DiVittorio_et_al_e3sm/carbon_scaling_time_series_3.dat", 
         "./../2025_DiVittorio_et_al_e3sm/carbon_scaling_time_series_4.dat",
         "./../2025_DiVittorio_et_al_e3sm/carbon_scaling_time_series_5.dat"]
    ],
    "output_labels": ["Control", "Full feedback", "Ag scaling", "Carbon scaling"],
    "plot_directory": "./../2025_DiVittorio_et_al_e3sm/time_series_plots/ensemble",
    "y_label": {"ZCO2": "CO$_2$ concentration (ppm)", "SFCO2": "CO$_2$ surface flux (Pg C/month)"},
    "monthly_aggregation_type": {"PRECIP": "sum", "NPP": "sum"},
    "x_limits": {"ZCO2": [2015, 2100]},
    "y_limits": {"ZCO2": [400, 700]},
    "use_latex": true,
    "include_seasons": {"ZCO2": {"MAM": false, "JJA": true, "SON": false, "DJF": true}},
    "seasons_to_plot_separately": {"ZCO2": {"MAM": true, "JJA": true, "SON": true, "DJF": true}},
    "monthly_time_series_plot": {"ZCO2": true},
    "monthly_time_series_end_year": 2100
}
```

**Key Features:**
- Four scenario sets, each with 5 ensemble members
- `output_files` organized by file set (recommended format)
- Each inner list contains all ensemble members for one scenario
- Script calculates mean and standard deviation across ensemble members
- Shaded uncertainty bands show ±1 standard deviation by default
- Statistical t-tests performed between Control and other scenarios

**Result:**
- Four lines representing ensemble means
- Shaded regions showing uncertainty within each ensemble
- Markers indicating statistically significant differences from control

---

### Example 5: Ensemble Percent Difference

**Purpose:** Show ensemble-averaged percent differences with uncertainty

```json
{
    "output_files": [
        ["./../2025_DiVittorio_et_al_e3sm/control_time_series.dat", 
         "./../2025_DiVittorio_et_al_e3sm/control_time_series_2.dat",
         "./../2025_DiVittorio_et_al_e3sm/control_time_series_3.dat", 
         "./../2025_DiVittorio_et_al_e3sm/control_time_series_4.dat",
         "./../2025_DiVittorio_et_al_e3sm/control_time_series_5.dat"],
        ["./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series.dat", 
         "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_2.dat",
         "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_3.dat", 
         "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_4.dat",
         "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_5.dat"],
        ...
    ],
    "output_labels": ["Control", "Full feedback", "Ag scaling", "Carbon scaling"],
    "plot_directory": "./../2025_DiVittorio_et_al_e3sm/time_series_plots/ensemble_percent_difference",
    "y_limits": {"ZCO2": [-10, 10]},
    "use_latex": true,
    "plot_percent_difference": true,
    ...
}
```

**Key Features:**
- Combines ensemble analysis with percent difference calculation
- Each scenario's ensemble mean is compared to Control ensemble mean
- Uncertainty bands reflect ensemble spread of the percent differences
- Useful for quantifying both the magnitude and uncertainty of changes

---

### Example 6: Individual Lines from Ensemble Data

**Purpose:** Plot all ensemble members as individual lines (not grouped)

```json
{
    "output_files": [
        ["./../2025_DiVittorio_et_al_e3sm/control_time_series.dat", 
         "./../2025_DiVittorio_et_al_e3sm/control_time_series_2.dat",
         ...],
        ["./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series.dat", 
         "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_2.dat",
         ...],
        ...
    ],
    "output_labels": ["Control", "Full feedback", "Ag scaling", "Carbon scaling"],
    "plot_type": "individual",
    "plot_directory": "./../2025_DiVittorio_et_al_e3sm/time_series_plots/individual_not_grouped_into_ensemble",
    ...
}
```

**Key Features:**
- Uses nested `output_files` but sets `plot_type: "individual"`
- Each file is plotted as a separate line (not ensemble-averaged)
- Labels are repeated for each ensemble member with matching colors
- Useful for visualizing ensemble spread without aggregation

**Result:**
- 20 individual lines (4 scenarios × 5 members)
- Same color for all members of each scenario
- No uncertainty bands (all data shown explicitly)

---

### Example 7: Basic Surface Data Comparison

**Purpose:** Simple two-scenario comparison with minimal options

```json
{
    "output_files": [
        "./../2025_DiVittorio_et_al_e3sm/control_time_series_surfdata_iESM_dyn_20240730.dat", 
        "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_surfdata_iESM_dyn_20240730.dat"
    ],
    "output_labels": ["Control", "Full feedback"],
    "plot_directory": "./../2025_DiVittorio_et_al_e3sm/time_series_plots/surfdata/",
    "use_latex": true
}
```

**Key Features:**
- Minimal configuration using defaults for most options
- Plots all variables found in the data files
- Default year range (2015-2100)
- Auto-generated plot names and y-axis labels

---

### Example 8: Regional Surface Data

**Purpose:** Compare global and Amazon regional surface data

```json
{
    "output_files": [
        "./../2025_DiVittorio_et_al_e3sm/control_time_series_surfdata_iESM_dyn_20240730.dat", 
        "./../2025_DiVittorio_et_al_e3sm/control_time_series_surfdata_iESM_dyn_20240730_amazon.dat"
    ],
    "output_labels": ["Control (Global)", "Control (Amazon)"],
    "plot_directory": "./../2025_DiVittorio_et_al_e3sm/time_series_plots/surfdata_amazon/",
    "use_latex": true
}
```

---

### Example 9: Version Comparison

**Purpose:** Compare outputs from different data versions/dates

```json
{
    "output_files": [
        "./../2025_DiVittorio_et_al_e3sm/control_time_series_surfdata_iESM_dyn_20240730.dat", 
        "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_surfdata_iESM_dyn_20240730.dat",
        "./../2025_DiVittorio_et_al_e3sm/control_time_series_surfdata_iESM_dyn_20240820.dat", 
        "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_surfdata_iESM_dyn_20240820.dat"
    ],
    "output_labels": ["Control (20240730)", "Full feedback (20240730)", "Control (20240820)", "Full feedback (20240820)"],
    "plot_directory": "./../2025_DiVittorio_et_al_e3sm/time_series_plots/surfdata_0730_vs_0820/",
    "use_latex": true
}
```

**Key Features:**
- Compares four scenarios: two scenarios × two versions
- Useful for quality control and version tracking
- Labels include version date identifiers

---

### Example 10: Surface Data Ensemble

**Purpose:** Ensemble analysis of surface data

```json
{
    "output_files": [
        ["./../2025_DiVittorio_et_al_e3sm/control_time_series_surfdata_iESM_dyn_20240730.dat", 
         "./../2025_DiVittorio_et_al_e3sm/control_time_series_surfdata_iESM_dyn_20240730_2.dat",
         "./../2025_DiVittorio_et_al_e3sm/control_time_series_surfdata_iESM_dyn_20240730_3.dat", 
         "./../2025_DiVittorio_et_al_e3sm/control_time_series_surfdata_iESM_dyn_20240730_4.dat",
         "./../2025_DiVittorio_et_al_e3sm/control_time_series_surfdata_iESM_dyn_20240730_5.dat"],
        ["./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_surfdata_iESM_dyn_20240730.dat", 
         "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_surfdata_iESM_dyn_20240730_2.dat",
         "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_surfdata_iESM_dyn_20240730_3.dat", 
         "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_surfdata_iESM_dyn_20240730_4.dat",
         "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_surfdata_iESM_dyn_20240730_5.dat"]
    ],
    "output_labels": ["Control", "Full feedback"],
    "plot_directory": "./../2025_DiVittorio_et_al_e3sm/time_series_plots/surfdata_ensemble/",
    "use_latex": true
}
```

**Key Features:**
- Two scenario ensembles with 5 members each
- Organized by file set (recommended format)
- Automatic ensemble statistics and t-tests

---

### Example 11: Surface Data Ensemble Percent Difference

**Purpose:** Ensemble percent difference for surface data

```json
{
    "output_files": [
        ["./../2025_DiVittorio_et_al_e3sm/control_time_series_surfdata_iESM_dyn_20240730.dat", 
         "./../2025_DiVittorio_et_al_e3sm/control_time_series_surfdata_iESM_dyn_20240730_2.dat",
         ...],
        ["./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_surfdata_iESM_dyn_20240730.dat", 
         "./../2025_DiVittorio_et_al_e3sm/full_feedback_time_series_surfdata_iESM_dyn_20240730_2.dat",
         ...]
    ],
    "output_labels": ["Control", "Full feedback"],
    "plot_directory": "./../2025_DiVittorio_et_al_e3sm/time_series_plots/surfdata_ensemble_percent_difference/",
    "plot_percent_difference": true,
    "use_latex": true
}
```

**Key Features:**
- Combines ensemble analysis with percent difference calculation
- Shows relative change of Full feedback compared to Control
- Includes uncertainty bands on percent differences

---

## Per-Variable Configuration

Most parameters can be specified either globally or per-variable using dictionaries:

### Global Setting (applies to all variables)

```json
{
    "y_limits": [0, 100]
}
```

### Per-Variable Setting

```json
{
    "y_limits": {
        "ZCO2": [400, 700],
        "SFCO2": [-2, 2],
        "PRECIP": [0, 500]
    }
}
```

Variables not specified in the dictionary will use default values.

---

## Seasonal Analysis

### Seasons Abbreviations

| Season | Months | Description |
|--------|--------|-------------|
| MAM | March, April, May | Northern Hemisphere Spring |
| JJA | June, July, August | Northern Hemisphere Summer |
| SON | September, October, November | Northern Hemisphere Fall |
| DJF | December, January, February | Northern Hemisphere Winter |

### Including Seasons on Annual Plot

```json
"include_seasons": {
    "ZCO2": {"MAM": false, "JJA": true, "SON": false, "DJF": true}
}
```

This adds JJA and DJF seasonal averages as additional lines on the main annual time series plot.

### Separate Seasonal Plot

```json
"seasons_to_plot_separately": {
    "ZCO2": {"MAM": true, "JJA": true, "SON": true, "DJF": true}
}
```

This creates a separate plot file (`*_seasons.pdf`) showing only the seasonal averages.

---

## Statistical Testing

The script automatically performs t-tests comparing the first file/set (control) against all other files/sets:

1. **Overall t-test:** Compares entire time series distributions
2. **Time-point t-tests:** Tests significance at each year/month

Results are:
- Printed to console during execution
- Saved to `p_values.dat` (or custom filename)
- Plotted as markers on time series where p < threshold

---

## Troubleshooting

### Common Issues

**Issue 1: LaTeX Errors**
```
RuntimeError: Failed to process string with tex
```

**Solution:**
- Set `"use_latex": false` or install a LaTeX distribution
- Escape special characters in labels

**Issue 2: File Not Found**
```
FileNotFoundError: [Errno 2] No such file or directory
```

**Solution:**
- Check file paths are correct
- Use absolute paths or correct relative paths

**Issue 3: Missing Variables**
```
KeyError: 'VariableName'
```

**Solution:**
- Verify variable names match column headers in data files
- Check for typos in variable names

**Issue 4: Ensemble Structure Mismatch**
```
ValueError: All inner lists must have same length
```

**Solution:**
- Ensure all ensemble sets have the same number of members
- Check for missing or extra files

---

## Best Practices

1. **Organize Output Files by Set:** Use Format 3 (organized by file set) for cleaner, more intuitive configuration

2. **Use Per-Variable Settings:** Customize axis limits and labels for each variable

3. **Enable LaTeX for Publications:** Set `use_latex: true` for professional typography

4. **Document p-value Results:** Use `p_value_file` to keep records of statistical tests

5. **Use Meaningful Labels:** Clear `output_labels` make plots self-explanatory

---

## References

- DiVittorio et al. (2025). "E3SM-GCAM coupling methodology and applications." *Journal of Advances in Modeling Earth Systems*. [DOI: 10.1029/2024MS004806](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2024MS004806)
- GitHub Repository: [https://github.com/philipmyint/e3sm--gcam_analysis](https://github.com/philipmyint/e3sm--gcam_analysis)
- E3SM Project: [https://e3sm.org/](https://e3sm.org/)
- Matplotlib Documentation: [https://matplotlib.org/](https://matplotlib.org/)

---

## Contact

For questions or issues:
- **Philip Myint**: [email protected]
- **Dalei Hao**: [email protected]

---

*Documentation generated for e3sm_plot_time_series.py*
