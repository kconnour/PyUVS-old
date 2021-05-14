import os
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.transform import resize
from pyuvs.graphics.coloring import Colormaps


class _AuxiliaryArray:
    """Abstract base class to read in an auxiliary numpy array.

    This acts like a numpy array, but provides some more convenient error
    handling.

    Parameters
    ----------
    file_path
        Absolute path of the array to read in.

    """
    def __init__(self, file_path: str) -> None:
        self.__file_path = file_path
        self.__array = self.__load_array()

    def __load_array(self) -> np.ndarray:
        try:
            return np.load(self.__file_path)
        except TypeError:
            message = 'file_path must be a string.'
            raise TypeError(message)
        except ValueError:
            message = 'file_path does not point to a numpy array'
            raise ValueError(message)

    def __getattr__(self, method):
        return getattr(self.__array, method)

    def __getitem__(self, item):
        return self.__array[item]

    @property
    def array(self) -> np.ndarray:
        """Get the loaded numpy array.

        """
        return self.__array

    @array.setter
    def array(self, val: np.ndarray) -> None:
        self.__array = val

    @property
    def file_location(self) -> str:
        """Get the absolute path of the loaded numpy array.

        """
        return self.__file_path


class SurfaceGeographyMap(_AuxiliaryArray):
    """Read in an auxiliary geography map.

    This class will read in the standard geographic map used with IUVS data
    unless another file is specified. It otherwise acts like a numpy.ndarray.

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

    @staticmethod
    def __make_file_path(file) -> str:
        return file if file is not None else \
            os.path.join(os.getcwd(), 'mars_surface_map.npy')


class ClosedMagneticFieldMap(_AuxiliaryArray):
    """Read in an auxiliary Martian closed magnetic field probability map.

    This class will read in the standard closed magnetic field map used with
    IUVS data unless another file is specified. It otherwise acts like a
    numpy.ndarray.

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
        self.array = np.flipud(self.array)  # to match the flipped QL I think

    @staticmethod
    def __make_file_path(file) -> str:
        return file if file is not None else \
            os.path.join(os.getcwd(), 'magnetic_field_closed_probability.npy')

    # TODO: make Zac look into gaussian smoothing with astropy
    def make_map_high_resolution(self) -> None:
        """ Make the map into a higher resolution map.

        """
        map_field = resize(self.array, (1800, 3600))
        V = map_field.copy()
        V[np.isnan(map_field)] = 0
        VV = gaussian_filter(V, sigma=1)
        W = 0 * map_field.copy() + 1
        W[np.isnan(map_field)] = 0
        WW = gaussian_filter(W, sigma=1)
        map_field = VV / WW
        map_field /= np.nanmax(map_field)
        self.array = map_field

    def colorize_map(self):
        """Colorize the map with the standard IUVS magnetic field coloring.

        """
        colormap = Colormaps()
        colormap.set_magnetic_field()
        self.array = colormap.cmap(colormap.norm(self.array))


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


if __name__ == '__main__':
    #m = SurfaceGeographyMap()
    #print(m.shape, m.file_location)
    #b = ClosedMagneticFieldMap()
    #b.make_map_high_resolution()
    #b.colorize_map()

    ff = Flatfield()
    wa = np.load('/pyuvs/aux/muv_flatfield_wavelengths.npy')
    ff.interpolate_to_new_scheme(50, wa[:-1])
    print(ff.shape)

