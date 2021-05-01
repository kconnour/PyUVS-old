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