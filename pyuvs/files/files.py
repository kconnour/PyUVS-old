# Built-in imports
import copy
import fnmatch as fnm
import os
from typing import Generator, Union
import warnings

# Local imports
from pyuvs.files.filenames import IUVSDataFilename


class IUVSDataFilenameCollection:
    """ An IUVSDataFilenameCollection is a container for holding IUVS data
    files and provides methods for getting subsets of that data. """
    def __init__(self, files: list[str]) -> None:
        """
        Parameters
        ----------
        files: list[str]
            Absolute paths of IUVS data files.
        """
        self.__abs_paths, self.__filenames = \
            self.__make_absolute_paths_and_filenames(files)
        self.__raise_value_error_if_no_files_found()

    def __make_absolute_paths_and_filenames(self, files: list[str]) -> \
            tuple[list[str], list[IUVSDataFilename]]:
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
    # TODO: When python 3.10 releases, change -> IUVSDataFilename | None
    def __make_filename(filename: str) -> Union[IUVSDataFilename, None]:
        try:
            return IUVSDataFilename(filename)
        except ValueError:
            return None

    @staticmethod
    def __get_latest_filenames(filenames: Generator) -> list[IUVSDataFilename]:
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
    def __get_latest_abs_paths(filenames: list[IUVSDataFilename],
                               abs_paths: list[str]) -> list[str]:
        return [f for f in abs_paths for g in filenames if g.filename in f]

    def __raise_value_error_if_no_files_found(self) -> None:
        if not self.__abs_paths:
            raise ValueError('None of the input strings are IUVS files.')

    @property
    def abs_paths(self) -> list[str]:
        """ Get the absolute paths of the input IUVS data files.

        Returns
        -------
        abs_paths: list[str]
            Absolute paths of the data files.
        """
        return self.__abs_paths

    @property
    def filenames(self) -> list[IUVSDataFilename]:
        """ Get the filenames of the input IUVS data files.

        Returns
        -------
        filenames: list[IUVSDataFilename]
            Filenames of the inputs.
        """
        return self.__filenames

    @property
    def n_files(self) -> int:
        """ Get the number of input IUVS data files

        Returns
        -------
        n_files: int
            The number of files.
        """
        return len(self.__abs_paths)

    def get_matching_abs_paths(self, pattern: str) -> list[str]:
        """ Get the absolute paths of filenames matching an input pattern.

        Parameters
        ----------
        pattern: str
            Glob pattern to match filenames to.

        Returns
        -------
        matching_paths: list[str]
            Absolute file paths containing files matching the input pattern.
        """
        try:
            matching_paths = [self.abs_paths[counter] for
                              counter, file in enumerate(self.filenames) if
                              fnm.fnmatch(str(file), pattern)]
            self.__warn_if_no_files_found(matching_paths)
            return matching_paths
        except TypeError:
            raise TypeError('pattern must be a string.')

    def get_matching_filenames(self, pattern: str) -> list[IUVSDataFilename]:
        """ Get the filenames matching an input pattern.

        Parameters
        ----------
        pattern: str
            Glob pattern to match filenames to.

        Returns
        -------
        matching_filenames: list[IUVSDataFilename]
            Filenames matching the input pattern.
        """
        try:
            matching_filenames = [f for f in self.filenames if
                                  fnm.fnmatch(str(f), pattern)]
            self.__warn_if_no_files_found(matching_filenames)
            return matching_filenames
        except TypeError:
            raise TypeError('pattern must be a string.')

    def downscale_abs_paths(self, match: list[bool]) -> list[str]:
        """ Downscale the absolute paths of filenames matching a boolean list.

        Parameters
        ----------
        match: list[bool]
            Booleans to filter files from. Must be same length as abs_files.

        Returns
        -------
        abs_paths: list[str]
            Absolute paths where match==True.
        """
        return self.__downscale_based_on_boolean(self.abs_paths, match)

    def downscale_filenames(self, match: list[bool]) -> list[IUVSDataFilename]:
        """ Downscale the filenames matching a boolean list.

        Parameters
        ----------
        match: list
            Booleans to filter files from. Must be same length as filenames.

        Returns
        -------
        filenames: list[IUVSDataFilename]
            Filenames where match==True.
        """
        return self.__downscale_based_on_boolean(self.filenames, match)

    def __downscale_based_on_boolean(self, files: list, match: list[bool]) \
            -> list:
        if len(match) != len(self.abs_paths):
            raise ValueError('The length of bools must match the number of '
                             'files.')
        matching_paths = [f for counter, f in enumerate(files) if
                          match[counter]]
        self.__warn_if_no_files_found(matching_paths)
        return matching_paths

    def all_l1b(self) -> bool:
        """ Determine if all the input files are level 1b files.

        Returns
        -------
        l1b: bool
            True if all files are level 1b; False otherwise.
        """
        return all((f.level == 'l1b' for f in self.filenames))

    def all_l1c(self) -> bool:
        """ Determine if all the input files are level 1c files.

        Returns
        -------
        l1c: bool
            True if all files are level 1c; False otherwise.
        """
        return all((f.level == 'l1c' for f in self.filenames))

    def all_apoapse(self) -> bool:
        """ Determine if all the input files are apoapse files.

        Returns
        -------
        apoapse: bool
            True if all files are from the apoapse segment; False otherwise.
        """
        return all((f.segment == 'apoapse' for f in self.filenames))

    def all_periapse(self) -> bool:
        """ Determine if all the input files are periapse files.

        Returns
        -------
        periapse: bool
            True if all files are from the periapse segment; False otherwise.
        """
        return all((f.segment == 'periapse' for f in self.filenames))

    def all_ech(self) -> bool:
        """ Determine if all the input files are echelle files.

        Returns
        -------
        ech: bool
            True if all files are from the ech channel; False otherwise.
        """
        return all((f.channel == 'ech' for f in self.filenames))

    def all_fuv(self) -> bool:
        """ Determine if all the input files are far-ultraviolet files.

        Returns
        -------
        fuv: bool
            True if all files are from the fuv channel; False otherwise.
        """
        return all((f.channel == 'fuv' for f in self.filenames))

    def all_muv(self) -> bool:
        """ Determine if all the input files are mid-ultraviolet files.

        Returns
        -------
        muv: bool
            True if all files are from the muv segment; False otherwise.
        """
        return all((f.channel == 'muv' for f in self.filenames))

    @staticmethod
    def __warn_if_no_files_found(files: list) -> None:
        if not files:
            warnings.warn('No files found matching the input pattern.')
