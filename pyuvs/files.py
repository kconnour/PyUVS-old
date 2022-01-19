"""The files module contains tools for getting IUVS data files from one's
computer.
"""
import copy
import fnmatch as fnm
from pathlib import Path
from warnings import warn
import numpy as np
import os
import time
import glob


class DataFilename:
    """A data structure containing info from a single IUVS filename.

    It ensures the input filename represents an IUVS filename and extracts all
    information related to the observation and processing pipeline from the
    input.

    Parameters
    ----------
    path
        The absolute path of an IUVS data product.

    Raises
    ------
    FileNotFoundError
        Raised if the input path does not lead to a valid file.
    TypeError
        Raised if the input path is not a string.
    ValueError
        Raised if the file is not an IUVS data file.

    """
    def __init__(self, path: str) -> None:
        self.__path = self.__create_path(path)
        self.__filename = self.__path.name

    @staticmethod
    def __create_path(path: str) -> Path:
        _DataFilePathChecker(path)
        return Path(path)

    def __str__(self) -> str:
        return str(self.__path)

    @property
    def path(self) -> str:
        """Get the input absolute path.

        """
        return str(self.__path)

    @property
    def filename(self) -> str:
        """Get the filename from the absolute path.

        """
        return self.__filename

    @property
    def spacecraft(self) -> str:
        """Get the spacecraft code from the filename.

        """
        return self.__split_filename_on_underscore()[0]

    @property
    def instrument(self) -> str:
        """Get the instrument code from the filename.

        """
        return self.__split_filename_on_underscore()[1]

    @property
    def level(self) -> str:
        """Get the data product level from the filename.

        """
        return self.__split_filename_on_underscore()[2]

    @property
    def description(self) -> str:
        """Get the description from the filename.

        """
        return self.__split_filename_on_underscore()[3]

    @property
    def segment(self) -> str:
        """Get the observation segment from the filename.

        """
        orbit_index = self.__get_split_index_containing_orbit()
        segments = self.__split_description()[:orbit_index]
        return '-'.join(segments)

    @property
    def orbit(self) -> int:
        """Get the orbit number from the filename.

        """
        orbit_index = self.__get_split_index_containing_orbit()
        orbit = self.__split_description()[orbit_index].removeprefix('orbit')
        return int(orbit)

    # TODO: in python3.10 change type hint to | type(None)
    @property
    def channel(self) -> str:
        """Get the observation channel from the filename.

        """
        orbit_index = self.__get_split_index_containing_orbit()
        try:
            return self.__split_description()[orbit_index + 1]
        except IndexError:
            return None

    @property
    def timestamp(self) -> str:
        """Get the timestamp of the observation from the filename.

        """
        return self.__split_filename_on_underscore()[4]

    @property
    def date(self) -> str:
        """Get the date of the observation from the filename.

        """
        return self.__split_timestamp()[0]

    @property
    def year(self) -> int:
        """Get the year of the observation from the filename.

        """
        return int(self.date[:4])

    @property
    def month(self) -> int:
        """Get the month of the observation from the filename.

        """
        return int(self.date[4:6])

    @property
    def day(self) -> int:
        """Get the day of the observation from the filename.

        """
        return int(self.date[6:])

    @property
    def time(self) -> str:
        """Get the time of the observation from the filename.

        """
        return self.__split_timestamp()[1]

    @property
    def hour(self) -> int:
        """Get the hour of the observation from the filename.

        """
        return int(self.time[:2])

    @property
    def minute(self) -> int:
        """Get the minute of the observation from the filename.

        """
        return int(self.time[2:4])

    @property
    def second(self) -> int:
        """Get the second of the observation from the filename.

        """
        return int(self.time[4:])

    @property
    def version(self) -> str:
        """Get the version code from the filename.

        """
        return self.__split_filename_on_underscore()[5]

    @property
    def revision(self) -> str:
        """Get the revision code from the filename.

        """
        return self.__split_filename_on_underscore()[6]

    @property
    def extension(self) -> str:
        """Get the extension of filename.

        """
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
        return self.timestamp.split('T')

    def __split_description(self) -> list[str]:
        return self.description.split('-')

    def __get_split_index_containing_orbit(self) -> int:
        return [c for c, f in enumerate(self.__split_description())
                if 'orbit' in f][0]


