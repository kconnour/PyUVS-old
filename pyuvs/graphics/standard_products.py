from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from pyuvs.constants import angular_slit_width, minimum_mirror_angle, maximum_mirror_angle
from pyuvs.spectra import fit_muv_templates_to_nightside_data
from pyuvs.swath import swath_number
from pyuvs.utils import set_bad_pixels_to_nan
from pyuvs.datafiles.path import find_latest_apoapse_muv_file_paths_from_block
from pyuvs.datafiles.contents import L1bFileCollection, L1bFile
from pyuvs.graphics.colorize import histogram_equalize_detector_image
from pyuvs.graphics.detector_image import make_swath_grid, pcolormesh_detector_image, pcolormesh_rgb_detector_image
from pyuvs.graphics.templates import ApoapseMUVQuicklook, SegmentDetectorImage
from pyuvs import load_flatfield_mid_res_no_app_flip, load_flatfield_mid_res_app_flip, load_flatfield_mid_hi_res_update, load_flatfield_mid_hi_res_my34gds
import cartopy.crs as ccrs
import psycopg


def checkerboard():
    """
    Create an 5-degree-size RGB checkerboard array for display with matplotlib.pyplot.imshow().

    Parameters
    ----------
    None.

    Returns
    -------
    grid : array
        The checkerboard grid.
    """

    # make and transpose the grid (don't ask how it's done)
    grid = np.repeat(np.kron([[0.67, 0.33] * 36, [0.33, 0.67] * 36] * 18, np.ones((5, 5)))[:, :, None], 3, axis=2)

    # return the array
    return grid


def latlon_meshgrid(latitude, longitude, altitude):
    # make meshgrids to hold latitude and longitude grids for pcolormesh display
    X = np.zeros((latitude.shape[0] + 1, latitude.shape[1] + 1))
    Y = np.zeros((longitude.shape[0] + 1, longitude.shape[1] + 1))
    mask = np.ones((latitude.shape[0], latitude.shape[1]))

    # loop through pixel geometry arrays
    for i in range(int(latitude.shape[0])):
        for j in range(int(latitude.shape[1])):

            # there are some pixels where some of the pixel corner longitudes are undefined
            # if we encounter one of those, set the data value to missing so it isn't displayed
            # with pcolormesh
            if np.size(np.where(np.isfinite(longitude[i, j]))) != 5:
                mask[i, j] = np.nan

            # also mask out non-disk pixels
            if altitude[i, j] != 0:
                mask[i, j] = np.nan

            # place the longitude and latitude values in the meshgrids
            X[i, j] = longitude[i, j, 1]
            X[i + 1, j] = longitude[i, j, 0]
            X[i, j + 1] = longitude[i, j, 3]
            X[i + 1, j + 1] = longitude[i, j, 2]
            Y[i, j] = latitude[i, j, 1]
            Y[i + 1, j] = latitude[i, j, 0]
            Y[i, j + 1] = latitude[i, j, 3]
            Y[i + 1, j + 1] = latitude[i, j, 2]

    # set any of the NaN values to zero (otherwise pcolormesh will break even if it isn't displaying the pixel).
    X[np.where(~np.isfinite(X))] = 0
    Y[np.where(~np.isfinite(Y))] = 0

    # set to domain [-180,180)
    X[np.where(X > 180)] -= 360

    # return the coordinate arrays and the mask
    return X, Y


