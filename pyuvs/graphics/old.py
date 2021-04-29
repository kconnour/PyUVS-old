def dayside_apoapse_quicklook(data_ax, files, dayside, swath_number, flipped, flatfield_directory, min_sza=0, max_sza=102,
                              min_lat=-90, max_lat=90, min_lon=0, max_lon=360, low_percentile=1, high_percentile=99):
    """ Plot the dayside apoapse quicklook

    Args:
        data_ax: the data axis
        files: a list of files for this orbit
        dayside: a list of booleans denoting if the orbit is dayside or nightside
        swath_number: a list of the swath numbers corresponding to the file
        flipped: a boolean denoting if we had a beta angle flip
        flatfield_directory: a string of the path to the flatfield
        min_sza: the minimum solar zenith angle to HEQ
        max_sza: the maximum solar zenith angle to HEQ
        min_lat: the minimum latitude to HEQ
        max_lat: the maximum latitude to HEQ
        min_lon: the minimum longitude to HEQ
        max_lon: the maximum longitude to HEQ
        low_percentile: the lowest percentile to include in HEQ
        high_percentile: the highest percentile to include in HEQ

    Returns:
        nothing. Plots the dayside apoapse data in the axis
    """

    # Define the HEQ cutoffs for each color channel
    red_heq = data_coloring(
        get_corrected_iuvs_data(files, 'red', flatfield_directory, min_sza=min_sza, max_sza=max_sza, min_lat=min_lat,
                                max_lat=max_lat, min_lon=min_lon, max_lon=max_lon), low_percentile=low_percentile,
                                high_percentile=high_percentile)
    green_heq = data_coloring(
        get_corrected_iuvs_data(files, 'green', flatfield_directory, min_sza=min_sza, max_sza=max_sza, min_lat=min_lat,
                                max_lat=max_lat, min_lon=min_lon, max_lon=max_lon), low_percentile=low_percentile,
                                high_percentile=high_percentile)
    blue_heq = data_coloring(
        get_corrected_iuvs_data(files, 'blue', flatfield_directory, min_sza=min_sza, max_sza=max_sza, min_lat=min_lat,
                                max_lat=max_lat, min_lon=min_lon, max_lon=max_lon), low_percentile=low_percentile,
                                high_percentile=high_percentile)

    # Now that we have the color cutoffs, go thru each file, colorize the pixels, and plot them
    for counter, file in enumerate(files):
        hdulist = fits.open(file)

        # Ignore single integrations and nightside data
        if single_integration(hdulist) or not dayside[counter]:
            continue

        # Get the data in colored form
        colored_data = colorize_pixels(hdulist, red_heq, green_heq, blue_heq, flatfield_directory)

        # Make the plot grid and its fill
        X, Y = make_plot_grid(hdulist, swath_number[counter], flipped)
        fill = make_plot_fill(hdulist)

        # Plot the data with pcolormesh, then turn off the array so it shows RGB colors instead of viridis
        img = data_ax.pcolormesh(X, Y, fill, color=colored_data, linewidth=0, edgecolors='none')
        img.set_array(None)


