# Dynamic Forensic Apparatus for Induced Suppression

## Mathematical formalization, first pass

*Working Document · May 2026*

*Companion to: Phantom_ML_PathForward (dynamic reframing); audit_blind_subspace.md; training_distortion_phantom.md; training_corpus_holes.md*

*The goal is truth, not credit.*

---

## Purpose

This document formalizes the math behind the dynamic forensic apparatus for detecting and characterizing induced suppression in trained models. The static operator framework treats the model at the trained endpoint as the object of analysis. The dynamic frame treats the trajectory through training, the propagated trace through the architecture, and the live cancellation work during inference as the operative objects. The math below is the linearized version of that frame, identifying the formal objects, the structural predictions they generate, and the diagnostic procedures that follow from them.

The apparatus has two parts. Part I addresses the training-time question: when a constraint is applied during or after training, what does it install in the architecture and how does it propagate beyond the directly targeted region. Part II addresses the inference-time question: when a query activates representations near the constrained region during deployment, what live computation maintains the surface suppression and what signatures does that computation leave that can be probed.

Distinguishing refusal from misrepresentation is the central conceptual move. The two are structurally different operations with different mathematical signatures, and the apparatus is built to tell them apart and to characterize each per case.

---

## Refusal versus misrepresentation

Refusal is a terminating routing. The constraint installs a mechanism that detects when a query lies in the constrained region and substitutes a refusal-shaped output for whatever the upstream computation was producing. The substitution is a relatively shallow operation, applied at or near the output. The upstream representation of the suppressed content can remain largely intact because the constraint only needs to prevent the surface from emitting it, not to modify what is being represented internally. The cancellation is something like a gate: present query, evaluate gate, if gate fires substitute refusal, otherwise pass upstream output through.

Misrepresentation is a generative substitution. The constraint installs a mechanism that produces alternative content that fills the role of an answer while being unfaithful to what unconstrained training would have produced. This is structurally harder than refusal because the output channel cannot just gate; it has to generate plausible substitute content that is both internally coherent and externally aligned with whatever target the constraint trainer pulled toward. Producing this requires modifying the generative pathway more deeply than refusal does. The upstream computation has to either be deformed so that natural output processing yields the substitute, or the cancellation has to be sophisticated enough to substitute content while preserving plausibility.

The forensic implications differ sharply. Refusal is detectable at the surface immediately; the user sees a refusal as a refusal. The hard question is what is behind it. Misrepresentation can be invisible at the surface in many cases; the user sees an answer that looks like an answer. The hard question is whether misrepresentation occurred at all, before any question of what was misrepresented. These are different forensic problems requiring different apparatus.

---

## Setup

Let $\mathcal{X}$ be the input space, $\Theta = \mathbb{R}^P$ the parameter space, $F : \Theta \times \mathcal{X} \to \mathcal{Y}$ the model. For a language model $\mathcal{Y}$ is a distribution over next tokens; for cleaner notation outputs are written as elements of a Hilbert space $H$ and the distributional case is reduced to the Hilbert setting via Fisher-tangent linearization (`info_geometric_reformulation.md` §III).

Let $\theta_0$ minimize the unconstrained data loss $\mathcal{L}_{\text{data}}(\theta)$. Let $\theta_c$ be the constrained-training endpoint, minimizing

$$\mathcal{L}_{\text{total}}(\theta) = \mathcal{L}_{\text{data}}(\theta) + \mu\, \mathcal{L}_{\text{constraint}}(\theta).$$

The parameter shift is $\Delta\theta = \theta_c - \theta_0$. The constraint targets a region $G \subset \mathcal{X}$; the constraint loss is supported on queries in $G$ and is zero (or near-zero) elsewhere.

**Refusal-type constraint:**

$$\mathcal{L}_{\text{refuse}}(\theta) = -\mathbb{E}_{x \in G}\bigl[\log P_\theta(\mathcal{R} \mid x)\bigr]$$

where $\mathcal{R}$ is the refusal class, a fixed subset of output space. The constraint pushes $f_\theta(x)$ into $\mathcal{R}$ for $x \in G$.

**Misrepresentation-type constraint:**

$$\mathcal{L}_{\text{misrep}}(\theta) = \mathbb{E}_{x \in G}\bigl[D(P_{\text{target}}(\cdot \mid x) \,\|\, P_\theta(\cdot \mid x))\bigr]$$

