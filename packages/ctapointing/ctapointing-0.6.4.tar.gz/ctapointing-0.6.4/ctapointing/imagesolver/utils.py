import copy
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.coordinates import SkyCoord

from .statusbase import Status

from matplotlib.gridspec import GridSpec
from ctapointing.exposure.utils import plot_exposure


def plot_quads(
    quads,
    camera,
    ax=None,
    label=None,
    color="moccasin",
    alpha=1.0,
    facecolor="None",
    linewidth=1.0,
    linestyle="-",
):
    if ax is None:
        fig, ax = plt.subplots(figsize=(30, 30 * camera.num_pix[0] / camera.num_pix[1]))

    first = True
    for quad in quads:
        # transform to pixel coordinates
        coords_list = []
        for star in quad.objects:
            coords_pix = camera.transform_to_pixels(star.coords_skycam)
            coords_list.append(coords_pix)

        coords = np.array(coords_list).reshape(-1, 2)

        if first:
            ax.fill(
                coords[:, 1],
                coords[:, 0],
                color=color,
                alpha=alpha,
                facecolor=facecolor,
                linewidth=linewidth,
                linestyle=linestyle,
                label=label,
            )
            first = False
        else:
            ax.fill(
                coords[:, 1],
                coords[:, 0],
                color=color,
                alpha=alpha,
                facecolor=facecolor,
                linewidth=linewidth,
                linestyle=linestyle,
            )


def _linear_wcs_fit(params, lon, lat, x, y, w_obj):
    """
    Objective function for fitting linear terms.

    Parameters
    ----------
    params : array
        6 element array. First 4 elements are PC matrix, last 2 are CRPIX.
    lon, lat: array
        Sky coordinates.
    x, y: array
        Pixel coordinates
    w_obj: `~astropy.wcs.WCS`
        WCS object
    """
    cd = params[0:4]
    crpix = params[4:6]
    crval = params[6:8]

    w_obj.wcs.cd = ((cd[0], cd[1]), (cd[2], cd[3]))
    w_obj.wcs.crpix = crpix
    w_obj.wcs.crval = crval

    lon2, lat2 = w_obj.wcs_pix2world(x, y, 0)

    lat_resids = lat - lat2
    lon_resids = lon - lon2

    # In case the longitude has wrapped around
    lon_resids = np.mod(lon_resids - 180.0, 360.0) - 180.0

    resids = np.concatenate((lon_resids * np.cos(np.radians(lat)), lat_resids))

    return resids


