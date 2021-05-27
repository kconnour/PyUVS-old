"""Convert UTC times into Martian times.

This module provides functions to convert coordinated universal time (UTC) into
Martian sols, Martian years, and solar longitude.

"""
import datetime
import math
import numpy as np
from pyuvs.constants import seconds_per_sol, sols_per_martian_year, \
    date_of_start_of_mars_year_0


def convert_to_solar_longitude(date: datetime.datetime) -> float:
    """Compute the Martian solar longitude of an input datetime.

    Parameters
    ----------
    date
        Any date.

    Raises
    ------
    TypeError
        Raised if :code:`date` is not a datetime.datetime.

    References
    ----------
    The equation used to convert to Ls can be found in `this paper
    <https://agupubs.onlinelibrary.wiley.com/doi/pdf/10.1029/97GL01950>`_."""
    _DateValidator(date)
    j2000 = datetime.datetime(2000, 1, 1, 12, 0, 0)
    elapsed_days = (date - j2000).total_seconds() / 86400
    m = np.radians(19.41 + 0.5240212 * elapsed_days)
    a = 270.39 + 0.5240384 * elapsed_days
    ls = a + (10.691 + 3.7 * 10 ** -7 * elapsed_days) * np.sin(m) + \
        0.623 * np.sin(2 * m) + 0.05 * np.sin(3 * m) + 0.005 * np.sin(4 * m)
    return ls % 360


def convert_to_fractional_mars_year(date: datetime.datetime) -> float:
    """Compute the fractional Mars year of an input datetime.

    Parameters
    ----------
    date
        Any date.

    Raises
    ------
    TypeError
        Raised if :code:`date` is not a datetime.datetime.

    """
    return sols_after_mars_year_0(date) / sols_per_martian_year


def convert_to_whole_mars_year(date: datetime.datetime) -> int:
    """Compute the integer Mars year of an input datetime.

    Parameters
    ----------
    date
        Any date.

    Raises
    ------
    TypeError
        Raised if :code:`date` is not a datetime.datetime.

    """
    return math.floor(convert_to_fractional_mars_year(date))


def convert_to_sol_number(date: datetime.datetime) -> float:
    """Compute the sol number (day of the year) of an input datetime.

    Parameters
    ----------
    date
        Any date.

    Raises
    ------
    TypeError
        Raised if :code:`date` is not a datetime.datetime.

    Notes
    -----
    This function begins counting from 0. Beware that some places like LMD
    use the convention that the new year starts on sol 1.

    """
    return sols_after_mars_year_0(date) % sols_per_martian_year


def sols_between_two_dates(early_date: datetime.datetime,
                           later_date: datetime.datetime) -> float:
    """Compute the number of sols between two datetimes.

    Parameters
    ----------
    early_date
        The earlier of the two dates.
    later_date
        The latter of the two dates.

    Raises
    ------
    TypeError
        Raised if either :code:`early_date` or :code:`later_date` are not a
        datetime.datetime.

    """
    _DateValidator(early_date)
    _DateValidator(later_date)
    elapsed_seconds = (later_date - early_date).total_seconds()
    return elapsed_seconds / seconds_per_sol


def sols_since_date(date: datetime.datetime) -> float:
    """Compute the number of sols between an input datetime and today.

    Parameters
    ----------
    date
        Any date.

    Raises
    ------
    TypeError
        Raised if :code:`date` is not a datetime.datetime.

    """
    return sols_between_two_dates(date, datetime.datetime.today())


def sols_after_mars_year_0(date: datetime.datetime) -> float:
    """Compute the number of sols between a datetime and the start of Mars year
    0.

    Parameters
    ----------
    date
        Any date.

    Raises
    ------
    TypeError
        Raised if :code:`date` is not a datetime.datetime.

    """
    return sols_between_two_dates(date_of_start_of_mars_year_0, date)


class _DateValidator:
    """Ensure an input date is a valid UTC datetime.

    """
    def __init__(self, date: datetime.datetime):
        """
        Parameters
        ----------
        date
            Any date.

        Raises
        ------
        TypeError
            Raised if date is not a datetime.date.

        """
        self.date = date

        self.__raise_type_error_if_not_datetime_date()

    def __raise_type_error_if_not_datetime_date(self):
        if not isinstance(self.date, datetime.datetime):
            message = 'date must be a datetime.datetime.'
            raise TypeError(message)


if __name__ == '__main__':
    d = datetime.datetime(2018, 10, 10, 0, 53, 30)
    print(convert_to_solar_longitude(date_of_start_of_mars_year_0))
    print(convert_to_sol_number(d))
