from itertools import product

from bst_id.region_algebra import (
    Cell, compatible, subsumes, meet, refine_axis, normalize,
    intersection, difference, region_atoms, semantic_equal,
    dense_intersection_oracle, dense_difference_oracle, contains,
)


def c1(bits: str) -> Cell:
    return Cell.from_parts(x=(len(bits), int(bits, 2)))


def c2(x: str, y: str) -> Cell:
    return Cell.from_parts(x=(len(x), int(x, 2)), y=(len(y), int(y, 2)))


def test_subsumption_and_binary_difference_examples():
    assert subsumes(c1('10'), c1('10111'))
    out = difference([c1('10')], [c1('101')])
    assert set(out) == {c1('100')}

    out = difference([c1('10')], [c1('1011')])
    assert set(out) == {c1('100'), c1('1010')}

    out = difference([c1('10')], [c1('101111')])
    assert set(out) == {c1('100'), c1('1010'), c1('10110'), c1('101110')}


def test_anisotropic_cross_nested_meet():
    a = c2('101', '10')
    b = c2('10', '1011')
    assert compatible(a, b)
    assert not subsumes(a, b)
    assert not subsumes(b, a)
    assert meet(a, b) == c2('101', '1011')


def test_normalize_semantic_invariance_and_idempotence():
    original = [c1('100'), c1('1010'), c1('1011')]
    n = normalize(original)
    assert n == (c1('10'),)
    assert normalize(n) == n
    work = {'x': 5}
    assert semantic_equal(original, n, work)


def test_input_order_invariance():
    items = [c1('100'), c1('1010'), c1('1011')]
    from itertools import permutations
    expected = normalize(items)
    for p in permutations(items):
        assert normalize(p) == expected


def test_exhaustive_1d_boolean_against_dense_oracle():
    # All prefix cells of depths 1..3, compared at working zoom 4.
    cells = [c1(format(i, f'0{z}b')) for z in range(1,4) for i in range(1 << z)]
    wz = {'x': 4}
    for a in cells:
        for b in cells:
            inter = intersection([a], [b])
            assert region_atoms(inter, wz) == dense_intersection_oracle([a], [b], wz)
            diff = difference([a], [b], working_zoom=wz)
            assert region_atoms(diff, wz) == dense_difference_oracle([a], [b], wz)


def test_exhaustive_2d_cross_nested_against_dense_oracle():
    # Small exhaustive 2-D cells, depths 1..2 per axis, at working zoom 3x3.
    cells = []
    for zx in (1,2):
        for zy in (1,2):
            for ix in range(1 << zx):
                for iy in range(1 << zy):
                    cells.append(Cell.from_parts(x=(zx, ix), y=(zy, iy)))
    wz = {'x': 3, 'y': 3}
    for a in cells:
        for b in cells:
            inter = intersection([a], [b])
            assert region_atoms(inter, wz) == dense_intersection_oracle([a], [b], wz)
            diff = difference([a], [b], working_zoom=wz)
            assert region_atoms(diff, wz) == dense_difference_oracle([a], [b], wz)


def test_reserved_route_membership_example():
    reserved = c2('101', '0110')
    current = c2('10110', '011011')
    assert contains([reserved], current)
