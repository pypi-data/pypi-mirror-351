import time
import uuid

import numpy as np
from scipy.spatial import KDTree
from skimage.transform import SimilarityTransform
import astropy.units as u
from astropy.coordinates import SkyCoord, ICRS

from ctapipe.core import Component
from ctapipe.core.traits import (
    Float,
    Unicode,
    Int,
)

from ctapointing.catalog import query_catalog
from ctapointing.config import from_config
from .registration import Registration, Spot, Star, StarSpotMatch
from .statusbase import Status
from .imagesolution import ImageSolution

N_FIELD_MATCH_EXP = 2


def match_field(
    quad_match,
    stars,
    spots,
    radius,
    min_matches=5,
):
    """
    Based on (a list of) QuadMatch objects, match a list of stars to
    a list of spots. Matching is done based on nearest neighbourhood in
    SkyCameraFrame coordinates, using an efficient kd tree with k=2.

    For the matching to work, similarity transformation parameters must
    exist for any QuadMatch object.

    For the field matching to be successful, certain quality criteria
    have to be met (see below).

    For all field-matched QuadMatch objects, a list of SpotStarMatch
    objects is created which store the Star and corresponding Spot
    object. The status flag of these QuadMatch objects is set to
    FIELDMATCHED.

    Parameters
    ----------
    quad_match: list
        list of QuadMatch objectsFor each object, a matching is performed.
    stars: list
        list of Star objects for matching
    spots: list
        list of Spot objects for matching
    radius: Float
        search radius (in SkyCameraFrame coordinate space) for accepted spot-star matches
    min_matches: Int
        minimum number of spot-star matches required to accept the matching (including the 3 stars
        and 3 spots from the original QuadMatch)
    min_matches: Int
        minimum fraction of all stars that must be matched to accept the matching

    Returns
    -------
    n_matched: Int
        number of successful spot-star matches
    """

    # before matching, recalculate position of stars on the chip
    # for this quad solution
    t = SimilarityTransform(quad_match.transformation_properties[5])

    # these are the original star coordinates
    coords_stars = np.array(
        [
            [s.coords_skycam.x.to_value(u.m), s.coords_skycam.y.to_value(u.m)]
            for s in stars
        ]
    )
    # these are the star coordinates transformed according to the best-matched quad
    coords_stars_for_match = t.inverse(coords_stars)

    coords_spots = np.array(
        [
            [s.coords_skycam.x.to_value(u.m), s.coords_skycam.y.to_value(u.m)]
            for s in spots
        ]
    )

    # perform KD tree search
    spot_tree = KDTree(coords_spots)
    star_tree = KDTree(coords_stars_for_match)

    matches = spot_tree.query_ball_tree(star_tree, r=radius.to_value(u.m))
    num_unique_matches = sum([len(m) for m in matches if len(m) == 1])

    if num_unique_matches < min_matches:
        return 0

    # build star-spot match list
    quad_match.star_spot_match_list = []
    coords_matched_stars = []
    coords_matched_spots = []
    for i, match in enumerate(matches):
        if len(match) > 0:
            s = StarSpotMatch(stars[match[0]], spots[i], status=Status.FIELDMATCHED)
            quad_match.star_spot_match_list.append(s)

            coords_matched_stars.append(coords_stars[match[0]])
            coords_matched_spots.append(coords_spots[i])

    # after matching, perform a similarity transform with all matched
    # stars and calculate quality parameters for outlier identification
    # Here we make sure to start with the original set of star coordinates,
    # as otherwise we would fit w.r.t. the above SimilarityTransform.
    coords_matched_stars = np.array(coords_matched_stars)
    coords_matched_spots = np.array(coords_matched_spots)

    t = SimilarityTransform()
    t.estimate(coords_matched_spots, coords_matched_stars)

    coords_stars_from_inverse = t.inverse(coords_matched_stars)
    delta = coords_stars_from_inverse - coords_matched_spots

    quad_match.mean_distance2 = np.mean(delta[0] ** 2 + delta[1] ** 2) * u.m**2
    quad_match.tparams_similarity = t.params
    quad_match.set_status(Status.FIELDMATCHED)

    return len(coords_matched_stars)


