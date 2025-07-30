import numpy as np
import matplotlib.pyplot as plt

from astropy.coordinates import Angle, SkyCoord
import astropy.units as u


def plot_camera_frame(
    camera, coords=None, camera_pointing_altaz=None, marker_size=1, **kwargs
):
    """
    Plots the chip frame of a PointingCamera object, with useful curves to show
    altitude/azimuth projections, camera rotation and distortions.
    Can also be used to display a set of coordinates on the chip.

    :param PointingCamera camera: PointingCamera object
    :param array(SkyCoord) coords: coordinates to plot into frame. Coordinates
    must be given in the chip coordinate (SkyCameraFrame) system
    ToDo camera_pointing_altaz must not be none
    :param array(float) marker_size: individual marker size for each coordinate

    further parameters (kwargs):
    :chip_centre: Plot the chip centre. True by default.
    :fov_centre: Plot the Fov centre. True by default.
    :chip_edges: Plot the chip edges. True by default.
    :alt_proj: Plot altitude lines. False by default.
    :az_proj: Plot azimuth lines. False by default.
    :proj_fov: Plot projected FoV circles. False by default.
    :chip_fov: Plot physical chip FoV circle. False by default.

    :returns: plot handles (fig, ax)
    """

    # parse plotting options
    plot_chip_centre = kwargs.get("chip_centre", True)
    plot_fov_centre = kwargs.get("fov_centre", True)
    plot_chip_edges = kwargs.get("chip_edges", True)
    plot_alt_proj = kwargs.get("alt_proj", False)
    plot_az_proj = kwargs.get("az_proj", False)
    plot_proj_fov = kwargs.get("proj_fov", False)
    plot_chip_fov = kwargs.get("chip_fov", False)

    # chip pointing
    az0 = camera_pointing_altaz.az
    alt0 = camera_pointing_altaz.alt

    # centre of the FoV
    centre_fov = camera.project_into(camera_pointing_altaz, camera_pointing_altaz)
    # TODO it doesn't make sense to me to give tow times the same parameter

    # chip centre
    centre_ccd = np.array([0.0, 0.0])

    # CCD edges
    cs = camera.chip_size.to("m").value
    ccd_corners = np.array(
        [
            [cs[0] / 2, cs[1] / 2],
            [cs[0] / 2, -cs[1] / 2],
            [-cs[0] / 2, -cs[1] / 2],
            [-cs[0] / 2, cs[1] / 2],
            [cs[0] / 2, cs[1] / 2],
        ]
    )

    # azimuth and altitude lines
    num_points = 100
    num_lines = 7

    fov = camera.fov.to("deg")

    # equal-altitude lines
    d_alt = Angle(np.linspace(-fov[0].value / 2, fov[0].value / 2, num_points) * u.deg)
    d_az = Angle(np.linspace(-fov[1].value / 2, fov[1].value / 2, num_lines) * u.deg)

    line_ccd_alt = []
    for angle in d_az:
        coords_alt = SkyCoord(az=az0 + angle, alt=alt0 + d_alt, frame="altaz")
        ccd_alt = camera.project_into(coords_alt, camera_pointing_altaz)

        line_ccd_alt.append(ccd_alt)

    # equal-azimuth lines
    d_az = Angle(
        np.linspace(
            -fov[1].value / 2 / np.cos(alt0),
            fov[1].value / 2 / np.cos(alt0),
            num_points,
        )
        * u.deg
    )
    d_alt = Angle(np.linspace(-fov[0].value / 2, fov[0].value / 2, num_lines) * u.deg)

    line_ccd_az = []
    for angle in d_alt:
        coords_az = SkyCoord(az=az0 + d_az, alt=alt0 + angle, frame="altaz")
        ccd_az = camera.project_into(coords_az, camera_pointing_altaz)

        line_ccd_az.append(ccd_az)

    # projected circles of FoV
    position_angle = np.linspace(0, 360, 100) * u.deg
    circle_radius_long = fov[1] / 2
    circle_radius_small = fov[0] / 2

    circle_coords_long = camera_pointing_altaz.directional_offset_by(
        position_angle, circle_radius_long
    )
    circle_ccd_long = camera.project_into(circle_coords_long, camera_pointing_altaz)

    circle_coords_small = camera_pointing_altaz.directional_offset_by(
        position_angle, circle_radius_small
    )
    circle_ccd_small = camera.project_into(circle_coords_small, camera_pointing_altaz)

    # cartesian circle for comparison
    radius = cs[1] / 2
    circle_ccd_cartesian_x = radius * np.sin(position_angle)
    circle_ccd_cartesian_y = radius * np.cos(position_angle)

    # plot
    fig, ax = plt.subplots(figsize=(10, 10 * cs[0] / cs[1]))

    az_label = "az projection (alt={:.1f}, rot={:.1f})".format(alt0, camera.rotation)
    alt_label = "alt projection (az={:.1f}, rot={:.1f})".format(az0, camera.rotation)

    # plot equal-altitude lines
    if plot_alt_proj:
        for idx, ccd_alt in enumerate(line_ccd_alt):
            if idx == len(line_ccd_alt) // 2:
                ax.plot(ccd_alt.y, ccd_alt.x, "-", label=alt_label, color="k")
            else:
                ax.plot(ccd_alt.y, ccd_alt.x, "-", color="k")

    # plot equal-azimuth lines
    if plot_az_proj:
        for idx, ccd_az in enumerate(line_ccd_az):
            if idx == len(line_ccd_az) // 2:
                ax.plot(ccd_az.y, ccd_az.x, "--", label=az_label, color="k")
            else:
                ax.plot(ccd_az.y, ccd_az.x, "--", color="k")

    # projected FoV
    if plot_proj_fov:
        ax.plot(
            circle_ccd_long.y,
            circle_ccd_long.x,
            "-",
            label="projected FoV (chip long side, {:.1f})".format(fov[0]),
        )
        ax.plot(
            circle_ccd_small.y,
            circle_ccd_small.x,
            "-",
            label="projected FoV (chip small side, {:.1f})".format(fov[1]),
        )

    # physical chip FoV
    if plot_chip_fov:
        ax.plot(
            circle_ccd_cartesian_x,
            circle_ccd_cartesian_y,
            ":",
            label="chip FoV (chip long side)",
        )

    # chip edges
    if plot_chip_edges:
        ax.plot(
            ccd_corners[:, 1], ccd_corners[:, 0], "-", color="gray", label="chip edges"
        )

    # FoV centre
    if plot_fov_centre:
        ax.plot(
            centre_fov.y,
            centre_fov.x,
            "P",
            markersize=10,
            color="r",
            label="optical axis (ox={:.4f}, oy={:.4f})".format(
                camera.offset[0].to("m"), camera.offset[1].to("m")
            ),
        )

    # chip centre
    if plot_chip_centre:
        ax.plot(
            centre_ccd[1],
            centre_ccd[0],
            "P",
            markersize=10,
            fillstyle="none",
            color="k",
            label="chip origin",
        )

    # coordinates:
    try:
        ax.plot(coords.y, coords.x, "o")
    except:
        pass

    ax.set_xlabel(r"$y_\mathrm{CCD}$ [m]")
    ax.set_ylabel(r"$x_\mathrm{CCD}$ [m]")
    ax.set_xlim(-cs[1] / 2 * 1.1, cs[1] / 2 * 1.1)
    ax.set_ylim(-cs[0] / 2 * 1.1, cs[0] / 2 * 1.1)
    ax.legend(loc="lower right")
    ax.grid()

    return (fig, ax)


def plot_distortion_correction(camera, plot_inverse=False, ax=None):
    """
    Plot the distortion correction model stored in the camera object
    """

    x = np.linspace(0, camera.num_pix[0], 10).reshape(-1, 1)
    y = np.linspace(0, camera.num_pix[1], 10).reshape(-1, 1)
    xx, yy = np.meshgrid(x, y)

    coords = np.concatenate((xx.reshape(-1, 1), yy.reshape(-1, 1)), axis=1)
    coords_relative = coords - camera.chip_centre

    if plot_inverse:
        correction = (
            camera.distortion_correction.apply_inverse_correction(coords_relative)
            - coords_relative
        )
    else:
        correction = (
            camera.distortion_correction.apply_correction(coords_relative)
            - coords_relative
        )

    if ax is None:
        fig, ax = plt.subplots()

    ax.quiver(yy, xx, correction[:, 1], correction[:, 0])

    return ax
