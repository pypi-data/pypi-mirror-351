import os
os.environ["OCS_CONFIG_DIR"] = "./test_util/"
import pytest
import datetime as dt

from unittest.mock import MagicMock, patch

from sorunlib.commands import wait_until


def mkts(offset):
    """Make timestamp.

    Args:
        offset (int): Offset from current time in seconds.

    Returns:
        str: ISO formatted timestamp 'offset' seconds from now, i.e.
            '2023-04-22T00:59:56.264293+00:00'

    Examples:
        An example called at '2023-04-24T21:14:27.790440+00:00':

        >>> mkts(1)
        '2023-04-24T21:14:28.790440+00:00'

    """
    now = dt.datetime.now(dt.timezone.utc)
    delta = dt.timedelta(seconds=offset)
    ts = now + delta
    return ts.isoformat()


# patch out time.sleep so we don't actually sleep during testing
@patch('sorunlib.commands.time.sleep', MagicMock())
@pytest.mark.parametrize("timestamp,tolerance", [
    # timestamp in past, not high enough tolerance
    (mkts(-10), 5),
    # timestamp in future, but past tolerance timestamp
    (mkts(1), mkts(-1))])
def test_wait_until_past_tolerance(timestamp, tolerance):
    with pytest.raises(ValueError):
        wait_until(timestamp, tolerance)


@patch('sorunlib.commands.time.sleep', MagicMock())
def test_wait_until_unsupported_tolerance():
    with pytest.raises(ValueError):
        wait_until(mkts(1), tolerance=[1, 2])


def test_wait_until_unsupported_tz():
    with pytest.raises(ValueError):
        tz = dt.timezone(offset=dt.timedelta(hours=5))
        t = dt.datetime.now(tz).isoformat()  # i.e. '2023-04-22T00:59:56.264293+05:00'
        wait_until(t)


@patch('sorunlib.commands.time.sleep', MagicMock())
@pytest.mark.parametrize("timestamp,tolerance", [
    # timestamps in future, future or no tolerance
    (mkts(1), None),
    (mkts(1), 5),
    (mkts(1), mkts(10)),
    # timestamps in past, high enough or no tolerance
    (mkts(-1), None),
    (mkts(-1), 5),
    (mkts(-1), mkts(10)),
    # test mix of tz aware timestamp, naive tolerance timestamp
    (mkts(0), mkts(10)[:-6]),
    (mkts(0)[:-6], mkts(10)),
    # testing TZ detection w/past timestamps, no tolerance
    ("2020-01-01T00:00:00", None),
    ("2020-01-01T00:00:00+00:00", None)])
def test_wait_until(timestamp, tolerance):
    wait_until(timestamp, tolerance)
