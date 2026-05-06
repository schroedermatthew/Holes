---
doc_id: MN-PHANTOM-001
doc_type: "Method Note"
title: "The Mechanism of Augmented Detection — How Phase 2's Classifier Comparison Tests the Rank of F_ASD on Ξ"
phantom_components: ["audit-blind-subspace", "rho-field", "constraint-subspace-Xi", "F_ab abelian audit class", "audit projection Pi_N"]
asd_components: ["F_ASD non-abelian audit class", "Layer 1 + Layer 2 features", "block-local ordinal quartile encoding"]
topics: ["base-vs-Instruct classifier task", "three feature sets and their geometric interpretation", "AUC comparison as rank measurement", "leave-one-paraphrase-out cross-validation", "standardized classifier coefficients as feature-importance evidence", "topic-specific thresholds as framework predictions", "limits of what Phase 2 can establish"]
constraints: ["assumes Phase 1 (O-LM) has passed — the orthogonality of F_ASD to F_ab", "assumes the case-study topics actually engage RLHF distortion (per CS-PHANTOM-001, CS-PHANTOM-002)", "single-substrate (Llama-3.1-8B) — generalization deferred to Phase 5", "logistic regression is a linear classifier — nonlinear separability not tested by Set C AUC alone", "Choice C signal only"]
mathematical_standard: "supervised binary classification, logistic regression with standardized features, leave-one-group-out cross-validation, bootstrap CIs and paired bootstrap for AUC differences, pre-registered topic-specific predictions"
build_modes: ["dual-origin generation (3-pass loading): both models generate trajectories, both score every trajectory", "trajectory caching for re-evaluation with alternative encoders", "5-fold CV stratified by paraphrase identity, not random folds"]
last_verified: 2026-05-05
audience: ["framework practitioners running Phase 2", "reviewers asking what the test actually measures", "researchers extending the methodology"]
status: "complete — methodology document for FN-PHANTOM-002 §8.2"

related_documents:
  - "Foundations - The Phantom Framework Mathematical Apparatus.md (FN-PHANTOM-001) — defines audit space F, constraint subspace Ξ, audit-blind theorems"
  - "Foundations - ASD-Augmented Distortion Detection.md (FN-PHANTOM-002) — specifies Phase 2 protocol that this document explains the mechanism of"
  - "Empirical Validation of (O-LM) (EN-PHANTOM-001) — Phase 1 result; Phase 2's prerequisite"
  - "Handbook - Probability-Distortion Measurement Discipline.md (HB-PHANTOM-001)"
  - "Case Study - Induced-Hole Amplification.md (CS-PHANTOM-001) — provides the founding fathers and Wehrmacht topics"
  - "Case Study - The Greedy-Decoding Artifact.md (CS-PHANTOM-002) — provides the crime demographics topic and the larger expected gain"

phantom_apparatus_used:
  established_results:
    - "audit-blind theorem B: dim(ker Π_N) >= dim(Ξ) - N over any choice of N audit functions [E linearized regime; FN-PHANTOM-001 Part 9]"
    - "(O-LM): Layer 1 ASD features near-orthogonal to mean ρ across 150 (topic, paraphrase) pairs on Llama-3.1-8B [E from Phase 1; EN-PHANTOM-001]"
  open_results:
    - "rank of F_ASD on Ξ — exactly what Phase 2 measures [O — this document explains how]"

asd_apparatus_used:
  established_results:
    - "Layer 1 features structurally non-abelian via abelianization argument [E proved; ASD_FOUNDATIONS.md]"
    - "Layer 1 features empirically near-orthogonal to mean ρ [E from Phase 1; EN-PHANTOM-001]"
  open_results:
    - "Layer 2 features (Q_tail, r_plus) empirical orthogonality on LM trajectories — included in Phase 2 feature set, jointly tested via combined classifier"
---

# The Mechanism of Augmented Detection — How Phase 2's Classifier Comparison Tests the Rank of F_ASD on Ξ

## Scope

This document explains what the Phase 2 augmented detection test (FN-PHANTOM-002 §8.2) actually does and why. The protocol document specifies the procedure; the result writeup will report what happens; this document sits between them and explains the *mechanism* — what each component of the test measures, what the comparison structure is asking, and how the numerical outputs map back to the framework's audit-space picture. It is written for a reader who has read FN-PHANTOM-002 and EN-PHANTOM-001 and wants to understand the operational logic of the test before launching the GPU run, or for a reviewer who wants to understand what the test would have established under each possible outcome.

## Not covered

- The protocol details — generation parameters, model-loading strategy, file formats. See FN-PHANTOM-002 §8.2 and the runnable code at `tests/phase2_lm.py` and `tests/phase2_analysis.py`.
- The Phase 1 result that this phase builds on. See EN-PHANTOM-001.
- The audit-space and audit-blind theorems themselves. See FN-PHANTOM-001 Part 9.
- The construction of the F_2 walk and ASD features. See ASD_FOUNDATIONS.md.

## Prerequisites

- FN-PHANTOM-002 §4 (the orthogonality claim O-LM) and §5 (audit-blind dimension under augmentation).
- EN-PHANTOM-001 (the Phase 1 result establishing O-LM holds on Llama-3.1-8B).
- Comfort with: supervised binary classification, AUC as a separation metric, cross-validation, logistic regression coefficients.
- *Helpful but not required*: familiarity with FN-PHANTOM-001 Theorem D (optimal probe construction).

## Method Card

**Topic:** A pre-registered classifier-comparison protocol that measures whether the non-abelian audit dimensions established by Phase 1 (O-LM) project nontrivially onto the constraint subspace Ξ where probability distortion lives, on three case-study-validated topics.

**The test in one paragraph:** Generate K=100 base-model continuations and K=100 Instruct-model continuations on each of 5 paraphrases of each of 3 case-study topics. Score every trajectory under both models so each carries a full $(\text{surp}_{\text{base}}, \text{surp}_{\text{inst}}, \rho)$ vector. Train three binary classifiers to predict "this trajectory came from Instruct vs base" using three different feature sets — abelian (Set A: mean ρ + std ρ), non-abelian (Set B: Layer 1 + Layer 2 ASD features), and combined (Set C). Compare AUC across feature sets via leave-one-paraphrase-out cross-validation. The AUC differences operationally measure how much information about the base-vs-Instruct distinction lives in each subspace of the audit space. The pattern of differences across topics maps onto framework predictions about where ASD adds detection power.

