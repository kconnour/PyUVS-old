"""The spice module contains classes to load in SPICE kernels of IUVS data.
"""
import julian
from datetime import datetime
import glob
import os
import re
import numpy as np
import spiceypy as spice


class Spice:
    """A collection of ways to furnish arrays.

    Spice takes the path to SPICE kernels. It provides methods to furn(i)sh
    relevant kernels.

    """
    def __init__(self) -> None:
        """

        Notes
        -----
        The kernels can be found online at the
        `NAIF <https://naif.jpl.nasa.gov/pub/naif/MAVEN/kernels/>_`.

        """
        pass

    def furnish_ck(self, ck_path: str) -> None:
        """Furnish the spacecraft C-kernels, which are kernels describing the
        attitude of MAVEN and its articulated payload platform.

        Parameters
        ----------
        ck_path
            Absolute path to the directory containing the C-kernels.

        """

        self.__furnish_ck_type(ck_path, 'app')
        self.__furnish_ck_type(ck_path, 'sc')

        f = glob.glob(os.path.join(ck_path, 'mvn_iuv_all_l0_20*.bc'))
        if len(f) > 0:
            self.__furnish_array(self.__find_latest_kernel(f, 4))
        else:
            print('No C kernels found.')

    def furnish_spk(self, spk_path: str) -> None:
        """Furnish the spacecraft spk kernels (ephemeris data of its location).

        Parameters
        ----------
        spk_path
            Absolute path to the directory containing spk kernels.

        """
        spk_kernels = glob.glob(os.path.join(spk_path, 'trj_orb_*-*_rec*.bsp'))

        if len(spk_kernels) > 0:
            rec, lastorb = self.__find_latest_kernel(spk_kernels, 3, getlast=True)

        self.__furnish_array(rec)

    def furnish_sclk(self, sclk_path) -> None:
        """Furnish the spacecraft sclk kernels (the spacecraft clock).

        Parameters
        ----------
        sclk_path
            Absolute path to the directory containing sclk kernels.

        Returns
        -------

        """
        tsc_path = os.path.join(sclk_path, 'MVN_SCLKSCET.0*.tsc')
        clock_kernels = sorted(glob.glob(tsc_path))
        self.__furnish_array(clock_kernels)

    def load_spice(self, spice_directory: str) -> None:
        """Load all of the kernels typically required by IUVS observations.

        Parameters
        ----------
        spice_directory
            Absolute path to the directory where SPICE files live.

        Notes
        -----
        The SPICE kernels are assumed to have a directory structure consistent
        with the IUVS standard, outlined below.

        spice_directory
        |---mvn
        |   |---ck
        |   |---spk
        |   |---sclk
        |---generic_kernels
        |   |---spk
        |   |   |mar097.bsp

        This method will clear all currently existing kernels before loading in
        IUVS kernels.

        """
        mvn_kernel_path = os.path.join(spice_directory, 'mvn')
        generic_kernel_path = os.path.join(spice_directory, 'generic_kernels')
        ck_path = os.path.join(mvn_kernel_path, 'ck')
        spk_path = os.path.join(mvn_kernel_path, 'spk')
        sclk_path = os.path.join(mvn_kernel_path, 'sclk')
        generic_spk_path = os.path.join(generic_kernel_path, 'spk')

        self.__clear_existing_kernels()

        # TODO: I have absolutely no idea why we need to call the pool method. I
        #  think we should just need to furnish them
        self.__pool_and_furnish(mvn_kernel_path, 'mvn')
        self.__pool_and_furnish(generic_kernel_path, 'generic')

        self.furnish_ck(ck_path)
        self.furnish_spk(spk_path)
        self.furnish_sclk(sclk_path)
        self.__furnish_mars(generic_spk_path)

    def __furnish_ck_type(self, ck_path: str, kernel_type: str) -> None:
        longterm_kernels, lastlong = \
            self.__find_long_term_kernels(ck_path, kernel_type)

        daily_kernels, lastday = \
            self.__find_daily_kernels(ck_path, kernel_type, lastlong)

        normal_kernels = \
            self.__find_normal_kernels(ck_path, kernel_type, lastday)

        self.__furnish_array(normal_kernels)
        self.__furnish_array(daily_kernels)
        self.__furnish_array(longterm_kernels)

    # TODO: -> list[str] | str in 3.10
    def __find_long_term_kernels(self, ck_path: str, kernel_type: str):
        kern_path = os.path.join(ck_path, f'mvn_{kernel_type}_rel_*.bc')
        f = glob.glob(kern_path)

        if len(f) > 0:
            longterm_kernels, lastlong = \
                self.__find_latest_kernel(f, 4, getlast=True)
        else:
            longterm_kernels, lastlong = None, None
        return longterm_kernels, lastlong

    # TODO: -> list[str] | str in 3.10
    def __find_daily_kernels(self, ck_path: str, kernel_type: str,
                             lastlong: str):
        kern_path = os.path.join(ck_path, f'mvn_{kernel_type}_red_*.bc')
        f = glob.glob(kern_path)

        if len(f) > 0:
            day, lastday = \
                self.__find_latest_kernel(f, 3, after=lastlong, getlast=True)
        else:
            day, lastday = None, None
        return day, lastday

    def __find_normal_kernels(self, ck_path: str, kernel_type: str,
                              lastday: str) -> list[str]:
        kern_path = os.path.join(ck_path, f'mvn_{kernel_type}_rec_*.bc')
        f = glob.glob(kern_path)

        if len(f) > 0:
            norm = self.__find_latest_kernel(f, 3, after=lastday)
        else:
            norm = []
        return norm

    @staticmethod
    def __furnish_array(kernels: list[str]) -> None:
        [spice.furnsh(k) for k in kernels]

    @staticmethod
    def __find_latest_kernel(filenames: list[str], part: int,
                             getlast: bool = False, after: str = None):
        # store the input filename list internally
        fnamelist = filenames

        # sort the list in reverse order so the most recent kernel appears first in a subset of kernels
        fnamelist.sort(reverse=True)

        # extract the filenames without their version number
        filetag = [os.path.basename(f).split("_v")[0] for f in fnamelist]

        # without version numbers, there are many repeated filenames, so find a single entry for each kernel
        uniquetags, uniquetagindices = np.unique(filetag, return_index=True)

        # make a list of the kernels with one entry per kernel
        fnamelist = np.array(fnamelist)[uniquetagindices]

        # extract the date portions of the kernel file paths
        datepart = [re.split('[-_]', os.path.basename(fname))[part]
                    for fname in fnamelist]

        # find the individual dates
        uniquedates, uniquedateindex = np.unique(datepart, return_index=True)

        # extract the finald ate
        last = uniquedates[-1]

        # if a date is chosen for after, then include only the latest kernels after the specified date
        if after is not None:
            retlist = [f for f, d in zip(
                fnamelist, datepart) if int(d) >= int(after)]

        # otherwise, return all the latest kernels
        else:
            retlist = [f for f, d in zip(fnamelist, datepart)]

        # if user wants, return also the date of the last of the latest kernels
        if getlast:
            return retlist, last

        # otherwise return just the latest kernels
        else:
            return retlist

    @staticmethod
    def __clear_existing_kernels() -> None:
        spice.kclear()

    def __pool_and_furnish(self, kernel_path: str, tm: str) -> None:
        split_path = self.__split_string_into_length(kernel_path, 78)
        spice.pcpool('PATH_VALUES', split_path)
        tm_path = os.path.join(kernel_path, f'{tm}.tm')
        spice.furnsh(tm_path)

    @staticmethod
    def __split_string_into_length(string: str, length: int) -> list[str]:
        # Turn a string into a list of strings that have a maximum length. This
        # is needed since spice can only handle strings of at most length 80.
        return [string[i: i+length] for i in range(0, len(string), length)]

    @staticmethod
    def __furnish_mars(mars_path: str) -> None:
        mars_kernel = os.path.join(mars_path, 'mar097.bsp')
        spice.furnsh(mars_kernel)


