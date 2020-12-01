import setuptools


def setup_package():
    setuptools.setup(
        name='maven_iuvs',
        version='0.0.1',
        description='Make MAVEN/IUVS data more easily accessible',
        url='https://github.com/kconnour/maven-iuvs',
        author='kconnour',
        python_requires='>=3.8',
        install_requires=[
            'astropy>=4.2',
            'numpy>=1.19.4',
        ],
    )


setup_package()
