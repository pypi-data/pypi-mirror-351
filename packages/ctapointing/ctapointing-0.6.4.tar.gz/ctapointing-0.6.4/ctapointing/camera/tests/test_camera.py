import pytest

import numpy as np

from astropy.coordinates import AltAz, SkyCoord
from astropy.time import Time
import astropy.units as u

from ctapointing.camera import PointingCamera, ApogeeAspen8050Camera, ZWO_ASI2600_Camera
from ctapointing.coordinates import SkyCameraFrame


@pytest.mark.parametrize("pixel_size", np.logspace(0, 2, 10) * u.micron)
@pytest.mark.parametrize("num_pix_x", np.arange(0, 5000, step=333))
@pytest.mark.parametrize("num_pix_y", np.arange(0, 5000, step=333))
def test_chip_size(pixel_size, num_pix_x, num_pix_y):
    camera = PointingCamera()
    camera.num_pix = [num_pix_x, num_pix_y]
    camera.pixel_size = pixel_size

    chip_size = np.array([num_pix_x, num_pix_y]) * pixel_size
    assert u.allclose(camera.chip_size, chip_size)


@pytest.mark.parametrize("pixel_size", np.logspace(0, 2, 10) * u.micron)
@pytest.mark.parametrize("num_pix_x", np.arange(0, 5000, step=333))
@pytest.mark.parametrize("num_pix_y", np.arange(0, 5000, step=333))
def test_chip_area(pixel_size, num_pix_x, num_pix_y):
    camera = PointingCamera()
    camera.num_pix = [num_pix_x, num_pix_y]
    camera.pixel_size = pixel_size

    chip_size = np.array([num_pix_x, num_pix_y]) * pixel_size
    assert u.allclose(camera.chip_area, chip_size[0] * chip_size[1])


@pytest.mark.parametrize("num_pix_x", np.arange(0, 5000, step=333))
@pytest.mark.parametrize("num_pix_y", np.arange(0, 5000, step=333))
def test_chip_centre(num_pix_x, num_pix_y):
    camera = PointingCamera()
    camera.num_pix = [num_pix_x, num_pix_y]

    centre_x, centre_y = camera.chip_centre

    assert np.isclose(2 * centre_x + 1, num_pix_x) & np.isclose(
        2 * centre_y + 1, num_pix_y
    )


@pytest.mark.parametrize("num_pix_x", np.arange(0, 5000, step=333))
@pytest.mark.parametrize("num_pix_y", np.arange(0, 5000, step=333))
@pytest.mark.parametrize("pixel_size", np.logspace(0, 2, 10) * u.micron)
def test_fov(pixel_size, num_pix_x, num_pix_y):
    camera = PointingCamera()
    camera.num_pix = [num_pix_x, num_pix_y]
    camera.pixel_size = pixel_size
    camera.focal_length = u.Quantity([50.0, 50.0], u.mm)

    assert u.allclose(camera.fov, np.arctan(camera.chip_size / camera.focal_length))


def test_project_into():
    """
    Test whether a simple projection from TelescopeFrame to SkyCameraFrame works
    """
    camera = PointingCamera.from_config(input_url="PointingCamera_ZWO.yaml")

    az, alt = 20 * u.deg, 40 * u.deg

    obstime = Time("2018-07-14 04:28:00")
    telescope_pointing = SkyCoord(az=az, alt=alt, obstime=obstime, frame=AltAz)

    coord = SkyCoord(az, alt, obstime=obstime, frame=AltAz)
    result = camera.project_into(coord, telescope_pointing)

    assert np.isclose(result.x, 0) & np.isclose(result.y, 0)


