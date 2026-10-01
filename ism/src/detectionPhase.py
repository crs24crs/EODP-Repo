
from ism.src.initIsm import initIsm
import numpy as np
from common.io.writeToa import writeToa
from common.plot.plotMat2D import plotMat2D
from common.plot.plotF import plotF

class detectionPhase(initIsm):

    def __init__(self, auxdir, indir, outdir):
        super().__init__(auxdir, indir, outdir)

        # Initialise the random see for the PRNU and DSNU
        np.random.seed(self.ismConfig.seed)


    def compute(self, toa, band):

        self.logger.info("EODP-ALG-ISM-2000: Detection stage")

        # Irradiance to photons conversion
        # -------------------------------------------------------------------------------
        self.logger.info("EODP-ALG-ISM-2010: Irradiances to Photons")
        area_pix = self.ismConfig.pix_size * self.ismConfig.pix_size # [m2]
        toa = self.irrad2Phot(toa, area_pix, self.ismConfig.t_int, self.ismConfig.wv[int(band[-1])])

        self.logger.debug("TOA [0,0] " +str(toa[0,0]) + " [ph]")

        # Photon to electrons conversion
        # -------------------------------------------------------------------------------
        self.logger.info("EODP-ALG-ISM-2030: Photons to Electrons")
        toa = self.phot2Electr(toa, self.ismConfig.QE)

        self.logger.debug("TOA [0,0] " +str(toa[0,0]) + " [e-]")

        if self.ismConfig.save_after_ph2e:
            saveas_str = self.globalConfig.ism_toa_e + band
            writeToa(self.outdir, saveas_str, toa)

        # PRNU
        # -------------------------------------------------------------------------------
        if self.ismConfig.apply_prnu:

            self.logger.info("EODP-ALG-ISM-2020: PRNU")
            toa = self.prnu(toa, self.ismConfig.kprnu)

            self.logger.debug("TOA [0,0] " +str(toa[0,0]) + " [e-]")

            if self.ismConfig.save_after_prnu:
                saveas_str = self.globalConfig.ism_toa_prnu + band
                writeToa(self.outdir, saveas_str, toa)

        # Dark-signal
        # -------------------------------------------------------------------------------
        if self.ismConfig.apply_dark_signal:

            self.logger.info("EODP-ALG-ISM-2020: Dark signal")
            toa = self.darkSignal(toa, self.ismConfig.kdsnu, self.ismConfig.T, self.ismConfig.Tref,
                                  self.ismConfig.ds_A_coeff, self.ismConfig.ds_B_coeff)

            self.logger.debug("TOA [0,0] " +str(toa[0,0]) + " [e-]")

            if self.ismConfig.save_after_ds:
                saveas_str = self.globalConfig.ism_toa_ds + band
                writeToa(self.outdir, saveas_str, toa)

        # Bad/dead pixels
        # -------------------------------------------------------------------------------
        if self.ismConfig.apply_bad_dead:

            self.logger.info("EODP-ALG-ISM-2050: Bad/dead pixels")
            toa = self.badDeadPixels(toa,
                               self.ismConfig.bad_pix,
                               self.ismConfig.dead_pix,
                               self.ismConfig.bad_pix_red,
                               self.ismConfig.dead_pix_red)


        # Write output TOA
        # -------------------------------------------------------------------------------
        if self.ismConfig.save_detection_stage:
            saveas_str = self.globalConfig.ism_toa_detection + band

            writeToa(self.outdir, saveas_str, toa)

            title_str = 'TOA after the detection phase [e-]'
            xlabel_str='ACT'
            ylabel_str='ALT'
            plotMat2D(toa, title_str, xlabel_str, ylabel_str, self.outdir, saveas_str)

            idalt = int(toa.shape[0]/2)
            saveas_str = saveas_str + '_alt' + str(idalt)
            plotF([], toa[idalt,:], title_str, xlabel_str, ylabel_str, self.outdir, saveas_str)

        return toa


    def irrad2Phot(self, toa, area_pix, tint, wv):
        """
        Conversion of the input Irradiances to Photons
        :param toa: input TOA in irradiances [mW/m2]
        :param area_pix: Pixel area [m2]
        :param tint: Integration time [s]
        :param wv: Central wavelength of the band [m]
        :return: Toa in photons
        """
        #TODO
        h = self.constants.speed_light
        c = self.constants.h_planck

        e_in = (toa / 1000.0) * area_pix * tint

        e_photon = (h * c) / wv

        toa_ph = e_in / e_photon

        return toa_ph

    def phot2Electr(self, toa, QE):
        """
        Conversion of photons to electrons
        :param toa: input TOA in photons [ph]
        :param QE: Quantum efficiency [e-/ph]
        :return: toa in electrons
        """
        #TODO
        #Convert from photons to electrons with QE
        toae = toa * QE

        # Check and clip values so none exceed the FWC
        if hasattr(self.ismConfig, 'FWC') and self.ismConfig.FWC is not None:
            if np.any(toae > self.ismConfig.FWC):
                self.logger.warning("Warning: Some pixels exceed the FWC. Limiting those values.")
            toae = np.clip(toae, 0, self.ismConfig.FWC)

        return toae

    def badDeadPixels(self, toa,bad_pix,dead_pix,bad_pix_red,dead_pix_red):
        """
        Bad and dead pixels simulation
        :param toa: input toa in [e-]
        :param bad_pix: Percentage of bad pixels in the CCD [%]
        :param dead_pix: Percentage of dead pixels in the CCD [%]
        :param bad_pix_red: Reduction in the quantum efficiency for the bad pixels [-, over 1]
        :param dead_pix_red: Reduction in the quantum efficiency for the dead pixels [-, over 1]
        :return: toa in e- including bad & dead pixels
        """
        #TODO
        #Get the number of pixels in the across-track direction
        toa_act = toa.shape[1]

        # Calculate the number of pixels affected
        n_bad = int(toa_act * (bad_pix / 100.0))
        n_dead = int(toa_act * (dead_pix / 100.0))

        # Determine evenly distributed steps and apply to the CCD
        idx_bad = []
        if n_bad > 0:
            step_bad = int(toa_act / n_bad)
            # Distribute evenly in the CCD starting at index 5
            idx_bad = range(5, toa_act, step_bad)
            # Apply the reduction factor to the DNs directly
            toa[:, idx_bad] *= (1.0 - bad_pix_red)

        idx_dead = []
        if n_dead > 0:
            step_dead = int(toa_act / n_dead)
            # Distribute evenly in the CCD starting at index 0
            idx_dead = range(0, toa_act, step_dead)
            # Apply the reduction factor to the DNs directly
            toa[:, idx_dead] *= dead_pix_red

        # Save to file the indexes for validation purposes
        import os
        os.makedirs(self.outdir, exist_ok=True)
        with open(os.path.join(self.outdir, 'bad_dead_indexes.txt'), 'w') as f:
            f.write(f"Bad pixel indexes: {list(idx_bad)}\n")
            f.write(f"Dead pixel indexes: {list(idx_dead)}\n")

        return toa

    def prnu(self, toa, kprnu):
        """
        Adding the PRNU effect
        :param toa: TOA pre-PRNU [e-]
        :param kprnu: multiplicative factor to the standard normal deviation for the PRNU
        :return: TOA after adding PRNU [e-]
        """
        #TODO
        #Get the number of columns in the ACT direction
        ncolumns = toa.shape[1]

        # Model PRNU for each pixel in the ACT direction using a standard normal distribution
        prnu_act = np.random.normal(loc=0.0, scale=1.0, size=ncolumns) * kprnu

        # Apply the error to the whole TOA image
        toa = toa * (1 + prnu_act)

        return toa


    def darkSignal(self, toa, kdsnu, T, Tref, ds_A_coeff, ds_B_coeff):
        """
        Dark signal simulation
        :param toa: TOA in [e-]
        :param kdsnu: multiplicative factor to the standard normal deviation for the DSNU
        :param T: Temperature of the system
        :param Tref: Reference temperature of the system
        :param ds_A_coeff: Empirical parameter of the model 7.87 e-
        :param ds_B_coeff: Empirical parameter of the model 6040 K
        :return: TOA in [e-] with dark signal
        """
        #TODO
        ncolumns = toa.shape[1]

        # Compute DSNU
        dsnu_act = np.abs(np.random.normal(loc=0.0, scale=1.0, size=ncolumns)) * kdsnu

        # Compute Sd
        sd = ds_A_coeff * ((T / Tref) ** 3) * np.exp(-ds_B_coeff * ((1.0 / T) - (1.0 / Tref)))

        # Compute total Dark Signal changes per pixel along the ACT direction
        ds_act = sd * (1.0 + dsnu_act)

        # Add the Dark Signal to the TOA
        toa = toa + ds_act

        return toa
