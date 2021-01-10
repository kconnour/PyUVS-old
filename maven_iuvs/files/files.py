# Built-in imports
import fnmatch as fnm
import os
from pathlib import Path
import warnings

# Local imports
from maven_iuvs.files.filenames import IUVSDataFilename


class IUVSDataFiles:
    def __init__(self, path, pattern):
        self.__check_path_exists(path)
        self.__input_glob = list(Path(path).glob(pattern))
        self.__input_abs_paths = self.__get_absolute_paths_of_input_glob()
        self.__input_filenames = self.__get_filenames_of_input_glob()
        self.__abs_paths = self.__make_absolute_paths()
        self.__filenames = self.__make_filenames()
        self.__raise_value_error_if_no_files_found()

    @staticmethod
    def __check_path_exists(path):
        try:
            if not os.path.exists(path):
                raise OSError(f'The path "{path}" does not exist on this '
                              'computer.')
        except TypeError:
            raise TypeError('The input value of path must be a string.')

    def __get_absolute_paths_of_input_glob(self):
        return sorted([str(f) for f in self.__input_glob if f.is_file()])

    def __get_filenames_of_input_glob(self):
        return sorted([f.name for f in self.__input_glob if f.is_file()])

    def __make_absolute_paths(self):
        return [self.__input_abs_paths[counter] for counter, f in
                enumerate(self.__input_filenames) if
                self.__make_filename(f) is not None]

    def __make_filenames(self):
        return [self.__make_filename(f) for f in self.__input_filenames if
                self.__make_filename(f) is not None]

    @staticmethod
    def __make_filename(filename):
        try:
            return IUVSDataFilename(filename)
        except ValueError:
            return None

    def __raise_value_error_if_no_files_found(self):
        if not self.filenames:
            raise ValueError('No files found matching the input pattern.')

    @property
    def abs_paths(self):
        return self.__abs_paths

    @property
    def filenames(self):
        return self.__filenames

    # TODO: index file functionality
    # TODO: downselect abs paths method based on pattern
    # TODO: downselect filenames method based on pattern
    # TODO: warn if no files found
    # TODO: downselect abs paths method based on bool list
    # TODO: downselect filenames method based on bool list
    # TODO: keep only the most recent files (like if r01 and r02 are present)
    # TODO: docstrings
    # TODO: filenames should work on .xml files but I need a .fits checker
    #  somewhere


path = '/media/kyle/Samsung_T5/IUVS_data/orbit07600'
pat = '*apoapse*7618*muv*'
a = IUVSDataFiles(path, pat)




