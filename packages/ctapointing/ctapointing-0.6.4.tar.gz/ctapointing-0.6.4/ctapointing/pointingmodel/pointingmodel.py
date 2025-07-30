import uuid
import numpy as np

import astropy.units as u
from astropy.coordinates import Longitude, Latitude, SkyCoord

from ctapipe.core import Component
from ctapipe.core.traits import (
    Unicode,
    AstroTime,
)
from ctapointing.config import (
    AstroQuantity,
    from_config,
)


class PointingModel(Component):
    """
    Super class that holds the parameters of a pointing model, provides
    a function to calculate pointing corrections for a particular coordinate,
    and enables loading of a model from the database or a file.
    """

    parameters = []

    uuid = Unicode(default_value=str(uuid.uuid4()), help="UUID of Pointing Model").tag(
        config=True
    )
    name = Unicode(help="model name", allow_none=False).tag(config=True)
    from_date = Unicode(None, "date of first validity of model", type=str)
    valid_from = AstroTime(
        help="start date of validity of model", default_value=None, allow_none=True
    ).tag(config=True)
    valid_until = AstroTime(
        help="end date of validity of model", default_value=None, allow_none=True
    ).tag(config=True)

    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(config=config, parent=parent, **kwargs)

    @classmethod
    def from_config(cls, **kwargs):
        """
        Read a pointing model from either configuration file or database.
        Either the path of a configuration file ('input_url') or a database collection
        ('collection') must be provided.


        Parameters
        ----------
        input_url: str or Path
            path of the configuration file.
        name: str
            name of the camera (as in `PointingCamera.name`).
            When loading the configuration from file, can be set to check that the configuration with the
            correct name is loaded.
            When loading from database, is used to identify the correct database record.
        uuid: str
            UUID of the camera (as in `PointingCamera.uuid`).
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
        camera: PointingCamera object
        """
        # load configuration and construct instance
        config = from_config(component_name=cls.__name__, **kwargs)
        return cls(config=config)

    def __str__(self):
        s = f"{self.__class__.__name__}(name={self.name}, uuid={self.uuid})\n"
        s += "  model parameters:\n"
        for k in self.parameters:
            s += f"    {k}: {getattr(self, k)}\n"
        s += f"  valid from:  {self.valid_from}\n"
        s += f"  valid until: {self.valid_until}\n"
        return s

    def __repr__(self):
        s = f"{self.__class__.__name__}(uuid={self.uuid}"
        s += f", num of parameters={len(self.parameters)})"
        return s

    def update_parameter_values(self, parameters: dict | list) -> None:
        """
        Set a model or parts of a model from individual arguments or a dictionary

        Parameters
        ----------
        parameters: dict
            dictionary of model parameters names (keys) and parameter values
        """
        if isinstance(parameters, (list, tuple)):
            for i, p in enumerate(parameters):
                k = self.parameters[i]
                unit = getattr(self, k).unit
                setattr(self, k, u.Quantity(p, unit))
        elif isinstance(parameters, dict):
            for k in parameters.keys():
                unit = getattr(self, k).unit
                setattr(self, k, u.Quantity(parameters[k], unit))

    def get_parameters_as_list(self, strip_units=False) -> list:
        """
        Return a list of parameter values (with or without units)
        """
        if strip_units:
            values = [
                getattr(self, self.parameters[i]).value
                for i in range(len(self.parameters))
            ]
        else:
            values = [
                getattr(self, self.parameters[i]) for i in range(len(self.parameters))
            ]
        return values

    def get_parameters_as_dict(self, strip_units=False) -> dict:
        """
        Return a list of parameter values (with or without units)
        """
        if strip_units:
            values = {
                self.parameters[i]: getattr(self, self.parameters[i]).value
                for i in range(len(self.parameters))
            }
        else:
            values = {
                self.parameters[i]: getattr(self, self.parameters[i])
                for i in range(len(self.parameters))
            }
        return values

    def get_corrected_pointing(self, nominal_pointing):
        """
        Calculates the corrected pointing for a single nominal pointing
        position.
        Must be implemented by child class.
        """

        print("not implemented in abstract base class.")
        raise NotImplementedError


class NullModel(PointingModel):
    """
    A pointing model without any corrections applied.
    """

    parameters = []

    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(config=config, parent=parent, **kwargs)

    def get_corrected_pointing(self, nominal_pointing):
        """
        Calculates the corrected pointing for a single nominal pointing
        position.

        In case of the NullModel, output is identical to input.

        Parameters
        ----------
        nominal_pointing : SkyCoord
            Nominal pointing of the telescope.

        Returns
        -------
        corrected_pointing : SkyCoord
            Corrected pointing of the telescope, according to
            the model prediction.

        """
        corrected_pointing = nominal_pointing.copy()
        return corrected_pointing


