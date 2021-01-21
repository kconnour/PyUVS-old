# Built-in imports
import os
from unittest import TestCase

# 3rd-party imports
import numpy as np

# Local imports
from pyuvs.files.finder import DataPath


class TestDataPath(TestCase):
    def setUp(self):
        self.root = '/foo/bar'
        self.path = DataPath(self.root)


class TestInit(TestDataPath):
    def test_DataPath_has_one_attribute(self):
        self.assertEqual(1, len(self.path.__dict__.keys()))

    def test_DataPath_cannot_be_initialized_with_int(self):
        with self.assertRaises(TypeError):
            DataPath(1)

    def test_DataPath_cannot_be_initialized_with_float(self):
        with self.assertRaises(TypeError):
            DataPath(2.5)

    def test_DataPath_cannot_be_initialized_with_list(self):
        with self.assertRaises(TypeError):
            DataPath([self.root])


class TestBlock(TestDataPath):
    def test_block_matches_expected_output(self):
        expected_path = os.path.join(self.root, 'orbit07700')
        self.assertEqual(expected_path, self.path.block(7700))
        self.assertEqual(expected_path, self.path.block(7799))

    def test_float_input_works(self):
        expected_path = os.path.join(self.root, 'orbit07700')
        self.assertEqual(expected_path, self.path.block(7700.0))

    def test_input_str_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.path.block('orbit07700')


class TestBlockPaths(TestDataPath):
    def test_block_paths_matches_expected_output_for_list(self):
        expected_output = [f'{self.root}/orbit07700',
                           f'{self.root}/orbit07700',
                           f'{self.root}/orbit07800']
        test_orbits = [7700, 7799, 7800]
        self.assertEqual(expected_output, self.path.block_paths(test_orbits))

    def test_block_paths_matches_expected_output_for_ndarray(self):
        expected_output = [f'{self.root}/orbit07700',
                           f'{self.root}/orbit07700',
                           f'{self.root}/orbit07800']
        test_orbits = [7700, 7799, 7800]
        test_iterable = np.array(test_orbits)
        self.assertEqual(expected_output, self.path.block_paths(test_iterable))

    def test_block_paths_matches_expected_output_for_generator(self):
        expected_output = [f'{self.root}/orbit07700',
                           f'{self.root}/orbit07700',
                           f'{self.root}/orbit07800']
        test_orbits = (7700, 7799, 7800)
        test_iterable = np.array(test_orbits)
        self.assertEqual(expected_output, self.path.block_paths(test_iterable))

    def test_list_of_str_raises_type_error(self):
        with self.assertRaises(TypeError):
            bad_input = ['7700', '7710']
            self.path.block_paths(bad_input)

    def test_int_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.path.block_paths(10)

    def test_2d_ndarray_raises_type_error(self):
        with self.assertRaises(TypeError):
            bad_input = np.zeros((10, 5))
            self.path.block_paths(bad_input)
