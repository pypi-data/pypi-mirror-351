import numpy as np
import matplotlib.pyplot as plt

import astropy.units as u
from astropy.coordinates import SkyCoord, AltAz


def plot_pointing_models(model_list, plot_difference=False, subtract_mean=False):
    """
    Plot the pointing corrections on the sky.
    model_list is a list of PointingModel objects.
    If plot_difference is True, the difference w.r.t.
    the first model is plotted.

    returns references to the two figures.
    """

    if not isinstance(model_list, (list, tuple)):
        model_list = [model_list]

    print(f"Plotting {len(model_list)} pointing models.")

    # construct grid for arrow plotting
    az_lin = np.linspace(-150.0, 180.0, 12) * u.deg
    alt_lin = np.linspace(15.0, 75.0, 5) * u.deg
    az, alt = np.meshgrid(az_lin, alt_lin)

    nom_altaz = SkyCoord(az, alt, frame=AltAz)

    # 20 arcsec is 1 deg on the standard plot, 2 arcsec for the difference plot
    scale_factor = 3600.0 / 20
    if plot_difference:
        scale_factor *= 10.0

    #
    # Polar plot, zenith at the pole
    #
    fig0 = plt.figure(figsize=(10, 10))
    ax0 = fig0.add_subplot(111, projection="polar")
    ax0.set_theta_zero_location("N")
    ax0.set_theta_direction(-1)
    ax0.set_rlim(0, 90.0)
    ax0.set_thetagrids(
        np.arange(0, 360, 30),
        labels=[
            "N",
            r"$30^\circ$",
            r"$60^\circ$",
            "E",
            r"$120^\circ$",
            r"$150^\circ$",
            "S",
            r"$-150^\circ$",
            r"$-120^\circ$",
            "W",
            r"$-60^\circ$",
            r"$-30^\circ$",
        ],
    )
    ax0.set_rgrids(np.arange(15, 90, 15))
    ax0.grid(True)

    #
    # Mollweide projection
    #
    fig1 = plt.figure(figsize=(10, 10))
    ax1 = fig1.add_subplot(111, projection="mollweide")
    ax1.grid(True)
    ax1.set_xticklabels(
        [
            r"$-150^\circ$",
            r"$-120^\circ$",
            "W",
            r"$-60^\circ$",
            r"$-30^\circ$",
            "N",
            r"$30^\circ$",
            r"$60^\circ$",
            "E",
            r"$120^\circ$",
            r"$150^\circ$",
        ]
    )

    u_ref, v_ref = 0, 0
    for idx, model in enumerate(model_list):
        corrected_altaz = model.get_corrected_pointing(nom_altaz)

        u_diff = corrected_altaz.az - nom_altaz.az
        v_diff = corrected_altaz.alt - nom_altaz.alt

        # wrap at 360 deg
        u_diff[u_diff > 180 * u.deg] -= 360 * u.deg

        if plot_difference:
            u_diff -= u_ref
            v_diff -= v_ref

        if subtract_mean:
            u_diff -= np.mean(u_diff)
            v_diff -= np.mean(v_diff)

        # keep this model as reference for the next model
        u_ref = np.copy(u_diff)
        v_ref = np.copy(v_diff)

        color = f"C{idx}"
        label = None

        if plot_difference:
            if idx == 0:
                title = str(
                    f"telescope pointing deviation (difference to model from {model.valid_from})\n"
                )
                title += "(arrow scale: 2 arcsec/deg)"

            else:
                label = f"model {model.uuid}"

        else:
            title = "telescope pointing deviation (full model)\n"
            title += "(arrow scale: 20 arcsec/deg)"
            label = f"model {model.uuid}"

        # Polar plot
        ax0.quiver(
            az.to_value(u.rad),
            90.0 - alt.to_value(u.deg),
            u_diff.to_value(u.rad),
            -v_diff.to_value(u.deg),
            angles="xy",
            scale_units="xy",
            scale=1.0 / scale_factor,
            color=color,
            width=0.003,
            headwidth=3.0,
            headlength=5.0,
            label=label,
        )

        # plot direction of the azimuth axis
        # if plot_difference is False:
        #     modelparameters = model.get_parameters()
        #     azm_amplitude = modelparameters[5] * scale_factor
        #     azm_phase = (
        #         modelparameters[6] + 90.0 * u.deg
        #     )  # do we really have to add 90deg to make it work?
        #
        #     if azm_amplitude < 0:
        #         azm_amplitude *= -1
        #         azm_phase += 180 * u.deg
        #
        #     ax0.plot(azm_phase.to_value(u.rad), azm_amplitude.to_value(u.deg), marker="P")

        # Mollweide projection
        ax1.quiver(
            az.to_value(u.rad),
            alt.to_value(u.rad),
            u_diff.to_value(u.rad),
            v_diff.to_value(u.rad),
            angles="xy",
            scale_units="xy",
            scale=1.0 / scale_factor,
            color=color,
            width=0.003,
            headwidth=3.0,
            headlength=5.0,
            label=label,
        )

    ax0.legend(loc="lower right")
    ax1.legend(loc="lower right")
    ax0.set_title(title)
    ax1.set_title(title)

    plt.tight_layout()
    plt.show()
    return fig0, fig1
