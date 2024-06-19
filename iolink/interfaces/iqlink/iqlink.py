################################################################################
# Copyright © 2019 TRINAMIC Motion Control GmbH & Co. KG
# (now owned by Analog Devices Inc.),
#
# Copyright © 2023 Analog Devices Inc. All Rights Reserved.
# This software is proprietary to Analog Devices, Inc. and its licensors.
################################################################################

from iolink.port import PortABC, IsduError

import ctypes
import ctypes.util
import os
import re
import sys


MST_DEV_SER_NUM_MAX_LEN = 16

_iqcomm_lib = None

if sys.platform == 'win32':
    if hasattr(sys.modules['__main__'], '__file__'):
        # there might be no main file, e.g. in interactive interpreter mode
        main_file_directory = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
        if os.path.isfile(os.path.join(main_file_directory, 'iqcomm.dll')):
            _iqcomm_lib = ctypes.windll.LoadLibrary(os.path.join(main_file_directory, 'iqcomm.dll'))
    if _iqcomm_lib is None:
        this_files_directory = os.path.dirname(__file__)
        if os.path.isfile(os.path.join(this_files_directory, 'iqcomm.dll')):
            _iqcomm_lib = ctypes.windll.LoadLibrary(os.path.join(this_files_directory, 'iqcomm.dll'))
        elif ctypes.util.find_library('iqcomm.dll') is not None:
            _iqcomm_lib = ctypes.windll.LoadLibrary(ctypes.util.find_library('iqcomm.dll'))


class MstConfigT(ctypes.Structure):
    _fields_ = [
        ('stackVersion', ctypes.c_uint16),
        ('cycleTimeOperate', ctypes.c_uint16),
        ('restOfCycleTimeOperate', ctypes.c_uint16),
        ('revisionID', ctypes.c_int),  # enum
        ('inspectionLevel', ctypes.c_int),  # enum
        ('deviceVendorID', ctypes.c_uint32),
        ('deviceID', ctypes.c_uint32),
        ('deviceFunctionID', ctypes.c_uint16),
        ('deviceSerialNumber', ctypes.c_uint8 * (MST_DEV_SER_NUM_MAX_LEN + 1)),
        ('deviceSerialNumberLen', ctypes.c_uint8),
        ('realBaudrate', ctypes.c_int),  # enum
        ('dsActivState', ctypes.c_int),  # enum
        ('dsUploadEnable', ctypes.c_bool),
        ('dsDownloadEnable', ctypes.c_bool),
    ]


