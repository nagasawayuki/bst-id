# BST-ID neighbor/carry-borrow update

Added primitives:
- neighbor_axis(cell, axis, step, boundary=...)
- offset_cell(cell, offsets, boundary=...)
- neighbor_set(cell, offsets, boundary=...)
- prefix_dilate(region, offsets, ...)
- neighbor_membership(region, query, offsets, ...)

Key behavior:
- 011 + 1 -> 100
- 100 - 1 -> 011
- 01111011 + 1 -> 01111100
- 100010100 - 1 -> 100010011
- reject/wrap/clamp boundary policies
- independent multi-axis carry/borrow
- neighbor membership can cross coarse/fine region boundaries via prefix subsumption
- prefix_dilate is hierarchy-aligned same-scale expansion, NOT fixed-metric working-grid dilation

Validation:
- 12 pytest tests passed.
