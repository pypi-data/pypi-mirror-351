import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u

from ctapointing.imagesolver import SpotExtractorSky
from ctapointing.camera import PointingCamera
from ctapointing.exposure import Exposure
from ctapointing.coordinates import SkyCameraFrame


def test_spotextractor():
    camera = PointingCamera.from_config(input_url="PointingCamera_ZWO.yaml")

    # make sure we have an odd number of pixels, such that
    # the centre of the camera system is at the centre of
    # the central pixel.
    camera.num_pix = [3001, 5001]

    exposure = Exposure()
    exposure.camera = camera
    exposure.create_empty_image()

    # find
    coord = SkyCoord(0.0 * u.m, 0.0 * u.m, frame=SkyCameraFrame)
    coord_pix = exposure.transform_to_camera(coord, to_pixels=True)
    index, _ = exposure.get_array_indexes(coord_pix)
    index_x = int(index[0][0])
    index_y = int(index[0][1])

    # create a symmetric 3x3 pixel "blob" centred at the central pixel
    exposure.image[index_x - 1 : index_x + 2, index_y - 1 : index_y + 2] = 1000
    exposure.image[index_x, index_y] = 2000

    extractor = SpotExtractorSky.from_config(input_url="SpotExtractor_default.yaml")
    extractor.kernel_size = 10

    # extract spot and compare to expected position
    spotlist = extractor.process(exposure)
    assert np.allclose(coord_pix, spotlist.coords_pix)
