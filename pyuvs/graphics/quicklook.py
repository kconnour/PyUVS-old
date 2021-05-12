"""

"""
from astropy.io import fits
import copy
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.ticker as ticker
from scipy.ndimage import gaussian_filter
from skimage.transform import resize
import spiceypy as spice
from pyuvs.files import FileFinder, DataFilenameCollection, orbit_code
from pyuvs.l1b.data_contents import L1bDataContents
from pyuvs.l1b.data_classifier import DataClassifier
from pyuvs.graphics.coloring import HistogramEqualizer
from pyuvs.spice import Spice


# TODO: get properties from data (method)
# TODO: get properties from database (method)
class ApoapseMUVQuicklookCreator:
    def __init__(self) -> None:
        self.__save_name = 'mvn_iuv_ql_apoapse-orbit00000-muv-TEST.png'

    def process_quicklook(self, data_location: str, flatfield_location: str,
                          spice_directory: str,
                          orbit: int, swath, flip, savelocation: str,
                          species: str):
        files = FileFinder(data_location).soschob(orbit, segment='apoapse',
                                                  channel='muv')
        flatfield = np.load(flatfield_location)
        ql = ApoapseMUVQuicklook(files, flatfield, swath, flip, spice_directory,
                                 species)
        ql.savefig(os.path.join(
            savelocation, self.__save_name.replace('00000', orbit_code(orbit))))


