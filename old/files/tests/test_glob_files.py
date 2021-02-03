# Built-in imports
import os
from pathlib import PosixPath
from unittest import TestCase, mock

# Local imports
from old.files import glob_files


class TestGlobFiles(TestCase):
    def test_glob_finds_all_abs_paths_of_only_files(self):
        with mock.patch('pathlib.Path.glob') as mock_glob, \
                mock.patch('pathlib.PosixPath.is_file') as mock_path:
            dummy_names = ['foo', 'bar', 'baz']
            dummy_files = (PosixPath(f'/{f}.{f}') for f in dummy_names)
            expected_files = sorted([f'/{f}.{f}' for f in dummy_names])
            mock_glob.return_value = dummy_files
            mock_path.return_value = True
            self.assertEqual(expected_files,
                             glob_files(os.path.abspath(os.sep), ''))
