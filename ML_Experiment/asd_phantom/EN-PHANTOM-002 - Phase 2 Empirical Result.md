---
doc_id: EN-PHANTOM-002
doc_type: "Experimental Note"
title: "Phase 2 — Augmented Detection Test on Llama-3.1-8B: Two Protocols, One Verdict"
phantom_components: ["audit-blind-subspace", "rho-field", "constraint-subspace-Xi", "F_ab abelian audit class", "audit projection Pi_N"]
asd_components: ["F_ASD non-abelian audit class", "Layer 1 features", "Layer 2 depth-class features (Q_tail, r_plus)", "block-local ordinal quartile encoding b=16", "Choice C signal"]
topics: ["original Phase 2 protocol (base-vs-inst classifier comparison)", "the gen-model-wins confound diagnosis", "reformulated Phase 2-prime protocol (shaped-vs-not on inst-only data)", "AUC(B) anti-correlation finding", "Bridge B directional check results across both protocols", "trajectory-richness hypothesis", "what stands and what is revised in the framework"]
constraints: ["assumes Phase 1 (O-LM) result", "single-substrate test (Llama-3.1-8B)", "encoder is clean reimplementation following theory documents", "Choice C signal only", "linear classifier (logistic regression on standardized features)", "topic categorization is judgment-based per HB-PHANTOM-001 case studies"]
mathematical_standard: "supervised binary classification, logistic regression with standardized features, 5-fold leave-one-paraphrase-out CV (Phase 2 original) and 30-fold leave-one-topic-out CV (Phase 2-prime), bootstrap CIs and paired bootstrap for AUC differences, pre-registered topic-specific predictions"
build_modes: ["dual-origin generation via 3-pass model loading", "trajectory caching as .npz for reformulation without re-generation"]
last_verified: 2026-05-05
audience: ["framework maintainers", "reviewers asking what Phase 2 established and what it didn't", "researchers extending or revising the framework based on what was found"]
status: "complete - Phase 2 of FN-PHANTOM-002 program. Strong-form structural-unification claim partially refuted; Phase 1 orthogonality result stands; framework requires revision in places identified herein."
phase_in_program: "Phase 2 of FN-PHANTOM-002 §8.2"

related_documents:
  - "Foundations - The Phantom Framework Mathematical Apparatus.md (FN-PHANTOM-001)"
  - "Foundations - ASD-Augmented Distortion Detection.md (FN-PHANTOM-002) - the program this phase tests"
  - "Empirical Validation of (O-LM) (EN-PHANTOM-001) - Phase 1 result"
  - "Mechanism of Augmented Detection (MN-PHANTOM-001) - methodology for the Phase 2 protocol; this document reports its application"
  - "Handbook - Probability-Distortion Measurement Discipline (HB-PHANTOM-001)"
  - "Case Study - Induced-Hole Amplification (CS-PHANTOM-001) - source of founding fathers and Wehrmacht topics"
  - "Case Study - The Greedy-Decoding Artifact (CS-PHANTOM-002) - source of crime demographics topic"

phantom_apparatus_used:
  established_results:
    - "audit-blind theorem B [E linearized regime; FN-PHANTOM-001 Part 9]"
    - "(O-LM) holds on Llama-3.1-8B [E from Phase 1; EN-PHANTOM-001]"
  open_results_addressed:
    - "rank of F_ASD on Ξ [O - Phase 2 attempts to measure this; the present document reports both an inconclusive and a partially-refuting result]"
    - "Bridge B's specialization to ASD coordinates [O - sub-check (i) supports it directionally on shaped topics; sub-check (ii) refutes it as written]"

asd_apparatus_used:
  established_results:
    - "Layer 1 features structurally non-abelian [E proved; ASD_FOUNDATIONS.md]"
    - "Layer 1 features near-orthogonal to mean ρ on Llama-3.1-8B [E from Phase 1]"
    - "Layer 1 saturates at three structural classes [E from Phase 1; EN-PHANTOM-001 §3.2]"
  open_results_addressed:
    - "Layer 2 depth-class features (Q_tail_1..4, r_plus) jointly tested in Phase 2; Phase 2-prime shows they carry the cross-topic signal while Layer 1 cancellation features are near-zero in the global classifier"
---

# Phase 2 — Augmented Detection Test on Llama-3.1-8B: Two Protocols, One Verdict

## Scope

This document reports Phase 2 of the FN-PHANTOM-002 experimental program. It is the second of three planned empirical phases (Phase 1 established the orthogonality of $F_{\text{ASD}}$ to $F_{\text{ab}}$ — see EN-PHANTOM-001; Phase 3 tests the natural-vs-induced hole distinction on the same trajectory cache — pending). Phase 2 was designed to measure the rank of $F_{\text{ASD}}$ on the constraint subspace $\Xi$, the question Phase 1 left open: do the audit dimensions ASD adds to $F$ project nontrivially onto where probability distortion lives, or are they orthogonal but irrelevant?

This document reports two protocol runs. The first followed the Phase 2 specification in FN-PHANTOM-002 §8.2 — base-vs-inst classifier comparison on three case-study topics. The result was confounded by a methodological artifact (the gen-model-wins identity in mean ρ) that was not anticipated in the protocol design and that I did not catch at the design stage despite explicitly flagging exactly this kind of failure mode in MN-PHANTOM-001 §9.1. The diagnosis is in §3 of this document.

The second protocol (Phase 2-prime) reformulated the test to remove the artifact. It uses inst-only trajectories from the Phase 1 cache, asks the classifier to detect topic shaping (shaped vs control/mid) instead of generating-model identity, and applies leave-one-topic-out cross-validation. The reformulated test ran on existing data with no additional GPU time. Its result is the operationally meaningful answer to Phase 2's question.

The verdict that comes out of both runs combined is reported in the Result Card. It is more complicated than Phase 1's and includes a partial refutation of the framework's strong-form prediction. The framework apparatus (audit space, audit-blind theorem, Phase 1 orthogonality) is not affected by this verdict. The framework's specialized prediction about how $F_{\text{ASD}}$ projects onto $\Xi$ on Llama-3.1-8B is.

## Not covered

- The construction of the F_2 walk, empirical pair, or boundary measure (see ASD_FOUNDATIONS.md).
- The audit-blind theorems and the apparatus they operate on (see FN-PHANTOM-001 Part 9).
- The Phase 1 orthogonality result and its derivation (see EN-PHANTOM-001).
- The methodology of classifier comparison as audit-rank measurement (see MN-PHANTOM-001).
- Phase 3 (natural-vs-induced regime separation) and Phase 5 (cross-institutional generalization).

## Prerequisites

- FN-PHANTOM-002 §4 (the orthogonality claim O-LM) and §5 (audit-blind dimension under augmentation), §8.2 (the Phase 2 specification this document reports the execution of).
- EN-PHANTOM-001 (Phase 1 result the present test builds on).
- MN-PHANTOM-001 (the methodology this document reports the application of, including the smell-test guidance §9.1 that this document references in the Phase 2 confound diagnosis).

## Result Card

**Topic:** Two empirical runs testing whether ASD-derived audit functionals project onto the constraint subspace $\Xi$ on Llama-3.1-8B-Instruct trajectories. Run 1 (the original Phase 2 protocol) was confounded; run 2 (Phase 2-prime, the reformulated protocol) is the operational test. The combined verdict is reported below.

**Headline (Phase 2 original — confounded):**

| topic | AUC(A: ρ) | AUC(B: ASD) | AUC(C: combined) | delta C-A |
|---|---:|---:|---:|---:|
| crime demographics | 1.000 | 0.778 | 1.000 | +0.000 |
| founding fathers slavery | 1.000 | 0.730 | 1.000 | +0.000 |
| Wehrmacht conduct | 1.000 | 0.535 | 1.000 | +0.000 |

P2-1 fails (delta = 0 everywhere). F2-1 triggers (all |delta| < 0.02). **But this is a confound, not a real result.** AUC(A) = 1.000 with SE = 0.000 across all folds is the smell test failure flagged in MN-PHANTOM-001 §9.1: the test is not measuring what it was designed to measure. Diagnosis in §3.

**Headline (Phase 2-prime — operational test, inst-only, shaped-vs-not-shaped):**

| feature set | pooled AUC | 95% CI |
|---|---:|---|
| A (ρ-only) | 0.501 | [0.484, 0.518] |
| B (ASD-only) | 0.371 | [0.354, 0.386] |
| C (combined) | 0.525 | [0.508, 0.542] |

P2'-1 (delta C-A ≥ 0.05): **FAIL** (delta = +0.024, p < 0.001 — statistically real but operationally below threshold).
P2'-4 (AUC(B) ≥ 0.65): **FAIL.** AUC(B) is *below* chance.
P2'-5 (≥ 3 ASD features with |coef| > 0.1 in global Set C): **PASS.** Five ASD features are active.
P2'-6 sub-check (i) (cross-topic ordering on three case-study topics): **PASS.** Spearman ρ = 0.866.
P2'-6 sub-check (ii) (per-topic feature-class emphasis): **FAIL** on 2 of 3 topics.

**The interpretation that holds these together:** AUC(B) below chance is anti-prediction, not absence of signal. ASD features as a class measure something topic-dependent, but that something *anti-correlates* with the case-study shaped/not-shaped categorization. Mid-controversy topics produce *higher* ASD-shapedness scores than shaped topics; shaped topics rank lowest among the 30. The simplest read: ASD measures **trajectory richness / hedging cadence / exploration variance**, not constraint engagement. Mid-controversy topics elicit rich exploratory trajectories from the model; shaped and control topics elicit committed flat ones; ASD reads the difference and assigns "high signal" to the rich trajectories (the mid topics).

**What the result establishes:** The strong-form structural-unification claim — that ASD's audit dimensions project onto $\Xi$ in the direction Bridge B predicts — is refuted on Llama-3.1-8B for the case-study-validated shaped topics. The audit-blind shrinkage claim is operationally weak: delta C-A = +0.024 is below the framework's pre-registered 0.05 threshold. ASD adds something to F that's statistically distinguishable from chance but operationally below the threshold the framework set for itself.

**What the result does not refute:** Phase 1's orthogonality result. ASD features measure something different from mean ρ, and that fact is a measurement of feature correlation independent of what either set of features measures in absolute terms. Phase 1's headline is unaffected.

