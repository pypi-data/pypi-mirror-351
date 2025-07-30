import os
import re
import uuid
import logging

import numpy as np

from astropy.time import Time
from astropy import units as u
from astropy.coordinates import SkyCoord, AltAz, Angle, ICRS, get_body
from astropy.io import fits

from ctapointing.exposure.exposure_container import ExposureContainer

from ctapointing.coordinates import SkyCameraFrame
from ctapointing.camera import PointingCamera

DTYPES = {8: np.uint8, 16: np.uint16, 32: np.uint32}  # supported bit depths

log = logging.getLogger(__name__)


class SimulationInfo:
    """
    Meta data class for simulated images.

    Stores simulation information about the simulated image, such as true RADec position
    of the centre of the simulated exposure, minimum and maximum magnitude of stars simulated,
    whether or not noise/moonlight have been simulated.
    """

    def __init__(self):
        self.time_step = None
        self.min_mag = None
        self.max_mag = None
        self.fov = None

        self.unsharp_radius = None  # radius for spot smearing
        self.num_unsharp_rays = None  # number of rays for spot smearing

        self.has_noise = None  # has noise applied
        self.has_moonlight = None  # has moonlight applied

        self.stars = None  # list of simulated stars

        self.magnitudes = None  # magnitudes of simulated stars
        self.coords_radec = None  # RADec coordinates of star field
        self.coords_altaz_meanexp = None  # AltAz coordinates at mean exposure
        self.coords_chip_meanexp = None  # chip coordinates at mean exposure
        self.coords_pix_meanexp = None  # pixel cooordinates at mean exposure


