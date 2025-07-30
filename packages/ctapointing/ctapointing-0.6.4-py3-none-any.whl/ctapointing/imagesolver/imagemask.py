import logging
from pathlib import Path
import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion
from astropy.io import fits

from ctapointing.config import get_basedir

log = logging.getLogger(__name__)


class ImageMask:
    """
    Class that stores an image mask.
    """

    def __init__(self, inverted=True):
        self._image = None
        self.is_inverted = inverted
        self.filename = None

    @classmethod
    def from_name(cls, filename: str or Path, inverted=True, **kwargs):
        """
        Read a ImageMask config from either file or database.

        Parameters
        ----------
        filename: str
            filename of the mask fits file

        kwargs: arguments forwarded to ImageMask.read_mask_from_fits()

        Returns
        -------
        mask: ImageMask object
        """

        mask = cls(inverted=inverted)
        mask.read_mask_from_fits(filename, **kwargs)

        return mask

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.__class__.__name__} (filename={self.filename}, is_inverted={self.is_inverted})"

    @property
    def image(self):
        if self._image is None:
            return None

        return ~self._image if self.is_inverted else self._image

    def read_mask_from_fits(self, input_url: str or Path, **kwargs) -> None:
        """
        Read image mask from FITS file.
        By default, the mask is flipped on the vertical axis, since this is the
        standard for the real images.

        Parameters
        ----------
        input_url: str or Path
            path to the FITS file
        swap_y: bool
            flag to mirror mask along y-axis (default True)
        """

        swap_y = kwargs.get("swap_y", True)
        input_url = Path(input_url)

        if not input_url.is_file():
            log.info(f"mask file {input_url} does not exist.")
            input_url = get_basedir() / "data/masks" / input_url.name
            log.info(f"trying {input_url}...")
            if not input_url.is_file():
                raise FileNotFoundError(f"mask file {input_url} does not exist.")

        try:
            with fits.open(input_url) as hdu_list:
                data = hdu_list[0].data
        except Exception as e:
            log.error(f"ImageMask: error reading mask image from file {input_url}: {e}")
            raise e

        self.filename = input_url

        if swap_y:
            data = np.flip(data, axis=1)

        # convert to boolean array
        mask = data == 0
        self._image = np.where(mask, False, True)

    def estimate_masked_area(self):
        """
        Estimate the area masked by the mask, relative to the FoV of the image.
        """
        if self.image is not None:
            return np.count_nonzero(self.image) / self.image.size

        return None

    def dilate(self, dilation_radius: int) -> np.array or None:
        """
        Dilate the mask using a (num_pixels x num_pixels) quadratic kernel.

        Parameters
        ----------
        dilation_radius: float
            dilation radius

        Returns
        -------
        image_dilated: np.array or None
            dilated image
        """
        image_dilated = None

        if self.image is not None:
            kernel = np.ones([dilation_radius] * 2)
            image_dilated = binary_dilation(self.image, structure=kernel)

        return image_dilated

    def erode(self, erosion_radius: int) -> np.array or None:
        """
        Return erosion of mask using a (num_pix x num_pix) quadratic kernel.

        Parameters
        ----------
        erosion_radius: float
            erosion radius

        Returns
        -------
        image_eroded: np.array or None
            erosion of mask image
        """
        image_eroded = None

        if self.image is not None:
            kernel = np.ones([erosion_radius] * 2)
            image_eroded = binary_erosion(self.image, structure=kernel)

        return image_eroded
