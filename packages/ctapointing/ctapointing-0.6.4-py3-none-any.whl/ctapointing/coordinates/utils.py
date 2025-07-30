import logging
import numpy as np
from scipy.spatial.transform import Rotation
from astropy.coordinates import SkyCoord
import astropy.units as u

log = logging.getLogger(__name__)


def rotate_around_vector(x, v, alpha):
    """
    Rotate vector x around direction vector v by angle alpha.
    Used e.g. to rotate the chip plane around the camera observation
    directon.
    :param array x: vector to rotate
    :param array v: vector to rotate around
    :param astropy.Quantity alpha: rotation angle
    :returns: rotated vector
    :rtype: array
    """

    # we perform an active transformation rather than a passive one
    a = -alpha

    # make sure rotation vector is normalised
    n = (v / np.linalg.norm(v)).flatten()

    # original rotation operation:
    # x_rot = np.dot(n, np.dot(n,x)) + np.cos(alpha) * np.cross(np.cross(n,x), n) \
    #  + np.sin(alpha) * np.cross(n, x)

    # but scipy's rotation is much faster and can be applied to
    # sets of vectors:
    r = Rotation.from_rotvec(a.to("rad").value * n)
    x_rot = r.apply(x)

    return x_rot


def rotate_to_pole(c, o):
    """
    Rotate a set of spherical coordinates to the pole of the unit sphere.
    The rotation is done such that the reference coordinate o is rotated
    directly to the pole, with the coordinates c having equal angular
    position w.r.t. o as before the transformation.
    :param SkyCoord c: array of coordinates to transform
    :param SkyCoord o: reference coordinate to transform
    """

    try:
        lat_angle = o.alt
    except:
        lat_angle = o.dec

    c.representation_type = "cartesian"
    c_vec = np.array([c.x, c.y, c.z]).T
    c.representation_type = "spherical"

    o.representation_type = "cartesian"
    o_vec = np.array([o.x, o.y, o.z])
    o.representation_type = "spherical"

    pole_vec = np.array([0.0, 0.0, 1.0])
    rot_vec = np.cross(pole_vec, o_vec)
    rot_angle = 90 * u.deg - lat_angle

    c_vec_rot = rotate_around_vector(c_vec, rot_vec, rot_angle)

    c_rot = SkyCoord(
        x=c_vec_rot[:, 0],
        y=c_vec_rot[:, 1],
        z=c_vec_rot[:, 2],
        frame=c.frame,
        representation_type="cartesian",
    )

    c_rot.representation_type = "spherical"

    return c_rot


def rotate_from_pole(c, o):
    """
    Rotate a set of spherical coordinates from the pole of the unit sphere to
    some position given by the reference coordinate o.
    The rotation is done such that the pole is rotated
    directly to the reference coordinate, with the coordinates c
    having equal angular position w.r.t. o as before the transformation.
    :param SkyCoord c: array of coordinates to transform
    :param SkyCoord o: reference coordinate to transform
    """

    try:
        lat_angle = o.alt
    except:
        lat_angle = o.dec

    c.representation_type = "cartesian"
    c_vec = np.array([c.x, c.y, c.z]).T
    c.representation_type = "spherical"

    o.representation_type = "cartesian"
    o_vec = np.array([o.x, o.y, o.z])
    o.representation_type = "spherical"

    pole_vec = np.array([0.0, 0.0, 1.0])
    rot_vec = np.cross(pole_vec, o_vec)
    rot_angle = -(90 * u.deg - lat_angle)

    c_vec_rot = rotate_around_vector(c_vec, rot_vec, rot_angle)

    c_rot = SkyCoord(
        x=c_vec_rot[:, 0],
        y=c_vec_rot[:, 1],
        z=c_vec_rot[:, 2],
        frame=c.frame,
        representation_type="cartesian",
    )

    c_rot.representation_type = "spherical"

    return c_rot


