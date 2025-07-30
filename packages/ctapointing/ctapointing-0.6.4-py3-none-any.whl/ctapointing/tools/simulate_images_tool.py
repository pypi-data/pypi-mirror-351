from tqdm.auto import tqdm

from astropy.coordinates import SkyCoord, ICRS

from ctapipe.core.traits import Unicode, Path, Bool, List
from ctapipe.core import Tool
from ctapipe.core.tool import export_tool_config_to_commented_yaml
from ctapipe.io import HDF5TableWriter

from ctapointing.camera import PointingCamera, ScienceCamera
from ctapointing.exposure import ExposureSimulator
from ctapointing.observation import ObservationPlan
from ctapointing.database import (
    MongoDBTableWriter,
    check_collection_exists,
)


class SimulateImagesTool(Tool):
    name = "ctapointing-simulate-images"
    description = "simulate camera images"

    # command-line arguments
    aliases = {
        "observation-plan": "ObservationPlan.input_url",
        #        "science-camera": "SimulateImagesTool.science_camera",
        "image-collection": "SimulateImagesTool.image_collection",
    }

    # classes registered for configuration information
    classes = [
        PointingCamera,
        ScienceCamera,
        ObservationPlan,
        ExposureSimulator,
        MongoDBTableWriter,
    ]

    image_url = Path(
        exists=None, file_ok=False, help="image directory", default_value="."
    ).tag(config=True)
    image_database = Unicode(
        help="image database", default_value="images", allow_none=False
    ).tag(config=True)
    image_collection = Unicode(
        help="image collection in database", default_value="test", allow_none=False
    ).tag(config=True)
    exposure_writers = List(default_value=["HDF5TableWriter"]).tag(config=True)
    hdf5_group_name = Unicode(
        help="group name under which table is written", default_value="exposure"
    ).tag(config=True)
    write_config = Path(
        default_value=None, help="write configuration to output file", allow_none=True
    ).tag(config=True)
    progress_bar = Bool(
        help="show progress bar during processing", default_value=False
    ).tag(config=True)
    simulate_science_camera = Bool(
        help="simulate the body/LEDs of the science camera", default_value=True
    ).tag(config=True)

    def setup(self):
        if self.write_config is not None:
            yaml_text = export_tool_config_to_commented_yaml(self)
            with open(self.write_config, "w") as output_file:
                output_file.write(yaml_text)

        # set up observation plan
        self.observation_plan = ObservationPlan(parent=self)

        # set up simulator and cameras
        self.simulator = ExposureSimulator(parent=self)

        self.camera = PointingCamera(parent=self)

        self.science_camera = None
        if self.simulate_science_camera:
            self.science_camera = ScienceCamera(parent=self)

        # set up database writer
        self.mongo_writer = None
        if "MongoDBTableWriter" in self.exposure_writers:
            if not self.overwrite and check_collection_exists(
                self.image_database, self.image_collection
            ):
                self.log.error(
                    f"Will not append to existing collection '{self.image_collection}'. "
                    f"Set option --overwrite=True to force appending."
                )
                raise FileExistsError

            self.mongo_writer = MongoDBTableWriter(
                database_name=self.image_database, parent=self
            )

        # create image directory
        try:
            if not self.image_url.is_dir():
                self.log.info(f"creating image directory {self.image_url}")
                self.image_url.mkdir(parents=False, exist_ok=True)
        except FileNotFoundError:
            self.log.error(
                f"unable to create image directory {self.image_url}. Make sure that parent directory exists."
            )
            raise FileNotFoundError

    def start(self):
        num_events = len(self.observation_plan)

        for pointing_observation in tqdm(
            self.observation_plan,
            desc=self.simulator.name,
            unit="img",
            total=num_events,
        ):
            self.log.info(f"simulating observation {pointing_observation}")

            target_pos = SkyCoord(
                pointing_observation.target_pos_ra,
                pointing_observation.target_pos_dec,
                frame=ICRS,
            )
            exposure = self.simulator.process(
                self.camera,
                target_pos,
                pointing_observation.start_time,
                pointing_observation.duration,
                science_camera=self.science_camera,
            )

            # write FITS file
            exposure.write_to_fits(
                self.image_url / f"ctapointing_simulation_{exposure.uuid}.fits.gz",
                force_overwrite=self.overwrite,
            )

            # write exposure information to H5 file
            if "HDF5TableWriter" in self.exposure_writers:
                with HDF5TableWriter(
                    self.image_url / f"ctapointing_simulation_{exposure.uuid}.h5"
                ) as writer:
                    writer.write(
                        table_name=self.hdf5_group_name,
                        containers=exposure.to_container(),
                    )

            # write exposure information to database
            if self.mongo_writer is not None:
                self.mongo_writer.write(
                    collection_name=self.image_collection,
                    containers=exposure.to_container(),
                    replace=self.overwrite,
                )

    def finish(self):
        self.log.info("Shutting down.")


def main():
    tool = SimulateImagesTool()
    tool.run()


if __name__ == "__main__":
    main()
