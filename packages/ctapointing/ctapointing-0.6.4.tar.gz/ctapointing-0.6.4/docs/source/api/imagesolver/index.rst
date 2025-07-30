.. _imagesolver:

=======================================================
Image solving and fitting (``ctapointing.imagesolver``)
=======================================================

.. currentmodule:: ctapointing.imagesolver

The `ctapointing.imagesolver` module contains the following core classes:

* `SpotExtractor`: set of classes to extract spots from a `ctapointing.Exposure` objects, such as stars and science camera LEDs.
* `ImageSolver`: provides functionality to `register` a set of extracted spots with a star catalog, i.e. functionality to identify which spot in an image belongs to which catalog star.
* `SkyFitter`: class that fits the coordinate transformation between the ICRS positions of catalog stars and their respective spots in an image, providing precise information about e.g. the pointing of the centre of the camera chip and its rotation w.r.t. the horizon.
* `LEDFitter`: class to determine the coordinate transformation between the LED positions on the front of the science camera and their positions in the pointing camera image. Provides information about e.g. the focal length of the telescope, and the position/rotation of the science camera w.r.t. the pointing camera.
* `ImageSolution`: class that stores the information about the solved and fitted image, in particular parameters that fix the above mentioned coordinate transformations.

API
===

.. automodapi:: ctapointing.imagesolver