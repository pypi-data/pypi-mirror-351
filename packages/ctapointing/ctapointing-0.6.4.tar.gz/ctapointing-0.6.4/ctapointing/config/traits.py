from traitlets.traitlets import TraitType
from astropy.units import Quantity, UnitConversionError
from astropy.coordinates import EarthLocation


class AstroQuantity(TraitType):
    """
    A trait representing an astropy.units.Quantity
    Can hold an arbitrary Quantity, even a quantity whose elements are stored in a list.

    In a yaml/toml/json configuration file, an AstroQuantity must be represented by
    - a string, e.g. "1.0 m"
    - a list of strings, e.g. ["1.0 m", "2.0 m", "4.0 m"], with identical units.
    """

    def validate(self, obj, value):
        """try to parse and to a unit conversion"""
        try:
            if isinstance(value, str):
                # string containing value and unit
                return Quantity(value)
            elif isinstance(value, list):
                # list of strings containing value and unit
                return Quantity([Quantity(element) for element in value])
            else:
                # astropy.Quantity instance
                return Quantity(value)

        except (ValueError, TypeError, UnitConversionError):
            return self.error(obj, value)

    def info(self):
        info = "an Astropy Quantity"
        if self.allow_none:
            info += "or None"
        return info


class AstroEarthLocation(TraitType):
    """
    A trait representing an Astropy.EarthLocation.

    In a yaml/toml/json configuration file, an AstroEarthLocation must be represented by
    - a string representing an EarthLocation.of_site() site name
    - a 3-list of strings, each representing the x, y, z coordinates in the geocentric coordinate system,
      e.g. ["1.0 m", "2.0 m", "4.0 m"] with units representing a length
    - a 3 list of strings, the first two representing the longitude and latitude of the location and the
      third representing the altitude, e.g ["20.0 deg", "30.0 deg", "8000 m"].
    """

    def validate(self, obj, value):
        """try to parse and to a unit conversion"""
        try:
            if isinstance(value, str):
                # location from site catalog
                return EarthLocation.of_site(value)
            elif isinstance(value, list):
                # geocentric coordinates
                x = Quantity(value[0])
                y = Quantity(value[1])
                z = Quantity(value[2])
                return EarthLocation(x, y, z)
            else:
                # EarthLocation instance
                return EarthLocation(value)

        except (ValueError, TypeError, UnitConversionError):
            return self.error(obj, value)

    def info(self):
        info = "an Astropy EarthLocation"
        if self.allow_none:
            info += "or None"
        return info
