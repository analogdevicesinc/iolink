################################################################################
# Copyright © 2019 TRINAMIC Motion Control GmbH & Co. KG
# (now owned by Analog Devices Inc.),
#
# Copyright © 2023 Analog Devices Inc. All Rights Reserved. This software is
# proprietary & confidential to Analog Devices, Inc. and its licensors.
################################################################################

from typing import Tuple
from abc import ABC, abstractmethod


class IsduError(Exception):
    def __init__(self, error_code):
        self.error_code = error_code


class PortABC(ABC):
    """Abstract base class that represents one Masters IO-Link port."""
    @abstractmethod
    def power_on(self):
        """Switches on the IO-Link power line of the port."""
        pass

    @abstractmethod
    def power_off(self):
        """Switches off the IO-Link power line of the port."""
        pass

    @abstractmethod
    def change_device_state_to(self, target_state: str):
        """Sends a request to the device to change the state.

        :param str target_state: allowed strings are 'Inactive', 'PreOperate' or 'Operate'.
        """
        pass

    @abstractmethod
    def get_device_pd_input_and_status(self) -> Tuple[bytes, int]:
        """Gets the input process data from a device and the state information."""
        pass

    @abstractmethod
    def set_device_pd_output(self, data: bytes):
        """Sets the output process data for a device."""
        pass

    @abstractmethod
    def read_device_isdu(self, index: int, subindex: int):
        """Reads content of a parameter from the device."""
        pass

    @abstractmethod
    def write_device_isdu(self, index: int, subindex: int, data):
        """Writes content of a parameter from the device.

        Make sure the size of the data matches the size of the devices parameter.
        """
        pass

    @abstractmethod
    def shut_down(self):
        pass
