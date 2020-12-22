# Built-in imports
import fnmatch as fnm
import glob
import os
import warnings


'''class Files:
    def __init__(self, pattern, path, recursive=False):
        """ A Files object is a container for storing absolute paths of files
        Parameters
        ----------
        pattern: str
            The regex pattern of filenames to search for
        path: str
            The absolute path where to begin looking for files
        recursive: bool
            Specify if you want to recursively look for files. Default is False

        Attributes
        ----------
        file_paths: list
            A sorted list of the absolute paths to the files matching pattern in path
        file_names: list
            A sorted list of the file names matching pattern in path
        """
        self.__check_inputs_are_strings(pattern, path)
        self.__check_path_exists(path)
        self.file_paths = self.__get_absolute_paths_matching_pattern_in_path(pattern, path, recursive)
        self.__inform_if_no_files_found()
        self.file_names = self.__get_filenames_from_absolute_paths()

    def get_abs_path_of_filenames_containing_pattern(self, pattern):
        """ Get the filenames that contain a pattern

        Parameters
        ----------
        pattern: str
            Regex pattern to check if files contain

        Returns
        -------
        List of files containing the user-input pattern
        """
        self.__check_input_is_string(pattern, 'identifier')
        matching_file_paths = []
        for counter, file in enumerate(self.file_names):
            if fnm.fnmatch(file, pattern):
                matching_file_paths.append(self.file_paths[counter])
        return matching_file_paths

    def __check_inputs_are_strings(self, pattern, path):
        self.__check_input_is_string(pattern, 'pattern')
        self.__check_input_is_string(path, 'path')

    @staticmethod
    def __check_input_is_string(variable, name):
        if not isinstance(variable, str):
            raise TypeError(f'{name} must be a string')

    @staticmethod
    def __check_path_exists(path):
        if not os.path.exists(path):
            print(f'The path {path} does not exist on this computer...')

    def __get_absolute_paths_matching_pattern_in_path(self, pattern, path, recursive):
        if recursive:
            files = self.__recursively_find_files_matching_pattern_in_path(pattern, path)
        else:
            files = self.__find_files_matching_pattern_in_directory(pattern, path)
        return sorted(files)

    @staticmethod
    def __recursively_find_files_matching_pattern_in_path(pattern, path):
        matching_files = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnm.fnmatch(name, pattern):
                    matching_files.append(os.path.join(root, name))
        return matching_files

    @staticmethod
    def __find_files_matching_pattern_in_directory(pattern, path):
        files = [fn for fn in next(os.walk(path))[2]]
        matching_files = []
        for name in files:
            if fnm.fnmatch(name, pattern):
                matching_files.append(os.path.join(path, name))
        return matching_files

    def __inform_if_no_files_found(self):
        if not self.file_paths:
            print('No files found matching the input pattern')

    def __get_filenames_from_absolute_paths(self):
        return [f.split('/')[-1] for f in self.file_paths]'''


'''class IUVSFiles(Files):
    """An IUVSFiles object is a container for storing absolute paths of IUVS data files"""

    def __init__(self, pattern, path, recursive=False):
        """
        Parameters
        ----------
        pattern: str
            The regex pattern of filenames to search for
        path: str
            The absolute path where to begin looking for files
        recursive: bool
            Specify if you want to recursively look for files. Default is False

        Attributes
        ----------
        file_paths: list
            A sorted list of the absolute paths to the files matching pattern in path
        file_names: list
            A sorted list of the file names matching pattern in path
        """
        super().__init__(pattern, path, recursive=recursive)
        self.__check_files_are_iuvs_data_files()

    def __check_files_are_iuvs_data_files(self):
        iuvs_files = self.get_abs_path_of_filenames_containing_pattern('mvn_iuv*')
        if self.file_paths != iuvs_files:
            raise ValueError('Some of the files are not IUVS files')'''


'''class L1bFiles(IUVSFiles):
    """An L1bFiles object is a container for storing absolute paths of level 1b IUVS data files"""

    def __init__(self, pattern, path, recursive=False):
        """
        Parameters
        ----------
        pattern: str
            The regex pattern of filenames to search for
        path: str
            The absolute path where to begin looking for files
        recursive: bool
            Specify if you want to recursively look for files. Default is False

        Attributes
        ----------
        file_paths: list
            A sorted list of the absolute paths to the files matching pattern in path
        file_names: list
            A sorted list of the file names matching pattern in path
        """
        super().__init__(pattern, path, recursive=recursive)
        self.__check_files_are_l1b_iuvs_data_files()

    def __check_files_are_l1b_iuvs_data_files(self):
        l1b_files = self.get_abs_path_of_filenames_containing_pattern('*l1b*')
        if self.file_paths != l1b_files:
            raise ValueError('Not all the IUVS files are l1b files')
        iuvs_data_files = self.get_abs_path_of_filenames_containing_pattern('*fits.gz')
        if self.file_paths != iuvs_data_files:
            raise ValueError('Not all the l1b files are .fits files')'''


