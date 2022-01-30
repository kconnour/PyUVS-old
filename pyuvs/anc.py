"""This module provides functions to load in standard dictionaries and arrays
for working with IUVS data."""
from pathlib import Path
import numpy as np

# delta bands: 1.7822 "detector"
# gamma bands: 1.0698 (for v0) "detector"
# epsilon bands: None
# take DN template where highest value is 1, multiply by above values, add them together, then renormalize


def _load_numpy_dict(file_path: Path) -> dict:
    return np.load(file_path, allow_pickle=True).item()


def get_package_path() -> Path:
    """Get the path of the PyUVS package.

    Returns
    -------
    Path
        Path of the package.

    Examples
    --------
    >>> import pyuvs as pu
    >>> pu.anc.get_package_path()
    PosixPath('/home/kyle/repos/PyUVS/pyuvs')

    """
    return Path(__file__).parent.resolve()


def load_magnetic_field_closed_probability() -> np.ndarray:
    """Load the map denoting the probability of a closed magnetic field line.

    Returns
    -------
    np.ndarray
        Array of the image.

    Notes
    -----
    The shape of this array is (180, 360).

    * The 0 :sup:`th` axis corresponds to latitude and spans -90 to 90 degrees.
    * The 1 :sup:`st` axis corresponds to east longitude and spans 0 to 360
      degrees.

    This map comes from MGS data.

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       b_field = pu.anc.load_magnetic_field_closed_probability()
       plt.imshow(b_field, cmap='Blues_r', origin='lower')
       plt.show()

    """
    file_path = get_package_path() / 'anc' / \
                'magnetic_field_closed_probability_map.npy'
    return np.load(file_path)


def load_magnetic_field_open_probability() -> np.ndarray:
    """Load the map denoting the probability of an open magnetic field line.

    Returns
    -------
    np.ndarray
        Array of the image.

    Notes
    -----
    The shape of this array is (180, 360).

    * The 0 :sup:`th` axis corresponds to latitude and spans -90 to 90 degrees.
    * The 1 :sup:`st` axis corresponds to east longitude and spans 0 to 360
      degrees.

    This map comes from MGS data.

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       b_field = pu.anc.load_magnetic_field_open_probability()
       plt.imshow(b_field, cmap='Blues_r', origin='lower')
       plt.show()

    """
    file_path = get_package_path() / 'anc' / \
                'magnetic_field_open_probability_map.npy'
    return np.load(file_path)


def load_mars_surface_map() -> np.ndarray:
    """Load the Mars surface map.

    Returns
    -------
    np.ndarray
        Array of the image.

    Notes
    -----
    The shape of this array is (1800, 3600, 4).

    * The 0 :sup:`th` axis corresponds to latitude and spans 90 to -90 degrees.
    * The 1 :sup:`st` axis corresponds to east longitude and spans 0 to 360
      degrees.
    * The 2 :sup:`nd` axis is the RGBA channel.

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       surface_map = pu.anc.load_mars_surface_map()
       plt.imshow(surface_map)
       plt.show()

    """
    file_path = get_package_path() / 'anc' / 'mars_surface_map.npy'
    return np.load(file_path)


def load_muv_templates() -> dict:
    """Load all the MUV spectral templates.

    Returns
    -------
    dict
        All the included MUV templates.

    Examples
    --------
    Get the dictionary keys:

    >>> import pyuvs as pu
    >>> pu.anc.load_muv_templates().keys()
    dict_keys(['co2p_fdb', 'co2p_uvd', 'co_cameron_bands', 'cop_1ng', 'n2_vk', 'no_nightglow', 'o2972', 'solar_continuum'])

    """
    file_path = get_package_path() / 'anc' / 'muv_templates.npy'
    return _load_numpy_dict(file_path)


def load_co2p_fdb_template() -> np.ndarray:
    """Load the MUV CO :sub:`2` :sup:`+` FDB (Fox-Duffendack-Barker) template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_co2p_fdb_template()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return load_muv_templates()['co2p_fdb']


def load_co2p_uvd_template() -> np.ndarray:
    """Load the MUV CO :sub:`2` :sup:`+` UVD (ultraviolet doublet) template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_co2p_uvd_template()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return load_muv_templates()['co2p_uvd']


def load_co_cameron_band_template() -> np.ndarray:
    """Load the MUV CO Cameron band template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_co_cameron_band_template()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return load_muv_templates()['co_cameron_bands']


def load_cop_1ng_template() -> np.ndarray:
    """Load the MUV CO :sup:`+` 1NG (first negative) template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_cop_1ng_template()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return load_muv_templates()['cop_1ng']