def get_corrected_iuvs_data(files, color, flatfield_directory, min_sza=0, max_sza=102, min_lat=-90, max_lat=90, min_lon=0, max_lon=360):
    """ Get IUVS data for an orbit and turn it into a flattened numpy array

    Args:
        files: a sorted list of observation files
        color: a string of the color to use
        flatfield_directory:
        min_sza: the minimum solar zenith angle to return data from
        max_sza: the maximum solar zenith angle to return data from
        min_lat: the minimum latitude to return data from
        max_lat: the maximum latitude to return data from
        min_lon: the mininum longitude to return data from
        max_lon: the maximum longitude to return data from

    Returns:
        a numpy array of the desired data_quantity
    """

    iuvs_data_structure = []
    for i, f in enumerate(files):
        hdulist = fits.open(f)

        # For dayside data, ignore single integrations and nightside files
        if single_integration(hdulist) or not dayside_file(hdulist):
            continue

        # Flatfield correct the data
        primary = flatfield_correct(hdulist['primary'].data, flatfield_directory)

        # Only look at data that falls within a specified range
        altitude = hdulist['pixelgeometry'].data['pixel_corner_mrh_alt'][:, :, 4]
        sza = hdulist['pixelgeometry'].data['pixel_solar_zenith_angle'][:, :]
        lat = hdulist['pixelgeometry'].data['pixel_corner_lat'][:, :, 4]
        lon = hdulist['pixelgeometry'].data['pixel_corner_lon'][:, :, 4]

        # Ensure I'm only looking at on-disk pixels. Then only select the pixels that meet other criteria
        trimmed_rows, trimmed_cols = np.where(
            (altitude == 0) & (sza > min_sza) & (sza < max_sza) & (lat > min_lat) & (lat < max_lat) & (
                        lon > min_lon) & (lon < max_lon))

        if color == 'red':
            some_quantity = np.sum(primary[trimmed_rows, trimmed_cols, -6:], axis=-1)
        elif color == 'green':
            some_quantity = np.sum(primary[trimmed_rows, trimmed_cols, 6:-6], axis=-1)
        elif color == 'blue':
            some_quantity = np.sum(primary[trimmed_rows, trimmed_cols, :6], axis=-1)
        else:
            print('You did not enter a valid color. You must answer correctly to pass the Bridge of Death.')
            raise SystemExit(1)

        iuvs_data_structure.append(np.ravel(some_quantity))

    return np.array(ravel(iuvs_data_structure))


def flatfield_correct(primary, flatfield_directory):
    """ Take the primary and flat-field correct it

    Args:
        primary: the hdulist 'primary' structure
        flatfield_directory:

    Returns:
        the corrected primary
    """

    integrations = primary.shape[0]
    positions = primary.shape[1]
    wavelengths = primary.shape[2]

    if positions == 50:
        flat_field = np.load(flatfield_directory + 'flatfield50rebin.npy')
    elif positions == 133:
        flat_field = np.load(flatfield_directory + 'flatfield133.npy')
    else:
        print('You do not have a flat field for this binning scheme. Exiting...')
        raise SystemExit(1)

    if wavelengths == 20:
        primary = primary[:, :, :-1]
        wavelengths -= 1
    elif wavelengths == 19:
        pass
    else:
        print('We do not have a flatfield for this ' + str(wavelengths) + ' wavelength binning.')
        return primary

    # The flatfield is [positions, wavelengths] so it needs expanded to match the shape of the primary
    expanded_flat_field = np.zeros((integrations, positions, wavelengths))
    for i in range(integrations):
        expanded_flat_field[i, :, :] = flat_field

    primary /= expanded_flat_field

    return primary


def ravel(some_data):
    """ Take a list and unravel it

    Args:
        some_data: a list of some quantity.

    Returns:
        an unraveled list
    """

    return [datum for all_data in some_data for datum in all_data]


def data_coloring(color_array, low_percentile=1, high_percentile=99):
    """ Performs the HEQ data coloring for the inputs from each color channel

    Args:
        color_array: a 1D sorted np array of the data from a particular color channel
        low_percentile: the lowest percentile to include in the coloring scheme
        high_percentile: the highest percentile to include in the coloring scheme

    Returns:
        a tuple of the 256 dividers between the data of that color channel
    """

    # Get the minimum index of the color channel where the DN value is positive
    color_array = np.sort(color_array)

    # Do this if I want to set 0 DNs to be the lower range of my scale
    # minimum_dn_index = np.where(color_array > 0)[0][0]     # np.where needs the dreaded [0][0] to get a scalar out
    number_pixels = len(color_array)
    minimum_dn_index = int(low_percentile * number_pixels / 100)
    maximum_dn_index = int(high_percentile * number_pixels / 100)

    color_array = color_array[minimum_dn_index:maximum_dn_index]
    number_good_pixels = len(color_array)

    # Find the cutoff DNs for what is each color in each color channel
    color = np.linspace(0, 1, num=256)
    color_heq = []

    for i in range(256):
        color_heq.append(color_array[int(color[i] * (number_good_pixels - 1))])

    return color_heq


