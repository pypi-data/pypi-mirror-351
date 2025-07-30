import logging
import uuid
import copy
from enum import IntFlag
from numpy import nan
import numpy as np
from astropy.time import Time
import astropy.units as u

from ctapipe.core import Container, Field
from ctapointing import __version__
from ctapointing.io import from_name

log = logging.getLogger(__name__)


class SpotType(IntFlag):
    """
    Spot type class.
    """

    UNKNOWN = 0  # Unknown spot
    SKY = 1  # spot from star field
    LED = 2  # spot from LED detection
    LID = 3  # spot from reflection on camera lid


class SpotList(Container):
    """
    Container for storing spot lists.
    """

    uuid = Field(None, "UUID", type=str)
    spot_type = Field(
        None, "spot type (0: UNKNOWN, 1: SKY, 2: LED, 3: LID", dtype=int, ndim=1
    )
    coord_x = Field(None, "x coordinate of spot", dtype=float, ndim=1)
    coord_y = Field(None, "y coordinate of spot", dtype=float, ndim=1)
    var_x = Field(None, "variance of spot profile along x", dtype=float, ndim=1)
    var_y = Field(None, "variance of spot profile along y", dtype=float, ndim=1)
    cov_xy = Field(None, "covariance of spot profile", dtype=float, ndim=1)
    flux = Field(None, "flux of spot", dtype=float, ndim=1)
    peak = Field(None, "peak flux of spot", dtype=float, ndim=1)

    mean_background = Field(nan, "mean background in image", type=float)
    rms_background = Field(nan, "rms background in image", type=float)

    start_time = Field(None, "start time of exposure", type=Time)
    duration = Field(nan * u.s, "exposure duration", unit=u.s)
    moon_position_az = Field(nan * u.deg, "moon position azimuth", unit=u.deg)
    moon_position_alt = Field(nan * u.deg, "moon position altitude", unit=u.deg)
    moon_phase = Field(-1.0, "moon phase", type=float)
    sun_position_az = Field(nan * u.deg, "sun position azimuth", unit=u.deg)
    sun_position_alt = Field(nan * u.deg, "sun position altitude", unit=u.deg)
    chip_temperature = Field(nan * u.K, "camera chip temperature", unit=u.K)
    camera_temperature = Field(nan * u.K, "camera housing temperature", unit=u.K)
    camera_humidity = Field(-1.0, "camera housing humidity", type=float)

    image_uuid = Field(None, "image UUID", type=str)
    camera_uuid = Field(None, "camera UUID", type=str)
    extractor_uuid = Field(None, "spot extractor UUID", type=str)
    detection_threshold = Field(nan, "spot detection threshold", type=float)
    when_extracted = Field(None, "time of spot extraction", type=str)

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
        s += f", image_uuid={self.image_uuid}"
        s += f", len={self.__len__()})"
        return s

    def __len__(self):
        """
        Return length of spot list, i.e. number of spots
        """
        try:
            return len(self["coord_x"])
        except TypeError:
            return 0

    @classmethod
    def from_name(cls, name, **kwargs):
        """
        Load SpotList from HDF5 file or database. See `ctapointing.io.from_name()` for details.
        """
        return from_name(name, cls, **kwargs)

    @property
    def coords_pix(self):
        """
        Return the pixel coordinates as an array.
        """
        return np.array((self.coord_x, self.coord_y)).T

    def append(self, spot_list, copy_meta: bool = False):
        """
        Append spots of another SpotList object to self.
        Only spot information is appended, i.e. any metadata, such as start time, is not touched,
        unless `copy_meta` is True

        Parameters
        ----------
        spot_list: SpotList or None
            Spot list the spots of which should be appended
        copy_meta: bool
            flag that indicates to copy metadata
        """
        if spot_list is None:
            return

        self.spot_type = np.append(self.spot_type, spot_list.spot_type)
        self.coord_x = np.append(self.coord_x, spot_list.coord_x)
        self.coord_y = np.append(self.coord_y, spot_list.coord_y)
        self.var_x = np.append(self.var_x, spot_list.var_x)
        self.var_y = np.append(self.var_y, spot_list.var_y)
        self.cov_xy = np.append(self.cov_xy, spot_list.cov_xy)
        self.flux = np.append(self.flux, spot_list.flux)
        self.peak = np.append(self.peak, spot_list.peak)

        if copy_meta:
            self.mean_background = spot_list.mean_background
            self.rms_background = spot_list.rms_background
            self.start_time = spot_list.start_time
            self.duration = spot_list.duration
            self.moon_position_az = spot_list.moon_position_az
            self.moon_position_alt = spot_list.moon_position_alt
            self.moon_phase = spot_list.moon_phase
            self.sun_position_az = spot_list.sun_position_az
            self.sun_position_alt = spot_list.sun_position_alt
            self.chip_temperature = spot_list.chip_temperature
            self.camera_temperature = spot_list.camera_temperature
            self.camera_humidity = spot_list.camera_humidity
            self.image_uuid = spot_list.image_uuid
            self.camera_uuid = spot_list.camera_uuid
            self.extractor_uuid = self.extractor_uuid
            self.detection_threshold = self.detection_threshold
            self.when_extracted = self.when_extracted

    def select_by_type(self, spot_type: SpotType):
        """
        Return a copy of self, limited to spots of type `spot_type`

        Parameters
        ----------
        spot_type: SpotType
            spot type

        Returns
        -------
        spot_list: SpotList
            new `SpotList`, limited to spots matching the selected spot type
        """

        selected_list = copy.deepcopy(self)
        selection_mask = self.spot_type == spot_type

        selected_list.spot_type = self.spot_type[selection_mask]
        selected_list.coord_x = self.coord_x[selection_mask]
        selected_list.coord_y = self.coord_y[selection_mask]
        selected_list.var_x = self.var_x[selection_mask]
        selected_list.var_y = self.var_y[selection_mask]
        selected_list.cov_xy = self.cov_xy[selection_mask]
        selected_list.flux = self.flux[selection_mask]
        selected_list.peak = self.peak[selection_mask]

        return selected_list