'''class Files:
    """ A Files object stores the absolute paths to files, along with some file
    handling routines. """
    def __init__(self, path, pattern):
        """
        Parameters
        ----------
        path: str
            The location where to start looking for files.
        pattern: str
            Glob pattern to match filenames to.

        Notes
        -----
        This class uses glob-style matching, so a pattern of '**/*.foo' will
        recursively search for .foo files starting from path.
        """
        self.__check_path_exists(path)
        self.__input_glob = list(Path(path).glob(pattern))
        self.__absolute_paths = self.__get_absolute_paths_of_input_glob()
        self.__filenames = self.__get_filenames_of_input_glob()
        self._raise_value_error_if_no_files_found(self.absolute_paths)

    @staticmethod
    def __check_path_exists(path):
        try:
            if not os.path.exists(path):
                raise OSError(f'The path "{path}" does not exist on this '
                              'computer.')
        except TypeError:
            raise TypeError('The input value of path must be a string.')

    def __get_absolute_paths_of_input_glob(self):
        return sorted([str(f) for f in self.__input_glob if f.is_file()])

    def __get_filenames_of_input_glob(self):
        return sorted([f.name for f in self.__input_glob if f.is_file()])

    @staticmethod
    def _raise_value_error_if_no_files_found(files):
        if not files:
            raise ValueError('No files found matching the input pattern.')

    @property
    def absolute_paths(self):
        """ Get the absolute paths.

        Returns
        -------
        absolute_paths: list
            Strings of absolute paths of all files matching 'pattern' in
            'path'.
        """
        return self.__absolute_paths

    @absolute_paths.setter
    def absolute_paths(self, val):
        """ Set absolute_paths.

        Parameters
        ----------
        val: list
            Strings of absolute paths to set "absolute_paths" to.

        Returns
        -------
        None
        """
        warnings.warn('Changing absolute_paths is not recommended. '
                      'Consider creating a new object instead.')
        self.__absolute_paths = val

    @property
    def filenames(self):
        """ Get the filenames.

        Returns
        -------
        filenames: list
            Strings of filenames of all files matching 'pattern' in 'path'.
        """
        return self.__filenames

    @filenames.setter
    def filenames(self, val):
        """ Set filenames.

        Parameters
        ----------
        val: list
            Strings of filenames to set "filenames" to.

        Returns
        -------
        None
        """
        warnings.warn('Changing filenames is not recommended. '
                      'Consider creating a new object instead.')
        self.__filenames = val

    def downselect_absolute_paths(self, pattern):
        """ Downselect the absolute paths of filenames matching an input
        pattern.

        Parameters
        ----------
        pattern: str
            Glob pattern to match filenames to.

        Returns
        -------
        matching_paths: list
            Sorted list of absolute file paths containing files matching the
            input pattern.
        """
        try:
            matching_paths = [str(self.absolute_paths[counter]) for
                              counter, file in enumerate(self.filenames) if
                              fnm.fnmatch(file, pattern)]
            self.__warn_if_no_files_found(matching_paths)
            return sorted(matching_paths)
        except TypeError:
            raise TypeError('pattern must be a string.')

    def downselect_filenames(self, pattern):
        """ Downselect the filenames matching an input pattern.

        Parameters
        ----------
        pattern: str
            Glob pattern to match filenames to.

        Returns
        -------
        matching_filenames: list
            Sorted list of filenames matching the input pattern.
        """
        try:
            matching_filenames = [f for f in self.filenames if
                                  fnm.fnmatch(f, pattern)]
            self.__warn_if_no_files_found(matching_filenames)
            return sorted(matching_filenames)
        except TypeError:
            raise TypeError('pattern must be a string.')

    @staticmethod
    def __warn_if_no_files_found(files):
        if not files:
            warnings.warn('No files found matching the input pattern.')


class IUVSFiles(Files):
    """ An IUVSFiles object stores the absolute paths to files and downselects
    these files to ensure they are IUVS files. """
    def __init__(self, path, pattern):
        """
        Parameters
        ----------
        path: str
            The location where to start looking for files.
        pattern: str
            Glob pattern to match filenames to.

        Notes
        -----
        This class uses glob-style matching, so a pattern of '**/*.foo' will
        recursively search for .foo files starting from path.
        """
        super().__init__(path, pattern)
        self.__remove_non_iuvs_files()

    def __remove_non_iuvs_files(self):
        iuvs_pattern = 'mvn_iuv*'
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            self.absolute_paths = self.downselect_absolute_paths(iuvs_pattern)
            self.filenames = self.downselect_filenames(iuvs_pattern)
            self._raise_value_error_if_no_files_found(self.absolute_paths)


class IUVSDataFiles(IUVSFiles):
    """ An IUVSDataFiles object stores the absolute paths to files and
    downselects these files to ensure they are IUVS data files. """
    def __init__(self, path, pattern):
        """
        Parameters
        ----------
        path: str
            The location where to start looking for files.
        pattern: str
            Glob pattern to match filenames to.

        Notes
        -----
        This class uses glob-style matching, so a pattern of '**/*.foo' will
        recursively search for .foo files starting from path.
        """
        super().__init__(path, pattern)
        self.__remove_non_iuvs_data_files()

    def __remove_non_iuvs_data_files(self):
        extension = '*.fits*'
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            self.absolute_paths = self.downselect_absolute_paths(extension)
            self.filenames = self.downselect_filenames(extension)
            self._raise_value_error_if_no_files_found(self.absolute_paths)


class L1bFiles(IUVSDataFiles):
    """ An L1bFiles object stores the absolute paths to files and downselects
    these files to ensure they are IUVS level 1b data files. """
    def __init__(self, path, pattern):
        """
        Parameters
        ----------
        path: str
            The location where to start looking for files.
        pattern: str
            Glob pattern to match filenames to.

        Notes
        -----
        This class uses glob-style matching, so a pattern of '**/*.foo' will
        recursively search for .foo files starting from path.
        """
        super().__init__(path, pattern)
        self.__remove_non_l1b_data_files()

    def __remove_non_l1b_data_files(self):
        identifier = '*l1b*'
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            self.absolute_paths = self.downselect_absolute_paths(identifier)
            self.filenames = self.downselect_filenames(identifier)
            self._raise_value_error_if_no_files_found(self.absolute_paths)

    @property
    def maximum_mirror_angle(self):
        """ Get the maximum mirror angle of the IUVS mirror.

        Returns
        -------
        maximum_mirror_angle: float
            The maximum mirror angle [degrees].
        """
        return 59.6502685546875

    @property
    def minimum_mirror_angle(self):
        """ Get the minimum mirror angle of the IUVS mirror.

        Returns
        -------
        minimum_mirror_angle: float
            The minimum mirror angle [degrees].
        """
        return 30.2508544921875

    def check_relays(self):
        """ Get which files associated with this object are relay files.

        Returns
        -------
        relay_files: list
            A list of booleans. True if the corresponding file is as relay
            file; False otherwise.
        """
        relay_files = []
        for counter, f in enumerate(self.absolute_paths):
            with fits.open(f) as hdulist:
                relay_files.append(
                    self.__check_if_hdulist_is_relay_swath(hdulist))
        return relay_files

    def all_relays(self):
        """ Check if all of the files associated with this object are relay
        files.

        Returns
        -------
        relay_files: bool
            True if all files are relay files; False otherwise.
        """
        relay_files = self.check_relays()
        return all(relay_files)

    def any_relays(self):
        """ Check if any of the files associated with this object are relay
        files.

        Returns
        -------
        relay_files: bool
            True if any files are relay files; False otherwise.
        """
        relay_files = self.check_relays()
        return any(relay_files)

    def __check_if_hdulist_is_relay_swath(self, hdulist):
        angles = hdulist['integration'].data['mirror_deg']
        min_ang = np.amin(angles)
        max_ang = np.amax(angles)
        return True if min_ang == self.minimum_mirror_angle and \
                       max_ang == self.maximum_mirror_angle else False


class SingleOrbitSequenceChannelL1bFiles(L1bFiles):
    """ A SingleOrbitSequenceChannelL1bFiles object stores the absolute paths
    to files and performs checks that the files are IUVS files from a single
    orbit, sequence, and channel. """
    def __init__(self, path, pattern):
        """
        Parameters
        ----------
        path: str
            The location where to start looking for files.
        pattern: str
            Glob pattern to match filenames to.

        Notes
        -----
        This class uses glob-style matching, so a pattern of '**/*.foo' will
        recursively search for .foo files starting from path.
        """
        super().__init__(path, pattern)
        self.__check_files_are_single_orbit_sequence_channel()

    def __check_files_are_single_orbit_sequence_channel(self):
        self.__check_files_are_single_orbit()
        self.__check_files_are_single_sequence()
        self.__check_files_are_single_channel()

    def __check_files_are_single_orbit(self):
        orbits = [self.__get_orbit_from_filename(f) for f in self.filenames]
        self.__check_list_contains_1_unique_element(orbits, 'orbit')

    def __check_files_are_single_sequence(self):
        sequences = [self.__get_sequence_from_filename(f) for f in
                     self.filenames]
        self.__check_list_contains_1_unique_element(sequences, 'sequence')

    def __check_files_are_single_channel(self):
        channels = [self.__get_channel_from_filename(f) for f in
                    self.filenames]
        self.__check_list_contains_1_unique_element(channels, 'channel')

    # TODO: this fails on "..._relay-echelle-orbit..." (ex. orbit 12201)
    # TODO: Add this to filenames.py
    @staticmethod
    def __get_sequence_from_filename(filename):
        return filename.split('_')[3].split('-')[0]

    # TODO: this fails on "..._relay-echelle-orbit..." (ex. orbit 12201)
    # TODO: Add this to filenames.py
    @staticmethod
    def __get_orbit_from_filename(filename):
        return filename.split('_')[3].split('orbit')[1][:5]

    # TODO: this fails on "..._relay-echelle-orbit..." (ex. orbit 12201)
    # TODO: Add this to filenames.py
    @staticmethod
    def __get_channel_from_filename(filename):
        return filename.split('_')[3].split('-')[2]

    @staticmethod
    def __check_list_contains_1_unique_element(segment, name):
        n_unique_elements = len(list(set(segment)))
        if n_unique_elements != 1:
            raise ValueError(f'The input files are not from from a single '
                             f'{name}.')

    @property
    def orbit(self):
        """ Get the orbit number of these files.

        Returns
        -------
        orbit: int
            The orbit number.
        """
        return int(self.__get_orbit_from_filename(self.filenames[0]))

    @property
    def sequence(self):
        """ Get the observing sequence of these files.

        Returns
        -------
        sequence: str
            The observing sequence.
        """
        return self.__get_sequence_from_filename(self.filenames[0])

    @property
    def channel(self):
        """ Get the observing channel of these files.

        Returns
        -------
        channel: str
            The observing channel.
        """
        return self.__get_channel_from_filename(self.filenames[0])


# TODO: I'd like to design Files such that it can make filenames and
#  absolute_paths, and that all Files-derived classes can also set these
#  attributes, but the user cannot modify them (f.filenames ['asdf'] is
#  impossible, as is f.filenames.append(['asdf'). I don't know how to make a
#  setter protected. Also, since setters are for replacing values, I'm not sure
#  if they can ever protect against appending, etc.'''
