# Local imports
from maven_iuvs.files.finder import glob_files, DataPattern, DataPath
import time
from maven_iuvs.data.l1b_properties import L1bDataProperties


if __name__ == '__main__':
    test_orbs = [3453, 7818, 8889]
    pat = DataPath('/media/kyle/Samsung_T5/IUVS_data')
    print(pat.block_paths(test_orbs))
    patt = DataPattern()
    print(patt.multi_orbit_patterns(test_orbs, 'apoapse', 'muv'))
    seg = patt.generic_pattern(['apoapse', 'inlimb'])
    chan = patt.generic_pattern(['ech', 'fuv'])
    crazy_pattern = patt.orbit_pattern(9984, seg, chan)
    a = glob_files(pat.block(9984), crazy_pattern)
    for i in a:
        print(i)
