# 3rd-party imports
from astropy.io import fits
import numpy as np

# Local imports
from maven_iuvs.data.data_properties import DataProperties
from maven_iuvs.data.l1b_contents import L1bDataContents


class L1bRelay(DataProperties):
    def __init__(self, filenames):
        super().__init__(filenames)

    @property
    def maximum_mirror_angle(self):
        """ Get the maximum mirror angle of the IUVS mirror.

        Returns
        -------
        maximum_mirror_angle: float
            The maximum mirror angle [degrees].
        """
        return 59.6502685546875

    @property
    def minimum_mirror_angle(self):
        """ Get the minimum mirror angle of the IUVS mirror.

        Returns
        -------
        minimum_mirror_angle: float
            The minimum mirror angle [degrees].
        """
        return 30.2508544921875

    def check_relays(self):
        """ Get which files associated with this object are relay files.

        Returns
        -------
        relay_files: list
            A list of booleans. True if the corresponding file is as relay
            file; False otherwise.
        """
        return [self.__check_if_file_is_relay_swath(f) for f in self.filenames]

    def all_relays(self):
        """ Check if all of the files associated with this object are relay
        files.

        Returns
        -------
        relay_files: bool
            True if all files are relay files; False otherwise.
        """
        return all(self.check_relays())

    def any_relays(self):
        """ Check if any of the files associated with this object are relay
        files.

        Returns
        -------
        relay_files: bool
            True if any files are relay files; False otherwise.
        """
        return any(self.check_relays())

    def __check_if_file_is_relay_swath(self, filename):
        angles = L1bDataContents(filename).mirror_angles
        min_ang = np.amin(angles)
        max_ang = np.amax(angles)
        return True if min_ang == self.minimum_mirror_angle and \
                       max_ang == self.maximum_mirror_angle else False


class L1bGeometry(DataProperties):
    def __init__(self, filenames):
        super().__init__(filenames)

    def check_geometry(self):
        return [self.__check_if_file_has_geometry(f) for f in self.filenames]

    def all_geometry(self):
        return all(self.check_geometry())

    def any_geometry(self):
        return any(self.check_geometry())

    @staticmethod
    def __check_if_file_has_geometry(filename):
        latitudes = L1bDataContents(filename).latitude
        return not np.isnan(latitudes).any()


class L1bDataProperties(L1bRelay, L1bGeometry):
    def __init__(self, filenames):
        super().__init__(filenames)
