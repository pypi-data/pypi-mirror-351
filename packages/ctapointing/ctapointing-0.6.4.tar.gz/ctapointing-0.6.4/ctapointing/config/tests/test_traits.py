import pytest
from traitlets.traitlets import TraitError
import astropy.units as u
from astropy.coordinates import EarthLocation, Longitude, Latitude
from ctapointing.config import AstroEarthLocation, AstroQuantity


def test_AstroQuantity():
    a = AstroQuantity(default_value=1.0 * u.deg)
    assert a.validate(None, 1.0 * u.deg) == u.Quantity(1.0 * u.deg)

    # test if string conversion works
    assert a.validate(None, "1.0 deg") == u.Quantity(1.0 * u.deg)

    # test if list conversion works
    result = a.validate(None, ["2.0m", "3.0m"])
    assert u.allclose(result, u.Quantity([2.0, 3.0] * u.m))

    with pytest.raises(TraitError) as e:
        a.validate(None, "test")
    assert "test" in str(e.value)

    b = AstroQuantity(default_value=1.0 * u.deg, allow_none=True)
    assert "or None" in b.info()


def test_AstroEarthLocation():
    a = AstroEarthLocation(
        default_value=EarthLocation.of_site("Roque de los Muchachos")
    )
    result = a.validate(None, EarthLocation.of_site("Roque de los Muchachos"))
    assert isinstance(result, EarthLocation)

    # check site string
    result = a.validate(None, "Roque de los Muchachos")
    assert isinstance(result, EarthLocation)

    # check list conversion (x, y, z)
    result = a.validate(None, ["1.2m", "1.2m", "2.4m"])
    assert isinstance(result, EarthLocation)

    # check list conversion (lon, lat, height)
    result = a.validate(None, ["10 deg", "20 deg", "500m"])
    assert isinstance(result, EarthLocation)
    assert u.isclose(result.lon, Longitude(10 * u.deg))
    assert u.isclose(result.lat, Latitude(20 * u.deg))
    assert u.isclose(result.height, u.Quantity(500 * u.m))

    with pytest.raises(TraitError) as e:
        a.validate(None, 42)
    assert "42" in str(e.value)

    b = AstroEarthLocation(default_value="Roque de los Muchachos", allow_none=True)
    assert "or None" in b.info()
