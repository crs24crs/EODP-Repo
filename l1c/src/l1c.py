from l1c.src.initL1c import initL1c
from common.io.writeToa import writeToa, readToa
from common.io.readGeodetic import readGeodetic, getCorners
import mgrs
import numpy as np
from scipy.interpolate import bisplrep, bisplev
import matplotlib.pyplot as plt
from common.io.l1cProduct import writeL1c
from matplotlib import cm
import geopy.distance
import os


class l1c(initL1c):

    def __init__(self, auxdir, indir, outdir):
        super().__init__(auxdir, indir, outdir)

    def processModule(self):

        self.logger.info("Start of the L1C Processing Module")

        for band in self.globalConfig.bands:

            self.logger.info("Start of BAND " + band)

            # Read TOA - output of the L1B in Radiances
            # -------------------------------------------------------------------------------
            toa = readToa(self.l1bdir, self.globalConfig.l1b_toa + band + '.nc')
            lat, lon = readGeodetic(self.gmdir, self.globalConfig.gm_geoloc)
            self.checkSize(lat, toa)

            # L1C reprojection onto the MGRS grid
            # -------------------------------------------------------------------------------
            lat_l1c, lon_l1c, toa_l1c = self.l1cProjtoa(lat, lon, toa, band)

            # Write output TOA
            # -------------------------------------------------------------------------------
            writeL1c(self.outdir, self.globalConfig.l1c_toa + band, lat_l1c, lon_l1c, toa_l1c)

            # Generate and save report plots specifically for the VNIR-0 band
            if band == 'VNIR-0':
                self.plot_grids_and_ssd(lat, lon, lat_l1c, lon_l1c)

            self.logger.info("End of BAND " + band)

        self.logger.info("End of the L1C Module!")

    def plot_grids_and_ssd(self, lat_l1b, lon_l1b, lat_l1c, lon_l1c):
        """Generates the L1B vs L1C grid plot and the Spatial Sampling Distance plot."""
        self.logger.info("Generating Report 3 Plots for VNIR-0...")

        # -------------------------------------------------------------------------
        # Plot 1: L1B Grid (Bounding Box) vs L1C Grid (Scatter)
        # -------------------------------------------------------------------------
        plt.figure(figsize=(10, 6))

        # Extract the 4 corners of the L1B 2D array to draw the boundary box
        # Sequence: Top-Left -> Top-Right -> Bottom-Right -> Bottom-Left -> Top-Left (to close loop)
        l1b_lat_corners = [lat_l1b[0, 0], lat_l1b[0, -1], lat_l1b[-1, -1], lat_l1b[-1, 0], lat_l1b[0, 0]]
        l1b_lon_corners = [lon_l1b[0, 0], lon_l1b[0, -1], lon_l1b[-1, -1], lon_l1b[-1, 0], lon_l1b[0, 0]]

        # Plot L1B as a black bounding box
        plt.plot(l1b_lon_corners, l1b_lat_corners, c='black', linewidth=1.5, label='L1B')

        # Plot L1C as red dots
        plt.scatter(lon_l1c, lat_l1c, c='red', s=4, alpha=0.8, label='L1C MGRS')

        plt.title('Projection on ground', fontsize=14)
        plt.xlabel('Longitude [deg]', fontsize=12)
        plt.ylabel('Latitude [deg]', fontsize=12)
        plt.legend(loc='upper right', fontsize=9)
        plt.grid(True, linestyle='-', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(self.outdir, 'L1B_vs_L1C_Grid.png'), dpi=300)
        plt.close()

        # -------------------------------------------------------------------------
        # Plot 2: Spatial Sampling Distance (Central Row)
        # -------------------------------------------------------------------------
        central_row_idx = lat_l1b.shape[0] // 2
        lat_center_row = lat_l1b[central_row_idx, :]
        lon_center_row = lon_l1b[central_row_idx, :]

        ssd = []
        for i in range(len(lat_center_row) - 1):
            point1 = (lat_center_row[i], lon_center_row[i])
            point2 = (lat_center_row[i + 1], lon_center_row[i + 1])
            dist = geopy.distance.great_circle(point1, point2).meters
            ssd.append(dist)

        plt.figure(figsize=(10, 6))
        plt.plot(range(len(ssd)), ssd, marker='.', linestyle='-', color='black', markersize=4)
        plt.title('Across-Track Spatial Sampling Distance (L1B Central Row)')
        plt.xlabel('Across-Track Pixel Transition Index [-]')
        plt.ylabel('Spatial Sampling Distance [m]')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(os.path.join(self.outdir, 'Spatial_Sampling_Distance.png'), dpi=300)
        plt.close()

        self.logger.info("Report 3 Plots saved successfully.")

    def l1cProjtoa(self, lat, lon, toa, band):
        tck = bisplrep(lat, lon, toa)
        m = mgrs.MGRS()
        mgrs_tiles = set([])

        for ii in range(toa.shape[0]):  # 100
            for jj in range(toa.shape[1]):  # 150
                mgrstile = m.toMGRS(lat[ii, jj], lon[ii, jj], MGRSPrecision=self.l1cConfig.mgrs_tile_precision)
                mgrs_tiles.add(mgrstile)

        mgrs_tiles = list(mgrs_tiles)

        toa_l1c = np.zeros(len(mgrs_tiles))
        lat_l1c = np.zeros(len(mgrs_tiles))
        lon_l1c = np.zeros(len(mgrs_tiles))

        for ii in range(len(mgrs_tiles)):
            (lat_l1c[ii], lon_l1c[ii]) = m.toLatLon(mgrs_tiles[ii])
            toa_l1c[ii] = bisplev(lat_l1c[ii], lon_l1c[ii], tck)

        return lat_l1c, lon_l1c, toa_l1c

    def checkSize(self, lat, toa):
        pass