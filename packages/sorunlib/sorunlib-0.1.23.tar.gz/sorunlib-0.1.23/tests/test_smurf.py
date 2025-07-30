import os
os.environ["OCS_CONFIG_DIR"] = "./test_util/"

from unittest.mock import MagicMock, patch

import pytest

from ocs.client_http import ControlClientError
from ocs.ocs_client import OCSReply

import sorunlib as run
from sorunlib import smurf
from util import create_patch_clients

os.environ["SORUNLIB_CONFIG"] = "./data/example_config.yaml"


# Use pytest-mock plugin to patch CLIENTS on all tests
patch_clients = create_patch_clients('satp', autouse=True)


# Used to mock errors communicating with an OCS Client
class ErrorProcess:
    def __init__(self, *args, **kwargs):
        pass

    def start(self, **kwargs):
        raise ControlClientError("no callee registered for procedure <observatory.controller.ops")

    def wait(self, timeout=None):
        raise ControlClientError("no callee registered for procedure <observatory.controller.ops")

    def status(self):
        raise ControlClientError("no callee registered for procedure <observatory.controller.ops")

    def stop(self):
        raise ControlClientError("no callee registered for procedure <observatory.controller.ops")


class ErrorClient:
    def __init__(self, instance_id, *args, **kwargs):
        self.stream = ErrorProcess()
        self.instance_id = instance_id


def test_set_targets():
    smurf.set_targets(['smurf1'])
    assert len(smurf.run.CLIENTS['smurf']) == 1
    assert smurf.run.CLIENTS['smurf'][0].instance_id == 'smurf1'


@patch('sorunlib.smurf.time.sleep', MagicMock())
@pytest.mark.parametrize("concurrent", [(True), (False)])
def test_bias_step(concurrent):
    smurf.bias_step(concurrent=concurrent, settling_time=10)
    for client in smurf.run.CLIENTS['smurf']:
        client.take_bias_steps.start.assert_called_with(tag=None)


@patch('sorunlib.smurf.time.sleep', MagicMock())
@pytest.mark.parametrize("concurrent", [(True), (False)])
def test_bias_step_single_failure(concurrent):
    # Create failure on smurf1
    mocked_response = OCSReply(
        0, 'msg', {'success': False, 'op_name': 'bias_step'})
    smurf.run.CLIENTS['smurf'][0].take_bias_steps.wait.side_effect = [mocked_response]

    smurf.bias_step(concurrent=concurrent, settling_time=10)
    for client in smurf.run.CLIENTS['smurf']:
        client.take_bias_steps.start.assert_called_once()


@patch('sorunlib.smurf.time.sleep', MagicMock())
@pytest.mark.parametrize("concurrent", [(True), (False)])
def test_bias_step_failure_threshold(concurrent):
    # Create failure on smurf1 and smurf2
    mocked_response = OCSReply(
        0, 'msg', {'success': False, 'op_name': 'bias_step'})
    smurf.run.CLIENTS['smurf'][0].take_bias_steps.wait.side_effect = [mocked_response]
    smurf.run.CLIENTS['smurf'][1].take_bias_steps.wait.side_effect = [mocked_response]

    with pytest.raises(RuntimeError):
        smurf.bias_step(concurrent=concurrent, settling_time=10)


@patch('sorunlib.smurf.time.sleep', MagicMock())
@pytest.mark.parametrize("concurrent", [(True), (False)])
def test_iv_curve(concurrent):
    smurf.iv_curve(concurrent=concurrent)
    for client in smurf.run.CLIENTS['smurf']:
        client.take_iv.start.assert_called_with(tag=None, kwargs=None)


@patch('sorunlib.smurf.time.sleep', MagicMock())
@pytest.mark.parametrize("concurrent", [(True), (False)])
def test_uxm_setup(concurrent):
    smurf.uxm_setup(concurrent=concurrent)
    for client in smurf.run.CLIENTS['smurf']:
        client.uxm_setup.start.assert_called_once()


@patch('sorunlib.smurf.time.sleep', MagicMock())
@pytest.mark.parametrize("concurrent", [(True), (False)])
def test_uxm_relock(concurrent):
    smurf.uxm_relock(concurrent=concurrent)
    for client in smurf.run.CLIENTS['smurf']:
        client.uxm_relock.start.assert_called_once()


@patch('sorunlib.smurf.time.sleep', MagicMock())
@pytest.mark.parametrize("test_mode", [(True), (False)])
def test_uxm_relock_test_mode(test_mode):
    smurf.uxm_relock(test_mode=test_mode)
    for client in smurf.run.CLIENTS['smurf']:
        if test_mode:
            client.uxm_relock.start.assert_called_with(test_mode=test_mode)
        else:
            client.uxm_relock.start.assert_called_with()


@pytest.mark.parametrize("concurrent", [(True), (False)])
def test_bias_dets(concurrent):
    smurf.bias_dets(concurrent=concurrent)
    for client in smurf.run.CLIENTS['smurf']:
        client.bias_dets.start.assert_called_once()


@pytest.mark.parametrize("concurrent", [(True), (False)])
def test_set_biases(concurrent):
    smurf.set_biases(bias=1, bias_group=None, concurrent=concurrent)
    for client in smurf.run.CLIENTS['smurf']:
        client.set_biases.start.assert_called_with(bias=1, bgs=None)


@pytest.mark.parametrize("concurrent", [(True), (False)])
def test_zero_biases(concurrent):
    smurf.zero_biases(bias_group=None, concurrent=concurrent)
    for client in smurf.run.CLIENTS['smurf']:
        client.zero_biases.start.assert_called_with(bgs=None)


@pytest.mark.parametrize("concurrent", [(True), (False)])
def test_bgmap(concurrent):
    smurf.take_bgmap(concurrent=concurrent)
    for client in smurf.run.CLIENTS['smurf']:
        client.take_bgmap.start.assert_called_with(tag=None)


@pytest.mark.parametrize("concurrent", [(True), (False)])
def test_take_noise(concurrent):
    smurf.take_noise(concurrent=concurrent)
    for client in smurf.run.CLIENTS['smurf']:
        client.take_noise.start.assert_called_with(tag=None)


@pytest.mark.parametrize("concurrent", [(True), (False)])
def test_shutdown(concurrent):
    smurf.shutdown(concurrent=concurrent)
    for client in smurf.run.CLIENTS['smurf']:
        client.all_off.start.assert_called_once()


@pytest.mark.parametrize("state", [("on"), ("off")])
def test_stream(state):
    smurf.stream(state=state)
    for client in smurf.run.CLIENTS['smurf']:
        if state == "on":
            client.stream.start.assert_called_once()
        else:
            client.stream.stop.assert_called_once()


@pytest.mark.parametrize("state", [("on"), ("off")])
def test_stream_single_failure(state):
    # Create failure on smurf1
    mocked_response = OCSReply(
        0, 'msg', {'success': False, 'op_name': 'stream'})
    # For state == 'on'
    smurf.run.CLIENTS['smurf'][0].stream.status.side_effect = [mocked_response]
    # For state == 'off'
    smurf.run.CLIENTS['smurf'][0].stream.wait.side_effect = [mocked_response]

    smurf.stream(state=state)
    for client in smurf.run.CLIENTS['smurf']:
        if state == "on":
            client.stream.start.assert_called_once()
        else:
            client.stream.stop.assert_called_once()


def test_stream_agent_unavailable_on_stop():
    # Replace 'smurf1' client with one that will error on stream.stop()
    run.CLIENTS['smurf'][0] = ErrorClient('smurf1')
    smurf.stream(state='off')
