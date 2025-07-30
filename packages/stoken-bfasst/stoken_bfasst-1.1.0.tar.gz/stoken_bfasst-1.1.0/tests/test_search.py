import random
import struct

import pytest

import stoken_bfasst as sb


def randbytes(n):
    rr = random.randrange
    return bytes(rr(256) for i in range(n))


@pytest.mark.parametrize("kto", list(range(4)))
@pytest.mark.parametrize("digits", [1, 2, 4, 8])
@pytest.mark.parametrize("random_seed", list(range(3)))
def test_search(random_seed, digits, kto):
    random.seed(random_seed)

    correct_seed = randbytes(16)
    time_blocks = randbytes(16 * 5)

    def make_params():
        return sb.params_from_time_blocks(time_blocks=time_blocks, digits=digits, key_time_offset=kto)

    passcode = sb.generate_passcode(correct_seed, make_params())

    seed_count = 10000
    buf = bytearray(range(16)) * seed_count
    for i in range(seed_count):
        buf[i * 16 : i * 16 + 4] = struct.pack("!i", i)

    correct_indices = {random.randrange(seed_count) for i in range(3)}

    for i in correct_indices:
        buf[i * 16 : (i + 1) * 16] = correct_seed

    # search through "buf" and return the seed indices that give you the same output passcode
    found_indices = set(sb.search_seed(wanted_code=passcode, seeds=buf, params=make_params()))

    assert correct_indices.issubset(found_indices)
    for i in range(seed_count):
        # check that an index *i* appears in *found_indices* if and only if the seed gives you a matching passcode
        seed_i = buf[i * 16 : (i + 1) * 16]
        seed_i_passcode = sb.generate_passcode(seed_i, make_params())
        matches = seed_i_passcode == passcode
        assert (i in found_indices) == matches
