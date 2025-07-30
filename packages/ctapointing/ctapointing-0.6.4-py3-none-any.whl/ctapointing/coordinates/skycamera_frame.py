import numpy as np
import astropy.units as u

from scipy.spatial.transform import Rotation

from astropy.coordinates import (
    BaseCoordinateFrame,
    CoordinateAttribute,
    QuantityAttribute,
    TimeAttribute,
    EarthLocationAttribute,
    FunctionTransform,
    frame_transform_graph,
    CartesianRepresentation,
    AltAz,
)
from astropy.units import Quantity

from ctapipe.coordinates import TelescopeFrame
from ctapipe.coordinates.representation import PlanarRepresentation


class SkyCameraFrame(BaseCoordinateFrame):
    """
    SkyCamera coordinate frame.

    Represents a camera coordinate frame with a fixed orientation w.r.t.
    a TelescopeFrame.

    The coordinate frame can be
    - tilted w.r.t. the Telescope frame by angles
      tilt_x (in the vertical direction, with positive tilt_x meaning that the
      CameraFrame is tilted towards positive altitude), tilt_y (in the horizontal
      direction, with positive tilt_y meaning that the CameraFrame is tilted
      towards positive azimuth)
    - rotated around the axis perpendicular to the CameraFrame's plane, with
      positive angles meaning counterclock-wise rotation
    - scaled by the focal length
    - shifted by offsets offset_x and offset_y.

    When viewed from the telescope towards the sky,
    - the x coordinate points towards the zenith
    - the y coordinate points towards East
    when the TelescopeSystem points to the horizon in Northern direction and no
    tilts have been applied.

    Gnomonic projection of the spherical TelescopeFrame to the planar SkyCameraFrame
    is properly accounted for (*no* small-angle approximation is applied).

    Attributes
    ----------
    focal_length : u.Quantity[length]
        Focal length of the CCD as a unit quantity (usually meters)
    rotation : u.Quantity[angle]
        Rotation angle of the camera (0 deg in most cases)
    tilt_x : u.Quantity[angle]
        Tilt of the camera w.r.t. the telescope pointing in vertical direction
    tilt_y : u.Quantity[angle]
        tilt of the camera w.r.t. the telescope pointing in horizontal direction
    telescope_pointing : SkyCoord[AltAz]
        Pointing direction of the telescope as SkyCoord in AltAz
    obstime: astropy.Time
        observation time
    location: astropy.EarthLocation
        observatory location
    pressure: astropy.Quantity[pressure]
        atmospheric ground-level pressure
    temperature: astropy.Quantity[temperature]
        atmospheric ground-level temperature

    The latter four parameters are needed for proper transformation from/to
    equatorial sky coordinates (ICRS).
    """

    default_representation = PlanarRepresentation

    focal_length = QuantityAttribute(default=1 * u.m, unit=u.m)
    rotation = QuantityAttribute(default=0 * u.deg, unit=u.deg)
    tilt_x = QuantityAttribute(default=0 * u.deg, unit=u.deg)
    tilt_y = QuantityAttribute(default=0 * u.deg, unit=u.deg)
    offset_x = QuantityAttribute(default=0 * u.m, unit=u.m)
    offset_y = QuantityAttribute(default=0 * u.m, unit=u.m)
    telescope_pointing = CoordinateAttribute(frame=AltAz, default=None)

    obstime = TimeAttribute(default=None)
    location = EarthLocationAttribute(default=None)
    pressure = QuantityAttribute(default=None, unit=u.hPa)
    temperature = QuantityAttribute(default=None, unit=u.deg_C)


@frame_transform_graph.transform(FunctionTransform, TelescopeFrame, SkyCameraFrame)
def telescope_to_skycamera(telescope_coord, camera_frame):
    """
    Transformation between TelescopeFrame and SkyCameraFrame
    Is called when a SkyCoord is transformed from TelescopeFrame into SkyCameraFrame
    """

    # calculate cartesian unit vectors of the spherical coordinate:
    # tx is the component along the telescope pointing direction
    # ty is the component along the azimuth coordinate
    # tz is the component along the altitude coordinate

    t = telescope_coord.cartesian.xyz.T

    # camera tilt in horizontal direction
    r = Rotation.from_euler("Z", -camera_frame.tilt_y.to_value(u.rad))
    t_tilted = r.apply(t)

    # camera tilt in vertical direction
    r = Rotation.from_euler("Y", camera_frame.tilt_x.to_value(u.rad))
    t_tilted = r.apply(t_tilted)

    # camera rotation
    r = Rotation.from_rotvec(
        -camera_frame.rotation.to_value(u.rad) * np.array([1, 0, 0])
    )
    t_rot = r.apply(t_tilted)

    # in case only one coordinate is transformed, t_rot.shape=(3,).
    # make sure that array is 2D always.
    t_rot = t_rot.reshape(-1, 3)

    # in the SkyCameraFrame, camx points towards the positive altitude
    # camy points towards the positive azimuth, when the telescope
    # is pointed to the horizon.
    # The tangential (gnomonic) projection is then given by the respective
    # z and x directions of the telescope coordinate unit vectors, scaled
    # by the inverse of tx:
    #
    # am_x = t_rot_z / tx * camera_frame.focal_length
    # cam_y = t_rot_y / tx * camera_frame.focal_length

    tx = t_rot[:, 0].reshape(-1, 1)
    cam = t_rot[:, :0:-1] / tx * camera_frame.focal_length

    # offsets
    offsets = Quantity([camera_frame.offset_x, camera_frame.offset_y]).reshape(1, 2)
    cam += offsets

    representation = PlanarRepresentation(cam[:, 0], cam[:, 1])

    return camera_frame.realize_frame(representation)


@frame_transform_graph.transform(FunctionTransform, SkyCameraFrame, TelescopeFrame)
def skycamera_to_telescope(camera_coord, telescope_frame):
    """
    Transformation between CameraFrame and TelescopeFrame.
    Is called when a SkyCoord is transformed from SkyCameraFrame into TelescopeFrame
    """

    cam_x = camera_coord.cartesian.x
    cam_y = camera_coord.cartesian.y

    # offsets
    cam_x -= camera_coord.offset_x
    cam_y -= camera_coord.offset_y

    # find cartesian representation
    tz_rot = cam_x / camera_coord.focal_length
    ty_rot = cam_y / camera_coord.focal_length
    tx = np.ones(tz_rot.shape)

    # camera rotation
    c = np.cos(-camera_coord.rotation)
    s = np.sin(-camera_coord.rotation)

    ty = ty_rot * c + tz_rot * s
    tz = -ty_rot * s + tz_rot * c

    t_tilted = np.concatenate(
        (tx.reshape((-1, 1)), ty.reshape((-1, 1)), tz.reshape((-1, 1))), axis=1
    )

    # camera tilt in vertical direction
    r = Rotation.from_euler("Y", -camera_coord.tilt_x.to_value(u.rad))
    t_tilted = r.apply(t_tilted)

    # camera tilt in horizontal direction
    r = Rotation.from_euler("Z", camera_coord.tilt_y.to_value(u.rad))
    t = r.apply(t_tilted)

    representation = CartesianRepresentation(x=t[:, 0], y=t[:, 1], z=t[:, 2])

    return telescope_frame.realize_frame(representation)