def make_dayside_segment_detector_image(orbit: int, data_location: Path, saveloc: str, figheight=6):
    """Make an image of a dayside detector image.

    Parameters
    ----------
    orbit
    data_location
    saveloc
    figheight

    Returns
    -------

    """
    # Load in the data
    data_paths = find_latest_apoapse_muv_file_paths_from_block(data_location, orbit)
    files = [L1bFile(f) for f in data_paths]
    fc = L1bFileCollection(files)

    # Load in my slit correction test
    #slit = np.load('/home/kyle/iuvs/slit/slit_correction.npy')
    #slit = np.load('/home/kyle/iuvs/slit/slit_correction_3points.npy')

    # Make data that's independent of day/night
    fov = fc.stack_field_of_view()
    swath_numbers = swath_number(fov)
    fc.make_daynight_integration_mask()
    dayside_integration_mask = fc.make_daynight_integration_mask()
    sza = fc.stack_daynight_solar_zenith_angle()

    template = SegmentDetectorImage(swath_numbers[-1] + 1, figheight)

    # Do the day/night stuff
    fc.dayside = True
    for daynight in [True, False]:
        if daynight not in dayside_integration_mask:
            continue

        primary = fc.stack_daynight_calibrated_detector_image()
        on_disk_mask = fc.make_daynight_on_disk_mask()
        daynight_mask = dayside_integration_mask == daynight
        daynight_fov = fov[daynight_mask]
        daynight_swath_number = swath_numbers[daynight_mask]
        n_spatial_bins = primary.shape[1]

        # Hack for geometry-free data
        if np.sum(on_disk_mask) == 0:
            print('No on disk data')
            on_disk_mask[:] = True

        if daynight:
            #primary = primary[:, :, :-1] / np.flipud(load_flatfield_mid_res_app_flip())
            #primary = primary# * slit
            sbins = primary.shape[-1]
            primary = primary / load_flatfield_mid_hi_res_my34gds()[:, :sbins]    # 14 spectral bins?
            rgb_primary = histogram_equalize_detector_image(primary, mask=np.logical_and(np.logical_and((sza <= 180), on_disk_mask), (sza >= 90))) / 255
            #rgb_primary = histogram_equalize_detector_image(primary, mask=np.logical_and((sza <= 102), on_disk_mask)) / 255
        else:
            dds = fc.stack_detector_image_dark_subtracted()
            dn_unc = fc.stack_detector_image_random_uncertainty_dn()
            file = fc.get_first_nightside_file()

            spbw = int(np.median(file.binning.spectral_pixel_bin_width))
            ssi = int(file.binning.spectral_pixel_bin_width[0] / spbw)
            spapbw = int(np.median(file.binning.spatial_pixel_bin_width))
            ww = np.median(file.observation.wavelength_width)
            vg = file.observation.voltage_gain
            it = file.observation.integration_time

            brightnesses = fit_muv_templates_to_nightside_data(
                dds, dn_unc, ww, spapbw, spbw, ssi, vg, it)
            no_kR = brightnesses[0, ...]
            aurora_kR = brightnesses[1, ...]

        for swath in np.unique(swath_numbers):
            # Do this no matter if I'm plotting primary or angles
            swath_inds = daynight_swath_number == swath
            n_integrations = np.sum(swath_inds)
            x, y = make_swath_grid(daynight_fov[swath_inds], swath,
                                   n_spatial_bins, n_integrations)

            # Plot the primary for dayside data
            if daynight:
                pcolormesh_rgb_detector_image(template.data_axis,
                                              rgb_primary[swath_inds], x, y)
            else:
                pcolormesh_detector_image(template.data_axis,
                    no_kR[swath_inds], x, y)#,
                    #cmap=template.no_colormap,
                    #norm=template.no_norm)

    template.data_axis.set_xlim(0, angular_slit_width * (swath_numbers[-1] + 1))
    template.data_axis.set_ylim(minimum_mirror_angle * 2, maximum_mirror_angle * 2)
    template.data_axis.set_xticks([])
    template.data_axis.set_yticks([])
    template.data_axis.set_facecolor('k')
    plt.savefig(saveloc)


