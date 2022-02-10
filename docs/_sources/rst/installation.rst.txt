Installation
============

General Installation
--------------------
.. hint::
   We recommend using virtual environments when installing PyUVS.

To install the latest version of PyUVS, simply clone the repository from Github
(using the command :code:`git clone https://github.com/kconnour/PyUVS.git`
in Terminal, or clone using your favorite GUI). You can then install it with
the command
:code:`<path to python interpreter> -m pip install <path to PyUVS>`. This
command will install PyUVS along with all of its subpackages.

You can now import PyUVS with :code:`import pyuvs`.

Subpackages
-----------
PyUVS comes a number of subpackages for specialized tasks that require
specialized libraries. By default PyUVS requires minimal dependencies but
most (if not all) of the subpackages require additional libraries. These are
not installed by default to reduce package clutter.

The following lists the subpackages and the optional dependencies needed (a
complete list and installation instructions are in the next section):

* **database**
   A subpackage for working with a PostgreSQL database. If you just want to
   query an already created database, you just need the :code:`database`
   dependency. If you want to create a database from data files, you also need
   the :code:`datafiles` dependency.
* **datafiles**
   A subpackage for working with data (.fits) files. This requires the
   :code:`datafiles` dependency.
* **graphics**
   A subpackage for working with graphics. Most graphics just require the
   :code:`graphics-basic` dependency. Some more advanced graphics like globe
   projections require the :code:`graphics-advanced` dependency.

Optional Dependencies
---------------------
The following lists all available optional dependencies.

* **all**
   Install all libraries needed for the whole project.

   .. warning::
      This requires GEOS and PROJ to already be installed on the system.

* **database**
   Install all libraries needed to work with PyUVS data via a database.

   .. note::
      This is a work in progress and currently has no effect.

* **datafiles**
   Install all libraries needed to with with PyUVS data via data (.fits) files.

* **docs**
   Install all libraries needed to build the documentation.

* **graphics-advanced**
   Install all libraries needed to create all specialized graphical products.

   .. warning::
      This requires GEOS and PROJ to already be installed on the system.

* **graphics-basic**
   Install all libraries needed to create most of the basic graphical products.

* **spice**
   Install all libraries needed to work with SPICE.

* **test**
    Install all libraries needed to run unit tests.

To install optional dependencies, simply execute this command in Terminal:
:code:`<path to python interpreter> -m pip install <path to pyuvs>[<option>]`.

For example, to install the datafiles dependencies simply use
:code:`<path to python interpreter> -m pip install <path to pyuvs>[datafiles]`.
You can install multiple of these dependencies at once by putting the
dependencies in square brackets *without spaces between them* like so:
:code:`[option0,option1,option2,...]`.
