import pathlib
from tqdm.auto import tqdm
from contextlib import ExitStack
from copy import deepcopy

from astropy.coordinates import SkyCoord, ICRS
import astropy.units as u

from ctapipe.core.traits import Unicode, Path, Float, List
from ctapipe.core import Tool
from ctapipe.io import HDF5TableWriter

from ctapointing.camera import PointingCamera, DistortionCorrectionSIP
from ctapointing.exposure import Exposure
from ctapointing.imagesolver import (
    ImageSolver,
    ImageSolution,
    SkyFitter,
    LEDFitter,
    SpotType,
)
from ctapointing.database import MongoDBTableWriter, check_collection_exists
from ctapointing.io import SpotListSource


class SolveImagesTool(Tool):
    name = "ctapointing-solve-images"
    description = "solve images from spot lists"

    # command-line arguments
    aliases = {
        "image-url": "SolveImagesTool.image_url",
        "input-url": "SpotListSource.input_url",
        "output-url": "SolveImagesTool.hdf5_output_url",
        "image-collection": "SolveImagesTool.image_collection",
        "estimated-pointing-alt": "SolveImagesTool.estimated_pointing_alt",
        "estimated-pointing-az": "SolveImagesTool.estimated_pointing_az",
        "estimated-camera-rotation": "SolveImagesTool.estimated_camera_rotation",
        "max-events": "SpotListSource.max_events",
    }

    # classes registered for configuration information
    classes = [
        SpotListSource,
        ImageSolver,
        SkyFitter,
        HDF5TableWriter,
        MongoDBTableWriter,
    ]

    # TODO: to load Exposure from database; should be removed at some point
    image_url = Path(
        exists=True, file_ok=False, help="image directory", default_value="."
    ).tag(config=True)
    image_database = Unicode(help="image database", default_value="").tag(config=True)
    image_collection = Unicode(
        help="image collection in database", default_value=""
    ).tag(config=True)
    image_solution_writers = List(default_value=["HDF5TableWriter"]).tag(config=True)
    hdf5_output_url = Path(
        directory_ok=False, help="output filename", allow_none=False
    ).tag(config=True)
    hdf5_group_name = Unicode(
        help="group name under which table is written", default_value="image_solutions"
    ).tag(config=True)
    mongo_output_database = Unicode(
        help="image solution database",
        default_value="image_solutions",
        allow_none=False,
    ).tag(config=True)
    mongo_output_collection = Unicode(
        help="image solution collection in database", allow_none=False
    ).tag(config=True)

    estimated_pointing_alt = Float(
        default_value=None,
        help="estimated telescope pointing (altitude, in degrees)",
        allow_none=True,
    ).tag(config=True)
    estimated_pointing_az = Float(
        default_value=None,
        help="estimated telescope pointing (azimuth, in degrees)",
        allow_none=True,
    ).tag(config=True)
    estimated_camera_rotation = Float(
        help="estimated rotation of camera w.r.t. horizon (in degrees)", allow_none=True
    ).tag(config=True)

    def setup(self):
        self.hdf5_writer = None
        self.mongo_writer = None

        if "HDF5TableWriter" in self.image_solution_writers:
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

        if "MongoDBTableWriter" in self.image_solution_writers:
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

        self.spotlist_source = SpotListSource(parent=self)
        self.solver = ImageSolver(parent=self)
        self.sky_fitter = SkyFitter(parent=self)
        self.led_fitter = LEDFitter(parent=self)
        self.pointing_camera = PointingCamera(parent=self)

    def start(self):
        with ExitStack() as stack:
            stack.enter_context(self.spotlist_source)
            if self.hdf5_writer is not None:
                stack.enter_context(self.hdf5_writer)
            if self.mongo_writer is not None:
                stack.enter_context(self.mongo_writer)

            i = 0
            for spotlist in tqdm(
                self.spotlist_source,
                desc=self.solver.name,
                unit="img",
                total=len(self.spotlist_source),
            ):
                if self.image_database:
                    exposure = Exposure.from_name(
                        spotlist.image_uuid,
                        database_name=self.image_database,
                        collection_name=self.image_collection,
                        load_image=False,
                    )
                else:
                    exposure = Exposure.from_name(
                        spotlist.image_uuid,
                        read_meta_from_fits=True,
                        load_image=True,
                        image_path=self.image_url,
                    )

                self.log.info(f"processing image {spotlist.image_uuid}")

                # load camera information (make sure we start each reconstruction with a fresh camera)
                exposure.camera = deepcopy(self.pointing_camera)
                exposure.ambient_temperature = (
                    exposure.camera_temperature
                )  # 0.0 * u.deg_C
                exposure.ambient_pressure = (
                    1020.0 * u.hPa
                )  # TODO: replace by proper pressure measurement

                if self.estimated_camera_rotation:
                    exposure.camera.rotation = self.estimated_camera_rotation * u.deg

                # try to set estimated pointing for star field matching
                estimated_pointing = None
                if self.estimated_pointing_alt is not None:
                    estimated_pointing_altaz = SkyCoord(
                        az=self.estimated_pointing_az * u.deg,
                        alt=self.estimated_pointing_alt * u.deg,
                        frame=exposure.altazframe,
                    )
                    estimated_pointing = estimated_pointing_altaz
                    self.log.info(
                        f"applying AltAz estimated pointing {estimated_pointing}"
                    )
                elif exposure.nominal_telescope_pointing is not None:
                    estimated_pointing = exposure.nominal_telescope_pointing
                    self.log.info(
                        f"applying nominal telescope pointing {estimated_pointing}"
                    )
                else:
                    self.log.info("no estimated pointing given. Will not fit to sky.")

                # create ImageSolution object to be filled by the different solvers/fitters
                # and fill with image information
                image_solution = ImageSolution()
                image_solution.mean_exposure_time = exposure.mean_exposure_time
                image_solution.exposure_duration = exposure.duration
                image_solution.camera_chip_temperature = spotlist.chip_temperature
                image_solution.camera_temperature = spotlist.camera_temperature
                image_solution.camera_humidity = spotlist.camera_humidity
                image_solution.mean_background = spotlist.mean_background
                image_solution.spotlist_uuid = spotlist.uuid
                image_solution.image_uuid = spotlist.image_uuid

                if estimated_pointing is not None:
                    estimated_pointing = estimated_pointing.transform_to(ICRS)
                    self.log.info(f"estimated ICRS pointing is {estimated_pointing}")

                    #
                    # sky fitting
                    #
                    spotlist_sky = spotlist.select_by_type(SpotType.SKY)

                    if len(spotlist_sky) > 0:
                        image_solution, match_list, stars, registration = (
                            self.solver.process(
                                spotlist=spotlist_sky,
                                exposure=exposure,
                                estimated_pointing=estimated_pointing,
                                image_solution=image_solution,
                            )
                        )

                        if match_list is not None and len(match_list) != 0:
                            best_match = match_list[0][0]
                            (
                                image_solution,
                                minuit_skyfit,
                                minuit_reverse_fit,
                            ) = self.sky_fitter.process(
                                best_match.star_spot_match_list,
                                exposure,
                                estimated_pointing,
                                distortion_correction=DistortionCorrectionSIP(),
                                image_solution=image_solution,
                            )
                        else:
                            self.log.warn("no proper quad found for exposure.")
                    else:
                        self.log.warn("no spots found for sky fitting.")

                #
                # LED fitting
                #
                spotlist_led = spotlist.select_by_type(SpotType.LED)

                if len(spotlist_led) > 0:
                    # TODO: get rid of explicit camera
                    from ctapointing.camera import FlashCam

                    science_cam = FlashCam()

                    image_solution, m, coord_leds_final, coord_spots_matched = (
                        self.led_fitter.process(
                            spotlist=spotlist_led,
                            exposure=exposure,
                            science_camera=science_cam,
                            image_solution=image_solution,
                        )
                    )
                else:
                    self.log.warn("no LEDs found for science camera fitting.")

                #
                # Lid parameters
                #
                spotlist_lid = spotlist.select_by_type(SpotType.LID)

                if len(spotlist_lid) > 0:
                    image_solution.lid_spots_x = spotlist_lid.coord_x
                    image_solution.lid_spots_y = spotlist_lid.coord_y
                else:
                    self.log.warn("no lid spot(s) found.")

                # write results to file and database
                if image_solution is not None:
                    if self.hdf5_writer is not None:
                        self.hdf5_writer.write(
                            f"image_solution_{i:06d}", image_solution
                        )
                    if self.mongo_writer is not None:
                        self.mongo_writer.write(
                            self.mongo_output_collection, image_solution
                        )
                else:
                    self.log.warn(
                        f"no solution found for exposure {exposure.uuid}. Skipping writing."
                    )

                i += 1

    def finish(self):
        self.log.warning("Shutting down.")


def main():
    tool = SolveImagesTool()
    tool.run()


if __name__ == "__main__":
    main()
