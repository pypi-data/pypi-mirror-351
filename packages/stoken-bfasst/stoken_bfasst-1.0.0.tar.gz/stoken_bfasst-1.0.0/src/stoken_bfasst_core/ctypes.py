from __future__ import annotations

import ctypes
from ctypes import c_byte, c_ubyte, c_int, c_char_p, c_size_t, POINTER, cast, c_void_p
from datetime import datetime
from typing import Iterator

c_ubyte_p = ctypes.POINTER(ctypes.c_ubyte)


class Parameters(ctypes.Structure):
    # struct StokenBruteForceAssist
    _fields_ = [
        ("seed", c_byte * 16),
        ("code_out", c_byte * 16),
        ("time_blocks", c_byte * (16 * 5)),
        ("digits", c_int),
        ("key_time_offset", c_int),
    ]

    @property
    def code_out_str(self):
        s = bytes(self.code_out)
        return s[: s.find(0)].decode("ascii")


class RawLib:
    @staticmethod
    def errcheck(result, func, *args, **kwargs):
        if result != 0:
            raise ValueError(f"function returned {result}")

    def __init__(self, lib):
        self.lib = lib

        self.generate_passcode = f = lib["stoken_bfasst_generate_passcode"]
        f.argtypes = [POINTER(Parameters)]
        f.restype = c_int
        f.errcheck = self.errcheck

        self.search_seed = f = lib["stoken_bfasst_search_seed"]
        f.argtypes = [
            POINTER(Parameters),
            c_char_p,  # wanted_code
            c_ubyte_p,  # 16-byte seeds
            c_size_t,  # seed count
            POINTER(c_size_t),  # index of successful seed
        ]
        f.restype = c_int
        f.errcheck = self.errcheck


def to_ubyte_array(data: bytes | memoryview | bytearray):
    if isinstance(data, bytes):
        t = c_ubyte * len(data)
        return cast(c_char_p(data), POINTER(t))
    else:
        data = memoryview(data)  # works whether it's a bytearray or a memoryview
        assert data.contiguous
        t = c_ubyte * data.nbytes
        return t.from_buffer(data)


class Lib:
    def __init__(self, raw_lib: RawLib):
        self.raw_lib = raw_lib

    @staticmethod
    def params_from_time_blocks(
        time_blocks: bytes | memoryview, digits: int, key_time_offset: int, seed: bytes | memoryview | None = None
    ):
        """You probably want to use :meth:`params_from_token` instead."""
        value = Parameters()

        if len(time_blocks) != 16 * 5:
            raise ValueError("time_blocks must have 5 * 16 elements")

        value.time_blocks[:] = time_blocks
        value.key_time_offset = key_time_offset
        value.digits = digits
        if seed is not None:
            value.seed[:] = seed
        return value

    @classmethod
    def params_from_token(cls, serial: str, interval: int, digits: int, timestamp: int | datetime):
        """
        Generate parameters from token information. This requires the :mod:`securid` module as a dependency.
        """
        # optional securid dependency
        from .securid import compute_time_blocks

        if not isinstance(timestamp, datetime):
            timestamp = datetime.utcfromtimestamp(int(timestamp))

        return cls.params_from_time_blocks(
            **compute_time_blocks(serial=serial, interval=interval, digits=digits, timestamp=timestamp)
        )

    def generate_passcode(self, seed: bytes, params: Parameters) -> str:
        """
        Generate a code given a *seed* and parameters *params*. This is provided mostly for debugging purposes.
        """
        if len(seed) != 16:
            raise ValueError("seed must be 16 bytes")
        params.seed[:] = seed
        self.raw_lib.generate_passcode(params)
        return params.code_out_str

    def search_seed(self, wanted_code: str, seeds: bytes | memoryview | bytearray, params: Parameters) -> Iterator[int]:
        """
        Search for a 16-byte seed among *seeds* such that when evaluated with parameters *params*, it gives you
        *wanted_code*.

        Yield every index inside *seeds* for which the generated code matches *wanted_code*.
        """
        out_index = c_size_t(-1)
        out_not_found = out_index.value
        wanted_code = ctypes.create_string_buffer(wanted_code.encode("ascii"))
        seeds_ptr = cast(to_ubyte_array(seeds), c_void_p).value
        seed_size = 16
        seeds_count = len(seeds) // seed_size

        index_offset = 0
        while seeds_count > 0:
            out_index.value = out_not_found
            self.raw_lib.search_seed(params, wanted_code, cast(c_void_p(seeds_ptr), c_ubyte_p), seeds_count, out_index)
            index = out_index.value

            if index == out_not_found:
                break

            yield index + index_offset

            delta = index + 1
            seeds_count -= delta
            seeds_ptr += delta * seed_size
            index_offset += delta
            del delta
