.. _observation:

===================================================
Observations planning (``ctapointing.observation``)
===================================================

.. currentmodule:: ctapointing.observation

Functionality to plan pointing observations and store their properties.

* `PointingObservation`: container to store information about individual pointing observations, such as target position, observation time and exposure duration.
* `StarSelector`: tool to select stars for pointing observations, such that their distribution is isotropic within specified altitude limits.
* `ObservationPlan`: functionality to schedule/plan pointing observations, select proper targets using e.g. the `StarSelection`, and read/write the observation plan from/to HDF5 file.

API
===

.. automodapi:: ctapointing.observation