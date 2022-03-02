import cartopy.crs as ccrs
import numpy as np
from shapely.geometry.polygon import LinearRing

import pyuvs.spice


def rotated_globe(rotated_polar_lat, rotated_polar_lon, sublon):
    # calculate a RotatedPole transform for the rotated pole position
    transform = ccrs.RotatedPole(pole_latitude=rotated_polar_lat,
                                 pole_longitude=rotated_polar_lon,
                                 central_rotated_longitude=0)

    # transform the viewer (0,0) point
    tcoords = transform.transform_point(0, 0, ccrs.PlateCarree())

    # find the angle by which the planet needs to be rotated about it's rotated polar axis and calculate a new
    # RotatedPole transform including this angle rotation
    rot_ang = sublon - tcoords[0]
    transform = ccrs.RotatedPole(pole_latitude=rotated_polar_lat,
                                 pole_longitude=rotated_polar_lon,
                                 central_rotated_longitude=rot_ang)
    return transform


def highres_NearsidePerspective(projection, altitude, r=3400 * 1e3):
    """
    Increases the resolution of the circular outline in cartopy.crs.NearsidePerspective projection.

    Parameters
    ----------
    projection : obj
        A cartopy.crs.NearsidePerspective() projection.
    altitude : int, float
        Apoapse altitude in meters.
    r : float
        The radius of the globe in meters (e.g., for Mars this is the radius of Mars in meters).

    Returns
    -------
    None. Changes the resolution of an existing projection.
    """

    # re-implement the cartopy code to figure out the new boundary shape
    a = np.float(projection.globe.semimajor_axis or r)
    h = np.float(altitude)
    max_x = a * np.sqrt(h / (2 * a + h))
    t = np.linspace(0, 2 * np.pi, 3601)
    coords = np.vstack([max_x * np.cos(t), max_x * np.sin(t)])[:, ::-1]

    # update the projection boundary
    projection._boundary = LinearRing(coords.T)


def highres_Orthographic(projection, r=3400 * 1e3):
    """
    Increases the resolution of the circular outline in cartopy.crs.Orthographic projection.

    Parameters
    ----------
    projection : obj
        A cartopy.crs.Orthographic() projection.
    r : float
        The radius of the globe in meters (e.g., for Mars this is the radius of Mars in meters).

    Returns
    -------
    None. Changes the resolution of an existing projection.
    """

    # re-implement the cartopy code to figure out the new boundary shape
    a = np.float(projection.globe.semimajor_axis or r)
    b = np.float(projection.globe.semiminor_axis or a)
    t = np.linspace(0, 2 * np.pi, 3601)
    coords = np.vstack([a * 0.99999 * np.cos(t), b * 0.99999 * np.sin(t)])[:, ::-1]

    # update the projection boundary
    projection._boundary = LinearRing(coords.T)


def make_apoapse_globe(et):


def make_rotated_apoapse_globe():
    pass


if __name__ == '__main__':
    from datetime import datetime
    from pathlib import Path
    p = Path('/media/kyle/Samsung_T5/IUVS_data/spice')
    sp = pyuvs.spice.Spice(p)
    sp.load_spice()
    sp.find_all_maven_apsis_et('apoapse', endtime=datetime(2020, 1, 1))


