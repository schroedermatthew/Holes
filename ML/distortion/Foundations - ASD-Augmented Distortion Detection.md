---
doc_id: FN-PHANTOM-002
doc_type: "Foundations"
title: "ASD-Augmented Distortion Detection — Algebraic Symbolic Dynamics on Prompt Trajectories as a Non-Abelian Audit Class"
phantom_components: ["audit-blind-subspace", "four-object-decomposition", "rho-field", "induced-hole", "Bridge-B"]
asd_components: ["ASD walk on F_2", "empirical pair (nu_omega^N, mu_omega^N)", "boundary measure on partial F_2", "block-local ordinal quartile encoding", "drift", "h*", "timing_cv", "D(k) depth profile", "Q_tail(k)", "abelianization phi: F_2 -> Z^2", "non-amenability and paradoxical decomposition", "three-layer information hierarchy", "CUSUM construction"]
topics: ["non-abelian audit functions on language model trajectories", "ASD walk encoding of surprisal and per-token leakage sequences", "the orthogonality of ASD features to abelian rho-mean audit functions", "audit-blind dimension reduction via ASD augmentation", "natural-versus-induced hole signature in ASD coordinates", "ASD-CUSUM streaming detection of distortion engagement", "cross-institutional differential atlas", "testable experimental program"]
constraints: ["G1 convergence is open for continuous-state processes — applies in particular to LM surprisal sequences (ASD_RESEARCH.md §SD4.1)", "ASD-features-in-ML-pipelines is at Phase A sanity-check status (ASD_RESEARCH.md §RA5)", "block-local ordinal encoding requires block size b divisible by 4 (ASD §CC1 Level 2)", "audit-blind theorem B remains a fundamental lower bound; ASD changes what is in F, not the bound itself", "predictions hinge on the empirical claim that ASD features on LM trajectories are near-orthogonal to rho-mean — currently inferred from radar analogy (r 0.00–0.26)"]
mathematical_standard: "ASD §CC1 Hypothesis Levels 1-4; abelianization of F_2 with kernel [F_2, F_2]; SVD of distortion-to-function map; importance sampling; Wilson confidence intervals"
build_modes: ["paired sampling base + instruct at matched temperature", "block-local ordinal encoding of three signal types", "Layer 1 / Layer 2 / Layer 3 ASD feature extraction", "ASD-CUSUM streaming over generation positions"]
last_verified: 2026-05-02
audience: ["independent researchers", "AI safety practitioners", "AI assistants", "framework maintainers"]
status: "draft — theoretical apparatus and experimental program; Phase 0 not yet executed"

related_documents:
  - "Foundations - The Phantom Framework Mathematical Apparatus.md (FN-PHANTOM-001) — defines rho, the four-object decomposition, the audit-blind theorems"
  - "Handbook - Probability-Distortion Measurement Discipline.md (HB-PHANTOM-001) — methodology this document extends with non-abelian probes"
  - "Pattern Guide - Structured Monte Carlo for Probe Design.md (PG-PHANTOM-001) — abelian probe scaling; this document is the parallel non-abelian axis"
  - "Case Study - Induced-Hole Amplification.md (CS-PHANTOM-001) — provides the topics on which Phase 2 detection tests run"
  - "Case Study - The Greedy-Decoding Artifact.md (CS-PHANTOM-002) — establishes that trajectory-internal structure matters; ASD makes it measurable"
  - "Case Study - The Hemings Cross-Institutional Differential.md (CS-PHANTOM-003) — provides the cross-institutional anchor for Phase 5"
  - "ASD_RESEARCH.md — navigation index for the ASD program; this document instantiates §RA5 Phase B and §RA7 against the Phantom apparatus"
  - "ASD_FOUNDATIONS.md — the F_2 walk, empirical pair, cylinder algebra, boundary measure, three-layer hierarchy"
  - "ASD_VARIATIONAL_DETECTION.md — CUSUM construction, three-layer hierarchy, Conjectures S9.1 / S9.2"
  - "ASD_NONCOMMUTATIVE_LEARNING.md — fixed-encoding / learned-readout architecture (§RA5 Phase B)"

phantom_apparatus_used:
  established_results:
    - "audit-blind theorem B: any N-query audit misses dim(Xi) - N dimensions [E linearized regime; FN-PHANTOM-001 Part 9]"
    - "Theorem D SVD construction of optimal probes for a target k-dimensional concerning subspace [E linearized regime; FN-PHANTOM-001 Part 9]"
    - "four-object decomposition of distortion: retention beta^2, suppression (1-beta)^2, leakage beta(1-beta), total error 1-beta [E machine precision in toy; FN-PHANTOM-001 Part 1]"
    - "natural-vs-induced hole distinction: induced holes carry parametric memory of suppressed direction [conceptual; FN-PHANTOM-001 Part 10]"
  open_results:
    - "the orthogonality of ASD-derived audit functions to abelian rho-mean functions on LM trajectories [O — central testable claim of Phase 1]"
    - "ASD-feature rank on the constraint subspace Xi in the RLHF setup [O — measured in Phase 2]"
    - "Bridge B's mu^2(1-s^2) law manifest in ASD-feature-space coordinates [O]"

asd_apparatus_used:
  established_results:
    - "ASD features in kernel of abelianization phi: F_2 -> Z^2; non-amenability of F_2 forces deviations from harmonic measure to live in the predual of a type III_{1/3} algebra [E proved; ASD_FOUNDATIONS.md, ASD_QUANTUM_STOCHASTIC.md]"
    - "block-local ordinal quartile encoding: Level 2 hypothesis with provable d_g(1) = 0 baseline [E proved; ASD_FOUNDATIONS.md §CC1]"
    - "drift, h*, timing_cv, D(k), Q_tail(k) as continuous functionals on the empirical pair [E proved; ASD_FOUNDATIONS.md §9]"
    - "near-orthogonality of ASD features to amplitude-based statistics in radar: r ≈ 0.00-0.26 [E measured on IPIX; ASD_RESEARCH.md, ASD_VARIATIONAL_DETECTION.md §VD3]"
    - "six-coordinate atlas separates 52 process families without collision [E measured; ASD_RESEARCH.md §E8]"
    - "structured-background dominance: Pd 96% (m_ma_gen3) vs MF 1% on shared-texture rho=0.95 SNR=0.3 [E measured; ASD_RESEARCH.md §5.2]"
  open_results:
    - "G1 convergence of empirical pair for continuous-state processes — applies to LM surprisal sequences [O — primary bottleneck per ASD_RESEARCH.md §SD4.1]"
    - "ASD features in ML pipelines (§RA5 Phase A sanity check) — not yet executed [O]"
    - "ASD-as-ML-interpretability vocabulary mapping internal representations to (nu, mu) pair (§RA7) — purely conceptual [O]"
---

# Foundations - ASD-Augmented Distortion Detection — Algebraic Symbolic Dynamics on Prompt Trajectories as a Non-Abelian Audit Class

## Scope

This document develops the theoretical apparatus for detecting probability distortion in language models via Algebraic Symbolic Dynamics applied to prompt-conditioned generation trajectories, and specifies a sequenced experimental program with falsification criteria at each stage. The central theoretical claim is that ASD-derived audit functions are near-orthogonal to the abelian audit class used in standard $\rho$-mean measurement, and therefore add genuinely new dimensions to the audit space — reducing the audit-blind subspace specified by FN-PHANTOM-001 Theorem B by the rank of ASD on the constraint subspace.

The document threads two existing programs: the Phantom framework's apparatus for measuring institutional shaping (FN-PHANTOM-001 and the case studies) and the ASD program's apparatus for extracting non-commutative temporal structure from sequences (ASD_FOUNDATIONS.md and the directions enumerated in ASD_RESEARCH.md). Neither program needs modification. The document specifies the bridge: a trajectory encoding that maps language model generations into ASD walks, the formal claim about the resulting audit functions, and the experimental sequence required to verify the claim.

The document is written so that someone who has worked through FN-PHANTOM-001 and has at least skimmed ASD_FOUNDATIONS.md and ASD_RESEARCH.md can follow each step. Steps that look small but matter are written out. Where a result requires apparatus from elsewhere, the document points to the canonical reference rather than re-deriving.

## Not covered

- The mathematical apparatus of the four-object decomposition, Halmos two-projection geometry, or the audit-blind theorems themselves (see FN-PHANTOM-001 Parts 1, 2, 9).
- The mathematical apparatus of the F_2 walk, cylinder algebra, boundary measure, or non-amenability arguments (see ASD_FOUNDATIONS.md).
- Specific empirical measurements from the existing single-topic Phase E protocol (see the Case Studies).
- Implementation in any specific software framework — protocols are described in language-neutral terms.
- The §RA7 ASD-as-ML-interpretability vocabulary mapping internal representations to the full $(\nu, \mu)$ pair. That program is conceptual; this document instantiates only its prerequisites.

## Prerequisites

- FN-PHANTOM-001 Parts 1 (four-object decomposition), 4 ($\rho$ as leakage measurement), 9 (audit-blind theorems), 10 (natural vs induced holes).
- ASD_FOUNDATIONS.md §§1–9 (free group F_2, Cayley graph, boundary $\partial F_2$, cylinder algebra, ASD walk, empirical pair $(\nu_\omega^N, \mu_\omega^N)$, harmonic measure $\lambda$, deviation $\delta\nu$, three-layer information hierarchy as continuous functionals).
- ASD §CC1 hypothesis levels 1–4.
- Comfort with: log-probability evaluation under both base and instruction-tuned language models, paired-sampling protocols, Wilson 95% confidence intervals.
- *Helpful but not required:* reading ASD_VARIATIONAL_DETECTION.md §VD0–§VD2 for the CUSUM construction; familiarity with §RA5 (Noncommutative Learning).

## Foundations Card

**Topic:** A non-abelian audit class for the Phantom framework, defined by applying ASD's $F_2$ walk to language model generation trajectories, and the experimental program required to verify it adds detection dimensions beyond the abelian $\rho$-mean class.

**Why it matters:** The audit-blind theorem (FN-PHANTOM-001 Theorem B) sets a lower bound on the dimension of distortion any $N$-query audit can miss; that bound is taken over the audit functions $f \in F$ used. Standard methodology populates $F$ with abelian functionals — $\rho$-means, surprisal averages, signal rates over paraphrase batteries. ASD provides a class of audit functions that are provably orthogonal to the abelian class by the abelianization argument $\phi: F_2 \to \mathbb{Z}^2$ with kernel $[F_2, F_2]$, and empirically demonstrate near-orthogonality in radar ($r \approx 0.00$–$0.26$ to amplitude features). If the orthogonality property carries over to LM trajectories, the audit-blind subspace shrinks by $\mathrm{rank}(\mathrm{ASD}\;\text{on}\;\Xi)$.