class ImageSolver(Component):
    """
    ImageSolver class.

    Hosts algorithms to solve a given image, i.e. determine the position of each
    individual pixel in sky (RADec) coordinates.
    Needs a reasonably well-known pointing position for the image. On the basis of
    this pointing, catalog stars are selected and matched with image spots using
    quad matching. The matching algorithm of the astroalign package is used.
    """

    uuid = Unicode(default_value=str(uuid.uuid4()), help="UUID of ImageSolver").tag(
        config=False
    )
    name = Unicode(help="name of ImageSolver").tag(config=True)
    min_magnitude = Float(
        default_value=-12.0, help="minimum magnitude of stars for catalog search"
    ).tag(config=True)
    max_magnitude = Float(
        default_value=9.0, help="maximum magnitude of stars for catalog search"
    ).tag(config=True)
    max_num_stars = Int(
        default_value=100, help="maximum number of stars used for matching"
    ).tag(config=True)
    max_num_spots = Int(
        default_value=15, help="maximum number of image spots used for matching"
    ).tag(config=True)
    matching_distance = Float(
        default_value=0.01,
        help="maximum distance for quad matching in L2/L1 L0/L1 plane",
    ).tag(config=True)
    matching_radius = Float(
        default_value=15,
        help="distance in pixels within which a star is matched to a spot in the field matching",
    ).tag(config=True)
    max_pointing_deviation = Float(
        default_value=2.0,
        help="assumed maximum angular deviation (in degrees) between true and nominal"
        "pointing position and/or pointing camera optical axis"
        "and true telescope pointing",
    ).tag(config=True)
    min_camera_shadow = Float(
        default_value=10.0,
        help="assumed minimum FoV side length (in degrees) blocked by an"
        "(assumed square) science camera in the inner part of the image",
    ).tag(config=True)
    scale_tolerance = Float(
        default_value=0.1,
        help="allowed deviation in true vs. nominal focal length of camera",
    ).tag(config=True)

    @classmethod
    def from_config(cls, **kwargs):
        """
        Read an ImageSolver configuration from either configuration file or database.
        Either the path of a configuration file ('input_url') or a database collection
        ('collection') must be provided.


        Parameters
        ----------
        input_url: str or Path
            path of the configuration file.
        name: str
            name of the ImageSolver (as in `ImageSolver.name`).
            When loading the configuration from file, can be set to check that the configuration with the
            correct name is loaded.
            When loading from database, is used to identify the correct database record.
        uuid: str
            UUID of the camera (as in `ImageSolver.uuid`).
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
        extractor: SpotExtractor object
        """
        # load configuration and construct instance
        config = from_config(component_name=cls.__name__, **kwargs)
        return cls(config=config)

    def process(
        self,
        spotlist,
        exposure,
        estimated_pointing=None,
        fov_radius=None,
        image_solution=None,
    ):
        """
        Solve the image given an exposure object.

        Parameters
        ----------
        spotlist : SpotList
            List of pixel coordinates of extracted spots
        exposure : Exposure
            Exposure object. Should be removed at some point.
        estimated_pointing: SkyCoord[RADec]
            guess of the optical axis pointing of the telescope.
            If None, try exposure.nominal_telescope_pointing
        fov_radius: Angle or None
            radius of the field of view (for star matching)
            If set to None, estimated FoV from camera parameters
        image_solution: ctapointing.imagesolver.ImageSolution
            object that is to be updated by the results of
            the image solving process. If None, new ImageSolution
            object is created and returned by this method.

        Returns
        -------
        Tuple of Registration object and best-match Quad object
        """

        if estimated_pointing is not None:
            exposure.telescope_pointing = estimated_pointing
        elif exposure.nominal_telescope_pointing is not None:
            self.log("no estimated_pointing given, try nominal telescope pointing...")
            exposure.telescope_pointing = exposure.nominal_telescope_pointing
        else:
            raise AttributeError(
                f"no estimated pointing position provided for exposure, "
                f"and nominal pointing position not set"
            )

        # estimate FoV radius from camera parameters
        if fov_radius is None:
            fov_radius = (
                np.max(exposure.camera.fov) / 2
                + np.sqrt(2) * self.max_pointing_deviation * u.deg
            )

        # query list of stars in the estimated direction of the image, including proper motion correction
        stars_coords_radec, mag, source_id = query_catalog(
            exposure.telescope_pointing,
            fov_radius,
            min_mag=self.min_magnitude,
            max_mag=self.max_magnitude,
            obstime=exposure.mean_exposure_time,
        )

        if len(stars_coords_radec) == 0:
            self.log.error("no stars found in catalog. Giving up.")
            return None, None, None, None

        # calculate pixel positions of all stars, according to assumed telescope pointing
        # and camera parameters
        stars_coords_skycam = stars_coords_radec.transform_to(exposure.skycameraframe)
        stars_coords_pix = exposure.camera.transform_to_pixels(stars_coords_skycam)

        # mask all stars that are possibly within the chip boundaries, taking into account
        # that the estimated pointing direction might be wrong by max_deviation in all directions
        max_pointing_deviation_pix = (
            self.max_pointing_deviation * u.deg / exposure.camera.pixel_angle[0]
        ).decompose()
        mask_within_chip = exposure.camera.clip_to_chip(
            stars_coords_pix, tolerance=max_pointing_deviation_pix
        )

        # mask all stars that may be shadowed by the science camera, taking into account
        # that the estimated pointing direction might be wrong by max_deviation in all directions
        #
        # for now we remove all stars which are projected within a circle of radius
        # min_camera_shadow/2 - max_deviation from the chip centre
        min_camera_shadow_pix = (
            self.min_camera_shadow * u.deg / exposure.camera.pixel_angle[0]
        ).decompose()
        radius = np.maximum(min_camera_shadow_pix / 2 - max_pointing_deviation_pix, 0)
        chip_centre = exposure.camera.chip_centre

        mask_outside_shadow = (stars_coords_pix[:, 0] - chip_centre[0]) ** 2 + (
            stars_coords_pix[:, 1] - chip_centre[1]
        ) ** 2 > radius**2

        # create list of stars and restrict to the brightest ones
        stars = []
        for i, radec in enumerate(stars_coords_radec):
            if mask_within_chip[i] and mask_outside_shadow[i]:
                stars.append(
                    Star(
                        radec,
                        stars_coords_skycam[i],
                        stars_coords_pix[i],
                        magnitude=mag[i],
                        id=f"Star{i}",
                    )
                )

        self.log.info(
            f"using pointing tolerance of {self.max_pointing_deviation}"
            f" and camera shadow of {self.min_camera_shadow}, {len(stars)} of {len(stars_coords_radec)}"
            f" stars may be in chip FoV"
        )

        if len(stars) > self.max_num_stars:
            self.log.info(
                f"restricting matching to brightest {self.max_num_stars} of {len(stars)} catalog stars."
            )

            for star in stars[self.max_num_stars :]:
                star.set_status(Status.DEFAULT)

        # read spots from spotlist and restrict to the brightest ones
        spots_coords_skycam = exposure.camera.transform_to_camera(spotlist.coords_pix)

        spots = []
        for i in range(len(spotlist)):
            spots.append(
                Spot(
                    None,
                    spots_coords_skycam[i],
                    spotlist.coords_pix[i],
                    flux=spotlist.flux[i],
                    id=f"Spot{i}",
                )
            )

        if len(spots) > self.max_num_spots:
            self.log.info(
                f"restricting matching to brightest {self.max_num_spots} of {len(spots)} spots."
            )

            for spot in spots[self.max_num_spots :]:
                spot.set_status(Status.DEFAULT)

        self.log.info("performing image registration...")

        start_registration = time.perf_counter()

        # start registration process:
        # build quad objects, preselect matches based on their distance,
        # perform a similarity transform and select from preselected
        # matches based on their transformation parameters
        registration = Registration(spots, stars)
        registration.find_matches(self.matching_distance)
        registration.preselect_by_scale(rtol=self.scale_tolerance)

        # set some loose boundaries on the expected parameters of the similarity
        # between spot and star quad match, i.e. on rotation, (angular) offset and scale
        exp_rotation = (0.0 * u.deg, 20.0 * u.deg)
        exp_scale = (1.0, 0.1)
        registration.select_by_similarity(exp_rotation, exp_scale, tolerance=1.0)

        stop_registration = time.perf_counter()
        registration_time = (stop_registration - start_registration) * u.s
        self.log.info(f"finished registration ({registration_time:.2f}).")

        # find the best quad match by matching more stars to the reconstructed spots
        quad_matches = [
            m for m in registration.quad_match_list if m.has_status(Status.SELECTED)
        ]

        # field matching: based on the selected quad matches, match other spots to stars
        # in the FoV
        self.log.info(f"performing field matching for {len(quad_matches)} quad matches")

        start_matching = time.perf_counter()

        # sort quad matches by descending quad area
        area_list = []
        for quad_match in quad_matches:
            area = quad_match.star_quad.area / exposure.camera.chip_area
            area_list.append((quad_match, area))

        area_list.sort(key=lambda element: element[1], reverse=True)

        # match the rest of the FoV, using a maximum matching radius (in pixels) to call a star-spot
        # coincidence a match.
        # calculate figure of merit, FOM = num_matched_stars**n * area; break if quads with smaller
        # area cannot increase FOM further
        match_list = []
        break_cond = 0.0
        for quad_match, area in area_list:
            # match the field and calculate FOM
            num_matched_stars = match_field(
                quad_match,
                stars,
                spots,
                self.matching_radius * exposure.camera.pixel_size,
            )
            quality_fom = num_matched_stars**N_FIELD_MATCH_EXP * area

            if quality_fom > 0:
                break_cond = quality_fom if break_cond < quality_fom else break_cond
                match_list.append((quad_match, quality_fom, num_matched_stars, area))

            if area < break_cond / len(spotlist) ** N_FIELD_MATCH_EXP:
                break

        stop_matching = time.perf_counter()
        matching_time = (stop_matching - start_matching) * u.s
        self.log.info(
            f"finished field matching ({len(match_list)} matches, {matching_time:.2f})."
        )

        # sort list by descending quality
        if len(match_list) > 0:
            match_list.sort(key=lambda element: element[1], reverse=True)
            match_list[0][0].set_status(Status.BESTMATCH)
        else:
            self.log.warning("no quad matches left after field matching")

        # store results
        if image_solution is None:
            image_solution = ImageSolution()
            image_solution.mean_exposure_time = exposure.mean_exposure_time
            image_solution.exposure_duration = exposure.duration
            try:
                image_solution.camera_chip_temperature = (
                    exposure.chip_temperature.value + 273.15
                ) * u.K
            except AttributeError:
                self.log.warning("no chip temperature available from exposure")
            image_solution.mean_background = spotlist.mean_background

        image_solution.num_quad_matches = len(registration.quad_match_list)
        image_solution.num_quad_matches_selected = len(quad_matches)
        image_solution.registration_time = registration_time
        image_solution.matching_time = matching_time
        image_solution.spotlist_uuid = spotlist.uuid
        image_solution.image_uuid = exposure.uuid

        return image_solution, match_list, stars, registration
