import math

from bst_id.constants import X_RANGE, MAX_MERCATOR_LAT
from bst_id.encoder_tile_calculator import encode_x_tile_index, encode_y_tile_index


def test_longitude_plus_180_wraps_to_minus_180():
    z = 10
    assert encode_x_tile_index(180.0, *X_RANGE, z) == encode_x_tile_index(-180.0, *X_RANGE, z)
    assert encode_x_tile_index(-180.0, *X_RANGE, z) == 0


def test_longitude_wraps_past_the_antimeridian():
    z = 12
    assert encode_x_tile_index(190.0, *X_RANGE, z) == encode_x_tile_index(-170.0, *X_RANGE, z)
    assert encode_x_tile_index(-190.0, *X_RANGE, z) == encode_x_tile_index(170.0, *X_RANGE, z)


def test_longitude_tile_index_stays_in_range():
    z = 8
    n = 1 << z
    for lng in (-540.0, -180.0, -0.0, 179.999999, 180.0, 360.0, 539.9):
        idx = encode_x_tile_index(lng, *X_RANGE, z)
        assert 0 <= idx < n


def test_latitude_is_clamped_before_the_tile_formula():
    z = 10
    n = 1 << z
    # Values outside the Mercator range would blow up math.tan/log without the clamp.
    assert encode_y_tile_index(90.0, z) == encode_y_tile_index(MAX_MERCATOR_LAT, z)
    assert encode_y_tile_index(-90.0, z) == encode_y_tile_index(-MAX_MERCATOR_LAT, z)
    assert encode_y_tile_index(90.0, z) == 0
    assert encode_y_tile_index(-90.0, z) == n - 1


def test_latitude_tile_index_stays_in_range():
    z = 9
    n = 1 << z
    for lat in (-89.9, -85.0, -10.0, 0.0, 10.0, 85.0, 89.9):
        idx = encode_y_tile_index(lat, z)
        assert 0 <= idx < n
