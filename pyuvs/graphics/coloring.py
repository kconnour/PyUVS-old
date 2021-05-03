import numpy as np
from pyuvs.files import DataFilenameCollection
from pyuvs.l1b.data_contents import L1bDataContents
from pyuvs.l1b.data_classifier import DataClassifier


# TODO: choose spectral indices
class HistogramEqualizer:
    def __init__(self, files: DataFilenameCollection, flatfield: np.ndarray,
                 min_lat: float = -90, max_lat: float = 90,
                 min_lon: float = 0, max_lon: float = 360,
                 min_sza: float = 0, max_sza: float = 102,
                 low_percentile: float = 1, high_percentile: float = 99) \
            -> None:
        self.__files = files
        self.__flatfield = flatfield
        self.__min_lat = min_lat
        self.__max_lat = max_lat
        self.__min_lon = min_lon
        self.__max_lon = max_lon
        self.__min_sza = min_sza
        self.__max_sza = max_sza
        self.__low_percentile = low_percentile
        self.__high_percentile = high_percentile

        self.__red_start = -6
        self.__red_end = None
        self.__green_start = 6
        self.__green_end = -6
        self.__blue_start = None
        self.__blue_end = 6

        self.__cutoffs = self.__make_heq_cutoffs()

    def __make_heq_cutoffs(self) -> np.ndarray:
        coadded_dn = self.__coadd_dayside_data()
        return self.__get_histogram_equalization_cutoffs(coadded_dn)

    def __coadd_dayside_data(self) -> np.ndarray:
        return np.stack((
            self.__coadd_dayside_data_channel(
                self.__red_start, self.__red_end),
            self.__coadd_dayside_data_channel(
                self.__green_start, self.__green_end),
            self.__coadd_dayside_data_channel(
                self.__blue_start, self.__blue_end)
        ))

    # TODO: I'm unsure if this fails on a single integration... it prob does
    def __coadd_dayside_data_channel(self, start_index: int, end_index: int) \
            -> np.ndarray:
        pixels = []
        for f in self.__files.filenames:
            df = L1bDataContents(f)
            dc = DataClassifier(f)
            if not dc.dayside():
                continue

            primary = df.primary / self.__flatfield
            rows, cols = np.where(
                (df.altitude[:, :, 4] == 0) &
                (df.latitude[:, :, 4] > self.__min_lat) &
                (df.latitude[:, :, 4] < self.__max_lat) &
                (df.longitude[:, :, 4] > self.__min_lon) &
                (df.longitude[:, :, 4] < self.__max_lon) &
                (df.solar_zenith_angle > self.__min_sza) &
                (df.solar_zenith_angle < self.__max_sza))

            coadded_primary = np.sum(primary[rows, cols, start_index:end_index],
                                     axis=-1)
            pixels.append(np.ravel(coadded_primary))
        return np.concatenate(pixels).ravel()

    def __get_histogram_equalization_cutoffs(self, colors: np.ndarray) \
            -> np.ndarray:
        return np.stack((
            self.__get_histogram_equalization_channel_cutoffs(colors[0, :]),
            self.__get_histogram_equalization_channel_cutoffs(colors[1, :]),
            self.__get_histogram_equalization_channel_cutoffs(colors[2, :])
        ))

    def __get_histogram_equalization_channel_cutoffs(
            self, data_numbers_channel: np.ndarray) -> np.ndarray:
        n_pixels = data_numbers_channel.size
        sorted_dn = np.sort(data_numbers_channel)

        minimum_dn_index = int(self.__low_percentile * n_pixels / 100)
        maximum_dn_index = int(self.__high_percentile * n_pixels / 100)
        trimmed_dn = sorted_dn[minimum_dn_index: maximum_dn_index]
        n_trimmed_pixels = len(trimmed_dn)

        cutoff_ind = np.linspace(0, n_trimmed_pixels - 1, num=255, dtype='int')
        return trimmed_dn[cutoff_ind]

    def colorize_primary(self, primary: np.ndarray) -> np.ndarray:
        """Turn the primary into RGB values from [0, 255].

        Parameters
        ----------
        primary
            The primary data structure

        """
        primary = primary / self.__flatfield
        red = self.__colorize_primary_channel(
            primary, self.__red_start, self.__red_end, 0)
        green = self.__colorize_primary_channel(
            primary, self.__green_start, self.__green_end, 1)
        blue = self.__colorize_primary_channel(
            primary, self.__blue_start, self.__blue_end, 2)
        return np.stack((red, green, blue))

    # TODO: this fails on single integrations
    def __colorize_primary_channel(self, primary: np.ndarray, start: int,
                                   end: int, channel_index: int) -> np.ndarray:
        coadded_primary = np.sum(primary[:, :, start:end], axis=-1)
        return np.searchsorted(self.__cutoffs[channel_index], coadded_primary)
