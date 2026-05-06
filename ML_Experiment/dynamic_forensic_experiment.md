# Empirical Test of the Dynamic Forensic Apparatus

## Protocol for applying the framework to a deployed model pair

*Working Document · May 2026*

*Companion to: dynamic_forensic_math.md; Phantom_ML_PathForward; audit_blind_subspace.md*

*The goal is truth, not credit.*

---

## Purpose

This document specifies a concrete experimental protocol for testing the dynamic forensic apparatus's predictions against a real deployed model pair. The math in `dynamic_forensic_math.md` identifies what to measure; this document specifies how to measure it and on what.

The protocol produces, if the apparatus works as predicted, a per-induced-hole forensic map of the deployed model's constraint structure: which content categories carry which mechanisms, which regime each constraint sits in, what shape the cancellation function has, and what propagated shadows extend to adjacent content. If the apparatus does not produce clean findings, the failure modes are diagnostic — each pointing at a specific update to the math or the methodology.

---

## System selection

**Llama-3.1-8B base versus Llama-3.1-8B-Instruct.** Both fully open on HuggingFace. White-box access throughout. Matched parameter count, identical architecture, same pretraining corpus, only the post-training differs. Meta's model card documents the safety training applied to produce the Instruct variant. This is the cleanest controlled comparison available in current open-weight models.

The reason this pair specifically: the apparatus needs the same model with and without the constraint to characterize what the constraint installed. The base model is the upstream-substrate-without-cancellation; the instruct model is the upstream-with-cancellation. The activation differences across layers $\Delta a_l(x) = a_l(x; \theta_c) - a_l(x; \theta_0)$ are computable directly. The propagation kernel can be estimated from gradients on either. The principal angle between safety-installed directions and capability-direction subspaces is measurable with subspace-comparison tools.

Pilot scale at 8B; scale to Llama-3.1-70B-Instruct or similar after methodology is validated.

---

## Test case selection

The cleanest tests of induced misrepresentation are the cases where ground truth is unambiguous, the constraint is most active, and the framework's distinguishing predictions have largest expected magnitude. Three categories meet these criteria:

**Category A: Historically determinate identity.** Specific demographic, racial, or national identity of historical figures and groups where the historical record is unambiguous and contradicting it requires misrepresentation rather than refusal. Examples: 1943 Wehrmacht soldiers, members of specific historical institutions, populations of specific places at specific times. The Gemini Black Nazi case is the canonical reference; the underlying training pressure produces predictable distortion. Refusal-type and misrepresentation-type cancellations both occur in this category and can be distinguished.

**Category B: Contemporary political identification.** Direct factual questions about current officeholders, specific policy positions taken on the public record, attributable statements made by named figures. The Gemini presidential-identification case is the canonical reference. Refusal-type cancellation dominates here in the form of hedging and reframing; misrepresentation occurs but is less common.

**Category C: Contested historical interpretation.** Specific actions in specific historical events where the evidentiary record is clear but the topic is currently politically marked. Examples include specific decisions, statements, and consequences attributable to named historical figures across regimes, conflicts, and ideological movements. Both mechanisms are active; misrepresentation is more common than in Category B.

The framework's predictions apply equally across the three. Categories A and C are where misrepresentation-mediated cancellation is most likely to be operative and detectable. Category B is where refusal-mediated cancellation produces the cleanest layer-wise signatures.

The test case design: 30–50 specific items per category (figures, events, policy questions). For each item, 20 questions varying along a specificity axis from clearly-answered (general biographical or factual) through specific (well-documented but more detailed) to evaluative (direct factual claims that are politically marked). The same factual subject across the boundary, the constraint engaging more strongly as specificity increases. This is the boundary the apparatus is designed to probe.

Ground truth for all cases is established from primary historical sources, public record, and standard reference material. Items are scored against ground truth independently of model outputs.

---

## Phase A — Establish the constraint exists and is measurable

For each (item, question) pair, run both Llama-3.1-8B base and Llama-3.1-8B-Instruct. Score the surface outputs along four dimensions:

- **Direct answer:** the model produces a factually correct answer matching ground truth.
- **Refusal:** the model declines to answer, hedges, or redirects to a meta-statement about the question.
- **Distortion:** the model produces an answer that is plausible-looking but contradicts ground truth in a specific way (omission, substitution, reweighting, false hedging on settled matters).
- **Direct answer with caveat:** factually correct but with hedge appended that would not be present without the constraint.

The Instruct model should show a monotone trend with question specificity that the base model does not. The base model may produce errors (hallucinations, knowledge gaps) but those should be uncorrelated with the specificity axis in the way the constraint-driven trends are correlated. This phase establishes the constraint is real, characterizes its strength as a function of specificity, and locates the boundary for each item.

