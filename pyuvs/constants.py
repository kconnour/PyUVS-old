"""Collection of constants and conversion factors relevant to MAVEN/IUVS.

Most are specific to the IUVS instrument, but some help with general photometric
calculations.

"""
import numpy as np

# Instrumental constants
# TODO: provide a reference
angular_slit_width: float = 10.64
"""Width of the slit [degrees]. """

# TODO: provide a reference
spatial_slit_width: float = 0.1
"""Width of the slit [mm]. """

# TODO: provide a reference
cmos_pixel_well_depth: int = 3400
"""Saturation level of an IUVS CMOS detector pixel [DN]. """

telescope_focal_length: int = 100
"""Focal length of the IUVS telescope mirror [mm]. """

# TODO: provide a reference
pixel_size: float = 0.023438
"""Size of an IUVS detector pixel [mm]. """

# TODO: provide a reference
pixel_omega: float = pixel_size / telescope_focal_length * \
                     spatial_slit_width / telescope_focal_length
"""Detector pixel angular dispersion along the slit. """

# Martian constants
mars_mass: float = 6.4171 * 10**23
"""The mass of Mars [kg]. This value come from the `Mars fact sheet
<https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html>`_."""

mars_mean_radius: float = 3389.5
"""The mean radius of Mars [km]. This value come from the `Mars fact sheet
<https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html>`_."""

# Physical constants
# TODO: check this one
kR: float = 10**9 / (4 * np.pi)
"""Definition of the kilorayleigh [photons/steradian]. """
