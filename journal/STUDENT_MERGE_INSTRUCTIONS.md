# BST-ID Journal Extension — Student Handoff / Merge Instructions

Repository:
https://github.com/nagasawayuki/bst-id

## Recommended workflow

1. Clone the current public repository and create a branch:

```bash
git clone https://github.com/nagasawayuki/bst-id.git
cd bst-id
git checkout -b journal-region-algebra
```

2. Unpack the supplied packages.

- `bst-id-validation-prism-package.zip`: journal region algebra, validation harness, tests, CSV/JSON, figures.
- `bst-id-neighbor-update.zip`: newer `region_algebra.py` / tests adding carry-borrow neighborhood primitives and hierarchy-aligned expansion.

If the same file exists in both packages, use the **neighbor-update version** as the newer version.

3. Merge journal extension files into the package:

```text
bst_id/region_algebra.py
tests/test_region_algebra.py
```

The extension contains canonical-region operations, Normalize, Union, anisotropic Intersection, selective Difference, refine/coarsen, dense correctness oracles, `neighbor_axis`, `offset_cell`, `neighbor_set`, `neighbor_membership`, and `prefix_dilate`.

`prefix_dilate()` is hierarchy-aligned expansion, not fixed-metric grid dilation.

4. Align the base library with the manuscript specification:

- Canonical external serialization is an **unsigned byte sequence**:
  `[4-bit XYHT presence][5-bit zoom fields for active axes][coordinate prefix bits][trailing zero padding to octet boundary]`.
- Stored zoom is `zoom - 1`: `00000 -> Level 1`, ..., `11111 -> Level 32`.
- A bare Python integer may remain an internal convenience representation, but is not the canonical serialization.
- Longitude is wrapped to `[-180, 180)`, including `+180 -> -180`.
- Latitude is clamped to the conventional valid Web Mercator latitude range before applying the tile formula.
- Use `h` as the public altitude axis; retain `f` only as a temporary documented legacy alias if needed.
- README should distinguish cell-level common-prefix / overlap primitives from region-level set-theoretic Union / Intersection.

5. Run tests:

```bash
python -m pytest -q
```

The focused neighborhood snapshot previously passed `12 passed`.
The broader validation harness previously executed `38,732` checks/cases with `0` failures.

After all base-library changes, rerun the entire validation from the final repository state.

6. Optional serialization tests: add XY, XYH, XYT, and XYHT round trips if convenient. The paper already reports 2000 full-XYHT round trips.

7. Prefer several small commits, e.g.:

```text
1. Add journal region algebra and correctness tests
2. Add carry-borrow neighbor primitives and prefix expansion
3. Add unsigned-byte BST-ID serialization
4. Align longitude/latitude encoder boundary handling
5. Rename altitude API f to h with legacy alias
6. Update README terminology and journal artifact instructions
```

8. Push branch:

```bash
git add .
git commit -m "Add BST-ID binary prefix region algebra"
git push -u origin journal-region-algebra
```

Then open a Pull Request or merge the branch to `main`.

## For Prof. Yaguchi

A local development environment is not required for review. The easiest workflow is:

1. Student pushes a branch and opens a GitHub Pull Request.
2. Review the PR in the browser under **Files changed**.
3. Confirm the test output posted in the PR.
4. Merge in the browser.
5. Record the final commit hash for the paper.

Before submission, insert that exact commit hash into the Software/Data Availability statement.