@pytest.mark.parametrize("coord_x", np.linspace(-1e-3, 1e3, 5) * u.m)
@pytest.mark.parametrize("coord_y", np.linspace(-1e-3, 1e3, 5) * u.m)
@pytest.mark.parametrize("tilt_x", np.linspace(-10, 10, 3) * u.deg)
@pytest.mark.parametrize("tilt_y", np.linspace(-10, 10, 3) * u.deg)
@pytest.mark.parametrize("rotation", np.linspace(-360, 360, 5) * u.deg)
def test_project_from(coord_x, coord_y, tilt_x, tilt_y, rotation):
    """
    Test whether the inverse transform works.
    """

    camera = PointingCamera.from_config(input_url="PointingCamera_ZWO.yaml")
    camera.tilt[0] = tilt_x
    camera.tilt[1] = tilt_y
    camera.rotation = rotation

    obstime = Time("2018-07-14 04:28:00")
    telescope_pointing = SkyCoord(
        az=20 * u.deg, alt=40 * u.deg, obstime=obstime, frame=AltAz
    )

    skyframe = SkyCameraFrame(
        focal_length=camera.focal_length[0],
        rotation=camera.rotation,
        tilt_x=camera.tilt[0],
        tilt_y=camera.tilt[1],
        telescope_pointing=telescope_pointing,
    )

    coord = SkyCoord(coord_x, coord_y, frame=skyframe)
    altaz_coord = camera.project_from(coord, obstime, telescope_pointing)
    coord_new = camera.project_into(altaz_coord, telescope_pointing)

    assert u.isclose(coord_new.x, coord.x) & u.isclose(coord_new.y, coord.y)


def test_transform_to_pixels():
    camera = PointingCamera.from_config(input_url="PointingCamera_ZWO.yaml")

    coord = SkyCoord(0.0 * u.m, 0.0 * u.m, frame=SkyCameraFrame)

    camera.num_pix = [3, 3]
    pix_coord = camera.transform_to_pixels(coord)

    assert np.allclose(pix_coord, 1)

    camera.num_pix = [4, 4]
    pix_coord = camera.transform_to_pixels(coord)

    assert np.allclose(pix_coord, 1.5)


def test_transform_to_camera():
    camera = PointingCamera.from_config(input_url="PointingCamera_ZWO.yaml")
    camera.num_pix = [3, 3]

    pix_coord = [1, 1]
    camera_coord = camera.transform_to_camera(pix_coord)

    assert u.isclose(camera_coord.x, 0.0 * u.m) & u.isclose(camera_coord.y, 0.0 * u.m)

    camera.num_pix = [4, 4]
    pix_coord = [1.5, 1.5]
    camera_coord = camera.transform_to_camera(pix_coord)

    assert u.isclose(camera_coord.x, 0.0 * u.m) & u.isclose(camera_coord.y, 0.0 * u.m)


def test_clip_to_chip():
    n = 10000

    camera = PointingCamera.from_config(input_url="PointingCamera_ZWO.yaml")
    nx, ny = camera.num_pix

    # coordinates within chip boundaries are
    # in the interval [-0.5, n_pix-0.5)
    pix_coords = np.random.rand(n, 2)
    pix_coords[:, 0] *= nx - 0.5
    pix_coords[:, 1] *= ny - 0.5

    assert np.all(camera.clip_to_chip(pix_coords))

    # coordinates outside chip boundaries
    pix_coords = np.random.rand(n, 2)
    pix_coords[:, 0] *= 2 * nx
    pix_coords[:, 1] *= 2 * ny

    pix_coords[:, 0] -= nx
    pix_coords[:, 1] -= ny

    # mark all coordinates within chip
    # this works, as tested above
    mask_inside = camera.clip_to_chip(pix_coords)

    # now test whether all remaining coordinates
    # are assigned to be outside of chip
    assert np.all(~camera.clip_to_chip(pix_coords[~mask_inside]))


def test_ApogeeAspen8050Camera():
    camera = ApogeeAspen8050Camera()
    assert np.allclose(
        camera.chip_size, u.Quantity(np.array([2472, 3296]) * 5.4 * u.micron)
    )


def test_ZWO_ASI2600_Camera():
    camera = ZWO_ASI2600_Camera()
    assert np.allclose(
        camera.chip_size, u.Quantity(np.array([4176, 6248]) * 3.76 * u.micron)
    )
