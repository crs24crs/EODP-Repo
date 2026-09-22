import os
import numpy
import netCDF4 as nc
import matplotlib.pyplot as plt

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

def recreate_equalization_plot(file_eq, file_no_eq, file_isrf, alt_line_idx=50):

    # Open datasets
    ds_eq = nc.Dataset(file_eq, 'r')
    ds_no_eq = nc.Dataset(file_no_eq, 'r')
    ds_isrf = nc.Dataset(file_isrf, 'r')

    # Extract the target variable
    var_eq = ds_eq.variables['toa']
    var_no_eq = ds_no_eq.variables['toa']
    var_isrf = ds_isrf.variables['toa']

    # Extract a single along-track line.
    # Adjust alt_line_idx if a specific line was used to generate the reference image.
    data_eq = var_eq[alt_line_idx, :]
    data_no_eq = var_no_eq[alt_line_idx, :]
    data_isrf = var_isrf[alt_line_idx, :]

    # Close datasets
    ds_eq.close()
    ds_no_eq.close()
    ds_isrf.close()

    # --- Plot ---
    # Adjust figure size to be like teachers result
    plt.figure(figsize=(10, 6))

    # Plot lines with colors and labels
    plt.plot(data_eq, color='black', label='TOA L1B with eq')
    plt.plot(data_no_eq, color='red', label='TOA L1B no eq')
    plt.plot(data_isrf, color='blue', label='TOA after the ISRF')

    # Apply titles, axis labels, and styling
    plt.title('Effect of the Equalization for VNIR-0')
    plt.xlabel('ACT pixel [-]')
    plt.ylabel('TOA [mW/m2/sr]')

    plt.grid()
    plt.legend()

    plt.tight_layout()

    # Save the plot as a PNG image in the current directory
    plt.savefig('Equalization_Model.png')

    # Show the plot
    plt.show()



# ---------------------------------------------------------------------------------------------

# Run validation
validate_equalised_results(teacher_output, my_output)

# Generate the plot
recreate_equalization_plot(file_with_eq, file_no_eq, file_isrf, alt_line_idx=50)