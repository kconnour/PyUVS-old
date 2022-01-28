from pathlib import Path
import numpy as np


def get_package_path() -> Path:
    return Path(__file__).parent.resolve()


def get_muv_template_filepath() -> Path:
    return get_package_path() / 'anc' / 'muv_templates.npy'


def load_muv_templates() -> dict:
    file_path = get_muv_template_filepath()
    return np.load(file_path, allow_pickle=True).item()


def load_no_nightglow_template() -> np.ndarray:
    return load_muv_templates()['no_nightglow']


def load_midhires_flatfield() -> np.ndarray:
    file_path = get_package_path() / 'anc' / 'mvn_iuv_flatfield.npy'
    return np.load(file_path, allow_pickle=True).item()['flatfield']


if __name__ == '__main__':
    import matplotlib.pyplot as plt
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

    plt.savefig('/home/kyle/ql_testing/ff_ratio.png', dpi=300)