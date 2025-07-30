import pytest

import numpy as np
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, AltAz, EarthLocation

from ctapipe.coordinates import TelescopeFrame
from ctapointing.coordinates import SkyCameraFrame, sciencecamera_frame


def test_altaz_projection():
    """
    Test if the conversion from AltAz to TelescopeFrame works when both the the AltAz coordinates
    and the TelescopeFrame telescope_pointing have different obstimes. Here, we check whether
    the telescope_pointing AltAz coordinate, when followed across the sky, always results in
    a TelescopeFrame coordinate (0,0).
    """

    location = EarthLocation.of_site("Roque de los Muchachos")

    start_time = Time("2018-07-14 04:28:00")
    duration = 1 * u.hour
    steps = 20

    # the source is observed at different times during time span "duration"
    obs_times = start_time + np.linspace(0, 1, steps) * duration

    # set up TelescopeFrame with AltAz pointings for the different obs_times
    tel_pointing = SkyCoord(ra="22h19m03.939s", dec="+58d49m38.440s", frame="icrs")
    altaz = AltAz(location=location, obstime=obs_times)
    tel_pointing_altaz = tel_pointing.transform_to(altaz)
    tel_frame = TelescopeFrame(
        telescope_pointing=tel_pointing_altaz, obstime=obs_times, location=location
    )

    # transform the RADec telescope pointing coordinate to the TelescopeFrame, using the
    # different obs_times

    tel_coords = tel_pointing.transform_to(tel_frame)

    fov_lat_close = np.allclose(tel_coords.fov_lat.to_value(u.deg), 0.0)
    fov_lon_close = np.allclose(tel_coords.fov_lon.to_value(u.deg), 0.0)

    assert fov_lat_close & fov_lon_close


@pytest.mark.parametrize("lon_offset", np.linspace(-90, 90, 10) * u.deg)
@pytest.mark.parametrize("lat_offset", np.linspace(-90, 90, 10) * u.deg)
def test_lon_lat_offset(lon_offset, lat_offset):
    """
    Tests whether the latitude and longitude values of coordinates in the
    TelescopeFrame match the angular distance in azimuth and altitude from the
    pointing position of the telescope in the AltAzFrame.
    This is only expected to be true for alt=0, so the test is over-simplistic.
    """

    tel_pointing_altaz = SkyCoord(az=0 * u.deg, alt=0 * u.deg, frame=AltAz)
    tel_frame = TelescopeFrame(telescope_pointing=tel_pointing_altaz)

    tel_coord = SkyCoord(fov_lon=lon_offset, fov_lat=lat_offset, frame=tel_frame)
    altaz_coord = tel_coord.transform_to(AltAz)

    lon_diff = tel_coord.fov_lat + tel_pointing_altaz.alt - altaz_coord.alt

    assert u.isclose(lon_diff, 0 * u.deg, atol=1e-3 * u.arcsec)


@pytest.mark.parametrize("rotation", np.linspace(-360, 360, 10) * u.deg)
@pytest.mark.parametrize("focal_length", np.logspace(-6, 2, 10) * u.m)
def test_projection_obspos(rotation, focal_length):
    """
    Test if observation position is properly transformed to (0,0) when
    different rotations and focal lengths are applied
    """

    tel_optical_axis = SkyCoord(
        fov_lon=0 * u.deg, fov_lat=0 * u.deg, frame=TelescopeFrame()
    )

    cam_frame = SkyCameraFrame(None)

    cam_coord = tel_optical_axis.transform_to(cam_frame)

    x_close = u.allclose(cam_coord.x, 0.0 * u.m)
    y_close = u.allclose(cam_coord.y, 0.0 * u.m)

    assert x_close & y_close


@pytest.mark.parametrize("offset_x", np.logspace(-6, 2, 5) * u.m)
@pytest.mark.parametrize("offset_y", np.logspace(-6, 2, 5) * u.m)
def test_offsets(offset_x, offset_y):
    """
    Test whether offsets work properly.
    """

    tel_optical_axis = SkyCoord(
        fov_lon=0 * u.deg, fov_lat=0 * u.deg, frame=TelescopeFrame()
    )

    cam_frame = SkyCameraFrame(offset_x=offset_x, offset_y=offset_y)
    cam_coord = tel_optical_axis.transform_to(cam_frame)

    x_close = u.allclose(cam_coord.x, offset_x)
    y_close = u.allclose(cam_coord.y, offset_y)

    assert x_close & y_close


