============
Installation
============

How to install iolink itself
----------------------------

Install **iolink** from PyPI using ``pip``:
::

    $ python -m pip install iolink

This makes sure that the ``pip`` you are using belongs to your Python distribution. But you may also do it with:
::

    $ pip install iolink

Dependencies that are required
------------------------------

When using an iqLink®
~~~~~~~~~~~~~~~~~~~~~

* Download the iqDLL (iqcomm.dll) from the `IQ2 website <https://www.iq2-development.com/downloads.html>`__.
* Make the iqDLL available to ``iolink`` by copying the iqcomm.dll file:

  * to the same directory where your main Python file resides, or by
  * copying the file to a known location in your system and adding this directory to the PATH environment variable.