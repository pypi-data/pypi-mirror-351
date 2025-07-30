import logging
import numpy as np

from astropy import units as u
from astropy import constants as const
from astropy.coordinates import Angle
from astropy.coordinates import get_body

from ..coordinates.utils import inv_tangential_projection

log = logging.getLogger(__name__)


class MoonlightMap:
    """
    Implements the calculation of a moonlight brightness map, following
    equation (15) of the paper by Krisciunas et al. (doi:10.1086/132921)

    The brightness is calculated for a given array of altaz coordinates.
    Time of observation and observer's location are extracted from these
    coordinates.

    Brightness is in units photon flux per steradian.
    """

    def __init__(self):
        pass

    def B(self, coords_altaz, moon_altaz, alpha, k=0.172):
        """
        Equation (15) of Krisciunas et al.
        Only valid for moon above the horizon. If moon is below horizon,
        brightness 0 is returned.

        :param SkyCoord coords_altaz: altaz coordinates for which to calculate brightness
        :param SkyCoord moon_altaz: altaz coordinates of the moon
        :param Angle alpha: phase angle of the moon
        :param float k: V-band extinction in units of mag/air mass

        :returns photon flux map
        :rtype array of astropy.Quantity
        """

        # zenith distance of each bin
        zenith = 90 * u.deg - coords_altaz.alt

        # zenith angle of the moon
        zen_moon = 90 * u.deg - moon_altaz.alt

        # separation of each bin to the moon
        rho = coords_altaz.separation(moon_altaz)

        # model is only applicable for moon above horizon.
        if zen_moon < 90 * u.deg:
            B = (
                self.f(rho)
                * self.I(alpha)
                * (1 - 10 ** (-0.4 * k * self.X(zenith)))
                * (10 ** (-0.4 * k * self.X(zen_moon)))
            )
        else:
            B = np.zeros(rho.shape)

        # B is now given in nanoLamberts. Convert to photon flux, assuming 550 nm wavelength
        wavelength = 550 * u.nm
        photon_energy = const.h * const.c / wavelength
        photon_flux = B * 1e-9 * 1e4 / np.pi / 683 * u.W / u.m**2 / u.sr / photon_energy

        return photon_flux.to("m-2 s-1 sr-1")

    def I(self, alpha):
        """
        Illuminance of the moon as function of moon phase angle.
        :param Angle alpha: phase angle of the moon
        :returns moon illuminance
        :rtype: float
        """
        alpha_deg = alpha.to("deg").value
        return 10 ** (-0.4 * (3.84 + 0.026 * np.abs(alpha_deg) + 4e-9 * alpha_deg**4))

    def f(self, rho):
        """
        Atmospheric scattering function as function of the distance
        between moon and observation.
        :param Angle rho: (array of) separations to the moon
        :returns amount of scattered light
        :rtpye (array of) float
        """
        rho_deg = rho.to("deg").value
        A = 5.36
        B = 1.06
        F = 6.15
        return 10**A * (B + (np.cos(rho)) ** 2) + 10 ** (F - rho_deg / 40)

    def X(self, zenith):
        """
        Atmospheric absorption as function of zenith angle
        """
        return (1 - 0.96 * (np.sin(zenith)) ** 2) ** (-0.5)

    def process(self, coords):
        """
        Calculate moon brightness map.

        :returns: brightness list, sun/moon coordinates, moon phase
        :rtype: array of astropy.Quantity, two astropy.SkyCoords, astropy.Angle
        """

        try:
            obstime = coords.frame.obstime
        except:
            raise TypeError("failed to get observation time from input coordinates")

        # moon and sun information
        moon = get_body("moon", obstime)
        moon_altaz = moon.transform_to(coords.frame)

        sun = get_body("sun", obstime)
        sun_altaz = sun.transform_to(coords.frame)

        if sun_altaz.alt <= 0 * u.deg:
            phase = "below"
        else:
            phase = "above"
        log.info("Sun is " + phase + " horizon ({:.1f})".format(sun_altaz.alt))

        if moon_altaz.alt <= 0 * u.deg:
            phase = "below"
        else:
            phase = "above"
        log.info("Moon is " + phase + " horizon ({:.1f})".format(moon_altaz.alt))

        # moon phase
        alpha = Angle(180.0 * u.deg) - moon.separation(sun)
        log.info(
            "Moon phase is {:.1f}".format(alpha.to("deg"))
            + " (i.e. {:.1f}% full moon)".format(np.cos(alpha / 2) * 100),
        )

        # calculate moon brightness (photon flux) and arrange in a map
        fluxes = self.B(coords, moon_altaz, alpha)

        return fluxes.flatten(), sun_altaz, moon_altaz, alpha
