from bst_id.encoder import BSTIDEncoder
from bst_id.decoder import BSTIDDecoder
from bst_id.logic import get_common_prefix_id, is_match, id_separate, iso8601_to_unix_time, unix_time_to_iso8601

# === 2つの異なる座標・時間を用意 ===
x1, y1, f1 = 139.75, 35.68, 15.0
x2, y2, f2 = 139, 35, 50.0
t_str1 = "2025-05-21T15:00:00Z"
t_str2 = "2025-05-21T15:05:00Z"
t1 = iso8601_to_unix_time(t_str1)
t2 = iso8601_to_unix_time(t_str2)

# Zoomレベルは固定（ここでは同一精度）
zoom_x = zoom_y = 15
zoom_f = 10
zoom_t = 20

# === エンコード（ID1, ID2） ===
id1, bit_len1 = BSTIDEncoder.encode(x1, y1, f1, t1, zoom_x, zoom_y, zoom_f, zoom_t)
id2, bit_len2 = BSTIDEncoder.encode(x2, y2, f2, t2, zoom_x, zoom_y, zoom_f, zoom_t)

# === デコードして確認 ===
decoded1 = BSTIDDecoder.decode(id1, bit_len1)
decoded2 = BSTIDDecoder.decode(id2, bit_len2)

# === Unionの計算（共通プレフィックス）===
union_id = get_common_prefix_id(id1, id2)

# === Intersectionの判定 ===
intersection = is_match(id1, id2)

# === 結果表示 ===
print("🧪 BST-ID 1")
print(f"  Binary: {bin(id1)}")
print(f"  Structure: {id_separate(id1)}")
print(f"  Decoded: x={decoded1[0]:.6f}, y={decoded1[1]:.6f}, f={decoded1[2]:.2f}, t={unix_time_to_iso8601(decoded1[3])}")

print("\n🧪 BST-ID 2")
print(f"  Binary: {bin(id2)}")
print(f"  Structure: {id_separate(id2)}")
print(f"  Decoded: x={decoded2[0]:.6f}, y={decoded2[1]:.6f}, f={decoded2[2]:.2f}, t={unix_time_to_iso8601(decoded2[3])}")

print("\n📌 共通プレフィックス（Union）")
print(f"  Binary: {union_id}")
print(f"  Structure: {id_separate(union_id)}")

print("\n📏 Intersection 判定")
print("  → Intersect" if intersection else "  → No intersection")




