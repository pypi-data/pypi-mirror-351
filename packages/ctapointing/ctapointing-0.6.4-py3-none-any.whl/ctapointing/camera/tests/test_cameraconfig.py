import pytest
from ctapointing.camera import PointingCamera


def test_from_config():
    """
    Test whether camera configuration can be read from default config file.
    """
    camera = PointingCamera.from_config(input_url="PointingCamera_ZWO.yaml")
    assert isinstance(camera, PointingCamera)


def test_from_nonexisting():
    """
    Test whether FileNotFoundError exception is correctly raised
    in case we try to read from non-existent file
    """
    with pytest.raises(FileNotFoundError) as e:
        camera = PointingCamera.from_config(input_url="unknown_name")
    assert str(e.value) == "config file does not exist."
