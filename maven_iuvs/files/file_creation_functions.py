# Local imports
from maven_iuvs.files.finder import DataPath, DataPattern, glob_files
from maven_iuvs.files.files import IUVSDataFilenameCollection





def orbit_range_files(path, orbit_start, orbit_end, segment='apoapse',
                      channel='muv'):
    """ Make an L1bDataFiles for all orbits in a range of orbits with a segment
    pattern and channel pattern, assuming orbits are organized in blocks of
    100.

    Parameters
    ----------
    path: str
        The location where to start looking for files.
    orbit_start: int
        The starting orbit to get files from.
    orbit_end: int
        The ending orbit to get files from.
    segment: str
        The observing segment to get files from. Default is 'apoapse'.
    channel: str
        The observing channel to get files from. Default is 'muv'.

    Returns
    -------
    files: L1bFiles
        An L1bFiles of all files within the input orbital range.
    """
    orbits = list(range(orbit_start, orbit_end))
    return multi_orbit_files(path, orbits, segment=segment, channel=channel)


if __name__ == '__main__':
    # Soschob example
    #p = '/media/kyle/Samsung_T5/IUVS_data'
    #s = soschob(p, 3453)
    #for i in s.abs_paths:
    #    print(i)

    # Multiorbit example
    #m = multi_orbit_files('/media/kyle/Samsung_T5/IUVS_data', [3453, 7618, 8889])
    #for i in m.abs_paths:
    #    print(i)

    # Range example
    m = orbit_range_files('/media/kyle/Samsung_T5/IUVS_data', 3495, 3505)
    for i in m.abs_paths:
        print(i)