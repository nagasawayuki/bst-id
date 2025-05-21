from typing import Optional, Tuple
from .constants import X_RANGE, H_RANGE
from .encoder_tile_calculator import encode_x_tile_index, encode_y_tile_index, encode_f_tile_index, encode_t_index

class BSTIDEncoder:
    @staticmethod
    def encode(
        x: Optional[float],
        y: Optional[float],
        f: Optional[float],
        t_unix: Optional[int],
        zoom_x: int = 0,
        zoom_y: int = 0,
        zoom_f: int = 0,
        zoom_t: int = 0
    ) -> Tuple[int,int]:
        """
        BST-IDをエンコードして、(bit列ID, 総ビット長) を返す
        """
        presence_flags = (
            (1 if x is not None else 0) << 3 |
            (1 if y is not None else 0) << 2 |
            (1 if f is not None else 0) << 1 |
            (1 if t_unix is not None else 0)
        )
        
        zooms = []
        payloads = []
        
        if x is not None:
            zooms.append(zoom_x -1)
            payloads.append(encode_x_tile_index(x, *X_RANGE, zoom_x))
        
        if y is not None:
            zooms.append(zoom_y - 1)
            payloads.append(encode_y_tile_index(y, zoom_y))

        if f is not None:
            zooms.append(zoom_f - 1)
            payloads.append(encode_f_tile_index(f, *H_RANGE, zoom_f))

        if t_unix is not None:
            zooms.append(zoom_t - 1)
            payloads.append(encode_t_index(t_unix, zoom_t))
            
        id_bits = presence_flags
        total_bits = 4
        
        for zoom_m1 in zooms:
            id_bits = (id_bits << 5) | zoom_m1
            total_bits += 5
            
        for zoom_m1, val in zip(zooms,payloads):
            zoom = zoom_m1 + 1
            id_bits = (id_bits << zoom) |val
            total_bits += zoom
            
        return id_bits, total_bits