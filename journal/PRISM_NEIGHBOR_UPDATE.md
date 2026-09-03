Please incorporate the attached neighbor/carry-borrow implementation into the current IJGI manuscript.

The updated reference code adds same-resolution binary neighbor primitives using integer increment/decrement on BST-ID payload indices. Integer arithmetic implicitly performs the carry/borrow required to cross binary subtree boundaries, e.g. 011* + 1 -> 100* and 100* - 1 -> 011*. The implementation supports reject, wrap, and clamp boundary policies and independent offsets on multiple axes.

Add this as a low-level binary primitive in Section 3.7 / Table 1. State that same-resolution adjacency does not require explicit parent-up/sibling/down tree traversal; a fixed-width integer offset crosses subtree boundaries through ordinary carry/borrow.

Important distinction:
1. `neighbor_axis` / `offset_cell` generate same-zoom candidate neighbors.
2. Multi-resolution region occupancy is then evaluated separately through prefix subsumption (`contains`), so a finer query neighbor can be covered by a coarser region prefix.
3. `prefix_dilate` is a hierarchy-aligned, same-scale expansion derived from neighbor generation plus Normalize. It is NOT equivalent to a fixed physical-distance or working-grid morphological dilation. Present it as an inexpensive hierarchical outer expansion / secondary operator, not as a replacement for metric morphology.

Please add a short example:
011* + 1 = 100*
and explain that this crosses a binary subtree boundary without explicit tree traversal.

Update morphology discussion to distinguish:
- metric/grid morphology at z_work, which retains dense/reference semantics;
- hierarchy-aligned prefix expansion, composed from neighbor offsets + containment + Normalize.

Do not claim that the new code proves the general O(B|S|+K) boundary-aware morphology bound. It demonstrates the required carry/borrow neighbor primitive and a secondary hierarchy-aligned expansion operator.

The updated pytest suite reports 12 passed tests, including carry, borrow, boundary policies, multi-axis offsets, coarse/fine neighbor membership, and hierarchy-aligned prefix dilation closure.
