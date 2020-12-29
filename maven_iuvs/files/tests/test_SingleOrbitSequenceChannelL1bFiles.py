# Built-in imports
import os
from unittest import TestCase

# Local imports
from maven_iuvs.files.files import SingleOrbitSequenceChannelL1bFiles as Single


class TestSingleOrbitSequenceChannelL1bFiles(TestCase):
    def setUp(self):
        self._path = os.path.join(os.path.dirname(os.path.abspath(
            os.path.realpath(__file__))), 'test_filenames')


class TestInit(TestSingleOrbitSequenceChannelL1bFiles):
    def test_init_raises_value_error_if_not_single_orbit(self):
        with self.assertRaises(ValueError):
            Single(self._path, '*apoapse*muv*')

    def test_init_raises_value_error_if_not_single_sequence(self):
        with self.assertRaises(ValueError):
            Single(self._path, '*12020*muv*')

    def test_init_raises_value_error_if_not_single_channel(self):
        with self.assertRaises(ValueError):
            Single(self._path, '*apoapse*12020*')

    def test_init_raises_value_error_if_no_files_found(self):
        with self.assertRaises(ValueError):
            Single(self._path, '*ech*12020*muv*')

    def test_init_finds_2_apoapse_12020_muv_files(self):
        files = Single(self._path, '*apoapse*12020*muv*')
        self.assertEqual(2, len(files.filenames))


class TestOrbit(TestSingleOrbitSequenceChannelL1bFiles):
    def test_orbit_matches_input(self):
        files = Single(self._path, '*apoapse*12020*muv*')
        self.assertEqual(12020, files.orbit)

    def test_orbit_is_read_only(self):
        files = Single(self._path, '*apoapse*12020*muv*')
        with self.assertRaises(AttributeError):
            files.orbit = 12020


class TestSequence(TestSingleOrbitSequenceChannelL1bFiles):
    def test_sequence_matches_known_input(self):
        files = Single(self._path, '*apoapse*12020*muv*')
        self.assertEqual('apoapse', files.sequence)

    def test_sequence_is_read_only(self):
        files = Single(self._path, '*apoapse*12020*muv*')
        with self.assertRaises(AttributeError):
            files.sequence = 'apoapse'


class TestChannel(TestSingleOrbitSequenceChannelL1bFiles):
    def test_channel_matches_known_input(self):
        files = Single(self._path, '*apoapse*12020*muv*')
        self.assertEqual('muv', files.channel)

    def test_channel_is_read_only(self):
        files = Single(self._path, '*apoapse*12020*muv*')
        with self.assertRaises(AttributeError):
            files.channel = 'muv'
