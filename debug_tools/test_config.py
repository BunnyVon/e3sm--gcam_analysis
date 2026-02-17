#!/usr/bin/env python3
"""
Quick test script to validate JSON configuration without running full analysis.
This helps debug configuration issues before submitting SLURM jobs.
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
def test_json_config(json_file):
    """Test JSON configuration for common issues."""
    
    print(f"Testing configuration file: {json_file}")
    print("=" * 60)
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        print(f"✓ JSON file loaded successfully")
        print(f"✓ Found {len(data)} configuration entries")
    except Exception as e:
        print(f"✗ Failed to load JSON: {e}")
        return False
    
    all_valid = True
    
    for i, entry in enumerate(data):
        print(f"\n--- Entry {i+1} ---")
        
        # Check required fields
        required_fields = ['variables', 'netcdf_substrings', 'simulation_path', 'output_file']
        for field in required_fields:
            if field not in entry:
                print(f"✗ Missing required field: {field}")
                all_valid = False
            else:
                print(f"✓ Has {field}")
        
        if 'variables' in entry and 'netcdf_substrings' in entry:
            # Check length consistency
            var_len = len(entry['variables'])
            netcdf_len = len(entry['netcdf_substrings'])
            
            print(f"Variables groups: {var_len}")
            print(f"NetCDF substring groups: {netcdf_len}")
            
            if var_len == netcdf_len:
                print("✓ Lengths match!")
            else:
                print(f"✗ Length mismatch: variables={var_len}, netcdf_substrings={netcdf_len}")
                all_valid = False
            
            # Show content structure
            print(f"Variables structure: {entry['variables']}")
            print(f"NetCDF structure: {entry['netcdf_substrings']}")
        
        # Check if simulation path exists
        if 'simulation_path' in entry:
            sim_path = Path(entry['simulation_path'])
            if sim_path.exists():
                print(f"✓ Simulation path exists: {sim_path}")
                # Count .nc files
                nc_files = list(sim_path.glob("*.nc"))
                print(f"  Found {len(nc_files)} .nc files")
            else:
                print(f"⚠ Simulation path not accessible: {sim_path}")
        
        # Check output directory
        if 'output_file' in entry:
            output_path = Path(entry['output_file']).parent
            print(f"Output directory: {output_path}")
            if not output_path.exists():
                print(f"⚠ Output directory doesn't exist, will be created")
        
        # Validate region names if present
        if 'regions' in entry and entry['regions']:
            print(f"Checking region names...")
            region_issues = validate_region_names(entry['regions'])
            if region_issues:
                print(f"⚠ Region validation warnings:")
                for issue in region_issues:
                    print(f"  • {issue}")
                all_valid = False
            else:
                print(f"✓ All regions recognized")
    
    print("\n" + "=" * 60)
    if all_valid:
        print("✓ Configuration appears valid for SLURM submission!")
    else:
        print("✗ Configuration has issues - fix before submitting")
    
    return all_valid

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_config.py <json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    success = test_json_config(json_file)
    sys.exit(0 if success else 1)