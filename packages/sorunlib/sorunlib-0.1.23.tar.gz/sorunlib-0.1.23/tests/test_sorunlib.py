from unittest.mock import MagicMock, patch

from util import mocked_clients

import sorunlib
from sorunlib import initialize


@patch('sorunlib.commands.time.sleep', MagicMock())
@patch('sorunlib.create_clients', mocked_clients)
def test_initialize():
    initialize()
    assert sorunlib.CLIENTS is not None
