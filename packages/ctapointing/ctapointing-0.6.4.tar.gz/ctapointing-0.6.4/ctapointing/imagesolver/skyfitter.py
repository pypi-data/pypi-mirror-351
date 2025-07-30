import numpy as np
import uuid
import time

import astropy.units as u
from astropy.coordinates import SkyCoord, ICRS
from astropy.time import Time

from iminuit import Minuit
from iminuit.util import describe

from ctapipe.core import Component
from ctapipe.core.traits import (
    Float,
    Unicode,
    Int,
    List,
    Bool,
)

from ctapointing.camera import DistortionCorrectionNull
from ctapointing.config import from_config
from .statusbase import Status
from .imagesolution import ImageSolution

DISTANCE_GOAL = 1  # distance goal for spot-star matching in pixels


def model_sky_to_pixels(
    star_coords_altaz,
    exposure,
    ra,
    dec,
    focal_length,
    rotation,
    tilt_x,
    tilt_y,
    offset_x,
    offset_y,
    **dist_coeff,
):
    """
    Model function to project star coordinates into the pointing camera pixel chip,
    given a telescope orientation and a set of camera parameters.

    Returns: list of star coordinates in camera pixels
    """

    # set observation direction, camera rotation and scale
    exposure.telescope_pointing = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame=ICRS)

    camera = exposure.camera
    camera.focal_length = [focal_length] * 2 * u.m
    camera.rotation = rotation * u.deg
    camera.tilt[0] = tilt_x * u.deg
    camera.tilt[1] = tilt_y * u.deg
    camera.offset[0] = offset_x * u.m
    camera.offset[1] = offset_y * u.m

    # set distortion model parameters, if applicable
    for k in dist_coeff:
        camera.distortion_correction.coeff_inv[k] = dist_coeff[k]

    # for now, we fit on the camera chip, because this allows to
    # comfortably set the frame attributes of the SkyCameraFrame.
    star_coords_pix = exposure.transform_to_camera(star_coords_altaz, to_pixels=True)

    return star_coords_pix


def model_pixels_to_intermediate_pixels(spot_coords_pix, exposure, **dist_coeff):
    camera = exposure.camera
    for k in dist_coeff:
        camera.distortion_correction.coeff[k] = dist_coeff[k]

    spot_coords_skycam = camera.transform_to_camera(spot_coords_pix)
    spot_coords_pix_new = camera.transform_to_pixels(spot_coords_skycam)

    return spot_coords_pix_new


class Leastsquares:
    """
    Implementation of iminuit cost function for star-spot fitting.
    """

    errordef = Minuit.LEAST_SQUARES

    def __init__(self, model, exposure, ref_coords_pix=None, coords=None):
        """
        coords: coordinates to be transformed
        ref_coords: reference coordinates w.r.t. which transformation is optimised
        """
        self.model = model
        self.exposure = exposure
        self.coords = coords
        self.ref_coords_pix = ref_coords_pix

        camera = exposure[0].camera
        self.num_camera_parameters = 6
        self.num_distortion_parameters = len(camera.distortion_correction.coeff)

        self.list_of_variables = describe(model)[4 : 4 + self.num_camera_parameters]
        for k in camera.distortion_correction.coeff_inv:
            self.list_of_variables.append(k)
        for i in range(len(exposure)):
            self.list_of_variables.append(f"ra{i}")
            self.list_of_variables.append(f"dec{i}")

        # make parameters known to iminuit
        self._parameters = {k: None for k in self.list_of_variables}

    @property
    def ndata(self):
        """
        report number of data points for calculation of reduced chi2
        """
        # number of images x number of spots per image
        return np.sum(np.array([len(s) for s in self.coords]))

    def __call__(self, *par):
        """
        iminuit cost function called during the fitting process.
        *par: list of parameters to be optimised. These are handed over to the model function.
        """

        # call minimisation function for each supplied exposure and sum the chi2
        chi2 = 0
        for i, exp in enumerate(self.exposure):
            # the vector of model parameters starts with camera parameters, which
            # are assumed to be identical for all exposures...
            camera_parameters = par[: self.num_camera_parameters]
            distortion_parameters = {}
            for j in range(self.num_distortion_parameters):
                name = self.list_of_variables[self.num_camera_parameters + j]
                distortion_parameters[name] = par[self.num_camera_parameters + j]

            # ...followed by the (ra,dec) orientation of each exposure, which we
            # extract for the given exposure
            idx_image_params = (
                self.num_camera_parameters + self.num_distortion_parameters + 2 * i
            )
            image_parameters = par[idx_image_params : idx_image_params + 2]

            # transform coordinates into pixel coordinates
            fit_parameters = image_parameters + camera_parameters
            transformed_coords_pix = self.model(
                self.coords[i], exp, *fit_parameters, **distortion_parameters
            )

            # minimize sum of quadratic distances between reference coordinates and
            # transformed coordinates
            distance2 = np.sum(
                (transformed_coords_pix - self.ref_coords_pix[i]) ** 2, axis=1
            )
            distance2 = distance2 / DISTANCE_GOAL**2

            use_soft_outliers = False
            # "non-linear" soft loss function to penalise outliers
            # see e.g. iminuit.cost.LeastSquares
            if use_soft_outliers:
                chi2 += np.sum((2 * np.sqrt(1 + distance2) - 2) ** 2)
            else:
                chi2 += np.sum(distance2)

        return chi2