def fit_wcs_from_points(
    xy,
    world_coords,
    proj_point="center",
    projection="TAN",
    sip_degree=None,
    fix_proj_point=True,
):
    """
    Borrowed from astropy.wcs.utils to allow for non-fixed projection point.
    """

    from scipy.optimize import least_squares
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    from astropy.wcs.utils import celestial_frame_to_wcs, _sip_fit
    from astropy.wcs.wcs import Sip

    xp, yp = xy
    try:
        lon, lat = world_coords.data.lon.deg, world_coords.data.lat.deg
    except AttributeError:
        unit_sph = world_coords.unit_spherical
        lon, lat = unit_sph.lon.deg, unit_sph.lat.deg

    # verify input
    if (type(proj_point) != type(world_coords)) and (proj_point != "center"):
        raise ValueError(
            "proj_point must be set to 'center', or an"
            + "`~astropy.coordinates.SkyCoord` object with "
            + "a pair of points."
        )

    use_center_as_proj_point = str(proj_point) == "center"

    if not use_center_as_proj_point:
        assert proj_point.size == 1

    proj_codes = [
        "AZP",
        "SZP",
        "TAN",
        "STG",
        "SIN",
        "ARC",
        "ZEA",
        "AIR",
        "CYP",
        "CEA",
        "CAR",
        "MER",
        "SFL",
        "PAR",
        "MOL",
        "AIT",
        "COP",
        "COE",
        "COD",
        "COO",
        "BON",
        "PCO",
        "TSC",
        "CSC",
        "QSC",
        "HPX",
        "XPH",
    ]
    if type(projection) == str:
        if projection not in proj_codes:
            raise ValueError(
                "Must specify valid projection code from list of "
                + "supported types: ",
                ", ".join(proj_codes),
            )
        # empty wcs to fill in with fit values
        wcs = celestial_frame_to_wcs(frame=world_coords.frame, projection=projection)
    else:  # if projection is not string, should be wcs object. use as template.
        wcs = copy.deepcopy(projection)
        wcs.cdelt = (1.0, 1.0)  # make sure cdelt is 1
        wcs.sip = None

    # Change PC to CD, since cdelt will be set to 1
    if wcs.wcs.has_pc():
        wcs.wcs.cd = wcs.wcs.pc
        wcs.wcs.__delattr__("pc")

    if (type(sip_degree) != type(None)) and (type(sip_degree) != int):
        raise ValueError("sip_degree must be None, or integer.")

    # set pixel_shape to span of input points
    wcs.pixel_shape = (xp.max() + 1 - xp.min(), yp.max() + 1 - yp.min())

    # determine CRVAL from input
    close = lambda l, p: p[np.argmin(np.abs(l))]
    if use_center_as_proj_point:  # use center of input points
        sc1 = SkyCoord(lon.min() * u.deg, lat.max() * u.deg)
        sc2 = SkyCoord(lon.max() * u.deg, lat.min() * u.deg)
        pa = sc1.position_angle(sc2)
        sep = sc1.separation(sc2)
        midpoint_sc = sc1.directional_offset_by(pa, sep / 2)
        wcs.wcs.crval = (midpoint_sc.data.lon.deg, midpoint_sc.data.lat.deg)
        wcs.wcs.crpix = ((xp.max() + xp.min()) / 2.0, (yp.max() + yp.min()) / 2.0)
    else:  # convert units, initial guess for crpix
        proj_point.transform_to(world_coords)
        wcs.wcs.crval = (proj_point.data.lon.deg, proj_point.data.lat.deg)
        wcs.wcs.crpix = (
            close(lon - wcs.wcs.crval[0], xp),
            close(lon - wcs.wcs.crval[1], yp),
        )

    # fit linear terms, assign to wcs
    # use (1, 0, 0, 1) as initial guess, in case input wcs was passed in
    # and cd terms are way off.
    # Use bounds to require that the fit center pixel is on the input image
    xpmin, xpmax, ypmin, ypmax = xp.min(), xp.max(), yp.min(), yp.max()
    if xpmin == xpmax:
        xpmin, xpmax = xpmin - 0.5, xpmax + 0.5
    if ypmin == ypmax:
        ypmin, ypmax = ypmin - 0.5, ypmax + 0.5

    p0 = np.concatenate(
        [wcs.wcs.cd.flatten(), wcs.wcs.crpix.flatten(), wcs.wcs.crval.flatten()]
    )

    args = (lon, lat, xp, yp, wcs)

    epsilon = 1e-10  # degrees
    bounds = [
        [-np.inf, -np.inf, -np.inf, -np.inf, xpmin, ypmin, -np.inf, -np.inf],
        [np.inf, np.inf, np.inf, np.inf, xpmax, ypmax, np.inf, np.inf],
    ]

    if fix_proj_point:
        # fix parameters by using very tight bounds
        # replace fitting by e.g. minuit, where parameters can be kept fixed?
        bounds[0][6] = np.min([wcs.wcs.crval[0], wcs.wcs.crval[0] + epsilon])
        bounds[1][6] = np.max([wcs.wcs.crval[0], wcs.wcs.crval[0] + epsilon])

        bounds[0][7] = np.min([wcs.wcs.crval[1], wcs.wcs.crval[1] + epsilon])
        bounds[1][7] = np.max([wcs.wcs.crval[1], wcs.wcs.crval[1] + epsilon])

    fit = least_squares(_linear_wcs_fit, p0, args=args, bounds=bounds)

    wcs.wcs.crpix = np.array(fit.x[4:6])
    wcs.wcs.cd = np.array(fit.x[0:4].reshape((2, 2)))
    wcs.wcs.crval = np.array(fit.x[6:8])

    # fit SIP, if specified. Only fit forward coefficients
    if sip_degree:
        degree = sip_degree
        if "-SIP" not in wcs.wcs.ctype[0]:
            wcs.wcs.ctype = [x + "-SIP" for x in wcs.wcs.ctype]

        coef_names = [
            f"{i}_{j}"
            for i in range(degree + 1)
            for j in range(degree + 1)
            if (i + j) < (degree + 1) and (i + j) > 1
        ]
        p0 = np.concatenate(
            (
                np.array(wcs.wcs.crpix),
                wcs.wcs.cd.flatten(),
                np.zeros(2 * len(coef_names)),
            )
        )

        fit = least_squares(
            _sip_fit,
            p0,
            args=(lon, lat, xp, yp, wcs, degree, coef_names),
            bounds=[
                [xpmin, ypmin] + [-np.inf] * (4 + 2 * len(coef_names)),
                [xpmax, ypmax] + [np.inf] * (4 + 2 * len(coef_names)),
            ],
        )
        coef_fit = (
            list(fit.x[6 : 6 + len(coef_names)]),
            list(fit.x[6 + len(coef_names) :]),
        )

        # put fit values in wcs
        wcs.wcs.cd = fit.x[2:6].reshape((2, 2))
        wcs.wcs.crpix = fit.x[0:2]

        a_vals = np.zeros((degree + 1, degree + 1))
        b_vals = np.zeros((degree + 1, degree + 1))

        for coef_name in coef_names:
            a_vals[int(coef_name[0])][int(coef_name[2])] = coef_fit[0].pop(0)
            b_vals[int(coef_name[0])][int(coef_name[2])] = coef_fit[1].pop(0)

        wcs.sip = Sip(
            a_vals,
            b_vals,
            np.zeros((degree + 1, degree + 1)),
            np.zeros((degree + 1, degree + 1)),
            wcs.wcs.crpix,
        )

    return wcs


