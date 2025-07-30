"""
Remove images from the database.
"""

import argparse
import time

from ctapointing.database import provide_image_db_write

parser = argparse.ArgumentParser(description="Remove corrupt images from the database")

parser.add_argument("collection", type=str, help="name of collection in image database")

parser.add_argument(
    "--really-do-it", action="store_true", help="really ultimately remove from database"
)

args = parser.parse_args()


def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timeformat = "Are you really sure? {:02d}:{:02d}".format(mins, secs)
        print(timeformat, end="\r")
        time.sleep(1)
        t -= 1
    print("\n")


with provide_image_db_write() as db:
    collection = db[args.collection]
    selection = {"duration": None}

    result = collection.count_documents(selection)
    print(f"number of images affected: {result}")

    if result > 0:
        if args.really_do_it:
            countdown(10)
            result = collection.delete_many(selection)

            print(f"deleted {result.deleted_count} images.")
        else:
            print("to delete the images, set --really-do-it flag.")
