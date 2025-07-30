from pathlib import Path
import inspect

import pytest

from ctapointing.config import get_basedir, from_config

TEST_CONFIGURATION = "SkyFitter_default.yaml"


def test_get_basedir():
    import ctapointing as c

    assert get_basedir() == Path(inspect.getfile(c)).parent


def test_from_config():
    # test for existence of arguments
    with pytest.raises(KeyError):
        from_config()

    # file not found
    with pytest.raises(FileNotFoundError):
        from_config(input_url="non_existing_config")

    # test for mutual exclusion of arguments
    with pytest.raises(KeyError):
        from_config(component_name="test", collection="test", database="test")

    # test for valid configuration/name
    with pytest.raises(ValueError):
        from_config(input_url=TEST_CONFIGURATION, component_name="NoComponent")

    with pytest.raises(ValueError):
        from_config(
            input_url=TEST_CONFIGURATION, component_name="SkyFitter", name="NoName"
        )
