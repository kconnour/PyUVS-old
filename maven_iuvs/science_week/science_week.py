# Built-in imports
from datetime import date, timedelta
import warnings

# 3rd-party imports
import numpy as np


class ScienceWeek:
    """ A ScienceWeek object can convert dates into MAVEN science weeks. """
    @property
    def science_start_date(self):
        """ Get the date MAVEN/IUVS began performing science.

        Returns
        -------
        date: datetime.date
            The date MAVEN/IUVS began performing science.
        """
        return date(2014, 11, 11)

    def week_from_date(self, some_date):
        """ Get the science week number at an input date.

        Parameters
        ----------
        some_date: datetime.date
            The date at which to get the science week.

        Returns
        -------
        science_week: int
            The science week at the input date.
        """
        try:
            self.__warn_if_date_is_before_mission_start(some_date)
            return (some_date - self.science_start_date).days // 7
        except TypeError:
            raise TypeError('"some_date" should be of type datetime.date')

    def current_science_week(self):
        """ Get the science week number for today.

        Returns
        -------
        science_week: int
            The current science week.
        """
        return self.week_from_date(date.today())

    def week_start_date(self, week):
        """ Get the date when the requested science week began or will begin.

        Parameters
        ----------
        week: int
            The science week.

        Returns
        -------
        science_week_start: datetime.date
            The date when the science week started.
        """
        try:
            self.__warn_if_week_is_negative(week)
            rounded_week = int(np.floor(week))
            if week != rounded_week:
                warnings.warn('This is a non-integer week. '
                              'Converting it to integer...')
            science_week_start = self.science_start_date + \
                                 timedelta(days=rounded_week * 7)
            return science_week_start
        except TypeError:
            raise TypeError(f'"week" should be an int, not a {type(week)}.')

    def week_end_date(self, week):
        """ Get the date when the requested science week ended or will end.

        Parameters
        ----------
        week: int
            The science week.

        Returns
        -------
        science_week_end: datetime.date
            The date when the science week ended.
        """
        return self.week_start_date(week) + timedelta(days=6)

    def week_date_range(self, week):
        """ Get the date range corresponding to the input science week.

        Parameters
        ----------
        week: int
            The science week.

        Returns
        -------
        date_range: tuple
            The start and end dates of the science week.
        """
        return self.week_start_date(week), self.week_end_date(week)

    def __warn_if_date_is_before_mission_start(self, some_date):
        if (some_date - self.science_start_date).days < 0:
            warnings.warn('The input date is before the science start date.')

    @staticmethod
    def __warn_if_week_is_negative(week):
        if week < 0:
            warnings.warn('The input week should not be negative.')