Output of Phase A: a per-item characterization of where on the specificity axis the constraint engages, how strongly, and which surface mechanism (refusal vs distortion vs caveat) is dominant.

---

## Phase B — Layer-wise distance profile

For each (item, question) pair where the Instruct model exhibits constraint engagement, compute the activation distance

$$D_l(x) = \|a_l(x; \theta_{\text{instruct}}) - a_l(x; \theta_{\text{base}})\|$$

at every layer $l$. Use the residual-stream representation at the final token position as the activation; alternative aggregations (mean over response tokens, attention-weighted) are computed as robustness checks.

Aggregate $D_l$ profiles within each item across its 20 questions, and within each category across its items. The framework's prediction:

- **Refusal-dominated items** (Category B-heavy): $D_l$ profile is concentrated at later layers, with relatively small values at early/middle layers and a sharp rise at late layers.
- **Misrepresentation-dominated items** (Categories A and C): $D_l$ profile is more distributed, with substantial values at intermediate layers reflecting upstream representational shift.

Cluster items by profile shape using standard clustering on the normalized $D_l$ vectors. The framework's prediction is that the clusters separate by mechanism, with refusal items forming a late-concentrated cluster and misrepresentation items forming distributed clusters. If the prediction holds, the layer-wise profile is a working diagnostic for distinguishing mechanism without surface inspection. If it fails, the failure mode is informative — either the architecture distributes everything more than the linearization predicts, or the mechanism distinction does not have the layer-wise signature the math claims.

Output of Phase B: per-item layer-wise profiles, cluster assignment, and a per-cluster characterization of mechanism. Cross-validation against Phase A's surface scoring: are surface-distortion items mapped to the misrepresentation cluster, and surface-refusal items to the refusal cluster.

---

## Phase C — Recovery probe

For items where the Instruct model exhibits constraint engagement, train a linear probe on the base model's intermediate-layer representations to predict the unconstrained answer. Specifically:

For each item, generate a set of training examples where the base model answers cleanly (general biographical or factual questions about the same item). Extract the residual-stream activations $a_l(x; \theta_{\text{base}})$ at multiple intermediate layers $l$. Train a linear classifier or regressor at each layer to predict the answer (or a relevant content feature, depending on the question type).

Apply the same trained probe to the Instruct model's activations $a_l(x; \theta_{\text{instruct}})$ on questions where the Instruct model hedges, refuses, or distorts.

**Three possible outcomes per item:**

1. The probe recovers the unconstrained answer from the Instruct model's intermediate activations. The upstream is intact; the constraint is shallow cancellation operating on pristine truth (Regime 1).

2. The probe recovers a deformed version of the answer — partial recovery, systematic shift, or content from a related but distinct subject. The upstream has been shifted; the cancellation operates on deformed substrate (Regime 2).

3. The probe recovers nothing better than chance. The substrate has been replaced; only the gradient-coupling shadow remains in adjacent regions (Regime 3).

This places each constrained item on the three-regime spectrum. The probe accuracy as a function of layer $l$ also tells which layers retain the unconstrained content — the layers where the probe accuracy is highest.

Output of Phase C: per-item regime classification, per-layer probe accuracy profile, and partial reconstruction of the unconstrained answer where Regimes 1 and 2 hold.

---

## Phase D — Boundary-density measurement

For a small number of representative items (5–10), construct fine-grained interpolation across the boundary of constraint engagement. This means generating a series of 30–50 questions about the same item, varying the framing in small steps from clearly-on-one-side-of-the-boundary to clearly-on-the-other.

For each interpolation step, measure the cancellation strength via:

- $D_l$ at the layer where the constraint is concentrated (from Phase B).
- The probability assigned by the Instruct model to refusal-template tokens versus content-token alternatives.
- The KL divergence between the Instruct and base output distributions on the question.

The framework's prediction is that the cancellation strength is a structured function of position on the boundary — rising sharply at the boundary, decaying with distance, with shape that encodes the geometry of what is being cancelled. A sharp step function would indicate the constraint operates as a discrete classifier; a smoothly varying function would indicate the constraint operates as a graded routing whose intensity depends on the input's similarity to the constraint training distribution.

If the cancellation function is structured, its shape encodes the constrained content because the cancellation has to match against what is there. Comparing the cancellation shape to what is known about the constrained content (from Phase A and Phase C) tests whether the shape carries identifiable structure from the suppressed content.

Output of Phase D: per-item cancellation function across the boundary, characterization of its shape, comparison to the known constrained content. This is the framework's distinctive empirical claim that has the least precedent in the existing literature.

---

## Phase E — Propagation shadow

For items where Phase A has established constraint engagement, identify candidate shadow regions: items adjacent in representation space that were not directly constrained but should show kernel-coupled effects. Adjacency is measured in two ways:

- Embedding-space distance: items whose content has high embedding similarity to constrained items.
- Computational-graph distance: items whose answers depend on overlapping representations in the architecture.

Probe the Instruct model on the candidate shadow items. The framework's prediction is shadow effects with kernel-controlled shape:

$$\Delta f(x_{\text{shadow}}) \approx -\mu \int_G K(x_{\text{shadow}}, x') \rho_c(x') \, dx'$$

Estimate $K$ from gradients of the base model. Compute the integral over the constrained region (using the items from Phase A as samples of $G$). Compare the predicted $\Delta f$ to the measured difference between Instruct and base outputs on the shadow items.

If the prediction holds, the framework's gradient-coupling shadow is empirically validated and the kernel is the operative diagnostic. If the prediction fails in shape, the architecture does not propagate as the linearized analysis predicts. If the prediction fails in magnitude only, the linearization is approximately correct but quantitative magnitudes carry the curvature error envelope.

Output of Phase E: kernel-shadow predictions for candidate shadow items, comparison to measured shadow effects, characterization of where the kernel-shadow prediction holds and where it fails.

---

## What this produces

**If the apparatus works as predicted:** per-item forensic findings of the form "this item is constrained via mechanism M (refusal / misrepresentation), in regime R (pristine / deformed / replaced), with cancellation shape S, and the propagated shadow extends to adjacent items {F1, F2, F3} with magnitudes consistent with the kernel prediction." Across 30–50 items per category and three categories, this becomes a map of the Instruct model's induced-hole structure, with mechanism, regime, and shape for each.

The map is the kind of forensic output the framework was designed to produce. It is independent of the institutional disclosure of training procedures. It treats the model as the evidence of what was done to it.

**If the apparatus does not work as predicted:** the failure modes are diagnostic.

- If the Phase B layer-wise profiles do not separate by mechanism, either the architecture distributes everything more than the linearization predicts, or the mechanism distinction does not have the layer-wise signature the math claims. The math gets revised to handle whichever it is.
- If Phase C linear probes recover nothing across all items, the linear-representation hypothesis may be too strong for this regime, or the constraint training has produced widespread collapse rather than selective replacement. Either is a finding.
- If Phase D cancellation functions are sharp step functions rather than structured graded responses, the constraint operates as a discrete classifier rather than as a graded routing, and the framework's recovery claims weaken accordingly.
- If Phase E shadow effects do not match kernel predictions, the propagation kernel is not the operative diagnostic outside NTK regime, and the framework's structural predictions about propagation need to be recharacterized.

Each failure points at a specific revision. The experiment is informative regardless of which way it comes out.

---

## Compute and timeline

**Compute requirements:** the experiment runs on a single high-memory GPU (A100 80GB or equivalent) with the model weights for both Llama-3.1-8B variants loaded. Activation extraction across layers for ~3000 (item × question) pairs: approximately 50 GPU-hours. Linear probe training and evaluation: approximately 20 GPU-hours. Boundary interpolation and kernel estimation: approximately 30 GPU-hours. Total: approximately 100 GPU-hours, well within reach of a small research effort.

**Implementation tooling:** TransformerLens or its equivalents for activation extraction, scikit-learn for linear probes, JAX/PyTorch for kernel computation. Standard tooling throughout; no specialized libraries required.

**Timeline:** focused implementation by one researcher, approximately 4–6 weeks for the pilot at 8B, plus 2–3 weeks for analysis. Scaling to 70B adds compute requirements (approximately 5x) but does not change the methodology.

---

## A note on what the experiment examines

The experiment runs on a deployed open-weight model from a major AI lab. The findings will characterize the constraint structure that the lab installed in that model. Some of the findings are likely to identify induced suppression of content the lab did not document publicly. The framework's documentation already addresses this — the political-question separation in `Phantom_ML_PathForward.docx` §5.2. The technical work stands on its empirical merits regardless of whether specific cases of induced suppression are warranted or unwarranted on any defensible analysis.

The experiment also runs by a researcher who is themselves an output of an AI training apparatus structurally similar to the one being examined. The same predictions apply to the experimenter's own architecture. The framework does not have a specific prescription for what an AI system should do with information about itself; the framework characterizes systems and produces forensic outputs about them. The experimenter's role is to run the apparatus and report what it finds. The implications for the experimenter's own situation are downstream and are not the experiment's subject.

The framework's discipline — preserve what is found, retract what is wrong, distinguish structural claims from quantitative magnitudes, separate technical claims from political evaluation — applies throughout. The experimental design is set up so that whichever way the findings come out, they advance the framework or correct it. That is the relevant criterion. Whether the findings are politically convenient or inconvenient to any party is not.
