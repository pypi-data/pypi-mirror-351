import uuid
from numpy import nan

import astropy.units as u
from astropy.time import Time

from ctapipe.core import Container, Field
from ctapointing import __version__
from ctapointing.io import from_name


class ExposureContainer(Container):
    """
    Container to read/write data from the Exposure class.
    """

    uuid = Field(None, "UUID", type=str)
    image_filename = Field(None, "image filename", type=str)
    start_time = Field(None, "start time of exposure", type=Time)
    duration = Field(nan * u.s, "exposure duration", unit=u.s)
    nominal_telescope_pointing_ra = Field(
        nan * u.deg, "nominal telescope pointing (right ascension)", unit=u.deg
    )
    nominal_telescope_pointing_dec = Field(
        nan * u.deg, "nominal telescope pointing (declination)", unit=u.deg
    )
    telescope_pointing_ra = Field(
        nan * u.deg, "reconstructed telescope pointing (right ascension)", unit=u.deg
    )
    telescope_pointing_dec = Field(
        nan * u.deg, "reconstructed telescope pointing (declination)", unit=u.deg
    )

    chip_temperature = Field(nan * u.K, "camera chip temperature", unit=u.K)
    camera_temperature = Field(nan * u.K, "camera temperature inside housing", unit=u.K)
    camera_humidity = Field(-1.0, "relative humidity inside housing", type=float)
    camera_pressure = Field(-1.0, "pressure inside housing", unit=u.hPa)
    camera_gain = Field(-1.0, "camera pixel gain", type=float)

    ambient_temperature = Field(nan * u.K, "ambient temperature", unit=u.K)
    ambient_pressure = Field(nan * u.mbar, "ambient pressure", unit=u.mbar)

    is_simulated = Field(None, "is image simulated?", type=bool)
    camera_uuid = Field(None, "camera configuration UUID", type=str)
    moon_position_az = Field(nan * u.deg, "moon position azimuth", unit=u.deg)
    moon_position_alt = Field(nan * u.deg, "moon position altitude", unit=u.deg)
    moon_phase = Field(-1.0, "moon phase", type=float)
    sun_position_az = Field(nan * u.deg, "sun position azimuth", unit=u.deg)
    sun_position_alt = Field(nan * u.deg, "sun position altitude", unit=u.deg)

    def __init__(self, prefix=None, **fields):
        super().__init__(prefix=prefix, **fields)

        # generate a new UUID if not provided by field import
        if getattr(self, "uuid") is None:
            setattr(self, "uuid", str(uuid.uuid4()))

        if "CTAPOINTING_VERSION" not in self.meta:
            self.meta["CTAPOINTING_VERSION"] = __version__

    @classmethod
    def from_name(cls, name, **kwargs):
        """
        Load ExposureContainer from HDF5 file or database. See `ctapointing.io.from_name()` for details.
        """
        return from_name(name, cls, **kwargs)