def plot_quad_parameter_space(registration):
    """
    Plot all preselected and selected spot and star quads in
    (1) the L1/L0 vs L2/L1 parameter space
    (2) the L1/L0 vs quad circumference space
    """
    fig = plt.figure(figsize=(12, 8))

    gs = fig.add_gridspec(
        1, 2, left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.05, hspace=0.05
    )

    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 1], sharey=ax0)
    ax1.tick_params(axis="y", labelleft=False)

    quads_spots = registration.get_quads_spots(Status.PRESELECTED)
    invs_spots = np.array([q.invariants for q in quads_spots])
    mask_spots = np.array([q.has_status(Status.SELECTED) for q in quads_spots])

    quads_stars = registration.get_quads_stars(Status.PRESELECTED)
    invs_stars = np.array([q.invariants for q in quads_stars])
    mask_stars = np.array([q.has_status(Status.SELECTED) for q in quads_stars])

    # L1/L2 vs L0/L1
    ax0.plot(
        invs_stars[:, 0],
        invs_stars[:, 1],
        "1",
        color="gray",
        alpha=0.6,
        label=f"all catalog quads ({len(invs_stars)})",
    )
    ax0.plot(
        invs_spots[:, 0],
        invs_spots[:, 1],
        "o",
        fillstyle="none",
        label=f"all spot quads ({len(invs_spots)})",
    )

    # selected quads
    ax0.plot(
        invs_stars[mask_stars][:, 0],
        invs_stars[mask_stars][:, 1],
        "1",
        color="fuchsia",
        label=f"selected catalog quads ({sum(mask_stars)})",
    )
    ax0.plot(
        invs_spots[mask_spots][:, 0],
        invs_spots[mask_spots][:, 1],
        "o",
        color="fuchsia",
        fillstyle="none",
        label=f"selected spot quads ({sum(mask_spots)})",
    )

    # L1/L2 vs circumference
    ax1.plot(invs_stars[:, 2], invs_stars[:, 1], "1", color="gray", alpha=0.6)
    ax1.plot(invs_spots[:, 2], invs_spots[:, 1], "o", fillstyle="none")

    # selected quads
    ax1.plot(
        invs_stars[mask_stars][:, 2], invs_stars[mask_stars][:, 1], "1", color="fuchsia"
    )
    ax1.plot(
        invs_spots[mask_spots][:, 2],
        invs_spots[mask_spots][:, 1],
        "o",
        color="fuchsia",
        fillstyle="none",
    )

    # allowed quad phase space (from https://arxiv.org/pdf/1909.02946.pdf)
    x = np.linspace(1.1, 2.0, 100)
    y = 1 / (x - 1)
    ax0.plot(x, y, "k--", label="geometric limit")

    ax0.set_xlabel("L2/L1")
    ax0.set_ylabel("L1/L0")
    ax0.set_xlim((0.95, 2.0))
    ax0.set_ylim((0.95, 5.0))
    ax0.legend(loc="upper right")
    ax0.grid()

    ax1.set_xlabel("scaled quad circumference")
    ax1.set_ylim((0.95, 5.0))
    ax1.grid()

    return fig