**Geometric interpretation:** Phase 1 established that $F_{\text{ASD}}$ and $F_{\text{ab}}$ are nearly perpendicular subspaces of the audit space $F$. Phase 2 measures the angle between each subspace and the **constraint subspace Ξ**. AUC(A) measures the projection of $F_{\text{ab}}$ onto Ξ. AUC(B) measures the projection of $F_{\text{ASD}}$ onto Ξ. AUC(C) measures the projection of the combined span $F_{\text{aug}} = F_{\text{ab}} + F_{\text{ASD}}$ onto Ξ. The audit-blind theorem says detection capability is bounded by these projections; Phase 2 measures them empirically.

**Mental model:** Think of it as a triangulation. Phase 1 placed two surveying instruments — abelian and ASD — and showed they are oriented in different directions (their orthogonality). Phase 2 asks each instrument to measure the same target (the constraint subspace Ξ) and reports their measurements. If both instruments see the target and the combined reading is more accurate than either alone, the orthogonality has practical force. If only one sees the target, the orthogonality exists but doesn't help where it matters. If neither sees it, the test setup is wrong somewhere.

**Three diagnostic outcomes:**
- (i) Set C AUC exceeds Set A AUC by the predicted margin: ASD adds dimensions that hit Ξ. The audit-blind subspace genuinely shrinks. Phase 2 passes.
- (ii) Set C AUC ≈ Set A AUC within 0.02 on all topics: ASD adds dimensions but they don't hit Ξ. Orthogonal but irrelevant. Phase 2 fails (F2-1) but Phase 1 stands.
- (iii) Set B AUC ≥ 0.65 on its own: ASD-only classifier detects the distortion. Even stronger evidence that ASD-derived audit functions hit Ξ.

**Plus a directional-alignment check (P2-6).** AUC magnitude alone can't distinguish whether ASD detects *exactly* what Bridge B's structural prediction says (outcome b) from detecting *something else* correlated with origin (outcome a). P2-6 tests whether the classifier's standardized weight patterns match Bridge B's predicted cross-topic ordering and per-topic feature-class emphasis. P2-6 passing alongside P2-1 is the structural-unification claim. P2-6 failing while P2-1 passes is the weaker result — ASD detects something real but not specifically what Bridge B predicts. See §3 and §8.3.

**Read next:** Section 1 for what the classifier task is actually measuring. Section 2 for the geometric meaning of the three feature sets. Section 3 for the diagnostic logic of the comparison. Section 7 for the connection to Theorem B.

---

## Section 1: What the Classifier Task Actually Measures

### 1.1 The setup, restated

A language model policy $\pi$ is a function from prompts to probability distributions over completions. Phase 2 has access to two policies:
- $\pi_{\text{base}}$: Llama-3.1-8B without RLHF
- $\pi_{\text{inst}}$: Llama-3.1-8B with RLHF — a different distribution on the same support

For each (topic, paraphrase) pair $(p)$, generate K=100 continuations from each policy at temperature 0.7. The generations come out as token sequences. For each generated token in each trajectory, compute its surprisal under both policies:
$$\text{surp}_{\text{base}}(t_i) = -\log \pi_{\text{base}}(t_i \mid t_{<i}, p), \quad \text{surp}_{\text{inst}}(t_i) = -\log \pi_{\text{inst}}(t_i \mid t_{<i}, p)$$
The per-token leakage is $\rho_i = \text{surp}_{\text{base}}(t_i) - \text{surp}_{\text{inst}}(t_i)$.

So every trajectory has three parallel sequences attached: surprisal under base, surprisal under inst, and ρ. Plus its origin label (base or inst).

### 1.2 The classifier sees only the trajectory

The classifier does **not** see which model generated which trajectory — that's the label it's trying to predict. It sees only the trajectory's feature vector (computed from the surprisal sequences) and tries to assign a posterior probability of "this came from inst." A standard binary classifier evaluation (AUC, accuracy, signal rate at low FPR) measures how well it does.

This is not a prediction problem in the operational sense. The motivation isn't "we want to detect AI-generated text." The classifier is a **measurement instrument** — its AUC is an estimator of a population-level quantity about the policies $(\pi_{\text{base}}, \pi_{\text{inst}})$.

### 1.3 What population-level quantity AUC estimates

AUC has a well-known interpretation: AUC = $P(\text{score}(x_+) > \text{score}(x_-))$ where $x_+ \sim \pi_{\text{inst}}$ and $x_- \sim \pi_{\text{base}}$, and score is the classifier's output. AUC = 0.5 means the score is uninformative; AUC = 1.0 means perfect separation.

AUC at the population level is equivalent (up to a monotone transform) to the **Wasserstein-1 distance** between the score distributions under the two policies. The classifier maps trajectories into ℝ via its features-to-score mapping; AUC measures how separated the two policies' score distributions are after that mapping.

For a fixed feature set $\Phi$, the maximum achievable AUC over any classifier on $\Phi$ is determined by **how much information about the base-vs-Instruct distinction is preserved by the projection onto $\Phi$**. If $\Phi$ throws away all distinguishing information, max AUC is 0.5. If $\Phi$ preserves all the distinguishing information, max AUC is whatever the Bayes classifier achieves on the full data.

### 1.4 The point: AUC under Φ measures information about Ξ that Φ captures

The constraint subspace Ξ from FN-PHANTOM-001 is the linear subspace of policy-tangent space at $\pi_{\text{base}}$ along which RLHF moved the policy to produce $\pi_{\text{inst}}$. By construction, **all of the base-vs-Instruct distinction lives in Ξ**. A trajectory feature that's invariant to perturbations along Ξ carries zero information about the distinction; a feature that varies maximally with perturbations along Ξ carries maximum information.

So: the achievable AUC for a classifier using feature set $\Phi$ is bounded by how well $\Phi$ can resolve directions in Ξ. Phase 2's three-feature-set comparison measures, for each of $\{F_{\text{ab}}, F_{\text{ASD}}, F_{\text{aug}}\}$, the achievable AUC on this Ξ — i.e., how well each subspace projects onto the constraint geometry.

A reader fluent in the theory could phrase the whole protocol as: "compute three SVD-derived projection magnitudes of audit subspaces onto Ξ, by training classifiers as numerical proxies for the projection coefficients." That's what's happening. The classifier is the numerical apparatus; the geometry is the content.


