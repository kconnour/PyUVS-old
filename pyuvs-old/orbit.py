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
    :class:`pyuvs-old.spice.Spice` for methods to do this.

    """

    def __init__(self):
        """

        """
        self.__target = 'Mars'
        self.__abcorr = 'NONE'
        self.__observer = 'MAVEN'

    def find_maven_apsis_et(self, end_time: datetime = None,
                            apsis: str = 'apoapse') \
            -> tuple[np.ndarray, np.ndarray]:
        """Calculate the ephemeris times at either orbital apses between a start
        and end time. To do this, SPICE checks the Mars-MAVEN distance in steps
        of 1 minute, and returns the local minima (for periapsis) or local
        maxima (for apoapsis).

        Parameters
        ----------
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
        # TODO: it'd be nice to be able to specify a start time. This is easy to
        #  implement here, but I'm not sure how I'd compute orbit numbers.
        et_start = 464623267
        et_end = spice.datetime2et(datetime.utcnow()) if end_time is None \
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

    def spice_positions(self, et: float):
        """Calculate MAVEN spacecraft position, Mars solar longitude, and the
        subsolar position for a given ephemeris time.

        Parameters
        ----------
        et
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
        spoint, trgepc, srfvec = \
            spice.subpnt('Intercept: ellipsoid', self.__target, et, 'IAU_MARS',
                         self.__abcorr, self.__observer)
        _, _, srvec_sun = \
            spice.subpnt('Intercept: ellipsoid', self.__target, et, 'IAU_MARS',
                         self.__abcorr, 'SUN')
        rpoint, colatpoint, lonpoint = spice.recsph(spoint)
        if lonpoint > np.pi:
            lonpoint -= 2 * np.pi
        subsc_lat = 90 - np.degrees(colatpoint)
        subsc_lon = np.degrees(lonpoint)
        sc_alt_km = np.sqrt(np.sum(srfvec ** 2))
        mars_sun_km = np.sqrt(np.sum(srvec_sun**2))

        # calculate subsolar position
        sspoint, strgepc, ssrfvec = \
            spice.subslr('Intercept: ellipsoid', self.__target, et, 'IAU_MARS',
                         self.__abcorr, self.__observer)
        srpoint, scolatpoint, slonpoint = spice.recsph(sspoint)
        if slonpoint > np.pi:
            slonpoint -= 2 * np.pi
        subsolar_lat = 90 - np.degrees(scolatpoint)
        subsolar_lon = np.degrees(slonpoint)

        ls = np.degrees(spice.lspcn(self.__target, et, self.__abcorr))

        return et, subsc_lat, subsc_lon, sc_alt_km, ls, subsolar_lat, \
            subsolar_lon, mars_sun_km

    def get_orbit_positions(self, end_time: datetime = None,) -> dict:
        """Calculate orbit segment geometry.

        Parameters
        ----------
        end_time
            The ending time to get orbital positions for.

        Returns
        -------
        orbit_data
            Calculations of the following keys:

            * orbit_number: The relative orbit number.
            * et: The ephemeris time [seconds past J2000].
            * subsc_lat: The sub-spacecraft latitude [degrees].
            * subsc_lon: The sub-spacecraft longitude [degrees].
            * subsc_alt: The sub-spacecraft altitude [km].
            * solar_longiutde: The Ls [degrees].
            * subsolar_lat: The sub-solar latitude [degrees].
            * subsolar_lon: The sub-solar longitude [degrees].
            * mars_sun_dist: The Mars-sun distance [km].

        All of these values are calculated for 3 times: The start of the orbit
        (which is 21.4 minutes before periapsis), periapsis, and apoapsis. The
        arrays stored in the keys are indexed in this order.

        """
        # get ephemeris times for orbit apoapse and periapse points
        orbit_numbers, periapse_et = \
            self.find_maven_apsis_et(end_time=end_time, apsis='periapse')
        _, apoapse_et = \
            self.find_maven_apsis_et(end_time=end_time, apsis='apoapse')
        n_orbits = len(orbit_numbers)

        et, subsc_lat, subsc_lon, sc_alt, mars_sun_dist, solar_longitude, \
        subsolar_lat, subsolar_lon = \
            self.__compute_geometry_arrays(n_orbits, periapse_et, apoapse_et)

        orbit_data = {
            'orbit_number': orbit_numbers,
            'et': et,
            'subsc_lat': subsc_lat,
            'subsc_lon': subsc_lon,
            'subsc_alt': sc_alt,
            'solar_longitude': solar_longitude,
            'subsolar_lat': subsolar_lat,
            'subsolar_lon': subsolar_lon,
            'mars_sun_dist': mars_sun_dist,
        }
        return orbit_data

    def __compute_geometry_arrays(self, n_orbits, periapse_et, apoapse_et):
        et = self.__make_array_of_nans((n_orbits, 3))
        subsc_lat = self.__make_array_of_nans((n_orbits, 3))
        subsc_lon = self.__make_array_of_nans((n_orbits, 3))
        sc_alt = self.__make_array_of_nans((n_orbits, 3))
        mars_sun_dist = self.__make_array_of_nans((n_orbits, 3))
        solar_longitude = self.__make_array_of_nans((n_orbits, 3))
        subsolar_lat = self.__make_array_of_nans((n_orbits, 3))
        subsolar_lon = self.__make_array_of_nans((n_orbits, 3))

        return self.__fill_arrays_with_calculations(
            n_orbits, et, subsc_lat, subsc_lon, sc_alt, mars_sun_dist,
            solar_longitude, subsolar_lat, subsolar_lon, periapse_et,
            apoapse_et)

    @staticmethod
    def __make_array_of_nans(shape: tuple) -> np.ndarray:
        return np.zeros(shape) * np.nan

    def __fill_arrays_with_calculations(
            self, n_orbits, et, subsc_lat, subsc_lon, sc_alt, mars_sun_dist,
            solar_longitude, subsolar_lat, subsolar_lon, periapse_et,
            apoapse_et):
        for i in range(n_orbits):
            for j in range(3):
                # first do orbit start positions
                if j == 0:
                    tet, tsubsc_lat, tsubsc_lon, tsc_alt_km, tls, tsubsolar_lat, \
                    tsubsolar_lon, mars_sun_km = self.spice_positions(
                        periapse_et[i] - 1284)

                # then periapse positions
                elif j == 1:
                    tet, tsubsc_lat, tsubsc_lon, tsc_alt_km, tls, tsubsolar_lat, \
                    tsubsolar_lon, mars_sun_km = self.spice_positions(
                        periapse_et[i])

                # and finally apoapse positions
                else:
                    tet, tsubsc_lat, tsubsc_lon, tsc_alt_km, tls, tsubsolar_lat, \
                    tsubsolar_lon, mars_sun_km = self.spice_positions(
                        apoapse_et[i])

                # place calculations into arrays
                et[i, j] = tet
                subsc_lat[i, j] = tsubsc_lat
                subsc_lon[i, j] = tsubsc_lon
                sc_alt[i, j] = tsc_alt_km
                mars_sun_dist[i, j] = mars_sun_km
                solar_longitude[i, j] = tls
                subsolar_lat[i, j] = tsubsolar_lat
                subsolar_lon[i, j] = tsubsolar_lon

        return et, subsc_lat, subsc_lon, sc_alt, mars_sun_dist, \
            solar_longitude, subsolar_lat, subsolar_lon