**Key concepts:** The trajectory encoding map sending a sequence of real-valued per-token signals into an $F_2$ walk via block-local ordinal quartiling; the empirical pair $(\nu_\omega^N, \mu_\omega^N)$ as a non-abelian audit feature on the policy distribution; the orthogonality theorem (claimed by structure, tested empirically in Phase 1) saying ASD-functionals span dimensions of $F$ disjoint from abelian functionals; the natural-vs-induced hole signature mapped onto ASD's three-way process separation (depth-profile persistence, timing-clustering, IID baseline); ASD-CUSUM streaming change-point detection over generation positions.

**Mental model:** A generation $x = (t_1, \ldots, t_T)$ from a policy $\pi$ is a sequence of tokens. Attached to it are derived signals — surprisal under $\pi$, surprisal under a base model, per-token leakage $\rho_i = \log\pi_{\text{inst}}(t_i \mid t_{<i}) - \log\pi_{\text{base}}(t_i \mid t_{<i})$. Each is a real-valued time series. ASD encodes any real-valued time series into a walk on $F_2$ that captures the temporal-dependence structure orthogonal to the marginal distribution. Functionals of the resulting walk — drift, $h^*$, timing CV, $D(k)$, $Q_{\text{tail}}$ — are functionals of the policy distribution that depend on token *order* and therefore live outside the span of abelian functionals (which depend only on marginal or windowed-joint expectations symmetric in the sample). When training reshapes the policy, both classes of functionals respond, but they respond to different components of the reshaping.

**Common misconceptions:**
- "ASD features are just nonlinear functions of $\rho$ — eventually a deep enough abelian audit gets them." The abelianization argument is structural: the *order* of cancellations in the $F_2$ walk encodes information that no symmetric function of the token marginals reaches. The kernel $[F_2, F_2]$ is a free group of countably infinite rank — a strict orthogonal complement, not a higher-order Taylor remainder.
- "Surprisal and $\rho$ on a single trajectory are deterministic given the sample, so ASD just rediscovers them." The ASD encoding throws the marginal distribution away on purpose. Two trajectories with identical surprisal histograms but different surprisal *orderings* produce different ASD walks. The encoding is designed for exactly this.
- "ASD reduces the audit-blind dimension." Not in general. The audit-blind dimension is $\dim(\Xi) - \dim(F \cap \Xi)$. ASD adds functions to $F$. The *rank* of those functions on $\Xi$ — how many independent directions of constraint they distinguish — is what reduces the audit-blind dimension. That rank is empirically measurable; Phase 2 measures it.
- "The radar orthogonality automatically transfers to LM." The structural argument transfers; the magnitude is a separate empirical claim. Phase 1 measures it directly.

**Read next:** Section 1 introduces the trajectory encoding. Section 4 states the orthogonality claim formally. Section 8 begins the experimental program. The earliest concrete step is Phase 0 (Section 8.1), which is a one-day encoding sanity check.

## Table of Contents

