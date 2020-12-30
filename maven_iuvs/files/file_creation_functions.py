# Local imports
from maven_iuvs.files.files import SingleOrbitSequenceChannelL1bFiles, L1bFiles


# TODO: My functions here seem awfully clunky. It may be nice to define
#  addition or summation as a method to combine multiple L1bFiles. But that too
#  seems clunky since glob cannot handle an orbit range.
# TODO: I iterate over an input list of orbits, but it would be nice to iterate
#  over an input list of sequences and channels too so they're more general.
# TODO: My helper functions may go elsewhere since they're not necessarily
#  specific to the 3 major functions here.
# TODO: The 3 major function names aren't very good...


def single_orbit_segment(path, orbit, sequence='apoapse', channel='muv',
                         recursive=False):
    """ Make a SingleOrbitSequenceChannelL1bFiles for files matching an input
    orbit, sequence, and channel.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbit: int
        The orbit to get files from.
    sequence: str
        The observing sequence to get files from.
    channel: str
        The observing mode to get files from.
    recursive: bool
        Denote whether to look recursively in path. Default is False.

    Returns
    -------
    files: SingleOrbitSequenceChannelL1bFiles:
        A SingleOrbitSequenceChannelL1bFiles containing files from the
        requested orbit, sequence, and channel.
    """
    pattern = make_recursive_glob_pattern(orbit, channel, sequence, recursive)
    return SingleOrbitSequenceChannelL1bFiles(path, pattern)


# TODO: allow multiple paths so user could specify files in multiple dirs
#     : like, if they want 3495--3510.
def orbital_segment(path, orbits, sequence='apoapse', channel='muv',
                    recursive=False):
    """ Make an L1bFiles for an input list of orbits.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbits: list
        List of ints of orbits to get files from.
    sequence: str
        The observing sequence. Can be '*'. Default is 'apoapse'.
    channel: str
        The observing channel. Can be '*'. Default is 'muv'.
    recursive: bool
        Denote whether to look recursively in path. Default is False.

    Returns
    -------
    files: list
        An L1bFiles of all files at the input orbits.
    """
    orbits = orbits_to_strings(orbits)
    patterns = make_patterns_from_orbits(orbits, sequence, channel, recursive)

    # TODO: abstract this
    single_orbit_files = []
    for pattern in patterns:
        try:
            file = L1bFiles(path, pattern)
            single_orbit_files.append(file)
        except ValueError:
            continue

    return combine_multiple_l1b_files(single_orbit_files)


def orbit_range_segment(path, orbit_start, orbit_end, sequence='apoapse',
                        channel='muv', recursive=False):
    """ Make an L1bFiles for all orbits between two endpoints.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbit_start: int
        The starting orbit to get files from.
    orbit_end: int
        The ending orbit to get files from.
    sequence: str
        The observing sequence. Can be '*'. Default is 'apoapse'.
    channel: str
        The observing channel. Can be '*'. Default is 'muv'.
    recursive: bool
        Denote whether to look recursively in path. Default is False.

    Returns
    -------
    files: L1bFiles
        An L1bFiles of all files within the input orbital range.
    """
    orbits = list(range(orbit_start, orbit_end + 1))
    return orbital_segment(path, orbits, sequence=sequence, channel=channel,
                           recursive=recursive)


# TODO: Add try statements so the user doesn't get cryptic errors.
def make_recursive_glob_pattern(orbit, sequence, channel, recursive):
    pattern = make_single_segment_glob_pattern(orbit, sequence, channel)
    if recursive:
        pattern = prepend_recursive_glob_pattern(pattern)
    return pattern


def make_single_segment_glob_pattern(orbit, sequence, channel):
    pattern = f'*{sequence}-*{orbit}-{channel}*'
    return remove_recursive_glob_pattern(pattern)


def remove_recursive_glob_pattern(pattern):
    return pattern.replace('**', '*')


def prepend_recursive_glob_pattern(pattern):
    return f'**/{pattern}'


def orbit_to_string(orbit):
    return str(orbit).zfill(5)


def orbits_to_strings(orbits):
    return [orbit_to_string(orbit) for orbit in orbits]


def make_patterns_from_orbits(orbits, sequence, channel, recursive):
    return [make_recursive_glob_pattern(orbit, sequence, channel, recursive)
            for orbit in orbits]


def combine_multiple_l1b_files(l1b_files):
    for counter, files in enumerate(l1b_files):
        if counter == 0:
            continue
        for f in range(len(files.filenames)):
            l1b_files[0].filenames.append(files.filenames[f])
            l1b_files[0].absolute_paths.append(files.absolute_paths[f])
    return l1b_files[0]
