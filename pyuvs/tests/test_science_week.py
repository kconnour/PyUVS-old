from datetime import date
from unittest import TestCase, mock
import warnings
import numpy as np
from pyuvs.science_week import ScienceWeek


class TestWeekFromDate(TestCase):
    def test_science_start_date_is_week_0(self) -> None:
        self.assertEqual(0, ScienceWeek().week_from_date(date(2014, 11, 11)))

    def test_known_science_week_and_date_matches_output(self) -> None:
        self.assertEqual(317, ScienceWeek().week_from_date(date(2020, 12, 14)))

    def test_int_input_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            ScienceWeek().week_from_date(100)

    def test_date_before_mission_start_raises_warning(self) -> None:
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            ScienceWeek().week_from_date(date(2000, 1, 1))
            self.assertEqual(1, len(warning))
            self.assertEqual(warning[-1].category, UserWarning)


class TestCurrentScienceWeek(TestCase):
    def test_current_science_week_as_though_today_was_mock_date(self) -> None:
        with mock.patch('pyuvs.science_week.date') as mock_date:
            mock_date.today.return_value = date(2020, 1, 1)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            self.assertEqual(268, ScienceWeek().current_science_week())


class TestWeekStartDate(TestCase):
    def test_start_of_week_0_is_mission_arrival_date(self) -> None:
        self.assertEqual(date(2014, 11, 11), ScienceWeek().week_start_date(0))

    def test_example_science_week_matches_its_known_start_date(self) -> None:
        self.assertEqual(date(2020, 12, 8), ScienceWeek().week_start_date(317))

    def test_floats_between_two_consecutive_integers_give_lower_output(self) \
            -> None:
        with warnings.catch_warnings(record=True):
            self.assertEqual(ScienceWeek().week_start_date(317),
                             ScienceWeek().week_start_date(317.0),
                             ScienceWeek().week_start_date(
                                 np.nextafter(318, 317)))

    def test_string_input_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            ScienceWeek().week_start_date('100')

    def test_ndarray_input_raises_value_error(self) -> None:
        test_weeks = np.linspace(1, 50, num=50, dtype=int)
        with self.assertRaises(ValueError):
            ScienceWeek().week_start_date(test_weeks)

    def test_nan_input_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            ScienceWeek().week_start_date(np.nan)

    def test_float_week_raises_no_warnings(self) -> None:
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            ScienceWeek().week_start_date(1.5)
            self.assertEqual(0, len(warning))

    def test_negative_week_raises_warning(self) -> None:
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            ScienceWeek().week_start_date(-1)
            self.assertEqual(1, len(warning))
            self.assertEqual(warning[-1].category, UserWarning)


class TestWeekEndDate(TestCase):
    def test_end_of_week_0_is_6_days_after_science_start_date(self) -> None:
        self.assertEqual(date(2014, 11, 17), ScienceWeek().week_end_date(0))

    def test_example_science_week_matches_its_known_end_date(self) -> None:
        self.assertEqual(date(2020, 12, 14), ScienceWeek().week_end_date(317))

    def test_floats_between_two_consecutive_integers_give_lower_output(self) \
            -> None:
        with warnings.catch_warnings(record=True):
            self.assertEqual(ScienceWeek().week_end_date(317),
                             ScienceWeek().week_end_date(317.0),
                             ScienceWeek().week_end_date(
                                 np.nextafter(318, 317)))

    def test_string_input_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            ScienceWeek().week_end_date('100')

    def test_ndarray_input_raises_value_error(self) -> None:
        test_weeks = np.linspace(1, 50, num=50, dtype=int)
        with self.assertRaises(ValueError):
            ScienceWeek().week_end_date(test_weeks)

    def test_nan_input_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            ScienceWeek().week_end_date(np.nan)

    def test_float_week_raises_no_warnings(self) -> None:
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            ScienceWeek().week_end_date(1.5)
            self.assertEqual(0, len(warning))

    def test_negative_week_raises_warning(self) -> None:
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            ScienceWeek().week_end_date(-1)
            self.assertEqual(1, len(warning))
            self.assertEqual(warning[-1].category, UserWarning)


class TestWeekDateRange(TestCase):
    def test_output_is_result_of_start_and_end_date_methods(self) -> None:
        expected = (ScienceWeek().week_start_date(100),
                    ScienceWeek().week_end_date(100))
        self.assertEqual(expected, ScienceWeek().week_date_range(100))

    def test_negative_week_throws_1_warning(self) -> None:
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("default")
            ScienceWeek().week_date_range(-1)
            self.assertEqual(1, len(warning))
            self.assertEqual(warning[-1].category, UserWarning)
