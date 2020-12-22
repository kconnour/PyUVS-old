# Built-in imports
from unittest import TestCase
from datetime import date, timedelta
import warnings
import os

# Local imports
from maven_iuvs.files.files import Files
from maven_iuvs.get_module_path import get_module_path


class TestFiles(TestCase):
    def setUp(self):
        self.files = Files
        self.npy_files = Files(os.path.join(get_module_path(), 'aux'), '**/*.npy')
        self.jpg_files = Files(os.path.join(get_module_path(), 'aux'), '**/*.jpg')


class TestFilesInit(TestFiles):
    def test_files_has_absolute_file_paths_attribute(self):
        self.assertTrue(hasattr(self.files, 'absolute_file_paths'))

    def test_files_has_filenames_attribute(self):
        self.assertTrue(hasattr(self.files, 'filenames'))

    def test_files_has_exactly_two_attributes(self):
        self.assertTrue(len(self.files.__dict__.keys()), 2)

    def test_files_found_correct_aux_absolute_paths(self):
        npy_files = []
        npy_files.append(os.path.join(get_module_path(), 'aux/flatfield133.npy'))
        npy_files.append(os.path.join(get_module_path(), 'aux/flatfield50rebin.npy'))
        self.assertEqual(npy_files, self.npy_files.absolute_file_paths)

        jpg_files = []
        jpg_files.append(os.path.join(get_module_path(), 'aux/mars_surface_map.jpg'))
        self.assertEqual(jpg_files, self.jpg_files.absolute_file_paths)

    def test_files_found_correct_aux_filenames(self):
        npy_files = []
        npy_files.append('flatfield133.npy')
        npy_files.append('flatfield50rebin.npy')
        self.assertEqual(npy_files, self.npy_files.filenames)

        jpg_files = []
        jpg_files.append('mars_surface_map.jpg')
        self.assertEqual(jpg_files, self.jpg_files.filenames)

    def test_absolute_file_paths_cannot_be_modified(self):
        with self.assertRaises(AttributeError):
            self.npy_files.absolute_file_paths = 0

    def test_filenames_cannot_be_modified(self):
        with self.assertRaises(AttributeError):
            self.npy_files.filenames = 0

    def test_nonexistent_path_raises_os_error(self):
        nonexistent_path = 'lBGduwfTwq'
        with self.assertRaises(OSError):
            self.files(nonexistent_path, '*')

    def test_int_path_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.files(1, '*.npy')

    def test_int_pattern_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.files(get_module_path(), 1)

    def test_nonexistent_files_raises_warning(self):
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            self.files(get_module_path(), 'aux/*.pdf')
            self.assertEqual(1, len(warning))
            self.assertEqual(warning[-1].category, UserWarning)


class TestGetAbsolutePathsOfFilenamesContainingPattern(TestFiles):
    def test_constructor_input_pattern_gives_same_result(self):
        self.assertEqual(self.npy_files.absolute_file_paths,
                         self.npy_files.get_absolute_paths_of_filenames_containing_pattern('*.npy'))

    def test_paths_are_within_absolute_file_paths(self):
        self.assertTrue(self.npy_files.get_absolute_paths_of_filenames_containing_pattern('*133*.npy')[0] in
                        self.npy_files.absolute_file_paths)

    def test_int_input_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.npy_files.get_absolute_paths_of_filenames_containing_pattern(1)

    def test_nonexistent_files_raises_warning(self):
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            self.npy_files.get_absolute_paths_of_filenames_containing_pattern('*.pdf')
            self.assertEqual(1, len(warning))
            self.assertEqual(warning[-1].category, UserWarning)

    def test_nonexistent_files_output_empty_list(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            output = self.npy_files.get_absolute_paths_of_filenames_containing_pattern('*.pdf')
            self.assertEqual([], output)


class TestGetFilenamesContainingPattern(TestFiles):
    def test_constructor_input_pattern_gives_same_result(self):
        self.assertEqual(self.npy_files.filenames, self.npy_files.get_filenames_containing_pattern('*.npy'))

    def test_paths_are_within_absolute_file_paths(self):
        self.assertTrue(self.npy_files.get_filenames_containing_pattern('*133*.npy')[0] in self.npy_files.filenames)

    def test_int_input_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.npy_files.get_filenames_containing_pattern(1)

    def test_nonexistent_files_raises_warning(self):
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            self.npy_files.get_filenames_containing_pattern('*.pdf')
            self.assertEqual(1, len(warning))
            self.assertEqual(warning[-1].category, UserWarning)

    def test_nonexistent_files_output_empty_list(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            output = self.npy_files.get_filenames_containing_pattern('*.pdf')
            self.assertEqual([], output)