class _DataPathChecker:
    def __init__(self, path: str):
        self.__path = self.__make_path(path)
        self.__warn_if_path_does_not_exist()

    @staticmethod
    def __make_path(path: str) -> Path:
        try:
            return Path(path)
        except TypeError:
            message = f'path should be a str, not a {type(path)}.'
            raise TypeError(message)

    def __warn_if_path_does_not_exist(self) -> None:
        if not self.__path.exists():
            message = 'path does not point to a valid directory.'
            warn(message)


class _DataFilePathChecker:
    def __init__(self, path: str) -> None:
        self.__path = self.__make_path(path)

        self.__raise_file_not_found_error_if_file_does_not_exist()
        self.__raise_value_error_if_not_iuvs_file()
        self.__raise_value_error_if_not_fits_file()

    @staticmethod
    def __make_path(path: str) -> Path:
        try:
            return Path(path)
        except TypeError:
            message = f'path should be a str, not a {type(path)}.'
            raise TypeError(message)

    def __raise_file_not_found_error_if_file_does_not_exist(self) -> None:
        if not self.__path.exists():
            message = 'The input path does not exist.'
            raise FileNotFoundError(message)

    def __raise_value_error_if_not_iuvs_file(self) -> None:
        if not self.__path.name.startswith('mvn_iuv_'):
            message = 'The input file is not an IUVS file.'
            raise ValueError(message)

    def __raise_value_error_if_not_fits_file(self) -> None:
        if not (self.__path.name.endswith('.fits') or
                self.__path.name.endswith('.fits.gz')):
            message = 'The input file is not a .fits file.'
            raise ValueError(message)


class Orbit:
    """A class for working with a single MAVEN orbit.

    This class ensures an input orbit is an int. It provides common
    manipulations performed on an orbit number.


    Parameters
    ----------
    orbit
        The orbit number.

    """
    def __init__(self, orbit: int) -> None:
        self. __orbit = orbit

        self.__raise_type_error_if_orbit_is_not_int()

    def __raise_type_error_if_orbit_is_not_int(self) -> None:
        if not isinstance(self.__orbit, int):
            message = 'orbit must be an int.'
            raise TypeError(message)

    def code(self) -> str:
        """Make the 5 digit "code" for this orbit.

        """
        return self.__generic_code(self.__orbit)

    def block(self) -> int:
        """Make the orbit block (group of 100 orbits) for this orbit.

        """
        return int(np.floor(self.__orbit / 100) * 100)

    def block_folder(self) -> str:
        """Make the IUVS-standard folder name for this orbit.

        """
        return f'orbit{self.__generic_code(self.block())}'

    @staticmethod
    def __generic_code(orbit: int) -> str:
        return str(orbit).zfill(5)

    @property
    def orbit(self) -> int:
        """Get the input orbit number.

        """
        return self.__orbit


class _StringMatcher:
    """A class for matching strings.

    This class ensures an input is a string and provides methods to see if it
    matches a set of patterns.

    Parameters
    ----------
    channel
        The channel pattern. Can be a glob-like pattern.

    """
    def __init__(self, pattern: str, name: str) -> None:
        self.__pattern = pattern
        self.__name = name

        self.__raise_type_error_if_pattern_is_not_str()

    def __raise_type_error_if_pattern_is_not_str(self) -> None:
        if not isinstance(self.__pattern, str):
            message = f'{self.__name} must be an str.'
            raise TypeError(message)

    def match_str(self, patterns: list[str]) -> list[bool]:
        """Check if the input strings matches elements in a list of patterns.

        """
        return [fnm.fnmatch(f, self.__pattern) for f in patterns]

    def raise_value_error_if_invalid_pattern(self, patterns: list[str]) -> None:
        """Raise a value error if the input to this class does not match a set
        of input patterns.

        """
        if not any(self.match_str(patterns)):
            message = f'{self.__name} does not match any known {self.__name}s.'
            raise ValueError(message)

    @property
    def pattern(self):
        return self.__pattern


