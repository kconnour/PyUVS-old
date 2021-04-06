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
    def __init__(self, spice_directory: str) -> None:
        """
        Parameters
        ----------
        spice_directory
            Absolute path to the location where SPICE kernels are located.

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

        """
        self.__mvn_kernel_path = os.path.join(spice_directory, 'mvn')
        self.__generic_kernel_path = \
            os.path.join(spice_directory, 'generic_kernels')

    # This was load_iuvs_spice
    def load_spice(self) -> None:
        """Load all of the kernels typically required by IUVS observations.

        Notes
        -----
        This method will clear all currently existing kernels before loading in
        IUVS kernels.

        Returns
        -------
        None

        """
        self.__clear_existing_kernels()

        # TODO: I have absolutely no idea why we need to call the pool method. I
        #  think we should just need to furnish them
        self.__pool_and_furnish(self.__mvn_kernel_path)
        self.__pool_and_furnish(self.__generic_kernel_path)

        self.load_spacecraft_attitude()
        self.__furnish_spacecraft_location()
        self.__furnish_spacecraft_clock_kernels()

        self.__furnish_mars()

    @staticmethod
    def __clear_existing_kernels() -> None:
        spice.kclear()

    def __pool_and_furnish(self, kernel_path: str) -> None:
        split_path = self.__split_string_into_length(kernel_path, 78)
        spice.pcpool('PATH_VALUES', split_path)
        tm_path = os.path.join(kernel_path, 'generic.tm')
        spice.furnsh(tm_path)

    @staticmethod
    def __split_string_into_length(string: str, length: int) -> list[str]:
        # Turn a string into a list of strings that have a maximum length. This
        # is needed since spice can only handle strings of at most length 80.
        return [string[i: i+length] for i in range(0, len(string), length)]

    def load_spacecraft_attitude(self) -> None:
        """Load the spacecraft C-kernels, which are essentially the attitude of
        the spacecraft and its articulated payload platform.

        Returns
        -------
        None

        """
        ck_path = os.path.join(self.__mvn_kernel_path, 'ck')

        # Load the APP and spacecraft orientation
        self.__load_attitude_type(ck_path, 'app')
        self.__load_attitude_type(ck_path, 'sc')

        f = glob.glob(os.path.join(ck_path, 'mvn_iuv_all_l0, 20*.bc'))
        if len(f) > 0:
            self.__furnish_array(self.__find_latest_kernel(f, 4))

    # This used to be load_sc_ck_type()
    def __load_attitude_type(self, ck_path, kernel_type) -> None:
        # Load long term kernels
        kern_path = os.path.join(ck_path, f'mvn_{kernel_type}_rel_*.bc')
        f = glob.glob(kern_path)

        if len(f) > 0:
            longterm_kernels, lastlong = self.__find_latest_kernel(f, 4, getlast=True)
        else:
            longterm_kernels, lastlong = None, None

        # Load daily kernels
        kern_path = os.path.join(ck_path, f'mvn_{kernel_type}_red_*.bc')
        f = glob.glob(kern_path)

        if len(f) > 0:
            day, lastday = self.__find_latest_kernel(f, 4, after=lastlong, getlast=True)
        else:
            day, lastday = None, None

        # Load normal kernels
        kern_path = os.path.join(ck_path, f'mvn_{kernel_type}_rec_*.bc')
        f = glob.glob(kern_path)

        if len(f) > 0:
            norm = self.__find_latest_kernel(f, 3, after=lastday)

        # Only load in the last 10 kernels
        longterm_kernels = longterm_kernels[-10:]

        self.__furnish_array(norm)
        self.__furnish_array(day)
        self.__furnish_array(longterm_kernels)





    def __furnish_spacecraft_clock_kernels(self) -> None:
        tsc_path = os.path.join(self.__mvn_kernel_path, 'sclk', 'MVN_SCLKSCET.0*.tsc')
        clock_kernels = sorted(glob.glob(tsc_path))
        self.__furnish_array(clock_kernels)



    @staticmethod
    def __furnish_array(kernels) -> None:
        [spice.furnsh(k) for k in kernels]





    @staticmethod
    def __find_latest_kernel(filenames: list[str], part: int, getlast: bool = False, after: int = None):
        # store the input filename list internally
        fnamelist = filenames

        # if the filename list is not actually a list but just a single string, convert it to a list
        if type(fnamelist) == str:
            fnamelist = [fnamelist]

        # sort the list in reverse order so the most recent kernel appears first in a subset of kernels
        fnamelist.sort(reverse=True)

        # extract the filenames without their version number
        filetag = [os.path.basename(f).split("_v")[0] for f in fnamelist]

        # without version numbers, there are many repeated filenames, so find a single entry for each kernel
        uniquetags, uniquetagindices = np.unique(filetag, return_index=True)

        # make a list of the kernels with one entry per kernel
        fnamelist = np.array(fnamelist)[uniquetagindices]

        # extract the date portions of the kernel file paths
        datepart = [re.split('[-_]', os.path.basename(fname))[part]
                    for fname in fnamelist]

        # find the individual dates
        uniquedates, uniquedateindex = np.unique(datepart, return_index=True)

        # extract the finald ate
        last = uniquedates[-1]

        # if a date is chosen for after, then include only the latest kernels after the specified date
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

    # This used to be load_sc_spk()
    def __furnish_spacecraft_location(self) -> None:
        spk_path = os.path.join(self.__mvn_kernel_path, 'spk')

        spk_kernels = glob.glob(os.path.join(spk_path, 'trj_orb_*-*_rec*.bsp'))

        if len(spk_kernels) > 0:
            rec, lastorb = self.__find_latest_kernel(spk_kernels, 3, getlast=True)

        self.__furnish_array(rec)

    def __furnish_mars(self) -> None:
        mars_kernel = os.path.join(self.__generic_kernel_path, 'spk',
                                   'mar097.bsp')
        spice.furnsh(mars_kernel)
