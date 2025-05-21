# BST-ID

A binary, variable-length **spatiotemporal ID encoding scheme** designed for hierarchical and bandwidth-constrained systems.

This library provides encoding, decoding, intersection checking, and common prefix extraction functionalities for spatiotemporal data using compact binary IDs.

---

## 📦 Installation

You can install this library directly from GitHub:

```bash
pip install git+https://github.com/nagasawayuki/bst-id.git
```

---

## 🚀 Features

### 1. `BSTIDEncoder.encode()`

Encodes spatial-temporal coordinates into a binary BST-ID.

### 2. `BSTIDDecoder.decode()`

Decodes a BST-ID back into (x, y, f, t) values.

### 3. `get_common_prefix_id()`

Returns the coarsest shared voxel between two BST-IDs (Union).

### 4. `is_match()`

Returns `True` if two BST-IDs intersect at any shared resolution (Intersection).

### 5. `id_separate()`

Returns a human-readable string representation of a BST-ID, broken into flags/headers/values.

### 6. `iso8601_to_unix_time()` / `unix_time_to_iso8601()`

Utility functions for time encoding/decoding.

---

## 📚 Usage Examples

### Example 1: Encoding and Decoding

```python
from bst_id.encoder import BSTIDEncoder
from bst_id.decoder import BSTIDDecoder
from bst_id.logic import iso8601_to_unix_time, unix_time_to_iso8601

x, y, f = 139.75, 35.68, 10.0
t = iso8601_to_unix_time("2025-05-21T15:00:00Z")
bst_id, bit_len = BSTIDEncoder.encode(x, y, f, t, 10, 10, 5, 20)

print("BST-ID:", bin(bst_id))

decoded = BSTIDDecoder.decode(bst_id, bit_len)
print("Decoded:", decoded)
```

**Output:**

```
BST-ID: 0b111101001010010010010011111000110101100100111000001101000001011011110
Decoded: (139.5703125, 35.746512259918504, 529.0, 1747836928)
```
### Example 2: ID Structure Visualization

```python
from bst_id.logic import id_separate
id1 = 0b111101001010010010010011111000110101100100111000001101000001011011110
print("Readable ID:", id_separate(id1))
```

**Output:**

```
Readable ID: 1/1/1/1/01001/01001/00100/10011/1110001101/0110010011/10000/01101000001011011110
```

### Example 3: Union (Common Prefix)

```python
from bst_id.encoder import BSTIDEncoder
from bst_id.logic import get_common_prefix_id, id_separate, iso8601_to_unix_time

x1, y1, f1 = 139.75, 35.68, 10.0
t1 = iso8601_to_unix_time("2025-05-21T15:00:00Z")
x2, y2, f2 = 139.7505, 35.6805, 12.0
t2 = iso8601_to_unix_time("2025-05-21T15:01:00Z")

id1, _ = BSTIDEncoder.encode(x1, y1, f1, t1, 12, 12, 6, 18)
id2, _ = BSTIDEncoder.encode(x2, y2, f2, t2, 12, 12, 6, 18)

id_union = get_common_prefix_id(id1, id2)
print("id1: ",bin(id1))
print("id2: ",bin(id2))
print("Union ID:", (id_union))
```

**Output:**

```
id1:  0b111101011010110010110001111000110110011001001100100000011010000010110111
id2:  0b111101011010110010110001111000110110011001001100100000011010000010110111
Union ID: 0b111101011010110010110001111000110110011001001100100000011010000010110111
```

### Example 4: Intersection Check

```python
from bst_id.encoder import BSTIDEncoder
from bst_id.logic import is_match, iso8601_to_unix_time

x1, y1, f1 = 139.75, 35.68, 10.0
t1 = iso8601_to_unix_time("2025-05-21T15:00:00Z")
x2, y2, f2 = 139.76, 35.69, 30.0
t2 = iso8601_to_unix_time("2025-05-21T16:00:00Z")

id1, _ = BSTIDEncoder.encode(x1, y1, f1, t1, 12, 12, 6, 18)
id2, _ = BSTIDEncoder.encode(x2, y2, f2, t2, 12, 12, 6, 18)

print("Intersect:", is_match(id1, id2))
```

**Output:**

```
Intersect: True
```


---