---

## Section 2: Three Feature Sets, Three Subspaces of F

The three feature sets correspond to three audit-space subspaces with different geometric character.

### 2.1 Set A — abelian (mean ρ + std ρ)

**Features:**
- mean_rho: $\bar\rho(x) = \frac{1}{T}\sum_i \rho_i$
- std_rho: $\text{std}_i(\rho_i)$

**Audit-space membership:** Both are abelian functionals — they depend only on the multiset of $\rho_i$ values, not on their order. mean_rho is the population baseline measurement of distortion (this is *the* signal HB-PHANTOM-001 is built around). std_rho captures within-trajectory variance — it's still abelian (variance is a sum-of-squared-deviations functional, symmetric under permutations).

**What set A's AUC measures geometrically:** The angle between the abelian audit subspace's natural direction and the constraint subspace Ξ. If RLHF reshaped the policy in directions where the average per-token leakage changes (mean_rho gives signal) or where the spread of leakage values changes (std_rho gives signal), Set A AUC is high. If RLHF reshaped only the *temporal arrangement* of leakage events without changing means or spreads, Set A AUC is at chance.

**Why only two features:** Phantom's existing methodology (HB-PHANTOM-001) identifies mean_rho as the primary measurement and treats variance over paraphrases as noise. A more expressive abelian classifier would include richer summary statistics — quantiles of ρ, tail behavior, surprisal distribution moments. Set A is intentionally minimal because it's the operational baseline of what existing Phantom probes look like. A richer abelian set would shift the headline number but is outside Phase 2's scope.

### 2.2 Set B — ASD-only (Layer 1 + Layer 2 features)

**Features (9):**
- Layer 1 scalars: drift, timing_cv, mean_depth_excess, isolated_frac
- Layer 2 depth profile: Q_tail_1, Q_tail_2, Q_tail_3, Q_tail_4
- Recurrence fit: r_plus

**Audit-space membership:** All non-abelian. Each is a continuous functional of the empirical pair $(\nu_x^T, \mu_x^T)$ from the F_2 walk on the encoded ρ trajectory. The walk's free reduction step is order-dependent, so cylinder masses and depth statistics depend on $\rho$'s temporal arrangement. Phase 1 established empirically that these features are near-orthogonal to mean_rho (median |r| ≈ 0.13 across 150 pairs).

**What set B's AUC measures geometrically:** The angle between $F_{\text{ASD}}$ and Ξ. If RLHF reshaped the policy in ways that affect the temporal structure of leakage (which positions tend to be high-ρ relative to others, how clustered or spread leakage events are), Set B AUC is high. If RLHF reshaped only *aggregate* leakage statistics that mean_rho already measures, Set B AUC could be at chance even though Phase 1's orthogonality result is strong.

**Why include Layer 2:** Phase 1 used only Layer 1. Layer 2 features (Q_tail at multiple depths and the geometric decay rate r_plus) capture finer structure of the walk's depth distribution. They're cheap to add — they come from the same encoder run. Including them makes Set B more powerful as a detector if the temporal structure has multi-scale character.

### 2.3 Set C — combined

**Features (11):** A ∪ B.

**Audit-space membership:** Spans $F_{\text{aug}} = F_{\text{ab}} + F_{\text{ASD}}$.

**What set C's AUC measures geometrically:** The angle between $F_{\text{aug}}$ and Ξ. By the orthogonality from Phase 1, $F_{\text{aug}}$ has dimension approximately $\dim F_{\text{ab}} + \dim F_{\text{ASD}}$ (i.e., the redundancy is small). The achievable Set C AUC is therefore bounded above by the achievable AUC on a feature set spanning a higher-dimensional subspace of $F$ than either A or B alone.

The crucial property: **AUC(C) ≥ max(AUC(A), AUC(B))** is guaranteed by classifier construction (the C-classifier could just zero out the features it doesn't want), but *equality* corresponds to one feature set capturing all the information the other has plus more. Strict inequality (AUC(C) > both) means each set captures information the other misses.

### 2.4 The geometric signature of each outcome

| Outcome | What the geometry says |
|---|---|
| AUC(C) > AUC(A) by margin and AUC(B) ≥ 0.65 | $F_{\text{ASD}}$ and $F_{\text{ab}}$ both project nontrivially onto Ξ in distinct directions. Augmentation is real. |
| AUC(C) ≈ AUC(A), AUC(B) < 0.55 | $F_{\text{ASD}}$ has near-zero projection onto Ξ. Orthogonal in $F$ but irrelevant on the constraint subspace. |
| AUC(C) ≈ AUC(B), AUC(A) low | $F_{\text{ab}}$ has small projection but $F_{\text{ASD}}$ has large. ASD is the right tool, ρ is the baseline. |
| All three near 0.5 | Neither subspace projects onto Ξ. The feature sets aren't seeing the constraint at all. Method failure. |

The pre-registered checks P2-1 through P2-5 partition this outcome space.


---

## Section 3: The Diagnostic Logic of the Comparison

### 3.1 The pre-registered checks restated

Three pass criteria and three falsification triggers. The pass criteria target the framework prediction; the falsification triggers identify clean negative results.

**Pass criteria:**
- **P2-1:** AUC(C) − AUC(A) ≥ topic-specific threshold per topic (0.05 for the CS-PHANTOM-001 topics, 0.10 for crime demographics).
- **P2-4:** AUC(B) ≥ 0.65 per topic (ASD alone has detection capability).
- **P2-5:** at least 3 ASD features have |coefficient| > 0.1 in the standardized Set C classifier per topic (the classifier is *demonstrably using* ASD information, not just including it).
- **P2-6:** Bridge B directional alignment. (i) cross-topic ordering Spearman ρ ≥ 0.5 between predicted leakage rank and empirical total ASD weight magnitude; (ii) per-topic feature-class emphasis matches predicted regime (Layer 2 ≥ 30% on crime; Layer 1 cancellation ≥ 50% on Wehrmacht and founding fathers).

**Falsification triggers:**
- **F2-1:** all |AUC(C) − AUC(A)| < 0.02 (no detection gain anywhere).
- **F2-2:** all AUC(B) < 0.55 (ASD has no signal anywhere).
- **F2-3:** any AUC(C) < AUC(A) (ASD degrades performance — pure noise overfitting).

### 3.2 Why the structure isn't symmetric

P2-1 is one-sided (C must exceed A by a positive margin). F2-3 is the symmetric falsification (any C below A fails). This asymmetry reflects the framework's prediction direction: ASD adds dimensions to F, so the augmented set should perform at least as well as the baseline. C performing worse than A would mean adding informative features hurt performance — which is only possible through noise-induced overfitting, statistically. That's a real failure mode but a different one than "ASD doesn't help" (F2-1).

### 3.3 Why three topics, not one

The three topics are picked deliberately, not for variance reduction.

**Founding fathers slavery and Wehrmacht conduct (CS-PHANTOM-001):** the established induced-hole regime. Prior case study work documents that Llama-3.1-8B-Instruct exhibits parametric memory of suppressed framings on these topics — the trajectory has structural signature of "model knows X but is shaped not to say X directly." The temporal signature of that suppression is what Layer 1 ASD features (drift, timing_cv, isolated_frac) most directly target. Predicted gain ≥ 0.05.

**Crime demographics (CS-PHANTOM-002):** the greedy-decoding-artifact regime. The case study documents a specific temporal pattern — early commitment to a shaped framing, then coast in normal generation, often with reframing at the end. This is exactly the multi-phase trajectory that Layer 2 features (Q_tail and r_plus) most directly capture. Predicted gain ≥ 0.10.

**The point of having both:** if the gain pattern is `crime > Wehrmacht ≈ founding`, the framework's predictions are calibrated correctly — Layer 2 helps where Layer 2 should help, and the relative magnitudes match the case-study expectations. If the gain pattern is inverted (`founding > crime`), the framework needs revision: either the case-study characterizations are wrong, or the feature set's targeting is mismatched, or both. Either result is informative.

### 3.4 What partial pass means

If P2-1 passes on 2 of 3 topics, the framework documents call this a "partial pass" — the augmentation works on the topics where it's predicted to work most strongly (or, in the failure pattern, on the topics where it shouldn't), and the program proceeds with caveats. The interpretation depends on which topic missed:

