Py-Functiontrace
================
The Python module for Functiontrace (https://functiontrace.com).

Dependencies
------------

The FunctionTrace server must be installed for this package to work.
See installation instructions at https://functiontrace.com#installation.

Usage
-----

To use, add `-m functiontrace` to the Python script you want to profile.  For example:

.. code:: sh

    $ python foo.py

should be run as

.. code:: sh

    $ python -m functiontrace foo.py

To see the various arguments, run

.. code:: sh

    $ python -m functiontrace --help
