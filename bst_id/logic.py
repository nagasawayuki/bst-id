from datetime import datetime, timezone
from typing import Tuple, Dict

# ======== BST-ID 基本処理 ========
def read_bits(b: int, pos: int, n: int) -> Tuple[int, int]:
    pos -= n
    val = (b >> pos) & ((1 << n) - 1)
    return val, pos

def parse_bst_id(bst_id: int) -> Tuple[int, Dict[str, int], Dict[str, int]]:
    pos = bst_id.bit_length()
    flags, pos = read_bits(bst_id, pos, 4)
    axes = ['x', 'y', 'f', 't']
    zooms, values = {}, {}
    for i, axis in enumerate(axes):
        if (flags >> (3 - i)) & 1:
            zoom_m1, pos = read_bits(bst_id, pos, 5)
            zooms[axis] = zoom_m1 + 1
    for axis in zooms:
        z = zooms[axis]
        val, pos = read_bits(bst_id, pos, z)
        values[axis] = val
    return flags, zooms, values

def build_bst_id(flags: int, zooms: Dict[str, int], values: Dict[str, int]) -> int:
    axes = ['x', 'y', 'f', 't']
    result = flags
    for axis in axes:
        if (flags >> (3 - axes.index(axis))) & 1:
            result = (result << 5) | (zooms[axis] - 1)
    for axis in axes:
        if (flags >> (3 - axes.index(axis))) & 1:
            z = zooms[axis]
            result = (result << z) | values[axis]
    return result

# ======== 共通プレフィックス（Union） ========
def get_common_prefix_id(id1: int, id2: int) -> int:
    f1, z1s, v1s = parse_bst_id(id1)
    f2, z2s, v2s = parse_bst_id(id2)

    axes = ['x', 'y', 'f', 't']
    flags = {}
    headers = {}
    values = {}

    for i, axis in enumerate(axes):
        flag = 0
        header = 0
        value = 0
        if (f1 >> (3 - i)) & 1 and (f2 >> (3 - i)) & 1:
            z1, z2 = z1s[axis], z2s[axis]
            v1, v2 = v1s[axis], v2s[axis]
            z = min(z1, z2)
            for j in range(z):
                if ((v1 >> (z1 - j - 1)) & 1) != ((v2 >> (z2 - j - 1)) & 1):
                    break
                value = (value << 1) | ((v1 >> (z1 - j - 1)) & 1)
                header = j
                flag = 1
        flags[axis] = flag
        headers[axis] = header
        values[axis] = value

    flags_int = (flags['x'] << 3) | (flags['y'] << 2) | (flags['f'] << 1) | flags['t']

    zooms = {}
    vals = {}
    for axis in axes:
        if flags[axis]:
            zooms[axis] = headers[axis] + 1
            vals[axis] = values[axis]

    return build_bst_id(flags_int, zooms, vals)



# ======== 交差判定（Intersection） ========
def is_match(id1: int, id2: int) -> bool:
    f1, z1s, v1s = parse_bst_id(id1)
    f2, z2s, v2s = parse_bst_id(id2)
    axes = ['x', 'y', 'f', 't']
    for i, axis in enumerate(axes):
        active1 = (f1 >> (3 - i)) & 1
        active2 = (f2 >> (3 - i)) & 1
        if active1 and active2:
            z1, z2 = z1s[axis], z2s[axis]
            v1, v2 = v1s[axis], v2s[axis]
            z = min(z1, z2)
            if (v1 >> (z1 - z)) != (v2 >> (z2 - z)):
                return False
    return True

# ======== 時刻ユーティリティ関数 ========
def iso8601_to_unix_time(iso8601_str: str) -> int:
    dt = datetime.strptime(iso8601_str, "%Y-%m-%dT%H:%M:%SZ")
    dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())

def unix_time_to_iso8601(unix_time: int) -> str:
    dt = datetime.fromtimestamp(unix_time, tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

# ======== IDの可読性を上げるため、要素ごとにスラッシュ挿入 ========
def id_separate(bst_id: int) -> str:
    if isinstance(bst_id, str):
        bst_id = int(bst_id, 2)  # 2進数文字列ならintに変換
    pos = bst_id.bit_length()
    segments = []

    # 読み出し用関数
    def read_bits(b: int, pos: int, n: int) -> Tuple[int, int, str]:
        pos -= n
        val = (b >> pos) & ((1 << n) - 1)
        bitstr = format(val, f'0{n}b')
        return val, pos, bitstr

    # 1. flags（4bit）
    flags_val, pos, flags_bits = read_bits(bst_id, pos, 4)
    segments.extend(list(flags_bits))  # flag_x, flag_y, flag_f, flag_t

    axes = ['x', 'y', 'f', 't']
    headers = {}
    header_bits = {}
    values = {}
    value_bits = {}

    # 2. headers（各5bit、flag==1の軸のみ）
    for i, axis in enumerate(axes):
        if (flags_val >> (3 - i)) & 1:
            h_val, pos, h_bits = read_bits(bst_id, pos, 5)
            headers[axis] = h_val
            header_bits[axis] = h_bits
            segments.append(h_bits)

    # 3. 各軸の値（header+1 bit）
    for axis in axes:
        if axis in headers:
            length = headers[axis] + 1
            v_val, pos, v_bits = read_bits(bst_id, pos, length)
            values[axis] = v_val
            value_bits[axis] = v_bits
            segments.append(v_bits)

    return '/'.join(segments)




