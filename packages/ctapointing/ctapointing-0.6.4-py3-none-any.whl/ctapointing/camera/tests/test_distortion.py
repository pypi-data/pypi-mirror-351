import numpy as np
from ctapointing.camera import DistortionCorrectionSIP, ZWO_ASI2600_Camera
import astropy.units as u


def test_distortion_correction_sip():
    # Create a DistortionCorrection object with initial coefficients
    dc = DistortionCorrectionSIP()

    # Define some distortion coefficients (from a typical image)
    dc.coeff["A10"] = 3.6e-6
    dc.coeff["A20"] = 1.7e-8
    dc.coeff["A11"] = 6.1e-9
    dc.coeff["A02"] = -3.6e-9
    dc.coeff["B10"] = 4.3e-6
    dc.coeff["B20"] = 2.1e-9
    dc.coeff["B11"] = 6.7e-9
    dc.coeff["B02"] = 3.0e-9

    dc.coeff_inv["AP10"] = -3.6e-6
    dc.coeff_inv["AP20"] = -1.7e-8
    dc.coeff_inv["AP11"] = -6.1e-9
    dc.coeff_inv["AP02"] = 3.6e-9
    dc.coeff_inv["BP10"] = -4.3e-6
    dc.coeff_inv["BP20"] = -2.1e-9
    dc.coeff_inv["BP11"] = -6.7e-9
    dc.coeff_inv["BP02"] = -3.0e-9

    camera = ZWO_ASI2600_Camera()

    # create some synthetic pixel coordinates
    pix_x = np.linspace(0, camera.num_pix[0], 100)
    pix_y = np.linspace(0, camera.num_pix[1], 100)
    xx, yy = np.meshgrid(pix_x, pix_y)

    pix_coords = np.append(xx.reshape(-1, 1), yy.reshape(-1, 1), axis=1)
    pix_coords_transformed = dc.apply_correction(pix_coords)
    pix_coords_backtransformed = dc.apply_inverse_correction(pix_coords_transformed)

    # after back-transform, make sure that original pixel coordinates are retained
    # within a precision of 1/100 arcsec.
    required_precision = 0.01 * u.arcsec
    required_precision_pix = required_precision / camera.pixel_angle[0]

    assert np.allclose(
        pix_coords, pix_coords_backtransformed, atol=required_precision_pix
    )
