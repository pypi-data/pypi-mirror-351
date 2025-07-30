import os
os.environ["OCS_CONFIG_DIR"] = "./test_util/"
import datetime as dt

import pytest

from ocs.ocs_client import OCSReply
from sorunlib import acu

from util import create_patch_clients


patch_clients_satp = create_patch_clients('satp')
patch_clients_lat = create_patch_clients('ccat')


def test_move_to(patch_clients_satp):
    acu.move_to(180, 60)
    acu.run.CLIENTS['acu'].go_to.assert_called_with(az=180, el=60)


def test_move_to_failed(patch_clients_satp):
    mocked_response = OCSReply(
        0, 'msg', {'success': False, 'op_name': 'go_to'})
    acu.run.CLIENTS['acu'].go_to.side_effect = [mocked_response]
    with pytest.raises(RuntimeError):
        acu.move_to(180, 90)


def test_move_to_target_before_start(patch_clients_satp):
    start = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=10)
    end = start + dt.timedelta(seconds=3600)
    acu.move_to_target(300, 50, start.isoformat(), end.isoformat(), -0.005)
    acu.run.CLIENTS['acu'].go_to.assert_called_with(az=300, el=50)


def test_move_to_target_within_range(patch_clients_satp):
    start = dt.datetime.now(dt.timezone.utc)
    end = start + dt.timedelta(seconds=3600)
    acu.move_to_target(300, 50, start.isoformat(), end.isoformat(), -0.005)
    acu.run.CLIENTS['acu'].go_to.assert_called_once()


def test_move_to_target_after_stop(patch_clients_satp):
    start = dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=3600)
    end = start + dt.timedelta(seconds=3590)
    acu.move_to_target(300, 50, start.isoformat(), end.isoformat(), -0.005)
    acu.run.CLIENTS['acu'].go_to.assert_not_called()


def test_set_boresight(patch_clients_satp):
    acu.set_boresight(20)
    acu.run.CLIENTS['acu'].set_boresight.assert_called_with(target=20)


def test_set_boresight_lat(patch_clients_lat):
    acu.set_boresight(20)


def test_set_scan_params(patch_clients_satp):
    acu.set_scan_params(az_speed=2, az_accel=2, reset=True)
    acu.run.CLIENTS['acu'].set_scan_params.assert_called_with(
        az_speed=2,
        az_accel=2,
        reset=True)
