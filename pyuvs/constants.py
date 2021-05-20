"""Collection of constants relevant to MAVEN/IUVS.

Most are specific to the IUVS instrument, but some help with general photometric
calculations.

"""
import numpy as np

# Instrumental constants
angular_slit_width: float = 10.64
""" Width of the slit [degrees]. """

cmos_pixel_well_depth: int = 3400
""" Saturation level of an IUVS CMOS detector [DN]. """

focal_length: float = 100.0
""" Focal length of the IUVS telescope mirror [mm]. """

pixel_size: float = 0.023438
""" Size of an IUVS detector pixel [mm]. """

spatial_slit_width: float = 0.1
""" Width of the slit [mm]. """

pixel_omega: float = pixel_size / focal_length * \
                     spatial_slit_width / focal_length
""" Detector pixel angular dispersion along the slit. """

# Physical constants
kR: float = 10**9 / (4 * np.pi)
""" Definition of the kilorayleigh [photons/steradian]. """

# Martian constants
mars_mass: float = 6.4171 * 10**23
""" The mass of Mars [kg]. """

mars_mean_radius: float = 3389.5
""" The mean radius of Mars [km]. """
