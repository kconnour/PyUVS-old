# Built-in imports
from unittest import TestCase, mock

# Local imports
from pyuvs.misc.get_project_path import get_project_path


class TestOrbitCode(TestCase):
    def test_(self):
        with mock.patch('os.path.realpath') as f:
            project_path = '/foo/bar/pyuvs'
            f.return_value = f'{project_path}/pyuvs/misc/get_module_path.py'
            self.assertEqual(project_path, get_project_path())