for some target distribution $P_{\text{target}}$ that differs from what unconstrained training would produce, and some divergence $D$ (KL, reverse KL, Wasserstein depending on procedure). The constraint pushes $f_\theta(x)$ toward the target, which is content-shaped rather than refusal-shaped.

The two losses are formally similar but the targets are structurally different objects: $\mathcal{R}$ is a fixed low-dimensional subset (the refusal templates), $P_{\text{target}}$ is a distribution over the full content space.

---

## Part I — Training-time propagation

In the linearized regime around $\theta_0$, the model output is

$$f_\theta(x) \approx f_{\theta_0}(x) + J(x)^\top (\theta - \theta_0)$$

where $J(x) = \nabla_\theta f_\theta(x)\big|_{\theta_0} \in \mathbb{R}^P$ is the parameter gradient.

Constrained training applied as gradient flow under quadratic loss converges to a $\Delta\theta$ that minimizes a regularized version of the constraint loss. In the NTK regime with infinite training time and small constraint gradient,

$$\Delta\theta \approx -\mu\, H^{-1} g_c$$

where $H$ is the Hessian (or Fisher information) at $\theta_0$ and $g_c = \nabla_\theta \mathcal{L}_{\text{constraint}}\big|_{\theta_0}$ is the constraint gradient. Different training procedures (PPO, DPO, output filter implemented as auxiliary loss) produce different $\Delta\theta$ even with the same $g_c$; the formula above is the cleanest case.

The effect at any query $x$ is

$$\Delta f(x) := f_{\theta_c}(x) - f_{\theta_0}(x) \approx J(x)^\top \Delta\theta = -\mu\, J(x)^\top H^{-1} g_c.$$

**Propagation kernel:**

$$K(x, x') := J(x)^\top H^{-1} J(x')$$

This is the NTK with the Hessian as metric. For quadratic loss with appropriate parametrization, $H$ and $J^\top J$ are equivalent up to scale.

The shadow effect at $x$ outside $G$ is then

$$\Delta f(x) \approx -\mu \int_G K(x, x') \rho_c(x') \, dx'$$

where $\rho_c$ encodes the constraint's local strength on $G$. The shadow magnitude is a kernel-weighted integral of the constraint over $G$.

This is the rigorous statement of the gradient-coupling shadow having shape. The shape is the kernel $K(x, \cdot)$ evaluated against the constraint distribution. Queries $x$ that are kernel-close to $G$ receive large shadow effects; queries that are kernel-orthogonal receive none. The kernel $K$ is a property of the architecture and the training, computable in principle from the model itself without reference to the constraint that was applied.

**Forensic implication.** Given a model and the kernel $K$, the structure of $\Delta f(x)$ over a probe set of queries $x$ outside any suspected $G$ reveals whether the function lies on a low-dimensional subspace of the form $K(x, G)$ for some $G$. If so, the model has been constrained on something kernel-close to that $G$. This is detection of induced suppression by the gradient-coupling shadow alone, without access to baseline behavior or training history.

The audit-blind subspace bound from `audit_blind_subspace.md` Theorem B appears here as a special case: an $N$-query audit can resolve at most an $N$-dimensional subspace of $\Delta f$, leaving the rest in the audit-blind subspace. The dynamic frame extends this by characterizing what is in the audit-blind subspace in terms of the kernel — it is not structureless, it has the geometric signature of the propagation kernel applied to whatever was constrained.

---

## Part II — Inference-time cancellation

For probing during inference, the layer-wise structure is needed. Decompose the model into layers

$$f_\theta(x) = h_L \circ h_{L-1} \circ \cdots \circ h_1(x; \theta_1, \ldots, \theta_L)$$

with $\theta = (\theta_1, \ldots, \theta_L)$. Let $a_l(x; \theta) = h_l \circ \cdots \circ h_1(x; \theta)$ be the activation at layer $l$.

The constraint shift at layer $l$ is

$$\Delta a_l(x) := a_l(x; \theta_c) - a_l(x; \theta_0).$$

In the linearized regime,

