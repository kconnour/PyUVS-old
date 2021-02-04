import os
from unittest import TestCase
import warnings
from pyuvs.files import DataFilename, DataFilenameCollection, DataPath, \
    DataPattern


class TestDataFilename(TestCase):
    def setUp(self) -> None:
        self.l1bfname = 'mvn_iuv_l1b_periapse-orbit05550-muv_' \
                        '20170810T131155_v13_r01.fits.gz'
        self.l1b_relay_fname = 'mvn_iuv_l1b_relay-echelle-orbit12190-ech_' \
                               '20200821T214652_v13_r01.fits.gz'
        self.l1cfname = 'mvn_iuv_l1c_periapse-orbit00335_' \
                        '20141201T001558_v13_r01.fits.gz'
        self.l1b_filename = DataFilename(self.l1bfname)
        self.l1b_relay_filename = DataFilename(self.l1b_relay_fname)
        self.l1c_filename = DataFilename(self.l1cfname)


class TestDataFilenameInit(TestDataFilename):
    def test_int_input_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            DataFilename(1)

    def test_non_fits_file_input_raises_value_error(self) -> None:
        fname = self.l1bfname.replace('fits.gz', 'foo')
        with self.assertRaises(ValueError):
            DataFilename(fname)

    def test_non_iuvs_data_fits_file_raises_value_error(self) -> None:
        fname = 'i_commend_you_for_looking_at_my_tests.fits.gz'
        with self.assertRaises(ValueError):
            DataFilename(fname)


class TestFilename(TestDataFilename):
    def test_filename_matches_known_values(self) -> None:
        self.assertEqual(self.l1bfname, self.l1b_filename.filename)
        self.assertEqual(self.l1b_relay_fname, self.l1b_relay_filename.filename)
        self.assertEqual(self.l1cfname, self.l1c_filename.filename)

    def test_filename_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.filename = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.filename = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.filename = 'foo'


class TestSpacecraft(TestDataFilename):
    def test_spacecraft_matches_known_values(self) -> None:
        self.assertEqual('mvn', self.l1b_filename.spacecraft)
        self.assertEqual('mvn', self.l1b_relay_filename.spacecraft)
        self.assertEqual('mvn', self.l1c_filename.spacecraft)

    def test_spacecraft_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.spacecraft = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.spacecraft = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.spacecraft = 'foo'


class TestInstrument(TestDataFilename):
    def test_instrument_matches_known_values(self) -> None:
        self.assertEqual('iuv', self.l1b_filename.instrument)
        self.assertEqual('iuv', self.l1b_relay_filename.instrument)
        self.assertEqual('iuv', self.l1c_filename.instrument)

    def test_instrument_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.instrument = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.instrument = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.instrument = 'foo'


class TestLevel(TestDataFilename):
    def test_level_matches_known_values(self) -> None:
        self.assertEqual('l1b', self.l1b_filename.level)
        self.assertEqual('l1b', self.l1b_relay_filename.level)
        self.assertEqual('l1c', self.l1c_filename.level)

    def test_level_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.level = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.level = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.level = 'foo'


class TestDescription(TestDataFilename):
    def test_description_matches_known_values(self) -> None:
        self.assertEqual('periapse-orbit05550-muv',
                         self.l1b_filename.description)
        self.assertEqual('relay-echelle-orbit12190-ech',
                         self.l1b_relay_filename.description)
        self.assertEqual('periapse-orbit00335', self.l1c_filename.description)

    def test_description_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.description = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.description = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.description = 'foo'


class TestSegment(TestDataFilename):
    def test_segment_matches_known_values(self) -> None:
        self.assertEqual('periapse', self.l1b_filename.segment)
        self.assertEqual('relay-echelle', self.l1b_relay_filename.segment)
        self.assertEqual('periapse', self.l1c_filename.segment)

    def test_segment_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.segment = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.segment = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.segment = 'foo'


class TestOrbit(TestDataFilename):
    def test_orbit_matches_known_values(self) -> None:
        self.assertEqual(5550, self.l1b_filename.orbit)
        self.assertEqual(12190, self.l1b_relay_filename.orbit)
        self.assertEqual(335, self.l1c_filename.orbit)

    def test_orbit_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.orbit = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.orbit = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.orbit = 'foo'


