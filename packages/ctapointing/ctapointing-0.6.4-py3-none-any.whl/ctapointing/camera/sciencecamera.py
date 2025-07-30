"""
CTA Science camera class.
"""

import uuid
import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord

from ctapipe.core import Component
from ctapipe.core.traits import (
    Unicode,
    Float,
    List,
)
from ctapointing.config import AstroQuantity, from_config
from ctapointing.coordinates import ScienceCameraFrame


class ScienceCamera(Component):
    """
    CTA Science camera class.

    Stores information about the focal plane of the camera, its distance from
    the mirror dish, and the position of pointing LEDs. Provides a method to
    transform sky coordinates into positions on the planar focal plane.
    """

    uuid = Unicode(default_value=str(uuid.uuid4()), help="UUID of Camera").tag(
        config=True
    )
    name = Unicode(help="camera name", allow_none=False).tag(config=True)
    model = Unicode(help="camera model").tag(config=True)
    manufacturer = Unicode(help="camera manufacturer").tag(config=True)
    focal_length = AstroQuantity(
        default_value=16.0 * u.m, help="focal length of mirror dish", allow_none=False
    ).tag(config=True)
    mirror_area = AstroQuantity(
        default_value=100 * u.m**2,
        help="effective area of mirror dish",
        allow_none=False,
    ).tag(config=True)
    rotation = AstroQuantity(
        default_value=0.0 * u.deg,
        help="rotation of camera w.r.t. horizon, in degrees",
        allow_none=False,
    ).tag(config=True)
    tilt = AstroQuantity(
        default_value=[0.0, 0.0] * u.deg,
        help="camera tilt w.r.t. telescope orientation (x/y)",
        allow_none=False,
    ).tag(config=True)
    offset = AstroQuantity(
        default_value=[0.0, 0.0] * u.m,
        help="offset of camera centre w.r.t. telescope orientation (x/y)",
        allow_none=False,
    ).tag(config=True)
    led_positions_x = AstroQuantity(
        default_value=[] * u.m, help="LED positions (x coordinate) in camera frame"
    ).tag(config=True)
    led_positions_y = AstroQuantity(
        default_value=[] * u.m, help="LED positions (y coordinate) in camera frame"
    ).tag(config=True)
    led_intensity = List(
        default_value=[], help="LED intensities (for simulations)"
    ).tag(config=True)
    led_radius = AstroQuantity(
        default_value=0.5 * u.mm, help="radius of the LED pinholes (for simulations)"
    ).tag(config=True)
    body_vertex_positions_x = AstroQuantity(
        default_value=[] * u.m,
        help="x coordinate of vertices defining body outer dimensions (for simulations, in camera frame)",
    ).tag(config=True)
    body_vertex_positions_y = AstroQuantity(
        default_value=[] * u.m,
        help="y coordinate of vertices defining body outer dimensions (for simulations, in camera fram)",
    ).tag(config=True)
    body_intensity = Float(
        default_value=0.0, help="intensity of camera body (for simulations)"
    ).tag(config=True)
    lid_radius = AstroQuantity(
        default_value=1.0 * u.m, help="radius of circular camera lid"
    ).tag(config=True)
    lid_intensity = Float(
        default_value=0.0, help="intensity of camera lid (for simulations)"
    ).tag(config=True)

    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(config=config, parent=parent, **kwargs)

        self.telescope_pointing_altaz = None

    @classmethod
    def from_config(cls, **kwargs):
        """
        Read a camera configuration from either configuration file or database.
        Either the path of a configuration file ('input_url') or a database collection
        ('collection') must be provided.


        Parameters
        ----------
        input_url: str or Path
            path of the configuration file.
        name: str
            name of the camera (as in `ScienceCamera.name`).
            When loading the configuration from file, can be set to check that the configuration with the
            correct name is loaded.
            When loading from database, is used to identify the correct database record.
        uuid: str
            UUID of the camera (as in `ScienceCamera.uuid`).
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
        camera: ScienceCamera object
        """
        # load configuration and construct instance
        config = from_config(component_name=cls.__name__, **kwargs)
        return cls(config=config)

    def __str__(self):
        s = f"{self.name} (uuid={self.uuid})\n"
        s += "parameters:\n"
        s += f"  focal length:          {self.focal_length}\n"
        s += f"  rotation:              {self.rotation}\n"
        s += f"  tilt:                  {self.tilt}\n"
        s += f"  offset:                {self.offset}\n"
        return s

    def __repr__(self):
        return f"{self.__class__.__name__}" f"(uuid={self.uuid}, name={self.name})"

    @property
    def led_positions(self):
        """
        Return the camera LED positions in the ScienceCameraFrame
        """
        return SkyCoord(
            self.led_positions_x, self.led_positions_y, frame=self.sciencecameraframe
        )

    @property
    def centre(self):
        """
        Return the centre of the camera in the ScienceCameraFrame
        """
        return SkyCoord(0.0 * u.m, 0.0 * u.m, frame=self.sciencecameraframe)

    @property
    def body_vertex_positions(self):
        if self.body_vertex_positions_x is not None:
            vertex_positions = SkyCoord(
                self.body_vertex_positions_x,
                self.body_vertex_positions_y,
                frame=self.sciencecameraframe,
            )
        else:
            vertex_positions = None

        return vertex_positions

    @property
    def sciencecameraframe(self):
        """
        Return a ScienceCameraFrame object, initialised from current
        camera (focal length, rotations, tilts etc.) properties.

        Can be used to transform from/to SciemceCameraFrame using
        up-to-date transformation parameters.
        """
        try:
            return ScienceCameraFrame(
                focal_length=self.focal_length,
                rotation=self.rotation,
                tilt_x=self.tilt[0],
                tilt_y=self.tilt[1],
                offset_x=self.offset[0],
                offset_y=self.offset[1],
                telescope_pointing=self.telescope_pointing_altaz,
            )
        except Exception as e:
            self.log.error(e)
            return None

    def project_into(self, coords, telescope_pointing=None):
        """
        Project a given array of altaz coordinates into the science camera frame.
        Takes current camera orientation and tilts into account.

        Parameters
        ----------
        coords: array(astropy.SkyCoord)
            array of sky coordinates in the AltAz system
        telescope_pointing: astropy.SkyCoord
            telescope pointing position (RADec or AltAz system)

        Returns
        -------
        coords_proj: SkyCoord
            2D projections in chip coordinates (in ScienceCameraFrame)

        todo: star projection is wrong when translation t is switched on. This happens because
        the altaz position of the (infinitely) distant star is converted to a vector on the
        unit circle. Should explicitly distinguish between star projection and projection of
        world objects.
        """

        if telescope_pointing is None:
            telescope_pointing = self.telescope_pointing_altaz

        frame = ScienceCameraFrame(
            focal_length=self.focal_length,
            rotation=self.rotation,
            tilt_x=self.tilt[0],
            tilt_y=self.tilt[1],
            offset_x=self.offset[0],
            offset_y=self.offset[1],
            telescope_pointing=telescope_pointing,
        )

        coords_proj = coords.transform_to(frame)

        return coords_proj

    def project_from(self, coords, obstime, telescope_pointing):
        """
        Project given SkyCameraFrame coordinates back to
        AltAz.

        Parameters
        ----------
        coords: SkyCoord in SkyCameraFrame
            coordinates on CCD chip in SkyCameraFrame
        obstime: Astropy.Time
            time of the observation
        telescope_pointing: SkyCoord
            telescope pointing direction

        Returns
        -------
        coords_altaz: SkyCoord
            transformed coordinates in the AltAz system
        """

        # update parameters of SkyCameraFrame
        ccd = ScienceCameraFrame(
            focal_length=self.focal_length[0],
            rotation=self.rotation,
            tilt_x=self.tilt[0],
            tilt_y=self.tilt[1],
            offset_x=self.offset[0],
            offset_y=self.offset[1],
            obstime=obstime,
            location=telescope_pointing.location,
            telescope_pointing=telescope_pointing,
            pressure=telescope_pointing.pressure,
            temperature=telescope_pointing.temperature,
        )

        coords_new = SkyCoord(coords, frame=ccd)
        coords_altaz = coords_new.transform_to(telescope_pointing)

        return coords_altaz


