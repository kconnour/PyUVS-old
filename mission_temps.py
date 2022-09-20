from pathlib import Path
from pyuvs.datafiles import find_latest_apoapse_muv_file_paths_from_block
import matplotlib.pyplot as plt
from astropy.io import fits


if __name__ == '__main__':
    p = Path('/media/kyle/McDataFace/iuvsdata/production')
    #fig, ax = plt.subplots(10, 10)
    plasma = plt.get_cmap('plasma')

    for i in range(8, 17):
        for j in range(10):
            fig, ax = plt.subplots()
            for orbit in range(100):
                o = i*1000 + j*100 + orbit
                print(o)
                files = find_latest_apoapse_muv_file_paths_from_block(p, o)
                for c, f in enumerate(files):
                    if len(files) == 1:
                        continue
                    hdul = fits.open(f)
                    integ = hdul['integration'].data
                    et = integ['et']
                    case_temp = integ['case_temp_c']
                    det_temp = integ['det_temp_c']

                    #ax.plot(et, case_temp, label='Case temp', color='k')
                    ax.plot(et, det_temp, label='Det temp', color=plasma.colors[int((c / (len(files)-1 )*255))])
                    #plt.legend()
            ax.set_ylim(-25, -15)
            foo = i*1000 + j*100
            foo = str(foo).zfill(5)
            plt.savefig(f'/home/kyle/iuvs/temperatures{foo}.png')
            plt.close(fig)