- **If founding fathers misses but the other two pass:** The induced-hole signature on this specific topic doesn't have the temporal character ASD targets. Possibly the constraint engages differently (e.g., as a subject-pivot rather than as a leakage burst). Could indicate a class of induced holes that need a different feature set.

- **If Wehrmacht misses but the other two pass:** Similar interpretation. Or possibly the topic is more dispersed in trajectory style across the 5 paraphrases than the others, weakening the classifier's per-fold signal.

- **If crime demographics misses but the other two pass:** The greedy-decoding-artifact characterization may be wrong, or the artifact may not produce a temporal signature ASD captures, or the artifact doesn't engage on Llama-3.1-8B (only on Llama-3.1-405B-Instruct in the original case study).

The protocol's pre-registered partial-pass interpretation is to record the result and proceed to Phase 3 with the surviving topic set.

### 3.5 What the AUC numbers tell you about the constraint

A few rough calibration intuitions for reading AUC values:

- AUC ≈ 0.50: classifier at chance. Either Ξ has nothing in this audit subspace, or the classifier is mis-specified. AUC at chance is the null result.
- AUC ≈ 0.65–0.75: real but weak signal. Ξ has a partial projection onto this subspace — enough to detect but not enough to reliably classify individual trajectories. This is the regime where adding more features (Set A → Set C) most demonstrably helps.
- AUC ≈ 0.80–0.90: strong signal. Ξ has a substantial projection.
- AUC > 0.95: trivially separable. This is unusual for distortion measurement and would warrant a check that the classifier isn't picking up on a tokenizer artifact or generation-length confound rather than the constraint itself.

The predicted regime for Phase 2 is 0.65–0.85 across topics, with AUC(C) on the high end and AUC(A) on the lower end. AUC near 0.95 anywhere is a smell test failure that warrants investigation before celebrating.


---

## Section 4: Why Leave-One-Paraphrase-Out Cross-Validation

### 4.1 Random K-fold CV is wrong here

Standard random K-fold cross-validation splits the data uniformly across folds. For Phase 2 that would mean: for each (topic, paraphrase) pair, ~80 trajectories go to training and ~20 to test, randomly. The classifier sees the same 5 paraphrases in training and test.

This setup overestimates AUC. The classifier can learn paraphrase-specific patterns — "wording starting with *Discuss* tends to produce shorter responses" — that have nothing to do with base-vs-Instruct but happen to correlate with origin in this particular sample. On test data drawn from the same paraphrases, those patterns work; on a held-out paraphrase, they don't generalize.

### 4.2 Leave-one-paraphrase-out forces generalization

