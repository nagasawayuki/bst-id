# Prism handoff — BST-ID IJGI validation integration

Please update the current IJGI manuscript with these confirmed results.

## Confirmed result
The binary-prefix region algebra was checked over **38,732 cases/checks with 0 failures**.

Replace future-tense correctness language in Section 7.8 with an actual validation section.

### Suggested text
“We validated the binary-prefix region algebra against a dense working-grid oracle using exhaustive and randomized tests. In total, 38,732 checks were executed with no observed failures. Exhaustive one-dimensional tests covered every pair of hierarchical prefixes at depths 1–5 for intersection and difference. Exhaustive two-dimensional tests covered independently varying x/y zooms at depths 1–2 for union, anisotropic intersection, and difference. Additional randomized tests evaluated three- and four-dimensional Boolean operations against dense reference sets. Normalization was checked for semantic invariance, idempotence, deterministic output under reversed input order, and removal of residual subsumption. Refinement/coarsening properties, morphology/frontier reference semantics and closure, full-XYHT descriptor serialization round-trip, and reserved-route descendant membership were also verified.”

Call this bounded exhaustive + randomized verification, not a formal proof.

## Validation table
Create a compact table from `validation_summary.csv`:
Test group | Cases | Passed | Failed

Total: **38,732 passed, 0 failed**.

## Figures
- `fig1_full_vs_selective_4d.png`: recommended main complexity figure.
- `fig2_full_to_selective_ratio.png`: optional supporting complexity figure.
- `fig3_validation_coverage.png`: validation coverage; main text or supplement.

For Fig. 1/2, explicitly say the selective K curve is an illustrative single-localized-overlap-path count, not a universal Difference bound.

## Preserve qualifications
- Full working-grid materialization is the correctness oracle/reference semantics.
- General selective Difference complexity remains O(K).
- O(Δ) applies only to the 1D single-contained-path example.
- In fragmented regions K≈G and the structural advantage disappears.
- Boundary-oriented morphology/frontier bounds remain conditional targets unless an optimized implementation is separately verified.
- Do not claim continuous-space geometric correctness.

## Software statement
The validation was run against the current public BST-ID package structure plus a journal-specific binary-prefix `region_algebra.py` reference implementation. The exact validation snapshot should be archived with the submission.

## Implementation audit items
Keep an author-facing TODO for:
- `f` vs `h` axis naming,
- explicit bit length/framing for leading-zero presence vectors,
- altitude endpoint convention,
- longitude wrap / latitude clamp behavior,
- README terminology for common-prefix “Union” and overlap “Intersection”.
