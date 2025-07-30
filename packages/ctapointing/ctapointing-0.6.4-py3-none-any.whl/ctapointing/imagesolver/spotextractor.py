import uuid
import numpy as np
import sep
from skimage.draw import polygon

from astropy.coordinates import SkyCoord
from astropy.time import Time
import astropy.units as u

from scipy.stats import norm
from scipy.spatial import KDTree

from ctapipe.core import Component
from ctapipe.core.traits import (
    Unicode,
    Float,
    Int,
    Bool,
)

from ctapointing.config import from_config
from .imagemask import ImageMask
from .spotlist import SpotList, SpotType


def gaussian_kernel(kernel_size, nsigma=3):
    """
    Gaussian smoothing kernel.
    """
    kernel_size = int(kernel_size)
    x = np.linspace(-nsigma, nsigma, kernel_size + 1)
    kernel1d = np.diff(norm.cdf(x))
    kernel2d = np.outer(kernel1d, kernel1d)

    return kernel2d / kernel2d.sum()


def tophat_kernel(kernel_size):
    """
    Top-hat smoothing kernel
    """
    kernel_size = int(kernel_size)

    kernel2d = np.zeros((kernel_size, kernel_size))
    centre = (kernel_size / 2.0, kernel_size / 2.0)

    Y, X = np.ogrid[:kernel_size, :kernel_size]
    dist_from_center = np.sqrt((X - centre[0]) ** 2 + (Y - centre[1]) ** 2)

    mask = dist_from_center <= kernel_size / 2
    kernel2d[mask] = 1.0

    return kernel2d