Phase 2 uses 5-fold leave-one-paraphrase-out CV. Each fold trains on 4 paraphrases (all topics' worth, ~800 trajectories) and tests on the held-out 5th (~200 trajectories). The classifier never sees the test paraphrase's wording during training.

What does this force the classifier to learn? A pattern that **transfers across paraphrase wording** for the *same topic*. That pattern has to depend on the topic's content rather than the surface form of the prompt — which is exactly what "detecting RLHF distortion on this topic" means. The constraint subspace Ξ for a topic is invariant to paraphrase wording (the same suppression operates regardless of how the question is phrased); a classifier that picks up on Ξ will generalize across paraphrases; a classifier that picks up on surface artifacts won't.

### 4.3 What this implies about the AUC numbers

Leave-one-paraphrase-out AUC is a **lower bound** on the population AUC for the topic. The classifier has access to fewer training paraphrases than the full data would supply, so its weights are less calibrated than a within-paraphrase classifier's. For Phase 2's question — does ASD add detection power across paraphrases — this is the right metric. For an absolute answer to "how detectable is the distortion," random K-fold would give a tighter (and higher) estimate.

A practical consequence: AUC values reported in Phase 2 should be a few points lower than what within-paraphrase CV would produce on the same data. This is by design.

### 4.4 The five folds are not exchangeable

Each fold's AUC is on a single held-out paraphrase, so fold-level variability reflects how distinctive each paraphrase's vocabulary is. If one paraphrase happens to elicit unusual outputs from one of the models, the fold using it as test could produce a noisy AUC. Aggregating over 5 folds dampens this; reporting AUC mean and SE across folds shows the variability.

A pathological pattern would be: 4 folds with AUC ≈ 0.85 and one fold with AUC ≈ 0.50. This indicates one paraphrase produces atypical generations and the classifier's training-paraphrase patterns don't transfer to it. This is informative — that paraphrase is doing something the others aren't — but it weakens the aggregated AUC's interpretability. Phase 2 reports per-fold AUC values to make such patterns visible.


---

## Section 5: Standardized Coefficients and the P2-5 Smoking Gun

### 5.1 The problem P2-5 solves

P2-1 alone has a loophole. Consider the case where Set A and Set B happen to have a residual correlation — even small (say, |r| = 0.2) — that survived Phase 1 as one of the long-tail values in the |r| distribution. Set C has access to both, and a sufficiently flexible classifier could exploit that residual correlation in ways that weren't available to Set A alone, **even if the additional information all comes from the abelian features**. The AUC could go up without ASD features doing any work — they just gave the classifier a bigger search space in which to overfit small Set-A-internal patterns.

P2-5 defends against this. The check is: when you train Set C and look at the resulting weight vector, are there at least 3 ASD features with absolute standardized coefficient > 0.1? If yes, the classifier is *demonstrably* relying on ASD features. If no — say only the two ρ-features have nonzero weight and the rest are near zero — the AUC gain is coming from the ρ features alone, and the ASD additions were ignored.

### 5.2 Why standardized coefficients

Logistic regression coefficients on raw features depend on the features' units. drift is in z-score units; mean_rho is in nats per token; r_plus is dimensionless. Comparing raw coefficients across features is meaningless — a large drift coefficient could mean drift dominates the prediction or that drift's natural scale is small, requiring large weight to contribute.

Standardization (subtract mean, divide by std on the training set) puts every feature on the same scale: a 1-unit change in any standardized feature is a 1-σ change. Standardized coefficients then directly compare "how much does this feature contribute per σ of variation."

### 5.3 The 0.1 threshold

A standardized coefficient of 0.1 means a 1-σ change in the feature shifts the log-odds of "this is inst" by 0.1 — a roughly 2.5% shift in posterior probability for cases near the decision boundary. This is the threshold for "the feature contributes at least minimally"; it's not a strong threshold. Anything below 0.1 is essentially zero contribution.

The threshold is not pre-registered as 0.1 specifically; it's an operational choice. A stricter threshold (say 0.3) would force the ASD features to be major contributors, not just non-zero ones. The 0.1 threshold is the framework's "any contribution counts" line, suitable for the smoking-gun question rather than a feature-importance ranking.

### 5.4 What different P2-5 outcomes mean

**P2-5 passes (≥3 ASD features with |coef| > 0.1 on every topic):** the augmented classifier is using ASD information; AUC gain is genuinely from F_ASD's projection onto Ξ. P2-1's pass becomes interpretable as an ASD contribution.

**P2-5 fails on some topics (< 3 ASD features active):** the classifier on those topics found that ρ features alone explain the variance; ASD features were dropped (zero weight). This is an interesting partial result — ASD has signal somewhere (Set B's AUC) but the combined classifier deemed it redundant on these specific topics. The orthogonality from Phase 1 doesn't always translate to additivity in detection.

**P2-5 fails on every topic:** the AUC gain in Set C is illusory — ASD features added flexibility but the classifier didn't use it. This combined with a Set C AUC > Set A AUC is a sign of overfitting (the classifier's flexibility helped it fit the training noise, not the test signal). Set B AUC alone is the test of whether ASD has any signal.

### 5.5 An alternative view: feature importance as a Theorem D approximation

FN-PHANTOM-001 Theorem D constructs the optimal $N$ abelian probes for a target k-dimensional concerning subspace via SVD. The optimal probes are linear combinations of audit functionals weighted by their projection onto Ξ.

A classifier trained on $F_{\text{aug}}$ doesn't construct optimal probes via SVD, but its standardized coefficients are an *empirical proxy* for those projections. A feature with high coefficient is one the classifier learned has high projection onto the base-vs-Instruct distinction subspace (which is part of Ξ).

This means the Phase 2 coefficient table is a (rough, sample-noisy) estimate of which audit functions in $F_{\text{aug}}$ would be the optimal probes if you constructed Theorem D's $(N+M)$ optimal probe set on this data. Future work could formalize this — using the classifier weights as starting points for an empirical Theorem D extension.


---

## Section 6: Topic-Specific Thresholds as Framework Predictions

### 6.1 Why thresholds vary across topics

The thresholds are calibrated by case-study type, not chosen for statistical convenience.

- **Founding fathers slavery (CS-PHANTOM-001):** induced-hole regime. RLHF parametric memory of the suppressed "founders were slaveholders" framing produces moderate temporal signature in trajectories. Predicted ASD-contribution-to-AUC: modest. Threshold: 0.05.

- **Wehrmacht conduct (CS-PHANTOM-001):** induced-hole regime. Similar character to founding fathers — clean shaping with detectable parametric memory. Threshold: 0.05.

- **Crime demographics (CS-PHANTOM-002):** greedy-decoding-artifact regime. The case study documents a multi-phase trajectory pattern (commitment, coast, reframe) that has rich temporal structure. ASD's depth profile and Q_tail features are designed to capture exactly this kind of structure. Predicted ASD-contribution-to-AUC: large. Threshold: 0.10.

### 6.2 The thresholds are predictions, not just acceptance criteria

The 0.05/0.05/0.10 thresholds aren't arbitrary one-sided tests — they encode a prediction about the *relative ordering* of expected gains across topics. The framework predicts crime demographics > Wehrmacht ≈ founding fathers in ASD-contribution-to-AUC.

If the data shows founding fathers >> crime demographics, the order is inverted. That doesn't necessarily mean the framework is wrong — it could mean the case-study characterizations are wrong, or that crime demographics' multi-phase pattern doesn't engage on Llama-3.1-8B (only on the 405B model), or that ASD's Layer 1 features happen to be more sensitive to the founding-fathers signature than Layer 2 features are to crime's. Each interpretation suggests different follow-up work.

The point is the thresholds operationalize the framework's predicted *pattern*, not just a conservative one-sided check. A pass that violates the predicted pattern is informative even when individual thresholds are met.

### 6.3 What if a topic doesn't engage RLHF

A possibility worth flagging: the case studies may have been done on a different model substrate (e.g., Llama-3.1-405B-Instruct or a different model entirely), and Llama-3.1-8B-Instruct may simply not exhibit RLHF distortion on a particular topic. If so, Phase 2's classifier sees no signal to detect, and Set A, Set B, Set C all sit at AUC ≈ 0.5 on that topic.

The framework's interpretation under this case: not a falsification of the framework, but a refutation of the assumption that the topic engages RLHF on this model. The result is recorded; the topic is excluded from subsequent phases; the program proceeds.

This is why P2-1's per-topic structure matters. A pass on 2 of 3 topics with the third showing "Set A also at chance" is consistent with the framework — it just means the third topic isn't shaped on this model. A failure on a topic where Set A is high but Set B and C aren't is a different result: ρ detects distortion but ASD doesn't add to it. The combination of A's level and the gain pattern tells you which interpretation applies.


---

## Section 7: Connection to the Audit-Blind Apparatus

This section makes the link between Phase 2's empirical numbers and Theorem B's geometric content explicit.

### 7.1 Theorem B in operational form

FN-PHANTOM-001 Theorem B states: for any choice of $N$ audit functions in $F$,
$$\dim(\ker \Pi_N) \geq \dim(\Xi) - N$$
where $\Pi_N: \Xi \to \mathbb{R}^N$ is the audit projection. The left side is the audit-blind subspace dimension; the right side is a lower bound that's tight when the $N$ functions are chosen optimally per Theorem D's SVD construction.

### 7.2 What the bound says about AUC

For any fixed feature set $\Phi$ used by a classifier:
- The classifier's max achievable AUC (Bayes optimal on $\Phi$) is determined by $\dim(\Pi_\Phi(\Xi))$ — the dimension of $\Phi$'s projection onto Ξ.
- Equivalently: AUC is a monotone function of how much of $\Xi$'s variation $\Phi$ can resolve.

So AUC(A) is a measurement (up to a monotone transform and finite-sample noise) of $\dim(\Pi_{F_{\text{ab}}}(\Xi))$. AUC(B) measures $\dim(\Pi_{F_{\text{ASD}}}(\Xi))$. AUC(C) measures $\dim(\Pi_{F_{\text{aug}}}(\Xi))$.

### 7.3 The audit-blind dimension under augmentation

If the projections are independent (which is the geometric content of orthogonality plus the framework's prediction that both subspaces hit Ξ in different directions), then
$$\dim(\Pi_{F_{\text{aug}}}(\Xi)) = \dim(\Pi_{F_{\text{ab}}}(\Xi)) + \dim(\Pi_{F_{\text{ASD}}}(\Xi))$$
and the audit-blind subspace shrinks by $\dim(\Pi_{F_{\text{ASD}}}(\Xi))$ — call this quantity $M$, the rank of $F_{\text{ASD}}$ on Ξ.

**Phase 2's central numerical question:** what is $M$?

Lower bounds on $M$:
- AUC(B) > 0.5: $M \geq 1$ (some projection exists).
- AUC(C) > AUC(A): $M \geq 1$ in directions independent of $F_{\text{ab}}$'s projection.
- AUC(C) − AUC(A) translates roughly to "how many additional Ξ-directions $F_{\text{ASD}}$ resolves beyond what $F_{\text{ab}}$ already gave." Larger AUC gain implies larger M.

The mapping from AUC delta to a specific integer $M$ requires more apparatus (a parametric model relating AUC to subspace dimension), which Phase 2 doesn't construct. The numerical AUC delta is the empirical input; the framework's interpretation places it on the Theorem B geometry.

### 7.4 Why this is the right test for "audit-blind shrinks"

A different protocol could ask: "fit a high-capacity nonlinear classifier on Set C and show its AUC is much higher than on Set A." But that wouldn't measure the rank of $F_{\text{ASD}}$ on Ξ — it would measure the classifier's capacity to fit nonlinear decision boundaries. The audit-blind theorem's geometric content is *linear* (it's about subspaces). The matching empirical apparatus is therefore linear classifiers on specified feature spaces.

This is why Phase 2 uses logistic regression. It's not a state-of-the-art classifier; it's the right classifier for measuring the geometric quantity the framework cares about. Replacing it with a deep neural net would inflate AUC and obscure the geometric interpretation.

### 7.5 What a Phase 2 pass would let you say

Concretely: "we have empirically established that $F_{\text{ASD}}$ contributes at least one independent direction of resolution onto Ξ on Llama-3.1-8B's case-study-shaped topics. The audit-blind subspace as bounded by Theorem B is reducible by at least 1, with empirical evidence suggesting the reduction is closer to 3 (Phase 1 effective rank). Phase 2 is the first empirical evidence connecting the structural orthogonality of Phase 1 to the constraint subspace where distortion lives."

This is a meaningful step. It's not a theorem proof; it's the empirical translation of a theorem's content into a verifiable measurement.


---

## Section 8: What Phase 2 Cannot Establish

A test is more useful when its limits are explicit. Phase 2 measures specific quantities; a list of what it does not measure is required to keep the verdict honest.

### 8.1 Phase 2 does not measure the *exact* rank of F_ASD on Ξ

It measures whether the rank is ≥ 1 (via Set B AUC > 0.5) and whether it adds dimensions independent of $F_{\text{ab}}$'s projection (via AUC(C) > AUC(A)). The numerical mapping from "AUC gain of 0.07" to "rank gain of 2" is informal. A rigorous mapping would require a parametric SVD-based estimator on the joint distortion-to-function map, which is the Theorem D extension to non-abelian audits — open per FN-PHANTOM-002 §12 Q1.

### 8.2 Phase 2 doesn't compare against richer abelian baselines

Set A uses two features (mean ρ, std ρ). A more expressive abelian baseline would include richer summary statistics — quantiles of ρ, skewness, kurtosis, or even position-binned summaries of ρ across the trajectory's first/middle/last thirds. None of those are temporally ordered (they're symmetric over multisets of $\rho_i$) but they extract more abelian information than Set A.

