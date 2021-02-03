import pytest


def pytest_addoption(parser):
    parser.addoption('--interface', action='store')


@pytest.fixture(scope='session')
def opt(request):
    opt = {'interface': request.config.getoption("--interface")}
    return opt
