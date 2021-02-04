"""The files module contains tools for getting IUVS data files from one's
computer.
"""
import copy
import os
from typing import Any, Generator
from warnings import warn
import numpy as np
from pyuvs.misc import orbit_code


# TODO: Most of the logic here could go into a higher class like IUVSFilename
#  so that it could work on .xml files or quicklooks
# TODO: pylint says I have too many instance variables (20 / 7)
class DataFilename:
    """DataFilename is a data structure containing info from IUVS filenames.

    DataFilename accepts a string of an IUVS data filename and extracts all
    information related to the observation and processing pipeline from the
    input.

    """

    def __init__(self, filename: str) -> None:
        """
        Parameters
        ----------
        filename: str
            The IUVS data filename.

        Raises
        ------
        TypeError
            Raised if the input is not a str.
        ValueError
            Raised if the input is not an IUVS data filename.

        """
        self.__filename = filename

        self.__raise_error_if_input_is_bad()

        self.__spacecraft = self.__extract_spacecraft_from_filename()
        self.__instrument = self.__extract_instrument_from_filename()
        self.__level = self.__extract_level_from_filename()
        self.__description = self.__extract_description_from_filename()
        self.__segment = self.__extract_segment_from_description()
        self.__orbit = self.__extract_orbit_from_description()
        self.__channel = self.__extract_channel_from_description()
        self.__timestamp = self.__extract_timestamp_from_filename()
        self.__date = self.__extract_date_from_timestamp()
        self.__year = self.__extract_year_from_date()
        self.__month = self.__extract_month_from_date()
        self.__day = self.__extract_day_from_date()
        self.__time = self.__extract_time_from_timestamp()
        self.__hour = self.__extract_hour_from_time()
        self.__minute = self.__extract_minute_from_time()
        self.__second = self.__extract_second_from_time()
        self.__version = self.__extract_version_from_filename()
        self.__revision = self.__extract_revision_from_filename()
        self.__extension = self.__extract_extension_from_filename()

    def __raise_error_if_input_is_bad(self) -> None:
        self.__raise_type_error_if_input_is_not_str()
        self.__raise_value_error_if_input_is_not_iuvs_data_filename()

    def __raise_type_error_if_input_is_not_str(self) -> None:
        if not isinstance(self.__filename, str):
            raise TypeError('filename must be a str.')

    def __raise_value_error_if_input_is_not_iuvs_data_filename(self) -> None:
        checks = self.__make_filename_checks()
        if not all(checks):
            raise ValueError('The input file is not an IUVS data file.')

    def __make_filename_checks(self) -> list[bool]:
        return [self.__check_file_begins_with_mvn_iuv(),
                self.__check_filename_has_fits_extension(),
                self.__check_filename_contains_6_underscores(),
                self.__check_filename_contains_orbit()]

    def __check_file_begins_with_mvn_iuv(self) -> bool:
        return self.__filename.startswith('mvn_iuv_')

    def __check_filename_has_fits_extension(self) -> bool:
        return self.__filename.endswith('fits') or \
               self.__filename.endswith('fits.gz')

    def __check_filename_contains_6_underscores(self) -> bool:
        return self.__filename.count('_') == 6

    def __check_filename_contains_orbit(self) -> bool:
        return 'orbit' in self.__filename

    def __extract_spacecraft_from_filename(self) -> str:
        return self.__split_filename_on_underscore()[0]

    def __extract_instrument_from_filename(self) -> str:
        return self.__split_filename_on_underscore()[1]

    def __extract_level_from_filename(self) -> str:
        return self.__split_filename_on_underscore()[2]

    def __extract_description_from_filename(self) -> str:
        return self.__split_filename_on_underscore()[3]

    def __extract_segment_from_description(self) -> str:
        orbit_index = self.__get_split_index_containing_orbit()
        segments = self.__split_description()[:orbit_index]
        return '-'.join(segments)

    def __extract_orbit_from_description(self) -> int:
        orbit_index = self.__get_split_index_containing_orbit()
        orbit = self.__split_description()[orbit_index].removeprefix('orbit')
        return int(orbit)

    # TODO: In 3.10 change this to str | type(None)
    def __extract_channel_from_description(self) -> str:
        orbit_index = self.__get_split_index_containing_orbit()
        try:
            return self.__split_description()[orbit_index + 1]
        except IndexError:
            return None

    def __extract_timestamp_from_filename(self) -> str:
        return self.__split_filename_on_underscore()[4]

    def __extract_date_from_timestamp(self) -> str:
        return self.__split_timestamp()[0]

    def __extract_year_from_date(self) -> int:
        return int(self.__date[:4])

    def __extract_month_from_date(self) -> int:
        return int(self.date[4:6])

    def __extract_day_from_date(self) -> int:
        return int(self.date[6:])

    def __extract_time_from_timestamp(self) -> str:
        return self.__split_timestamp()[1]

    def __extract_hour_from_time(self) -> int:
        return int(self.__time[:2])

    def __extract_minute_from_time(self) -> int:
        return int(self.__time[2:4])

    def __extract_second_from_time(self) -> int:
        return int(self.__time[4:])

    def __extract_version_from_filename(self) -> str:
        return self.__split_filename_on_underscore()[5]

    def __extract_revision_from_filename(self) -> str:
        return self.__split_filename_on_underscore()[6]

    def __extract_extension_from_filename(self) -> str:
        return self.__split_stem_from_extension()[1]

    def __split_filename_on_underscore(self) -> list[str]:
        stem = self.__split_stem_from_extension()[0]
        return stem.split('_')

    def __split_stem_from_extension(self) -> list[str]:
        extension_index = self.__filename.find('.')
        stem = self.__filename[:extension_index]
        extension = self.__filename[extension_index + 1:]
        return [stem, extension]

    def __split_timestamp(self) -> list[str]:
        return self.__timestamp.split('T')

    def __split_description(self) -> list[str]:
        return self.__description.split('-')

    def __get_split_index_containing_orbit(self) -> int:
        return [c for c, f in enumerate(self.__split_description())
                if 'orbit' in f][0]

    def __str__(self) -> str:
        return self.__filename

    @property
    def filename(self) -> str:
        """Get the input filename.

        Returns
        -------
        str
            The input filename.

        """
        return self.__filename

    @property
    def spacecraft(self) -> str:
        """Get the spacecraft code from the filename.

        Returns
        -------
        str
            The spacecraft code.

        """
        return self.__spacecraft

    @property
    def instrument(self) -> str:
        """Get the instrument code from the filename.

        Returns
        -------
        str
            The instrument code.

        """
        return self.__instrument

    @property
    def level(self) -> str:
        """Get the data product level from the filename.

        Returns
        -------
        str
            The data product level.

        """
        return self.__level

    @property
    def description(self) -> str:
        """Get the description from the filename.

        Returns
        -------
        str
            The observation description.

        """
        return self.__description

    @property
    def segment(self) -> str:
        """Get the observation segment from the filename.

        Returns
        -------
        str
            The observation segment.

        """
        return self.__segment

    @property
    def orbit(self) -> int:
        """Get the orbit number from the filename.

        Returns
        -------
        orbit: int
            The orbit number.

        """
        return self.__orbit

    @property
    def channel(self) -> str:
        """Get the observation channel from the filename.

        Returns
        -------
        str
            The observation channel.

        """
        return self.__channel

    @property
    def timestamp(self) -> str:
        """Get the timestamp of the observation from the filename.

        Returns
        -------
        str
            The timestamp of the observation.

        """
        return self.__timestamp

    @property
    def date(self) -> str:
        """Get the date of the observation from the filename.

        Returns
        -------
        str
            The date of the observation.

        """
        return self.__date

    @property
    def year(self) -> int:
        """Get the year of the observation from the filename.

        Returns
        -------
        int
            The year of the observation.

        """
        return self.__year

    @property
    def month(self) -> int:
        """Get the month of the observation from the filename.

        Returns
        -------
        int
            The month of the observation.

        """
        return self.__month

    @property
    def day(self) -> int:
        """Get the day of the observation from the filename.

        Returns
        -------
        int
            The day of the observation.

        """
        return self.__day

    @property
    def time(self) -> str:
        """Get the time of the observation from the filename.

        Returns
        -------
        str
            The time of the observation.

        """
        return self.__time

    @property
    def hour(self) -> int:
        """Get the hour of the observation from the filename.

        Returns
        -------
        int
            The hour of the observation.

        """
        return self.__hour

    @property
    def minute(self) -> int:
        """Get the minute of the observation from the filename.

        Returns
        -------
        int
            The minute of the observation.

        """
        return self.__minute

    @property
    def second(self) -> int:
        """Get the second of the observation from the filename.

        Returns
        -------
        int
            The second of the observation.

        """
        return self.__second

    @property
    def version(self) -> str:
        """Get the version code from the filename.

        Returns
        -------
        str
            The version code.

        """
        return self.__version

    @property
    def revision(self) -> str:
        """Get the revision code from the filename.

        Returns
        -------
        rstr
            The revision code.

        """
        return self.__revision

    @property
    def extension(self) -> str:
        """Get the extension of filename.

        Returns
        -------
        str
            The extension.

        """
        return self.__extension


