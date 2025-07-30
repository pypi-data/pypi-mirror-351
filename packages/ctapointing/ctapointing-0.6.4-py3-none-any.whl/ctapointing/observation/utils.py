import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from matplotlib import animation

from astropy.coordinates import Angle
import astropy.units as u


def plot_observations_altaz(observations):
    """
    Plot the target distribution of a list of PointingObservations

    Parameters
    ----------
    observation: iterable of type PointingObservation
        observation pland or list of PointingObservations

    Returns
    -------
    axes object
    """
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection="hammer")

    coords_az = []
    coords_alt = []
    for obs in observations:
        coords = obs.target_pos_altaz
        coords_az.append(coords.az)
        coords_alt.append(coords.alt)

    coords_az = Angle(coords_az).wrap_at(180 * u.deg)
    coords_alt = Angle(coords_alt)

    ax.scatter(
        coords_az.radian,
        coords_alt.radian,
        marker=".",
        cmap=cm.Blues,
        c=range(len(coords_az)),
        label="previous targets",
    )
    ax.scatter(
        coords_az[-1].radian,
        coords_alt[-1].radian,
        marker="*",
        color="tab:Orange",
        label="last target",
    )
    ax.plot(coords_az.radian, coords_alt.radian, color="grey", lw=0.2, alpha=0.5)

    ax.grid()
    ax.legend(loc="lower right")

    return ax


def create_animation_altaz(observations):
    """
    Creates a matplotlib.animation object that shows the
    selected targets one after the other.

    Parameters
    ----------
    observations: iterable of type PointingObservations
        observation plan or list of PointingObservations

    Returns
    -------
    reference to matplotlib.animation
    """

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection="hammer")

    coords_az = []
    coords_alt = []
    for obs in observations:
        coords = obs.target_pos_altaz
        coords_az.append(coords.az)
        coords_alt.append(coords.alt)

    coords_az = Angle(coords_az).wrap_at(180 * u.deg)
    coords_alt = Angle(coords_alt)

    def update_frame(n):
        coords = np.array([coords_az[: n + 1].radian, coords_alt[: n + 1].radian]).T
        scat1.set_offsets(coords)
        scat1.set_facecolors(cm.Blues(colors.Normalize()(range(n))))

        scat2.set_offsets(coords[n])

        plt1.set_data(coords[:, 0], coords[:, 1])

        return (scat1, scat2, plt1)

    scat1 = ax.scatter([], [], marker=".", label="previous targets")
    scat2 = ax.scatter([], [], marker="*", color="tab:Orange", label="last target")

    (plt1,) = ax.plot([0], [0], color="grey", lw=1.0, alpha=0.2)

    ax.grid()
    ax.legend(loc="lower right")

    anim = animation.FuncAnimation(
        fig,
        update_frame,
        frames=len(observations),
        interval=500,
        blit=True,
        repeat=False,
    )

    return anim


def plot_observations_projection(observations):
    """
    Plot altitude and azimuth projections of a list of PointingObservations

    Parameters
    ----------
    observation_list: iterable of type PointingObservation
        ObservationPlan or list of Pointing Observations

    Returns
    -------
    array of axes objects
    """

    fig, ax = plt.subplots(ncols=2)

    coords_az = []
    coords_alt = []
    for obs in observations:
        coords = obs.target_pos_altaz
        coords_az.append(coords.az)
        coords_alt.append(coords.alt)

    coords_az = Angle(coords_az).wrap_at(180 * u.deg)
    coords_alt = Angle(coords_alt)

    nbins = 12
    az_hist, az_edges = np.histogram(
        coords_az.to_value(u.deg),
        bins=np.linspace(-180.0, 180.0, nbins),
    )
    az_bins = (az_edges[1:] + az_edges[:-1]) / 2

    cos_zenith = np.cos(90.0 * u.deg - coords_alt)
    cos_zenith_min = np.min(cos_zenith)
    cos_zenith_max = np.max(cos_zenith)

    cos_zenith_bins = np.linspace(cos_zenith_min, cos_zenith_max, nbins)
    cos_zenith_binwidth = (cos_zenith_bins[1] - cos_zenith_bins[0]) / 2

    cos_zenith_hist, cos_zenith_edges = np.histogram(
        cos_zenith,
        bins=cos_zenith_bins,
    )
    cos_zenith_bin_centres = (cos_zenith_edges[1:] + cos_zenith_edges[:-1]) / 2

    hist_max = max(np.max(az_hist), np.max(cos_zenith_hist)) * 1.2

    ax[0].errorbar(
        az_bins, az_hist, np.sqrt(az_hist), (az_edges[1:] - az_edges[:-1]) / 2, fmt="o"
    )

    ax[0].grid()
    ax[0].set_xlabel("azimuth (deg)")
    ax[0].set_ylabel("number of targets")
    ax[0].set_ylim((0, hist_max))

    ax[1].errorbar(
        cos_zenith_bin_centres,
        cos_zenith_hist,
        np.sqrt(cos_zenith_hist),
        cos_zenith_binwidth,
        fmt="o",
    )

    ax[1].grid()
    ax[1].set_xlabel("cos(zenith distance)")
    ax[1].set_ylim((0, hist_max))

    return ax
