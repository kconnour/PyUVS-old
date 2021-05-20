import numpy as np
from pyuvs.anc.flatfield import Flatfield, FlatfieldWavelengths


class MUVFlatfield:
    """Read in and manipulate the flatfield.

    This class reads in the standard mid-ultraviolet flatfield. It provides
    methods to interpolate it to a different binning scheme, as well as a
    different wavelength grid.

    """
    def __init__(self):
        self.__ff = Flatfield()
        self.__wavelengths = FlatfieldWavelengths()
        self.__n_positions = self.__ff.shape[0]
        self.__n_wavelengths = self.__ff.shape[1]

        self.__val = np.copy(self.__ff)

    def interpolate_to_new_scheme(self, n_positions: int,
                                  wavelengths: np.ndarray) -> None:
        """Interpolate the original flatfield to a new binning scheme.

        Parameters
        ----------
        n_positions
            The new number of positions.
        wavelengths
            The new wavelengths.

        """
        self.__val = self.__interpolate_to_positions(
            n_positions, self.__interpolate_to_new_wavelengths(wavelengths))

    def __interpolate_to_new_wavelengths(self, wavs: np.ndarray) -> np.ndarray:
        return np.array(
            [[np.interp(w, self.__wavelengths, self.val[pos, :]) for w in wavs]
             for pos in range(self.__n_positions)])

    def __interpolate_to_positions(self, n_positions: int,
                                   trimmed_ff: np.ndarray) -> np.ndarray:
        new_positions = np.linspace(0, self.__n_positions,
                                    num=n_positions)
        original_positions = np.linspace(0, self.__n_positions,
                                         num=self.__n_positions)
        return np.array(
            [[np.interp(pos, original_positions, trimmed_ff[:, wav])
              for wav in range(trimmed_ff.shape[-1])] for pos in new_positions]
        )

    @property
    def val(self):
        """ Get the value of the transformed flatfield.

        """
        return self.__val
