import glob
import os
import fnmatch as fnm

'''path = '/home/kyle'
pattern = '*.npy'

#files = [os.path.join(path, fn) for fn in next(os.walk(path))[2]]


#for f in files:
#    print(f)

files = [fn for fn in next(os.walk(path))[2]]
matching_files = []
for name in files:
    if fnm.fnmatch(name, pattern):
        matching_files.append(os.path.join(path, name))

for f in matching_files:
    print(f)

#print(glob.glob(path))
'''

from maven_iuvs.files.files import Files, SingleOrbitL1bFiles, L1bFiles, IUVSFiles
pattern = '*apoapse*3453*muv*.fits.gz'
path = '/media/kyle/Samsung_T5/IUVS_data/orbit03400'
f = SingleOrbitL1bFiles(3453, path)
for i in f.file_paths:
    print(i)

print('~'*20)

for k in f.get_abs_path_of_filenames_containing_pattern('*T045*'):
    print(k)

#h = f.get_filenames_containing_pattern('*T04*52*')
#print(h)
#f = SingleOrbitL1bFiles(3453, path, recursive=False)
#f = L1bFiles(pattern, path)

#from maven_iuvs.aux.aux_files import aux_path

#print(aux_path())
#print(os.path.abspath(os.path.join(aux_path(), '..')))