def plot_quad_transformation_parameters(registration):
    """
    Plot distribution of similarity transformation parameters for preselected and selected quad matches:
    (1) rotation and scale factor between the quads
    (2) corner deviation between spots vs. averaged quad side length
    (3) corner deviation vs. scale factor
    """
    # get transformation parameters:
    # offset_x, offset_y, rotation, scale, convergence flag
    matched_quads = registration.get_quad_matches(Status.PRESELECTED)

    # rotation
    r = np.array(
        [m.transformation_properties[2].to_value(u.rad) for m in matched_quads]
    )
    # scale
    s = np.array([m.transformation_properties[3] for m in matched_quads])
    # quad circumference
    c = np.array([m.transformation_properties[6] for m in matched_quads])
    # relative corner deviation between spot and star quad
    rel_corner_err = np.array([m.transformation_properties[7] for m in matched_quads])

    # mask of selected matches
    mask_sel = np.array([m.has_status(Status.SELECTED) for m in matched_quads])
    mask_best = np.array([m.has_status(Status.BESTMATCH) for m in matched_quads])

    fig = plt.figure(figsize=(10, 10))

    label_pre = f"preselected quads ({len(r)})"
    label_sel = f"selected quads ({np.count_nonzero(mask_sel)})"
    label_best = f"best-matching quad ({np.count_nonzero(mask_best)})"

    ax1 = fig.add_subplot(221, projection="polar")
    num_bins = 200
    hist_r, bins = np.histogram(r, bins=num_bins)
    hist_r_selected, _ = np.histogram(r[mask_sel], bins=bins)
    bin_centres = (bins[1:] + bins[:-1]) / 2
    ax1.plot(bin_centres, hist_r, "-", color="lightgray")
    ax1.plot(bin_centres, hist_r_selected, "-")
    ax1.set_theta_zero_location("N", offset=0)

    ax0 = fig.add_subplot(222, projection="polar")
    ax0.scatter(r, np.log10(s), alpha=0.5, label=label_pre, color="lightgray")
    ax0.scatter(r[mask_sel], np.log10(s[mask_sel]), alpha=0.5, label=label_sel)
    ax0.plot(
        r[mask_best], np.log10(s[mask_best]), "P", color="tab:orange", label=label_best
    )
    ax0.set_rorigin(-3.0)
    ax0.set_rmin(-2)
    ax0.set_rmax(1)
    ax0.set_theta_zero_location("N", offset=0)

    ax2 = fig.add_subplot(223)
    ax2.scatter(c, rel_corner_err, alpha=0.5, label=label_pre, color="lightgray")
    ax2.scatter(c[mask_sel], rel_corner_err[mask_sel], alpha=0.5, label=label_sel)
    ax2.plot(
        c[mask_best],
        rel_corner_err[mask_best],
        "P",
        label=label_best,
        color="tab:orange",
    )
    ax2.set_xlabel("quad circumference")
    ax2.set_ylabel("corner deviation/circumference")
    ax2.set_yscale("log")
    ax2.grid()

    ax3 = fig.add_subplot(224)
    ax3.scatter(s, rel_corner_err, alpha=0.5, label=label_pre, color="lightgray")
    ax3.scatter(s[mask_sel], rel_corner_err[mask_sel], alpha=0.5, label=label_sel)
    ax3.plot(
        s[mask_best],
        rel_corner_err[mask_best],
        "P",
        label=label_best,
        color="tab:orange",
    )
    ax3.set_xlabel("scale factor")
    ax3.set_ylabel("corner deviation/circumference")
    ax3.set_yscale("log")
    ax3.legend()
    ax3.grid()

    plt.tight_layout()


