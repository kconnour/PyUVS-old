import numpy as np
from pyuvs.files import DataFilenameCollection
from pyuvs.l1b.data_contents import L1bDataContents
from pyuvs.l1b._files import L1bDataFilenameCollection


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
    def __init__(self, files: DataFilenameCollection):
        L1bDataFilenameCollection(files)
        self.__files = files

    def swath_number(self) -> list[int]:
        swath = []
        current_swath = 0
        first_file = True
        for file in self.__files.filenames:
            l1b = L1bDataContents(file)

            # Determine which way the mirror is scanning
            integration = l1b['integration'].data
            positive_mirror_direction = integration['mirror_deg'][-1] - \
                                        integration['mirror_deg'][0] > 0
            starting_mirror_angle = integration['mirror_deg'][0]

            # If it's the first file, it's obviously in the first swath
            if first_file:
                previous_ending_angle = integration['mirror_deg'][-1]
                swath.append(0)
                first_file = False
                continue

            if positive_mirror_direction and starting_mirror_angle < previous_ending_angle:
                current_swath += 1
            if not positive_mirror_direction and starting_mirror_angle > previous_ending_angle:
                current_swath += 1

            swath.append(current_swath)
            previous_ending_angle = integration['mirror_deg'][-1]

        return swath

    def dayside(self) -> list[bool]:
        return [DataClassifier(L1bDataContents(f)).dayside() for f in self.__files]

    def all_dayside(self) -> bool:
        return all(self.dayside())

    def any_dayside(self) -> bool:
        return any(self.dayside())

    def relay(self) -> list[bool]:
        return [DataClassifier(L1bDataContents(f)).relay() for f in self.__files]

    def all_relay(self) -> bool:
        return all(self.relay())

    def any_relay(self) -> bool:
        return any(self.relay())



if __name__ == '__main__':
    from pyuvs.files import FileFinder
    files = FileFinder('/media/kyle/Samsung_T5/IUVS_data').soschob(3453, segment='apoapse', channel='muv')
    dfc = DataCollectionClassifier(files)
    print(dfc.swath_number())
    print(dfc.dayside())
