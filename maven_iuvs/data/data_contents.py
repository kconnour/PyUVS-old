# 3rd-party imports
from astropy.io import fits
import numpy as np

# Local imports
from maven_iuvs.files.filenames import IUVSDataFilename


class IUVSDataContents:
    """ An IUVS DataContents object will open a IUVS .fits file and provide
    methods to get some of its content. """
    def __init__(self, filename):
        """
        Parameters
        ----------
        filename: IUVSDataFilename
            The filename to get contents of.
        """
        self.__check_input_is_IUVSDataFilename(filename)
        self.hdulist = fits.open(filename)

    @staticmethod
    def __check_input_is_IUVSDataFilename(filename):
        if not isinstance(filename, IUVSDataFilename):
            raise TypeError('filename must be an instance of '
                            'IUVSDataFilename.')

    def info(self):
        """ Print info about the input file.

        Returns
        -------
        None
        """
        self.hdulist.info()

    @property
    def primary(self):
        """ Get the primary data structure.

        Returns
        -------
        primary: np.ndarray
            The primary structure.
        """
        return self.hdulist['primary'].data

    @property
    def n_integrations(self):
        """ Get the number of integrations of this observation file.

        Returns
        -------
        n_integrations: int
            The number of integrations.
        """
        return self.__primary_shape()[0]

    @property
    def n_positions(self):
        """ Get the number of detector positions of this observation file.

        Returns
        -------
        n_positions: int
            The number of positions.
        """
        return self.__primary_shape()[1]

    @property
    def n_wavelengths(self):
        """ Get the number of wavelengths of this observation file.

        Returns
        -------
        n_wavelengths: int
            The number of wavelengths
        """
        return self.__primary_shape()[2]

    @staticmethod
    def _print_column(column):
        print(column.columns)

    def __primary_shape(self):
        if np.ndim(self.primary) == 2:
            return self.primary[np.newaxis, :, :].shape
        elif np.ndim(self.primary) == 3:
            return self.primary.shape
        else:
            raise IndexError(
                f'This file has {np.ndim(self.primary)} dimensions, not the '
                f'standard 2 or 3. Unsure how to deal with this file...')
