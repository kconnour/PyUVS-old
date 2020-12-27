# Built-in imports
import fnmatch as fnm
import os
from pathlib import Path
import warnings


# TODO: Add a method to combine multiple objects together by combining lists
#     : of attributes. Or a function instead?
class Files:
    """ A Files object stores the absolute paths to files, along with some file
    handling routines."""
    def __init__(self, path, pattern):
        """
        Parameters
        ----------
        path: str
            The location where to start looking for files.
        pattern: str
            Glob pattern to match filenames to.

        Attributes:
        ----------
        absolute_paths: list
            Strings of absolute paths of all files matching 'pattern' in
            'path'.
        filenames: list
            Strings of filenames of all files matching 'pattern' in 'path'.

        Notes
        -----
        This class uses glob-style matching, so a pattern of '**/*.pdf' will
        recursively search for .pdf files starting from path.
        """
        self.__check_path_exists(path)
        self.__input_glob = list(Path(path).glob(pattern))
        self.absolute_paths = self.__get_absolute_paths_of_input_pattern()
        self.filenames = self.__get_filenames_of_input_pattern()
        self._raise_value_error_if_no_files_found(self.absolute_paths)

    @staticmethod
    def __check_path_exists(path):
        try:
            if not os.path.exists(path):
                raise OSError(f'The path "{path}" does not exist on this '
                              f'computer.')
        except TypeError:
            raise TypeError('The input value of "path" must be a string.')

    def __get_absolute_paths_of_input_pattern(self):
        return sorted([f for f in self.__input_glob if f.is_file()])

    def __get_filenames_of_input_pattern(self):
        return sorted([f.name for f in self.__input_glob if f.is_file()])

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
            matching_paths = []
            for counter, file in enumerate(self.filenames):
                if fnm.fnmatch(file, pattern):
                    matching_paths.append(self.absolute_paths[counter])
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

    @staticmethod
    def _raise_value_error_if_no_files_found(files):
        if not files:
            raise ValueError('No files found matching the input pattern.')


class IUVSFiles(Files):
    """ An IUVSFiles object stores the absolute paths to files and downselects
    these files to ensure they are IUVS files."""
    def __init__(self, path, pattern):
        """
        Parameters
        ----------
        path: str
            The location where to start looking for files.
        pattern: str
            Glob pattern to match filenames to.

        Attributes:
        ----------
        absolute_paths: list
            Strings of absolute paths of all files matching 'pattern' in
            'path'.
        filenames: list
            Strings of filenames of all files matching 'pattern' in 'path'.

        Notes
        -----
        This class uses glob-style matching, so a pattern of '**/*.pdf' will
        recursively search for .pdf files starting from path.
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
    downselects these files to ensure they are IUVS data files."""
    def __init__(self, path, pattern):
        """
        Parameters
        ----------
        path: str
            The location where to start looking for files.
        pattern: str
            Glob pattern to match filenames to.

        Attributes:
        ----------
        absolute_paths: list
            Strings of absolute paths of all files matching 'pattern' in
            'path'.
        filenames: list
            Strings of filenames of all files matching 'pattern' in 'path'.

        Notes
        -----
        This class uses glob-style matching, so a pattern of '**/*.pdf' will
        recursively search for .pdf files starting from path.
        """
        super().__init__(path, pattern)
        self.__remove_non_iuvs_data_files()

    def __remove_non_iuvs_data_files(self):
        iuvs_pattern = '*.fits*'
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            self.absolute_paths = self.downselect_absolute_paths(iuvs_pattern)
            self.filenames = self.downselect_filenames(iuvs_pattern)
            self._raise_value_error_if_no_files_found(self.absolute_paths)
