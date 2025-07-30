from . import acu, hwp, seq, smurf, wiregrid

from .commands import wait_until
from .util import create_clients

CLIENTS = None


def initialize(test_mode=False):
    """Initialize global clients list.

    Args:
        test_mode (bool): Operate in 'test mode'. Use this to find Agents that
            are meant to stand in for real agents while testing, i.e.
            SmurfFileEmulators instead of PysmurfControllers.
    """
    global CLIENTS
    CLIENTS = create_clients(test_mode=test_mode)


__all__ = ["acu",
           "hwp",
           "seq",
           "smurf",
           "wiregrid",
           "wait_until",
           "initialize"]

from . import _version
__version__ = _version.get_versions()['version']
