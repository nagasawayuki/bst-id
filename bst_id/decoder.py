from typing import Optional, Tuple
from .constants import X_RANGE,H_RANGE, T_BITS
import math

class BSTIDDecoder:
    @staticmethod
    def decode(bit_id: int, bit_len: int) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[int]]:
        b = bit_id
        pos = bit_len
        
        def read(n: int) -> int:
            nonlocal b, pos
            pos -= n
            return(b >> pos) & ((1<<n) -1)
        
        flags = read(4)
        axes = ['x','y','f','t'] # h → f
        zooms = {}
        values = {}
        
        for i, axis in enumerate(axes):
            if (flags >> (3-i)) & 1:
                zooms[axis] = read(5) +1 
                
        for axis in zooms:
            z = zooms[axis]
            tile = read(z)
            n = 1 << z
            #x軸
            if axis == 'x':
                unit = (X_RANGE[1] - X_RANGE[0]) / n
                values['x'] = X_RANGE[0] + tile * unit
            #y軸
            elif axis =='y':
                unit = (math.pi * 2) / n
                lat_rad = math.atan(math.sinh(math.pi*(1- 2*tile / n)))
                values['y'] = math.degrees(lat_rad)
            #f軸
            elif axis =='f':
                scale = (1 << z) -1
                values['f'] = H_RANGE[0] + (tile / scale)*(H_RANGE[1] - H_RANGE[0])
            #t軸
            elif axis =='t':
                t_min = tile << (T_BITS - z)
                values['t'] = t_min
                
        return values.get("x"), values.get("y"), values.get("f"), values.get("t")
    