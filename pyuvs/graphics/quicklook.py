import os

from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
from pyuvs.files import FileFinder, DataFilenameCollection
from pyuvs.misc import get_project_path
from pyuvs.l1b.data_contents import L1bDataContents
from pyuvs.l1b.data_classifier import DataClassifier


class Quicklook:
    def __init__(self, n_swaths: int) -> None:
        self.__n_swaths = n_swaths

    def make_standard_ql(self, data_path: str, orbit: int):
        files = FileFinder(data_path).soschob(orbit, segment='apoapse', channel='muv')
        self.__draw_standard_ql()

        coloring = Coloring(files)
        pixels = coloring.downselect_data()
        red_cutoffs = coloring.get_histogram_equalization_cutoffs(pixels[:, 0])
        green_cutoffs = coloring.get_histogram_equalization_cutoffs(pixels[:, 1])
        blue_cutoffs = coloring.get_histogram_equalization_cutoffs(pixels[:, 2])

        for f in files.filenames:
            coadded_dns = coloring.coadd_primary(f)

            coadded_dns[:, :, 0] = coloring.dn_to_rgb(coadded_dns[:, :, 0], red_cutoffs)
            coadded_dns[:, :, 1] = coloring.dn_to_rgb(coadded_dns[:, :, 1], green_cutoffs)
            coadded_dns[:, :, 2] = coloring.dn_to_rgb(coadded_dns[:, :, 2], blue_cutoffs)

            # For reasons unknown pcolormesh wants an array that's the shape (n_pixels, 3)
            colored_data = np.reshape(coadded_dns, (coadded_dns.shape[0] * coadded_dns.shape[1], coadded_dns.shape[2]))

            when I get back I'm on the make plot fill and make plot grid


        # Add banner
        # Add dayside
        # add nightside
        # Add geometry
        # add Local time
        # add sza
        # add ea
        # add pa

    def __draw_standard_ql(self, bg_color=(0, 0, 0, 1)):

        fig = plt.figure(figsize=(5, 10))

        ql_axis = self.__add_ax(fig, 0.05, 0.95, 5/8, 7/8, bg_color=bg_color)
        geo_axis = self.__add_ax(fig, 0.05, 0.95, 1/4 + 3/32, 5/8-1/32, bg_color=bg_color)
        lt_axis = self.__add_ax(fig, 0.05, 0.475, 3/16, 1/4+1/16, bg_color=bg_color)
        sza_axis = self.__add_ax(fig, 0.525, 0.95, 3/16, 1/4+1/16, bg_color=bg_color)
        ea_axis = self.__add_ax(fig, 0.05, 0.475, 1/32, 1/32+1/8, bg_color=bg_color)
        pa_axis = self.__add_ax(fig, 0.525, 0.95, 1/32, 1/32+1/8, bg_color=bg_color)

    def __add_ax(self, fig, hmin: float, hmax: float, vmin: float, vmax: float,
                 bg_color=(0, 0, 0, 1)) -> plt.axis:

        axis = fig.add_subplot(1, 1, 1)
        axis.set_position(Bbox([[hmin, vmin], [hmax, vmax]]))
        axis.set_facecolor(bg_color)
        self.__turn_off_ticks(axis)
        self.__set_axis_limits(axis)

        return axis

    @staticmethod
    def __turn_off_ticks(axis) -> None:
        axis.set_xticks([])
        axis.set_yticks([])

    def __set_axis_limits(self, axis):
        slit_width = 10.64
        axis.set_xlim(0, slit_width * self.__n_swaths)
        axis.set_ylim(60, 120)

    @staticmethod
    def savefig(location):
        plt.savefig(location, dpi=300)

    '''@staticmethod
    def __make_solid_text() -> None:
        # Make sure the typeface isn't outlined when saved as a .pdf
        plt.rc('pdf', fonttype=42)  # ???
        plt.rc('ps', fonttype=42)  # postscript

    def __set_font_stuff(self, text_color) -> None:
        """
        Parameters
        ----------
        text_color
            The rbg tuple to make the text

        """
        plt.rc('font', size=self.__font_size)
        plt.rc('axes', titlesize=self.__font_size)
        plt.rc('axes', labelsize=self.__font_size)
        plt.rc('axes', titlepad=3)  # Set a little space around the title
        plt.rc('figure', titlesize=self.__font_size)
        plt.rc('font', **{'family': 'STIXGeneral'})  # Set the typeface to stix
        plt.rc('mathtext', fontset='stix')  # Set all math font to stix
        plt.rc('text', usetex=False)
        plt.rc('text', color=text_color)

    def __set_border_thickness(self) -> None:
        plt.rc('lines', linewidth=0.8)
        plt.rc('axes', linewidth=0.4)
        plt.rcParams.update({'font.size': self.__font_size})

    def __set_quicklook_rc_params(self, text_color):
        self.__make_solid_text()
        self.__set_font_stuff(text_color)
        self.__set_border_thickness()'''


