# Built-in imports
from unittest import TestCase

# 3rd-party import
import numpy as np

# Local imports
from old.files import DataPattern


class TestDataPatternClass(TestCase):
    def setUp(self):
        self.pattern = DataPattern()


class TestDataPattern(TestDataPatternClass):
    def test_pattern_works_without_input(self):
        expected_pattern = 'mvn_iuv_*_*-orbit*-*_*T*_*_*.fits*'
        self.assertEqual(expected_pattern, self.pattern.data_pattern())

    def test_pattern_adds_level_to_proper_position(self):
        level = 'l1b'
        expected_pattern = f'mvn_iuv_{level}_*-orbit*-*_*T*_*_*.fits*'
        self.assertEqual(expected_pattern,
                         self.pattern.data_pattern(level=level))

    def test_pattern_adds_segment_to_proper_position(self):
        segment = 'periapse'
        expected_pattern = f'mvn_iuv_*_{segment}-orbit*-*_*T*_*_*.fits*'
        self.assertEqual(expected_pattern,
                         self.pattern.data_pattern(segment=segment))

    def test_pattern_adds_orbit_to_proper_position(self):
        orbit = '*9000'
        expected_pattern = f'mvn_iuv_*_*-orbit{orbit}-*_*T*_*_*.fits*'
        self.assertEqual(expected_pattern,
                         self.pattern.data_pattern(orbit=orbit))

    def test_pattern_adds_channel_to_proper_position(self):
        channel = 'fuv'
        expected_pattern = f'mvn_iuv_*_*-orbit*-{channel}_*T*_*_*.fits*'
        self.assertEqual(expected_pattern,
                         self.pattern.data_pattern(channel=channel))

    def test_pattern_adds_timestamp_to_proper_position(self):
        timestamp = '20200101'
        expected_pattern = f'mvn_iuv_*_*-orbit*-*_{timestamp}T*_*_*.fits*'
        self.assertEqual(expected_pattern,
                         self.pattern.data_pattern(timestamp=timestamp))

    def test_pattern_adds_version_to_proper_position(self):
        version = 'v13'
        expected_pattern = f'mvn_iuv_*_*-orbit*-*_*T*_{version}_*.fits*'
        self.assertEqual(expected_pattern,
                         self.pattern.data_pattern(version=version))

    def test_pattern_adds_extension_to_proper_position(self):
        extension = 'xml'
        expected_pattern = f'mvn_iuv_*_*-orbit*-*_*T*_*_*.{extension}*'
        self.assertEqual(expected_pattern,
                         self.pattern.data_pattern(extension=extension))

    def test_input_can_be_int(self):
        orbit = 10000
        expected_pattern = f'mvn_iuv_*_*-orbit{orbit}-*_*T*_*_*.fits*'
        self.assertEqual(expected_pattern,
                         self.pattern.data_pattern(orbit=orbit))

    def test_input_can_be_float(self):
        orbit = 10000.95857
        expected_pattern = f'mvn_iuv_*_*-orbit{orbit}-*_*T*_*_*.fits*'
        self.assertEqual(expected_pattern,
                         self.pattern.data_pattern(orbit=orbit))


class TestOrbitPattern(TestDataPatternClass):
    def test_expected_input_matches_expected_output(self):
        expected_output = 'mvn_iuv_*_inlimb-orbit09000-muv_*T*_*_*.fits*'
        self.assertEqual(expected_output,
                         self.pattern.orbit_pattern(9000, 'inlimb', 'muv'))

    def test_list_orbit_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.pattern.orbit_pattern([9000], 'inlimb', 'muv')

    def test_str_orbit_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.pattern.orbit_pattern('foo', 'inlimb', 'muv')


class TestMultiOrbitPatterns(TestDataPatternClass):
    def test_list_of_ints_matches_expected_output(self):
        expected_output = ['mvn_iuv_*_apoapse-orbit03453-muv_*T*_*_*.fits*',
                           'mvn_iuv_*_apoapse-orbit03455-muv_*T*_*_*.fits*']
        self.assertEqual(expected_output, self.pattern.multi_orbit_patterns(
            [3453, 3455], 'apoapse', 'muv'))

    def test_ndarray_of_ints_matches_expected_output(self):
        expected_output = ['mvn_iuv_*_apoapse-orbit03453-muv_*T*_*_*.fits*',
                           'mvn_iuv_*_apoapse-orbit03455-muv_*T*_*_*.fits*']
        self.assertEqual(expected_output, self.pattern.multi_orbit_patterns(
            np.array([3453, 3455]), 'apoapse', 'muv'))

    def test_int_orbit_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.pattern.multi_orbit_patterns(1, 'apoapse', 'muv')

    def test_orbit_list_of_str_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.pattern.multi_orbit_patterns(['foo', 'bar'], 'apoapse', 'muv')


class TestGenericPattern(TestDataPatternClass):
    def test_same_sized_patterns_matches_expected_output(self):
        patterns = ['muv', 'ech']
        expected_output = '*[me][uc][vh]*'
        self.assertEqual(expected_output,
                         self.pattern.generic_pattern(patterns))

    def test_different_sized_patterns_matches_expected_output(self):
        patterns = ['apoapse', 'inlimb']
        expected_output = '*[ai][pn][ol][ai][pm][sb]*'
        self.assertEqual(expected_output,
                         self.pattern.generic_pattern(patterns))

    def test_int_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.pattern.generic_pattern(10)

    def test_list_of_ints_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.pattern.generic_pattern([10, 11])


class TestPrependRecursivePattern(TestDataPatternClass):
    def test_prepend_matches_expected_output(self):
        dummy_str = 'foo/bar'
        expected_output = '**/foo/bar'
        self.assertEqual(expected_output,
                         self.pattern.prepend_recursive_pattern(dummy_str))
