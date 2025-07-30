.. ctapointing documentation master file, created by
   sphinx-quickstart on Mon Jul 17 14:23:22 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

============================================================
Prototype CTA Telescope Pointing Framework (``ctapointing``)
============================================================

.. currentmodule:: ctapointing

This code is a prototype data processing framework and is under rapid
development. It is not recommended for production use unless you are an
expert or developer!

* Code: https://gitlab.com/vaneldik/ctapointing/
* Docs: see notebook examples in ctapointing/examples and this documentation

Installation for Developers
===========================

*ctapointing* and its dependencies can be installed using *Anaconda*.

The following steps need to be taken:

* Clone the repository: `git clone https://gitlab.com/vaneldik/ctapointing.git`
* Switch to the new repository: `cd ctapointing`
* Tell git where you remote repository is: `git remote add upstream https://gitlab.com/vaneldik/ctapointing.git`
* Create a conda environment: `conda env create -n ctapointing -f ctapointing-environment.yml`
* Activate the new environment: `conda activate ctapointing`
* Add repository to python search path: `pip install -e .`

Your environment should now be ready. If you open a new terminal, just don't forget to execute `conda activate ctapointing` to activate the environment also in this terminal.


API Documentation
=================

.. toctree::
   :maxdepth: 1
   :glob:

   api/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