def load_n2_vk_template() -> np.ndarray:
    """Load the MUV N :sub:`2` VK (Vegard-Kaplan) template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_n2_vk_template()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return load_muv_templates()['n2_vk']


def load_no_nightglow_template() -> np.ndarray:
    """Load the MUV NO nightglow template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_no_nightglow_template()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return load_muv_templates()['no_nightglow']


def load_oxygen_2972_template() -> np.ndarray:
    """Load the MUV oxygen 297.2 nm template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_oxygen_2972_template()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return load_muv_templates()['o2972']


def load_solar_continuum_template() -> np.ndarray:
    """Load the MUV solar continuum template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.anc.load_solar_continuum_template()
       wavelengths = pu.anc.load_muv_wavelength_center()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')
       plt.show()

    """
    return load_muv_templates()['solar_continuum']


def load_muv_wavelengths() -> dict:
    """Load all the MUV wavlengths.

    Returns
    -------
    dict
        All the included MUV wavelengths.

    Examples
    --------
    Get the dictionary keys:

    >>> import pyuvs as pu
    >>> pu.anc.load_muv_wavelengths().keys()
    dict_keys(['wavelength_centers', 'wavelength_edges'])

    """
    file_path = get_package_path() / 'anc' / 'muv_wavelengths.npy'
    return _load_numpy_dict(file_path)


def load_muv_wavelength_center() -> np.ndarray:
    """Load the MUV wavelength center.

    Returns
    -------
    np.ndarray
        Array of the center MUV wavelengths.

    Notes
    -----
    The shape of this array is (1024,).

    """
    return load_muv_wavelengths()['wavelength_centers']


def load_muv_wavelength_edge() -> np.ndarray:
    """Load the MUV wavelength edge.

    Returns
    -------
    np.ndarray
        Array of the edge MUV wavelengths.

    Notes
    -----
    The shape of this array is (1025,).

    """
    return load_muv_wavelengths()['wavelength_edges']







def load_midhires_flatfield_data() -> dict:
    file_path = get_package_path() / 'anc' / 'mvn_iuv_flatfield.npy'
    return _load_numpy_dict(file_path)


def load_midhires_flatfield() -> np.ndarray:
    return load_midhires_flatfield_data()['flatfield']


def load_midhires_flatfield_wavelengths() -> np.ndarray:
    return load_midhires_flatfield_data()['wavelengths']


if __name__ == '__main__':
    pass
    '''import matplotlib.pyplot as plt
    from scipy.io import readsav
    #from pyuvs

    fig, ax = plt.subplots(2, 3)
    a = load_midhires_flatfield()

    # REscale FF
    master = np.zeros((50, 19))
    for i in range(19):
        foo = np.linspace(0, 132, num=50)
        bar = np.linspace(0, 132, num=133)
        master[:, i] = np.interp(foo, bar, a[:, i])

    flatfields = ['MIDRESAPO_FLATFIELD_19X50_ORBIT03733_3739.sav',
                  'MIDRESAPO_FLATFIELD_19X50_ORBIT03744_3750.sav']

    before = readsav(f'/home/kyle/ql_testing/{flatfields[0]}')['midresapo_flatfield_19x50_orbit03733_3739']
    after = readsav(f'/home/kyle/ql_testing/{flatfields[1]}')['midresapo_flatfield_19x50_orbit03744_3750']

    cmap = 'inferno'

    ax[0, 0].imshow(np.flipud(after/before), cmap=cmap, vmin=0.9, vmax=1.1)
    ax[0, 0].set_title('after/before')
    ax[0, 1].imshow(np.flipud(before/master), cmap=cmap, vmin=0.9, vmax=1.1)
    ax[0, 1].set_title('before/master')
    ax[0, 2].imshow(np.flipud(after/master), cmap=cmap, vmin=0.9, vmax=1.1)
    ax[0, 2].set_title('after/master')

    ax[1, 0].imshow(np.flipud(after - before), cmap=cmap, vmin=-0.08, vmax=0.08)
    ax[1, 0].set_title('after - before')
    ax[1, 1].imshow(np.flipud(before - master), cmap=cmap, vmin=-0.08, vmax=0.08)
    ax[1, 1].set_title('before - master')
    ax[1, 2].imshow(np.flipud(after - master), cmap=cmap, vmin=-0.08, vmax=0.08)
    ax[1, 2].set_title('after - master')

    print(after-before)

    plt.savefig('/home/kyle/ql_testing/ff_ratio.png', dpi=300)'''