@pytest.mark.parametrize("tilt_x", np.linspace(-80, 80, 5) * u.deg)
def test_latitude_reco(tilt_x):
    """
    Test whether camera tilts work properly.
    TODO: make work for 90 deg tilts
    """

    # test only for lon=0, since only then the altitude
    # is easily calculated
    lon = 0.0 * u.deg

    # test for various latitudes
    lat = np.linspace(-30, 30, 11) * u.deg
    tel_coords = SkyCoord(fov_lon=lon, fov_lat=lat, frame=TelescopeFrame)

    focal_length = 1 * u.m
    cam_frame = SkyCameraFrame(tilt_x=tilt_x, focal_length=focal_length)
    cam_coords = tel_coords.transform_to(cam_frame)

    # calculate expected coordinates in the SkyCameraFrame
    # using simple tangential projection
    exp_cam_x = np.tan(tel_coords.fov_lat - tilt_x) * focal_length
    exp_cam_y = np.tan(tel_coords.fov_lon) * focal_length

    # test proper latitude angle reconstruction
    x_close = u.allclose(cam_coords.x, exp_cam_x)
    y_close = u.allclose(cam_coords.y, exp_cam_y)

    assert x_close & y_close


@pytest.mark.parametrize("tilt_y", np.linspace(-80, 80, 5) * u.deg)
def test_latitude_reco(tilt_y):
    """
    Test whether camera tilts work properly.
    TODO: make work for 90 deg tilts
    """

    # test only for lat=0, since only then the altitude
    # is easily calculated
    lat = 0.0 * u.deg

    # test for various longitudes
    lon = np.linspace(-90, 90, 11) * u.deg
    tel_coords = SkyCoord(fov_lon=lon, fov_lat=lat, frame=TelescopeFrame)

    focal_length = 1 * u.m
    cam_frame = SkyCameraFrame(tilt_y=tilt_y, focal_length=focal_length)
    cam_coords = tel_coords.transform_to(cam_frame)

    # calculate expected coordinates in the SkyCameraFrame
    # using simple tangential projection
    exp_cam_x = np.tan(tel_coords.fov_lat) * focal_length
    exp_cam_y = np.tan(tel_coords.fov_lon - tilt_y) * focal_length

    print(exp_cam_x, exp_cam_y)
    print(cam_coords.x, cam_coords.y)

    # test proper longitude angle reconstruction
    x_close = u.allclose(cam_coords.x, exp_cam_x)
    y_close = u.allclose(cam_coords.y, exp_cam_y)

    assert x_close & y_close


@pytest.mark.parametrize("rotation", np.linspace(-360, 360, 10) * u.deg)
@pytest.mark.parametrize("tilt_x", np.linspace(-30, 30, 5) * u.deg)
@pytest.mark.parametrize("tilt_y", np.linspace(-30, 30, 5) * u.deg)
@pytest.mark.parametrize("focal_length", np.logspace(-6, 2, 5) * u.m)
def test_circular_transformation(rotation, tilt_x, tilt_y, focal_length):
    """
    Test transformation from SkyCameraFrame to TelescopeFrame and back.

    Returns
    -------
    None.

    """

    # define SkyCameraFrame
    cam = SkyCameraFrame(
        focal_length=focal_length, rotation=rotation, tilt_x=tilt_x, tilt_y=tilt_y
    )

    # define random positions in frame
    x = np.random.uniform(-10, 10, 10) * u.mm
    y = np.random.uniform(-10, 10, 10) * u.mm

    cam_coords = SkyCoord(x, y, frame=cam)

    # transform to telescope system and back
    tel_coords = cam_coords.transform_to(TelescopeFrame())
    cam_coords_repr = tel_coords.transform_to(cam)

    # test for numerical equality
    x_close = u.allclose(cam_coords.x, cam_coords_repr.x)
    y_close = u.allclose(cam_coords.y, cam_coords_repr.y)

    assert x_close & y_close


def test_sciencecamera_to_telescope():  # TODO tests are not verry usefull yet
    tel_optical_axis = SkyCoord(
        fov_lon=0 * u.deg, fov_lat=0 * u.deg, frame=TelescopeFrame()
    )
    cameraframe = sciencecamera_frame.ScienceCameraFrame()

    assert isinstance(
        sciencecamera_frame.telescope_to_sciencecamera(tel_optical_axis, cameraframe),
        sciencecamera_frame.ScienceCameraFrame,
    )


def test_telescope_to_sciencecamera():  # TODO tests are not verry usefull yet
    tel_optical_axis = SkyCoord(
        fov_lon=0 * u.deg, fov_lat=0 * u.deg, frame=TelescopeFrame()
    )
    cameraframe = sciencecamera_frame.ScienceCameraFrame()

    assert isinstance(
        sciencecamera_frame.telescope_to_sciencecamera(tel_optical_axis, cameraframe),
        sciencecamera_frame.ScienceCameraFrame,
    )
