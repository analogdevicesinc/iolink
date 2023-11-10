################################################################################
# Copyright © 2019 TRINAMIC Motion Control GmbH & Co. KG
# (now owned by Analog Devices Inc.),
#
# Copyright © 2023 Analog Devices Inc. All Rights Reserved. This software is
# proprietary & confidential to Analog Devices, Inc. and its licensors.
################################################################################

"""Test an IO-Link port of against a connected PD42-1-1243-IOLINK

Run this test with pytest `pytest --interface iqLink` for example.

"""

import iolink
import pytest
import dataclasses
import struct
import ctypes


@dataclasses.dataclass
class Parameter:
    index: int
    datatype: type


class PD1243:

    parameter_table = {
        'System Command': Parameter(0x02, ctypes.c_uint8),
        # General Configuration
        'Microstep Resolution': Parameter(0x40, ctypes.c_uint8),
        # Current Limits
        'Maximum Current': Parameter(0x50, ctypes.c_int16),
        'Standby Current': Parameter(0x51, ctypes.c_int16),
        # Encoder Parameter
        'Initialize Position': Parameter(0x61, bool),
        'Following Error Window': Parameter(0x62, ctypes.c_int32),
        'Set Encoder Position': Parameter(0x63, ctypes.c_int32),
        # Monitoring
        'Actual Load Value': Parameter(0xC0, ctypes.c_int16),
        'PWM Scale Value': Parameter(0xC1, ctypes.c_int16),
        'Motor Supply Voltage': Parameter(0xC2, ctypes.c_int32),
        'Actual Current': Parameter(0xC3, ctypes.c_int16),
        'Encoder Position': Parameter(0xC4, ctypes.c_int32),
        # Homing
        'Set Actual Position': Parameter(0xD0, ctypes.c_int32),
    }
    int_types = [ctypes.c_uint8, ctypes.c_int32, ctypes.c_int16]

    def __init__(self, port):
        self._port = port

    def set_pd_output(self, target_position, target_velocity, mode):
        mode_enum = {'stop': 0, 'pos': 1, 'vel': 2}
        mode_byte = mode_enum[mode]
        self._port.set_device_pd_output(struct.pack('>llB', target_position, target_velocity, mode_byte))

    def get_pd_input(self):
        pd_data_in, status = self._port.get_device_pd_input_and_status()
        return struct.unpack('>lllB', pd_data_in)

    def write_isdu_parameter(self, name, value):
        parameter = self.parameter_table[name]
        if parameter.datatype in self.int_types:
            value_bytes = value.to_bytes(ctypes.sizeof(parameter.datatype), byteorder='big')
            self._port.write_device_isdu(parameter.index, 0, value_bytes)
        elif parameter.datatype == bool:
            if value:
                self._port.write_device_isdu(parameter.index, 0, bytes([0x01]))
            else:
                self._port.write_device_isdu(parameter.index, 0, bytes([0x00]))

    def read_isdu_parameter(self, name):
        parameter = self.parameter_table[name]
        answer = self._port.read_device_isdu(parameter.index, 0)
        if parameter.datatype in self.int_types:
            assert len(answer) == ctypes.sizeof(parameter.datatype)
            return int.from_bytes(answer,  byteorder='big', signed=True)
        elif parameter.datatype == bool:
            assert len(answer) == 1
            return bool(answer[0])
        else:
            return answer

    def set_custom_data_select(self, name):
        custom_data_select_enum = {
            'Actual Load Value': 0,
            'PWM Scale Value': 1,
            'Motor Supply Voltage': 2,
            'Actual Current': 3,
            'Encoder Position': 4,
        }
        self.write_isdu_parameter('Custom Data Select', custom_data_select_enum[name])


@pytest.fixture(scope='module')
def pd1243(opt):
    with iolink.get_port(interface=opt['interface']) as port:
        port.change_device_state_to('Operate')
        pd1243 = PD1243(port)
        pd1243.write_isdu_parameter('Set Actual Position', 0)
        yield pd1243
        # Restore factory settings
        port.write_device_isdu(0x02, 0, bytes([0x82]))


def test_process_data(pd1243):
    """Turns the motor one complete rotation."""
    pd1243.set_pd_output(51_200, 0, 'pos')
    state_byte = 0x00
    while not state_byte & 0x2:
        _, _, _, state_byte = pd1243.get_pd_input()
    pd1243.set_pd_output(0, 0, 'stop')


def test_isdu_parameter(pd1243):
    """Writes a parameter and reads back its new value."""
    old_standby_current = pd1243.read_isdu_parameter('Standby Current')
    assert 0 < old_standby_current < 128
    temp_standby_current = old_standby_current + 8
    pd1243.write_isdu_parameter('Standby Current', temp_standby_current)
    assert pd1243.read_isdu_parameter('Standby Current') == temp_standby_current
    # restore the initial value
    pd1243.write_isdu_parameter('Standby Current', old_standby_current)
