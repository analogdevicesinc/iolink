################################################################################
# Copyright © 2019 TRINAMIC Motion Control GmbH & Co. KG
# (now owned by Analog Devices Inc.),
#
# Copyright © 2023 Analog Devices Inc. All Rights Reserved. This software is
# proprietary & confidential to Analog Devices, Inc. and its licensors.
################################################################################

from .interfaces.iqlink.iqlink import IqLinkPort

from contextlib import contextmanager

available_interfaces = {'iqLink': IqLinkPort}


@contextmanager
def get_port(interface):
    """Factory of specific instances of the abstract Port class.

    :param str interface: ID of your IO-Link master device - currently only `iqLink` is supported.
    """
    port = available_interfaces[interface]()
    yield port
    port.shut_down()