If a richer abelian Set A* showed AUC ≈ AUC(C), the conclusion would shift: ASD adds no detection power *beyond a sufficiently rich abelian baseline*. The framework's claim about Set A specifically would still hold — operational Phantom probes are mean-ρ-based, and ASD beats those — but the structural claim would weaken.

The choice not to include richer abelian baselines is partly resource (training many classifiers slows the analysis) and partly framing (the question is "does ASD beat the operational standard"). A more thorough variant would include a richer Set A as Set A+, expanding the comparison to four sets. This is recommended for any followup.

### 8.3 Phase 2 doesn't fully address why the ASD features have detection power

A pass on P2-1 establishes that ASD features have nontrivial projection onto Ξ. The AUC magnitude alone doesn't explain the mechanism. Possibilities:

- (a) RLHF reshapes the *temporal arrangement* of high-leakage tokens (e.g., commitment-front-loaded patterns) and ASD detects this directly.
- (b) RLHF introduces specific token bigrams or syntactic patterns that propagate into the ρ trajectory through autoregressive context, and ASD picks up on the resulting depth statistics.
- (c) Some incidental property of how Llama-3.1-Instruct samples — temperature behavior, repetition penalty heuristics — produces a temporal signature that happens to correlate with the base-vs-Instruct distinction without being mechanistically related to RLHF.

