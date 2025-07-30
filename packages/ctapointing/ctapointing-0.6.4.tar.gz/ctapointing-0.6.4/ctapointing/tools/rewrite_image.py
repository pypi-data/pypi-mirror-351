import logging
import os
import sys
import uuid
import argparse
import numpy as np
from astropy.io import fits

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("rewrite_image")

parser = argparse.ArgumentParser(
    description="Rewrite old FITS images to standard format"
)
parser.add_argument(
    "file", type=str, nargs="*", help="file name(s) or file(s) containing list of files"
)

parser.add_argument(
    "--flip-image",
    action="store_true",
    help="flip image at vertical axis (for MAGIC-campaign real images)",
)
parser.add_argument(
    "--overwrite",
    action="store_true",
    help="overwrite in case output file already existing",
)
parser.add_argument("--uuid", action="store_true", help="add uuid4 to FITS header")

args = parser.parse_args()

filelist = []
for filename in args.file:
    try:
        # test for file containing list of files
        with open(filename, "r") as listfile:
            files = listfile.read()
            filelist.extend(str.splitlines(files))
    except:
        # else: should be an image file
        filelist.append(filename)

n_images = len(filelist)
if n_images == 0:
    log.info("no image to process.")
    sys.exit()
else:
    log.info(f"processing {n_images} image(s).")

for idx, filename in enumerate(filelist):
    if not os.path.exists(filename):
        log.error(f"Cannot open file {filename}.")
        continue

    # create new filename by splitting off the (possibly double) extension
    basename = os.path.basename(filename)

    r = basename.rfind(".fits.gz")
    if r > 0:
        name = basename[:r]
        ext = basename[r + 1 :]
    else:
        name, ext = basename.rsplit(".", 1)

    filename_new = name + "_with_uuid." + ext
    if os.path.exists(filename_new) and not args.overwrite:
        log.error(f"not writing {filename_new}: file exists already.")
        continue

    # open input file, add UUID, and flip
    hdu_list = fits.open(filename)

    data = hdu_list[0].data
    header = hdu_list[0].header

    if args.uuid:
        header["UUID"] = str(uuid.uuid4())
        header.comments["UUID"] = "auto-generated UUID4"

    if args.flip_image:
        data = np.flip(data, axis=1)

    hdu = fits.PrimaryHDU(data, header)
    hdu_list = fits.HDUList([hdu])

    try:
        hdu_list.writeto(filename_new, overwrite=args.overwrite)
    except Exception as e:
        log.error(f"Could not write file {filename_new}: {e}")
