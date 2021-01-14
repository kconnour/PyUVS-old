# 3rd-party imports
from astropy.io import fits
import numpy as np


class DataContents:
    def __init__(self, filename):
        self.hdulist = fits.open(filename)

    def info(self):
        self.hdulist.info()

    def primary(self):
        return self.hdulist['primary']

    def __primary_shape(self):
        if np.ndim(self.primary()) == 2:
            return self.primary()[np.newaxis, :, :].shape
        else:
            return self.primary().shape

    @property
    def n_integrations(self):
        return self.__primary_shape()[0]

    @property
    def n_positions(self):
        return self.__primary_shape()[1]

    @property
    def n_wavelengths(self):
        return self.__primary_shape()[2]

    @staticmethod
    def _print_column(column):
        print(column.columns)
