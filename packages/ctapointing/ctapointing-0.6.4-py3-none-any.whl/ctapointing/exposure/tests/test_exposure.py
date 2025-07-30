import pytest
import numpy as np

from astropy.time import Time
import astropy.units as u
from astropy.coordinates import SkyCoord

from ctapointing.coordinates import SkyCameraFrame
from ctapointing.config import get_basedir
from ctapointing.camera import PointingCamera
from ctapointing.exposure import Exposure


def test_exposure():

    # read sample exposure from fits file
    exposure = Exposure.from_name(
        "ctapointing_simulation_0a0375d7-e6ba-45ed-b47d-09291ff2493d.fits.gz",
        load_camera=False,
        read_meta_from_fits=True,
        image_path=get_basedir() / "data" / "images" / "simulated",
    )

    assert exposure is not None
    assert exposure.start_time == Time("2023-01-01T00:00:00.000")
    assert exposure.duration == 10.0 * u.s

    # invent some mock metadata
    camera = PointingCamera.from_config(input_url="PointingCamera_ZWO.yaml")
    exposure.camera = camera
    exposure.camera_uuid = camera.uuid
    exposure.camera_humidity = 0.6
    exposure.camera_temperature = 20 * u.deg_C
    exposure.chip_temperature = 2 * u.deg_C
    exposure.ambient_temperature = 30 * u.deg_C

    # write exposure to container, read back and check for consistency
    container = exposure.to_container()

    assert Exposure.from_container("some random string") is None
    assert Exposure.from_container(2796835.973465) is None

    exposure2 = Exposure.from_container(container=container)
    exposure2.camera = PointingCamera.from_config(input_url="PointingCamera_ZWO.yaml")

    assert exposure2.mean_exposure_time == exposure.mean_exposure_time
    assert exposure2.ambient_pressure == exposure.ambient_pressure
    assert exposure2.ambient_temperature == exposure.ambient_temperature
    assert exposure2.camera_temperature == exposure.camera_temperature
    assert exposure2.camera_humidity == exposure.camera_humidity
    assert exposure2.chip_temperature == exposure.chip_temperature
    assert exposure2.camera_uuid == exposure.camera_uuid
    assert exposure2.duration == exposure.duration
    assert exposure2.image_filename == exposure.image_filename
    assert exposure2.is_simulated == exposure.is_simulated
    assert exposure2.moon_phase == exposure.moon_phase
    assert exposure2.start_time == exposure.start_time
    assert exposure2.uuid == exposure.uuid

    # test if FITS writing works
    exposure.write_to_fits("test.fits.gz", force_overwrite=True)

    exposure2 = Exposure()
    assert exposure2.read_from_fits() is False

    exposure2.read_from_fits("test.fits.gz", read_meta_from_fits=True)
    assert exposure2.camera_uuid == exposure.camera_uuid
    assert exposure2.start_time == exposure.start_time
    assert exposure2.chip_temperature == exposure.chip_temperature
    assert exposure2.camera_temperature == exposure.camera_temperature
    assert exposure2.camera_humidity == exposure.camera_humidity
    assert exposure2.is_simulated == exposure.is_simulated
    assert exposure2.nominal_telescope_pointing == exposure.nominal_telescope_pointing


def test_image_array():
    num_pix_x = 1001
    num_pix_y = 501

    expected_index_x = (num_pix_x - 1) / 2
    expected_index_y = (num_pix_y - 1) / 2

    exposure = Exposure()

    # test creation of empty image without proper camera info
    with pytest.raises(AttributeError):
        exposure.create_empty_image()

    camera = PointingCamera.from_config(input_url="PointingCamera_ZWO.yaml")
    camera.num_pix = [num_pix_x, num_pix_y]

    # now assign camera and try again
    exposure.camera = camera
    exposure.create_empty_image()
    assert exposure.image.shape == tuple(camera.num_pix)

    # check that chip centre is exactly at expected indexes
    coord = SkyCoord(0.0 * u.m, 0.0 * u.m, frame=SkyCameraFrame)
    coords_pix = exposure.transform_to_camera(coord, to_pixels=True)

    pix_indexes, _ = exposure.get_array_indexes(coords_pix)
    assert pix_indexes[0, 0] == expected_index_x
    assert pix_indexes[0, 1] == expected_index_y

    # check that setting and getting intensities works
    exposure.set_intensity(coords_pix, 255)
    assert exposure.get_intensity(coords_pix)[0] == 255
