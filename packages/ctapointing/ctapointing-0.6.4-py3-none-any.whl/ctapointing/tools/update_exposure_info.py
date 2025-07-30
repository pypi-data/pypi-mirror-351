"""
Update exposure info on database
"""

import argparse

from ctapointing.database import provide_image_db_write
from ctapointing.exposure import Exposure
from ctapointing.config import Config

Config.read_config("default")

parser = argparse.ArgumentParser(description="Update exposure information on database")
parser.add_argument("collection", type=str, help="image collection name")
parser.add_argument(
    "--write-to-db", action="store_true", help="write image info to database"
)

args = parser.parse_args()

with provide_image_db_write() as db:
    collection = db[args.collection]

    result = collection.find({})

for r in result:
    exposure = Exposure.from_name(r["uuid"], collection=args.collection)
    print(f"  processing {exposure.__repr__()}")

    if args.write_to_db:
        exposure.write_exposure(collection=args.collection, replace=True)