class _ChannelChecker(_StringMatcher):
    """A class for working with IUVS channels.

    This class ensures an input channel is an str and that the pattern matches
    known channels.

    Parameters
    ----------
    channel
        The channel pattern. Can be a glob-like pattern.

    """
    def __init__(self, channel: str) -> None:
        super().__init__(channel, 'channel')
        self.__channels = ['ech', 'fuv', 'muv']
        self.raise_value_error_if_invalid_pattern(self.__channels)

    @property
    def channels(self) -> list[str]:
        """Get the list of known IUVS channels.

        """
        return self.__channels


class _SegmentChecker(_StringMatcher):
    """A class for working with MAVEN orbital segments.

    This class ensures an input segment is an str and that the pattern matches
    known segments.

    Parameters
    ----------
    segment
        The segment pattern. Can be a glob-like pattern.

    """
    def __init__(self, segment: str):
        super().__init__(segment, 'segment')
        self.__segments = ['apoapse', 'incorona', 'inlimb', 'outcorona',
                           'outlimb', 'periapse', 'star']
        self.raise_value_error_if_invalid_pattern(self.__segments)

    @property
    def segments(self) -> list[str]:
        """Get the list of known MAVEN orbital segments.

        """
        return self.__segments


class DataFilenameCollection:
    """A data structure for holding IUVS data filenames.

    This class checks that the input files are IUVS data files and only keeps
    the most recent data files.

    """
    def __init__(self, files: list[str]) -> None:
        """
        Parameters
        ----------
        files
            Absolute paths of IUVS data files.

        Raises
        ------
        TypeError
            Raised if the input files are not an iterable.
        ValueError
            Raised if none of the input files are IUVS data files.

        """
        self.__filenames = self.__make_latest_data_filenames(files)
        self.__raise_value_error_if_no_input_iuvs_files()
        self.__counter = 0

    def __make_latest_data_filenames(self, files: list[str]) \
            -> list[DataFilename]:
        try:
            filenames = self.__make_filenames(sorted(files))
            return self.__get_latest_filenames(filenames)
        except TypeError as te:
            raise TypeError('files must be a list of strings.') from te

    def __make_filenames(self, filenames: list[str]) -> list[DataFilename]:
        return [k for f in filenames if
                (k := self.__make_filename(f)) is not None]

    @staticmethod
    # TODO: When python 3.10 releases, change -> DataFilename | None
    def __make_filename(filename: str) -> DataFilename:
        try:
            return DataFilename(filename)
        except FileNotFoundError:
            return None
        except TypeError:
            return None
        except ValueError:
            return None

    # TODO: this logic can now be simplified since I don't need to keep the indx
    @staticmethod
    def __get_latest_filenames(filenames: list[DataFilename]) \
            -> list[DataFilename]:
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
    def __remove_non_fits_files(filenames: list[DataFilename]) \
            -> list[DataFilename]:
        return [f for f in filenames if
                f.extension == 'fits' or f.extension == 'fits.gz']

    def __raise_value_error_if_no_input_iuvs_files(self) -> None:
        if not self.__filenames:
            raise ValueError('There were no input IUVS data files.')

    def __iter__(self):
        return self

    def __next__(self):
        if self.__counter < self.n_files:
            self.__counter += 1
            return self.__filenames[self.__counter - 1]
        else:
            self.__counter = 0
        raise StopIteration

    @property
    def filenames(self) -> list[DataFilename]:
        """Get the collection of DataFilenames made from the input files.

        """
        return self.__filenames

    @property
    def n_files(self) -> int:
        """Get the number of unique files.

        """
        return len(self.__filenames)

    def all_l1b(self) -> bool:
        """Determine if all files in the collection are level 1b data files.

        """
        return all((f.level == 'l1b' for f in self.filenames))

    def all_l1c(self) -> bool:
        """Determine if all files in the collection are level 1c data files.

        """
        return all((f.level == 'l1c' for f in self.filenames))

    def all_apoapse(self) -> bool:
        """Determine if all files in the collection are apoapse data files.

        """
        return all((f.segment == 'apoapse' for f in self.filenames))

    def all_periapse(self) -> bool:
        """Determine if all files in the collection are periapse data files.

        """
        return all((f.segment == 'periapse' for f in self.filenames))

    def all_ech(self) -> bool:
        """Determine if all files in the collection are echelle data files..

        """
        return all((f.channel == 'ech' for f in self.filenames))

    def all_fuv(self) -> bool:
        """Determine if all files in the collection are far-ultraviolet data
        files.

        """
        return all((f.channel == 'fuv' for f in self.filenames))

    def all_muv(self) -> bool:
        """Determine if all files in the collection are mid-ultraviolet data
        files.

        """
        return all((f.channel == 'muv' for f in self.filenames))


