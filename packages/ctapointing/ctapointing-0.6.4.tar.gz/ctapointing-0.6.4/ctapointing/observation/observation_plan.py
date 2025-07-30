import uuid
import pathlib

from astropy.table import QTable
from astropy.time import Time
from astropy.coordinates import SkyCoord, ICRS
import astropy.units as u

from ctapipe.core import Component
from ctapipe.core.traits import Unicode, Path, Undefined

from ctapointing.config import from_config
from ctapointing.config import AstroEarthLocation
from ctapointing.observation.pointing_observation import PointingObservation
from ctapointing.observation.starselector import StarSelectorIsotropic


class ObservationPlan(Component):
    """
    Observation planning for pointing observations.
    """

    uuid = Unicode(default_value=str(uuid.uuid4()), help="UUID of ObservationPlan").tag(
        config=True
    )
    name = Unicode(
        default_value="MyObservationPlan", help="name of ObservationPlan"
    ).tag(config=True)
    input_url = Path(
        default_value=None,
        exists=True,
        directory_ok=False,
        help="observation plan file",
        allow_none=True,
    ).tag(config=True)

    def __init__(self, config=None, parent=None, **kwargs):
        """
        Class to create and store observation plans.
        """
        super().__init__(config=config, parent=parent, **kwargs)

        self.pointing_observations = []
        if self.input_url is not None:
            self.read(self.input_url)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = f"{self.__class__.__name__}(uuid={self.uuid}"
        s += f", number of targets={len(self.pointing_observations)})"
        return s

    @classmethod
    def from_config(cls, **kwargs):
        """
        Read an observation plan configuration from either configuration file or database.
        Either the path of a configuration file ('input_url') or a database collection
        ('collection') must be provided.

        Parameters
        ----------
        input_url: str or pathlib.Path
            path of the configuration file.
        name: str
            name of the camera (as in `PointingCamera.name`).
            When loading the configuration from file, can be set to check that the configuration with the
            correct name is loaded.
            When loading from database, is used to identify the correct database record.
        uuid: str
            UUID of the camera (as in `PointingCamera.uuid`).
            When loading the configuration from file, can be set to check that the configuration with the
            correct UUID is loaded.
            When loading from database, is used to identify the correct database record.
        collection: str
            name of the database collection from which
            configuration is read
        database: str
            name of the database in which the collection
            is stored

        Returns
        -------
        plan: ObservationPlan object
        """

        config = from_config(component_name=cls.__name__, **kwargs)
        return cls(config=config)

    def get_schedule(self):
        """
        Return observation plan as a QTable.

        Returns
        -------
        astropy.table.QTable
        """
        data = []
        for po in self.pointing_observations:
            data.append(po.as_dict())

        meta = {"name": self.name, "uuid": self.uuid}
        table = QTable(rows=data, meta=meta)

        return table

    def write(
        self,
        filename: str or Path or None = None,
        file_format: str = "hdf5",
        overwrite: bool = False,
    ):
        """
        Write observation schedule to file.

        The observation plan is converted to an astropy.tables.QTable.
        The file format can be chosen from those available within astropy.tables

        Parameters
        ----------
        filename: str or Path
            filename to which observation plan is written
        file_format: str or Path
            file format, according to astropy specifications
        overwrite: bool
            force overwrite of already existing file if True

        Returns
        -------
        filename: str
            filename of output file
        """
        table = self.get_schedule()

        if filename is None:
            filename = pathlib.Path(".") / f"{self.name}_{self.uuid}.h5"
            file_format = "hdf5"

        filename = str(filename)
        print(f"writing ObservationPlan to {filename}...")
        table.write(
            filename,
            format=file_format,
            serialize_meta=True,
            overwrite=overwrite,
            path="observation_plan",
        )
        return filename

    def read(self, filename: str or Path, file_format: str = "hdf5"):
        """
        Load an observation plan from file (to which it was previously written using ObservationPlan.write()).

        Parameters
        ----------
        filename: str or Path
            filename from which to read the observation plan.
        file_format: str
            file format according to astropy specifications (default: "auto")
        """
        table = QTable.read(str(filename), format=file_format, path="observation_plan")

        self.name = table.meta["name"]
        self.uuid = table.meta["uuid"]
        self.input_url = filename
        self.pointing_observations = []
        for row in table:
            row_dict = {k: v for k, v in zip(row.keys(), row.values())}
            self.pointing_observations.append(PointingObservation(**row_dict))

    def add_target(self, target_name, target_pos, start_time, duration):
        """
        Add a new target at the end of the observation plan.

        Parameters
        ----------
        name: str
            target name
        target_pos: astropy.SkyCoord
            target position (ICRS or AltAz frame)
        start_time: astropy.Time
            start time of observation
        duration: astropy.Quantity
            duration of the observation
        """
        po = PointingObservation()
        po.name = target_name

        # make sure we are in equatorial coordinates
        target_pos_radec = target_pos.transform_to(ICRS)

        po.target_pos_ra = target_pos_radec.ra
        po.target_pos_dec = target_pos_radec.dec
        po.start_time = start_time
        po.duration = duration

        # in case AltAz coordinates are provided, store location
        try:
            po.location_x = target_pos.location.x
            po.location_y = target_pos.location.y
            po.location_z = target_pos.location.z
        except AttributeError:
            po.location_x = None
            po.location_y = None
            po.location_z = None

        self.pointing_observations.append(po)

    def schedule_coordinates_altaz(self, target_position_altaz, duration):
        """
        Schedule according to a set of AltAz coordinates
        """
        target_position_radec = target_position_altaz.transform_to(ICRS)
        for rd, altaz in zip(target_position_radec, target_position_altaz):
            po = PointingObservation()
            po.start_time = altaz.obstime
            po.duration = duration
            po.target_pos_ra = rd.ra
            po.target_pos_dec = rd.dec
            po.location_x = altaz.location.x
            po.location_y = altaz.location.y
            po.location_z = altaz.location.z
            po.ambient_temperature = altaz.temperature
            po.ambient_pressure = altaz.pressure

            self.pointing_observations.append(po)

    def schedule_isotropic(
        self,
        num_targets: int,
        start_time: Time or str,
        location: AstroEarthLocation,
        duration: u.Quantity = 10.0 * u.s,
        time_between_targets: u.Quantity = 120.0 * u.s,
        altitude_limits: (u.Quantity, u.Quantity) = (10.0 * u.deg, 70 * u.deg),
        magnitude_limits: (float, float) = (-3.0, 4.0),
    ):
        """
        Schedule an isotropic observation plan, i.e. aim at selecting targets such that
        isotropy on the (half-)sky is reached.

        Parameters
        ----------
        num_targets: int
            number of targets to schedule
        start_time: astropy.time.Time or str
            start time of the observations
        location: AstroEarthLocation
            earth location of observer
        duration: astropy.units.Quantity
            duration of each exposure
        time_between_targets: astropy.units.Quantity
            time between the targets
        altitude_limits: tuple of astropy.units.Quantity
            altitude lower and upper limit
        magnitude_limits: tuple of float
            magnitude range for star selection
        """
        start_time = Time(start_time)

        time_between_targets = u.Quantity(time_between_targets)
        if time_between_targets <= duration:
            print("Warning: time between targets is smaller than exposure duration.")

        selector = StarSelectorIsotropic(
            location=location,
            altitude_limits=altitude_limits,
            magnitude_limits=magnitude_limits,
        )

        st = start_time
        for i in range(num_targets):
            po = selector.select_target(st, duration)
            self.pointing_observations.append(po)
            st += time_between_targets

    def schedule_polaris(self):
        po = PointingObservation()
        po.target_name = "polaris"
        po.start_time = Time("2023-01-01T00:00:00")
        po.duration = 10.0 * u.s

        polaris = SkyCoord.from_name("polaris")
        po.target_pos_ra = polaris.ra
        po.target_pos_dec = polaris.dec

        self.pointing_observations.append(po)

    @staticmethod
    def is_compatible(file_path):
        return True

    @property
    def is_stream(self):
        return False

    def __len__(self):
        return len(self.pointing_observations)

    def __iter__(self):
        """
        Iterate over SpotList tables

        """
        for po in self.pointing_observations:
            yield po

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def close(self):
        pass
