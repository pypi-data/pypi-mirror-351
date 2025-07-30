import uuid
import numpy as np
from numpy import nan

from astropy.time import Time
from astropy.coordinates import SkyCoord, ICRS
import astropy.units as u

from ctapipe.core import Container, Field
from ctapointing import __version__
from ctapointing.io import from_name


class ImageSolution(Container):
    """
    Container for storing image solutions.
    """

    uuid = Field(None, "UUID", type=str)
    telescope_pointing_ra = Field(
        nan * u.deg, "right ascension coordinate of telescope pointing", unit=u.deg
    )
    telescope_pointing_dec = Field(
        nan * u.deg, "declination coordinate of telescope pointing", unit=u.deg
    )
    telescope_pointing_alt = Field(
        nan * u.deg, "altitude coordinate of telescope pointing", unit=u.deg
    )
    telescope_pointing_az = Field(
        nan * u.deg, "right ascension coordinate of telescope pointing", unit=u.deg
    )
    nominal_telescope_pointing_ra = Field(
        nan * u.deg, "right ascension of nominal telescope pointing", unit=u.deg
    )
    nominal_telescope_pointing_dec = Field(
        nan * u.deg, "declination of nominal telescope pointing", unit=u.deg
    )
    mean_exposure_time = Field(None, "mean time of exposure (UTC)", type=Time)

    #
    # pointing camera parameters and star field
    #
    exposure_duration = Field(nan * u.s, "exposure duration", unit=u.s)
    camera_focal_length = Field(nan * u.m, "pointing camera focal length", unit=u.m)
    camera_rotation = Field(nan * u.deg, "pointing camera rotation", unit=u.deg)
    camera_tilt_x = Field(nan * u.deg, "pointing camera tilt in x", unit=u.deg)
    camera_tilt_y = Field(nan * u.deg, "pointing camera tilt in y", unit=u.deg)
    camera_offset_x = Field(nan * u.m, "pointing camera offset in x", unit=u.m)
    camera_offset_y = Field(nan * u.m, "pointing camera offset in y", unit=u.m)
    camera_chip_temperature = Field(
        nan * u.K, "pointing camera chip temperature", unit=u.K
    )
    camera_temperature = Field(
        nan * u.K, "pointing camera housing temperature", unit=u.K
    )
    camera_humidity = Field(
        -1.0, "pointing camera housing relative humidity", type=float
    )

    num_quad_matches = Field(-1, "number of quad matches", type=int)
    num_quad_matches_selected = Field(-1, "number of selected quad matches", type=int)
    num_iterations_skyfit = Field(-1, "number of iterations for sky fit", type=int)
    num_outliers_skyfit = Field(-1, "number of outliers for sky fit", type=int)
    num_fitted_stars_skyfit = Field(-1, "number of fitted stars in sky fit", type=int)
    residual_mean_x = Field(
        nan * u.arcsec, "mean residual in x of sky fit", unit=u.arcsec
    )
    residual_mean_y = Field(
        nan * u.arcsec, "mean residual in y of sky fit", unit=u.arcsec
    )
    residual_rms_x = Field(
        nan * u.arcsec, "rms residual in x of sky fit", unit=u.arcsec
    )
    residual_rms_y = Field(
        nan * u.arcsec, "rms residual in y of sky fit", unit=u.arcsec
    )
    residual_r68 = Field(
        nan * u.arcsec, "68% containment of residuals of sky fit", unit=u.arcsec
    )
    residual_r95 = Field(
        nan * u.arcsec, "95% containment of residuals of sky fit", unit=u.arcsec
    )
    stars_fit_converged = Field(False, "True if fit converged", type=bool)
    stars_fit_quality = Field(-1.0, "fit function at minimum", type=float)
    stars_fitted_ra = Field(
        None, "RA position of fitted stars", dtype=float, unit=u.deg, ndim=1
    )
    stars_fitted_dec = Field(
        None, "Dec position of fitted stars", dtype=float, unit=u.deg, ndim=1
    )
    stars_fitted_x = Field(None, "x position of fitted stars", dtype=float, ndim=1)
    stars_fitted_y = Field(None, "y position of fitted stars", dtype=float, ndim=1)
    stars_fitted_mag = Field(None, "magnitude of fitted stars", dtype=float, ndim=1)
    star_spots_fitted_ra = Field(
        None, "RA position of fitted spots", dtype=np.float64, ndim=1, unit=u.deg
    )
    star_spots_fitted_dec = Field(
        None, "Dec position of fitted spots", dtype=np.float64, ndim=1, unit=u.deg
    )
    star_spots_fitted_x = Field(
        None, "x position of fitted star spots", dtype=float, ndim=1
    )
    star_spots_fitted_y = Field(
        None, "y position of fitted star spots", dtype=float, ndim=1
    )
    star_spots_fitted_flux = Field(
        None, "intensity of fitted star spots", dtype=float, ndim=1
    )

    mean_background = Field(None, "mean background in image", type=float)

    #
    # science camera parameters and LEDs
    #
    science_camera_focal_length = Field(
        nan * u.m, "science camera focal length", unit=u.m
    )
    science_camera_rotation = Field(nan * u.deg, "science camera rotation", unit=u.deg)
    science_camera_tilt_x = Field(nan * u.deg, "science camera tilt in x", unit=u.deg)
    science_camera_tilt_y = Field(nan * u.deg, "science camera tilt in y", unit=u.deg)
    science_camera_offset_x = Field(nan * u.m, "science camera offset in x", unit=u.m)
    science_camera_offset_y = Field(nan * u.m, "science camera offset in y", unit=u.m)

    science_camera_centre_x = Field(
        None, "x position of science camera centre", type=float
    )
    science_camera_centre_y = Field(
        None, "y position of science camera centre", type=float
    )

    leds_fitted_x = Field(None, "x position of fitted LEDs", dtype=float, ndim=1)
    leds_fitted_y = Field(None, "y position of fitted LEDs", dtype=float, ndim=1)
    led_spots_fitted_x = Field(
        None, "x position of fitted LED spots", dtype=float, ndim=1
    )
    led_spots_fitted_y = Field(
        None, "y position of fitted LED spots", dtype=float, ndim=1
    )
    led_fit_quality = Field(-1.0, "LED fit function at minimum", type=float)

    #
    # spots on camera lid
    #
    lid_spots_x = Field(None, "x position of lid spots", dtype=float, ndim=1)
    lid_spots_y = Field(None, "y position of lid spots", dtype=float, ndim=1)

    registration_time = Field(None, "registration time", unit=u.s)
    matching_time = Field(None, "matching time", unit=u.s)
    fitting_time = Field(None, "fitting time", unit=u.s)

    spotlist_uuid = Field(None, "SpotList UUID", type=str)
    image_uuid = Field(None, "image UUID", type=str)
    when_solved = Field(None, "time of solving", type=str)

    def __init__(self, prefix=None, **fields):
        super().__init__(prefix=prefix, **fields)

        # generate a new UUID if not provided by field import
        if getattr(self, "uuid") is None:
            setattr(self, "uuid", str(uuid.uuid4()))

        if "CTAPOINTING_VERSION" not in self.meta:
            self.meta["CTAPOINTING_VERSION"] = __version__

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = f"{self.__class__.__name__}(uuid={self.uuid}"
        s += f", spotlist_id={self.spotlist_uuid})"
        return s

    @classmethod
    def from_name(cls, name, **kwargs):
        """
        Load ImageSolution from HDF5 file or database. See `ctapointing.io.from_name()` for details.
        """
        return from_name(name, cls, **kwargs)

    @property
    def telescope_pointing(self):
        try:
            return SkyCoord(
                self.telescope_pointing_ra,
                self.telescope_pointing_dec,
                frame=ICRS,
            )
        except TypeError:
            return None