class DataPath:
    """Create absolute paths to where data products reside.

    DataPath contains methods to create strings of absolute paths to where data
    products reside, given a set of assumptions.

    """
    def __init__(self, path: str) -> None:
        """
        Parameters
        ----------
        path
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
        self.__path = self.__make_path(path)

    @staticmethod
    def __make_path(path: str) -> Path:
        _DataPathChecker(path)
        return Path(path)

    def block(self, orbit: int) -> str:
        """Make the path to an orbit, assuming orbits are organized in blocks
        of 100 orbits.

        Parameters
        ----------
        orbit
            The orbit number.

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
        orbit = Orbit(orbit)
        return str(Path.joinpath(self.__path, orbit.block_folder()))

    def block_paths(self, orbits: list[int]) -> list[str]:
        """Make paths to a series of orbits, assuming orbits are organized in
        blocks of 100 orbits.

        Parameters
        ----------
        orbits
            The orbit numbers.

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
        try:
            return [self.block(f) for f in orbits]
        except TypeError:
            raise ValueError('Each value in orbits must be an int.') from None


class DataPattern:
    """Create glob search patterns for IUVS data.

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
        level
            The level pattern to get data from.
        segment
            The segment pattern to get data from.
        orbit
            The orbit pattern to get data from.
        channel
            The channel pattern to get data from.
        timestamp
            The timestamp pattern to get data from.
        version
            The version pattern to get data from.
        extension
            The extension pattern to get data from.

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
        orbit
            The orbit number to get data from.
        segment
            The segment pattern to get data from.
        channel
            The channel pattern to get data from.

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
            o = Orbit(orbit)
            return self.data_pattern(orbit=o.code(), segment=segment,
                                     channel=channel)
        except TypeError as te:
            raise TypeError('orbit must be an int.') from te

    def multi_orbit_patterns(self, orbits: list[int], segment: str,
                             channel: str) -> list[str]:
        """Make glob patterns for each orbit in a list of orbits.

        Parameters
        ----------
        orbits
            Orbits to make patterns for.
        segment
            The segment pattern to get data from.
        channel
            The channel pattern to get data from.

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
        patterns
            Patterns to search for.

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
        """Prepend `**/` to the input pattern.

        Parameters
        ----------
        pattern: str
            Generic glob pattern.

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


