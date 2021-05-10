"""

"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
from mpl_toolkits.axes_grid1 import make_axes_locatable
from pyuvs.files import FileFinder, DataFilenameCollection, orbit_code
from pyuvs.l1b.data_contents import L1bDataContents
from pyuvs.l1b.data_classifier import DataClassifier
from pyuvs.graphics.coloring import HistogramEqualizer

"""
_QuicklookPlotter

"""

# TODO: this is flipped compared to Zac's QLs
# TODO: Add ability to choose spectral indices in HistogramEqualizer
# TODO: this breaks on a single integration
# TODO: should HEQ break if I try to apply the coloring to a file that didn't
#  make the coloring?
# TODO: set the ticks separately from the numbers on the colorbar
# TODO: EA should have the same colorbar as SZA and PA but only use half of it
# TODO: labels on the right side
# TODO banner
# TODO: minor ticks on the colorbars


class ApoapseMUVQuicklook:
    def __init__(self, files: DataFilenameCollection, flatfield: np.ndarray,
                 swath_numbers: list[int], flip: bool) -> None:
        self.__files = files
        self.__flatfield = flatfield
        self.__swath_numbers = swath_numbers
        self.__flip = flip
        self.__slit_width = 10.64

        self.__set_quicklook_rc_params()
        self.__fig = plt.figure(figsize=(5, 10))
        self.__axes = self.__make_axes()
        self.__fill_plots()

    @staticmethod
    def __set_quicklook_rc_params() -> None:
        # Make sure the typeface isn't outlined when saved as a .pdf
        plt.rc('pdf', fonttype=42)  # ???
        plt.rc('ps', fonttype=42)  # postscript

        # Set the plot to be $\LaTeXe{}$-like
        font_size = 8
        plt.rc('axes', titlepad=3)  # Set a little space around the title
        plt.rc('font', **{'family': 'STIXGeneral'})  # Set the typeface to stix
        plt.rc('mathtext', fontset='stix')  # Set all math font to stix
        plt.rc('text', usetex=False)

        plt_thick = 0.4
        plt.rc('lines', linewidth=0.8)
        plt.rc('axes', linewidth=plt_thick)

    def __make_axes(self):
        data_axis = self.__add_ax(self.__fig, 0.05, 0.95, 5 / 8, 7 / 8)
        geo_axis = self.__add_ax(self.__fig, 0.05, 0.95, 1 / 4 + 3 / 32,
                                 5 / 8 - 1 / 32)
        lt_axis = self.__add_ax(self.__fig, 0.05, 0.45, 3 / 16, 1 / 4 + 1 / 16)
        sza_axis = self.__add_ax(self.__fig, 0.525, 0.9, 3 / 16,
                                 1 / 4 + 1 / 16)
        ea_axis = self.__add_ax(self.__fig, 0.05, 0.45, 1 / 32, 1 / 32 + 1 / 8)
        pa_axis = self.__add_ax(self.__fig, 0.525, 0.9, 1 / 32, 1 / 32 + 1 / 8)

        return {'data': data_axis,
                'geography': geo_axis,
                'local_time': lt_axis,
                'solar_zenith_angle': sza_axis,
                'emission_angle': ea_axis,
                'phase_angle': pa_axis}

    def __add_ax(self, fig, hmin: float, hmax: float, vmin: float,
                 vmax: float) -> plt.axis:
        axis = fig.add_subplot(1, 1, 1)
        axis.set_position(Bbox([[hmin, vmin], [hmax, vmax]]))
        axis.set_facecolor((0, 0, 0, 1))
        self.__turn_off_ticks(axis)
        self.__set_axis_limits(axis)
        return axis

    @staticmethod
    def __turn_off_ticks(axis: plt.Axes) -> None:
        axis.set_xticks([])
        axis.set_yticks([])

    def __set_axis_limits(self, axis: plt.Axes) -> None:
        axis.set_xlim(0, self.__slit_width * (self.__swath_numbers[-1] + 1))
        axis.set_ylim(60, 120)

    def __fill_plots(self) -> None:
        #self.__fill_data_axis()
        self.__fill_local_time_axis()
        self.__fill_solar_zenith_angle_axis()
        self.__fill_emission_angle_axis()
        self.__fill_phase_angle_axis()

    def __fill_data_axis(self) -> None:
        ql = Quicklook(self.__files, self.__axes['data'], self.__swath_numbers,
                       self.__flip)
        ql.histogram_equalize_dayside(self.__flatfield)

    def __fill_local_time_axis(self) -> None:
        lt_axis = self.__axes['local_time']
        ql = Quicklook(self.__files, lt_axis, self.__swath_numbers, self.__flip)
        img = ql.fill_local_time()

        ticks = np.linspace(6, 18, num=13, dtype='int')
        tick_labels = np.where(ticks % 3, '', ticks)
        self.__add_colorbar(img, lt_axis, ticks, 'Local Time [hours]', tick_labels)

    def __fill_solar_zenith_angle_axis(self) -> None:
        sza_axis = self.__axes['solar_zenith_angle']
        ql = Quicklook(self.__files, sza_axis, self.__swath_numbers, self.__flip)
        img = ql.fill_solar_zenith_angle()

        ticks = np.linspace(0, 180, num=19, dtype='int')
        tick_labels = np.where(ticks % 30, '', ticks)
        self.__add_colorbar(img, sza_axis, ticks, 'Solar Zenith Angle [degrees]', tick_labels)

    def __fill_emission_angle_axis(self) -> None:
        ea_axis = self.__axes['emission_angle']
        ql = Quicklook(self.__files, ea_axis, self.__swath_numbers, self.__flip)
        img = ql.fill_emission_angle()

        ticks = np.linspace(0, 90, num=10, dtype='int')
        tick_labels = np.where(ticks % 15, '', ticks)
        self.__add_colorbar(img, ea_axis, ticks, 'Emission Angle [degrees]', tick_labels)

    def __fill_phase_angle_axis(self) -> None:
        pa_axis = self.__axes['phase_angle']
        ql = Quicklook(self.__files, pa_axis, self.__swath_numbers, self.__flip)
        img = ql.fill_phase_angle()

        ticks = np.linspace(0, 180, num=19, dtype='int')
        tick_labels = np.where(ticks % 30, '', ticks)
        self.__add_colorbar(img, pa_axis, ticks, 'Phase Angle [degrees]', tick_labels)

    @staticmethod
    def __add_colorbar(img, ax: plt.Axes, ticks: np.ndarray, label: str,
                       tick_labels: np.ndarray) -> None:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        #cbar = plt.colorbar(img, cax=cax, ticks=ticks)
        cbar = plt.colorbar(img, cax=cax)
        cbar.set_ticks(ticks)
        cbar.set_ticklabels(tick_labels)
        cbar.ax.tick_params(labelsize=6)
        cbar.set_label(label, fontsize=6)

    @staticmethod
    def savefig(location: str) -> None:
        plt.savefig(location, dpi=300)


# TODO: get properties from data (method)
# TODO: get properties from database (method)
class ApoapseMUVQuicklookCreator:
    def __init__(self) -> None:
        self.__save_name = 'mvn_iuv_ql_apoapse-orbit00000-muv.png'

    def process_quicklook(self, data_location: str, flatfield_location: str,
                          orbit: int, swath, flip, savelocation: str):
        files = FileFinder(data_location).soschob(orbit, segment='apoapse',
                                                  channel='muv')
        flatfield = np.load(flatfield_location)
        ql = ApoapseMUVQuicklook(files, flatfield, swath, flip)
        ql.savefig(os.path.join(
            savelocation, self.__save_name.replace('00000', orbit_code(orbit))))


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

    def fill_local_time(self):
        for c, f in enumerate(self.__files.filenames):
            l1b = L1bDataContents(f)
            lt = np.where(l1b.altitude[:, :, 4] != 0, np.nan, l1b.local_time)
            X, Y = self.__make_plot_grid(l1b, self.__swath_numbers[c])
            img = self.__ax.pcolormesh(X, Y, lt, cmap='twilight_shifted', vmin=6, vmax=18)
        return img

    def fill_solar_zenith_angle(self):
        for c, f in enumerate(self.__files.filenames):
            l1b = L1bDataContents(f)
            sza = np.where(l1b.altitude[:, :, 4] != 0, np.nan, l1b.solar_zenith_angle)
            X, Y = self.__make_plot_grid(l1b, self.__swath_numbers[c])
            img = self.__ax.pcolormesh(X, Y, sza, cmap='cividis_r', vmin=0, vmax=180)
        return img

    def fill_emission_angle(self):
        for c, f in enumerate(self.__files.filenames):
            l1b = L1bDataContents(f)
            ea = np.where(l1b.altitude[:, :, 4] != 0, np.nan, l1b.emission_angle)
            X, Y = self.__make_plot_grid(l1b, self.__swath_numbers[c])
            img = self.__ax.pcolormesh(X, Y, ea, cmap='cividis_r', vmin=0, vmax=90)
        return img

    def fill_phase_angle(self):
        for c, f in enumerate(self.__files.filenames):
            l1b = L1bDataContents(f)
            pa = np.where(l1b.altitude[:, :, 4] != 0, np.nan, l1b.phase_angle)
            X, Y = self.__make_plot_grid(l1b, self.__swath_numbers[c])
            img = self.__ax.pcolormesh(X, Y, pa, cmap='cividis_r', vmin=0, vmax=180)
        return img

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
        return X, Y

    @staticmethod
    def __make_plot_fill(file: L1bDataContents) -> np.ndarray:
        return np.where(file.altitude[:, :, 4] != 0, np.nan, 1)

    def __plot_custom_primary(self, X, Y, fill, colors) -> None:
        img = self.__ax.pcolormesh(X, Y, fill, color=colors, linewidth=0,
                                   edgecolors='none')
        img.set_array(None)


if __name__ == '__main__':
    pa = '/media/kyle/Samsung_T5/IUVS_data'
    ff = '/home/kyle/repos/pyuvs/aux/flatfield133.npy'
    saveloc = '/home/kyle'

    a = ApoapseMUVQuicklookCreator()
    swaths = [0, 0, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5]
    a.process_quicklook(pa, ff, 3453, swaths, False, saveloc)
