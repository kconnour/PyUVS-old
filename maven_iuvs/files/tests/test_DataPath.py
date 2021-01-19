# Built-in imports
import inspect
import os
from unittest import TestCase

# 3rd-party imports
import numpy as np

# Local imports
from maven_iuvs.files.finder import DataPath


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
        self.assertEqual(os.path.join(self.root, 'orbit07700'),
                         self.path.block(7700))
        self.assertEqual(os.path.join(self.root, 'orbit07700'),
                         self.path.block(7799))

    def test_input_float_raises_value_error(self):
        with self.assertRaises(TypeError):
            self.path.block(7700.0)

    def test_input_str_raises_value_error(self):
        with self.assertRaises(TypeError):
            self.path.block('orbit07700')


class TestBlockPaths(TestDataPath):
    def test_blockpaths_matches_expected_output(self):
        expected_output = [f'{self.root}/orbit07700',
                           f'{self.root}/orbit07700',
                           f'{self.root}/orbit07800']
        test_orbits = [7700, 7799, 7800]
        self.assertEqual(expected_output, self.path.block_paths(test_orbits))

    def test_blockpaths_works_with_iterable(self):
        expected_output = [f'{self.root}/orbit07700',
                           f'{self.root}/orbit07700',
                           f'{self.root}/orbit07800']
        test_orbits = [7700, 7799, 7800]
        test_iterable = np.array(test_orbits)
        self.assertEqual(expected_output, self.path.block_paths(test_iterable))

    def test_blockpaths_failes_with_floats(self):
        with self.assertRaises(TypeError):
            test_orbits = [7700.0, 7799.0, 7800.0]
            self.path.block_paths(test_orbits)
