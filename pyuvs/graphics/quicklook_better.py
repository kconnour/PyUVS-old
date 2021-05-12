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
from pyuvs.constants import slit_width


class Colormaps:
    """ Make an object to hold predefined colormaps.

    """
    def __init__(self) -> None:
        self.__cmap = None
        self.__norm = None

    def set_magnetic_field(self) -> None:
        self.__cmap = plt.get_cmap('Blues_r')
        self.__norm = colors.Normalize(vmin=0, vmax=1)

    def set_local_time(self) -> None:
        self.__cmap = plt.get_cmap('twilight_shifted')
        self.__norm = colors.Normalize(vmin=6, vmax=18)

    def set_solar_zenith_angle(self) -> None:
        self.__cmap = plt.get_cmap('cividis_r')
        self.__norm = colors.Normalize(vmin=0, vmax=180)

    # TODO: surely this can be cleaner...
    def set_emission_angle(self) -> None:
        self.__cmap = colors.LinearSegmentedColormap.from_list(
            'cividis_half', copy.copy(plt.get_cmap('cividis_r'))
            (np.linspace(0, 0.5, 256)))
        self.__norm = colors.Normalize(vmin=0, vmax=90)

    def set_phase_angle(self) -> None:
        self.__cmap = plt.get_cmap('cividis_r')
        self.__norm = colors.Normalize(vmin=0, vmax=180)

    @property
    def cmap(self):
        return self.__cmap

    @property
    def norm(self):
        return self.__norm


class Colorbar:
    """Fill a colorbar. Add methods to add more info to it

    """
    def __init__(self, axis, cmap, norm):
        self.__axis = axis
        self.__cmap = cmap
        self.__norm = norm
        self.__colorbar = self.__make_colorbar()

    def __make_colorbar(self):
        data_sm = plt.cm.ScalarMappable(cmap=self.__cmap, norm=self.__norm)
        data_sm.set_array(np.array([]))
        return plt.colorbar(data_sm, cax=self.__axis)

    def set_label(self, label: str) -> None:
        self.__colorbar.set_label(label)

    def add_major_ticks(self, major_ticks: float) -> None:
        self.__colorbar.ax.yaxis.set_major_locator(
            ticker.MultipleLocator(major_ticks))

    def add_minor_ticks(self, minor_ticks: float) -> None:
        self.__colorbar.ax.yaxis.set_minor_locator(
            ticker.MultipleLocator(minor_ticks))


class QuicklookColorbarBundle:
    """Bundle together QL and its colorbar. Add methods to fill them.

    """
    def __init__(self, quicklook_ax: plt.Axes, colorbar_ax: plt.Axes) -> None:
        self.__quicklook_ax = quicklook_ax
        self.__colorbar_ax = colorbar_ax

    def fill_magnetic_field(self, files: DataFilenameCollection,
                            swath_number: list[int], flip: bool, spice_directory) -> None:
        cmap = Colormaps()
        cmap.set_magnetic_field()

        #ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        #ql.fill_magnetic_field(spice_directory, cmap, norm)

        cbar = Colorbar(self.__colorbar_ax, cmap.cmap, cmap.norm)
        cbar.set_label('Closed field line probability')
        cbar.add_major_ticks(0.2)
        cbar.add_minor_ticks(0.05)

    def fill_local_time(self, files: DataFilenameCollection,
                        swath_number: list[int], flip: bool) -> None:
        cmap = Colormaps()
        cmap.set_local_time()

        #ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        #ql.fill_local_time(cmap, norm)

        cbar = Colorbar(self.__colorbar_ax, cmap.cmap, cmap.norm)
        cbar.set_label('Local Time [hours]')
        cbar.add_major_ticks(3)
        cbar.add_minor_ticks(1)

    def fill_solar_zenith_angle(self, files: DataFilenameCollection,
                                swath_number: list[int], flip: bool) -> None:
        cmap = Colormaps()
        cmap.set_solar_zenith_angle()

        #ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        #ql.fill_local_time(cmap, norm)

        cbar = Colorbar(self.__colorbar_ax, cmap.cmap, cmap.norm)
        cbar.set_label(r'Solar Zenith Angle [$\degree$]')
        cbar.add_major_ticks(30)
        cbar.add_minor_ticks(10)

    def fill_emission_angle(self, files: DataFilenameCollection,
                            swath_number: list[int], flip: bool) -> None:
        cmap = Colormaps()
        cmap.set_emission_angle()

        #ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        #ql.fill_local_time(cmap, norm)

        cbar = Colorbar(self.__colorbar_ax, cmap.cmap, cmap.norm)
        cbar.set_label(r'Emission Angle [$\degree$]')
        cbar.add_major_ticks(15)
        cbar.add_minor_ticks(5)

    def fill_phase_angle(self, files: DataFilenameCollection,
                         swath_number: list[int], flip: bool) -> None:
        cmap = Colormaps()
        cmap.set_phase_angle()

        #ql = Quicklook(files, self.__quicklook_ax, swath_number, flip)
        #ql.fill_local_time(cmap, norm)

        cbar = Colorbar(self.__colorbar_ax, cmap.cmap, cmap.norm)
        cbar.set_label(r'Phase Angle [$\degree$]')
        cbar.add_major_ticks(30)
        cbar.add_minor_ticks(10)