class MechanicalModelHESS(PointingModel):
    """
    The HESS standard pointing model.
    """

    parameters = [
        "amp_se_az",
        "phase_se_az",
        "amp_se_alt",
        "phase_se_alt",
        "offset_se_az",
        "amp_non_vert_az",
        "phase_non_vert_az",
        "camera_offset_vert",
        "camera_offset_vert_reverse",
        "camera_offset_hor",
        "amp_non_perp_alt",
        "bending_vert",
        "bending_hor",
        "const_refraction",
        "amp_sin_2az",
        "mix_sin_2az",
        "phase_sin_2az",
        "const_camera_rot",
        "const_focal_length",
    ]

    amp_se_az = AstroQuantity(
        default_value=0.0 * u.arcsec, help="amplitude of shaft encoder error azimuth"
    ).tag(config=True)
    phase_se_az = AstroQuantity(
        default_value=0.0 * u.deg, help="phase of shaft encoder error azimuth"
    ).tag(config=True)
    amp_se_alt = AstroQuantity(
        default_value=0.0 * u.arcsec, help="amplitude of shaft encoder error altitude"
    ).tag(config=True)
    phase_se_alt = AstroQuantity(
        default_value=0.0 * u.deg, help="phase of shaft encoder error altitude"
    ).tag(config=True)
    offset_se_az = AstroQuantity(
        default_value=0.0 * u.deg, help="offset of shaft encoder azimuth"
    ).tag(config=True)
    amp_non_vert_az = AstroQuantity(
        default_value=0.0 * u.arcsec, help="amplitude of non-verticality azimuth axis"
    ).tag(config=True)
    phase_non_vert_az = AstroQuantity(
        default_value=0.0 * u.deg, help="phase of non-verticality azimuth axis"
    ).tag(config=True)
    camera_offset_vert = AstroQuantity(
        default_value=0.0 * u.arcsec, help="vertical camera offset"
    ).tag(config=True)
    camera_offset_vert_reverse = AstroQuantity(
        default_value=0.0 * u.arcsec, help="vertical camera offset (reverse)"
    ).tag(config=True)
    camera_offset_hor = AstroQuantity(
        default_value=0.0 * u.arcsec, help="horizontal camera offset"
    ).tag(config=True)
    amp_non_perp_alt = AstroQuantity(
        default_value=0.0 * u.arcsec,
        help="amplitude of non-perpendicularity altitude axis",
    ).tag(config=True)
    bending_vert = AstroQuantity(
        default_value=0.0 * u.arcsec, help="vertical camera bending"
    ).tag(config=True)
    bending_hor = AstroQuantity(
        default_value=0.0 * u.arcsec, help="horizontal camera bending"
    ).tag(config=True)
    const_refraction = AstroQuantity(
        default_value=0.0 * u.arcsec, help="constant refraction"
    ).tag(config=True)
    amp_sin_2az = AstroQuantity(
        default_value=0.0 * u.arcsec, help="amplitude of sin(2az) effect"
    ).tag(config=True)
    mix_sin_2az = AstroQuantity(
        default_value=0.0 * u.deg, help="mixing angle of sin(2az) effect"
    ).tag(config=True)
    phase_sin_2az = AstroQuantity(
        default_value=0.0 * u.deg, help="phase of sin(2az) effect"
    ).tag(config=True)
    const_camera_rot = AstroQuantity(
        default_value=0.0 * u.deg, help="constant camera rotation"
    ).tag(config=True)
    const_focal_length = AstroQuantity(
        default_value=0.0 * u.m, help="constant focal length"
    ).tag(config=True)

    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(config=config, parent=parent, **kwargs)

    def get_corrected_pointing(self, nominal_pointing):
        """
        Calculates the corrected pointing for a (array-like) sky coordinate
        in the AltAz system.

        Implements the 19 parameters HESS mechanical pointing model.

        Parameters
        ----------
        nominal_pointing : SkyCoord
            Nominal pointing of the telescope.

        Returns
        -------
        corrected_pointing : SkyCoord
            Corrected pointing of the telescope, according to
            the model predicition.

        """

        az0 = Longitude(nominal_pointing.az)
        alt0 = Latitude(nominal_pointing.alt)

        # drive system error AZ
        az1 = az0 + self.amp_se_az * np.sin(az0 + self.phase_se_az)

        # drive system error ALT: difficult to detangle from p10 !
        # p2 and p3 should be fixed
        alt1 = alt0 + self.amp_se_alt * np.sin(alt0 + self.phase_se_alt)

        # SE-offsets
        az2 = az1 + self.offset_se_az
        alt2 = alt1

        # not independent!
        # alt2 += fPars[xxx]/3600.;

        # non-verticality az-axis
        x1 = np.cos(alt2) * np.cos(az2)
        y1 = np.cos(alt2) * np.sin(az2)
        z1 = np.sin(alt2)

        sina = np.sin(self.amp_non_vert_az)
        cosa = np.cos(self.amp_non_vert_az)

        sinb = np.sin(self.phase_non_vert_az)
        cosb = np.cos(self.phase_non_vert_az)

        x2 = (
            x1 * ((cosb * cosb) + (sinb * sinb) * cosa)
            + y1 * (sinb * cosb - cosa * sinb * cosb)
            + z1 * (-sina * sinb)
        )
        y2 = (
            x1 * (sinb * cosb - cosa * sinb * cosb)
            + y1 * ((sinb * sinb) + cosa * (cosb * cosb))
            + z1 * (sina * cosb)
        )
        z2 = x1 * (sina * sinb) + y1 * (-sina * cosb) + z1 * cosa

        alt3 = np.arcsin(z2)

        argument = x2 / np.cos(alt3)

        # dirty trick ...
        argument[argument > 1.0] = 1.0
        argument[argument < -1.0] = -1.0

        mask = y2 > 0.0
        az3 = np.arccos(argument)
        az3[~mask] = 360.0 * u.deg - np.arccos(argument[~mask])

        # check az-range
        az3[(az3 > 330.0 * u.deg) & (az0 < 30.0 * u.deg)] -= 360.0 * u.deg
        az3[(az3 < 30.0 * u.deg) & (az0 > 330.0 * u.deg)] += 360.0 * u.deg

        # now camera system
        dy = alt3 - alt0  # vertical !
        dx = (az3 - az0) * np.cos(alt3)  # horizontal !

        # camera offsets
        # p8 only can be measured if normal + reverse mode data is available
        # p8 should be fixed.
        dy += self.camera_offset_vert + self.camera_offset_vert_reverse
        dx += self.camera_offset_hor

        # non-perpendicularity alt-axis
        # difference in vertical direction is very small, neglected
        # dy += np.arcsin(np.cos(self.amp_non_perp_alt) * sin(alt3))
        dx += np.arcsin(np.sin(self.amp_non_perp_alt) * np.sin(alt3))

        # bending
        dy -= self.bending_vert * np.cos(alt3)

        # horizontal bending not really needed.
        # fix parameter p12
        dx += self.bending_hor * np.cos(alt3)

        # refraction : is yet corrected by measured weather!
        # fix parameter p13
        dy += self.const_refraction * np.tan((90.0 * u.deg - alt3))

        # effect that depends on sin(2 az)
        dx += (
            self.amp_sin_2az
            * np.cos(self.mix_sin_2az)
            * np.sin(2 * (az3 + self.phase_sin_2az))
        )
        dy += (
            self.amp_sin_2az
            * np.sin(self.mix_sin_2az)
            * np.sin(2 * (az3 + self.phase_sin_2az))
        )

        # apply correction
        corrected_pointing = nominal_pointing.copy()
        corrected_pointing.data.lon[()] += dx
        corrected_pointing.data.lat[()] += dy
        corrected_pointing.cache.clear()

        return corrected_pointing

    # def get_parameters(self, reduced=False):
    #     """
    #     Return the vector of model parameters.
    #     If reduced is set to True, return parameters which are corrected
    #     for overflow in periodicity and for which amplitudes are converted
    #     to positive values.
    #     """
    #
    #     if not reduced:
    #         return self.parameters
    #
    #     parameters = self.parameters.copy()
    #
    #     # SE error
    #     parameters[1] = parameters[1] % 360.0
    #     if parameters[0] < 0:
    #         parameters[0] = np.fabs(parameters[0])
    #         parameters[1] = parameters[1] - 180.0
    #
    #     # non-verticality az axis
    #     parameters[6] = parameters[6] % 360.0
    #     if parameters[5] < 0:
    #         parameters[5] = np.fabs(parameters[5])
    #         parameters[6] = parameters[6] - 180.0
    #
    #     # sin(2az) effect
    #     parameters[15] = parameters[15] % 360.0
    #     parameters[16] = parameters[16] % 180.0
    #     if parameters[14] < 0:
    #         parameters[14] = np.fabs(parameters[14])
    #         parameters[15] = (parameters[15] - 180.0) % 360.0
    #
    #     if parameters[15] > 180.0:
    #         parameters[15] = parameters[15] - 180.0
    #         parameters[16] = (parameters[16] - 90.0) % 180.0
    #
    #     return parameters
