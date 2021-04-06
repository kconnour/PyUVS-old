"""The spice module contains classes to load in SPICE kernels of IUVS data.
"""
import glob
import os
import re
import numpy as np
import spiceypy as spice


class Spice:
    """A collection of ways to furnish arrays.

    Spice takes the path to SPICE kernels. It provides methods to furn(i)sh
    relevant kernels.

    """
    def __init__(self) -> None:
        """

        Notes
        -----
        The kernels can be found online at the
        `NAIF <https://naif.jpl.nasa.gov/pub/naif/MAVEN/kernels/>_`.

        """
        pass

    def furnish_ck(self, ck_path: str) -> None:
        """Furnish the spacecraft C-kernels, which are kernels describing the
        attitude of MAVEN and its articulated payload platform.

        Parameters
        ----------
        ck_path
            Absolute path to the directory containing the C-kernels.

        """

        self.__furnish_ck_type(ck_path, 'app')
        self.__furnish_ck_type(ck_path, 'sc')

        f = glob.glob(os.path.join(ck_path, 'mvn_iuv_all_l0_20*.bc'))
        if len(f) > 0:
            self.__furnish_array(self.__find_latest_kernel(f, 4))
        else:
            print('No ck kernels found.')

    def furnish_spk(self, spk_path: str) -> None:
        """Furnish the spacecraft spk kernels (ephemeris data of its location).

        Parameters
        ----------
        spk_path
            Absolute path to the directory containing spk kernels.

        """
        spk_kernels = glob.glob(os.path.join(spk_path, 'trj_orb_*-*_rec*.bsp'))

        if len(spk_kernels) > 0:
            rec, _ = self.__find_latest_kernel(spk_kernels, 3, getlast=True)
            self.__furnish_array(rec)
        else:
            print('No spk kernels found.')

    def furnish_sclk(self, sclk_path) -> None:
        """Furnish the spacecraft sclk kernels (the spacecraft clock).

        Parameters
        ----------
        sclk_path
            Absolute path to the directory containing sclk kernels.

        """
        tsc_path = os.path.join(sclk_path, 'MVN_SCLKSCET.0*.tsc')
        clock_kernels = sorted(glob.glob(tsc_path))
        self.__furnish_array(clock_kernels)

    def load_spice(self, spice_directory: str) -> None:
        """Load all of the kernels typically required by IUVS observations.

        Parameters
        ----------
        spice_directory
            Absolute path to the directory where SPICE files live.

        Notes
        -----
        The SPICE kernels are assumed to have a directory structure consistent
        with the IUVS standard, outlined below.

        spice_directory
        |---mvn
        |   |---ck
        |   |---spk
        |   |---sclk
        |---generic_kernels
        |   |---spk
        |   |   |mar097.bsp

        This method will clear all currently existing kernels before loading in
        IUVS kernels.

        """
        mvn_kernel_path = os.path.join(spice_directory, 'mvn')
        generic_kernel_path = os.path.join(spice_directory, 'generic_kernels')
        ck_path = os.path.join(mvn_kernel_path, 'ck')
        spk_path = os.path.join(mvn_kernel_path, 'spk')
        sclk_path = os.path.join(mvn_kernel_path, 'sclk')
        generic_spk_path = os.path.join(generic_kernel_path, 'spk')

        self.__clear_existing_kernels()

        # TODO: I have absolutely no idea why we need to call the pool method. I
        #  think we should just need to furnish them
        self.__pool_and_furnish(mvn_kernel_path, 'mvn')
        self.__pool_and_furnish(generic_kernel_path, 'generic')

        self.furnish_ck(ck_path)
        self.furnish_spk(spk_path)
        self.furnish_sclk(sclk_path)
        self.__furnish_mars(generic_spk_path)

    def __furnish_ck_type(self, ck_path: str, kernel_type: str) -> None:
        longterm_kernels, lastlong = \
            self.__find_long_term_kernels(ck_path, kernel_type)

        daily_kernels, lastday = \
            self.__find_daily_kernels(ck_path, kernel_type, lastlong)

        normal_kernels = \
            self.__find_normal_kernels(ck_path, kernel_type, lastday)

        self.__furnish_array(normal_kernels)
        self.__furnish_array(daily_kernels)
        self.__furnish_array(longterm_kernels)

    # TODO: -> list[str] | str in 3.10
    def __find_long_term_kernels(self, ck_path: str, kernel_type: str):
        kern_path = os.path.join(ck_path, f'mvn_{kernel_type}_rel_*.bc')
        f = glob.glob(kern_path)

        if len(f) > 0:
            longterm_kernels, lastlong = \
                self.__find_latest_kernel(f, 4, getlast=True)
        else:
            longterm_kernels, lastlong = None, None
        return longterm_kernels, lastlong

    # TODO: -> list[str] | str in 3.10
    def __find_daily_kernels(self, ck_path: str, kernel_type: str,
                             lastlong: str):
        kern_path = os.path.join(ck_path, f'mvn_{kernel_type}_red_*.bc')
        f = glob.glob(kern_path)

        if len(f) > 0:
            day, lastday = \
                self.__find_latest_kernel(f, 3, after=lastlong, getlast=True)
        else:
            day, lastday = None, None
        return day, lastday

    def __find_normal_kernels(self, ck_path: str, kernel_type: str,
                              lastday: str) -> list[str]:
        kern_path = os.path.join(ck_path, f'mvn_{kernel_type}_rec_*.bc')
        f = glob.glob(kern_path)

        if len(f) > 0:
            norm = self.__find_latest_kernel(f, 3, after=lastday)
        else:
            norm = []
        return norm

    @staticmethod
    def __furnish_array(kernels: list[str]) -> None:
        [spice.furnsh(k) for k in kernels]

    # TODO: I think this can be greatly simplified, but I can't understand
    #  what it does exactly
    @staticmethod
    def __find_latest_kernel(filenames: list[str], part: int,
                             getlast: bool = False, after: str = None):
        # sort the list in reverse order so the most recent kernel appears first
        # in a subset of kernels
        filenames.sort(reverse=True)

        # extract the filenames without their version number
        filetag = [os.path.basename(f).split("_v")[0] for f in filenames]

        # without version numbers, there are many repeated filenames, so find a
        # single entry for each kernel
        uniquetags, uniquetagindices = np.unique(filetag, return_index=True)

        # make a list of the kernels with one entry per kernel
        fnamelist = np.array(filenames)[uniquetagindices]

        # extract the date portions of the kernel file paths
        datepart = [re.split('[-_]', os.path.basename(fname))[part]
                    for fname in fnamelist]

        # find the individual dates
        uniquedates, uniquedateindex = np.unique(datepart, return_index=True)

        # extract the finald ate
        last = uniquedates[-1]

        # if a date is chosen for after, then include only the latest kernels
        # after the specified date
        if after is not None:
            retlist = [f for f, d in zip(
                fnamelist, datepart) if int(d) >= int(after)]

        # otherwise, return all the latest kernels
        else:
            retlist = [f for f, d in zip(fnamelist, datepart)]

        # if user wants, return also the date of the last of the latest kernels
        if getlast:
            return retlist, last

        # otherwise return just the latest kernels
        else:
            return retlist

    @staticmethod
    def __clear_existing_kernels() -> None:
        spice.kclear()

    def __pool_and_furnish(self, kernel_path: str, tm: str) -> None:
        split_path = self.__split_string_into_length(kernel_path, 78)
        spice.pcpool('PATH_VALUES', split_path)
        tm_path = os.path.join(kernel_path, f'{tm}.tm')
        spice.furnsh(tm_path)

    @staticmethod
    def __split_string_into_length(string: str, length: int) -> list[str]:
        # Turn a string into a list of strings that have a maximum length. This
        # is needed since spice can only handle strings of at most length 80.
        return [string[i: i+length] for i in range(0, len(string), length)]

    @staticmethod
    def __furnish_mars(mars_path: str) -> None:
        mars_kernel = os.path.join(mars_path, 'mar097.bsp')
        spice.furnsh(mars_kernel)
