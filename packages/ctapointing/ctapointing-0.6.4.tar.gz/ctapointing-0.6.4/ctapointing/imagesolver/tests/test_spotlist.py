import numpy as np
from ctapipe.io import HDF5TableWriter, HDF5TableReader

from ctapointing.imagesolver import SpotList


def create_spotlist(num_spots):
    spotlist = SpotList()
    spotlist.coord_x = np.random.rand(num_spots)
    spotlist.coord_y = np.random.rand(num_spots)

    return spotlist


def test_create_spotlist(num_spots=20):
    spotlist = create_spotlist(num_spots)
    assert spotlist.uuid is not None


def test_len_spotlist(num_spots=20):
    spotlist = create_spotlist(num_spots)
    assert len(spotlist) == num_spots


def test_read_write_spotlist_to_file(num_spots=20):
    spotlist = create_spotlist(num_spots)

    with HDF5TableWriter("test_write_spotlist.h5") as writer:
        writer.write("spots", spotlist)

    with HDF5TableReader("test_write_spotlist.h5") as reader:
        spotlist_read = next(reader.read("/spots", SpotList))

    assert spotlist.uuid == spotlist_read.uuid
    assert np.allclose(spotlist.coord_x - spotlist_read.coord_x, 0.0)
    assert np.allclose(spotlist.coord_y - spotlist_read.coord_y, 0.0)


def test_from_name(num_spots=20):
    spotlist = create_spotlist(num_spots)

    with HDF5TableWriter("test_write_spotlist.h5") as writer:
        writer.write("spots", spotlist)

    spotlist_read = SpotList.from_name("test_write_spotlist.h5", table_name="/spots")

    assert spotlist.uuid == spotlist_read.uuid
    assert np.allclose(spotlist.coord_x - spotlist_read.coord_x, 0.0)
    assert np.allclose(spotlist.coord_y - spotlist_read.coord_y, 0.0)
