from pyuvs.files import FileFinder
from pyuvs.data_contents import IUVSDataContents, L1bDataContents
from pyuvs.geography import Geography
import numpy as np


g = Geography()
ff = FileFinder('/media/kyle/Samsung_T5/IUVS_data')
gale = []
for f in range(7200, 7400):
    try:
        files = ff.soschob(f)
    except ValueError:
        continue
    inorb = []
    for i in files.abs_paths:
        l1bc = L1bDataContents(i)
        inorb.append(g.location_in_file(l1bc, g.locations['gale_crater']))
    print(any(inorb))
    gale.append(any(inorb))

a = np.array(gale, dtype=bool)
np.save('/home/kyle/gale.npy', a)
