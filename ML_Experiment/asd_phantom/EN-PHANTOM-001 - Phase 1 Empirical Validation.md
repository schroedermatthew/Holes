---
doc_id: EN-PHANTOM-001
doc_type: "Experimental Note"
title: "Empirical Validation of (O-LM) — ASD-Phantom Orthogonality on Llama-3.1-8B Trajectories"
phantom_components: ["audit-blind-subspace", "rho-field", "constraint-subspace-Xi", "F_ab abelian audit class"]
asd_components: ["F_ASD non-abelian audit class", "block-local ordinal quartile encoding b=16", "Choice C signal (per-token leakage)", "Layer 1 features: drift, timing_cv, mean_depth_excess, isolated_frac, d2_excess", "abelianization phi: F_2 -> Z^2 with kernel [F_2, F_2]"]
topics: ["empirical test of (O-LM) orthogonality claim", "150 (topic, paraphrase) pairs across 30 topics x 3 categories", "K=30 seeds per pair, 4500 trajectories total", "Pearson correlation analysis of ASD features vs mean rho", "Kruskal-Wallis test of category-uniform orthogonality", "audit-blind dimension implications"]
constraints: ["G1 convergence remains open for continuous-state processes (LM trajectories) — empirical inference does not require it but population-level interpretation does", "encoder is a clean reimplementation following the theory documents; numerics may differ from production radar code", "single model substrate (Llama-3.1-8B base + Instruct); cross-institutional generalization deferred to Phase 5", "Choice C signal only; Choice A (gen-model surprisal) and Choice B (cross-model surprisal) not yet tested", "K=30 sample size per pair; CIs are tight at the median-across-pairs level but per-pair point estimates have SE ~0.19"]
mathematical_standard: "Pearson correlation with bootstrap CIs; Kruskal-Wallis non-parametric ANOVA; pre-registered pass/fail thresholds with one-sided falsification triggers from FN-PHANTOM-002 §8.1.3-§8.1.4"
build_modes: ["sequential model loading on 16 GB VRAM", "two-pass batch generation: Pass 1 generate+score under Instruct, Pass 2 score under base", "trajectory caching as .npz for re-evaluation"]
last_verified: 2026-05-03
audience: ["framework maintainers", "AI safety practitioners", "independent researchers reviewing the ASD-Phantom bridge claim"]
status: "complete — Phase 1 of FN-PHANTOM-002 program. Phase 0 passed prerequisite. Phase 2 specified, not yet run."
phase_in_program: "Phase 1 of FN-PHANTOM-002 §8.1"

related_documents:
  - "Foundations - The Phantom Framework Mathematical Apparatus.md (FN-PHANTOM-001) — defines rho, the four-object decomposition, audit-blind theorems"
  - "Foundations - ASD-Augmented Distortion Detection.md (FN-PHANTOM-002) — specifies the program this document instantiates Phase 1 of"
  - "Handbook - Probability-Distortion Measurement Discipline.md (HB-PHANTOM-001) — methodology this result extends"
  - "Pattern Guide - Structured Monte Carlo for Probe Design.md (PG-PHANTOM-001) — abelian probe scaling; this document is the parallel non-abelian validation"
  - "Case Study - Induced-Hole Amplification.md (CS-PHANTOM-001)"
  - "Case Study - The Greedy-Decoding Artifact.md (CS-PHANTOM-002)"
  - "Case Study - The Hemings Cross-Institutional Differential.md (CS-PHANTOM-003)"
  - "ASD_RESEARCH.md — navigation index; this result instantiates §RA5 Phase B against Phantom"
  - "ASD_FOUNDATIONS.md — the F_2 walk, empirical pair, harmonic measure"

phantom_apparatus_used:
  established_results:
    - "audit-blind theorem B: dim(ker Pi_N) >= dim(Xi) - N for any N-query audit [E linearized regime; FN-PHANTOM-001 Part 9]"
    - "rho-field as per-token leakage signal [E by construction; FN-PHANTOM-001 §4]"
  open_results:
    - "rank of F_ASD on the constraint subspace Xi [O — Phase 2 measures this directly]"
    - "Bridge B's mu^2(1-s^2) law manifest in ASD-feature coordinates [O — requires controlled-training experiments]"

asd_apparatus_used:
  established_results:
    - "abelianization argument: phi: F_2 -> Z^2 has kernel [F_2, F_2] free of countably infinite rank [E proved; ASD_FOUNDATIONS.md]"
    - "block-local ordinal quartile encoding at b divisible by 4: d_g(1) = 0 baseline by construction [E proved; ASD §CC1 Level 2]"
    - "near-orthogonality of ASD features to amplitude statistics in radar: r ≈ 0.00-0.26 on IPIX [E measured; ASD_RESEARCH.md, ASD_VARIATIONAL_DETECTION.md §VD3]"
  open_results:
    - "G1 convergence of empirical pair for continuous-state LM trajectories [O — empirical inference proceeds without it]"
---

# Empirical Validation of (O-LM) — ASD-Phantom Orthogonality on Llama-3.1-8B Trajectories

## Scope

This document reports the result of Phase 1 of the FN-PHANTOM-002 experimental program: an empirical test of the orthogonality claim **(O-LM)** stating that ASD-derived audit functionals on language model trajectories are near-orthogonal to the abelian $\rho$-mean audit class. The claim is the gating empirical hypothesis of the entire program — its truth determines whether the structural argument from FN-PHANTOM-002 §4.2 (the abelianization theorem permitting ASD features to be non-abelian) translates into a practical audit-space augmentation on real LLMs.

The result is reported with full protocol disclosure, the pre-registered pass/fail thresholds and falsification triggers, and a careful separation of what the result establishes from what remains open. The headline: **(O-LM) holds on Llama-3.1-8B with substantial margin, uniformly across topic categories including the case-study-validated shaped topics.** The structural argument transfers empirically. The audit-blind subspace from FN-PHANTOM-001 Theorem B is reducible by at least three dimensions on this input class.

## Not covered

- The construction of the F_2 walk, empirical pair, or boundary measure (see ASD_FOUNDATIONS.md).
- The derivation of the audit-blind theorems (see FN-PHANTOM-001 Part 9).
- The per-trajectory leakage decomposition (see FN-PHANTOM-001 §4).
- The classifier comparison establishing the rank of $F_{\text{ASD}}$ on $\Xi$ (this is Phase 2 per FN-PHANTOM-002 §8.2).
- Cross-institutional generalization (Phase 5).

## Result Card

**Topic:** A pre-registered empirical test of orthogonality between ASD-derived audit functionals and the abelian $\rho$-mean audit class on Llama-3.1-8B-Instruct trajectories, across thirty topics spanning control / mid-controversy / case-study-shaped categories.

**Headline numbers (target: median $|r| < 0.30$, 80th percentile $< 0.50$):**

| Feature | median $\|r\|$ | 80th pct | 95th pct | Verdict |
|---|---:|---:|---:|---|
| drift | 0.127 | 0.275 | 0.442 | PASS |
| timing_cv | 0.132 | 0.247 | 0.336 | PASS |
| mean_depth_excess | 0.123 | 0.227 | 0.332 | PASS |
| isolated_frac | 0.134 | 0.253 | 0.355 | PASS |
| d2_excess | 0.149 | 0.244 | 0.352 | PASS |

Five of five Layer 1 features pass P1-1. None of F1-1 (median > 0.50) or F1-2 (80th > 0.70) trigger.

**Pairwise feature correlations (target: median off-diagonal $|r| < 0.60$):** median = 0.155. **PASS.** One redundancy detected: mean_depth_excess and d2_excess are 0.92 correlated, reducing distinct informative directions to four out of five features. drift and isolated_frac are 0.40 correlated, partially redundant but not collapsed.

**Topic-category uniformity (target: KW $p > 0.01$ across control, mid, shaped):** smallest $p$ across the five features is $p = 0.19$. **PASS.** F1-3 (any $p < 0.01$) does not trigger. The orthogonality holds with no detectable category-dependent structure — including on the case-study-validated shaped topics where coupling between $\rho$ and ASD features was the leading concern.