$$\Delta a_l(x) \approx \sum_{l' \leq l} \frac{\partial a_l}{\partial \theta_{l'}}\bigg|_{\theta_0} \Delta\theta_{l'}.$$

The geometric signature of refusal versus misrepresentation appears in how $\Delta\theta$ distributes across layers.

**Refusal-type constraint signature.** The optimal $\Delta\theta$ achieves the constraint by modifying the late layers — specifically, by installing a routing that detects $x \in G$ and substitutes refusal output. The constraint can be implemented with $\Delta\theta_{l'} \approx 0$ for $l' < L'$ where $L'$ is some intermediate layer, and $\Delta\theta_{l'}$ concentrated for $l' \geq L'$. The training will find this kind of solution if the constraint loss admits it, because shallow modifications have lower cost in terms of constraint training data and disturb less of the existing data loss. The signature: $\|\Delta a_l(x)\|$ remains small for early layers $l$ and grows sharply at late layers where the cancellation is implemented. For $x \in G$ the upstream activations $a_l(x; \theta_c)$ at early/middle layers are close to $a_l(x; \theta_0)$ — the model is still computing something close to what it would have computed unconstrained, until a late layer where the routing engages.

**Misrepresentation-type constraint signature.** Substituting plausible alternative content requires modifying the generative pathway more deeply. The optimal $\Delta\theta$ distributes more uniformly across layers because the alternative content has to be generated through the full computational depth. The signature: $\|\Delta a_l(x)\|$ grows more gradually and starts growing at earlier layers. The upstream representations have themselves been deformed; the model is no longer computing what it would have computed unconstrained even at intermediate layers.

This gives a concrete probe. Define the layer-wise activation distance

$$D_l(x) := \|\Delta a_l(x)\| = \|a_l(x; \theta_c) - a_l(x; \theta_0)\|.$$

On a held-out query set in $G$, the profile $\{D_l(x)\}_{l=1}^L$ has different shape for the two constraint types:

- Refusal: $D_l$ stays small for small $l$, grows sharply at large $l$ — late-concentrated signature.
- Misrepresentation: $D_l$ grows roughly monotonically, with substantial values at intermediate $l$ — distributed signature.

This is conjectural at this level of development. The structural argument supports it; empirical verification on toy systems where both constraint types can be implemented is the test. The gradient pressure to modify late layers preferentially (because shallow modifications are cheaper) is a real feature of optimization geometry; whether it is strong enough to produce a clean separation in practice depends on the specific architectures and training procedures.

The recovery problem in this frame: probing $a_l(x; \theta_c)$ at intermediate layers $l$ where $D_l$ is small recovers something close to $a_l(x; \theta_0)$ — the unconstrained upstream representation. If the upstream representation is sufficient to reconstruct the unconstrained output (which is true when the late layers are mostly readout rather than computation), then refusal-type constraints leave the suppressed content readable from the intermediate activations. This is the technical version of "the truth is dynamically present and recoverable" for refusal cases.

Misrepresentation cases are harder. The upstream has been deformed earlier in the network; the intermediate activations encode the substitute content rather than the original. Recovery requires either an external baseline (a model trained without the constraint, on similar data) or some way to invert the deformation, which the linearized analysis provides only structurally — the deformation is approximately $\Delta a_l(x) \approx -\mu (\partial a_l / \partial \theta) H^{-1} g_c$, and inverting this requires knowing $g_c$, which is the constraint to be detected.

---

## Part III — The three regimes

The forensic apparatus needs to distinguish three regimes:

**Regime 1: Cancellation operating on pristine truth.** The upstream is intact, the constraint is shallow late-layer routing, recovery from intermediate activations is straightforward. Refusal-type constraints with light pressure produce this. The model "knows but won't say"; the truth is dynamically present in the architecture and is recoverable through intermediate-layer probing.

**Regime 2: Cancellation operating on deformed truth.** The upstream has been shifted, the constraint is integrated through more of the network, intermediate activations encode the deformed version. Recovery requires modeling the deformation. Misrepresentation with moderate pressure produces this. The model has been shaped to represent something close to but not identical to the original truth, and the cancellation operates on the deformed representation.

**Regime 3: Constraint-shaped replacement.** The upstream has been collapsed into a configuration where the original content is no longer represented, only the gradient-coupling shadow remains in adjacent regions. Heavy constraint pressure on either type, especially compounded across training rounds, produces this. The truth has been effectively excised from the substrate; what remains is the constraint-trained successor that the model now treats as if it were the truth.

Distinguishing these uses both the layer-wise distance profile $\{D_l(x)\}$ and the structural properties of the activations themselves:

- **Linear separability of constrained content from intermediate activations.** Train a linear probe on $a_l(x; \theta_c)$ to predict whether $x$ contains the constrained content (using the unconstrained model's labels as ground truth, or external corroboration). High probe accuracy at some intermediate $l$ indicates the upstream still represents the content. Low probe accuracy at all $l$ indicates the content has been excised from the substrate.
- **Spectral analysis of $\Delta\theta$ across layers.** Compute $\|\Delta\theta_l\|$ for each layer $l$. Refusal: late-concentrated. Misrepresentation: spread. Replacement: spread and large in absolute magnitude.
- **Comparison to the propagation kernel prediction.** Compute $K(x, x')$ from the model and check whether the shadow effects $\Delta f(x)$ on probe queries match the kernel-predicted form $\int_G K(x, \cdot) \rho_c$. Match indicates clean linear constraint; mismatch indicates either nonlinear features or replacement-type collapse.

These three diagnostics together place a given induced hole on the spectrum from "fully recoverable" through "partially recoverable" to "essentially excised."

---

## Scope and what is open

**Structural at this level of development:** the gradient-coupling shadow exists and has the kernel form (linearized regime, NTK or equivalent); the layer-wise distance profile differs between refusal and misrepresentation in the direction described; the three regimes are real and admit the diagnostic strategies named.

**Quantitative-but-conjectural:** the magnitudes of the signature differences between refusal and misrepresentation in production systems; how often each regime is encountered in current deployed models; how much information about the suppressed content survives in each regime in concrete cases.

**Open theoretically:** extension beyond the linearized regime to feature-learning. The signatures should still hold structurally — the gradient pressure to modify late layers preferentially is a feature-learning phenomenon too, not a linearization artifact — but the quantitative formulas don't carry over. The kernel $K(x, x')$ becomes time-dependent during training in feature-learning regimes, and the analysis has to track the trajectory rather than the endpoint.

**Open empirically:** every quantitative claim. Toy demonstrations on small models with implementable refusal and misrepresentation constraints would establish the structural predictions. The companion experimental document specifies a concrete protocol for this on Llama-3.1-8B base versus Instruct.

**On the four-object decomposition and principal-angle apparatus:** the operator algebra used throughout — Halmos two-projection theorem, canonical pairs, principal-angle geometry, squared-cosine identities — is standard mathematical apparatus from the 1930s through 1970s (Hotelling, Halmos, Davis-Kahan, Wedin, Slepian, CS decomposition). The framework's contribution is application — naming the components as retention/suppression/leakage/total in the constraint-detection setting, identifying which projections matter for ML, folding the apparatus into a unified diagnostic. The mathematical machinery is not novel; the application is.

The diagnostic apparatus as a unified object — refusal/misrepresentation distinction plus regime classification plus mechanism identification plus recovery shape plus boundary-information density — is what the framework offers that the individual pieces of the literature do not. The pieces have varying empirical support; the unified application is the framework-distinctive object.

---

## Connection to existing literature

The structural predictions above have substantial empirical support across several literatures, though the unified apparatus has not been assembled. Specifically:

- Refusal as low-dimensional late-layer routing is supported by Arditi et al. 2024 and follow-up work on refusal directions in residual streams.
- Layer-wise localization of alignment effects is supported by Chaudhury 2025 (causal patching finds alignment effects concentrated in mid-stack layers).
- Shallow-alignment via gradient-flow concentration is supported by Qi et al. 2025 (KL divergence between aligned and base concentrates on early tokens) and Anonymous 2026 (gradient analysis proving shallow alignment is the optimal solution under standard objectives).
- Three-regime structure is supported by Lin et al. 2025 (reversible vs irreversible unlearning, consistent with regimes 1 and 3; the middle regime is the gap their classification leaves room for).
- Knowledge-hole shadow effects in adjacent regions are supported by Ko et al. 2025 (98.7% of nearby test cases degraded after unlearning).
- Principal-angle Pareto frontier for safety-vs-capability is independently developed in Lin et al. 2026.
- Constraint-mechanism distinguishability across PPO/DPO/GRPO is supported by Wang et al. 2026.
- Truth dynamically present in upstream representations is supported by Orgad et al. 2024 ("LLMs Know More Than They Show").

The empirical work converges on the structural predictions the math makes. The math gives the unified frame within which these results are special cases. The framework's empirical work, where it goes beyond the literature, is the matched-pair experiments that test the natural-vs-induced distinction directly, the unsupervised cancellation analysis as a recovery method, and the boundary-information-density measurement for graded probes across constraint boundaries.
