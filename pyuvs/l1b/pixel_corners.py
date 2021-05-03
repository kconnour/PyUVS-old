import numpy as np
from pyuvs.l1b.data_contents import L1bDataContents


class PixelCorners:
    def __init__(self, file: L1bDataContents) -> None:
        self.__file = file

    #def __reshape_vector(self):

    def local_time(self) -> np.ndarray:
        delta_lon = (self.__file.longitude.T - self.__file.sub_solar_lon).T
        return np.mod(34/360 * delta_lon + 12, 24)
