import json
import os
import logging

from contextlib import contextmanager
from functools import partial

from pymongo import MongoClient

log = logging.getLogger(__name__)

_databases = [
    "images",
    "spots",
    "image_solutions",
    "camera_config",
    "solver_config",
    "ctapointing_config",
]


def check_collection_exists(database_name: str, collection_name: str) -> bool:
    """
    Check if collection `collection` exists in database `database`

    Parameters
    ----------
    database_name: str
        name of the database
    collection_name: str
        name of the collection

    Returns
    -------
    does_exist: Bool
        True if collection exists, False otherwise
    """
    provide_database = partial(provide_mongo_db, database=database_name)

    try:
        with provide_database() as db:
            return collection_name in db.list_collection_names()
    except KeyError as e:
        log.error(
            f"could not access database {database_name}/collection {collection_name}: {e}"
        )


@contextmanager
def provide_mongo_db(database, access_role="read"):
    """
    Provide a context for a certain mongodb database.

    Usage example:
    with provide_image_db() as db:
        [operate on db]
    """
    config = read_mongo_config()

    # return if config file could not be read
    if config is None:
        yield None

    host = config["host"]
    port = config["port"]

    user = config[database][access_role]["user"]
    password = config[database][access_role]["password"]

    with MongoClient(
        host, port, username=user, password=password, authSource=database
    ) as client:
        db = client.get_database(database)
        yield db


provide_image_db = partial(provide_mongo_db, database="images")

provide_image_db_write = partial(
    provide_mongo_db, database="images", access_role="readWrite"
)

provide_solutions_db = partial(provide_mongo_db, database="image_solutions")

provide_solutions_db_write = partial(
    provide_mongo_db, database="image_solutions", access_role="readWrite"
)

provide_camera_db = partial(provide_mongo_db, database="camera_config")

provide_camera_db_write = partial(
    provide_mongo_db, database="camera_config", access_role="readWrite"
)

provide_solver_db = partial(provide_mongo_db, database="solver_config")

provide_solver_db_write = partial(
    provide_mongo_db, database="solver_config", access_role="readWrite"
)

provide_config_db = partial(provide_mongo_db, database="ctapointing_config")

provide_config_db_write = partial(
    provide_mongo_db, database="ctapointing_config", access_role="readWrite"
)


def read_mongo_config(filename=None):
    """
    Read mongo configuration from file

    The mongo configuration file is a JSON document that contains information
    about the mongo connection (host and port) and the usernames, passwords and
    access roles for all databases.
    """

    if filename is None:
        filename = os.path.join(os.path.expanduser("~"), ".mongorc")

    try:
        with open(filename, "r") as infile:
            config = json.load(infile)
    except Exception as e:
        log.error(f"Problem in reading configuration from file {filename}: {e}")
        return None

    return config


def create_mongo_config(
    user, password, host, port, write_access=False, databases=None, filename=None
):
    """
    Create a mongo configuration in JSON format. Save to file upon request.
    """
    config_dict = {"host": host, "port": port}

    if databases is None:
        databases = _databases

    for db in databases:
        config_dict[db] = {"read": {"user": user, "password": password}}

        if write_access:
            config_dict[db]["readWrite"] = {
                "user": user + "_write",
                "password": password,
            }

    if filename is not None:
        try:
            with open(filename, "w") as outfile:
                json.dump(config_dict, outfile, indent=4)
        except Exception as e:
            print(f"problem in writing configuration to file {filename}: {e}")

    return config_dict


def create_mongo_account(config):
    """
    Create account in the mongo database.
    Username, password and access rights are set according
    to the information stored in the JSON-type
    config dictionary.
    """
    admin_config = read_mongo_config()

    try:
        host = admin_config["host"]
        port = admin_config["port"]
        admin_user = admin_config["admin"]["readWrite"]["user"]
        admin_password = admin_config["admin"]["readWrite"]["password"]
    except KeyError:
        print("Could not extract admin role from ~/.mongorc")
        return

    with MongoClient(
        host, port, username=admin_user, password=admin_password, authSource="admin"
    ) as client:
        databases = [
            key for key in config.keys() if key not in ("admin", "host", "port")
        ]
        for db_name in databases:
            db = client[db_name]
            for role in config[db_name]:
                user = config[db_name][role]["user"]
                password = config[db_name][role]["password"]

                print("database", db_name, ": creating user", user, "with role", role)
                try:
                    db.command("createUser", user, pwd=password, roles=[role])
                except Exception as e:
                    print(e)


def remove_mongo_account(username, really_remove=False):
    """
    Remove mongo user from the database.
    """
    if username == "admin":
        print("admin user cannot be removed.")
        return

    users = get_all_mongo_accounts()

    print("user", username, "has access to the following databases:")
    databases = []
    for user in users:
        if user["user"] == username:
            database = user["db"]
            print("\t", database)
            databases.append(database)

    admin_config = read_mongo_config()

    try:
        host = admin_config["host"]
        port = admin_config["port"]
        admin_user = admin_config["admin"]["readWrite"]["user"]
        admin_password = admin_config["admin"]["readWrite"]["password"]
    except KeyError:
        print(f"Could not extract admin role from ~/.mongorc")
        return

    with MongoClient(
        host, port, username=admin_user, password=admin_password, authSource="admin"
    ) as client:
        for database in databases:
            db = client[database]
            try:
                print("removing", username, "from database", database)
                if really_remove:
                    db.command("dropUser", username)
                else:
                    print("\t *not* removed yet (set really_remove=True to remove)")
            except Exception as e:
                print(e)


def get_all_mongo_accounts():
    admin_config = read_mongo_config()

    try:
        host = admin_config["host"]
        port = admin_config["port"]
        admin_user = admin_config["admin"]["readWrite"]["user"]
        admin_password = admin_config["admin"]["readWrite"]["password"]
    except KeyError:
        print(f"Could not extract admin role from ~/.mongorc")
        return

    users = []
    with MongoClient(
        host, port, username=admin_user, password=admin_password, authSource="admin"
    ) as client:
        db = client["admin"]
        try:
            users = db.command("usersInfo", {"forAllDBs": True})["users"]
        except Exception as e:
            print(e)

    return users
