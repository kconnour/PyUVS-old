Installation
============
.. hint::
   I recommend using virtual environments when installing PyUVS (or any Python
   library).

To install the latest version of PyUVS simply clone the repository from Github
(using :code:`git clone https://github.com/kconnour/PyUVS.git` from Terminal,
or clone using your favorite GUI). You can then install it with
:code:`<path to python interpreter> -m pip install <path to pyuvs>`. This
command will install PyUVS along with all of its dependencies.

You can now import PyUVS with :code:`import pyuvs`.

Optional dependencies
---------------------
PyUVS will install some standard libraries needed to work with IUVS data.
For specialized usage, it needs additional libraries.The following lists the
options available.

* **docs**
   Install all libraries needed to build the documentation.
* **graphics**
   Install all libraries needed to create specialized graphical products.

   .. warning::
      This requires GEOS and PROJ to already be installed on the system.

* **test**
    Install all libraries needed to run unit tests.

For example, to install the docs dependencies simply use
:code:`<path to python interpreter> -m pip install <path to pyuvs>[docs]`.
