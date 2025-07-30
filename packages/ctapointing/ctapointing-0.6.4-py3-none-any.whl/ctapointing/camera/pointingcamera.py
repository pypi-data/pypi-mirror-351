import uuid
import numpy as np

import astropy.units as u
from astropy.coordinates import (
    SkyCoord,
    EarthLocation,
)

from ctapipe.core import Component, non_abstract_children
from ctapipe.core.traits import (
    Unicode,
    Float,
    Int,
    List,
    Enum,
    AstroTime,
)
from ctapointing.config import (
    AstroQuantity,
    AstroEarthLocation,
    from_config,
)
from ctapointing.coordinates import SkyCameraFrame
from .distortion import DistortionCorrection, DistortionCorrectionNull


class PointingCamera(Component):
    """
    Pointing camera class.

    Hosts routines and parameters necessary to project Alt-Az coordinates into
    the chip plane.

    Uses correct tangential projection into the chip plane (i.e. no small-angle
    approximation). Takes account for the orientation of the telescope
    (in Alt-Az coordinates), rotation of the camera w.r.t. the horizon, a tilt of
    the camera's optical axis w.r.t. the telescope pointing, and possible shifts
    of the chip centre w.r.t. the optical axis and lens distortions.

    The camera coordinate system has its origin exactly at the centre of the chip
    (for chips with odd number of pixels in the middle of the central pixel, for
    chips with even number of pixels at the boundary between the two innermost pixels).

    Transformation of camera coordinates into chip coordinates follows the FITS/astropy
    standard, in which integer pixel coordinates are at the centre of a pixel,
    with pixel index 0 covering the range [-0.5, 0.5], representing physical pixel 1.

    `x` points from bottom to top of the up-right chip, when viewing from the chip into the scene;
    `y` points from left to right.

    By default, a `ctapointing.camera.DistortionCorrectionNull` model is loaded as the default
    for the correction of lens distortions. Any other DistortionCorrection model can be applied
    by adding it as a sub-component of the camera config in the configuration file.

    Parameters
    ----------
    uuid: Unicode
        UUID of the camera
    name: Unicode
        name of the camera
    location: astropy.coordinates.EarthLocation
        location of the camera on Earth
    f_stop: Float
        f_stop of the lens (focal length / aperture diameter)
    num_pix: List of Int: number of pixels in x and y
    pixel_size: AstroQuantity[length]
        size of a pixel edge
    tilt: AstroQuantity[angle]
        camera tilt w.r.t. telescope orientation (x/y)
    offset: AstroQuantity[length]
        offset of chip centre w.r.t. telescope orientation (x/y)
    rotation: AstroQuantity[angle]
        rotation of the camera around optical axis
    noise_mean: List[float]
        list of mean noise values (one per pixel fraction)
    noise_rms: List[float]
        list of rms noise values (one per pixel fraction)
    noise_pixel_fraction: List[Float]
        list of pixel fractions
    expansion_coefficient: Float
        chip expansion coefficient
    efficiency: Float
        pixel efficiency
    manufacturer: Unicode
        camera manufacturer
    model: Unicode
        camera model
    serial_number: Unicode
        camera serial number
    telescope_id: Int
        telescope ID
    dtype: Enum
        pixel depth (in bits)
    used_since: AstroTime
        date and time of first operation
    used_until: AstroTime
        date and time of decommissioning
    """

    uuid = Unicode(default_value=str(uuid.uuid4()), help="UUID of Camera").tag(
        config=True
    )
    name = Unicode(help="camera name", allow_none=False).tag(config=True)
    model = Unicode(help="camera model").tag(config=True)
    manufacturer = Unicode(help="camera manufacturer").tag(config=True)
    serial_number = Unicode(help="camera serial number", allow_none=True).tag(
        config=True
    )

    telescope_id = Int(help="telescope ID", allow_none=True).tag(config=True)
    location = AstroEarthLocation(
        help="earth location of camera, either 'x, y, z' in geocentric"
        "coordinates or site location string",
        allow_none=True,
    ).tag(config=True)

    f_stop = Float(help="f-stop of lens", allow_none=False).tag(config=True)
    focal_length = AstroQuantity(
        help="focal length of lens (x/y chip direction)", allow_none=False
    ).tag(config=True)
    num_pix = List(
        help="camera chip number of pixels (x/y chip direction", allow_none=False
    ).tag(config=True)
    pixel_size = AstroQuantity(help="camera pixel size", allow_none=False).tag(
        config=True
    )
    tilt = AstroQuantity(
        default_value=[0.0, 0.0] * u.deg,
        help="camera tilt w.r.t. telescope orientation (x/y)",
        allow_none=False,
    ).tag(config=True)
    offset = AstroQuantity(
        default_value=[0.0, 0.0] * u.m,
        help="offset of chip centre w.r.t. telescope orientation (x/y)",
        allow_none=False,
    ).tag(config=True)
    rotation = AstroQuantity(
        default_value=0.0 * u.deg,
        help="rotation of camera w.r.t. horizon, in degrees",
        allow_none=False,
    ).tag(config=True)
    noise_mean = List(
        default_value=[],
        help="list of mean noise values (one per pixel fraction)",
    ).tag(config=True)
    noise_rms = List(
        default_value=[],
        help="list of rms noise values (one per pixel fraction)",
    ).tag(config=True)
    noise_pixel_fraction = List(default_value=[], help="list of pixel fractions").tag(
        config=True
    )
    expansion_coefficient = AstroQuantity(
        default_value=0.0 * u.m, help="chip expansion coefficient"
    ).tag(config=True)
    efficiency = Float(default_value=1.0, help="pixel efficiency").tag(config=True)

    bit_depth = Enum(
        values=[8, 16, 32],
        default_value=16,
        help="pixel depth (bits)",
    ).tag(config=True)
    used_since = AstroTime(
        help="date of first usage", default_value=None, allow_none=True
    ).tag(config=True)
    used_until = AstroTime(
        help="date of decommissioning", default_value=None, allow_none=True
    ).tag(config=True)

    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(config=config, parent=parent, **kwargs)

        # create DistortionCorrection from name
        self.distortion_correction = (
            DistortionCorrectionNull()
        )  # fall back to null correction model

        # instantiate correct DistortionCorrection class and load its
        # configuration from the sub-config of the camera class
        if config is not None:
            for distortion_class in non_abstract_children(DistortionCorrection):
                if distortion_class.__name__ in config[self.__class__.__name__].keys():
                    self.distortion_correction = Component.from_name(
                        name=distortion_class.__name__,
                        config=config[self.__class__.__name__],
                        **kwargs,
                    )

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
            name of the camera (as in `PointingCamera.name`).
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
        camera: PointingCamera object
        """
        # load configuration and construct instance
        config = from_config(component_name=cls.__name__, **kwargs)
        return cls(config=config)

    @property
    def chip_size(self):
        """
        Camera chip size (in physical units).

        Returns
        -------
        (size_x, size_y): tuple of astropy.Quantity
            size along x and y axes
        """
        try:
            return self.num_pix * self.pixel_size
        except TypeError:
            return None

    @property
    def chip_area(self):
        """
        Camera chip area (in physical units).

        Returns
        -------
        area: astropy.Quantity
            chip area
        """
        chip_size = self.chip_size
        try:
            return chip_size[0] * chip_size[1]
        except TypeError:
            return None

    @property
    def chip_centre(self):
        """
        Camera chip centre in physical pixel coordinates.

        * for odd number of pixels, the chip centre is located at the centre of the central pixel,
          hence the centre corresponds to an integer in physical pixel coordinates
        * for even number of pixels, the chip centre is in between
          the innermost pixels, hence the centre corresponds to an integer+0.5 in physical
          pixel coordinates
        * the pixel with index 0 covers the coordinate range [-0.5, 0.5]

        Returns
        -------
        (centre_x, centre_y): array of floats
            physical pixel coordinates of chip centre
        """
        try:
            return np.array(self.num_pix) // 2 - 0.5 * (
                (np.array(self.num_pix) + 1) % 2
            )  # + 1
        except (AttributeError, TypeError):
            return None

    @property
    def fov(self):
        """
        Angular field of view.

        Returns
        -------
        (fov_x, fov_y): tuple of astropy.Angle
            field of view along x and y direction
        """
        try:
            return np.arctan(self.chip_size / self.focal_length)
        except (AttributeError, TypeError):
            return None

    @property
    def fov_plane_projected(self):
        """
        Field of view, projected onto
        a tangent plane of the unit sphere.

        Returns
        -------
        (fov_x, fov_y): tuple of astropy.Angle
            field of view along x and y direction, plane projected
        """
        try:
            return (self.chip_size / self.focal_length).decompose() * u.rad
        except (AttributeError, TypeError):
            return None

    @property
    def aperture(self):
        """
        Aperture of the camera lens.

        Returns
        -------
        aperture: astropy.Quantity
            lens aperture in millimeter-squared
        """
        try:
            aperture = np.pi * (self.focal_length[0] / self.f_stop / 2) ** 2
            return aperture.to("mm2")
        except (AttributeError, TypeError):
            return None

    @property
    def pixel_angle(self):
        """
        Angle covered by a pixel edge in units of arcsec

        Returns
        -------
        angle: astropy.Quantity
            angle in arc seconds
        """
        try:
            pixel_angle = (self.pixel_size / self.focal_length).decompose() * u.rad
            return pixel_angle.to("arcsec")
        except (AttributeError, TypeError):
            return None

    @property
    def pixel_solid_angle(self):
        """
        Returns the solid angle of a pixel in units of arc seconds squared

        Returns
        -------
        solid_angle: astropy.Quantity
            solid angle in arc seconds squared
        """
        try:
            pixel_angle = self.pixel_angle
            solid_angle = pixel_angle[0] * pixel_angle[1]
            return solid_angle.to("arcsec2")
        except (AttributeError, TypeError):
            return None

    def project_into(
        self, coords, telescope_pointing, use_obstime_of_first_coordinate=True
    ):
        """
        Project a given array of altaz coordinates into the pointing camera chip.
        Takes current camera orientation, camera intrinsic parameters and
        distortions into account.

        Parameters
        ----------
        coords: array(astropy.SkyCoord)
            array of sky coordinates in the AltAz system
        telescope_pointing: astropy.SkyCoord
            telescope pointing position (RADec or AltAz system)
        use_obstime_of_first_coordinate: bool
            use observation time of the first coordinate if array of SkyCoords is provided.
            This reduces computation time by a lot, and should be the default for coordinates
            that are part of the same image.

        Returns
        -------
        coords_proj: SkyCoord
            2D projections in chip coordinates (in SkyCameraFrame)

        todo: star projection is wrong when translation t is switched on. This happens because
        the altaz position of the (infinitely) distant star is converted to a vector on the
        unit circle. Should explicitly distinguish between star projection and projection of
        world objects.
        """

        # Transform RADec telescope pointing into AltAz, using obstime information
        # of the input coordinates
        # TODO: for performance reasons, assume same observation time of
        # all coordinates, instead of transforming each coordinate by its own
        # AltAz system.

        if use_obstime_of_first_coordinate:
            # SkyCoord can be iterable or scalar
            try:
                first_coord = coords[0]
            except TypeError:
                first_coord = coords
            finally:
                obstime = first_coord.obstime
                frame = first_coord.frame
        else:
            obstime = coords.obstime
            frame = coords.frame

        location = (
            self.location
            if telescope_pointing.location is None
            else telescope_pointing.location
        )
        tel_pointing_altaz = telescope_pointing.transform_to(frame)

        # Transform to SkyCameraFrame
        ccd = SkyCameraFrame(
            focal_length=self.focal_length[0],
            rotation=self.rotation,
            tilt_x=self.tilt[0],
            tilt_y=self.tilt[1],
            offset_x=self.offset[0],
            offset_y=self.offset[1],
            obstime=obstime,
            location=location,
            telescope_pointing=tel_pointing_altaz,
            pressure=telescope_pointing.pressure,
            temperature=telescope_pointing.temperature,
        )

        coords_proj = coords.transform_to(ccd)

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
        ccd = SkyCameraFrame(
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

    def transform_to_pixels(self, coords_cam):
        """
        Transform coordinates from the SkyCameraFrame to pixel coordinates.

        Parameters
        ----------
        coords_cam: SkyCoord
            coordinates in the SkyCameraFrame

        Returns
        -------
        coords_pix: numpy.array
            2D array of pixel coordinates
        """

        centre = self.chip_centre

        cx = (
            (coords_cam.x / self.pixel_size)
            .to_value(u.dimensionless_unscaled)
            .reshape((-1, 1))
        )
        cy = (
            (coords_cam.y / self.pixel_size)
            .to_value(u.dimensionless_unscaled)
            .reshape((-1, 1))
        )

        coords_pix = np.concatenate((cx, cy), axis=1)

        # apply chip and lens distortions
        coords_pix = self.distortion_correction.apply_inverse_correction(coords_pix)

        return coords_pix + centre

    def transform_to_camera(self, coords_pix):
        """
        Transform coordinates from the pixel system to the SkyCameraFrame.

        Parameters
        ----------
        coords_pix: 2D array of pixel coordinates

        Returns
        -------
        cam_coords: SkyCoord
            coordinates in SkyCameraFrame
        """

        c = (coords_pix - self.chip_centre).reshape(-1, 2)

        # apply chip and lens distortions
        c = self.distortion_correction.apply_correction(c)

        ccd_sys = SkyCameraFrame(
            focal_length=self.focal_length[0],
            rotation=self.rotation,
            tilt_x=self.tilt[0],
            tilt_y=self.tilt[1],
            offset_x=self.offset[0],
            offset_y=self.offset[1],
        )

        c = c * self.pixel_size
        cam_coords = SkyCoord(x=c[:, 0], y=c[:, 1], frame=ccd_sys)

        return cam_coords

    def clip_to_chip(self, pix_coords, tolerance=0):
        """
        Clip an array of pixel coordinates to those coordinates which are inside the
        chip boundaries.

        Parameters
        ----------
        pix_coords: array
            2D array of pixel coordinates
        tolerance: float
            tolerance in units of pixels

        Returns
        -------
        mask: numpy.array
            boolean array of same shape as pix_coords, with positions which
            are inside the chip boundaries (and within tolerance) set to True (and False otherwise)
        """

        nx, ny = self.num_pix

        mask = (
            (pix_coords[:, 0] < nx + tolerance - 0.5)
            & (pix_coords[:, 0] >= -tolerance - 0.5)
            & (pix_coords[:, 1] < ny + tolerance - 0.5)
            & (pix_coords[:, 1] >= -tolerance - 0.5)
        )

        return mask

    def __str__(self):
        s = f"{self.name} (uuid={self.uuid})\n"
        s += f"  manufacturer:          {self.manufacturer}\n"
        s += f"  model:                 {self.model}\n"
        s += f"  serial number:         {self.serial_number}\n"
        s += f"  telescope id:          {self.telescope_id}\n"
        s += f"  used since:            {self.used_since}\n"
        s += f"  used until:            {self.used_until}\n"
        s += f"  focal length:          {self.focal_length}\n"
        s += f"  pixel size:            {self.pixel_size}\n"
        s += f"  number of pixels:      {self.num_pix}\n"
        s += f"  chip size:             {self.chip_size}\n"
        s += f"  chip centre:           {self.chip_centre}\n"
        s += f"  pixel angle:           {self.pixel_angle}\n"
        s += f"  pixel solid angle:     {self.pixel_solid_angle}\n"
        try:
            fov = self.fov.to(u.deg)
        except (AttributeError, TypeError):
            fov = None
        s += f"  camera field of view:  {fov}\n"
        try:
            rot = self.rotation.to(u.deg)
        except (AttributeError, TypeError):
            rot = None
        s += f"  camera rotation:       {rot}\n"
        try:
            tx = self.tilt[0].to(u.deg)
            ty = self.tilt[1].to(u.deg)
        except (AttributeError, TypeError):
            tx, ty = None, None
        s += f"  camera tilts (x/y):    {tx}, {ty}\n"
        s += f"  chip offsets (x/y):    {self.offset[0]}, {self.offset[1]}\n"
        try:
            loc = self.location.to_geodetic()
        except (AttributeError, TypeError):
            loc = None
        s += f"  location:              {loc}\n"
        s += f"  distortion correction: {self.distortion_correction}"
        return s

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(uuid={self.uuid}, name={self.name}, "
            f"manufacturer={self.manufacturer}, model={self.model})"
        )


class ApogeeAspen8050Camera(PointingCamera):
    """
    Class that describes a generic Apogee Aspen 8050 CCD camera.
    """

    def __init__(self, config=None, parent=None, **kwargs):
        self.name = "ApogeeAspen8050"
        self.manufacturer = "Apogee Imaging Systems"
        self.model = "Aspen CG8050-S-G01-HSH"
        self.pixel_size = 5.4 * u.micron  # pixel size
        self.num_pix = [2472, 3296]  # number of pixels along x,y
        self.bit_depth = 16  # data type
        self.efficiency = 0.6  # photon detection efficiency
        self.noise_mean = [1300]
        self.noise_rms = [50]
        self.noise_pixel_fraction = [1]
        self.f_stop = 5.6  # f_stop of lens (focal length/aperture diameter)
        self.focal_length = [50.0, 50.0] * u.mm
        self.location = EarthLocation.of_site("Roque de los Muchachos")

        super().__init__(config=config, parent=parent, **kwargs)


class SBIG_STC428_Camera(PointingCamera):
    """
    Class that describes an SBIG STC-428 CMOS camera.
    """

    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(config=config, parent=parent, **kwargs)

        self.name = "SBIG STC-428"
        self.manufacturer = "SBIG"
        self.model = "STC-428-OEM"
        self.pixel_size = 4.5 * u.micron  # pixel size
        self.num_pix = [2200, 3208]  # number of pixels along x,y
        self.bit_depth = 16  # data type
        self.efficiency = 0.6  # photon detection efficiency
        self.f_stop = 5.6  # f_stop of lens (focal length/aperture diameter)
        self.focal_length = [50.0, 50.0] * u.mm
        self.location = EarthLocation.of_site("Roque de los Muchachos")


class ZWO_ASI2600_Camera(PointingCamera):
    """
    Class that describes a ZWO ASI2600-MM CMOS camera.
    """

    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(config=config, parent=parent, **kwargs)

        self.uuid = "994e6ee4-ca6f-4354-b1af-6006766ddc3f"  # assign unique UUID for identification
        self.name = "ZWO ASI2600"
        self.manufacturer = "ZW Optics"
        self.model = "ASI2600-MM Pro"
        self.pixel_size = 3.76 * u.micron  # pixel size
        self.num_pix = [4176, 6248]  # number of pixels along x,y
        self.bit_depth = 16
        self.f_stop = 11.0  # f_stop of lens (focal length/aperture diameter)
        self.focal_length = [50.0, 50.0] * u.mm
        self.noise_mean = [45]
        self.noise_rms = [45]
        self.noise_pixel_fraction = [1]
        self.location = EarthLocation.of_site("Roque de los Muchachos")