def tangential_projection(c, t):
    """
    Projects a coordinate c on the unit sphere onto a tangential plane that
    touches the sphere in the tangent point t.
    :param astropy.SkyCoord c: spherical coordinate to map
    :param astropy.SkyCoord t: spherical coordinate of tangent point
    :returns: projected plane coordinates (x,y)
    :rtype: array
    """

    # check that distance between coordinate and tangent point does not
    # exceed 90 deg
    invalid_angle_mask = c.separation(t) >= 90 * u.deg

    if np.any(invalid_angle_mask):
        log.warning(
            "tangential projection: warning: for some of the coordinates,"
            + " distance to tangent point exceeds 90 deg"
        )

    # rotate coordinate system such that tangent point is at the pole
    try:
        lat_angle = t.alt
    except:
        lat_angle = t.dec

    # rotation angle
    alpha = 90 * u.deg - lat_angle

    # convert tangent point to cartesian direction vector,
    # where z-coordinate points to the pole
    r = t.representation_type
    t.representation_type = "cartesian"
    t_vec = np.array([t.x, t.y, t.z])
    t.representation_type = r

    # find the direction vector around which to rotate the tangent
    # point to the pole. This is the vector perpendicular to the
    # plane made of the pole direction and the tangent point direction.
    pole_vec = np.array([0, 0, 1])
    rot_vec = np.cross(pole_vec, t_vec)

    # now rotate all coordinates c to the pole
    r = c.representation_type
    c.representation_type = "cartesian"
    c_vec = np.array([c.x, c.y, c.z]).T
    c.representation_type = r

    c_vec_rot = rotate_around_vector(c_vec, rot_vec, alpha)

    # finally, do tangential projection at the pole.
    # the x,y coordinates in the tangential plane system
    # are simply given by dividing the rotated x,y coordinates
    # by the respective z coordinate.
    c_vec_proj = np.copy(c_vec_rot[:, 0:2])
    c_vec_proj[:, 0] /= c_vec_rot[:, 2]
    c_vec_proj[:, 1] /= c_vec_rot[:, 2]

    # mark coordinates that could not be projected as 'nan'
    invalid_angle_mask = invalid_angle_mask[:, np.newaxis]
    invalid_angle_mask = np.repeat(invalid_angle_mask, 2, axis=1)
    c_vec_proj[invalid_angle_mask] = np.nan

    return c_vec_proj


def inv_tangential_projection(c, t):
    """
    Projects a coordinate c on the a tangential plane to the unit sphere
    that touches the plane in the tangent point t.
    :param array-like c: tangential coordinate to map
    :param astropy.SkyCoord t: spherical coordinate of tangent point
    :returns: spherical coordinates
    :rtype: astropy.SkyCoord
    """

    # calculate from tangential coordinates the corresponding
    # spherical coordinates.
    # for this, add the z-component to the 2D plane vector
    # and reconstruct spherical unit direction vector
    c_rot = np.copy(c)
    c_rot = np.concatenate((c_rot, np.zeros((c_rot.shape[0], 1))), axis=1)

    # distance to tangent point in the plane
    r = np.sqrt(c[:, 0] ** 2 + c[:, 1] ** 2)

    # angular distance of coordinate from tangent point on unit sphere
    # and polar angle
    theta = np.arctan(1 / r)
    phi = np.arctan(c[:, 0] / c[:, 1])

    # cartensian coordinates of direction vector on unit sphere
    c_rot[:, 0] = np.sign(c[:, 0]) * np.cos(theta) * np.sin(np.abs(phi))
    c_rot[:, 1] = np.sign(c[:, 1]) * np.cos(theta) * np.cos(phi)
    c_rot[:, 2] = np.abs(c_rot[:, 0] / c[:, 0])

    # rotate coordinate system such that tangent point is at the pole
    try:
        lat_angle = t.alt
    except:
        lat_angle = t.dec

    alpha = -(90 * u.deg - lat_angle)

    # convert tangent point to cartesian direction vector,
    # where z-coordinate points to the pole
    r = t.representation_type
    t.representation_type = "cartesian"
    t_vec = np.array([t.x, t.y, t.z])
    t.representation_type = r

    # find the direction vector around which to rotate the tangent
    # point to the pole. This is the vector perpendicular to the
    # plane made of the pole direction and the tangent point direction.
    pole_vec = np.array([0, 0, 1])
    rot_vec = np.cross(pole_vec, t_vec)

    # rotate all vectors away from the pole to their correct
    # position on the unit sphere
    c_rot = rotate_around_vector(c_rot, rot_vec, alpha)

    c_spherical = SkyCoord(
        x=c_rot[:, 0],
        y=c_rot[:, 1],
        z=c_rot[:, 2],
        representation_type="cartesian",
        frame=t.frame,
    )
    c_spherical.representation_type = t.representation_type

    return c_spherical


def sample_from_sphere_isotropic(n, seed=None):
    """
    Generates a sample of n coordinates sampled istropically
    from the sphere.
    """

    if seed is not None:
        np.random.seed(seed)

    lat = np.arcsin(np.random.rand(n) * 2 - 1)
    lon = np.random.rand(n) * 2 * np.pi

    return lon * u.rad, lat * u.rad
