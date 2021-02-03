from unittest import TestCase, mock
from pyuvs.misc import get_project_path, orbit_code


class TestGetProjectPath(TestCase):
    def test_(self):
        with mock.patch('os.path.realpath') as f:
            project_path = '/foo/bar/pyuvs'
            f.return_value = f'{project_path}/pyuvs/misc/get_module_path.py'
            self.assertEqual(project_path, get_project_path())


class TestOrbitCode(TestCase):
    def test_str_raises_type_error(self):
        with self.assertRaises(TypeError):
            orbit_code('foo')

    def test_list_raises_type_error(self):
        with self.assertRaises(TypeError):
            orbit_code([5617])

    def test_float_raises_type_error(self):
        with self.assertRaises(TypeError):
            orbit_code(5617.)

    def test_int_input_gives_expected_output(self):
        self.assertEqual('05617', orbit_code(5617))
