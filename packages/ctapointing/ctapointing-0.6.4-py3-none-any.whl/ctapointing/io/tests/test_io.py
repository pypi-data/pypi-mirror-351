import numpy as np
import pytest
import astropy.units as u

from ctapipe.io import HDF5TableWriter
from ctapointing.io import SpotListSource, ImageSolutionSource, from_name
from ctapointing.imagesolver import ImageSolution, SpotList
from ctapointing.imagesolver.tests.test_spotlist import create_spotlist


def test_spotlistsource():
    GROUPNAME = "spots"

    # create temporary spotlist file
    s = create_spotlist(num_spots=20)
    with HDF5TableWriter(
        filename="test_write_spotlist.h5",
        group_name=GROUPNAME,
    ) as writer:
        writer.write("spotlist", s)

    # read back file and test source iterator
    with SpotListSource(input_url="test_write_spotlist.h5") as source:
        for spotlist in source:
            assert spotlist.uuid == s.uuid
            assert np.allclose(spotlist.coord_x, s.coord_x)
            assert np.allclose(spotlist.coord_y, s.coord_y)

    # test from_url() class method
    with SpotListSource.from_url("test_write_spotlist.h5") as source:
        assert len(source) == 1

    with pytest.raises(FileNotFoundError):
        SpotListSource.from_url("no_spotlist.h5")


def create_imagesolution():
    i = ImageSolution()

    i.telescope_pointing_ra = 20 * u.deg
    i.telescope_pointing_dec = 30 * u.deg

    return i


def test_imagesolutionsource():
    GROUPNAME = "image_solutions"

    # create temporary spotlist file
    i = create_imagesolution()
    with HDF5TableWriter(
        filename="test_write_imagesolution.h5",
        group_name=GROUPNAME,
    ) as writer:
        writer.write("imagesolution", i)

    # read back file and test source iterator
    with ImageSolutionSource(input_url="test_write_imagesolution.h5") as source:
        for solution in source:
            assert solution.uuid == i.uuid
            assert u.isclose(solution.telescope_pointing_ra, i.telescope_pointing_ra)
            assert u.isclose(solution.telescope_pointing_dec, i.telescope_pointing_dec)

    # test from_url() class method
    with ImageSolutionSource.from_url("test_write_imagesolution.h5") as source:
        assert len(source) == 1

    with pytest.raises(FileNotFoundError):
        SpotListSource.from_url("no_imagesolution.h5")


def test_from_name():
    # read in SpotList object, check length
    spotlist = from_name(
        "test_write_spotlist.h5", SpotList, table_name="/spots/spotlist"
    )
    assert len(spotlist) == 20

    # test for missing arguments
    with pytest.raises(AttributeError):
        from_name("test_write_spotlist.h5", SpotList)

    with pytest.raises(TypeError):
        from_name("test_write_spotlist.h5", float)
