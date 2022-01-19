"""Collection of constants and conversion factors relevant to MAVEN/IUVS.

Most are specific to the IUVS instrument, but some help with general photometric
calculations.

"""
import datetime
import numpy as np

# Instrumental constants
# TODO: provide a reference
angular_slit_width: float = 10.64
"""Width of the slit [degrees]."""

# TODO: provide a reference
spatial_slit_width: float = 0.1
"""Width of the slit [mm]."""

# TODO: provide a reference
cmos_pixel_well_depth: int = 3400
"""Saturation level of an IUVS CMOS detector pixel [DN]."""

telescope_focal_length: int = 100
"""Focal length of the IUVS telescope mirror [mm]."""

# TODO: provide a reference
pixel_size: float = 0.023438
"""Size of an IUVS detector pixel [mm]."""

# TODO: provide a reference
pixel_omega: float = pixel_size / telescope_focal_length * \
                     spatial_slit_width / telescope_focal_length
"""Detector pixel angular dispersion along the slit."""

# Operational constants
science_start_date: datetime.date = datetime.date(2014, 11, 11)
"""Date MAVEN began performing nominal science."""

pre_wizard_end_date = datetime.date(2021, 6, 7)
"""Last date of nominal science before wizard-ops."""

post_wizard_start_date = datetime.date(2021, 6, 10)
"""First date of nominal science after wizard-ops."""

# Martian physical constants
mars_mass: float = 6.4171 * 10**23
"""The mass of Mars [kg]. This value comes from the `Mars fact sheet
<https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html>`_."""

mars_mean_radius: float = 3389.5
"""The mean radius of Mars [km]. This value comes from the `Mars fact sheet
<https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html>`_."""

# Martian temporal constants
martian_sol_length: float = 24.6597
"""Length of a Martian sol [hours]. This value comes from the `Mars fact sheet
<https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html>`_."""

seconds_per_sol: float = martian_sol_length / 24 * 86400
"""Number of seconds per Martian sol."""

sols_per_martian_year: float = 686.973 * 24 / martian_sol_length
"""Number of sols per Martian year."""

date_of_start_of_mars_year_0: datetime.datetime = \
    datetime.datetime(1953, 5, 24, 11, 57, 7)
"""Time of the start of Mars year 0. This value comes from `this article
<https://doi.org/10.1016/j.icarus.2014.12.014>`_."""

# Martian locations
arsia_mons_coordinates: tuple[float, float] = (-8.35, 239.91)
"""Location of the center of Arsia Mons (degrees N, degrees E)."""

ascraeus_mons_coordinates: tuple[float, float] = (11.92, 255.92)
"""Location of the center of Ascraeus Mons (degrees N, degrees E)."""

gale_crater_coordinates: tuple[float, float] = (-5.24, 127.48)
"""Location of the center of Gale crater (degrees N, degrees E)."""

olympus_mons_coordinates: tuple[float, float] = (18.39, 226.12)
"""Location of the center of Olympus Mons (degrees N, degrees E)."""

pavonis_mons_coordinates: tuple[float, float] = (1.48, 247.04)
"""Location of the center of Pavonis Mons (degrees N, degrees E)."""

# Physical constants
# TODO: check this one
kR: float = 10**9 / (4 * np.pi)
"""Definition of the kilorayleigh [photons/steradian]."""
