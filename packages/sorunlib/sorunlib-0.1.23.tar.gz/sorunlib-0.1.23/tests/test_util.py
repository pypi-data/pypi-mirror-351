import os
import pytest

from ocs.client_http import ControlClientError
from unittest.mock import MagicMock, patch

from sorunlib import util
from sorunlib.util import CrossbarConnectionError

os.environ["OCS_CONFIG_DIR"] = "./test_util/"
os.environ["SORUNLIB_CONFIG"] = "./data/example_config.yaml"


# I think this could be generalized with the Mock 'spec' argument, building an
# object that mocks a given Agent's API, but I'm not totally sure we need that
# yet, or how to make it so a different spec is loaded depending on which agent
# the client is for.
def create_mock_ocsclient(session):
    def mock_client(*args, **kwargs):
        client = MagicMock()
        client.main.status = MagicMock(return_value=(None, None, session))
        return client

    return mock_client


reg_session = {'session_id': 0,
               'op_name': 'main',
               'op_code': 3,
               'status': 'running',
               'success': None,
               'start_time': 1669919099.7585046,
               'end_time': None,
               'data': {
                   'observatory.smurf-file-emulator-5': {
                       'expired': False,
                       'time_expired': None,
                       'last_updated': 1669935108.8366735,
                       'op_codes': {
                           'uxm_setup': 1,
                           'uxm_relock': 1,
                           'take_iv': 1,
                           'take_bias_steps': 1,
                           'take_bgmap': 1,
                           'bias_dets': 1,
                           'take_noise': 1,
                           'stream': 1},
                       'agent_class': 'SmurfFileEmulator',
                       'agent_address': 'observatory.smurf-file-emulator-5'},
                   'observatory.smurf-file-emulator-7': {
                       'expired': False,
                       'time_expired': None,
                       'last_updated': 1669935108.989246,
                       'op_codes': {
                           'uxm_setup': 1,
                           'uxm_relock': 1,
                           'take_iv': 1,
                           'take_bias_steps': 1,
                           'take_bgmap': 1,
                           'bias_dets': 1,
                           'take_noise': 1,
                           'stream': 1},
                       'agent_class': 'SmurfFileEmulator',
                       'agent_address': 'observatory.smurf-file-emulator-7'},
                   'observatory.fake-data-1': {
                       'expired': True,
                       'time_expired': None,
                       'last_updated': 1669935108.989246,
                       'op_codes': {
                           'acq': 3,
                           'count': 3,
                           'set_heartbeat': 1,
                           'delay_task': 1},
                       'agent_class': 'FakeDataAgent',
                       'agent_address': 'observatory.fake-data-1'},
                   'observatory.hwp-supervisor': {
                       'expired': False,
                       'time_expired': None,
                       'last_updated': 1710168924.336035,
                       'op_codes': {
                           'monitor': 3,
                           'spin_control': 3,
                           'pid_to_freq': 1,
                           'set_const_voltage': 1,
                           'brake': 1,
                           'pmx_off': 1,
                           'abort_action': 7
                       },
                       'agent_class': 'HWPSupervisor',
                       'agent_address': 'observatory.hwp-supervisor'
                   },
                   'observatory.acu-sat1': {
                       'expired': False,
                       'time_expired': None,
                       'last_updated': 1669997169.469505,
                       'op_codes': {
                           'monitor': 3,
                           'broadcast': 3,
                           'generate_scan': 1,
                           'go_to': 1,
                           'constant_velocity_scan': 1,
                           'fromfile_scan': 1,
                           'set_boresight': 1,
                           'stop_and_clear': 1},
                       'agent_class': 'ACUAgent',
                       'agent_address': 'observatory.acu-sat1'}}}
mock_registry_client = create_mock_ocsclient(reg_session)

