import numpy as np
import uuid

from ctapipe.core import Component
from ctapipe.core.traits import (
    Unicode,
    Dict,
)


class DistortionCorrection(Component):
    """
    Base class for implementing distortion corrections.
    """

    uuid = Unicode(default_value=str(uuid.uuid4()), help="UUID of Camera").tag(
        config=True
    )
    name = Unicode(help="distortion correction name", allow_none=False).tag(config=True)
    coeff = Dict(
        default_value={}
    )  # dictionary of coefficients for forward transformation
    coeff_inv = Dict(
        default_value={}
    )  # dictionary of coefficients for inverse transformation

    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(config=config, parent=parent, **kwargs)

    def __repr__(self):
        s = f"{self.__class__.__name__}"
        s += f" (uuid={self.uuid}, name={self.name}"
        s += ")"
        return s

    @classmethod
    def from_config(cls, **kwargs):
        """
        Read a DistortionCorrection configuration from either configuration file or database.
        Either the path of a configuration file ('input_url') or a database collection
        ('collection') must be provided.


        Parameters
        ----------
        input_url: str or Path
            path of the configuration file.
        name: str
            name of the DistortionCorrection (as in `DistortionCorrection.name`).
            When loading the configuration from file, can be set to check that the configuration with the
            correct name is loaded.
            When loading from database, is used to identify the correct database record.
        uuid: str
            UUID of the camera (as in `DistortionCorrection.uuid`).
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
        extractor: DistortionCorrection object
        """
        # load configuration and construct instance
        config = from_config(component_name=cls.__name__, **kwargs)
        return cls(config=config)

    def apply_correction(self, coords):
        raise NotImplementedError(
            "not implemented in base class - use specific distortion model instead."
        )

    def apply_inverse_correction(self, coords_p):
        raise NotImplementedError(
            "not implemented in base class - use specific distortion model instead."
        )


class DistortionCorrectionNull(DistortionCorrection):
    def apply_correction(self, coords):
        return coords

    def apply_inverse_correction(self, coords_p):
        return coords_p


class DistortionCorrectionBrownConrady(DistortionCorrection):
    coeff = Dict(
        default_value={
            "XC": 0.0,
            "YC": 0.0,
            "K1": 0.0,
            "K2": 0.0,
            "P1": 0.0,
            "P2": 0.0,
            "P3": 0.0,
            "P4": 0.0,
        }
    ).tag(config=True)
    coeff_inv = Dict(
        default_value={
            "XPC": 0.0,
            "YPC": 0.0,
            "KP1": 0.0,
            "KP2": 0.0,
            "PP1": 0.0,
            "PP2": 0.0,
            "PP3": 0.0,
            "PP4": 0.0,
        }
    ).tag(config=True)

    def apply_correction(self, coords):
        coords_rel = coords - np.array([self.coeff["XC"], self.coeff["YC"]]).reshape(
            1, 2
        )

        coords_rel_x = coords_rel[:, 0]
        coords_rel_y = coords_rel[:, 1]

        r2 = coords_rel_x**2 + coords_rel_y**2
        #        r2 = np.sum(coords_rel**2, axis=1)

        p = coords_rel_x * (self.coeff["K1"] * r2 + self.coeff["K2"] * r2**2)
        +(
            self.coeff["P1"] * (r2 + 2 * coords_rel_x**2)
            + 2 * self.coeff["P2"] * coords_rel_x * coords_rel_y
        ) * (1 + self.coeff["P3"] * r2 + self.coeff["P4"] * r2**2)

        q = coords_rel_y * (self.coeff["K1"] * r2 + self.coeff["K2"] * r2**2)
        +(
            self.coeff["P2"] * (r2 + 2 * coords_rel_y**2)
            + 2 * self.coeff["P1"] * coords_rel_x * coords_rel_y
        ) * (1 + self.coeff["P3"] * r2 + self.coeff["P4"] * r2**2)

        correction = np.concatenate((p.reshape(-1, 1), q.reshape(-1, 1)), axis=1)

        return coords + correction

    def apply_inverse_correction(self, coords_p):
        coords_rel = coords_p - np.array(
            [self.coeff_inv["XPC"], self.coeff_inv["YPC"]]
        ).reshape(1, 2)

        coords_rel_x = coords_rel[:, 0]
        coords_rel_y = coords_rel[:, 1]

        r2 = coords_rel_x**2 + coords_rel_y**2
        #        r2 = np.sum(coords_rel**2, axis=1)

        p = coords_rel_x * (self.coeff_inv["KP1"] * r2 + self.coeff_inv["KP2"] * r2**2)
        +(
            self.coeff_inv["PP1"] * (r2 + 2 * coords_rel_x**2)
            + 2 * self.coeff_inv["PP2"] * coords_rel_x * coords_rel_y
        ) * (1 + self.coeff_inv["PP3"] * r2 + self.coeff_inv["PP4"] * r2**2)

        q = coords_rel_y * (self.coeff_inv["KP1"] * r2 + self.coeff_inv["KP2"] * r2**2)
        +(
            self.coeff_inv["PP2"] * (r2 + 2 * coords_rel_y**2)
            + 2 * self.coeff_inv["PP1"] * coords_rel_x * coords_rel_y
        ) * (1 + self.coeff_inv["PP3"] * r2 + self.coeff_inv["PP4"] * r2**2)

        correction = np.concatenate((p.reshape(-1, 1), q.reshape(-1, 1)), axis=1)

        return coords_p + correction