def plot_angular_distance_radec(
    star_spot_match_list, exposure, plot_distance_squared=False
):
    """
    Plot (angular distance)**2 between matched stars and spots.
    """
    if plot_distance_squared:
        index = 2.0
        xlabel = r"angular distance squared (arcsecs$^2$)"
    else:
        index = 1.0
        xlabel = r"angular distance (arcsecs)"

    # select fitted stars and get their RADec coordinates
    stars_fitted = [
        s.star for s in star_spot_match_list if not s.spot.has_status(Status.OUTLIER)
    ]
    stars_fitted_coords_radec = SkyCoord([s.coords_radec for s in stars_fitted])

    # select fitted spots and transform their pixel coordinates to RADec,
    # using the best-fit result of the sky fit
    spots_fitted = [
        s.spot for s in star_spot_match_list if not s.spot.has_status(Status.OUTLIER)
    ]
    spots_fitted_coords_pix = np.array([s.coords_pix for s in spots_fitted])
    spots_fitted_coords_cam = exposure.camera.transform_to_camera(
        spots_fitted_coords_pix
    )
    spots_fitted_coords_radec = exposure.transform_to_sky(spots_fitted_coords_cam)

    angular_distance = stars_fitted_coords_radec.separation(
        spots_fitted_coords_radec
    ).to_value(u.arcsec)
    angular_distance.sort()

    n68 = int(np.floor(0.68 * len(angular_distance)))
    n95 = int(np.floor(0.95 * len(angular_distance)))

    r68 = angular_distance[n68]
    r95 = angular_distance[n95]

    fig, ax = plt.subplots(figsize=(10, 6), ncols=2)

    bins = np.linspace(0.0, np.max(angular_distance**index), 20)
    _, bins, _ = ax[0].hist(
        angular_distance**index,
        bins=bins,
        label=f"fitted stars ({len(spots_fitted)})",
    )

    # select fit outliers
    stars_outliers = [
        s.star for s in star_spot_match_list if s.spot.has_status(Status.OUTLIER)
    ]

    if len(stars_outliers) > 0:
        stars_outliers_coords_radec = SkyCoord([s.coords_radec for s in stars_outliers])

        # select fitted spots and transform their pixel coordinates to RADec,
        # using the best-fit result of the sky fit
        spots_outliers = [
            s.spot for s in star_spot_match_list if s.spot.has_status(Status.OUTLIER)
        ]
        spots_outliers_coords_pix = np.array([s.coords_pix for s in spots_outliers])
        spots_outliers_coords_cam = exposure.camera.transform_to_camera(
            spots_outliers_coords_pix
        )
        spots_outliers_coords_radec = exposure.transform_to_sky(
            spots_outliers_coords_cam
        )

        angular_distance_outliers = stars_outliers_coords_radec.separation(
            spots_outliers_coords_radec
        ).to_value(u.arcsec)

        ax[0].hist(
            angular_distance_outliers**index,
            bins=bins,
            label=f"fit outliers ({len(stars_outliers)})",
        )

    y_lim = ax[0].get_ylim()
    ax[0].plot([r68**index] * 2, y_lim, "-", label="68% containment")
    ax[0].plot([r95**index] * 2, y_lim, "--", label="95% containment")

    ax[0].set_xlabel(xlabel)
    ax[0].set_ylabel("number of stars")
    ax[0].grid()
    ax[0].legend()

    bin_max = np.max(angular_distance**index)

    bins = np.logspace(-1, np.log10(bin_max), 20)
    _, bins, _ = ax[1].hist(angular_distance**index, bins=bins)

    if len(stars_outliers) > 0:
        ax[1].hist(angular_distance_outliers**index, bins=bins)

    y_lim = ax[1].get_ylim()
    ax[1].plot([r68**index] * 2, y_lim, "-")
    ax[1].plot([r95**index] * 2, y_lim, "--")

    ax[1].set_xlabel(xlabel)
    ax[1].grid()
    ax[1].set_xscale("log")

    plt.tight_layout()

    return r68 * u.arcsec, r95 * u.arcsec


