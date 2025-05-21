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

### Example 2: Union (Common Prefix)

```python
from bst_id.logic import get_common_prefix_id, id_separate

id_union = get_common_prefix_id(id1, id2)
print("Union ID:", id_separate(id_union))
```

### Example 3: Intersection Check

```python
from bst_id.logic import is_match

if is_match(id1, id2):
    print("IDs intersect")
else:
    print("IDs do not intersect")
```

### Example 4: ID Structure Visualization

```python
from bst_id.logic import id_separate

print("Readable ID:", id_separate(bst_id))
```

---





