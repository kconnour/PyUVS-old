"""The templates module loads ancillary spectral templates.
"""
from pyuvs.anc._arrays import _AncillaryArray, _AncillaryFileLoader


class CO2PlusFDB(_AncillaryArray):
    """Create the CO:sub:2:sup:+:Fox-DB band system template.

    This class will read in the template. It otherwise acts like a
    numpy.ndarray.

    Notes
    -----
    The wavelengths where this template is defined can be found in
    :class:`MUVWavelengthCenters`.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('muv_templates.npy')
        array = anc.load_dict()['co2p_fdb']
        return super().__new__(cls, array, anc.path)


class CO2PlusUltravioletDoublet(_AncillaryArray):
    """Create the CO:sub:2:sup:+: ultraviolet doublet template.

    This class will read in the template. It otherwise acts like a
    numpy.ndarray.

    Notes
    -----
    The wavelengths where this template is defined can be found in
    :class:`MUVWavelengthCenters`.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('muv_templates.npy')
        array = anc.load_dict()['co2p_uvd']
        return super().__new__(cls, array, anc.path)


class COCameronBands(_AncillaryArray):
    """Create the CO Cameron band system template.

    This class will read in the template. It otherwise acts like a
    numpy.ndarray.

    Notes
    -----
    The wavelengths where this template is defined can be found in
    :class:`MUVWavelengthCenters`.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('muv_templates.npy')
        array = anc.load_dict()['co_cameron_bands']
        return super().__new__(cls, array, anc.path)


class COPlus1NG(_AncillaryArray):
    """Create the CO:sup:+:1NG band system template.

    This class will read in the template. It otherwise acts like a
    numpy.ndarray.

    Notes
    -----
    The wavelengths where this template is defined can be found in
    :class:`MUVWavelengthCenters`.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('muv_templates.npy')
        array = anc.load_dict()['cop_1ng']
        return super().__new__(cls, array, anc.path)


class N2VergardKaplan(_AncillaryArray):
    """Create the N:sub:2:Vergard-Kaplan band system template.

    This class will read in the template. It otherwise acts like a
    numpy.ndarray.

    Notes
    -----
    The wavelengths where this template is defined can be found in
    :class:`MUVWavelengthCenters`.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('muv_templates.npy')
        array = anc.load_dict()['n2_vk']
        return super().__new__(cls, array, anc.path)


class NitricOxideNightglow(_AncillaryArray):
    """Create the nitric oxide nightglow template.

    This class will read in the template. It otherwise acts like a
    numpy.ndarray.

    Notes
    -----
    The wavelengths where this template is defined can be found in
    :class:`MUVWavelengthCenters`.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('muv_templates.npy')
        array = anc.load_dict()['no_nightglow']
        return super().__new__(cls, array, anc.path)


class SolarContinuum(_AncillaryArray):
    """Create the solar continuum template.

    This class will read in the template. It otherwise acts like a
    numpy.ndarray.

    Notes
    -----
    The wavelengths where this template is defined can be found in
    :class:`MUVWavelengthCenters`.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('muv_templates.npy')
        array = anc.load_dict()['solar_continuum']
        return super().__new__(cls, array, anc.path)


class MUVWavelengthCenters(_AncillaryArray):
    """Create the center wavelengths used in the mid-ultraviolet channel.

    This class reads in the center wavelengths. It otherwise acts like a
    numpy.ndarray.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('muv_wavelengths.npy')
        array = anc.load_dict()['wavelength_centers']
        return super().__new__(cls, array, anc.path)


class MUVWavelengthEdges(_AncillaryArray):
    """Create the edge wavelengths used in the mid-ultraviolet channel.

    This class reads in the edge wavelengths. It otherwise acts like a
    numpy.ndarray.

    """
    def __new__(cls):
        anc = _AncillaryFileLoader('muv_wavelengths.npy')
        array = anc.load_dict()['wavelength_edges']
        return super().__new__(cls, array, anc.path)