class DistortionCorrectionSIP(DistortionCorrection):
    """
    Class implementing simple polynomial distortion correction
    for images

    Pixel corrections are implemented according to
    "The SIP Convention for Representing Distortion in FITS Image Headers"

    Currently, a 2nd order polynominal correction is implemented.
    For the transformation from ideal (intermediate) pixel coordinates to
    physical pixel coordinates:

    .. math::
        x_p = A_{10} x^1 y^0 + A_{20} x^2 y^0 + A_{11} x^1 y^1 + A_{02} x^0 y^2

        y_p = B_{10} x^1 y^0 + B_{20} x^2 y^0 + B_{11} x^1 y^1 + B_{02} x^0 y^2

    For the inverse transformation from physical pixel coordinates to
    ideal (intermediate) pixel coordinates:

    .. math::
        x = AP_{10} x_p^1 y_p^0 + AP_{20} x_p^2 y_p^0 + AP_{11} x_p^1 y_p^1 + AP_{02} x_p^0 y_p^2

        y = BP_{10} x_p^1 y_p^0 + BP_{20} x_p^2 y_p^0 + BP_{11} x_p^1 y_p^1 + BP_{02} x_p^0 y_p^2
    """

    coeff = Dict(
        default_value={
            "A10": 0.0,
            "A20": 0.0,
            "A11": 0.0,
            "A02": 0.0,
            "B10": 0.0,
            "B20": 0.0,
            "B11": 0.0,
            "B02": 0.0,
        }
    ).tag(config=True)
    coeff_inv = Dict(
        default_value={
            "AP10": 0.0,
            "AP20": 0.0,
            "AP11": 0.0,
            "AP02": 0.0,
            "BP10": 0.0,
            "BP20": 0.0,
            "BP11": 0.0,
            "BP02": 0.0,
        }
    ).tag(config=True)

    def apply_correction(self, coords):
        """
        Apply distortion correction from ideal (intermediate) pixel coordinates
        ``(x, y)`` to physical pixel coordinates ``(xp, yp)``.

        Parameters
        ----------
        coords: np.array
            2D array of ideal pixel positions

        Returns
        -------
        coords_p: np.array
            2D array of physical pixel positions
        """

        coeff_matrix_A = np.zeros((3, 3))
        coeff_matrix_A[1, 0] = self.coeff["A10"]  # A_10
        coeff_matrix_A[2, 0] = self.coeff["A20"]  # A_20
        coeff_matrix_A[1, 1] = self.coeff["A11"]  # A_11
        coeff_matrix_A[0, 2] = self.coeff["A02"]  # A_02

        coeff_matrix_B = np.zeros((3, 3))
        coeff_matrix_B[1, 0] = self.coeff["B10"]  # B_10
        coeff_matrix_B[2, 0] = self.coeff["B20"]  # B_20
        coeff_matrix_B[1, 1] = self.coeff["B11"]  # B_11
        coeff_matrix_B[0, 2] = self.coeff["B02"]  # B_02

        p = np.polynomial.polynomial.polyval2d(
            coords[:, 0], coords[:, 1], coeff_matrix_A
        ).reshape(-1, 1)

        q = np.polynomial.polynomial.polyval2d(
            coords[:, 0], coords[:, 1], coeff_matrix_B
        ).reshape(-1, 1)

        correction = np.concatenate((p, q), axis=1)
        return coords + correction

    def apply_inverse_correction(self, coords_p):
        """
        Apply distortion correction from physical pixel coordinates
        ``(xp, yp)`` to ideal (intermediate) pixel coordinates ``(x, y)``.

        Parameters
        ----------
        coords_p: np.array
            2D array of physical pixel positions

        Returns
        -------
        coords: np.array
            2D array of ideal pixel positions

        """

        coeff_matrix_AP = np.zeros((3, 3))
        coeff_matrix_AP[1, 0] = self.coeff_inv["AP10"]  # AP_10
        coeff_matrix_AP[2, 0] = self.coeff_inv["AP20"]  # AP_20
        coeff_matrix_AP[1, 1] = self.coeff_inv["AP11"]  # AP_11
        coeff_matrix_AP[0, 2] = self.coeff_inv["AP02"]  # AP_02

        coeff_matrix_BP = np.zeros((3, 3))
        coeff_matrix_BP[1, 0] = self.coeff_inv["BP10"]  # BP_10
        coeff_matrix_BP[2, 0] = self.coeff_inv["BP20"]  # BP_20
        coeff_matrix_BP[1, 1] = self.coeff_inv["BP11"]  # BP_11
        coeff_matrix_BP[0, 2] = self.coeff_inv["BP02"]  # BP_02

        p = np.polynomial.polynomial.polyval2d(
            coords_p[:, 0], coords_p[:, 1], coeff_matrix_AP
        ).reshape(-1, 1)

        q = np.polynomial.polynomial.polyval2d(
            coords_p[:, 0], coords_p[:, 1], coeff_matrix_BP
        ).reshape(-1, 1)

        correction = np.concatenate((p, q), axis=1)
        return coords_p + correction
