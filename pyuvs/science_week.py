"""science_week.py contains ScienceWeek, which can perform conversions between
Earth times and MAVEN times.
"""
from datetime import date, timedelta
import warnings
import numpy as np


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