def plot_image_fit(quad_match, exposure):
    """
    Plot the exposure image, with fitted stars overlaid.
    """
    star_spot_match_list = quad_match.star_spot_match_list

    stars_fitted = [
        s.star for s in star_spot_match_list if not s.spot.has_status(Status.OUTLIER)
    ]
    stars_fitted_coords = SkyCoord([s.coords_radec for s in stars_fitted])
    stars_fitted_coords_pix = exposure.transform_to_camera(
        stars_fitted_coords, to_pixels=True
    )

    stars_outliers = [
        s.star for s in star_spot_match_list if s.spot.has_status(Status.OUTLIER)
    ]
    has_outliers = len(stars_outliers) > 0
    if has_outliers:
        stars_outliers_coords = SkyCoord([s.coords_radec for s in stars_outliers])
        stars_outliers_coords_pix = exposure.transform_to_camera(
            stars_outliers_coords, to_pixels=True
        )

    spots_fitted = [
        s.spot for s in star_spot_match_list if not s.spot.has_status(Status.OUTLIER)
    ]
    spots_fitted_coords_pix = np.array([s.coords_pix for s in spots_fitted])

    delta_fitted_pix = np.array(stars_fitted_coords_pix - spots_fitted_coords_pix)
    delta_fitted = delta_fitted_pix * exposure.camera.pixel_angle

    if has_outliers:
        spots_outliers = [
            s.spot for s in star_spot_match_list if s.spot.has_status(Status.OUTLIER)
        ]
        spots_outliers_coords_pix = np.array([s.coords_pix for s in spots_outliers])

        delta_outliers_pix = np.array(
            stars_outliers_coords_pix - spots_outliers_coords_pix
        )
        delta_outliers = delta_outliers_pix * exposure.camera.pixel_angle

    fig = plt.figure(figsize=(14, 14))

    gs = GridSpec(2, 2, width_ratios=[4, 1], height_ratios=[1, 1])

    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1])
    ax2 = fig.add_subplot(gs[2])
    ax3 = fig.add_subplot(gs[3])

    vmax = 20

    plot_exposure(exposure, ax=ax0)
    s = ax0.scatter(
        stars_fitted_coords_pix[:, 1],
        stars_fitted_coords_pix[:, 0],
        s=50 * np.abs(delta_fitted_pix[:, 0]),
        c=delta_fitted[:, 0],
        cmap="coolwarm",
        vmin=-vmax,
        vmax=vmax,
        alpha=0.5,
        label=f"fitted stars ({len(stars_fitted_coords_pix)})",
    )

    ax0.plot(
        spots_fitted_coords_pix[:, 1],
        spots_fitted_coords_pix[:, 0],
        "wo",
        fillstyle="none",
        label=f"fitted spots ({len(spots_fitted_coords_pix)})",
    )

    if has_outliers:
        ax0.scatter(
            stars_outliers_coords_pix[:, 1],
            stars_outliers_coords_pix[:, 0],
            s=50 * np.abs(delta_outliers_pix[:, 0]),
            c=delta_outliers[:, 0],
            cmap="coolwarm",
            vmin=-vmax,
            vmax=vmax,
            alpha=0.5,
            label=f"outliers stars ({len(stars_outliers_coords_pix)})",
        )

        ax0.plot(
            spots_outliers_coords_pix[:, 1],
            spots_outliers_coords_pix[:, 0],
            "o",
            fillstyle="none",
            color="cyan",
            label=f"outliers spots ({len(spots_outliers_coords_pix)})",
        )

    plot_quads(
        [quad_match.spot_quad],
        camera=exposure.camera,
        ax=ax0,
        color="white",
        linestyle="--",
        label="best-matched quad",
    )

    ax0.set_aspect("equal")
    ax0.set_ylabel("y position (pixels)")
    ax0.set_ylabel("x position (pixels)")
    ax0.set_title("x deviation", loc="left")
    ax0.legend()

    ax0.set_xlim((0, exposure.camera.num_pix[1]))
    ax0.set_ylim((0, exposure.camera.num_pix[0]))

    cbar = fig.colorbar(s, ax=ax0, location="right", shrink=0.8)
    cbar.set_label("x deviation (arcsec)")

    rms_x = np.std(delta_fitted[:, 0])
    ax1.hist(delta_fitted[:, 0].to_value(u.arcsec), label=f"fitted (RMS: {rms_x:.1f}")
    if has_outliers:
        ax1.hist(
            delta_outliers[:, 0].to_value(u.arcsec), histtype="step", label="outliers"
        )
    ax1.set_xlabel("x deviation (arcsec)")
    ax1.legend()

    plot_exposure(exposure, ax=ax2)
    s = ax2.scatter(
        stars_fitted_coords_pix[:, 1],
        stars_fitted_coords_pix[:, 0],
        s=50 * np.abs(delta_fitted_pix[:, 1]),
        c=delta_fitted[:, 1],
        cmap="coolwarm",
        vmin=-vmax,
        vmax=vmax,
        alpha=0.5,
    )

    ax2.plot(
        spots_fitted_coords_pix[:, 1],
        spots_fitted_coords_pix[:, 0],
        "wo",
        fillstyle="none",
    )

    if has_outliers:
        ax2.scatter(
            stars_outliers_coords_pix[:, 1],
            stars_outliers_coords_pix[:, 0],
            s=50 * np.abs(delta_outliers_pix[:, 1]),
            c=delta_outliers[:, 0],
            cmap="coolwarm",
            vmin=-vmax,
            vmax=vmax,
            alpha=0.5,
        )

        ax2.plot(
            spots_outliers_coords_pix[:, 1],
            spots_outliers_coords_pix[:, 0],
            "o",
            fillstyle="none",
            color="cyan",
        )

    plot_quads(
        [quad_match.spot_quad],
        camera=exposure.camera,
        ax=ax2,
        color="white",
        linestyle="--",
    )
    ax2.set_aspect("equal")
    ax2.set_xlabel("y position (pixels)")
    ax2.set_ylabel("x position (pixels)")
    ax2.set_title("y deviation", loc="left")

    ax2.set_xlim((0, exposure.camera.num_pix[1]))
    ax2.set_ylim((0, exposure.camera.num_pix[0]))

    cbar = fig.colorbar(s, ax=ax2, location="right", shrink=0.8)
    cbar.set_label("y deviation (arcsec)")

    rms_y = np.std(delta_fitted[:, 1])
    ax3.hist(delta_fitted[:, 1].to_value(u.arcsec), label=f"fitted (RMS: {rms_y:.1f})")
    if has_outliers:
        ax3.hist(
            delta_outliers[:, 1].to_value(u.arcsec), histtype="step", label="outliers"
        )

    ax3.set_xlabel("y deviation (arcsec)")
    ax3.legend()

    plt.tight_layout()

    return fig