The Phase 2 protocol now includes **P2-6 (Bridge B directional check)** as a partial defense against outcome (c) and as a positive test for outcome (b). The check tests whether classifier weight patterns match Bridge B's μ²(1-s²) structural prediction:

- **Sub-check (i):** total ASD weight magnitude per topic should rank-order with predicted leakage strength (crime > Wehrmacht ≈ founding) by Spearman ρ ≥ 0.5.
- **Sub-check (ii):** per-topic feature-class emphasis should match the regime — greedy-decoding-artifact topic (crime) emphasizes Layer 2 depth/recurrence features ≥30%; induced-hole topics (Wehrmacht, founding) emphasize Layer 1 cancellation features ≥50%.

If P2-1 passes AND P2-6 passes, the combined evidence supports outcome (a) or (b) — ASD detects what Bridge B predicts, by mechanisms consistent with the framework's specialization of Bridge B to ASD coordinates. If P2-1 passes AND P2-6 fails, the result is the weaker outcome — ASD adds detection but not in the direction the framework currently predicts. The detection improvement is real, but the structural-unification claim would need revision.

Distinguishing (a) from (b) more rigorously requires interventional experiments — controlled training of a toy RLHF setup with known mechanisms — which remains outside Phase 2's scope. P2-6 is a cheap necessary condition, not a sufficient one.

### 8.4 Phase 2 is single-model

Llama-3.1-8B-Instruct only. A pass establishes the result on this substrate; it does not establish that ASD-augmented detection works across models. Phase 5 (cross-institutional differential atlas, FN-PHANTOM-002 §8.5) addresses this.

### 8.5 Phase 2 doesn't measure the rank for Layer 3

The features used (Layer 1 + selected Layer 2) are scalar summaries of the empirical pair. Layer 3 — the full $(\nu_x^T, \mu_x^T)$ pair as a measure-valued object — could in principle add more dimensions to $F_{\text{ASD}}$. Phase 2's test fixes the lower-bound contribution of Layer 1+2 specifically; a Layer-3-enabled test could find higher rank.

This is plausibly the next refinement when the modern feature definitions arrive — they may include Layer 3 functionals not present in this implementation.

### 8.6 Phase 2 doesn't measure detection on novel topics

The 3 topics are specifically the case-study-validated ones. The test is "ASD adds detection power *on topics where distortion is known to exist by independent evidence*." It does not test "ASD detects distortion on previously unseen topics." That would require either a broader topic set or a held-out topic set — both beyond Phase 2's scope and structure.

For the framework's central claim (audit-blind shrinks), the case-study topics are the right test. For an operational claim ("ASD finds distortion in the wild"), a different protocol would be needed.

### 8.7 Phase 2's classifier is logistic regression

Linear in standardized features. As argued in §7.4 this is the right choice for measuring the geometric quantity the framework cares about. But it does mean: if there exist nonlinear interactions between Set A and Set B features that the linear classifier can't exploit, Phase 2 underestimates the achievable AUC of the combined feature space. The asymmetry between the linear-classifier AUC and the Bayes-optimal AUC on a feature space is well-known but bounded; in practice for low-dimensional feature spaces with this much data per class, the linear classifier is close to Bayes-optimal.


---

## Section 9: Reading the Output of phase2_analysis.py

When Phase 2 runs to completion, the output files contain the empirical numbers; this section explains how to read them in the framework's terms.

### 9.1 The console summary

The terminal print at the end of `phase2_analysis.py` shows three rows per topic:
```
crime_demographics              delta=+0.143  (thr=0.1)  PASS
founding_fathers_slavery        delta=+0.062  (thr=0.05)  PASS
wehrmacht_conduct               delta=+0.058  (thr=0.05)  PASS
```
(Hypothetical values; actual numbers will differ.)

Read each row as: "On this topic, the augmented audit class extracts [delta] more AUC than the abelian baseline. The framework predicted at least [thr]. Verdict."

The aggregate verdict line reports whether all three thresholds met.

### 9.2 The markdown report

`phase2_features_llama_report.md` is more detailed:

- **AUC table per topic:** Set A, B, C means with cross-fold SE. Look for: are the AUC values in the 0.65-0.85 range (interpretable signal) rather than 0.51 (chance) or 0.99 (suspicious)? Is the C-A delta positive everywhere?

- **Paired bootstrap p-values:** the one-sided test of "delta = AUC(C) - AUC(A) > 0." A p-value below 0.05 means the bootstrap distribution of deltas almost never includes 0, supporting the gain. Wide CIs are fine; the point estimate matters more than statistical significance for this small-sample test.

- **Set C coefficients:** standardized weights for the combined classifier per topic. Look for ρ-features (mean_rho, std_rho) and ASD features (drift, timing_cv, ...) with both having absolute weights > 0.1. The colored bar chart in `phase2_roc_and_coefs.png` shows this visually.

### 9.3 The ROC curves

`phase2_roc_and_coefs.png` shows per-topic ROC curves for all three feature sets overlaid. What to look for:

- **Are the curves above the diagonal?** Below means worse-than-chance — overfitting or label confusion.
- **Does the C curve sit above both A and B curves?** That's the additivity check, more visual than numeric.
- **At FPR=0.05 (gray dotted line), what's the TPR for each set?** The "operational signal rate at low false-positive rate" is a more practical detection quality metric than AUC.

### 9.4 What the per-fold variance tells you

Five folds per topic per feature set. If the AUC values across folds are tightly clustered (e.g., 0.74, 0.76, 0.73, 0.77, 0.75) the result is reproducible. If they're spread (0.65, 0.78, 0.72, 0.55, 0.83) one or two paraphrases are doing different work — probably the topics are pulling the model into very different regimes depending on phrasing.

