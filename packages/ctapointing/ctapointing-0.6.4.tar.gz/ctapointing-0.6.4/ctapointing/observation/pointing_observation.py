import logging
import uuid

from numpy import nan
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, SkyCoord, ICRS

from ctapipe.core import Container, Field
from ctapointing import __version__
from ctapointing.io import from_name

log = logging.getLogger(__name__)


class PointingObservation(Container):
    """
    Class storing information about a pointing observation
    """

    uuid = Field(None, "UUID", type=str)
    target_name = Field("", "target name", type=str)
    start_time = Field(None, "start time of exposure", type=Time)
    duration = Field(nan * u.s, "exposure duration", unit=u.s)
    target_pos_ra = Field(nan * u.deg, "target position (right ascension)", unit=u.deg)
    target_pos_dec = Field(nan * u.deg, "target position (declination)", unit=u.deg)
    location_x = Field(nan * u.m, "geocentric location (x)", unit=u.m)
    location_y = Field(nan * u.m, "geocentric location (y)", unit=u.m)
    location_z = Field(nan * u.m, "geocentric location (z)", unit=u.m)
    ambient_pressure = Field(nan * u.mbar, "atmospheric pressure", unit=u.mbar)
    ambient_temperature = Field(nan * u.deg_C, "atmospheric temperature", unit=u.deg_C)

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
        s += f", start_time={self.start_time}"
        s += f", target_pos_altaz={self.target_pos_altaz})"
        return s

    @classmethod
    def from_name(cls, name, **kwargs):
        """
        Load PointingObservation from HDF5 file or database. See `ctapointing.io.from_name()`for details.
        """
        return from_name(name, cls, **kwargs)

    @property
    def altazframe(self):
        """
        Return AltAz frame, using currently available meta information.
        """
        try:
            location = EarthLocation(
                x=self.location_x, y=self.location_y, z=self.location_z
            )
        except AttributeError:
            location = None

        return AltAz(
            obstime=self.mean_observation_time,
            location=location,
            pressure=self.ambient_pressure,
            temperature=self.ambient_temperature,
        )

    @property
    def mean_observation_time(self):
        """
        Return time of mean time of observation.

        Returns
        -------
        mean observation time: astropy.Time
        """
        try:
            return self.start_time + self.duration / 2
        except TypeError:
            return None

    @property
    def target_pos_altaz(self):
        """
        Return AltAz telescope pointing, i.e. the telescope orientation
        at the time of mean exposure.
        """
        try:
            pos = SkyCoord(ra=self.target_pos_ra, dec=self.target_pos_dec, frame=ICRS)
            return pos.transform_to(self.altazframe)
        except:
            return None
