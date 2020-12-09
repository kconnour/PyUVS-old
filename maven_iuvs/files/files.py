# Built-in imports
import os
import fnmatch as fnm


class Files:
    """A Files object is a container for storing absolute paths of files"""

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
        return [f.split('/')[-1] for f in self.file_paths]


class IUVSFiles(Files):
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
            raise ValueError('Some of the files are not IUVS files')


class L1bFiles(IUVSFiles):
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
            raise ValueError('Not all the l1b files are .fits files')


class SingleOrbitL1bFiles(L1bFiles):
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
            raise ValueError(f'mode must be one of {modes}')