# TODO: this is flipped compared to Zac's QLs
# TODO: Add ability to choose spectral indices in HistogramEqualizer
# TODO: this breaks on a single integration
# TODO: should HEQ break if I try to apply the coloring to a file that didn't
#  make the coloring?
# TODO banner
class ApoapseMUVQuicklook:
    def __init__(self, files: DataFilenameCollection, flatfield: np.ndarray,
                 swath_numbers: list[int], flip: bool, spice_directory: str,
                 species: str) -> None:
        self.__files = files
        self.__flatfield = flatfield
        self.__swath_numbers = swath_numbers
        self.__flip = flip
        self.__spice_directory = spice_directory
        self.__species = species
        self.__slit_width = 10.64

        self.__axes = self.__setup_fig_and_axes()
        self.__fill_plots()

    def __setup_fig_and_axes(self):
        self.__set_quicklook_rc_params()
        fig, axis_grid = self.__make_axis_grid()
        self.__combine_top_axes_rows(fig, axis_grid)
        axes = self.__create_axis_dict(fig.axes)
        self.__setup_axes(axes)
        return axes

    # TODO: I hate this function and I can't completely identify why
    @staticmethod
    def __set_quicklook_rc_params() -> None:
        # Make sure the typeface isn't outlined when saved as a .pdf
        plt.rc('pdf', fonttype=42)  # ???
        plt.rc('ps', fonttype=42)  # postscript

        # Set the plot to be $\LaTeXe{}$-like
        plt.rc('font', **{'family': 'STIXGeneral'})  # Set the typeface to stix
        plt.rc('mathtext', fontset='stix')  # Set all math font to stix
        plt.rc('text', usetex=False)

        plt_thick = 0.5
        plt.rc('lines', linewidth=plt_thick)
        plt.rc('axes', linewidth=plt_thick)

    @staticmethod
    def __make_axis_grid():
        text_axis_height = 1
        data_axis_height = 2
        angular_axis_height = 1
        colorbar_width = 1/15
        height_ratios = [text_axis_height, data_axis_height, data_axis_height,
                         angular_axis_height, angular_axis_height]
        width_ratios = [1, colorbar_width, 1, colorbar_width]

        fig, axes = plt.subplots(5, 4, figsize=(6, 8),
                                 gridspec_kw={'height_ratios': height_ratios,
                                              'width_ratios': width_ratios},
                                 constrained_layout=True)
        return fig, axes

    def __combine_top_axes_rows(self, fig, axes):
        self.__combine_row_of_axes(fig, axes, 0, None)
        self.__combine_row_of_axes(fig, axes, 1, 3)
        self.__combine_row_of_axes(fig, axes, 2, 3)

    @staticmethod
    def __combine_row_of_axes(fig, axes, row, end_index):
        gs = axes[row, 0].get_gridspec()
        [ax.remove() for ax in axes[row, :end_index]]
        fig.add_subplot(gs[row, :end_index])
        return fig, axes

    @staticmethod
    def __create_axis_dict(axes):
        return {'text': axes[10],
                'data': axes[11],
                'data_colorbar': axes[0],
                'geography': axes[12],
                'geography_colorbar': axes[1],
                'local_time': axes[2],
                'local_time_colorbar': axes[3],
                'solar_zenith_angle': axes[4],
                'solar_zenith_angle_colorbar': axes[5],
                'emission_angle': axes[6],
                'emission_angle_colorbar': axes[7],
                'phase_angle': axes[8],
                'phase_angle_colorbar': axes[9]}

    def __setup_axes(self, axes):
        self.__turn_off_frame(axes['text'])
        for key in axes.keys():
            self.__turn_off_ticks(axes[key])
            # self.__set_axis_limits(axes[key])
            self.__set_background_black(axes[key])

    @staticmethod
    def __turn_off_frame(axis: plt.Axes) -> None:
        axis.set_frame_on(False)

    @staticmethod
    def __turn_off_ticks(axis: plt.Axes) -> None:
        axis.set_xticks([])
        axis.set_yticks([])

    def __set_axis_limits(self, axis: plt.Axes) -> None:
        axis.set_xlim(0, self.__slit_width * (self.__swath_numbers[-1] + 1))
        axis.set_ylim(60, 120)

    @staticmethod
    def __set_background_black(axis: plt.Axes) -> None:
        axis.set_facecolor((0, 0, 0))

    def __fill_plots(self) -> None:
        if self.__species == 'NO':
            self.__fill_plots_no_nightglow()
        elif self.__species == 'aurora':
            self.__fill_plots_aurora()

    def __fill_plots_aurora(self):
        # self.__fill_data_axis()
        self.__fill_geometry_axes_magnetic_field()
        # self.__fill_local_time_axes()
        # self.__fill_solar_zenith_angle_axes()
        # self.__fill_emission_angle_axes()
        # self.__fill_phase_angle_axes()

    def __fill_plots_no_nightglow(self):
        # self.__fill_data_axis()
        self.__fill_geometry_axis_context_map()
        self.__axes['geography_colorbar'].remove()
        # self.__fill_local_time_axes()
        # self.__fill_solar_zenith_angle_axes()
        # self.__fill_emission_angle_axes()
        # self.__fill_phase_angle_axes()

    def __fill_data_axis(self) -> None:
        ql = Quicklook(self.__files, self.__axes['data'], self.__swath_numbers,
                       self.__flip)
        ql.histogram_equalize_dayside(self.__flatfield)

    def __fill_geometry_axis_context_map(self):
        ql = Quicklook(self.__files, self.__axes['geography'],
                       self.__swath_numbers, self.__flip)
        ql.fill_context_map(self.__spice_directory)

    def __fill_geometry_axes_magnetic_field(self):
        bundle = QuicklookColorbarBundle(
            self.__axes['geography'],
            self.__axes['geography_colorbar'])
        bundle.fill_magnetic_field(
            self.__files, self.__swath_numbers, self.__flip, self.__spice_directory)

    def __fill_local_time_axes(self) -> None:
        bundle = QuicklookColorbarBundle(
            self.__axes['local_time'],
            self.__axes['local_time_colorbar'])
        bundle.fill_local_time(
            self.__files, self.__swath_numbers, self.__flip)

    def __fill_solar_zenith_angle_axes(self) -> None:
        bundle = QuicklookColorbarBundle(
            self.__axes['solar_zenith_angle'],
            self.__axes['solar_zenith_angle_colorbar'])
        bundle.fill_solar_zenith_angle(
            self.__files, self.__swath_numbers, self.__flip)

    def __fill_emission_angle_axes(self) -> None:
        bundle = QuicklookColorbarBundle(
            self.__axes['emission_angle'],
            self.__axes['emission_angle_colorbar'])
        bundle.fill_emission_angle(
            self.__files, self.__swath_numbers, self.__flip)

    def __fill_phase_angle_axes(self) -> None:
        bundle = QuicklookColorbarBundle(
            self.__axes['phase_angle'],
            self.__axes['phase_angle_colorbar'])
        bundle.fill_phase_angle(
            self.__files, self.__swath_numbers, self.__flip)

    @staticmethod
    def savefig(location: str) -> None:
        plt.savefig(location, dpi=300)


