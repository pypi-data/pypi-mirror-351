import argparse
import os.path
import json
import logging

from ctapointing.exposure.exposure_container import ExposureContainer
from ctapointing.database import MongoDBTableReader

log = logging.getLogger()
log.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

log.addHandler(handler)

parser = argparse.ArgumentParser(description="Select images from database")
parser.add_argument(
    "-image-collection",
    type=str,
    help="database collection",
)
parser.add_argument(
    "--image-database",
    type=str,
    help="image database",
    default="images",
)
parser.add_argument(
    "--selection",
    type=str,
    help="optional MONGO selection string (default: %(default)s)",
    default="{}",
)
parser.add_argument(
    "--max-entries",
    type=int,
    help="maximum number of entries to return (0: all)",
    default=0,
)

args = parser.parse_args()
selection = json.loads(args.selection)

with MongoDBTableReader(args.image_database) as reader:
    for container in reader.read(
        args.image_collection,
        containers=ExposureContainer,
        selection_dict=selection,
        limit=args.max_entries,
    ):
        print(f"{container.image_filename}\t{container.uuid}")