class TestChannel(TestDataFilename):
    def test_channel_matches_known_values(self) -> None:
        self.assertEqual('muv', self.l1b_filename.channel)
        self.assertEqual('ech', self.l1b_relay_filename.channel)
        self.assertEqual(None, self.l1c_filename.channel)

    def test_channel_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.channel = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.channel = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.channel = 'foo'


class TestTimestamp(TestDataFilename):
    def test_timestamp_matches_known_values(self) -> None:
        self.assertEqual('20170810T131155', self.l1b_filename.timestamp)
        self.assertEqual('20200821T214652', self.l1b_relay_filename.timestamp)
        self.assertEqual('20141201T001558', self.l1c_filename.timestamp)

    def test_timestamp_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.timestamp = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.timestamp = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.timestamp = 'foo'


class TestYear(TestDataFilename):
    def test_year_matches_known_values(self) -> None:
        self.assertEqual(2017, self.l1b_filename.year)
        self.assertEqual(2020, self.l1b_relay_filename.year)
        self.assertEqual(2014, self.l1c_filename.year)

    def test_year_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.year = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.year = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.year = 'foo'


class TestMonth(TestDataFilename):
    def test_month_matches_known_values(self) -> None:
        self.assertEqual(8, self.l1b_filename.month)
        self.assertEqual(8, self.l1b_relay_filename.month)
        self.assertEqual(12, self.l1c_filename.month)

    def test_month_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.month = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.month = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.month = 'foo'


class TestDay(TestDataFilename):
    def test_day_matches_known_values(self) -> None:
        self.assertEqual(10, self.l1b_filename.day)
        self.assertEqual(21, self.l1b_relay_filename.day)
        self.assertEqual(1, self.l1c_filename.day)

    def test_day_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.day = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.day = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.day = 'foo'


class TestTime(TestDataFilename):
    def test_time_matches_known_values(self) -> None:
        self.assertEqual('131155', self.l1b_filename.time)
        self.assertEqual('214652', self.l1b_relay_filename.time)
        self.assertEqual('001558', self.l1c_filename.time)

    def test_time_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.time = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.time = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.time = 'foo'


class TestHour(TestDataFilename):
    def test_hour_matches_known_values(self) -> None:
        self.assertEqual(13, self.l1b_filename.hour)
        self.assertEqual(21, self.l1b_relay_filename.hour)
        self.assertEqual(0, self.l1c_filename.hour)

    def test_hour_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.hour = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.hour = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.hour = 'foo'


class TestMinute(TestDataFilename):
    def test_minute_matches_known_values(self) -> None:
        self.assertEqual(11, self.l1b_filename.minute)
        self.assertEqual(46, self.l1b_relay_filename.minute)
        self.assertEqual(15, self.l1c_filename.minute)

    def test_minute_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.minute = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.minute = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.minute = 'foo'


class TestSecond(TestDataFilename):
    def test_second_matches_known_values(self) -> None:
        self.assertEqual(55, self.l1b_filename.second)
        self.assertEqual(52, self.l1b_relay_filename.second)
        self.assertEqual(58, self.l1c_filename.second)

    def test_second_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.second = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.second = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.second = 'foo'


class TestVersion(TestDataFilename):
    def test_version_matches_known_values(self) -> None:
        self.assertEqual('v13', self.l1b_filename.version)
        self.assertEqual('v13', self.l1b_relay_filename.version)
        self.assertEqual('v13', self.l1c_filename.version)

    def test_version_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.version = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.version = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.version = 'foo'


class TestRevision(TestDataFilename):
    def test_revision_matches_known_values(self) -> None:
        self.assertEqual('r01', self.l1b_filename.revision)
        self.assertEqual('r01', self.l1b_relay_filename.revision)
        self.assertEqual('r01', self.l1c_filename.revision)

    def test_revision_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.revision = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.revision = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.revision = 'foo'


