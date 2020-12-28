# Local imports
from maven_iuvs.files.files import SingleOrbitSequenceChannelL1bFiles, L1bFiles


def single_orbit_segment(path, orbit, channel='muv', sequence='apoapse'):
    """ Make a SingleOrbitSequenceChannelL1bFiles for files matching an input
    orbit, sequence, and channel.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbit: int
        The orbit to get files from.
    channel: str
        The observing mode to get files from.
    sequence: str
        The observing sequence to get files from.

    Returns
    -------
    files: SingleOrbitSequenceChannelL1bFiles:
        A SingleOrbitSequenceChannelL1bFiles containing files from the
        requested orbit, sequence, and channel.
    """
    pattern = f'**/*{sequence}-*{orbit}-*{channel}*'
    return SingleOrbitSequenceChannelL1bFiles(path, pattern)


# TODO: allow multiple paths so user could specify files in multiple dirs
#     : like, if they want 3495--3510.
# TODO: Allow for multiple channels and multiple sequences via '*'. Right now
#     : it'll error since '**' is special.
def orbital_segment(path, orbits, sequence='apoapse', channel='muv'):
    """ Make an L1bFiles for an input list of orbits.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbits: list
        List of ints of orbits to get files from.
    sequence: str
        The observing sequence. Default is 'apoapse'.
    channel: str
        The observing channel. Default is 'muv'.

    Returns
    -------
    files: L1bFiles
        An L1bFiles of all files at the input orbits.
    """
    # TODO: this entire function an unreadable mess... fix
    orbits = [str(orbit).zfill(5) for orbit in orbits]
    patterns = [f'**/*{sequence}-*{orbit}-*{channel}*' for orbit in orbits]

    l1b_files = []
    for counter, pattern in enumerate(patterns):
        try:
            file = L1bFiles(path, pattern)
            l1b_files.append(file)
        except ValueError:
            continue

    if len(l1b_files) == 0:
        raise ValueError('There are no files for any of the input orbits.')
    elif len(l1b_files) == 1:
        return l1b_files
    else:
        for counter, files in enumerate(l1b_files):
            if counter == 0:
                file = files
            else:
                for j in range(len(files.absolute_paths)):
                    file.absolute_paths.append(files.absolute_paths[j])
                    file.filenames.append(files.filenames[j])
    return file


def orbit_range_segment(path, orbit_start, orbit_end, sequence='apoapse',
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
        The observing sequence. Default is 'apoapse'.
    channel: str
        The observing channel. Default is 'muv'.

    Returns
    -------
    files: L1bFiles
        An L1bFiles of all files within the input orbital range.
    """
    orbits = list(range(orbit_start, orbit_end + 1))
    return orbital_segment(path, orbits, sequence=sequence, channel=channel)