class LeastsquaresInverse:
    """
    Implementation of iminuit cost function for inverse spot-spot fitting.
    """

    errordef = Minuit.LEAST_SQUARES

    def __init__(self, model, exposure, ref_coords_pix=None, coords=None):
        """
        coords: coordinates to be transformed
        ref_coords: reference coordinates w.r.t. which transformation is optimised
        """
        self.model = model
        self.exposure = exposure
        self.coords = coords
        self.ref_coords_pix = ref_coords_pix

        camera = exposure[0].camera
        self.list_of_variables = []
        for k in camera.distortion_correction.coeff:
            self.list_of_variables.append(k)

        self._parameters = {k: None for k in self.list_of_variables}

    @property
    def ndata(self):
        """
        report number of data points for calculation of reduced chis2
        """
        return len(self.coords)

    def __call__(self, *par):
        """
        iminuit cost function called during the fitting process.
        *par: list of parameters to be optimised. These are handed over to the model function.
        """

        distortion_parameters = {}
        for j in range(len(self.list_of_variables)):
            name = self.list_of_variables[j]
            distortion_parameters[name] = par[j]

        # call minimisation function for each supplied exposure and sum the chi2
        chi2 = 0
        for i, exp in enumerate(self.exposure):
            # transform from pixel coordinates to SkyCam coordinates and back, using
            # (fixed) distortion model for the SkyCam->pixel transformation and
            # the to-be-optimised distortion model for the pixel->SkyCam transformation
            transformed_coords_pix = self.model(
                self.coords[i], exp, **distortion_parameters
            )

            # minimize sum of quadratic distances between reference coordinates and
            # transformed coordinates
            distance2 = np.sum(
                (transformed_coords_pix - self.ref_coords_pix[i]) ** 2, axis=1
            )
            distance2 = distance2 / DISTANCE_GOAL**2

            use_soft_outliers = False
            # "non-linear" soft loss function to penalise outliers
            # see e.g. iminuit.cost.LeastSquares
            if use_soft_outliers:
                chi2 += np.sum((2 * np.sqrt(1 + distance2) - 2) ** 2)
            else:
                chi2 += np.sum(distance2)

        return chi2


