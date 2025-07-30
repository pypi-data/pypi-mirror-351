"""
Catalog utility functions.

Query both bright star and Gaia catalogs for stars in a given magnitude range
and within a given (circular) field of view
"""

from astropy.table import vstack
from astropy.time import Time
from astropy.coordinates import SkyCoord, ICRS
from ctapointing.catalog import BrightStarCatalog, GaiaCatalog

MIN_MAG = -12.0
MAX_MAG = 12.0


def query_catalog(
    fov_centre, fov_radius, min_mag=MIN_MAG, max_mag=MAX_MAG, obstime=None
):
    """
    Query both bright star and Gaia catalogs for stars in a given magnitude range
    and within a given (circular) field of view.

    A correction of the Gaia magnitude is applied to match that magnitude to
    the V-magnitude provided by the bright star catalog.

    Proper motion is taken into account; the ICRS coordinates of the stars
    are computed for the given observation time.

    Parameters
    ----------
    fov_centre : Coordinate
        Sky coordinate of field-of-view centre
    fov_radius: Angle
        Opening angle of the field-of-view
    min_mag : float
        Minimum magnitude. Only stars with mag >= min_mag are considered.
    max_mag : float
        Maximum magnitude. Only stars with mag <= max_mag are considered.
    obstime : astropy.time.Time or None
        Time of observation. This is used to calculate the ICRS position of
        each star after proper motion correction. Set to 'None' for no correction.

    Returns
    -------
    coords, mag, source-id : tuple
        Coordinates and magnitudes of all found stars.
    """

    # Yale Bright Star Catalog
    bsc = BrightStarCatalog(min_mag=min_mag)
    bsc_star_list = bsc.select_around_position(fov_centre, fov_radius)

    # Gaia Catalog
    gaia = GaiaCatalog(max_mag=max_mag, magnitude_correction=0.25)
    gaia_star_list = gaia.select_around_position(fov_centre, fov_radius)

    # merge the two lists
    star_list = vstack([bsc_star_list, gaia_star_list])
    source_id = star_list["source_id"]
    mag = star_list["phot_v_mean_mag"]

    apply_pm = obstime is not None

    # construct coordinates with proper motion information and
    # correct epoch
    coords = SkyCoord(
        ra=star_list["ra"],
        dec=star_list["dec"],
        frame=ICRS,
        pm_dec=star_list["pmdec"] if apply_pm else None,
        pm_ra_cosdec=star_list["pmra"] if apply_pm else None,
        #        equinox=(
        #            Time(star_list["ref_epoch"], format="jyear")
        #            if obstime is not None
        #            else None
        #        ),
    )

    # apply proper motion correction
    apply_pm = False
    if apply_pm and not len(coords) == 0:
        coords.apply_space_motion(obstime)
        coords = SkyCoord(coords.ra, coords.dec, frame=ICRS)

    return coords, mag, source_id