class Coloring:
    def __init__(self, files: DataFilenameCollection) -> None:
        self.__files = files

    def downselect_data(self, min_lat=-90, max_lat=90, min_lon=0, max_lon=360, min_sza=0, max_sza=102):
        flatfield = self.__load_flatfield()
        red_pixels = []
        green_pixels = []
        blue_pixels = []
        for f in self.__files.filenames:
            df = L1bDataContents(f)
            dc = DataClassifier(f)
            if not dc.dayside():
                continue

            primary = df.primary / flatfield
            trimmed_rows, trimmed_cols = np.where(
                (df.altitude == 0) &
                (df.solar_zenith_angle > min_sza) &
                (df.solar_zenith_angle < max_sza) &
                (df.latitude > min_lat) &
                (df.latitude < max_lat) &
                (df.longitude > min_lon) &
                (df.longitude < max_lon))

            # TODO: dynamically choose the indices
            red_pixels.append(np.ravel(np.sum(primary[trimmed_rows, trimmed_cols, -6:], axis=-1)))
            green_pixels.append(np.ravel(np.sum(primary[trimmed_rows, trimmed_cols, 6:-6], axis=-1)))
            blue_pixels.append(np.ravel(np.sum(primary[trimmed_rows, trimmed_cols, :6], axis=-1)))

        red = np.concatenate(red_pixels).ravel()
        green = np.concatenate(green_pixels).ravel()
        blue = np.concatenate(blue_pixels).ravel()
        colors = np.zeros((len(red), 3))
        colors[:, 0] = red
        colors[:, 1] = green
        colors[:, 2] = blue
        return colors

    def coadd_primary(self, data_contents):
        flatfield = self.__load_flatfield()
        dc = L1bDataContents(data_contents)

        data = np.zeros((dc.n_integrations, dc.n_positions, 3))
        primary = dc.primary / flatfield

        data[:, :, 0] = np.sum(primary[:, :, -6:], axis=-1)
        data[:, :, 1] = np.sum(primary[:, :, 6:-6], axis=-1)
        data[:, :, 2] = np.sum(primary[:, :, :6], axis=-1)

        return data

    @staticmethod
    def dn_to_rgb(coadded_data: np.ndarray, cutoffs: np.ndarray):
        for i in range(coadded_data.shape[0]):
            for j in range(coadded_data.shape[1]):
                if np.isnan(coadded_data[i, j]):
                    coadded_data[i, j] = 0
                    continue
                else:
                    position_color = np.searchsorted(cutoffs, coadded_data[i, j])

                if position_color > 255:
                    coadded_data[i, j] = 255
                else:
                    coadded_data[i, j] = position_color

        return coadded_data / 255.

    @staticmethod
    def __load_flatfield():
        # TODO: choose the correct flatfield
        return np.load(os.path.join(get_project_path(), 'aux', 'flatfield133.npy'))

    @staticmethod
    def get_histogram_equalization_cutoffs(colors: np.ndarray, low_percentile: float = 1, high_percentile: float = 99):
        """

        Parameters
        ----------
        colors
            1D array
        low_percentile
        high_percentile

        Returns
        -------

        """
        # Get the minimum index of the color channel where the DN value is positive
        sorted_dn = np.sort(colors)

        # Do this if I want to set 0 DNs to be the lower range of my scale
        # minimum_dn_index = np.where(color_array > 0)[0][0]     # np.where needs the dreaded [0][0] to get a scalar out
        n_pixels = len(sorted_dn)
        minimum_dn_index = int(low_percentile * n_pixels / 100)
        maximum_dn_index = int(high_percentile * n_pixels / 100)

        color_array = sorted_dn[minimum_dn_index:maximum_dn_index]
        n_good_pixels = len(color_array)

        # Find the cutoff DNs for what is each color in each color channel
        color = np.linspace(0, 1, num=256)

        return np.array([color_array[int(color[i] * (n_good_pixels - 1))] for i in range(256)])




if __name__ == '__main__':
    ql = Quicklook(8)
    ql.make_standard_ql('/media/kyle/Samsung_T5/IUVS_data', 3453)
    #ql.savefig('/home/kyle/qltest.png')
