
@property
def maximum_mirror_angle(self):
    """ Get the maximum mirror angle of the IUVS mirror.

    Returns
    -------
    maximum_mirror_angle: float
        The maximum mirror angle [degrees].
    """
    return 59.6502685546875

@property
def minimum_mirror_angle(self):
    """ Get the minimum mirror angle of the IUVS mirror.

    Returns
    -------
    minimum_mirror_angle: float
        The minimum mirror angle [degrees].
    """
    return 30.2508544921875

def check_relays(self):
    """ Get which files associated with this object are relay files.

    Returns
    -------
    relay_files: list
        A list of booleans. True if the corresponding file is as relay
        file; False otherwise.
    """
    relay_files = []
    for counter, f in enumerate(self.absolute_paths):
        with fits.open(f) as hdulist:
            relay_files.append(
                self.__check_if_hdulist_is_relay_swath(hdulist))
    return relay_files

def all_relays(self):
    """ Check if all of the files associated with this object are relay
    files.

    Returns
    -------
    relay_files: bool
        True if all files are relay files; False otherwise.
    """
    relay_files = self.check_relays()
    return all(relay_files)

def any_relays(self):
    """ Check if any of the files associated with this object are relay
    files.

    Returns
    -------
    relay_files: bool
        True if any files are relay files; False otherwise.
    """
    relay_files = self.check_relays()
    return any(relay_files)

def __check_if_hdulist_is_relay_swath(self, hdulist):
    angles = hdulist['integration'].data['mirror_deg']
    min_ang = np.amin(angles)
    max_ang = np.amax(angles)
    return True if min_ang == self.minimum_mirror_angle and \
                   max_ang == self.maximum_mirror_angle else False