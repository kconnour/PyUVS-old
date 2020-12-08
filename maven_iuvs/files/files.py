# Built-in imports
import os
import fnmatch as fnm


class Files:
    """A Files object is a container for storing absolute paths of files"""

    def __init__(self, pattern, path):
        """
        Parameters
        ----------
        pattern: str
            The regex pattern to look for
        path: str
            The absolute path where to begin looking for files

        Attributes
        ----------
        files: list
            A sorted list of the absolute paths to the files matching pattern in path

        Notes
        -----
        I need to add recursive option for speed
        """
        self.__check_inputs_are_strings(pattern, path)
        self.__check_path_exists(path)
        self.files = self.__find_files_matching_pattern_in_path(pattern, path)
        self.__inform_if_no_files_found()

    @staticmethod
    def __find_files_matching_pattern_in_path(pattern, path):
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnm.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return sorted(result)

    def get_filenames_containing_identifier(self, identifier):
        """ Get the filenames that contain an input identifier

        Parameters
        ----------
        identifier: str
            Pattern to check if files contain

        Returns
        -------
        list of files containing pattern
        """
        self.__check_input_is_string(identifier, 'identifier')
        return [f for f in self.files if identifier in f]

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

    def __inform_if_no_files_found(self):
        if not self.files:
            print('No files found matching the input pattern')


class IUVSFiles(Files):
    """An IUVSFiles object is a container for storing absolute paths of IUVS data files"""

    def __init__(self, pattern, path):
        """
        Parameters
        ----------
        pattern: str
            The regex pattern to look for
        path: str
            The absolute path where to begin looking for files

        Attributes
        ----------
        files: list
            A sorted list of the absolute paths to the files matching pattern in path

        Notes
        -----
        I need to add recursive option for speed
        """
        super().__init__(pattern, path)
        self.__check_files_are_iuvs_data_files()

    def __check_files_are_iuvs_data_files(self):
        iuvs_data_files = self.get_filenames_containing_identifier('mvn_iuv')
        if self.files != iuvs_data_files:
            raise ValueError('Not all of the files are IUVS files')


class L1bFiles(IUVSFiles):
    """An L1bFiles object is a container for storing absolute paths of level 1b IUVS data files"""

    def __init__(self, pattern, path):
        """
        Parameters
        ----------
        pattern: str
            The regex pattern to look for
        path: str
            The absolute path where to begin looking for files

        Attributes
        ----------
        files: list
            A sorted list of the absolute paths to the files matching pattern in path

        Notes
        -----
        I need to add recursive option for speed
        """
        super().__init__(pattern, path)
        self.__check_files_are_l1b_iuvs_data_files()

    def __check_files_are_l1b_iuvs_data_files(self):
        iuvs_data_files = self.get_filenames_containing_identifier('l1b')
        if self.files != iuvs_data_files:
            raise ValueError('Not all the IUVS data files are l1b files')


class SingleOrbitL1bFiles(L1bFiles):
    """A SingleOrbitL1bFiles object is a container for storing absolute paths of level 1b IUVS data files for a single
    orbit"""

    def __init__(self, orbit, path, sequence='apoapse', mode='muv'):
        """
        Parameters
        ----------
        orbit: int
            The orbit to look for files from
        path: str
            The absolute path where to begin looking for files
        sequence: str
            The observing sequence to look for files from. Default is 'apoapse'
        mode: str
            The observing mode to look for files from. Default is 'muv'

        Attributes
        ----------
        files: list
            A sorted list of the absolute paths to the files matching pattern in path
        orbit: int
            The orbit corresponding to files

        Notes
        -----
        I need to add recursive option for speed
        """
        self.orbit = orbit
        self.__check_orbit_is_int()
        pattern = f'*{sequence}*{orbit}*{mode}*'
        super().__init__(pattern, path)

    def __check_orbit_is_int(self):
        if not isinstance(self.orbit, int):
            raise TypeError('orbit must be an int')
