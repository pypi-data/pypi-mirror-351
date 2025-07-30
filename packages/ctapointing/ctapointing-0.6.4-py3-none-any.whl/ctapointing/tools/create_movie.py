import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from tqdm.auto import tqdm
from astropy.coordinates import Longitude, Latitude
import astropy.units as u

from ctapipe.core.traits import Unicode, Path, Dict, Int, Float
from ctapipe.core import Tool

from ctapointing.database import MongoDBTableReader
from ctapointing.exposure import Exposure
from ctapointing.exposure.exposure_container import ExposureContainer
from ctapointing.io import SpotListSource, ImageSolutionSource


class CreateMovieTool(Tool):
    name = "ctapointing-create-movie"
    description = "create a movie from ctapointing images"

    aliases = {
        "image-url": "CreateMovieTool.image_url",
        "image-database": "CreateMovieTool.image_database",
        "image-collection": "CreateMovieTool.image_collection",
        "image-selection": "CreateMovieTool.image_selection",
        "spotlist-url": "SpotListSource.input_url",
        "imagesolution-url": "ImageSolutionSource.input_url",
        "output-file": "CreateMovieTool.output_file",
        "max-frames": "CreateMovieTool.max_frames",
        "frame-step": "CreateMovieTool.frame_step",
        "frame-rate": "CreateMovieTool.frame_rate",
        "trail-length": "CreateMovieTool.trail_length",
    }

    image_url = Path(
        exists=True, file_ok=False, help="image directory", default_value="."
    ).tag(config=True)
    image_database = Unicode(
        help="image database", default_value="images", allow_none=False
    ).tag(config=True)
    image_collection = Unicode(
        help="image collection in database", allow_none=False
    ).tag(config=True)
    image_selection = Dict(help="image selection dictionary", default_value={}).tag(
        config=True
    )
    output_file = Path(
        help="output file name", default_value="ctapointing-movie.mp4"
    ).tag(config=True)
    max_frames = Int(
        default_value=None,
        help="maximum number of frames that are produced",
        allow_none=True,
    ).tag(config=True)
    frame_step = Int(
        default_value=1, help="step size in between consecutive images"
    ).tag(config=True)
    frame_rate = Float(default_value=10, help="frame rate in Hz").tag(config=True)
    trail_length = Int(
        default_value=10, help="length of star trails", allow_none=True
    ).tag(config=True)

    def setup(self):
        self.image_uuids = []
        self.spotlists = []
        self.solutions = []
        self.image_spotlist_dict = {}
        self.image_solutions_dict = {}
        self.image = None
        self.fig = None
        self.ax = None

        # read image UUIDs from database
        with MongoDBTableReader(self.image_database) as reader:
            self.log.info(
                f"reading images from collection {self.image_database}/{self.image_collection}"
            )

            for container in reader.read(
                self.image_collection,
                containers=ExposureContainer,
                selection_dict=self.image_selection,
            ):
                self.image_uuids.append(container.uuid)

        self.log.info(f"read {len(self.image_uuids)} images.")

        # read in spotlists
        with SpotListSource(parent=self) as source:
            for spotlist in source:
                if spotlist is not None:
                    self.spotlists.append(spotlist)

            self.log.info(f"read {len(self.spotlists)} spot lists.")
            self.image_spotlist_dict = {
                s.image_uuid: i for i, s in enumerate(self.spotlists)
            }

        # read image solutions
        with ImageSolutionSource(parent=self) as source:
            for solution in source:
                if solution is not None:
                    self.solutions.append(solution)

            self.log.info(f"read {len(self.solutions)} image solutions.")
            self.image_solutions_dict = {
                s.image_uuid: i for i, s in enumerate(self.solutions)
            }

        # prepare animation
        exposure = Exposure.from_name(
            self.image_uuids[0],
            database_name=self.image_database,
            collection_name=self.image_collection,
            swap_y=True,
            image_path=self.image_url,
        )

        self.fig, self.ax = plt.subplots(
            figsize=(15, 15 * exposure.camera.num_pix[0] / exposure.camera.num_pix[1])
        )
        self.ax.set_aspect("equal")
        self.ax.set_title("test")

        # image
        self.image = self.ax.imshow(
            exposure.image,
            vmin=exposure.image.mean() - 2 * exposure.image.std(),
            vmax=exposure.image.mean() + 2 * exposure.image.std(),
            cmap="binary",
            origin="lower",
        )

        # spots
        (self.spot_tick1,) = self.ax.plot(
            [],
            [],
            color="b",
            marker="|",
            linestyle="None",
        )

        (self.spot_tick2,) = self.ax.plot(
            [], [], color="b", marker="_", linestyle="None", label="extracted spots"
        )

        (self.spot_tick3,) = self.ax.plot(
            [],
            [],
            color="b",
            marker="|",
            linestyle="None",
        )

        (self.spot_tick4,) = self.ax.plot(
            [],
            [],
            color="b",
            marker="_",
            linestyle="None",
        )

        # fitted stars
        (self.fitted_stars,) = self.ax.plot(
            [],
            [],
            color="r",
            marker="o",
            fillstyle="none",
            linestyle="none",
            label="projected stars (fitted)",
        )

        # set up star trails
        if self.trail_length is not None:
            if self.trail_length < 1:
                self.trail_length = None
            else:
                self.trail_x = []
                self.trail_y = []
                self.trail_stars = self.ax.scatter([], [], c="g", marker=".", alpha=0.5)

        # exposure information
        props = dict(boxstyle="square", facecolor="white", alpha=0.7)
        self.exposure_text = self.ax.text(
            0.02,
            0.98,
            "",
            bbox=props,
            transform=self.ax.transAxes,
            verticalalignment="top",
        )

        self.ax.legend(loc="upper right")
        self.ax.set_xlabel(r"$y_\mathrm{camera}$ (pix)")
        self.ax.set_ylabel(r"$x_\mathrm{camera}$ (pix)")

    def start(self):
        # number of frames
        self.num_frames = len(self.image_uuids) // self.frame_step
        self.num_frames = (
            min(self.num_frames, self.max_frames)
            if self.max_frames is not None
            else self.num_frames
        )

        # maximum image number, taking into account allowed number of frames
        # and frame step size
        max_image_no = self.num_frames * self.frame_step
        print(self.num_frames, max_image_no)

        self.animation = FuncAnimation(
            self.fig,
            self._animate,
            frames=tqdm(np.arange(max_image_no, step=self.frame_step), unit="img"),
            fargs=(),
            interval=1000 / self.frame_rate,
        )

    def _animate(self, frame_no):
        self.log.info(f"processing image {frame_no}")

        # update image
        image_uuid = self.image_uuids[frame_no]
        exposure = Exposure.from_name(
            image_uuid,
            database_name=self.image_database,
            collection_name=self.image_collection,
            swap_y=True,
            image_path=self.image_url,
        )
        self.image.set_array(exposure.image)

        m = exposure.image.mean()
        s = exposure.image.std()
        vmin = m - 3 * s
        vmax = m + 3 * s
        self.image.set_clim((vmin, vmax))

        # update spots
        radius = 50
        if image_uuid in self.image_spotlist_dict:
            sl_index = self.image_spotlist_dict[image_uuid]
            sl = self.spotlists[sl_index]
            self.spot_tick1.set_data(sl.coord_y, sl.coord_x - radius)
            self.spot_tick2.set_data(sl.coord_y + radius, sl.coord_x)
            self.spot_tick3.set_data(sl.coord_y, sl.coord_x + radius)
            self.spot_tick4.set_data(sl.coord_y - radius, sl.coord_x)

        # fitted stars and outliers
        fitted_position_ra = np.nan * u.deg
        fitted_position_dec = np.nan * u.deg
        fitted_position_alt = np.nan * u.deg
        fitted_position_az = np.nan * u.deg
        camera_rotation = np.nan * u.deg
        focal_length = np.nan * u.mm
        if image_uuid in self.image_solutions_dict:
            sl_index = self.image_solutions_dict[image_uuid]
            sl = self.solutions[sl_index]
            self.fitted_stars.set_data(sl.stars_fitted_y, sl.stars_fitted_x)

            # star trails
            if self.trail_length is not None:
                tx = [item for row in self.trail_x for item in row]
                ty = [item for row in self.trail_y for item in row]
                t = np.array([ty, tx]).T
                self.trail_stars.set_offsets(t)

                # set transparency
                if len(self.trail_x) > 0:
                    alpha = [
                        [row_idx] * len(row) for row_idx, row in enumerate(self.trail_x)
                    ]
                    alpha = np.array(
                        [item for row in alpha for item in row], dtype=np.float64
                    )
                    norm = np.max(alpha) if np.max(alpha) > 0 else 1.0
                    alpha /= norm * 2
                else:
                    alpha = 0.5

                self.trail_stars.set_alpha(alpha)

                # store trail of stars (keep a maximum of self.trail_length)
                self.trail_x.append(sl.stars_fitted_x)
                self.trail_y.append(sl.stars_fitted_y)
                if len(self.trail_x) > self.trail_length:
                    self.trail_x.pop(0)
                    self.trail_y.pop(0)

            fitted_position_ra = sl.telescope_pointing_ra
            fitted_position_dec = sl.telescope_pointing_dec
            fitted_position_alt = sl.telescope_pointing_alt
            fitted_position_az = sl.telescope_pointing_az
            camera_rotation = sl.camera_rotation
            focal_length = sl.camera_focal_length

        # title and info box
        self.ax.set_title(f"Exposure (uuid={exposure.uuid})")
        box_text = f"""UTC: {exposure.start_time}
exposure duration: {exposure.duration}
RADec: ($\\alpha=${fitted_position_ra:.2f}, $\\delta=${fitted_position_dec:.2f})
AltAz: ($\\alpha=${fitted_position_az:.2f}, $\\delta=${fitted_position_alt:.2f})
rotation: {camera_rotation:.2f}
focal length: {focal_length.to(u.mm):.2f}"""
        self.exposure_text.set_text(box_text)

        return self.image

    def finish(self):
        self.animation.save(self.output_file)
        self.log.info("Shutting down.")


def main():
    tool = CreateMovieTool()
    tool.run()


if __name__ == "__main__":
    main()