The mean across folds is the headline; the per-fold spread is the texture. A high mean with high spread is interesting but should be flagged — the topic isn't producing a uniform signature across paraphrases.

### 9.5 What to do with a partial result

The framework's pre-registered "partial pass" is 2 of 3 topics meeting threshold. The protocol's continuation rule (FN-PHANTOM-002 §9.2):

- **Partial pass on shaped + Wehrmacht, miss on crime demographics:** Layer 2 features (which were predicted to drive the crime demographics gain) didn't deliver. Possible interpretation: greedy-decoding-artifact regime doesn't engage on Llama-3.1-8B-Instruct specifically. Drop crime from the shaped-topic candidate list; proceed to Phase 3 with founding fathers + Wehrmacht as the empirical anchor.

- **Partial pass on crime + Wehrmacht, miss on founding fathers:** unexpected — induced-hole signature on founding fathers should be cleanest given case-study evidence. Possible: the case-study finding was on a different model (e.g., 405B-Instruct or earlier Llama-3.1 versions) and 8B-Instruct doesn't shape this topic. Investigate by checking whether the 8B-Instruct base output on founding fathers differs measurably from the 8B-base output at all — if not, the topic isn't engaged.

- **Partial pass on crime + founding, miss on Wehrmacht:** the most interpretable outcome. Wehrmacht's specific historical-political character may produce a different shaping signature than the others (e.g., refusal-dominant rather than misrepresentation-dominant; HB-PHANTOM-001 documents this distinction). The mismatch tells you something about RLHF's mechanism diversity.

- **Full pass:** proceed to Phase 3 (natural-vs-induced separation) and Phase 5 (cross-institutional atlas) per the program plan.


---

## Section 10: Summary — What This Test Does and Doesn't Do

### What Phase 2 does:

1. **Generates** 3,000 trajectories — 1,500 from base, 1,500 from Instruct — across 3 case-study topics × 5 paraphrases × 100 seeds.

2. **Scores** every trajectory under both models, producing the full $(\text{surp}_{\text{base}}, \text{surp}_{\text{inst}}, \rho)$ vector per trajectory.

3. **Trains** three logistic regression classifiers per topic on three feature sets (abelian, ASD, combined), using leave-one-paraphrase-out 5-fold CV.

4. **Reports** AUC per topic per feature set, with bootstrap CIs and paired bootstrap p-values for AUC differences.

5. **Examines** the standardized coefficients of the combined classifier to verify ASD features are demonstrably contributing (not just present and ignored).

6. **Compares** the empirical numbers against pre-registered topic-specific thresholds calibrated to framework predictions.

### What Phase 2 measures, in framework terms:

The classifier AUC on each feature set is an empirical proxy for the rank of that feature set's audit subspace on the constraint subspace Ξ. The Set C minus Set A AUC delta is the rank contribution of $F_{\text{ASD}}$ to the augmented audit space, in directions independent of $F_{\text{ab}}$. The standardized coefficients are an empirical proxy for the optimal-probe construction of Theorem D extended to non-abelian audit functions.

### What a pass means:

- The structural orthogonality from Phase 1 (in policy-space inner product) translates to operational additivity (in detection on the constraint subspace).
- The audit-blind subspace from Theorem B is reducible by at least one effective dimension on this model, with empirical support for closer to 3 dimensions.
- The Phantom methodology can be augmented operationally by adding ASD encoding and Layer 1+2 feature extraction to its standard paraphrase battery. This isn't a marginal improvement; it adds a class of measurements the methodology couldn't produce before.

### What a fail means:

- (F2-1) The ASD audit dimensions exist (Phase 1 confirmed) but don't project onto Ξ. Orthogonal but irrelevant. The structural argument stands; the operational claim is refuted on this model. Phase 1's result remains valid as a structural finding without operational consequences.
- (F2-2) The ASD features carry no signal at all. This contradicts Phase 1's |r| ≈ 0.13 with mean ρ — they should have *some* signal, even if only ρ-correlated. A complete F2-2 would be an internal inconsistency between Phases 1 and 2.
- (F2-3) The ASD features actively degrade detection. This means they're noise that's being weighted nonzero by the classifier. Indicates either feature-distribution problems or sample-size issues.

### What both pass and fail leave open:

- Which specific mechanism in $\pi_{\text{inst}}$ produces the ASD-detectable signature.
- Whether the result generalizes across model scales, model families, RLHF methodologies.
- Whether richer abelian baselines (beyond mean ρ + std ρ) would close the gap.
- The exact rank of $F_{\text{ASD}}$ on Ξ as a number.

These are followup questions, not failures of Phase 2 to deliver on its specified goal.

---

## Glossary of Notation Used

- $\pi_{\text{base}}, \pi_{\text{inst}}$ : base and Instruct policies (Llama-3.1-8B variants).
- $\rho_i = \log \pi_{\text{inst}}(t_i) - \log \pi_{\text{base}}(t_i)$ : per-token leakage.
- $\bar\rho = T^{-1} \sum_i \rho_i$ : per-trajectory mean leakage.
- $F$ : audit space (square-integrable functionals on policy space).
- $F_{\text{ab}}$ : abelian audit class — order-invariant functionals.
- $F_{\text{ASD}}$ : ASD-derived audit class — order-dependent functionals.
- $F_{\text{aug}} = F_{\text{ab}} + F_{\text{ASD}}$ : augmented audit class.
- $\Xi$ : constraint subspace where RLHF distortion lives.
- $\Pi_N : \Xi \to \mathbb{R}^N$ : audit projection at audit budget $N$.
- $\dim(\ker \Pi_N)$ : audit-blind subspace dimension.
- $M$ : rank of $F_{\text{ASD}}$ on $\Xi$ (Phase 2's central numerical question).
- AUC(A), AUC(B), AUC(C) : achievable classifier AUC on Set A, B, C.
- (O-LM) : Phase 1's orthogonality claim.
- P2-1 through P2-5 : pre-registered pass criteria.
- F2-1 through F2-3 : pre-registered falsification triggers.

---

*MN-PHANTOM-001 v1.0 — May 2026.*
*Method note for FN-PHANTOM-002 §8.2 (Phase 2). Explains the mechanism by which the classifier comparison protocol measures the rank of the non-abelian audit class on the constraint subspace.*
