'''
# These used to be things that acted on the B field map but they can
really apply to any image with a few tweaks
# TODO: make Zac look into gaussian smoothing with astropy
    def make_map_high_resolution(self) -> None:
        """ Make the map into a higher resolution map.

        """
        map_field = resize(self.array, (1800, 3600))
        V = map_field.copy()
        V[np.isnan(map_field)] = 0
        VV = gaussian_filter(V, sigma=1)
        W = 0 * map_field.copy() + 1
        W[np.isnan(map_field)] = 0
        WW = gaussian_filter(W, sigma=1)
        map_field = VV / WW
        map_field /= np.nanmax(map_field)
        self.array = map_field

    def colorize_map(self):
        """Colorize the map with the standard IUVS magnetic field coloring.

        """
        colormap = Colormaps()
        colormap.set_magnetic_field()
        self.array = colormap.cmap(colormap.norm(self.array))'''
