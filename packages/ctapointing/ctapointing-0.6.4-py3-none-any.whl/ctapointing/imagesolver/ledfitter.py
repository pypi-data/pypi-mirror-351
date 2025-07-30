import numpy as np
import uuid
from scipy.spatial import KDTree
from scipy.optimize import least_squares

from iminuit import Minuit
import astropy.units as u

from ctapipe.core import Component
from ctapipe.core.traits import (
    Float,
    Unicode,
    List,
)

from ctapointing.config import from_config
from .imagesolution import ImageSolution

DISTANCE_GOAL = 1  # distance goal for spot-LED matching in pixels


class LEDFitter(Component):
    """
    LED fitting class.

    TODO: If we can really base this on a cicle fit, consider using the method
    proposed in https://link.springer.com/content/pdf/10.1007/s10851-010-0249-8.pdf

    """

    uuid = Unicode(default_value=str(uuid.uuid4()), help="UUID of LEDFitter").tag(
        config=True
    )
    name = Unicode(help="name of LEDFitter").tag(config=True)
    matching_distance = Float(
        default_value=100,
        help="maximum distance between spot and predicted LED position (in pixels",
    ).tag(config=True)
    distance_goal = Float(default_value=0.1, help="fit distance goal").tag(config=True)
    fixed_parameters = List(
        default_value=[], help="list of parameters fixed during fitting"
    ).tag(config=True)

    def __str__(self):
        s = self.__repr__()
        return s

    def __repr__(self):
        return f"{self.__class__.__name__}" f"(uuid={self.uuid}, name={self.name}, "

    @classmethod
    def from_config(cls, **kwargs):
        """
        Read a LEDFitter configuration from either configuration file or database.
        Either the path of a configuration file ('input_url') or a database collection
        ('collection') must be provided.

        Parameters
        ----------
        input_url: str or Path
            path of the configuration file.
        name: str
            name of the LEDExtractor (as in `LEDFitter.name`).
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
        extractor: LEDFitter object or None
        """
        # load configuration and construct instance
        config = from_config(component_name=cls.__name__, **kwargs)
        return cls(config=config)

    def process(self, spotlist, exposure, science_camera, image_solution=None):
        """
        Fit a list of spots to science camera LEDs to find the transformation between
        pointing camera pixel coordinates and science camera coordinates.

        Parameters
        ----------
        spotlist: ctapointing.imagesolver.SpotList
            spotlist of extracted LED spots
        exposure: Exposure
            exposure object, holding information about the actual exposure (camera properties etc.)
        science_camera: ctapointing.camera.ScienceCamera
            science camera object, storing the geometric properties of the science camera (LED positions etc.)
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
        coords_spots = spotlist.coords_pix

        if len(coords_spots) < 3:
            self.log.warning(f"not enough LEDs ({len(coords_spots)}) to perform fit")
        #            return (np.nan, np.nan), np.nan, np.nan, np.array([np.nan, np.nan])

        self.log.debug("spot coordinates:")
        self.log.debug(coords_spots)

        # project LEDs into pointing camera, using transformation parameters
        # currently stored in the science_camera object
        coords_leds = exposure.transform_to_camera(
            science_camera.led_positions, to_pixels=True
        )

        self.log.debug("LED coordinates:")
        self.log.debug(coords_leds)

        # match spots to LEDs
        pos_tree = KDTree(coords_leds)
        spot_tree = KDTree(coords_spots)

        matches = pos_tree.query_ball_tree(spot_tree, r=self.matching_distance)

        led_number_matched = []
        coords_leds_mask = [False] * len(coords_leds)
        coords_spots_matched = []
        for idx, match in enumerate(matches):
            if len(match) == 0:
                continue

            coords_leds_mask[idx] = True
            led_number_matched.append(idx)
            coords_spots_matched.append(
                [coords_spots[match[0], 0], coords_spots[match[0], 1]]
            )

        coords_spots_matched = np.array(coords_spots_matched)
        self.log.debug("matched spots:")
        self.log.debug(coords_spots_matched)

        coords_leds_matched = coords_leds[coords_leds_mask]
        self.log.debug("matched LEDs:")
        self.log.debug(coords_leds_matched)

        if len(coords_spots_matched) < 3:
            self.log.warning(
                f"not enough spots ({len(coords_spots_matched)}) matched for fit."
            )
            return (np.nan, np.nan), np.nan, np.nan, np.array([np.nan, np.nan])

        # fit matched spots to true camera LED positions
        def cost_function(focal_length, rotation, tilt_x, tilt_y, offset_x, offset_y):
            # set transformation properties of ScienceCameraFrame
            science_camera.focal_length = focal_length * u.m
            science_camera.rotation = rotation * u.deg
            science_camera.tilt[0] = tilt_x * u.deg
            science_camera.tilt[1] = tilt_y * u.deg
            science_camera.offset[0] = offset_x * u.m
            science_camera.offset[1] = offset_y * u.m

            # do transformation (for LEDs previously matched to spots)
            coords_leds_matched = exposure.transform_to_camera(
                science_camera.led_positions[coords_leds_mask]
            )
            coords_leds_matched = exposure.camera.transform_to_pixels(
                coords_leds_matched
            )

            # compare to spots
            distance = np.hypot(
                coords_leds_matched[:, 0] - coords_spots_matched[:, 0],
                coords_leds_matched[:, 1] - coords_spots_matched[:, 1],
            )

            distance2 = (distance / DISTANCE_GOAL) ** 2
            chi2 = np.sum(distance2)

            return chi2

        self.log.info("performing full LED fit")
        m = Minuit(
            cost_function,
            focal_length=science_camera.focal_length.to_value(u.m),
            rotation=science_camera.rotation.to_value(u.deg),
            tilt_x=science_camera.tilt[0].to_value(u.deg),
            tilt_y=science_camera.tilt[1].to_value(u.deg),
            offset_x=science_camera.offset[0].to_value(u.m),
            offset_y=science_camera.offset[1].to_value(u.m),
        )
        m.errordef = Minuit.LEAST_SQUARES

        m.fixed[4] = True
        m.fixed[5] = True

        m.migrad()

        # write best-fit parameters to science_camera
        science_camera.focal_length = m.values[0] * u.m
        science_camera.rotation = m.values[1] * u.deg
        science_camera.tilt_x = m.values[2] * u.deg
        science_camera.tilt_y = m.values[3] * u.deg
        science_camera.offset_x = m.values[4] * u.m
        science_camera.offset_y = m.values[4] * u.m

        # transform LED positions using best-fit parameters
        coords_leds_final = exposure.transform_to_camera(
            science_camera.led_positions[coords_leds_mask]
        )
        coords_leds_final = exposure.camera.transform_to_pixels(coords_leds_final)

        # transform science camera centre
        science_camera_centre_pix = exposure.transform_to_camera(
            science_camera.centre, to_pixels=True
        )

        self.log.debug("final LED positions:")
        self.log.debug(coords_leds_final)

        self.log.debug("spot positions:")
        self.log.debug(coords_spots_matched)

        # store results in ImageSolution
        if image_solution is None:
            image_solution = ImageSolution()

        image_solution.led_fit_quality = m.fmin.fval / m.ndof if m.ndof > 0 else -1.0

        image_solution.science_camera_focal_length = (
            science_camera.sciencecameraframe.focal_length
        )
        image_solution.science_camera_rotation = (
            science_camera.sciencecameraframe.rotation
        )
        image_solution.science_camera_tilt_x = science_camera.sciencecameraframe.tilt_x
        image_solution.science_camera_tilt_y = science_camera.sciencecameraframe.tilt_y
        image_solution.science_camera_offset_x = (
            science_camera.sciencecameraframe.offset_x
        )
        image_solution.science_camera_offset_y = (
            science_camera.sciencecameraframe.offset_y
        )

        image_solution.science_camera_centre_x = science_camera_centre_pix[0][0]
        image_solution.science_camera_centre_y = science_camera_centre_pix[0][1]

        image_solution.leds_fitted_x = coords_leds_final[:, 0]
        image_solution.leds_fitted_y = coords_leds_final[:, 1]
        image_solution.led_spots_fitted_x = coords_spots_matched[:, 0]
        image_solution.led_spots_fitted_y = coords_spots_matched[:, 1]

        return image_solution, m, coords_leds_final, coords_spots_matched

    @staticmethod
    def circlefit(spotlist):
        """
        Fit a circle to all coordinates of the spotlist.
        """

        def calculate_radius(centre):
            """
            Calculate circle radius, based on assumed centre
            and spot coordinates:

            radius = sqrt((x-centre_x)**2 + (y-centre_y)**2)
            """
            return np.hypot((coords - centre)[:, 0], (coords - centre)[:, 1])

        def fcn(centre):
            """
            Cost function. Minimise the distance of each
            spot to the circle as a function of the
            circle's centre.
            """
            radii = calculate_radius(centre)
            return radii - radii.mean()

        coords = spotlist.coords_pix
        if len(coords) < 3:
            return (None, None), None, None

        centre_start = np.mean(coords, axis=0)

        result = least_squares(fcn, centre_start)
        centre = result.x
        residuals = result.fun

        # calculate final radius
        radius = calculate_radius(centre).mean()

        return centre, radius, residuals

    @staticmethod
    def construct_leds_on_circle(radius, position_angles, centre=None):
        """
        Construct LED position coordinates in the CTA CameraFrame
        (i.e. x points down, y points left when viewed from the dish)

        radius: circle radius
        position_angles: list of position angles

        returns:
        array of coordinates
        """

        x = (-radius * np.cos(position_angles)).reshape(-1, 1)
        y = (radius * np.sin(position_angles)).reshape(-1, 1)

        if centre is not None:
            x = x + centre[0]
            y = y + centre[1]

        return np.concatenate((x, y), axis=1)