class DataFilenameCollection:
    """A DataFilenameCollection is a data structure for holding IUVS data files.

    A DataFilenameCollection checks that the input files are IUVS data and only
    keeps the most recent data files. It also keeps a parallel list of
    DataFilename objects corresponding to the input filenames.

    """

    def __init__(self, files: list[str]) -> None:
        """
        Parameters
        ----------
        files: list[str]
            Absolute paths of IUVS data files.

        Raises
        ------
        TypeError
            Raised if files is not a list
        ValueError
            Raised if any of the values in files are not strings.

        """
        self.__raise_error_if_input_is_not_list_of_str(files)

        self.__abs_paths, self.__filenames = \
            self.__make_absolute_paths_and_filenames(files)
        self.__raise_value_error_if_no_files_found()

    @staticmethod
    def __raise_error_if_input_is_not_list_of_str(files) -> None:
        if not isinstance(files, list):
            raise TypeError('files must be a list.')
        if not all([isinstance(f, str) for f in files]):
            raise ValueError('all elements in files must be strs.')

    def __make_absolute_paths_and_filenames(self, files: list[str]) -> \
            tuple[list[str], list[DataFilename]]:
        input_abs_paths = self.__get_unique_absolute_paths(files)
        input_filenames = self.__get_filenames_from_paths(input_abs_paths)
        iuvs_data_filenames = self.__make_filenames(input_filenames)
        latest_filenames = self.__get_latest_filenames(iuvs_data_filenames)
        latest_abs_paths = self.__get_latest_abs_paths(latest_filenames,
                                                       input_abs_paths)
        return latest_abs_paths, latest_filenames

    @staticmethod
    def __get_unique_absolute_paths(files: list[str]) -> list[str]:
        return sorted(list(set(files)))

    @staticmethod
    def __get_filenames_from_paths(paths: list[str]) -> Generator:
        return (os.path.basename(f) for f in paths)

    def __make_filenames(self, filenames: Generator) -> Generator:
        return (k for f in filenames if
                (k := self.__make_filename(f)) is not None)

    @staticmethod
    # TODO: When python 3.10 releases, change -> DataFilename | None
    def __make_filename(filename: str) -> DataFilename:
        try:
            return DataFilename(filename)
        except ValueError:
            return None

    @staticmethod
    def __get_latest_filenames(filenames: Generator) -> list[DataFilename]:
        fnames = {f.filename.replace('s0', 'a0'): f for f in filenames}
        prev_key, prev_time = '', ''
        for k, v in copy.deepcopy(fnames).items():
            if v.timestamp != prev_time:
                prev_time = v.timestamp
            else:
                del fnames[prev_key]
            prev_key = k
        return [*fnames.values()]

    @staticmethod
    def __get_latest_abs_paths(filenames: list[DataFilename],
                               abs_paths: list[str]) -> list[str]:
        return [f for f in abs_paths for g in filenames if g.filename in f]

    def __raise_value_error_if_no_files_found(self) -> None:
        if not self.__abs_paths:
            raise ValueError('None of the input strings are IUVS files.')

    @property
    def abs_paths(self) -> list[str]:
        """Get the absolute paths of the input IUVS data files.

        Returns
        -------
        list[str]
            Absolute paths of the data files.

        """
        return self.__abs_paths

    @property
    def filenames(self) -> list[DataFilename]:
        """Get the filenames of the input IUVS data files.

        Returns
        -------
        list[IUVSDataFilename]
            Filenames of the inputs.

        """
        return self.__filenames


