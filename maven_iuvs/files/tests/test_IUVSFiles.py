# Built-in imports
import os
from unittest import TestCase
import warnings

# Local imports
from maven_iuvs.files.files import IUVSFiles


class TestIUVSFiles(TestCase):
    def setUp(self):
        self._path = os.path.join(os.path.dirname(os.path.abspath(
            os.path.realpath(__file__))), 'test_filenames')
        self.files = IUVSFiles(self._path, '*')


class TestInit(TestIUVSFiles):
    def test_init_found_13_iuvs_files(self):
        self.assertEqual(13, len(self.files.filenames))

    def test_init_raises_no_warnings_when_downselecting(self):
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            IUVSFiles(self._path, '*')
            self.assertEqual(0, len(warning))

    def test_init_raises_value_error_if_no_iuvs_files(self):
        with self.assertRaises(ValueError):
            IUVSFiles(self._path, 'mars*')
