# Local imports
from maven_iuvs.files.files import IUVSDataFiles, L1bDataFiles
from maven_iuvs.files.finder import GlobFiles, PatternGlob, DataPath
import numpy as np
from maven_iuvs.files.file_creation_functions import multi_orbit_files, orbit_range_files
import glob
from astropy.io import fits
import time
from maven_iuvs.data.l1b_properties import L1bDataProperties


if __name__ == '__main__':
    """p = '/media/kyle/Samsung_T5/IUVS_data/orbit03400'
    pat = '*apoapse*3453*muv*'
    g = GlobFiles(p, pat)
    v = SingleFlargL1bDataFiles(g.abs_paths)
    for i in v.abs_paths:
        print(i)
    bar = np.zeros(len(v.filenames))
    bar[-2:] = True
    bar[:2] = True
    foo = v.downselect_filenames(bar)
    for i in v.filenames:
        print(i.filename)
    print('~'*20)
    for i in foo:
        print(i.filename, i.second)"""
    #o = [3453, 8701, 8704, 10900]
    #a = flarg('/media/kyle/Samsung_T5/IUVS_data', 3453, channel='fuv', segment='periapse')
    #a = multi_orbit_files('/media/kyle/Samsung_T5/IUVS_data', o, channel='fuv',
    #          segment='periapse')
    #a = orbit_range_files('/media/kyle/Samsung_T5/IUVS_data', 3496, 3505)
    #for i in a.filenames:
    #    print(i.filename, i.timestamp)
    #a = sorted(glob.glob('/media/kyle/Samsung_T5/IUVS_data/orbit09900/*9980*[em][cu][hv]*.fits.gz'))
    #for i in a:
    #    print(i)

    '''p = DataPath().block_path('/media/kyle/Samsung_T5/IUVS_data', 9980)
    seg = ['apoapse', 'outdisk', 'outlimb']
    cha = ['muv', 'ech']
    segment = PatternGlob().generic_glob_pattern(seg)
    channel = PatternGlob().generic_glob_pattern(cha)
    pat = PatternGlob().pattern(9980, segment=segment, channel=channel)
    abs_paths = GlobFiles(p, pat).abs_paths

    for i in abs_paths:
        print(i)'''

    p = '/media/kyle/Samsung_T5/IUVS_data/orbit10000'
    pat = '*apoapse*10061*muv*'
    g = GlobFiles(p, pat)
    v = L1bDataFiles(g.abs_paths)
    t0 = time.time()
    r = L1bDataProperties(v.abs_paths)
    print(len(r.check_relays()))
    #print(r.all_relays())
    t1 = time.time()
    '''for i in v.abs_paths:
        hdu = fits.open(i)
        angles = hdu['integration'].data['mirror_deg']
        min_ang = np.amin(angles)
        max_ang = np.amax(angles)'''
    t2 = time.time()
    print(t1-t0)
