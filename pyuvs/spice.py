import glob
import os
import re
import numpy as np
import spiceypy as spice


class Spice:
    def __init__(self, spice_directory: str) -> None:
        self.__mvn_kpath = os.path.join(spice_directory, 'mvn')
        self.__generic_kpath = os.path.join(spice_directory, 'generic_kernels')

    # This was load_iuvs_spice
    def load_spice(self, ) -> None:
        self.__clear_existing_kernels()

        self.__pool_and_furnsh(self.__mvn_kpath)
        self.__pool_and_furnsh(self.__generic_kpath)

        self.__furnish_spacecraft_clock_kernels()

    @staticmethod
    def __clear_existing_kernels() -> None:
        spice.kclear()

    def __pool_and_furnsh(self, kpath) -> None:
        split_path = self.__split_string_into_length(kpath, 78)  # spice can only handle strings of length 78
        spice.pcpool('PATH_VALUES', split_path)
        tm_path = os.path.join(kpath, 'generic.tm')
        spice.furnsh(tm_path)

    def __furnish_spacecraft_clock_kernels(self) -> None:
        tsc_path = os.path.join(self.__mvn_kpath, 'sclk', 'MVN_SCLKSCET.0*.tsc')
        clock_kernels = sorted(glob.glob(tsc_path))
        self.__furnish_array(clock_kernels)

    # This used to be breakup_path()
    @staticmethod
    def __split_string_into_length(string: str, length: int) -> list[str]:
        # Turn a string into a list of strings that have a maximum length. This
        # is needed since spice can only handle strings of a certain length
        return [string[i: i+length] for i in range(0, len(string), length)]

    @staticmethod
    def __furnish_array(kernels) -> None:
        [spice.furnsh(k) for k in kernels]

    