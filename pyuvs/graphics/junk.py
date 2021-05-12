from scipy.io import readsav
import numpy as np
a = readsav('/home/kyle/Downloads/jeremy_topology_maps.sav', verbose=True)
o = a['open']
c = a['closed']

np.save('/home/kyle/repos/pyuvs/aux/magnetic_field_open_probability', o)
np.save('/home/kyle/repos/pyuvs/aux/magnetic_field_closed_probability', c)