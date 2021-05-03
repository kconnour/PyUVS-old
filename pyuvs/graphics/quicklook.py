"""

"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
from pyuvs.files import FileFinder, DataFilenameCollection, orbit_code
from pyuvs.l1b.data_contents import L1bDataContents
from pyuvs.l1b.data_classifier import DataClassifier
from pyuvs.graphics.coloring import HistogramEqualizer
from pyuvs.l1b.pixel_corners import PixelCorners

# TODO: Add ability to choose spectral indices in HistogramEqualizer
# TODO: this breaks on a single integration
# TODO: should HEQ break if I try to apply the coloring to a file that didn't
#  make the coloring?


class ApoapseMUVQuicklook:
    def __init__(self, files: DataFilenameCollection, flatfield: np.ndarray,
                 swath_numbers: list[int], flip: bool) -> None:
        self.__files = files
        self.__flatfield = flatfield
        self.__swath_numbers = swath_numbers
        self.__flip = flip
        self.__slit_width = 10.64

        self.__fig = plt.figure(figsize=(5, 10))
        self.__axes = self.__make_axes()
        self.__fill_plots()

    def __make_axes(self):
        data_axis = self.__add_ax(self.__fig, 0.05, 0.95, 5 / 8, 7 / 8)
        geo_axis = self.__add_ax(self.__fig, 0.05, 0.95, 1 / 4 + 3 / 32,
                                 5 / 8 - 1 / 32)
        lt_axis = self.__add_ax(self.__fig, 0.05, 0.475, 3 / 16, 1 / 4 + 1 / 16)
        sza_axis = self.__add_ax(self.__fig, 0.525, 0.95, 3 / 16,
                                 1 / 4 + 1 / 16)
        ea_axis = self.__add_ax(self.__fig, 0.05, 0.475, 1 / 32, 1 / 32 + 1 / 8)
        pa_axis = self.__add_ax(self.__fig, 0.525, 0.95, 1 / 32, 1 / 32 + 1 / 8)

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
    def __turn_off_ticks(axis) -> None:
        axis.set_xticks([])
        axis.set_yticks([])

    def __set_axis_limits(self, axis):
        axis.set_xlim(0, self.__slit_width * (self.__swath_numbers[-1] + 1))
        axis.set_ylim(60, 120)

    def __fill_plots(self):
        #self.__fill_data_axis()
        #print('done with data')
        self.__fill_local_time_axis()

    def __fill_data_axis(self):
        ql = DaysideQuicklook(self.__files, self.__flatfield,
                              self.__axes['data'], self.__swath_numbers,
                              self.__flip)
        ql.histogram_equalize()

    def __fill_local_time_axis(self) -> None:
        ql = DaysideQuicklook(self.__files, self.__flatfield,
                              self.__axes['local_time'], self.__swath_numbers,
                              self.__flip)
        ql.fill_with_local_time('twilight_shifted', 6, 18)

    @staticmethod
    def savefig(location):
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


class DaysideQuicklook:
    """Put a quicklook-style plot in an axis.

    Quicklook has methods to add a quicklook to an axis.

    """
    def __init__(self, files: DataFilenameCollection, flatfield: np.ndarray,
                 ax, swath_numbers: list[int], flip: bool):
        """
        Parameters
        ----------
        files
            A collection of files to plot a quicklook for.
        flatfield
            The flatfield for the files.
        ax
            The axis to put the quicklook into.
        swath_numbers
            The swath numbers for each of the swaths in the files.
        flip
            Denote whether the files were beta-angle flipped.

        """
        self.__files = files
        self.__flatfield = flatfield
        self.__ax = ax
        self.__swath_numbers = swath_numbers
        self.__flip = flip
        self.__slit_width = 10.64

    def histogram_equalize(self, min_lat: float = -90, max_lat: float = 90,
                 min_lon: float = 0, max_lon: float = 360,
                 min_sza: float = 0, max_sza: float = 102,
                 low_percentile: float = 1, high_percentile: float = 99) \
            -> None:
        """ Make a quicklook with histogram equalization.

        Parameters
        ----------
        min_lat
        max_lat
        min_lon
        max_lon
        min_sza
        max_sza
        low_percentile
        high_percentile

        """
        heq = HistogramEqualizer(
            self.__files, self.__flatfield, min_lat, max_lat, min_lon, max_lon,
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

    @staticmethod
    def __reshape_data_for_pcolormesh(colors) -> np.ndarray:
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
        fill = np.ones((file.n_integrations, file.n_positions))
        fill[np.where(file.altitude[:, :, 4] != 0)] = np.nan
        return fill

    def __plot_custom_primary(self, X, Y, fill, colors) -> None:
        img = self.__ax.pcolormesh(X, Y, fill, color=colors, linewidth=0,
                                   edgecolors='none')
        img.set_array(None)

    def fill_with_local_time(self, cmap: str, vmin: float, vmax: float) -> None:
        for c, f in enumerate(self.__files.filenames):
            l1b = L1bDataContents(f)
            X, Y = self.__make_plot_grid(l1b, self.__swath_numbers[c])
            corners = PixelCorners(l1b).local_time()[:, :, 0]
            self.__ax.pcolormesh(X, Y, corners, cmap=cmap, vmin=vmin, vmax=vmax)


if __name__ == '__main__':
    pa = '/media/kyle/Samsung_T5/IUVS_data'
    ff = '/home/kyle/repos/pyuvs/aux/flatfield133.npy'
    saveloc = '/home/kyle'

    a = ApoapseMUVQuicklookCreator()
    swaths = [0, 0, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5]
    a.process_quicklook(pa, ff, 3453, swaths, False, saveloc)
