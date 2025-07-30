from ctapointing.database import provide_image_db

# try to access the "images_magic" collection of the "images" database
with provide_image_db() as db:
    print(db)

    image_collection = db.images_magic
    print(image_collection)

    expression = {"exposure_duration": 10, "simulation": False}
    result = image_collection.find(expression).limit(10)

    for r in result:
        print(r["filename"], r["exposure_start"], r["exposure_duration"])

    print("total number of matches:", image_collection.count_documents(expression))
