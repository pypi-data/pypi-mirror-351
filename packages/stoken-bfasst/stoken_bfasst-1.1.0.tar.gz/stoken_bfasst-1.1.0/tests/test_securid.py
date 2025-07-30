import datetime

import pytest

try:
    from securid import Token
except ImportError:
    pytest.skip("securid not installed", allow_module_level=True)

import stoken_bfasst as sb


@pytest.mark.parametrize("ts_offset", [i + j for i in [0, 30, 60] for j in [0, 1, 14, 15, 16, 29]])
@pytest.mark.parametrize("digits", [8])
@pytest.mark.parametrize("interval", [30, 60])
def test_cross_verify_against_securid(interval, digits, ts_offset):
    token = Token(interval=interval, digits=digits, seed=bytes(range(16)), serial="1234567")

    timestamp = datetime.datetime(2000, 1, 2, 3, 4, 0, tzinfo=datetime.timezone.utc)
    timestamp += datetime.timedelta(seconds=ts_offset)

    params = sb.params_from_token(serial=token.serial, interval=interval, digits=digits, timestamp=timestamp)
    code_bfasst = sb.generate_passcode(seed=token.seed, params=params)
    code_securid = token.at(timestamp)

    assert code_bfasst == code_securid, "output code does not match"
