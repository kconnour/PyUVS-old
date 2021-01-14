# Local imports
from maven_iuvs.files.files import IUVSDataFiles, L1bDataFiles, SingleFlargL1bDataFiles
from maven_iuvs.files.glob_files import GlobFiles, PatternGlob, DataPath
import numpy as np
from maven_iuvs.files.file_creation_functions import flarg, multi_orbit_files, orbit_range_files
import glob


p = DataPath()
#print(p.block_path('/home/kyle', 8999))
#print(p.orbit_block_paths('/home/kyle', [3459, 4090, 6784]))

pg = PatternGlob()
#print(pg.recursive_pattern(3453, 'apoapse', 'muv'))
#print(pg.recursive_orbit_patterns([3453, 9000], 'apoapse', 'muv'))

g = GlobFiles(p.block_path('/media/kyle/Samsung_T5/IUVS_data', 3453), pg.pattern(3453, 'apoapse', 'muv'))
#for i in g.abs_paths:
#    print(i)

f = IUVSDataFiles(g.abs_paths)
#for k in f.filenames:
#    print(k.timestamp, k.segment, k.channel, k.extension)

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

    p = DataPath().block_path('/media/kyle/Samsung_T5/IUVS_data', 9980)
    seg = ['apoapse', 'outdisk', 'outlimb']
    cha = ['muv', 'ech']
    segment = PatternGlob().generic_glob_pattern(seg)
    channel = PatternGlob().generic_glob_pattern(cha)
    pat = PatternGlob().pattern(9980, segment=segment, channel=channel)
    abs_paths = GlobFiles(p, pat).abs_paths

    for i in abs_paths:
        print(i)