def make_apoapse_muv_globe(orbit: int, data_location: Path, saveloc: str) -> None:
    """Make an image of a dayside detector image.

    Parameters
    ----------
    orbit
    data_location
    saveloc
    figheight

    Returns
    -------

    """
    # Load in the data
    data_paths = find_latest_apoapse_muv_file_paths_from_block(data_location, orbit)
    files = [L1bFile(f) for f in data_paths]
    fc = L1bFileCollection(files)

    # Make data that's independent of day/night
    fov = fc.stack_field_of_view()
    swath_numbers = swath_number(fov)
    fc.make_daynight_integration_mask()
    dayside_integration_mask = fc.make_daynight_integration_mask()

    # DB query
    with psycopg.connect(host='localhost', dbname='iuvs', user='kyle',
                         password='iuvs') as connection:
        # I still need Mars year, Sol
        # Open a cursor for db operations
        with connection.cursor() as cursor:
            cursor.execute(f"select subspacecraft_latitude, subspacecraft_longitude, subspacecraft_altitude from apoapse where orbit = {orbit}")
            sub_sc_lat, sub_sc_lon, sub_sc_alt = cursor.fetchall()[0]

    # Setup the graphic
    rmars = 3400
    fig = plt.figure(figsize=(6, 6), facecolor='w')
    globe = ccrs.Globe(semimajor_axis=rmars * 1e3, semiminor_axis=rmars * 1e3)
    projection = ccrs.NearsidePerspective(central_latitude=sub_sc_lat, central_longitude=sub_sc_lon, satellite_height=sub_sc_alt * 10 ** 3, globe=globe)
    transform = ccrs.PlateCarree(globe=globe)
    globe_ax = plt.axes(projection=projection)

    checkerboard_surface = checkerboard() * 0.1
    globe_ax.imshow(checkerboard_surface, transform=transform, extent=[-180, 180, -90, 90])

    plt.savefig(saveloc)
    plt.close(fig)
    raise SystemExit(9)

    # Do the slit correction
    '''old_slit = np.load('/home/kyle/iuvs/slit/slit_correction_3points.npy')
    foo = np.linspace(0, 1, num=50)
    bar = np.linspace(0, 1, num=133)
    new_slit = np.zeros((133, 19))
    for i in range(19):
        new_slit[:, i] = np.interp(bar, foo, old_slit[:, i])'''

    # Do the day/night stuff
    fc.dayside = True
    for daynight in [True]:
        if daynight not in dayside_integration_mask:
            continue
        primary = fc.stack_daynight_calibrated_detector_image()
        latitude = fc.stack_daynight_latitude()
        longitude = fc.stack_daynight_longitude()
        altitude = fc.stack_daynight_altitude_center()
        on_disk_mask = fc.make_daynight_on_disk_mask()
        daynight_swath_number = swath_numbers[dayside_integration_mask == daynight]

        if daynight:
            # Flatfield correct
            #primary = primary[:, :, :-1] / np.flipud(load_flatfield_mid_res_app_flip())
            primary = primary / load_flatfield_mid_hi_res_update()
            #sbins = primary.shape[-1]
            #primary = primary / load_flatfield_mid_hi_res_my34gds()[:, :sbins]    # 14 spectral bins?
            rgb_primary = histogram_equalize_detector_image(primary, mask=on_disk_mask) / 255

        for swath in np.unique(swath_numbers):
            # Do this no matter if I'm plotting primary or angles
            swath_inds = daynight_swath_number == swath

            primary_slice = rgb_primary[swath_inds]

            x, y = latlon_meshgrid(latitude[swath_inds], longitude[swath_inds], altitude[swath_inds])

            # Plot the primary for dayside data
            fill = primary_slice[:, :, 0]
            colors = np.reshape(primary_slice, (primary_slice.shape[0] * primary_slice.shape[1], primary_slice.shape[2]))
            globe_ax.pcolormesh(x, y, fill, color=colors, linewidth=0, edgecolors='none', rasterized=True,
                                      transform=transform).set_array(None)

    plt.savefig(saveloc)
    plt.close(fig)


def make_apoapse_muv_quicklook(orbit: int, data_location: Path, saveloc: str) -> None:
    """Make the standard apoapse MUV quicklook.

    Parameters
    ----------
    orbit
    data_location
    saveloc

    Returns
    -------
    None

    """
    pass


if __name__ == '__main__':
    p = Path('/media/kyle/McDataFace/iuvsdata/stage')
    #p = Path('/media/kyle/Samsung_T5/IUVS_data')

    for o in [16471]:
        print(o)
        #try:
        make_dayside_segment_detector_image(o, p, f'/home/kyle/iuvs/ql/orbit{o}-twilight-mask.png')
            #make_apoapse_muv_globe(o, p, f'/home/kyle/iuvs/globe/orbit{o}-mask.png')
        #except ValueError:
        #    print(f'skipping orbit {o}')
        #    continue


