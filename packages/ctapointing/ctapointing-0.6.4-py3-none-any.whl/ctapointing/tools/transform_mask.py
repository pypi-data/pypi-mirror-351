"""
Recompute pixel exclusion map for a different camera type/orientation
"""

import argparse
import logging

import numpy as np

from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.io import fits

from ctapointing.exposure import Exposure
from ctapointing.camera import PointingCamera

log = logging.getLogger()
log.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

log.addHandler(handler)

parser = argparse.ArgumentParser(
    description="Recompute pixel exclusion map for different camera type/orientation"
)
parser.add_argument(
    "-src-config",
    type=str,
    help="original camera configuration (default %(default)s)",
    default="ApogeeAspen8050-standard",
)
parser.add_argument(
    "-dst-config",
    type=str,
    help="destination camera configuration (default %(default)s)",
    default="ApogeeAspen8050-standard",
)
parser.add_argument("-src-mask-file", type=str, help="path to original mask FITS file")
parser.add_argument(
    "-dst-mask-file", type=str, help="path to destination mask FITS file"
)

args = parser.parse_args()

# load camera configurations
camera_src = PointingCamera.from_name(args.src_config)
camera_dst = PointingCamera.from_name(args.dst_config)

# construct source exposure object and
# read in mask image
exposure_src = Exposure()
exposure_src.read_from_fits(args.src_mask_file)
exposure_src.camera = camera_src

# for projection into destination camera, a transformation to an (arbitrary)
# altaz frame is needed
exposure_src.telescope_pointing = SkyCoord(0.0 * u.deg, 30.0 * u.deg, frame="altaz")

# construct destination exposure object
exposure_dst = Exposure()
exposure_dst.camera = camera_dst
exposure_dst.image = np.ones(camera_dst.num_pix, dtype=np.uint8) * 255
exposure_dst.telescope_pointing = exposure_src.telescope_pointing

# construct list of all pixel coordinates in destination image
pix_x = np.linspace(0, camera_dst.num_pix[0], camera_dst.num_pix[0], endpoint=False)
pix_y = np.linspace(0, camera_dst.num_pix[1], camera_dst.num_pix[1], endpoint=False)

xx = np.repeat(pix_x, len(pix_y))
yy = np.tile(pix_y, len(pix_x))
pix_dst_coords = np.append(xx.reshape((-1, 1)), yy.reshape(-1, 1), axis=1)

# transform destination image pixel position to source image via altaz system
camera_dst_coords = camera_dst.transform_to_camera(pix_dst_coords)
altaz_coords = exposure_dst.project_from(camera_dst_coords, obstime=None)

camera_src_coords = exposure_src.project_into(altaz_coords)
pix_src_coords = camera_src.transform_to_pixels(camera_src_coords)

# read out the intensities at the coordinates of the source image
# which represent pixels of the destination image
mask_src_intensities = exposure_src.get_intensity(pix_src_coords)

# for coordinates that are outside of the source image, intensities
# are set to np.nan by default. Set them to 255, meaning that
# in the final mask these regions correspond to visible sky
mask_src_intensities[np.isnan(mask_src_intensities)] = 255

exposure_dst.set_intensity(pix_dst_coords, mask_src_intensities)

# write image to simple FITS file
hdu = fits.PrimaryHDU(exposure_dst.image, None)

hdu_list = fits.HDUList([hdu])
hdu_list.writeto(args.dst_mask_file, overwrite=True)