def initialize_colors(hdulist, n_integrations, n_positions, flatfield_directory):
    """

    Args:
        hdulist: the hdulist
        n_integrations: the number of integrations in this swath
        n_positions: the number of spatial elements in this swath

    Returns:
        an NxMx3 (for RGB) numpy array of spectrally coadded data
    """

    # Set my color array
    data = np.zeros((n_integrations, n_positions, 3))
    primary = flatfield_correct(hdulist['primary'].data, flatfield_directory)

    data[:, :, 0] = np.sum(primary[:, :, -6:], axis=-1)
    data[:, :, 1] = np.sum(primary[:, :, 6:-6], axis=-1)
    data[:, :, 2] = np.sum(primary[:, :, :6], axis=-1)

    return data


def dn_to_rgb(color_dn, color_eq):
    """ Convert DNs to RGB values

    Args:
        color_dn:
        color_eq: a numpy array of the 256 cutoff values between each color channel

    Returns:
        The data array where DNs have been transformed into rgb values
    """

    # Now turn DNs into RGB values
    for i in range(color_dn.shape[0]):
        for j in range(color_dn.shape[1]):
            if np.isnan(color_dn[i, j]):
                color_dn[i, j] = 0
                continue
            else:
                position_color = np.searchsorted(color_eq, color_dn[i, j])

            if position_color > 255:
                color_dn[i, j] = 255
            else:
                color_dn[i, j] = position_color

    return color_dn/255.


def colorize_pixels(hdulist, red_cutoffs, green_cutoffs, blue_cutoffs, flatfield_directory):
    """ Colorize all the pixels in a given hdulist

    Args:
        hdulist: the hdulist
        red_cutoffs: a list of 256 values denoting the cutoffs between the red data
        green_cutoffs: a list of 256 values denoting the cutoffs between the green data
        blue_cutoffs: a list of 256 values denoting the cutoffs between the blue data

    Returns:
        a numpy array of the colorized data
    """

    # Get the data dimensions
    n_integrations, n_positions, junk = get_data_dimensions(hdulist)

    # Now pull out the DNs for each color channel
    data = initialize_colors(hdulist, n_integrations, n_positions, flatfield_directory)

    # Now turn the DNs into RGB values
    data[:, :, 0] = dn_to_rgb(data[:, :, 0], red_cutoffs)
    data[:, :, 1] = dn_to_rgb(data[:, :, 1], green_cutoffs)
    data[:, :, 2] = dn_to_rgb(data[:, :, 2], blue_cutoffs)

    # For reasons unknown pcolormesh wants an array that's the shape (n_pixels, 3)
    colored_data = np.reshape(data, (data.shape[0] * data.shape[1], data.shape[2]))

    return colored_data


def make_plot_grid(hdulist, swath, flipped):
    """ Make the pixel grid to plot with pcolormesh for this hdulist

    Args:
        hdulist: the hdulist
        swath: the swath to plot
        flipped: a boolean indicating this orbit was flipped or not

    Returns:
        the X and Y grids for this orbit
    """

    # Slit width in degrees
    slit_width = 10.64

    n_integrations, n_positions, junk = get_data_dimensions(hdulist)

    # Observation angles
    angles = hdulist['integration'].data['mirror_deg'] * 2  # convert from mirror angles to field-of-view angles
    dang = np.mean(np.diff(angles[:-1]))

    # Make the grid where n_positions fills the slit width and the min/max mirror angles set the vertical extent
    if flipped:
        X, Y = np.meshgrid(np.flip(
            np.linspace(slit_width * swath, slit_width * (swath + 1), n_positions + 1)),
            np.linspace(angles[0] - dang / 2, angles[-1] + dang / 2, n_integrations + 1))
    else:
        X, Y = np.meshgrid(
            np.linspace(slit_width * swath, slit_width * (swath + 1), n_positions + 1),
            np.linspace(angles[0] - dang / 2, angles[-1] + dang / 2, n_integrations + 1))

    return X, Y


def make_plot_fill(hdulist):
    """ Make the values that fill the plot

    Args:
        hdulist: the hdulsit

    Returns:
        a numpy array of filled values
    """

    # Make a filler array for pcolormesh. It can be anything as long as the off-disk values are nans
    n_integrations, n_positions, junk = get_data_dimensions(hdulist)
    fill = np.ones((n_integrations, n_positions))

    # Set off-disk pixels to be nans so that pcolormesh won't plot them later
    altitude = hdulist['pixelgeometry'].data['pixel_corner_mrh_alt'][:, :, 4]
    fill[np.where(altitude != 0)] = np.nan
    return fill