class Geometry:
    @staticmethod
    def find_maven_apsis(segment='apoapse'):
        """
        Calculates the ephemeris times at apoapse or periapse for all MAVEN orbits between orbital insertion and now.

        Parameters
        ----------
        segment : str
            The orbit point at which to calculate the ephemeris time. Choices are 'periapse' and 'apoapse'. Defaults to
            'periapse'.

        Returns
        -------
        orbit_numbers : array
            Array of MAVEN orbit numbers.
        et_array : array
            Array of ephemeris times for chosen orbit segment.
        """

        # set starting and ending times
        et_start = 464623267  # MAVEN orbital insertion
        #et_end = spice.datetime2et(datetime.utcnow())  # right now
        et_end = spice.datetime2et(datetime(2020, 1, 1, 0, 0, 0, 0))

        # do very complicated SPICE stuff
        target = 'Mars'
        abcorr = 'NONE'
        observer = 'MAVEN'
        refval = 0.
        if segment == 'periapse':
            relate = 'LOCMIN'
            refval = 3396 + 500
        elif segment == 'apoapse':
            relate = 'LOCMAX'
            refval = 3396 + 6200
        else:
            raise ValueError('segment is wrong...')
        adjust = 0.
        step = 60.  # 1 minute steps, since we are only looking within periapse segment for periapsis
        et = [et_start, et_end]
        cnfine = spice.utils.support_types.SPICEDOUBLE_CELL(2)
        spice.wninsd(et[0], et[1], cnfine)
        ninterval = round((et[1] - et[0]) / step)
        result = spice.utils.support_types.SPICEDOUBLE_CELL(
            round(1.1 * (et[1] - et[0]) / 4.5))

        spice.gfdist(target, abcorr, observer, relate, refval, adjust, step,
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

    @staticmethod
    def spice_positions(et):
        """
        Calculates MAVEN spacecraft position, Mars solar longitude, and subsolar position for a given ephemeris time.

        Parameters
        ----------
        et : float
            Input epoch in ephemeris seconds past J2000.

        Returns
        -------
        et : array
            The input ephemeris times. Just givin'em back.
        subsc_lat : array
            Sub-spacecraft latitudes in degrees.
        subsc_lon : array
            Sub-spacecraft longitudes in degrees.
        sc_alt_km : array
            Sub-spacecraft altitudes in kilometers.
        ls : array
            Mars solar longitudes in degrees.
        subsolar_lat : array
            Sub-solar latitudes in degrees.
        subsolar_lon : array
            Sub-solar longitudes in degrees.
        mars_sun_km: array
        """

        # do a bunch of SPICE stuff only Justin understands...
        target = 'Mars'
        abcorr = 'LT+S'
        observer = 'MAVEN'
        spoint, trgepc, srfvec = spice.subpnt('Intercept: ellipsoid', target, et, 'IAU_MARS', abcorr, observer)
        junk0, junk0, srvec_sun = spice.subpnt('Intercept: ellipsoid', target, et, 'IAU_MARS', abcorr, 'SUN')
        rpoint, colatpoint, lonpoint = spice.recsph(spoint)
        if lonpoint > np.pi:
            lonpoint -= 2 * np.pi
        subsc_lat = 90 - np.degrees(colatpoint)
        subsc_lon = np.degrees(lonpoint)
        sc_alt_km = np.sqrt(np.sum(srfvec ** 2))
        mars_sun_km = np.sqrt(np.sum(srvec_sun**2))

        # calculate subsolar position
        sspoint, strgepc, ssrfvec = spice.subslr('Intercept: ellipsoid', target, et, 'IAU_MARS', abcorr, observer)
        srpoint, scolatpoint, slonpoint = spice.recsph(sspoint)
        if slonpoint > np.pi:
            slonpoint -= 2 * np.pi
        subsolar_lat = 90 - np.degrees(scolatpoint)
        subsolar_lon = np.degrees(slonpoint)

        # calculate solar longitude
        ls = spice.lspcn(target, et, abcorr)
        ls = np.degrees(ls)

        # return the position information
        return et, subsc_lat, subsc_lon, sc_alt_km, ls, subsolar_lat, subsolar_lon, mars_sun_km

    def get_orbit_positions(self):
        """
        Calculates orbit segment geometry data.

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
        orbit_numbers, periapse_et = self.find_maven_apsis(segment='periapse')
        orbit_numbers, apoapse_et = self.find_maven_apsis(segment='apoapse')
        n_orbits = len(orbit_numbers)

        # make arrays to hold information
        et = np.zeros((n_orbits, 3)) * np.nan
        subsc_lat = np.zeros((n_orbits, 3)) * np.nan
        subsc_lon = np.zeros((n_orbits, 3)) * np.nan
        sc_alt_km = np.zeros((n_orbits, 3)) * np.nan
        mars_sun_dist = np.zeros((n_orbits, 3)) * np.nan
        solar_longitude = np.zeros((n_orbits, 3)) * np.nan
        subsolar_lat = np.zeros((n_orbits, 3)) * np.nan
        subsolar_lon = np.zeros((n_orbits, 3)) * np.nan

        # loop through orbit numbers and calculate positions
        for i in range(n_orbits):

            for j in range(3):

                # first do orbit start positions
                if j == 0:
                    tet, tsubsc_lat, tsubsc_lon, tsc_alt_km, tls, tsubsolar_lat, tsubsolar_lon, mars_sun_km= self.spice_positions(
                        periapse_et[i] - 1284)

                # then periapse positions
                elif j == 1:
                    tet, tsubsc_lat, tsubsc_lon, tsc_alt_km, tls, tsubsolar_lat, tsubsolar_lon, mars_sun_km = self.spice_positions(
                        periapse_et[i])

                # and finally apoapse positions
                else:
                    tet, tsubsc_lat, tsubsc_lon, tsc_alt_km, tls, tsubsolar_lat, tsubsolar_lon, mars_sun_km = self.spice_positions(
                        apoapse_et[i])

                # place calculations into arrays
                et[i, j] = tet
                subsc_lat[i, j] = tsubsc_lat
                subsc_lon[i, j] = tsubsc_lon
                sc_alt_km[i, j] = tsc_alt_km
                mars_sun_dist[i, j] = mars_sun_km
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
            'mars_sun_km': mars_sun_dist,
            'position_indices': np.array(['orbit start (periapse - 21.4 minutes)', 'periapse', 'apoapse']),
        }

        # return the calculations
        return orbit_data

    @staticmethod
    def utc_to_sol(utc):
        """ Zac wrote this
        Converts a UTC datetime object into the equivalent Martian decimal sol and year.

        Parameters
        ----------
        utc : object
            UTC datetime object.

        Returns
        -------
        sol : float
            The decimal sol date.
        my : int
            The Mars year.
        """
        # constants
        ns = 668.6  # number of sols in a Mars year
        jdref = 2442765.667  # reference Julian date corresponding to Ls = 0
        myref = 12  # jdref is the beginning of Mars year 12

        # convert datetime object to Julian date
        jd = julian.to_jd(utc, fmt='jd')

        # calculate the sol
        sol = (jd - jdref) * (86400. / 88775.245) % ns

        # calculate the Mars year
        my = int((jd - jdref) * (86400. / 88775.245) / ns + myref)

        # return the decimal sol and Mars year
        return sol, my


if __name__ == '__main__':
    p = '/media/kyle/Samsung_T5/IUVS_data/spice'
    Spice().load_spice(p)

    #g = Geometry()
    #foo = g.get_orbit_positions()
    #import pickle
    #with open('/home/kyle/myOrbitDict.pickle', 'wb') as handle:
    #    pickle.dump(foo, handle)
