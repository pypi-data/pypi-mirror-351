.. _exposure:

============================================
Exposure handling (``ctapointing.exposure``)
============================================

.. currentmodule:: ctapointing.exposure

The `Exposure` class within the `ctapointing.exposure` module is the core class to store information
about a camera exposure, including the image itself, methods to read/write an image for FITS format, and
methods to perform coordinate transformations in/from the plane of the camera chip.

The class `ctapointing.ExposureSimulator` provides functionality to simulate pointing images of the sky,
including proper field rotation, moon light simulation and the possibility to simulate science camera LEDs and
star light reflected by the closed lid of the science camera (e.g. for simulating pointing observations).

API
===

.. automodapi:: ctapointing.exposure