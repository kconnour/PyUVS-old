"""The spice module contains classes to load in SPICE kernels of IUVS data.
"""
from datetime import datetime
import glob
import os
from pathlib import Path
import re
import numpy as np
import spiceypy as spice

import pyuvs.datafiles


class Spice:
    """An object for working with SPICE kernels.

    Instantiating this object will clear all currently existing kernels.
    More info about SPICE can be found
    `here <https://naif.jpl.nasa.gov/naif/spiceconcept.html>`_.

    Parameters
    ----------
    spice_directory
        Absolute path to the directory where SPICE files live.

    Notes
    -----
    The SPICE kernels are assumed to have a directory structure consistent
    with the IUVS standard:

    | spice_directory
    | ├── mvn
    |    ├── ck
    |    ├── spk
    |    ├── sclk
    | ├── generic_kernels
    |        ├── mar097.bsp

    There may be more kernels than the ones shown here, but these are all that
    this class uses.

    The kernels can also be found online at the `NAIF
    <https://naif.jpl.nasa.gov/pub/naif/MAVEN/kernels/>`_.

    """

    def __init__(self, spice_directory: Path) -> None:
        self._spicedir = spice_directory
        self._clear_existing_kernels()
        self.target = 'Mars'
        self.observer = 'MAVEN'

    @staticmethod
    def _clear_existing_kernels() -> None:
        spice.kclear()

    def furnish_ck(self) -> None:
        """Furnish the spacecraft C-kernels, which are kernels describing the
        attitude of MAVEN and its articulated payload platform.

        Returns
        -------
        None

        """
        ck_path = self._spicedir / 'mvn' / 'ck'
        self._furnish_ck_type(ck_path, 'app')
        self._furnish_ck_type(ck_path, 'sc')

        f = glob.glob(os.path.join(ck_path, 'mvn_iuv_all_l0_20*.bc'))
        if len(f) > 0:
            self._furnish_array(self._find_latest_kernel(f, 4))
        else:
            print('No ck kernels found.')

    def _furnish_ck_type(self, ck_path: Path, kernel_type: str) -> None:
        longterm_kernels, lastlong = \
            self._find_long_term_kernels(ck_path, kernel_type)
        daily_kernels, lastday = \
            self._find_daily_kernels(ck_path, kernel_type, lastlong)
        normal_kernels = \
            self._find_normal_kernels(ck_path, kernel_type, lastday)

        self._furnish_array(normal_kernels)
        self._furnish_array(daily_kernels)
        self._furnish_array(longterm_kernels)

    def _find_long_term_kernels(self, ck_path: Path, kernel_type: str):
        kern_path = str(ck_path / f'mvn_{kernel_type}_rel_*.bc')
        f = glob.glob(kern_path)

        if len(f) > 0:
            longterm_kernels, lastlong = \
                self._find_latest_kernel(f, 4, getlast=True)
        else:
            longterm_kernels, lastlong = None, None
        return longterm_kernels, lastlong

    def _find_daily_kernels(self, ck_path: Path, kernel_type: str,
                             lastlong: str):
        kern_path = str(ck_path / f'mvn_{kernel_type}_red_*.bc')
        f = glob.glob(kern_path)

        if len(f) > 0:
            day, lastday = \
                self._find_latest_kernel(f, 3, after=lastlong, getlast=True)
        else:
            day, lastday = None, None
        return day, lastday

    def _find_normal_kernels(self, ck_path: Path, kernel_type: str,
                              lastday: str) -> list[str]:
        kern_path = str(ck_path / f'mvn_{kernel_type}_rec_*.bc')
        f = glob.glob(kern_path)

        if len(f) > 0:
            norm = self._find_latest_kernel(f, 3, after=lastday)
        else:
            norm = []
        return norm

    @staticmethod
    def _furnish_array(kernels: list[str]) -> None:
        [spice.furnsh(k) for k in kernels]

    @staticmethod
    def _find_latest_kernel(filenames: list[str], part: int,
                             getlast: bool = False, after: str = None):
        # sort the list in reverse order so the most recent kernel appears first
        # in a subset of kernels
        filenames.sort(reverse=True)

        # extract the filenames without their version number
        filetag = [os.path.basename(f).split("_v")[0] for f in filenames]

        # without version numbers, there are many repeated filenames, so find a
        # single entry for each kernel
        uniquetags, uniquetagindices = np.unique(filetag, return_index=True)

        # make a list of the kernels with one entry per kernel
        fnamelist = np.array(filenames)[uniquetagindices]

        # extract the date portions of the kernel file paths
        datepart = [re.split('[-_]', os.path.basename(fname))[part]
                    for fname in fnamelist]

        # find the individual dates
        last = np.unique(datepart)[-1]

        # if a date is chosen for after, then include only the latest kernels
        # after the specified date
        if after is not None:
            retlist = [f for f, d in zip(
                fnamelist, datepart) if int(d) >= int(after)]

        # otherwise, return all the latest kernels
        else:
            retlist = fnamelist

        # if user wants, return also the date of the last of the latest kernels
        if getlast:
            return retlist, last

        # otherwise return just the latest kernels
        else:
            return retlist

    def furnish_spk(self) -> None:
        """Furnish the spacecraft spk kernels (ephemeris data of its location).

        """
        spk_path = self._spicedir / 'mvn' / 'spk'
        spk_kernels = glob.glob(os.path.join(spk_path, 'trj_orb_*-*_rec*.bsp'))

        if len(spk_kernels) > 0:
            rec, _ = self._find_latest_kernel(spk_kernels, 3, getlast=True)
            self._furnish_array(rec)
        else:
            print('No spk kernels found.')

    def furnish_sclk(self) -> None:
        """Furnish the spacecraft sclk kernels (the spacecraft clock).

        """
        sclk_path = self._spicedir / 'mvn' / 'sclk'
        tsc_path = os.path.join(sclk_path, 'MVN_SCLKSCET.0*.tsc')
        clock_kernels = sorted(glob.glob(tsc_path))
        self._furnish_array(clock_kernels)

    def load_spice(self) -> None:
        r"""Load all the kernels typically required by IUVS observations.

        """
        mvn_kernel_path = self._spicedir / 'mvn'
        generic_kernel_path = self._spicedir / 'generic_kernels'

        self._pool_and_furnish(mvn_kernel_path, 'mvn')
        self._pool_and_furnish(generic_kernel_path, 'generic')

        self.furnish_ck()
        self.furnish_spk()
        self.furnish_sclk()
        self._furnish_mars(generic_kernel_path / 'spk')

    def _pool_and_furnish(self, kernel_path: Path, tm: str) -> None:
        split_path = self._split_string_into_length(str(kernel_path), 78)
        spice.pcpool('PATH_VALUES', split_path)
        tm_path = os.path.join(kernel_path, f'{tm}.tm')
        spice.furnsh(tm_path)

    @staticmethod
    def _split_string_into_length(string: str, length: int) -> list[str]:
        # Turn a string into a list of strings that have a maximum length. This
        # is needed since spice can only handle strings of at most length 80.
        return [string[i: i+length] for i in range(0, len(string), length)]

    @staticmethod
    def _furnish_mars(mars_path: Path) -> None:
        mars_kernel = str(mars_path / 'mar097.bsp')
        spice.furnsh(mars_kernel)

    def find_all_maven_apsis_et(
            self, segment='periapse',
            starttime: float = 464623267,
            endtime: datetime = datetime.utcnow()):
        """Calculate the ephemeris time at either apoapse or periapse.

        This algorithm works by getting a time range to look for maxima or
        minima (apoapse or periapse). It then simply finds the those values.
        It takes step sizes of 1 minute in this search.

        Parameters
        ----------
        segment : str
            The orbit point at which to calculate the ephemeris time. Choices
            are 'periapse' and 'apoapse'. Defaults to 'periapse'.
        starttime: float
            The starting ephemeris time to get data from. This is the ET of
            MAVEN's orbital insertion.
        endtime: datetime
            The last time to get the info for.

        Returns
        -------
        orbit_numbers : array
            Array of MAVEN orbit numbers.
        et_array : array
            Array of ephemeris times for chosen orbit segment.
        """

        # set starting and ending times
        et_start = starttime
        et_end = spice.datetime2et(endtime)  # right now

        # do very complicated SPICE stuff
        abcorr = 'NONE'
        refval = 0.
        if segment == 'periapse':
            relate = 'LOCMIN'
            refval = 3396. + 500.
        elif segment == 'apoapse':
            relate = 'LOCMAX'
            refval = 3396. + 6200.
        adjust = 0.
        step = 60.  # 1 minute steps, since we are only looking within periapse segment for periapsis
        et = [et_start, et_end]
        cnfine = spice.utils.support_types.SPICEDOUBLE_CELL(2)
        spice.wninsd(et[0], et[1], cnfine)
        ninterval = round((et[1] - et[0]) / step)
        result = spice.utils.support_types.SPICEDOUBLE_CELL(
            round(1.1 * (et[1] - et[0]) / 4.5))
        spice.gfdist(self.target, abcorr, self.observer, relate, refval, adjust, step,
                     ninterval, cnfine, result=result)
        count = spice.wncard(result)
        et_array = np.zeros(count)
        if count == 0:
            print('Result window is empty.')
        else:
            for i in range(count):
                lr = spice.wnfetd(result, i)
                left = lr[0]
                right = lr[1]
                if left == right:
                    et_array[i] = left

        # make array of orbit numbers
        orbit_numbers = np.arange(1, len(et_array) + 1, 1, dtype=int)

        # return orbit numbers and array of ephemeris times
        return orbit_numbers, et_array

    def orbital_geometry(self, et):
        """Calculate the MAVEN spacecraft position, Mars Ls, and subsolar
        position for a given ephemeris time.

        Parameters
        ----------
        et: float
            Input epoch in ephemeris seconds past J2000.

        Returns
        -------
        et: array
            The input ephemeris times. Just givin'em back.
        subsc_lat: array
            Sub-spacecraft latitudes in degrees.
        subsc_lon: array
            Sub-spacecraft longitudes in degrees.
        sc_alt_km: array
            Sub-spacecraft altitudes in kilometers.
        ls: array
            Mars solar longitudes in degrees.
        subsolar_lat: array
            Sub-solar latitudes in degrees.
        subsolar_lon: array
            Sub-solar longitudes in degrees.

        """

        # do a bunch of SPICE stuff only Justin understands...
        abcorr = 'LT+S'
        spoint, trgepc, srfvec = spice.subpnt(
            'Intercept: ellipsoid', self.target, et, 'IAU_MARS', abcorr,
            self.observer)
        rpoint, colatpoint, lonpoint = spice.recsph(spoint)
        if lonpoint > np.pi:
            lonpoint -= 2 * np.pi
        subsc_lat = 90 - np.degrees(colatpoint)
        subsc_lon = np.degrees(lonpoint)
        sc_alt_km = np.sqrt(np.sum(srfvec ** 2))

        # calculate subsolar position
        sspoint, strgepc, ssrfvec = spice.subslr(
            'Intercept: ellipsoid', self.target, et, 'IAU_MARS',
             abcorr, self.observer)
        srpoint, scolatpoint, slonpoint = spice.recsph(sspoint)
        if slonpoint > np.pi:
            slonpoint -= 2 * np.pi
        subsolar_lat = 90 - np.degrees(scolatpoint)
        subsolar_lon = np.degrees(slonpoint)

        # calculate solar longitude
        ls = spice.lspcn(self.target, et, abcorr)
        ls = np.degrees(ls)

        # return the position information
        return et, subsc_lat, subsc_lon, sc_alt_km, ls, subsolar_lat, subsolar_lon

    def get_segment_positions(self):
        """Calculate geometry data for all 3 segments: start of orbit,
        periapse, and apoapse.

        Parameters
        ----------
        None.

        Returns
        -------
        orbit_data : dict
            Calculations of the spacecraft and Mars position. Includes orbit numbers, ephemeris time,
            sub-spacecraft latitude, longitude, and altitude (in km), and solar longitude for three orbit segments: start,
            periapse, apoapse.
        """

        # get ephemeris times for orbit apoapse and periapse points
        orbit_numbers, periapse_et = self.find_all_maven_apsis_et(segment='periapse')
        orbit_numbers, apoapse_et = self.find_all_maven_apsis_et(segment='apoapse')
        n_orbits = len(orbit_numbers)

        # make arrays to hold information
        et = np.zeros((n_orbits, 3)) * np.nan
        subsc_lat = np.zeros((n_orbits, 3)) * np.nan
        subsc_lon = np.zeros((n_orbits, 3)) * np.nan
        sc_alt_km = np.zeros((n_orbits, 3)) * np.nan
        solar_longitude = np.zeros((n_orbits, 3)) * np.nan
        subsolar_lat = np.zeros((n_orbits, 3)) * np.nan
        subsolar_lon = np.zeros((n_orbits, 3)) * np.nan

        # loop through orbit numbers and calculate positions
        for i in range(n_orbits):

            for j in range(3):

                # first do orbit start positions
                if j == 0:
                    tet, tsubsc_lat, tsubsc_lon, tsc_alt_km, tls, tsubsolar_lat, tsubsolar_lon = self.orbital_geometry(
                        periapse_et[i] - 1284)

                # then periapse positions
                elif j == 1:
                    tet, tsubsc_lat, tsubsc_lon, tsc_alt_km, tls, tsubsolar_lat, tsubsolar_lon = self.orbital_geometry(
                        periapse_et[i])

                # and finally apoapse positions
                else:
                    tet, tsubsc_lat, tsubsc_lon, tsc_alt_km, tls, tsubsolar_lat, tsubsolar_lon = self.orbital_geometry(
                        apoapse_et[i])

                # place calculations into arrays
                et[i, j] = tet
                subsc_lat[i, j] = tsubsc_lat
                subsc_lon[i, j] = tsubsc_lon
                sc_alt_km[i, j] = tsc_alt_km
                solar_longitude[i, j] = tls
                subsolar_lat[i, j] = tsubsolar_lat
                subsolar_lon[i, j] = tsubsolar_lon

        # make a dictionary of the calculations
        orbit_data = {
            'orbit_numbers': orbit_numbers,
            'et': et,
            'subsc_lat': subsc_lat,
            'subsc_lon': subsc_lon,
            'subsc_alt_km': sc_alt_km,
            'solar_longitude': solar_longitude,
            'subsolar_lat': subsolar_lat,
            'subsolar_lon': subsolar_lon,
            'position_indices': np.array(['orbit start (periapse - 21.4 minutes)', 'periapse', 'apoapse']),
        }

        # return the calculations
        return orbit_data

    def rotated_transform(self, et):
        """
        Calculate the rotated pole transform for a particular orbit to replicate the viewing geometry at MAVEN apoapse.

        Parameters
        ----------
        et : obj
            MAVEN apoapsis ephemeris time.

        Returns
        -------
        transform : ???
            A Cartopy rotated pole transform.
        """

        # calculate various parameters using SPICE
        frame = 'MAVEN_MME_2000'
        abcorr = 'LT+S'
        observer = 'MAVEN'
        state, ltime = spice.spkezr(self.target, et, frame, abcorr, observer)
        spoint, trgepc, srfvec = spice.subpnt('Intercept: ellipsoid', self.target,
                                              et, 'IAU_MARS', abcorr, observer)
        rpoint, colatpoint, lonpoint = spice.recsph(spoint)
        if lonpoint < 0.:
            lonpoint += 2 * np.pi
        G = 6.673e-11 * 6.4273e23
        r = 1e3 * state[0:3]
        v = 1e3 * state[3:6]
        h = np.cross(r, v)
        n = h / np.linalg.norm(h)
        ev = np.cross(v, h) / G - r / np.linalg.norm(r)
        evn = ev / np.linalg.norm(ev)
        b = np.cross(evn, n)

        # get the sub-spacecraft latitude and longitude, and altitude (converted to meters)
        sublat = 90 - np.degrees(colatpoint)
        sublon = np.degrees(lonpoint)
        if sublon > 180:
            sublon -= 360
        alt = np.sqrt(np.sum(srfvec ** 2)) * 1e3

        # north pole unit vector in the IAU Mars basis
        polar_vector = [0, 0, 1]

        # when hovering over the sub-spacecraft point unrotated (the meridian of the point is a straight vertical line,
        # this is the exact view when using cartopy's NearsidePerspective or Orthographic with central_longitude and
        # central latitude set to the sub-spacecraft point), calculate the angle by which the planet must be rotated
        # about the sub-spacecraft point
        angle = np.arctan2(np.dot(polar_vector, -b), np.dot(polar_vector, n))

        # first, rotate the pole to a different latitude given the subspacecraft latitude
        # cartopy's RotatedPole uses the location of the dateline (-180) as the lon_0 coordinate of the north pole
        pole_lat = 90 + sublat
        pole_lon = -180

        # convert pole latitude to colatitude (for spherical coordinates)
        # also convert to radians for use with numpy trigonometric functions
        phi = pole_lon * np.pi / 180
        theta = (90 - pole_lat) * np.pi / 180

        # calculate the Cartesian vector pointing to the pole
        polar_vector = [np.cos(phi) * np.sin(theta),
                        np.sin(phi) * np.sin(theta), np.cos(theta)]

        # by rotating the pole, the observer's sub-point in cartopy's un-transformed coordinates is (0,0)
        # the rotation axis is therefore the x-axis
        rotation_axis = [1, 0, 0]

        # rotate the polar vector by the calculated angle
        rotated_polar_vector = np.dot(pyuvs.rotation_matrix(rotation_axis, -angle),
                                      polar_vector)

        # get the new polar latitude and longitude after the rotation, with longitude offset to dateline
        rotated_polar_lon = np.arctan(
            rotated_polar_vector[1] / rotated_polar_vector[
                0]) * 180 / np.pi - 180
        if sublat < 0:
            rotated_polar_lat = 90 - np.arccos(
                rotated_polar_vector[2] / np.linalg.norm(
                    rotated_polar_vector)) * 180 / np.pi
        else:
            rotated_polar_lat = 90 + np.arccos(
                rotated_polar_vector[2] / np.linalg.norm(
                    rotated_polar_vector)) * 180 / np.pi

        return rotated_polar_lat, rotated_polar_lon, sublon


if __name__ == '__main__':
    import time
    d = Path('/media/kyle/Samsung_T5/IUVS_data/')
    p = Path('/media/kyle/Samsung_T5/IUVS_data/spice')
    t0 = time.time()
    s = Spice(p)
    s.load_spice()
    d = datetime(2014, 11, 11)
    print(spice.datetime2et(d))
    t1=time.time()
    et = s.find_all_maven_apsis_et('apoapse', endtime=datetime(2020, 1, 1))
    o = et[1][5000]
    foo = s.orbital_geometry(o)
    print(foo)

    #from astropy.io import fits
    #files = pyuvs.datafiles.find_latest_apoapse_muv_file_paths_from_block(d, 5738)
    #hdul = fits.open(files[0])
    #print(hdul['integration'].data.columns)

