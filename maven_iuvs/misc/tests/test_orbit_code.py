# Built-in imports
from unittest import TestCase

# 3rd-party imports
import numpy as np

# Local imports
from maven_iuvs.misc.orbit_code import orbit_code


class TestOrbitCode(TestCase):
    def test_int_input_gives_expected_output(self):
        self.assertEqual('05617', orbit_code(5617))

    def test_float_input_gives_expected_output(self):
        self.assertEqual('05617', orbit_code(5617.))
        self.assertEqual('05617', orbit_code(np.nextafter(5618, 5617)))

    def test_str_of_int_gives_expected_output(self):
        self.assertEqual('05617', orbit_code('05617'))

    def test_generic_str_raises_value_error(self):
        with self.assertRaises(ValueError):
            orbit_code('foo')

    def test_list_raises_type_error(self):
        with self.assertRaises(TypeError):
            orbit_code([5617])
