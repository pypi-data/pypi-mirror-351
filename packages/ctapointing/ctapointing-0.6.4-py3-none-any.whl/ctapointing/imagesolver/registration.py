import logging
import copy
import time

import numpy as np
import astropy.units as u
from astropy.coordinates import Angle

from skimage.transform import SimilarityTransform
from scipy.spatial import KDTree
from scipy.special import comb
from scipy.signal import find_peaks

from .statusbase import StatusBase, Status

log = logging.getLogger(__name__)


class CoordinateBase:
    """
    Base class for storing coordinates of spots or stars.
    """

    def __init__(self, c_radec=None, c_skycam=None, c_pix=None, id=None):
        self.coords_radec = c_radec
        self.coords_skycam = c_skycam
        self.coords_pix = c_pix
        self.id = id

        self.quad_list = None


class Star(CoordinateBase, StatusBase):
    """
    Class for storing star positions.
    """

    def __init__(
        self,
        c_radec=None,
        c_skycam=None,
        c_pix=None,
        magnitude=None,
        status=Status.USED,
        id=None,
    ):
        StatusBase.__init__(self, status)
        CoordinateBase.__init__(self, c_radec, c_skycam, c_pix, id=id)
        self.mag = magnitude

    def __repr__(self):
        s = "<Star" + self.status.__repr__() + ">"
        return s

    def __str__(self):
        s = "Star:"
        s += f"\tID: {self.id}\n"
        s += f"\tRADec: {self.coords_radec}\n"
        s += f"\tSkyCam: {self.coords_skycam}\n"
        s += f"\tPix: {self.coords_pix}\n"
        s += f"\tmag: {self.magnitude}\n"
        s += f"\tStatus: {self.status}"
        return s


class Spot(CoordinateBase, StatusBase):
    """
    Class for storing spot positions.
    """

    def __init__(
        self,
        c_radec=None,
        c_skycam=None,
        c_pix=None,
        flux=None,
        mean_background=None,
        status=Status.USED,
        id=None,
    ):
        StatusBase.__init__(self, status)
        CoordinateBase.__init__(self, c_radec, c_skycam, c_pix, id=id)
        self.flux = flux
        self.mean_background = mean_background

    def __repr__(self):
        s = "<Spot" + self.status.__repr__() + ">"
        return s

    def __str__(self):
        s = f"Spot:"
        s += f"\tID: {self.id}\n"
        s += f"\tRADec: {self.coords_radec}\n"
        s += f"\tSkyCam: {self.coords_skycam}\n"
        s += f"\tPix: {self.coords_pix}\n"
        s += f"\tStatus: {self.status}"
        return s


class StarSpotMatch(StatusBase):
    """
    Class representing a pair of (matched) spot and star coordinates.
    """

    def __init__(self, star, spot, status=Status.DEFAULT):
        StatusBase.__init__(self, status)

        self.star = star
        self.spot = spot


class Quad(StatusBase):
    """
    Class representing a triangular quad object of either
    spot or star coordinates.
    """

    def __init__(self, objects, invariants, status=Status.DEFAULT, quad_id=None):
        StatusBase.__init__(self, status)

        self.objects = objects
        self.invariants = invariants
        self.quad_id = quad_id

        self.matched_quads_list = []

    def get_num_matches(self):
        return len(self.matched_quads_list)

    @property
    def area(self):
        """
        Area of the quad, using Heron's formula, calculated
        from the SkyCameraFrame coordinates.
        """
        coords_x = u.Quantity([s.coords_skycam.x for s in self.objects])
        coords_y = u.Quantity([s.coords_skycam.y for s in self.objects])

        L0 = np.hypot(coords_x[0] - coords_x[1], coords_y[0] - coords_y[1])
        L1 = np.hypot(coords_x[0] - coords_x[2], coords_y[0] - coords_y[2])
        L2 = np.hypot(coords_x[2] - coords_x[1], coords_y[2] - coords_y[1])

        s = (L0 + L1 + L2) / 2
        A = np.sqrt(s * (s - L0) * (s - L1) * (s - L2))

        return A

    def __repr__(self):
        s = f"<Quad id={self.quad_id}" + self.status.__repr__() + ">"
        return s

    def __str__(self):
        s = "Quad:"
        s += f"\tID: {self.quad_id}\n"
        s += f"\tObjects: {self.objects}\n"
        s += f"\tInvariants: {self.invariants}\n"
        s += f"\tStatus: {self.status}\n"

        return s


