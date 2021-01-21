# Built-in imports
from unittest import TestCase

# 3rd-party imports
import numpy as np

# Local imports
from pyuvs.files.filenames import IUVSDataFilename


class TestIUVSDataFilename(TestCase):
    def setUp(self):
        self.fname = IUVSDataFilename
        self.testfname = 'mvn_iuv_l1b_periapse-orbit05550-muv_20170810T131155_v13_r01.fits.gz'
        self.testfile = self.fname(self.testfname)


class TestInit(TestIUVSDataFilename):
    def test_non_fits_file_cannot_initialize(self):
        with self.assertRaises(ValueError):
            fname = self.testfname.replace('fits.gz', 'foo')
            self.fname(fname)

    def test_generic_fits_file_cannot_initialize(self):
        with self.assertRaises(ValueError):
            fname = 'i_commend_you_for_looking_at_my_tests.fits.gz'
            self.fname(fname)


class TestFilename(TestIUVSDataFilename):
    def test_filename_matches_test_filename(self):
        self.assertEqual(self.testfname, self.testfile.filename)


class TestSpacecraft(TestIUVSDataFilename):
    def test_spacecraft_matches_test_filename(self):
        self.assertEqual('mvn', self.testfile.spacecraft)


class TestInstrument(TestIUVSDataFilename):
    def test_instrument_matches_test_filename(self):
        self.assertEqual('iuv', self.testfile.instrument)


class TestLevel(TestIUVSDataFilename):
    def test_level_matches_test_filename(self):
        self.assertEqual('l1b', self.testfile.level)


class TestDescription(TestIUVSDataFilename):
    def test_description_matches_test_filename(self):
        self.assertEqual('periapse-orbit05550-muv', self.testfile.description)


class TestSegment(TestIUVSDataFilename):
    def test_segment_matches_test_filename(self):
        self.assertEqual('periapse', self.testfile.segment)


class TestOrbit(TestIUVSDataFilename):
    def test_orbit_matches_test_filename(self):
        self.assertEqual(5550, self.testfile.orbit)


class TestChannel(TestIUVSDataFilename):
    def test_channel_matches_test_filename(self):
        self.assertEqual('muv', self.testfile.channel)


class TestTimestamp(TestIUVSDataFilename):
    def test_timestamp_matches_test_filename(self):
        self.assertEqual('20170810T131155', self.testfile.timestamp)


class TestYear(TestIUVSDataFilename):
    def test_year_matches_test_filename(self):
        self.assertEqual(2017, self.testfile.year)


class TestMonth(TestIUVSDataFilename):
    def test_year_matches_test_filename(self):
        self.assertEqual(8, self.testfile.month)


class TestDay(TestIUVSDataFilename):
    def test_day_matches_test_filename(self):
        self.assertEqual(10, self.testfile.day)


class TestTime(TestIUVSDataFilename):
    def test_time_matches_test_filename(self):
        self.assertEqual('131155', self.testfile.time)


class TestHour(TestIUVSDataFilename):
    def test_hour_matches_test_filename(self):
        self.assertEqual(13, self.testfile.hour)


class TestMinute(TestIUVSDataFilename):
    def test_minute_matches_test_filename(self):
        self.assertEqual(11, self.testfile.minute)


class TestSecond(TestIUVSDataFilename):
    def test_second_matches_test_filename(self):
        self.assertEqual(55, self.testfile.second)


class TestVersion(TestIUVSDataFilename):
    def test_version_matches_test_filename(self):
        self.assertEqual('v13', self.testfile.version)


class TestRevision(TestIUVSDataFilename):
    def test_revision_matches_test_filename(self):
        self.assertEqual('r01', self.testfile.revision)


class TestExtension(TestIUVSDataFilename):
    def test_extension_matches_test_filename(self):
        self.assertEqual('fits.gz', self.testfile.extension)
