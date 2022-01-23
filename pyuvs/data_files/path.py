import math
from pathlib import Path
from pyuvs.data_files.filename import DataFilename

# TODO: somewhere I should validate that the paths I found were indeed IUVS
#  filenames.


class Orbit(int):
    """An object representing an orbit number.

    Parameters
    ----------
    value
        The orbit number.

    Raises
    ------
    TypeError
        Raised if the input type cannot be converted to an int.
    ValueError
        Raised if the orbit is not positive.
    """

    def __new__(cls, value, *args, **kwargs):
        return super().__new__(cls, value, *args, **kwargs)

    def __init__(self, value):
        self._raise_value_error_if_orbit_is_not_positive()

    def _raise_value_error_if_orbit_is_not_positive(self) -> None:
        if self <= 0:
            message = f'The input orbit ({self}) must be a positive integer.'
            raise ValueError(message)

    def make_code(self) -> str:
        """Make the 5 digit orbit "code".

        Returns
        -------
        The orbit code

        Examples
        --------
        >>> from pyuvs.data_files import Orbit
        >>> Orbit(3453).make_code()
        '03453'

        """
        return f'{self}'.zfill(5)

    def get_block(self) -> int:
        """Make the block number corresponding to this orbit.

        Returns
        -------
        The orbit block

        Examples
        --------
        >>> from pyuvs.data_files import Orbit
        >>> Orbit(3453).get_block()
        3400

        """
        return math.floor(self / 100) * 100

    def get_block_folder(self) -> str:
        """Make the folder block number corresponding to this orbit.

        Returns
        -------
        The orbit block folder

        Examples
        --------
        >>> from pyuvs.data_files import Orbit
        >>> Orbit(3453).get_block_folder()
        'orbit03400'

        """
        block = self.get_block()
        orbit_code = Orbit(block).make_code()
        return f'orbit{orbit_code}'


class Segment(str):
    """An object representing an orbital segment

    Parameters
    ----------
    value
        The segment name.

    Raises
    ------
    ValueError
        Raised if the segment is not in the known list of segments.
    """
    def __new__(cls, value, *args, **kwargs):
        return super().__new__(cls, value, *args, **kwargs)

    def __init__(self, value):
        self._segments = ['apoapse', 'incorona', 'inlimb', 'outcorona',
                          'outlimb', 'periapse', 'star']
        self._raise_value_error_if_segment_not_a_known_segment()

    def _raise_value_error_if_segment_not_a_known_segment(self):
        if self not in self._segments:
            message = f'The input segment ({self}) is not in the known ' \
                      f'segments ({self._segments}).'
            raise ValueError(message)


class Channel(str):
    """An object representing an channel.

    Parameters
    ----------
    value
        The channel name.

    Raises
    ------
    ValueError
        Raised if the segment is not in the known list of channels.
    """
    def __new__(cls, value, *args, **kwargs):
        return super().__new__(cls, value)

    def __init__(self, value):
        self._channels = ['ech', 'fuv', 'muv']
        self._raise_value_error_if_channel_not_a_known_channel()

    def _raise_value_error_if_channel_not_a_known_channel(self):
        if self not in self._channels:
            message = f'The input channel ({self}) is not in the known ' \
                      f'channels ({self._channels}).'
            raise ValueError(message)


