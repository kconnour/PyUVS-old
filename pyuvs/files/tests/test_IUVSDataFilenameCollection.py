# Built-in imports
from unittest import TestCase

# Local imports
from pyuvs.files.files import IUVSDataFilenameCollection


class TestIUVSDataFilenameCollection(TestCase):
    def setUp(self):
        f0 = 'mvn_iuv_l1b_apoapse-orbit10080-muv_20191009T153108_v13_r01.fits.gz'
        f0xml = 'mvn_iuv_l1b_apoapse-orbit10080-muv_20191009T153108.xml'
        f1 = 'mvn_iuv_l1b_apoapse-orbit10080-muv_20191009T165130_v13_r01.fits.gz'
        f1xml = 'mvn_iuv_l1b_apoapse-orbit10080-muv_20191009T165130.xml'
        self.dirty_files = [f'/foo/{f}' for f in [f0, f0xml, f1, f1xml]]
        self.clean_files = [f'/foo/{f}' for f in [f0, f1]]
        self.very_dirty_files = [f'/foo/{f}' for f in [f0xml, f1xml]]


class TestInit(TestIUVSDataFilenameCollection):
    def test_class_can_be_initialized_with_no_bad_files(self):
        IUVSDataFilenameCollection(self.clean_files)

    def test_class_can_be_initialized_with_some_bad_files(self):
        IUVSDataFilenameCollection(self.dirty_files)

    def test_class_with_no_iuvs_data_files_raises_value_error(self):
        with self.assertRaises(ValueError):
            IUVSDataFilenameCollection(self.very_dirty_files)

    def test_class_cannot_be_initialized_with_empty_list(self):
        with self.assertRaises(TypeError):
            IUVSDataFilenameCollection(1)


class TestAbsPaths(TestIUVSDataFilenameCollection):
    def test_class_matches_clean_known_input(self):
        i = IUVSDataFilenameCollection(self.clean_files)
        self.assertEqual(self.clean_files, i.abs_paths)

    def test_class_matches_dirty_known_input(self):
        i = IUVSDataFilenameCollection(self.dirty_files)
        self.assertEqual(self.clean_files, i.abs_paths)

    def test_abs_paths_is_read_only(self):
        with self.assertRaises(AttributeError):
            i = IUVSDataFilenameCollection(self.clean_files)
            i.abs_paths = 0


# TODO: test filenames
# TODO: test nfiles
# TODO: test get matching abs paths
# TODO: test get matching filenames
# TODO: test downscale abs paths
# TODO: test downscale filenames
# TODO: test all l1b
# TODO: test all l1c
# TODO: test all apoapse
# TODO: test all peripase
# TODO: test all muv
# TODO: test all fuv
# TODO: test all ech
