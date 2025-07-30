import argparse

from ctapointing.database.mongodb import provide_image_db, provide_image_db_write

parser = argparse.ArgumentParser(
    description="Search for image duplicates in the database"
)

parser.add_argument("collection", type=str, help="image collection to search")
parser.add_argument(
    "--keyword",
    type=str,
    help="keyword that is used to identify documents as duplicates",
    default="uuid",
)
parser.add_argument(
    "--delete-from-db",
    action="store_true",
    help="delete duplicate documents from database",
)

args = parser.parse_args()

# data aggregation:
# (1) group all documents of the collection by keyword
# (2) count how many there are per keyword
# (3) select those for which there is more than one document
# (4) sort by descending number of duplicates
pipeline = [
    {
        "$group": {
            "_id": {"UUID": "$" + args.keyword},
            "uniqueIds": {"$addToSet": "$_id"},
            "count": {"$sum": 1},
        }
    },
    {"$match": {"count": {"$gt": 1}}},
    {"$sort": {"count": -1}},
]

with provide_image_db() as db:
    collection = db[args.collection]

    num_documents = collection.count_documents({})
    print(f"there are {num_documents} documents in the collection")

    result = collection.aggregate(pipeline)

duplicate_list = list(result)
to_delete = len(duplicate_list)
print(f"found {to_delete} duplicate images according to keyword '{args.keyword}'")

if to_delete > 0 and args.delete_from_db:
    print("removing duplicate images...")
    with provide_image_db_write() as db:
        collection = db[args.collection]

        for duplicate in duplicate_list:
            ids = duplicate["uniqueIds"]

            # remove all documents with matching id, except the first one
            for id in ids[1:]:
                collection.delete_one({"_id": id})
