import pytest

import numpy as np

# use a copy of astropy's fit_wcs_from_points until bug is fixed in stable astropy version (>4.8)
from ctapointing.imagesolver.utils import fit_wcs_from_points

# from astropy.wcs.utils import fit_wcs_from_points

from astropy.coordinates import SkyCoord, EarthLocation, AltAz, ICRS
from astropy.time import Time
import astropy.units as u

from ctapointing.camera import ApogeeAspen8050Camera


@pytest.mark.parametrize("alt_pointing", np.linspace(-90, 90, 5) * u.deg)
@pytest.mark.parametrize("az_pointing", np.linspace(0, 360, 6) * u.deg)
@pytest.mark.parametrize("tilt_x", np.linspace(-5, 5, 5) * u.deg)
@pytest.mark.parametrize("tilt_y", np.linspace(-5, 5, 5) * u.deg)
def test_wcs_fitting(alt_pointing, az_pointing, tilt_x, tilt_y, atol=0.02, nspots=50):
    """
    Tests whether astropy's WCS fitting of positions on a CCD chip to
    ICRS sky positions results in values close to those of the full coordinate
    transformation (using the SkyCameraFrame).

    Matching is required at the sub-pixel level (parameter atol is the maximum tolerance
    of each spot-sky correspondance in camera pixels).

    Remark: Achievable tolerance is presumably limited by
    the precision of the astropy wcs fit. In particular, higher tolerances need to be
    accepted at low altitudes when refraction correction is switched on (which is
    currently not the case for this test).
    """

    # create AltAz system at dummy location
    location = EarthLocation.of_site("Roque de los Muchachos")
    obstime = Time("2000-01-01 00:00:00")
    altaz = AltAz(location=location, obstime=obstime, pressure=None, temperature=None)

    # create camera, with pointing to alt=50 deg, az=0 deg
    camera = ApogeeAspen8050Camera()
    camera.tilt_x = tilt_x
    camera.tilt_y = tilt_y

    telpointing = SkyCoord(az=az_pointing, alt=alt_pointing, frame=altaz)

    # create random points on the chip, transform to ICRS
    np.random.seed(1234)  # keep always same random numbers

    pix_coords = np.random.rand(nspots, 2) * camera.num_pix
    skycam_coords = camera.transform_to_camera(pix_coords)

    sky_coords = camera.project_from(
        skycam_coords,
        obstime=obstime,
        telescope_pointing=telpointing,
    ).transform_to(ICRS)

    # for WCS fitting, use chip centre in ICRS coordinates as (initial) WCS tangent point
    camera_centre_skycam = camera.transform_to_camera(camera.chip_centre)
    camera_centre = camera.project_from(
        camera_centre_skycam, obstime, telpointing
    ).transform_to(ICRS)

    # WCS fitting (pixels to ICRS), using all grid points
    # note that (x,y) pixel coordinates are flipped because in the SkyCameraFrame, x points along the
    # "y-axis" and y points along the "x-axis" of the upright image
    wcs = fit_wcs_from_points(
        (pix_coords[:, 1], pix_coords[:, 0]),
        sky_coords,
        sip_degree=0,
        proj_point=camera_centre[0],
    )

    # transform RADec positions to pixels, using WCS fit
    # these should be the same as the onces transformed by camera.project_into()
    x, y = sky_coords.to_pixel(wcs)
    pix_from_sky_coords = np.append(y.reshape(-1, 1), x.reshape(-1, 1), axis=1)

    print("pix_coords:")
    print(pix_coords)
    print("pix_from_sky_coords:")
    print(pix_from_sky_coords)

    allclose = np.allclose(pix_coords, pix_from_sky_coords, atol=atol)
    print("allclose:", allclose)

    # compare whether both solutions match
    assert np.allclose(pix_coords, pix_from_sky_coords, atol=atol)


if __name__ == "__main__":
    test_wcs_fitting(0.0 * u.deg, 0.0 * u.deg, -5.0 * u.deg, 5.0 * u.deg)
