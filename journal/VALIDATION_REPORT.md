# BST-ID Region Algebra Validation Report

## Overall result
- Total validated checks/cases: **38,732**
- Passed: **38,732**
- Failed: **0**
- Overall pass rate: **100.000%**

## Validation groups

| test                                                 |   cases |   passed |   failed |   seconds |
|:-----------------------------------------------------|--------:|---------:|---------:|----------:|
| 1D exhaustive Boolean (depth 1-5)                    |    7688 |     7688 |        0 |    0.2284 |
| 2D exhaustive Boolean (depth 1-2)                    |    3888 |     3888 |        0 |    0.1751 |
| 3D randomized Boolean                                |    4500 |     4500 |        0 |    0.3638 |
| 4D randomized Boolean                                |    3000 |     3000 |        0 |    0.5494 |
| 1D normalization properties                          |    4000 |     4000 |        0 |    0.079  |
| 2D normalization properties                          |    3200 |     3200 |        0 |    0.1337 |
| 3D normalization properties                          |    1600 |     1600 |        0 |    0.1138 |
| 4D normalization properties                          |     800 |      800 |        0 |    0.105  |
| 1D refine/coarsen properties                         |    2000 |     2000 |        0 |    0.0115 |
| 2D refine/coarsen properties                         |    1600 |     1600 |        0 |    0.0182 |
| 3D refine/coarsen properties                         |     800 |      800 |        0 |    0.0117 |
| 4D refine/coarsen properties                         |     400 |      400 |        0 |    0.0056 |
| 1D morphology/frontier reference semantics + closure |    1800 |     1800 |        0 |    0.4578 |
| 2D morphology/frontier reference semantics + closure |    1200 |     1200 |        0 |    4.6835 |
| XYHT Cell descriptor -> BST-ID int -> descriptor     |    2000 |     2000 |        0 |    0.0211 |
| XYHT reserved-route descendant membership            |     256 |      256 |        0 |    0.0008 |

## Scope verified
- Exhaustive 1D Boolean correctness for all prefix-cell pairs at depths 1–5.
- Exhaustive 2D Boolean correctness for independently zoomed x/y cells at depths 1–2.
- Randomized 3D and 4D union/intersection/difference against dense working-grid oracles.
- Normalize: semantic invariance, idempotence, deterministic reversed-input output, no residual subsumption.
- Refinement semantic invariance and coarsening containment.
- 1D and 2D morphology/frontier reference semantics followed by canonical normalization/closure.
- Full-XYHT Cell descriptor -> BST-ID integer -> descriptor round-trip.
- Exhaustive descendant membership for the XYHT reserved-route/conformance example.

## Complexity illustration
For equal added depth Δ across D active dimensions:
- Full working-grid materialization: **G = 2^(DΔ)**.
- For the manuscript's single localized overlap-path illustration, each split generates two children and only one branch continues, giving an illustrative **K ≈ 2DΔ** generated-prefix count.

The K expression is an illustrative localized-path count, not a universal Difference bound. The general result remains O(K). In maximally fragmented regions, K can approach G.

## Morphology qualification
The current test package verifies dense working-grid morphology/frontier semantics and closure after normalization. It does **not** prove the conditional boundary-oriented O(B|S|+K) implementation target. Keep that bound explicitly conditional unless a separate optimized boundary-aware implementation is supplied and verified.

## Known implementation consistency issues
1. Public code uses axis name `f`; manuscript uses altitude `h`.
2. Integer-only parsing may lose leading zero presence bits; variable-presence-vector serialization should retain explicit bit length/framing.
3. Current altitude constant is `(-16383.0, 16384.0)`.
4. Explicit longitude wrap / latitude clamp claims should be checked against the actual encoder.
5. README terms “Union” (common-prefix extraction) and “Intersection” (overlap predicate) should be distinguished from set-theoretic union and anisotropic meet/intersection in the journal.
