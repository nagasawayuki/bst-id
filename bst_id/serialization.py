"""Canonical external serialization for BST-ID.

The canonical on-the-wire form of a BST-ID is an **unsigned byte sequence**:

    [4-bit XYHT presence flags]
    [5-bit stored-zoom field per active axis, in x, y, f, t order]
    [coordinate prefix bits per active axis, in x, y, f, t order]
    [trailing zero padding up to the next octet boundary]

(``f`` is the current package spelling of the altitude/height axis; the
manuscript calls it ``h``.)

Stored zoom is ``zoom - 1`` (``00000`` -> level 1, ``11111`` -> level 32),
matching :class:`bst_id.encoder.BSTIDEncoder`.

A bare Python ``int`` remains a convenient internal representation, but it is
not the canonical serialization: integer parsing via ``int.bit_length()``
silently drops leading zero bits, so an ID whose highest presence flag is 0
cannot be parsed unambiguously from an integer alone. The byte sequence is
self-framing -- the presence flags and per-axis zoom fields determine the
exact payload length, and everything after it is padding.
"""
from typing import Tuple

_AXES = ("x", "y", "f", "t")


def id_to_bytes(bst_id: int, bit_len: int) -> bytes:
    """Pack ``(bst_id, bit_len)`` into the canonical unsigned byte sequence.

    ``bst_id`` / ``bit_len`` are the pair returned by
    :meth:`bst_id.encoder.BSTIDEncoder.encode`.
    """
    if bit_len < 4:
        raise ValueError("bit_len must be at least 4 (the presence flags)")
    if bst_id < 0 or bst_id.bit_length() > bit_len:
        raise ValueError("bst_id does not fit in bit_len bits")
    pad = (-bit_len) % 8
    return (bst_id << pad).to_bytes((bit_len + pad) // 8, "big")


def id_from_bytes(data: bytes) -> Tuple[int, int]:
    """Recover the exact ``(bst_id, bit_len)`` pair from a byte sequence.

    Trailing padding bits are discarded. Leading zero presence flags are
    preserved because the frame length is derived from the header, not from
    the integer's ``bit_length()``.
    """
    total_bits = len(data) * 8
    if total_bits < 8:
        raise ValueError("byte sequence too short to contain a BST-ID header")
    raw = int.from_bytes(data, "big")

    pos = total_bits

    def read(n: int) -> int:
        nonlocal pos
        pos -= n
        return (raw >> pos) & ((1 << n) - 1)

    flags = read(4)
    active = [(flags >> (3 - i)) & 1 for i in range(4)]

    payload_bits = 0
    for is_active in active:
        if is_active:
            zoom_m1 = read(5)
            payload_bits += zoom_m1 + 1

    bit_len = 4 + 5 * sum(active) + payload_bits
    if bit_len > total_bits:
        raise ValueError("declared BST-ID length exceeds the byte sequence")
    bst_id = raw >> (total_bits - bit_len)
    return bst_id, bit_len
