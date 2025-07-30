"""
Functions to read and write configurations to file and database
"""

import logging
import json
import re
from os import path, environ, walk
import uuid
from functools import partial

from .mongodb import provide_mongo_db

log = logging.getLogger(__name__)


def read_configuration(name, database, collection_name, read_from_file):
    """
    Read a configuration from either database or file.

    Parameters
    ----------
    name: str
        name of the configuration (or filename)
    database: str
        name of the database to read from
    read_from_file: bool
        read from database if False, from file if True
    collection_name: str
        mongo database collection to read from

    Returns
    -------
    configuration: dict
        (nested) dictionary of configuration parameters
        or None in case of unsuccessful reading
    """

    if isinstance(name, uuid.UUID):
        name = str(name)

    # read from file
    if read_from_file is True:
        fullname = None

        # full path name used?
        if path.isfile(name):
            fullname = name
        else:
            search_dirs = ["."]
            ctapointing_data_path = environ.get("CTAPOINTING_DATA")
            if ctapointing_data_path is not None:
                search_dirs.append(ctapointing_data_path)
            for d in search_dirs:
                for root, _, files in walk(d):
                    for filename in files:
                        name_string = r"^" + name + r".*json"
                        name_match = re.search(name_string, filename)
                        fullname_string = r"^" + name
                        fullname_match = re.search(fullname_string, filename)
                        uuid_string = r".*" + name + r"*.json"
                        uuid_match = re.search(uuid_string, filename)
                        if name_match or fullname_match or uuid_match:
                            fullname = path.join(root, filename)
                            break

        if fullname is None:
            return None

        try:
            with open(fullname, "r") as infile:
                result = json.load(infile)
        except (FileNotFoundError, ValueError):
            log.error("unable to read configuration from file {fullname}")
            return None

        return result

    # read from database
    provide_database = partial(provide_mongo_db, database=database, access_role="read")

    try:
        with provide_database() as db:
            db_collection = db[collection_name]
            result = db_collection.find({"$or": [{"name": name}, {"uuid": name}]})[0]
    except IndexError:
        log.warning(f"unable to read {name} from collection {collection_name}.")
        return None

    return result


def write_configuration(
    data, database, collection_name, replace=False, write_to_file=False, filepath=None
):
    """
    Write a configuration to either database or file.

    Parameters
    ----------
    data: dict
        (nested) dictionary of data to write
    database: str
        name of the database to write to
    replace: bool
        if True, replace file or database entry
    write_to_file: bool
        write to database if False, to file if True
    collection_name: str
        mongo database collection to write to
    filepath: str or None
        directory to which file gets written

    Returns
    -------
    result: path to output file or database storage result
    """

    # write to file
    if write_to_file is True:
        filename = f"{data['name']}_{data['uuid']}.json"
        pathname = environ.get("CTAPOINTING_DATA")

        if filepath is not None and path.isdir(filepath):
            filename = path.join(filepath, filename)
        elif pathname is not None and path.isdir(pathname):
            filename = path.join(pathname, filename)

        if path.exists(filename) and not replace:
            raise FileExistsError

        with open(filename, "w") as outfile:
            json.dump(data, outfile, indent=4)

        return path.abspath(filename)

    # write to database
    provide_database = partial(
        provide_mongo_db, database=database, access_role="readWrite"
    )

    with provide_database() as db:
        db_collection = db[collection_name]

        uuid = data["uuid"]
        name = data["name"]

        # UUID already existing in database?
        is_in_db = db_collection.count_documents({"uuid": uuid}) > 0

        if is_in_db and replace:
            result = db_collection.replace_one({"uuid": uuid}, data, upsert=True)
        elif not is_in_db:
            result = db_collection.insert_one(data)
        else:
            log.warning(
                f"Not writing camera config {name} to database because entry with UUID {uuid} already exists"
            )
            return None

    return result


def get_known_configurations(database, collection_name):
    """
    Lists all available database entries in this database

    Returns
    -------
    config_names: list
        list of tuples with name and UUID of configurations
    """

    provide_database = partial(provide_mongo_db, database=database, access_role="read")

    config_names = []
    with provide_database() as db:
        db_collection = db[collection_name]

        try:
            results = db_collection.find({})

        except Exception as e:
            log.error(f"could not read collection {db_collection}: {e}")
            return []

        for result in results:
            config_names.append([result["name"], result["uuid"]])

    return config_names
