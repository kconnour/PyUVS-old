"""The arrays module contains classes to read in external arrays.
"""
import numpy as np
from pathlib import Path


class _AncillaryArray(np.ndarray):
    """Create a numpy.ndarray of an ancillary array. It also stores the path.

    Attributes
    ----------
    array
        The ancillary array.
    path
        The absolute path to the ancillary array.

    """
    def __new__(cls, array, path):
        obj = np.asarray(array).view(cls)
        obj.path = path
        return obj

    def __array_finalize(self, obj):
        if obj is None:
            return
        self.path = getattr(obj, 'path', None)


class _AncillaryFileLoader:
    """Create the path of an ancillary file from a filename.

    Attributes
    ----------
    filename
        The filename of a file to load in.

    """
    def __init__(self, filename: str) -> None:
        self.__file_path = self.__make_file_path(filename)

    @staticmethod
    def __make_file_path(filename: str) -> Path:
        return Path.joinpath(Path(__file__).parents[0], 'files', filename)

    def load_array(self) -> np.ndarray:
        return np.load(str(self.__file_path))

    def load_dict(self) -> dict:
        return np.load(str(self.__file_path), allow_pickle=True).item()

    @property
    def path(self) -> Path:
        return self.__file_path