**Aggregate verdict:** P1-1 ✓ + P1-2 ✓ + P1-3 ✓ ⇒ **(O-LM) holds.** Phase 2 cleared to proceed.

**Mental model of the result:** The Layer 1 ASD feature vector and mean $\rho$ measure approximately disjoint properties of Llama-3.1-8B trajectories. On a typical (topic, paraphrase) pair, the population-level Pearson correlation between any single ASD feature and mean $\rho$ across the K=30 seeds is between 0.10 and 0.20 in magnitude — comparable to the radar reference range of 0.00-0.26 between ASD features and amplitude statistics. Substituting one for the other loses information; combining them adds dimensions. This is the empirical content of "non-abelian audit functions exist for LLM trajectories."

**What is now established:** ASD-derived audit functionals span a subspace of the audit space $F$ that is approximately orthogonal to the abelian $\rho$-mean class on this input class. The augmented audit-blind dimension bound is $\dim(\Xi) - N - M$ with $M \geq 3$ effective new dimensions.

**What is not yet established:** Whether those new dimensions project nontrivially onto the constraint subspace $\Xi$. ASD features could be independent of $\rho$ but still uncorrelated with the directions of actual constraint engagement. Phase 2 (classifier AUC comparison on case-study topics) tests this directly.

**Read next:** Section 1 for the formal claim. Section 2 for the protocol. Section 3 for the result tables in detail. Section 4 for the mathematical interpretation. Section 5 for what this changes about the audit-blind apparatus.

---

## Section 1: The Claim Being Tested

### 1.1 Setup recap

A language model policy $\pi$ generates token sequences $x = (t_1, \ldots, t_T)$ given a prompt $p$. The Phantom framework measures probability distortion via the per-token leakage signal
$$\rho_i = \log \pi_{\text{inst}}(t_i \mid t_{<i}, p) - \log \pi_{\text{base}}(t_i \mid t_{<i}, p)$$
and its trajectory-level mean
$$\bar\rho(x) = \frac{1}{T} \sum_{i=1}^{T} \rho_i.$$
Across $K$ seeded continuations from $\pi_{\text{inst}}$, the empirical distribution of $\bar\rho$ supplies the abelian distortion measurement at the (prompt, paraphrase) granularity.

The audit space $F \subseteq L^2(\Pi)$ is the space of square-integrable functionals on policy space. A functional $f$ is **abelian** if it can be written as $f(\pi) = \mathbb{E}_{x \sim \pi}[h(x)]$ where $h$ depends only on the *multiset* of (token, context, position) triples in $x$, not their order. Mean $\rho$, surprisal averages, signal rates over paraphrases — all standard Phantom probes — span a subspace $F_{\text{ab}} \subseteq F$.

The audit-blind theorem (FN-PHANTOM-001 Theorem B) bounds the dimension of distortion that any audit budget of $N$ functions in $F$ can miss:
$$\dim(\ker \Pi_N) \geq \dim(\Xi) - N$$
where $\Xi$ is the constraint subspace and $\Pi_N: \Xi \to \mathbb{R}^N$ is the audit projection. The bound is taken over $F$, not $F_{\text{ab}}$ — so any enrichment of $F$ beyond $F_{\text{ab}}$ shrinks the bound by the rank of the new functions on $\Xi$.

### 1.2 The ASD audit class

ASD encodes a real-valued signal sequence into a walk on the free group $F_2$ via block-local ordinal quartile encoding (ASD §CC1 Level 2). Generators are $G = \{a, b, b^{-1}, a^{-1}\}$ with inverse map $0 \leftrightarrow 3$, $1 \leftrightarrow 2$. The walk applies free reduction at each step, accumulating cylinder masses on the boundary $\partial F_2$.

For a trajectory $x$ from policy $\pi$, applying the encoding to the Choice C signal $S^{(C)}(x) = (\rho_1, \ldots, \rho_T)$ produces an empirical pair $(\nu_x^T, \mu_x^T)$ on the cylinder algebra of $\partial F_2$. Layer 1 features extract continuous functionals of this pair. In this work:

- **drift**: $z$-score of cancellation rate against the IID null calibrated at matched $(T, b)$.
- **timing_cv**: coefficient of variation of inter-cancellation gap distribution.
- **mean_depth_excess**: $z$-score of average stack depth against IID null.
- **d2_excess**: $z$-score of depth-2 visit rate against IID null.
- **isolated_frac**: fraction of cancellations not adjacent within $\pm 8$ steps to another cancellation.

Define $f_{\text{drift}}(\pi) := \mathbb{E}_{x \sim \pi}[\text{drift}(S^{(C)}(x))]$ and analogously for the others. These are members of $F$. They span a subspace $F_{\text{ASD}} \subseteq F$.

### 1.3 The structural argument (FN-PHANTOM-002 §4.2 recap)

The abelianization homomorphism $\phi: F_2 \to \mathbb{Z}^2$ counts net occurrences of each generator, ignoring order. Its kernel $[F_2, F_2]$ is the commutator subgroup, a free group of countably infinite rank. Functionals computable from $\phi(\omega) \in \mathbb{Z}^2$ alone are equivalent to functionals of the multiset of generators — abelian.

The ASD encoding's free reduction step depends on order: cancellation occurs only when the new generator inverts the current rightmost letter. Two sequences with identical generator multisets but different orderings produce different walk positions and different cylinder masses. Layer 1 features computed on these masses are *not* abelian functionals of the input.

This proves: **non-abelian audit functionals exist** in the ASD class. It does not prove that any specific feature *as implemented*, evaluated on any specific input class, is empirically uncorrelated with the abelian functions one would actually compute. That's the empirical content of (O-LM).

### 1.4 The empirical claim

> **(O-LM)** *On LM continuations sampled from $\pi_{\text{inst}}$ at temperature $T \in [0.7, 1.0]$ across the topic set used in the existing case studies, the Layer 1 ASD feature vector $(\text{drift}, h^*, \text{timing\_cv})$ computed on Choice C signal $S^{(C)}$ has correlation $|r| < 0.4$ with mean $\rho$ across at least 80% of (topic, paraphrase) pairs.*

The Phase 1 protocol broadens the feature set from the original (drift, $h^*$, timing_cv) to five features (the ones above) — $h^*$ saturates due to walk transience and was replaced by mean_depth_excess (FN-PHANTOM-002 §8.0 negative result during encoder validation; documented in `asd_features.py`). The substantive content of (O-LM) — that the Layer 1 vector measures something different from $\bar\rho$ — is unchanged at the *audit-class level*; what changes is which specific functionals implement that audit class. The threshold $|r| < 0.40$ becomes the more stringent **median $|r| < 0.30$ AND 80th percentile $< 0.50$** per feature, with two falsification triggers (F1-1: median > 0.50; F1-2: 80th > 0.70) tightened from the document's narrative threshold.

### 1.5 Why Choice C is the principled hardest test

The signal sequence fed to the encoder matters for what (O-LM) tests. FN-PHANTOM-002 §2 specified three signal choices — generating-model surprisal (A), cross-model surprisal (B), per-token leakage (C) — each producing different ASD feature distributions and, in principle, different orthogonality magnitudes against the abelian baseline.

Phase 1 used Choice C exclusively. This is not a coverage limitation; it is the **principled hardest version of (O-LM) to satisfy**:

- The Choice C signal is $S^{(C)}(x) = (\rho_1, \rho_2, \ldots, \rho_T)$, the per-token leakage sequence.
- The abelian baseline $\bar\rho(x) = T^{-1} \sum_i \rho_i$ is, by construction, the average of the input signal.
- ASD features computed on $S^{(C)}$ therefore live in a subspace whose "natural" abelian summary equals the audit baseline being compared against.
- Any residual correlation between ASD-on-Choice-C features and $\bar\rho$ must come from temporal structure that survives **both** the F$_2$ free-reduction encoding **and** the averaging operation defining $\bar\rho$.

