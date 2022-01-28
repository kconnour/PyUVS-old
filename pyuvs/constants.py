"""Collection of constants and conversion factors relevant to the instrument.

"""

angular_slit_width: float = 10.64
"""Width of the slit [degrees]."""

spatial_slit_width: float = 0.1
"""Width of the slit [mm]."""

cmos_pixel_well_depth: int = 3400
"""Saturation level of an IUVS CMOS detector pixel [DN]."""

day_night_voltage_boundary: int = 790
"""Voltage defining the boundary between dayside and nightside settings."""

minimum_mirror_angle: float = 30.2508544921875
"""Minimum angle [degrees] the scan mirror can be."""

maximum_mirror_angle: float = 59.6502685546875
"""Maximum angle [degrees] the scan mirror can be."""

telescope_focal_length: int = 100
"""Focal length of the IUVS telescope mirror [mm]."""

pixel_size: float = 0.023438
"""Size of an IUVS detector pixel [mm]."""

pixel_omega: float = pixel_size / telescope_focal_length * \
                     spatial_slit_width / telescope_focal_length
"""Detector pixel angular dispersion along the slit."""