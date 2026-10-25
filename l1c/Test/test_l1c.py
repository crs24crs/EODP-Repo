import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc

# PATHS:
file_l1c_grid = r"C:\Users\crs24\OneDrive\Desktop\Master\5SC\EODP\EODP_TER_2021\EODP-TS-L1C\outputCarlos\l1c_toa_VNIR-0.nc"
file_l1b_grid = r"C:\Users\crs24\OneDrive\Desktop\Master\5SC\EODP\EODP_TER_2021\EODP-TS-L1B\outputCarlos\l1b_toa_VNIR-0.nc"

# Open datasets
ds_l1b = nc.Dataset(file_l1b_grid, 'r')
ds_l1c = nc.Dataset(file_l1c_grid, 'r')

# Print the variable names to see the exact keys
print("L1B Variables:", ds_l1b.variables.keys())
print("L1C Variables:", ds_l1c.variables.keys())

# Extract Lat/Lon arrays
l1b_lat = ds_l1b.variables['lat'][:]
l1b_lon = ds_l1b.variables['lon'][:]
l1c_lat = ds_l1c.variables['lat'][:]
l1c_lon = ds_l1c.variables['lon'][:]

# -------------------------------------------------------------------------
# Plot 1: L1B Grid vs L1C Grid
# -------------------------------------------------------------------------
plt.figure(figsize=(10, 8))

# Scatter plotting the grids. Using a small marker size (s=2) and transparency
# to clearly visualize the overlapping grid structures.
plt.scatter(l1b_lon.flatten(), l1b_lat.flatten(), c='red', s=2, alpha=0.7, label='L1B Grid (Irregular)')
plt.scatter(l1c_lon.flatten(), l1c_lat.flatten(), c='blue', s=2, alpha=0.7, label='L1C Grid (Regular MGRS)')

plt.title('L1B versus L1C Geolocation Grids (VNIR-0)')
plt.xlabel('Longitude [°]')
plt.ylabel('Latitude [°]')
plt.legend(loc='upper right')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('L1B_vs_L1C_Grid.png', dpi=300)
plt.show()

# -------------------------------------------------------------------------
# Plot 2: Spatial Sampling Distance (Central Row)
# -------------------------------------------------------------------------
# Identify the central ACT (across-track) column index
central_act_idx = l1b_lat.shape[1] // 2

# Extract the along-track (ALT) profile for the central column
lat_center = l1b_lat[:, central_act_idx]
lon_center = l1b_lon[:, central_act_idx]


def vectorized_haversine(lat1, lon1, lat2, lon2):
    """
    Computes the great-circle distance between two points on a sphere
    given their longitudes and latitudes using the haversine formula.
    """
    R = 6371000  # Earth radius in meters
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)

    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c


# Calculate SSD between consecutive pixels along the ALT direction
ssd = vectorized_haversine(lat_center[:-1], lon_center[:-1], lat_center[1:], lon_center[1:])

plt.figure(figsize=(10, 6))
plt.plot(range(len(ssd)), ssd, marker='.', linestyle='-', color='black', markersize=4)
plt.title('Along-Track Spatial Sampling Distance (L1B Central Column)')
plt.xlabel('Along-Track Pixel Transition Index [-]')
plt.ylabel('Spatial Sampling Distance [m]')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('Spatial_Sampling_Distance.png', dpi=300)
plt.show()

# Close datasets
ds_l1b.close()
ds_l1c.close()