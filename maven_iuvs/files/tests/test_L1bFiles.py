# Built-in imports
import os
from unittest import TestCase
import warnings

# 3rd-party imports
import numpy as np

# Local imports
from maven_iuvs.files.files import L1bFiles


class TestL1bFiles(TestCase):
    def setUp(self):
        self._path = os.path.join(os.path.dirname(os.path.abspath(
            os.path.realpath(__file__))), 'test_filenames')
        self.files = L1bFiles(self._path, '*')
        # TODO: generalize this, though even if a user sets their l1b data path
        #  elsewhere, there's no guarantee they have these 3 orbits of data.
        self.data_location = '/Volumes/Samsung_T5/IUVS_data/orbit10000'
        self.all_relays = L1bFiles(self.data_location, '*apoapse*10060*muv*')
        self.some_relays = L1bFiles(self.data_location, '*apoapse*10061*muv*')
        self.no_relays = L1bFiles(self.data_location, '*apoapse*10062*muv*')


class TestInit(TestL1bFiles):
    def test_init_found_10_l1b_files(self):
        self.assertEqual(10, len(self.files.filenames))

    def test_init_raises_no_warnings_when_downselecting(self):
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            L1bFiles(self._path, '*')
            self.assertEqual(0, len(warning))

    def test_init_raises_value_error_if_no_iuvs_files(self):
        with self.assertRaises(ValueError):
            L1bFiles(self._path, 'mars*')


class TestMaximumMirrorAngle(TestL1bFiles):
    def test_maximum_mirror_angle_is_known_value(self):
        self.assertEqual(59.6502685546875, self.files.maximum_mirror_angle)

    def test_maximum_mirror_angle_cannot_be_modified(self):
        with self.assertRaises(AttributeError):
            self.files.maximum_mirror_angle = 0


class TestMinimumMirrorAngle(TestL1bFiles):
    def test_mainimum_mirror_angle_is_known_value(self):
        self.assertEqual(30.2508544921875, self.files.minimum_mirror_angle)

    def test_minimum_mirror_angle_cannot_be_modified(self):
        with self.assertRaises(AttributeError):
            self.files.minimum_mirror_angle = 0


class TestCheckRelays(TestL1bFiles):
    def test_orbits_known_relay_swaths_match_output(self):
        zeros = np.zeros(17, dtype=bool)
        zeros[0] = True
        self.assertEqual(list(zeros), self.some_relays.check_relays())


class TestAnyRelays(TestL1bFiles):
    def test_orbit_known_to_have_all_relays_returns_true(self):
        self.assertTrue(self.all_relays.any_relays())

    def test_orbit_known_to_have_some_relays_returns_true(self):
        self.assertTrue(self.some_relays.any_relays())

    def test_orbit_known_to_have_no_relays_returns_false(self):
        self.assertTrue(not self.no_relays.any_relays())


class TestAllRelays(TestL1bFiles):
    def test_orbit_known_to_have_all_relays_returns_true(self):
        self.assertTrue(self.all_relays.any_relays())

    def test_orbit_known_to_have_some_relays_returns_false(self):
        self.assertTrue(self.some_relays.any_relays())

    def test_orbit_known_to_have_no_relays_returns_false(self):
        self.assertTrue(not self.no_relays.any_relays())
