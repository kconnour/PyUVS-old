import os
from unittest import TestCase
from pyuvs.finder import DataPath


class TestDataPath(TestCase):
    def setUp(self) -> None:
        self.cwd = os.getcwd()
        self.path = DataPath(self.cwd)


class TestInit(TestDataPath):
    def test_int_input_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            DataPath(1)

    def test_list_input_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            DataPath(['/'])

    def test_nonexistent_path_raises_is_a_directory_error(self) -> None:
        with self.assertRaises(IsADirectoryError):
            DataPath('/AZBK5nLKDE')


class TestBlock(TestDataPath):
    def test_block_matches_expected_output(self) -> None:
        expected_path = os.path.join(self.cwd, 'orbit07700')
        self.assertEqual(expected_path, self.path.block(7700))
        self.assertEqual(expected_path, self.path.block(7799))

    def test_input_float_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            self.path.block(7777.0)

    def test_input_str_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            self.path.block('orbit07700')


class TestBlockPaths(TestDataPath):
    def test_block_paths_matches_expected_output_for_list(self) -> None:
        expected_output = [os.path.join(self.cwd, 'orbit07700'),
                           os.path.join(self.cwd, 'orbit07700'),
                           os.path.join(self.cwd, 'orbit07800')]
        test_orbits = [7700, 7799, 7800]
        self.assertEqual(expected_output, self.path.block_paths(test_orbits))

    def test_tuple_input_raises_type_error(self) -> None:
        test_orbits = (7700, 7799, 7800)
        with self.assertRaises(TypeError):
            self.path.block_paths(test_orbits)

    def test_int_input_raises_type_error(self) -> None:
        test_orbits = 7700
        with self.assertRaises(TypeError):
            self.path.block_paths(test_orbits)

    def test_list_of_floats_raises_value_error(self) -> None:
        test_orbits = [7700.0, 7710.0]
        with self.assertRaises(ValueError):
            self.path.block_paths(test_orbits)

    def test_list_of_strs_raises_value_error(self) -> None:
        test_orbits = ['7700', '7710']
        with self.assertRaises(ValueError):
            self.path.block_paths(test_orbits)
