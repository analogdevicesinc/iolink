################################################################################
# Copyright © 2019 TRINAMIC Motion Control GmbH & Co. KG
# (now owned by Analog Devices, Inc.),
#
# Copyright © 2023 Analog Devices, Inc.
################################################################################

import pytest


def pytest_addoption(parser):
    parser.addoption('--interface', action='store')


@pytest.fixture(scope='session')
def opt(request):
    opt = {'interface': request.config.getoption("--interface")}
    return opt
