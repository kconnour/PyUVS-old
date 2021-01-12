# Local imports
from maven_iuvs.files.files import IUVSDataFiles
from maven_iuvs.files.glob_files import GlobFiles, PatternGlob, DataPath
import numpy as np


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
    p = '/media/kyle/Samsung_T5/IUVS_data/orbit03400'
    pat = '*apoapse*3453*muv*'
    g = GlobFiles(p, pat)
    v = IUVSDataFiles(g.abs_paths)
    bar = np.zeros(len(v.filenames))
    bar[-2:] = True
    bar[:2] = True
    foo = v.downselect_filenames(bar)
    for i in v.filenames:
        print(i.filename)
    print('~'*20)
    for i in foo:
        print(i.filename, i.second)
