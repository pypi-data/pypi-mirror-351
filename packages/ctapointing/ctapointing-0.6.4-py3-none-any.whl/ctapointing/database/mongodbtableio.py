import enum
from functools import partial
import logging
import numpy as np

from astropy.units import Quantity
from astropy.time import Time

from ctapipe.core import Container
from ctapipe.io import TableWriter, TableReader
from ctapipe.io.tableio import (
    ColumnTransform,
    EnumColumnTransform,
    TimeColumnTransform,
    QuantityColumnTransform,
)

from ctapointing.database.mongodb import provide_mongo_db

log = logging.getLogger(__name__)


class NDArrayColumnTransform(ColumnTransform):
    """A Column transformation that converts a numpy array to a list"""

    def __init__(self, dtype):
        self.dtype = dtype

    def __call__(self, value):
        """
        Convert numpy array to list
        """
        return value.tolist()

    def inverse(self, value):
        return np.array(value, dtype=self.dtype)

    def get_meta(self, colname):
        return {
            f"CTAFIELD_{colname}_TRANSFORM": "ndarray",
            f"CTAFIELD_{colname}_DTYPE": str(self.dtype),
        }


class MongoDBTableWriter(TableWriter):
    """
    Class for writing `~ctapipe.core.Container` objects to a mongo database table
    """

    def __init__(
        self,
        database_name,
        add_prefix=False,
        parent=None,
        config=None,
    ):
        super().__init__(add_prefix=add_prefix, parent=parent, config=config)
        self.database_name = database_name
        self.open(database_name)

    def open(self, filename, **kwargs):
        pass

    def close(self):
        pass

    def _prepare_data(self, collection_name, container):
        """
        Prepare the data stored in the container by converting
        non-standard data types to mongo types
        """

        data = {}
        meta = {}

        # prepare Field data
        for name, value in container.items(add_prefix=self.add_prefix):
            # set up automatic transforms to make values that cannot be
            # written in their default form into a form that is serializable
            tr = None
            if isinstance(value, enum.Enum):
                tr = EnumColumnTransform(enum=value.__class__)
            elif isinstance(value, Quantity):
                tr = QuantityColumnTransform(unit=value.unit)
            elif isinstance(value, np.ndarray):
                tr = NDArrayColumnTransform(value.dtype)
            elif isinstance(value, Time):
                tr = TimeColumnTransform(scale=value.scale, format=value.format)

            if tr is not None:
                self.add_column_transform(collection_name, name, tr)
                value = self._apply_col_transform(collection_name, name, value)
                if hasattr(tr, "get_meta"):
                    meta.update(tr.get_meta(name))
                meta[f"CTAFIELD_{name}_NAME"] = name

            # make sure that arrays are converted to lists, as mongo cannot store arrays
            if isinstance(value, np.ndarray):
                value = value.tolist()

            data[name] = value

        # prepare meta data, which will be stored in the database table in a separate meta object
        for k, v in container.meta.items():
            if isinstance(v, np.ndarray):
                meta[k] = v.tolist()
            else:
                meta[k] = v
        data["meta"] = meta
        return data

    def write(self, collection_name, containers, replace=False):
        """
        Write the contents of the given container or containers to a MongoDB table.
        Parameters
        ----------
        collection_name: str
            name of collection within the database to write to
        containers: `ctapipe.core.Container` or `Iterable[ctapipe.core.Container]`
            container to write
        replace: replace table entry in database if already existing
        """
        if isinstance(containers, Container):
            containers = (containers,)

        provide_database = partial(
            provide_mongo_db, database=self.database_name, access_role="readWrite"
        )

        result = None
        with provide_database() as db:
            collection = db[collection_name]

            for container in containers:
                # make sure data is complete
                container.validate()

                if not isinstance(container.uuid, str):
                    log.warning("No UUID found in container metadata. Skip writing.")
                    continue

                data = self._prepare_data(collection_name, container)

                is_in_db = collection.count_documents({"uuid": container.uuid}) > 0

                if is_in_db and replace:
                    result = collection.replace_one(
                        {"uuid": container.uuid}, data, upsert=True
                    )
                elif not is_in_db:
                    result = collection.insert_one(data)
                else:
                    log.warning(
                        f"Not writing container {container.uuid} to database: entry already exists"
                    )

        return result


class MongoDBTableReader(TableReader):
    """
    Class for reading a `ctapipe.core.Container` object from a Mongo database table.
    """

    def __init__(self, database_name, **kwargs):
        """
        Parameters
        ----------
        database_name: str
            name of database table
        kwargs:
            any other arguments that will be passed through
        """

        super().__init__()
        self.database_name = database_name
        self.open(database_name, **kwargs)

    def open(self, database_name, **kwargs):
        pass

    def close(self):
        pass

    def _convert_data(self, data):
        """
        Convert read-in data back to original type, using stored meta information
        """
        meta = data["meta"]

        for name, value in data.items():
            tr = None
            transform_name = f"CTAFIELD_{name}_TRANSFORM"

            if transform_name in meta:
                if meta[transform_name] == "time":
                    scale = meta[f"CTAFIELD_{name}_TIME_SCALE"]
                    time_format = meta[f"CTAFIELD_{name}_TIME_FORMAT"]
                    tr = TimeColumnTransform(scale=scale, format=time_format)

                elif meta[transform_name] == "quantity":
                    unit = meta[f"CTAFIELD_{name}_UNIT"]
                    tr = QuantityColumnTransform(unit)

                elif meta[transform_name] == "enum":
                    enum = meta[f"CTAFIELD_{name}_ENUM"]
                    tr = EnumColumnTransform(enum)

                elif meta[transform_name] == "ndarray":
                    dtype = meta[f"CTAFIELD_{name}_DTYPE"]
                    tr = NDArrayColumnTransform(dtype)

                if tr is not None:
                    data[name] = tr.inverse(value)

        return data

    def read(
        self, collection_name, containers, prefixes=None, selection_dict={}, limit=0
    ):
        return_iterable = True

        if isinstance(containers, Container):
            raise TypeError("Expected container *classes*, not *instances*")

        # check for a single container
        if isinstance(containers, type):
            containers = (containers,)
            return_iterable = False

        for container in containers:
            if isinstance(container, Container):
                raise TypeError("Expected container *classes*, not *instances*")

        if prefixes is False:
            prefixes = ["" for _ in containers]
        elif prefixes is True:
            prefixes = [container.default_prefix for container in containers]
        elif isinstance(prefixes, str):
            prefixes = [prefixes for _ in containers]
        elif prefixes is None:
            prefixes = [None] * len(containers)

        if len(prefixes) != len(containers):
            raise ValueError("Length of provided prefixes does not match containers")

        provide_database = partial(
            provide_mongo_db, database=self.database_name, access_role="read"
        )

        with provide_database() as db:
            ret = []

            for container, prefix in zip(containers, prefixes):
                collection = db[collection_name]

                try:
                    _ = collection.count_documents(selection_dict)
                except Exception as e:
                    log.error(f"Could not access collection {collection_name}: {e}")
                    return None

                try:
                    result = collection.find(selection_dict, limit=limit)
                except Exception as e:
                    log.error(
                        f"Could not read any item from collection {collection_name}: {e}"
                    )
                    return None

                for data in result:
                    del data["_id"]  # remove mongo id

                    data = self._convert_data(data)
                    c = container(**data, prefix=prefix)
                    yield c

                # iterables not working at the moment
                # if return_iterable:
                #     yield ret
                # else:
                #     yield ret[0]
