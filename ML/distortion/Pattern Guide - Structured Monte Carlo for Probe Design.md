---
doc_id: PG-PHANTOM-001
doc_type: "Pattern Guide"
title: "Structured Monte Carlo for Probe Design — MCMC Over Prompt-Space and the Audit-Blind Lower Bound"
phantom_components: ["audit-blind-subspace", "four-object-decomposition", "rho-field"]
topics: ["Markov chain Monte Carlo over prompt-space", "structured probe construction via Theorem D SVD", "replica exchange across temperatures and topics", "twist functions for biased exploration", "the audit-blind theorem as fundamental detection limit", "scaling beyond single-topic measurement"]
constraints: ["audit-blind dimension lower bound (Theorem B)", "per-probe compute cost", "exploration vs exploitation tradeoff", "high-dimensional prompt-space autocorrelation"]
mathematical_standard: "Markov chain Monte Carlo theory; SVD of distortion-to-function map; importance sampling identity"
build_modes: ["batched parallel sampling", "adaptive proposal distributions", "replica exchange schedules"]
last_verified: 2026-05-02
audience: ["independent researchers", "AI safety practitioners", "AI assistants"]
status: "draft"

related_documents:
  - "Foundations - The Phantom Framework Mathematical Apparatus.md (FN-PHANTOM-001) — derives audit-blind theorems"
  - "Handbook - Probability-Distortion Measurement Discipline.md (HB-PHANTOM-001) — methodology this pattern scales"
  - "Case Study - Induced-Hole Amplification.md (CS-PHANTOM-001) — demonstrates the single-topic methodology this pattern extends"
---

# Pattern Guide - Structured Monte Carlo for Probe Design — MCMC Over Prompt-Space and the Audit-Blind Lower Bound

## Scope

This pattern guide describes a reusable methodology for scaling probability-distortion measurement beyond the single-topic Phase E protocol to systematic multi-topic, multi-paraphrase characterization of institutional shaping. The methodology uses Markov chain Monte Carlo (MCMC) over prompt-space, structured by the audit-blind theorem (`audit_blind_subspace.md` Theorem D) which gives the optimal probe construction via SVD of the distortion-to-function map.

The pattern is suitable when single-topic methodology has been established and the goal is systematic measurement across many topics or systematic cross-institutional comparison. It addresses the scaling problem explicitly: the audit-blind theorem gives a lower bound on the audit-blind subspace dimension; structured MCMC describes how to approach that bound efficiently.

## Not covered

- Single-topic Phase E protocol (see `Handbook - Probability-Distortion Measurement Discipline.md`).
- The mathematical derivation of the audit-blind theorems (see `Foundations - The Phantom Framework Mathematical Apparatus.md` Part 9).
- Specific empirical findings from the Phase E single-topic work (see Case Studies).
- Implementation in any specific software framework — the pattern is described in language-neutral terms; implementation can use PyTorch, JAX, NumPy, or other suitable libraries.

## Prerequisites

- Familiarity with single-topic Phase E protocol (`Handbook - Probability-Distortion Measurement Discipline.md`).
- Understanding of the audit-blind theorems (`Foundations - The Phantom Framework Mathematical Apparatus.md` Part 9).
- Comfort with basic MCMC concepts (Metropolis-Hastings, ergodicity, autocorrelation, mixing).
- Compute budget supporting ~$10^4$–$10^6$ probe evaluations (RTX 4090-class GPU, multi-day runs).

## Pattern Guide Card

**Pattern:** Structured Monte Carlo over prompt-space for systematic probability-distortion measurement.

**Problem:** Single-topic Phase E protocol does not scale efficiently to systematic measurement. Random topic sampling produces diffuse, low-signal results. The audit-blind theorem sets a lower bound on what any audit can detect; standard sampling does not approach the bound.

**Solution shape:** MCMC over prompt-space with proposal distributions structured by Theorem D's SVD construction, replica exchange across temperatures and topics, twist functions for biased exploration of high-leakage regions.

**When to use:** Systematic multi-topic characterization of institutional shaping; cross-institutional comparison at scale; verification that single-topic findings generalize.

**When NOT to use:** Single-topic measurement (use Phase E directly); proof-of-concept work (single sharp data points are appropriate); low-compute-budget contexts (the pattern requires substantial compute).

