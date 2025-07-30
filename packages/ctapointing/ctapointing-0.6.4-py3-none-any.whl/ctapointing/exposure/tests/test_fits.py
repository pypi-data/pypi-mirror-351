import pathlib
import uuid

import astropy.units as u
from ctapointing.exposure import Exposure
from ctapointing.config import get_basedir


def test_read_fits_by_fullpath():
    """
    Test if a simple FITS file can be read, with full path provided.
    """
    filename = (
        "data/images/simulated/ZWO_2600/"
        "Polaris/ctapointing_simulation_0a0375d7-e6ba-45ed-b47d-09291ff2493d.fits.gz"
    )
    datapath = str(get_basedir() / filename)

    exposure = Exposure.from_name(datapath, read_meta_from_fits=True, load_camera=None)
    assert isinstance(exposure, Exposure)
    assert exposure.duration == 10 * u.s
    assert exposure.uuid == "0a0375d7-e6ba-45ed-b47d-09291ff2493d"


# def test_read_fits_by_uuid():
#     """
#     Test if a simple real FITS file can be read, with UUID provided.
#     """
#
#     os.environ["CTAPOINTING_DATA"] = os.path.join(Config.get_basedir(), "data/images")
#     _uuid = "0a0375d7-e6ba-45ed-b47d-09291ff2493d"
#     exposure = Exposure.from_name(_uuid, read_meta_from_fits=True, load_camera=None)
#     print(exposure)
#     assert (exposure.duration == 10 * u.s) and (exposure.uuid == uuid.UUID(_uuid))
#
#
# def test_read_fits_by_name():
#     """
#     Test if a simple real FITS file can be read, with just the name provided.
#     """
#
#     os.environ["CTAPOINTING_DATA"] = os.path.join(Config.get_basedir(), "data/images")
#     filename = "ctapointing_simulation_0a0375d7-e6ba-45ed-b47d-09291ff2493d.fits.gz"
#
#     exposure = Exposure.from_name(filename, read_meta_from_fits=True, load_camera=None)
#     print(exposure)
#     assert (exposure.duration == 10 * u.s) and (
#         exposure.uuid == uuid.UUID("0a0375d7-e6ba-45ed-b47d-09291ff2493d")
#     )
#

if __name__ == "__main__":
    test_read_fits_by_fullpath()
