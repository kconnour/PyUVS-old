import os

package_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',))
module_path = os.path.join(package_path, 'pyuvs')
os.system(f'/home/kyle/repos/maven-iuvs/venv/bin/pdoc --html {module_path} --force')
# Test