class IqLinkPort(PortABC):

    # mst_OperModeT
    op_modes = {
        'INACTIVE': 0,
        'AUTO': 3,
        'PREOPERATE': 4,
        'OPERATE': 5,
    }
    # mst_StateT
    op_states = {
        'INACTIVE': 0,
        'CHK_FAULT': 3,
        'PREOPERATE': 4,
        'OPERATE': 5,
    }

    def __init__(self, **kwargs):
        if sys.platform == 'win32':
            if _iqcomm_lib is None:
                raise FileNotFoundError('iqcomm.dll')
        else:
            raise NotImplementedError('The iqLink support is only available for windows')

        self._port = None
        self._error_msg_buffer = ctypes.create_string_buffer(256)
        self._check_iqcomm_lib_version()
        self._connect()

    def power_on(self):
        self._switch_power('on')

    def power_off(self):
        self._switch_power('off')

    def change_device_state_to(self, target_state):
        self._check_port()
        target_state_to_op_modes_str = {
            'Inactive': 'INACTIVE',
            'PreOperate': 'PREOPERATE',
            'Operate': 'OPERATE',
        }
        op_modes_str = target_state_to_op_modes_str[target_state]
        self._go_to_state(op_modes_str)

    def get_device_pd_input_and_status(self):
        self._check_port()
        status = ctypes.c_uint8()
        pd_data_buffer = ctypes.create_string_buffer(64)
        ret = _iqcomm_lib.mst_GetStatus(self._port,
                                        ctypes.byref(status),
                                        pd_data_buffer,
                                        ctypes.c_uint16(len(pd_data_buffer)),
                                        self._error_msg_buffer)
        ret = ctypes.c_int16(ret)
        if ret.value < 0:
            raise ConnectionError(self._error_msg_buffer.value.decode('utf8'))
        return pd_data_buffer[:ret.value], status

    def set_device_pd_output(self, data: bytes):
        self._check_port()
        if not isinstance(data, bytes):
            return ValueError

        ret = _iqcomm_lib.mst_SetPDValue(self._port,
                                         data,
                                         ctypes.c_uint16(len(data)),
                                         self._error_msg_buffer)
        ret = ctypes.c_int16(ret)
        if ret.value < 0:
            raise ConnectionError(self._error_msg_buffer.value.decode('utf8'))

        ret = _iqcomm_lib.mst_SetPDValidity(self._port,
                                            1,
                                            self._error_msg_buffer)
        ret = ctypes.c_int16(ret)
        if ret.value < 0:
            raise ConnectionError(self._error_msg_buffer.value.decode('utf8'))

    def read_device_isdu(self, index, subindex):
        self._check_port()
        _iqcomm_lib.mst_StartReadOD(self._port, index, subindex, self._error_msg_buffer)

        ret = _iqcomm_lib.mst_WaitODRsp(self._port, index, subindex, self._error_msg_buffer)
        ret = ctypes.c_int16(ret)
        if ret.value < 0:
            raise TimeoutError(self._error_msg_buffer.value.decode('utf8'))

        isdu_data_buffer = ctypes.create_string_buffer(1024)
        isdu_error = ctypes.c_uint16(0)
        ret = _iqcomm_lib.mst_GetReadODRsp(self._port,
                                           isdu_data_buffer,
                                           len(isdu_data_buffer),
                                           ctypes.byref(isdu_error),
                                           self._error_msg_buffer)
        ret = ctypes.c_int16(ret)
        if ret.value < 0:
            raise IsduError(isdu_error.value)

        return isdu_data_buffer[:ret.value]

    def write_device_isdu(self, index, subindex, data):
        self._check_port()
        _iqcomm_lib.mst_StartWriteOD(self._port, index, subindex, data, len(data), self._error_msg_buffer)

        ret = _iqcomm_lib.mst_WaitODRsp(self._port, index, subindex, self._error_msg_buffer)
        ret = ctypes.c_int16(ret)
        if ret.value < 0:
            raise TimeoutError(self._error_msg_buffer.value.decode('utf8'))

        isdu_error = ctypes.c_uint16(0)
        ret = _iqcomm_lib.mst_GetWriteODRsp(self._port,
                                            ctypes.byref(isdu_error),
                                            self._error_msg_buffer)
        ret = ctypes.c_int16(ret)
        if ret.value < 0:
            raise IsduError(isdu_error.value)

    def shut_down(self):
        if self._port:
            ret = _iqcomm_lib.mst_Disconnect(self._port, self._error_msg_buffer)
        ret = ctypes.c_int16(ret)
        if ret.value < 0:
            raise ConnectionError(self._error_msg_buffer.value)

    def _switch_power(self, to):
        assert to.upper() in ['ON', 'OFF']
        self._check_port()
        if to.upper() == 'ON':
            ret = _iqcomm_lib.mst_PowerControl(self._port, ctypes.c_uint8(1), self._error_msg_buffer)
        else:
            ret = _iqcomm_lib.mst_PowerControl(self._port, ctypes.c_uint8(0), self._error_msg_buffer)
        ret = ctypes.c_int16(ret)
        if ret.value < 0:
            raise ConnectionError(self._error_msg_buffer.value.decode('utf8'))

    def _check_iqcomm_lib_version(self):
        version_major = ctypes.c_uint16()
        version_minor = ctypes.c_uint16()
        _iqcomm_lib.mst_GetVersion(ctypes.byref(version_major),
                                   ctypes.byref(version_minor),
                                   self._error_msg_buffer)
        # make sure that iqcomm lib version is at least 2.0
        if version_major.value < 2:
            raise Exception('This version of the iqcomm lib is not supported')

    def _check_port(self):
        if not self._port:
            raise UnboundLocalError

    def _connect(self, com_port=None):
        if com_port is not None:
            com_port_num = self._com_port_str_to_int(com_port)
            ret = _iqcomm_lib.mst_Connect(ctypes.c_uint8(com_port_num),
                                          ctypes.c_uint8(com_port_num),
                                          self._error_msg_buffer)
        else:
            ret = _iqcomm_lib.mst_Connect(ctypes.c_uint8(0), ctypes.c_uint8(255), self._error_msg_buffer)
        ret = ctypes.c_int16(ret)
        if ret.value < 0:
            raise ConnectionError(self._error_msg_buffer.value.decode('utf8'))
        self._port = ret

    def _go_to_state(self, mode):

        set_state = ctypes.c_uint8(self.op_modes[mode])
        if mode != 'AUTO':
            expected_state = ctypes.c_uint8(self.op_states[mode])
        else:
            expected_state = ctypes.c_uint8()

        actual_state = ctypes.c_uint8()
        ret = _iqcomm_lib.mst_SetOperatingMode(self._port,
                                               set_state,
                                               expected_state,
                                               ctypes.byref(actual_state),
                                               self._error_msg_buffer)
        ret = ctypes.c_int16(ret)
        if ret.value < 0:
            raise ConnectionError(self._error_msg_buffer.value.decode('utf8'))

        if mode != 'AUTO':
            if actual_state.value != expected_state.value:
                raise ConnectionRefusedError

    @classmethod
    def _com_port_str_to_int(cls, comport):
        """
        info for the regex expression:
            https://stackoverflow.com/questions/16519744/python-regex-to-match-space-character-or-end-of-string
        """
        m = re.match(r'COM([0-9]+)(?:\s+|$)', comport)
        if not m:
            raise NameError
        return int(m.groups()[0])
