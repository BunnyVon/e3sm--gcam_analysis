# E3SM Spatial Data Plotting Script Documentation

## Overview

**Script Name:** `e3sm_plot_spatial_data.py`

**Purpose:** Creates publication-quality spatial (map) plots from E3SM NetCDF data files with support for absolute differences, percent differences, ensemble analysis, statistical significance testing (stippling), and separate visualizations for different scenarios.

**Key Capabilities:**
- Global and regional spatial maps
- Absolute and percent difference plots
- Ensemble mean with statistical significance stippling
- Separate plots for individual scenarios or ensemble members
- Support for both ELM (structured grid) and EAM (unstructured grid)
- Customizable colormaps and projections
- Statistical significance testing (aggregated and per-gridcell)
- Parallel processing for efficiency
- Flexible ensemble file organization

**Authors:** Philip Myint (myint1@llnl.gov) and Dalei Hao (dalei.hao@pnnl.gov)

**Repository:** [E3SM-GCAM Analysis Scripts](https://github.com/philipmyint/e3sm--gcam_analysis)

---

## Table of Contents

1. [Overview](#overview)
2. [Installation & Requirements](#installation--requirements)
3. [Basic Usage](#basic-usage)
4. [Complete Parameter Reference](#complete-parameter-reference)
5. [Plot Types Explained](#plot-types-explained)
6. [Statistical Testing Explained](#statistical-testing-explained)
7. [Ensemble File Organization](#ensemble-file-organization)
8. [ELM vs EAM Differences](#elm-vs-eam-differences)
9. [Comprehensive JSON Examples](#comprehensive-json-examples)
10. [Output Files](#output-files)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Installation & Requirements

### Required Python Libraries

```bash
pip install xarray uxarray cartopy matplotlib scipy numpy pandas multiprocessing
```

### Required Utility Modules

- `utility_constants` - Physical constants
- `utility_dataframes` - DataFrame operations (t-tests)
- `utility_functions` - General utilities (includes `transpose_scenarios_if_needed()`)
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
2. Loads NetCDF spatial data files (from `e3sm_extract_spatial_data_h0.py`)
3. Calculates temporal means/differences over specified years
4. Performs statistical testing (aggregated and per-gridcell)
5. Creates spatial maps with:
   - Coastlines
   - Colorbars
   - Statistical annotations (min, mean, median, max, std)
   - Stippling for significance (ELM only)
6. Saves plots as PDF or PNG
7. Outputs p-value files

---

## Complete Parameter Reference

### Required Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `netcdf_files` | string/list/nested list | **Yes** | - | NetCDF file path(s) |
| `plot_directory` | string | No | `'./'` | Output directory for plots |

### Core Optional Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|---------|---------|-------------|
| `variables` | list or `'all'` | No | `'all'` | Variables to plot |
| `plot_type` | string | No | `'absolute_difference'` | Plot type (see below) |
| `start_year` | integer | No | `2071` | First year for temporal averaging |
| `end_year` | integer | No | `2090` | Last year for temporal averaging |
| `time_calculation` | string | No | `'mean'` | `'mean'` or `'sum'` for temporal aggregation |
| `grid_file` | string | No | `None` | **Required for EAM**, grid file path |
| `netcdf_file_sets` | list | No | Auto-generated | Labels for ensemble file sets |
| `mean_or_sum_if_over_a_single_dataset` | string | No | `'mean'` | For single file: `'mean'` or `'sum'` |

**Plot Type Options:**
- `'absolute_difference'` - Scenario minus control (default)
- `'percent_difference'` - (Scenario - Control) / Control × 100
- `'separate_plots'` - Individual plots for each scenario/ensemble


### Visual Customization

| Parameter | Type | Required | Default | Description |
|-----------|------|---------|---------|-------------|
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
|-----------|------|---------|---------|-------------|
| `cbar_on` | boolean | No | `true` | Show colorbar |
| `cbar_limits` | list `[min, max]` | No | `None` | Colorbar limits (auto if None) |
| `cbar_label_size` | integer | No | `20` | Colorbar tick label size |
| `cbar_x_offset` | float | No | `0.06` | Colorbar horizontal offset |

### Stippling Parameters (Statistical Significance)

| Parameter | Type | Required | Default | Description |
|-----------|------|---------|---------|-------------|
| `stippling_on` | boolean | No | `false` | Enable stippling |
| `stippling_hatches` | string | No | `'xxxx'` | Hatch pattern (e.g., `'///'`, `'xxx'`) |
| `stippling_std_multiple` | float | No | `2` | Std deviation multiple for stippling |

**Stippling Behavior:**
- **Ensemble data (≥2 members per set):** Stipples where p < threshold (ELM only)
- **Single dataset:** Stipples where |value| > mean ± N×std

### Statistical Testing Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|---------|---------|-------------|
| `p_value_threshold` | float | No | `0.05` | Significance threshold |
| `p_value_file` | string | No | `'p_values.dat'` | Output file for p-values |
| `p_value_file_print_only_if_below_threshold` | boolean | No | `true` | Only print significant p-values |

### Advanced Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|---------|---------|-------------|
| `multiplier` | float/dict | No | `1` | Scale data values |
| `plot_name` | dict | No | Auto-generated | Custom plot filenames per variable |
| `title` | dict | No | Auto-generated | Custom titles per variable |

---

## Plot Types Explained

### 1. Absolute Difference (`plot_type: "absolute_difference"`)

**Description:** Shows scenario minus control in original units

**When to Use:**
- Multiple files provided
- Want actual magnitude of changes
- Variables where absolute change is meaningful

**Processing:**
- **Individual (simple list):** Averages all files, then subtracts first from average
- **Ensemble (nested list):** Calculates ensemble mean for each set, then difference

**Formula:**
```
Difference = Scenario_ensemble_mean - Control_ensemble_mean
```

**Example:**
```json
{
    "netcdf_files": [
        ["control.nc", "control_2.nc", "control_3.nc"],
        ["scenario.nc", "scenario_2.nc", "scenario_3.nc"]
    ],
    "netcdf_file_sets": ["Control", "Scenario"],
    "plot_type": "absolute_difference"
}
```

**Output:** GPP change of +2.5 gC/m²/month shown on map

---

### 2. Percent Difference (`plot_type: "percent_difference"`)

**Description:** Shows percent change relative to control

**When to Use:**
- Emphasizing relative changes
- Variables with widely varying magnitudes
- Comparing fractional impacts

**Formula:**
```
% Difference = (Scenario - Control) / |Control| × 100
```

**Auto-limits:** Sets colorbar to [-100, 100]% if max exceeds 100%

**Example:**
```json
{
    "netcdf_files": ["control.nc", "scenario.nc"],
    "plot_type": "percent_difference"
}
```

**Output:** GPP change of +15% shown on map

---

### 3. Separate Plots (`plot_type: "separate_plots"`)

**Description:** Creates individual maps for each scenario or ensemble

**When to Use:**
- Want to see absolute values for each scenario
- Side-by-side comparison in publications
- Showing spatial patterns individually

**Processing:**
- **Individual (simple list):** One map per file
- **Ensemble (nested list):** One ensemble mean map per set

**Example:**
```json
{
    "netcdf_files": [
        ["control.nc", "control_2.nc"],
        ["scenario.nc", "scenario_2.nc"]
    ],
    "netcdf_file_sets": ["Control", "Scenario"],
    "plot_type": "separate_plots"
}
```

**Output:**
- `spatial_GPP_set_1.pdf` (Control ensemble mean)
- `spatial_GPP_set_2.pdf` (Scenario ensemble mean)

---

## Statistical Testing Explained

The script performs **two types of statistical tests**:

### 1. Aggregated t-test (Always Performed)

**What:** Tests if means differ across all gridcells combined

**When:** Both individual and ensemble configurations

**How:**
- Takes all gridcell values for Control
- Takes all gridcell values for Scenario
- Performs two-sample t-test
- Records p-value in file

**Example Output:**
```
p_values.dat:
GPP in Scenario: 1.234e-04
```

**Interpretation:** Scenario is significantly different from Control globally

---

### 2. Per-Gridcell t-test (Ensemble Only, ELM Only)

**What:** Tests if means differ at each individual gridcell

**When:** 
- Nested list configuration (ensemble)
- ≥2 members per scenario
- **ELM data only** (too slow for EAM unstructured grid)

**How:**
- At gridcell (45°N, 90°W): Compare Control ensemble vs Scenario ensemble
- Performs t-test for that gridcell
- If p < threshold, adds stippling to that gridcell
- Repeats for all gridcells

**Visual Result:** Stippling (hash marks) appears where differences are significant

**Example:** Amazon basin shows dense stippling → significant GPP changes there

**EAM Limitation:** Per-gridcell tests disabled for EAM due to computational cost with unstructured grids

---

### Statistical Testing Summary

**Individual Files (simple list):**
```
✓ Aggregated (all gridcells) - saved to file
✗ Per-gridcell - not applicable (need ensemble)
```

**Ensemble Files (nested list):**
```
✓ Aggregated (all gridcells) - saved to file
✓ Per-gridcell (ELM only) - stippling on map
✗ Per-gridcell (EAM) - disabled (too slow)
```

**P-Value File Contents:**
```
GPP in Full feedback: 2.345e-05
NPP in Full feedback: 1.234e-03
```

**Stippling Controls:**
- `stippling_on`: Enable/disable (default: false)
- `p_value_threshold`: Significance level (default: 0.05)
- `stippling_hatches`: Pattern style (default: 'xxxx')

---

## Ensemble File Organization

When plotting ensembles, you can organize your file lists in **two equivalent ways**:

### Option 1: Organized by File Set (Intuitive)

Each row groups all ensemble members for one scenario:

```json
{
    "netcdf_files": [
        ["control.nc", "control_2.nc", "control_3.nc", "control_4.nc", "control_5.nc"],
        ["feedback.nc", "feedback_2.nc", "feedback_3.nc", "feedback_4.nc", "feedback_5.nc"]
    ],
    "netcdf_file_sets": ["Control", "Full feedback"]
}
```

**Structure:**
- Row 1: All Control files
- Row 2: All Full feedback files
- Easy to see which files belong to each scenario

---

### Option 2: Organized by Ensemble Member

Each row contains one member from each scenario:

```json
{
    "netcdf_files": [
        ["control.nc", "feedback.nc"],
        ["control_2.nc", "feedback_2.nc"],
        ["control_3.nc", "feedback_3.nc"],
        ["control_4.nc", "feedback_4.nc"],
        ["control_5.nc", "feedback_5.nc"]
    ],
    "netcdf_file_sets": ["Control", "Full feedback"]
}
```

**Structure:**
- Row 1: Member 1 for all scenarios
- Row 2: Member 2 for all scenarios
- Easy to add/remove ensemble members

---

### Automatic Detection

The script automatically detects which organization you're using.

**Both produce identical results!** Use whichever is more intuitive.

**Tip:** Always provide `netcdf_file_sets` to label your scenarios clearly.

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

**Stippling:** ✓ **Available** for per-gridcell significance testing

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

**Stippling:** ✗ **Not available** for per-gridcell tests (too slow for unstructured grids)

**Grid Files:**
- ne30: `ne30pg2_scrip_c20191218.nc`
- ne120: `ne120pg2_scrip_c20200803.nc`

---

## Comprehensive JSON Examples

### ELM Examples

#### Example 1: Single Control Map (ELM Config #1)

**From JSON file:**
```json
{
    "netcdf_files": "./control_spatial_data_elm.nc",
    "plot_directory": "./spatial_plots/elm_control",
    "use_latex": true
}
```

**What This Creates:**

**Individual spatial maps for all variables:**
- `spatial_GPP.pdf` - Control GPP map (2071-2090 mean)
- `spatial_NPP.pdf` - Control NPP map
- `spatial_NBP.pdf` - Control NBP map
- `spatial_ER.pdf` - Control ER map
- ... (all variables in NetCDF file)

**Statistics panel on each map:**
```
Max: 1.23e+01
Mean: 4.56e+00
Median: 3.89e+00
Min: -2.34e-01
Std: 2.67e+00
```

**No statistical testing** (only one file, nothing to compare)

**Use case:** Visualizing baseline/control spatial patterns

---

#### Example 2: Single Scenario Map (ELM Config #2)

**From JSON file:**
```json
{
    "netcdf_files": "./full_feedback_spatial_data_elm.nc",
    "plot_directory": "./spatial_plots/elm_full_feedback",
    "use_latex": true
}
```

**What This Creates:**

Same as Example 1, but for Full feedback scenario

**Use case:** Visualizing scenario spatial patterns independently

---

#### Example 3: Individual Absolute Difference (ELM Config #3)

**From JSON file:**
```json
{
    "netcdf_files": [
        "./control_spatial_data_elm.nc", 
        "./full_feedback_spatial_data_elm.nc"
    ],
    "plot_directory": "./spatial_plots/elm_full_feedback_minus_control_individual_absolute_difference",
    "use_latex": true
}
```

**What This Creates:**

**Difference maps (Full feedback - Control):**
- `spatial_GPP.pdf` - Difference map showing where GPP increased/decreased
- Positive values (red): GPP increased in Full feedback
- Negative values (blue): GPP decreased in Full feedback
- White/near-zero: Little change

**Example interpretation for GPP:**
- Amazon: +5 to +10 gC/m²/month (strong increase, red)
- Sahara: ±0.1 gC/m²/month (minimal change, white)
- Northern Canada: +2 to +4 gC/m²/month (moderate increase, light red)

**Statistical testing:**
- Aggregated t-test in `p_values.dat`
- Example: `GPP: 1.234e-05` (highly significant globally)

**No stippling** (simple list, not ensemble)

---

#### Example 4: Individual Percent Difference (ELM Config #4)

**From JSON file:**
```json
{
    "netcdf_files": [
        "./control_spatial_data_elm.nc", 
        "./full_feedback_spatial_data_elm.nc"
    ],
    "plot_directory": "./spatial_plots/elm_full_feedback_minus_control_individual_percent_difference",
    "use_latex": true,
    "plot_type": "percent_difference"
}
```

**What This Creates:**

**Percent change maps:**
- Shows relative change: (Full feedback - Control) / Control × 100
- Highlights areas with large fractional changes

**Example interpretation for GPP:**
- Amazon: +25% to +40% (large relative increase)
- Boreal forests: +10% to +15% (moderate relative increase)
- Deserts: +/-500% (unreliable, very low base values)

**Colorbar:** Often set to [-100, 100]% for readability

**Statistical testing:** Same as Example 3 (aggregated only)

**Use case:** Emphasizing relative impacts regardless of absolute magnitude

---

#### Example 5: Ensemble Absolute Difference (ELM Config #5)

**From JSON file:**
```json
{
    "netcdf_files": [
        ["./control.nc", "./control_2.nc", "./control_3.nc", "./control_4.nc", "./control_5.nc"],
        ["./feedback.nc", "./feedback_2.nc", "./feedback_3.nc", "./feedback_4.nc", "./feedback_5.nc"]
    ],
    "netcdf_file_sets": ["Control", "Full feedback"],
    "plot_directory": "./spatial_plots/elm_full_feedback_minus_control_ensemble_absolute_difference",
    "plot_type": "absolute_difference",
    "use_latex": true
}
```

**What This Creates:**

**Ensemble mean difference maps:**
- Calculates: (Full feedback ensemble mean) - (Control ensemble mean)
- Each ensemble mean is average of 5 members

**Example for GPP:**
- Control ensemble mean: 120 ± 5 gC/m²/month (varies by location)
- Full feedback ensemble mean: 128 ± 6 gC/m²/month
- Difference map shows: +8 gC/m²/month

**Statistical testing:**
1. **Aggregated:** Global t-test in `p_values.dat`
   - Example: `GPP in Full feedback: 3.456e-07`
2. **Per-gridcell:** NO stippling by default (stippling_on: false)

**Use case:** Robust difference estimates with ensemble uncertainty

---

#### Example 6: Ensemble Percent Difference with Stippling (ELM Config #6)

**From JSON file:**
```json
{
    "netcdf_files": [
        ["./control.nc", "./control_2.nc", "./control_3.nc", "./control_4.nc", "./control_5.nc"],
        ["./feedback.nc", "./feedback_2.nc", "./feedback_3.nc", "./feedback_4.nc", "./feedback_5.nc"]
    ],
    "netcdf_file_sets": ["Control", "Full feedback"],
    "plot_directory": "./spatial_plots/elm_full_feedback_minus_control_ensemble_percent_difference",
    "plot_type": "percent_difference",
    "use_latex": true,
    "stippling_on": true
}
```

**What This Creates:**

**Ensemble mean percent difference with significance:**
- Shows % change: (Full feedback mean - Control mean) / Control mean × 100
- **Stippling (xxxx pattern)** where p < 0.05 at individual gridcells

**Example for GPP:**
- Amazon basin: +35% change, **dense stippling** (highly significant)
- Sahara: +5% change, no stippling (not significant due to high variability)
- Boreal: +15% change, **moderate stippling** (significant in some gridcells)

**Statistical testing:**
1. **Aggregated:** `GPP in Full feedback: 2.345e-08`
2. **Per-gridcell:** Stippling shows where specific locations differ significantly

**Interpretation:**
- Stippled regions: Changes are statistically robust at that location
- Non-stippled regions: Changes may be due to natural variability

**Use case:** Publication-quality significance testing showing where changes are reliable

---

#### Example 7: Ensemble Separate Plots with Stippling (ELM Config #7)

**From JSON file:**
```json
{
    "netcdf_files": [
        ["./control.nc", "./control_2.nc", "./control_3.nc", "./control_4.nc", "./control_5.nc"],
        ["./feedback.nc", "./feedback_2.nc", "./feedback_3.nc", "./feedback_4.nc", "./feedback_5.nc"]
    ],
    "netcdf_file_sets": ["Control", "Full feedback"],
    "plot_directory": "./spatial_plots/elm_full_feedback_minus_control_ensemble_separate_plots",
    "plot_type": "separate_plots",
    "use_latex": true,
    "stippling_on": true
}
```

**What This Creates:**

**Two separate ensemble mean maps:**
- `spatial_GPP_set_1.pdf` - Control ensemble mean
  - Shows absolute GPP values (e.g., 100-150 gC/m²/month)
  - **Stippling:** Where Control ensemble has high confidence (low variability)
  
- `spatial_GPP_set_2.pdf` - Full feedback ensemble mean
  - Shows absolute GPP values (e.g., 105-160 gC/m²/month)
  - **Stippling:** Where Full feedback ensemble has high confidence

**Stippling meaning for separate plots:**
- Tests where ensemble mean differs from individual members
- Shows regions with consistent behavior across ensemble
- Based on: |value - ensemble_mean| > N×std (default N=2)

**Use case:** Side-by-side comparison showing absolute values with confidence indicators

---

### EAM Examples

#### Example 8: Single Control Map (EAM Config #1)

**From JSON file:**
```json
{
    "netcdf_files": "./control_spatial_data_eam.nc",
    "plot_directory": "./spatial_plots/eam_control",
    "use_latex": true,
    "grid_file": "./eam_grid_file/ne30pg2_scrip_c20191218.nc"
}
```

**What This Creates:**

**Individual spatial maps for all EAM variables:**
- `spatial_TREFHT.pdf` - Surface temperature map
- `spatial_PRECC.pdf` - Convective precipitation
- `spatial_PRECL.pdf` - Large-scale precipitation
- `spatial_ZCO2.pdf` - CO₂ concentration
- ... (all variables in EAM NetCDF file)

**Key:** `grid_file` parameter **required** for EAM

**Statistics panel:** Same as ELM examples

**No stippling** (single file)

---

#### Example 9: Individual Percent Difference (EAM Config #4)

**From JSON file:**
```json
{
    "netcdf_files": [
        "./control_spatial_data_eam.nc", 
        "./full_feedback_spatial_data_eam.nc"
    ],
    "plot_directory": "./spatial_plots/eam_full_feedback_minus_control_individual_percent_difference",
    "use_latex": true,
    "plot_type": "percent_difference",
    "grid_file": "./eam_grid_file/ne30pg2_scrip_c20191218.nc"
}
```

**What This Creates:**

**Percent difference maps for EAM variables:**

**Example for TREFHT (temperature):**
- Arctic: +2% to +5% (enhanced warming)
- Tropics: +0.5% to +1% (modest warming)
- Oceans: +1% to +2% (moderate warming)

**Example for PRECC (convective precipitation):**
- Tropical rainbelts: +10% to +30% (intensification)
- Subtropics: -5% to -10% (drying)
- Monsoon regions: +15% to +25% (strengthening)

**Statistical testing:** Aggregated only (no per-gridcell for EAM)

---

#### Example 10: Ensemble Absolute Difference (EAM Config #5)

**From JSON file:**
```json
{
    "netcdf_files": [
        ["./control_eam.nc", "./control_eam_2.nc", "./control_eam_3.nc", "./control_eam_4.nc", "./control_eam_5.nc"],
        ["./feedback_eam.nc", "./feedback_eam_2.nc", "./feedback_eam_3.nc", "./feedback_eam_4.nc", "./feedback_eam_5.nc"]
    ],
    "netcdf_file_sets": ["Control", "Full feedback"],
    "plot_directory": "./spatial_plots/eam_full_feedback_minus_control_ensemble_absolute_difference",
    "plot_type": "absolute_difference",
    "use_latex": true,
    "grid_file": "./eam_grid_file/ne30pg2_scrip_c20191218.nc"
}
```

**What This Creates:**

**Ensemble mean difference maps for EAM:**

**Example for TREFHT:**
- Control ensemble mean: 288.5 ± 0.3 K (global average)
- Full feedback ensemble mean: 290.2 ± 0.4 K
- Difference map: +1.7 K average, varying spatially
  - Arctic: +3 to +5 K (strong amplification)
  - Tropics: +1 to +2 K
  - Mid-latitudes: +1.5 to +2.5 K

**Statistical testing:**
- Aggregated: `TREFHT in Full feedback: 1.234e-12` (extremely significant)
- **No per-gridcell stippling** (disabled for EAM)

**Note:** Even without stippling, ensemble averaging provides robust estimates

---

#### Example 11: Ensemble Percent Difference NO Stippling (EAM Config #6)

**From JSON file:**
```json
{
    "netcdf_files": [
        ["./control_eam.nc", "./control_eam_2.nc", "./control_eam_3.nc", "./control_eam_4.nc", "./control_eam_5.nc"],
        ["./feedback_eam.nc", "./feedback_eam_2.nc", "./feedback_eam_3.nc", "./feedback_eam_4.nc", "./feedback_eam_5.nc"]
    ],
    "netcdf_file_sets": ["Control", "Full feedback"],
    "plot_directory": "./spatial_plots/eam_full_feedback_minus_control_ensemble_percent_difference",
    "plot_type": "percent_difference",
    "use_latex": true,
    "stippling_on": false,
    "grid_file": "./eam_grid_file/ne30pg2_scrip_c20191218.nc"
}
```

**Key:** `stippling_on: false` explicitly disables stippling (default for EAM anyway)

**What This Creates:**

Same as Example 10 but with percent differences instead of absolute

**Example for PRECC:**
- Tropical Pacific: +40% to +60% (strong convection increase)
- Mediterranean: -20% to -30% (drying)
- Southeast Asia monsoon: +30% to +50% (intensification)

**No stippling shown** (computational limitation with EAM unstructured grid)

**Interpretation:** Rely on ensemble averaging to reduce noise, use aggregated p-value for global significance

---

#### Example 12: Ensemble Separate Plots (EAM Config #7)

**From JSON file:**
```json
{
    "netcdf_files": [
        ["./control_eam.nc", "./control_eam_2.nc", "./control_eam_3.nc", "./control_eam_4.nc", "./control_eam_5.nc"],
        ["./feedback_eam.nc", "./feedback_eam_2.nc", "./feedback_eam_3.nc", "./feedback_eam_4.nc", "./feedback_eam_5.nc"]
    ],
    "netcdf_file_sets": ["Control", "Full feedback"],
    "plot_directory": "./spatial_plots/eam_full_feedback_minus_control_ensemble_separate_plots",
    "plot_type": "separate_plots",
    "use_latex": true,
    "stippling_on": false,
    "grid_file": "./eam_grid_file/ne30pg2_scrip_c20191218.nc"
}
```

**What This Creates:**

**Two separate ensemble mean maps:**
- `spatial_TREFHT_set_1.pdf` - Control temperature (288-290 K typical range)
- `spatial_TREFHT_set_2.pdf` - Full feedback temperature (289-291 K)

**Use case:** Show absolute spatial patterns for each scenario side-by-side

**No stippling** (EAM limitation)

---

## Output Files

### Plot Files

**Naming Convention:**
```
{plot_directory}/spatial_{variable}.pdf
{plot_directory}/spatial_{variable}_set_1.pdf  (separate_plots)
{plot_directory}/spatial_{variable}_set_2.pdf  (separate_plots)
```

**Example Output Directory (ELM):**
```
./spatial_plots/elm_ensemble_percent_difference/
├── spatial_GPP.pdf
├── spatial_NPP.pdf
├── spatial_NBP.pdf
├── spatial_ER.pdf
└── p_values.dat
```

**Example Output Directory (EAM):**
```
./spatial_plots/eam_ensemble_absolute_difference/
├── spatial_TREFHT.pdf
├── spatial_PRECC.pdf
├── spatial_PRECL.pdf
├── spatial_ZCO2.pdf
└── p_values.dat
```

### P-Value Files

**Purpose:** Records aggregated statistical significance across all gridcells

**Format:**
```
GPP in Full feedback: 1.234e-05
NPP in Full feedback: 3.456e-03
NBP in Full feedback: 5.678e-02
```

**Location:** `{plot_directory}/p_values.dat`

**Note:** Contains **aggregated** p-values (all gridcells combined). Per-gridcell p-values shown as stippling on maps (ELM only).

---

## Best Practices

### 1. Choose Appropriate Plot Type

**Use `absolute_difference` when:**
- Comparing scenarios
- Want actual magnitude of changes
- Publishing quantitative results

**Use `percent_difference` when:**
- Emphasizing relative changes
- Variables with varying baseline magnitudes
- Highlighting fractional impacts

**Use `separate_plots` when:**
- Need to show absolute values for each scenario
- Side-by-side comparison
- Presenting individual spatial patterns

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

**Why average?** Reduces interannual variability, shows robust climate signal

---

### 3. Stippling Strategy

**For ELM ensemble plots:**
```json
"stippling_on": true
```

**Benefits:**
- Shows where changes are statistically significant
- Identifies robust vs noisy patterns
- Publication-quality confidence visualization

**For EAM or individual plots:**
```json
"stippling_on": false
```

**Why:**
- EAM: Too slow for unstructured grids
- Individual: No ensemble for statistical testing

---

### 4. Colormap Selection

**For differences (default):**
```json
"cmap": "bwr"  // Blue-White-Red
```
- Blue: Decreases
- White: No change
- Red: Increases

**Alternative diverging:**
```json
"cmap": "RdBu_r"  // Red-Blue reversed
"cmap": "PuOr"    // Purple-Orange
```

**For absolute values:**
```json
"cmap": "viridis"  // Sequential
"cmap": "plasma"
```

---

### 5. EAM Grid Files

**Check your simulation resolution:**
- ne30: `ne30pg2_scrip_c20191218.nc`
- ne120: `ne120pg2_scrip_c20200803.nc`
- ne256: `ne256pg2_scrip_c20200803.nc`

**Always provide correct grid file for EAM!**

---

### 6. Variable Selection

**Plot all:**
```json
"variables": "all"
```

**Plot specific:**
```json
"variables": ["GPP", "NPP", "NBP"]
```

**Recommendation:** Start specific for testing, expand to "all" for comprehensive analysis

---

### 7. File Organization

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

### Issue 1: Grid File Missing (EAM)

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

### Issue 2: Stippling Not Appearing (EAM)

**Symptom:** Expected stippling but none appears

**Cause:** Stippling disabled for EAM (computational limitation)

**Explanation:** Per-gridcell t-tests too slow for unstructured grids

**Solution:** 
- Accept limitation for EAM
- Use aggregated p-values for global significance
- Consider ELM data if per-gridcell testing critical

---

### Issue 3: Stippling Not Appearing (ELM)

**Symptom:** Expected stippling but none appears on ELM plot

**Possible Causes:**
1. `stippling_on: false` (default)
2. Simple list (not ensemble)
3. All gridcells non-significant (p > 0.05)

**Solutions:**

**Check configuration:**
```json
"stippling_on": true  // Must enable
```

**Verify ensemble format:**
```json
"netcdf_files": [
    ["ctrl.nc", "ctrl_2.nc"],  // Nested list required
    ["scen.nc", "scen_2.nc"]
]
```

**Check p-values:**
If aggregated p-value > 0.05, likely no gridcells significant either

---

### Issue 4: File Not Found

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

### Issue 5: Variable Not Found

**Error:**
```
KeyError: 'GPP'
```

**Solution:**
```python
import xarray as xr
ds = xr.open_dataset('spatial_data.nc')
print(list(ds.keys()))
```

Check exact variable names (case-sensitive)

---

### Issue 6: Wrong Grid File

**Symptom:** Distorted or incorrect map

**Cause:** Grid file doesn't match simulation resolution

**Solution:**
- Verify simulation was ne30, ne120, etc.
- Use corresponding grid file
- Check grid file date matches data generation

---

## Advanced Features

### Per-Variable Configuration

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

```json
"projection": "Robinson"           // Global (default)
"projection": "PlateCarree"        // Equirectangular
"projection": "Mollweide"          // Equal-area
"projection": "NorthPolarStereo"   // Arctic
"projection": "SouthPolarStereo"   // Antarctic
```

---

### Time Aggregation

**Mean (default):**
```json
"time_calculation": "mean"
```
Use for: Temperature, CO₂ concentration

**Sum:**
```json
"time_calculation": "sum"
```
Use for: Precipitation, fluxes

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
**Documentation Version:** 2.0  
**Last Updated:** January 2026  
**Python Version:** 3.7+  
**Dependencies:** xarray, uxarray, cartopy, matplotlib, scipy, numpy, pandas

---

*This documentation provides comprehensive guidance for using the `e3sm_plot_spatial_data.py` script to create publication-quality spatial maps from E3SM model output with ensemble analysis and statistical significance testing.*