class Quicklook:
    """Put a quicklook-style plot in an axis.

    Quicklook has methods to add a variety of quicklooks into an axis.

    """
    def __init__(self, files: DataFilenameCollection, ax: plt.Axes,
                 swath_numbers: list[int], flip: bool) -> None:
        """
        Parameters
        ----------
        files
            A collection of files to plot a quicklook for.
        ax
            The axis to put the quicklook into.
        swath_numbers
            The swath numbers for each of the swaths in the files.
        flip
            Denote whether the files were beta-angle flipped.

        """
        self.__files = files
        self.__ax = ax
        self.__swath_numbers = swath_numbers
        self.__flip = flip
        self.__slit_width = 10.64

    def histogram_equalize_dayside(
            self, flatfield: np.ndarray, min_lat: float = -90,
            max_lat: float = 90, min_lon: float = 0, max_lon: float = 360,
            min_sza: float = 0, max_sza: float = 102, low_percentile: float = 1,
            high_percentile: float = 99) -> None:
        """ Make a quicklook with histogram equalization.

        Parameters
        ----------
        flatfield
            The flatfield [n_positions, n_wavelengths] for the files.
        min_lat
            The minimum latitude to consider when making the coloring.
        max_lat
            The maximum latitude to consider when making the coloring.
        min_lon
            The minimum longitude to consider when making the coloring.
        max_lon
            The maximum longitude to consider when making the coloring.
        min_sza
            The minimum solar zenith angle to consider when making the coloring.
        max_sza
            The maximum solar zenith angle to consider when making the coloring.
        low_percentile
            The percentile where data below it will be set to 0.
        high_percentile
            The percentile where data below it will be set to 1.

        """
        heq = HistogramEqualizer(
            self.__files, flatfield, min_lat, max_lat, min_lon, max_lon,
            min_sza, max_sza, low_percentile, high_percentile)
        for c, f in enumerate(self.__files.filenames):
            l1b = L1bDataContents(f)
            if not DataClassifier(f).dayside():
                continue
            colors = heq.colorize_primary(l1b.primary) / 255
            reshaped_colors = self.__reshape_data_for_pcolormesh(colors)
            X, Y = self.__make_plot_grid(l1b, self.__swath_numbers[c])
            fill = self.__make_plot_fill(l1b)
            self.__plot_custom_primary(X, Y, fill, reshaped_colors)

    def fill_local_time(self, cmap, norm):
        for c, f in enumerate(self.__files.filenames):
            l1b = L1bDataContents(f)
            lt = np.where(l1b.altitude[:, :, 4] != 0, np.nan, l1b.local_time)
            X, Y = self.__make_plot_grid(l1b, self.__swath_numbers[c])
            self.__ax.pcolormesh(X, Y, lt, cmap=cmap, norm=norm)

    def fill_solar_zenith_angle(self, cmap, norm):
        for c, f in enumerate(self.__files.filenames):
            l1b = L1bDataContents(f)
            sza = np.where(l1b.altitude[:, :, 4] != 0, np.nan, l1b.solar_zenith_angle)
            X, Y = self.__make_plot_grid(l1b, self.__swath_numbers[c])
            self.__ax.pcolormesh(X, Y, sza, cmap=cmap, norm=norm)

    def fill_emission_angle(self, cmap, norm):
        for c, f in enumerate(self.__files.filenames):
            l1b = L1bDataContents(f)
            ea = np.where(l1b.altitude[:, :, 4] != 0, np.nan, l1b.emission_angle)
            X, Y = self.__make_plot_grid(l1b, self.__swath_numbers[c])
            self.__ax.pcolormesh(X, Y, ea, cmap=cmap, norm=norm)

    def fill_phase_angle(self, cmap, norm):
        for c, f in enumerate(self.__files.filenames):
            l1b = L1bDataContents(f)
            pa = np.where(l1b.altitude[:, :, 4] != 0, np.nan, l1b.phase_angle)
            X, Y = self.__make_plot_grid(l1b, self.__swath_numbers[c])
            self.__ax.pcolormesh(X, Y, pa, cmap=cmap, norm=norm)

    def fill_magnetic_field(self, spice_directory, cmap, norm):
        Spice().load_spice(spice_directory)
        field_map = self.magnetic_field_map(cmap, norm)
        for c, f in enumerate(self.__files.filenames):
            hdul = fits.open(f.path)
            lat, lon, sza, ea, pa, lt, x, y, cx, cy, cm = \
                self.highres_swath_geometry(hdul, field_map)

            y = (120 - y) + 60
            # offset X array by swath number
            x += self.__slit_width * self.__swath_numbers[c]

            cm = cm.reshape(cm.shape[0] * cm.shape[1], cm.shape[2])

            self.__ax.pcolormesh(x, y, np.ones_like(cx), color=cm, linewidth=0,
                                 edgecolors='none',
                       rasterized=True).set_array(None)

    def fill_context_map(self, spice_directory):
        Spice().load_spice(spice_directory)
        sfc_map = np.load('/home/kyle/repos/pyuvs/aux/mars_surface_map.npy')
        for c, f in enumerate(self.__files.filenames):
            hdul = fits.open(f.path)
            lat, lon, sza, ea, pa, lt, x, y, cx, cy, cm = \
                self.highres_swath_geometry(hdul, sfc_map)

            y = (120 - y) + 60
            # offset X array by swath number
            x += self.__slit_width * self.__swath_numbers[c]

            cm = cm.reshape(cm.shape[0] * cm.shape[1], cm.shape[2])

            self.__ax.pcolormesh(x, y, np.ones_like(cx), color=cm, linewidth=0,
                                 edgecolors='none',
                       rasterized=True).set_array(None)

    def magnetic_field_map(self, cmap, norm):
        field = np.load('/home/kyle/repos/pyuvs/aux/magnetic_field_closed_probability.npy')
        field = np.flipud(self.__resize_map(field))
        return cmap(norm(field))

    @staticmethod
    def __resize_map(map_field):
        map_field = resize(map_field, (1800, 3600))
        V = map_field.copy()
        V[np.isnan(map_field)] = 0
        VV = gaussian_filter(V, sigma=1)
        W = 0 * map_field.copy() + 1
        W[np.isnan(map_field)] = 0
        WW = gaussian_filter(W, sigma=1)
        map_field = VV / WW
        map_field /= np.nanmax(map_field)
        return map_field

    @staticmethod
    def __reshape_data_for_pcolormesh(colors: np.ndarray) -> np.ndarray:
        colors = np.moveaxis(colors, 0, -1)
        return np.reshape(colors, (colors.shape[0] * colors.shape[1],
                                   colors.shape[2]))

    def __make_plot_grid(self, file: L1bDataContents, swath: int) \
            -> tuple[np.ndarray, np.ndarray]:
        angles = file.mirror_angles * 2
        delta_angles = np.mean(np.diff(angles[:-1]))
        x = np.linspace(self.__slit_width * swath,
                        self.__slit_width * (swath + 1), file.n_positions + 1)
        if self.__flip:
            x = np.flip(x)

        X, Y = np.meshgrid(
            x,
            np.linspace(angles[0] - delta_angles / 2,
                        angles[-1] + delta_angles / 2, file.n_integrations + 1)
        )
        Y = 180 - Y
        return X, Y

    @staticmethod
    def __make_plot_fill(file: L1bDataContents) -> np.ndarray:
        return np.where(file.altitude[:, :, 4] != 0, np.nan, 1)

    def __plot_custom_primary(self, X, Y, fill, colors) -> None:
        img = self.__ax.pcolormesh(X, Y, fill, color=colors, linewidth=0,
                                   edgecolors='none')
        img.set_array(None)

    def highres_swath_geometry(self, hdul, map_data, res=200):
        """
        Generates an artificial high-resolution slit, calculates viewing geometry and surface-intercept map.
        Parameters
        ----------
        hdul : HDUList
            Opened FITS file.
        res : int, optional
            The desired number of artificial elements along the slit. Defaults to 200.

        Returns
        -------
        latitude : array
            Array of latitudes for the centers of each high-resolution artificial pixel. NaNs if pixel doesn't intercept
            the surface of Mars.
        longitude : array
            Array of longitudes for the centers of each high-resolution artificial pixel. NaNs if pixel doesn't intercept
            the surface of Mars.
        sza : array
            Array of solar zenith angles for the centers of each high-resolution artificial pixel. NaNs if pixel doesn't
            intercept the surface of Mars.
        ea
        pa
        local_time : array
            Array of local times for the centers of each high-resolution artificial pixel. NaNs if pixel doesn't intercept
            the surface of Mars.
        x : array
            Horizontal coordinate edges in angular space. Has shape (n+1, m+1) for geometry arrays with shape (n,m).
        y : array
            Vertical coordinate edges in angular space. Has shape (n+1, m+1) for geometry arrays with shape (n,m).
        cx : array
            Horizontal coordinate centers in angular space. Same shape as geometry arrays.
        cy : array
            Vertical coordinate centers in angular space. Same shape as geometry arrays.
        context_map : array
            High-resolution image of the Mars surface as intercepted by the swath. RGB tuples with shape (n,m,3).
        """
        # get swath vectors, ephemeris times, and mirror angles
        vec = hdul['pixelgeometry'].data['pixel_vec']
        et = hdul['integration'].data['et']
        # get dimensions of the input data
        n_int = hdul['integration'].data.shape[0]
        n_spa = len(hdul['binning'].data['spapixlo'][0])
        # set the high-resolution slit width and calculate the number of high-resolution integrations
        hifi_spa = res
        hifi_int = int(hifi_spa / n_spa * n_int)
        # make arrays of ephemeris time and array to hold the new swath vector calculations
        et_arr = np.expand_dims(et, 1) * np.ones((n_int, n_spa))
        et_arr = resize(et_arr, (hifi_int, hifi_spa), mode='edge')
        vec_arr = np.zeros((hifi_int + 1, hifi_spa + 1, 3))
        # make an artificially-divided slit and create new array of swath vectors
        if self.__flip:
            lower_left = vec[0, :, 0, 0]
            upper_left = vec[-1, :, 0, 1]
            lower_right = vec[0, :, -1, 2]
            upper_right = vec[-1, :, -1, 3]
        else:
            lower_left = vec[0, :, 0, 1]
            upper_left = vec[-1, :, 0, 0]
            lower_right = vec[0, :, -1, 3]
            upper_right = vec[-1, :, -1, 2]
        for e in range(3):
            a = np.linspace(lower_left[e], upper_left[e], hifi_int + 1)
            b = np.linspace(lower_right[e], upper_right[e], hifi_int + 1)
            vec_arr[:, :, e] = np.array(
                [np.linspace(i, j, hifi_spa + 1) for i, j in zip(a, b)])
        # resize array to extract centers
        vec_arr = resize(vec_arr, (hifi_int, hifi_spa, 3), anti_aliasing=True)
        # make empty arrays to hold geometry calculations
        latitude = np.zeros((hifi_int, hifi_spa)) * np.nan
        longitude = np.zeros((hifi_int, hifi_spa)) * np.nan
        sza = np.zeros((hifi_int, hifi_spa)) * np.nan
        phase_angle = np.zeros((hifi_int, hifi_spa)) * np.nan
        emission_angle = np.zeros((hifi_int, hifi_spa)) * np.nan
        local_time = np.zeros((hifi_int, hifi_spa)) * np.nan
        context_map = np.zeros((hifi_int, hifi_spa, 4)) * np.nan

        # calculate intercept latitude and longitude using SPICE, looping through each high-resolution pixel
        target = 'Mars'
        frame = 'IAU_Mars'
        abcorr = 'LT+S'
        observer = 'MAVEN'
        body = 499  # Mars IAU code
        for i in range(hifi_int):
            for j in range(hifi_spa):
                et = et_arr[i, j]
                los_mid = vec_arr[i, j, :]
                # try to perform the SPICE calculations and record the results
                try:
                    # calculate surface intercept
                    spoint, trgepc, srfvec = spice.sincpt('Ellipsoid', target,
                                                          et, frame, abcorr,
                                                          observer, frame,
                                                          los_mid)
                    # calculate illumination angles
                    trgepc, srfvec, phase_for, solar, emissn = spice.ilumin(
                        'Ellipsoid', target, et, frame, abcorr,
                        observer, spoint)
                    # convert from rectangular to spherical coordinates
                    rpoint, colatpoint, lonpoint = spice.recsph(spoint)
                    # convert longitude from domain [-pi,pi) to [0,2pi)
                    if lonpoint < 0.:
                        lonpoint += 2 * np.pi
                    # convert ephemeris time to local solar time
                    hr, mn, sc, time, ampm = spice.et2lst(et, body, lonpoint,
                                                          'planetocentric',
                                                          timlen=256,
                                                          ampmlen=256)
                    # convert spherical coordinates to latitude and longitude in degrees
                    latitude[i, j] = np.degrees(np.pi / 2 - colatpoint)
                    longitude[i, j] = np.degrees(lonpoint)
                    # convert illumination angles to degrees and record
                    sza[i, j] = np.degrees(solar)
                    phase_angle[i, j] = np.degrees(phase_for)
                    emission_angle[i, j] = np.degrees(emissn)
                    # convert local solar time to decimal hour
                    local_time[i, j] = hr + mn / 60 + sc / 3600
                    # convert latitude and longitude to pixel coordinates
                    map_lat = int(np.round(np.degrees(colatpoint), 1) * 10)
                    map_lon = int(np.round(np.degrees(lonpoint), 1) * 10)
                    # make a corresponding magnetic field topology map
                    context_map[i, j] = map_data[map_lat, map_lon]
                # if the SPICE calculation fails, this (probably) means it didn't intercept the planet
                except:
                    pass
        # get mirror angles
        angles = hdul['integration'].data[
                     'mirror_deg'] * 2  # convert from mirror angles to FOV angles
        dang = np.diff(angles)[0]
        # create an meshgrid of angular coordinates for the high-resolution pixel edges
        x, y = np.meshgrid(np.linspace(0, self.__slit_width, hifi_spa + 1),
                           np.linspace(angles[0] - dang / 2,
                                       angles[-1] + dang / 2, hifi_int + 1))
        # calculate the angular separation between pixels
        dslit = self.__slit_width / hifi_spa
        # create an meshgrid of angular coordinates for the high-resolution pixel centers
        cx, cy = np.meshgrid(
            np.linspace(0 + dslit, self.__slit_width - dslit, hifi_spa),
            np.linspace(angles[0], angles[-1], hifi_int))
        # beta-flip the coordinate arrays if necessary
        if self.__flip:
            x = np.fliplr(x)
            y = (np.fliplr(y) - 90) / (-1) + 90
            cx = np.fliplr(cx)
            cy = (np.fliplr(cy) - 90) / (-1) + 90
        # convert longitude to [-180,180)
        longitude[np.where(longitude > 180)] -= 360
        # return the geometry and coordinate arrays
        # cx, cy is for a lat/lon grid on top of the map (50, 1) --> (200, 4)
        # all but x, y, context_map is (n_integrations, n_positions)
        # the context map has shape (n_integrations, n_positions, 4)
        # x, y, cx, cy are (n_int +1, n_pos + 1)
        return latitude, longitude, sza, emission_angle, phase_angle, \
               local_time, x, y, cx, cy, context_map


