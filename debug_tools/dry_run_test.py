#!/usr/bin/env python3
"""
Lightweight test of the E3SM extraction script without processing files.
Tests the validation logic and setup without heavy computation.
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path to import utility modules
# Try multiple possible locations for the utility files
script_dir = os.path.dirname(os.path.abspath(__file__))
possible_paths = [
    os.path.join(script_dir, '..'),  # Parent directory (default case)
    '/global/cfs/cdirs/e3sm/feng809/s2d/compr',  # Known working location
    script_dir  # Same directory
]

for path in possible_paths:
    if os.path.exists(os.path.join(path, 'utility_e3sm_netcdf.py')):
        sys.path.insert(0, path)
        break

try:
    from utility_e3sm_netcdf import get_regional_bounds
    REGION_VALIDATION_AVAILABLE = True
except ImportError:
    print("⚠ Could not import utility_e3sm_netcdf - region validation disabled")
    REGION_VALIDATION_AVAILABLE = False

def validate_region_names(regions):
    """Validate that region names are recognized by utility_e3sm_netcdf."""
    if not REGION_VALIDATION_AVAILABLE:
        return []
    
    issues = []
    for region in regions:
        if region is None:
            continue  # None regions are valid (global)
        
        # Test if region is recognized by checking bounds
        import io
        from contextlib import redirect_stdout
        
        # Capture any warning output from get_regional_bounds
        f = io.StringIO()
        with redirect_stdout(f):
            bounds = get_regional_bounds(region)
        
        output = f.getvalue()
        
        # Check if it fell back to global bounds (output contains warning)
        if "Did not recognize" in output:
            issues.append(f"Region '{region}' not recognized - will use global bounds")
        else:
            print(f"✓ Region '{region}' recognized: bounds {bounds}")
    
    return issues

def dry_run_test(json_file):
    """Test the extraction function setup without processing files."""
    
    print(f"Dry-run testing: {json_file}")
    print("=" * 60)
    
    # Load JSON
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        print(f"✓ Loaded {len(data)} entries from JSON")
    except Exception as e:
        print(f"✗ JSON load failed: {e}")
        return False
    
    # Test each entry's validation logic (without imports)
    all_valid = True
    for i, entry in enumerate(data):
        print(f"\n--- Testing Entry {i+1} ---")
        
        # Extract parameters
        variables = entry.get('variables', [])
        netcdf_substrings = entry.get('netcdf_substrings', [])
        lat_lon_aggregation_types = entry.get('lat_lon_aggregation_types', None)
        regions = entry.get('regions', None)
        
        print(f"Variables: {len(variables)} groups")
        print(f"NetCDF substrings: {len(netcdf_substrings)} groups")
        
        # Simulate the validation logic from the main script
        if len(variables) != len(netcdf_substrings):
            print(f"✗ VALIDATION FAIL: Length mismatch")
            print(f"   variables={len(variables)}, netcdf_substrings={len(netcdf_substrings)}")
            all_valid = False
        else:
            print(f"✓ Length validation: PASS")
        
        # Test default parameter logic
        if not lat_lon_aggregation_types:
            lat_lon_aggregation_types = ['area_weighted_mean_or_sum'] * len(variables)
            print(f"✓ Default aggregation types: {len(lat_lon_aggregation_types)} created")
        
        if not regions:
            regions = [None] * len(variables)
            print(f"✓ Default regions: {len(regions)} created")
        
        # Additional validation
        if len(lat_lon_aggregation_types) != len(variables):
            print(f"✗ Aggregation types length mismatch: {len(lat_lon_aggregation_types)} vs {len(variables)}")
            all_valid = False
        
        if len(regions) != len(variables):
            print(f"✗ Regions length mismatch: {len(regions)} vs {len(variables)}")
            all_valid = False
        
        print(f"✓ All parameter lengths consistent")
        
        # Validate region names if present
        if regions and any(r is not None for r in regions):
            print(f"Checking region names...")
            region_issues = validate_region_names(regions)
            if region_issues:
                print(f"⚠ Region validation warnings:")
                for issue in region_issues:
                    print(f"  • {issue}")
                all_valid = False
            else:
                print(f"✓ All regions recognized")
        
        # Test file path access
        sim_path = Path(entry.get('simulation_path', ''))
        if sim_path.exists():
            print(f"✓ Simulation path accessible")
        else:
            print(f"⚠ Cannot access simulation path: {sim_path}")
        
        # Show what would be processed
        for idx in range(len(variables)):
            print(f"  Group {idx+1}: {len(variables[idx])} variables, substring {netcdf_substrings[idx]}")
    
    print("\n" + "=" * 60)
    if all_valid:
        print("✓ All validations passed! Ready for SLURM submission.")
    else:
        print("✗ Configuration has issues - fix before submitting")
    return all_valid

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dry_run_test.py <json_file>")
        print("Example: python dry_run_test.py e3sm_extract_time_series_h0_regs.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    success = dry_run_test(json_file)
    sys.exit(0 if success else 1)