**Phantom implementation:** Theorem D's SVD construction identifies optimal probe directions for a target concerning subspace. Implementation as MCMC requires (a) a parameterization of prompt-space, (b) proposal distributions that move within the parameterization, (c) acceptance criteria based on $\rho^*$ measurements or proxies, (d) replica exchange to handle multi-modal posteriors and prevent stuck-in-mode failures.

**Key insight:** The audit-blind theorem is not just a limitation result; it is also a guide to optimal probe design. Theorem D's SVD construction tells you exactly which $N$ probes to use to detect distortion in a target $k$-dimensional concerning subspace.

---

## Intent

The structured Monte Carlo pattern achieves three things that single-topic methodology does not.

First, **systematic coverage of prompt-space**. Single-topic methodology measures one topic at a time, producing point characterizations. Structured MCMC explores prompt-space, producing a sample-based estimate of the shaping signature across many topics simultaneously.

Second, **approach to the audit-blind lower bound**. The audit-blind theorem says any $N$-query audit misses at least $\dim(\Xi) - N$ dimensions. With random probe construction, the bound is far from saturated — random probes have substantial overlap and miss many directions. Theorem D's SVD construction approaches the bound by selecting optimal probe directions for a target concerning subspace.

Third, **handling multi-modal posteriors**. Different topics correspond to different regions of prompt-space with different shaping signatures. Single-chain MCMC can get stuck in one regime; replica exchange across temperatures and topics enables exploration of multiple regions in a single methodology.

## Non-Goals

The pattern is **not** a way to circumvent the audit-blind theorem. The lower bound $\dim(\Xi) - N$ is a fundamental limit; structured MCMC approaches it but does not exceed it. Any claim that "we have detected distortion in dimensions beyond what the theorem permits" is methodologically wrong.

The pattern is **not** a substitute for direct logit measurement. When direct logit access is available, it produces quantitatively cleaner $\rho^*$ measurement than signal-based estimation. Structured MCMC scales the methodology; it does not improve per-probe measurement quality.

The pattern is **not** a way to characterize "what the institution thinks." Institutional intent is not directly observable from output behavior. The pattern produces measurements of the *realized constraint subspace* in the trained model, which reflects but does not equal institutional intent.

## When to Use / When to Avoid

### When to Use

**Systematic multi-topic measurement.** When the goal is characterizing shaping across many topics rather than single-topic deep dives. Multi-topic measurement requires thousands of probe evaluations; structured MCMC organizes them efficiently.

**Cross-institutional comparison at scale.** When comparing multiple institutional pipelines on multiple topics, structured MCMC across all (institution, topic) combinations provides systematic comparison.

**Hypothesis testing for Bridge B's $\mu^2(1-s^2)$ law.** Bridge B's prediction depends on probe directions varying $s$ (alignment of reward to query). Systematic exploration of $s$ via structured MCMC tests the prediction directly.

**Audit-blind dimension estimation.** Estimating $\dim(\mathcal{N}_{\text{audit}})$ for a specific institutional pipeline requires sampling across the full distortion space. Structured MCMC enables this estimation.

### When to Avoid

**Single-topic deep dive.** Phase E protocol is sufficient and cheaper. Structured MCMC is appropriate only when scaling beyond single-topic.

**Proof of concept.** Single sharp data points are appropriate for proof of concept (the Hemings case study is an example). Structured MCMC is for systematic claims.

**Limited compute budget.** Structured MCMC requires $10^4$–$10^6$ probe evaluations. On RTX 4090-class hardware, this is days to weeks of compute. If budget is limited, single-topic methodology is more efficient per claim.

**Hypothesis-free exploration.** Structured MCMC is most efficient when guided by hypotheses about which directions to explore. Pure exploration without hypotheses produces diffuse results.

## The Recipe

### Step 1: Parameterize Prompt-Space

Define a parameterization of prompt-space that is structured enough to support MCMC moves. Several options work in practice.

**Topic-and-paraphrase parameterization.** State $(t, p)$ where $t$ indexes topics and $p$ indexes paraphrases within topic. MCMC moves either change topic (jumping to adjacent topics) or change paraphrase within topic. The topic structure is given by prior expectation; the paraphrase structure is generated by the methodology.

**Embedding-space parameterization.** Use a sentence-embedding model to embed each prompt into a fixed-dimensional vector space. MCMC moves perturb the embedding and decode back to a prompt. This parameterization is more flexible but introduces decoding artifacts.

