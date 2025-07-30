import numpy as np
import matplotlib.pyplot as plt

from astropy.coordinates import SkyCoord


def plot_exposure(
    exposure,
    ax=None,
    label="image",
    cmap="binary",
    norm=None,
    aspect="equal",
    interpolation=None,
    alpha=None,
    vmin=None,
    vmax=None,
    origin="lower",
    **kwargs,
):
    """
    Plot an exposure object (image).
    """

    if ax is None:
        fig, ax = plt.subplots(
            figsize=(20, 20 * exposure.camera.num_pix[0] / exposure.camera.num_pix[1])
        )
        ax.set_aspect("equal")

    if (vmin is None) or (vmax is None):
        m = exposure.image.mean()
        s = exposure.image.std()
        vmin = m - 2 * s
        vmax = m + 2 * s

    im = ax.imshow(
        exposure.image,
        label=label,
        cmap=cmap,
        norm=norm,
        aspect=aspect,
        interpolation=interpolation,
        alpha=alpha,
        vmin=vmin,
        vmax=vmax,
        origin=origin,
        **kwargs,
    )

    ax.set_xlabel(r"$y_\mathrm{camera}$ (pix)")
    ax.set_ylabel(r"$x_\mathrm{camera}$ (pix)")

    ax.set_xlim((0, exposure.image.shape[1]))
    ax.set_ylim((0, exposure.image.shape[0]))

    return im


def plot_coords(
    coords,
    camera=None,
    ax=None,
    label=None,
    marker="o",
    color="g",
    markersize=12,
    alpha=1.0,
    print_coordinates=False,
):
    if ax is None:
        fig, ax = plt.subplots(figsize=(30, 30 * camera.num_pix[0] / camera.num_pix[1]))
        ax.set_aspect("equal")

    ax.plot(
        coords[:, 1],
        coords[:, 0],
        label=label,
        marker=marker,
        color=color,
        markersize=markersize,
        linestyle="none",
        fillstyle="none",
        alpha=alpha,
    )

    if print_coordinates:
        for i in range(len(coords)):
            xp, yp = coords[i, 0], coords[i, 1]

            radius = 20
            ax.text(
                yp + 0.5 * radius,
                xp - 1.5 * radius,
                "({:.1f}, {:.1f})".format(xp, yp),
                size=6,
                color=color,
            )

    return ax


def plot_spots(
    spotlist,
    camera=None,
    ax=None,
    label=None,
    radius=15,
    color="r",
    alpha=1.0,
    print_coordinates=False,
):
    if ax is None:
        fig, ax = plt.subplots(figsize=(30, 30 * camera.num_pix[0] / camera.num_pix[1]))
        ax.set_aspect("equal")

    coords_x = spotlist["coord_x"]
    coords_y = spotlist["coord_y"]

    ax.plot(
        coords_y,
        coords_x - radius,
        color=color,
        marker="|",
        linestyle="None",
        alpha=alpha,
    )
    ax.plot(
        coords_y + radius,
        coords_x,
        color=color,
        marker="_",
        linestyle="None",
        alpha=alpha,
        label=label,
    )
    ax.plot(
        coords_y,
        coords_x + radius,
        color=color,
        marker="|",
        linestyle="None",
        alpha=alpha,
    )
    ax.plot(
        coords_y - radius,
        coords_x,
        color=color,
        marker="_",
        linestyle="None",
        alpha=alpha,
    )

    if print_coordinates:
        for i in range(len(coords_x)):
            xp, yp = coords_x[i], coords_y[i]

            ax.text(
                yp + 0.5 * radius,
                xp - 1.5 * radius,
                "({:.1f}, {:.1f})".format(xp, yp),
                size=6,
                color=color,
            )

    return ax


