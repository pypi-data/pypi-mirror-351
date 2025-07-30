import os
import logging

from astropy.table import Table, Column
from astropy.coordinates import SkyCoord, Angle
import astropy.units as u

import matplotlib.pyplot as plt

log = logging.getLogger(__name__)


class Catalog:
    """
    General class to construct a star catalog from a raw data source (such as file
    or database), to write catalog parameters into an astropy table and to write
    the table to/read it from hdf5 files.
    """

    def __init__(
        self, create_from_database=False, filename=None, min_mag=-12.0, max_mag=10.0
    ):
        self._filename = filename
        self.__pathname = "star_catalog"
        self.min_mag = min_mag
        self.max_mag = max_mag
        self.table = None
        self.table_selected = None

        if create_from_database:
            self._create_from_database()
            self.__write_to_file()
        else:
            self.__load_from_file()

    def __build_filename(self):
        filename = self._filename + "_{:.1f}-{:.1f}.hdf5".format(
            self.min_mag, self.max_mag
        )

        path = os.environ.get("CTAPOINTING_DATA")
        if path is None:
            path = "."

        return os.path.join(path, filename)

    def __write_to_file(self):
        filename = self.__build_filename()
        log.debug("writing catalog to file '{}'.".format(filename))

        try:
            self.table.write(
                filename, path=self.__pathname, serialize_meta=True, overwrite=True
            )
        except:
            log.error("there was a problem writing the catalog to file")

    def __load_from_file(self):
        filename = self.__build_filename()
        log.debug("loading catalog from file '{}'.".format(filename))

        try:
            self.table = Table.read(filename, path=self.__pathname)
        except IOError as e:
            log.info(
                "it seems that catalog file '{}' does not exist. Rebuilding catalog.".format(
                    filename
                )
            )

            self._create_from_database()
            self.__write_to_file()

    def select_around_position(self, sky_position, search_radius):
        """
        Select all object from the catalog that are located within circle of given radius around a sky position.

        :param astropy.Coordinate sky_position: centre sky position
        :param astropy.Angle search_radius: search radius of the cone around sky_position
        :returns: table of selected objects
        :rtype: astropy.table
        """

        # make sure that we are in the RADec coordinate system
        try:
            sky_position = sky_position.transform_to("icrs")
        except:
            log.error(
                "could not transform coordinate {} to ICRS system.".format(sky_position)
            )
            return None

        log.debug(
            "finding all stars within {:.1f} around ICRS position (RA={:.2f}, Dec={:.2f})".format(
                search_radius.to("deg"),
                sky_position.ra.to("deg"),
                sky_position.dec.to("deg"),
            )
        )
        log.debug("magnitude range: {:.1f} - {:.1f}".format(self.min_mag, self.max_mag))

        try:
            pos_catalog = SkyCoord(
                ra=self.table["ra"],
                dec=self.table["dec"],
                pm_ra_cosdec=self.table["pmra"],
                pm_dec=self.table["pmdec"],
            )
            distance = pos_catalog.separation(sky_position)

            self.table_selected = self.table[distance < search_radius]
            log.info("found {} stars".format(len(self.table_selected)))
        except Exception as e:
            log.error("could not access catalog table")
            raise e

        return self.table_selected

    def plot_catalog(self):
        """
        Plot catalog of stars in a RADec Aitoff projection.
        Both the total catalog and (if existing) the current star selection is shown.
        """

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection="hammer")

        try:
            ra_pos = Angle(self.table["ra"])
            ra_pos = ra_pos.wrap_at(180 * u.deg)
            dec_pos = Angle(self.table["dec"])
            ax.scatter(ra_pos.radian, dec_pos.radian, marker=".", label="all stars")
        except:
            pass

        try:
            ra_pos_selected = Angle(self.table_selected["ra"])
            ra_pos_selected = ra_pos_selected.wrap_at(180 * u.deg)
            dec_pos_selected = Angle(self.table_selected["dec"])
            ax.scatter(
                ra_pos_selected.radian,
                dec_pos_selected.radian,
                marker=".",
                label="selected stars",
            )
        except:
            pass

        ax.set_xticklabels(
            ["14h", "16h", "18h", "20h", "22h", "0h", "2h", "4h", "6h", "8h", "10h"]
        )
        ax.grid(True)
        ax.legend()


