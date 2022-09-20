import numpy as np
from scipy.io import readsav


def make_gain_correction(dds, spa_size, spe_size, integration_time, mcp_volt, mcp_gain):
    """

    Parameters
    ----------
    dds: np.ndarray
        The detector dark subtacted
    spa_size: int
        The number of detector pixels in a spatial bin
    spe_size: int
        The number of detector pixels in a spectral bin
    integration_time
    mcp_volt
    mcp_gain

    Returns
    -------

    """
    f = readsav('/home/kyle/repos/PyUVS/iuvs_nonlinear_gain_correction.sav')
    volt_array = f['volt_array']
    ab = f['ab_array']
    ref_mcp_gain = 50.909455

    normalized_img = dds / integration_time / spa_size / spe_size

    a = np.interp(mcp_volt, volt_array, ab[:, 0])
    b = np.interp(mcp_volt, volt_array, ab[:, 1])

    norm_img = np.exp(a + b * np.log(normalized_img))

    return norm_img / normalized_img * mcp_gain / ref_mcp_gain


if __name__ == '__main__':
    from pathlib import Path
    from astropy.io import fits
    import matplotlib.pyplot as plt
    orbit = 3464
    p = Path('/media/kyle/McDataFace/iuvsdata/production/orbit03400')
    files = sorted(p.glob(f'*apoapse*{orbit}*muv*r01*.gz'))

    hdul = fits.open(files[5])
    detds = hdul['detector_dark_subtracted'].data
    spectral_bin_width: int = int(np.median(hdul['binning'].data['spebinwidth'][0]))  # bins
    spatial_bin_width: int = int(np.median(hdul['binning'].data['spabinwidth'][0]))  # bins
    voltage: float = hdul['observation'].data['mcp_volt'][0]
    voltage_gain: float = hdul['observation'].data['mcp_gain'][0]
    integration_time: float = hdul['observation'].data['int_time'][0]

    corr = make_gain_correction(detds, spatial_bin_width, spectral_bin_width, integration_time, voltage, voltage_gain)
    print(np.median(np.median(corr, axis=0), axis=0))
    print(voltage, voltage_gain)
    fig, ax = plt.subplots()
    ax.imshow(corr[..., -1], vmin=1.16, vmax=1.17)
    plt.savefig('/home/kyle/iuvs/gain_corr.png')
