"""Reference region algebra for BST-ID.

This module implements the binary/prefix operations used in the journal draft.
It operates on parsed BST-ID cell descriptors and therefore does not reconstruct
continuous geometry for Boolean region operations.

Notes
-----
* The public BST-ID package currently parses an integer ID using ``bit_length``.
  Integer serialization drops leading zero bits, so IDs whose highest presence
  flag is zero require an explicit bit length (or another framed serialization)
  for unambiguous parsing.  The algebra itself is independent of this issue;
  tests below use full XYHT IDs or construct ``Cell`` objects directly.
* The implementation uses axis name ``f`` because that is the current package
  spelling for the altitude/height axis.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Dict, Iterable, Iterator, Mapping, Optional, Sequence, Tuple

from .logic import parse_bst_id, build_bst_id

AXES: Tuple[str, ...] = ("x", "y", "f", "t")


@dataclass(frozen=True, order=True)
class Cell:
    """One BST-ID hierarchical cell as per-axis (zoom, integer-prefix) pairs."""

    flags: int
    zooms: Tuple[int, int, int, int]
    values: Tuple[int, int, int, int]

    @classmethod
    def from_id(cls, bst_id: int) -> "Cell":
        flags, z, v = parse_bst_id(bst_id)
        zooms = tuple(z.get(a, 0) for a in AXES)
        values = tuple(v.get(a, 0) for a in AXES)
        return cls(flags, zooms, values)

    @classmethod
    def from_parts(
        cls,
        *,
        x: Optional[Tuple[int, int]] = None,
        y: Optional[Tuple[int, int]] = None,
        f: Optional[Tuple[int, int]] = None,
        t: Optional[Tuple[int, int]] = None,
    ) -> "Cell":
        parts = {"x": x, "y": y, "f": f, "t": t}
        flags = 0
        zs = []
        vs = []
        for idx, axis in enumerate(AXES):
            p = parts[axis]
            if p is None:
                zs.append(0); vs.append(0)
                continue
            z, value = p
            if not (1 <= z <= 32):
                raise ValueError(f"zoom for {axis} must be in [1,32]")
            if not (0 <= value < (1 << z)):
                raise ValueError(f"value for {axis} does not fit zoom {z}")
            flags |= 1 << (3 - idx)
            zs.append(z); vs.append(value)
        return cls(flags, tuple(zs), tuple(vs))

    def to_id(self) -> int:
        z = {a: self.zooms[i] for i, a in enumerate(AXES) if self.active(i)}
        v = {a: self.values[i] for i, a in enumerate(AXES) if self.active(i)}
        return build_bst_id(self.flags, z, v)

    def active(self, axis: int | str) -> bool:
        i = AXES.index(axis) if isinstance(axis, str) else axis
        return bool((self.flags >> (3 - i)) & 1)

    def descriptor(self, axis: int | str) -> Tuple[int, int]:
        i = AXES.index(axis) if isinstance(axis, str) else axis
        if not self.active(i):
            raise ValueError(f"axis {AXES[i]} is not active")
        return self.zooms[i], self.values[i]

    def replace_axis(self, axis: int | str, zoom: int, value: int) -> "Cell":
        i = AXES.index(axis) if isinstance(axis, str) else axis
        if not self.active(i):
            raise ValueError(f"axis {AXES[i]} is not active")
        zs = list(self.zooms); vs = list(self.values)
        zs[i] = zoom; vs[i] = value
        return Cell(self.flags, tuple(zs), tuple(vs))


def _same_domain(a: Cell, b: Cell) -> None:
    if a.flags != b.flags:
        raise ValueError("region algebra requires the same presence vector")


def truncate(value: int, zoom: int, q: int) -> int:
    if not (0 <= q <= zoom):
        raise ValueError("q must satisfy 0 <= q <= zoom")
    return value >> (zoom - q)


def compatible(a: Cell, b: Cell) -> bool:
    """True iff the two dyadic cells overlap in every active axis."""
    _same_domain(a, b)
    for i in range(4):
        if not a.active(i):
            continue
        za, va = a.zooms[i], a.values[i]
        zb, vb = b.zooms[i], b.values[i]
        q = min(za, zb)
        if truncate(va, za, q) != truncate(vb, zb, q):
            return False
    return True


def subsumes(container: Cell, contained: Cell) -> bool:
    """Return True iff C(contained) is a subset of C(container)."""
    _same_domain(container, contained)
    for i in range(4):
        if not container.active(i):
            continue
        zc, vc = container.zooms[i], container.values[i]
        zd, vd = contained.zooms[i], contained.values[i]
        if zc > zd or vc != truncate(vd, zd, zc):
            return False
    return True


def meet(a: Cell, b: Cell) -> Optional[Cell]:
    """Anisotropic cell intersection (axis-wise longer compatible prefix)."""
    _same_domain(a, b)
    if not compatible(a, b):
        return None
    zs = list(a.zooms); vs = list(a.values)
    for i in range(4):
        if not a.active(i):
            continue
        if b.zooms[i] > a.zooms[i]:
            zs[i] = b.zooms[i]
            vs[i] = b.values[i]
    return Cell(a.flags, tuple(zs), tuple(vs))


def refine_axis(c: Cell, axis: int | str) -> Tuple[Cell, Cell]:
    i = AXES.index(axis) if isinstance(axis, str) else axis
    z, v = c.descriptor(i)
    if z >= 32:
        raise ValueError("cannot refine beyond zoom 32")
    return (
        c.replace_axis(i, z + 1, (v << 1) | 0),
        c.replace_axis(i, z + 1, (v << 1) | 1),
    )


def refine(c: Cell, axes: Sequence[int | str]) -> Tuple[Cell, ...]:
    out = [c]
    for axis in axes:
        nxt = []
        for cell in out:
            nxt.extend(refine_axis(cell, axis))
        out = nxt
    return tuple(out)


def coarsen(c: Cell, targets: Mapping[str, int]) -> Cell:
    out = c
    for axis, q in targets.items():
        z, v = out.descriptor(axis)
        if q > z:
            raise ValueError("coarsening target must not be finer than current zoom")
        out = out.replace_axis(axis, q, truncate(v, z, q))
    return out


def _merge_siblings_once(region: set[Cell], axis: int) -> bool:
    """Merge sibling pairs on one axis. Returns True if any merge occurred."""
    buckets: Dict[Tuple, Dict[int, Cell]] = {}
    for c in region:
        if not c.active(axis) or c.zooms[axis] <= 1:
            continue
        z, v = c.zooms[axis], c.values[axis]
        # Other axis descriptors must be identical; current axis is keyed by parent.
        other = tuple(
            (c.zooms[j], c.values[j]) if j != axis else (z - 1, v >> 1)
            for j in range(4)
        )
        key = (c.flags, axis, other)
        buckets.setdefault(key, {})[v & 1] = c

    for _, bits in buckets.items():
        if 0 in bits and 1 in bits:
            c0, c1 = bits[0], bits[1]
            # Defensive check: exact siblings.
            if c0.values[axis] >> 1 != c1.values[axis] >> 1:
                continue
            parent = c0.replace_axis(axis, c0.zooms[axis] - 1, c0.values[axis] >> 1)
            region.remove(c0); region.remove(c1); region.add(parent)
            return True
    return False


def normalize(cells: Iterable[Cell]) -> Tuple[Cell, ...]:
    """Deterministic normal form under x,y,f,t bottom-up sibling merging."""
    region = set(cells)
    if not region:
        return tuple()
    flags = next(iter(region)).flags
    if any(c.flags != flags for c in region):
        raise ValueError("all cells must share a presence vector")

    changed = True
    while changed:
        changed = False
        # N1: remove cells covered by another prefix.
        ordered = sorted(region, key=lambda c: (sum(c.zooms), c.zooms, c.values))
        keep: list[Cell] = []
        for c in ordered:
            if any(subsumes(k, c) for k in keep):
                changed = True
                continue
            keep.append(c)
        region = set(keep)

        # N2: deterministic axis order, one merge at a time, then restart N1.
        for axis in range(4):
            if _merge_siblings_once(region, axis):
                changed = True
                break

    return tuple(sorted(region))


def union(a: Iterable[Cell], b: Iterable[Cell]) -> Tuple[Cell, ...]:
    return normalize(tuple(a) + tuple(b))


def intersection(a: Iterable[Cell], b: Iterable[Cell]) -> Tuple[Cell, ...]:
    aa, bb = tuple(a), tuple(b)
    out = []
    for x in aa:
        for y in bb:
            m = meet(x, y)
            if m is not None:
                out.append(m)
    return normalize(out)


def _subtract_cell(a: Cell, b: Cell, working_zoom: Optional[Mapping[str, int]] = None) -> list[Cell]:
    _same_domain(a, b)
    if not compatible(a, b):
        return [a]
    if subsumes(b, a):
        return []

    # Partial overlap is possible only where a is coarser than b in at least one axis.
    candidates = []
    for i, axis in enumerate(AXES):
        if not a.active(i):
            continue
        if a.zooms[i] < b.zooms[i]:
            limit = 32 if working_zoom is None else working_zoom.get(axis, 32)
            if a.zooms[i] < limit:
                candidates.append(i)
    if not candidates:
        # At the declared working resolution the overlap cannot be further distinguished.
        # Conservative subtraction removes the unresolved overlapping cell.
        return []

    axis = candidates[0]  # deterministic x,y,f,t order
    out: list[Cell] = []
    for child in refine_axis(a, axis):
        if compatible(child, b):
            out.extend(_subtract_cell(child, b, working_zoom))
        else:
            out.append(child)
    return out


def difference(
    a: Iterable[Cell],
    b: Iterable[Cell],
    working_zoom: Optional[Mapping[str, int]] = None,
) -> Tuple[Cell, ...]:
    survivors = list(normalize(a))
    for sub in normalize(b):
        nxt: list[Cell] = []
        for cell in survivors:
            nxt.extend(_subtract_cell(cell, sub, working_zoom))
        survivors = list(normalize(nxt))
    return normalize(survivors)


def expand_to_working_grid(c: Cell, working_zoom: Mapping[str, int]) -> Tuple[Cell, ...]:
    """Dense oracle expansion; intentionally materializes all working-grid atoms."""
    out = [c]
    for i, axis in enumerate(AXES):
        if not c.active(i):
            continue
        target = working_zoom[axis]
        if target < c.zooms[i]:
            raise ValueError("working zoom must be no coarser than every input cell")
        for _ in range(target - c.zooms[i]):
            nxt = []
            for q in out:
                nxt.extend(refine_axis(q, axis))
            out = nxt
    return tuple(out)


def region_atoms(region: Iterable[Cell], working_zoom: Mapping[str, int]) -> frozenset[Cell]:
    atoms = set()
    for c in region:
        atoms.update(expand_to_working_grid(c, working_zoom))
    return frozenset(atoms)


def dense_difference_oracle(a: Iterable[Cell], b: Iterable[Cell], working_zoom: Mapping[str, int]) -> frozenset[Cell]:
    return region_atoms(a, working_zoom) - region_atoms(b, working_zoom)


def dense_intersection_oracle(a: Iterable[Cell], b: Iterable[Cell], working_zoom: Mapping[str, int]) -> frozenset[Cell]:
    return region_atoms(a, working_zoom) & region_atoms(b, working_zoom)


def semantic_equal(a: Iterable[Cell], b: Iterable[Cell], working_zoom: Mapping[str, int]) -> bool:
    return region_atoms(a, working_zoom) == region_atoms(b, working_zoom)


def contains(region: Iterable[Cell], query: Cell) -> bool:
    """Prefix membership: true when one region prefix subsumes query."""
    return any(subsumes(r, query) for r in region)
