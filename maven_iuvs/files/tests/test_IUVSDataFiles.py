# Built-in imports
import os
from unittest import TestCase
import warnings

# Local imports
from maven_iuvs.files.files import IUVSDataFiles


class TestIUVSDataFiles(TestCase):
    def setUp(self):
        self._path = os.path.join(os.path.dirname(os.path.abspath(
            os.path.realpath(__file__))), 'test_filenames')
        self.files = IUVSDataFiles(self._path, '*')


class TestInit(TestIUVSDataFiles):
    def test_init_found_11_iuvs_data_files(self):
        self.assertEqual(11, len(self.files.filenames))

    def test_init_raises_no_warnings_when_downselecting(self):
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            IUVSDataFiles(self._path, '*')
            self.assertEqual(0, len(warning))

    def test_init_raises_value_error_if_no_iuvs_data_files(self):
        with self.assertRaises(ValueError):
            IUVSDataFiles(self._path, '*flatfield*')
