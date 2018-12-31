.. filabel documentation master file, created by
   sphinx-quickstart on Mon Dec 31 12:47:34 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Filabel
=======

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   filabel



Filabel si tool for auto-generating github PR labels based on config files.


Instalation
-----------

1. Clone repository from https://github.com/bezstpav/FIT-MI-PYT-FILABEL
2. Install package::
     
     $ python setup.py install

Help
----
For help you can use --help::

     Usage: filabel [OPTIONS] [REPOSLUGS]...
     CLI tool for filename-pattern-based labeling of GitHub PRs
     Options:
          -s, --state [open|closed|all] Filter pulls by state. [default: open]
          -d, --delete-old / -D, --no-delete-old  Delete labels that do not match anymore.     [default: True]
          -b, --base BRANCH   Filter pulls by base (PR target) branch name.
          -a, --config-auth FILENAME    File with authorization configuration.[required]
          -l, --config-labels FILENAME  File with labels configuration. [required]
          -x, --async    Use asynchronnous (faster) logic.
          --help    Show this message and exit.


Async mode
==========

If you want to speed up process you can use async mode.::
     
     -x, --async

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
