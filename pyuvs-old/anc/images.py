"""The images module loads ancillary images as numpy.ndarrays.
"""
from pyuvs.anc._arrays import _AncillaryArray, _AncillaryFileLoader


class SurfaceGeographyMap(_AncillaryArray):
    """Create the Martian geographic map.

    This class will read in the standard geographic map used with IUVS data.
    It otherwise acts like a numpy.ndarray.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('mars_surface_map.npy')
        array = anc.load_array()
        return super().__new__(cls, array, anc.path)


class ClosedMagneticFieldMap(_AncillaryArray):
    """Create the Martian closed magnetic field probability map.

    This class will read in the standard closed magnetic field map used with
    IUVS data. It otherwise acts like a numpy.ndarray.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('magnetic_field_closed_probability.npy')
        array = anc.load_array()
        return super().__new__(cls, array, anc.path)


class OpenMagneticFieldMap(_AncillaryArray):
    """Create the Martian open magnetic field probability map.

    This class will read in the standard open magnetic field map used with
    IUVS data. It otherwise acts like a numpy.ndarray.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('magnetic_field_open_probability.npy')
        array = anc.load_array()
        return super().__new__(cls, array, anc.path)
