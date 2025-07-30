import os
os.environ["OCS_CONFIG_DIR"] = "./test_util/"
os.environ["SORUNLIB_CONFIG"] = "./data/example_config.yaml"

from sorunlib.config import load_config

CONFIG = {'smurf_failure_threshold': 2,
          'wiregrid_motor_current': 3.0,
          'registry': 'registry',
          'wiregrid': {'labjack': 'wg-labjack'}}


def test_load_config():
    cfg = load_config("./data/example_config.yaml")
    assert cfg == CONFIG


def test_load_config_from_env():
    cfg = load_config()
    assert cfg == CONFIG
