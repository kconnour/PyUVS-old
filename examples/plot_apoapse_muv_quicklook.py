"""
Apoapse MUV quicklook
=====================

Create a standard apoapse MUV quicklook.

"""
from pathlib import Path
from pyuvs.graphics.standard_products import make_apoapse_muv_quicklook

orbit = 13000
data_path = Path('/media/kyle/T7/IUVS_data')
sl = f'/home/kyle/ql_testing/apoapse-muv-quicklook-orbit{orbit}.pdf'
make_apoapse_muv_quicklook(orbit, data_path, sl)