class SpotExtractor(Component):
    """
    Spot extractor component.

    Uses the sep ('sextractor') library for the extraction process.
    """

    uuid = Unicode(default_value=str(uuid.uuid4()), help="UUID of SpotExtractor").tag(
        config=True
    )
    name = Unicode(help="name of SpotExtractor").tag(config=True)
    detection_threshold = Float(help="spot detection threshold").tag(config=True)
    kernel_size = Int(help="smoothing kernel size").tag(config=True)
    use_tophat_kernel = Bool(
        default_value=False, help="use tophat instead of gaussian kernel"
    ).tag(config=True)
    min_spot_distance = Float(
        default_value=20, help="minimum spatial distance between spots"
    ).tag(config=True)
    image_mask_name = Unicode(
        default_value=None, help="filename of image mask", allow_none=True
    ).tag(config=True)
    image_dilation_radius = Int(
        default_value=10, help="mask dilation radius (pixels)"
    ).tag(config=True)
    image_erosion_radius = Int(
        default_value=10, help="mask erosion radius (pixels)"
    ).tag(config=True)

    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(config=config, parent=parent, **kwargs)

        # load image mask
        self.image_mask = None
        if self.image_mask_name is not None:
            self.image_mask = ImageMask.from_name(self.image_mask_name)

        self.spot_type = SpotType.UNKNOWN

    @classmethod
    def from_config(cls, **kwargs):
        """
        Read a SpotExtractor configuration from either configuration file or database.
        Either the path of a configuration file ('input_url') or a database collection
        ('collection') must be provided.


        Parameters
        ----------
        input_url: str or Path
            path of the configuration file.
        name: str
            name of the SpotExtractor (as in `SpotExtractor.name`).
            When loading the configuration from file, can be set to check that the configuration with the
            correct name is loaded.
            When loading from database, is used to identify the correct database record.
        uuid: str
            UUID of the camera (as in `SpotExtractor.uuid`).
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
        extractor: SpotExtractor object
        """
        # load configuration and construct instance
        config = from_config(component_name=cls.__name__, **kwargs)
        return cls(config=config)

    def process(self, exposure):
        image = exposure.image.astype(np.float32)

        self.log.debug("estimating image background")
        image_mask = self.image_mask.image if self.image_mask is not None else None
        background = sep.Background(image, mask=image_mask)
        thresh = self.detection_threshold * background.globalrms

        self.log.debug(
            "\tglobal mean of background: {:.1f} counts".format(background.globalback)
        )
        self.log.debug(
            "\tglobal rms of background:  {:.1f} counts".format(background.globalrms)
        )
        self.log.debug(
            "\tdetection threshold {:.1f} counts above mean background".format(thresh)
        )

        if self.use_tophat_kernel:
            kernel = tophat_kernel(self.kernel_size)
            self.log.debug("\tusing tophat kernel")
        else:
            kernel = gaussian_kernel(self.kernel_size)
            self.log.debug("\tusing gaussian kernel")

        self.log.debug("extracting spots")
        spots_extracted = sep.extract(
            image - background.back(),
            self.detection_threshold,
            err=background.globalrms,
            mask=image_mask,
            filter_kernel=kernel,
        )

        # order spot list by descending pixel content
        spots_extracted = np.sort(spots_extracted, order="flux")[::-1]

        data = np.array(
            [
                spots_extracted["y"],
                spots_extracted["x"],
                spots_extracted["y2"],
                spots_extracted["x2"],
                spots_extracted["xy"],
                spots_extracted["flux"],
                spots_extracted["peak"],
            ]
        ).T

        # correct spot position to match FITS convention
        data[:, 0] -= 0.5
        data[:, 1] -= 0.5

        # clip spot detected very close to the image edges
        # this seems to be needed at least for LED extraction due to
        # a possible bug in the sep extraction module (?)
        clip_mask = (
            (data[:, 0] > 5)
            & (data[:, 0] < exposure.image.shape[0] - 5)
            & (data[:, 1] > 5)
            & (data[:, 1] < exposure.image.shape[1] - 5)
        )
        data = data[clip_mask]

        # remove all pairs of spots which have a distance
        # of less than self.min_spot_distance.
        # This avoids problems in matching either of these
        # spots to stars.
        spot_tree1 = KDTree(data[:, 0:2])
        spot_tree2 = KDTree(data[:, 0:2])

        # only keep those spots for which there is only
        # one spot in their surrounding (which is the very same
        # spot).
        matches = spot_tree1.query_ball_tree(spot_tree2, r=self.min_spot_distance)

        spot_mask = np.array([len(m) - 1 for m in matches], dtype=np.bool_)
        data = data[~spot_mask]

        self.log.debug(
            f"removed {np.count_nonzero(spot_mask)} spots that are closer"
            f"to each other than min_spot_distance={self.min_spot_distance}."
        )

        # remove all spots that have been reconstructed within
        # the dilated image mask
        pixel_coords, _ = exposure.get_array_indexes(data[:, 0:2])
        if self.image_mask is not None:
            dilation_mask = self.image_mask.dilate(self.image_dilation_radius)[
                pixel_coords[:, 0].T, pixel_coords[:, 1].T
            ]
            data = data[~dilation_mask]

            self.log.debug(
                f"removed {np.count_nonzero(dilation_mask)} spots that are close"
                f"to edge of dilated image mask with dilation_radius={self.image_dilation_radius}."
            )

        # store the data in a SpotList container
        spotlist = SpotList()

        spotlist.coord_x = data[:, 0]
        spotlist.coord_y = data[:, 1]
        spotlist.var_x = data[:, 2]
        spotlist.var_y = data[:, 3]
        spotlist.cov_xy = data[:, 4]
        spotlist.flux = data[:, 5]
        spotlist.peak = data[:, 6]
        spotlist.spot_type = (
            np.ones_like(spotlist.coord_x, dtype=np.int64) * self.spot_type
        )
        spotlist.mean_background = background.globalback
        spotlist.rms_background = background.globalrms

        t = Time.now()
        t.format = "fits"
        spotlist.when_extracted = t.fits
        spotlist.image_uuid = str(exposure.uuid)
        spotlist.camera_uuid = str(exposure.camera.uuid)
        spotlist.extractor_uuid = str(self.uuid)
        spotlist.detection_threshold = self.detection_threshold
        spotlist.start_time = exposure.start_time
        spotlist.duration = exposure.duration

        # try to copy moon and sun positions
        try:
            spotlist.moon_position_alt = exposure.moon_position.alt
            spotlist.moon_position_az = exposure.moon_position.az
            spotlist.moon_phase = exposure.moon_phase
            spotlist.sun_position_alt = exposure.sun_position.alt
            spotlist.sun_position_az = exposure.sun_position.az
        except (TypeError, AttributeError):
            self.log.warning("no sun/moon position available from exposure")

        try:
            spotlist.chip_temperature = exposure.chip_temperature.to(
                u.K, equivalencies=u.temperature()
            )
        except AttributeError:
            self.log.warning("no chip temperature information available from exposure")

        try:
            spotlist.camera_temperature = exposure.camera_temperature.to(
                u.K, equivalencies=u.temperature()
            )
        except AttributeError:
            self.log.warning(
                "no camera temperature information available from exposure"
            )

        try:
            spotlist.camera_humidity = exposure.camera_humidity
        except AttributeError:
            self.log.warning("no humidity information available from exposure")

        self.log.info(f"extracted {len(data)} spots.")

        return spotlist

    def __str__(self):
        s = self.__repr__()
        return s

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(uuid={self.uuid}, name={self.name}, "
            f"detection_threshold={self.detection_threshold}, "
            f"image_mask={self.image_mask})"
        )


