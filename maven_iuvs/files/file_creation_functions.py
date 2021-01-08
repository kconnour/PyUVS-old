# Built-in imports
import os

# 3rd-party imports
import numpy as np

# Local imports
from maven_iuvs.files.files import SingleOrbitSequenceChannelL1bFiles, L1bFiles


def segment(path, orbit, sequence='apoapse', channel='muv'):
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

    Returns
    -------
    files: SingleOrbitSequenceChannelL1bFiles:
        A SingleOrbitSequenceChannelL1bFiles containing files from the
        requested orbit, sequence, and channel.
    """
    pattern = IUVSGlobs().make_recursive_glob_pattern(orbit, sequence, channel)
    return SingleOrbitSequenceChannelL1bFiles(path, pattern)


def multi_segments(path, orbits, sequence='apoapse', channel='muv'):
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

    Returns
    -------
    files: list
        An L1bFiles of all files at the input orbits.
    """
    paths = IUVSGlobs().make_orbit_paths(path, orbits)
    patterns = IUVSGlobs().make_recursive_patterns_from_orbits(orbits,
                                                               sequence,
                                                               channel)

    single_orbit_files = []
    for i in range(len(paths)):
        try:
            file = L1bFiles(paths[i], patterns[i])
            single_orbit_files.append(file)
        except ValueError:
            continue

    return combine_multiple_l1b_files(single_orbit_files)


def segment_range(path, orbit_start, orbit_end, sequence='apoapse',
                  channel='muv'):
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

    Returns
    -------
    files: L1bFiles
        An L1bFiles of all files within the input orbital range.
    """
    orbits = list(range(orbit_start, orbit_end))
    return multi_segments(path, orbits, sequence=sequence, channel=channel)


# TODO: This should be a method in Files
def combine_multiple_l1b_files(l1b_files):
    for counter, files in enumerate(l1b_files):
        if counter == 0:
            continue
        for f in range(len(files.filenames)):
            l1b_files[0].filenames.append(files.filenames[f])
            l1b_files[0].absolute_paths.append(files.absolute_paths[f])
    return l1b_files[0]