class BrightStarCatalog(Catalog):
    """
    Yale Bright Star Catalog.
    Source: http://vizier.u-strasbg.fr/viz-bin/VizieR-3?-source=V/50/catalog

    Catalog is created from a raw data ASCII file (bsc5.dat).
    """

    def __init__(
        self,
        create_from_database=False,
        filename="bright_star_catalog",
        min_mag=-12.0,
        max_mag=3.0,
    ):
        self.__rawcatalog = "bsc5.dat"  # raw file of the catalog
        Catalog.__init__(self, create_from_database, filename, min_mag, max_mag)

    def _create_from_database(self):
        catalog = os.path.dirname(__file__) + "/" + self.__rawcatalog

        log.info("creating catalog from catalog raw file {}".format(catalog))

        id_num = []
        ra = []
        dec = []
        pmra = []
        pmdec = []
        mag = []

        # go through the catalog line by line
        for line in open(catalog, "rt"):
            if (len(line) < 100) or (line[0] == "#"):
                continue

            try:
                id = int(line[0:4])

                # name = line[5:14].lstrip()

                # read RA (J2000)
                ra_hrs = float(line[75:77])
                ra_min = float(line[77:79])
                ra_sec = float(line[79:82])

                # read Dec (J2000)
                dec_deg = float(line[83:86])
                dec_min = float(line[86:88])
                dec_sec = float(line[88:90])

                # read magnitude
                m = float(line[102:107])

                # read proper motion RA/Dec
                pmr = float(line[148:154]) * 1000.0  # in units of mas/yr
                pmd = float(line[155:160]) * 1000.0  # in units of mas/yr

            except ValueError as error:
                continue

            id_num.append(id)
            ra.append(Angle(f"{ra_hrs:.0f}h{ra_min:.0f}m{ra_sec}s").to("deg").value)
            dec.append(Angle(f"{dec_deg:.0f}d{dec_min:.0f}m{dec_sec}").value)
            mag.append(m)
            pmra.append(pmr)
            pmdec.append(pmd)

        # create astropy table object
        t = Table()
        t["source_id"] = Column(id_num)
        t["ra"] = Column(ra, unit="deg")
        t["dec"] = Column(dec, unit="deg")
        t["ref_epoch"] = Column([2000.0] * len(id_num), unit="yr")
        t["pmra"] = Column(pmra, unit="mas/yr")
        t["pmdec"] = Column(pmdec, unit="mas/yr")
        t["phot_v_mean_mag"] = Column(mag, unit="mag")

        # no effective temperature available for this catalog
        t["teff"] = Column(-1, unit="K")

        # cut catalog to requested magnitude values
        t = t[
            (t["phot_v_mean_mag"] <= self.max_mag)
            & (t["phot_v_mean_mag"] > self.min_mag)
        ]

        self.table = t

        # sort by magnitude
        self.table.sort("phot_v_mean_mag")


class GaiaCatalog(Catalog):
    """
    Gaia DR2 star catalog.
    Data to construct the catalog is read from the Gaia server using astroquery.gaia.
    """

    def __init__(
        self,
        create_from_database=False,
        filename="gaia_catalog",
        min_mag=3.0,
        max_mag=9.0,
        magnitude_correction=0.25,
    ):
        # Gaia G band magnitudes must be corrected in order to be similar to V band magnitudes
        # observed by other missions. The correction is e.g. +0.25 in magnitude if one compares
        # to the Yale bright star catalog.
        self.magnitude_correction = magnitude_correction

        Catalog.__init__(self, create_from_database, filename, min_mag, max_mag)

    def _create_from_database(self):
        # import only when needed. This avoids frequent automatic
        # connection establishment
        from astroquery.gaia import Gaia

        log.info("creating catalog from database.")
        log.debug("\tminimum magnitude: {}".format(self.min_mag))
        log.debug("\tmaximum magnitude: {}".format(self.max_mag))
        log.debug("\tmagnitude correction: {}".format(self.magnitude_correction))

        # select objects and calculate proper J2000.0 coordinates
        selection_str = (
            "SELECT source_id, "
            " COORD1(EPOCH_PROP_POS(ra, dec, parallax, pmra, pmdec, radial_velocity, ref_epoch, 2000)) AS ra,"
            " COORD2(EPOCH_PROP_POS(ra, dec, parallax, pmra, pmdec, radial_velocity, ref_epoch, 2000)) AS dec,"
            " ref_epoch, pmra, pmdec, phot_g_mean_flux,"
            " phot_g_mean_mag, teff_gspphot"
            " from gaiadr3.gaia_source"
            #                         " JOIN gaiadr3.astrophysical_parameters as params"
            #                         " ON gaia.source_id = params.source_id"
            " where phot_g_mean_mag<="
            + str(self.max_mag + self.magnitude_correction)
            + " and phot_g_mean_mag>"
            + str(self.min_mag + self.magnitude_correction)
            + str(" order by phot_g_mean_mag")
        )
        log.debug(f"\tselection string: {selection_str}")

        try:
            job = Gaia.launch_job_async(selection_str, dump_to_file=True)
            self.table = job.get_results()
        except:
            log.error("there was a problem in creating the catalog from database")
            return self.table

        # assign proper units to coordinates
        self.table["ra"].unit = u.deg
        self.table["dec"].unit = u.deg

        log.debug(
            "applying correction {} to translate from G band to V band".format(
                self.magnitude_correction
            )
        )

        # append table of corrected V band magnitudes
        self.table["phot_v_mean_mag"] = (
            self.table["phot_g_mean_mag"] + self.magnitude_correction
        )

        # rename effective temperature column
        self.table.rename_column("teff_gspphot", "teff")

        # sort by magnitude
        self.table.sort("phot_v_mean_mag")
