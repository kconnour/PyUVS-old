Getting Started
===============
Before installing PyUVS, let's do an overview of the package.

If you're new to IUVS, check out :ref:`about-iuvs`.

If you're new to PyUVS, check out :ref:`about-pyuvs`.

PyUVS code overview
-------------------
PyUVS is largely a collection of array manipulation functions that do tasks
relevant to IUVS data. All of these utilities are imported into the highest
level namespace.

Working with IUVS data can involve specialized libraries, therefore many of
these tasks are relegated to PyUVS subpackages. These include working with
data files, working with a database, using SPICE, and creating custom
graphics. It's unlikely that you'll want all of these features, so you'll
need to decide which options you want when installing PyUVS.

For example, it's likely that you'll want to either work with data files or
query a database of the IUVS data, but not both. Perhaps you want to run a
server that extracts data from data files and puts it into a database. In this
scenario you wouldn't have a need to install any graphical routines. The
subpackage structure therefore gives you fine control over the tools you need.

Subpackages
-----------
These are the subpackages included with PyUVS. Note that some are currently
under construction.

database
~~~~~~~~
This subpackage includes utilities for creating and/or querying a PostgreSQL
database.

.. note::
   If you'll be creating a database from IUVS data files, you'll also need the
   :code:`datafiles` subpackage. If you'll use SPICE kernels to populate the
   database, yoou'll also need the :code:`spice` subpackage.

datafiles
~~~~~~~~~
This subpackage includes utilities for working with IUVS .fits data files.

graphics
~~~~~~~~
This subpackage includes utilities for creating custom IUVS graphics. It also
comes with some standard graphics used amongst the IUVS team.

spice
~~~~~
This subpackage includes an utilities for working with SPICE kernels.
