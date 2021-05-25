"""Collection of tools for converting between Earth and Martian times.
"""
import datetime
import warnings
import julian
import numpy as np


class ScienceWeek:
    """Convert between dates and MAVEN science weeks.

    This class contains a variety of methods that can either convert a science
    week number into an Earth date, or convert an Earth date into a MAVEN
    science weeks.

    Notes
    -----
    MAVEN's science weeks initially ran Tuesday--Monday, but in June of 2021
    they switched to a Thursday--Wednesday schedule.

    """
    def __init__(self):
        self.__science_start_date = datetime.date(2014, 11, 11)
        self.__normal_end_date = datetime.date(2021, 6, 8)
        self.__new_start_date = datetime.date(2021, 6, 10)

    @property
    def start_date(self) -> datetime.date:
        """Get the date that MAVEN begin performing science.

        """
        return self.__science_start_date

    def week_from_date(self, date: datetime.date) -> int:
        """Compute the MAVEN science week number corresponding to an input date.

        Parameters
        ----------
        date
            The date to get the science week from.

        Raises
        ------
        TypeError
            Raised if date is not a datetime.date.
        ValueError
            Raised if date is before the start of IUVS science.

        Warnings
        --------
        UserWarning
            Raised if the input date was during the bridge phase.

        Examples
        --------
        >>> import datetime
        >>> sw = ScienceWeek()
        >>> sw.week_from_date(sw.start_date)
        0
        >>> sw.week_from_date(datetime.date(2020, 1, 1))
        268

        """
        self._DateValidator(date, self.start_date)
        if date < self.__normal_end_date:
            return (date - self.start_date).days // 7
        elif date >= self.__new_start_date:
            return 343 + (date - self.__new_start_date).days // 7
        else:
            message = 'The requested date was during the bridge phase.'
            warnings.warn(message)
            return np.nan

    def current_science_week(self) -> int:
        """Compute today's MAVEN science week number.

        """
        return self.week_from_date(datetime.date.today())

    def week_start_date(self, week: int) -> datetime.date:
        """Compute the date when the requested science week began or will begin.

        Parameters
        ----------
        week
            The science week number.

        Raises
        ------
        TypeError
            Raised if week is not an int.
        ValueError
            Raised if week is negative.

        Examples
        --------
        >>> ScienceWeek().week_start_date(0)
        datetime.date(2014, 11, 11)
        >>> ScienceWeek().week_start_date(300)
        datetime.date(2020, 8, 11)

        """
        self._WeekValidator(week)
        if week < 343:
            return self.__science_start_date + datetime.timedelta(days=week*7)
        else:
            return self.__new_start_date + datetime.timedelta(days=(week-343)*7)

    def week_end_date(self, week: int) -> datetime.date:
        """Compute the date when the requested science week ended or will end.

        Parameters
        ----------
        week
            The science week number.

        Raises
        ------
        TypeError
            Raised if week is not an int.
        ValueError
            Raised if week is negative.

        Examples
        --------
        >>> ScienceWeek().week_end_date(300)
        datetime.date(2020, 8, 17)

        """
        return self.week_start_date(week) + datetime.timedelta(days=6)

    def week_date_range(self, week: int or float) -> \
            tuple[datetime.date, datetime.date]:
        """Compute the date range corresponding to the input science week.

        Parameters
        ----------
        week
            The science week number.

        Raises
        ------
        TypeError
            Raised if week is not an int.
        ValueError
            Raised if week is negative.

        Examples
        --------
        >>> ScienceWeek().week_date_range(300)
        (datetime.date(2020, 8, 11), datetime.date(2020, 8, 17))

        """
        return self.week_start_date(week), self.week_end_date(week)

    class _DateValidator:
        """Ensure an input date is a valid IUVS science date.

        """
        def __init__(self, date: datetime.date, start: datetime.date):
            """
            Parameters
            ----------
            date
                Any date.
            start
                The date IUVS began performing science.

            Raises
            ------
            TypeError
                Raised if date is not a datetime.date.
            ValueError
                Raised if date is before the start of IUVS science.

            """
            self.date = date
            self.start = start

            self.__raise_type_error_if_not_datetime_date()
            self.__raise_value_error_if_before_science_start()

        def __raise_type_error_if_not_datetime_date(self):
            if not isinstance(self.date, datetime.date):
                message = 'date must be a datetime.date'
                raise TypeError(message)

        def __raise_value_error_if_before_science_start(self):
            if (self.date - self.start).days < 0:
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