class TestExtension(TestDataFilename):
    def test_extension_matches_known_values(self) -> None:
        self.assertEqual('fits.gz', self.l1b_filename.extension)
        self.assertEqual('fits.gz', self.l1b_relay_filename.extension)
        self.assertEqual('fits.gz', self.l1c_filename.extension)

    def test_extension_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.l1b_filename.extension = 'foo'
        with self.assertRaises(AttributeError):
            self.l1b_relay_filename.extension = 'foo'
        with self.assertRaises(AttributeError):
            self.l1c_filename.extension = 'foo'


class TestDataPath(TestCase):
    def setUp(self) -> None:
        self.cwd = os.getcwd()
        self.path = DataPath(self.cwd)


class TestDataPathInit(TestDataPath):
    def test_int_input_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            DataPath(1)

    def test_list_input_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            DataPath(['/'])

    def test_nonexistent_path_raises_is_a_directory_error(self) -> None:
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            DataPath('/AZBK5nLKDE')
            self.assertEqual(1, len(warning))
            self.assertEqual(warning[-1].category, UserWarning)


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


class TestDataPattern(TestCase):
    def setUp(self) -> None:
        self.pattern = DataPattern()


# TODO: I hate this name, which only arises cause the class + method have the
#  same name.
class TestDataPatternMethod(TestDataPattern):
    def test_data_pattern_without_input_gives_expected_result(self) -> None:
        expected_pattern = 'mvn_iuv_*_*-orbit*-*_*T*_*_*.fits*'
        self.assertEqual(expected_pattern, self.pattern.data_pattern())

    def test_pattern_adds_level_to_proper_position(self) -> None:
        answer = f'mvn_iuv_l1b_*-orbit*-*_*T*_*_*.fits*'
        self.assertEqual(answer, self.pattern.data_pattern(level='l1b'))

    def test_pattern_adds_segment_to_proper_position(self) -> None:
        answer = f'mvn_iuv_*_periapse-orbit*-*_*T*_*_*.fits*'
        self.assertEqual(answer, self.pattern.data_pattern(segment='periapse'))

    def test_pattern_adds_orbit_to_proper_position(self) -> None:
        answer = f'mvn_iuv_*_*-orbit*9000-*_*T*_*_*.fits*'
        self.assertEqual(answer, self.pattern.data_pattern(orbit='*9000'))

    def test_pattern_adds_channel_to_proper_position(self) -> None:
        answer = f'mvn_iuv_*_*-orbit*-fuv_*T*_*_*.fits*'
        self.assertEqual(answer, self.pattern.data_pattern(channel='fuv'))

    def test_pattern_adds_timestamp_to_proper_position(self) -> None:
        answer = f'mvn_iuv_*_*-orbit*-*_20200101T*_*_*.fits*'
        self.assertEqual(answer, self.pattern.data_pattern(timestamp='20200101'))

    def test_pattern_adds_version_to_proper_position(self) -> None:
        answer = f'mvn_iuv_*_*-orbit*-*_*T*_v13_*.fits*'
        self.assertEqual(answer, self.pattern.data_pattern(version='v13'))

    def test_pattern_adds_extension_to_proper_position(self) -> None:
        answer = f'mvn_iuv_*_*-orbit*-*_*T*_*_*.xml*'
        self.assertEqual(answer, self.pattern.data_pattern(extension='xml'))

    def test_orbit_input_can_be_int(self) -> None:
        answer = f'mvn_iuv_*_*-orbit10000-*_*T*_*_*.fits*'
        self.assertEqual(answer, self.pattern.data_pattern(orbit=10000))

    def test_channel_can_be_empty_str(self) -> None:
        answer = 'mvn_iuv_*_*-orbit*_*T*_*_*.fits*'
        self.assertEqual(answer, self.pattern.data_pattern(channel=''))


class TestOrbitPattern(TestDataPattern):
    def test_output_is_expected(self) -> None:
        answer = 'mvn_iuv_*_inlimb-orbit09000-muv_*T*_*_*.fits*'
        self.assertEqual(answer, self.pattern.orbit_pattern(9000, 'inlimb', 'muv'))

    def test_list_orbit_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            self.pattern.orbit_pattern([9000], 'inlimb', 'muv')

    def test_str_orbit_raises_value_error(self) -> None:
        with self.assertRaises(TypeError):
            self.pattern.orbit_pattern('foo', 'inlimb', 'muv')