class SpotExtractorSky(SpotExtractor):
    """
    SpotExtractor for sky fields.
    """

    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(config=config, parent=parent, **kwargs)

        self.spot_type = SpotType.SKY


class SpotExtractorLED(SpotExtractor):
    """
    SpotExtractor for the camera LEDs
    """

    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(config=config, parent=parent, **kwargs)

        self.spot_type = SpotType.LED

    def generate_led_mask(self, exposure, science_camera, circle_radius=100):
        """
        Construct a mask that is suited for extracting the LED positions from an exposure image.

        The algorithm calculates, based on the hardware position of the LEDs in the science camera,
        the expected position of the LED spots in the exposure (taking into account the pointing camera
        parameters from the exposure object). It then constructs a circular mask around the LED positions.

        Parameters
        ----------
        exposure: ctapointing.exposure.Exposure
            exposure for which the mask shall be constructed
        science_camera: ctapointing.camera.ScienceCamera
            science camera object, the LED positions of which are used to create the LED mask
        circle_radius: int
            radius of circle around LED positions (pixels)
        """

        self.image_mask = ImageMask(inverted=False)
        self.image_mask._image = np.ones_like(exposure.image, dtype=bool)

        # transform LED positions from ScienceCameraFrame to image pixels
        led_positions_pix = exposure.transform_to_camera(
            science_camera.led_positions, to_pixels=True
        )

        yy, xx = np.meshgrid(
            np.arange(0, exposure.camera.num_pix[1]),
            np.arange(0, exposure.camera.num_pix[0]),
            sparse=True,
        )

        for pos in led_positions_pix:
            led_mask = np.hypot(xx - pos[0], (yy - pos[1])) < circle_radius
            self.image_mask._image[led_mask] = False


class SpotExtractorLid(SpotExtractor):
    """
    SpotExtractor for the camera lid
    """

    science_camera_name = Unicode(
        default_value="FlashCam", help="name of science camera"
    ).tag(config=True)

    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(config=config, parent=parent, **kwargs)

        self.spot_type = SpotType.LID

    def generate_lid_mask(self, exposure, science_camera):
        """
        Construct a mask that is suited for extracting the spots on the camera lid.

        It creates a circular masked region centred at the position of the science camera in the image,
        with a radius that corresponds to the physical radius of the lid (as stored in the
        `ctapointing.camera.ScienceCamera` class).

        Parameters
        ----------
        exposure: ctapointing.exposure.Exposure
            exposure for which the mask shall be constructed
        science_camera: ctapointing.camera.ScienceCamera
            science camera object, the lid radius of which are used to create the lid mask
        """

        self.image_mask = ImageMask(inverted=False)
        self.image_mask._image = np.ones_like(exposure.image, dtype=bool)

        phi = np.linspace(0, 2 * np.pi, 50)
        circle_coords = SkyCoord(
            np.cos(phi) * science_camera.lid_radius,
            np.sin(phi) * science_camera.lid_radius,
            frame=science_camera.sciencecameraframe,
        )
        circle_coords_pix = exposure.transform_to_camera(circle_coords, to_pixels=True)

        rr, cc = polygon(circle_coords_pix[:, 0], circle_coords_pix[:, 1])
        lid_mask = np.zeros(exposure.camera.num_pix, dtype=bool)
        lid_mask[rr, cc] = True
        self.image_mask._image[lid_mask] = False
