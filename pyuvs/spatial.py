"""The spatial module performs pertinent spatial calculations.
"""
from datetime import datetime
import numpy as np
import spiceypy as spice


class OrbitalGeometry:
    """OrbitalGeometry contains methods for finding spatial quantities from
    MAVEN's orbit.

    Notes
    -----
    The class relies on you having already loaded SPICE kernels. See
    :class:`pyuvs.spice.Spice` for methods to do this.

    """

    def __init__(self):
        """

        """
        self.__target = 'Mars'
        self.__abcorr = 'NONE'
        self.__observer = 'MAVEN'

    def find_maven_apsis(self, start_time: datetime = None,
                         end_time: datetime = None,
                         apsis: str = 'apoapse') \
            -> tuple[np.ndarray, np.ndarray]:
        """Calculate the ephemeris times at either orbital apses between a start
        and end time.

        Parameters
        ----------
        start_time
            Starting datetime to get apsis ephemeris times for. Default is
            :code:`None`, which will start at the time of orbital insertion.
        end_time
            Ending datetime to get apsis ephemeris times for. Default is
            :code:`None`, which will get times up until today.
        apsis
            The apsis to get the ephemeris times for. Can be either 'apoapse' or
            'periapse'.

        Returns
        -------
        orbits
            Relative MAVEN orbit numbers between the start and end dates.
        et
            Ephemeris times at the given apsis for all the orbits in the time
            range.

        """
        et_start = 464623267 if start_time is not None \
            else spice.datetime2et(start_time)
        et_end = spice.datetime2et(datetime.utcnow()) if end_time is not None \
            else spice.datetime2et(end_time)

        relate, refval = self.__set_apsis_flags(apsis)
        adjust = 0.
        step = 60.

        cnfine = spice.utils.support_types.SPICEDOUBLE_CELL(2)
        spice.wninsd(et_start, et_end, cnfine)
        ninterval = round((et_end - et_start) / step)
        result = spice.utils.support_types.SPICEDOUBLE_CELL(
            round(1.1 * (et_end - et_start) / 4.5))

        spice.gfdist(self.__target, self.__abcorr, self.__observer, relate,
                     refval, adjust, step, ninterval, cnfine, result=result)
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

    # TODO: in python3.10 this can be a switch case
    @staticmethod
    def __set_apsis_flags(apsis: str) -> tuple[str, int]:
        if apsis not in ['apoapse', 'periapse']:
            message = f'{apsis} is not a valid apsis.'
            raise ValueError(message)
        if apsis == 'periapse':
            relate = 'LOCMIN'
            refval = 3396 + 500
        elif apsis == 'apoapse':
            relate = 'LOCMAX'
            refval = 3396 + 6200
        return relate, refval

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
        orbit_numbers, periapse_et = self.find_maven_apsis(apsis='periapse')
        orbit_numbers, apoapse_et = self.find_maven_apsis(apsis='apoapse')
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


if __name__ == '__main__':
    from pyuvs.spice import Spice
    from pyuvs.science_week import ScienceWeek

    p = '/media/kyle/Samsung_T5/IUVS_data/spice'
    Spice().load_spice(p)

    sw = ScienceWeek()
    start = sw.week_start_date(0)
    d = datetime.combine(start, datetime.min.time())
    print(spice.datetime2et(d))



    '''g = OrbitalGeometry()
    foo = g.get_orbit_positions()

    print(foo['orbit_numbers'][3999])
    print(foo['subsc_lat'][3999, 2])
    print(foo['subsc_alt_km'][3999, 2])
    print(foo['solar_longitude'][3999, 2])'''
    #import pickle
    #with open('/home/kyle/myOrbitDict.pickle', 'wb') as handle:
    #    pickle.dump(foo, handle)