class TestMultiOrbitPatterns(TestDataPattern):
    def test_list_of_ints_matches_expected_output(self) -> None:
        expected_output = ['mvn_iuv_*_apoapse-orbit03453-muv_*T*_*_*.fits*',
                           'mvn_iuv_*_apoapse-orbit03455-muv_*T*_*_*.fits*']
        self.assertEqual(expected_output, self.pattern.multi_orbit_patterns(
            [3453, 3455], 'apoapse', 'muv'))

    def test_int_orbit_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            self.pattern.multi_orbit_patterns(1, 'apoapse', 'muv')

    def test_orbit_list_of_str_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            self.pattern.multi_orbit_patterns(['foo', 'bar'], 'apoapse', 'muv')


class TestGenericPattern(TestDataPattern):
    def test_same_sized_patterns_matches_expected_output(self) -> None:
        patterns = ['muv', 'ech']
        expected_output = '*[me][uc][vh]*'
        self.assertEqual(expected_output,
                         self.pattern.generic_pattern(patterns))

    def test_different_sized_patterns_matches_expected_output(self) -> None:
        patterns = ['apoapse', 'inlimb']
        expected_output = '*[ai][pn][ol][ai][pm][sb]*'
        self.assertEqual(expected_output,
                         self.pattern.generic_pattern(patterns))

    def test_int_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            self.pattern.generic_pattern(10)

    def test_list_of_ints_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            self.pattern.generic_pattern([10, 11])


class TestPrependRecursivePattern(TestDataPattern):
    def test_prepend_recursive_pattern_matches_expected_output(self) -> None:
        dummy_str = 'foo/bar'
        expected_output = '**/foo/bar'
        self.assertEqual(expected_output,
                         self.pattern.prepend_recursive_pattern(dummy_str))


class TestDataFilenameCollection(TestCase):
    def setUp(self) -> None:
        f0 = 'mvn_iuv_l1b_apoapse-orbit10080-muv_20191009T153108_v13_r01.fits.gz'
        f0xml = 'mvn_iuv_l1b_apoapse-orbit10080-muv_20191009T153108.xml'
        f1 = 'mvn_iuv_l1b_apoapse-orbit10080-muv_20191009T165130_v13_r01.fits.gz'
        f1xml = 'mvn_iuv_l1b_apoapse-orbit10080-muv_20191009T165130.xml'
        self.dirty_files = [f'/foo/{f}' for f in [f0, f0xml, f1, f1xml]]
        self.clean_files = [f'/foo/{f}' for f in [f0, f1]]
        self.very_dirty_files = [f'/foo/{f}' for f in [f0xml, f1xml]]


class TestInit(TestDataFilenameCollection):
    def test_class_can_be_initialized_with_no_bad_files(self) -> None:
        DataFilenameCollection(self.clean_files)

    def test_class_can_be_initialized_with_some_bad_files(self) -> None:
        DataFilenameCollection(self.dirty_files)

    def test_class_with_no_iuvs_data_files_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            DataFilenameCollection(self.very_dirty_files)

    def test_empty_list_input_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            DataFilenameCollection([])

    def test_int_input_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            DataFilenameCollection(1)

    def test_list_of_ints_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            DataFilenameCollection([1, 2, 3])


class TestAbsPaths(TestDataFilenameCollection):
    def test_class_matches_clean_known_input(self) -> None:
        i = DataFilenameCollection(self.clean_files)
        self.assertEqual(self.clean_files, i.abs_paths)

    def test_class_matches_dirty_known_input(self) -> None:
        i = DataFilenameCollection(self.dirty_files)
        self.assertEqual(self.clean_files, i.abs_paths)

    def test_abs_paths_is_read_only(self) -> None:
        i = DataFilenameCollection(self.clean_files)
        with self.assertRaises(AttributeError):
            i.abs_paths = 0


class TestFilenames(TestDataFilenameCollection):
    def test_filenames_is_read_only(self) -> None:
        i = DataFilenameCollection(self.clean_files)
        with self.assertRaises(AttributeError):
            i.filenames = 0