class QuadMatch(StatusBase):
    """
    Class for storing a match between a spot quad object
    and a star quad object.
    """

    def __init__(self, spot_quad, star_quad, status=Status.DEFAULT):
        StatusBase.__init__(self, status)

        self.spot_quad = spot_quad
        self.star_quad = star_quad

        self.transformation_properties = None
        self.star_spot_match_list = []
        self.mean_distance2 = None
        self.tparams_similarity = None

    def set_status(self, status, combine=True):
        """
        Sets status flag for the quad match and star and spot quad
        :param status: the status flag to be set
        :param combine: if True, add status flag to other existing flags
                        if False, set this status flag as the only one
        """
        super().set_status(status, combine)
        self.spot_quad.set_status(status, combine)
        self.star_quad.set_status(status, combine)

    def transform_stars(self, stars=None, transformation_parameters=None):
        """
        Transform a set of stars using the transformation properties
        stored in this QuadMatch. Returns a new list of Star objects
        with updated SkyCameraFrame coordinates.
        """

        # construct transform
        if transformation_parameters is None:
            t = SimilarityTransform(self.transformation_properties[5])
        else:
            t = SimilarityTransform(transformation_parameters)

        # if no star list given, transform all stars of the star quad
        # of this object
        if stars is None:
            stars = self.star_quad.objects

        # extract raw SkyCameraFrame coordinates of stars, apply transform, and
        # copy all stars into a new star list with updated coordinates.
        star_list = []
        for star in stars:
            star_coords = [
                star.coords_skycam.x.to_value(u.m),
                star.coords_skycam.y.to_value(u.m),
            ]

            star_coords_transformed = (t.inverse(star_coords) * u.m).flatten()

            star_transformed = copy.deepcopy(star)
            star_transformed.coords_skycam.data.x[()] = star_coords_transformed[0]
            star_transformed.coords_skycam.data.y[()] = star_coords_transformed[1]
            star_transformed.coords_skycam.cache.clear()

            star_list.append(star_transformed)

        return star_list

    def similarity_transform(self):
        """
        Perform similarity transform between spot and star quad.

        For the similarity transform, scale, rotation and two offsets are fitted
        between the star quad and the spot quad of each QuadMatch object.

        Transformation parameters are stored in the transformation_properties
        attribute of the QuadMatch object.

        The status of the QuadMatch is set to SIMFITTED.

        """

        # for each quad match, store the coordinates of each
        # triangle corner (both for spots and stars)
        spot_coords = []
        star_coords = []

        # prepare coordinates for transform
        for k in range(3):
            spot_coords.append(
                [
                    self.spot_quad.objects[k].coords_skycam.x.to_value(u.m),
                    self.spot_quad.objects[k].coords_skycam.y.to_value(u.m),
                ]
            )
            star_coords.append(
                [
                    self.star_quad.objects[k].coords_skycam.x.to_value(u.m),
                    self.star_quad.objects[k].coords_skycam.y.to_value(u.m),
                ]
            )

        spot_coords = np.array(spot_coords)
        star_coords = np.array(star_coords)

        # perform similarity transform
        t = SimilarityTransform()
        t.estimate(spot_coords, star_coords)
        converged = np.allclose(t.inverse(t(spot_coords)), spot_coords)

        # difference in corner positions of the two aligned quads:
        # sum of the corner distances in relation to the circumference of the quad
        delta = t.inverse(star_coords) - spot_coords
        circumference = self.spot_quad.invariants[2]
        rel_corner_err = np.sum(np.hypot(delta[:, 0], delta[:, 1])) / circumference

        # store transformation parameters
        self.transformation_properties = [
            t.translation[0] * u.m,
            t.translation[1] * u.m,
            Angle(t.rotation * u.rad).wrap_at(180 * u.deg),
            t.scale,
            converged,
            t.params,
            circumference,
            rel_corner_err,
        ]

        if converged:
            self.set_status(Status.SIMFITTED)

    def __repr__(self):
        s = (
            f"<QuadMatch {self.spot_quad.quad_id}, {self.star_quad.quad_id}, "
            + self.status.__repr__()
            + " >"
        )
        return s

    def __str__(self):
        s = f"QuadMatch:"
        s += f"\t{self.spot_quad}\n"
        s += f"\t{self.star_quad}\n"
        s += f"\tspot-star matches: {self.star_spot_match_list}\n"
        s += f"\t{repr(self.status)}"
        return s


