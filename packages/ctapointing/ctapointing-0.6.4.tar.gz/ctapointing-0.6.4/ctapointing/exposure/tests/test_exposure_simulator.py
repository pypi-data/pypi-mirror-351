import pytest
import numpy as np

from astropy.coordinates import EarthLocation, SkyCoord
from astropy.time import Time
import astropy.units as u

from ctapointing.exposure import ExposureSimulator
from ctapointing.camera import ApogeeAspen8050Camera


def test_simulator_from_config():
    simulator = ExposureSimulator.from_config(
        input_url="ExposureSimulator_default.yaml"
    )
    assert simulator.name == "ExposureSimulator-default"


# @pytest.mark.parametrize("unsharp_radius", [0.0, 1.0] * u.arcsec)
# def test_exposure_simulator_pixel_index(unsharp_radius):
#     """
#     Test whether a simple star simulation works. In particular, test whether
#     the targeted star is imaged into the centre of the numpy image array.
#
#     For this, we simulate a very short exposure on Vega, with a chip of only
#     3x3 pixels.
#     """
#
#     simulator = ExposureSimulator()
#     simulator.apply_noise = False
#     simulator.moonlight = False
#     simulator.max_magnitude = 6.0
#     simulator.unsharp_radius = unsharp_radius
#
#     camera = ApogeeAspen8050Camera()
#     camera.num_pix = [3, 3]
#     camera.noise_mean = [0.0]
#     camera.noise_rms = [0.0]
#     camera.noise_pixel_fraction = [1.0]
#
#     start_time = Time("2021-02-22 03:00:00")
#     duration = 0.1 * u.s
#     tel_pointing = SkyCoord.from_name("Vega")
#
#     # switch off any smearing, noise, moonlight
#     exposure = simulator.process(
#         camera,
#         tel_pointing,
#         start_time,
#         duration,
#     )
#
#     mask = np.array([[True, True, True], [True, False, True], [True, True, True]])
#     assert np.allclose(exposure.image[mask], 0) and np.sum(exposure.image) > 0
#     assert exposure.mean_exposure_time == Time("2021-02-22 03:00:00") + 0.05 * u.s
