# Built-in imports
from datetime import date, timedelta
import warnings

# 3rd-party imports
import numpy as np


class ScienceWeek:
    # TODO: Decide if I want to prohibit users from inputting negative science weeks, or dates that result in them
    # TODO: Decide how to handle future science week (should I warn if they request science week from a future date?)
    def __init__(self):
        """ A ScienceWeek object can convert dates into MAVEN science weeks.

        Properties
        ----------
        science_start_date: datetime.date
            The date when IUVS began performing science.
        """
        self.__science_start_date = date(2014, 11, 11)

    @property
    def science_start_date(self):
        return self.__science_start_date

    def get_science_week_from_date(self, some_date):
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
            science_week = (some_date - self.__science_start_date).days // 7
            return science_week
        except TypeError:
            raise TypeError('some_date should be of type datetime.date')

    def get_current_science_week(self):
        """ Get the science week number for today.

        Returns
        -------
        science_week: int
            The current science week.
        """
        science_week = self.get_science_week_from_date(date.today())
        return science_week

    def get_science_week_start_date(self, week):
        """ Get the date when the requested science week began.

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
            rounded_week = int(np.floor(week))
            if week != rounded_week:
                warnings.warn('This is a non-integer week. Converting it to integer...')
            science_week_start = self.__science_start_date + timedelta(days=rounded_week * 7)
            return science_week_start
        except TypeError:
            raise TypeError(f'week should be an int, not a {type(week)}.')

    def get_science_week_end_date(self, week):
        """ Get the date when the requested science week ended.

        Parameters
        ----------
        week: int
            The science week.

        Returns
        -------
        science_week_end: datetime.date
            The date when the science week ended.
        """
        return self.get_science_week_start_date(week + 1) - timedelta(days=1)

    def get_science_week_date_range(self, week):
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
        date_range = self.get_science_week_start_date(week), self.get_science_week_end_date(week)
        return date_range


# TODO: Decide if I want a subclass to handle requests related to science week (ex. get_orbit_range_from_science_week)
# Pro: It's easy to code after making the database and it'd be helpful
# Con: It might be easier to make 1 utility for database searching and tell users to apply it to science week