class DataPath:
    """A DataPath object creates absolute paths to where data products reside.

    DataPath contains methods to create strings of absolute paths to where data
    products reside, given a set of assumptions.

    """

    def __init__(self, path: str) -> None:
        """
        Parameters
        ----------
        path: str
            Absolute path of the IUVS data root location.

        Raises
        ------
        TypeError
            Raised if path is not a str.

        Warnings
        --------
        UserWarning
            Raised if path does not point to a valid directory.

        """
        self.__path = path

        self.__raise_error_if_input_is_bad()
        self.__warn_if_path_does_not_exist()

    def __raise_error_if_input_is_bad(self) -> None:
        self.__raise_type_error_if_input_is_not_string()

    def __raise_type_error_if_input_is_not_string(self) -> None:
        if not isinstance(self.__path, str):
            raise TypeError('path must be a str.')

    def __warn_if_path_does_not_exist(self) -> None:
        if not os.path.exists(self.__path):
            warn('path must point to a valid directory.')

    def block(self, orbit: int) -> str:
        """Make the path to an orbit, assuming orbits are organized in blocks
        of 100 orbits.

        Parameters
        ----------
        orbit: int
            The orbit number.

        Returns
        -------
        str
            The path with orbit block appended corresponding to the input
            orbit.

        Raises
        ------
        TypeError
            Raised if orbit is not an int.

        Examples
        --------
        >>> path = DataPath('/foo/bar')
        >>> path.block(7777)
        '/foo/bar/orbit07700'

        """
        self.__raise_type_error_if_input_is_not_int(orbit, 'orbit')
        return os.path.join(self.__path, self.__block_folder_name(orbit))

    def block_paths(self, orbits: list[int]) -> list[str]:
        """Make paths to a series of orbits, assuming orbits are organized in
        blocks of 100 orbits.

        Parameters
        ----------
        orbits: list[int]
            The orbit numbers.

        Returns
        -------
        list[str]
            The path with orbit block appended corresponding to the input
            orbits.

        Raises
        ------
        TypeError
            Raised if orbits is not a list.
        ValueError
            Raised if any of the values in orbits are not ints.

        Examples
        --------
        >>> path = DataPath('/foo/bar')
        >>> path.block_paths([3495, 3500, 3505])
        ['/foo/bar/orbit03400', '/foo/bar/orbit03500', '/foo/bar/orbit03500']

        """
        self.__raise_type_error_if_input_is_not_list(orbits, 'orbits')
        try:
            return [self.block(f) for f in orbits]
        except TypeError:
            raise ValueError('Each value in orbits must be an int.') from None

    @staticmethod
    def __raise_type_error_if_input_is_not_int(quantity: Any, name: str) \
            -> None:
        if not isinstance(quantity, int):
            raise TypeError(f'{name} must be an int.')

    def __block_folder_name(self, orbit: int) -> str:
        orbit_block = self.__orbit_block(orbit)
        return f'orbit{orbit_code(orbit_block)}'

    @staticmethod
    def __orbit_block(orbit: int) -> int:
        return int(np.floor(orbit / 100) * 100)

    @staticmethod
    def __raise_type_error_if_input_is_not_list(quantity: Any, name: str) \
            -> None:
        if not isinstance(quantity, list):
            raise TypeError(f'{name} must be a list.')


