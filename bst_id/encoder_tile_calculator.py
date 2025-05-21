from typing import Optional
import math
from .constants import X_RANGE, Y_RANGE, H_RANGE, T_BITS


#符号化(空間ID）

# x軸(経度)
def encode_x_tile_index(lng: float, min_val: float, max_val: float, zoom: int) -> int:
    n = 1 << zoom
    normalized = (lng - min_val) / (max_val - min_val)
    return int(normalized * n)
# y軸(緯度)
def encode_y_tile_index(lat: float, zoom: int) -> int:
    n = 1 << zoom
    lat_rad = math.radians(lat)
    ytile = int((1.0 - math.log(math.tan(lat_rad)+ 1/math.cos(lat_rad))/math.pi)/2.0 * n)
    return ytile
#f軸(標高)
def encode_f_tile_index(h: float, min_val: float, max_val: float, zoom: int, max_zoom: int = 32) -> int:
    scale = (1 << max_zoom) - 1
    normalized = (h - min_val) / (max_val - min_val)
    full_f_value = int(normalized * scale)
    return full_f_value >> (max_zoom - zoom)

def encode_t_index(t: int, zoom: int) -> int:
    return t >> (T_BITS - zoom)