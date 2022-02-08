"""
Apoapse dayside image
=====================

Create a histogram equalized dayside image from data files.

"""
from pathlib import Path
from pyuvs.graphics.standard_products import make_dayside_segment_detector_image

orbit = 3453
data_path = Path('/media/kyle/Samsung_T5/IUVS_data')
sl = f'/home/kyle/ql_testing/segment-quicklook-orbit{orbit}.pdf'
make_dayside_segment_detector_image(orbit, data_path, sl)