class SkyFitter(Component):
    """
    Sky fitting class

    Fits a list of spots to matched stars using the full
    transformation tree or an astropy WCS transformation
    """

    uuid = Unicode(default_value=str(uuid.uuid4()), help="UUID of SkyFitter").tag(
        config=True
    )
    name = Unicode(help="name of SkyFitter").tag(config=True)
    max_num_fit_iterations = Int(
        default_value=10, help="maximum number of fit iterations"
    ).tag(config=True)
    distance_goal = Float(default_value=0.1, help="fit distance goal").tag(config=True)
    fixed_parameters = List(
        default_value=[], help="list of parameters fixed during fitting"
    ).tag(config=True)
    fit_camera_distortion = Bool(
        default_value=False, help="fit camera distortion parameters"
    ).tag(config=True)
    residual_cut = Float(
        default_value=3.0, help="cut value for spot outlier removal"
    ).tag(config=True)

    def __str__(self):
        s = self.__repr__()
        return s

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(uuid={self.uuid}, name={self.name}, "
            f"fit_camera_distortion={self.fit_camera_distortion}, "
            f"max_num_fit_iterations={self.max_num_fit_iterations})"
        )

    @classmethod
    def from_config(cls, **kwargs):
        """
        Read a SkyFitter configuration from either configuration file or database.
        Either the path of a configuration file ('input_url') or a database collection
        ('collection') must be provided.


        Parameters
        ----------
        input_url: str or Path
            path of the configuration file.
        name: str
            name of the SpotExtractor (as in `SkyFitter.name`).
            When loading the configuration from file, can be set to check that the configuration with the
            correct name is loaded.
            When loading from database, is used to identify the correct database record.
        uuid: str
            UUID of the camera (as in `PointingCamera.uuid`).
            When loading the configuration from file, can be set to check that the configuration with the
            correct UUID is loaded.
            When loading from database, is used to identify the correct database record.
        collection: str
            name of the database collection from which
            configuration is read
        database: str
            name of the database in which the collection
            is stored

        Returns
        -------
        fitter: SkyFitter object or None
        """
        # load configuration and construct instance
        config = from_config(component_name=cls.__name__, **kwargs)
        return cls(config=config)

    def process(
        self,
        spot_star_match_list,
        exposure,
        estimated_pointing=None,
        distortion_correction=None,
        image_solution=None,
    ):
        """
        Fit a list of spots to pre-matched stars to find the transformation parameters
        for coordinate transformations from pixel coordinates to sky coordinates.

        The fit uses the full (non-idealised) set of coordinate transformations, taking
        into account refraction effects in the atmosphere and lens distortion.

        Parameters
        ----------
        spot_star_match_list: list
            list of StarSpotMatch objects that contain information about the pre-matched spot-star pairs
        exposure: Exposure
            exposure object, holding information about the actual exposure (camera properties etc.)
        estimated_pointing: astropy.SkyCoord
            estimated telescope pointing position (in the ICRS frame)
        image_solution: ctapointing.imagesolver.ImageSolution
            image solution object that is updated with fit results. If None, a new object is created.

        Returns
        -------
        solution: ImageSolution
            ImageSolution object containing summary information on the result
        m: iminuit.minuit
            minuit object for the sky -> pixels fit
        m_inv: iminuit.minuit
            minuit object for the pixel -> intermediate pixel coordinates fit
        """

        if not isinstance(spot_star_match_list[0], list | tuple):
            spot_star_match_list = [spot_star_match_list]
        if not isinstance(exposure, list | tuple):
            exposure = [exposure]
        if estimated_pointing is None:
            estimated_pointing = [None] * len(exposure)
        elif not isinstance(estimated_pointing, list | tuple):
            estimated_pointing = [estimated_pointing]

        # if ImageSolution object not provided, create one.
        if image_solution is None:
            image_solution = [ImageSolution() for i in range(len(exposure))]
        elif not isinstance(image_solution, list | tuple):
            image_solution = [image_solution]

        if len(image_solution) != len(exposure):
            raise AttributeError(
                "size of list of exposures must match that of image_solution."
            )

        # make sure a DistortionCorrection object is available
        camera = exposure[0].camera
        if distortion_correction is not None:
            camera.distortion_correction = distortion_correction
        elif camera.distortion_correction is None:
            camera.distortion_correction = DistortionCorrectionNull()

        self.log.info(
            f"performing iterative sky fitting (max iterations {self.max_num_fit_iterations})"
        )

        start_fitting = time.perf_counter()

        # Step 1: fit transformation from sky to camera pixels, including distortion corrections
        # Do this in several iterations, removing far-away outliers that are presumably wrong
        # associations

        # least-square minimisation, using the sky_to_pixels transformation function to
        # transform altaz star coordinates into pixel coordinates and minimise w.r.t.
        # true spot coordinates
        lsq = Leastsquares(model_sky_to_pixels, exposure)

        # set (ra,dec) start parameters for all exposures
        fit_parameters = {}
        for i, exp in enumerate(exposure):
            self.log.info(f"fitting exposure {exp.uuid}")

            if estimated_pointing[i] is None:
                if exp.nominal_telescope_pointing is not None:
                    estimated_pointing[i] = exp.nominal_telescope_pointing
                else:
                    raise AttributeError(
                        f"no estimated pointing position provided for exposure {i}, "
                        f"and nominal pointing position not set"
                    )

            fit_parameters[f"ra{i}"] = estimated_pointing[i].ra.to_value(u.deg)
            fit_parameters[f"dec{i}"] = estimated_pointing[i].dec.to_value(u.deg)

            image_solution[i]["nominal_telescope_pointing_ra"] = estimated_pointing[
                i
            ].ra
            image_solution[i]["nominal_telescope_pointing_dec"] = estimated_pointing[
                i
            ].dec

        # set camera parameters common for all exposures
        fit_parameters["focal_length"] = camera.focal_length[0].to_value(u.m)
        fit_parameters["rotation"] = camera.rotation.to_value(u.deg)
        fit_parameters["tilt_x"] = camera.tilt[0].to_value(u.deg)
        fit_parameters["tilt_y"] = camera.tilt[1].to_value(u.deg)
        fit_parameters["offset_x"] = camera.offset[0].to_value(u.m)
        fit_parameters["offset_y"] = camera.offset[1].to_value(u.m)

        for k in camera.distortion_correction.coeff_inv:
            fit_parameters[k] = camera.distortion_correction.coeff_inv[k]

        m = Minuit(lsq, **fit_parameters)

        # limit sky coordinates to avoid running out of domain
        for i, exp in enumerate(exposure):
            m.limits[f"ra{i}"] = (0.0, 360.0)
            m.limits[f"dec{i}"] = (-90.0, 90.0)

        # mark parameters as fixed if requested
        if self.fit_camera_distortion is False:
            for k in camera.distortion_correction.coeff_inv:
                m.fixed[k] = True

        for par in self.fixed_parameters:
            m.fixed[par] = True

        self.num_fitted_star_spot_matches = len(spot_star_match_list)

        self.log.info(f"fit starting values:\n{m.init_params}")

        num_fits = 1
        while num_fits <= self.max_num_fit_iterations:
            coords_list = []
            ref_coords_list = []
            for i, exp in enumerate(exposure):
                # prepare match list: fit only those combinations
                # which have not been marked as OUTLIER during a preceding fit
                match_list = [
                    s
                    for s in spot_star_match_list[i]
                    if not s.spot.has_status(Status.OUTLIER)
                ]

                self.log.info(
                    f"iteration {num_fits}/{self.max_num_fit_iterations}: exposure {i}:"
                    f" fitting {len(match_list)} star-spot matches"
                )

                stars = [s.star for s in match_list]
                star_coords = SkyCoord([s.coords_radec for s in stars])
                star_coords_altaz = star_coords.transform_to(exp.altazframe)
                coords_list.append(star_coords_altaz)

                spots = [s.spot for s in match_list]
                spot_coords_pix = np.array([s.coords_pix for s in spots])
                ref_coords_list.append(spot_coords_pix)

            # update data in minimisation object
            lsq.coords = coords_list
            lsq.ref_coords_pix = ref_coords_list

            # minimise
            m.migrad()

            # calculate residuals:
            # transform star radec positions to pixel coordinates
            # using best-fit pointing solution and compare to spot
            # positions
            total_num_outliers = 0
            for i, exp in enumerate(exposure):
                # update exposure object with best-fit values
                exp.telescope_pointing = SkyCoord(
                    ra=m.values[f"ra{i}"] * u.deg,
                    dec=m.values[f"dec{i}"] * u.deg,
                    frame=ICRS,
                )

                exp.camera.focal_length = [m.values["focal_length"]] * 2 * u.m
                exp.camera.rotation = m.values["rotation"] * u.deg
                exp.camera.tilt[0] = m.values["tilt_x"] * u.deg
                exp.camera.tilt[1] = m.values["tilt_y"] * u.deg
                exp.camera.offset[0] = m.values["offset_x"] * u.m
                exp.camera.offset[1] = m.values["offset_y"] * u.m

                if self.fit_camera_distortion:
                    if exp.camera.distortion_correction is None:
                        exp.camera.distortion_correction = DistortionCorrectionNull()

                    for k in exp.camera.distortion_correction.coeff_inv:
                        exp.camera.distortion_correction.coeff_inv[k] = m.values[k]

                match_list = [
                    s
                    for s in spot_star_match_list[i]
                    if not s.spot.has_status(Status.OUTLIER)
                ]

                stars = [s.star for s in match_list]
                star_coords = SkyCoord([s.coords_radec for s in stars])
                star_coords_pix = exp.transform_to_camera(star_coords, to_pixels=True)
                star_mag = np.array([s.mag for s in stars])

                spot_coords_pix = np.array([s.spot.coords_pix for s in match_list])
                spot_flux = np.array([s.spot.flux for s in match_list])

                delta = (
                    np.array(star_coords_pix - spot_coords_pix) * exp.camera.pixel_angle
                )
                delta_mean = np.mean(delta, axis=0)
                delta_rms = np.std(delta, axis=0)

                self.log.info(f"exposure {i}: number of fitted stars: {len(delta)}")
                self.log.debug(
                    f"residual mean (chip): {delta_mean[0]}, {delta_mean[1]}"
                )
                self.log.debug(f"residual rms (chip): {delta_rms[0]}, {delta_rms[1]}")

                mask_outliers = (
                    np.abs(delta - delta_mean) > self.residual_cut * delta_rms
                )
                mask_outliers = np.any(mask_outliers, axis=1)
                num_outliers = np.count_nonzero(mask_outliers)
                self.log.info(f"number of outliers: {num_outliers}")

                # mask outliers in spot list
                for j in range(len(mask_outliers)):
                    if mask_outliers[j]:
                        match_list[j].spot.set_status(Status.OUTLIER)

                total_num_outliers += num_outliers

                image_solution[i].residual_mean_x = delta_mean[0]
                image_solution[i].residual_mean_y = delta_mean[1]
                image_solution[i].residual_rms_x = delta_rms[0]
                image_solution[i].residual_rms_y = delta_rms[1]
                image_solution[i].num_outliers_skyfit = num_outliers
                image_solution[i].num_fitted_stars_skyfit = len(delta)
                image_solution[i].stars_fitted_ra = star_coords.ra
                image_solution[i].stars_fitted_dec = star_coords.dec
                image_solution[i].stars_fitted_x = star_coords_pix[:, 0]
                image_solution[i].stars_fitted_y = star_coords_pix[:, 1]
                image_solution[i].stars_fitted_mag = star_mag
                image_solution[i].star_spots_fitted_x = spot_coords_pix[:, 0]
                image_solution[i].star_spots_fitted_y = spot_coords_pix[:, 1]
                image_solution[i].star_spots_fitted_flux = spot_flux
                image_solution[i].stars_fit_converged = m.valid
                image_solution[i].stars_fit_quality = (
                    m.fmin.fval / m.ndof if m.ndof > 0 else -1.0
                )

            # stop fitting if no outliers left
            if total_num_outliers == 0:
                break

            num_fits += 1

        if m.valid:
            self.log.info("fit converged.")
        else:
            self.log.warn("fit did not converge.")
        self.log.info(f"fit status:\n{m.fmin}")
        self.log.info(f"{m.fmin.fval}, {m.ndof}, {m.fmin.reduced_chi2}")
        self.log.info(f"best-fit values:\n{m.params}")
        try:
            self.log.info(f"correlation matrix:\n{m.covariance.correlation()}")
        except AttributeError:
            pass

        # Step 2: fit transformation from camera pixels to intermediate camera coordinates
        # to determine the inverse distortion corrections
        m_inv = None
        if self.fit_camera_distortion:
            lsq_inv = LeastsquaresInverse(model_pixels_to_intermediate_pixels, exposure)

            # read inverse distortion parameters from camera object
            camera = exposure[0].camera

            # only fit if distortion model contains parameters (avoid fitting Null model)
            if len(camera.distortion_correction.coeff) > 0:
                m_inv = Minuit(
                    lsq_inv,
                    **camera.distortion_correction.coeff,
                )
                # m_inv.errordef = Minuit.LEAST_SQUARES

                coords_list = []
                for i, exp in enumerate(exposure):
                    # prepare match list: fit only those combinations
                    # which have not been marked as OUTLIER during a preceding fit
                    match_list = [
                        s
                        for s in spot_star_match_list[i]
                        if not s.spot.has_status(Status.OUTLIER)
                    ]

                    self.log.info(
                        f"exposure {i}: inverse transform: fitting {len(match_list)} spot-spot matches"
                    )

                    spot_coords_pix = [s.spot.coords_pix for s in match_list]
                    coords_list.append(spot_coords_pix)

                # minimise
                lsq_inv.coords = coords_list
                lsq_inv.ref_coords_pix = coords_list
                m_inv.migrad()

                # update exposure objects
                for i, exp in enumerate(exposure):
                    for k in exp.camera.distortion_correction.coeff:
                        exp.camera.distortion_correction.coeff[k] = m_inv.values[k]

        # Step 3: calculate residual in RADec and store results
        #
        when_solved = Time.now()
        when_solved.format = "fits"

        stop_fitting = time.perf_counter()
        fitting_time = (stop_fitting - start_fitting) * u.s

        for i, exp in enumerate(exposure):
            match_list = [
                s
                for s in spot_star_match_list[i]
                if not s.spot.has_status(Status.OUTLIER)
            ]

            # transform spot coordinates to RADec and calculate 68% and 95%
            # containment distances
            spot_coords_pix = [s.spot.coords_pix for s in match_list]
            spot_coords_skycam = exp.camera.transform_to_camera(spot_coords_pix)
            spot_coords_radec = exp.transform_to_sky(spot_coords_skycam)

            star_coords = SkyCoord([s.star.coords_radec for s in match_list])

            angular_distance = star_coords.separation(spot_coords_radec)
            angular_distance.sort()

            n68 = int(np.floor(0.68 * len(angular_distance)))
            n95 = int(np.floor(0.95 * len(angular_distance)))

            residual_radec_r68 = angular_distance[n68]
            residual_radec_r95 = angular_distance[n95]

            self.log.info(
                f"exposure {i}: angular distance (68%/95%): {residual_radec_r68.to(u.arcsec):.2f}/"
                f"{residual_radec_r95.to(u.arcsec):.2f}"
            )

            image_solution[i].telescope_pointing_ra = exp.telescope_pointing.ra
            image_solution[i].telescope_pointing_dec = exp.telescope_pointing.dec
            image_solution[i].telescope_pointing_alt = exp.telescope_pointing_altaz.alt
            image_solution[i].telescope_pointing_az = exp.telescope_pointing_altaz.az

            image_solution[i].star_spots_fitted_ra = spot_coords_radec.ra
            image_solution[i].star_spots_fitted_dec = spot_coords_radec.dec

            image_solution[i].camera_focal_length = exp.camera.focal_length[0]
            image_solution[i].camera_rotation = exp.camera.rotation
            image_solution[i].camera_tilt_x = exp.camera.tilt[0]
            image_solution[i].camera_tilt_y = exp.camera.tilt[1]
            image_solution[i].camera_offset_x = exp.camera.offset[0]
            image_solution[i].camera_offset_y = exp.camera.offset[1]
            image_solution[i].num_iterations_skyfit = num_fits
            image_solution[i].num_outliers_skyfit = np.count_nonzero(
                [
                    True
                    for s in spot_star_match_list[i]
                    if s.spot.has_status(Status.OUTLIER)
                ]
            )
            image_solution[i].num_fitted_stars_skyfit = len(match_list)
            image_solution[i].residual_r68 = residual_radec_r68.to(u.arcsec)
            image_solution[i].residual_r95 = residual_radec_r95.to(u.arcsec)

            image_solution[i].fitting_time = fitting_time
            image_solution[i].when_solved = when_solved.fits

            image_solution[i].mean_exposure_time = exp.mean_exposure_time
            image_solution[i].exposure_duration = exp.duration

        self.log.info(f"finished sky fitting ({fitting_time:.2f}).")

        if len(image_solution) > 1:
            return image_solution, m, m_inv
        else:
            return image_solution[0], m, m_inv

    # @classmethod
    # def fit_wcs(cls, exposure, star_spot_match_list, sip_degree=0, fix_proj_point=True):
    #     if len(star_spot_match_list) == 0:
    #         return None
    #
    #     x_pix = []
    #     y_pix = []
    #     ra = []
    #     dec = []
    #     for match in star_spot_match_list:
    #         x_pix.append(match.spot.coords_pix[1])
    #         y_pix.append(match.spot.coords_pix[0])
    #
    #         ra.append(match.star.coords_radec.ra)
    #         dec.append(match.star.coords_radec.dec)
    #
    #     x_pix = np.array(x_pix)
    #     y_pix = np.array(y_pix)
    #
    #     star_coords = SkyCoord(ra=ra, dec=dec, frame=ICRS)
    #
    #     wcs = fit_wcs_from_points(
    #         (x_pix, y_pix),
    #         star_coords,
    #         proj_point=exposure.nominal_telescope_pointing,
    #         sip_degree=sip_degree,
    #         fix_proj_point=fix_proj_point,
    #     )
    #
    #     return wcs
