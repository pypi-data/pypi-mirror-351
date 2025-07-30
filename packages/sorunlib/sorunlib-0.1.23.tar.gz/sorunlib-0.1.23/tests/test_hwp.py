import os
os.environ["OCS_CONFIG_DIR"] = "./test_util/"

import pytest
from unittest.mock import MagicMock
import time

import ocs
from ocs.ocs_client import OCSReply
from sorunlib import hwp

from util import create_patch_clients, create_session

patch_clients_satp = create_patch_clients('satp')


def create_hwp_client(direction):
    """Create a HWP client with mock acq Process session.data.

    Args:
        direction (str): direction of the HWP. 'ccw' (counter-clockwise) or 'cw' (clockwise).

    """
    client = MagicMock()
    session = create_session('acq')
    session.data = {
        'hwp_state': {
            'direction': direction,
        },
        'timestamp': time.time(),
    }
    reply = OCSReply(ocs.OK, 'msg', session.encoded())
    client.monitor.status = MagicMock(return_value=reply)

    return client


@pytest.mark.parametrize('direction', ['ccw', 'cw'])
def test__get_direction(patch_clients_satp, direction):
    hwp.run.CLIENTS['hwp'] = create_hwp_client(direction)
    ret = hwp._get_direction()
    if direction == 'ccw':
        assert ret == 'ccw'
    elif direction == 'cw':
        assert ret == 'cw'
    hwp.run.CLIENTS['hwp'].monitor.status.assert_called_once()


@pytest.mark.parametrize('direction', [None, ''])
def test__get_direction_invalid(patch_clients_satp, direction):
    hwp.run.CLIENTS['hwp'] = create_hwp_client(direction)
    with pytest.raises(RuntimeError) as e:
        hwp._get_direction()
    assert str(e.value) == "The HWP direction is unknown. Aborting..."
    hwp.run.CLIENTS['hwp'].monitor.status.assert_called_once()


@pytest.mark.parametrize("active", [True, False])
def test_stop(patch_clients_satp, active):
    hwp.stop(active=active)
    if active:
        hwp.run.CLIENTS['hwp'].brake.assert_called_with()
    else:
        hwp.run.CLIENTS['hwp'].pmx_off.assert_called()


def test_stop_brake_voltage(patch_clients_satp):
    VOLTAGE = 5.0
    hwp.stop(active=True, brake_voltage=VOLTAGE)
    hwp.run.CLIENTS['hwp'].brake.assert_called_with(brake_voltage=VOLTAGE)


def test_set_freq(patch_clients_satp):
    hwp.set_freq(freq=2.0)
    hwp.run.CLIENTS['hwp'].pid_to_freq.assert_called_with(target_freq=2.0)
