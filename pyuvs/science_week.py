"""science_week.py contains ScienceWeek, which can perform conversions between
Earth times and MAVEN times.
"""
from datetime import date, timedelta
import warnings
import numpy as np


# TODO: clean up docstrings slightly
class ScienceWeek:
    """ScienceWeek can convert between dates and MAVEN science weeks.

    ScienceWeek contains a variety of methods that can either convert a week
    number into a datetime.date object representing the corresponding Earth
    date, or convert a datetime.date object into MAVEN science weeks.

    """

    @property
    def science_start_date(self) -> date:
        """ Get the date MAVEN/IUVS began performing science.

        Returns
        -------
        date: datetime.date
            The date MAVEN/IUVS began performing science.
        """
        return date(2014, 11, 11)

    def week_from_date(self, some_date: date) -> int:
        """ Get the science week number at an input date.

        Parameters
        ----------
        some_date: datetime.date
            The date at which to get the science week.

        Returns
        -------
        science_week: int
            The science week at the input date.

        Examples
        --------
        >>> ScienceWeek().week_from_date(date(2020, 1, 1))
        268
        """
        try:
            self.__warn_if_date_is_before_mission_start(some_date)
            return (some_date - self.science_start_date).days // 7
        except TypeError:
            raise TypeError('some_date should be of type datetime.date.')

    def current_science_week(self) -> int:
        """ Get today's science week number.

        Returns
        -------
        science_week: int
            The current science week number.
        """
        return self.week_from_date(date.today())

    def week_start_date(self, week: int) -> date:
        """ Get the date when the requested science week began or will begin.

        Parameters
        ----------
        week: int
            The science week.

        Returns
        -------
        science_week_start: datetime.date
            The date when the science week started.

        Examples
        --------
        >>> ScienceWeek().week_start_date(300)
        datetime.date(2020, 8, 11)
        """
        try:
            self.__warn_if_week_is_negative(week)
            rounded_week = int(np.floor(week))
            return self.science_start_date + timedelta(days=rounded_week * 7)
        except TypeError:
            raise TypeError(f'"week" should be an int, not a {type(week)}.')

    def week_end_date(self, week: int) -> date:
        """ Get the date when the requested science week ended or will end.

        Parameters
        ----------
        week: int
            The science week.

        Returns
        -------
        science_week_end: datetime.date
            The date when the science week ended.

        Examples
        --------
        >>> ScienceWeek().week_end_date(300)
        datetime.date(2020, 8, 17)
        """
        return self.week_start_date(week) + timedelta(days=6)

    def week_date_range(self, week: int) -> tuple[date, date]:
        """ Get the date range corresponding to the input science week.

        Parameters
        ----------
        week: int
            The science week.

        Returns
        -------
        date_range: tuple
            The start and end dates of the science week.

        Examples
        --------
        >>> ScienceWeek().week_date_range(300)
        (datetime.date(2020, 8, 11), datetime.date(2020, 8, 17))
        """
        return self.week_start_date(week), self.week_end_date(week)

    def __warn_if_date_is_before_mission_start(self, some_date: date) -> None:
        if (some_date - self.science_start_date).days < 0:
            warnings.warn('The input date is before the science start date.')

    @staticmethod
    def __warn_if_week_is_negative(week: int) -> None:
        if week < 0:
            warnings.warn('The input week should not be negative.')
