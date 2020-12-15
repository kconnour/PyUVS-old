# Built-in imports
import unittest
import os

# Local imports
from maven_iuvs.files.files import Files
from aux.aux_files import aux_path


class TestFiles(unittest.TestCase):
    def setUp(self):
        self.files = Files


class TestInit(TestFiles):
    def test_int_input_raises_value_error(self):
        self.assertRaises(TypeError, lambda: self.files(1, 1))

    def test_input_npy_files(self):
        files = self.files('*.npy', aux_path())
        npy_files = sorted(['flatfield50rebin.npy', 'flatfield133.npy'])
        for counter, f in enumerate(npy_files):
            npy_files[counter] = os.path.join(aux_path(), f)
        self.assertEqual(files.file_paths, npy_files)

    def test_recursive_input_npy_files(self):
        module_path = os.path.abspath(os.path.join(aux_path(), '..'))
        files = self.files('*.npy', module_path, recursive=True)
        npy_files = sorted(['flatfield50rebin.npy', 'flatfield133.npy'])
        for counter, f in enumerate(npy_files):
            npy_files[counter] = os.path.join(aux_path(), f)
        self.assertEqual(files.file_paths, npy_files)


#class TestGetFilenamesContainingPattern(TestFiles):

