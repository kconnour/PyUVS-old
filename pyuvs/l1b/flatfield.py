'''
This needs to be a mutable flatfield object. This was the old one

class MUVFlatfield(_AuxiliaryArray):
    """Read in the standard MUV flatfield.

    This class will read in the standard MUV flatfield (133 positions,
    19 wavelengths) unless another file is specified. It otherwise acts like a
    numpy.ndarray. It contains methods to interpolate to another binning
    scheme if necessary.

    Parameters
    ----------
    file_path
       Absolute path of the array to read in.

    Raises
    ------
    TypeError
        Raised if :code:`file_path` is not a string or None.
    ValueError
        Raised if :code:`file_path` does not have a .npy extension.

    """
    def __init__(self, file_path=None):
        file_path = self.__make_file_path(file_path)
        super().__init__(file_path)
        self.__wavelengths = self.__get_flatfield_wavelengths()
        self.__n_positions = self.array.shape[0]
        self.__n_wavelengths = self.array.shape[1]

    @staticmethod
    def __make_file_path(file) -> str:
        return file if file is not None else \
            os.path.join(os.getcwd(), 'muv_flatfield.npy')

    @staticmethod
    def __get_flatfield_wavelengths() -> _AuxiliaryArray:
        path = os.path.join(os.getcwd(), 'muv_flatfield_wavelengths.npy')
        return _AuxiliaryArray(path)

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
        self.array = self.__interpolate_to_positions(
            n_positions, self.__interpolate_to_new_wavelengths(wavelengths))

    def __interpolate_to_new_wavelengths(self, wavs: np.ndarray) -> np.ndarray:
        return np.array(
            [[np.interp(w, self.__wavelengths, self[pos, :]) for w in wavs]
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
'''