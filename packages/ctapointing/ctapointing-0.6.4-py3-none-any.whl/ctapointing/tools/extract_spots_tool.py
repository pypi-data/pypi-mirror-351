import pathlib
from contextlib import ExitStack
from tqdm.auto import tqdm

from ctapipe.core.traits import Unicode, Path, Dict, List, Int, Bool
from ctapipe.core import Tool
from ctapipe.core.tool import export_tool_config_to_commented_yaml
from ctapipe.io import HDF5TableWriter

from ctapointing.camera import ScienceCamera, PointingCamera
from ctapointing.exposure import Exposure
from ctapointing.exposure.exposure_container import ExposureContainer
from ctapointing.imagesolver import SpotExtractorSky, SpotExtractorLED, SpotExtractorLid
from ctapointing.database import (
    MongoDBTableReader,
    MongoDBTableWriter,
    check_collection_exists,
)


class ExtractSpotsTool(Tool):
    name = "ctapointing-extract-spots"
    description = "extract spots from camera images"

    # command-line arguments
    aliases = {
        "image-url": "ExtractSpotsTool.image_url",
        "image-database": "ExtractSpotsTool.image_database",
        "image-collection": "ExtractSpotsTool.image_collection",
        "image-selection": "ExtractSpotsTool.image_selection",
        "output-url": "ExtractSpotsTool.hdf5_output_url",
        "max-events": "ExtractSpotsTool.max_events",
    }

    # classes registered for configuration information
    classes = [
        SpotExtractorSky,
        SpotExtractorLED,
        SpotExtractorLid,
        HDF5TableWriter,
        MongoDBTableWriter,
        PointingCamera,
    ]

    image_url = Path(
        exists=True, file_ok=False, help="image directory", default_value="."
    ).tag(config=True)
    image_database = Unicode(help="image database", default_value="").tag(config=True)
    image_collection = Unicode(
        help="image collection in database", default_value=""
    ).tag(config=True)
    image_selection = Dict(help="image selection dictionary", default_value={}).tag(
        config=True
    )
    spot_extractors = List(default_value=["SpotExtractorSky"]).tag(config=True)
    spotlist_writers = List(default_value=["HDF5TableWriter"]).tag(config=True)
    hdf5_group_name = Unicode(
        help="group name under which table is written", default_value="spots"
    ).tag(config=True)
    hdf5_output_url = Path(
        directory_ok=False, help="output filename", allow_none=False
    ).tag(config=True)
    mongo_output_database = Unicode(
        help="spotlist database", default_value="spots", allow_none=False
    ).tag(config=True)
    mongo_output_collection = Unicode(
        help="spotlist collection in database", allow_none=False
    ).tag(config=True)
    max_events = Int(
        default_value=None,
        help="maximum number of events that are processed",
        allow_none=True,
    ).tag(config=True)
    write_config = Path(
        default_value=None, help="write configuration to output file", allow_none=True
    ).tag(config=True)
    progress_bar = Bool(
        help="show progress bar during processing", default_value=False
    ).tag(config=True)

    def setup(self):
        if self.write_config is not None:
            yaml_text = export_tool_config_to_commented_yaml(self)
            with open(self.write_config, "w") as output_file:
                output_file.write(yaml_text)

        if len(self.spot_extractors) == 0:
            self.log.error(
                "At least one SpotExtractor must be set in spot_extractors list."
            )
            raise AttributeError(
                "At least one SpotExtractor must be set in spot_extractors list."
            )

        # set up spot extractors
        self.spot_extractor_sky = (
            SpotExtractorSky(parent=self)
            if "SpotExtractorSky" in self.spot_extractors
            else None
        )
        self.spot_extractor_led = (
            SpotExtractorLED(parent=self)
            if "SpotExtractorLED" in self.spot_extractors
            else None
        )
        self.spot_extractor_lid = (
            SpotExtractorLid(parent=self)
            if "SpotExtractorLid" in self.spot_extractors
            else None
        )
        self.science_camera = (
            ScienceCamera(parent=self)
            if "SpotExtractorLED" in self.spot_extractors
            or "SpotExtractorLid" in self.spot_extractors
            else None
        )
        self.pointing_camera = PointingCamera(parent=self)

        # set up spot list writer components
        self.hdf5_writer = None
        self.mongo_writer = None
        if "HDF5TableWriter" in self.spotlist_writers:
            if not self.overwrite and pathlib.Path(self.hdf5_output_url).exists():
                self.log.error(
                    f"Will not overwrite existing output file {self.hdf5_output_url}. "
                    f"Set option --overwrite=True to force overwriting."
                )
                raise FileExistsError

            self.hdf5_writer = HDF5TableWriter(
                filename=self.hdf5_output_url,
                group_name=self.hdf5_group_name,
                parent=self,
            )
        if "MongoDBTableWriter" in self.spotlist_writers:
            if not self.overwrite and check_collection_exists(
                self.mongo_output_database, self.mongo_output_collection
            ):
                self.log.error(
                    f"Will not append to existing collection {self.mongo_output_collection}. "
                    f"Set option --overwrite=True to force appending."
                )
                raise FileExistsError

            self.mongo_writer = MongoDBTableWriter(
                database_name=self.mongo_output_database, parent=self
            )

        self.image_list = []
        if self.image_database:
            with MongoDBTableReader(self.image_database) as reader:
                self.log.info(
                    f"reading images from collection {self.image_database}/{self.image_collection}"
                )

                for container in reader.read(
                    self.image_collection,
                    containers=ExposureContainer,
                    selection_dict=self.image_selection,
                ):
                    self.image_list.append(container.uuid)
        else:
            # read image names from image directory
            self.image_list = [f for f in self.image_url.glob("*fits*")]

        self.log.info(f"read {len(self.image_list)} images.")

    def start(self):
        # use context manager that can run one or more spot writers
        with ExitStack() as stack:
            if self.hdf5_writer is not None:
                stack.enter_context(self.hdf5_writer)
            if self.mongo_writer is not None:
                stack.enter_context(self.mongo_writer)

            i = 0
            num_events = (
                self.max_events if self.max_events is not None else len(self.image_list)
            )
            for image_name in tqdm(
                self.image_list,
                unit="img",
                total=num_events,
            ):
                self.log.info(f"loading image {image_name}")
                if self.image_database:
                    exposure = Exposure.from_name(
                        image_name,
                        database_name=self.image_database,
                        collection_name=self.image_collection,
                        image_path=self.image_url,
                    )
                else:
                    exposure = Exposure.from_name(
                        image_name,
                        read_meta_from_fits=True,
                        image_path=self.image_url,
                    )
                if exposure.image is None:
                    self.log.warn(
                        f"Skipping exposure {exposure.uuid} because image not found."
                    )
                    continue

                # load camera information
                exposure.camera = self.pointing_camera

                self.log.info(f"processing image {image_name}")

                spotlist = None
                if self.spot_extractor_sky:
                    spotlist = self.spot_extractor_sky.process(exposure)

                if self.spot_extractor_led:
                    self.spot_extractor_led.generate_led_mask(
                        exposure, science_camera=self.science_camera
                    )
                    if spotlist is None:
                        spotlist = self.spot_extractor_led.process(exposure)
                    else:
                        spotlist.append(self.spot_extractor_led.process(exposure))

                if self.spot_extractor_lid:
                    self.spot_extractor_lid.generate_lid_mask(
                        exposure, science_camera=self.science_camera
                    )
                    if spotlist is None:
                        spotlist = self.spot_extractor_lid.process(exposure)
                    else:
                        spotlist.append(self.spot_extractor_lid.process(exposure))

                if self.hdf5_writer is not None:
                    self.hdf5_writer.write(f"spotlist_{i:06d}", spotlist)
                if self.mongo_writer is not None:
                    self.mongo_writer.write(self.mongo_output_collection, spotlist)

                if i >= num_events:
                    break

                i += 1

    def finish(self):
        self.log.info("Shutting down.")


def main():
    tool = ExtractSpotsTool()
    tool.run()


if __name__ == "__main__":
    main()