'''class SingleOrbitL1bFiles(L1bFiles):
    """A SingleOrbitL1bFiles object is a container for storing absolute paths of level 1b IUVS data files for a single
    orbit"""

    def __init__(self, orbit, path, sequence='apoapse', mode='muv', recursive=False):
        """
        Parameters
        ----------
        orbit: int
            The orbit from which to look for files
        path: str
            The absolute path where to begin looking for files
        sequence: str
            The observing sequence from which to look for files. Default is 'apoapse'
        mode: str
            The observing mode from which to look for files. Default is 'muv'
        recursive: bool
            Specify if you want to recursively look for files. Default is False

        Attributes
        ----------
        file_paths: list
            A sorted list of the absolute paths to the files matching pattern in path
        file_names: list
            A sorted list of the file names matching pattern in path
        orbit: int
            The orbit corresponding to files
        """
        self.__check_inputs_are_expected_types(orbit, sequence, mode)
        self.orbit = orbit
        pattern = f'*{sequence}*{orbit}*{mode}*'
        super().__init__(pattern, path, recursive=recursive)

    def __check_inputs_are_expected_types(self, orbit, sequence, mode):
        self.__check_orbit_is_int(orbit)
        self.__check_sequence_is_valid(sequence)
        self.__check_mode_is_valid(mode)

    @staticmethod
    def __check_orbit_is_int(orbit):
        if not isinstance(orbit, int):
            raise TypeError('orbit must be an int')

    @staticmethod
    def __check_sequence_is_valid(sequence):
        sequences = ['apoapse', 'incorona', 'indisk', 'inlimb', 'outcorona', 'outdisk', 'outlimb', 'periapse', 'star']
        if sequence not in sequences:
            raise ValueError(f'sequence must be one of {sequences}')

    @staticmethod
    def __check_mode_is_valid(mode):
        modes = ['fuv', 'muv']
        if mode not in modes:
            raise ValueError(f'mode must be one of {modes}')'''


class Files:
    def __init__(self, path, pattern):
        """ A Files object stores the absolute paths to files, along with some file handling routines.

        Parameters
        ----------
        path: str
            The location where to start looking for files.
        pattern: str
            The regex pattern to match filenames to.

        Properties
        ----------
        absolute_file_paths: list
            Absolute file paths of all files matching pattern in path.
        filenames: list
            Filenames of all files matching pattern in path.

        Notes
        -----
        This class used glob-style matching, so '**/*.pdf' will recursively search for .pdf files starting from path
        """
        self.__check_path_exists(path)
        self.__absolute_paths = self.__get_absolute_file_paths_matching_pattern_in_path(path, pattern)
        self.__filenames = self.__get_filenames_from_absolute_paths(self.__absolute_paths)
        self.__warn_if_no_files_found(self.__absolute_paths)

    @property
    def absolute_file_paths(self):
        return self.__absolute_paths

    @property
    def filenames(self):
        return self.__filenames

    def get_absolute_paths_of_filenames_containing_pattern(self, pattern):
        """ Get the absolute paths of filenames that contain a requested pattern.

        Parameters
        ----------
        pattern: str
            A regex pattern to search filenames for.

        Returns
        -------
        matching_file_paths: list
            A list of absolute paths of filenames that match pattern.
        """
        try:
            matching_file_paths = []
            for counter, file in enumerate(self.__filenames):
                if fnm.fnmatch(file, pattern):
                    matching_file_paths.append(self.__absolute_paths[counter])
            self.__warn_if_no_files_found(matching_file_paths)
            return matching_file_paths
        except TypeError:
            raise TypeError('pattern must be a string.')

    def get_filenames_containing_pattern(self, pattern):
        """ Get the filenames that contain a requested pattern.

        Parameters
        ----------
        pattern: str
            A regex pattern to search filenames for.

        Returns
        -------
        matching_filenames: list
            A list of filenames that match pattern.
        """
        absolute_paths = self.get_absolute_paths_of_filenames_containing_pattern(pattern)
        matching_filenames = self.__get_filenames_from_absolute_paths(absolute_paths)
        return matching_filenames

    @staticmethod
    def __check_path_exists(path):
        try:
            if not os.path.exists(path):
                raise OSError(f'The path {path} does not exist on this computer.')
        except TypeError:
            raise TypeError('The input value of path should be a string.')

    @staticmethod
    def __get_absolute_file_paths_matching_pattern_in_path(path, pattern):
        try:
            return glob.glob(os.path.join(path, pattern), recursive=True)
        except TypeError:
            raise TypeError('Cannot join path and pattern. The inputs are probably not strings.')

    @staticmethod
    def __get_filenames_from_absolute_paths(absolute_paths):
        # TODO: splitting on / is not OS independent, not that I think many users will use Windows
        return [f.split('/')[-1] for f in absolute_paths]

    @staticmethod
    def __warn_if_no_files_found(absolute_paths):
        if not absolute_paths:
            warnings.warn('No files found matching the input pattern.')
