import time
import uuid

import numpy
import numpy as np
from skimage.draw import polygon
from scipy.interpolate import griddata

from astropy import units as u
from astropy import constants as const
from astropy.coordinates import SkyCoord, AltAz

from ctapipe.core import Component
from ctapipe.core.traits import (
    Float,
    Int,
    Bool,
    Unicode,
)
from ctapipe.coordinates import TelescopeFrame

import ctapointing.camera
from ctapointing.config import AstroQuantity, from_config

from .exposure import Exposure, DTYPES
from .moonlight import MoonlightMap
from ..coordinates.utils import rotate_from_pole
from ..catalog import query_catalog

WAVELENGTH = 550  # wavelength of starlight (nm)


class ExposureSimulator(Component):
    """
    Class that simulates images of the sky.
    """

    uuid = Unicode(
        default_value=str(uuid.uuid4()), help="UUID of ExposureSimulator"
    ).tag(config=False)
    name = Unicode(help="name of ExposureSimulator").tag(config=True)
    min_magnitude = Float(
        default_value=-12.0, help="minimum magnitude of stars that are simulated"
    ).tag(config=True)
    max_magnitude = Float(
        default_value=9.0, help="maximum magnitude of stars that are simulated"
    ).tag(config=True)
    num_time_steps = Int(
        default_value=20, help="number of time steps used in simulation"
    ).tag(config=True)
    unsharp_radius = AstroQuantity(
        default_value=50 * u.arcsec, help="radius defining un-sharpness of stars"
    ).tag(config=True)
    unsharp_radius_lid = AstroQuantity(
        default_value=0.16 * u.deg,
        help="radius defining the un-sharpness of reflected stars on lid",
    ).tag(config=True)
    num_unsharp_rays_stars = Int(
        default_value=500, help="number of light rays simulated per star"
    ).tag(config=True)
    num_unsharp_rays_leds = Int(
        default_value=2000, help="number of light rays simulated per LED"
    ).tag(config=True)
    apply_moonlight = Bool(default_value=True, help="apply moonlight simulation").tag(
        config=True
    )
    apply_noise = Bool(default_value=True, help="apply noise in simulation").tag(
        config=True
    )
    ambient_temperature = AstroQuantity(
        default_value=None, allow_none=True, help="ambient temperature"
    ).tag(config=True)
    ambient_pressure = AstroQuantity(
        default_value=None, allow_none=True, help="ambient pressure"
    ).tag(config=True)

    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(config=config, parent=parent, **kwargs)

        self.exposure = None

    @classmethod
    def from_config(cls, **kwargs):
        """
        Read an ExposureSimulator configuration from either configuration file or database.
        Either the path of a configuration file ('input_url') or a database collection
        ('collection') must be provided.


        Parameters
        ----------
        input_url: str or Path
            path of the configuration file.
        name: str
            name of the ExposureSimulator (as in `ExposureSimulator.name`).
            When loading the configuration from file, can be set to check that the configuration with the
            correct name is loaded.
            When loading from database, is used to identify the correct database record.
        uuid: str
            UUID of the camera (as in `ExposureSimulator.uuid`).
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

    def process(
        self,
        camera,
        telescope_pointing,
        start_time,
        duration,
        science_camera=None,
    ):
        """
        Perform the sky simulation.

        Parameters
        ----------
        camera: ctapointing.camera.PointingCamera
            pointing camera object
        telescope_pointing: astropy.SkyCoord
            pointing position of the image
        start_time: astropy.Time
            start time of the simulated observation
        duration: astropy.Quantity
            duration of the exposure
        science_camera: ctapointing.camera.ScienceCamera
            science camera (for body and LED simulations, stars on lid)

        Returns
        -------
        exposure: ctapointing.exposure.Exposure
            exposure object including simulated image
        """

        self.log.info(f"simulating image...")
        self.log.info(f"pointing {telescope_pointing}")
        self.log.info(f"camera {camera.__repr__()}")
        self.log.info(f"exposure start: {start_time}, duration: {duration}")

        start = time.perf_counter()

        # create exposure
        self.exposure = Exposure(is_simulated=True)
        self.exposure.camera = camera
        self.exposure.camera_configname = camera.name

        # simulation settings
        siminfo = self.exposure.simulation_info
        siminfo.time_step = duration / self.num_time_steps
        siminfo.min_mag = self.min_magnitude
        siminfo.max_mag = self.max_magnitude

        siminfo.unsharp_radius = self.unsharp_radius
        siminfo.num_unsharp_rays = self.num_unsharp_rays_stars

        siminfo.has_noise = self.apply_noise
        siminfo.has_moonlight = self.apply_moonlight

        siminfo.fov = camera.fov.to(u.deg)
        siminfo.coords_radec = telescope_pointing

        # exposure and camera settings
        self.exposure.start_time = start_time
        self.exposure.duration = duration
        self.exposure.telescope_pointing = telescope_pointing
        self.exposure.nominal_telescope_pointing = telescope_pointing
        self.exposure.ambient_pressure = self.ambient_pressure
        self.exposure.ambient_temperature = self.ambient_temperature

        # science camera
        self.science_camera = science_camera

        # generate list of stars in the region, including proper motion correction
        c, mag, source_id = query_catalog(
            fov_centre=self.exposure.camera_pointing,
            fov_radius=1.5 * np.max(siminfo.fov) / 2,
            min_mag=siminfo.min_mag,
            max_mag=siminfo.max_mag,
            obstime=self.exposure.mean_exposure_time,
        )

        siminfo.coords_radec = SkyCoord(c.ra, c.dec)
        siminfo.magnitudes = mag

        # calculate true star positions in AltAz and in the CCD chip. These are the ones at
        # the time of half the duration of the exposure.
        siminfo.coords_altaz_meanexp = siminfo.coords_radec.transform_to(
            self.exposure.altazframe
        )
        siminfo.coords_chip_meanexp = siminfo.coords_radec.transform_to(
            self.exposure.skycameraframe
        )
        siminfo.coords_pix_meanexp = camera.transform_to_pixels(
            siminfo.coords_chip_meanexp
        )

        # now render the image
        # take into account field rotation during the exposure
        # for this we render the image at different time steps and sum up the pixel contents

        # observation time steps
        obstime = (
            self.exposure.start_time
            + np.linspace(0, 1, self.num_time_steps, endpoint=False)
            * self.exposure.duration
        )

        # create altaz systems for all time steps simultaneously
        altaz_sys = AltAz(
            location=camera.location,
            obstime=obstime[:, np.newaxis],
            pressure=self.ambient_pressure,
            temperature=self.ambient_temperature,
        )

        # transform star position coordinates. Make use of astropy broadcasting that
        # creates a SkyCoord object of shape (n_times, n_stars)
        coords_altaz = siminfo.coords_radec.transform_to(altaz_sys)

        # calculate photon flux for each star, based on stellar and camera properties
        photon_weights = self._calculate_photon_weights(
            aperture=camera.aperture, efficiency=camera.efficiency
        )

        # smear star coordinates according to resolution
        coords_smeared, photon_weights = self._apply_gaussian_smearing(
            coords_altaz, photon_weights, self.unsharp_radius
        )

        # render image
        self.log.info("rendering star image")
        image = self._render_image(coords_smeared, photon_weights)

        # apply moonlight
        if siminfo.has_moonlight:
            self.log.info("applying moonlight")
            image += self._estimate_moonlight()

        # simulate science camera body and reflected stars on lid
        if self.science_camera is not None:
            self.log.info("rendering science camera")
            camera_body, lid_mask = self._simulate_science_camera_body()
            mask = camera_body > 0
            image[mask] = camera_body[mask]

            # simulate stars on lid
            # photon weight is given by flux reflected onto the lid by the mirror dish, assuming
            # that the lid is a perfect Lambertian reflector
            photon_weights_lid = self._calculate_photon_weights(
                aperture=science_camera.mirror_area
                / science_camera.focal_length**2
                * camera.aperture,
                efficiency=camera.efficiency,
            )

            telescope_pointing_altaz = self.exposure.telescope_pointing.transform_to(
                altaz_sys
            )

            # reflect star coordinates at pointing position
            coords_reflected_altaz = telescope_pointing_altaz.directional_offset_by(
                coords_altaz.position_angle(telescope_pointing_altaz),
                coords_altaz.separation(telescope_pointing_altaz),
            )

            # Gaussian smearing according to resolution
            coords_reflected_smeared, photon_weights_lid = (
                self._apply_gaussian_smearing(
                    coords_reflected_altaz, photon_weights_lid, self.unsharp_radius_lid
                )
            )

            # render image and add part which is covered by lid
            image_reflected = self._render_image(
                coords_reflected_smeared, photon_weights_lid
            )
            image[lid_mask] += image_reflected[lid_mask]

        # apply image noise
        if siminfo.has_noise:
            self.log.info("applying noise")

            try:
                for mean, rms, pixel_fraction in zip(
                    self.exposure.camera.noise_mean,
                    self.exposure.camera.noise_rms,
                    self.exposure.camera.noise_pixel_fraction,
                ):
                    noise_image = np.random.normal(
                        loc=mean,
                        scale=rms,
                        size=image.shape,
                    )
                    pixel_mask = np.random.uniform(size=image.shape)
                    noise_image[pixel_mask < (1 - pixel_fraction)] = (
                        0  # only fraction of pixels contributes
                    )
                    noise_image[noise_image < 0] = 0  # noise is non-negative
                    image += noise_image
            except Exception as e:
                self.log.warning(f"applying image noise failed: {e}")

        # convert to proper bit depth
        dtype = DTYPES[camera.bit_depth]

        # prune image in case of overexposure
        bit_depth = dtype(0).nbytes * 8
        max_value = 2**bit_depth - 1
        if np.any(image[image > max_value]):
            self.log.warning("image is overexposed.")

        image[image > max_value] = max_value
        self.exposure.image = image.astype(dtype)

        stop = time.perf_counter()
        self.log.info(f"simulation finished ({(stop - start):.2f} seconds).")

        return self.exposure

    def _estimate_moonlight(self):
        """
        Produce a moon-light map: construct homogeneously distributed coordinates in a FoV-sized cone,
        calculate expected moon brightness and transform into the image

        Returns
        -------
        moon_image: np.array
            image of moonlight in counts/pixel
        """

        camera = self.exposure.camera

        # dice points homogeneously distributed in the FoV cone
        fov = 1.1 * np.sqrt(camera.fov[0] ** 2 + camera.fov[1] ** 2)
        n = 10000

        # use polar coordinates as approximation of spherical coordinates
        r = np.sqrt(np.random.rand(n) * (fov / 2) ** 2)
        phi = np.random.rand(n) * 360.0 * u.deg

        # point distribution at the pole of the coordinate system, rotate to
        # observation position, and project into chip

        camera_centre_altaz = self.exposure.camera_pointing.transform_to(
            self.exposure.altazframe
        )

        b_coords = SkyCoord(alt=90 * u.deg - r, az=phi, frame=self.exposure.altazframe)
        b_coords_rot = rotate_from_pole(b_coords, camera_centre_altaz)
        b_coords_pix = camera.transform_to_pixels(
            self.exposure.transform_to_camera(b_coords_rot)
        )
        b_mask = camera.clip_to_chip(b_coords_pix)

        self.log.info("\tusing FoV of {:.1f}".format(fov.to("deg")))
        self.log.info("\tusing {} test coordinates".format(n))
        self.log.info(
            "\thit efficiency is {:.1f}%".format(np.count_nonzero(b_mask) / n * 100)
        )

        # calculate moonlight brightness at these coordinates
        m = MoonlightMap()
        b_fluxes, _, _, _ = m.process(b_coords_rot)

        # calculate observed photons from fluxes and interpolate
        solid_angle = camera.pixel_solid_angle
        aperture = camera.aperture

        photons = (
            b_fluxes
            * aperture
            * self.exposure.duration
            * camera.efficiency
            * solid_angle
        ).decompose()

        xx, yy = np.mgrid[0 : camera.num_pix[0], 0 : camera.num_pix[1]]
        xx = xx.reshape(-1, 1)
        yy = yy.reshape(-1, 1)
        inter_coords = np.concatenate((xx, yy), axis=1) + 0.5

        moon_image = griddata(b_coords_pix, photons, inter_coords).reshape(
            camera.num_pix
        )

        return moon_image

    def _calculate_photon_weights(self, aperture, efficiency):
        """
        Calculate number of photons from stars detected by camera of a given aperture
        and collection efficiency

        Parameters
        ----------
        aperture: astropy.Quantity
            aperture of the (lens) opening, in units of area
        efficency: Float
            photon collection efficiency
        """

        # determine stellar photon flux from the visual magnitudes
        wavelength = WAVELENGTH * u.nm  # somewhere in the blue-green (?)

        # conversion of magnitude to flux taken from Wikipedia
        # (probably wrong)
        # apply magnitude +0.25 correction, obtained from comparing to real images
        energy_flux = (
            np.power(
                10,
                -0.4 * (self.exposure.simulation_info.magnitudes / u.mag + 19 + 0.25),
            )
            * u.W
            / u.m**2
        )
        photon_energy = const.h * const.c / wavelength

        # number of photons detected by CCD chip
        photon_weights = (
            energy_flux
            * aperture
            / photon_energy
            * self.exposure.simulation_info.time_step
            * efficiency
        ).decompose()

        return photon_weights

    def _apply_gaussian_smearing(self, coords_altaz, photon_weights, radius):
        """
        Apply a Gaussian smearing to provided coordinates by simulating many (Gaussian-distributed)
        rays around the AltAz position of the stars.
        We smear by the angular resolution that corresponds to a given
        confusion circle in pixels on the chip

        Parameters
        ----------
        coords_altaz: SkyCoord
            (array of) AltAz coordinates of stars
        photon_weights: array
            array of photon weights
        radius: astropy.Quantity
            Gaussian smearing radius (units of angle)

        Returns
        -------
        coords_smeared: SkyCoord
            (array of) smeared coordinates
        photon_weights: array
            array of scaled photon weights
        """

        siminfo = self.exposure.simulation_info

        # check if smearing is needed
        if not np.isclose(radius.to_value(u.arcsec), 0.0):
            n_stars = len(siminfo.magnitudes)
            self.log.info(
                "smearing star positions by Gaussian of width {:.1f}".format(radius)
            )

            # use 2D Gaussian (polar coordinates) as smearing kernel
            radial_offset = (
                np.sqrt(
                    np.random.exponential(
                        radius.to_value(u.arcsec) ** 2,
                        size=(siminfo.num_unsharp_rays, self.num_time_steps, n_stars),
                    )
                )
                * u.arcsec
            )
            position_angle = (
                np.random.random(
                    size=(siminfo.num_unsharp_rays, self.num_time_steps, n_stars)
                )
                * 360
                * u.deg
            )

            # smear coordinates in the altaz system
            # this results in a coordinate array of shape (n_times, n_beams*n_stars)
            # with correctly ordered elements
            coords_smeared = np.swapaxes(
                coords_altaz.directional_offset_by(position_angle, radial_offset), 0, 1
            ).reshape(self.num_time_steps, -1)

            # distribute photon flux among all smeared light rays
            photon_weights /= siminfo.num_unsharp_rays
            photon_weights = np.tile(photon_weights, siminfo.num_unsharp_rays)

        else:
            coords_smeared = coords_altaz

        return coords_smeared, photon_weights

    def _render_image(self, coords, photon_weights):
        """
        Render the image, given a vector of (smeared) AltAz coordinates of stars and
        photon weights
        """
        first = True
        for i in range(self.num_time_steps):
            # project star positions into PointingCamera
            # select those (pre-transformed) altaz positions that belong
            # to the given time step.
            # Note: handling each time step separately is necessary because
            # the project_into() method assumes (for performance reasons)
            # that all AltAz coordinates have the same time.
            #
            # TODO: check for horizon
            #
            coords_ccd = self.exposure.camera.project_into(
                coords[i], telescope_pointing=self.exposure.telescope_pointing
            )

            # project into pixel system and clip to chip boundaries
            coords_pix = self.exposure.camera.transform_to_pixels(coords_ccd)
            clip_mask = self.exposure.camera.clip_to_chip(coords_pix)

            # add up all coordinates to common vector
            if first:
                coords_pix_aggregated = coords_pix[clip_mask]
                photon_weights_aggregated = photon_weights[clip_mask]
                first = False
            else:
                coords_pix_aggregated = np.append(
                    coords_pix_aggregated,
                    coords_pix[clip_mask],
                    axis=0,
                )
                photon_weights_aggregated = np.append(
                    photon_weights_aggregated, photon_weights[clip_mask]
                )

            self.log.debug(
                "\tprocessed {}/{} time steps".format(i + 1, self.num_time_steps)
            )

        # to fill the image, create the image as a 2D histogram with
        # proper number of pixels, then fill each star coordinate with the
        # proper photon flux weight.
        # take care that FITS/astropy convention is followed, i.e. numpy
        # index 0 covers physical pixel 1 which covers the range [-0.5, 0.5]
        nx, ny = self.exposure.camera.num_pix
        image, _ = np.histogramdd(
            coords_pix_aggregated,
            bins=(nx, ny),
            weights=photon_weights_aggregated.value,
            range=((-0.5, nx - 0.5), (-0.5, ny - 0.5)),
        )

        return image

    def _simulate_science_camera_body(self) -> (numpy.array, numpy.array):
        """
        Constructs the body of the science camera.

        Body geometry and led position as well as the intensity of the lid body
        and of the emitting LEDs are properties of scienceCamera.

        Parameters
        ----------
        sciencecamera: ctapointing.camera.ScienceCamera
            description of camera body dimensions and LEDs

        Returns
        -------
        image: numpy.array
            image of simulated body including LEDs. Pixels unaffected by
            the body are set to zero.
        lid_mask: numpy.array
            mask of camera lid in image
        """

        # first step: create polygon from camera body edges, and fill that polygon
        # with a homogeneous intensity in the image.

        # read body edge positions from science camera
        # and transform to pixel coordinates
        vertex_positions_pix = self.exposure.transform_to_camera(
            self.science_camera.body_vertex_positions, to_pixels=True
        )

        # rasterize the polygon from the vertex positions, i.e. get pixel
        # coordinates for which body is visible, then set them to a
        # homogeneous intensity in the full image
        rr, cc = polygon(vertex_positions_pix[:, 0], vertex_positions_pix[:, 1])

        body_image = np.zeros(self.exposure.camera.num_pix)
        body_image[rr, cc] = self.science_camera.body_intensity

        #
        # second step: simulate circular camera lid
        #
        phi = np.linspace(0, 2 * np.pi, 50)
        circle_coords = SkyCoord(
            np.cos(phi) * self.science_camera.lid_radius,
            np.sin(phi) * self.science_camera.lid_radius,
            frame=self.science_camera.sciencecameraframe,
        )
        circle_coords_pix = self.exposure.transform_to_camera(
            circle_coords, to_pixels=True
        )

        rr, cc = polygon(circle_coords_pix[:, 0], circle_coords_pix[:, 1])

        lid_image = np.zeros(self.exposure.camera.num_pix)
        lid_image[rr, cc] = self.science_camera.lid_intensity

        lid_mask = np.zeros_like(lid_image, dtype=bool)
        lid_mask[rr, cc] = True

        #
        # third step: simulate LEDs
        #
        positions = self.science_camera.led_positions
        radius = self.science_camera.led_radius
        intensity = np.array(self.science_camera.led_intensity)

        n_spots = len(positions)

        # create Gaussian distributed rays and store their coordinates in
        # array of shape (n_rays, n_spots, 2)
        # TODO: this line we might want to put into a function,
        # such that for different profiles only a different function
        # call is needed here.
        offsets = (
            np.random.multivariate_normal(
                (0, 0),
                np.diag([radius.to_value(u.m) ** 2] * 2),
                self.num_unsharp_rays_leds * n_spots,
            )
            * u.m
        )

        # add offsets to LED positions by hand, since not supported
        # by astropy (?)
        led_pos = (
            np.array([positions.x.to_value(u.m), positions.y.to_value(u.m)]).T * u.m
        )

        led_pos = np.tile(led_pos, (self.num_unsharp_rays_leds, 1))
        led_pos += offsets
        led_pos = SkyCoord(led_pos[:, 0], led_pos[:, 1], frame=positions.frame)

        # transform to pixel coordinates
        led_pos_pix = self.exposure.transform_to_camera(led_pos, to_pixels=True)

        # set up array of weights; weights are chosen such that, for each LED,
        # the total number of rays for that LED is assigned the full LED
        # intensity.
        weights = np.ones((self.num_unsharp_rays_leds, n_spots)) * intensity.T
        weights = weights.flatten() / self.num_unsharp_rays_leds
        nx, ny = self.exposure.camera.num_pix

        led_image, _ = np.histogramdd(
            led_pos_pix,
            bins=(nx, ny),
            weights=weights,
            range=((-0.5, nx - 0.5), (-0.5, ny - 0.5)),
        )

        return body_image + led_image + lid_image, lid_mask
