L1bFile
=======
This page shows the documentation for the :code:`L1bFile`. This file
represents a MAVEN/IUVS level 1b file and is enormous; consequently, the
properties are split into different classes. None of the classes shown
here (besides :code:`L1bFile`) should be directly instantiated. They're
included to see the properties in each of them.

L1bFile
-------
.. autoclass:: pyuvs.data_files.L1bFile
   :members: detector_image, integration, binning, pixel_geometry,
             observation, dark_integration, dark_observation

DetectorImage
-------------
.. autoclass:: pyuvs.data_files.L1bFile.DetectorImage
   :members:

Integration
-----------
.. autoclass:: pyuvs.data_files.L1bFile.Integration
   :members:

Binning
-------
.. autoclass:: pyuvs.data_files.L1bFile.Binning
   :members:

SpacecraftGeometry
------------------
.. autoclass:: pyuvs.data_files.L1bFile.SpacecraftGeometry
   :members:

PixelGeometry
-------------
.. autoclass:: pyuvs.data_files.L1bFile.PixelGeometry
   :members:

Observation
-----------
.. autoclass:: pyuvs.data_files.L1bFile.Observation
   :members:
