"""
This module contains the code that depends on securid. It is an optional dependency, so we don't
import this module by default.
"""

from datetime import datetime

from securid import token as _token


class TokenHackOutputException(Exception):
    """Used to return key information out of :class:`TokenHack`."""


class TokenHack(_token.Token):
    def _output_code(self, input: datetime, key: bytes):
        """
        Hack which figures out the key_time_offset.
        """
        cookie = 123
        fake_key = bytes((i + cookie if j == 3 else 0) for i in range(4) for j in range(4))
        fake_code = super()._output_code(input, fake_key)
        key_time_offset = int(fake_code) - cookie
        assert 0 <= key_time_offset < 4
        raise TokenHackOutputException("catch this", key_time_offset)

    def stoken_bfasst_generate_time_blocks(self, input: datetime) -> bytes:
        """
        Hack which generates the time blocks. This is a modified version of :meth:`generate_otp`.
        """
        out = []
        bcd_time = self._compute_bcd_time(input)
        for bcd_time_bytes in _token.BCD_TIME_BYTES:
            out.append(self._key_from_time(bcd_time, bcd_time_bytes, self.serial))

        return b"".join(out)


def compute_time_blocks(serial: str, interval: int, digits: int, timestamp: datetime) -> dict:
    token = TokenHack(serial=serial, seed=b"x" * 16, interval=interval, digits=8)
    try:
        # Here we are using an exception as a form of non-local control flow.
        token.at(timestamp)
        raise AssertionError("expected to catch TokenHackOutput")  # pragma: no cover
    except TokenHackOutputException as exc:
        d = dict(key_time_offset=exc.args[1])
    d["time_blocks"] = token.stoken_bfasst_generate_time_blocks(timestamp)
    d["digits"] = digits
    return d
