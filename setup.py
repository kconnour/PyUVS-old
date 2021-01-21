import setuptools


def setup_package():
    setuptools.setup(
        name='pyuvs',
        version='0.0.1',
        description='Make MAVEN/IUVS data more easily accessible',
        url='https://github.com/kconnour/maven-iuvs',
        author='kconnour',
        packages=setuptools.find_packages(),
        include_package_data=True,
        python_requires='>=3.9',
        install_requires=[
            'astropy>=4.2',
            'numpy>=1.19.4',
            'pdoc3>=0.9.2',
        ],
    )


setup_package()
