# Built-in imports
import fnmatch as fnm
import os
import warnings

# Local imports
from maven_iuvs.files.filenames import IUVSDataFilename


class IUVSDataFilenameCollection:
    """ An IUVSDataFilenameCollection is a container for holding IUVS data
    files and provides methods for getting subsets of that data. """
    def __init__(self, files: list):
        """
        Parameters
        ----------
        files: list
            List of strings of absolute paths to IUVS data files.
        """
        self.__abs_paths, self.__filenames = \
            self.__make_absolute_paths_and_filenames(files)
        self.__raise_value_error_if_no_files_found()

    def __make_absolute_paths_and_filenames(self, files):
        input_abs_paths = self.__get_unique_absolute_paths(files)
        input_filenames = self.__get_filenames_from_paths(input_abs_paths)
        iuvs_data_filenames = self.__make_filenames(input_filenames)
        latest_filenames = self.__get_latest_filenames(iuvs_data_filenames)
        latest_abs_paths = self.__get_latest_abs_paths(latest_filenames,
                                                       input_abs_paths)
        return latest_abs_paths, latest_filenames

    @staticmethod
    def __get_unique_absolute_paths(files):
        return sorted(list(set(files)))

    @staticmethod
    def __get_filenames_from_paths(paths):
        return [os.path.basename(f) for f in paths]

    def __make_filenames(self, filenames):
        return [k for f in filenames if
                (k := self.__make_filename(f)) is not None]

    @staticmethod
    def __make_filename(filename):
        try:
            return IUVSDataFilename(filename)
        except ValueError:
            return None

    # TODO: make this suck less
    def __get_latest_filenames(self, filenames):
        input_filenames = [f.filename for f in filenames]
        modified_fnames = sorted([f.replace('s0', 'a0') for f in
                                  input_filenames])
        data_filenames = [IUVSDataFilename(f) for f in modified_fnames]
        old_filename_indices = self.__get_old_filename_indices(data_filenames)
        latest_modified_filenames = [f for counter, f in
                                     enumerate(data_filenames) if
                                     counter not in old_filename_indices]
        latest_filenames = [IUVSDataFilename(f.filename.replace('a0', 's0'))
                            for f in latest_modified_filenames]
        return latest_filenames

    # TODO: make this suck less
    @staticmethod
    def __get_old_filename_indices(filenames):
        old_filename_indices = []
        for i in range(len(filenames)):
            if i == len(filenames)-1:
                continue
            if filenames[i].timestamp == filenames[i+1].timestamp:
                old_filename_indices.append(i)
        return old_filename_indices

    @staticmethod
    def __get_latest_abs_paths(filenames, abs_paths):
        return [f for f in abs_paths for g in filenames if g.filename in f]

    def __raise_value_error_if_no_files_found(self):
        if not self.__abs_paths:
            raise ValueError('None of the input strings are IUVS files.')

    @property
    def abs_paths(self) -> list:
        """ Get the absolute paths of the input IUVS data files.

        Returns
        -------
        abs_paths: list
            List of strings of absolute paths of the data files.
        """
        return self.__abs_paths

    @property
    def filenames(self) -> list:
        """ Get the filenames of the input IUVS data files.

        Returns
        -------
        filenames: list
            List of IUVSDataFilenames.
        """
        return self.__filenames

    def get_matching_abs_paths(self, pattern: str) -> list:
        """ Get the absolute paths of filenames matching an input pattern.

        Parameters
        ----------
        pattern: str
            Glob pattern to match filenames to.

        Returns
        -------
        matching_paths: list
            List of absolute file paths containing files matching the
            input pattern.
        """
        try:
            matching_paths = [self.abs_paths[counter] for
                              counter, file in enumerate(self.filenames) if
                              fnm.fnmatch(str(file), pattern)]
            self.__warn_if_no_files_found(matching_paths)
            return matching_paths
        except TypeError:
            raise TypeError('pattern must be a string.')

    def get_matching_filenames(self, pattern: str) -> list:
        """ Get the filenames matching an input pattern.

        Parameters
        ----------
        pattern: str
            Glob pattern to match filenames to.

        Returns
        -------
        matching_filenames: list
            List of IUVSDataFilenames matching the input pattern.
        """
        try:
            matching_filenames = [f for f in self.filenames if
                                  fnm.fnmatch(str(f), pattern)]
            self.__warn_if_no_files_found(matching_filenames)
            return matching_filenames
        except TypeError:
            raise TypeError('pattern must be a string.')

    def downscale_abs_paths(self, match: list) -> list:
        """ Downscale the absolute paths of filenames matching a boolean list.

        Parameters
        ----------
        match: list
            Boolean list to filter files from. Must be same length as
            abs_files.

        Returns
        -------
        abs_paths: list
            List of IUVSDataFilenames where match==True.
        """
        return self.__downscale_based_on_boolean(self.abs_paths, match)

    def downscale_filenames(self, match: list) -> list:
        """ Downscale the filenames matching a boolean list.

        Parameters
        ----------
        match: list
            Boolean list to filter files from. Must be same length as
            filenames.

        Returns
        -------
        filenames: list
            List of strings where match==True.
        """
        return self.__downscale_based_on_boolean(self.filenames, match)

    def __downscale_based_on_boolean(self, files: list, match: list) -> list:
        if len(match) != len(self.abs_paths):
            raise ValueError('The length of bools must match the number of '
                             'files.')
        matching_paths = [f for counter, f in enumerate(files) if
                          match[counter]]
        self.__warn_if_no_files_found(matching_paths)
        return matching_paths

    @staticmethod
    def __warn_if_no_files_found(files: list):
        if not files:
            warnings.warn('No files found matching the input pattern.')


'''class L1bDataFiles(IUVSDataFiles):
    # TODO: docstring
    def __init__(self, files):
        # TODO: docstring
        super().__init__(files)
        self.__raise_value_error_if_not_all_l1b_files()

    # TODO: docstring
    def __raise_value_error_if_not_all_l1b_files(self):
        levels = [f.level for f in self.filenames]
        if not all(f == 'l1b' for f in levels):
            raise ValueError('Not all input files are l1b files.')


class SingleSoschobL1bDataFiles(L1bDataFiles):
    # TODO: docstring
    def __init__(self, files):
        # TODO: docstring
        super().__init__(files)
        self.__raise_value_error_if_not_single_soschob()

    def __raise_value_error_if_not_single_soschob(self):
        self.__check_single_orbit()
        self.__check_single_segment()
        self.__check_single_channel()

    def __check_single_segment(self):
        segments = [f.segment for f in self.filenames]
        self.__raise_value_error_if_not_single_property(segments, 'segment')

    def __check_single_orbit(self):
        orbits = [f.orbit for f in self.filenames]
        self.__raise_value_error_if_not_single_property(orbits, 'orbit')

    def __check_single_channel(self):
        channels = [f.channel for f in self.filenames]
        self.__raise_value_error_if_not_single_property(channels, 'channel')

    def __raise_value_error_if_not_single_property(self, prop, prop_name):
        single_property = self.__check_list_contains_one_unique_value(prop)
        if not single_property:
            raise ValueError(f'The input does not contain one {prop_name}')

    @staticmethod
    def __check_list_contains_one_unique_value(inp):
        return True if len(list(set(inp))) == 1 else False'''