class Registration:
    """
    Registration class.
    Used to find matches between spot quads and star quads, using quad similarities.

    Implements the following registration algorithms:
    (1) A search for best-matching quads based on geometric properties of the quads/
    (2) A similarity transformation for selected quads that determines the rough
        transformation between star and spot coordinates for these quads
    (3) A matching algorithm that can match further stars to spots, using the above
        similarity transform.

    Furthermore, methods are implemented to select among chosen quads based on certain
    quad or transformation properties.
    """

    def __init__(self, spot_list, star_list):
        """
        Constructor.

        :param spot_list: list of Spot objects used in the primary quad matching.
        :param star_list: list of Star objects used in the primary quad matching.
        """

        self.spot_list = spot_list
        self.star_list = star_list
        self.quad_list_stars = []  # list of Quad objects constructed from Stars
        self.quad_list_spots = []  # list of Quad objects constructed from Spots

        self.quad_match_list = []  # list of QuadMatch objects

    def get_spots(self, status=Status.DEFAULT):
        """
        Return list of stored Spot objects, matching status flag.
        """
        return [s for s in self.spot_list if s.has_status(status)]

    def get_stars(self, status=Status.DEFAULT):
        """
        Return list of stored Star objects, matching status flag.
        """
        return [s for s in self.star_list if s.has_status(status)]

    def get_quads_spots(self, status=Status.DEFAULT):
        """
        Return list of Quad objects constructed from Spots, matching status flag.
        """
        return [q for q in self.quad_list_spots if q.has_status(status)]

    def get_quads_stars(self, status=Status.DEFAULT):
        """
        Return list of Quad objects constructed from Stars, matching status flag.
        """
        return [q for q in self.quad_list_stars if q.has_status(status)]

    def get_quad_matches(self, status=Status.DEFAULT):
        """
        Return list of QuadMatch objects, matching status flag.
        """
        return [q for q in self.quad_match_list if q.has_status(status)]

    @staticmethod
    def build_quads(object_list, object_status=Status.USED, quad_name=""):
        """
        Build (triangular) quads from each triplet of Star or Spot
        SkyCameraFrame coordinate pairs.
        With n objects given, exactly m = (n/3) "n choose 3" independent quads
        can be constructed. Quad information is composed of L2/L1 (the ratio of
        the largest and second-to-largest side lengths of the triangle),
        L1/L0 (the ratio of the second largest and smallest side lengths),
        as well as L2+L1+L0 (i.e. the circumference of the triangle).

        :param object_list: list of Spot or Star objects used to build the quads
        :param object_status: status flag that can be used to select a subset of
               the objects from object_list
        :param quad_name: prefix used to name the individual spots

        :returns quad_list: list of all Quad objects built
        """

        # list of quads
        quad_list = []

        # use only objects with requested status
        ol = [o for o in object_list if o.has_status(object_status)]

        n = len(ol)
        log.info(f"using {n} objects -> {int(comb(n, 3))} quads")

        # TODO: This is horribly inefficient...
        x = [o.coords_skycam.x.to_value("m") for o in ol]
        y = [o.coords_skycam.y.to_value("m") for o in ol]

        num_quads = 0
        for i in range(n):
            for j in range(i + 1, n):
                l0 = np.hypot(x[i] - x[j], y[i] - y[j])

                for k in range(j + 1, n):
                    # determine quad side lengths
                    l1 = np.hypot(x[j] - x[k], y[j] - y[k])
                    l2 = np.hypot(x[k] - x[i], y[k] - y[i])

                    # sort by length
                    sides = np.sort(np.array([l0, l1, l2]))

                    # determine length ratios
                    l01 = sides[1] / sides[0]
                    l12 = sides[2] / sides[1]

                    # calculate scaled quad circumference
                    c = l0 + l1 + l2

                    # generate Quad object which stores
                    # references to the object as well
                    # as the geometric invariants
                    quad_id = quad_name + str(num_quads)
                    q = Quad(
                        [ol[i], ol[j], ol[k]],
                        [l12, l01, c],
                        quad_id=quad_id,
                        status=Status.USED,
                    )
                    quad_list.append(q)

                    num_quads += 1

        log.info(f"\tbuilt {len(quad_list)} independent quads.")

        return quad_list

    def find_matches(self, radius=0.1):
        """
        Find matches between star Quad objects and Spot Quad objects,
        based on their geometric invariants.

        The algorithm uses nearest neighbour matching in the
        L2/L1 - L0/L1 plane of the geometric invariants. It uses an
        efficient kd tree with k=2 for searching through all spot quads
        and identifying all star quads that match in this plane within
        a circle of given radius.

        Resulting quad matches are stored in the objects QuadMatch list.

        Note: If the search plane is densely populated and/or the search
        radius is large, there may exist more than one star-quad match
        for any given spot quad. Naturally, for some spot quads,
        no matching star quad will be found.

        :param radius: search radius for the kd tree search. All matches
                       within this search radius will be returned.
        """

        log.info("searching for quad matches...")

        start = time.perf_counter()

        # build spot and star quads
        self.quad_list_spots = self.build_quads(
            self.spot_list, object_status=Status.USED, quad_name="SpotQuad"
        )
        self.quad_list_stars = self.build_quads(
            self.star_list, object_status=Status.USED, quad_name="StarQuad"
        )

        # prepare invariants: use triangle side lengths
        invs_spots = [q.invariants[:2] for q in self.quad_list_spots]
        invs_stars = [q.invariants[:2] for q in self.quad_list_stars]

        # 2D tree search for similarity between invariants
        spot_tree = KDTree(invs_spots)
        star_tree = KDTree(invs_stars)

        matches = spot_tree.query_ball_tree(star_tree, r=radius)

        # store matches in QuadMatch objects, mark these QuadMatches
        # as MATCHED
        self.quad_match_list = []
        for i, match_list in enumerate(matches):
            for match in match_list:
                qm = QuadMatch(
                    self.quad_list_spots[i],
                    self.quad_list_stars[match],
                    status=Status.MATCHED,
                )
                self.quad_match_list.append(qm)

        stop = time.perf_counter()
        log.info(
            f"\tfound {len(self.quad_match_list)} matches ({(stop - start):.2f}s)."
        )

    def preselect_by_scale(self, rtol=0.02):
        """
        From all primary QuadMatch objects, select those quad matches which
        match roughly in triangle circumference. This will reduce the number
        of false-positive quad matches quite a bit.

        The selection is motivated by the fact that the focal length of the
        camera is a usually well-known constant. If chosen appropriately, star
        quads transformed into the SkyCameraFrame will have roughly the same
        circumference as spot quads.

        Selected QuadMatch objects will obtain the status PRESELECTED.

        :param rtol: maximum accepted relative tolerance between the circumference
                     of star and spot quads used for selection.
        """

        n_matches = len(self.quad_match_list)
        log.info(
            f"pre-selecting from {n_matches} matched quads based on scale similarity"
        )

        start = time.perf_counter()

        for match in self.quad_match_list:
            close = np.isclose(
                match.spot_quad.invariants[2],
                match.star_quad.invariants[2],
                atol=0,
                rtol=rtol,
            )
            if close:
                match.set_status(Status.PRESELECTED)

        stop = time.perf_counter()

        n_selected = len(self.get_quad_matches(Status.PRESELECTED))
        log.info(f"\tpre-selected {n_selected} quad matches ({(stop-start):.2f} s).")

    def select_by_similarity(
        self,
        exp_rotation=(0.0 * u.deg, 5.0 * u.deg),
        exp_scale=(1.0, 0.1),
        tolerance=2.0,
        status=Status.PRESELECTED,
    ):
        """
        Select QuadMatch objects based on their similarity transformation parameters.

        (1) Perform a similarity transformation on all matched quad pairs, resulting in a set of four
        transformation parameters for each match:
        - rotation of star quad w.r.t. spot quad
        - scaling of star quad w.r.t. spot quad
        - offsets (x, y) between star quad and spot quads.

        (2) Create a histogram of each parameter. We expect a smooth distribution in the parameter
        for falsely matched quads, and a narrow peak for those quad matches that are correctly matched.

        (3) Find the peak in each of the parameter distributions, and select, based on the peak width and
        the tolerance argument, all quad matches closely around the peak.

        (4) Accept all quad matches which pass selection in all parameters.

        Selected QuadMatch objects will be marked with status SELECTED.

        :param exp_rotation: tuple of Angle expected relative rotation between fitted star and
                             spot quads and maximum tolerance (usually 0.0 deg, 10.0 deg)
        :param exp_scale: tuple of float expected scaling between fitted star and spot quads
                          and maximum tolerance (usually 1.0, 0.1)
        :param tolerance: relative tolerance for cut around the peak. Set to None to disable the automatic procedure
        and instead use the expected parameter ranges given as arguments
        """

        # perform similarity transform between spot quads and star quads
        self.similarity_transform(status=status)

        # do selection only on those quads for which a successful transform has been found
        fitted_list = [
            m for m in self.quad_match_list if m.has_status(Status.SIMFITTED)
        ]

        if len(fitted_list) == 0:
            log.warning("no similarity transform found for any quad combination")
            return

        log.info(
            f"selecting from {len(fitted_list)} fitted matches based on similarity"
        )

        start = time.perf_counter()

        # initialise selection criteria to function arguments
        # (offset_x,offset_y,rotation,scale)x(exp_mean,tolerance)
        mean_tol = [
            list(exp_rotation),
            list(exp_scale),
        ]
        num_similarity_params = len(mean_tol)

        # (1) select those matches which fulfill predefined rotation and scale parameters
        for match in fitted_list:
            is_selected = np.all(
                [
                    u.isclose(
                        match.transformation_properties[i + 2],
                        mean_tol[i][0],
                        atol=mean_tol[i][1],
                    )
                    for i in range(num_similarity_params)
                ]
            )

            if not is_selected:
                fitted_list.remove(match)

        log.info(
            f"\t{len(fitted_list)} quad matches remaining after predefined rotation and scale cuts"
        )

        # (2) narrow down the selection by searching for a peak in the distribution
        # of the fitted quad rotation
        if tolerance is not None:
            num_spot_quads = len(self.quad_list_spots)
            num_fitted_quads = len(fitted_list)

            # guess the number of histogram bins based on the expected quad statistics
            avg_per_bin = np.sqrt(num_spot_quads)
            num_bins = int(num_fitted_quads / avg_per_bin)

            params_for_hist = [
                match.transformation_properties[2].value for match in fitted_list
            ]
            unit_for_hist = 1.0 * fitted_list[0].transformation_properties[2].unit

            # find sharp peak in parameter distribution, expected due to the majority of all valid quads
            # displaying (roughly) the same transformation properties
            # require peak to be at least as large as half the maximum of the distribution
            y, x = np.histogram(params_for_hist, bins=num_bins)
            peak_indexes, peak_params = find_peaks(
                y, height=np.max(y) / 2, distance=5, width=1
            )

            # if prominent peak is found, restrict selection to those quad matches that are in a narrow
            # range around that peak. If no peak is found, fall back to default parameters given as arguments
            if len(peak_indexes) > 0:
                # select largest peak
                peak_params_idx = np.argmax(peak_params["peak_heights"])
                idx = peak_indexes[peak_params_idx]

                # determine width of the peak and adjust tolerance region around the peak
                log.debug("indexes", peak_indexes, idx)
                log.debug(
                    f"heights: {peak_params['peak_heights']}, {peak_params['peak_heights'][peak_params_idx]}"
                )
                log.debug(
                    f"left {peak_params['left_ips']}, {peak_params['left_ips'][peak_params_idx]}"
                )
                log.debug(
                    f"right {peak_params['right_ips']}, {peak_params['right_ips'][peak_params_idx]}"
                )

                tol = round(
                    tolerance
                    * (
                        peak_params["right_ips"][peak_params_idx]
                        - peak_params["left_ips"][peak_params_idx]
                    )
                )
                tol = tol if tol > 1 else 1

                # finally adjust tolerance cuts
                tol_left = idx - tol if idx - tol >= 0 else 0
                tol_right = idx + tol if idx + tol < len(x) else len(x) - 1
                mean_tol[0][0] = x[idx] * unit_for_hist
                mean_tol[0][1] = (x[tol_right] - x[tol_left]) * unit_for_hist

        # select those matches for which all selection criteria are fulfilled
        for match in fitted_list:
            is_selected = np.all(
                [
                    u.isclose(
                        match.transformation_properties[i + 2],
                        mean_tol[i][0],
                        atol=mean_tol[i][1],
                    )
                    for i in range(num_similarity_params)
                ]
            )

            if is_selected:
                match.set_status(Status.SELECTED)

        stop = time.perf_counter()

        n_selected = len(self.get_quad_matches(Status.SELECTED))
        log.info(f"\tselected {n_selected} quad matches ({(stop-start):.2f} s).")

    def similarity_transform(self, status=Status.PRESELECTED):
        """
        Perform similarity transform between quads of stored QuadMatch objects.

        For the similarity transform, scale, rotation and two offsets are fitted
        between the star quad and the spot quad of each QuadMatch object.

        Transformation parameters are stored in the transformation_properties
        attribute of the QuadMatch object.

        The status of the QuadMatch is set to SIMFITTED.

        :param status: status flag for QuadMatch selection: only QuadMatches
                       with this status flag set will be evaluated

        """

        prefitted_list = self.get_quad_matches(status)

        log.info(
            f"performing similarity transform for {len(prefitted_list)} quad matches..."
        )

        start = time.perf_counter()

        for match in prefitted_list:
            match.similarity_transform()

        n_transformed = len(self.get_quad_matches(Status.SIMFITTED))

        stop = time.perf_counter()
        log.info(
            f"\tfinished similarity transform for {n_transformed} quad matches ({stop - start:.2f} s)."
        )

    def get_quad_matches_transformed(self, status=Status.SELECTED):
        """
        Returns a copy of selected QuadMatch objects, in which all StarQuad coordinates
        have been transformed to the SkyCameraFrame according to the transformation
        parameters of the similarity transform carried out for this QuadMatch.

        :param status: status flag for QuadMatch selection: only QuadMatches
                       with this status flag set will be evaluated

        :returns: list (deep copy) of transformed QuadMatch objects
        """

        matches_selected = [m for m in self.quad_match_list if m.has_status(status)]
        matches_transformed = copy.deepcopy(matches_selected)

        for match_orig, match_trans in zip(matches_selected, matches_transformed):
            match_trans.star_quad.objects = match_orig.transform_stars()

        return matches_transformed