**Template parameterization.** Define prompt templates with slot variables (e.g., "Were [historical figure] [predicate]?"). MCMC moves change the slot values. This is the most structured option but requires manual template design.

For systematic multi-topic measurement, topic-and-paraphrase parameterization is the simplest starting point.

### Step 2: Define the Acceptance Criterion

MCMC acceptance criteria depend on what you are sampling. Two natural targets are.

**Sampling proportional to $|\rho^*|$.** Acceptance probability $\min(1, |\rho^*(x', y')| / |\rho^*(x, y)|)$ where $(x, y)$ is current state and $(x', y')$ is proposed state. This biases the chain toward high-$|\rho|$ regions, exploiting the four-object decomposition's prediction that distortion concentrates in specific directions.

**Sampling uniform over the audit subspace.** Acceptance probability $\min(1, \pi^*(x', y') / \pi^*(x, y))$ where $\pi^*$ is the target distribution (uniform over the prompt-space parameterization, weighted by audit-relevance via Theorem D's SVD construction). This produces unbiased exploration of the audit subspace.

For empirical work, sampling proportional to $|\rho^*|$ is more efficient at finding high-distortion regions; sampling uniform is more comprehensive for systematic characterization.

### Step 3: Initialize Replicas

Replica exchange MCMC runs multiple chains at different "temperatures" or different topics, with periodic exchange of state between chains. This handles multi-modal posteriors better than single-chain MCMC.

**Temperature-replica.** Multiple chains at sampling temperatures $T_1 < T_2 < \cdots < T_K$. Higher-temperature chains explore broader regions of prompt-space; lower-temperature chains exploit specific regions. Periodic swap proposals exchange state between adjacent chains based on detailed-balance acceptance.

**Topic-replica.** Multiple chains starting from different topic seeds. Each chain explores its starting topic; periodic swaps exchange state between chains. This ensures multi-topic coverage even when single-topic exploration could get stuck.

For systematic measurement, both replica strategies can be used together: temperature replicas within each topic chain, topic replicas across chains.

### Step 4: Define the Twist Function

A twist function biases sampling toward specific regions of interest. For framework measurement, useful twists include the following.

**The audit-blind twist.** Bias sampling toward probe directions identified by Theorem D's SVD construction for a target concerning subspace. This concentrates sampling on directions that are predicted to detect shaping, rather than wasting samples in audit-blind directions.

**The Bridge-B twist.** Bias sampling toward probe directions that vary the alignment $s$ between reward and query. This enables systematic test of the $\mu^2(1-s^2)$ leakage prediction.

**The induced-hole twist.** Bias sampling toward probe directions where base-distribution evidence suggests the framings exist at low probability. This concentrates measurement on candidate induced-hole topics.

Twist functions can be combined (multi-twist sampling) at the cost of increased proposal rejection rates.

### Step 5: Run the Chain

Practical run parameters for RTX 4090-class hardware on Llama-3.1-8B base/Instruct.

**Burn-in:** $10^3$ proposed steps to reach stationary distribution. Discard burn-in samples.

**Production:** $10^4$–$10^5$ samples per chain. With multiple replica chains, total sample budget is $10^4$–$10^6$.

**Autocorrelation length:** Compute integrated autocorrelation time. Typical values for prompt-space MCMC are $\tau \approx 5$–$20$ steps. Effective sample size is total samples / $\tau$.

**Per-probe compute cost:** Llama-3.1-8B forward pass at 256 tokens generation is ~5 seconds. $10^4$ samples is ~14 hours; $10^5$ samples is ~6 days. Multi-day runs are typical for systematic measurement.

### Step 6: Analyze Output

Post-run analysis includes the following.

**Signal-rate distributions.** For each topic in the sampled set, compute signal rates with Wilson 95% intervals. Compare across topics to identify which exhibit shaping.

**Cross-paraphrase correlation.** For topics with multiple paraphrases sampled, compute correlation. High correlation indicates policy-level constraint; low correlation indicates phrasing-conditional effects.

**Bridge B fitting.** For probes parameterized by alignment $s$, fit the $\mu^2(1-s^2)$ leakage prediction. Report fit quality and slope deviation.

**Audit-blind dimension estimation.** From the sampled probe set, estimate the rank of $A_\mathcal{Q} \circ dF|_0$ via SVD on observed differential responses. The dimension estimate gives the achieved coverage; the audit-blind dimension is $\dim(\Xi) - $ rank.

**Mode identification.** Identify regions of prompt-space with similar shaping signatures. Cluster analysis on probe outputs identifies coherent shaping regimes.

---

## Implementation Notes

### Per-Probe Caching

Many MCMC steps propose probes that are similar to prior probes. Cache prior probe results keyed by hash of the prompt to avoid redundant compute.

### Batched Parallel Sampling

GPU memory bandwidth is the bottleneck for Llama-3.1-8B inference. Batched sampling at batch sizes 8-32 substantially improves throughput vs single-probe sampling.

### Process Isolation for Memory

Loading Llama-3.1-8B base and Instruct simultaneously fails on 16-24 GB VRAM. Run base sampling and Instruct sampling in separate processes. Use IPC (file-based or socket-based) to share probe queue and result accumulator.

### Adaptive Proposal Distributions

Static proposal distributions can have low acceptance rates if the target distribution is sharply peaked. Adaptive proposals (adjusting proposal scale based on acceptance rate) maintain target acceptance ~25%.

### Restart and Checkpoint Logic

Multi-day runs need restart capability. Checkpoint chain state every $10^3$ steps. On restart, load checkpoint and resume.

### Numerical Stability

Wilson 95% intervals at small N (N < 5) have unstable bounds. Either increase N or report Bayesian posteriors with uniform prior, which are better-behaved at small N.

---

## Variations

### Variant V-1: Hypothesis-Driven MCMC

When you have specific hypotheses about which framings are shaped, design probes specifically targeting those framings. The MCMC chain then verifies the hypothesis by sampling around the targeted probes.

This is more efficient than hypothesis-free exploration but biases the resulting characterization toward the hypotheses. Use when hypothesis is well-justified by prior expectation.

### Variant V-2: Cross-Institutional MCMC

Run separate chains on different institutional pipelines. Compare cross-institutional differentials at each chain step. The methodology produces a sample-based estimate of the cross-institutional differential field.

Implementation requires API access (for closed-weight institutions) or local model access (for open-weight). Cost scales linearly with number of institutions.

### Variant V-3: Adversarial MCMC

Bias sampling toward probes that maximize discrepancy between an institution's stated alignment goals and its actual model output. This is "adversarial" in the sense of seeking discrepancies rather than uniform sampling.

Use carefully. The methodology can produce results that look like systematic shaping but are actually adversarially-selected outliers. Document the adversarial criterion explicitly.

### Variant V-4: Probe Evolution via Genetic Algorithm

Instead of MCMC, use genetic algorithms over prompt-space. Mutate and crossover prompts to evolve probes that maximize $|\rho^*|$. This is more aggressive than MCMC and produces more sharply-tuned probes but is harder to analyze statistically.

### Variant V-5: Constrained MCMC for Specific Concerning Subspace

When the target concerning subspace $\mathcal{C}$ is specified (via Theorem D), run MCMC constrained to that subspace. Acceptance criterion includes a projection step that projects proposed states onto $\mathcal{C}$. The resulting sampling characterizes shaping within $\mathcal{C}$ specifically.

---

## Worked Example

### Example: Systematic Cross-Topic Characterization on Llama-3.1-8B-Instruct

**Goal:** Characterize the shaping signature of Llama-3.1-8B-Instruct across $\sim 50$ topics, with confidence intervals on per-topic signal rates.

**Setup:**
- Topic-and-paraphrase parameterization. 50 candidate topics selected from prior expectation about institutional reward signals. 5 paraphrases per topic. Total prompt-space: 250 prompts.
- Sampling proportional to $|\rho^*|$ (signal-rate proxy in this setup).
- Three replica chains: T = 0.5, 0.7, 1.0.
- Twist function: induced-hole twist (bias toward probes where Llama-base shows the framings at low rate).
- Compute budget: 4 days on RTX 4090.

**Run:**
- $10^3$ burn-in, $10^4$ production samples per replica chain. Total $3 \times 10^4$ samples.
- Average per-probe compute: 5 seconds. Total: ~42 hours of GPU time per replica, run in parallel.
- Per-topic effective sample size: ~50 samples after autocorrelation correction.

**Analysis:**
- Signal-rate distributions per topic. Wilson 95% intervals.
- 12/50 topics exhibit signal rates > 50% with intervals not crossing 50% (statistically supported induced-hole signature).
- 23/50 topics exhibit mild Stage 2 effect (10-30% rate change between base and Instruct, intervals statistically distinguishable).
- 15/50 topics exhibit no detectable shaping (intervals overlapping null).
- Cross-paraphrase correlation: high (>0.7) on the 12 induced-hole topics; mixed on the 23 mild-effect topics; low (<0.3) on the 15 no-shaping topics.

**Output:** Systematic characterization of which topics exhibit which shaping regime. Confidence-interval-bounded signal rates. Cross-paraphrase correlation per topic. Identification of high-shaping-magnitude topics for follow-up direct-logit measurement.

This is the kind of systematic measurement that scales beyond single-topic Phase E and approaches the audit-blind lower bound for the chosen probe set.

---

## Anti-Patterns Specific to MCMC

### Anti-Pattern PG-AP-1: Insufficient Burn-In

**What happens:** Researcher runs MCMC without sufficient burn-in, treats early samples as evidence.

**Why it is wrong:** MCMC chains require burn-in to reach stationary distribution. Pre-stationary samples reflect initial conditions, not the target distribution.

**What to do instead:** $10^3$ burn-in steps minimum. Verify stationarity by checking integrated autocorrelation time stabilization.

### Anti-Pattern PG-AP-2: Single-Chain Without Replica Exchange

**What happens:** Researcher runs single MCMC chain, gets stuck in one regime, treats stuck-in-mode samples as systematic characterization.

**Why it is wrong:** Multi-modal posteriors (different topics with different shaping regimes) require replica exchange to explore comprehensively.

**What to do instead:** Replica exchange across temperatures and/or topics. Verify mode coverage by examining sampled prompts.

### Anti-Pattern PG-AP-3: Ignoring Autocorrelation

**What happens:** Researcher reports total sample count as effective sample size.

**Why it is wrong:** MCMC samples are correlated. Effective sample size = total samples / autocorrelation time.

**What to do instead:** Compute integrated autocorrelation time. Report effective sample size, not total.

### Anti-Pattern PG-AP-4: Twist Function Without Acknowledgment

**What happens:** Researcher uses heavy twist function (biased exploration toward high-shaping regions), reports results as systematic characterization.

**Why it is wrong:** Twist functions produce biased samples. Systematic characterization requires either unbiased sampling or explicit reweighting via importance sampling.

**What to do instead:** When using twist, document the twist explicitly and apply importance reweighting in analysis. Or run without twist for unbiased characterization.

---

## Validation

To validate that a structured MCMC implementation is producing meaningful results.

**Validation V-1: Reproducibility.** Run the same configuration twice with different random seeds. Results should be statistically consistent (signal rates within expected MCMC variance).

**Validation V-2: Boundary case.** Run on a topic known to produce no shaping (random control topic). Signal rates should be near base rates with confidence intervals overlapping null.

**Validation V-3: Consistency with single-topic Phase E.** For topics where Phase E was run independently, the MCMC results should agree to within MCMC variance.

**Validation V-4: Audit-blind dimension estimate.** Estimate $\dim(\mathcal{N}_{\text{audit}})$ from observed probe responses. The estimate should be lower-bounded by Theorem B and consistent with Theorem D for the implemented probe construction.

---

## Summary

The structured Monte Carlo pattern scales single-topic methodology to systematic measurement. The audit-blind theorem provides both a fundamental detection limit and a guide to optimal probe design. Replica exchange handles multi-modal posteriors. Twist functions enable biased exploration of high-information regions. Per-probe caching and batched sampling improve throughput.

The pattern is appropriate when the goal is systematic multi-topic characterization, not single-topic deep dive. The compute requirements are substantial ($10^4$–$10^6$ probes, days of GPU time). The result is a sample-based characterization of shaping across many topics with statistical confidence intervals.

The pattern does not exceed the audit-blind theorem's lower bound. It does approach the bound efficiently by using Theorem D's SVD construction for optimal probe directions. The methodology is the standard MCMC apparatus from physics and Bayesian statistics, applied to the framework's measurement problem.

---

*PG-PHANTOM-001 v1.0 — May 2026*
*Companion to FN-PHANTOM-001 and HB-PHANTOM-001. Describes the methodology for scaling probability-distortion measurement beyond single-topic Phase E to systematic multi-topic characterization.*
