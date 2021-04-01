iolink
======

IO-Link is a standardized point-to-point connection down at the edge layer of the factory automation pyramid.

The ``iolink`` Python package allows access to IO-Link devices from within Python,
by providing a common abstraction layer to different IO-Link adapters.

Note that for now, only the iqLink® device is supported and only under Windows.

Installation
------------

Use pip to install the libary.
::

    $ pip install iolink

Apart from that, you need to install the `dependencies that are required <https://iolink.readthedocs.io/en/latest/install.html#dependencies-that-are-required>`_ for your adapter.

Example usage
-------------

This example prints the product name of a connected device, by reading out the standard ISDU parameter 0x12.

.. code-block:: python

   import iolink

   # create a port instance
   with iolink.get_port(interface='iqLink') as port:
       # change state of the connected device to "Operate"
       port.change_device_state_to('Operate')
       # read standard ISDU
       isdu_0x12_data = port.read_device_isdu(0x12, 0)
       # convert the received bytes object that's supposed
       # to be an ASCII string to a standard Python 3 string
       # and print the result
       print(f'Product Name: {isdu_0x12_data.decode("utf8")}')


Contributing
------------

Pull requests are welcome. For any major changes or questions regarding implementation, please open an issue to ask or discuss first.

License
-------
iolink is licensed under the MIT License.

Trademarks
----------
IO-Link is a registered trademark of Profibus User Organization (PNO)