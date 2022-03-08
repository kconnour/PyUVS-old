import matplotlib.colors as colors


def NO_colormap(bad=None, n=256):
    """
    Generates the NO nightglow black/green/yellow-green/white colormap (IDL #8).

    Parameters
    ----------
    bad : (3,) tuple
        Normalized color tuple (R,G,B) for missing data (NaN) display. Defaults to None (bad values are masked).
    n : int
        Number of colors to generate. Defaults to 256.

    Returns
    -------
    cmap : object
        Special NO nightglow colormap.
    """

    # color sequence from black -> green -> yellow-green -> white
    cmap_colors = [(0, 0, 0), (0, 0.5, 0), (0.61, 0.8, 0.2), (1, 1, 1)]

    # set colormap name
    cmap_name = 'NO'

    # make a colormap using the color sequence and chosen name
    cmap = colors.LinearSegmentedColormap.from_list(cmap_name, cmap_colors,
                                                    N=n)

    # set the nan color
    if bad is not None:
        try:
            cmap.set_bad(bad)
        except:
            raise Exception(
                'Invalid choice for bad data color. Try a color tuple, e.g., (0,0,0).')

    # return the colormap
    return cmap


def CO2p_colormap(bad=None, n=256):
    """
    Generates the custom CO2p black/pink/white colormap.

    Parameters
    ----------
    bad : (3,) tuple
        Normalized color tuple (R,G,B) for missing data (NaN) display. Defaults to None (bad values are masked).
    n : int
        Number of colors to generate. Defaults to 256.

    Returns
    -------
    cmap : object
        Special aurora colormap.
    """

    # color sequence from black -> purple -> white
    cmap_colors = [(0, 0, 0), (0.7255, 0.0588, 0.7255), (1, 1, 1)]

    # set colormap name
    cmap_name = 'CO2p'

    # make a colormap using the color sequence and chosen name
    cmap = colors.LinearSegmentedColormap.from_list(cmap_name, cmap_colors,
                                                    N=n)

    # set the nan color
    if bad is not None:
        try:
            cmap.set_bad(bad)
        except:
            raise Exception(
                'Invalid choice for bad data color. Try a color tuple, e.g., (0,0,0).')

    # return the colormap
    return cmap
