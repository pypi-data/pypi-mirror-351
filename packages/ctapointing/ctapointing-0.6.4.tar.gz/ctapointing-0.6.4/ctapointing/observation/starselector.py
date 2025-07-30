import logging

import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord, AltAz, ICRS

from ctapointing.catalog import query_catalog
from .pointing_observation import PointingObservation

log = logging.getLogger(__name__)


class StarSelectorIsotropic:
    """
    A class for selecting stellar targets for pointing calibration observations

    Targets are selected based on maximum isotropic coverage of the sky based on
    - previously visited targets (history)
    - planned start time of the observation
    within the provided azimuth and altitude limits (if requested).

    Parameters:
    ----------
    location: astropy.coordinates.EarthLocation
        earth location of the telescope
    altitude limits: None or tuple of astropy.Angle
        tuple of two angles representing the altitude range in which
        targets get selected
    magnitude limits: None or tuple of float
        tuple representing minimum and maximum magnitude of catalog stars
        used as targets

    TODO: Make target history work. This requires generating a random
    selection of targets outside the altitude range, as otherwise
    the resulting distribution will be biased.
    """

    def __init__(
        self,
        location,
        altitude_limits=(10.0, 70.0) * u.deg,
        magnitude_limits=(-3, 4),
    ):
        self.location = location
        self.altitude_limits = altitude_limits
        self.magnitude_limits = magnitude_limits

        self.target_list_az = []
        self.target_list_alt = []

        self._full_list_az = []
        self._full_list_alt = []

    def select_target(self, start_time, duration):
        """
        Select the next best target, based on observation history.
        Target is selected such that the resulting AltAz distribution
        is as isotropic as possible (within the limits of the star
        distribution)

        Parameters
        ----------
        start_time: astropy.Time
            Time at which the observation of the target will start
        duration: astropy.units.Quantity
            duration of the observation

        Returns
        -------
        PointingObservation or list of PointingObservation
        """

        # select catalog stars currently visible above the horizon
        # include some below-horizon safety margin, as otherwise
        # the generated distribution will be biased to low altitudes
        altaz = AltAz(location=self.location, obstime=start_time + duration / 2)
        zenith = SkyCoord(alt=90 * u.deg, az=0 * u.deg, frame=altaz)

        coords, mag, source_id = query_catalog(
            fov_centre=zenith.transform_to(ICRS),
            fov_radius=100 * u.deg,  # safety margin: 10 deg below horizon
            min_mag=self.magnitude_limits[0],
            max_mag=self.magnitude_limits[1],
            obstime=start_time
            + duration / 2,  # be sure to include proper motion correction
        )
        coords_altaz = coords.transform_to(altaz)

        # create mask for altitude limits
        mask_alt = np.greater(coords_altaz.alt, self.altitude_limits[0]) & np.less(
            coords_altaz.alt, self.altitude_limits[1]
        )

        # select catalog star for which the sum of (distances**(-2)) to all previously
        # observed stars is smallest. This guarantees an isotropic selection.
        if len(self.target_list_az) > 0:
            # To avoid a bias at the altitude limits, we cannot simply neglect
            # targets outside the boundaries. Rather, we have to accept these
            # as well and populate the phase space outside the limits, and start over.
            while True:
                # be careful here: always convert AltAz positions of previous targets
                # "by hand" in the current AltAz system - otherwise, the difference
                # in observation times of the different targets would mess up the
                # calculation of angular differences
                target_coords = SkyCoord(
                    az=(np.array(self._full_list_az) * u.deg).reshape(-1, 1),
                    alt=(np.array(self._full_list_alt) * u.deg).reshape(-1, 1),
                    frame=altaz,
                )

                # determine star which on average is most distant w.r.t.
                # targets already observed
                distance = target_coords.separation(coords_altaz)
                distance[np.isclose(distance, 0 * u.deg)] = (
                    1 * u.arcsec
                )  # avoid division by zero
                distance_criterion = np.sum(distance ** (-2), axis=0)
                most_distant = np.argmin(distance_criterion)

                selected_az = coords_altaz[most_distant].az
                selected_alt = coords_altaz[most_distant].alt
                self._full_list_az.append(selected_az.to_value(u.deg))
                self._full_list_alt.append(selected_alt.to_value(u.deg))

                # if star is within altitude bounds, accept as a new target,
                # otherwise start over.
                if mask_alt[most_distant]:
                    break

        else:
            # first target: brightest star within boundaries
            most_distant = np.argwhere(mask_alt)[0][0]
            self._full_list_az.append(coords_altaz[most_distant].az.to_value(u.deg))
            self._full_list_alt.append(coords_altaz[most_distant].alt.to_value(u.deg))

        # create PointingObservation object
        data = {
            "start_time": start_time,
            "duration": duration,
            "target_pos_ra": coords[most_distant].ra,
            "target_pos_dec": coords[most_distant].dec,
            "location_x": self.location.x,
            "location_y": self.location.y,
            "location_z": self.location.z,
        }
        po = PointingObservation(**data)

        # store in accepted targets list
        self.target_list_az.append(coords_altaz[most_distant].az.to_value(u.deg))
        self.target_list_alt.append(coords_altaz[most_distant].alt.to_value(u.deg))

        return po
