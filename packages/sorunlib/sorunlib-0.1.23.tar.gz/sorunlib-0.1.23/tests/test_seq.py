import os
os.environ["OCS_CONFIG_DIR"] = "./test_util/"
os.environ["SORUNLIB_CONFIG"] = "./data/example_config.yaml"
import datetime as dt

import ocs
import pytest
from unittest.mock import MagicMock, patch
from ocs.ocs_client import OCSReply

import sorunlib
from sorunlib import seq

from util import create_patch_clients, create_session


patch_clients = create_patch_clients('satp')


@patch('sorunlib._internal.time.sleep', MagicMock())
def test_scan(patch_clients):
    # This affects test runtime duration keep it short
    target = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=0.01)
    seq.scan(description='test', stop_time=target.isoformat(), width=20.)


@patch('sorunlib._internal.time.sleep', MagicMock())
def test_scan_passed_stop_time(patch_clients):
    # This affects test runtime duration keep it short
    target = dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=10)
    seq.scan(description='test', stop_time=target.isoformat(), width=20.)
    seq.run.CLIENTS['acu'].generate_scan.start.assert_not_called()


@patch('sorunlib._internal.time.sleep', MagicMock())
def test_scan_passed_min_duration(patch_clients):
    # This affects test runtime duration keep it short
    target = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=10)
    seq.scan(description='test', stop_time=target.isoformat(), width=20., min_duration=60)
    seq.run.CLIENTS['acu'].generate_scan.start.assert_not_called()


@patch('sorunlib.commands.time.sleep', MagicMock())
def test_scan_no_session(patch_clients):
    # Setup mock OCSReply without session object
    mock_reply = MagicMock()
    mock_reply.session = None
    sorunlib.CLIENTS['acu'].generate_scan.start = MagicMock(return_value=mock_reply)

    target = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=1)
    with pytest.raises(Exception):
        seq.scan(description='test', stop_time=target.isoformat(), width=20.)


@patch('sorunlib.commands.time.sleep', MagicMock())
def test_scan_failed_to_start(patch_clients):
    # Setup mock OCSReply with failed status
    failed_session = create_session('generate_scan')
    failed_session.success = False
    failed_session.set_status('running')
    failed_session.add_message('A simulated error has occurred.')
    failed_session.set_status('done')

    mock_reply = OCSReply(ocs.OK, 'msg', failed_session.encoded())
    sorunlib.CLIENTS['acu'].generate_scan.start = MagicMock(return_value=mock_reply)
    sorunlib.CLIENTS['acu'].generate_scan.wait = MagicMock(return_value=mock_reply)

    # Example of failed reply this is trying to emulate.
    # OCSReply: OK : Operation "generate_scan" is currently not running (FAILED).
    #   generate_scan[session=15]; status=done with ERROR 116.5 s ago, took 68.8 s
    #   messages (4 of 4):
    #     1702337679.564 Status is now "starting".
    #     1702337679.565 Status is now "running".
    #     1702337748.356 Problems during scan
    #     1702337748.357 Status is now "done".
    #   other keys in .session: op_code, data
    print(mock_reply)

    target = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=10)
    with pytest.raises(RuntimeError):
        seq.scan(description='test', stop_time=target.isoformat(), width=20.)


@patch('sorunlib._internal.time.sleep', MagicMock())
def test_scan_failed_smurfs_on_shutdown(patch_clients):
    # Create failure on all three smurf agents
    mocked_response = OCSReply(
        0, 'msg', {'success': False, 'op_name': 'stream'})
    seq.run.CLIENTS['smurf'][0].stream.wait.side_effect = [mocked_response]
    seq.run.CLIENTS['smurf'][1].stream.wait.side_effect = [mocked_response]
    seq.run.CLIENTS['smurf'][2].stream.wait.side_effect = [mocked_response]

    seq._stop_scan()
    seq.run.CLIENTS['acu'].generate_scan.wait.assert_called()
