"""The sensitivity module loads the ancillary sensitivity curves as
numpy.ndarrays.
"""
from warnings import warn
from pyuvs.anc._arrays import _AncillaryArray, _AncillaryFileLoader


class FUVCurve(_AncillaryArray):
    """Create the far-ultraviolet sensitivity curve.

    This class will read in the standard FUV sensitivity curve. It otherwise
    acts like a numpy.ndarray.

    Notes
    -----
    The wavelengths associated with this curve are stored in
    :class:`FUVWavelengths`. This curve was created on 2014-06-09.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('mvn_iuv_sensitivity-fuv.npy')
        array = anc.load_dict()['sensitivity']
        return super().__new__(cls, array, anc.path)


class FUVWavelengths(_AncillaryArray):
    """Create the wavelengths for the far-ultraviolet sensitivity curve.

    This class will read in the standard FUV sensitivity curve wavelengths.
    It otherwise acts like a numpy.ndarray.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('mvn_iuv_sensitivity-fuv.npy')
        array = anc.load_dict()['wavelength']
        return super().__new__(cls, array, anc.path)


class MUVCurve(_AncillaryArray):
    """Create the mid-ultraviolet sensitivity curve.

    This class will read in the standard MUV sensitivity curve. It otherwise
    acts like a numpy.ndarray.

    Notes
    -----
    The wavelengths associated with this curve are stored in
    :class:`MUVWavelengths`. This curve was created on 2018-10-19.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('mvn_iuv_sensitivity-muv.npy')
        array = anc.load_dict()['sensitivity']
        return super().__new__(cls, array, anc.path)


class MUVWavelengths(_AncillaryArray):
    """Create the wavelengths for the mid-ultraviolet sensitivity curve.

    This class will read in the standard MUV sensitivity curve wavelengths.
    It otherwise acts like a numpy.ndarray.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('mvn_iuv_sensitivity-muv.npy')
        array = anc.load_dict()['wavelength']
        return super().__new__(cls, array, anc.path)


class PipelineMUVCurve(_AncillaryArray):
    """Create the mid-ultraviolet sensitivity curve used by the IUVS pipeline
    when converting level 1A data to level 1B.

    This class will read in the pipeline MUV sensitivity curve. This uses an
    early version of the calibration (see :class:`MUVCurve` for updated
    calibration) but is included for legacy purposes. It otherwise acts like a
    numpy.ndarray.

    Warnings
    --------
    UserWarning
        Raised if this class is used, as all current and future work should use
        the improved calibration.

    Notes
    -----
    The wavelengths associated with this curve are stored in
    :class:`PipelineMUVWavelengths`. This curve was created on 2014-06-09.

    """
    def __new__(cls):
        cls.__warn_this_is_deprecated()
        anc = _AncillaryFileLoader('mvn_iuv_sensitivity-muv-pipeline.npy')
        array = anc.load_dict()['sensitivity']
        return super().__new__(cls, array, anc.path)

    @staticmethod
    def __warn_this_is_deprecated():
        message = 'This object uses the old pipeline values. For updated ' \
                  'values, use MUVCurve instead.'
        warn(message)


class PipelineMUVWavelengths(_AncillaryArray):
    """Create the wavelengths for the mid-ultraviolet sensitivity curve used by
    the IUVS pipeline when converting level 1A data to level 1B.

    This class will read in the pipeline MUV sensitivity curve wavelengths.
    It otherwise acts like a numpy.ndarray.

    Warnings
    --------
    UserWarning
        Raised if this class is used, as all current and future work should use
        the improved calibration.

    """
    def __new__(cls):
        cls.__warn_this_is_deprecated()
        anc = _AncillaryFileLoader('mvn_iuv_sensitivity-muv-pipeline.npy')
        array = anc.load_dict()['wavelength']
        return super().__new__(cls, array, anc.path)

    @staticmethod
    def __warn_this_is_deprecated():
        message = 'This object uses the old pipeline values. For updated ' \
                  'values, use MUVWavelengths instead.'
        warn(message)
