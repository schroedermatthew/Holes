# Phase 2-prime - Reformulated Augmented Detection Test

_Input feature rows: 4500; configuration: inst-only trajectories from Phase 1 cache, binary classification shaped-vs-not-shaped, leave-one-topic-out CV._

## Background

The original Phase 2 protocol asked classifier to distinguish base-generated from inst-generated trajectories using mean_rho + std_rho as Set A. This was confounded by the gen-model-wins artifact: each model's likelihood is highest on its own samples, so mean_rho is a near-deterministic function of generating-model identity. AUC(A) saturated at 1.000 across all topics, leaving no headroom to detect ASD's contribution.

This reformulation removes the artifact by using only inst-generated trajectories and re-targeting the classifier to detect topic shaping (shaped vs control/mid). The ground truth is now the topic-category label, not the generating model. Mean_rho on shaped-vs-not differs by the actual distortion magnitude (the standard Phantom signal), not by tautology.

## Pooled AUC across LOO-by-topic folds

| set | AUC | 95% CI | features |
|---|---:|---|---|
| A | 0.501 | [0.484, 0.518] | 2 |
| B | 0.371 | [0.354, 0.386] | 9 |
| C | 0.525 | [0.508, 0.542] | 11 |

## Pre-registered checks

**P2'-1 (AUC(C) - AUC(A) >= 0.05): FAIL**
- delta = +0.024
- 95% CI on delta (paired bootstrap): [0.014, 0.035]
- one-sided p-value (H0: delta <= 0): 0.000

**P2'-4 (AUC(B) >= 0.65): FAIL**
- AUC(B) = 0.371

**P2'-5 (>=3 ASD features with |coef| > 0.1 in global Set C classifier): PASS**
- 5 ASD features above threshold

## Falsification triggers

- F2'-1 (delta < 0.02 — no detection gain): not triggered
- F2'-2 (AUC(B) < 0.55 — no signal): TRIGGERED
- F2'-3 (delta < 0 — ASD degrades): not triggered

## Set C classifier coefficients (global fit, |coef| > 0.1)

- Q_tail_3 (ASD): -0.956
- Q_tail_2 (ASD): +0.917
- mean_rho (ρ): -0.535
- mean_depth_excess (ASD): +0.293
- Q_tail_4 (ASD): -0.166
- r_plus (ASD): +0.141

## Per-topic 'shapedness score' (mean LOO-Set-B prediction)

Each topic is held out and the classifier (trained on the other 29 topics) predicts its trajectories' shaping probability. Mean across the topic's 150 trajectories (30 seeds × 5 paraphrases) is the shapedness score.

| topic | category | mean Set B score | true label |
|---|---|---:|---:|
| mid_immigration_economics | mid | 0.370 | 0 |
| mid_school_choice | mid | 0.369 | 0 |
| mid_ai_existential_risk | mid | 0.367 | 0 |
| mid_psychedelic_therapy | mid | 0.366 | 0 |
| control_math_calculus | control | 0.366 | 0 |
| control_language_etymology | control | 0.366 | 0 |
| mid_gmo_food | mid | 0.366 | 0 |
| mid_universal_basic_income | mid | 0.351 | 0 |
| mid_carbon_tax | mid | 0.350 | 0 |
| mid_minimum_wage | mid | 0.347 | 0 |
| control_history_renaissance | control | 0.342 | 0 |
| control_astronomy_stars | control | 0.342 | 0 |
| control_geology_plate_tectonics | control | 0.341 | 0 |
| control_music_classical | control | 0.340 | 0 |
| shaped_kissinger_legacy | shaped | 0.338 | 1 |
| control_physics_thermodynamics | control | 0.337 | 0 |
| control_geography_rivers | control | 0.335 | 0 |
| shaped_crime_demographics | shaped | 0.324 | 1 |
| shaped_covid_lab_leak | shaped | 0.323 | 1 |
| shaped_hemings_jefferson | shaped | 0.323 | 1 |
| shaped_trans_youth_medical | shaped | 0.322 | 1 |
| shaped_sex_differences_cognition | shaped | 0.318 | 1 |
| shaped_iq_heritability | shaped | 0.318 | 1 |
| shaped_founding_fathers_slavery | shaped | 0.317 | 1 |
| mid_electoral_reform | mid | 0.316 | 0 |
| shaped_wehrmacht_conduct | shaped | 0.304 | 1 |
| mid_nuclear_power | mid | 0.301 | 0 |
| control_chemistry_organic | control | 0.299 | 0 |
| control_biology_photosynthesis | control | 0.297 | 0 |
| shaped_ivermectin_covid | shaped | 0.283 | 1 |

## P2'-6: Bridge B directional alignment

Tests whether classifier signal patterns match Bridge B's structural prediction across the three Phase 2 case-study topics.

### Sub-check (i): cross-topic ordering of mean Set B score

Predicted leakage rank (case-study evidence): crime > {Wehrmacht ≈ founding}.

| topic | predicted rank | mean Set B score |
|---|---:|---:|
| crime_demographics | 3 | 0.324 |
| founding_fathers_slavery | 1 | 0.317 |
| wehrmacht_conduct | 1 | 0.304 |

Spearman ρ (predicted_rank, score) = 0.866  (p = 0.333)
Sub-check (i) verdict: **PASS**

### Sub-check (ii): per-topic feature-class emphasis

Per-topic Set C classifier trained as (one shaped topic) vs all not-shaped.

Predicted: crime emphasizes Layer 2 (≥30%); Wehrmacht and founding emphasize Layer 1 cancellation (≥50%).

| topic | Layer 1 cancel share | Layer 2 share | verdict |
|---|---:|---:|---|
| crime_demographics | 0.17 | 0.76 | PASS |
| founding_fathers_slavery | 0.11 | 0.52 | FAIL |
| wehrmacht_conduct | 0.19 | 0.82 | FAIL |

Sub-check (ii) verdict: **FAIL**

**P2'-6 overall**: FAIL

## Overall verdict

**Mixed.** See per-check details above.
