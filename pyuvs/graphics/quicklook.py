import matplotlib.pyplot as plt
import numpy as np
from pyuvs.graphics.color_transform import turn_primary_to_3_channels, \
    histogram_equalize_rgb_image
from pyuvs.swath import swath_number


if __name__ == '__main__':
    from pyuvs.data_files import L1bFile, \
        find_latest_apoapse_muv_file_paths_from_block
    from pathlib import Path

    # Read in data
    p = Path('/Volumes/Samsung_T5/IUVS_data')
    files = find_latest_apoapse_muv_file_paths_from_block(p, 3453)
    files = [L1bFile(f) for f in files]

    # Make data that I need
    primaries = np.vstack([f.primary for f in files])
    alts = np.vstack([f.pixel_geometry.tangent_altitude for f in files])
    amask = np.where(alts[..., 4] == 0, True, False)
    swaths = np.concatenate([f.integration.mirror_angle for f in files])
    print(swaths.shape)

    # Color transform
    rgbp = turn_primary_to_3_channels(primaries)
    rgb = histogram_equalize_rgb_image(rgbp, mask=amask)

    plt.imshow(rgb/255)
    plt.show()