"""

"""
import copy
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.ticker as ticker
from pyuvs.files import FileFinder, DataFilenameCollection, orbit_code
from pyuvs.l1b.data_contents import L1bDataContents
from pyuvs.l1b.data_classifier import DataClassifier
from pyuvs.graphics.coloring import HistogramEqualizer


# TODO: get properties from data (method)
# TODO: get properties from database (method)
class ApoapseMUVQuicklookCreator:
    def __init__(self) -> None:
        self.__save_name = 'mvn_iuv_ql_apoapse-orbit00000-muv-TEST.png'

    def process_quicklook(self, data_location: str, flatfield_location: str,
                          orbit: int, swath, flip, savelocation: str):
        files = FileFinder(data_location).soschob(orbit, segment='apoapse',
                                                  channel='muv')
        flatfield = np.load(flatfield_location)
        ql = ApoapseMUVQuicklook(files, flatfield, swath, flip)
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
                 swath_numbers: list[int], flip: bool) -> None:
        self.__files = files
        self.__flatfield = flatfield
        self.__swath_numbers = swath_numbers
        self.__flip = flip
        self.__slit_width = 10.64

        self.__set_quicklook_rc_params()
        self.__axes = self.__setup_axes()
        self.__fill_plots()

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

    def __setup_axes(self):
        axes = self.__setup_fig_and_axes()
        self.__turn_off_frame(axes['text'])
        for key in axes.keys():
            self.__turn_off_ticks(axes[key])
            self.__set_axis_limits(axes[key])
            self.__set_background_black(axes[key])
        return axes

    def __setup_fig_and_axes(self):
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

        gs = axes[0, 0].get_gridspec()
        [ax.remove() for ax in axes[0, :]]
        fig.add_subplot(gs[0, :])

        for row in [1, 2]:
            gs = axes[row, 0].get_gridspec()
            [ax.remove() for ax in axes[row, :3]]
            fig.add_subplot(gs[row, :3])

        return self.__create_axis_dict(fig.axes)

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
        self.__setup_local_time_colorbar()
        lt_axis = self.__axes['local_time']
        ql = Quicklook(self.__files, lt_axis, self.__swath_numbers, self.__flip)
        ql.fill_local_time()

    def __setup_local_time_colorbar(self):
        lt_cbar_axis = self.__axes['local_time_colorbar']
        cmap = 'twilight_shifted'
        norm = colors.Normalize(vmin=6, vmax=18)
        label = 'Local Time [hours]'
        lt_cbar = self.__setup_colorbar(lt_cbar_axis, cmap, norm, label)
        lt_cbar.ax.yaxis.set_major_locator(ticker.MultipleLocator(3))
        lt_cbar.ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))

    def __fill_solar_zenith_angle_axis(self) -> None:
        self.__setup_solar_zenith_angle_colorbar()
        sza_axis = self.__axes['solar_zenith_angle']
        ql = Quicklook(self.__files, sza_axis, self.__swath_numbers, self.__flip)
        ql.fill_solar_zenith_angle()

    def __setup_solar_zenith_angle_colorbar(self):
        sza_cbar_axis = self.__axes['solar_zenith_angle_colorbar']
        cmap = 'cividis_r'
        norm = colors.Normalize(vmin=0, vmax=180)
        label = 'Solar Zenith Angle [$\degree$]'
        sza_cbar = self.__setup_colorbar(sza_cbar_axis, cmap, norm, label)
        sza_cbar.ax.yaxis.set_major_locator(ticker.MultipleLocator(30))
        sza_cbar.ax.yaxis.set_minor_locator(ticker.MultipleLocator(10))

        # TODO: this is how to add cbar lines
        # sza_cbar.ax.axhline()

    def __fill_emission_angle_axis(self) -> None:
        self.__setup_emission_angle_colorbar()
        ea_axis = self.__axes['emission_angle']
        ql = Quicklook(self.__files, ea_axis, self.__swath_numbers, self.__flip)
        ql.fill_emission_angle()

    def __setup_emission_angle_colorbar(self):
        ea_cbar_axis = self.__axes['emission_angle_colorbar']
        # TODO: copy this cmap and place it in the EA plotting axis
        cmap = colors.LinearSegmentedColormap.from_list('cividis_half', copy.copy(plt.get_cmap('cividis_r'))(np.linspace(0, 0.5, 256)))
        norm = colors.Normalize(vmin=0, vmax=90)
        label = 'Emission Angle [$\degree$]'
        ea_cbar = self.__setup_colorbar(ea_cbar_axis, cmap, norm, label)
        ea_cbar.ax.yaxis.set_major_locator(ticker.MultipleLocator(15))
        ea_cbar.ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))

    def __fill_phase_angle_axis(self) -> None:
        self.__setup_phase_angle_colorbar()
        pa_axis = self.__axes['phase_angle']
        ql = Quicklook(self.__files, pa_axis, self.__swath_numbers, self.__flip)
        ql.fill_phase_angle()
        
    def __setup_phase_angle_colorbar(self):
        pa_cbar_axis = self.__axes['phase_angle_colorbar']
        cmap = 'cividis_r'
        norm = colors.Normalize(vmin=0, vmax=180)
        label = 'Phase Angle [$\degree$]'
        pa_cbar = self.__setup_colorbar(pa_cbar_axis, cmap, norm, label)
        pa_cbar.ax.yaxis.set_major_locator(ticker.MultipleLocator(30))
        pa_cbar.ax.yaxis.set_minor_locator(ticker.MultipleLocator(10))

        # TODO: this is how to add cbar lines
        # sza_cbar.ax.axhline()

    @staticmethod
    def __setup_colorbar(axis, cmap, norm, label):
        data_sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        data_sm.set_array(np.array([]))
        return plt.colorbar(data_sm, cax=axis, label=label)

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

    def fill_local_time(self):
        for c, f in enumerate(self.__files.filenames):
            l1b = L1bDataContents(f)
            lt = np.where(l1b.altitude[:, :, 4] != 0, np.nan, l1b.local_time)
            X, Y = self.__make_plot_grid(l1b, self.__swath_numbers[c])
            self.__ax.pcolormesh(X, Y, lt, cmap='twilight_shifted', vmin=6, vmax=18)

    def fill_solar_zenith_angle(self):
        for c, f in enumerate(self.__files.filenames):
            l1b = L1bDataContents(f)
            sza = np.where(l1b.altitude[:, :, 4] != 0, np.nan, l1b.solar_zenith_angle)
            X, Y = self.__make_plot_grid(l1b, self.__swath_numbers[c])
            self.__ax.pcolormesh(X, Y, sza, cmap='cividis_r', vmin=0, vmax=180)

    def fill_emission_angle(self):
        for c, f in enumerate(self.__files.filenames):
            l1b = L1bDataContents(f)
            ea = np.where(l1b.altitude[:, :, 4] != 0, np.nan, l1b.emission_angle)
            X, Y = self.__make_plot_grid(l1b, self.__swath_numbers[c])
            self.__ax.pcolormesh(X, Y, ea, cmap='cividis_r', vmin=0, vmax=90)

    def fill_phase_angle(self):
        for c, f in enumerate(self.__files.filenames):
            l1b = L1bDataContents(f)
            pa = np.where(l1b.altitude[:, :, 4] != 0, np.nan, l1b.phase_angle)
            X, Y = self.__make_plot_grid(l1b, self.__swath_numbers[c])
            self.__ax.pcolormesh(X, Y, pa, cmap='cividis_r', vmin=0, vmax=180)

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


if __name__ == '__main__':
    pa = '/media/kyle/Samsung_T5/IUVS_data'
    ff = '/home/kyle/repos/pyuvs/aux/flatfield133.npy'
    saveloc = '/home/kyle'

    a = ApoapseMUVQuicklookCreator()
    swaths = [0, 0, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5]
    a.process_quicklook(pa, ff, 3453, swaths, False, saveloc)