class DataPattern:
    """A DataPattern object creates glob search patterns for IUVS data.

    DataPattern contains methods to create strings of glob search patterns,
    tailored to IUVS data.

    """

    def data_pattern(self, level: str = '*', segment: str = '*',
                     orbit: str = '*', channel: str = '*',
                     timestamp: str = '*', version: str = '*',
                     extension: str = 'fits') -> str:
        """Make a glob pattern of an IUVS data filename.

        Parameters
        ----------
        level: str, optional
            The level pattern to get data from. Default is '*'.
        segment: str, optional
            The segment pattern to get data from. Default is '*'.
        orbit: str, optional
            The orbit pattern to get data from. Default is '*'.
        channel: str, optional
            The channel pattern to get data from. Default is '*'.
        timestamp: str, optional
            The timestamp pattern to get data from. Default is '*'.
        version: str, optional
            The version pattern to get data from. Default is '*'.
        extension: str, optional
            The extension pattern to get data from. Default is 'fits'.

        Returns
        -------
        str
            The pattern with the input sub-patterns.

        Examples
        --------
        >>> dp = DataPattern()
        >>> dp.data_pattern()
        'mvn_iuv_*_*-orbit*-*_*T*_*_*.fits*'

        >>> dp.data_pattern(segment='apoapse', channel='ech')
        'mvn_iuv_*_apoapse-orbit*-ech_*T*_*_*.fits*'
        """

        # TODO: this is a hackish solution to accommodate l1c files, which have
        #  no channel info in the filename evidently.
        if channel:
            pattern = f'mvn_iuv_{level}_{segment}-orbit{orbit}-{channel}_' \
                      f'{timestamp}T*_{version}_*.{extension}*'
        else:
            pattern = f'mvn_iuv_{level}_{segment}-orbit{orbit}{channel}_' \
                      f'{timestamp}T*_{version}_*.{extension}*'
        return self.__remove_recursive_glob_pattern(pattern)

    def orbit_pattern(self, orbit: int, segment: str, channel: str) -> str:
        """Make a glob pattern for an input orbit number, as well as segment
        and channel patterns.

        Parameters
        ----------
        orbit: int
            The orbit number to get data from.
        segment: str
            The segment pattern to get data from.
        channel: str
            The channel pattern to get data from.

        Returns
        -------
        pattern: str
            The glob pattern that matches the input patterns.

        Raises
        ------
        TypeError
            Raised if orbit is not an int.

        Examples
        --------
        >>> dp = DataPattern()
        >>> dp.orbit_pattern(9000, 'inlimb', 'muv')
        'mvn_iuv_*_inlimb-orbit09000-muv_*T*_*_*.fits*'

        >>> segment_pattern = dp.generic_pattern(['apoapse', 'inlimb'])
        >>> dp.orbit_pattern(9984, segment_pattern, 'fuv')
        'mvn_iuv_*_*[ai][pn][ol][ai][pm][sb]*-orbit09984-fuv_*T*_*_*.fits*'
        """

        try:
            return self.data_pattern(orbit=orbit_code(orbit), segment=segment,
                                     channel=channel)
        except TypeError as te:
            raise TypeError('orbit must be an int.') from te

    def multi_orbit_patterns(self, orbits: list[int], segment: str,
                             channel: str) -> list[str]:
        """Make glob patterns for each orbit in a list of orbits.

        Parameters
        ----------
        orbits: list[int]
            Orbits to make patterns for.
        segment: str
            The segment pattern to get data from.
        channel: str
            The channel pattern to get data from.

        Returns
        -------
        list[str]
            Patterns for each input orbit.

        Raises
        ------
        TypeError
            Raised if the input is not a list of ints.

        Examples
        --------
        >>> DataPattern().multi_orbit_patterns([3453, 3455], 'apoapse', 'muv')
        ['mvn_iuv_*_apoapse-orbit03453-muv_*T*_*_*.fits*', 'mvn_iuv_*_apoapse-orbit03455-muv_*T*_*_*.fits*']
        """

        try:
            return [self.orbit_pattern(f, segment, channel) for f in orbits]
        except TypeError:
            raise TypeError('The input value of orbit should be a list of ints.')

    @staticmethod
    def generic_pattern(patterns: list[str]) -> str:
        """Create a generic glob search pattern from a list of patterns. This
        replicates the functionality of the brace expansion glob has in some
        shells.

        Parameters
        ----------
        patterns: list[str]
            Patterns to search for.

        Returns
        -------
        str
            The glob search pattern that accounts for the input patterns.

        Raises
        ------
        TypeError
            Raised if the patterns are not an iterable.

        Examples
        --------
        >>> segments = ['apoapse', 'inlimb']
        >>> DataPattern().generic_pattern(segments)
        '*[ai][pn][ol][ai][pm][sb]*'

        """
        try:
            shortest_pattern_length = min([len(f) for f in patterns])
            split_patterns = (''.join([f[i] for f in patterns]) for i in
                              range(shortest_pattern_length))
            pattern = ''.join([f'[{f}]' for f in split_patterns])
            return '*' + pattern + '*'
        except TypeError:
            raise TypeError('patterns must be an iterable.')

    @staticmethod
    def prepend_recursive_pattern(pattern: str) -> str:
        """Prepend '**/' to the input pattern.

        Parameters
        ----------
        pattern: str
            Generic glob pattern.

        Returns
        -------
        str
            Input pattern with '**/' prepended.

        Examples
        --------
        >>> dp = DataPattern()
        >>> dp.prepend_recursive_pattern(dp.data_pattern())
        '**/mvn_iuv_*_*-orbit*-*_*T*_*_*.fits*'

        """
        return f'**/{pattern}'

    @staticmethod
    def __remove_recursive_glob_pattern(pattern: str) -> str:
        return pattern.replace('**', '*')