reg_session_single_smurf = {'session_id': 0,
                            'op_name': 'main',
                            'op_code': 3,
                            'status': 'running',
                            'success': None,
                            'start_time': 1669919099.7585046,
                            'end_time': None,
                            'data': {
                                'observatory.smurf-file-emulator-5': {
                                    'expired': False,
                                    'time_expired': None,
                                    'last_updated': 1669935108.8366735,
                                    'op_codes': {
                                        'uxm_setup': 1,
                                        'uxm_relock': 1,
                                        'take_iv': 1,
                                        'take_bias_steps': 1,
                                        'take_bgmap': 1,
                                        'bias_dets': 1,
                                        'take_noise': 1,
                                        'stream': 1},
                                    'agent_class': 'SmurfFileEmulator',
                                    'agent_address': 'observatory.smurf-file-emulator-5'}}}
mock_registry_client_single_smurf = create_mock_ocsclient(reg_session_single_smurf)


class NoAgentClient:
    def __init__(self, *args, **kwargs):
        raise ControlClientError("no callee registered for procedure fake.agent.op")


class UnexpectedErrorClient:
    def __init__(self, *args, **kwargs):
        raise ControlClientError("Server replied with code 500")


def test_load_site_config():
    cfg = util._load_site_config()
    assert 'localhost' in cfg.hosts
    assert 'ocs-docker' in cfg.hosts
    assert 'registry_address' in cfg.hub.data


def test_find_instances():
    instances = util._find_instances('PysmurfController')
    assert instances == ['pysmurf-controller']


def test_find_instances_host():
    instances = util._find_instances('PysmurfController', host='localhost')
    assert instances == []


@patch('sorunlib.util.OCSClient', mock_registry_client)
def test_find_active_instances():
    instances = util._find_active_instances('SmurfFileEmulator')
    assert 'smurf-file-emulator-5' in instances
    assert 'smurf-file-emulator-7' in instances


@patch('sorunlib.util.OCSClient', mock_registry_client)
def test_find_active_instances_expired():
    instances = util._find_active_instances('FakeDataAgent')
    assert 'fake-data-1' not in instances


def test__try_client_no_crossbar_connection():
    """This test assumes a crossbar server isn't running at
    http://localhost:8001. It tests that we raise an error when trying to
    connect to the registry to scan for agents if crossbar is unavailable."""
    with pytest.raises(CrossbarConnectionError):
        util._try_client('test-agent')


@patch('sorunlib.util.OCSClient', NoAgentClient)
def test__try_client_no_agent_connection():
    """This tests that we get None back when the agent is offline."""
    client = util._try_client('test-agent')
    assert client is None


@patch('sorunlib.util.OCSClient', UnexpectedErrorClient)
def test__try_client_other_error():
    with pytest.raises(ControlClientError):
        util._try_client('test-agent')


@patch('sorunlib.util.OCSClient', mock_registry_client)
def test_create_clients():
    clients = util.create_clients()
    assert 'acu' in clients
    assert 'smurf' in clients
    assert len(clients['smurf']) == 0  # since we're not in test_mode
    assert 'wiregrid' in clients


@patch('sorunlib.util.OCSClient', mock_registry_client)
def test_create_clients_test_mode():
    clients = util.create_clients(test_mode=True)
    assert 'acu' in clients
    assert 'smurf' in clients
    assert len(clients['smurf']) == 2
    assert 'wiregrid' in clients


@patch('sorunlib.util.OCSClient', mock_registry_client_single_smurf)
def test_create_clients_test_mode_single_smurf():
    clients = util.create_clients(test_mode=True)
    assert 'smurf' in clients
    assert len(clients['smurf']) == 1


@patch('sorunlib.util.OCSClient', mock_registry_client)
def test__create_clients_minimal_config():
    clients = util.create_clients(sorunlib_config='./data/minimal_config.yaml')
    assert 'acu' in clients
    assert 'smurf' in clients
    assert len(clients['smurf']) == 0  # since we're not in test_mode
    # Optional configs
    assert 'wiregrid' in clients
    for client in clients['wiregrid'].values():
        assert client is None
