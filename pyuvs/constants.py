"""Collection of constants. Most are specific to the IUVS instrument, but some
help with general photometric calculations.

Attributes
----------
angular_slit_width: float
    Width of the slit [degrees].
cmos_pixel_well_depth: int
    Saturation level of an IUVS CMOS detector [DN].
focal_length: int
    Focal length of the IUVS telescope mirror [mm].
kR: float
    Definition of the kilorayleigh [photons/steradian].
pixel_omega: float
    Detector pixel angular dispersion along the slit.
pixel_size: float
    Size of an IUVS detector pixel [mm].
spatial_slit_width: float
    Width of the slit [mm].

"""
import numpy as np

angular_slit_width = 10.64
cmos_pixel_well_depth = 3400
focal_length = 100
kR = 10**9 / (4 * np.pi)
pixel_size = 0.023438
spatial_slit_width = 0.1
pixel_omega = pixel_size / focal_length * spatial_slit_width / focal_length
