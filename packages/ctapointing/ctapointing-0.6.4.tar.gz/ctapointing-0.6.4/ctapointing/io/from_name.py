import re
from os import path, environ, walk
import logging

from ctapipe.core.container import ContainerMeta
from ctapipe.io import HDF5TableReader
from ctapointing.database import MongoDBTableReader

log = logging.getLogger(__name__)


def from_name(name, container, **kwargs):
    """
    Read data from either HDF5 file or database into Container.

    Parameters
    ----------
    name: str
        when reading from database (see below), name refers to the UUID of the dataset
        when reading from file, name refers to the file name
    container: ctapipe.core.Container
        container class into which the data is read
    **kwargs:
        database_name: str or None
            if specified, read from database with name database_name. Must be specified
            for reading from database. If set to None, file reading mode is assumed
        collection_name: str or None
            if specified, read from database collection collection_name. Must be specified
            for database reading
        table_name: str or None:
            the table within the HDF5 file from which data is read. Must be specified
            for file reading

    Returns
    -------
    Container: Container
        object of type container
    """
    database_name = kwargs.pop("database_name", None)
    collection_name = kwargs.pop("collection_name", None)
    table_name = kwargs.pop("table_name", None)

    if not isinstance(name, str):
        raise TypeError("argument 'name' must be of type str")

    if not isinstance(container, ContainerMeta):
        raise TypeError(
            f"argument 'container' must inherit from ctapipe.core.ContainerMeta, but is of type {type(container)}"
        )

    if (database_name is None or collection_name is None) and table_name is None:
        raise AttributeError(
            "either database/collection name or table name must be provided."
        )

    # read from database
    if database_name is not None:
        with MongoDBTableReader(database_name, **kwargs) as reader:
            gen = reader.read(
                collection_name=collection_name,
                containers=container,
                selection_dict={"uuid": name},
            )
            return next(gen)

    # read from file
    else:
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
                        name_string = r"^" + name + r".*h.*5"
                        name_match = re.search(name_string, filename)
                        fullname_string = r"^" + name
                        fullname_match = re.search(fullname_string, filename)
                        uuid_string = r".*" + name + r"*.h.*5"
                        uuid_match = re.search(uuid_string, filename)
                        if name_match or fullname_match or uuid_match:
                            fullname = path.join(root, filename)
                            break

        if fullname is None:
            log.warning("no HDF5 file found on search paths %s" % search_dirs)
            return None

        try:
            with HDF5TableReader(fullname, **kwargs) as reader:
                gen = reader.read(table_name, container, **kwargs)
                return next(gen)
        except Exception as e:
            log.warning(f"problem opening HDF5 file: {e}")
            return None
