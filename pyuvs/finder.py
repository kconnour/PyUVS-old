"""finder.py contains a variety of tools to help a user find IUVS data files on
their computer.
"""
import os
from typing import Any
import numpy as np
from pylint import epylint as lint
from pyuvs.misc import orbit_code


class DataPath:
    """A DataPath object creates absolute paths to where data products.

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
        IsADirectoryError
            Raised if path does not point to a valid directory.
        TypeError
            Raised if path is not a str.

        """
        self.__path = path

        self.__raise_error_if_input_is_bad()

    def __raise_error_if_input_is_bad(self) -> None:
        self.__raise_type_error_if_input_is_not_string()
        self.__raise_is_a_directory_error_if_path_does_not_exist()

    def __raise_type_error_if_input_is_not_string(self) -> None:
        if not isinstance(self.__path, str):
            raise TypeError('path must be a str.')

    def __raise_is_a_directory_error_if_path_does_not_exist(self) -> None:
        if not os.path.exists(self.__path):
            raise IsADirectoryError('path must point to a valid directory.')

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
        >>> path = DataPath('/foo/bar/')
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
