"""
Register a pointing image with the image database
"""

import logging
import argparse
from os.path import basename

from ctapointing.database import MongoDBTableWriter
from ctapointing.exposure import Exposure
from ctapointing.camera import ZWO_ASI2600_Camera

log = logging.getLogger()
log.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(levelname)s - %(asctime)s - %(funcName)s - %(message)s"
)
handler.setFormatter(formatter)
log.addHandler(handler)

parser = argparse.ArgumentParser(
    description="Register pointing image(s) with the image database"
)
parser.add_argument("image", type=str, nargs="*", help="image file name(s)")
parser.add_argument(
    "--camera-uuid", type=str, help="UUID of camera configuration", default=None
)
parser.add_argument(
    "--image-collection",
    type=str,
    help="name of collection in image database",
    default="test",
)
parser.add_argument(
    "--replace", action="store_true", help="replace image entry if already existing"
)
parser.add_argument(
    "--dry-run", action="store_true", help="do not write to database (for testing)"
)

args = parser.parse_args()

camera = ZWO_ASI2600_Camera.from_config(
    input_url="PointingCamera_ZWO.yaml", uuid=args.camera_uuid
)
if camera is None:
    error = f"could not find camera {args.camera_uuid} in database"
    raise RuntimeError(error)

logging.info(f"register_image_with_db: processing {len(args.image)} image(s).")

for i, filename in enumerate(args.image):
    print(f"  processing image {i}/{len(args.image)} ({filename})")

    exposure = Exposure.from_name(filename, read_meta_from_fits=True)
    exposure.image_filename = basename(filename)
    exposure.camera_uuid = camera.uuid
    exposure.camera = camera

    if not args.dry_run:
        with MongoDBTableWriter(database_name="images") as writer:
            writer.write(
                collection_name=args.image_collection,
                containers=exposure.to_container(),
                replace=args.replace,
            )