class FileClassifier:
    """FileClassifier determines if IUVS data filenames meet a condition.

    A FileClassifier object contains methods to determine if a
    DataFilenameCollection fits a given condition.

    """

    def __init__(self, collection: DataFilenameCollection) -> None:
        self.__dfc = collection
        self.__raise_type_error_if_input_is_not_data_filename_collection()

    def __raise_type_error_if_input_is_not_data_filename_collection(self) \
            -> None:
        if not isinstance(self.__dfc, DataFilenameCollection):
            raise TypeError('collection must be a DataFilenameCollection.')

    def all_l1b(self) -> bool:
        """Determine if all files in the collection are level 1b data files.

        Returns
        -------
        bool
            True if all files are level 1b; False otherwise.

        """
        return all((f.level == 'l1b' for f in self.__dfc.filenames))

    def all_l1c(self) -> bool:
        """Determine if all files in the collection are level 1c data files.

        Returns
        -------
        bool
            True if all files are level 1c; False otherwise.
        """
        return all((f.level == 'l1c' for f in self.__dfc.filenames))

    def all_apoapse(self) -> bool:
        """Determine if all files in the collection are apoapse data files.

        Returns
        -------
        bool
            True if all files are from the apoapse segment; False otherwise.

        """
        return all((f.segment == 'apoapse' for f in self.__dfc.filenames))

    def all_periapse(self) -> bool:
        """Determine if all files in the collection are periapse data files.

        Returns
        -------
        bool
            True if all files are from the periapse segment; False otherwise.

        """
        return all((f.segment == 'periapse' for f in self.__dfc.filenames))

    def all_ech(self) -> bool:
        """Determine if all files in the collection are echelle data files..

        Returns
        -------
        bool
            True if all files are from the ech channel; False otherwise.

        """
        return all((f.channel == 'ech' for f in self.__dfc.filenames))

    def all_fuv(self) -> bool:
        """Determine if all files in the collection are far-ultraviolet data
        files.

        Returns
        -------
        bool
            True if all files are from the fuv channel; False otherwise.

        """
        return all((f.channel == 'fuv' for f in self.__dfc.filenames))

    def all_muv(self) -> bool:
        """Determine if all files in the collection are mid-ultraviolet data
        files.

        Returns
        -------
        bool
            True if all files are from the muv segment; False otherwise.

        """
        return all((f.channel == 'muv' for f in self.__dfc.filenames))
