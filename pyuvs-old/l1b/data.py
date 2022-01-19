from astropy.io import fits
import numpy as np
from pyuvs.files import DataFilename, DataFilenameCollection
from pyuvs.l1b._files import L1bDataFilenameCollection


class L1bDataContents:
    def __init__(self, filename: DataFilename) -> None:
        """

        Parameters
        ----------
        filename
        """
        self.__hdulist = fits.open(filename.path)
        self.__primary_shape = self.__primary_shape()

    def __primary_shape(self) -> tuple[int, int, int]:
        primary = self.__hdulist['primary'].data
        ndims = np.ndim(primary)
        if ndims == 2:
            return primary[np.newaxis, :, :].shape
        elif ndims == 3:
            return primary.shape
        else:
            message = f'This file has {ndims} dimensions, not the standard 2 ' \
                      f'or 3. Unsure how to deal with this file...'
            raise IndexError(message)

    def __getattr__(self, method):
        return getattr(self.val, method)

    def __getitem__(self, x):
        return self.__hdulist[x]

    def info(self) -> None:
        """ Print info about the input file.

        """
        self.__hdulist.info()

    @property
    def n_integrations(self) -> int:
        """ Get the number of integrations in this observation file.

        """
        return self.__primary_shape[0]

    @property
    def n_positions(self) -> int:
        """ Get the number of detector positions in this observation file.

        """
        return self.__primary_shape[1]

    @property
    def n_wavelengths(self) -> int:
        """ Get the number of wavelengths used in this observation file.

        """
        return self.__primary_shape[2]

    @property
    def hdulist(self) -> fits.hdu.hdulist.HDUList:
        return self.__hdulist


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
    """Classify a collection of level 1b files.

    Attributes
    ----------
    files
        Collection of level 1b files.

    Raises
    ------
    ValueError
        Raised if any of the input files are not level 1b files.

    """
    def __init__(self, files: DataFilenameCollection):
        L1bDataFilenameCollection(files)
        self.__files = files

    def swath_number(self) -> list[int]:
        """Compute the swath number associated with each of the files in the
        collection of files. This assumes you give it a complete list of files
        from a single orbit, segment, and channel---otherwise the result of this
        function has no real meaning. I don't perform any checks because there
        is no way to ensure the list of files are complete.

        """
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

    def geometry(self) -> list[bool]:
        return [DataClassifier(L1bDataContents(f)).geometry() for f in self.__files]

    def all_geometry(self) -> bool:
        return all(self.geometry())

    def any_geometry(self) -> bool:
        return any(self.geometry())


if __name__ == '__main__':
    from pyuvs.files import FileFinder
    files = FileFinder('/media/kyle/Samsung_T5/IUVS_data').soschob(3453, segment='apoapse', channel='muv')
    dcc = DataCollectionClassifier(files)
    print(dcc.swath_number())