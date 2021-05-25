Installation
============
There are (or will be) several ways to install PyUVS. Regardless of how you
choose to install the package, we highly recommend you use virtual environments
during the process. All that follows will assume you are using them.

PYPI installation
-----------------
The package is coming to the PyPI soon!

Github installation
-------------------
To install the latest version of PyUVS simply clone the repository from Github
(using :code:`git clone https://github.com/kconnour/PyUVS.git` from Terminal,
or clone using your favorite GUI). You can then install it with
:code:`<path to python interpreter> -m pip install <path to pyuvs>`. This
command will install PyUVS along with all of its dependencies.

You can now import PyUVS with :code:`import pyuvs`!

Optional dependencies
---------------------
PyUVS will only install the minimum libraries needed to work with IUVS data.
For more advanced usage, some additional libraries are needed. The following
lists the options available.

* **all**
   Install all optional libraries.
* **docs**
   Install all libraries needed to build the documentation.
* **graphics**
   Install all libraries needed to create standard graphical products.

   .. warning::
      This requires GEOS and PROJ to already be installed.

For example, to install the docs dependencies simply use
:code:`<path to python interpreter> -m pip install <path to pyuvs>[docs]`.
