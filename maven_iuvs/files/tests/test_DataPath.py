# Built-in imports
import inspect
from unittest import TestCase

# Local imports
from maven_iuvs.files.finder import DataPath


'''class TestScienceWeek(TestCase):
    def setUp(self):
        self.science_week = ScienceWeek()


class TestInit(TestScienceWeek):
    def test_science_week_has_science_start_date_property(self):
        self.assertTrue(not inspect.ismethod(ScienceWeek.science_start_date))

    def test_science_week_has_no_attributes(self):
        self.assertEqual(0, len(self.science_week.__dict__.keys()))


class TestScienceStartDate(TestScienceWeek):
    def test_science_start_date_is_2014_11_11(self):
        self.assertEqual(date(2014, 11, 11),
                         self.science_week.science_start_date)

    def test_science_start_date_is_immutable(self):
        with self.assertRaises(AttributeError):
            self.science_week.science_start_date = date(2014, 11, 11)'''