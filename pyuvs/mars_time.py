"""The time module contains classes for converting Earth times into Martian
times.
"""
# TODO: consider making an ET class to go to Earth times
from datetime import date, datetime, timedelta
import warnings
import julian
import numpy as np


class UTC:
    """An object that can convert UTC times into Martian times.

    UTC accepts a a coordinated universal time and contains methods to convert
    it to various Martian times.

    """
    def __init__(self, time: datetime) -> None:
        """
        Parameters
        ----------
        time
            The UTC time.

        Raises
        ------
        TypeError
            Raised if time is not an instance of datetime.datetime.

        """
        self.__time = time
        self.__raise_type_error_if_not_datetime()

        self.__input_julian_date = julian.to_jd(self.__time, fmt='jd')
        self.__sols_per_mars_year = 668.6
        self.__julian_ref = 2442765.667
        self.__mars_year_ref = 12
        self.__seconds_earth_day = 86400
        self.__seconds_mars_day = 88775.245

    def __raise_type_error_if_not_datetime(self) -> None:
        if not isinstance(self.__time, datetime):
            raise TypeError('time must be an instance of datetime.datetime.')

    def to_sol(self) -> float:
        """Convert the UTC to Martian sol.

        """
        delta_julian = self.__input_julian_date - self.__julian_ref
        day_length_ratio = self.__seconds_earth_day / self.__seconds_mars_day
        return delta_julian * day_length_ratio % self.__sols_per_mars_year

    def to_fractional_mars_year(self) -> float:
        """Convert the UTC to fractional Martian year.

        """
        delta_julian = self.__input_julian_date - self.__julian_ref
        day_length_ratio = self.__seconds_earth_day / self.__seconds_mars_day
        return delta_julian * day_length_ratio / self.__sols_per_mars_year + \
            self.__mars_year_ref

    def to_whole_mars_year(self) -> int:
        """Convert the UTC to the Martian year.

        """
        return int(np.floor(self.to_fractional_mars_year()))

    def to_ls(self) -> float:
        """Convert the UTC to Martian solar longitude.

        References
        ----------
        The equation used to convert to Ls can be found in `this paper
        <https://agupubs.onlinelibrary.wiley.com/doi/pdf/10.1029/97GL01950>`_

        """
        j2000 = julian.to_jd(datetime(2000, 1, 1, 12, 0, 0))
        dt_j2000 = self.__input_julian_date - j2000
        m = np.radians(19.41 + 0.5240212 * dt_j2000)
        a = 270.39 + 0.5240384 * dt_j2000
        ls = a + (10.691 + 3.7*10**-7 * dt_j2000) * np.sin(m) + \
            0.623*np.sin(2*m) + 0.05*np.sin(3*m) + 0.005*np.sin(4*m)
        return ls % 360


class ScienceWeek:
    """ScienceWeek can convert between dates and MAVEN science weeks.

    ScienceWeek contains a variety of methods that can either convert a week
    number into a datetime.date object representing the corresponding Earth
    date, or convert a datetime.date object into MAVEN science weeks.

    """
    def __init__(self):
        self.__science_start_date = date(2014, 11, 11)

    def week_from_date(self, some_date: date) -> int:
        """Compute the MAVEN science week number at an input date.

        Parameters
        ----------
        some_date: datetime.date
            The date to get the science week from.

        Returns
        -------
        int
            The science week at the input date.

        Raises
        ------
        TypeError
            Raised if the input is not an instance of datetime.date.

        Examples
        --------
        >>> from datetime import date
        >>> ScienceWeek().week_from_date(date(2020, 1, 1))
        268

        """
        try:
            self.__warn_if_date_is_before_mission_start(some_date)
            return (some_date - self.__science_start_date).days // 7
        except TypeError:
            message = 'some_date should be an instance of datetime.date.'
            raise TypeError(message) from None

    def current_science_week(self) -> int:
        """Compute today's MAVEN science week number.

        Returns
        -------
        int
            The current science week number.

        """
        return self.week_from_date(date.today())

    def week_start_date(self, week: int or float) -> date:
        """Compute the date when the requested science week began or will begin.

        Parameters
        ----------
        week: int or float
            The science week number.

        Returns
        -------
        datetime.date
            The date when the science week began or will begin.

        Raises
        ------
        TypeError
            Raised if the input type is incompatible with timedelta.
        ValueError
            Raised if the input has an error.

        Examples
        --------
        >>> ScienceWeek().week_start_date(0)
        datetime.date(2014, 11, 11)
        >>> ScienceWeek().week_start_date(300)
        datetime.date(2020, 8, 11)

        """
        try:
            self.__warn_if_week_is_negative(week)
            rounded_week = int(np.floor(week))
            return self.__science_start_date + timedelta(days=rounded_week * 7)
        except TypeError:
            raise TypeError(f'week should be an int, not a {type(week)}.') \
                from None
        except ValueError:
            raise ValueError('There is an issue with the value of week.') \
                from None

    def week_end_date(self, week: int or float) -> date:
        """Compute the date when the requested science week ended or will end.

        Parameters
        ----------
        week: int or float
            The science week number.

        Returns
        -------
        datetime.date
            The date when the science week ended or will end.

        Raises
        ------
        TypeError
            Raised if the input type is incompatible with timedelta.
        ValueError
            Raised if the input has an error.

        Examples
        --------
        >>> ScienceWeek().week_end_date(300)
        datetime.date(2020, 8, 17)

        """
        return self.week_start_date(week) + timedelta(days=6)

    def week_date_range(self, week: int or float) -> tuple[date, date]:
        """Compute the date range corresponding to the input science week.

        Parameters
        ----------
        week: int
            The science week.

        Returns
        -------
        tuple
            The start and end dates of the science week.

        Raises
        ------
        TypeError
            Raised if the input type is incompatible with timedelta.
        ValueError
            Raised if the input has an error.

        Examples
        --------
        >>> ScienceWeek().week_date_range(300)
        (datetime.date(2020, 8, 11), datetime.date(2020, 8, 17))

        """
        return self.week_start_date(week), self.week_end_date(week)

    def __warn_if_date_is_before_mission_start(self, some_date: date) -> None:
        if (some_date - self.__science_start_date).days < 0:
            warnings.warn('The input date is before the science start date.')

    @staticmethod
    def __warn_if_week_is_negative(week: int) -> None:
        if week < 0:
            warnings.warn('The input week should not be negative.')


if __name__ == '__main__':
    u = UTC(datetime(2018, 6, 27))
    print(u.to_ls())
    print(u.to_fractional_mars_year())
    print(u.to_sol())
