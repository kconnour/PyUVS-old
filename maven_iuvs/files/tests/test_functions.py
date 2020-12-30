# Built-in imports
from unittest import TestCase

# Local imports
from maven_iuvs.files.file_creation_functions import single_orbit_segment


'''class TestFiles(TestCase):
    def setUp(self):
        self._path = os.path.join(os.path.dirname(os.path.abspath(
            os.path.realpath(__file__))), 'test_filenames')
        self.files = Files(self._path, '*')'''


#class TestSingleOrbitSegement:
#    def test_

p = '/Users/kyco2464/iuvsdata'
f = single_orbit_segment(p, 12010, recursive=True)
