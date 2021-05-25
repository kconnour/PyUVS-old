"""Convert between dates and IUVS science weeks.

This module provides functions to convert between Earth dates and IUVS science
week numbers, along with functions to convert science week numbers into Earth
dates.

Notes
-----
IUVS's science week schedule initially ran Tuesday--Monday. This ended
June 8, 2021 when Lockheed Martin implemented "wizard-ops", leading to a 2 day
science pause. Science weeks switched to a Thursday--Wednesday schedule
afterwards.

"""
import datetime
import warnings

science_start_date: datetime.date = datetime.date(2014, 11, 11)
"""Date MAVEN began performing nominal science."""

pre_wizard_end_date = datetime.date(2021, 6, 7)
"""Last date of nominal science before wizard-ops."""

post_wizard_start_date = datetime.date(2021, 6, 10)
"""First date of nominal science after wizard-ops."""


def week_from_date(date: datetime.date) -> int:
    """Compute the IUVS science week number corresponding to an input date.

    Parameters
    ----------
    date
        The date to get the science week from.

    Raises
    ------
    TypeError
        Raised if :code:`date` is not a datetime.date.
    ValueError
        Raised if :code:`date` is before the start of IUVS science.

    Warnings
    --------
    UserWarning
        Raised if the input date was during the bridge phase.

    Examples
    --------
    >>> import datetime
    >>> week_from_date(science_start_date)
    0
    >>> week_from_date(datetime.date(2020, 1, 1))
    268

    """
    _DateValidator(date)
    if date <= pre_wizard_end_date:
        return (date - science_start_date).days // 7
    elif date >= post_wizard_start_date:
        return 343 + (date - post_wizard_start_date).days // 7
    else:
        message = 'The requested date was during the bridge phase.'
        warnings.warn(message)


def current_week() -> int:
    """Compute today's MAVEN science week number.

    """
    return week_from_date(datetime.date.today())


def week_start_date(week: int) -> datetime.date:
    """Compute the date when the requested science week began or will begin.

    Parameters
    ----------
    week
        The science week number.

    Raises
    ------
    TypeError
        Raised if :code:`week` is not an int.
    ValueError
        Raised if :code:`week` is negative.

    Examples
    --------
    >>> week_start_date(0)
    datetime.date(2014, 11, 11)
    >>> week_start_date(300)
    datetime.date(2020, 8, 11)

    """
    _WeekValidator(week)
    if week < 343:
        return science_start_date + datetime.timedelta(days=week*7)
    else:
        return post_wizard_start_date + datetime.timedelta(days=(week-343)*7)


def week_end_date(week: int) -> datetime.date:
    """Compute the date when the requested science week ended or will end.

    Parameters
    ----------
    week
        The science week number.

    Raises
    ------
    TypeError
        Raised if :code:`week` is not an int.
    ValueError
        Raised if :code:`week` is negative.

    Examples
    --------
    >>> week_end_date(300)
    datetime.date(2020, 8, 17)

    """
    return week_start_date(week) + datetime.timedelta(days=6)


def week_date_range(week: int or float) -> tuple[datetime.date, datetime.date]:
    """Compute the date range corresponding to the input science week.

    Parameters
    ----------
    week
        The science week number.

    Raises
    ------
    TypeError
        Raised if :code:`week` is not an int.
    ValueError
        Raised if :code:`week` is negative.

    Examples
    --------
    >>> week_date_range(300)
    (datetime.date(2020, 8, 11), datetime.date(2020, 8, 17))

    """
    return week_start_date(week), week_end_date(week)


class _DateValidator:
    """Ensure an input date is a valid IUVS science date.

    """
    def __init__(self, date: datetime.date):
        """
        Parameters
        ----------
        date
            Any date.

        Raises
        ------
        TypeError
            Raised if date is not a datetime.date.
        ValueError
            Raised if date is before the start of IUVS science.

        """
        self.date = date

        self.__raise_type_error_if_not_datetime_date()
        self.__raise_value_error_if_before_science_start()

    def __raise_type_error_if_not_datetime_date(self):
        if not isinstance(self.date, datetime.date):
            message = 'date must be a datetime.date'
            raise TypeError(message)

    def __raise_value_error_if_before_science_start(self):
        if (self.date - science_start_date).days < 0:
            message = 'date is before the start of IUVS science.'
            raise ValueError(message)


class _WeekValidator:
    """Ensure an input week is a valid IUVS science week.

    """
    def __init__(self, week: int):
        """
        Parameters
        ----------
        week
            Any plausible science week.

        Raises
        ------
        TypeError
            Raised if week is not an int.
        ValueError
            Raised if week is negative.

        """
        self.week = week

        self.__raise_type_error_if_not_int()
        self.__raise_value_error_if_before_mission_start()

    def __raise_type_error_if_not_int(self):
        if not isinstance(self.week, int):
            message = 'week must be an int.'
            raise TypeError(message)

    def __raise_value_error_if_before_mission_start(self) -> None:
        if self.week < 0:
            message = 'week must be non-negative.'
            raise ValueError(message)
