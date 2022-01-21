import numpy as np
from astropy.io import fits
from skimage.exposure import equalize_hist
import matplotlib.pyplot as plt


'''import glob
files = sorted(glob.glob('/media/kyle/Samsung_T5/IUVS_data/orbit03400/*apoapse*3453*muv*'))

primary = []
alt = []
for f in files:
    hdul = fits.open(f)
    pr = hdul['primary'].data
    al = hdul['pixelgeometry'].data['pixel_corner_mrh_alt']
    primary.append(pr)
    alt.append(al)

foo = np.vstack(primary)
bar = np.vstack(alt)
np.save('/home/kyle/primary3453.npy', foo)
np.save('/home/kyle/alt3453.npy', bar)'''


class FalseColorDetectorImage:
    def __init__(self, primary: np.ndarray):
        self.primary = primary
        self.rgb = None

    def split_primary_into_rgb_channels(self):
        n_spectral_bins = self.primary.shape[-1]
        blue_green_cutoff = int(n_spectral_bins / 3)
        green_red_cutoff = int(n_spectral_bins * 2 / 3)
        red = np.sum(self.primary[:, :, green_red_cutoff:], axis=-1)
        green = np.sum(self.primary[:, :, blue_green_cutoff: green_red_cutoff], axis=-1)
        blue = np.sum(self.primary[:, :, :blue_green_cutoff], axis=-1)
        return np.dstack([red, green, blue])

    def histogram_equalize(self, mask=None):
        coadded_primary = self.split_primary_into_rgb_channels()
        red = equalize_hist(coadded_primary[:, :, 0], mask=mask)
        green = equalize_hist(coadded_primary[:, :, 1], mask=mask)
        blue = equalize_hist(coadded_primary[:, :, 2], mask=mask)
        self.rgb = np.dstack([red, green, blue])


def histogram_equalize_grayscale_image(image: np.ndarray, mask: np.ndarray = None) -> np.ndarray:
    """Histogram equalize a grayscale image.

    This applies a histogram equalization algorithm to the input image. The
    image can have any shape, though it doesn't make much sense unless it is
    2D.

    Parameters
    ----------
    image
        The image to histogram equalize.
    mask
        A mask of booleans where :code:`False` values are excluded from the
        histogram equalization scaling. This must be the same shape as
        :code:`image`.

    Returns
    -------
    Histogram equalized values ranging from 0 to 255.

    See Also
    --------
    histogram_equalize_rgb_image: Histogram equalize a 3-color channel image.

    Notes
    -----
    I could not get the scikit-learn algorithm to work so I created this.

    The algorithm works like this:

    1. Sort all data used in the coloring.
    2. Use these sorted values to determine the 256 left bin cutoffs.
    3. Linearly interpolate each value in the grid over 256 RGB values and the
       corresponding data values.
    4. Take the floor of the interpolated values since I'm using left cutoffs.

    """
    sorted_values = np.sort(image[mask], axis=None)
    left_cutoffs = np.array([sorted_values[int(i / 256 * len(sorted_values))]
                             for i in range(256)])
    rgb = np.linspace(0, 255, num=256)
    return np.floor(np.interp(image, left_cutoffs, rgb))


def histogram_equalize_rgb_image(image: np.ndarray, mask: np.ndarray = None) -> np.ndarray:
    """Histogram equalize an RGB image.

    This applies a histogram equalization algorithm to the input image. The
    RGB dimension is assumed to be the last dimension and should have a length
    of 3. Indices 0, 1, and 2 correspond to R, G, and B, respectively. The
    input image can be any shape, though it doesn't make much sense unless it
    is 3D.

    Parameters
    ----------
    image
        The image to histogram equalize.
    mask
        A mask of booleans where :code:`False` values are excluded from the
        histogram equalization scaling. This must be the same shape as the
        first N-1 dimensions of :code:`image`.

    Returns
    -------
    Histogram equalized values ranging from 0 to 255.

    See Also
    --------
    histogram_equalize_grayscale_image: Histogram equalize a 1-color channel
    image.

    """
    red = histogram_equalize_grayscale_image(image[..., 0], mask=mask)
    green = histogram_equalize_grayscale_image(image[..., 1], mask=mask)
    blue = histogram_equalize_grayscale_image(image[..., 2], mask=mask)
    return np.dstack([red, green, blue])


if __name__ == '__main__':
    primary3453 = np.load('/home/kyle/primary3453.npy')  # (2914, 133, 19)  387562
    alt3453 = np.load('/home/kyle/alt3453.npy')[:, :, -1]  # (2914, 133)
    altmask = np.where(alt3453 == 0, True, False)

    r = np.sum(primary3453[:, :, 13:], axis=-1)
    g = np.sum(primary3453[:, :, 6:13], axis=-1)
    b = np.sum(primary3453[:, :, :6], axis=-1)
    rgb = np.dstack([r, g, b])

    rgb = histogram_equalize_rgb_image(rgb, altmask)

    plt.imshow(rgb/255)
    plt.savefig('/home/kyle/rgb.png', dpi=300)
