.. decide documentation master file, created by
   sphinx-quickstart on Sat Dec 16 19:31:56 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to decide's documentation!
==================================

The objective of this project is to implement a secure electronic voting platform that complies with a series of basic guarantees, 
such as anonymity and secrecy of the vote.

This is an educational project, designed for the study of voting systems, so that simplicity takes precedence over efficiency whenever 
possible. Therefore, some shortcomings are assumed to allow it to be understandable and extensible.

Subsystems, apps and base project
=================================

The project is divided into `subsystems <https://github.com/EGC-23-24/decide-part-lorca/blob/main/doc/subsistemas.md>`_, which will be decoupled from each other. To achieve this, the subsystems will be connected to 
each other via APIs and we need a base project where to configure the routing of these APIs.

This Django project will be divided into apps (subsystems and base project), where any app can be replaced individually.

.. toctree::
   :caption: Contents:
   :titlesonly:

   modules/index
   memes

