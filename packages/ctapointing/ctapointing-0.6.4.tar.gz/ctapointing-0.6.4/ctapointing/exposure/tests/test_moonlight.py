import pytest
from astropy import units as u
from ctapointing.exposure.moonlight import MoonlightMap
from astropy.coordinates import SkyCoord, AltAz, EarthLocation, get_body
from astropy.time import Time


def test_B():
    b_coords = SkyCoord(alt=90 * u.deg, az=0 * u.deg, frame=AltAz)
    moon_coords = SkyCoord(alt=-5 * u.deg, az=0 * u.deg, frame=AltAz)
    ml = MoonlightMap()
    assert ml.B(b_coords, moon_coords, 9 * u.deg).value == 0


def test_process():
    ml = MoonlightMap()
    frame = AltAz(
        obstime=Time("2023-01-21T00:00:00"),
        location=EarthLocation.of_site("Roque de los Muchachos"),
        pressure=None,
        temperature=None,
    )
    coords = SkyCoord(alt=90 * u.deg, az=0 * u.deg, frame=frame)
    with pytest.raises(
        TypeError, match="failed to get observation time from input coordinates"
    ):
        ml.process(5)

    flux, sun, moon, alpha = ml.process(coords)
    assert flux.value == 0

    frame = AltAz(
        obstime=Time("2028-07-22T02:01:00"),  # solar eclipse in greenwich
        location=EarthLocation.of_site("greenwich"),
        pressure=None,
        temperature=None,
    )
    coords = SkyCoord(
        alt=29.5 * u.deg, az=327.66 * u.deg, frame=frame
    )  # direction of sun
    flux, sun, moon, alpha = ml.process(coords)
    assert flux.value == 0
    assert abs(alpha.value) < 1 or abs(180 - alpha.value) < 1