class Colorbar:
    def __init__(self, axis, cmap, norm, label, major_tick_spacing,
                 minor_tick_spacing):
        self.__axis = axis
        self.__cmap = cmap
        self.__norm = norm
        self.__label = label
        self.__major = major_tick_spacing
        self.__minor = minor_tick_spacing

    def fill(self):
        data_sm = plt.cm.ScalarMappable(cmap=self.__cmap, norm=self.__norm)
        data_sm.set_array(np.array([]))
        cbar = plt.colorbar(data_sm, cax=self.__axis, label=self.__label)
        cbar.ax.yaxis.set_major_locator(ticker.MultipleLocator(self.__major))
        cbar.ax.yaxis.set_minor_locator(ticker.MultipleLocator(self.__minor))


# TODO: this is how to add cbar lines. Add to SZA and PA
# sza_cbar.ax.axhline()

class QuicklookColorbarBundle:
    def __init__(self, quicklook_ax: plt.Axes, colorbar_ax: plt.Axes) -> None:
        self.__quicklook_ax = quicklook_ax
        self.__colorbar_ax = colorbar_ax

    def fill_magnetic_field(self, files: DataFilenameCollection,
                            swath_number: list[int], flip: bool, spice_directory) -> None:
        cmap = plt.get_cmap('Blues_r')
        norm = colors.Normalize(vmin=0, vmax=1)
        label = 'Closed field line probability'
        ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        ql.fill_magnetic_field(spice_directory, cmap, norm)
        Colorbar(self.__colorbar_ax, cmap, norm, label, 0.2, 0.05).fill()

    def fill_local_time(self, files: DataFilenameCollection,
                        swath_number: list[int], flip: bool) -> None:
        cmap = 'twilight_shifted'
        norm = colors.Normalize(vmin=6, vmax=18)
        label = 'Local Time [hours]'
        ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        ql.fill_local_time(cmap, norm)
        Colorbar(self.__colorbar_ax, cmap, norm, label, 3, 1).fill()

    def fill_solar_zenith_angle(self, files: DataFilenameCollection,
                                swath_number: list[int], flip: bool) -> None:
        cmap = 'cividis_r'
        norm = colors.Normalize(vmin=0, vmax=180)
        label = r'Solar Zenith Angle [$\degree$]'
        ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        ql.fill_solar_zenith_angle(cmap, norm)
        Colorbar(self.__colorbar_ax, cmap, norm, label, 30, 10).fill()

    def fill_emission_angle(self, files: DataFilenameCollection,
                            swath_number: list[int], flip: bool) -> None:
        cmap = colors.LinearSegmentedColormap.from_list(
            'cividis_half', copy.copy(plt.get_cmap('cividis_r'))
            (np.linspace(0, 0.5, 256)))
        norm = colors.Normalize(vmin=0, vmax=90)
        label = r'Emission Angle [$\degree$]'
        ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        ql.fill_emission_angle(cmap, norm)
        Colorbar(self.__colorbar_ax, cmap, norm, label, 15, 5).fill()

    def fill_phase_angle(self, files: DataFilenameCollection,
                         swath_number: list[int], flip: bool) -> None:
        cmap = 'cividis_r'
        norm = colors.Normalize(vmin=0, vmax=180)
        label = r'Phase Angle [$\degree$]'
        ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        ql.fill_phase_angle(cmap, norm)
        Colorbar(self.__colorbar_ax, cmap, norm, label, 30, 10).fill()


if __name__ == '__main__':
    pa = '/media/kyle/Samsung_T5/IUVS_data'
    ff = '/home/kyle/repos/pyuvs/aux/flatfield133.npy'
    sp = '/media/kyle/Samsung_T5/IUVS_data/spice'
    saveloc = '/home/kyle'

    a = ApoapseMUVQuicklookCreator()
    swaths = [0, 0, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5]
    a.process_quicklook(pa, ff, sp, 3453, swaths, False, saveloc, 'NO')
