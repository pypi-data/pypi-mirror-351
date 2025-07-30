import logging
from pathlib import Path
import json
import yaml
import inspect
from functools import partial

import traitlets.config as tc

from ctapointing.database import (
    provide_mongo_db,
)

log = logging.getLogger(__name__)


def get_basedir() -> Path:
    """
    Return path of the ctapointing installation directory
    """
    import ctapointing as c

    return Path(inspect.getfile(c)).parent


def from_config(**kwargs) -> tc.Config:
    """
    Read a configuration from either configuration file or database.
    Either the path of a configuration file ('input_url') or a database collection
    ('collection') must be provided.

    Parameters
    ----------
    component_name: str or None
        name of the ctapointing.Component which the configuration will be applied to.
        Used to build the outer dictionary of the configuration.
    input_url: str or Path
        path of the configuration file.
    name: str
        name of the configuration (as e.g. in `PointingCamera.name`).
        When loading the configuration from file, can be set to check that the configuration with the
        correct name is loaded.
        When loading from database, is used to identify the correct database record.
    uuid: str
        UUID of the configuration (as in `PointingCamera.uuid`).
        When loading the configuration from file, can be set to check that the configuration with the
        correct UUID is loaded.
        When loading from database, is used to identify the correct database record.
    collection: str
        name of the database collection from which configuration is read
    database: str
        name of the database in which the collection is stored

    Returns
    -------
    config: traitlets.config.Config
        Configuration object
    """
    component_name = kwargs.get("component_name", None)
    input_url = kwargs.get("input_url", None)
    collection = kwargs.get("collection", None)
    database = kwargs.get("database", None)

    if input_url is not None and (collection is not None or database is not None):
        raise KeyError(
            "The arguments 'input_url' and ['collection', 'database'] are mutually exclusive."
        )

    name = kwargs.get("name", None)
    uuid = kwargs.get("uuid", None)

    config = {}
    if input_url:
        config = read_config_from_file(input_url)
    elif collection is not None and database is not None:
        if uuid is None and name is None:
            raise KeyError(
                "At least one of the arguments 'name' and 'uuid' must be provided."
            )
        if uuid is not None:
            config = read_config_from_database(
                name_or_uuid=uuid,
                database=database,
                collection=collection,
                class_name=component_name,
            )
        elif name is not None:
            config = read_config_from_database(
                name_or_uuid=name,
                database=database,
                collection=collection,
                class_name=component_name,
            )
    else:
        raise KeyError(
            "Exactly one of that arguments 'input_url' and [collection', 'database'] must be provided."
        )

    # check that the proper configuration exists in configuration file
    if component_name is not None and component_name not in config.keys():
        raise ValueError(
            f"Requested component {component_name} does not exist in config file."
        )

    # check camera name and UUID (if provided)
    if name is not None and config[component_name].name != str(name):
        raise ValueError(
            f"Requested name '{name}' does not match name "
            f"'{config[component_name].name}' in configuration."
            f" Available name in configuration: '{config[component_name].name}'."
        )
    elif uuid is not None and config[component_name].uuid != str(uuid):
        raise ValueError(
            f"Requested UUID '{uuid}' does not match name "
            f"'{config[component_name].uuid}' in configuration."
            f" Available UUID in configuration: '{config[component_name].uuid}'."
        )

    return config


def read_config_from_file(input_url: str or Path) -> tc.Config:
    """
    Read a configuration (traitlets.config.Config) from file.

    Supported file types: YAML, JSON

    Parameters
    ----------
    input_url: str or Path
        path to the configuration file

    Returns
    -------
    config: traitlets.config.Config
        configuration
    """
    input_url = Path(input_url)

    # check for existence of file (provided path and default directory
    if not input_url.is_file():
        log.info(f"config file {input_url} does not exist.")
        input_url = get_basedir() / "resources" / input_url.name
        log.info(f"trying {input_url}...")
        if not input_url.is_file():
            raise FileNotFoundError("config file does not exist.")

    with open(input_url, "r") as infile:
        if input_url.suffix in [".yaml", ".yml"]:
            return tc.Config(yaml.safe_load(infile))
        elif input_url.suffix == ".json":
            return tc.Config(json.load(infile))


def read_config_from_database(
    name_or_uuid: str, database: str, collection: str, class_name: str or None = None
) -> tc.Config:
    """
    Read a configuration (traitlets.config.Config) from database.

    Parameters
    ----------
    name_or_uuid: str
        name or UUID of the configuration in the database collection
    database: str
        name of the database table
    collection: str
        name of the database collection
    class_name: str or None
        name of the class (ctapipe.core.Component) this configuration will be applied to.
        Will be used to build the outer dictionary of the configuration.

    Returns
    -------
    config: traitlets.config.Config
        configuration
    """
    provide_database = partial(provide_mongo_db, database=database, access_role="read")

    with provide_database() as db:
        db_collection = db[collection]
        cursor = db_collection.find(
            {"$or": [{"name": name_or_uuid}, {"uuid": name_or_uuid}]}
        )
        try:
            config_dict = cursor[0]
        except IndexError:
            raise IndexError(
                f"No such name or UUID '{name_or_uuid}' in database '{database}'/collection '{collection}'."
            )

    del config_dict["_id"]  # remove mongo ID
    config_dict = {class_name: config_dict} if class_name is not None else config_dict
    return tc.Config(config_dict)