class Exposure:
    """
    Class holding a PointingCamera image, including meta information
    such as telescope pointing and image meta data.

    While a new ``Exposure`` object can be directly instantiated by calling the
    constructor, the more frequent use cases are

    * construction by reading an image from database and file, using the ``Exposure.from_name()`` method
    * construction by simulation, using the ``ctapointing.exposure.ExposureSimulator``.

    See tutorials to learn about frequent use cases.

    ``Exposure`` supports low-level image reading from and writing to FITS files through the methods
    ``Exposure.read_from_fits()`` and ``Exposure.write_to_fits()``.

    """

    def __init__(self, is_simulated=False):
        self._uuid = str(uuid.uuid4())

        self.is_simulated = is_simulated
        self.image_filename = None
        self.start_time = None
        self.duration = None
        self.nominal_telescope_pointing = None  # nominal RADec telescope pointing
        self.telescope_pointing = None  # RADec telescope pointing

        self.chip_temperature = (
            0.0 * u.deg_C  # recorded chip temperature (Astropy.Quantity[temperature])
        )
        self.camera_temperature = (
            0.0
            * u.deg_C  # recorded camera housing temperature (Astropy.Quantity[temperature])
        )
        self.camera_humidity = 0.0  # recorded camera housing humidity (float)
        self.camera_pressure = (
            0.0 * u.hPa
        )  # recorded camera housing pressure (Astropy.Quantity[pressure])
        self.camera_gain = None  #: camera gain (float)
        self.camera_uuid = None  # camera uuid (str)

        self.ambient_temperature = (
            None  # ambient temperature (Astropy.Quantity[temperature])
        )
        self.ambient_pressure = (
            None  # ambient atmospheric pressure (Astropy.Quantity[pressure])
        )

        self.camera = None  # camera used for the exposure
        self.image = None  # resulting image

        self.simulation_info = SimulationInfo() if is_simulated else None

    def __str__(self):
        s = f"Exposure (uuid={self.uuid})\n"
        s += f"  img filename:    {self.image_filename}\n"
        try:
            s += f"  start time:      {self.start_time.fits}\n"
        except AttributeError:
            s += f"  start time:      {self.start_time}\n"
        s += f"  duration:        {self.duration}\n"
        s += f"  pressure:        {self.ambient_pressure}\n"
        s += f"  chip temp:       {self.chip_temperature}\n"
        s += f"  ambient temp:    {self.ambient_temperature}\n"
        s += f"  camera temp:     {self.camera_temperature}\n"
        s += f"  camera humidity: {self.camera_humidity}\n"
        s += f"  camera pressure: {self.camera_pressure}\n"
        s += f"  camera gain:     {self.camera_gain}\n"
        s += f"  camera uuid:   {self.camera_uuid}\n"

        s += "Exposure Pointing:\n"
        s += f"  telescope_pointing: {self.telescope_pointing}\n"
        s += f"  nominal_telescope_pointing: {self.nominal_telescope_pointing}\n"

        try:
            s += "Pixel quantiles:\n"
            q = np.array([0.05, 0.32, 0.5, 0.68, 0.95, 0.99])
            n = np.quantile(self.image, q)

            s += f"  min: {np.min(self.image):>5}\n"
            for _q, _n in zip(q, n):
                s += f"  q{_q * 100:>02g}: {_n:>5g}\n"
            s += f"  max: {np.max(self.image):>5}\n"
        except TypeError:
            pass

        if self.simulation_info is not None:
            sim = self.simulation_info
            s += "\n  SimulationInfo:\n"
            s += "    time step: {}".format(sim.time_step) + "\n"
            s += "    min mag: {}".format(sim.min_mag) + "\n"
            s += "    max mag: {}".format(sim.max_mag) + "\n"
            s += "    fov: {}".format(sim.fov) + "\n"

        return s

    def __repr__(self):
        return f"{self.__class__.__name__}(uuid: {self.uuid}, img filename: {self.image_filename})"

    @property
    def uuid(self):
        """
        Return UUID of the exposure.
        """
        return self._uuid

    @property
    def altazframe(self):
        """
        Return AltAz coordinate frame, using currently available meta information.
        """
        try:
            location = self.camera.location
        except AttributeError:
            location = None

        return AltAz(
            obstime=self.mean_exposure_time,
            location=location,
            pressure=self.ambient_pressure,
            temperature=self.ambient_temperature,
        )

    @property
    def skycameraframe(self):
        """
        Return a SkyCameraFrame object, initialised from current
        exposure (observation time, location, telescope pointing)
        and camera (focal length, rotations, tilts etc.) properties.

        Can be used to transform from/to SkyCameraFrame using
        up-to-date transformation parameters.
        """
        try:
            return SkyCameraFrame(
                focal_length=self.camera.focal_length[0],
                rotation=self.camera.rotation,
                tilt_x=self.camera.tilt[0],
                tilt_y=self.camera.tilt[1],
                offset_x=self.camera.offset[0],
                offset_y=self.camera.offset[1],
                obstime=self.mean_exposure_time,
                location=self.camera.location,
                telescope_pointing=self.telescope_pointing_altaz,
                pressure=self.ambient_pressure,
                temperature=self.ambient_temperature,
            )
        except Exception as e:
            log.error(e)
            return None

    @property
    def mean_exposure_time(self):
        """
        Return time of mean exposure of image.
        """
        try:
            return self.start_time + self.duration / 2
        except Exception as e:
            log.warning(e)
            return None

    @property
    def telescope_pointing_altaz(self):
        """
        Return AltAz telescope pointing, i.e. the telescope orientation
        at the time of mean exposure.
        """
        try:
            return self.telescope_pointing.transform_to(self.altazframe)
        except Exception as e:
            return None

    @property
    def sun_position(self):
        """
        Return Sun's AltAz position at mean exposure time
        """
        try:
            sun = get_body("sun", self.mean_exposure_time)
            return sun.transform_to(self.altazframe)
        except Exception as e:
            log.warning(e)
            return None

    @property
    def moon_position(self):
        """
        Return Moon's AltAz position at mean exposure time

        Returns
        -------
        Moon's position in AltAz frame (SkyCoord)
        """
        try:
            moon = get_body("moon", self.mean_exposure_time)
            return moon.transform_to(self.altazframe)
        except Exception as e:
            log.warning(e)
            return None

    @property
    def moon_phase(self):
        """
        Return Moon's phase at mean exposure time

        Returns
        -------
        Moon phase (float)
        """
        try:
            moon = get_body("moon", self.mean_exposure_time)
            sun = get_body("sun", self.mean_exposure_time)
            moon_phase = (Angle(180.0 * u.deg) - moon.separation(sun)).to_value(u.rad)
            return np.cos(moon_phase / 2)
        except Exception as e:
            log.warning(e)
            return None

    @classmethod
    def from_name(
        cls,
        name,
        **kwargs,
    ):
        """
        Construct an instance by reading the image information from the database
        or directly from the FITS file.

        Parameters
        ----------
        name: str
            image filename in case of reading image directly from file, UUID in case
            of reading from container/database
        **kwargs:
            see below

        Keyword Arguments
        -----------------
        load_image: bool
            load image pixel data (defaults to True)
        load_camera: bool
            load camera data from database (defaults to True)
        read_meta_from_fits:
            read meta-data (exposure time, location etc) directly from image FITS header (defaults to False)
        swap_y:
            swap `y` coordinate of pixel data (defaults to False)

        Returns
        -------
        exposure: Exposure object
            instance of Exposure object
        """

        load_image = kwargs.pop("load_image", True)
        load_camera = kwargs.pop("load_camera", True)
        read_meta_from_fits = kwargs.get("read_meta_from_fits", False)

        # if reading meta information from FITS file is requested,
        # load exposure from FITS
        if read_meta_from_fits:
            exposure = Exposure()
            exposure.image_filename = name

            success = exposure.read_from_fits(name=exposure.image_filename, **kwargs)

            if success:
                return exposure
            else:
                return None

        # otherwise try to load exposure via ExposureContainer
        container = ExposureContainer.from_name(name, **kwargs)

        if container is None:
            return None

        exposure = Exposure.from_container(container)

        # image from FITS file. If requested, try to also read meta info
        if load_image:
            log.debug(f"reading image from file {exposure.image_filename}")
            exposure.read_from_fits(name=exposure.image_filename, **kwargs)

        # read camera information
        if load_camera:
            log.debug(f"loading camera {exposure.camera_uuid}")
            exposure.camera = PointingCamera.from_config(
                uuid=exposure.camera_uuid,
                database="camera_config",
                collection="test_component",
            )
            log.debug(exposure.camera)

        return exposure

    def to_container(self, prefix=None):
        """
        Write exposure image information to a `ctapipe.core.Container` for file or database storage.

        Parameters
        ----------
        prefix: str or None (default to None)
            `prefix` passed to `ctapipe.core.Container`

        Returns
        -------
        exposure_container: ctapipe.core.Container
            instance of exposure container
        """

        data = {
            "uuid": str(self.uuid),
            "image_filename": self.image_filename,
            "start_time": self.start_time,
            "duration": self.duration,
        }

        try:
            data["nominal_telescope_pointing_ra"] = self.nominal_telescope_pointing.ra
            data["nominal_telescope_pointing_dec"] = self.nominal_telescope_pointing.dec
        except AttributeError:
            pass

        try:
            data["telescope_pointing_ra"] = self.telescope_pointing.ra
            data["telescope_pointing_dec"] = self.telescope_pointing.dec
        except AttributeError:
            pass

        # manually transform temperatures to Kelvin, as only Kelvin supported by
        # `ctapipe.io.TableWriter` and no astropy transformation exists
        try:
            unit = self.chip_temperature.unit.to_string()
            if unit == "deg_C":
                data["chip_temperature"] = (self.chip_temperature.value + 273.15) * u.K
            elif unit == "K":
                data["chip_temperature"] = self.chip_temperature
        except AttributeError:
            pass

        try:
            unit = self.camera_temperature.unit.to_string()
            if unit == "deg_C":
                data["camera_temperature"] = (
                    self.camera_temperature.value + 273.15
                ) * u.K
            elif unit == "K":
                data["camera_temperature"] = self.camera_temperature
        except AttributeError:
            pass

        data["camera_humidity"] = self.camera_humidity
        data["camera_pressure"] = self.camera_pressure
        data["camera_gain"] = self.camera_gain

        try:
            unit = self.ambient_temperature.unit.to_string()
            if unit == "deg_C":
                data["ambient_temperature"] = (
                    self.ambient_temperature.value + 273.15
                ) * u.K
            elif unit == "K":
                data["ambient_temperature"] = self.ambient_temperature
        except AttributeError:
            pass

        data["ambient_pressure"] = self.ambient_pressure
        data["is_simulated"] = self.is_simulated
        try:
            data["camera_uuid"] = self.camera.uuid
        except AttributeError:
            data["camera_uuid"] = self.camera_uuid

        try:
            data["moon_position_az"] = self.moon_position.az
            data["moon_position_alt"] = self.moon_position.alt
        except (TypeError, AttributeError):
            pass
        data["moon_phase"] = self.moon_phase

        try:
            data["sun_position_az"] = self.sun_position.az
            data["sun_position_alt"] = self.sun_position.alt
        except (TypeError, AttributeError):
            pass

        exposure_container = ExposureContainer(prefix=prefix, **data)
        return exposure_container

    @classmethod
    def from_container(
        cls,
        container,
    ):  # TODO loading of moon and sun position doesnt work
        """
        Construct Exposure object from an ExposureContainer

        Parameters
        ----------
        Container: ctapointing.exposure.ExposureContainer
            instance of ExposureContainer from which exposure is filled

        Returns
        -------
        exposure: Exposure object
            exposure object
        """

        if not isinstance(container, ExposureContainer):
            return None

        # create instance
        exposure = cls()

        # copy data
        exposure._uuid = container.uuid
        exposure.image_filename = container.image_filename

        # convert times to UTC if needed
        try:
            exposure.start_time = Time(container.start_time, scale="utc", format="fits")
        except (TypeError, AttributeError, ValueError):
            exposure.start_time = None

        exposure.duration = container.duration

        try:
            exposure.nominal_telescope_pointing = SkyCoord(
                ra=container.nominal_telescope_pointing_ra,
                dec=container.nominal_telescope_pointing_dec,
                frame=ICRS,
            )
        except (TypeError, AttributeError):
            exposure.nominal_telescope_pointing = None

        try:
            exposure.telescope_pointing = SkyCoord(
                ra=container.telescope_pointing_ra,
                dec=container.telescope_pointing_dec,
                frame=ICRS,
            )
        except (TypeError, AttributeError):
            exposure.telescope_pointing = None

        # manually transform temperatures to deg_C, as only Kelvin supported by
        # `ctapipe.io.TableWriter` and no astropy transformation exists
        try:
            exposure.chip_temperature = (
                container.chip_temperature.value - 273.15
            ) * u.deg_C
        except AttributeError:
            exposure.chip_temperature = None
        try:
            exposure.camera_temperature = (
                container.camera_temperature.value - 273.15
            ) * u.deg_C
        except AttributeError:
            exposure.camera_temperature = None
        try:
            exposure.ambient_temperature = (
                container.ambient_temperature.value - 273.15
            ) * u.deg_C
        except AttributeError:
            exposure.ambient_temperature = None

        exposure.camera_humidity = container.camera_humidity
        exposure.camera_pressure = container.camera_pressure
        exposure.camera_gain = container.camera_gain
        exposure.ambient_pressure = container.ambient_pressure
        exposure.is_simulated = container.is_simulated
        exposure.camera_uuid = container.camera_uuid

        return exposure

    @property
    def camera_pointing(self):
        """
        Calculate sky coordinates of the camera centre, using actual
        telescope pointing and SkyCameraFrame parameters.

        .. caution::
            Coincides with the telescope pointing position only if the camera
            is not tilted against the optical axis of the telescope

        Returns
        -------
        camera_centre: SkyCoord
            camera centre in the ICRS frame
        """
        camera_centre = SkyCoord(0.0 * u.m, 0.0 * u.m, self.skycameraframe)

        return camera_centre.transform_to(ICRS)[0]

    def transform_to_camera(self, coords, to_pixels=False):
        """
        Project a given sky coordinate into the CCD chip.
        Takes current camera orientation, camera intrinsic parameters and
        distortions into account.

        Parameters
        ----------
        coords: SkyCoord
            sky coordinate (ICRS or AltAz)
        to_pixels: bool
            True: convert to camera pixels
            False: convert to SkyCamera coordinates

        Returns
        -------
        coords: SkyCoord in SkyCameraFrame or array of pixel coordinates
        """
        coords_skycam = coords.transform_to(self.skycameraframe)

        if to_pixels:
            return self.camera.transform_to_pixels(coords_skycam)

        return coords_skycam

    def transform_to_sky(self, coords, update_skyframe=True):
        """
        Project a given array of SkyCameraFrame coordinates to ICRS.
        Takes current camera orientation, camera intrinsic parameters and
        distortions into account.

        If `update_skyframe` is True, all SkyCameraFrame parameters that
        are internally stored in `coords` will be updated by the ones
        stored in this exposure object (only modifying the coordinate frame's
        meta information, not the coordinate values themselves).

        Parameters
        ----------
        coords: SkyCoord
            coordinates in SkyCameraFrame system
        update_skyframe: bool
            update coordinates with current SkyCameraFrame parameters

        Returns
        -------
        SkyCoord in ICRS system
        """

        if update_skyframe:
            coords_updated = SkyCoord(coords.x, coords.y, frame=self.skycameraframe)
            return coords_updated.transform_to(ICRS)

        return coords.transform_to(ICRS)

    def create_empty_image(self):
        """
        Create an empty image.
        """
        try:
            self.image = np.zeros(shape=self.camera.num_pix)
        except AttributeError:
            log.error(
                "Exposure object must provide a valid camera in order to create an image."
            )
            raise AttributeError

        # convert to proper bit depth
        dtype = DTYPES[self.camera.bit_depth]
        self.image = self.image.astype(dtype)

    def get_array_indexes(self, coords: np.ndarray):
        """
        Return internal numpy array indexes that represent given pixel coordinates

        Parameters
        ----------
        coords: numpy.ndarray
            2D array of pixel coordinates

        Returns
        -------
        (pixel_coords, mask): tuple of numpy.ndarray
            internal pixel coordinates and mask indicating valid (on-chip) pixel coordinates
        """

        # convert coordinates to array indices
        # use FITS convention whereby pixel 0 is represented by coordinates in between [-0.5, 0.5]
        x, y = np.transpose(coords)
        x = np.array(x + 0.5, dtype=np.uint)
        y = np.array(y + 0.5, dtype=np.uint)

        # mask all coordinates that do not fall onto chip as "nan"
        mask = self.camera.clip_to_chip(coords)

        pixel_coords = np.concatenate((x.reshape(-1, 1), y.reshape(-1, 1)), axis=1)
        return pixel_coords, mask

    def get_intensity(self, coords: np.ndarray):
        """
        Return the intensity value stored in the image at the particular coordinates

        Parameters
        ----------
        coords: numpy.ndarray
            2D array of pixel coordinates

        Returns
        -------
        intensity: numpy.ndarray
            pixel intensities at given coordinates
        """

        # convert coordinates to array indices
        indexes, mask = self.get_array_indexes(coords)
        x = indexes[:, 0]
        y = indexes[:, 1]

        # initialise intensity array
        # set intensities for coordinates outside chip to "nan"
        try:
            intensity = np.zeros(len(coords))
            intensity[~mask] = np.nan

            intensity[mask] = self.image[x[mask], y[mask]]

        except TypeError:
            return None

        return intensity

    def set_intensity(
        self, coords: np.ndarray, intensities: np.ndarray or list or float or int
    ):
        """
        Set image intensity at coordinates `coords` to values `intensity`

        Parameters
        ----------
        coords: numpy.ndarray
            2D array of pixel coordinates
        intensities: numpy.ndarray or list, float, int
            1D array of intensities or single intensity value
        """

        if isinstance(intensities, list):
            intensities = np.array(list)
        elif isinstance(intensities, (float, int)):
            intensities = np.array([intensities] * len(coords))

        # convert coordinates to array indices
        pixel_coords, mask = self.get_array_indexes(coords)

        # initialise intensity array
        # set intensities for coordinates outside chip to "nan"
        self.image[pixel_coords[mask][:, 0], pixel_coords[mask][:, 1]] = intensities[
            mask
        ]

    def read_from_fits(self, name=None, **kwargs):
        """
        Read image data from FITS file.
        The image can be flipped on the vertical axis, since this is
        standard for the real images.

        Recursive search is possible, e.g. to search subdirectories of
        image_path.
        """

        swap_y = kwargs.get("swap_y", False)
        read_meta_from_fits = kwargs.get("read_meta_from_fits", False)
        image_path = kwargs.get("image_path", None)

        fullname = None
        if name is None:
            # try to set filename from attribute
            if self.image_filename is None:
                log.error("no filename given and Exposure.image_filename not set.")
                return False

            name = self.image_filename

        search_dirs = ["."]

        # full path name used?
        if os.path.isfile(name):
            fullname = name
        else:
            if image_path is not None and os.path.isdir(image_path):
                search_dirs.append(image_path)

            for d in search_dirs:
                for root, _, files in os.walk(d):
                    for filename in files:
                        name_string = r"^" + name + r".*fits.gz$"
                        name_match = re.search(name_string, filename)
                        fullname_string = r"^" + name
                        fullname_match = re.search(fullname_string, filename)
                        uuid_string = r".*" + name + r".*fits.gz$"
                        uuid_match = re.search(uuid_string, filename)
                        if name_match or fullname_match or uuid_match:
                            fullname = os.path.join(root, filename)
                            break

        if fullname is None:
            log.error(f"could not find image {name} on search paths {search_dirs}")
            return False

        log.debug(f"loading image from {fullname}")
        try:
            with fits.open(fullname) as hdu_list:
                data = hdu_list[0].data
                header = hdu_list[0].header

                if swap_y:
                    self.image = np.flip(data, axis=1)
                else:
                    self.image = data

                # load image meta information
                if read_meta_from_fits:
                    self._uuid = header["UUID"]

                    # camera parameters
                    self.camera = PointingCamera()
                    try:
                        self.camera.name = header["CAMERA"]
                    except Exception as e:
                        log.warning(e)
                        self.camera.name = None
                    try:
                        self.camera_uuid = header["CAMUUID"]
                    except Exception as e:
                        try:
                            self.camera_uuid = header["CAMERAID"]
                        except Exception as e:
                            self.camera_uuid = None
                    try:
                        self.camera.f_stop = header["F-NUMBER"]
                    except Exception as e:
                        self.camera.f_stop = -1.0

                    try:
                        self.camera.num_pix = [header["NAXIS2"], header["NAXIS1"]]
                    except Exception as e:
                        log.warning(e)
                        self.camera.num_pix = None

                    # exposure start time: try both time string and unix time
                    try:
                        self.start_time = Time(header["EXPSTART"])
                    except Exception as e:
                        try:
                            self.start_time = Time(
                                float(header["EXPSTART"]), format="unix"
                            )
                            self.start_time.format = "fits"
                        except Exception as e:
                            log.warning(e)
                            self.start_time = None
                    # duration and temperature
                    try:
                        self.duration = header["EXPOSURE"] * u.s
                    except Exception as e:
                        log.warning(e)
                        self.duration = None
                    try:
                        self.chip_temperature = header["TEMP"] * u.deg_C
                    except Exception as e:
                        try:
                            self.chip_temperature = header["CHIPTEMP"] * u.deg_C
                        except Exception as e:
                            self.chip_temperature = None
                    try:
                        self.camera_temperature = header["ENVTEMP"] * u.deg_C
                    except Exception as e:
                        try:
                            self.camera_temperature = header["CAMTEMP"] * u.deg_C
                        except Exception as e:
                            self.camera_temperature = None
                    try:
                        self.camera_humidity = header["ENVHUMR"]
                    except Exception as e:
                        try:
                            self.camera_humidity = header["CAMHUM"]
                        except Exception as e:
                            self.camera_humidity = None
                    try:
                        self.camera_pressure = header["CAMPRESS"] * u.hPa
                    except Exception as e:
                        self.camera_pressure = None
                    try:
                        self.camera_gain = header["GAIN"]
                    except Exception as e:
                        self.camera_gain = None
                    try:
                        self.is_simulated = header["SIM"]
                    except Exception as e:
                        self.is_simulated = False

                    try:
                        pointing_ra = Angle(header["CRVAL1"] * u.deg)
                        pointing_dec = Angle(header["CRVAL2"] * u.deg)
                        self.nominal_telescope_pointing = SkyCoord(
                            pointing_ra, pointing_dec, frame=ICRS
                        )
                    except Exception as e:
                        self.nominal_telescope_pointing = None

        except Exception as e:
            log.error(f"error reading image from file {fullname}: {e}")
            self.image = None
            return False

        return True

    def write_to_fits(self, filename, **kwargs):
        """
        Write the image data to FITS file, with appropriate meta information.
        The image can be flipped on the vertical axis, since this is
        standard for the real images.

        Parameters
        ----------
        filename: str
            image file name (including full path)
        """

        wcs = kwargs.get("wcs", None)
        swap_y = kwargs.get("swap_y", False)
        force_overwrite = kwargs.get("force_overwrite", False)
        write_camera_info = kwargs.get("write_camera_info", True)
        get_wcs_from_camera = kwargs.get("get_wcs_from_camera", True)

        if os.path.exists(filename) and not force_overwrite:
            raise FileExistsError(
                f"File {filename} already exists and force_overwrite=False"
            )

        # convert to plain array and flip if needed
        data = np.array(self.image)
        if swap_y:
            data = np.flip(data, axis=1)

        try:
            header = wcs.to_header(relax=True)
        except Exception as e:
            header = None

        hdu = fits.PrimaryHDU(data, header)

        header = hdu.header

        header["UUID"] = str(self.uuid)

        header["BSCALE"] = 1  # default scaling factor
        header["BZERO"] = 32768  # offset data range to that of unsigned short

        try:
            header["EXPOSURE"] = self.duration.to("s").value  # exposure time
        except (TypeError, AttributeError):
            header["EXPOSURE"] = None
        try:
            header["CHIPTEMP"] = self.chip_temperature.to(
                "deg_C"
            ).value  # chip temperature
        except (TypeError, AttributeError) as e:
            header["CHIPTEMP"] = None
        try:
            header["CAMTEMP"] = self.camera_temperature.to(
                "deg_C"
            ).value  # camera temperature
        except (TypeError, AttributeError):
            header["CAMTEMP"] = None

        header["CAMHUM"] = self.camera_humidity
        try:
            header["CAMPRESS"] = self.camera_pressure.to("hPa").value
        except (TypeError, AttributeError) as e:
            header["CAMPRESS"] = None

        header["GAIN"] = self.camera_gain
        header["F-NUMBER"] = self.camera.f_stop

        self.start_time.format = "fits"
        header["EXPSTART"] = self.start_time.value

        file_date = Time.now()
        file_date.format = "fits"
        header["DATE"] = file_date.value

        if write_camera_info:
            header["CAMERA"] = self.camera.name
            header["CAMERAID"] = self.camera.uuid
            header.comments["CAMERA"] = "Camera name"
            header.comments["CAMERAID"] = "Camera UUID"

        try:
            if wcs is None and get_wcs_from_camera:
                header["WCSAXES"] = 2

                # WCS in simulated coordinates
                header["CTYPE1"] = "RA---TAN"
                header["CTYPE2"] = "DEC--TAN"
                header["LONPOLE"] = 180.0
                header["LATPOLE"] = 0.0
                header["RADESYS"] = "ICRS"

                # \todo this assumes that the camera optical axis is aligned to the nominal telescope pointing
                header["CRVAL1"] = self.nominal_telescope_pointing.ra.to_value(
                    u.deg
                )  # self.camera_pointing.ra.to_value(u.deg)
                header["CRVAL2"] = self.nominal_telescope_pointing.dec.to_value(
                    u.deg
                )  # self.camera_pointing.dec.to_value(u.deg)
                header["CRPIX1"] = self.camera.chip_centre[1]
                header["CRPIX2"] = self.camera.chip_centre[0]

                # pixel to WCS transformation matrix, not including FoV distortions
                # (see Greisen & Calabretta, A&A 395, 1061–1075 (2002))
                # in our case, ignoring 2nd order effects, this is the matrix which scales from
                # pixels to degrees on the sky and rotates the altaz coordinate system to RADec.
                header["CUNIT1"] = "deg"
                header["CUNIT2"] = "deg"

                # calculate rotation matrix
                # for this, take a small distance along RA, transform to altaz, and determine the
                # rotation between the two
                # \todo currently assumes that the CCD is aligned to the telescope optical axis
                t = self.camera_pointing
                td = SkyCoord(ra=t.ra + 0.01 * u.deg, dec=t.dec, frame=t.frame)

                # transform for the average exposure time
                altaz = AltAz(
                    obstime=self.start_time + self.duration / 2,
                    location=self.camera.location,
                )
                t_altaz = t.transform_to(altaz)
                td_altaz = td.transform_to(altaz)

                angle_td = td.position_angle(t)
                angle_td_altaz = td_altaz.position_angle(t_altaz)

                # take intrinsic camera rotation w.r.t. horizon into account
                rot_angle = (
                    (angle_td - angle_td_altaz - self.camera.rotation).to("rad").value
                )

                scale = (
                    (self.camera.pixel_size / self.camera.focal_length[0])
                    .decompose()
                    .value
                )
                scale = np.rad2deg(scale)

                if swap_y:
                    # flipped case
                    header["CD1_1"] = -np.cos(rot_angle) * scale
                    header["CD1_2"] = np.sin(rot_angle) * scale
                    header["CD2_1"] = -np.sin(rot_angle) * scale
                    header["CD2_2"] = -np.cos(rot_angle) * scale
                else:
                    header["CD1_1"] = np.cos(rot_angle) * scale
                    header["CD1_2"] = np.sin(rot_angle) * scale
                    header["CD2_1"] = np.sin(rot_angle) * scale
                    header["CD2_2"] = -np.cos(rot_angle) * scale

                header.comments["CD1_1"] = "Transformation matrix"
                header.comments["CRVAL1"] = "RA of reference point"
                header.comments["CRVAL2"] = "DEC of reference point"
                header.comments["CRPIX1"] = "X reference pixel"
                header.comments["CRPIX2"] = "Y reference pixel"
                header.comments["CUNIT1"] = "X pixel scale units"
                header.comments["CUNIT2"] = "Y pixel scale units"

                header.comments["CTYPE1"] = "TAN (gnomic) projection"
                header.comments["CTYPE2"] = "TAN (gnomic) projection"

        except Exception as e:
            log.warning(
                f"Failed to calculate WCS information from camera configuration.: {e}"
            )

        header.comments["NAXIS1"] = "length of data axis 1"
        header.comments["NAXIS2"] = "length of data axis 2"

        header.comments["BSCALE"] = "default scaling factor"
        header.comments["BZERO"] = "offset data range to that of unsigned short"
        header.comments["EXPOSURE"] = "total exposure time (sec)"
        header.comments["CHIPTEMP"] = "CCD temperature (degC)"
        header.comments["CAMTEMP"] = "temperature measured in housing (degC)"
        header.comments["CAMHUM"] = "rel humidity measured in housing"
        header.comments["CAMPRESS"] = "pressure measured in housing"
        header.comments["GAIN"] = "pixel gain"
        header.comments["F-NUMBER"] = "aperture f-number"
        header.comments["EXPSTART"] = "start of exposure (UTC)"
        header.comments["DATE"] = "file creation date (UTC)"

        if self.is_simulated:
            try:
                header["SIM"] = 1
                header["SIM_RA"] = self.telescope_pointing.ra.to_value(u.deg)
                header["SIM_DEC"] = self.telescope_pointing.dec.to_value(u.deg)
                header["SIM_ROT"] = self.camera.rotation.to_value(u.deg)
                header["SIM_FL"] = self.camera.focal_length[0].to_value(u.m)
                header["SIM_TX"] = self.camera.tilt[0].to_value(u.deg)
                header["SIM_TY"] = self.camera.tilt[1].to_value(u.deg)
                header["SIM_OX"] = self.camera.offset[0].to_value(u.m)
                header["SIM_OY"] = self.camera.offset[1].to_value(u.m)
                header["SIM_STEP"] = self.simulation_info.time_step.to_value(u.s)
                header["SIM_MINM"] = self.simulation_info.min_mag
                header["SIM_MAXM"] = self.simulation_info.max_mag
                header["SIM_URAD"] = self.simulation_info.unsharp_radius.to_value(
                    u.arcsec
                )
                header["SIM_URAY"] = self.simulation_info.num_unsharp_rays
                header["SIM_NOIS"] = self.simulation_info.has_noise
                header["SIM_MOON"] = self.simulation_info.has_moonlight

                header.comments["SIM"] = "simulated image?"
                header.comments["SIM_RA"] = "simulated RA of pointing (deg)"
                header.comments["SIM_DEC"] = "simulated DEC of pointing (deg)"
                header.comments["SIM_ROT"] = "simulated rotation of camera (deg)"
                header.comments["SIM_FL"] = "simulated focal length (m)"
                header.comments["SIM_TX"] = "simulated camera tilt X (deg)"
                header.comments["SIM_TY"] = "simulated camera tilt Y (deg)"
                header.comments["SIM_OX"] = "simulated camera offset X (m)"
                header.comments["SIM_OY"] = "simulated camera offset Y (m)"
                header.comments["SIM_STEP"] = "simulated time step (s)"
                header.comments["SIM_MINM"] = "simulated min magnitude"
                header.comments["SIM_MAXM"] = "simulated max magnitude"
                header.comments["SIM_URAD"] = "simulated unsharp radius (pix)"
                header.comments["SIM_URAY"] = "simulated number of smearing rays"
                header.comments["SIM_NOIS"] = "camera noise simulated"
                header.comments["SIM_MOON"] = "moonlight simulated"
            except Exception as e:
                log.warning(f"Failed to fill simulation information.: {e}")

        hdu_list = fits.HDUList([hdu])
        hdu_list.writeto(filename, overwrite=True)

        self.image_filename = os.path.basename(filename)
