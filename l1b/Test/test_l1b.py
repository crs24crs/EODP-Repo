import os
import numpy
import netCDF4 as nc

# PATHS:
teacher_output = r"C:\\Users\\crs24\\OneDrive\\Desktop\\Master\\5SC\\EODP\\EODP_TER_2021\\EODP-TS-L1B\\output"
my_output = r"C:\\Users\\crs24\\OneDrive\\Desktop\\Master\\5SC\\EODP\\EODP_TER_2021\\EODP-TS-L1B\\outputCarlos"

file_with_eq = "C:\\Users\\crs24\\OneDrive\\Desktop\\Master\\5SC\\EODP\\EODP_TER_2021\\EODP-TS-L1B\\outputCarlos\\l1b_toa_VNIR-0.nc"
file_no_eq = "C:\\Users\\crs24\\OneDrive\\Desktop\\Master\\5SC\\EODP\\EODP_TER_2021\\EODP-TS-L1B\\output_not_equalized\\l1b_toa_VNIR-0.nc"
file_isrf = "C:\\Users\\crs24\\OneDrive\\Desktop\\Master\\5SC\\EODP\\EODP_TER_2021\\EODP-TS-L1B\\input\\ism_toa_isrf_VNIR-0.nc"

def validate_equalised_results(ref_dir, my_dir, threshold_pct=1e-3):
    # Convert percentage to decimal (1e-3 % = 1e-5)
    threshold = threshold_pct / 100.0
    all_passed = True

    # Find NetCDF files in directory
    files_to_check = [f for f in os.listdir(my_dir) if f.startswith('l1b_toa') and f.endswith('.nc')]

    for filename in files_to_check:
        ref_path = os.path.join(ref_dir, filename)
        my_path = os.path.join(my_dir, filename)

        print(f"Checking: {filename}:")

        # Open the two datasets
        with nc.Dataset(ref_path, 'r') as ds_ref, nc.Dataset(my_path, 'r') as ds_my:
            # Iterate through all variables in the NetCDF file
            for var_name in ds_ref.variables:

                # Extract data in numpy arrays
                ref_data = ds_ref.variables[var_name][:]
                my_data = ds_my.variables[var_name][:]

                # Calculate relative difference: |(mine - reference) / reference|
                rel_diff = numpy.abs((my_data - ref_data) / ref_data)

                # Get the maximum relative difference
                max_rel_diff = numpy.nanmax(rel_diff)

                if max_rel_diff >= threshold:
                    print(f"  [FAIL] {var_name} -> Max Rel Diff: {max_rel_diff * 100:.6e}% >= {threshold_pct}%")
                    all_passed = False
                else:
                    print(f"  [PASS] {var_name} -> Max Rel Diff: {max_rel_diff * 100:.6e}% < {threshold_pct}%")

    print("\n--- Final Result ---")
    if all_passed:
        print(f"PASS: All equalised results showed a relative difference lower than {threshold_pct}%")
    else:
        print("FAILED: One or more equalised results exceeded the maximum allowed relative difference.")

# ---------------------------------------------------------------------------------------------

# Run validation
validate_equalised_results(teacher_output, my_output)