class FileFinder:
    """Find IUVS data files on their computer.

    FileFinder holds methods that help the user find files on their computer
    given a set of assumptions.

    """
    def __init__(self, path: str) -> None:
        """
        Parameters
        ----------
        path
            The absolute path where to begin looking for IUVS data files.

        Raises
        ------
        OSError
            Raised if path does not exist.
        TypeError
            Raised if path is not a str.

        """
        self.__path = path

        self.__raise_error_if_input_path_is_bad()

    def __raise_error_if_input_path_is_bad(self) -> None:
        self.__raise_type_error_if_path_is_not_str()

    def __raise_type_error_if_path_is_not_str(self) -> None:
        if not isinstance(self.__path, str):
            raise TypeError('path must be a str.')

    def soschob(self, orbit: int, segment: str, channel: str) \
            -> DataFilenameCollection:
        """Make a DataFilenameCollection for files matching an input orbit,
        segment pattern, and channel pattern, assuming orbits are organized in
        blocks of 100.

        Parameters
        ----------
        orbit
            The orbit to get files from.
        segment
            The observing segment to get files from.
        channel
            The observing mode to get files from.

        """
        p = DataPath(self.__path).block(orbit)
        pat = DataPattern().orbit_pattern(orbit, segment, channel)
        abs_paths = self.__glob_files(p, pat)
        return DataFilenameCollection(abs_paths)

    def multi_orbit_files(self, orbits: list[int], segment: str, channel: str) \
            -> DataFilenameCollection:
        """Make a DataFilenameCollection for an input list of orbits,
        segment pattern, and channel pattern, assuming orbits are organized in
        blocks of 100.

        Parameters
        ----------
        orbits
            Orbits to get files from.
        segment
            The observing segment to get files from.
        channel
            The observing channel to get files from.

        """
        p = DataPath(self.__path).block_paths(orbits)
        pat = DataPattern().multi_orbit_patterns(orbits, segment, channel)
        path_list = [self.__glob_files(p[f], pat[f]) for f in range(len(p))]
        abs_paths = [k for f in path_list for k in f]
        return DataFilenameCollection(abs_paths)

    def orbit_range_files(self, orbit_start: int, orbit_end: int, segment: str,
                          channel: str) -> DataFilenameCollection:
        """ Make a DataFilenameCollection for all orbits in a range of orbits
        with a segment pattern and channel pattern, assuming orbits are
        organized in blocks of 100.

        Parameters
        ----------
        orbit_start
            The starting orbit to get files from.
        orbit_end
            The ending orbit to get files from.
        segment
            The observing segment to get files from.
        channel
            The observing channel to get files from.

        """
        orbits = list(range(orbit_start, orbit_end))
        return self.multi_orbit_files(orbits, segment=segment, channel=channel)

    def __glob_files(self, path: str, pattern: str) -> list[str]:
        g = self.__perform_glob(path, pattern)
        return self.__get_absolute_paths_of_glob(g)

    @staticmethod
    def __perform_glob(path: str, pattern: str):
        return Path(path).glob(pattern)

    @staticmethod
    def __get_absolute_paths_of_glob(inp_glob) -> list[str]:
        return sorted([str(f) for f in inp_glob if f.is_file()])



class FileCollection:
    def __init__(self, directory_path: str):
        self.directory = Path(directory_path)
        self._raise_not_a_directory_error_if_not_a_directory()
        self.files = self._get_files_in_directory()

    def _raise_not_a_directory_error_if_not_a_directory(self):
        if not self.directory.is_dir():
            raise NotADirectoryError('The input is not a directory.')

    def _get_files_in_directory(self):
        return sorted([str(f) for f in self.directory.iterdir() if f.is_file()])

    def get_non_latest_files(self) -> list[str]:
        all_files = sorted([f.replace('s0', 'a0') for f in self.files])
        last_time_stamp = ''
        old_files = []
        for file in all_files:
            if 'aurora' in file:
                current_time_stamp = file[-34:-19]  # Ex. 20190428T115842
            else:
                current_time_stamp = file[-27:-12]  # Ex. 20190428T115842
            if current_time_stamp == last_time_stamp:
                # Remove s0 files
                if 'a0' in last_file:
                    old_files.append(last_file.replace('a0', 's0'))
                # Remove r0 files
                else:
                    old_files.append(last_file)

            # Update my variables
            last_time_stamp = current_time_stamp
            last_file = file

        return old_files

    def remove_non_latest_files(self) -> None:
        non_latest_files = self.get_non_latest_files()
        for f in non_latest_files:
            os.remove(f)
            self.files.remove(f)


class QuicklookSwathGeometry(FileCollection):
    def __init__(self, directory_path: str):
        super().__init__(directory_path)

    def get_empty_quicklooks(self) -> list[str]:
        return [f for f in self.files if 'missing' in f]

    def remove_empty_quicklooks(self) -> None:
        empty_qls = self.get_empty_quicklooks()
        for f in empty_qls:
            os.remove(f)
            self.files.remove(f)


def remove_zac_old_quicklooks(directory_path: str):
    ql = QuicklookSwathGeometry(directory_path)
    ql.remove_empty_quicklooks()
    ql.get_non_latest_files()


if __name__ == '__main__':
    d = '/Volumes/MacBackup/milby_ql/ql_apoapse-swath-geometry-muv'
    for i in range(156):
        p = d + '/orbit' + str(i*100).zfill(5)
        remove_zac_old_quicklooks(p)
