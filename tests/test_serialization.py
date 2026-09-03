import random

from bst_id.encoder import BSTIDEncoder
from bst_id.decoder import BSTIDDecoder
from bst_id.serialization import id_to_bytes, id_from_bytes
from bst_id.logic import iso8601_to_unix_time

T = iso8601_to_unix_time("2025-05-21T15:00:00Z")


def _roundtrip(bst_id: int, bit_len: int) -> None:
    data = id_to_bytes(bst_id, bit_len)
    assert isinstance(data, bytes)
    assert len(data) * 8 - bit_len < 8  # padding stays below one octet
    assert id_from_bytes(data) == (bst_id, bit_len)


def test_xy_roundtrip():
    bst_id, bit_len = BSTIDEncoder.encode(139.75, 35.68, None, None, 12, 12, 0, 0)
    _roundtrip(bst_id, bit_len)


def test_xyh_roundtrip():
    bst_id, bit_len = BSTIDEncoder.encode(139.75, 35.68, 10.0, None, 12, 12, 6, 0)
    _roundtrip(bst_id, bit_len)


def test_xyt_roundtrip():
    bst_id, bit_len = BSTIDEncoder.encode(139.75, 35.68, None, T, 12, 12, 0, 18)
    _roundtrip(bst_id, bit_len)


def test_xyht_roundtrip():
    bst_id, bit_len = BSTIDEncoder.encode(139.75, 35.68, 10.0, T, 12, 12, 6, 18)
    _roundtrip(bst_id, bit_len)


def test_leading_zero_presence_flag_survives():
    # y / altitude / t only: the x presence flag is 0, so the integer loses its
    # leading bit. The framed byte sequence must still round-trip exactly.
    bst_id, bit_len = BSTIDEncoder.encode(None, 35.68, 10.0, T, 0, 8, 6, 18)
    assert bst_id.bit_length() < bit_len
    _roundtrip(bst_id, bit_len)


def test_randomized_full_xyht_roundtrip():
    rng = random.Random(20260903)
    for _ in range(2000):
        x = rng.uniform(-179.9, 179.9)
        y = rng.uniform(-84.0, 84.0)
        f = rng.uniform(-16000.0, 16000.0)
        t = rng.randint(0, 2**31)
        zx, zy, zf, zt = (rng.randint(1, 20) for _ in range(4))
        bst_id, bit_len = BSTIDEncoder.encode(x, y, f, t, zx, zy, zf, zt)
        data = id_to_bytes(bst_id, bit_len)
        assert id_from_bytes(data) == (bst_id, bit_len)
        # the decoded coordinates are unchanged by the byte round-trip
        rid, rlen = id_from_bytes(data)
        assert BSTIDDecoder.decode(rid, rlen) == BSTIDDecoder.decode(bst_id, bit_len)