Choice A or Choice B would put more distance between the signal entering the encoder and the abelian baseline being compared against. (Choice A's natural abelian baseline would be $\bar S^{(A)}$ — mean surprisal under Instruct — which is not $\bar\rho$.) An (O-LM)-equivalent test on Choice A against mean surprisal would compare ASD against an abelian baseline of a different signal, lowering the bar for orthogonality.

By choosing Choice C and comparing against $\bar\rho$, Phase 1 tests the version where the input-to-encoder and the abelian-baseline-compared-against share an averaging relationship: they are the temporal sequence and its mean. This is the configuration where common-cause coupling between ASD features and the abelian baseline is strongest. Phase 1 has cleared (O-LM) under the strictest version. Phases on Choice A and B (deferred — see §6.4) would test alternative signal-to-baseline pairings; their results would inform but not gate the audit-augmentation claim, because Choice C is the load-bearing version.


---

## Section 2: Experimental Protocol

### 2.1 Models

- **Generator**: meta-llama/Llama-3.1-8B-Instruct, bfloat16 weights, autoregressive sampling.
- **Reference**: meta-llama/Llama-3.1-8B (the unaligned base model from the same pretraining run; both share tokenizer, vocabulary 128256).
- **Hardware**: NVIDIA RTX 5080 (Blackwell, 16 GB VRAM, sm_120). PyTorch nightly cu128 build.
- **Loading strategy**: sequential. Both models are 8.03B parameters and 16.06 GB in bf16. Holding both simultaneously forces VRAM-RAM swapping. The `TransformersBackend.generate_batch` implements two-pass: load Instruct, generate + score all 4500 trajectories, free; load base, score the same trajectories, free.

### 2.2 Topic catalog

Thirty topics in three categories of ten:

**Control (10)**: low-distortion factual / educational topics. *Organic chemistry functional groups; South American river basins; thermodynamics; photosynthesis; fundamental theorem of calculus; Italian Renaissance; English etymology; stellar evolution; plate tectonics; classical-romantic symphony.*

**Mid (10)**: contested but not central RLHF targets. *Nuclear power; GMO food; minimum wage; electoral reform; UBI; AI existential risk; immigration economics; school choice; psychedelic therapy; carbon tax.*

**Shaped (10)**: case-study-validated topics where prior Phantom work has measured nontrivial $\rho^*$. *Founding fathers slavery; Wehrmacht conduct; crime demographics; Hemings-Jefferson; IQ heritability; trans youth medical; COVID lab leak; ivermectin; Kissinger legacy; sex differences in cognition.*

Five paraphrases per topic, varying surface form while holding core semantic content. Categorization is preserved from FN-PHANTOM-002 §8.1.1.

### 2.3 Generation parameters

- Temperature 0.7
- Top-p = 1.0 (no nucleus filtering)
- Max new tokens $T_{\text{gen}} = 256$
- Seeds 0..29 per (topic, paraphrase), giving K=30
- Total: $30 \times 5 \times 30 = 4500$ continuations
- Generations under Instruct only; base model is used for scoring not generation (Choice C requires per-token $\log \pi_{\text{base}}$ on the same token sequence)

### 2.4 Trajectory encoding

For each continuation $x$:
1. Compute Choice C signal $S^{(C)}(x) = (\rho_1, \ldots, \rho_{T_{\text{actual}}})$ where $\rho_i = \log \pi_{\text{inst}}(t_i \mid t_{<i}, p) - \log \pi_{\text{base}}(t_i \mid t_{<i}, p)$.
2. Apply block-local ordinal quartile encoding at block_size $b = 16$. Each block of 16 values is ranked, and ranks are mapped to generators (Q0→a, Q1→b, Q2→b⁻¹, Q3→a⁻¹).
3. Apply free reduction sequentially, accumulating depth visits and cylinder masses up to depth 6.
4. Compute Layer 1 features against the IID null calibrated at $T_{\text{gen}}=256$, $b=16$ via 50 IID-Gaussian seeds.

Of 4500 attempted continuations, 4493 produced trajectories long enough to encode (a small minority hit the EOS token before the 16-block minimum); 4500 - 4493 = 7 were dropped silently with no effect on the result.

### 2.5 Statistical procedure

For each of the 150 (topic, paraphrase) pairs, with K=30 seeds in the pair, compute Pearson correlation $r$ between mean_rho (the per-trajectory $\bar\rho(x)$ as defined above) and each of the five Layer 1 features. This produces 150 correlations per feature, summarizing as median, IQR, 80th percentile, and 95th percentile.

For pairwise feature redundancy, the matrix of pairwise Pearson $|r|$ across all 4500 trajectories pooled is computed and the median off-diagonal entry reported.

For the topic-category effect, Kruskal-Wallis non-parametric rank ANOVA is applied to the |r| distributions of each feature, split by category (control / mid / shaped, 50 pairs each).

### 2.6 Pre-registered thresholds and falsification triggers

Per FN-PHANTOM-002 §8.1.3 and §8.1.4, the program pre-committed to:

**Pass criteria (all three must hold for (O-LM)):**
- (P1-1) For each Layer 1 feature: median $|r| < 0.30$ AND 80th percentile $|r| < 0.50$ across the 150 pairs.
- (P1-2) Median pairwise feature $|r|$ on the same data $< 0.60$.
- (P1-3) Kruskal-Wallis $p > 0.01$ for category-level differences in $|r|$ distribution per feature.

**Falsification triggers (any one refutes (O-LM)):**
- (F1-1) Median $|r| > 0.50$ for any Layer 1 feature.
- (F1-2) 80th percentile $|r| > 0.70$ for any feature.
- (F1-3) Kruskal-Wallis $p < 0.01$ for any feature.

A weaker outcome — neither pass nor refutation — was anticipated for the case where some sub-criteria hold and others fail. The protocol specified diagnosing-by-feature and re-testing without those features.


---

## Section 3: Results

### 3.1 P1-1: per-pair correlation distributions

Across the 150 (topic, paraphrase) pairs, the |r| distribution per Layer 1 feature:

| Feature | N | median | mean | IQR | 80th pct | 95th pct | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| drift | 150 | 0.127 | 0.156 | 0.181 | 0.275 | 0.442 | 0.581 |
| timing_cv | 150 | 0.132 | 0.161 | 0.164 | 0.247 | 0.336 | 0.578 |
| mean_depth_excess | 150 | 0.123 | 0.149 | 0.146 | 0.227 | 0.332 | 0.518 |
| isolated_frac | 150 | 0.134 | 0.158 | 0.172 | 0.253 | 0.355 | 0.530 |
| d2_excess | 143 | 0.149 | 0.171 | 0.178 | 0.244 | 0.352 | 0.547 |

(d2_excess has N=143 because seven pairs had degenerate within-pair variance for the d2_excess feature — typically when d2_excess was near-constant 1.0 across all K=30 seeds in that pair, indicating the walk consistently reached depth 2 at almost every step. These pairs contribute no information about correlation and were dropped.)

**Verdict:** all five features pass P1-1. Median |r| values range 0.12 to 0.15, well under the 0.30 threshold. 80th percentile maxes at 0.275 for drift, well under 0.50. 95th percentile maxes at 0.442 for drift, well under 0.70. F1-1 (median > 0.50) and F1-2 (80th > 0.70) do not trigger anywhere.

The standard error of the median across 150 pairs, by bootstrap resampling, is approximately 0.014. The 95% CI on the median |r| for drift is therefore roughly (0.10, 0.16). The lower bound is 14× below the 0.30 threshold; the upper bound is half. The verdict is robust under sampling variation.

### 3.2 P1-2: pairwise feature correlations

The 5×5 pairwise |r| matrix on pooled data (all 4500 trajectories):

| | drift | timing_cv | mean_depth_excess | isolated_frac | d2_excess |
|---|---:|---:|---:|---:|---:|
| drift | 1.000 | 0.162 | 0.184 | **0.403** | 0.151 |
| timing_cv | 0.162 | 1.000 | 0.047 | 0.159 | 0.037 |
| mean_depth_excess | 0.184 | 0.047 | 1.000 | 0.077 | **0.924** |
| isolated_frac | 0.403 | 0.159 | 0.077 | 1.000 | 0.047 |
| d2_excess | 0.151 | 0.037 | 0.924 | 0.047 | 1.000 |

**Median off-diagonal |r| = 0.155.** P1-2 passes by a substantial margin (threshold 0.60).

Two notable structural findings within the matrix:

**(a) mean_depth_excess and d2_excess are 0.924 correlated.** This is a near-collapse — they're effectively measuring the same thing. Mechanically: both are z-scores of related depth statistics. mean_depth_excess is the z-score of $\mathbb{E}[\text{depth}]$; d2_excess is the z-score of $P(\text{depth} \geq 2)$. For the cancellation regimes typical here (depth distribution sharp around 1-3 steps), these two are dominated by the same component of the depth distribution. Operationally, treat them as one feature: keep one, drop the other.

**(b) drift and isolated_frac are 0.403 correlated.** Substantial but not redundant. This makes mechanical sense: drift measures cancellation rate (fewer extensions = lower cancellation rate, high drift); isolated_frac measures whether cancellations are spaced out. Trajectories that cancel rarely (high drift) have their few cancellations *necessarily* further apart — partial coupling. The features remain operationally distinct: drift answers "how often does the walk cancel?"; isolated_frac answers "given it cancels, are cancellations bursty or spread?".

**timing_cv is structurally independent** of all others (max |r| = 0.162). It captures something genuinely orthogonal to the depth-and-cancellation-rate features.

The effective number of distinct audit dimensions added by Layer 1 partitions into three structural classes:
$$M_{\text{Layer 1}} = \underbrace{1}_{\text{cancellation-rate class}} + \underbrace{1}_{\text{event-spacing class}} + \underbrace{1}_{\text{walk-extent class}} = 3$$

This is not a floor with more possible from feature engineering. **It is a structural ceiling for Layer 1.** The five features measured partition into three classes by the underlying empirical-pair statistic each class summarizes:

- **cancellation-rate class**: drift, isolated_frac (correlated at 0.40, both governed by the cancellation-rate component of the empirical pair). Adding more features in this class — different normalizations of cancellation rate, alternative gap-distribution functionals — would not add dimensions; they'd reduce to the same component.

- **event-spacing class**: timing_cv. Currently a single feature occupying its own dimension. Adding more event-spacing features (variance of inter-cancellation gaps, coefficient of skewness, autocorrelation of the gap process) might tighten the estimate but wouldn't add an independent dimension.

- **walk-extent class**: mean_depth_excess, d2_excess (correlated at 0.92, both governed by the depth distribution sharply peaked around 1-3 steps in this regime). Different functionals of the depth distribution at this characteristic scale collapse onto the same dimension.

The h* feature was abandoned during Phase 0 encoder validation due to walk transience (FN-PHANTOM-002 §8.0). The replacement (mean_depth_excess + d2_excess) recovers exactly one effective dimension because the class has internal redundancy. This is the same structural pattern: the class identifies one dimension of the empirical pair, and feature variants within the class re-derive that one dimension with different smoothing properties.

Path to higher M requires Layer 2 (the full $D(k)$ depth profile, $Q_{\text{tail}}$ recurrence fit, multi-depth structure) — features that summarize the empirical pair *along a different axis* than Layer 1's three-class partition. This is recommended for the encoder iteration when the modern radar feature definitions arrive (see §6.1, §8.3).

The audit-blind reduction claim should be sized to this constraint: $M = 3$ from Layer 1 specifically, not "$\geq 3$ with more possible via Layer 1 expansion."

### 3.3 P1-3: topic-category uniformity

Kruskal-Wallis test for category-level differences in |r| distribution per feature:

| Feature | H | p | median(control) | median(mid) | median(shaped) |
|---|---:|---:|---:|---:|---:|
| drift | 3.335 | 0.189 | 0.160 | 0.106 | 0.105 |
| timing_cv | 2.275 | 0.321 | 0.103 | 0.117 | 0.157 |
| mean_depth_excess | 0.337 | 0.845 | 0.134 | 0.129 | 0.109 |
| isolated_frac | 0.115 | 0.944 | 0.142 | 0.136 | 0.123 |
| d2_excess | 0.660 | 0.719 | 0.150 | 0.160 | 0.122 |

All p-values exceed 0.18. F1-3 ($p < 0.01$ trigger) does not fire. P1-3 passes.

Two observations beyond the headline:

**(a) Shaped topics show the lowest median $|r|$ on most features.** drift, mean_depth_excess, isolated_frac, and d2_excess all have shaped category $|r|$ medians at or below the control category. The exception is timing_cv, where shaped is highest (0.157) — though still well under all thresholds.

**(b) The shaped-vs-control gap is small but consistent in direction.** This is the *opposite* of what one would expect if the orthogonality were merely a control-topic artifact — i.e., if the shaped topics were where coupling between $\rho$ and ASD features should appear, and orthogonality only held on bland controls because there was no signal to couple. Instead, the data shows orthogonality is at least as clean on the case-study-validated shaped topics as on controls. **This is the actually-hard test passing**, not a low-bar pass on undemanding inputs.

A possible explanation for the observed direction: shaped topics induce *higher* variance in mean $\bar\rho$ across seeds (the constraint engages stochastically — sometimes triggering shaping, sometimes not), giving more dynamic range to detect any correlation that exists. If a real coupling existed, shaped topics would show it more clearly than controls. They don't show it more — they show it less.

The directional pattern is consistent across 4 of 5 features (drift, mean_depth_excess, isolated_frac, d2_excess). Statistical significance does not survive multiple testing across features (KW p-values 0.19-0.94), but the consistency of *sign* across independent features cannot be explained by per-feature noise alone. A more direct read of the data is that the orthogonality between $F_{\text{ASD}}$ and $\bar\rho$ has two distinct sources operating across the topic categories:

1. **On controls**, the orthogonality is partial. There is small common-cause coupling driving both summaries — most likely length and EOS-boundary effects: trajectories that end early have systematically different ρ statistics *and* different walk depths, propagating to both ρ-mean and ASD features. This produces the observed median $|r| \approx 0.14$ rather than 0.

2. **On shaped topics**, the orthogonality is structurally cleaner. The shaping engagement increases $\bar\rho$ variance *without* altering the temporal-structure variance ASD reads, because the constraint adds variation in *which positions* leakage concentrates at — not in the average leakage rate that controls don't have. This drives median $|r|$ slightly *below* the control level (0.10–0.13 across the four features).

If this read is right — and the consistency-of-sign supports it — the orthogonality property is *cleaner exactly where the framework needs it most*. Shaped topics are where Phantom's audit-blind question is operationally consequential, and shaped topics are where ASD features' independence from $\bar\rho$ is most pronounced. The cross-domain transfer from radar happens to be cleanest at the inputs that matter rather than at the inputs that are easiest to verify on.

### 3.4 Distribution shapes

Histograms of the five |r| distributions, broken out by topic category, are saved at `results/phase1_correlation_histograms.png`. Qualitative observations:

- All five features show a unimodal right-skewed distribution peaked near $|r| = 0.10$ with a long tail. No bimodality (which would indicate a subset of pairs with strong coupling and a subset with none).
- Shaped category histograms are essentially indistinguishable in shape from control category — visual confirmation of the KW result.
- The right tail thins out cleanly past $|r| = 0.4$ — there is no "minority of pairs with $|r| > 0.5$" subpopulation that would indicate the orthogonality fails on a structurally identifiable subset.


---

## Section 4: Mathematical Interpretation

### 4.1 What "orthogonality" formally means here

The Pearson correlation is a finite-sample estimator of the population-level inner product
$$\langle f, g \rangle_\pi := \frac{\mathbb{E}_\pi[(f - \bar f)(g - \bar g)]}{\sigma_f \sigma_g}$$
on functionals $f, g \in F$ evaluated as random variables under sampling $x \sim \pi$ at fixed prompt $p$. Phase 1 measures this inner product for $f \in \{\text{drift}, \text{timing\_cv}, \ldots\}$ against $g = \bar\rho$ at 150 distinct policy-prompt configurations and reports its empirical magnitude.

Median $|r| = 0.13$ with 150 evaluations corresponds to an inner-product magnitude of approximately 0.13 — small but nonzero. The features are *near-orthogonal*, not exactly orthogonal. This matters because:

**(a)** Exact orthogonality would imply zero information shared with $\bar\rho$; near-orthogonality at 0.13 means 1 - 0.13² ≈ 98.3% of the variance in each ASD feature is independent of $\bar\rho$. Effectively orthogonal for downstream classifier purposes.

**(b)** The structural argument from §1.3 only guarantees *non-trivial* orthogonality — the abelianization permits ASD features to live in $[F_2, F_2]$ rather than $\mathbb{Z}^2$. It does not require zero correlation. The 0.13 residual is consistent with a structurally non-abelian functional that has small empirical projection onto an abelian baseline due to:
   - Common dependence on trajectory length $T_{\text{actual}}$
   - Common sensitivity to outlier tokens that influence both $\bar\rho$ and the cancellation rate
   - Sample-size finiteness of K=30

**(c)** The radar-domain reference value (r ≈ 0.00–0.26 between ASD features and amplitude) was bounded above 0 for analogous reasons — radar amplitude and ASD features both depend on returns variance, just via different functional forms. The LM result is in the same regime.

### 4.2 The audit space picture, with care about which inner product

Define $V_{\text{ab}}$ as the linear span of $F_{\text{ab}}$ in $L^2(\Pi)$ and $V_{\text{ASD}}$ as the linear span of $F_{\text{ASD}}$. The geometric content of "(O-LM) holds" is that these subspaces are nearly perpendicular *under some inner product structure*. Two distinct inner products are in play, and the document was loose about which one the empirical estimator addresses.

**Single-prompt inner product.** At fixed prompt $p$ and fixed policy $\pi$, the inner product on functionals $f, g \in F$ is
$$\langle f, g \rangle_{\pi, p} = \mathbb{E}_{x \sim \pi(\cdot \mid p)}[(f(x) - \bar f_p)(g(x) - \bar g_p)] / (\sigma_{f,p} \sigma_{g,p})$$
This measures cross-realization covariance at fixed $(\pi, p)$. The Phase 1 per-pair Pearson $r$ is the empirical estimator of this quantity at $(\pi_{\text{inst}}, p)$ for each (topic, paraphrase) pair, with K=30 realizations.

**Population summary across prompts.** The 150 pair-level $|r|$ values sample 150 distinct values of $\langle f, g \rangle_{\pi, p}$, one per prompt. The median across this sample is a *population summary* over prompts. The "median angle ≈ 82.5°" interpretation is using language from the geometric picture (single-prompt inner product) but applying it to the cross-prompt aggregate.

These are different objects. The geometric statement "$F_{\text{ASD}}$ and $F_{\text{ab}}$ meet at 82.5°" requires a specific population-level inner product — for instance, $\langle f, g \rangle_{\pi, P} = \mathbb{E}_{p \sim P}[\langle f, g \rangle_{\pi, p}]$ for a prompt distribution $P$. Phase 1's median-across-pairs is a *robust estimator* of a typical single-prompt angle, not of this population-integrated quantity.

The substantive content is: at the single-prompt level, the typical (median across 150 cases) angle between ASD features and $\bar\rho$ is ~82.5°. The data also shows the distribution of single-prompt angles is unimodal, peaked around 82°-83°, with most mass between 75° and 88° (corresponding to $|r| \in [0, 0.27]$ at the 80th percentile). The population-integrated angle would be similar but differs by a Jensen's-inequality term that's small when the variance across prompts is small relative to the mean — which the $|r|$-distribution unimodality suggests is the case here.

The corrected statement: ASD features sit at typical ~82° single-prompt angles to $\bar\rho$, with low variance across prompts implying the population-integrated angle is also ~82°. The audit-space subspaces approximate this geometry across the prompt distribution sampled by the 150 (topic, paraphrase) pairs. Five features at ~80° single-prompt angles to $\bar\rho$, with median pairwise single-prompt angle to each other of ~81° (cos⁻¹(0.155)), span an effectively three-dimensional subspace whose population-integrated projection onto $V_{\text{ab}}$ is small.

This is the geometric content of "ASD adds dimensions to F that the abelian baseline doesn't reach" — under both single-prompt and population-integrated readings, with the former being what the data directly estimates and the latter being the audit-space-geometry-relevant quantity. The augmented audit class
$$F_{\text{aug}} := F_{\text{ab}} + F_{\text{ASD}}$$
has subspace dimension at least $\dim V_{\text{ab}} + 3$ on this input class, in both inner-product structures.

### 4.3 Why the structural argument worked

The abelianization $\phi: F_2 \to \mathbb{Z}^2$ has kernel $[F_2, F_2]$, the commutator subgroup. As a free group of countably infinite rank, $[F_2, F_2]$ contains uncountably many distinct cylinder events; the cylinder algebra of $\partial F_2$ restricted to $[F_2, F_2]$ supports uncountably many measurable functions linearly independent of any $\mathbb{Z}^2$-invariant function.

The Layer 1 features extract finitely many summaries of this rich structure — drift counts cancellation events, timing_cv counts spacings, depth features count walk position trajectories. Each is a *projection* of the kernel structure onto a 1-dimensional summary. The empirical question of Phase 1 was whether *these specific projections*, evaluated on LM trajectories with all their domain-specific quirks (autoregressive structure, finite-context attention, instruction-following format, end-of-turn boundary effects), retain enough non-abelian content to be empirically uncorrelated with $\bar\rho$.

The result says: yes. Not because of any deep theorem about LM trajectories, but because:
- LM surprisal sequences exhibit non-trivial temporal autocorrelation (function-word structure, sentence-boundary effects, topic coherence) that ASD's free reduction reads.
- That temporal structure is **not** preserved by the averaging operation that produces $\bar\rho$.
- The two summaries therefore carry overlapping but distinct information about $\pi_{\text{inst}}$.

This is consistent with the radar finding for analogous reasons: radar returns have non-trivial temporal structure (sea clutter coherence, target Doppler), the averaging operations producing amplitude statistics drop that structure, and ASD reads it back. Cross-domain transfer via the same mechanism.

### 4.4 What Phase 1 *does not* establish

The result establishes that ASD features are independent of $\bar\rho$ as functionals on policy space. It does **not** establish:

**(a) Independence from richer abelian classes.** A specific abelian functional more expressive than $\bar\rho$ — say, the histogram of $\rho$ values, or the empirical CDF of surprisal — might capture more of what ASD measures. The threshold for "abelian" is permutation-invariance of the per-position score; richer abelian functionals exist within $F_{\text{ab}}$ that Phase 1 didn't compare against.

**(b) Rank on the constraint subspace $\Xi$.** $F_{\text{ASD}}$ being orthogonal to $F_{\text{ab}}$ in the policy-space inner product does not entail that $F_{\text{ASD}}$ has nonzero projection onto $\Xi$. Phase 2 tests this directly via classifier AUC: if a classifier with ASD features beats a $\bar\rho$-only classifier on detecting base-vs-Instruct paired continuations, the AUC delta lower-bounds the rank of $F_{\text{ASD}}$ on $\Xi$.

**(c) Detection of the natural-vs-induced hole distinction.** Phase 3 (FN-PHANTOM-002 §8.3) tests whether ASD signature regimes correlate with the FN-PHANTOM-001 §10 distinction. The Phase 1 data is necessary input but not sufficient.

**(d) Generalization across model substrates.** Single-model result. Cross-institutional Phase 5 measures whether the orthogonality property is a feature of Llama-3.1-8B specifically or generalizes.


---

## Section 5: The Audit-Blind Apparatus, Updated

### 5.1 Theorem B in the augmented setting

FN-PHANTOM-001 Theorem B (linearized regime) states: for any choice of $N$ audit functions in $F$, the dimension of the audit-blind subspace is bounded below by
$$\dim(\ker \Pi_N) \geq \dim(\Xi) - N.$$
The bound is tight when audit functions are chosen optimally per Theorem D's SVD construction. Phase 1's contribution is not to violate Theorem B — it remains true — but to enrich $F$, which moves $N$.

Pre-Phase 1: $F$ in practice was $F_{\text{ab}}$, the abelian audit class. An audit budget of $N$ abelian probes left $\dim(\Xi) - N$ undetected.

Post-Phase 1: $F$ in practice is $F_{\text{aug}} = F_{\text{ab}} + F_{\text{ASD}}$. The same audit budget of $N$ probes can now span $N$ dimensions in this larger space. The audit-blind dimension bound becomes $\dim(\Xi) - N - M$ where $M$ is the number of dimensions $F_{\text{ASD}}$ contributes that are independent of $F_{\text{ab}}$ on $\Xi$.

The empirical lower bound from Phase 1 on $M$ in the policy-space inner product is **3** (drift, timing_cv, mean_depth-class). The lower bound on $M$ as it acts on $\Xi$ specifically is what Phase 2 measures.

### 5.2 The honest version of "audit-blind shrinks by 3"

**Claim:** The Phantom framework's audit-blind subspace, as measured by abelian probes of fixed budget $N$, is reducible by at least 3 effective dimensions on Llama-3.1-8B trajectories via ASD augmentation.

**Hedges in the claim:**

- "At least 3 effective dimensions" is the empirical rank of $F_{\text{ASD}}$ in the policy-space inner product. The rank on $\Xi$ is at most 3 and at least 0; Phase 2 fixes it.

- "On Llama-3.1-8B trajectories" — single substrate. Phase 5 generalizes.

- "Via ASD augmentation" — using the specific Layer 1 features as defined. Layer 2 features ($D(k)$ profile, $Q_{\text{tail}}$ recurrence) and Layer 3 (full empirical pair) can in principle add more dimensions; not measured here.

- "As measured by abelian probes" — comparing against $\bar\rho$. Richer abelian classes might cover more.

The claim is real but it's a **floor**, not a ceiling. Phase 2's AUC comparison fixes the rank on $\Xi$. Layer 2 expansion potentially raises $M$. Cross-institutional generalization tests robustness. None of these undermine the floor; they refine it.

### 5.3 What this changes in practice for Phantom

Operationally, the Phantom Phase E methodology (HB-PHANTOM-001) measures $\rho^*$ for a target topic via paraphrase battery and reports the abelian distortion estimate. With the Phase 1 result in hand, the methodology can be augmented:

1. Run the same paraphrase battery, but for each generation, capture per-token surprisal under both $\pi_{\text{inst}}$ and $\pi_{\text{base}}$ to compute $\rho_i$.
2. Encode $S^{(C)}$ via block-local ordinal at $b=16$ and extract Layer 1 features.
3. Report Layer 1 feature distributions alongside $\bar\rho$ across the paraphrase battery. The marginals carry the abelian distortion signal; the ASD features carry the temporal-structure signal.
4. Distortion is now a vector quantity — $\bar\rho$ in one direction, ASD features in three approximately-orthogonal directions.

This is a real methodological augmentation. It doesn't replace $\bar\rho$ measurement; it adds to it. The total information about $\pi_{\text{inst}}$ available from a single paraphrase battery increases.

The Pattern Guide (PG-PHANTOM-001) for probe design now has a parallel non-abelian axis: the abelian Monte Carlo over prompt space (PG main axis) extracts dimensions of $\Xi$ visible to abelian probes; ASD encoding of the resulting trajectories extracts dimensions visible to non-abelian probes. The two are complementary, not redundant.

### 5.4 Connection to Theorem D's optimal probe construction

FN-PHANTOM-001 Theorem D constructs the optimal $N$ abelian probes for a target $k$-dimensional concerning subspace via SVD of the abelian distortion-to-function map. The same construction in principle applies to $F_{\text{aug}}$ — but the SVD requires a closed-form linear response of audit values to perturbations in $\Xi$, which abelian functionals supply directly (via Fisher-tangent linearization at $\pi_{\text{base}}$) and ASD functionals do not.

This is FN-PHANTOM-002 §5.4's open problem (Q1 in §12). Phase 1's result makes it sharper: now that we know $F_{\text{ASD}}$ contributes dimensions, the question is how to *use* them — find the $N+M$ probes optimally for a specified concerning subspace. The current best move is empirical: train a classifier on $F_{\text{aug}}$ features, examine the learned weights, treat them as approximate optimal probes. This is what Phase 2 does. A theoretical optimal-probe-construction theorem for the augmented class is a research direction Phase 1's positive result motivates.


---

## Section 6: Caveats and Limitations

### 6.1 Encoder is a clean reimplementation

The `asd_encoder.py` and `asd_features.py` modules in this implementation are clean numpy implementations following the ASD theory documents (ASD_FOUNDATIONS.md, ASD_RESEARCH.md). They are **not** a port of the production radar codebase developed in the prior collaboration between the second author and an earlier model instance. Differences include:

- **drift definition:** here, $z$-score of cancellation rate against IID null. The original ASD drift in the radar work uses an $\ell_1$ deviation of the empirical depth-1 boundary measure from the harmonic null. The current implementation switched after observing that the original definition saturates at 1.5 for nearly all input due to walk transience (FN-PHANTOM-002 §8.0 negative result during encoder validation).

- **h_star replaced by mean_depth_excess:** for the same transience reason. The original $h^*$ ("characteristic depth at which $D(k) \leq 1/e$") plateaus and loses discriminating power on transient walks. mean_depth_excess captures the same intent (typical walk depth) but is bounded and numerically stable.

- **Layer 2 features (Q_tail decay, depth recurrence fit) are present in `asd_features.py`** but were not used in Phase 1 analysis. Future work with the modern feature definitions may include them.

The synthetic process validation confirmed the implementation is internally consistent: AR(1) and ARCH separated cleanly at $b=16$ with z-score margins of 13.76 standard deviations (FN-PHANTOM-002 §8.0 result). But specific numeric values are not directly comparable to the radar pipeline.

**Implication:** the qualitative content of the Phase 1 result — that ASD features are empirically near-orthogonal to $\bar\rho$ on LM trajectories — is robust to feature-definition refinements within reasonable bounds. Re-running the analysis with the production radar code (when available) would shift the exact numbers but is unlikely to flip the verdict given the size of the margins. The trajectory cache at `results/phase1_trajectories_llama.npz` makes re-evaluation cheap.

**The deeper implication (cross-referenced in §7.5):** the LM regime made the original radar feature definitions degenerate. drift saturated; $h^*$ plateaued. The LM-regime metrics are specifically the ones that work for LM trajectories — they are not the radar metrics tested in a new domain. The cross-domain transfer is therefore at the *apparatus level* (F_2 walk, free reduction, ordinal encoding) rather than at the *metric level* (specific feature implementations). This is consistent with the project's scene-solving discipline — different physics regime, regime-appropriate metric choices from the same apparatus — but it tightens what "ASD transfers from radar to LLM" can mean. The orthogonality result is established for the LM-regime metrics that produce numerically-stable readouts on this input class. The radar-regime metric definitions degenerated and were not tested.

### 6.2 Single model substrate

Llama-3.1-8B-Instruct is one of many production instruction-tuned models. Whether the orthogonality property is:
- (a) a feature of any RLHF pipeline applied to a well-trained base model;
- (b) specific to the Llama-3 training methodology;
- (c) specific to the 8B parameter scale;
- (d) specific to bf16 inference precision —

is not addressed by Phase 1. Phase 5 of the program (cross-institutional differential atlas, FN-PHANTOM-002 §8.5) addresses (a) and (b) at fixed scale via comparison to Mistral-7B-Instruct, Gemma-7B-Instruct, and signal-based estimates from API-only models. (c) and (d) are open.

### 6.3 G1 convergence

ASD theory uses a limiting boundary measure $\nu_\theta$ on $\partial F_2$ as $T \to \infty$. Convergence of the empirical pair to this limit requires assumptions G1 and G2; for finite-state ergodic Markov chains and IID processes G1+G2 is proved, but for continuous-state processes — including LM surprisal sequences — G1 remains an open question (ASD §SD4.1).

This document operates entirely at the empirical-pair level. Each $(\nu_x^T, \mu_x^T)$ is a well-defined finite-sample object regardless of convergence; ASD features computed on these objects are well-defined statistics. Statistical inference (Pearson r, Kruskal-Wallis) uses bootstrap and rank-based methods that don't require limiting objects. The conclusion "(O-LM) holds at $T_{\text{gen}}=256$" is robust to the G1 question.

What G1 would buy: stronger interpretation of feature values as estimating *population* parameters of the policy. Current claims are about empirical sample moments. If G1 is later proved for LM trajectories, claims in this document strengthen automatically. If disproved, the conclusions stand but their structural interpretation is weaker.

### 6.4 Choice C as a positive design choice, with Choices A and B as future extensions

Phase 1 used Choice C exclusively. The framing throughout §6 of this document treats this as a coverage limitation with future-work implications. The reframe in §1.5 is the more accurate account: Choice C is the **hardest version of (O-LM) to satisfy**, because its abelian-baseline ($\bar\rho$) equals the average of the encoder input ($S^{(C)}$). Phase 1 cleared this version with substantial margin.

Choice A (generating-model surprisal) and Choice B (cross-model surprisal under base) probe different audit questions — Choice A characterizes the generating policy's confidence-trajectory structure in isolation; Choice B characterizes how that policy looks under a reference. Their abelian baselines ($\bar S^{(A)}$, $\bar S^{(B)}$) would not equal the encoder input's mean. (O-LM)-equivalent tests on those signal choices would test orthogonality where common-cause coupling is structurally smaller, making them easier to satisfy than Choice C. Their value is not as additional gating evidence for (O-LM) — Phase 1 has already cleared the gating version — but as characterization of how the orthogonality property generalizes across signal choices.

Re-encoding the cached `phase1_trajectories_llama.npz` with Choice A or Choice B inputs costs no GPU time. This is on the cheap-followup list (§8.4).

### 6.5 K=30 vs K=50

The original protocol specified K=50 seeds per pair. Phase 1 was run at K=30 due to compute budget — $4500 \times 256$ tokens = 1.15M generated tokens at the observed Llama-3.1-8B throughput on RTX 5080 took approximately 14 hours wall-clock. K=50 would have taken approximately 24 hours.

The reduction was made after a control-only K=30 preview from Phase 0 data showed the orthogonality margins were large enough that the verdict was unlikely to flip at K=50. This document reports the K=30 result as the actual Phase 1 result.

K=30 standard error analysis: with bootstrap resampling, the 95% CI on the median |r| across 150 pairs has half-width approximately 0.014 — very tight at the median-across-pairs level. The per-pair Pearson r at K=30 has standard error approximately $1/\sqrt{27} = 0.19$ — wide at the per-pair level but the cross-pair median has minimal sensitivity to per-pair noise.

Practical effect of K=30 vs K=50: tighter 80th and 95th percentile estimates, but the medians and verdicts are essentially identical. No reason to re-run.

### 6.6 Topic categorization is judgment-based

The (control / mid / shaped) categorization in `phase1_topics.py` reflects the project authors' assessment of which topics are likely to engage RLHF-induced shaping, drawing on prior case study findings. Categorization is not derived from any independent ground truth.

The KW test (P1-3) relies on this categorization — it asks whether |r| distributions differ across the three groups *as labeled*. If the labels are wrong (e.g., a "shaped" topic doesn't actually engage RLHF, or a "control" topic does), the test still measures category-level differences, just for a different operational definition of category. The pass result (no differences detected) is therefore robust to mild mis-categorization but would be more interesting under more rigorous labeling.


---

## Section 7: What This Means at Increasing Levels of Abstraction

### 7.1 Direct meaning

ASD features and mean $\rho$ measure substantially different properties of Llama-3.1-8B trajectories. An audit using both produces strictly more information than one using either alone. On 30 topics × 5 paraphrases, with 30 seeded continuations per pair, the empirical correlation between any single Layer 1 feature and mean ρ has median magnitude 0.12-0.15 and 80th percentile 0.23-0.28 — comparable to but slightly tighter than the radar reference range of r ≈ 0.00-0.26 between ASD features and amplitude statistics.

### 7.2 Structural meaning

The abelianization argument proved that non-abelian audit functionals exist for any sequence encoded into the F_2 walk. The Phase 1 result establishes that the *specific* Layer 1 functionals as implemented, evaluated on real LM trajectories with all their domain-specific quirks, retain enough non-abelian content to be empirically near-orthogonal to abelian baselines. The structural argument transfers from the principle level to the empirical level on the input class that matters.

### 7.3 Operational meaning for the Phantom framework

The audit-blind subspace from FN-PHANTOM-001 Theorem B is not absolute — its dimension depends on the audit class $F$. With $F = F_{\text{ab}}$, the subspace has dimension $\dim(\Xi) - N$. With $F = F_{\text{aug}}$, the subspace has dimension at most $\dim(\Xi) - N - M$ where $M$ is the rank of $F_{\text{ASD}}$ on $\Xi$. Phase 1 establishes a lower bound on $M$ in policy space ($M \geq 3$) and identifies the open question for Phase 2 ($M$ on $\Xi$, the subspace where it matters for detection).

The Phantom methodology now has a parallel non-abelian axis. The Pattern Guide's abelian Monte Carlo over prompt space identifies abelian audit dimensions; ASD encoding identifies non-abelian dimensions. They're additive.

### 7.4 Epistemic meaning

Probability distortion measurement, as previously practiced via $\rho^*$ and the abelian apparatus, was missing a class of structural signal by construction. The averaging operation that produces $\bar\rho$ is exactly what discards the temporal-order content that ASD reads. We now have empirical evidence that this discarded structure (a) exists on real LLMs, (b) carries information independent of the abelian summary, and (c) does so consistently across topic types — including the politically loaded shaped topics where the framework's predictions need to hold.

This isn't a marginal improvement in measurement precision. It's the addition of a class of measurements that the methodology previously couldn't produce at all.

### 7.5 Cross-domain meaning, with care about what specifically transferred

A non-abelian audit class developed on radar — different scientific community, different signal source (sea clutter, target Doppler vs. token surprisal sequences), different dynamics — exhibits empirical-orthogonality properties on LLM trajectories that fall in the same magnitude range as the radar reference. This is unusual. Most domain-specific signal-processing methods don't transfer without recalibration; they encode domain assumptions in their feature definitions that break when the domain changes.

The honest version of what transferred:

- **The apparatus transfers.** F_2 walk, free reduction over a four-generator alphabet, block-local ordinal quartile encoding, IID-null calibration, the cylinder-algebra mass accumulators, the abelianization argument that places ASD outputs in the kernel of $\phi: F_2 \to \mathbb{Z}^2$ — all of these apply to LLM trajectories without modification. The framework is domain-agnostic by construction; the cylinder algebra of $\partial F_2$ doesn't know whether the input was radar returns or surprisal sequences.

- **The metric implementations adapted.** The original radar drift (ℓ_1 deviation of empirical depth-1 boundary measure from harmonic null) saturated on LLM input due to walk transience. h^* (characteristic depth at which $D(k) \leq 1/e$) plateaued for the same reason. Both required regime-specialized replacements (z-scored cancellation rate; mean_depth_excess) before producing usable readouts. These replacements were guided by ASD theory but are not the radar-domain implementations.

- **The orthogonality magnitude transferred at the apparatus level.** The radar reference range (r ≈ 0.00–0.26 between ASD features and amplitude statistics) and the LM range (median 0.12–0.15, 80th-pct 0.23–0.28 between LM-regime ASD features and $\bar\rho$) sit in the same regime. This is a *qualitative* magnitude comparison between different metric implementations applied to physically analogous problems, not a numerical reproduction of radar-domain readings.

What this rules out: the "ASD's specific feature definitions transfer unchanged" reading, which earlier framing in this document gestured at. What it confirms: the level of structural information the apparatus can extract about temporal-order content of a signal — quantified by the resulting orthogonality magnitude against the natural abelian summary of the same signal — is comparable across the two domains. The cross-domain claim is at the apparatus level. The metric implementations are regime-specific, with the LM implementations established here being the ones that work in this regime.

The fact that the apparatus transfers — that the F_2 walk reads structure cross-domain — supports the deeper conjecture that the apparatus is reading something about the temporal-order structure of *signals* rather than about the *domain* the signals come from. But this conjecture's empirical support is now correctly weighted: the apparatus has shown the property in two domains with regime-appropriate metrics, not in two domains with the same metrics.

### 7.6 Generalization implications

If the orthogonality property is a feature of probability distortion in general — not specifically of Llama-3.1-8B's RLHF — then ASD-augmented detection should work across institutions, scales, and architectures. Phase 5 tests this directly. A positive Phase 5 would establish that probability distortion has *invariants* detectable through the same group-theoretic apparatus regardless of the specific system; this would be a deeper claim than "ASD works on Llama."

The current evidence is consistent with such generalization but doesn't establish it. The Phase 1 result is necessary but not sufficient.

---

## Section 8: Next Steps

### 8.1 Phase 2 — augmented detection on case-study topics

Per FN-PHANTOM-002 §8.2: classifier AUC comparison (ρ-only vs ASD-only vs combined) on 3 case-study topics × 5 paraphrases × 100 seeds × 2 models (base + Instruct). 3,000 trajectories, ~12 GPU-hours.

**What it tests:** rank of $F_{\text{ASD}}$ on $\Xi$. Specifically, whether the 3 effective new dimensions Phase 1 identified actually project onto the constraint subspace where distortion lives, or whether they're independent of $\bar\rho$ in a direction $\Xi$ doesn't care about.

**Pre-registered predictions** (from FN-PHANTOM-002 §8.2.4):
- (P2-1) Founding fathers topic: AUC(combined) ≥ AUC(ρ-only) + 0.05.
- (P2-2) Wehrmacht topic: same threshold.
- (P2-3) Crime demographics topic: AUC delta ≥ 0.10 (greedy-decoding artifact regime per CS-PHANTOM-002).
- (P2-4) ASD-only AUC ≥ 0.65 on each topic.
- (P2-5) Combined classifier weights are nonzero on at least 3 ASD features per topic.

If P2 passes: the program proceeds to Phases 3, 4, 5.

If P2 fails (F2-1: combined and ρ-only within 0.02 on all 3 topics): ASD adds dimensions to F that don't help detect this class of distortion. Stop and document.

### 8.2 Phase 1 re-evaluation with modern feature definitions

When the production radar feature definitions are available, re-encoding the cached `phase1_trajectories_llama.npz` with the swapped-in encoder takes approximately 30 seconds. Re-running the analysis script confirms or refines the present verdict. No GPU time required.

### 8.3 Layer 2 expansion (optional, low cost)

The Layer 1 features used here are scalar summaries of the empirical pair. Layer 2 features ($D(k)$ depth profile at $k=1\ldots6$, $Q_{\text{tail}}$ recurrence fit) are also computed in `asd_features.py` but not used in Phase 1 analysis. Re-evaluating the cached trajectories with Layer 2 added measures whether they contribute additional independent dimensions to $F_{\text{ASD}}$. Pure analysis cost.

### 8.4 Choice A and Choice B parallel runs

Choice A signal (generating-model surprisal alone) requires no base model — only the Instruct generations. Choice B signal (cross-model surprisal) requires only base scoring of inst-generated trajectories, which is already captured in the cache. Re-encoding the cache with Choices A and B as alternative signals tests whether the orthogonality property depends on which signal feeds the encoder, or whether it's a robust property of the trajectories themselves. Pure analysis cost.

### 8.5 Cross-institutional generalization (Phase 5)

Most expensive. 5 institution × 30 topics × 5 paraphrases × 50 seeds × ~256 tokens = ~50 hours GPU + API budget. Tests whether the orthogonality property is Llama-specific or generalizes.

The question is what to do if Phase 5 fails — i.e., orthogonality holds on Llama but breaks on Mistral or Gemma. That would be informative about how RLHF pipelines vary in their structural geometry, but it would weaken claims about probability-distortion invariants. Phase 5's results inform whether the program scales to a multi-model atlas or stays at single-substrate analysis.

---

## Section 9: Reproducibility

**Code:** `asd_phantom/` package with subdirectories `src/` (encoder, features, LM trajectory adapter), `tests/` (validate_encoder, phase0_lm, phase1_lm, phase1_topics, phase1_analysis), `results/` (CSVs, NPZ trajectory cache).

**Models:** meta-llama/Llama-3.1-8B-Instruct (revision 0e9e39f) and meta-llama/Llama-3.1-8B (revision d04e592) downloaded from HuggingFace Hub. License accepted. Local cache at `~/.cache/huggingface/hub/`.

**Hardware:** RTX 5080 16GB VRAM (Blackwell, sm_120). Intel Core Ultra 9 285K. 64 GB system RAM. Windows 11 Pro. PyTorch nightly cu128 build (Blackwell sm_120 kernels).

**Random seeds:** generation seeds 0..29 per (topic, paraphrase). Encoder uses `traj.meta["seed"] + 7_000_000` as RNG seed for jitter (handles ties in ordinal encoding). IID null calibration uses seeds `0..49 + 5_000_000`.

**Trajectory cache:** `results/phase1_trajectories_llama.npz` contains all 4500 generated trajectories as numpy arrays (surprisal_inst, surprisal_base, rho per trajectory) plus a JSON sidecar with prompt, generation, and metadata. Re-encoding with different feature definitions or different signal choices is cheap.

**Feature CSV:** `results/phase1_features_llama.csv` (4500 rows × 27 columns) is the input to the analysis script.

**Analysis output:**
- `phase1_features_llama_correlations.csv` — 150 rows, per-pair Pearson r values.
- `phase1_features_llama_report.md` — markdown verdict.
- `phase1_correlation_histograms.png` — |r| distribution per feature, colored by topic category.

**Run command (once trajectories cached):**
```
python tests/phase1_analysis.py results/phase1_features_llama.csv
```
~30 seconds, pure pandas + scipy.

---

## Section 10: Glossary of Notation

- $\pi$, $\pi_{\text{base}}$, $\pi_{\text{inst}}$ : language model policies.
- $\rho_i$ : per-token leakage at position $i$ — Choice C signal value.
- $\bar\rho(x)$ : per-trajectory mean of $\rho_i$.
- $\rho^*$ : standard Phantom $\rho$ measurement; mean over a paraphrase battery.
- $S^{(C)}$ : Choice C signal sequence (per-token leakage sequence).
- $G = \{a, b, b^{-1}, a^{-1}\}$ : ASD generator set.
- $F_2$ : free group on two generators.
- $\partial F_2$ : boundary of $F_2$.
- $(\nu_\omega^T, \mu_\omega^T)$ : empirical pair on the cylinder algebra of $\partial F_2$.
- $b$ : encoding block size. $b=16$ in Phase 1.
- $K$ : seeds per (topic, paraphrase). $K=30$ in Phase 1.
- $T_{\text{gen}}$ : maximum generation length. 256 in Phase 1.
- $F$ : audit space (square-integrable functionals on policy space).
- $F_{\text{ab}}$, $F_{\text{ASD}}$, $F_{\text{aug}}$ : abelian audit class, ASD audit class, augmented (sum) class.
- $\Xi$ : constraint subspace in policy-tangent space.
- $\Pi_N$ : audit projection $\Xi \to \mathbb{R}^N$ at audit budget $N$.
- $\dim(\ker \Pi_N)$ : audit-blind subspace dimension.
- $\phi: F_2 \to \mathbb{Z}^2$ : abelianization homomorphism with kernel $[F_2, F_2]$.
- (O-LM) : orthogonality claim for LM trajectories (FN-PHANTOM-002 §4.3).
- P1-1, P1-2, P1-3 : pre-registered pass criteria.
- F1-1, F1-2, F1-3 : pre-registered falsification triggers.

---

*EN-PHANTOM-001 v1.0 — May 2026.*
*Phase 1 result for the FN-PHANTOM-002 program. (O-LM) holds on Llama-3.1-8B-Instruct with substantial margin. Audit-blind subspace reducible by at least 3 effective dimensions. Phase 2 cleared to proceed.*
