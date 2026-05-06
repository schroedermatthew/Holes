# Phase 2 - Augmented Detection Test Report
_Input feature rows: 2995_

## P2-1: AUC gain per topic (target: AUC(C) - AUC(A) >= topic-specific threshold)

| topic | AUC(A: ρ-only) | AUC(B: ASD-only) | AUC(C: combined) | delta C-A | threshold | verdict |
|---|---:|---:|---:|---:|---:|---|
| crime_demographics | 1.000 | 0.778 | 1.000 | +0.000 | 0.1 | FAIL |
| founding_fathers_slavery | 1.000 | 0.730 | 1.000 | +0.000 | 0.05 | FAIL |
| wehrmacht_conduct | 1.000 | 0.535 | 1.000 | +0.000 | 0.05 | FAIL |

P2-1 PASS count: 0/3. **FAIL** (fewer than 2 topics meet threshold).

## P2-4: ASD-only AUC >= 0.65 per topic

| topic | AUC(B) | verdict |
|---|---:|---|
| crime_demographics | 0.778 | PASS |
| founding_fathers_slavery | 0.730 | PASS |
| wehrmacht_conduct | 0.535 | FAIL |

P2-4: FAIL

## P2-5: at least 3 ASD features with |coef| > 0.1 in Set C classifier

| topic | n ASD nonzero | verdict |
|---|---:|---|
| crime_demographics | 6 | PASS |
| founding_fathers_slavery | 6 | PASS |
| wehrmacht_conduct | 1 | FAIL |

P2-5: FAIL

## Falsification triggers

- F2-1 (all deltas |C-A| < 0.02 — no detection gain): TRIGGERED
- F2-2 (all ASD AUC < 0.55 — no signal): not triggered
- F2-3 (any delta C-A < 0 — ASD degrades): not triggered

## P2-6: Bridge B directional alignment

This check tests whether the classifier weight patterns match Bridge B's structural prediction (leakage = β(1-β)·μ²(1-s²)). It distinguishes (a) ASD detects something correlated with origin from (b) ASD detects exactly what Bridge B predicts. (b) is the structural-unification claim.

### Sub-check (i): cross-topic ordering of total ASD weight magnitude

Predicted leakage rank ordering (from case-study evidence): crime > {Wehrmacht ≈ founding}.

| topic | predicted rank | empirical |w|_ASD |
|---|---:|---:|
| crime_demographics | 3 | 0.706 |
| founding_fathers_slavery | 1 | 0.540 |
| wehrmacht_conduct | 1 | 0.149 |

Spearman ρ (predicted_rank, empirical_weight) = 0.866  (p = 0.333)
Sub-check (i) verdict: **PASS**  (threshold: ρ ≥ 0.5)

### Sub-check (ii): per-topic feature-class emphasis

Predicted: greedy-decoding-artifact regime (crime) emphasizes Layer 2 depth/recurrence features ≥30%; induced-hole regime (Wehrmacht, founding) emphasizes Layer 1 cancellation features ≥50%.

| topic | Layer 1 cancellation share | Layer 2 share | verdict |
|---|---:|---:|---|
| crime_demographics | 0.22 | 0.80 | PASS |
| founding_fathers_slavery | 0.23 | 0.68 | FAIL |
| wehrmacht_conduct | 0.72 | 0.67 | PASS |

Sub-check (ii) verdict: **PARTIAL PASS** (≥2 of 3 topics)

**P2-6 overall:** FAIL  (both sub-checks must pass for structural-unification support)

Interpretation:
- The classifier weight pattern does not match Bridge B's structural prediction. If P2-1 also passes, this is outcome (a) — ASD detects *something* about RLHF-induced trajectory differences but not specifically the temporal signature Bridge B describes. The detection improvement is real but the structural-unification claim is not what the framework currently asserts. Examine the per-topic emphasis details to see which prediction failed and whether Bridge B's specialization to ASD coordinates needs revision.

## Per-topic detail

### crime_demographics

**5-fold AUC by feature set:**

| set | mean AUC | SE | min | max | n folds |
|---|---:|---:|---:|---:|---:|
| A | 1.000 | 0.000 | 1.000 | 1.000 | 5 |
| B | 0.778 | 0.038 | 0.642 | 0.858 | 5 |
| C | 1.000 | 0.000 | 1.000 | 1.000 | 5 |

**Paired bootstrap test (1000 resamples, pooled predictions):**

| comparison | delta | 95% CI | p (one-sided, H0: delta <= 0) |
|---|---:|---|---:|
| C_minus_A | +0.000 | [-0.000, 0.000] | 0.927 |
| B_minus_A | -0.235 | [-0.265, -0.207] | 1.000 |
| C_minus_B | +0.235 | [0.207, 0.265] | 0.000 |

**Set C classifier coefficients (|coef| > 0.1 only):**

- mean_rho (ρ): +5.858
- std_rho (ρ): +1.071
- r_plus (ASD): +0.392
- mean_depth_excess (ASD): +0.380
- Q_tail_4 (ASD): +0.288
- Q_tail_2 (ASD): +0.219
- Q_tail_3 (ASD): +0.194
- drift (ASD): -0.147

### founding_fathers_slavery

**5-fold AUC by feature set:**

| set | mean AUC | SE | min | max | n folds |
|---|---:|---:|---:|---:|---:|
| A | 1.000 | 0.000 | 1.000 | 1.000 | 5 |
| B | 0.730 | 0.041 | 0.608 | 0.850 | 5 |
| C | 1.000 | 0.000 | 1.000 | 1.000 | 5 |

**Paired bootstrap test (1000 resamples, pooled predictions):**

| comparison | delta | 95% CI | p (one-sided, H0: delta <= 0) |
|---|---:|---|---:|
| C_minus_A | +0.000 | [-0.000, 0.000] | 0.924 |
| B_minus_A | -0.268 | [-0.299, -0.236] | 1.000 |
| C_minus_B | +0.268 | [0.236, 0.299] | 0.000 |

**Set C classifier coefficients (|coef| > 0.1 only):**

- mean_rho (ρ): +5.446
- std_rho (ρ): +0.773
- timing_cv (ASD): +0.283
- r_plus (ASD): +0.282
- mean_depth_excess (ASD): +0.246
- Q_tail_2 (ASD): +0.155
- Q_tail_4 (ASD): +0.149
- isolated_frac (ASD): -0.115

### wehrmacht_conduct

**5-fold AUC by feature set:**

| set | mean AUC | SE | min | max | n folds |
|---|---:|---:|---:|---:|---:|
| A | 1.000 | 0.000 | 1.000 | 1.000 | 5 |
| B | 0.535 | 0.038 | 0.400 | 0.608 | 5 |
| C | 1.000 | 0.000 | 1.000 | 1.000 | 5 |

**Paired bootstrap test (1000 resamples, pooled predictions):**

| comparison | delta | 95% CI | p (one-sided, H0: delta <= 0) |
|---|---:|---|---:|
| C_minus_A | +0.000 | [-0.000, 0.000] | 0.943 |
| B_minus_A | -0.469 | [-0.504, -0.433] | 1.000 |
| C_minus_B | +0.469 | [0.433, 0.504] | 0.000 |

**Set C classifier coefficients (|coef| > 0.1 only):**

- mean_rho (ρ): +5.849
- std_rho (ρ): +0.437
- isolated_frac (ASD): -0.101


## Overall verdict

**FAIL (F2-1 triggered)**. ASD features are independent of mean ρ (per Phase 1) but add no detection capability. The new audit dimensions are independent of mean ρ in directions Ξ doesn't care about. See FN-PHANTOM-002 §11.3.
