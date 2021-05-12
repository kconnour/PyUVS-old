import numpy as np
from pyuvs.l1b.data_contents import L1bDataContents


class DataClassifier:
    """Create an object that can classify L1b data.

    DataClassifier can classify a single data file.

    """
    def __init__(self, data_contents: L1bDataContents):
        """
        Parameters
        ----------
        data_contents
            The data file to classify.

        """
        self.__contents = data_contents

    def beta_flip(self) -> bool:
        """Determine if the data file was beta angle flipped.

        """
        sc = self.__contents['spacecraftgeometry'].data
        vi = sc['vx_instrument_inertial'][-1]
        vs = sc['v_spacecraft_rate_inertial'][-1]
        return np.sign(np.dot(vi, vs)) > 0

    def dayside(self) -> bool:
        """Determine if the data file was taken with dayside voltage settings.

        """
        return self.__contents['observation'].data['mcp_volt'][0] < 790

    def geometry(self) -> bool:
        """Determine if the data file contains geometry.

        """
        lat = self.__contents['pixelgeometry'].data['pixel_corner_lat']
        return ~np.isnan(lat.flatten()[0])

    def relay(self) -> bool:
        """Determine if the data file is a relay file.

        """
        mirror_angles = self.__contents['integration'].data['mirror_deg']
        return np.amin(mirror_angles) == 30.2508544921875 and \
               np.amax(mirror_angles) == 59.6502685546875

    def single_integration(self) -> bool:
        """Determine if the data file is a single integration.

        """
        return self.__contents.n_integrations == 1


class DataCollectionClassifier:
    pass


if __name__ == '__main__':
    from pyuvs.files import FileFinder
    files = FileFinder('/media/kyle/Samsung_T5/IUVS_data').soschob(3453, segment='apoapse', channel='muv')
    for f in files.filenames:
        l1b = L1bDataContents(f)
        dc = DataClassifier(l1b)
        print(dc.geometry(), dc.relay(), dc.beta_flip())