class FlashCam(ScienceCamera):
    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(config=config, parent=parent, **kwargs)

        # LED positions private communication GP (12.7.2021),
        # as viewed from the backside of the camera
        self.led_positions_x = [
            -339.70,
            -927.70,
            -1136.20,
            -1136.20,
            -927.70,
            -339.70,
            339.70,
            927.70,
            1136.20,
            1136.20,
            927.70,
            339.70,
        ] * u.mm

        self.led_positions_y = [
            1267.30,
            927.70,
            656.00,
            -656.00,
            -927.70,
            -1267.30,
            -1267.30,
            -927.70,
            -656.00,
            656.00,
            927.70,
            1267.30,
        ] * u.mm

        self.led_intensity = [
            60000,
            60000,
            60000,
            60000,
            60000,
            60000,
            60000,
            60000,
            60000,
            60000,
            60000,
            60000,
        ]

        height, width = (2.918, 2.918)
        self.body_vertex_positions_x = [
            -width / 2,
            width / 2,
            width / 2,
            -width / 2,
        ] * u.m
        self.body_vertex_positions_y = [
            -height / 2,
            -height / 2,
            height / 2,
            height / 2,
        ] * u.m
        self.body_intensity = 10

        self.lid_radius = 400.0 * u.mm
        self.lid_intensity = 20

        self.mirror_area = 88.0 * u.m**2

        self.rotation = 0.0 * u.deg
        self.focal_length = 16.0 * u.m
        self.tilt = [0.0, 0.0] * u.deg
        self.offset = [0.0, 0.0] * u.m
        self.led_radius = 5e-3 * u.m


class MAGICCam(ScienceCamera):
    """
    Dummy implementation of a MAGIC camera.
    """

    def __init__(self, name="MAGICCam"):
        ScienceCamera.__init__(self, name=name)

        self.rotation = 0.0 * u.deg
        self.focal_length = 17 * u.m
        self.tilt = [0.0, 0.0] * u.deg
        self.offset = [0.0, 0.0] * u.m

        self._led_positions = self._construct_leds_on_circle()
        self.led_radius = 5e-3 * u.m  # TODO: t.b.d.
        self.led_intensity = [
            60000,
            60000,
            60000,
            60000,
            60000,
            60000,
            60000,
            60000,
            60000,
            60000,
            60000,
            60000,
        ]

        height, width = (2.0, 2.3)
        self._body_vertex_positions = [
            [-width / 2, -height / 2],
            [width / 2, -height / 2],
            [width / 2, height / 2],
            [-width / 2, height / 2],
        ] * u.m

        self.body_intensity = 1000

    @staticmethod  # TODO make it a property?
    def _construct_leds_on_circle():
        """
        Helper function to construct the position of the 8
        MAGIC LEDs in the science camera frame
        """

        radius = 0.63 * u.m  # LED circle radius (from MAGIC drawings)
        position_angles = np.linspace(0, 330, 12) * u.deg

        x = (-radius * np.cos(position_angles)).reshape(-1, 1)
        y = (radius * np.sin(position_angles)).reshape(-1, 1)

        return np.concatenate((x, y), axis=1)
