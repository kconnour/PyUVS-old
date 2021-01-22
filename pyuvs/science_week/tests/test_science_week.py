# Built-in imports
from unittest import TestCase, mock
from datetime import date, timedelta
import warnings

# 3rd-party imports
import numpy as np

# Local imports
from pyuvs.science_week.science_week import ScienceWeek


class TestScienceWeek(TestCase):
    def setUp(self):
        self.science_week = ScienceWeek()


class TestScienceStartDate(TestScienceWeek):
    def test_science_start_date_is_2014_11_11(self):
        self.assertEqual(date(2014, 11, 11),
                         self.science_week.science_start_date)

    def test_science_start_date_is_immutable(self):
        with self.assertRaises(AttributeError):
            self.science_week.science_start_date = date(2014, 11, 11)


class TestWeekFromDate(TestScienceWeek):
    def test_science_start_date_is_week_0(self):
        self.assertEqual(0, self.science_week.week_from_date(
            self.science_week.science_start_date))

    def test_known_science_week_and_date_matches_output(self):
        test_date = date(2020, 12, 14)
        self.assertEqual(317, self.science_week.week_from_date(test_date))

    def test_int_input_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.science_week.week_from_date(100)

    def test_date_before_mission_start_raises_warning(self):
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            self.science_week.week_from_date(date(2000, 1, 1))
            self.assertEqual(1, len(warning))
            self.assertEqual(warning[-1].category, UserWarning)


class TestGetCurrentScienceWeek(TestScienceWeek):
    def test_science_week_of_today(self):
        with mock.patch('pyuvs.science_week.date') as mock_date:
            mock_date.today.return_value = date(2020, 1, 1)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            self.assertEqual(268, self.science_week.current_science_week())


class TestWeekStartDate(TestScienceWeek):
    def test_start_of_week_0_is_mission_arrival_date(self):
        self.assertEqual(self.science_week.science_start_date,
                         self.science_week.week_start_date(0))

    def test_example_science_week_matches_its_known_start_date(self):
        self.assertEqual(date(2020, 12, 8),
                         self.science_week.week_start_date(317))

    def test_floats_between_two_consecutive_integers_give_lower_output(self):
        with warnings.catch_warnings(record=True):
            self.assertEqual(self.science_week.week_start_date(317),
                             self.science_week.week_start_date(317.0),
                             self.science_week.week_start_date(
                                 np.nextafter(318, 317)))

    def test_float_week_raises_no_warnings(self):
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            self.science_week.week_start_date(1.5)
            self.assertEqual(0, len(warning))

    def test_ndarray_input_raises_value_error(self):
        test_weeks = np.linspace(1, 50, num=50, dtype=int)
        with self.assertRaises(ValueError):
            self.science_week.week_start_date(test_weeks)

    def test_string_input_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.science_week.week_start_date('100')

    def test_nan_input_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.science_week.week_start_date(np.nan)

    def test_negative_week_raises_warning(self):
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            self.science_week.week_start_date(-1)
            self.assertEqual(1, len(warning))
            self.assertEqual(warning[-1].category, UserWarning)


class TestWeekEndDate(TestScienceWeek):
    def test_end_of_week_0_is_6_days_after_science_start_date(self):
        self.assertEqual(self.science_week.science_start_date +
                         timedelta(days=6), self.science_week.week_end_date(0))

    def test_example_science_week_matches_its_known_end_date(self):
        self.assertEqual(date(2020, 12, 14),
                         self.science_week.week_end_date(317))

    def test_floats_between_two_consecutive_integers_give_lower_output(self):
        with warnings.catch_warnings(record=True):
            self.assertEqual(self.science_week.week_end_date(317),
                             self.science_week.week_end_date(317.0),
                             self.science_week.week_end_date(
                                 np.nextafter(318, 317)))

    def test_float_week_raises_no_warnings(self):
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            self.science_week.week_end_date(1.5)
            self.assertEqual(0, len(warning))

    def test_ndarray_input_raises_value_error(self):
        test_weeks = np.linspace(1, 50, num=50, dtype=int)
        with self.assertRaises(ValueError):
            self.science_week.week_end_date(test_weeks)

    def test_string_input_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.science_week.week_end_date('100')

    def test_nan_input_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.science_week.week_end_date(np.nan)

    def test_negative_week_raises_warning(self):
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            self.science_week.week_end_date(-1)
            self.assertEqual(1, len(warning))
            self.assertEqual(warning[-1].category, UserWarning)


class TestWeekDateRange(TestScienceWeek):
    def test_output_is_tuple(self):
        self.assertTrue(isinstance(self.science_week.week_date_range(100),
                                   tuple))

    def test_output_is_2_elements(self):
        self.assertTrue(len(self.science_week.week_date_range(100)), 2)

    def test_output_is_result_of_start_and_end_date_methods(self):
        self.assertTrue(self.science_week.week_start_date(100),
                        self.science_week.week_date_range(100)[0])
        self.assertTrue(self.science_week.week_end_date(100),
                        self.science_week.week_date_range(100)[1])

    def test_negative_week_throws_1_warning_by_default(self):
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("default")
            self.science_week.week_date_range(-1)
            self.assertEqual(1, len(warning))
            self.assertEqual(warning[-1].category, UserWarning)