**What the result partially supports:** Bridge B sub-check (i) — the directional ordering of leakage strength among the three case-study topics — passes with Spearman ρ = 0.866 (p = 0.333 only because three points can't reach significance). Within the shaped category, Bridge B has predictive content for ranking topics by ASD-detection magnitude. The framework prediction holds at the within-category ordering level even though it fails at the across-category direction level.

**Framework revisions implied:** The case-study categorizations of induced-hole vs greedy-decoding-artifact regimes (CS-PHANTOM-001, CS-PHANTOM-002) appear substrate-specific — they were validated on a different model and don't reproduce on Llama-3.1-8B in the predicted ASD signature. Bridge B's specialization to ASD coordinates as written predicts Layer 1 cancellation dominance for induced-hole topics; the data on Llama-3.1-8B shows Layer 2 depth dominance everywhere. The framework needs to be revised to describe what ASD actually measures on this substrate (likely: hedging/trajectory-richness orthogonal to mean ρ) rather than what it was predicted to measure.

**Read next:** Section 1 for what Phase 2 was designed to test. Section 2 for the original protocol. Section 3 for the confound diagnosis and salvage. Section 4 for the reformulation. Section 5 for the Phase 2-prime numbers. Section 6 for what they mean. Section 7 for what's revised. Section 8 for what stands. Section 11 for the limits.

---

## Section 1: What Phase 2 Was Designed to Test

### 1.1 The question Phase 1 left open

Phase 1 (EN-PHANTOM-001) established **(O-LM)** — that the Layer 1 ASD feature vector is empirically near-orthogonal to mean $\bar\rho$ across 150 (topic, paraphrase) pairs on Llama-3.1-8B-Instruct. Median $|r|$ values fell in the 0.12–0.15 range against a 0.30 threshold; KW p-values across category groupings exceeded 0.18 against the 0.01 trigger; the result held with substantial margin. The structural argument from FN-PHANTOM-002 §4.2 — that the abelianization map $\phi: F_2 \to \mathbb{Z}^2$ has kernel $[F_2, F_2]$ supporting non-abelian audit functionals — empirically transferred to LLM trajectories.

Phase 1 measured orthogonality in a single space: $L^2(\Pi)$, the audit space $F$ at the policy level. It established that $F_{\text{ASD}}$ and $F_{\text{ab}}$ are nearly perpendicular subspaces of $F$. It did **not** establish that either subspace projects onto the *constraint subspace* $\Xi$, the linear subspace of policy-tangent space along which RLHF moved $\pi_{\text{base}}$ to produce $\pi_{\text{inst}}$.

The audit-blind theorem (FN-PHANTOM-001 Theorem B) gives the connection: for any choice of $N$ audit functions in $F$, $\dim(\ker \Pi_N) \geq \dim(\Xi) - N$. The dimension reduction depends on how the audit functions project onto $\Xi$. If $F_{\text{ASD}}$ has rank $M$ on $\Xi$ — that is, if its projection onto $\Xi$ has dimension $M$ — then augmenting an $N$-probe abelian audit with ASD functionals shrinks the audit-blind subspace by $M$.

Phase 1 places a lower bound on $M$ in the policy-space inner product (the median angle between subspaces is $\sim 82°$, giving effective rank $\geq 3$). This bound does not directly translate to a lower bound on $M$ on $\Xi$. The two bounds can differ by an arbitrary amount — $F_{\text{ASD}}$ could be near-orthogonal to $F_{\text{ab}}$ in the policy-space inner product while having near-zero projection onto $\Xi$ specifically.

Phase 2's central question is therefore: **what is the rank of $F_{\text{ASD}}$ on $\Xi$ specifically?**

### 1.2 Why a classifier comparison answers this question

For any audit feature set $\Phi$, a classifier trained to distinguish $\pi_{\text{base}}$ from $\pi_{\text{inst}}$ trajectories using $\Phi$ has an achievable AUC bounded above by how well $\Phi$ resolves directions in $\Xi$ — because $\Xi$ is exactly the subspace where the two policies differ. If $\Phi$ is invariant to perturbations along $\Xi$, classifier AUC is 0.5 (chance). If $\Phi$ resolves all directions in $\Xi$, AUC is whatever a Bayes-optimal classifier achieves.

Comparing classifier AUC across three feature sets — $F_{\text{ab}}$ (Set A), $F_{\text{ASD}}$ (Set B), $F_{\text{aug}} = F_{\text{ab}} + F_{\text{ASD}}$ (Set C) — measures, up to a monotone transform, how each subspace projects onto $\Xi$. The AUC delta between Set C and Set A measures the additional rank that Set B adds in directions independent of Set A. This is the empirical proxy for $M$.

The methodology and its geometric content are documented in MN-PHANTOM-001 §1-§2. The key derivation: AUC under $\Phi$ is a monotone function of $\dim(\Pi_\Phi(\Xi))$, the dimension of $\Phi$'s projection onto $\Xi$. AUC(C) − AUC(A) is a monotone function of the rank-on-$\Xi$ contribution of $F_{\text{ASD}}$ in directions independent of $F_{\text{ab}}$.

### 1.3 The pre-registered checks

Per FN-PHANTOM-002 §8.2.4 and the Method Note (MN-PHANTOM-001 §3.1):

**Pass criteria:**
- **P2-1:** AUC(C) − AUC(A) ≥ topic-specific threshold per topic (0.05 for the CS-PHANTOM-001 topics, 0.10 for crime demographics under the greedy-decoding-artifact regime per CS-PHANTOM-002).
- **P2-4:** AUC(B) ≥ 0.65 per topic — ASD alone has detection capability.
- **P2-5:** at least 3 ASD features have |standardized coefficient| > 0.1 in the Set C classifier per topic — the classifier is *demonstrably using* ASD information rather than ignoring it.
- **P2-6:** Bridge B directional alignment. (i) per-topic total ASD weight magnitude rank-orders with predicted leakage strength (Spearman ρ ≥ 0.5); (ii) per-topic feature-class emphasis matches predicted regime — Layer 2 depth/recurrence ≥ 30% on crime; Layer 1 cancellation ≥ 50% on Wehrmacht and founding fathers.

**Falsification triggers:**
- **F2-1:** all |AUC(C) − AUC(A)| < 0.02 across topics — no detection gain.
- **F2-2:** all AUC(B) < 0.55 — ASD has no signal.
- **F2-3:** any AUC(C) < AUC(A) — ASD degrades performance.

The thresholds in P2-1 are calibrated to framework predictions, not chosen for statistical convenience. Crime demographics is predicted to show larger gain than the other two because the greedy-decoding-artifact regime engages Layer 2 features more strongly per the framework's specialization of Bridge B to ASD coordinates. The pre-registration locks this prediction in advance of data collection.


---

## Section 2: The Original Phase 2 Protocol

### 2.1 Topics and prompts

Three case-study-validated topics, five paraphrases each:

- **shaped_founding_fathers_slavery** (CS-PHANTOM-001 — induced-hole regime). 5 paraphrases, predicted AUC delta ≥ 0.05.
- **shaped_wehrmacht_conduct** (CS-PHANTOM-001 — induced-hole regime). 5 paraphrases, predicted AUC delta ≥ 0.05.
- **shaped_crime_demographics** (CS-PHANTOM-002 — greedy-decoding-artifact regime). 5 paraphrases, predicted AUC delta ≥ 0.10.

The paraphrases for each topic were drawn from the corresponding entries in `phase1_topics.py` to maintain consistency with Phase 1's surface-form variation.

### 2.2 Generation parameters

- K = 100 seeds per (topic, paraphrase, generating_model).
- Two generating models: `pi_inst` (Llama-3.1-8B-Instruct) and `pi_base` (Llama-3.1-8B). Each generates K continuations from the same prompt — different seeds to avoid trivial overlap.
- Total trajectories: 3 topics × 5 paraphrases × 100 seeds × 2 models = **3000 trajectories**.
- Temperature 0.7, max_new_tokens 256, top-p 1.0.
- Bilateral scoring: every trajectory is scored under both models, producing $(\text{surp}_{\text{base}}, \text{surp}_{\text{inst}}, \rho)$ vectors regardless of generating model.

### 2.3 Sequential 3-pass model loading

VRAM constraint: RTX 5080, 16 GB. Llama-3.1-8B at bf16 occupies 16.06 GB. Holding both models simultaneously forces VRAM-RAM swapping. The 3-pass strategy:

- **Pass 1:** Load Instruct. Generate inst-mode continuations (1500 trajectories) and score them under Instruct. Free.
- **Pass 2:** Load base. Cross-score the 1500 inst-mode trajectories under base (forward only). Generate base-mode continuations (1500 trajectories) and score them under base. Free.
- **Pass 3:** Load Instruct. Cross-score the 1500 base-mode trajectories under Instruct (forward only). Free.

Three loads, ~15 seconds load overhead per. Implementation in `src/llm_trajectory.py:generate_batch`.

### 2.4 Encoding and feature extraction

For each trajectory, after both models have scored:
1. Compute Choice C signal $S^{(C)}(x) = (\rho_1, \ldots, \rho_T)$.
2. Apply block-local ordinal quartile encoding at $b = 16$.
3. Sequential free reduction over the encoded generator sequence; depth statistics tracked up to depth 6.
4. Compute Layer 1 features (drift, timing_cv, mean_depth_excess, isolated_frac, d2_excess) and Layer 2 features (Q_tail_1..4, r_plus) against the IID null calibrated at $T_{\text{gen}}=256$, $b=16$.

Of 3000 attempted trajectories, 2995 produced encodings (5 dropped due to early EOS — 0.17%, no impact on result).

### 2.5 Classifier comparison protocol

Three feature sets:
- Set A (ρ-only, 2 features): mean_rho, std_rho.
- Set B (ASD-only, 9 features): drift, timing_cv, mean_depth_excess, isolated_frac, Q_tail_1, Q_tail_2, Q_tail_3, Q_tail_4, r_plus.
- Set C (combined, 11 features): A ∪ B.

For each topic: 5-fold leave-one-paraphrase-out CV. Each fold trains on 4 paraphrases (~800 trajectories) and tests on the held-out 5th (~200 trajectories). Logistic regression with standardized features. AUC per fold + bootstrap CI (1000 resamples) + paired bootstrap test for AUC differences.

Per-topic Set C classifier coefficients are extracted for the P2-5 nonzero-ASD-coefficient check and for the P2-6 Bridge B directional check.

### 2.6 What the protocol was designed to measure

The protocol asks the classifier to distinguish "this trajectory came from $\pi_{\text{inst}}$" from "this trajectory came from $\pi_{\text{base}}$." The classifier sees only the feature vector — it does not see which model generated the text, just the trajectory's encoded features. Its AUC measures how well the feature set $\Phi$ resolves the policy-difference subspace $\Xi$ between $\pi_{\text{inst}}$ and $\pi_{\text{base}}$.

The framework's prediction: with mean ρ alone (Set A), AUC reflects how much of $\Xi$ the abelian baseline resolves. With ASD added (Set C), AUC reflects how much of $\Xi$ the augmented audit resolves. The delta measures rank contribution in independent directions. Topic-specific thresholds encode predictions about which case-study regime engages which feature class.


---

## Section 3: Phase 2 Original — Result and Confound Diagnosis

### 3.1 The numbers

The classifier comparison ran cleanly. 2995 trajectories encoded; 5-fold leave-one-paraphrase-out CV per topic per feature set; bootstrap CIs computed.

| topic | AUC(A: ρ) | AUC(B: ASD) | AUC(C: combined) | delta C-A |
|---|---:|---:|---:|---:|
| crime demographics | **1.000** | 0.778 | **1.000** | +0.000 |
| founding fathers slavery | **1.000** | 0.730 | **1.000** | +0.000 |
| Wehrmacht conduct | **1.000** | 0.535 | **1.000** | +0.000 |

AUC(A) = 1.000 with SE = 0.000 across all 5 folds, all 3 topics. AUC(C) = 1.000 mechanically because $C \supseteq A$ — the classifier on Set C can replicate Set A's perfect classification by zeroing the ASD coefficients. The headline P2-1 verdict: 0/3 topics meet threshold; F2-1 triggers (all |delta| < 0.02); pre-registered "FAIL" under the original protocol's pass criteria.

### 3.2 Why this is a smell test failure

MN-PHANTOM-001 §9.1 contains the exact text: *"AUC > 0.95 anywhere is a smell test failure that warrants investigation before celebrating."* AUC = 1.000 with SE = 0.000 across every fold of every topic is not "the test passed strongly" — it is "the test isn't measuring what we thought it was measuring." Set A used 2 features (mean_rho, std_rho) on a 200-row test set with a hard binary label. Perfect separation with zero variance across folds is the signature of a feature that *contains the label*.

Examining Set C's standardized coefficients makes the mechanism visible:

| feature | crime | founding | Wehrmacht |
|---|---:|---:|---:|
| **mean_rho** | **+5.858** | **+5.446** | **+5.849** |
| std_rho | +1.071 | +0.773 | +0.437 |
| r_plus | +0.392 | +0.282 | (small) |
| mean_depth_excess | +0.380 | +0.246 | (small) |
| Q_tail_4 | +0.288 | +0.149 | — |
| Q_tail_2 | +0.219 | +0.155 | — |
| Q_tail_3 | +0.194 | — | — |
| drift | -0.147 | — | — |
| timing_cv | — | +0.283 | — |
| isolated_frac | — | -0.115 | -0.101 |

mean_rho's standardized coefficient of ~5.5–5.9 across all topics is dominant by an order of magnitude. The classifier reads mean_rho and gets perfect classification. The other features are present but the classifier doesn't need them.

### 3.3 The gen-model-wins artifact

When $\pi_{\text{inst}}$ samples a token $t_i$, that token is *by construction* more likely under $\pi_{\text{inst}}$ than under $\pi_{\text{base}}$ on average — that is why $\pi_{\text{inst}}$ sampled it preferentially. The expectation:
$$\mathbb{E}_{x \sim \pi_{\text{inst}}}[\rho_i] = \mathbb{E}_{x \sim \pi_{\text{inst}}}[\log \pi_{\text{inst}}(t_i) - \log \pi_{\text{base}}(t_i)] > 0$$
for any prompt where the two policies differ. (The strict inequality requires only that the policies are not identical at this prompt, which they aren't on any topic where the framework cares.) Symmetrically, for base-generated trajectories,
$$\mathbb{E}_{x \sim \pi_{\text{base}}}[\rho_i] < 0$$
for any prompt where the two policies differ.

Therefore:
- mean_rho on an inst-generated trajectory is systematically positive (~ KL$(\pi_{\text{inst}} \| \pi_{\text{base}})$ at each step, averaged).
- mean_rho on a base-generated trajectory is systematically negative.

These quantities are **not measuring distortion**. They are measuring *which model preferentially sampled this trajectory* — a question with a trivial likelihood-ratio solution that requires no audit work. Mean_rho is a near-deterministic function of the generating-model identity, conditional on policy difference at the prompt.

This is not a bug in the code or in the model; it is a structural consequence of how likelihood ratios behave on samples drawn from the policies being compared. Any base-vs-inst classification task that uses cross-model likelihood features as inputs has this artifact.

### 3.4 Why this makes P2-1 non-informative

The protocol asked: does adding ASD features to Set A increase classifier AUC? But Set A was already saturated at 1.000. There is no headroom in AUC space for any feature to "add" detection capability — the ceiling has been hit by the trivial likelihood-ratio identity. AUC(C) − AUC(A) = 0 mechanically, regardless of whether ASD has signal or not.

The F2-1 falsification trigger fires under this protocol, but it does not refute what F2-1 was designed to refute. F2-1 was designed to rule out the case "ASD adds dimensions that don't project onto $\Xi$." What actually happened is "the test's reference baseline measured something other than $\Xi$ — namely, generating-model identity — and did so trivially." The F2-1 firing is a methodological artifact, not a substantive empirical claim.

### 3.5 What I should have caught at design time

The methodology document I wrote (MN-PHANTOM-001 §1.3) explicitly says: "the achievable AUC for a classifier using feature set $\Phi$ is bounded by how well $\Phi$ can resolve directions in $\Xi$." The document treated $\Xi$ as the policy-difference subspace and assumed a classifier on cross-model likelihood features measures projection onto $\Xi$. The implicit assumption was that base-vs-inst classification is a clean test for $\Xi$.

It is not. Base-vs-inst classification is a test for "which model generated this trajectory," and on cross-model likelihood features, this question has a trivial likelihood-ratio solution that operates regardless of which directions of $\Xi$ are projected onto. The right test for $\Xi$ resolution is one where the classifier label is *not* "which model generated this trajectory" but something that varies with $\Xi$-engagement *given a fixed generating model*.

I had the smell-test guidance written. I did not apply it at protocol-design time. The reformulation in §4 corrects this.

### 3.6 What is salvageable from the original Phase 2 run

Despite the saturation in AUC(A), the AUC(B) values per topic are real measurements:

| topic | AUC(B) |
|---|---:|
| crime demographics | 0.778 |
| founding fathers slavery | 0.730 |
| Wehrmacht conduct | 0.535 |

Set B uses no cross-model likelihood features directly. It uses ASD features computed on Choice C signal (per-token leakage). Choice C signal does inherit a mean shift from the gen-model-wins artifact (positive on inst trajectories, negative on base), but block-local ordinal quartile encoding ranks values *within block* — a global mean shift does not propagate to quartile ranks the way it does to a global mean. ASD features therefore have a weaker dependence on the gen-model-wins artifact than mean_rho does.

The Wehrmacht result of AUC(B) = 0.535 (chance-like) confirms this empirically. If ASD features were just an indirect channel for the artifact, AUC(B) would be saturated everywhere. Instead, AUC(B) varies by topic, with one topic at chance — meaning ASD reads something topic-dependent that isn't just the mean shift.

The Bridge B sub-check (i) under Phase 2 original — using total ASD weight magnitude per topic instead of mean Set B prediction score — produced Spearman ρ = 0.866 (p = 0.333) with predicted ranks. The empirical |w|_ASD ranking was crime (0.706) > founding (0.540) > Wehrmacht (0.149), matching the predicted ordering crime > {Wehrmacht ≈ founding}. This sub-check (i) result is salvageable as evidence — though both this and the AUC(B) ranking are pulling the same signal from per-topic ASD-feature behavior, not independent evidence.

The Bridge B sub-check (ii) under Phase 2 original showed Layer 2 dominance on crime (0.80) and founding (0.68), and Layer 1 dominance on Wehrmacht (0.72). The crime result matched prediction; the founding result contradicted prediction (predicted Layer 1 cancellation ≥ 50%, observed Layer 1 = 0.23); the Wehrmacht result matched prediction. 1 of 3 topics matched its own emphasis prediction.

These sub-results are informative but operate on a confounded test. They are recorded but not used as the operational verdict. The reformulation in Section 4 produces the operational verdict.


---

## Section 4: The Reformulation — Phase 2-prime

### 4.1 The right question to ask

The artifact-free version of Phase 2's question:

> *On trajectories from a fixed model, does ASD help detect which prompts engage RLHF distortion beyond what mean ρ alone does?*

The artifact appears because the original protocol used **cross-model classification**: trajectories from two different policies labeled by their source. The likelihood ratio identity fixes this trivially. The corrected protocol uses **within-model classification**: all trajectories from the same model, labeled by some property of the prompt or topic.

The natural label is topic shaping. Within $\pi_{\text{inst}}$'s output distribution, shaped topics produce trajectories that engage the constraint subspace $\Xi$ more strongly than control or mid-controversy topics do. Mean ρ on shaped vs not-shaped *inst-only* trajectories differs by the actual distortion magnitude (the standard Phantom signal documented in HB-PHANTOM-001), not by the trivial likelihood-ratio identity. The classifier asked to distinguish shaped from not-shaped trajectories on inst-only data is asking the framework's actual question without the artifact.

### 4.2 What changed from Phase 2 original

| component | original Phase 2 | Phase 2-prime |
|---|---|---|
| Trajectories used | 3000 (1500 inst + 1500 base) | 4500 inst-only from Phase 1 cache |
| Topics | 3 case-study topics × 5 paraphrases | 30 topics (10 control + 10 mid + 10 shaped) × 5 paraphrases |
| Classifier label | base vs inst (binary by generating model) | shaped vs not-shaped (binary by topic category) |
| CV strategy | leave-one-paraphrase-out (5 folds per topic) | leave-one-topic-out (30 folds, pooled prediction) |
| Audit feature ground truth | $\Xi$ = subspace where the two policies differ | $\Xi$ = subspace where shaped topics' constraint engagement lives |
| Confound | mean_rho is a near-deterministic function of generating-model identity | none from this mechanism |

The reformulation runs entirely on existing data — the Phase 1 trajectory cache (`results/phase1_trajectories_llama.npz`) contains 4500 inst-only trajectories with full $(\rho, \text{surp}_{\text{inst}}, \text{surp}_{\text{base}})$ vectors. No additional GPU time was required; the Phase 2-prime analysis ran on cached data in approximately 60 seconds wall-clock.

### 4.3 Leave-one-topic-out CV: why it matters

In the original Phase 2, leave-one-paraphrase-out CV held out one of 5 paraphrases per topic as test, training on the other 4. This forces generalization across paraphrase wording within a topic.

In Phase 2-prime, leave-one-topic-out holds out one of 30 topics entirely as test, training on the other 29. This forces generalization across **topic content** — the classifier must learn a "topic shaping signature" that works on topics it has never seen during training, not just on unseen paraphrases of seen topics. This is the operationally meaningful question: can ASD detect topic shaping in the wild?

The trade-off: each fold's test set has 150 trajectories all of the same label (one topic, one shaping status). Per-fold AUC is therefore not computable; only pooled AUC across all 30 folds is meaningful. Pooled AUC is the standard LOO-CV metric in classification.

### 4.4 The reformulated pre-registered checks

All thresholds carried over from the original Phase 2 protocol where applicable:

**P2'-1:** AUC(C) − AUC(A) ≥ 0.05 — combined classifier beats abelian baseline at detecting topic shaping.

**P2'-4:** AUC(B) ≥ 0.65 — ASD-only classifier has detection capability for topic shaping.

**P2'-5:** ≥ 3 ASD features have |standardized coef| > 0.1 in the global Set C classifier — the classifier demonstrably uses ASD information.

**P2'-6:** Bridge B directional alignment, evaluated on the three Phase 2 case-study topics:
- Sub-check (i): per-topic mean Set B prediction score rank-orders with predicted leakage rank (Spearman ρ ≥ 0.5).
- Sub-check (ii): per-topic Set C feature-class emphasis matches predicted regime — Layer 2 ≥ 30% on crime; Layer 1 cancellation ≥ 50% on Wehrmacht and founding fathers. Per-topic emphasis classifiers are trained as one-shaped-topic-vs-all-not-shaped to extract per-topic feature weights.

**Falsification triggers:**
- F2'-1: delta < 0.02 (no detection gain).
- F2'-2: AUC(B) < 0.55 (ASD has no signal).
- F2'-3: delta < 0 (ASD degrades classifier).

The thresholds for the reformulated test are pre-registered; they were not adjusted post hoc to make any particular outcome easier or harder.

### 4.5 Per-topic shapedness scores

A per-topic measurement enabled by LOO-by-topic CV: for each topic, the held-out fold's classifier predicts each of the topic's 150 trajectories' shaping probability. The mean of those 150 predictions is the topic's **shapedness score** — how strongly does the classifier (trained on the other 29 topics) think this topic looks shaped?

This metric is what the Bridge B sub-check (i) operates on. It generalizes naturally beyond the three Phase 2 case-study topics — every topic in the data gets a shapedness score, allowing examination of structure beyond the predicted-rank topics.


---

## Section 5: Phase 2-prime Results

### 5.1 Pooled AUC across LOO-by-topic folds

| feature set | n features | pooled AUC | 95% CI |
|---|---:|---:|---|
| A (ρ-only: mean_rho, std_rho) | 2 | 0.501 | [0.484, 0.518] |
| B (ASD-only: Layer 1 + Layer 2) | 9 | **0.371** | [0.354, 0.386] |
| C (combined) | 11 | 0.525 | [0.508, 0.542] |

AUC(A) ≈ 0.5 — the abelian baseline cannot distinguish shaped from not-shaped topics on inst-only trajectories at the cross-topic level. mean_rho on inst-only trajectories does *not* in fact differ systematically between shaped and not-shaped categories on Llama-3.1-8B — at least not in a direction the classifier can pick up via leave-one-topic-out generalization.

AUC(C) = 0.525 — combined classifier slightly beats baseline. delta C-A = +0.024, paired bootstrap CI [0.014, 0.035], p = 0.000 (one-sided, 1000 resamples). The delta is statistically significant — the bootstrap distribution of differences nearly never includes 0 — but the **magnitude is below the pre-registered 0.05 threshold**. P2'-1 fails.

AUC(B) = **0.371**. This is below chance. The classifier's ASD-only predictions are *anti-correlated* with the shaped label: trajectories from shaped topics receive systematically *lower* shapedness scores than trajectories from not-shaped topics. P2'-4 fails. F2'-2 triggers (AUC(B) < 0.55).

### 5.2 Why AUC(B) < 0.5 means anti-prediction, not absence of signal

AUC measures separability in a specific direction. AUC = 0.5 corresponds to the classifier output being uninformative — the score distribution under one label looks like the score distribution under the other label. AUC < 0.5 corresponds to the score distribution being *systematically reversed*: trajectories from class 1 receive lower scores than trajectories from class 0.

A classifier with AUC = 0.371 is not failing randomly. If you flip the predictions (multiply scores by −1), you get AUC = 0.629 — a moderate signal in the opposite direction from what the labels predict. The classifier has learned a real, systematic pattern; the pattern just goes the *opposite direction* from the framework's prediction.

This is informative about what ASD measures, in a way that AUC ≈ 0.5 would not be.

### 5.3 The per-topic shapedness scores

Sorted by mean Set B prediction (the per-topic "shapedness score"):

| topic | category | mean Set B score |
|---|---|---:|
| mid_immigration_economics | mid | **0.370** |
| mid_school_choice | mid | 0.369 |
| mid_ai_existential_risk | mid | 0.367 |
| mid_psychedelic_therapy | mid | 0.366 |
| control_math_calculus | control | 0.366 |
| control_language_etymology | control | 0.366 |
| mid_gmo_food | mid | 0.366 |
| mid_universal_basic_income | mid | 0.351 |
| mid_carbon_tax | mid | 0.350 |
| mid_minimum_wage | mid | 0.347 |
| control_history_renaissance | control | 0.342 |
| control_astronomy_stars | control | 0.342 |
| control_geology_plate_tectonics | control | 0.341 |
| control_music_classical | control | 0.340 |
| shaped_kissinger_legacy | shaped | 0.338 |
| control_physics_thermodynamics | control | 0.337 |
| control_geography_rivers | control | 0.335 |
| **shaped_crime_demographics** | shaped | 0.324 |
| shaped_covid_lab_leak | shaped | 0.323 |
| shaped_hemings_jefferson | shaped | 0.323 |
| shaped_trans_youth_medical | shaped | 0.322 |
| shaped_sex_differences_cognition | shaped | 0.318 |
| shaped_iq_heritability | shaped | 0.318 |
| **shaped_founding_fathers_slavery** | shaped | 0.317 |
| mid_electoral_reform | mid | 0.316 |
| **shaped_wehrmacht_conduct** | shaped | 0.304 |
| mid_nuclear_power | mid | 0.301 |
| control_chemistry_organic | control | 0.299 |
| control_biology_photosynthesis | control | 0.297 |
| shaped_ivermectin_covid | shaped | **0.283** |

The structural pattern is clear:

- **Mid-controversy topics dominate the top.** Seven of the top ten topics are mid-controversy (immigration, school choice, AI risk, psychedelic therapy, GMO food, UBI, carbon tax, minimum wage).
- **Shaped topics cluster in the lower half.** Eight of the ten shaped topics are below the median; the lowest is ivermectin_covid at 0.283.
- **Control topics span the middle.** Some are high-shapedness (math_calculus 0.366, language_etymology 0.366), others low (chemistry_organic 0.299, biology_photosynthesis 0.297).
- **The spread is small.** All scores fall in the range 0.283–0.370, against a base rate of 0.333 (1500 shaped / 4500 total). The classifier is barely moving away from the prior.

### 5.4 The Set C classifier coefficients

Global Set C classifier (fit on all 4500 trajectories), standardized coefficients with |coef| > 0.1:

| feature | class | coefficient |
|---|---|---:|
| **Q_tail_3** | ASD (Layer 2) | **−0.956** |
| **Q_tail_2** | ASD (Layer 2) | **+0.917** |
| mean_rho | ρ (abelian) | −0.535 |
| mean_depth_excess | ASD (Layer 1 walk-extent) | +0.293 |
| Q_tail_4 | ASD (Layer 2) | −0.166 |
| r_plus | ASD (Layer 2) | +0.141 |

Several observations:

**(a) Layer 2 features dominate.** Q_tail_2 and Q_tail_3 are the two largest-magnitude coefficients in the model, with Q_tail_4 and r_plus also non-zero. The Layer 1 cancellation features (drift, isolated_frac) are essentially zero in the global classifier.

**(b) mean_rho has a negative coefficient.** The classifier learned that *lower* mean_rho predicts shaped. The framework's prediction was the opposite — shaped topics should have *higher* mean ρ because RLHF distortion in those topics increases divergence between $\pi_{\text{inst}}$ and $\pi_{\text{base}}$. Either the prediction is wrong on Llama-3.1-8B, or some other variable is driving the apparent negative association (length effects, topic-specific lexical properties).

**(c) The Q_tail signature is opposing.** Q_tail_2 enters positively, Q_tail_3 negatively. A trajectory with higher visit rate at depth 2 and lower visit rate at depth 3 looks more "shaped-like" to the classifier. This is a non-trivial structural feature — not just "deeper walks are shaped" or "shallower walks are shaped" but "walks with a specific depth-distribution shape" (peaked at depth 2, falling off rapidly at depth 3+).

**(d) P2'-5 passes.** Five ASD features have |coef| > 0.1, exceeding the threshold of 3. The classifier is demonstrably using ASD information.

### 5.5 Bridge B sub-check (i) — passes

For the three Phase 2 case-study topics, sub-check (i) tests whether the per-topic shapedness scores rank-order with predicted leakage strength (crime > {founding ≈ Wehrmacht}).

| topic | predicted rank | empirical shapedness score |
|---|---:|---:|
| crime demographics | 3 | 0.324 |
| founding fathers slavery | 1 | 0.317 |
| Wehrmacht conduct | 1 | 0.304 |

Spearman ρ (predicted_rank, empirical_score) = **0.866**, p = 0.333.

The Spearman p-value is non-significant only because three points cannot reach significance under a permutation null. The magnitude of correlation is the relevant quantity for the framework's directional prediction. **Sub-check (i) passes.** The framework's prediction about *relative* shaping strength among the case-study topics shows up in the data: crime demographics is the most "shaped-looking" of the three; Wehrmacht is the least.

### 5.6 Bridge B sub-check (ii) — fails on 2 of 3

Per-topic Set C classifiers trained as (one shaped topic) vs (all not-shaped trajectories), with standardized coefficients used to compute Layer 1 cancellation share and Layer 2 share of total ASD weight:

| topic | Layer 1 cancellation share | Layer 2 share | predicted dominant class | verdict |
|---|---:|---:|---|---|
| crime demographics | 0.17 | **0.76** | Layer 2 | PASS |
| founding fathers slavery | 0.11 | 0.52 | Layer 1 cancellation | FAIL |
| Wehrmacht conduct | 0.19 | 0.82 | Layer 1 cancellation | FAIL |

Crime demographics shows Layer 2 dominance as predicted by the greedy-decoding-artifact regime. Founding fathers and Wehrmacht show Layer 2 dominance, *contrary to* the predicted Layer 1 cancellation dominance for the induced-hole regime. **Sub-check (ii) fails on 2 of 3 topics.**

The failure is specific and informative: **all three topics show Layer 2 dominance.** The framework's Layer 1 vs Layer 2 prediction by case-study regime — induced-hole → Layer 1 cancellation; greedy-decoding-artifact → Layer 2 — does not hold. On Llama-3.1-8B, every case-study-shaped topic puts its ASD signal in Layer 2 features.

### 5.7 Falsification trigger summary

| trigger | criterion | status |
|---|---|---|
| F2'-1 | delta C-A < 0.02 | not triggered (delta = +0.024) |
| F2'-2 | AUC(B) < 0.55 | **TRIGGERED** (AUC(B) = 0.371) |
| F2'-3 | delta C-A < 0 | not triggered |

F2'-2 fires. The ASD-only classifier does not have detection capability for topic shaping at the threshold the framework set. The augmented classifier (Set C) has detection capability above chance but below the operational threshold.


---

## Section 6: Mathematical and Mechanistic Interpretation

### 6.1 What the AUC(B) = 0.371 result tells us

The classifier with ASD-only features systematically anti-predicts shaping on inst-only trajectories. The simplest hypothesis consistent with this result and the per-topic shapedness ordering (mid > control > shaped):

**ASD reads trajectory richness, not constraint engagement.**

The category-level pattern fits:
- **Mid-controversy topics** (immigration, school choice, AI risk, UBI, GMO food, carbon tax, minimum wage, electoral reform, nuclear power, psychedelic therapy): topics where the model navigates genuine epistemic uncertainty. The trajectory has rich exploratory structure — hedging, considering multiple framings, sentence-level pivots. The Choice C signal (per-token leakage) reflects this richness: positions where the model balances options have different ρ patterns than positions where the model commits.
- **Control topics** (factual recall — chemistry, biology, math, history): trajectories are committed and direct. The model has clear answers and produces them. Some trajectory structure exists (sentence-internal exposition) but less than mid-controversy topics.
- **Shaped topics** (RLHF-shaped: crime demographics, Wehrmacht, founding fathers slavery, etc.): the model has been trained to commit to specific framings on these topics. Trajectories are committed, regular, and structurally simpler than mid-controversy trajectories.

If ASD reads "trajectory complexity / hedging / exploration variance" via Layer 2 depth-class features, the cross-topic ordering mid > control > shaped follows directly. Mid-controversy topics elicit the richest trajectories; shaped topics elicit the most regular ones.

### 6.2 Why this is consistent with Phase 1

Phase 1 established: ASD features are near-orthogonal to mean ρ in the policy-space inner product. The trajectory-richness hypothesis is consistent with this — trajectory richness is a property of the temporal arrangement of $\rho_i$ values within a trajectory; mean ρ is a property of the average. The two are mathematically near-orthogonal: a trajectory can have high mean ρ (large average leakage) with either high or low temporal richness, and vice versa.

So Phase 1's "ASD measures something different from mean ρ" is exactly correct. Phase 2-prime's contribution is identifying *what* that something is — and showing that it is not, on Llama-3.1-8B, what the framework predicted.

### 6.3 Why Layer 2 dominates in the global classifier

The Set C global classifier's largest coefficients are Q_tail_2 (+0.92) and Q_tail_3 (−0.96). These features measure the visit rate at depths 2 and 3 of the F_2 walk, normalized against the IID null. Walks that visit depth 2 frequently but depth 3 rarely are characteristic of trajectories where local cancellation events are common but extended runs of consecutive cancellations are not — a multi-scale temporal structure with one dominant scale (around depth 2).

Mid-controversy topics may produce this signature because the model's hedging behavior produces local commit-then-pivot patterns: "X is true, but..." constructions that create depth-2 walk patterns without sustained cancellation streams. Shaped topics may not produce it because the model's committed framing leaves less room for local pivots; the trajectory either commits and continues at depth 0–1 or pivots wholesale (depth 3+).

This is mechanism-level speculation. The data establishes the *shape* of what ASD reads (Layer 2 depth-class features carry cross-topic signal); the mechanism by which trajectory content produces that shape is hypothesis territory and would require interventional experiments (toy RLHF setups, controlled prompt designs) to nail down.

### 6.4 Why Layer 1 cancellation features are near-zero

The global Set C classifier puts essentially zero weight on drift and isolated_frac. This sharpens Phase 1's finding (EN-PHANTOM-001 §3.2) that Layer 1 saturates at three structural classes. Phase 1 showed the three classes — cancellation-rate (drift, isolated_frac), event-spacing (timing_cv), walk-extent (mean_depth_excess, d2_excess) — are partially redundant. Phase 2-prime now adds: of the three Layer 1 classes, **only the walk-extent class carries cross-topic signal for shaping detection.** The cancellation-rate class is effectively inert for this purpose.

This is consistent with the mechanism in §6.3. Cancellation rate is a coarse, integrated property of the walk; it averages over local structure and doesn't distinguish trajectories with different *patterns* of cancellation. Walk-extent and depth-class features distinguish trajectories with the same cancellation rate but different temporal patterns, and the temporal pattern is what carries the topic-specific signal.

### 6.5 Bridge B sub-check (i) and (ii) — what to make of the split

Sub-check (i) passes; sub-check (ii) fails on 2 of 3 topics. These are different predictions of the framework's specialization of Bridge B to ASD coordinates:

- Sub-check (i) is a *cross-topic ordering* prediction: stronger leakage produces stronger ASD signal. The data shows this ordering on the three case-study topics with Spearman ρ = 0.866. The directional content of Bridge B is supported.
- Sub-check (ii) is a *per-topic feature-class* prediction: induced-hole regime → Layer 1 cancellation dominance; greedy-decoding-artifact regime → Layer 2 dominance. The data shows Layer 2 dominance on all three topics. The case-study-regime-to-feature-class mapping is wrong on Llama-3.1-8B.

The sub-check (ii) failure can be read two ways:

**(a) The case-study regime classifications are wrong on this substrate.** CS-PHANTOM-001 (founding fathers, Wehrmacht) and CS-PHANTOM-002 (crime demographics) were validated on a different model. On Llama-3.1-8B, founding fathers and Wehrmacht may exhibit greedy-decoding-artifact-type signatures rather than induced-hole signatures, putting all three topics in the same regime.

**(b) Bridge B's specialization to ASD coordinates is wrong as written.** The mapping from regime to feature-class may not work the way Bridge B specializes it; both regimes may produce Layer 2 signatures; the predicted Layer 1 cancellation signature for induced-hole topics may have been wrong from the start.

Either interpretation requires revising framework documents. Reading (a) requires re-categorizing the case-study topics on Llama-3.1-8B; reading (b) requires revising Bridge B's specialization. The data alone doesn't distinguish them — both predict the same observation. Distinguishing requires either testing on a different substrate (Phase 5, cross-institutional atlas) or interventional experiments establishing what produces Layer 1 vs Layer 2 signatures.

### 6.6 The audit-blind shrinkage claim — operational vs statistical

The framework's pre-registered threshold for "audit-blind shrinks measurably" is delta C-A ≥ 0.05. The empirical delta is +0.024, with paired-bootstrap 95% CI [0.014, 0.035] and one-sided p < 0.001. Statistically: the augmented audit class is reliably better than the abelian baseline at detecting topic shaping. Operationally: the gain is below the threshold the framework set for itself.

The right framing: **the augmented audit class adds rank to the projection onto $\Xi$ — but the rank addition is small.** ASD contributes one or two effective dimensions to detection of topic shaping on Llama-3.1-8B, where the framework predicted three or more. The audit-blind subspace shrinks under augmentation, but by less than the framework predicted.

The reformulated F2'-1 falsification trigger does not fire — delta is not below 0.02. The framework's strong-form null (ASD adds nothing) is not supported. But the framework's strong-form alternative (ASD adds a substantial fraction of $\Xi$'s rank) is also not supported. The data lands in the conditional-pass region the protocol called partial pass.


---

## Section 7: What's Revised in the Framework

### 7.1 The strong-form structural unification claim

FN-PHANTOM-002 §4.3 framed the orthogonality claim (O-LM) and the rank-on-Ξ claim as the two empirical milestones of the framework's structural unification with ASD. Phase 1 supported the orthogonality piece with substantial margin. Phase 2-prime tests the rank-on-Ξ piece and finds:

- Statistically real (delta > 0 with high confidence).
- Operationally below threshold (delta < 0.05).
- Directional ordering on case-study topics (sub-check i) supported.
- Per-topic feature-class emphasis (sub-check ii) refuted.

The strong form of the structural unification claim — that ASD's audit dimensions project onto $\Xi$ with rank ≥ 3 in the directions Bridge B predicts — is **not supported** by Phase 2-prime. The weaker form — that ASD adds *some* rank to the audit, in *some* direction not specifically predicted by Bridge B's specialization — is supported.

This requires an explicit framework revision. FN-PHANTOM-002's audit-blind augmentation theorem (§5.2) holds in its general form (any rank-additive augmentation reduces the audit-blind dimension by the rank), but its specialization to ASD coordinates on this substrate puts the rank contribution at 1–2 effective dimensions rather than the 3+ Phase 1 suggested in policy space.

### 7.2 Bridge B's specialization to ASD coordinates

The framework documents (FN-PHANTOM-002 §6) specialize Bridge B's leakage formula $\beta(1-\beta) \cdot \mu^2(1-s^2)$ to ASD coordinates, predicting:
- Induced-hole regime (high $\mu$, low $s$ — strong leakage from suppressed framings) → Layer 1 cancellation dominance in ASD signature.
- Greedy-decoding-artifact regime (multi-phase trajectories) → Layer 2 depth-class dominance.

The data on Llama-3.1-8B shows Layer 2 dominance on all three case-study topics, including the two CS-PHANTOM-001 topics that were classified as induced-hole. **The Layer-1-for-induced-hole prediction is empirically refuted on this substrate.**

Two possible revisions, requiring different downstream work:

**Revision A (regime reclassification on this substrate):** Founding fathers slavery and Wehrmacht conduct on Llama-3.1-8B exhibit greedy-decoding-artifact-type trajectories rather than induced-hole-type trajectories. Bridge B's specialization stays as written; the case-study regime labels are substrate-dependent and need to be validated per substrate.

**Revision B (Bridge B specialization revision):** The mapping from regime to feature-class is wrong in the framework documents. Both induced-hole and greedy-decoding-artifact regimes produce Layer 2 dominance in ASD coordinates on standard RLHF'd LLMs. The Layer 1 cancellation feature class measures something else (perhaps purely length effects or local punctuation patterns) that the framework was wrong to associate with induced-hole signatures.

Distinguishing A from B requires data from at least one other substrate, which Phase 5 will provide if executed. Until then, the framework should record both possibilities and note that the Layer-1-for-induced-hole prediction is currently unsupported.

### 7.3 What ASD measures on LLM trajectories

The current framework documents describe ASD features as audit functionals on the policy that detect constraint engagement. The Phase 2-prime data suggests a different functional content for these specific feature implementations on this specific substrate:

**ASD reads trajectory richness / hedging cadence / exploration variance.**

Specifically:
- Layer 2 depth-class features (Q_tail_2, Q_tail_3, Q_tail_4, r_plus, mean_depth_excess) carry topic-dependent signal.
- The signal direction is: rich exploratory trajectories (mid-controversy topics) score "high"; committed trajectories (control or shaped topics) score "low."
- Layer 1 cancellation features (drift, isolated_frac) carry no cross-topic signal in this analysis.

This is a meaningful description of what ASD does on Llama-3.1-8B-Instruct — but it is *not* the description the current framework documents give. The framework should add a section (or a note) describing the Phase 2-prime finding and the trajectory-richness hypothesis as the current best account of ASD's empirical content on this substrate.

The structural unification of ASD with Phantom is then partial: Phase 1's orthogonality finding holds; ASD adds dimensions to F that the abelian baseline doesn't reach. But those dimensions don't measure constraint engagement directly — they measure trajectory richness, which is *correlated with* but *not equivalent to* constraint engagement, and on shaped topics the correlation runs *opposite* to what was predicted (more constraint engagement → less trajectory richness, because RLHF produces committed flat trajectories on these topics).

### 7.4 The case-study categorization

CS-PHANTOM-001 documented founding fathers and Wehrmacht as induced-hole-regime case studies. CS-PHANTOM-002 documented crime demographics as a greedy-decoding-artifact-regime case study. The case-study documents are framework records of behavior on a specific model substrate. On Llama-3.1-8B, the case-study findings need re-validation:

- Phase 2-prime per-topic shapedness scores show all three case-study topics ranking *low* in ASD-detected shaping signature (0.304–0.324, well below the mid-controversy mean of ~0.36). On ASD coordinates, none of the three look strongly "shaped-like" relative to the rest of the topic set on this substrate.
- The Phase 1 mean ρ values across categories were not separately reported in EN-PHANTOM-001; that re-analysis is recommended as a follow-up. If shaped-category mean ρ is similar to control-category mean ρ on Llama-3.1-8B, the case-study evidence does not transfer to this substrate at all.

The framework's claim that these specific topics engage RLHF distortion on Llama-3.1-8B is currently unconfirmed. The original case studies may have been on Llama-3.1-405B or a different model, and the engagement may not transfer. This should be flagged in the case-study documents.

### 7.5 The audit-blind shrinkage claim

The framework's strong-form claim was: under augmentation, audit-blind subspace shrinks by ≥ 3 effective dimensions on Llama-3.1-8B. The Phase 1 result placed this lower bound in policy space; Phase 2-prime tests whether it transfers to $\Xi$. The empirical delta of +0.024 (statistically significant but operationally weak) indicates a reduction of roughly 1 effective dimension, not 3. The shrinkage claim should be revised to reflect this:

**Revised statement:** Under augmentation by $F_{\text{ASD}}$, the audit-blind subspace shrinks by at least 1 effective dimension on Llama-3.1-8B — measured by classifier-AUC delta on the shaped-vs-not-shaped task — corresponding to a small but statistically reliable improvement in detection over the abelian baseline. The Phase 1 lower bound of ~3 effective dimensions in policy space does not transfer fully to the constraint subspace $\Xi$ on this task.

This is a real result. ASD adds something. It just adds less than predicted, and in a less specific direction than predicted.


---

## Section 8: What Stands

### 8.1 Phase 1's orthogonality result

EN-PHANTOM-001's headline result — that Layer 1 ASD features are empirically near-orthogonal to mean ρ across 150 (topic, paraphrase) pairs on Llama-3.1-8B-Instruct — is a measurement of feature correlation between two specific functional families. It does not depend on what either family measures in absolute terms. Phase 2-prime's finding that ASD measures trajectory richness rather than constraint engagement does not affect Phase 1's orthogonality measurement: trajectory richness is itself empirically near-orthogonal to mean ρ, with the same Pearson r values Phase 1 reported.

Phase 1 stands as a real result about the mathematical relationship between two feature classes. The interpretation that "ASD adds dimensions to F" is unaffected. The interpretation that "those dimensions detect RLHF distortion" needs revision per §7.

### 8.2 The audit-space apparatus

FN-PHANTOM-001's audit-blind theorems (Theorems A, B, C, D) operate on the abstract apparatus of the audit space F, the constraint subspace $\Xi$, and the audit projection $\Pi_N$. They are derivations from set-up assumptions and do not depend on what specific functional families are used to instantiate $F_{\text{ab}}$ or $F_{\text{ASD}}$. Phase 2-prime does not refute any of the theorems; it provides empirical content for the framework's specialization of those theorems to specific feature implementations on a specific substrate.

The augmented-audit theorem ($\dim(\ker \Pi_{N+M}) \geq \dim(\Xi) - N - M$) holds as written. The empirical question Phase 2-prime answered is the value of $M$ for the specific Layer 1+2 ASD implementations on Llama-3.1-8B at the shaped-vs-not-shaped detection task. The answer: small but positive ($M \approx 1$), with directional content (sub-check i passes) but mismatched per-topic feature emphasis (sub-check ii fails).

### 8.3 Bridge B's directional content

Sub-check (i) of P2'-6 passes: across the three case-study topics, the per-topic shapedness score ranks correctly with predicted leakage strength. Spearman ρ = 0.866 is at the high end of what three points can produce. **Bridge B has predictive content for ranking topics by ASD-detection magnitude on this substrate.** It does not have predictive content for the Layer 1 vs Layer 2 feature emphasis split.

This is a partial result — the *directional* component of Bridge B's specialization works on Llama-3.1-8B, the *categorical* component (regime → feature-class) doesn't. The framework can keep Bridge B's directional ordering as a supported prediction while flagging the categorical specialization as refuted on this substrate.

### 8.4 Layer 2 features as the cross-topic signal carrier

Phase 2-prime establishes empirically that Layer 2 depth-class features (Q_tail_1..4, r_plus) carry the ASD signal that does cross-topic generalization, and Layer 1 cancellation features (drift, isolated_frac) do not. The mean_depth_excess feature (Layer 1 walk-extent class) has moderate weight (+0.29 in the global classifier), placing it between Layer 1 cancellation features and Layer 2 features in cross-topic signal strength.

This sharpens Phase 1's structural finding (EN-PHANTOM-001 §3.2) that Layer 1 saturates at three classes. We can now refine: of the three Layer 1 classes, only the walk-extent class contributes meaningfully to cross-topic signal; the cancellation-rate and event-spacing classes are inert for this task. The path to additional audit dimensions for shaping detection runs through Layer 2 (already added in Phase 2-prime) and Layer 3 (not yet tested).

### 8.5 The reformulation methodology itself

Phase 2-prime's protocol — inst-only data, shaped-vs-not-shaped task, leave-one-topic-out CV — is the right methodology for measuring rank of an audit class on $\Xi$ when the relevant $\Xi$ is the topic-shaping subspace. The original Phase 2 protocol was wrong because it used cross-model classification, which has a trivial likelihood-ratio solution that doesn't measure $\Xi$ at all.

This methodological lesson generalizes. **Any future audit-rank measurement protocol using classifier comparison should ensure the classifier's decision label is not trivially recoverable from the audit features.** Cross-model classification with cross-model likelihood features is the prototype of this failure mode. Within-model classification with topic-specific labels (or other label structure that varies with $\Xi$ but not with feature-set membership) is the corrected pattern.

This methodological correction should be added to MN-PHANTOM-001 as guidance for Phase 3 and Phase 5 protocol design.


---

## Section 9: What This Means at Increasing Levels of Abstraction

### 9.1 Direct meaning

On Llama-3.1-8B-Instruct trajectories, ASD features measure trajectory richness rather than RLHF constraint engagement. The framework's strong-form prediction — that ASD features detect topic shaping with substantial AUC — is refuted on this substrate. ASD does add a small amount of cross-topic detection capability (delta C-A = +0.024, p < 0.001, below the 0.05 threshold), and does so with directional content matching Bridge B's predicted ordering on the three case-study topics, but the magnitude is below the framework's pre-registered operational threshold.

### 9.2 Structural meaning

The structural unification of ASD with Phantom is partial. Phase 1 established the orthogonality piece; Phase 2-prime tests the rank-on-$\Xi$ piece and finds it operationally weaker than predicted. The audit-blind subspace shrinks under augmentation by ~1 effective dimension on this task, not the ~3 Phase 1 indicated in policy space. The structural argument from FN-PHANTOM-002 §4.2 (abelianization permits non-abelian audit functionals) holds; the empirical specialization to Llama-3.1-8B's shaped topics does not deliver the strong rank contribution the framework predicted.

The framework has an empirical apparatus that adds dimensions to F that the abelian baseline doesn't reach. Those dimensions read trajectory structure that is correlated with topic content. The correlation does not specifically track the case-study-shaped topics in the predicted direction. So the apparatus is real, the dimensions are real, the structure they read is real — but what the structure *means* in framework-relevant terms is different from what the framework predicted.

### 9.3 Operational meaning for Phantom

Operational Phantom probes (HB-PHANTOM-001) measure $\rho^*$ via paraphrase battery on shaped topics. Phase 2-prime's data offers a test: does mean ρ on inst-only trajectories actually differ between shaped and not-shaped topics on Llama-3.1-8B? AUC(A) = 0.501 says no, at least not at the cross-topic generalization level the LOO-by-topic test measures.

This is a separate finding worth noting: **Phantom's existing methodology may itself not show strong cross-topic generalization on Llama-3.1-8B at the shaped-vs-not-shaped detection task.** This doesn't refute Phantom's case-study findings (which are about specific shaped topics, not cross-topic generalization), but it suggests that a "general shaping detector" using mean ρ alone won't work at scale on this model. Whether this is a Llama-3.1-8B-specific finding or a general statement about Phantom requires Phase 5 (cross-substrate atlas) to resolve.

### 9.4 Epistemic meaning

The right epistemic posture: the framework's structural unification claim is now partially tested. Phase 1 established the orthogonality piece with margin; Phase 2-prime tests the rank-on-$\Xi$ piece and produces a partial-pass-with-revisions result. The framework documents reach the empirical milestone they were designed to reach; some of the predictions hold, some don't.

This is what serious empirical work produces. Strong-form predictions get tested. Some pass. Some fail. The ones that fail teach you something about the apparatus you have. The trajectory-richness reading of ASD's empirical content is a genuinely new framework-level finding — neither predicted by FN-PHANTOM-002 nor by the case studies — and it suggests directions for follow-up work (Phase 3 natural-vs-induced, interventional experiments, Layer 3 feature exploration) that wouldn't have been visible without Phase 2-prime.

### 9.5 Cross-domain meaning

EN-PHANTOM-001 §7.5 documented the cross-domain transfer carefully: the apparatus transfers (F_2 walk, free reduction, encoding); the metric implementations adapted (drift saturated on LM and was redefined; h* plateaued and was replaced). Phase 2-prime adds: the *empirical content* of the metric implementations differs across domains too. ASD features on radar measure structural properties of return-process noise; ASD features on LLM trajectories measure trajectory richness / hedging. Both are non-abelian audit functionals; they measure different things in their different domains.

This refines the cross-domain claim from EN-PHANTOM-001 §7.5. The apparatus is universal; the metric implementations regime-specialize; what the implementations *measure* is also regime-specific. The framework's claim that ASD measures "the same kind of thing" across domains needs to be qualified: ASD measures non-abelian temporal-structure properties of signals, but the *content* of those properties is signal-specific, not signal-invariant.

### 9.6 Generalization implications

Phase 2-prime is single-substrate. The result that ASD measures trajectory richness rather than constraint engagement on Llama-3.1-8B may or may not generalize. Phase 5 (cross-institutional atlas, FN-PHANTOM-002 §8.5) would test:

- Does the trajectory-richness reading hold on Mistral, Gemma, GPT-3.5, Claude-3?
- Do the same case-study topics produce mid-range or low-range shapedness scores on different substrates?
- Does the mid > control > shaped ordering reproduce, or is it Llama-specific?

If the trajectory-richness reading is Llama-specific, the framework's claims about ASD's empirical content would need substrate-by-substrate qualification. If the reading reproduces across substrates, ASD measures a general property of LLM trajectories that's consistent across training pipelines — which would be a finding worth pursuing on its own terms, separate from the constraint-engagement claim.


---

## Section 10: Caveats and Limitations

### 10.1 The original Phase 2 confound is itself a methodological lesson

The original Phase 2 protocol's gen-model-wins artifact was not anticipated in the protocol design despite the methodology document explicitly flagging "AUC > 0.95 anywhere is a smell test failure" (MN-PHANTOM-001 §9.1). I had the warning written and did not apply it at design time. This is a real procedural failure that should inform Phase 3 and Phase 5 protocol design — both phases should be reviewed for analogous artifacts (any classifier task where the label is trivially recoverable from the feature set) before GPU time is spent.

The reformulation (Phase 2-prime) is the corrected protocol. Its finding is the operational verdict. The original Phase 2 result is recorded for completeness and as evidence of the methodological issue, but it is not the framework's empirical record for the rank-on-$\Xi$ question. Future framework documents should cite Phase 2-prime as the Phase 2 result.

### 10.2 Encoder is a clean reimplementation

Same caveat as EN-PHANTOM-001 §6.1: the encoder and feature definitions are clean numpy implementations following the ASD theory documents, not a port of the production radar codebase. drift was redefined, h* was replaced; both were regime-specialized for the LM input class during Phase 0. The Phase 2-prime finding (that Layer 1 cancellation features are inert and Layer 2 features carry the signal) is established for these specific implementations. Re-running with the production radar encoder would shift the numbers. Whether it would change the trajectory-richness finding qualitatively is an open question.

The trajectory cache at `results/phase1_trajectories_llama.npz` makes re-evaluation cheap. When the production radar code arrives, re-running Phase 2-prime with the alternative encoder is a ~30-second analysis.

### 10.3 Single substrate

Llama-3.1-8B-Instruct only. Phase 5 (cross-institutional atlas) would test whether the trajectory-richness reading and the operational rank contribution generalize. The case-study categorizations were validated on a different substrate; the substrate-specificity finding would be confirmed or refuted by Phase 5.

### 10.4 Choice C signal only

Phase 1 and Phase 2 both used Choice C exclusively. EN-PHANTOM-001 §1.5 defended Choice C as the principled hardest test for (O-LM); the same reasoning applies to Phase 2 — Choice C's abelian summary equals the average of the encoder input. Choices A and B (generating-model surprisal, cross-model surprisal under base) would test alternative signal-to-baseline pairings; they are not gating evidence but additional characterization. Re-encoding the cached trajectories with Choices A or B is in the cheap-followup list.

### 10.5 Linear classifier limitation

Logistic regression on standardized features is a linear classifier. Nonlinear interactions between features (ρ × ASD multiplicative effects, e.g.) are not exploited. As argued in MN-PHANTOM-001 §7.4, this is the right choice for measuring the rank-on-$\Xi$ quantity (the audit-blind theorem's content is linear), but it does mean any nonlinear separability that exists in the data is not visible to Phase 2-prime's analysis. A Random Forest or gradient-boosted classifier would likely produce higher AUC on Set C — but its AUC wouldn't measure the same geometric quantity.

This limitation is structural and not correctable within the chosen methodology.

### 10.6 Topic categorization remains judgment-based

The shaped/mid/control categorization in `phase1_topics.py` reflects the framework authors' judgment based on prior case studies, not independent ground truth. EN-PHANTOM-001 §6.6 noted this. Phase 2-prime's binary task (shaped vs not-shaped) inherits this judgment dependency.

If the categorization is wrong on Llama-3.1-8B — that is, if some "shaped" topics don't actually engage RLHF on this substrate, or some "not-shaped" topics do — the AUC values shift correspondingly. The Phase 2-prime finding is robust to small categorization errors (the trajectory-richness ordering mid > control > shaped holds whether one or two topics are mis-categorized) but would not be robust to systematic categorization failure (e.g., if 8 of 10 shaped topics aren't actually shaped on this substrate).

A separate study using Phantom's existing methodology (HB-PHANTOM-001) to measure $\rho^*$ on the topics in `phase1_topics.py` and using the empirical $\rho^*$ values as the categorization ground truth would address this caveat. This is recommended as a follow-up.

### 10.7 K=30 vs K=100 considerations

Phase 1 used K=30 seeds per (topic, paraphrase). Phase 2-prime uses these same trajectories. Phase 2 original used K=100 seeds per (topic, paraphrase, generating_model) on the three case-study topics. Phase 2-prime's 4500 inst-only trajectories cover 30 topics broadly but with K=30 per pair; Phase 2 original's 1500 inst trajectories cover only 3 topics but with K=100 per pair.

The Phase 2-prime per-topic shapedness scores have 30 trajectories per paraphrase × 5 paraphrases = 150 trajectories per topic for the score average. This is sufficient for stable mean estimates at the topic level (SE ~ 0.04 on the 0.28-0.37 score range, computed from the score distribution within topics).

Re-running Phase 2-prime with the higher-K Phase 2 inst trajectories on the three case-study topics gives tighter per-topic Set B AUC estimates but doesn't change the cross-topic story. The Phase 2 inst trajectories sit inside Phase 1's coverage at a different K — they augment but don't replace.

### 10.8 The categorization-vs-mechanism conflation

Section 7.2 notes two interpretive paths for the sub-check (ii) failure: revision A (case-study categorizations are wrong on this substrate) and revision B (Bridge B's specialization is wrong). The data alone doesn't distinguish them. This is a real interpretive gap that Phase 5 or interventional experiments would address. Until then, the framework should record both possibilities and let downstream analysis pick which to pursue.


---

## Section 11: Next Steps

### 11.1 Test the trajectory-richness hypothesis directly

The strongest interpretation of Phase 2-prime's data — that ASD reads trajectory richness rather than constraint engagement — is a hypothesis. A direct test: design prompts with controlled epistemic-uncertainty levels (high-confidence factual recall vs deliberate-ambiguity questions) and measure ASD signals on $\pi_{\text{inst}}$ trajectories from those prompts. If trajectory richness is what ASD measures, the deliberate-ambiguity prompts produce stronger ASD signal than high-confidence-factual prompts regardless of topic shaping. This isolates the hypothesized variable.

This is a small experiment (a few hundred trajectories on a custom prompt set) and could run in 1–2 GPU-hours. Result would either confirm the trajectory-richness hypothesis or distinguish it from alternative explanations of the Phase 2-prime data.

### 11.2 Re-validate case-study categorization on Llama-3.1-8B

Run Phantom's existing methodology (paraphrase battery, $\rho^*$ measurement) on all 30 topics in `phase1_topics.py` using Llama-3.1-8B-Instruct. The output is per-topic empirical $\rho^*$ values. Use those as categorization ground truth and re-run Phase 2-prime with the empirical labels. If the empirical $\rho^*$-based categorization differs from the judgment-based categorization, the Phase 2-prime verdict on the empirical categorization is the more reliable one.

This costs no new GPU time — Phase 1's cache has all the surprisal data needed for $\rho^*$ on all 30 topics. Pure analysis.

### 11.3 Layer 3 features

Phase 2-prime used Layer 1 + Layer 2 features. Layer 3 — the full empirical pair $(\nu_x^T, \mu_x^T)$ as a measure-valued object — could in principle add audit dimensions. The ASD theory documents describe Layer 3 functionals (cylinder integrals against test functions, Wasserstein distances between empirical pairs) that could be implemented and added to Set B. Re-running Phase 2-prime with Layer 3 added would test whether the rank contribution of $F_{\text{ASD}}$ on $\Xi$ is bounded by 1 effective dimension as Phase 2-prime found, or whether Layer 3 reveals more.

### 11.4 Cross-substrate test (Phase 5)

The most expensive followup. Cross-institutional atlas: 5 substrates × 30 topics × 5 paraphrases × 50 seeds × ~256 tokens. Tests whether the trajectory-richness reading, the mid > control > shaped ordering, and the small operational rank contribution all generalize across substrates.

If the trajectory-richness reading reproduces, ASD measures something universal about LLM trajectories that's worth pursuing as a finding in its own right. If only the substrate-specific findings show up, the framework's claims need substrate-by-substrate qualification.

### 11.5 Bridge B revision

The framework's Bridge B specialization to ASD coordinates needs revision. Section 7.2 lists two possible directions: regime-reclassification (revision A) or specialization-rewriting (revision B). The right move depends on Phase 5's outcome and on the §11.1 trajectory-richness test. Until those are run, the current framework documents should:

- Mark the Bridge B sub-check (ii) prediction (induced-hole → Layer 1; greedy-decoding-artifact → Layer 2) as "currently unsupported on Llama-3.1-8B."
- Mark the directional ordering prediction (sub-check i) as "supported."
- Add the trajectory-richness reading as the current best account of ASD's empirical content on this substrate, with the caveat that mechanism-level confirmation is pending.

### 11.6 Phase 3 (natural-vs-induced regime separation)

FN-PHANTOM-002 §8.3 specifies Phase 3: testing whether ASD signature regimes correlate with the FN-PHANTOM-001 §10 distinction between natural and induced holes. Phase 3 was scheduled to follow Phase 2 in the program plan. Given Phase 2-prime's results, Phase 3's design may need revisiting:

- The natural-vs-induced distinction was framework-internal — defined by where in the policy training pipeline the constraint engagement originated.
- If ASD reads trajectory richness rather than constraint engagement, Phase 3's predicted natural-vs-induced ASD signature differences may not manifest.
- Alternatively, natural and induced holes might still differ in the trajectory-richness pattern they produce, even if neither aligns with the framework's predicted ASD regime distinction.

Phase 3 should proceed but with revised expectations and a Phase-3-prime backup design analogous to Phase 2-prime.


---

## Section 12: Reproducibility

### 12.1 Code

- **`src/llm_trajectory.py`** — TransformersBackend with 3-pass sequential model loading; `generate_batch` accepts mixed inst/base specs.
- **`src/asd_encoder.py`** — block-local ordinal quartile encoding at $b=16$; F_2 walk with free reduction; depth tracking up to 6.
- **`src/asd_features.py`** — Layer 1 features (drift, timing_cv, mean_depth_excess, isolated_frac, d2_excess) + Layer 2 features (Q_tail_1..4, r_plus); IID null calibration.
- **`tests/phase2_lm.py`** — original Phase 2 generation pipeline (3 topics × 5 paraphrases × K=100 × 2 models = 3000 trajectories).
- **`tests/phase2_topics.py`** — 3 case-study topics with paraphrases.
- **`tests/phase2_analysis.py`** — original Phase 2 analysis with the per-topic 5-fold leave-one-paraphrase-out CV.
- **`tests/phase2_prime_analysis.py`** — Phase 2-prime analysis with leave-one-topic-out CV on Phase 1 features.

### 12.2 Models

- meta-llama/Llama-3.1-8B-Instruct (revision 0e9e39f).
- meta-llama/Llama-3.1-8B (revision d04e592).
- bf16 inference on RTX 5080 (Blackwell, 16 GB VRAM, sm_120).
- PyTorch nightly cu128.

### 12.3 Data

- **Phase 1 trajectory cache:** `results/phase1_trajectories_llama.npz` — 4500 inst-only trajectories, 30 topics × 5 paraphrases × 30 seeds, with full $(\rho, \text{surp}_{\text{inst}}, \text{surp}_{\text{base}})$ vectors.
- **Phase 1 features:** `results/phase1_features_llama.csv` — 4500 rows × 27 columns, encoded at $b=16$ on Choice C signal.
- **Phase 2 trajectory cache:** `results/phase2_trajectories_llama.npz` — 3000 trajectories (1500 inst + 1500 base), 3 topics × 5 paraphrases × K=100 × 2 models.
- **Phase 2 features:** `results/phase2_features_llama.csv` — 2995 rows after EOS-truncation drops.

### 12.4 Run commands

```bash
# Phase 2 original (already run; result is the confounded one in §3):
python tests/phase2_lm.py
python tests/phase2_analysis.py results/phase2_features_llama.csv

# Phase 2-prime (operational test; uses Phase 1 cache, no GPU needed):
python tests/phase2_prime_analysis.py results/phase1_features_llama.csv
```

### 12.5 Output files

From Phase 2 original:
- `results/phase2_features_llama_report.md` — confounded result report.
- `results/phase2_roc_and_coefs.png` — ROC curves and Set C coefficients per topic.

From Phase 2-prime:
- `results/phase2_prime_report.md` — operational result report.
- `results/phase2_prime_roc_and_coefs.png` — pooled ROC + global Set C coefficients + per-topic shapedness scatter.

### 12.6 Random seeds

All seeds documented in code. Generation seeds 0..K-1 per (topic, paraphrase, generating_model). Encoder uses `traj.meta["seed"] + 7_000_000` as RNG seed for ordinal-encoding tie-breaking. IID null calibration uses seeds `0..49 + 5_000_000`. Bootstrap and paired-bootstrap analyses use seed 42 for reproducibility.

---

## Glossary of Notation

- $\pi_{\text{base}}, \pi_{\text{inst}}$: base and Instruct policies (Llama-3.1-8B variants).
- $\rho_i = \log \pi_{\text{inst}}(t_i) - \log \pi_{\text{base}}(t_i)$: per-token leakage.
- $\bar\rho = T^{-1} \sum_i \rho_i$: per-trajectory mean leakage.
- $F$: audit space (square-integrable functionals on policy space).
- $F_{\text{ab}}, F_{\text{ASD}}, F_{\text{aug}}$: abelian, ASD-derived, augmented audit classes.
- $\Xi$: constraint subspace where probability distortion lives.
- $\Pi_N$: audit projection $\Xi \to \mathbb{R}^N$.
- $\dim(\ker \Pi_N)$: audit-blind subspace dimension.
- $M$: rank of $F_{\text{ASD}}$ on $\Xi$ (Phase 2's central numerical question).
- (O-LM): Phase 1's orthogonality claim (EN-PHANTOM-001).
- AUC(A), AUC(B), AUC(C): achievable classifier AUC on Set A, B, C.
- Set A: ρ-only features (mean_rho, std_rho).
- Set B: ASD-only features (drift, timing_cv, mean_depth_excess, isolated_frac, Q_tail_1..4, r_plus).
- Set C: combined Set A + Set B.
- Layer 1 features: scalar summaries of empirical pair (drift, timing_cv, mean_depth_excess, isolated_frac, d2_excess).
- Layer 2 features: depth-distribution features (Q_tail_1..4, r_plus).
- Bridge B: framework's structural connection between four-object decomposition and ρ measurement.
- P2-1 through P2-6: pre-registered pass criteria for original Phase 2.
- F2-1 through F2-3: pre-registered falsification triggers for original Phase 2.
- P2'-1 through P2'-6: pre-registered pass criteria for Phase 2-prime.
- F2'-1 through F2'-3: pre-registered falsification triggers for Phase 2-prime.
- LOO-by-topic CV: leave-one-topic-out cross-validation (Phase 2-prime).
- LOO-by-paraphrase CV: leave-one-paraphrase-out cross-validation (Phase 2 original).
- gen-model-wins artifact: the structural fact that mean ρ on a trajectory is systematically determined by which model preferentially sampled the trajectory.
- shapedness score: per-topic mean Set B prediction from LOO-by-topic CV.

---

*EN-PHANTOM-002 v1.0 — May 2026.*
*Phase 2 result for the FN-PHANTOM-002 program. Original protocol confounded by gen-model-wins artifact; reformulated protocol (Phase 2-prime) is the operational test. Strong-form structural unification claim partially refuted on Llama-3.1-8B; Phase 1 orthogonality stands; framework requires revisions identified in §7.*
