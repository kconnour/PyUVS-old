"""The flatfield module loads the ancillary flatfield as a numpy.ndarray.
"""
from pyuvs.anc._arrays import _AncillaryArray, _AncillaryFileLoader


class Flatfield(_AncillaryArray):
    """Create the mid-ultraviolet flatfield

    This class will read in the standard MUV flatfield used with IUVS data.
    It otherwise acts like a numpy.ndarray.

    Notes
    -----
    This file is only designed to be used with level 1B data. To calibrate the
    data, divide the data by the flatfield. The wavelengths associated with this
    flatfield are stored in :class:`FlatfieldWavelengths`.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('mvn_iuv_flatfield.npy')
        array = anc.load_dict()['flatfield']
        return super().__new__(cls, array, anc.path)


class FlatfieldWavelengths(_AncillaryArray):
    """Create the mid-ultraviolet flatfield wavelengths.

    This class will read in the wavelengths used when creating the standard MUV
    flatfield. It otherwise acts like a numpy.ndarray.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('mvn_iuv_flatfield.npy')
        array = anc.load_dict()['wavelengths']
        return super().__new__(cls, array, anc.path)