class DataPath:
    """An object that can find paths of IUVS data.

    Parameters
    ----------
    data_directory
        Absolute path to the directory where data are located.

    Raises
    ------
    NotADirectoryError
        Raised if :code:`data_directory` does not point to a valid directory.

    """
    def __init__(self, data_directory: str):
        self.data_directory = data_directory
        self._original_directory = self.data_directory

    @staticmethod
    def _raise_not_a_directory_error_if_directory_does_not_exist(
            path: Path) -> None:
        if not path.exists():
            message = f'The input data directory ({path}) does not exist.'
            raise NotADirectoryError(message)

    @property
    def data_directory(self) -> Path:
        """Get the location of the set data directory.

        Returns
        -------
        The data directory.

        """
        return self._data_directory

    @data_directory.setter
    def data_directory(self, directory: str):
        directory = Path(directory)
        self._raise_not_a_directory_error_if_directory_does_not_exist(
            directory)
        self._data_directory = directory

    def reset_to_original_directory(self) -> None:
        """Reset the data directory to its original value.

        """
        self.data_directory = self._original_directory

    def add_block_to_directory(self, orbit: int) -> None:
        """Add an obit block to the end of the data directory.

        Parameters
        ----------
        orbit
            The orbit number.

        """
        block = Orbit(orbit).get_block_folder()
        self.data_directory = self._data_directory / block

    def find_all_files(self, segment: str, orbit: int, channel: str) \
            -> list[Path]:
        """Find all files that match a set of patterns.

        Parameters
        ----------
        segment
            The segment name.
        orbit
            The orbit number.
        channel
            The channel name.

        """
        data_filename_pattern = self._make_filename_pattern(
            segment, orbit, channel)
        return sorted(self.data_directory.glob(data_filename_pattern))

    def find_latest_files(self, segment: str, orbit: int, channel: str) \
            -> list[Path]:
        """Find the latest files that match a set of patterns.

        Parameters
        ----------
        segment
            The segment name.
        orbit
            The orbit number.
        channel
            The channel name.

        """
        all_files = self.find_all_files(segment, orbit, channel)
        outdated_files = self._find_outdated_files(all_files)
        return [f for f in all_files if f not in outdated_files]

    @staticmethod
    def _make_filename_pattern(segment: str, orbit: int, channel: str) -> str:
        return f'*{Segment(segment)}*{Orbit(orbit)}*{Channel(channel)}*.fits*'

    @staticmethod
    def _find_outdated_files(files: list[Path]) -> list[Path]:
        filenames = [str(f).replace('s0', 'a0') for f in files]
        last_time_stamp = ''
        last_channel = ''
        last_file = None
        old_files = []
        for f in filenames:
            df = DataFilename(f)
            if df.timestamp == last_time_stamp and df.channel == last_channel:
                old_files.append(Path(last_file))
            if 'a0' in f:
                f = f.replace('a0', 's0')
            last_time_stamp = df.timestamp
            last_channel = df.channel
            last_file = f
        return old_files


def find_latest_file_paths(
        data_directory: str, segment: str, orbit: int, channel: str) \
        -> list[Path]:
    """Find the latest file paths of a given pattern in a given directory.

    Parameters
    ----------
    data_directory
        The directory where the data are located.
    segment
        The segment name.
    orbit
        The orbit number.
    channel
        The channel name.

    """
    dp = DataPath(data_directory)
    return dp.find_latest_files(segment, orbit, channel)


def find_latest_file_paths_from_block(
        data_directory: str, segment: str, orbit: int, channel: str) \
        -> list[Path]:
    """Find the latest file paths of a given pattern in a given directory,
    where the directory is divided into blocks of data spanning 100 orbits.

    Parameters
    ----------
    data_directory
        The directory where the data blocks are located.
    segment
        The segment name.
    orbit
        The orbit number.
    channel
        The channel name.

    """
    dp = DataPath(data_directory)
    dp.add_block_to_directory(orbit)
    return dp.find_latest_files(segment, orbit, channel)


def find_latest_apoapse_muv_file_paths_from_block(
        data_directory: str, orbit: int) -> list[Path]:
    """Find the latest apoapse muv file paths in a given directory, where the
    directory is divided into blocks of data spanning 100 orbits.

    Parameters
    ----------
    data_directory
        The directory where the data blocks are located.
    orbit
        The orbit number.

    """
    return find_latest_file_paths_from_block(
        data_directory, 'apoapse', orbit, 'muv')