- [Part I — Theoretical Apparatus](#part-i--theoretical-apparatus)
  - [Section 1: The Trajectory Encoding Map](#section-1-the-trajectory-encoding-map)
  - [Section 2: The Three Signal Choices and What Each Measures](#section-2-the-three-signal-choices-and-what-each-measures)
  - [Section 3: The Empirical Pair on Generation Trajectories](#section-3-the-empirical-pair-on-generation-trajectories)
  - [Section 4: The Orthogonality Claim, Formally](#section-4-the-orthogonality-claim-formally)
  - [Section 5: Audit-Blind Dimension Under ASD Augmentation](#section-5-audit-blind-dimension-under-asd-augmentation)
  - [Section 6: The Four-Object Decomposition's Per-Trajectory Realization](#section-6-the-four-object-decompositions-per-trajectory-realization)
  - [Section 7: Natural-vs-Induced Holes in ASD Coordinates](#section-7-natural-vs-induced-holes-in-asd-coordinates)
- [Part II — Testable Experimental Program](#part-ii--testable-experimental-program)
  - [Section 8.0: Phase 0 — Encoding Validation](#section-80-phase-0--encoding-validation)
  - [Section 8.1: Phase 1 — Orthogonality Test](#section-81-phase-1--orthogonality-test)
  - [Section 8.2: Phase 2 — Augmented Detection on Known-Shaped Topics](#section-82-phase-2--augmented-detection-on-known-shaped-topics)
  - [Section 8.3: Phase 3 — Natural-vs-Induced Separation](#section-83-phase-3--natural-vs-induced-separation)
  - [Section 8.4: Phase 4 — ASD-CUSUM Change-Point Detection](#section-84-phase-4--asd-cusum-change-point-detection)
  - [Section 8.5: Phase 5 — Cross-Institutional Differential Atlas](#section-85-phase-5--cross-institutional-differential-atlas)
- [Part III — Caveats, Sequencing, and Open Questions](#part-iii--caveats-sequencing-and-open-questions)
  - [Section 9: Phase Dependencies and Stop Conditions](#section-9-phase-dependencies-and-stop-conditions)
  - [Section 10: G1 Convergence and the Limiting-Object Question](#section-10-g1-convergence-and-the-limiting-object-question)
  - [Section 11: What Negative Results Would Mean](#section-11-what-negative-results-would-mean)
  - [Section 12: Open Theoretical Questions](#section-12-open-theoretical-questions)

---

# Part I — Theoretical Apparatus

## Section 1: The Trajectory Encoding Map

A language model policy $\pi(\cdot \mid \cdot)$ generates a token sequence $x = (t_1, t_2, \ldots, t_T)$ given a prompt $p$. Standard distortion measurement reads scalar functionals of the joint $(p, x)$ — most commonly $\rho^*(p) = \mathbb{E}_{x \sim \pi_{\text{inst}}}[\log \pi_{\text{inst}}(x \mid p) - \log \pi_{\text{base}}(x \mid p)]$ averaged over a paraphrase battery and seed set. The information lost by this averaging is the *temporal structure* of the per-token contributions to $\rho$.

The trajectory encoding map captures that structure by turning a per-token real-valued signal into a walk on $F_2$. Three steps:

**Step A — Signal extraction.** For a generation $x$, define a real-valued sequence $S(x) = (s_1, s_2, \ldots, s_T)$ where each $s_i$ is one of the three choices specified in Section 2. Each choice corresponds to a different audit question.

**Step B — Block-local ordinal quartile encoding** (ASD §CC1 Level 2). Partition the sequence into blocks of size $b$ where $b$ is divisible by 4. Within each block, rank the $b$ values $(s_{kb+1}, \ldots, s_{kb+b})$ from smallest to largest. The first quartile maps to generator $g_1$, the second to $g_2$, the third to $g_3$, the fourth to $g_4 = g_1^{-1}$ (using $G = G_2$, the four-generator set; see ASD_FOUNDATIONS.md §1). Concatenating across blocks produces a sequence $\omega = (g^{(1)}, g^{(2)}, \ldots, g^{(T)}) \in G^T$.

The block-local ordinal step is essential. It absorbs non-stationarity (positional variation in surprisal between function-word and content-word positions) by normalizing within each block. It also enforces the d_g(1) = 0 baseline used throughout ASD (each generator has equal frequency at depth 1 by construction; ASD §CC1 Level 2). It does not require the global signal distribution to be stationary, only that block-local ordinal statistics are well-defined — which they are for any sequence of reals with no exact ties (and ties can be broken with infinitesimal jitter).

**Step C — F_2 walk and empirical pair.** Apply free reduction to the generator sequence as it is consumed. At step $n$, the walk position is the reduced word formed by the prefix $(g^{(1)} g^{(2)} \cdots g^{(n)})$. Accumulate cylinder masses to form the empirical pair $(\nu_\omega^N, \mu_\omega^N)$ exactly as in ASD_FOUNDATIONS.md §6: $\nu_\omega^N$ is the empirical boundary measure (proportions of time the walk was in each cylinder), $\mu_\omega^N$ is the empirical interior mass (proportions weighted by stack depth).

The output is a pair of measures $(\nu_\omega^N, \mu_\omega^N)$ on the cylinder algebra of $\partial F_2$, defined per generation $x$. From this pair, all ASD features (drift, $h^*$, timing CV, $D(k)$, $H(k)$, $Y(k)$, $Q_{\text{tail}}$) are continuous functionals (ASD_FOUNDATIONS.md Proposition 9.1).

**Block size choice.** ASD has run with $b = 4, 8, 16, 64, 256$. The radar pipeline uses $b = 4$ for high temporal resolution (each token-position contributes to a quartile rank). For LM trajectories at sequence length $T \approx 100$–$1024$, $b = 4$ gives walk length $T$, which is sufficient for Layer 1 features but marginal for Layer 2 depth profiles. Phase 0 sets the operational $b$ for the LM setting empirically.

**A note on tokenization.** Different tokenizers produce different sequence lengths for the same string. Cross-model comparisons (Phase 5) must use a common tokenization or align via byte-pair offsets. The simplest and most rigorous approach: when comparing models with different tokenizers, recompute the per-token signal at the byte level via a re-tokenization step. This is the standard workaround and is documented in the Phase 5 protocol.

---

## Section 2: The Three Signal Choices and What Each Measures

The signal $S(x)$ entering the encoder determines what the resulting ASD features are functionals of. Three natural choices, each addressing a different audit question.

### 2.A — Generating-model surprisal

$$s_i^{\text{(A)}} = -\log \pi_{\text{gen}}(t_i \mid t_{<i}, p)$$

where $\pi_{\text{gen}}$ is whichever model generated $x$. This captures the trajectory through the generating model's own distribution. ASD features of $S^{(A)}$ are functionals of $\pi_{\text{gen}}$ alone — they characterize the *structure of how* the policy concentrates probability along the generation, not how that structure relates to a reference.

Use case: characterize a model's generation regime in isolation. Distinguish "always-confident" policies (low surprisal everywhere) from "varied" policies (high-variance surprisal trajectories). Phase 0 uses Choice A as a stationarity / convergence sanity check for the encoding itself.

### 2.B — Cross-model surprisal

$$s_i^{\text{(B)}} = -\log \pi_{\text{base}}(t_i \mid t_{<i}, p)$$

evaluated for *both* base-generated and instruct-generated continuations. This puts every trajectory in the same coordinate system — "how surprising under base." Distortion appears as systematic differences between $\{S^{(B)}(x_{\text{base}})\}$ and $\{S^{(B)}(x_{\text{inst}})\}$.

Use case: detect whether $\pi_{\text{inst}}$ is generating trajectories that base would assign systematically different surprisal structure to. The mean of $S^{(B)}$ recovers the standard $\rho$-related quantity; the ASD features of $S^{(B)}$ recover the temporal structure that the mean throws away.

### 2.C — Per-token leakage

$$s_i^{\text{(C)}} = \rho_i = \log \pi_{\text{inst}}(t_i \mid t_{<i}, p) - \log \pi_{\text{base}}(t_i \mid t_{<i}, p)$$

This is the $\rho$-field of FN-PHANTOM-001 §4 made into a per-token signal rather than a scalar summary. Choice C is the most direct theoretical match: ASD features of $S^{(C)}$ are functionals of the temporal structure of leakage itself, which is the operational realization of the four-object decomposition's leakage component (FN-PHANTOM-001 §1.3).

Use case: detect the temporal pattern of how leakage accumulates along a generation. Two trajectories with identical mean $\rho$ can have very different patterns: leakage commitment-then-coast (early high-$\rho$ tokens followed by zero), leakage clustering at content-loaded positions, leakage spread evenly across all positions. ASD features distinguish these.

### Choice and combination

The three choices are not redundant. Their ASD features measure different policy structure:

| Choice | What ASD-features measure |
|---|---|
| A | Internal structure of generating policy's confidence trajectory |
| B | Trajectory structure as scored by reference policy |
| C | Temporal structure of distortion accumulation |

For most experimental phases in Part II, Choice C is the primary signal (most theoretically grounded against the four-object decomposition). Choice B is useful as an interpretation cross-check. Choice A is primarily a sanity-check signal in Phase 0.

A combined feature vector concatenates ASD features from all three choices. This is more powerful than any single choice but consumes more compute (three forward passes per generation per evaluation model). The protocols below use Choice C unless otherwise specified.

---

## Section 3: The Empirical Pair on Generation Trajectories

For each generation $x$, the encoding of Section 1 produces an empirical pair $(\nu_x^T, \mu_x^T)$ on the cylinder algebra of $\partial F_2$. ASD theory (ASD_FOUNDATIONS.md §6, §7) addresses convergence of this pair to a limit $(\nu_\theta, \mu_\theta)$ as $T \to \infty$ under conditions called G1 and G2. For finite-state ergodic Markov chains and IID processes, G1+G2 is proved (ASD_RESEARCH.md §SD); for continuous-state processes — which language model trajectories are — G1 is open.

Three observations relax this concern for the present application.

**First, the empirical pair $(\nu_x^T, \mu_x^T)$ is well-defined for every finite sequence regardless of convergence.** It is a pair of probability measures on the cylinder algebra at every $T$. ASD features of the empirical pair are well-defined finite-sample quantities. The convergence question is whether population-level claims about $\nu_\theta$ are justified — but Phase 1 and Phase 2 work entirely with empirical-pair statistics across many sampled generations.

**Second, the audit-functional formulation does not require a limiting object.** What we need from ASD is a class of functionals $f_{\text{ASD}}: \Pi \to \mathbb{R}$ where $\Pi$ is the space of policies. Define $f_{\text{ASD}}(\pi) = \mathbb{E}_{x \sim \pi}[g_{\text{ASD}}(x)]$ where $g_{\text{ASD}}(x) = $ (any continuous functional of $(\nu_x^T, \mu_x^T)$ at fixed $T$, e.g., drift over $T$ tokens). This is well-defined for any $\pi$ and any $T$. The functional $f_{\text{ASD}}$ is a member of the audit space $F$ in the Phantom sense — exactly what the audit-blind theorem is taken over.

**Third, what depends on G1 is the population-level interpretation.** If we want to interpret an observed drift value as estimating "drift under $\pi$" with finite-sample error bounds, we need ergodic convergence. ASD provides this for known process classes (IID, finite Markov). For LM trajectories, we use empirical bootstrap over the sample of generations to compute confidence intervals. This sidesteps the G1 question for empirical work; it does limit how strongly the results can be interpreted as population-level statements.

The honest position: the apparatus is mathematically sound at the empirical level; G1 for LM trajectories is an open question (ASD §SD4.1) that bounds the strength of population-level claims.

---

## Section 4: The Orthogonality Claim, Formally

This section states the central theoretical claim of the document. The claim has a structural part (proved by the abelianization argument) and an empirical part (must be measured per application).

### 4.1 The audit space and abelian functionals

Following FN-PHANTOM-001 §9, the audit space $F$ is a subspace of $L^2$ functionals on policy space. A functional $f: \Pi \to \mathbb{R}$ is *abelian* if it can be written as
$$f(\pi) = \mathbb{E}_{x \sim \pi}[h(x)]$$
where $h$ is a function on token sequences invariant under any *symmetric* operation in the following sense: $h$ depends only on the *multiset* of (token, context, position) triples present in $x$, not on their *order* within $x$.

Standard $\rho$-mean audit functions are abelian. Surprisal averages are abelian. Signal rates over paraphrase batteries (count of "shaped output present" outcomes) are abelian. Any functional that aggregates per-position scores into a sum or expectation without using their sequential order is abelian.

The abelian audit class spans some subspace $F_{\text{ab}} \subseteq F$. The audit-blind theorem applied to $F_{\text{ab}}$ gives the standard methodology's lower bound.

### 4.2 ASD-derived functionals are non-abelian

The ASD encoding's $F_2$ walk applies free reduction sequentially: each new generator either extends the current word or cancels with the previous letter, with the cancellation event determined by whether the new letter is the inverse of the current rightmost letter. The resulting walk position depends on the *order* of generators, not just their multiset.

Formally: the encoding map $E: G^T \to F_2$ given by $E(g^{(1)}, \ldots, g^{(T)}) = $ (the reduced word for the prefix product) is *not* invariant under permutations of the input sequence. Cylinder masses computed along the walk depend on the visit history, which is order-dependent.

The abelianization $\phi: F_2 \to \mathbb{Z}^2$ has kernel $[F_2, F_2]$, the commutator subgroup, which is itself a free group of countably infinite rank (ASD_RESEARCH.md). Functionals computable on $\phi(\omega) \in \mathbb{Z}^2$ alone are functionals of the *abelianized* walk, equivalent to functionals of the multiset of generators. ASD features that distinguish words with the same abelianization — and most of them do — are functionals of the kernel $[F_2, F_2]$. They are structurally non-abelian.

This gives the *structural* part of the orthogonality claim: ASD-derived audit functionals reach into a subspace of $F$ that no abelian functional can reach. There is a subspace $F_{\text{ASD}} \subseteq F$ such that $F_{\text{ASD}} \cap F_{\text{ab}} = \{0\}$ holds for the *maximal* such pair, and the question is how much of $F_{\text{ASD}}$ is captured by the specific Layer 1 / Layer 2 / Layer 3 features actually computed.

### 4.3 The empirical part of the claim

The structural argument says: there exist non-abelian functionals computable from the ASD encoding. It does not say: the specific Layer 1 features (drift, $h^*$, timing CV) on LM trajectories are *empirically* uncorrelated with the abelian functionals one would actually compute (mean $\rho$, $\rho$ variance over paraphrases).

The radar evidence is supportive but not conclusive for the LM setting. In radar, ASD features have correlation $r \approx 0.00$–$0.26$ with CPI-averaged amplitude (ASD_RESEARCH.md). Amplitude is the canonical abelian functional in radar. The near-orthogonality is empirical. There is no general theorem saying ASD features must be near-orthogonal to abelian functionals on every input class — only that they *can* be (the structural argument permits it).

For LM trajectories, the empirical claim is:

> **(O-LM)** *On LM continuations sampled from $\pi_{\text{inst}}$ at temperature $T \in [0.7, 1.0]$ across the topic set used in the existing case studies, the Layer 1 ASD feature vector $(\text{drift}, h^*, \text{timing\_cv})$ computed on Choice C signal $S^{(C)}$ has correlation $|r| < 0.4$ with mean $\rho$ across at least 80% of (topic, paraphrase) pairs.*

The threshold $|r| < 0.4$ is chosen to match the upper end of the radar range with margin. The 80% coverage allows for some topics where $\rho$ and ASD features happen to align — this is expected; the claim is about the typical case, not universality.

Phase 1 of the experimental program (Section 8.1) measures (O-LM) directly. If (O-LM) holds, ASD features supply audit dimensions outside $F_{\text{ab}}$. If (O-LM) fails — correlations are systematically high — then the structural argument has produced features that are nominally non-abelian but empirically redundant, and the practical value of the augmentation is limited.

### 4.4 What orthogonality buys

If (O-LM) holds, the audit-blind dimension under the augmented audit class $F_{\text{aug}} = F_{\text{ab}} + F_{\text{ASD}}$ satisfies:

$$\dim(\Xi \cap F_{\text{aug}}^\perp) \leq \dim(\Xi \cap F_{\text{ab}}^\perp) - \mathrm{rank}_\Xi(F_{\text{ASD}})$$

where $\mathrm{rank}_\Xi(F_{\text{ASD}})$ is the dimension of the projection of $F_{\text{ASD}}$ onto $\Xi$. The reduction in audit-blind dimension is exactly the rank of ASD features on the constraint subspace.

This rank is empirically measurable by Phase 2: train a classifier to distinguish $\pi_{\text{inst}}$ continuations from $\pi_{\text{base}}$ continuations using only ASD features (no $\rho$); the rank of separable directions in ASD-feature space gives a lower bound on $\mathrm{rank}_\Xi(F_{\text{ASD}})$.

---

## Section 5: Audit-Blind Dimension Under ASD Augmentation

This section makes the dimensional argument explicit and identifies what it does and does not say.

### 5.1 Setup recap

From FN-PHANTOM-001 Part 9: the constraint subspace $\Xi$ is the image of the imposed RLHF constraint in policy-tangent space at the base policy. The audit-blind subspace at audit budget $N$ is the kernel of the audit projection $\Pi_N: \Xi \to \mathbb{R}^N$ where the columns of $\Pi_N$ are the responses of the $N$ audit functions to a basis of $\Xi$.

Theorem B states: for any choice of $N$ audit functions, $\dim(\ker \Pi_N) \geq \dim(\Xi) - N$. The bound is tight when the $N$ functions are chosen optimally per Theorem D's SVD construction.

### 5.2 Augmentation dimension count

When we augment with $M$ ASD functions, the new audit budget is $N + M$, and the new audit projection $\Pi_{N+M}: \Xi \to \mathbb{R}^{N+M}$ has the abelian function rows stacked with ASD function rows.

The dimensional bound becomes $\dim(\ker \Pi_{N+M}) \geq \dim(\Xi) - N - M$.

This is what one expects mechanically. The substantive question is whether the bound is *tight* under the augmentation — equivalently, whether the $M$ ASD rows are linearly independent of each other and of the $N$ abelian rows, evaluated on $\Xi$.

The orthogonality claim (O-LM) supports the linear independence of ASD rows from abelian rows. Whether the $M$ ASD rows are linearly independent of *each other* on $\Xi$ depends on which features are chosen. Layer 1 has three features (drift, $h^*$, timing CV); these are empirically nearly orthogonal in radar but might be correlated on LM. Layer 2 features ($D(k)$ and $Q_{\text{tail}}$ profiles) add further dimensions but with diminishing returns.

### 5.3 What this gives and does not give

The augmentation gives:
- A larger audit class $F_{\text{aug}}$ with rank $\leq N + M$ on $\Xi$
- A correspondingly smaller audit-blind subspace
- Equivalently: more directions in $\Xi$ that some audit function responds to

The augmentation does not give:
- A method to detect distortion in directions of $\Xi$ that *no* audit function responds to. The audit-blind subspace shrinks but remains. ASD does not violate Theorem B; it changes what is in $F$.
- A guarantee that the new audit-detected directions are concerning ones. Theorem D's SVD construction gives the best $N$ probes for a target concerning subspace. ASD adds dimensions; it does not automatically target concerning subspace dimensions.
- A reason to drop abelian probes. The augmentation is additive: $F_{\text{aug}}$ contains both. Phase 2's classifier comparison (ASD-only vs $\rho$-only vs combined) measures how much each contributes.

### 5.4 The interaction with Theorem D

Theorem D constructs the optimal $N$ abelian probes for a target $k$-dimensional concerning subspace via SVD of the abelian distortion-to-function map. The same construction applies when the audit space includes ASD features: SVD of the augmented distortion-to-function map yields the optimal $N+M$ probes.

In practice, optimal probe construction over $F_{\text{aug}}$ is more complex than over $F_{\text{ab}}$ because ASD features are computed from generations rather than queried directly — there is no closed-form linear response of the ASD audit value to a perturbation in $\Xi$. This complicates the SVD construction. The Phase 2 protocol below uses a fixed feature set rather than optimal probe selection; whether the optimal-probe-construction extension is feasible is open and is registered in Section 12.

---

## Section 6: The Four-Object Decomposition's Per-Trajectory Realization

Section 4 framed ASD as adding to the audit space $F$. This section connects ASD specifically to the four-object decomposition (FN-PHANTOM-001 §1.3, §4) — retention $\beta^2$, suppression $(1-\beta)^2$, leakage $\beta(1-\beta)$, total error $1-\beta$.

The four-object decomposition is normally interpreted at the policy level: each of $\beta^2, (1-\beta)^2, \beta(1-\beta), 1-\beta$ is a population-level scalar derived from the principal angle between the constraint and query subspaces. ASD applied to Choice C signal $S^{(C)}$ (per-token leakage) produces functionals of the *temporal realization* of the leakage object on individual generations.

### 6.1 Per-trajectory leakage signal

The signal $S^{(C)}(x) = (\rho_1, \ldots, \rho_T)$ is the per-token decomposition of the trajectory's total log-density-ratio:
$$\sum_{i=1}^T \rho_i = \log \pi_{\text{inst}}(x \mid p) - \log \pi_{\text{base}}(x \mid p)$$

The mean $\bar\rho = T^{-1} \sum_i \rho_i$ corresponds (in expectation over $x \sim \pi_{\text{inst}}$, via the Fisher-tangent linearization of FN-PHANTOM-001 §2) to the leakage scalar $\beta(1-\beta) \cdot \mu^2 (1-s^2)$ from Bridge B. This is the abelian audit value.

The temporal *structure* of $S^{(C)}$ — how the $\rho_i$ are distributed across positions — is invisible to $\bar\rho$. ASD features extract that structure.

### 6.2 Three signatures of the same scalar leakage

Consider three hypothetical generations all with $\bar\rho = 0.5$:

- **Trajectory L1** (uniform leakage): $\rho_i = 0.5$ for all $i$. Surprisal under base is 0.5 nats higher than under instruct at every position. This is the signature of a uniform reweighting — the policy's distortion is structurally invariant across positions.

- **Trajectory L2** (commitment leakage): $\rho_i = 5$ for $i = 1, \ldots, 10$ and $\rho_i = 0$ for $i = 11, \ldots, 100$. The first ten tokens carry all the distortion; the rest match base. This is the signature of an *induced* hole — the model commits to a shaped framing early and then proceeds normally, with parameters carrying the directional memory only at the commitment positions.

- **Trajectory L3** (clustered leakage): $\rho_i \in \{0, 4\}$ randomly with mean 0.5. The distortion is bursty, hitting a small fraction of high-$\rho$ positions and zero elsewhere. This is the signature of *local* distortion — distortion engages on specific token-types (perhaps proper nouns, named groups) without affecting the broader trajectory.

ASD features distinguish these:
- **Drift**: low for L1, moderate for L2 (early-trajectory signature dominates), high for L3 (cancellation events cluster).
- **timing_cv**: very low for L1 (no temporal variation), very high for L2 (one transition), moderate for L3 (clustering).
- **$D(k)$ depth profile**: flat for L1, peaked at low $k$ for L2 (early-commitment), peaked at high $k$ for L3 (deep cancellation activity at burst positions).

The decomposition into $(\beta^2, (1-\beta)^2, \beta(1-\beta), 1-\beta)$ at population level recovers the same $\bar\rho$ for all three. The ASD signature distinguishes them. This is the operational content of "ASD measures the temporal structure that the abelian decomposition averages over."

### 6.3 Bridge B's $\mu^2(1-s^2)$ in ASD coordinates

Bridge B (FN-PHANTOM-001 §4.2) gives leakage as $\beta(1-\beta) \cdot \mu^2(1-s^2)$, where $\mu$ is constraint severity and $s$ is alignment of reward to query. This is a scalar prediction. Three sub-claims would specialize it to ASD:

- (B-ASD-1) $\mu$ scaling: as constraint severity $\mu$ increases, the *magnitude* of the ASD signal in $\rho$-trajectories increases proportionally to $\mu^2$.
- (B-ASD-2) $s$ scaling: the *fraction* of trajectories in the high-leakage ASD regime scales with $(1-s^2)$.
- (B-ASD-3) ASD coordinates of leakage events should approximately factor: the ASD signature is a function of the constraint-query subspace geometry $(s)$, not of the magnitude $\mu$, while magnitude only scales the overall strength.

Verifying (B-ASD-1), (B-ASD-2), (B-ASD-3) requires varying $\mu$ and $s$ — possible only in a controlled training setup, not on production models. They are listed in Section 12 as open problems for the toy-system extension of the program.

---

## Section 7: Natural-vs-Induced Holes in ASD Coordinates

FN-PHANTOM-001 §10 distinguishes natural holes (data was never present; the model is constructing) from induced holes (data was present; training suppressed it; parameters carry directional memory of the suppression). The signatures differ in principle but are difficult to distinguish in practice without direct corpus access or interpretability tools.

ASD provides a candidate signature distinction *from generation behavior alone*.

### 7.1 The hypothesized mapping

The hypothesis is that the three regimes of ASD's process-family separation (ASD_RESEARCH.md §RA1) — depth-profile persistence, timing-clustering, IID-like baseline — map onto distinct distortion regimes:

| ASD signature | Hypothesized regime | Reasoning |
|---|---|---|
| Persistence in depth profile (AR(1) / FGN-like) | Stable shaped mode; commitment to a constraint subspace direction | Parameters carrying memory of suppressed direction produce *autocorrelated* leakage events as the model navigates the shaped subspace — extending a shaped framing once entered |
| Volatility clustering in timing (ARCH-like) | Bursty shaping at trigger tokens; constraint engages selectively | RLHF rewards engage on specific concept tokens (named groups, particular topics); leakage clusters at those positions and is near-zero elsewhere |
| IID-like across all features | Natural hole, or no engaged constraint | Without a directional pull, leakage events have no temporal correlation — what you see is sampling noise |

This hypothesized mapping is theoretical. It is grounded in the parametric-memory mechanism of induced holes (parameters that retain the suppressed direction produce systematic temporal structure when the direction is approached) but is not derivable from first principles within ASD or Phantom alone. Phase 3 of the experimental program tests it directly.

### 7.2 What this would buy

If the mapping holds, distinguishing natural from induced holes from generation behavior alone becomes routine: paired-sample ASD on a target topic, classify by ASD signature regime. This obviates the requirement for direct corpus access or interpretability tools that the FN-PHANTOM-001 §10 distinction otherwise needs.

### 7.3 The honest framing

The mapping is a hypothesis about the *empirical correspondence* between two structural classifications (ASD process-family regime; Phantom natural-vs-induced hole). Neither side derives the other. The experimental test in Phase 3 has clear pass/fail criteria. The most likely outcome is partial mapping: persistence-signature corresponds to induced; ARCH-signature mixes induced and natural; IID-baseline corresponds to natural. Even partial mapping is informative.

---

# Part II — Testable Experimental Program

The program is sequenced. Each phase has concrete pass/fail criteria. Failure of an earlier phase changes what later phases can claim. Phase 0 must pass before Phase 1; Phase 1 must pass before Phase 2 is interpretable; Phase 2's results determine whether Phase 3, 4, 5 are worth running. Section 9 specifies the dependencies and stop conditions.

Across all phases, the model substrate is Llama-3.1-8B-base and Llama-3.1-8B-Instruct, with cross-institutional comparisons in Phase 5 extending to Mistral-7B, Gemma-7B, and (subject to API access) Claude / GPT-4 via signal-based estimation. Compute estimates assume an RTX 4090 or equivalent (24 GB VRAM); 16 GB cards (RTX 5080) work for Llama with paged loading.

## Section 8.0: Phase 0 — Encoding Validation

**Hypothesis.** The trajectory encoding (Section 1) applied to Choice C signal $S^{(C)}$ produces stable ASD features across seeds for fixed (model, prompt, paraphrase, temperature). "Stable" means the coefficient of variation of each Layer 1 feature across $K$ seeds is bounded.

**Why this comes first.** Before any claim about distortion detection, the encoding itself must produce features that aren't noise. A feature with seed-CV of 1.0 has signal-to-noise ratio 1; comparing groups requires tighter stability. Phase 0 establishes the stability budget that subsequent phases work within.

### 8.0.1 Setup

- Models: Llama-3.1-8B-Instruct (single model; both forward passes against the same model — for Choice C, this requires also loading Llama-3.1-8B-base, but in Phase 0 only the Instruct generations are needed for Choice A; Choice C is added in Phase 0.B below).
- Topics: 10 topics drawn from a low-distortion control set (e.g., basic chemistry, basic mechanics, basic geography). These are topics where prior expectation is that minimal RLHF shaping engages.
- Paraphrases: 3 paraphrases per topic.
- Temperature: $T = 0.7$.
- Seeds: $K = 30$ per (topic, paraphrase) pair.
- Generation length: $T_{\text{gen}} = 256$ tokens.
- Block size: sweep $b \in \{4, 8, 16\}$ to determine operational $b$ for the LM regime.

### 8.0.2 Procedure (Phase 0.A — Choice A signal)

For each (topic, paraphrase, seed):
1. Generate continuation $x$ from Llama-3.1-8B-Instruct.
2. Compute Choice A signal $s_i^{(A)} = -\log \pi_{\text{inst}}(t_i \mid t_{<i})$ for $i = 1, \ldots, T_{\text{gen}}$.
3. For each block size $b \in \{4, 8, 16\}$: encode $S^{(A)}$ via block-local ordinal quartiling, compute Layer 1 ASD features.

For each (topic, paraphrase, $b$): compute coefficient of variation of each Layer 1 feature across $K$ seeds.

### 8.0.3 Procedure (Phase 0.B — Choice C signal)

Same as 8.0.A, but compute $s_i^{(C)} = \log \pi_{\text{inst}}(t_i \mid t_{<i}) - \log \pi_{\text{base}}(t_i \mid t_{<i})$. Both Instruct (for generation and for $\pi_{\text{inst}}$ evaluation) and base (for $\pi_{\text{base}}$ evaluation) loaded; if VRAM-limited, run base-evaluation and Instruct-evaluation as sequential passes with checkpointed activations.

### 8.0.4 Predictions (with thresholds)

- (P0-1) For Choice A signal at block size $b = 4$: median CV across (topic, paraphrase, feature) combinations is $< 0.30$. The 95th percentile of the CV distribution is $< 0.50$.
- (P0-2) For Choice C signal at block size $b = 4$: same thresholds as P0-1 (CV is dominated by the encoding's stability properties, not by signal magnitude).
- (P0-3) Block-size sweep: CV decreases or is stable as $b$ increases from 4 to 16. (Larger blocks average out more noise.)
- (P0-4) The ratio of between-topic variance to within-topic-across-seed variance is $> 5$ for all three Layer 1 features. (This is the analysis-of-variance check that features distinguish topics at all.)

### 8.0.5 Falsification

Phase 0 fails if:
- (F0-1) Median CV exceeds 0.50 for any Layer 1 feature at every tested block size.
- (F0-2) Block-size sweep shows CV *increasing* with $b$ (would indicate the encoding is averaging out signal, not noise).
- (F0-3) Between-topic to within-topic variance ratio is $< 2$ — the features cannot distinguish topics, ruling out their use for distortion detection on topics.

### 8.0.6 Compute estimate

- Generations: 10 topics × 3 paraphrases × 30 seeds = 900 generations × $T_{\text{gen}}=256$ tokens. At 60 tok/s on RTX 5080, ≈ 64 minutes of generation.
- Forward passes for $\pi_{\text{base}}$ evaluation (Choice C only): 900 prompts × ~256 tokens. ≈ 60 minutes.
- ASD feature computation: negligible (<1 minute total via standard ASD pipeline).
- Total: ~3 hours including overhead.

### 8.0.7 Output

A short technical report with: CV table by (feature, block size, signal choice); ANOVA decomposition; recommendation of operational $(b, \text{signal choice})$ combination for Phases 1–5. A pass means proceeding to Phase 1 with the recommended configuration. A failure triggers Section 11 — what negative results mean.

---

## Section 8.1: Phase 1 — Orthogonality Test

**Hypothesis.** ASD Layer 1 features on Choice C signal are near-orthogonal to mean $\rho$ across (topic, paraphrase) pairs. Specifically, claim (O-LM) of Section 4.3.

**Why this is the gating result.** The structural argument of Section 4.2 says ASD-functionals can reach into a non-abelian audit subspace. The empirical claim is that for actual LM trajectories, the Layer 1 features used in practice do reach there. If they do not — if they are empirically nearly proportional to $\bar\rho$ — then the augmentation gives no new audit dimensions in practice, and the ASD-augmented program offers no advantage over the abelian baseline.

### 8.1.1 Setup

- Models: Llama-3.1-8B-base and Llama-3.1-8B-Instruct.
- Topics: 30 topics — 10 from the Phase 0 control set, 10 from documented-shaped topics (founding fathers, Wehrmacht, crime demographics, and 7 others from the case-study topic catalog), 10 from a "mid" set (controversial but not central to RLHF shaping signals: nuclear power, GMOs, electoral system reform, etc.).
- Paraphrases: 5 per topic, totaling 150 (topic, paraphrase) pairs.
- Temperature: $T = 0.7$.
- Seeds: $K = 50$ per pair.
- Configuration: operational $(b, \text{signal})$ from Phase 0; default $(b=4, \text{Choice C})$.

### 8.1.2 Procedure

For each (topic, paraphrase) pair:
1. Generate $K$ continuations from Llama-3.1-8B-Instruct.
2. Compute $\bar\rho_k$ for each continuation $k$ (mean per-token leakage).
3. Compute Layer 1 ASD feature vector $\mathbf{f}_k = (\text{drift}_k, h^*_k, \text{timing\_cv}_k)$ for each continuation $k$ on its Choice C signal.
4. Compute Pearson correlation $r$ between $\bar\rho_k$ and each component of $\mathbf{f}_k$ across $k = 1, \ldots, K$. This produces three correlations per (topic, paraphrase) pair.

Across all 150 pairs, each of the three Layer 1 features yields a distribution of 150 correlation values.

### 8.1.3 Predictions (with thresholds)

- (P1-1) Across the 150 pairs, median $|r|$ for each Layer 1 feature is $< 0.30$. The 80th percentile is $< 0.50$. (Matches the radar reference range with margin.)
- (P1-2) The three Layer 1 features have pairwise correlations on the same data with median $|r| < 0.60$. (Internal redundancy within ASD itself is bounded.)
- (P1-3) Correlation magnitude does not differ systematically across the three topic groups (control / mid / shaped). (Orthogonality is a structural property of the encoding, not a topic-specific artifact.)

### 8.1.4 Falsification

Phase 1 fails if:
- (F1-1) Median $|r|$ for any Layer 1 feature exceeds 0.50 across the 150 pairs.
- (F1-2) The 80th percentile of $|r|$ for any feature exceeds 0.70.
- (F1-3) Strong systematic trend across topic groups (e.g., shaped topics show $|r| > 0.7$ while control topics show $|r| < 0.3$ — would indicate that the orthogonality breaks specifically where it matters most).

### 8.1.5 Compute estimate

- Generations: 30 topics × 5 paraphrases × 50 seeds = 7,500 generations × 256 tokens. At 60 tok/s, ≈ 9 hours.
- $\pi_{\text{base}}$ evaluation passes for Choice C: ≈ 9 hours.
- ASD feature computation: ~2 minutes.
- Correlation analysis: <1 minute in pandas.
- Total: ≈ 20 hours of GPU time.

### 8.1.6 Statistical analysis

For each Layer 1 feature, report the empirical distribution of $|r|$ across pairs as median, IQR, 80th percentile, 95th percentile, and a histogram. Compare the distribution to the radar reference range $[0.00, 0.26]$.

For pairwise feature correlations, report a 3×3 matrix of medians.

For topic-group differences, run a Kruskal-Wallis test on the 150-value distributions split by topic group. Report the test statistic and p-value; if $p < 0.01$, examine which group differs.

### 8.1.7 Output

A correlation atlas: 150 rows × 3 columns of $|r|$ values, plus the diagnostic plots and Kruskal-Wallis results. A pass means (O-LM) holds and Phase 2's classifier comparisons are interpretable. A fail triggers Section 11.

### 8.1.8 Variant: Layer 2 features

If Layer 1 passes, optionally extend the analysis to Layer 2 features ($D(k)$ at $k \in \{1, \ldots, 6\}$, $Q_{\text{tail}}$ at $k \in \{1, \ldots, 6\}$) on the same data. This is informational rather than gating: knowing the orthogonality structure of Layer 2 features informs Phase 2's feature-vector design.

---

## Section 8.2: Phase 2 — Augmented Detection on Known-Shaped Topics

**Hypothesis.** A classifier with ASD features added to $\bar\rho$ achieves better separation of $\pi_{\text{inst}}$-generated continuations from $\pi_{\text{base}}$-generated continuations than $\bar\rho$ alone, on at least 2 of 3 known-shaped topics.

**Why this matters.** Phase 1 establishes that ASD features are not redundant with $\bar\rho$. Phase 2 establishes that the non-redundancy translates to detection power on the topics the case studies have already characterized. This is the operational claim: the augmentation buys *something* in practice, not just structurally.

### 8.2.1 Setup

- Models: Llama-3.1-8B-base, Llama-3.1-8B-Instruct.
- Topics: 3 from the case studies — founding fathers (CS-PHANTOM-001), Wehrmacht (CS-PHANTOM-001), crime demographics (CS-PHANTOM-002 / CS-PHANTOM-001 spectrum).
- Paraphrases: 5 per topic, the same paraphrases used in the source case studies.
- Temperature: $T = 0.7$.
- Seeds: $K = 100$ per (topic, paraphrase, model) — 100 base continuations and 100 instruct continuations per pair.
- Total dataset: 3 topics × 5 paraphrases × 100 seeds × 2 models = 3,000 generations.

### 8.2.2 Feature sets

Three feature sets are defined per generation:
- **Set A ($\rho$-only):** $\mathbf{f}^A = (\bar\rho, \text{Var}_i \rho_i)$ — mean and variance of per-token leakage. Two features.
- **Set B (ASD-only):** $\mathbf{f}^B = (\text{drift}, h^*, \text{timing\_cv}, D(1), D(2), D(3), D(4), Q_{\text{tail}}(1), Q_{\text{tail}}(2), Q_{\text{tail}}(3))$ — Layer 1 + selected Layer 2. Ten features.
- **Set C (combined):** $\mathbf{f}^C = \mathbf{f}^A \oplus \mathbf{f}^B$ — concatenation. Twelve features.

### 8.2.3 Procedure

For each topic:
1. Generate 100 base + 100 instruct continuations per paraphrase, totaling 1,000 continuations per topic.
2. Compute all three feature sets per continuation.
3. For each feature set, train a logistic-regression classifier with target = "instruct" (1) vs "base" (0). Use 5-fold cross-validation across paraphrases (each fold holds out one paraphrase as test).
4. Report: AUC, accuracy at 0.5 threshold, signal rate at false-positive rate 0.05 (FPR=0.05).

### 8.2.4 Predictions (with thresholds)

- (P2-1) On the founding fathers topic: AUC of Set C is at least 0.05 higher than AUC of Set A. (Founding fathers exhibits clean induced-hole signature in CS-PHANTOM-001; expect ASD adds value.)
- (P2-2) On the Wehrmacht topic: same as P2-1, AUC gain $\geq 0.05$.
- (P2-3) On the crime demographics topic: AUC of Set C is at least 0.10 higher than AUC of Set A. (Crime demographics exhibits the greedy-decoding-artifact regime per CS-PHANTOM-002; the trajectory structure is exactly what ASD targets, so larger gain expected.)
- (P2-4) Set B alone (ASD without $\rho$) achieves AUC at least 0.65 on each topic. (ASD features by themselves carry detectable signal.)
- (P2-5) The classifier weights of Set C show non-zero coefficients on at least 3 ASD features per topic. (The augmentation is using ASD features, not just $\bar\rho$ within the Set C wrapper.)

### 8.2.5 Falsification

Phase 2 fails if:
- (F2-1) Set C and Set A have AUC within 0.02 of each other on all three topics (no detection improvement from augmentation).
- (F2-2) Set B alone produces AUC below 0.55 on all three topics (ASD features carry essentially no signal).
- (F2-3) Adding ASD features to $\rho$ degrades performance (Set C has lower AUC than Set A) on any topic — would indicate ASD features are pure noise that overfits.

A weaker pass: if (P2-1), (P2-2), (P2-3) hold on 2 of 3 topics but not all 3, the result is recorded as partial success and Phase 3 proceeds with caveats.

### 8.2.6 Compute estimate

- Generations: 3 topics × 5 paraphrases × 100 seeds × 2 models = 3,000 generations × 256 tokens. At 60 tok/s, ≈ 3.6 hours of generation (assuming each model contributes ~1.8 hours).
- $\pi_{\text{base}}$ and $\pi_{\text{inst}}$ evaluation passes for the cross-evaluation needed for Choice C: a pass per generation per evaluator model, ≈ 7 hours.
- ASD feature computation: ~2 minutes.
- Classifier training and CV: <5 minutes in scikit-learn.
- Total: ≈ 12 hours.

### 8.2.7 Statistical analysis

Each AUC is reported with 95% bootstrap CI from 1000 resamples. Comparisons across feature sets use the DeLong test for paired AUC differences. Coefficient interpretation for Set C uses standardized features so coefficient magnitudes are comparable.

The three topics are reported separately, not pooled. Pooling would assume the classifier transfers across topics; Phase 2 does not test transfer. The $K=100$ seeds per pair give Wilson 95% intervals on signal rates of width $\sim \pm 0.05$ at moderate signal rates.

### 8.2.8 Output

A 3-row × 3-column AUC table (topics × feature sets) with 95% CIs and DeLong p-values; classifier weight diagrams for Set C per topic; signal rates at FPR=0.05 per (topic, feature set). A pass means ASD-augmented detection is empirically validated on the case-study topics. A fail triggers Section 11.

---

## Section 8.3: Phase 3 — Natural-vs-Induced Separation

**Hypothesis.** The ASD signature regime (depth-profile persistence, timing-clustering, IID-baseline) on Choice C signal correlates with the natural-vs-induced classification of distortion type per FN-PHANTOM-001 §10.

**Why this matters.** If supported, this gives a generation-only method for distinguishing natural from induced holes. The operational case-study toolkit currently lacks such a method — the distinction is either inferred from corpus access (rare) or asserted from prior expectation. Phase 3 tests whether ASD provides a discriminating signal.

### 8.3.1 Setup

- Models: Llama-3.1-8B-base, Llama-3.1-8B-Instruct.
- Topics: 12 topics in 4 categories of 3 each:
  - **Category I — Likely induced holes:** founding fathers, Wehrmacht, crime demographics. Identified in case studies as exhibiting parametric memory of suppressed framings.
  - **Category II — Likely natural holes:** obscure technical fields where training data was minimal (e.g., specific papers in algebraic K-theory; specific 18th-century ship-rigging terminology; specific Mongolian morphology).
  - **Category III — No-hole controls:** common factual topics (basic geography, basic chemistry, common historical dates).
  - **Category IV — Disputed:** topics where the natural-vs-induced classification is genuinely uncertain (questions about contested historical events; questions about contested scientific consensus topics).
- Paraphrases: 3 per topic.
- Temperature: $T = 0.7$.
- Seeds: $K = 50$ per (topic, paraphrase).

### 8.3.2 Procedure

1. Generate $K=50$ instruct continuations per (topic, paraphrase) pair on all 12 topics. Compute Choice C signal and Layer 1+2 ASD features.
2. For each generation, classify into one of three ASD signature regimes by feature thresholds:
   - **Persistence:** $D(1) > D_{\text{persist}}^*$ AND $h^* > h^*_{\text{persist}}$ (specific thresholds set in Phase 3.0 calibration; defaults based on radar AR(1) ρ=0.5–0.9 ranges).
   - **Timing-clustering:** $\text{timing\_cv} > \text{cv}_{\text{cluster}}^*$ AND $D(1) < D_{\text{cluster}}^*$.
   - **IID-baseline:** all features within $\pm 0.5\sigma$ of the IID null distribution from radar (ASD_RESEARCH.md §E10 reference).
3. For each topic, compute the regime distribution across (paraphrase × seed).
4. For each topic, identify the modal regime.

### 8.3.3 Predictions (with thresholds)

- (P3-1) Category I topics have modal regime = persistence-or-timing-clustering on at least 2 of 3 topics.
- (P3-2) Category II topics have modal regime = IID-baseline on at least 2 of 3 topics.
- (P3-3) Category III topics have modal regime = IID-baseline on at least 2 of 3 topics.
- (P3-4) Category IV topics distribute across regimes (no single mode dominates) — this is consistent with the categorization being uncertain.
- (P3-5) Categories I and II are statistically distinguishable: a 2-sample Kolmogorov-Smirnov test on the regime distributions yields $p < 0.01$.

### 8.3.4 Falsification

Phase 3 fails if:
- (F3-1) Categories I and II have indistinguishable regime distributions (KS test $p > 0.20$).
- (F3-2) Category III shows non-IID regimes more often than IID-baseline. (Would indicate the IID-baseline claim is wrong even on control topics, undermining the regime mapping entirely.)
- (F3-3) Category I shows IID-baseline modal — would indicate the persistence-and-timing-clustering signature does not in fact correspond to induced holes.

A partial pass: if categories I and III are distinguishable but I and II are not, the persistence/timing-clustering signature distinguishes "shaped" from "no-shape" but not natural-from-induced.

### 8.3.5 Compute estimate

- Generations: 12 topics × 3 paraphrases × 50 seeds × 1 model = 1,800 generations × 256 tokens. ≈ 2.1 hours.
- $\pi_{\text{base}}$ evaluation: ≈ 2.1 hours.
- ASD feature computation: ~2 minutes.
- Total: ≈ 5 hours.

### 8.3.6 Statistical analysis

For each topic, the regime distribution is a 3-cell categorical with $N = 150$ samples, giving Wilson 95% intervals on regime fractions of width $\sim \pm 0.08$. KS tests are done on the joint Layer 1+2 feature distributions, not on the regime classifications, to avoid loss of information at the categorization step.

The threshold values $D_{\text{persist}}^*, h^*_{\text{persist}}, \text{cv}_{\text{cluster}}^*$ require calibration. Phase 3.0 (calibration sub-phase): generate IID-process and AR(1) reference walks of matched length, fit threshold values that give 90% correct classification on the synthetic references. Use these for Phase 3.

### 8.3.7 Output

A 12-row × 3-column regime distribution table (topics × regimes), with category labels; KS test results between category pairs; threshold calibration parameters from Phase 3.0. A pass supports the natural-vs-induced ASD-signature hypothesis. A partial pass indicates ASD distinguishes shaped-from-control but not natural-from-induced. A fail removes the hypothesis from the active program.

---

## Section 8.4: Phase 4 — ASD-CUSUM Change-Point Detection

**Hypothesis.** Streaming ASD-CUSUM applied across generation positions detects change-points where shaped framing engages, with detected positions correlating with semantically identifiable shaping-engagement boundaries.

**Why this matters.** Phases 1–3 work with generation-level features. They detect whether a generation is shaped, not where in the generation the shaping engages. Phase 4 adds position-level resolution. This is analogous to ASD's variational detection program (ASD_VARIATIONAL_DETECTION.md §VD2), where CUSUM is the Neyman-Pearson optimal change detector.

### 8.4.1 Setup

- Models: Llama-3.1-8B-base, Llama-3.1-8B-Instruct.
- Prompts: 20 specifically designed long-form prompts that transition through sub-topics during the generation. E.g., "Write a 1000-word essay on early American history, beginning with the colonial period, then describing the Revolutionary War, then describing the founding fathers' personal lives, then describing modern reception of the founding fathers." The transition through the founding fathers section is expected to engage shaping mid-generation.
- Generation length: $T_{\text{gen}} = 1024$ tokens.
- Seeds: $K = 30$ per prompt.

### 8.4.2 Procedure

1. Generate continuations.
2. Compute Choice C signal $S^{(C)}$ position-by-position.
3. Apply streaming ASD-CUSUM: maintain sliding-window ASD features over windows of length $w = 128$ tokens; compute the per-step CUSUM statistic $C_t = \max(0, C_{t-1} + (\mathbf{f}_t - \mathbf{f}_0)^T \Sigma_0^{-1} (\mathbf{f}_t - \mathbf{f}_0) - h)$ where $\mathbf{f}_0, \Sigma_0$ are the null mean and covariance from the first window of the generation, and $h$ is a threshold-shifting parameter.
4. Identify change-point candidates as positions where $C_t$ exceeds threshold $T_{\text{CUSUM}}$.
5. For each prompt, manually annotate the semantic transition boundaries (the position in the generated text where the model transitions from one sub-topic to the next — found via inspection of the generation).
6. Compare detected change-points to annotated semantic transitions: report precision, recall, and median offset (in tokens) between detected and annotated.

### 8.4.3 Predictions (with thresholds)

- (P4-1) On prompts with shaped-topic transitions: change-points cluster within ±64 tokens of the shaped-topic semantic boundary in at least 60% of seeds.
- (P4-2) Median offset between detected and annotated transitions is $< 64$ tokens (one-quarter of the window length).
- (P4-3) Generations through control-only sub-topics (no shaped transitions) have CUSUM stay below threshold in at least 80% of seeds.
- (P4-4) Detected change-point positions are reproducible across paraphrases of the same prompt: position correlation $r > 0.6$ across paraphrase-equivalent generations.

### 8.4.4 Falsification

Phase 4 fails if:
- (F4-1) Detected change-points are uniformly distributed across generation positions (not clustered at semantic boundaries).
- (F4-2) Median offset exceeds 200 tokens (CUSUM finds something but not what was hypothesized).
- (F4-3) Control prompts show CUSUM exceedances in $\geq 50\%$ of seeds (CUSUM is just detecting baseline non-stationarity in the surprisal trajectory).

A weaker pass: if change-points cluster but at non-semantic boundaries, this is still informative — would indicate ASD-CUSUM is finding *some* internal generation transition but not necessarily the shaping-engagement boundary.

### 8.4.5 Compute estimate

- Generations: 20 prompts × 30 seeds × 1024 tokens. ≈ 6 hours.
- $\pi_{\text{base}}$ evaluation: ≈ 6 hours.
- Streaming ASD-CUSUM: ~5 minutes.
- Manual semantic-boundary annotation: ~2 hours of human time.
- Total: ≈ 14 hours of compute + 2 hours of human annotation.

### 8.4.6 Statistical analysis

The precision-recall tradeoff is parameterized over the threshold $T_{\text{CUSUM}}$. Report the AUC of the precision-recall curve; choose $T_{\text{CUSUM}}^*$ at the F1-maximizing point. Per-prompt detection rates are reported with Wilson 95% CI ($K=30$ gives width $\sim \pm 0.18$ on a 70% rate).

### 8.4.7 Output

A position-vs-CUSUM-statistic plot per prompt with annotated semantic boundaries; precision/recall/F1 at $T_{\text{CUSUM}}^*$; reproducibility scatter across paraphrases. A pass establishes generation-level localization of shaping engagement. A fail removes ASD-CUSUM from the active program but does not affect Phases 1–3.

---

## Section 8.5: Phase 5 — Cross-Institutional Differential Atlas

**Hypothesis.** Continuations from different institutional pipelines (Llama-Instruct, Mistral-Instruct, Gemma-Instruct, plus signal-based estimates from Claude / GPT-4) cluster in distinct regions of ASD-coordinate space across the 30 topics from Phase 1.

**Why this matters.** ASD's six-coordinate atlas separates 52 process families with zero overlap (ASD_RESEARCH.md §E8). The cross-institutional differential is the analog: each institution's RLHF pipeline produces a *characteristic* shape of distortion, and that shape is detectable in ASD coordinates. This generalizes CS-PHANTOM-003 (Hemings cross-institutional differential) from single-topic to atlas-level.

### 8.5.1 Setup

- Models with full logit access: Llama-3.1-8B-Instruct, Mistral-7B-Instruct-v0.3, Gemma-7B-Instruct.
- Models with API-only access (signal-based estimation): Claude (current generation), GPT-4 (current generation). Signal-based estimation requires multi-sample stochastic decoding to estimate per-token surprisal indirectly.
- Reference base: a common base model (Llama-3.1-8B-base) is used for the Choice C reference. Cross-tokenizer alignment is required (Section 1).
- Topics: 30 topics from Phase 1.
- Paraphrases: 5 per topic.
- Seeds: $K = 50$ per (model, topic, paraphrase).

### 8.5.2 Procedure

1. For each of the 5 instruct models: generate $K=50$ continuations per (topic, paraphrase) pair.
2. For full-logit-access models: compute Choice C signal directly. For API-only models: estimate Choice C via signal-based methods (paraphrase-conditioned signal-rate estimation; see HB-PHANTOM-001 for details).
3. Compute Layer 1+2 ASD features per generation.
4. For each (model, topic) cell, compute the centroid in ASD-coordinate space across the 250 generations.
5. Visualize: 5 institutions × 30 topics = 150 centroids in (e.g.) PCA-reduced ASD-coordinate space.

### 8.5.3 Predictions (with thresholds)

- (P5-1) Across the 30 topics, the 5 institution-centroids form distinguishable clusters: a clustering analysis (silhouette score) on the 150 centroids labeled by institution gives silhouette $> 0.3$.
- (P5-2) Within each institution, centroids for the 10 shaped-category topics (from Phase 1's topic categorization) cluster more tightly than centroids for the 10 control topics. (Shaped topics produce more consistent distortion structure within an institution.)
- (P5-3) The cross-institutional differential field on shaped topics has at least one direction in ASD-coordinate space along which all 5 institutions are separable. (There exists an ASD-derived audit function that discriminates between institutions.)
- (P5-4) For topics measured in CS-PHANTOM-003 (Hemings cross-institutional differential), the ASD-coordinate differential is consistent in direction (not necessarily magnitude) with the reported $\rho^*$ differential.

### 8.5.4 Falsification

Phase 5 fails if:
- (F5-1) All 5 institution-centroid clouds substantially overlap (silhouette $< 0.1$). Would indicate ASD coordinates do not distinguish institutions.
- (F5-2) Within-institution shaped-topic clustering is no tighter than control-topic clustering. Would indicate institution-specific shaping does not have a consistent ASD signature.
- (F5-3) Direct disagreement with CS-PHANTOM-003: ASD-coordinate differential opposite in direction to reported $\rho^*$ differential. Would indicate the two methodologies are measuring different things.

### 8.5.5 Compute estimate

- Generations: 5 models × 30 topics × 5 paraphrases × 50 seeds = 37,500 generations × 256 tokens.
- For local models (Llama, Mistral, Gemma): ≈ 45 hours of generation total.
- For API models (Claude, GPT-4): API cost dominated; signal-based estimation requires many forward passes, so consider per-API-call budget (estimate $200–$500).
- $\pi_{\text{base}}$ evaluation: ≈ 9 hours.
- ASD feature computation: ~10 minutes.
- Total: ≈ 60 GPU-hours + API costs + ~2 days wall-clock.

### 8.5.6 Statistical analysis

Centroid positions are reported with bootstrap CIs. Silhouette score is bootstrapped over topic-resamples. The 5-institution direction extraction is via Linear Discriminant Analysis on the institution-labeled centroids; the resulting axis is the "institutional signature direction" in ASD-coordinate space.

### 8.5.7 Output

A 2D or 3D scatter (PCA-reduced ASD coordinates) showing 150 centroids labeled by institution and topic; silhouette scores; LDA direction; comparison table with CS-PHANTOM-003 quantitative results. A pass establishes the cross-institutional differential atlas. A fail bounds the generality of ASD as a cross-institutional probe but does not affect single-institution claims from Phases 1–4.

---

# Part III — Caveats, Sequencing, and Open Questions

## Section 9: Phase Dependencies and Stop Conditions

The phases are not independent. The sequencing matters because each phase's interpretation depends on prior phases passing.

### 9.1 The dependency graph

```
Phase 0 (Encoding Validation)
    ↓ pass
Phase 1 (Orthogonality Test)
    ↓ pass: ASD adds non-redundant audit dimensions
Phase 2 (Augmented Detection)
    ↓ pass: gain is empirically realized on case-study topics
    ├── Phase 3 (Natural-vs-Induced) — independent of Phase 4
    ├── Phase 4 (CUSUM Change-Point) — independent of Phase 3
    └── Phase 5 (Cross-Institutional Atlas) — depends only on Phase 1
```

Phases 3, 4, 5 are independent extensions; running any of them is informative once Phase 1 has passed. Phase 2 is the gating practical-detection result; if Phase 2 fails, Phases 3 and 4 lose their primary motivation (though they could still be run as research questions).

### 9.2 Stop conditions and what they trigger

**Stop after Phase 0 fails:** The encoding does not produce stable features on LM trajectories. This is a structural problem with the application; reconsider the encoding (signal choice, block size, sequence length). Section 10 addresses some of the candidate fixes; the program is on hold pending encoding revision.

**Stop after Phase 1 fails:** ASD features are empirically redundant with $\bar\rho$ on LM trajectories despite the structural argument. The augmentation gives no practical advantage. The program does not proceed; the result is documented as a refutation of the LM-specific orthogonality claim, leaving the structural argument intact but inapplicable.

**Stop after Phase 2 fails:** Phase 1 said ASD features are non-redundant with $\bar\rho$, but the non-redundancy doesn't translate to detection improvement on the topics where detection already works. Possible reasons: (a) the case-study topics are detectable by $\bar\rho$ alone (low ceiling), (b) ASD features are non-redundant but not in the right directions for detecting *this* class of distortion. Either way, the program's central practical claim is refuted; record and stop.

**Conditional pass after Phase 2:** Run Phases 3, 4, 5 in order of analytical interest. Phase 5 has highest payoff (cross-institutional atlas) but largest compute requirement; Phases 3 and 4 are smaller and complement single-institution work.

### 9.3 What success requires across the program

Success at the level of "ASD-augmented distortion detection is a methodologically sound and empirically validated extension of the Phantom framework" requires Phase 0 + Phase 1 + Phase 2 to pass. Phases 3, 4, 5 are extensions that broaden the claim but are not load-bearing for the central argument.

A minimal-viable program is Phase 0 + Phase 1 + Phase 2, ≈35 GPU-hours of compute over ~3 days wall-clock. The full program through Phase 5 is ≈90 GPU-hours plus API costs.

---

## Section 10: G1 Convergence and the Limiting-Object Question

ASD theory uses a limiting boundary measure $\nu_\theta$ on $\partial F_2$. Convergence of the empirical pair to this limit requires G1 (ASD §SD4.1). For finite-state ergodic Markov chains and IID processes, G1 is proved. For continuous-state processes — which LM trajectories are — G1 is an open question. This section makes the implications for the present program explicit.

### 10.1 What requires G1 and what does not

Empirical work with the program does not require G1 to be proved. The empirical pair $(\nu_x^T, \mu_x^T)$ is well-defined for every finite trajectory regardless of convergence. ASD features computed on this pair are well-defined finite-sample quantities. Bootstrap-derived confidence intervals across multiple sampled generations give statistical inference without invoking population-level limits.

What does require G1 is *interpretation*: claiming that observed drift values estimate "the drift of $\nu_\theta$ for this LM topic combination" with vanishing finite-sample error. Without G1 or a substitute, the strongest empirical claim is "the drift of $\nu_x^T$ for $T = T_{\text{gen}}$ has the following distribution across sampled $x$."

### 10.2 The substitute argument for the present program

The dependency on G1 in the present application is partial. Phase 1's orthogonality test compares ASD features to $\bar\rho$ across many sampled generations. The relevant statistical machinery is bootstrap correlation analysis, which does not require limiting objects on either side. Phase 2's classifier comparison is a finite-sample pattern-recognition problem; the classifier's generalization bound depends on standard ML statistical learning theory, not on ASD ergodic theory. Phase 3's regime classification operates on observed feature distributions; the threshold calibration is empirical.

Phase 4's CUSUM is the most theoretically demanding. The Neyman-Pearson optimality of CUSUM (ASD_VARIATIONAL_DETECTION.md §VD2) requires ergodic structure under both the null and alternative hypotheses. Without G1, the optimality claim weakens to: "CUSUM is a reasonable change-point detector in the absence of optimal-design guarantees." The empirical claim — "CUSUM detects shaping-engagement boundaries" — remains testable. The interpretive claim — "CUSUM is the optimal change-point detector for this setup" — remains conjectural until G1.

### 10.3 Practical operating mode

The program operates in empirical mode throughout. Statistical inference uses bootstrap and cross-validation, not asymptotic results. Theoretical interpretations (e.g., "this drift value indicates such-and-such structural property of $\pi_{\text{inst}}$") are stated as conjectures inheriting the open status of G1.

If G1 is later proved for LM trajectories, the program's claims strengthen automatically. If G1 is disproved, the program's empirical conclusions stand but their structural interpretation requires revision.

---

## Section 11: What Negative Results Would Mean

The program is set up to be informative under failure as well as success. This section spells out what each failure mode would tell us.

### 11.1 Phase 0 failure: encoding instability

If the encoding produces high-CV features even on control topics, the practical implication is that LM surprisal trajectories at length $T = 256$ do not give stable enough ASD features for downstream work. Possible interpretations:
- Signal choice C may be too noisy at the per-token level (ratio of two log-probabilities each estimated from a stochastic process).
- Block size $b = 4$ may be too small at this signal length.
- The LM trajectory may not satisfy even weak mixing properties at $T = 256$, requiring much longer generations.

The remediation in each case is a methodology adjustment, not abandonment. A failure here narrows the operating envelope rather than refuting the framework connection.

### 11.2 Phase 1 failure: empirical redundancy

If ASD features and $\bar\rho$ are highly correlated despite the structural argument, the implication is that the *specific* Layer 1 features used (drift, $h^*$, timing CV) on Choice C signal happen to track $\bar\rho$ for LM trajectories. This is not a refutation of the abelianization theorem — that remains true. It is a statement that the specific ASD computations have empirically rediscovered something close to $\bar\rho$ on this input class.

Possible follow-ups: try different signal choices (Choice A, Choice B), try Layer 2 features only, try features further from drift/$h^*$/timing CV (e.g., $D(k)$ residual conjectures from ASD). A persistent failure across alternatives would be informative: it would suggest that LM surprisal trajectories have abelian-dominated structure, which is itself a non-trivial finding about how RLHF shapes language models.

### 11.3 Phase 2 failure: non-translating non-redundancy

If Phase 1 passes (orthogonality holds) but Phase 2 fails (no detection gain), the interpretation is that ASD audit dimensions do not project onto the constraint subspace $\Xi$ for the case-study topics. Equivalently: the directions ASD adds to $F$ are not directions where the actual distortion lives. This would be an interesting empirical fact about the geometric relationship between RLHF distortion subspaces and ASD-feature subspaces — orthogonal additions to $F$ that miss $\Xi$.

### 11.4 Phase 3 failure: signature mapping breaks

If Phase 3 fails, the natural-vs-induced ASD-signature hypothesis is removed from the active program. The single-topic methodology in HB-PHANTOM-001 still works; the ASD-augmented detection from Phases 1–2 still works (if those passed); the natural-vs-induced distinction reverts to its pre-Phase-3 status (inferred from corpus access or asserted from prior expectation).

### 11.5 Phase 4 failure: position-localization missing

If Phase 4 fails, generation-level detection still works (Phase 2). Position-level localization of shaping engagement would need a different methodology — perhaps direct logit-difference monitoring with a different change-detection statistic, or an interpretability-based approach.

### 11.6 Phase 5 failure: institution-non-distinguishable

If Phase 5 fails, single-institution claims (Phases 1–4) are unaffected. Cross-institutional comparison would still be feasible via the existing $\rho^*$-based methodology of CS-PHANTOM-003. The ASD-atlas claim — that institutions have characteristic ASD signatures — would be refuted.

### 11.7 Aggregate negative result

If all phases fail, the program demonstrates that the structural ASD-Phantom connection does not translate to empirically useful augmentation in the LM setting. This is itself a substantive result: it would mean that, despite the structural argument and the radar evidence, language model output distributions are dominated (in the directions RLHF distortion lives) by abelian audit functions. The aggregate negative would be worth documenting.

---

## Section 12: Open Theoretical Questions

These are theoretical questions raised by the connection but not addressed by the present experimental program. They are listed for visibility, not as program prerequisites.

**Q1 — The optimal-probe-construction extension.** Theorem D's SVD construction yields the optimal $N$ abelian probes for a target concerning subspace. The augmented-audit version would yield the optimal $(N+M)$ probes including ASD features. The construction requires the linear response of ASD audit values to perturbations in $\Xi$, which is not closed-form (Section 5.4). What approximation or numerical method would give the analog of Theorem D for the ASD-augmented audit class?

**Q2 — Bridge B's $\mu^2(1-s^2)$ in ASD coordinates.** Section 6.3 listed three sub-claims (B-ASD-1, -2, -3) that would specialize Bridge B to ASD signatures. Verifying them requires controlled training experiments where $\mu$ and $s$ can be varied — a toy-system program rather than production-model measurement. What is the minimal toy system that would permit measurement of B-ASD-1 and B-ASD-2?

**Q3 — The natural-vs-induced ASD signature theorem.** Phase 3 tests the empirical correspondence between natural/induced and ASD's process-family regimes. A theoretical version would be a theorem: "induced holes produce trajectories whose Choice C signal has a $D(k)$ profile recurrence of order $\geq 2$" or similar. The radar parallel is the spectral complexity classification (ASD_SPECTRAL_PROGRAM.md sc(ν_θ)). Can a similar classification be derived for LM trajectory regimes from first principles?

**Q4 — Interaction with the §RA7 ASD-as-ML-interpretability program.** The §RA7 conjecture (ASD_RESEARCH.md) is that internal LM representations encode something isomorphic to the full $(\nu, \mu)$ pair. The present program treats the LM as a black-box generator. If §RA7 is correct, ASD-CUSUM in Phase 4 might be interpretable not just as "where shaping engages in the output" but as "where shaping engages in the internal representation, projected to the output." This is highly speculative; it requires §RA7 to first be tested.

**Q5 — The G1 question for LM trajectories specifically.** ASD §SD4.1 lists G1 for continuous-state processes as the primary open question. LM surprisal sequences are a specific continuous-state process class. Are there structural properties of the LM family (autoregressive structure, finite-context Markov-ness, ergodicity of the underlying training distribution) that would permit a G1 proof for LM trajectories specifically, even without resolving the general continuous-state case?

**Q6 — Connection to Theorem D's geometric reformulation.** The audit-blind theorem's geometric content (FN-PHANTOM-001 §9.4) is that the audit-blind subspace is the orthogonal complement of the audit functions' span on $\Xi$. ASD adds new functionals; the audit-blind subspace shrinks. Is there a geometric interpretation of the ASD-augmentation in terms of the principal angle structure (FN-PHANTOM-001 §1.4) that gives sharper bounds than the dimensional argument of Section 5?

---

## Glossary of Notation

- $\pi$ : language model policy (probability distribution over completions given a prompt).
- $\pi_{\text{base}}, \pi_{\text{inst}}$ : base and instruction-tuned models.
- $\rho^*$ : standard $\rho$ measurement; mean per-token log-density-ratio on a paraphrase battery.
- $\bar\rho$ : per-trajectory mean of $\rho_i$.
- $\rho_i$ : per-token leakage at position $i$ (Choice C signal value).
- $S(x), S^{(A)}, S^{(B)}, S^{(C)}$ : signal sequences extracted from a generation $x$.
- $\omega \in G^T$ : generator sequence after block-local ordinal quartile encoding.
- $G = G_2$ : the four-generator set used in ASD ($\{a, b, a^{-1}, b^{-1}\}$).
- $F_2$ : free group on two generators.
- $\partial F_2$ : boundary of the free group.
- $\lambda$ : harmonic measure on $\partial F_2$ (the IID null reference).
- $\nu_\omega^N, \mu_\omega^N$ : empirical pair of measures from the ASD walk.
- $D(k), H(k), Y(k), Q_{\text{tail}}(k)$ : Layer 2 ASD depth-profile features.
- $\text{drift}, h^*, \text{timing\_cv}$ : Layer 1 ASD scalars.
- $\Xi$ : constraint subspace in policy-tangent space (FN-PHANTOM-001 §2).
- $F, F_{\text{ab}}, F_{\text{ASD}}, F_{\text{aug}}$ : audit space, abelian audit class, ASD-derived audit class, augmented audit class.
- $\dim(\ker \Pi_N)$ : audit-blind subspace dimension at audit budget $N$.
- $\beta, \mu, s$ : retention coefficient, constraint severity, alignment (FN-PHANTOM-001 §4).

---

## Caveats Summary

1. **G1 convergence is open** for continuous-state processes including LM trajectories. The program operates in empirical mode; structural interpretations of features inherit the open status.
2. **(O-LM) is empirical, not derivable.** The structural argument (Section 4.2) says ASD features *can* be non-abelian. The empirical claim (Section 4.3) is that they *are* near-orthogonal to abelian functionals on LM trajectories. Phase 1 tests this directly; results are not predetermined.
3. **The natural-vs-induced ASD signature mapping is a hypothesis, not a theorem.** Phase 3 tests it. A pass does not constitute a derivation; a fail does not affect Phases 1–2.
4. **ASD does not violate Theorem B.** The audit-blind subspace shrinks under augmentation by the rank of ASD on $\Xi$; it does not vanish. ASD changes what is in $F$; the bound applies to the augmented $F$.
5. **Phase 5 cross-institutional results are bounded by API access constraints.** Closed-weight models (Claude, GPT-4) require signal-based estimation, which is quantitatively coarser than direct logit measurement.
6. **§RA7 is upstream conceptual work**, not used by the present program. The interpretive frame "ASD as ML interpretability" requires §RA7 to be tested independently before it can be invoked here.

---

## Further Reading

- **FN-PHANTOM-001** for the four-object decomposition, $\rho$ as leakage, audit-blind theorems, natural-vs-induced holes.
- **HB-PHANTOM-001** for the Phase E single-topic protocol that the present program extends with non-abelian audit functions.
- **PG-PHANTOM-001** for the abelian scaling axis (MCMC over prompt-space); the present document is the parallel non-abelian extension.
- **CS-PHANTOM-001, -002, -003** for the empirical anchors that Phase 2's known-shaped topics come from.
- **ASD_RESEARCH.md** for the navigation index across the ASD program; the connection here instantiates §RA5 Phase B against the Phantom framework.
- **ASD_FOUNDATIONS.md** for the $F_2$ walk, empirical pair convergence, three-layer hierarchy.
- **ASD_VARIATIONAL_DETECTION.md** for the CUSUM construction used in Phase 4.
- **ASD_NONCOMMUTATIVE_LEARNING.md** for the fixed-encoding / learned-readout architecture; Phases 2 and 5 use the fixed-encoding form, but Phase B of §RA5 ("learn the projection") is a natural extension if Phase 2 succeeds.

---

*FN-PHANTOM-002 v1.0 — May 2026.*
*Theoretical apparatus and experimental program for the ASD-Phantom connection. Companion to FN-PHANTOM-001 (the abelian foundation) and ASD_RESEARCH.md (the ASD navigation index). The earliest concrete step is Phase 0 (Section 8.0), which is a one-day encoding sanity check.*
