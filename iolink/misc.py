
from .interfaces.iqlink.iqlink import IqLinkPort

from contextlib import contextmanager


available_interfaces = {'iqlink': IqLinkPort}


@contextmanager
def get_port(interface):
    """Factory of specific instances of the abstract Port class.

    :param str interface: ID of your IO-Link master device - currently only `iqlink` is supported.
    """
    port = available_interfaces[interface]()
    yield port
    port.shut_down()
