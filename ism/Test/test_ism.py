import os
import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt
from scipy.special import j1

teacher_output = r"C:\\Users\\crs24\\OneDrive\\Desktop\\Master\\5SC\\EODP\\EODP_TER_2021\\EODP-TS-ISM\\output"
my_output = r"C:\\Users\\crs24\\OneDrive\\Desktop\\Master\\5SC\\EODP\\EODP_TER_2021\\EODP-TS-ISM\\outputCarlos"

def validate_ism_outputs(ref_dir, my_dir, threshold_pct=1e-3):
    threshold = threshold_pct / 100.0
    all_passed = True

    # Target ISM specific NetCDF files
    files_to_check = [f for f in os.listdir(my_dir) if f.startswith('ism_') and f.endswith('.nc')]

    for filename in files_to_check:
        ref_path = os.path.join(ref_dir, filename)
        my_path = os.path.join(my_dir, filename)

        if not os.path.exists(ref_path):
            continue

        print(f"Checking {filename}:")

        with nc.Dataset(ref_path, 'r') as ds_ref, nc.Dataset(my_path, 'r') as ds_my:
            for var_name in ds_ref.variables:
                ref_data = ds_ref.variables[var_name][:]
                my_data = ds_my.variables[var_name][:]

                # Suppress divide-by-zero warnings in background areas
                with np.errstate(divide='ignore', invalid='ignore'):
                    rel_diff = np.abs((my_data - ref_data) / ref_data)

                max_rel_diff = np.nanmax(rel_diff)

                if max_rel_diff >= threshold:
                    print(f"  [FAIL] {var_name} -> Max Rel Diff: {max_rel_diff * 100:.6e}%")
                    all_passed = False
                else:
                    print(f"  [PASS] {var_name} -> Max Rel Diff: {max_rel_diff * 100:.6e}%")

    print("\n--- Final ISM Validation Result ---")
    if all_passed:
        print(f"PASS: All ISM results showed a relative difference lower than {threshold_pct}%")
    else:
        print("FAILED: One or more ISM results exceeded the maximum allowed relative difference.")

# Run validation
validate_ism_outputs(teacher_output, my_output)