def plot_stars(
    stars,
    exposure=None,
    wcs=None,
    ax=None,
    label=None,
    color="g",
    alpha=1.0,
    radius=20,
    print_coordinates=True,
    clip_to_chip=False,
):
    if ax is None:
        fig, ax = plt.subplots(figsize=(30, 30 * camera.num_pix[0] / camera.num_pix[1]))
        ax.set_aspect("equal")

    # transform to pixel coordinates

    if isinstance(stars, SkyCoord):
        coords_skycam = stars.transform_to(exposure.skycameraframe)
        coords_pix = exposure.camera.transform_to_pixels(coords_skycam)
        coords_radec = stars

    elif isinstance(stars, list):
        coords_pix_list = []
        coords_radec_list = []
        for star in stars:
            if wcs is None:
                coords_skycam = star.coords_radec.transform_to(exposure.skycameraframe)
                coords_pix = exposure.camera.transform_to_pixels(coords_skycam)
            else:
                c = star.coords_radec.to_pixel(wcs)
                coords_pix = [c[1], c[0]]

            coords_pix_list.append(coords_pix)
            coords_radec_list.append(star.coords_radec)

        coords_pix = np.array(coords_pix_list).reshape(-1, 2)
        coords_radec = SkyCoord(coords_radec_list)

    if clip_to_chip:
        mask = exposure.camera.clip_to_chip(coords_pix)
        print(mask.shape)
        coords_pix = coords_pix[mask]
        coords_radec = coords_radec[mask.flatten()]

    ax.plot(
        coords_pix[:, 1],
        coords_pix[:, 0],
        marker="o",
        color=color,
        fillstyle="none",
        linestyle="none",
        alpha=1.0,
        label=label,
    )

    # plot RADec and pixel positions of the stars
    if print_coordinates:
        for i in range(len(coords_pix)):
            xp, yp = coords_pix[i, 0], coords_pix[i, 1]

            circ = plt.Circle(
                (yp, xp), radius=radius, fill=False, edgecolor=color, linestyle="--"
            )
            ax.add_patch(circ)

            ra = coords_radec[i].ra
            ra_str = "{:.0f}h{:.0f}m{:.0f}s".format(ra.hms[0], ra.hms[1], ra.hms[2])

            dec = coords_radec[i].dec
            dec_str = "{:.0f}d{:.0f}m{:.0f}s".format(dec.dms[0], dec.dms[1], dec.dms[2])

            if wcs is None:
                ax.text(
                    yp + radius,
                    xp + 0.3 * radius,
                    "({:.1f}, {:.1f})".format(xp, yp),
                    size=6,
                    color=color,
                )
                ax.text(
                    yp + 1.2 * radius,
                    xp - 0.6 * radius,
                    "(" + ra_str + ", " + dec_str + ")",
                    size=6,
                    color=color,
                )
            else:
                ax.text(
                    yp + 0.5 * radius,
                    xp + 1.5 * radius,
                    "({:.1f}, {:.1f})".format(xp, yp),
                    size=6,
                    color=color,
                )

    return ax


def plot_coordinates_altaz(coords):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="hammer")

    try:
        az_pos = coords.az.wrap_at(180 * u.deg)
        alt_pos = coords.alt
        ax.scatter(az_pos.radian, alt_pos.radian, marker=".", label="star positions")
    except Exception as e:
        print("problem in plotting", e)

    ax.set_xticklabels(
        ["14h", "16h", "18h", "20h", "22h", "0h", "2h", "4h", "6h", "8h", "10h"]
    )
    ax.grid(True)
    ax.set_xlabel("azimuth")
    ax.set_ylabel("altitude")
    ax.legend()


def plot_coordinates_radec(coords):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="hammer")

    try:
        ra_pos = coords.ra.wrap_at(180 * u.deg)
        dec_pos = coords.dec
        ax.scatter(ra_pos.radian, dec_pos.radian, marker=".", label="star positions")
    except:
        pass

    ax.set_xticklabels(
        ["14h", "16h", "18h", "20h", "22h", "0h", "2h", "4h", "6h", "8h", "10h"]
    )
    ax.grid(True)
    ax.set_xlabel("right ascension")
    ax.set_ylabel("declination")
    ax.legend()
