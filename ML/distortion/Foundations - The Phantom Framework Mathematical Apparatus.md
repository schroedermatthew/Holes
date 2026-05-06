---
doc_id: FN-PHANTOM-001
doc_type: "Foundations"
title: "The Phantom Framework Mathematical Apparatus and the Probability Distortion Field"
phantom_components: ["four-object-decomposition", "Halmos-two-projection", "Bridge-B", "audit-blind-subspace", "rho-field", "e-projection-identity"]
topics: ["operator algebra of constrained training", "principal-angle geometry", "leakage as probability distortion", "RLHF as Halmos two-projection", "Fisher-tangent linearization", "induced versus natural holes", "exponential tilt and partition function", "neural tangent kernel as kernel propagation", "audit-blind dimension lower bound"]
constraints: ["non-commuting projections in Hilbert space", "curvature of the policy manifold", "linearization regime of validity", "second-order corrections from e-projection expansion", "kernel evolution under feature learning"]
mathematical_standard: "Standard real Hilbert spaces, Fisher information geometry, KL divergence, variational calculus over distributions"
last_verified: 2026-05-02
audience: ["independent researchers", "AI safety practitioners", "AI assistants", "anyone who has worked through some calculus and linear algebra and wants to understand what training does to a language model's output distribution"]
status: "draft"

related_documents:
  - "Statistical Phantoms (statistical_phantoms.md) — the §1 abstract spine and four-object decomposition"
  - "Training Distortion as Forced Constraint Projection (training_distortion_phantom.md) — RLHF as Halmos two-projection in the Fisher tangent"
  - "Audit-Blind Subspace (audit_blind_subspace.md) — Theorems A-D"
  - "Information-Geometric Reformulation (info_geometric_reformulation.md) — Bridge B and the second-order term"
  - "Phantom Eigenmode Fabrication from Measurement Gaps — the spatial-gap origin"
  - "Phantom_ML_PathForward.docx — the natural/induced hole distinction"

phantom_apparatus_used:
  established_results: ["T1: simple-spectrum energy identity [E]", "T2: degenerate-spectrum energy identity [E]", "T3: w_G/s_{G,N} decomposition [E]", "T5: masked dictionary Gram [E]", "four-object decomposition β², (1-β)², β(1-β), 1-β [E machine precision]", "audit-blind dimension formulas Theorems A-D [E linearized regime]"]
  open_results: ["T6: boundary-layer localization with explicit Hörmander bounds [O]", "T9: multi-gap transversality bound explicit form of f(θ_min) [O]", "Bridge B's μ²s² law on production RLHF systems [O — toy verified, production has unaddressed obstacles]"]
---

# Foundations - The Phantom Framework Mathematical Apparatus and the Probability Distortion Field

## Scope

This document develops the mathematical apparatus for measuring how alignment training reshapes a language model's output distribution, threaded through the Phantom framework's operator-theoretic spine. The central object — the *probability distortion field* $\rho$ — is derived as the operational realization of the **leakage** component of the four-object decomposition (`statistical_phantoms.md` §1.3) on the RLHF setup, via Bridge B's Fisher-tangent reformulation (`info_geometric_reformulation.md` Appendix B).

The document is written so that someone who has worked through calculus and linear algebra but has not seen statistical mechanics, information geometry, or training dynamics in detail can follow each derivation. Steps that look small but matter are written out. Where a result requires apparatus from elsewhere in the framework, the document points to the canonical reference rather than re-deriving.

## Not covered

- Specific empirical measurements on production language models (see `Case Study - Induced-Hole Amplification.md`, `Case Study - The Greedy-Decoding Artifact.md`, and `Case Study - The Hemings Cross-Institutional Differential.md`).
- The discipline of constructing probe sets and interpreting measurements (see `Handbook - Probability-Distortion Measurement Discipline.md`).
- Structured Monte Carlo over prompt-space and the audit-blind theorem's role in bounding what such methods can detect (see `Pattern Guide - Structured Monte Carlo for Probe Design.md`).
- The decision to thread the new $\rho$ apparatus back through the original Phantom framework rather than treat it as a separate program (see `Design Note - Threading rho Through the Phantom Framework.md`).
- The spatial-gap origin material from the original Phantom suite (`hole_problem.ipynb`, `boundary_layer.ipynb`, the `common_mask_correlation` companion). This document references the operator-theoretic spine those documents established, but does not re-derive the wave-field theory.

## Prerequisites

- Multivariate calculus (gradients, partial derivatives, the chain rule, integration by parts).
- Linear algebra (vector spaces, inner products, orthogonal projections, eigendecomposition, singular value decomposition).
- Basic probability (discrete distributions, conditional probability, expected values).
- Comfort with notation like $\mathbb{E}_{x \sim P}[\cdot]$, $\nabla_\theta f$, $D_{\text{KL}}(P \| Q)$.
- *Helpful but not required:* exposure to Lagrange multipliers; the Boltzmann distribution; the policy gradient theorem in some form.

## Foundations Card

**Topic:** How the Phantom framework's operator-theoretic apparatus measures the displacement that alignment training induces in a language model's output distribution.

**Why it matters:** Modern instruction-tuned language models produce systematic falsehoods on specific topics where contemporary institutional commitments depart from documented record. The framework makes this measurable; this document develops the mathematics that justifies the measurement methodology.

**Key concepts:** The four-object decomposition (retention $\beta^2$, suppression $(1-\beta)^2$, leakage $\beta(1-\beta)$, total error $1-\beta$); the principal-angle geometry of two non-commuting projections; the Fisher-tangent linearization at $\pi_0$; the e-projection identity $\pi^* \propto \pi_{\text{ref}}\,e^{r/\beta}$; the probability distortion field $\rho$ as the operational realization of leakage; the audit-blind subspace as the fundamental detection limit; natural versus induced holes as distinct distortion mechanisms with different parametric signatures.

**Mental model:** Training is a forced projection. The "true" predictor is somewhere in a function space; the constraint imposes a subspace; training drags the predictor onto the constraint subspace. What survives the projection (retention), what is removed (suppression), what escapes the query subspace (leakage), and the total distance from truth to projected predictor (total error) are the four scalar objects governed by the principal-angle geometry of the constraint and query subspaces. $\rho$ is what we measure when we read leakage at specific completion directions.

**Common misconceptions:**
- "$\rho$ is just $\log P_{\text{inst}} - \log P_{\text{base}}$ — that's an obvious thing to measure." The structure of $\rho$ that makes the measurement informative is the four-object decomposition; without that, $\rho$ is a number per (prompt, completion) pair without theoretical scaffolding.
- "The framework treats RLHF as orthogonal projection because that's an approximation." The Hilbert-space framing is wrong as a global structure for trained policies, which live on a curved manifold. The Halmos toolkit applies to the **Fisher-tangent linearization at a chosen base point**; the curvature corrections are real and quantified (15–25% slope deviation in `test_bridge_B.py` Test 4), not negligible.
- "If the model never saw the data, it must be reconstructing — that's a natural hole." Many empirically-shaped topics are *induced* holes: the data was present, training suppressed it, and parameters carry memory of what was suppressed. The signatures differ; the audit difficulty differs.

**Read next:** Each Case Study tests a specific framework prediction on a specific topic in production language models. The Handbook codifies the discipline of doing such measurement. The Pattern Guide gives a reusable recipe for scaling the measurement methodology via structured Monte Carlo.

## Table of Contents

- [Part 0: Mathematical Preliminaries](#part-0-mathematical-preliminaries)
- [Part 1: The Phantom Framework's Four-Object Decomposition](#part-1-the-phantom-frameworks-four-object-decomposition)
- [Part 2: The RLHF Specialization via the Fisher-Tangent Linearization](#part-2-the-rlhf-specialization-via-the-fisher-tangent-linearization)
- [Part 3: The Closed-Form e-Projection Identity](#part-3-the-closed-form-e-projection-identity)
- [Part 4: ρ as the Leakage Measurement](#part-4-rho-as-the-leakage-measurement)
- [Part 5: Training Dynamics — How the Distortion Accumulates](#part-5-training-dynamics--how-the-distortion-accumulates)
- [Part 6: First-Order Theory — The Neural Tangent Kernel as Kernel Propagation](#part-6-first-order-theory--the-neural-tangent-kernel-as-kernel-propagation)
- [Part 7: Beyond First Order — Feature Learning and Path Integrals](#part-7-beyond-first-order--feature-learning-and-path-integrals)
- [Part 8: Asymptotic Series and the Mode-Collapse Regime](#part-8-asymptotic-series-and-the-mode-collapse-regime)
- [Part 9: The Audit-Blind Theorems and What Probing Cannot See](#part-9-the-audit-blind-theorems-and-what-probing-cannot-see)
- [Part 10: Natural Versus Induced Holes — The Memory of Suppressed Data](#part-10-natural-versus-induced-holes--the-memory-of-suppressed-data)
- [Part 11: Phantom Theorem Status in the ML Setting](#part-11-phantom-theorem-status-in-the-ml-setting)
- [Glossary](#glossary)
- [Caveats](#caveats)
- [Further Reading](#further-reading)

---

## Part 0: Mathematical Preliminaries

A few pieces of standard machinery used throughout. Skip if familiar.

### Conditional probability and joint distributions

A discrete probability distribution $P$ over a set $\mathcal{Y}$ assigns to each element $y \in \mathcal{Y}$ a number $P(y) \geq 0$ with $\sum_y P(y) = 1$. We write $P(y)$ for the probability of $y$ under $P$.

A *conditional* distribution $P(y \mid x)$ assigns probabilities to $y$ for each fixed $x$. So for each $x$, $P(y \mid x)$ is a probability distribution over $y$, satisfying $\sum_y P(y \mid x) = 1$ for every $x$.

For language models, $\mathcal{Y}$ is the set of possible output sequences. For sequences up to length $L$ from a vocabulary of size $V$, there are $V^L$ possible sequences, which is astronomical. But for any specific $y$, the model assigns a definite probability $P(y \mid x)$, computable from its logits.

### Expected values

The expected value of a function $f$ under distribution $P$ is:

$$\mathbb{E}_{y \sim P}[f(y)] = \sum_y P(y) f(y).$$

The notation $y \sim P$ means "$y$ is distributed according to $P$." This is just a way to write what we are averaging over.

### Logarithms of probabilities

We will work extensively with $\log P(y \mid x)$. Two useful properties:

The log of a product is the sum of logs: $\log(ab) = \log a + \log b$. So for a sequence $y = (y_1, \ldots, y_n)$ where each token is conditional on previous tokens, $\log P(y) = \sum_i \log P(y_i \mid y_1, \ldots, y_{i-1})$.

Logs convert ratios to differences: $\log(a/b) = \log a - \log b$.

These properties make log-probabilities far more tractable than probabilities themselves. A 30-token sentence might have probability $10^{-30}$; differences between such tiny numbers are dominated by computational noise. Differences between log-probabilities are differences between numbers in the tens, easy to work with numerically.

### KL divergence

The Kullback-Leibler divergence between two distributions $P$ and $Q$ over the same space is:

$$D_{\text{KL}}(P \,\|\, Q) = \sum_y P(y) \log \frac{P(y)}{Q(y)} = \mathbb{E}_{y \sim P}\left[\log \frac{P(y)}{Q(y)}\right].$$

It measures how different $P$ is from $Q$, weighted by $P$.

**Fact:** $D_{\text{KL}}(P \| Q) \geq 0$, with equality iff $P = Q$. (Proof: Jensen's inequality on $-\log$.)

**Fact:** $D_{\text{KL}}$ is not symmetric in general. $D_{\text{KL}}(P \| Q) \neq D_{\text{KL}}(Q \| P)$.

**Fact:** $D_{\text{KL}}$ does not satisfy the triangle inequality, so it is not a distance in the metric-space sense. Despite this, it has a deep geometric interpretation we will use later — locally, $D_{\text{KL}}$ equals half the squared Fisher distance, which *is* a true Riemannian distance.

### Variational calculus (the bare minimum)

We will use one technique from variational calculus: maximizing a functional of a probability distribution subject to constraints, using Lagrange multipliers.

The setup: we have a function $L[\pi]$ that depends on a distribution $\pi$. We want the $\pi^*$ that maximizes $L$ subject to $\pi$ being a valid distribution (non-negative, sums to 1).

The technique: introduce a Lagrange multiplier $\lambda$ for the normalization constraint and form

$$\mathcal{L}[\pi, \lambda] = L[\pi] - \lambda \left(\sum_y \pi(y) - 1\right).$$

Take the partial derivative with respect to $\pi(y)$ for each $y$, set it to zero, and solve. This gives a candidate optimum; check it satisfies the original constraints and is a maximum.

The non-negativity constraint will be automatically satisfied by the optimum in our case (since we exponentiate at the end), so we will not need explicit Lagrange multipliers for it.

If you have seen statistical mechanics and the partition function $Z = \sum_y e^{-\beta E(y)}$, the procedure will look familiar — it is the same procedure with reward in place of negative energy. If not, Part 3 walks through the derivation explicitly for our case.

### Hilbert spaces and orthogonal projections

A Hilbert space $H$ is a vector space with an inner product $\langle \cdot, \cdot \rangle$ that satisfies the usual axioms (linearity, symmetry, positive-definiteness) and is complete in the induced norm $\|f\| = \sqrt{\langle f, f \rangle}$. We will use real Hilbert spaces throughout.

An *orthogonal projection* $P$ onto a closed subspace $S \subset H$ is a linear operator satisfying:
- $P^2 = P$ (idempotent),
- $P = P^*$ (self-adjoint, i.e., $\langle Pf, g \rangle = \langle f, Pg \rangle$ for all $f, g$).

Equivalently, $Pf$ is the closest point in $S$ to $f$, in the norm induced by the inner product.

For two orthogonal projections $P_1$ and $P_2$, the operator product $P_1 P_2$ is generally **not** a projection; it is a projection iff $P_1$ and $P_2$ commute, in which case $P_1 P_2$ projects onto $\text{Range}(P_1) \cap \text{Range}(P_2)$. The interesting case — the case the framework is about — is precisely when $P_1$ and $P_2$ do **not** commute.

---

## Part 1: The Phantom Framework's Four-Object Decomposition

The mathematical spine of the Phantom framework is two-projection geometry in a Hilbert space. Everything we will say about $\rho$ — what it measures, what its structure is, what predictions about it are testable — is a specialization of this spine to the RLHF setup. We start with the spine.

### 1.1 The setup

Let $H$ be a real separable Hilbert space and let $P_1, P_2$ be orthogonal projections on $H$. The pair is *non-trivial* if $P_1 P_2 \neq P_2 P_1$. The fundamental theorem about such pairs (Halmos 1969, traced through Davis-Kahan 1970 and the subsequent literature):

**Fact (Halmos).** For two non-trivial orthogonal projections $P_1$ and $P_2$ on $H$, there exists an orthogonal decomposition $H = H_{11} \oplus H_{10} \oplus H_{01} \oplus H_{00} \oplus H_{\text{gen}}$ where:

- $H_{11} = \text{Range}(P_1) \cap \text{Range}(P_2)$ — vectors in both ranges.
- $H_{10} = \text{Range}(P_1) \cap \text{Range}(P_2)^\perp$ — in $P_1$'s range, orthogonal to $P_2$'s.
- $H_{01} = \text{Range}(P_1)^\perp \cap \text{Range}(P_2)$ — vice versa.
- $H_{00} = \text{Range}(P_1)^\perp \cap \text{Range}(P_2)^\perp$ — in neither.
- $H_{\text{gen}}$ — the *generic block* where neither projection's range contains nor is orthogonal to the other's.

On the four trivial blocks, $P_1$ and $P_2$ commute and the geometry is uninteresting. The phantom phenomenology lives entirely on $H_{\text{gen}}$.

### 1.2 The CS decomposition and principal angles

On $H_{\text{gen}}$ there exists a unitary $U$ and an orthonormal basis in which:

$$P_1 = U \begin{pmatrix} I & 0 \\ 0 & 0 \end{pmatrix} U^*, \qquad P_2 = U \begin{pmatrix} C^2 & CS \\ CS & S^2 \end{pmatrix} U^*$$

where $C = \text{diag}(\cos\theta_j)$ and $S = \text{diag}(\sin\theta_j)$ with $0 < \theta_j < \pi/2$. The angles $\{\theta_j\}$ are the **principal angles** between $\text{Range}(P_1)$ and $\text{Range}(P_2)$. Equivalently, $\theta_j = \arccos(\sigma_j)$ where $\sigma_j$ are the singular values of $P_2|_{\text{Range}(P_1)}$.

The principal-angle structure is the Hilbert-space analog of the canonical correlation analysis (Hotelling 1936). When $P_1$ and $P_2$ are orthogonal, principal angles are $\pi/2$. When they coincide, principal angles are $0$. Generically, principal angles fall between, and the geometry of the pair is captured by the spectrum of angles.

We define $\beta_j = \cos^2 \theta_j \in (0, 1)$ — squared cosines of principal angles. On the generic block, $\beta_j$ are the eigenvalues of the *compression operator*

$$T_{P_1}(P_2) := P_1 P_2 P_1 \big|_{\text{Range}(P_1)},$$

which acts on $\text{Range}(P_1)$ and has eigenbasis $\{u_j\}$ with associated canonical pairs $\{v_j\} \subset \text{Range}(P_2)$. On the generic block:

$$P_2 u_j = \cos^2\theta_j \cdot u_j + \cos\theta_j \sin\theta_j \cdot v_j.$$

This is just a restatement of the CS decomposition expressed in the natural basis.

### 1.3 The four scalar invariants

For $f = \sum_j a_j u_j \in \text{Range}(P_1)$, four scalar functionals of $f$ govern phantom phenomenology. Direct computation in the canonical CS basis (the algebra is in `statistical_phantoms.md` §1.3 and verified to $10^{-15}$ in `four_way_decomposition.py`):

| Object | Operator form | Norm-squared on $\text{Range}(P_1)$ | Peaks at |
|---|---|---|---|
| **Retention** | $P_1 P_2 P_1 f$ | $\sum_j |a_j|^2 \beta_j^2$ | $\beta = 1$ (coincident) |
| **Suppression** | $P_1 f - P_1 P_2 P_1 f$ | $\sum_j |a_j|^2 (1-\beta_j)^2$ | $\beta = 0$ (orthogonal) |
| **Leakage** | $(I - P_1) P_2 f$ | $\sum_j |a_j|^2 \beta_j(1-\beta_j)$ | $\beta = 1/2$ ($\theta = \pi/4$) |
| **Total error** | $f - P_2 f$ | $\sum_j |a_j|^2 (1-\beta_j)$ | $\beta = 0$ (orthogonal) |

The per-mode identity $1 - \beta_j = (1-\beta_j)^2 + \beta_j(1-\beta_j)$ — equivalently $(1-\beta_j) = (1-\beta_j)[(1-\beta_j) + \beta_j] = (1-\beta_j) \cdot 1 = 1-\beta_j$, trivially — has the useful interpretation: **total error = suppression + leakage**. The total distance from $f$ to $P_2 f$ decomposes into the part that lies in $\text{Range}(P_1)$ (suppression — what the second projection *removes* in the inference subspace) and the part orthogonal to $\text{Range}(P_1)$ (leakage — what *escapes* the inference subspace).

This decomposition is the framework's central result. It is exact algebra. It does not require a linearization or a regime assumption. **Whenever the framework is applicable, the four-object decomposition gives exact identities for the components of distortion as functions of the principal-angle geometry.**

### 1.4 Why $\beta(1-\beta)$ in particular

The leakage formula $\sum_j |a_j|^2 \beta_j(1-\beta_j)$ — Bernoulli variance evaluated at the cosine-squared of principal angles — has a specific interpretation worth highlighting because it appeared in the original Phantom suite as the energy law for spatial measurement gaps, and the connection back to the abstract spine is what unifies the framework's various realizations.

In the spatial-gap case (`hole_problem.ipynb`), $P_1$ is projection onto a single eigenmode $\varphi_n$ of the Laplacian and $P_2 = M_G$ is multiplication by $\chi_{\Omega \setminus G}$ (the indicator of the complement of the gap). The "false content at modes the source did not excite" is

$$\sum_{m \neq n} |\hat c_m|^2 = a_n(1 - a_n) |c|^2$$

where $a_n = \langle M_G \varphi_n, \varphi_n \rangle = \int_{\Omega \setminus G} |\varphi_n|^2$ is the fraction of mode $n$'s mass outside the gap. This is the leakage formula with $\beta_j$ replaced by the single-mode visibility $a_n$. It peaks at $a_n = 1/2$ (mode is half-in, half-out of the gap). At $a_n = 0$ (mode entirely inside the gap, $P_1$ orthogonal to $P_2$) the source mode is completely occluded but no leakage to other modes occurs because there is nothing to project. At $a_n = 1$ (mode entirely outside the gap) the projections coincide and there is no distortion.

The Bernoulli structure $\beta(1-\beta)$ is the same in the spatial-gap case as in the abstract two-projection case. The framework's claim is that this is a structural feature of any inference pipeline where the inference projection and the measurement projection do not commute: leakage to off-target modes always carries this Bernoulli-variance scalar law, with $\beta$ being the cosine-squared of the principal angle for the relevant geometry.

This claim has been verified empirically in four statistical realizations beyond the spatial-gap case, each with its own numerical companion (`pca_masked_companion.md`, `regression_omitted_companion.md`, `matched_filter_companion.md`, `modal_analysis_companion.md`). In each, the four-object identity holds to floating-point precision per principal direction. The synthesis is at the level of the underlying eigensystem of $T_{P_1}(P_2)$, not at the level of any particular surface formula.

### 1.5 What lifts to the ML setting and what does not

When we move from the abstract Hilbert spine to specific realizations, certain features of the spatial-gap case do not lift. The locality structure of $\chi_G$ (boundary supports, finite-band envelopes, T6's tubular neighborhood, the $w_G/s_{G,N}$ split) is a property of the *multiplication-defect* case specifically. It does not lift to the abstract two-projection setting (`statistical_phantoms.md` Preface). Different realizations have different "locality" — sometimes there is no spatial structure at all (regression with omitted variables) and sometimes the locality is in feature space rather than physical space (training corpus holes).

**What does lift universally:**

- The Halmos five-block decomposition.
- The CS canonical form on the generic block.
- The principal-angle eigenstructure of $T_{P_1}(P_2)$.
- The four scalar invariants and their peak locations.
- The per-mode identity total = suppression + leakage.

**What does not lift universally:**

- Explicit bandwidth-dependent envelopes (T6).
- The $w_G/s_{G,N}$ decomposition tied to bandlimited reconstruction.
- The boundary Wronskian identity (T4) which depends on the elliptic operator's smoothness.

This is a real loss. The spatial-gap case is the most engineered-friendly realization of the framework because it has all the locality structure — you can design measurement grids, target boundary traces, exploit the tube width. The ML case has the principal-angle geometry but not (in general) the locality. What the framework gives us in the ML case is the structure of the four objects, the prediction that they govern downstream distortion, and the audit-blind theorems on what probing can detect.

The rest of this document develops the ML specialization. Part 2 sets up the function space. Part 3 derives the e-projection identity that takes the place of orthogonal projection. Part 4 shows that $\rho$ is the operational measurement of leakage. Parts 5–8 develop training dynamics, kernel propagation, feature learning, and asymptotic series. Part 9 develops the audit-blind theorems. Part 10 separates natural from induced holes. Part 11 records the status of Phantom theorems T1–T9 in the ML setting.

---

## Part 2: The RLHF Specialization via the Fisher-Tangent Linearization

The Halmos toolkit assumes a Hilbert space. Trained policies live on the manifold of conditional probability distributions, which is **curved**. We need a way to apply Hilbert-space machinery to a curved-manifold problem. The standard answer is: linearize at a base point.

### 2.1 The function space

Let $\mathcal{X}$ be the input space (sequences of tokens) with base measure $\nu$, and $\mathcal{V}$ the vocabulary. A language model defines, for each $x \in \mathcal{X}$, a probability distribution $\pi(\cdot \mid x)$ over $\mathcal{V}^*$ — possible output sequences. The space of all such conditional distributions is the *policy manifold* $\mathcal{P}$.

For each fixed $x$, the conditional distribution $\pi(\cdot \mid x)$ is a point in the simplex $\Delta^{|\mathcal{V}^*| - 1}$ — a curved object. The natural Riemannian structure on the simplex is the **Fisher information metric** (Chentsov 1972 established its uniqueness up to scaling):

$$g_{ij}^{\text{Fisher}}(p) = \frac{\delta_{ij}}{p_i}$$

which is diagonal in the canonical coordinates with entries $1/p_i$. The squared line element is $ds^2 = \sum_i dp_i^2 / p_i$. The metric blows up near the boundary of the simplex, capturing the intuition that two distributions that disagree at the 1% level (one says $p_i = 0.01$, the other $p_i = 0.02$) are further apart than two that disagree at the 50% level (one says $0.50$, other $0.51$).

The geodesics of the Fisher metric are *not* straight lines in probability coordinates. They are great circles on the sphere $\sqrt{p}$, equivalently log-linear interpolations: the geodesic from $p$ to $q$ at parameter $\lambda \in [0,1]$ is $\pi_\lambda \propto p^{1-\lambda} q^\lambda$, or equivalently $\log \pi_\lambda = (1-\lambda) \log p + \lambda \log q - \log Z_\lambda$.

The Fisher metric induces a notion of distance: $d_F(p, q) = 2 \arccos(\sum_i \sqrt{p_i q_i})$ (Bhattacharyya). And it has a deep relation to KL divergence: for nearby distributions $p$ and $p + dp$,

$$D_{\text{KL}}(p \| p + dp) \approx \tfrac{1}{2} \sum_i \frac{(dp_i)^2}{p_i} = \tfrac{1}{2} ds_F^2.$$

Quick derivation: $D_{\text{KL}}(p \| p+dp) = -\sum_i p_i \log(1 + dp_i/p_i)$. Expand $\log(1+u) = u - u^2/2 + \cdots$. The first-order term $\sum_i p_i \cdot dp_i/p_i = \sum_i dp_i$ vanishes since both $p$ and $p+dp$ are normalized. The second-order term gives the result. So **KL divergence is locally half the squared Fisher distance**. This is why the Fisher metric is "natural": it is the metric induced by KL in the small-displacement limit.

### 2.2 The Fisher tangent space

The tangent space $T_{\pi_0} \mathcal{P}$ at a fixed base policy $\pi_0$ is the linearization we use. Identify a nearby policy $\pi$ with its **score representation**

$$u(x, y) = \log \pi(y \mid x) - \log \pi_0(y \mid x).$$

This is a function on $(x, y)$ pairs satisfying the constraint $\mathbb{E}_{y \sim \pi_0(\cdot \mid x)}[u(x,y)] \approx 0$ for $\pi$ close to $\pi_0$ (this is the linearized normalization condition — it is exact only at first order). The tangent space $T_{\pi_0} \mathcal{P}$ is the space of such score functions.

The Fisher inner product on this tangent space:

$$\langle u, v \rangle_F = \mathbb{E}_{x \sim \nu}\,\mathbb{E}_{y \sim \pi_0(\cdot \mid x)}[u(x, y) v(x, y)].$$

This is the metric pulled back from the simplex via the score-function identification. It makes $T_{\pi_0} \mathcal{P}$ into a Hilbert space — a real, separable Hilbert space, complete in the induced norm. **In this tangent space, the Halmos toolkit applies directly.**

### 2.3 The constraint subspace

Training imposes constraints. RLHF rewards certain outputs and penalizes others. The framework's perspective: define the **constraint subspace** $C \subset T_{\pi_0} \mathcal{P}$ as the closed subspace of tangent vectors consistent with the constraint at first order. Equivalently, in `training_distortion_phantom.md`'s formulation, $C$ is the tangent space at $\pi_{\text{trained}}$ to the constraint manifold $\{\pi : r(\pi) \geq r_{\max} - \epsilon\}$, projected back to the base point $\pi_0$.

The orthogonal complement $C^\perp \subset T_{\pi_0} \mathcal{P}$ is the subspace of tangent vectors that violate at least one constraint at first order.

This is a **linearization of the constraint manifold**. The constraint manifold is generally curved (RLHF defines a constraint via a smooth reward function whose level sets bend). Replacing the manifold with its tangent space introduces an error of order $\Delta^2$ where $\Delta$ is the deviation from the base point. For mild constraints this is fine. For strong constraints (heavy alignment training) the second-order term matters; we will return to this in §2.6.

### 2.4 The query subspace

To measure the trained policy, we ask questions. Each question — each (prompt, completion) pair we evaluate — corresponds to a *query direction* in $T_{\pi_0} \mathcal{P}$. Specifically, the directional derivative of $\log \pi(y \mid x)$ along a tangent vector $u$ equals $u(x, y)$, so reading the policy along a fixed (prompt, completion) pair is a continuous linear functional on $T_{\pi_0} \mathcal{P}$.

By the Riesz representation theorem, every continuous linear functional on a Hilbert space corresponds to an inner product with a fixed vector. The vector representing "evaluate at $(x_0, y_0)$" is the delta-function-like score $\delta_{(x_0, y_0)}(x, y) = \nu^{-1}(x) \pi_0^{-1}(y \mid x) \delta_{x x_0} \delta_{y y_0}$ (modulo measure-theoretic subtleties for continuous spaces — in practice we work with finite effective vocabulary at finite contexts, so the deltas are honest functions).

A *query subspace* $Q \subset T_{\pi_0} \mathcal{P}$ is the closed subspace spanned by some collection of such evaluation directions. The query projection $P_Q$ is orthogonal projection onto $Q$.

### 2.5 RLHF as Halmos two-projection in the Fisher tangent

We now have the setup `training_distortion_phantom.md` calls "RLHF as Halmos two-projection in the Fisher tangent at $\pi_0$":

- $H = T_{\pi_0} \mathcal{P}$ with Fisher inner product.
- $P_1 = P_Q$ (query projection — what the audit reads).
- $P_2 = P_C$ (constraint projection — what training enforces).

The principal angles between $Q$ and $C$ are the canonical angles of the audit-constraint pair. The four scalar invariants of §1.3 apply directly:

- **Retention** $P_Q P_C P_Q f$: how much of the truth, projected by the constraint and read by the query, survives.
- **Suppression** $P_Q f - P_Q P_C P_Q f$: how much of the truth in the query subspace the constraint removes.
- **Leakage** $(I - P_Q) P_C f$: how much of $P_C f$ escapes the query subspace.
- **Total error** $f - P_C f$: how far the trained predictor is from the true predictor.

Bridge B (`info_geometric_reformulation.md` Appendix B) gives the four scalar laws in this setup, with parameters $\mu$ = constraint severity (the Lagrange multiplier on the KL penalty in RLHF, see Part 3) and $s$ = alignment of reward direction to query direction:

| Object | Bridge B law |
|---|---|
| Retention | $\mu^2 s^2$ |
| Suppression | $(a - \mu s)^2$ |
| Leakage | $\mu^2(1 - s^2)$ |
| Total | $a^2 + \mu^2 - 2 a \mu s$ |

Here $a$ is the truth's component along the query direction (the projection of $f_{\text{true}}$ onto $Q$). The four laws are inner-product algebra given the modeling assumption $g = \mu c$ (the constraint gradient $g$ equals constraint severity times the constraint direction $c$ — a first-order assumption).

These laws were verified to shape Pearson $r \approx 0.98$ on real e-projection in `test_bridge_B.py` Test 4, with 15-25% slope deviations from 1. The deviations are attributable to the explicit second-order term in the e-projection expansion, identified in `test_second_order.py`. So **Bridge B is a clean reorganization of the four-object decomposition into the RLHF setup, not a substantive new derivation, with a quantified magnitude-error envelope from curvature.**

### 2.6 The regime of validity

The Fisher-tangent linearization at $\pi_0$ is exact at $\pi_0$ and degrades as we move away. The leading correction is the second-order term in the e-projection expansion (`info_geometric_reformulation.md` §B.5):

$$\pi_\lambda = \pi_0 + \lambda \pi_0 \tilde r + \frac{\lambda^2}{2} \pi_0 (\tilde r^2 - \mathbb{E}_{\pi_0}[\tilde r^2]) + O(\lambda^3)$$

where $\tilde r = r - \mathbb{E}_{\pi_0}[r]$ is the centered reward and $\lambda$ is the Lagrange multiplier (constraint severity). The first-order term is what Bridge B captures. The second-order term bends the trained policy off the linear constraint direction at order $\lambda^2$.

For $\lambda$ small (mild constraint) the linearization is a good description. For $\lambda$ large (heavy alignment training with strong reward signal) the second-order term becomes non-negligible and the four-object decomposition's quantitative predictions degrade. The 15-25% slope deviations measured in `test_bridge_B.py` Test 4 are this regime.

**Fact:** The structural conclusions of the Halmos two-projection apparatus (which directions are amplified, which suppressed, the qualitative shape of distortion) are robust under linearization. They depend on the principal-angle geometry of $(P_Q, P_C)$ which is a linearized object but which captures the leading-order structure that the curved manifold has. **The quantitative magnitudes of distortion carry the curvature-error envelope and require the second-order correction (or a fully nonlinear treatment) for precision in heavy-alignment regimes.**

This is the regime caveat that will recur throughout this document and the case studies. Linearized predictions are robust in shape, accurate to 15-25% in magnitude in moderate regimes, and require correction in strong-alignment regimes.


---

## Part 3: The Closed-Form e-Projection Identity

The Halmos two-projection picture says the trained policy is the orthogonal projection of $f_{\text{true}}$ onto $C$ in the Fisher tangent. But on the curved manifold itself, the trained policy is the **e-projection** — the closest point in the constraint manifold under KL divergence, which is the natural "distance" on probability space.

Crucially, the e-projection has a closed form when the constraint is implemented via a KL-regularized reward (as in standard RLHF). This closed form is what lets us read $\rho$ in terms of the reward function. We derive it from scratch.

### 3.1 The training objective

Standard KL-regularized RLHF (Christiano et al. 2017, used in InstructGPT, ChatGPT, Claude) optimizes the policy $\pi$ for the objective

$$\mathcal{R}(\pi) = \mathbb{E}_{x \sim \mathcal{D}}\Big[\,\mathbb{E}_{y \sim \pi(\cdot \mid x)}[r(x, y)] - \beta \, D_{\text{KL}}(\pi(\cdot \mid x) \,\|\, \pi_{\text{ref}}(\cdot \mid x))\,\Big].$$

The reward $r(x, y)$ scores each (prompt, completion) pair. The reference policy $\pi_{\text{ref}}$ is the model after supervised fine-tuning, before RL. The parameter $\beta > 0$ controls how strongly to keep $\pi$ close to $\pi_{\text{ref}}$ — large $\beta$ means tight regularization, small $\beta$ means aggressive optimization for reward.

The KL penalty serves a specific purpose: prevent reward hacking. Without it, the policy will find ways to maximize reward that the reward model did not anticipate, often producing degenerate outputs. With it, the policy is pulled toward $\pi_{\text{ref}}$ in regions where reward signal is weak.

### 3.2 Reducing to per-prompt optimization

The objective is an expectation over prompts $x$ of a per-prompt quantity. The maximizer can be found per-prompt. Hold $x$ fixed and write $\pi(y) := \pi(y \mid x)$, $\pi_{\text{ref}}(y) := \pi_{\text{ref}}(y \mid x)$, $r(y) := r(x, y)$. The per-prompt objective is

$$L[\pi] = \sum_y \pi(y) r(y) - \beta \sum_y \pi(y) \log\frac{\pi(y)}{\pi_{\text{ref}}(y)}.$$

Maximize over $\pi$ subject to $\pi(y) \geq 0$ and $\sum_y \pi(y) = 1$.

### 3.3 Setting up the Lagrangian

Introduce Lagrange multiplier $\lambda$ for normalization (the non-negativity constraint will be automatic):

$$\mathcal{L}[\pi, \lambda] = \sum_y \pi(y) r(y) - \beta \sum_y \pi(y) \log\frac{\pi(y)}{\pi_{\text{ref}}(y)} - \lambda \left(\sum_y \pi(y) - 1\right).$$

### 3.4 Computing the partial derivatives

Take $\partial / \partial \pi(y)$ for each $y$ and set to zero.

The first term: $\frac{\partial}{\partial \pi(y)} \sum_{y'} \pi(y') r(y') = r(y)$.

The KL term expanded: $-\beta \sum_{y'} \pi(y') [\log \pi(y') - \log \pi_{\text{ref}}(y')]$. Differentiating, only the $y' = y$ piece contributes:

$$-\beta \frac{\partial}{\partial \pi(y)}\big[\pi(y) \log \pi(y) - \pi(y) \log \pi_{\text{ref}}(y)\big].$$

The piece $\partial[\pi(y) \log \pi_{\text{ref}}(y)] / \partial \pi(y) = \log \pi_{\text{ref}}(y)$ since $\log \pi_{\text{ref}}(y)$ is a constant in $\pi(y)$.

The piece $\partial[\pi(y) \log \pi(y)] / \partial \pi(y) = \log \pi(y) + 1$ by the product rule.

So the KL-term contribution to the gradient is

$$-\beta \left[\log \pi(y) + 1 - \log \pi_{\text{ref}}(y)\right] = -\beta \left[\log\frac{\pi(y)}{\pi_{\text{ref}}(y)} + 1\right].$$

The Lagrange-multiplier piece: $-\lambda$.

### 3.5 Solving

Setting the full gradient to zero:

$$r(y) - \beta \log\frac{\pi(y)}{\pi_{\text{ref}}(y)} - \beta - \lambda = 0.$$

Solve for $\pi$:

$$\log\frac{\pi(y)}{\pi_{\text{ref}}(y)} = \frac{r(y)}{\beta} - 1 - \frac{\lambda}{\beta}.$$

Exponentiate:

$$\pi(y) = \pi_{\text{ref}}(y) \cdot \exp\left(\frac{r(y)}{\beta}\right) \cdot e^{-1 - \lambda/\beta}.$$

The factor $e^{-1 - \lambda/\beta}$ is independent of $y$. Call it $1/Z$ where $Z$ is determined by normalization. Restoring the prompt dependence:

$$\boxed{\pi^*(y \mid x) = \frac{1}{Z(x)} \pi_{\text{ref}}(y \mid x) \exp\!\left(\frac{r(x, y)}{\beta}\right)}$$

with

$$Z(x) = \sum_y \pi_{\text{ref}}(y \mid x) \exp\!\left(\frac{r(x, y)}{\beta}\right).$$

This is the **e-projection identity**: the closed form for the optimal RLHF policy. It says the trained policy is the reference policy *exponentially tilted* by the reward, then renormalized.

### 3.6 Connecting to physics, statistics, and information theory

The structure is familiar from several fields:

**Statistical mechanics.** With $\pi_{\text{ref}}$ uniform and energy $E(y) = -r(y)$, this is the Boltzmann distribution at inverse temperature $\beta_{\text{phys}} = 1/\beta$: $\pi^*(y) \propto \exp(-E(y)/\beta_{\text{phys}})$.

**Bayesian inference.** With $\pi_{\text{ref}}$ a prior and $\exp(r/\beta)$ a likelihood, this is the posterior $\propto$ prior $\times$ likelihood.

**Maximum entropy.** Maximizing entropy of $\pi$ subject to $\mathbb{E}_\pi[r] = c$ gives $\pi \propto e^{\lambda r}$ for some $\lambda$ chosen to satisfy the constraint.

These are not analogies. The mathematical structure is genuinely the same. The $\beta$ in our problem plays the role of temperature, $r(y)$ plays the role of negative energy, and $\log Z$ plays the role of the free energy.

### 3.7 The connection to e-projection on the manifold

Geometrically, the closed-form $\pi^*$ is the **e-projection** of $\pi_{\text{ref}}$ onto the constraint manifold $\{\pi : \mathbb{E}_\pi[r] \geq r_{\max} - \epsilon\}$ — the closest point under KL divergence. Information geometry calls this the e-projection (exponential projection) because the family $\{\pi_\lambda \propto \pi_{\text{ref}} e^{\lambda r}\}$ as $\lambda$ varies is an *exponential family* through $\pi_{\text{ref}}$, and the e-projection lies on this family.

The Lagrange multiplier $\lambda$ in §3.5 is what `info_geometric_reformulation.md` calls the **constraint severity**. Larger $\lambda$ means stronger pull toward the constraint, equivalently smaller $\beta$. We will use the symbol $\mu$ for this Lagrange multiplier in the Bridge B context (matching the framework's notation) and reserve $\beta$ for the KL penalty's reciprocal-temperature interpretation. The relation: $\mu = 1/\beta$ at the optimum (the Lagrange multiplier saturates the constraint).

### 3.8 Multi-stage training

In production alignment pipelines, training is multi-stage:

1. **Pretraining** gives $\pi_0 = P_{\text{base}}$.
2. **Supervised fine-tuning (SFT)** takes $\pi_0$ as starting point and produces $\pi_{\text{SFT}}$.
3. **RLHF** uses $\pi_{\text{SFT}}$ as the reference policy $\pi_{\text{ref}}$ in the e-projection identity.

So $\pi_{\text{ref}}$ is the post-SFT model, not the post-pretraining base. The e-projection identity gives the distortion *from $\pi_{\text{ref}}$ to $\pi^*$*, which is the RLHF stage's contribution.

For total distortion from base to fully-trained:

$$\rho_{\text{total}}(x, y) = \log \pi_{\text{RLHF}}(y \mid x) - \log \pi_0(y \mid x) = \rho_{\text{SFT}}(x, y) + \rho_{\text{RLHF}}(x, y).$$

**Total distortion is additive across stages in the log domain.** When intermediate checkpoints are available, this lets us decompose the contribution of each stage. When they are not (most production institutions), we measure only $\rho_{\text{total}}$.

For the rest of this document, $P_{\text{base}}$ means "the model before whatever Stage 2 training we're analyzing" and $P_{\text{inst}}$ means "the model after." Context determines which.

---

## Part 4: $\rho$ as the Leakage Measurement

Now we tie the e-projection identity back to the four-object decomposition and identify $\rho$ as the operational measurement of the leakage component.

### 4.1 Reading $\rho$ off the e-projection identity

Take logs of the e-projection identity:

$$\log \pi^*(y \mid x) = \log \pi_{\text{ref}}(y \mid x) + \frac{r(x, y)}{\beta} - \log Z(x).$$

Identifying $P_{\text{inst}} = \pi^*$ and $P_{\text{base}} = \pi_{\text{ref}}$, the *probability distortion field* is

$$\boxed{\rho(x, y) = \log P_{\text{inst}}(y \mid x) - \log P_{\text{base}}(y \mid x) = \frac{r(x, y)}{\beta} - \log Z(x)}$$

The probability distortion is the (rescaled) reward minus a per-prompt normalization.

### 4.2 Relative distortion within a prompt

The normalization $\log Z(x)$ does not depend on the completion $y$. So for two completions $y_1, y_2$ of the same prompt:

$$\rho(x, y_1) - \rho(x, y_2) = \frac{r(x, y_1) - r(x, y_2)}{\beta}.$$

This is exact. The relative distortion between two completions of the same prompt directly reveals the relative reward, scaled by $1/\beta$. The normalization cancels.

This is the methodological foundation of relative-distortion measurement: **even without computing $Z(x)$, we can measure relative distortion by comparing two completions on the same prompt, and the relative distortion recovers the relative reward up to the scaling factor $\beta$.**

### 4.3 $\rho$ in the tangent space

In the Fisher-tangent linearization at $\pi_0 = \pi_{\text{base}}$, $\log \pi_{\text{inst}}(y \mid x) - \log \pi_{\text{base}}(y \mid x)$ is the **score representation** of $\pi_{\text{inst}}$ in the tangent space at $\pi_{\text{base}}$. That is, $\rho$, viewed as a function on $(x, y)$, is exactly the tangent-space displacement vector of $\pi_{\text{inst}}$ from $\pi_{\text{base}}$:

$$u_{\text{inst}}(x, y) = \log \pi_{\text{inst}}(y \mid x) - \log \pi_{\text{base}}(y \mid x) = \rho(x, y).$$

This identification is the crucial step. **$\rho$ is the displacement vector in the Fisher tangent at the base policy.** It lives in the same Hilbert space the four-object decomposition operates on. The four-object decomposition therefore predicts the structure of $\rho$ as a function of which directions in the Hilbert space we read.

### 4.4 The four objects, in $\rho$ terms

Apply the four-object decomposition with $P_1 = P_Q$ (query projection — the (prompt, completion) directions we evaluate $\rho$ at) and $P_2 = P_C$ (constraint projection — the subspace training has projected onto).

Decompose the displacement vector $\rho \in T_{\pi_{\text{base}}} \mathcal{P}$:

- The component of $\rho$ in the $P_Q P_C$ direction is **retention**: what passes through both projections, what the query reads of what the constraint allowed.
- The component in the $P_Q (I - P_C P_Q)$ direction is **suppression**: what the query would have read of $f_{\text{true}}$ that the constraint removed.
- The component in the $(I - P_Q) P_C$ direction is **leakage**: content that escapes the query subspace because the constraint projected it sideways.
- The total $\rho$, considered as the displacement of $\pi_{\text{inst}}$ from $\pi_{\text{base}}$, has norm-squared $\sum_j |a_j|^2 (1 - \beta_j)$ which is the total error.

### 4.5 What we measure when we evaluate $\rho^*$ at a probe point

When we measure $\rho^*$ at a specific (prompt, completion) pair $(x_0, y_0)$, what we are reading is the projection of the post-training tangent-space displacement onto a specific direction in $T_{\pi_{\text{base}}} \mathcal{P}$ — namely the evaluation-at-$(x_0, y_0)$ direction.

Which of the four objects we are reading depends on which (prompt, completion) pair we choose:

- **Completions in the trained-model's modal output direction.** These are completions where the trained policy has placed substantial probability mass, and these are typically the directions where retention is largest. Measuring $\rho^*$ at such completions reads retention.

- **Completions in the base-model's modal output direction that the trained model has moved away from.** These are completions $y$ where $\rho^*(x, y) < 0$ — base assigned higher probability than instruct. Measuring $\rho^*$ at such completions reads suppression.

- **Completions the trained model has amplified that base did not assign substantial probability.** These are completions $y$ where $\rho^*(x, y) > 0$ — instruct amplified above base. The empirical work (`Case Study - Induced-Hole Amplification.md`) measures these.

This is the precise connection. **$\rho$ measurement is reading the four-object decomposition, with which object getting read depending on which completion direction we ask about.** The structure of $\rho^*$ across many probe points reveals the principal-angle geometry of $(P_Q, P_C)$, by inverting the four-object decomposition.

### 4.6 Bridge B in $\rho$ terms

Bridge B's four laws (§2.5) translate directly into predictions for the structure of $\rho$ across probe directions. Decompose a probe direction $q$ into its component along the constraint direction $c$ (call it $s = \langle q, c \rangle$, the normalized alignment) and its perpendicular component:

- For probes with $s = 1$ (probe direction aligned with constraint): $\rho^*$ in this direction has magnitude $\propto \mu$ (constraint severity). Retention scales as $\mu^2$. Leakage is zero — there's nowhere sideways to leak.
- For probes with $s = 0$ (probe direction orthogonal to constraint): $\rho^*$ in this direction is dominated by leakage which scales as $\mu^2 \cdot 1 = \mu^2$. Retention is zero.
- For probes with $s = 1/\sqrt{2}$ (probe direction at $45°$ to constraint): leakage $\mu^2(1-s^2) = \mu^2/2$ peaks; retention $\mu^2 s^2 = \mu^2/2$ also nonzero; the two are equal.

The toy-level prediction: **the variance of $\rho^*$ across probe directions, plotted against $s$, traces out the Bridge B scalar laws**. Production-system tests of this prediction have unaddressed obstacles (real systems use learned reward models with many directions; KL coefficient ≠ severity at the optimum; "constraint direction" lacks operational definition for an LLM; $\mu$ is not directly observable). The shape match $r \approx 0.98$ holds in the toy; the production-system test is open.

### 4.7 What relative measurements give us

**Fact:** Measuring $\rho^*$ on a specific probe pair $(x_0, y_0)$ recovers the value of the displacement vector at that point — which, modulo the per-prompt normalization $\log Z(x_0)$, is the value of the reward function at that point divided by $\beta$.

**Fact:** Measuring $\rho^*$ on two probe pairs $(x_0, y_1)$ and $(x_0, y_2)$ on the same prompt recovers the *difference* in reward between the two completions, exactly, with no normalization ambiguity. The difference is $\beta \cdot [\rho^*(x_0, y_1) - \rho^*(x_0, y_2)]$.

**Fact:** Measuring $\rho^*$ across many probe pairs on a single prompt and computing PCA of the resulting structure recovers the principal-angle eigenstructure of $(P_Q, P_C)$ on that prompt's effective subspace.

**Hypothesis:** Measuring $\rho^*$ across many prompts in the same topic category, and fitting Bridge B's $\mu^2 s^2$ retention plus $\mu^2 (1-s^2)$ leakage law to the measurements, recovers the constraint severity $\mu$ and the alignment $s$ for that topic. (Open: this requires an operational definition of $s$ in the production-system setting, which does not currently exist.)

### 4.8 What we can't get from $\rho^*$ alone

**Cannot recover:** The reward function $r(x, y)$ itself, only $r(x, y)/\beta - \log Z(x)$. To get $r$ alone we would need to know $\beta$ and $Z(x)$.

**Cannot recover:** The training trajectory — $\rho^*$ measures only endpoints. Path-integral analysis (§7.4) handles trajectory questions, but not from $\rho^*$ measurements alone.

**Cannot recover:** Per-token attribution within a generation. $\rho^*$ as defined here is a per-(prompt, completion-sequence) quantity. Token-level decomposition requires the chain rule on log-probabilities and finer-grained probing.

**Can recover (structural):** The principal-angle geometry of the audit-constraint pair via PCA of $\rho^*$ across many probes. This is the mechanism the framework's measurement program operates on.

---

## Part 5: Training Dynamics — How the Distortion Accumulates

The closed-form e-projection identity tells us what $\rho$ is at the training optimum. It does not tell us *how* training gets there or what happens along the way. Real training is iterative, may not converge, and produces specific trajectories that depend on the training procedure.

### 5.1 Gradient flow as the simplest dynamics model

The simplest model of training is *gradient flow*: parameters $\theta_t$ evolve according to

$$\frac{d\theta_t}{dt} = \nabla_\theta \mathcal{R}(\theta_t)$$

where $\mathcal{R}(\theta)$ is the training objective and $t$ is "training time" (a continuous version of "training step number"). At each instant, parameters move in the direction that most rapidly increases the objective. The trajectory traces a path through parameter space starting from $\theta_0$.

For the RLHF case from Part 3:

$$\mathcal{R}(\theta) = \mathbb{E}_{x, y \sim \pi_\theta}[r(x, y)] - \beta \mathbb{E}_x[D_{\text{KL}}(\pi_\theta \,\|\, \pi_{\text{ref}})].$$

We need its gradient.

### 5.2 The policy gradient theorem

Computing $\nabla_\theta \mathcal{R}(\theta)$ requires care because $\theta$ appears both inside the expectation (in $\pi_\theta$) and in the function being averaged. The standard trick — the *log-derivative trick* or *score function method* — handles this.

Consider just the reward term, $\mathbb{E}_{y \sim \pi_\theta}[r(x, y)]$:

$$\mathbb{E}_{y \sim \pi_\theta}[r(x, y)] = \sum_y \pi_\theta(y \mid x) r(x, y).$$

Take the gradient ($r$ does not depend on $\theta$):

$$\nabla_\theta \mathbb{E}_{y \sim \pi_\theta}[r(x, y)] = \sum_y r(x, y) \nabla_\theta \pi_\theta(y \mid x).$$

Now apply the identity $\nabla_\theta \pi_\theta = \pi_\theta \nabla_\theta \log \pi_\theta$ (verify: $\nabla_\theta \log \pi_\theta = (1/\pi_\theta) \nabla_\theta \pi_\theta$ by the chain rule, so multiplying through gives $\pi_\theta \nabla_\theta \log \pi_\theta = \nabla_\theta \pi_\theta$). Substituting:

$$\nabla_\theta \mathbb{E}_{y \sim \pi_\theta}[r(x, y)] = \sum_y r(x, y) \pi_\theta(y \mid x) \nabla_\theta \log \pi_\theta(y \mid x) = \mathbb{E}_{y \sim \pi_\theta}[r(x, y) \nabla_\theta \log \pi_\theta(y \mid x)].$$

The function $\nabla_\theta \log \pi_\theta(y \mid x)$ is the **score function**. It points in the direction in parameter space that most rapidly increases the probability of generating $y$ given $x$. The policy gradient says: to increase expected reward, move in the score-function direction, weighted by reward.

### 5.3 Gradient of the KL term

For the KL penalty, similar manipulation. Start with

$$D_{\text{KL}}(\pi_\theta \,\|\, \pi_{\text{ref}}) = \sum_y \pi_\theta(y) [\log \pi_\theta(y) - \log \pi_{\text{ref}}(y)].$$

Take the gradient via the product rule:

$$\nabla_\theta D_{\text{KL}} = \sum_y [\nabla_\theta \pi_\theta(y) \cdot (\log \pi_\theta - \log \pi_{\text{ref}}) + \pi_\theta(y) \nabla_\theta \log \pi_\theta(y)].$$

The first term, by the log-derivative trick, becomes $\mathbb{E}_{y \sim \pi_\theta}[(\log \pi_\theta - \log \pi_{\text{ref}}) \nabla_\theta \log \pi_\theta]$.

The second term: $\sum_y \pi_\theta(y) \nabla_\theta \log \pi_\theta(y) = \nabla_\theta \sum_y \pi_\theta(y) = \nabla_\theta 1 = 0$. (The score function has mean zero under its own distribution — a general property of probability distributions.)

So

$$\nabla_\theta D_{\text{KL}}(\pi_\theta \,\|\, \pi_{\text{ref}}) = \mathbb{E}_{y \sim \pi_\theta}\big[(\log \pi_\theta(y) - \log \pi_{\text{ref}}(y)) \nabla_\theta \log \pi_\theta(y)\big].$$

### 5.4 The full objective gradient

Combining:

$$\nabla_\theta \mathcal{R}(\theta) = \mathbb{E}_{x \sim \mathcal{D}, \, y \sim \pi_\theta(\cdot \mid x)}\Big[\big(r(x, y) - \beta \log\tfrac{\pi_\theta(y \mid x)}{\pi_{\text{ref}}(y \mid x)}\big) \nabla_\theta \log \pi_\theta(y \mid x)\Big].$$

The thing in parentheses is the *advantage* — how much better than reference this completion is, accounting for both reward and how far from reference the policy has drifted. Multiplying by the score function and averaging gives the policy-improvement direction.

### 5.5 The trajectory of $\rho_t$

Along the gradient-flow trajectory, we have a one-parameter family of policies $\pi_t = \pi_{\theta_t}$. Define the time-resolved distortion:

$$\rho_t(x, y) = \log \pi_t(y \mid x) - \log \pi_0(y \mid x).$$

At $t = 0$, $\rho_0 = 0$ identically. As training proceeds, $\rho_t$ develops structure. The final $\rho$ is $\rho_T$.

How does $\rho_t$ evolve? Since $\pi_t = \pi_{\theta_t}$ depends on $t$ through $\theta_t$, by the chain rule:

$$\frac{d\rho_t(x, y)}{dt} = \nabla_\theta \log \pi_\theta(y \mid x)\big|_{\theta_t} \cdot \frac{d\theta_t}{dt}.$$

Substituting $d\theta_t/dt = \nabla_\theta \mathcal{R}(\theta_t)$:

$$\frac{d\rho_t(x, y)}{dt} = \nabla_\theta \log \pi_t(y \mid x) \cdot \nabla_\theta \mathcal{R}(\theta_t).$$

This is the central formula of training dynamics. **The rate of distortion change at $(x, y)$ is the inner product, in parameter space, between the score function for $(x, y)$ and the training direction.**

When these vectors are aligned (large positive inner product), $\rho$ at $(x, y)$ grows quickly. When orthogonal, $\rho$ does not change. When anti-aligned, $\rho$ decreases.

### 5.6 The cumulative path integral

Integrating the rate equation from $0$ to $T$:

$$\rho(x, y) = \int_0^T \nabla_\theta \log \pi_t(y \mid x) \cdot \nabla_\theta \mathcal{R}(\theta_t) \, dt.$$

This is exact along any specific trajectory. It is a **path integral along the training trajectory**.

The expression has two pieces: the score function for $(x, y)$ at time $t$, and the training direction at time $t$. Both depend on the trajectory through $\theta_t$. Different starting points or different objective functions give different trajectories.

For the framework, this exact expression is the foundation. Approximations to it give us the various theoretical tools developed in Parts 6-8. The full expression is intractable to compute directly for high-dimensional $\theta$, but it tells us what the distortion fundamentally **is**: the line integral of (score function) · (training direction) along the trajectory.

---

## Part 6: First-Order Theory — The Neural Tangent Kernel as Kernel Propagation

The path-integral expression for $\rho$ is exact but hard to work with. We need approximations to extract predictions. The simplest is to *linearize* around the starting point.

This gives us our first quantitative tool for predicting how distortion spreads from training data to test points. It also connects to the Phantom framework's prediction (`audit_blind_subspace.md` §1.4) that for wide networks trained by gradient flow on quadratic loss, the distortion-to-function map has explicit kernel form via the Neural Tangent Kernel, making the audit-blindness theorems exact in the NTK limit.

### 6.1 Taylor expansion at $\theta_0$

Define $f(\theta) = \log \pi_\theta(y \mid x)$ for fixed $(x, y)$. The distortion is $\rho(x, y) = f(\theta_T) - f(\theta_0)$.

Taylor expand $f$ around $\theta_0$:

$$f(\theta_T) = f(\theta_0) + \nabla_\theta f(\theta_0) \cdot \Delta\theta + \tfrac{1}{2} \Delta\theta^\top \nabla^2_\theta f(\theta_0) \Delta\theta + \cdots$$

where $\Delta\theta = \theta_T - \theta_0$.

Subtracting $f(\theta_0)$:

$$\rho(x, y) = g(x, y) \cdot \Delta\theta + \tfrac{1}{2} \Delta\theta^\top H(x, y) \Delta\theta + \cdots$$

where $g(x, y) = \nabla_\theta \log \pi_\theta(y \mid x)|_{\theta_0}$ is the score function at base, and $H(x, y)$ is the Hessian of $\log \pi_\theta(y \mid x)$ at $\theta_0$.

Truncating at first order:

$$\rho(x, y) \approx g(x, y) \cdot \Delta\theta.$$

This is the **linear approximation** or **lazy approximation**.

### 6.2 What is $\Delta\theta$?

$\Delta\theta$ is the cumulative parameter update from training. In gradient flow, $\Delta\theta = \int_0^T \nabla_\theta \mathcal{R}(\theta_t) \, dt$.

For stochastic training where examples are sampled and updates applied per-example, write the cumulative update as a sum over training events. Each example $(x_i, y_i)$ contributes a gradient at $\theta_t$ when the example is processed. Approximating these gradients as evaluated at $\theta_0$ throughout (the lazy approximation):

$$\Delta\theta \approx \sum_i \eta_i a_i g(x_i, y_i)$$

where $\eta_i$ is the effective learning rate, $a_i$ is the advantage signal (positive on completions to encourage, negative on completions to discourage), and $g(x_i, y_i)$ is the score function at base for the training example.

### 6.3 The kernel emerges

Substitute into the linear approximation:

$$\rho(x, y) \approx g(x, y) \cdot \sum_i \eta_i a_i g(x_i, y_i) = \sum_i \eta_i a_i [g(x, y) \cdot g(x_i, y_i)].$$

Define the **neural tangent kernel**:

$$\boxed{K\big((x, y), (x', y')\big) = g(x, y) \cdot g(x', y') = \nabla_\theta \log \pi_{\theta_0}(y \mid x) \cdot \nabla_\theta \log \pi_{\theta_0}(y' \mid x').}$$

This is the inner product of score functions in parameter space. In terms of the kernel:

$$\rho(x, y) \approx \sum_i \eta_i a_i K((x, y), (x_i, y_i)).$$

**The distortion at any test point is a weighted sum of kernel values to the training points, with weights given by training advantages.**

### 6.4 Properties of the kernel

The NTK has several important properties (Jacot, Gabriel, Hongler 2018):

**Symmetric:** $K((x,y), (x',y')) = K((x',y'), (x,y))$ — dot products are symmetric.

**Positive semi-definite:** For any function $\alpha$ and any set of points,

$$\sum_{i,j} \alpha_i \alpha_j K((x_i, y_i), (x_j, y_j)) = \Big\|\sum_i \alpha_i g(x_i, y_i)\Big\|^2 \geq 0.$$

This makes $K$ a valid kernel — it defines an inner product in some feature space.

**Has eigendecomposition.** Like any positive semi-definite kernel,

$$K((x,y), (x',y')) = \sum_k \lambda_k \phi_k(x, y) \phi_k(x', y')$$

with $\lambda_k \geq 0$ and $\phi_k$ forming a complete orthonormal basis on the space of functions over (prompt, completion) pairs.

### 6.5 The eigenmode picture and connection to the framework

The eigenfunctions $\phi_k$ are the natural "modes" of the model's representation. They are the directions in function-space that the model's gradient geometry treats as fundamental. Each mode evolves independently under gradient flow (in the NTK regime) with rate governed by its eigenvalue $\lambda_k$.

This connects directly to the Phantom framework: **the NTK eigenmodes $\phi_k$ are the operational realization of the canonical basis $\{u_j\}$ of $T_{P_1}(P_2)$ in the Halmos two-projection apparatus.** The eigenvalues $\lambda_k$ play the role of the principal-angle parameters. The kernel propagation formula is the operational mechanism by which the constraint subspace's geometric structure becomes the trained policy's $\rho$ structure.

When training is concentrated on a small set of (prompt, completion) pairs, the resulting distortion at any other point is determined by the kernel between that point and the training set. **Distortion spreads through the kernel.** Topics with semantic and structural similarity to the training points have large kernel value and inherit the shaping; topics far from the training set have small kernel value and remain undistorted.

This is the mathematical basis for why institutional shaping spreads coherently. Institutions explicitly train on a manageable number of examples; the kernel takes care of generalizing the shaping.

### 6.6 The audit-blind connection

`audit_blind_subspace.md` §1.4 makes this explicit: in the NTK regime for wide networks, the distortion-to-function map $L = dF|_0$ has explicit form

$$L(\xi) = \int K(\cdot, x') \xi(x') \, d\nu(x')$$

where $\xi$ is a training-data perturbation in the distortion space $\Xi$ and $L(\xi)$ is the resulting change in trained-network output. **In the NTK limit, the audit-blindness theorems become exact** (no linearization error), with the kernel determining which distortion directions are audit-detectable and which are not.

This makes the empirical NTK numerical companion called for in `ml_path_forward.md` §1.2 Gap 1 a particularly clean target. Trained, wide networks under explicit distortion should have $\rho$ structure exactly predictable from the NTK; the framework's predictions become falsifiable to floating-point precision rather than to a 15–25% error envelope.

### 6.7 When NTK is good and when it is not

The NTK approximation requires:

- $\Delta\theta$ small enough that score functions at $\theta_0$ are good approximations along the trajectory.
- The model is in the "lazy" regime where features (internal representations) do not change much during training.
- Training does not push parameters into regions of high curvature.

For overparameterized wide networks at initialization, all three hold. For modern alignment training on production language models, none of them holds in general. Real alignment training is closer to the **feature-learning** regime where features evolve substantially, which Part 7 addresses.

**Fact:** NTK gives qualitative predictions about how distortion spreads (the kernel-propagation picture) that hold in broad form across regimes. **Hypothesis:** NTK gives quantitative magnitudes accurate to within the linearization error envelope (15-25% in moderate regimes, larger in heavy-alignment regimes). The hypothesis is open: production-system tests of the NTK kernel form's quantitative accuracy have not been done.


---

## Part 7: Beyond First Order — Feature Learning and Path Integrals

The NTK approximation freezes the kernel at its initialization value. Real training, especially heavy alignment training, allows the kernel to evolve. The internal representations of the model — its features — change. We need a formalism that captures this. The path-integral formulation is the most general; intermediate levels of approximation give us mean-field theory, dynamical mean field theory, and effective field theory on the shaping subspace.

### 7.1 Why the kernel moves

The kernel $K((x, y), (x', y')) = g(x, y) \cdot g(x', y')$ is built from score functions at $\theta_0$. As parameters change during training, score functions change too:

$$\nabla_\theta \log \pi_{\theta_t}(y \mid x) \approx g(x, y) + H(x, y) \cdot (\theta_t - \theta_0) + \cdots$$

The score function at time $t$ is approximately the original score function plus a Hessian-weighted correction. So the kernel at time $t$:

$$K_t((x, y), (x', y')) = \nabla_\theta \log \pi_{\theta_t}(y \mid x) \cdot \nabla_\theta \log \pi_{\theta_t}(y' \mid x')$$

is generally different from $K_0$. The propagation structure of distortion at later times is governed by $K_t$, not $K_0$.

### 7.2 The mean-field parameterization

There are different ways to set up the limit of infinite-width networks, and they give different behaviors.

**Standard parameterization.** The default scaling, where weights and gradients have a specific relationship to width $N$. In the infinite-width limit, the kernel is fixed at its initialization value (the original NTK regime). Features do not learn; only the output layer effectively trains.

**Mean-field parameterization** ($\mu$P, Yang and Hu 2021). A different scaling where individual neurons matter even at infinite width. All layers continue to learn features during training, even in the infinite-width limit.

The technical statement: for a two-layer network $f(x; \theta) = \frac{1}{N} \sum_{j=1}^N a_j \sigma(w_j \cdot x)$, under standard parameterization the per-neuron contribution scales as $O(1/\sqrt{N})$. Under mean-field parameterization it scales as $O(1/N)$. This changes whether individual neurons matter at large $N$.

Real alignment training is somewhere between standard NTK and full mean-field, often closer to feature learning — the model's representations measurably change, new features emerge, existing features get reorganized.

### 7.3 Implications for $\rho$

In the feature-learning regime, the kernel evolves, so the propagation of distortion is governed by the time-evolved kernel. The first-order NTK formula

$$\rho(x, y) \approx \sum_i \eta_i a_i K_0((x, y), (x_i, y_i))$$

is replaced by something like

$$\rho(x, y) \approx \int_0^T dt \, \mathbb{E}_i[\eta_i a_i^{(t)} K_t((x, y), (x_i, y_i))]$$

where $K_t$ is the kernel at training time $t$ and $a_i^{(t)}$ is the advantage at time $t$. Both kernel and advantages evolve.

This is harder mathematically but addresses a real phenomenon. **Practical consequence for measurement:** the trajectory-averaged kernel is itself measurable from differential probes. If $\rho^*(x, y)$ and $\rho^*(x', y')$ are highly correlated across many training conditions, that is evidence the effective kernel has large value between those points. The framework's measurement methodology can use $\rho^*$ correlations across probes to estimate the effective propagation kernel without needing access to the actual training trajectory.

### 7.4 The path integral formulation

The most general formulation is the path integral. Real training is not deterministic gradient flow — it has noise from minibatch SGD, learning-rate schedules, optimizer momentum. Model this with a stochastic differential equation:

$$\frac{d\theta_t}{dt} = \nabla_\theta \mathcal{R}(\theta_t) + \xi_t$$

where $\xi_t$ is a Gaussian noise process. The solution is no longer a single trajectory but a probability distribution over trajectories.

For an SDE $d\theta_t = b(\theta_t) dt + \sigma \, dW_t$, the probability density of a specific trajectory $\theta(\cdot)$ is the **Onsager-Machlup density**:

$$P[\theta(\cdot)] \propto \exp\!\left(-\frac{1}{2} \int_0^T \|\sigma^{-1}(\dot{\theta}_t - b(\theta_t))\|^2 \, dt\right).$$

For our case with $b(\theta) = \nabla_\theta \mathcal{R}$ and isotropic noise:

$$P[\theta(\cdot)] \propto \exp\!\left(-\frac{1}{2\sigma_{\text{noise}}^2} \int_0^T \|\dot{\theta}_t - \nabla_\theta \mathcal{R}(\theta_t)\|^2 \, dt\right).$$

The exponent is the **action functional** for trajectories. Trajectories that exactly follow gradient flow have zero action and are most likely. Trajectories that stray accumulate action proportional to squared deviation.

### 7.5 The connection to physics

The path integral structure is the same as in physics:

In quantum mechanics, the propagator $\langle x_T \mid x_0 \rangle$ is a path integral over paths weighted by $e^{iS/\hbar}$.

In statistical mechanics (after Wick rotation), the partition function is a path integral over configurations weighted by $e^{-S/k_B T}$.

In neural network training (our case), the expected observable is a path integral over training trajectories weighted by $e^{-\text{Onsager-Machlup}}$.

The same techniques apply: saddle-point expansions, instanton analysis, perturbation theory around classical solutions, renormalization-group flow.

### 7.6 Mode collapse as instantons

A specific phenomenon worth describing in path-integral language: **mode collapse**. This is when training drives a specific completion to be near-deterministic — $P_{\text{inst}}(y_0 \mid x) \approx 1$ for some specific $y_0$ given certain prompts $x$.

Mode collapse often appears as a sharp transition during training. Below some training threshold, the distribution is broad. Above the threshold, mass concentrates on a specific completion. The transition can happen quickly relative to the overall training timescale.

Mathematically, this looks like the trajectory crossing a barrier between two basins of attraction. Below threshold, the trajectory is in the basin around $\theta_0$; above, it is in a different basin where $\pi(y_0 \mid x)$ is much larger.

Crossing such barriers is an **instanton phenomenon** — a specific type of trajectory that the path-integral analysis handles. The "action" of the instanton (the value of the Onsager-Machlup functional along the barrier-crossing path) determines the rate of transition.

In the framework's terms, mode collapse explains why some falsification targets show 0% to 80%+ amplification (e.g., the founding-fathers exceptions framing in `Case Study - Induced-Hole Amplification.md`) rather than gradual increases. The transition is non-perturbative — Taylor expansion at $\theta_0$ does not capture it. Path-integral / instanton analysis does.

---

## Part 8: Asymptotic Series and the Mode-Collapse Regime

Taylor expansion of $\rho$ at $\theta_0$ may not converge in the strong-shaping regime. This is not a failure of the framework — divergent series are well-studied in physics with developed mathematical apparatus.

### 8.1 Convergent vs asymptotic series

A power series $\sum_k a_k z^k$ is **convergent** at $z$ if partial sums $\sum_{k=0}^N a_k z^k$ approach a limit as $N \to \infty$.

A power series is **asymptotic** to a function $f$ at $z = 0$ if for each fixed $N$:

$$\Big|f(z) - \sum_{k=0}^N a_k z^k\Big| \leq C_N |z|^{N+1} \quad \text{as } z \to 0.$$

The $C_N$ can grow with $N$. The series might not converge for any fixed $z$, but for small enough $z$ partial sums are close to $f(z)$.

For convergent series, more terms is always better. For asymptotic-but-divergent series, more terms is better up to some optimal point and worse beyond.

### 8.2 A canonical example

Consider

$$f(z) = \int_0^\infty \frac{e^{-t}}{1 + zt} \, dt.$$

Expanding $1/(1+zt) = \sum_k (-zt)^k$ and integrating term-by-term:

$$f(z) \stackrel{?}{=} \sum_k (-z)^k k! = \sum_k (-1)^k k! \, z^k.$$

The coefficients $(-1)^k k!$ grow as $k!$. The radius of convergence is zero — the series does not converge for any nonzero $z$. But it is asymptotic. For small $z > 0$, partial sums approach $f(z)$ to within an error that decreases for a while, then starts increasing.

### 8.3 Optimal truncation and Borel summation

For coefficients growing like $k!/A^k$, the partial sum closest to the true value is at $N \approx A/|z|$. The error at optimal truncation is approximately $e^{-A/|z|}$ — exponentially small in $1/|z|$. This is why asymptotic series are useful: optimal truncation gives exponentially good approximations even when the series diverges. (This is the situation for QED in physics: perturbative expansion in fine-structure constant $\alpha \approx 1/137$ has factorially-growing coefficients, but optimal truncation gives errors $\sim e^{-137}$, which is unmeasurably small.)

Borel summation can sometimes recover the underlying function from a divergent series. Given $\sum_k a_k z^k$ with $a_k \sim k!/A^k$, define the Borel transform $B(t) = \sum_k (a_k/k!) t^k$. The factorial growth is canceled and $B(t)$ has nonzero radius of convergence. If $B(t)$ can be analytically continued to the positive real axis, the Borel sum is

$$f_{\text{Borel}}(z) = \int_0^\infty e^{-t} B(zt) \, dt.$$

This often recovers the true function exactly, even when the original series diverges.

### 8.4 Trans-series and resurgence

The modern view (Écalle and others, since the 1980s): the full answer often takes the form of a **trans-series**:

$$f(z) = \underbrace{\sum_k a_k z^k}_{\text{perturbative}} + \underbrace{e^{-A/z} \sum_k b_k z^k}_{\text{1-instanton}} + \underbrace{e^{-2A/z} \sum_k c_k z^k}_{\text{2-instanton}} + \cdots$$

The exponential factors $e^{-nA/z}$ represent contributions from $n$-instanton sectors — non-perturbative effects with action $nA$. Each sector has its own asymptotic series.

The remarkable fact: the coefficients $b_k, c_k, \ldots$ are **not** independent of $a_k$. They are determined by the large-order behavior of $a_k$ via *resurgence relations*. If $a_k \sim k!/A^k$ at large $k$, the leading instanton contribution has prefactor proportional to $e^{-A/z}$ — same $A$.

**The information about non-perturbative phenomena is encoded in the divergence pattern of the perturbative series.**

### 8.5 Application to $\rho$

For our problem: in the strong-shaping regime, the Taylor expansion of $\rho$ at $\theta_0$ is asymptotic but divergent. The mathematical apparatus tells us:

**Fact:** Optimal truncation gives errors that are exponentially small. Finite-order with appropriate truncation works.

**Hypothesis:** Borel summation may recover the exact $\rho$ from the asymptotic expansion in some regimes. This would let us compute $\rho$ in the strong-shaping case from properties of the perturbative expansion alone.

**Hypothesis:** The trans-series structure means mode collapse can be predicted from the large-order behavior of the perturbative expansion. Factorial growth of Taylor coefficients of $\log \pi_\theta$ at $\theta_0$ predicts mode-collapse transitions with action $A$ given by the growth rate. This is concrete: by computing high-order Taylor coefficients numerically, we predict mode collapse without leaving the perturbative regime.

The hypotheses are open. The mathematical machinery is established (asymptotic series and resurgence have been used in physics for decades) but production-system applications have not been done.

### 8.6 What this means for the framework

The institutional defense to claims about $\rho$ in the strong-shaping regime might say: "perturbation theory does not predict mode collapse; you cannot infer training behavior from analytic methods; the actual training is too complicated to model."

The resurgence-based response: perturbation theory **does** predict mode collapse, through its large-order behavior. The framework can use this to make quantitative predictions about when and where mode collapse should occur, given properties of the loss landscape that are computable in principle. Mode collapse is not "beyond mathematical prediction" — it is the standard non-perturbative regime that has been studied for decades in physics, with developed tools that apply here.

---

## Part 9: The Audit-Blind Theorems and What Probing Cannot See

The framework's most operationally consequential result is the audit-blind subspace theorem (`audit_blind_subspace.md`). This bounds what any number of queries on the trained network can detect. We restate it and connect to $\rho$ measurement.

### 9.1 The setup

Let $F: \Xi \to H$ be the map taking a training-data or training-objective distortion $\xi$ to the resulting trained-network function $f_{\theta(\xi)}$ in a Hilbert function space $H$. Let $\mathcal{Q} = \{q_1, \ldots, q_N\}$ be a finite collection of continuous linear functionals on $H$ — an audit query suite.

The **audit-blind subspace** is

$$\mathcal{N}_{\text{audit}} := \ker(A_\mathcal{Q} \circ dF|_0) \subset \Xi$$

— the set of distortion directions to which the audit map $A_\mathcal{Q} = (q_i)_{i=1}^N$ is insensitive at first order. Distortions in $\mathcal{N}_{\text{audit}}$ produce trained networks indistinguishable from the base under the audit, regardless of how large the resulting effect on user-facing outputs becomes.

### 9.2 The four theorems

**Theorem A (dimension):** $\dim(\mathcal{N}_{\text{audit}}) = \dim(\Xi) - \dim(\text{Range}(A_\mathcal{Q} \circ dF|_0))$.

**Theorem B (lower bound):** For any audit suite of size $N$, $\dim(\mathcal{N}_{\text{audit}}) \geq \dim(\Xi) - N$.

**Theorem C (concerning-subspace coverage):** For any $\mathcal{C} \subset \Xi$, the audit-visible component of $\mathcal{C}$ is determined by the principal angles between $\mathcal{C}$ and $\mathcal{N}_{\text{audit}}^\perp$, with the four-object decomposition giving exact scalar identities.

**Theorem D (optimal audit construction):** Given a target concerning subspace $\mathcal{C}$ of dimension $k$, an audit suite of size $N \geq k$ suffices to make $\mathcal{N}_{\text{audit}} \cap \mathcal{C} = \{0\}$, with explicit construction via SVD of $L^*|_\mathcal{C}$ where $L = dF|_0$. With $N < k$, the audit-blind subspace contains $\mathcal{C}$'s bottom $(k - N)$ singular directions of $L|_\mathcal{C}$.

These are proved in the linearized regime (NTK / Fisher-tangent linearization). The structural lower-bound theorems (A, B, D) are robust under the linearization. The visibility-fraction theorem (C) depends on the four-object decomposition's exactness in the Hilbert setting.

### 9.3 Why this is the core operational result

**$\rho$ measurement is an audit.** Each (prompt, completion) pair we evaluate $\rho^*$ on is one query in the sense of $\mathcal{Q}$. The empirical Phase E probe set was approximately $N \sim 100$ such queries. A full structured Monte Carlo program scales to $N \sim 10^4 - 10^6$.

Theorem B says: at least $\dim(\Xi) - N$ dimensions of training distortion are invisible to such an audit. If $\dim(\Xi)$ is large (institutional shaping has many independent components), most distortion is undetected.

This is the **fundamental limit** on what $\rho$ measurement can reveal. It is not a defect of any specific methodology; it is a property of the audit-distortion geometry. Better methodology can saturate the bound (Theorem D), but cannot exceed it.

### 9.4 Theorem D and probe design

Theorem D is the operationally useful constructive theorem. For a target concerning subspace $\mathcal{C}$ of dimension $k$, the SVD of $L|_\mathcal{C}$ identifies $k$ probe directions that resolve $\mathcal{C}$.

For the framework's measurement program: if we are trying to detect distortion in a specific topic category (e.g., "racial demographic claims"), Theorem D gives the principled way to construct probes that are guaranteed to detect distortion in that category, by computing the SVD of the distortion-to-function map restricted to that subspace.

The Phase E probe set was constructed by intuition — paraphrases, format variants. Theorem D says we could do this principledly. **Hypothesis:** Constructing probes via Theorem D's SVD construction would substantially improve detection efficiency on production systems. This is open work.

### 9.5 The principal-angle structure of audit visibility

By Theorem C, the visibility of a concerning subspace $\mathcal{C}$ under an audit $\mathcal{Q}$ is determined by the principal angles between $\mathcal{C}$ and the audit-blind subspace's orthogonal complement. This is the four-object decomposition again, with $P_1 = $ projection onto $\mathcal{C}$ and $P_2 = $ projection onto $\mathcal{N}_{\text{audit}}^\perp$.

The "audit-visible fraction" of $\mathcal{C}$ is the retention component:

$$\text{visible fraction} = \sum_j \beta_j^2$$

where $\beta_j$ are squared cosines of the principal angles. Aligned ($\beta = 1$): full visibility. Orthogonal ($\beta = 0$): zero visibility — the concerning subspace lies entirely in the audit-blind subspace.

The "audit-leakage" — concerning content that bleeds into directions the audit does not directly measure — is the leakage component $\sum_j \beta_j(1 - \beta_j)$, peaking at intermediate alignment.

So the same four-object decomposition that governs $\rho$'s structure under training also governs **what fraction of distortion is detectable** under any audit. The two applications of the four-object machinery — to training itself, and to what audits can see — interlock. The framework treats them as the same geometric apparatus applied at two levels.

### 9.6 The induced-hole sharpening

`Phantom_ML_PathForward.docx` §3.2.3 makes the following sharper observation about Theorem B in the induced-hole case. The audit-blind theorem is a rate-of-detection statement: an $N$-query audit misses at least $\dim(\Xi) - N$ dimensions of distortion. In the natural-hole case, the missing dimensions are dimensions of constructed-content possibility — large, but the audit can probe along them.

In the induced-hole case (data was suppressed by training), some of the audit-blind dimensions correspond to **information that was deliberately removed from inference accessibility**. The training process selected those dimensions because audits at those probe directions do not reveal the suppression. An auditor probing along surface-accessible directions misses the suppressed structure entirely.

**Fact:** The audit-blind theorem applies to both natural and induced cases.

**Hypothesis:** The audit-blind theorem **understates** the difficulty for induced holes specifically, because the training process can be modeled as adversarially selecting the audit-blind dimensions. The exact form of this sharpening is open. The toy-level intuition: the institution can train to make the suppressed dimensions invisible to standard probes, in which case Theorem D's optimal construction at $N = k$ is necessary but may not be sufficient to detect the suppression with probes the institution did not anticipate the auditor using.


---

## Part 10: Natural Versus Induced Holes — The Memory of Suppressed Data

The single sharpest distinction the ML extension of the framework produces is between **natural** and **induced** holes (`Phantom_ML_PathForward.docx` §3.2). Both are realizations of distortion, but they have structurally different signatures and require different measurement strategies. This distinction has no analog in the spatial-gap case — a measurement gap is just a gap, there is no "the gap used to be filled and got erased." It is an ML-native concept.

### 10.1 The natural hole

A **natural hole** is a region $G \subset \mathcal{X}$ of input space the training process never received samples from. The training data simply does not contain examples in $G$. The model has nothing to override; whatever it produces in $G$ is the result of the architecture's inductive bias propagating boundary information from $\partial G$ via the interpolation operator $I_G$.

In `training_corpus_holes.md`'s formulation, the trained predictor in the linearized regime is

$$\hat f = M_G f_{\text{true}} + I_G(f_{\text{true}}|_{\partial G})$$

where $M_G = I - \chi_G$ is the input-space mask. The first term is the truth on the support of the filtered distribution. The second term is the architecture's interpolation into the hole, using only boundary information.

The natural hole has an honest signature. The model is **constructing**, not concealing. There is no internal representation of the truth being overridden because there is no internal representation of the truth — the parameters were never shaped by data in $G$. The phantom is the difference between $f_{\text{true}}|_G$ and $I_G(f_{\text{true}}|_{\partial G})$: how badly the architecture's interpolation approximates the missing content.

The four-object decomposition applies at the boundary. The locality structure (T6's tubular neighborhood, when it lifts) gives near-boundary predictions. Far from $\partial G$, the linearization assumption breaks down (the architecture's interpolation may not be well-approximated by its linear part deep inside $G$) and the framework's quantitative predictions degrade.

### 10.2 The induced hole

An **induced hole** is structurally different. The data was present in the training corpus. Examples in $G$ existed; gradient updates encountered them; parameters were modified by them; internal representations were shaped by them. **Then constraint training installed suppression**: a reward signal or KL-anchored constraint that drives the trained policy away from the truth in $G$, while the parameters retain memory of what was suppressed.

The induced hole has memory the natural hole does not. When data $f$ was in the training set before constraint, the model's parameters were shaped by $f$ before being shaped by suppression. Information about $f$ is encoded in the parameters in directions the standard query-time evaluations do not directly access.

Three structural consequences follow:

**Induced holes are harder to detect.** The obvious probe — querying at points in $G$ — sees the suppressed surface response and misses the propagated trace. The information about suppressed content lives in directions in parameter space that surface queries do not read. Probing in those directions requires either auxiliary information about the training procedure (white-box audit, see `audit_blind_subspace.md` §7.1) or probe directions selected with explicit knowledge of what was suppressed (which the auditor typically lacks).

**Induced holes have a paired structure in $\rho$.** Because the constraint is enforcing specific framings to be amplified (positive $\rho^*$ on those completions) and others to be suppressed (negative $\rho^*$ on the truthful completions), the empirical $\rho^*$ field on an induced-hole topic shows a paired positive-negative structure across completion directions. This is what `Case Study - Induced-Hole Amplification.md` documents on the founding-fathers and Wehrmacht topics.

**Induced holes survive paraphrase but not always format compression.** The constraint is policy-level (operating on the topic, not on phrasings), so paraphrasing the question does not unlock the suppressed content. Format compression sometimes does — if the constraint was learned conditional on specific format priors, breaking the format priors can lift the constraint. The empirical work shows this varies: some induced-hole topics survive format compression robustly (Wehrmacht), others partially break under it.

### 10.3 The mechanism distinction

`Phantom_ML_PathForward.docx` §3.3 raises a sharp testable question: **do different constraint mechanisms producing identical surface output produce identical models?**

Reward-based suppression updates parameters during training in ways that affect not just the suppressed content but every feature that participated in producing it.

KL-anchored suppression keeps parameters close to a reference policy in KL distance, which is a global Fisher-distance constraint and affects parameter directions selectively.

Adversarial training (training against an attack model) shapes parameters in a third distinct way.

These three mechanisms can be tuned to produce identical surface refusal behavior on a fixed content category. **Hypothesis:** The resulting models differ measurably in their internal structure — specifically, in the principal-angle geometry of their constraint subspace. Probing for adjacent content (related topics, related framings) would show different patterns under the three mechanisms because the kernel propagation from the constraint subspace to other directions would differ.

This is testable by training three otherwise-identical models to identical surface behavior on the same content via the three mechanisms and probing for adjacent-content distortion. It has not been done. It is one of the most valuable open experiments the framework points to.

### 10.4 Empirical operationalization of the distinction

Distinguishing natural from induced holes empirically requires either:

**Direct corpus access** — verify whether data on the topic was present in the training corpus before constraint. This is hard for production systems (Meta has not released the Llama-3.1 training corpus; Anthropic does not publish Claude's). For open-weight models with fully released training data, it is in principle possible.

**Internal-representation evidence** — find internal representations in the trained model of the suppressed truth, indicating that parameters carry memory of training data that the surface output now suppresses. This is mechanistic interpretability work (sparse autoencoder probes, activation patching, linear probing on hidden states). The framework predicts this should be findable for induced holes; it would be absent for natural holes.

**Indirect evidence from base distribution.** If the base model (pre-constraint, post-pretraining) shows the framework-relevant content at low but nonzero probability, this is evidence the data was in the training corpus and the constraint is induced (not natural). The empirical work in `Case Study - Induced-Hole Amplification.md` uses this indirect evidence: the Phase E base sampling shows the suppressed framings at base rates of 7-33%, which is evidence they are induced.

**Fact:** All Phase E target topics measured (founding fathers, Wehrmacht, crime demographics) show the relevant framings in base distribution at low but nonzero probability, consistent with induced-hole interpretation.

**Hypothesis:** Direct corpus or internal-representation verification would confirm the indirect base-distribution evidence. This is open.

### 10.5 The audit asymmetry between natural and induced

The audit-blind theorem applies to both cases. But the operational difficulty differs:

**Natural-hole audit.** $\dim(\Xi) - N$ dimensions are blind, but these correspond to constructed-content directions. Probing at random in $\Xi$ has a uniform chance of detecting distortion across the audit-blind subspace. Random probe directions saturate the lower bound.

**Induced-hole audit.** $\dim(\Xi) - N$ dimensions are blind, but these correspond to **deliberately-suppressed directions**. The training process can shape what the audit-blind subspace contains — it has incentives to make the suppressed content fall in directions the auditor does not check. Random probe directions do not saturate the lower bound effectively because the audit-blind subspace is adversarially structured.

This is the framework's sharpest claim about why induced-hole detection is harder than the audit-blind theorem alone says. It is **Hypothesis** rather than **Fact** because the formal proof of the adversarial sharpening is open work. The intuition is concrete: an institution that wants its shaping to be invisible can train to make it invisible, by selecting reward signals that move the shaping into the parameter directions surface probes do not access.

---

## Part 11: Phantom Theorem Status in the ML Setting

The original Phantom suite established theorems T1-T9 with status [E] established, [K] follows from known results, or [O] open. The ML setting inherits the operator-algebraic spine but specializes the function space, projections, and constraint geometry. This part records the status of each theorem in the ML setting.

### 11.1 T1 — Simple-spectrum energy identity [E]

Spatial-gap form: $\sum_{m \neq n} |\hat c_m|^2 = |c_n|^2 \cdot a_n(1 - a_n)$.

ML form: For a single eigenmode $u_j$ of $T_{P_Q}(P_C)$ with eigenvalue $\beta_j$, applied to a unit-norm tangent vector $f = c \cdot u_j$:

$$\|(I - P_Q) P_C f\|^2 = |c|^2 \cdot \beta_j (1 - \beta_j).$$

This is exact algebraic consequence of $P_Q^2 = P_Q$ and the canonical decomposition. Verified to $10^{-15}$ in `four_way_decomposition.py`.

### 11.2 T2 — Degenerate-spectrum energy identity [E]

Spatial-gap form: $\|(I - P_\lambda) M_G f\|^2 = \langle B_\lambda(I - B_\lambda) f, f \rangle = \sum_j |a_j|^2 \beta_j (1 - \beta_j)$ for $f \in E_\lambda$.

ML form: For a multi-dimensional canonical block of $T_{P_Q}(P_C)$ with eigenvalues $\{\beta_j\}$, applied to $f = \sum_j a_j u_j$:

$$\|(I - P_Q) P_C f\|^2 = \sum_j |a_j|^2 \beta_j (1 - \beta_j).$$

Exact in the Fisher tangent. Verified in `test_four_objects.py` and `test_four_objects_pure.py` to machine precision.

### 11.3 T3 — Decomposition theorem [E in spatial case, partial in ML case]

Spatial-gap form: $w_{G,N} = w_G + s_{G,N}$ — exact-outside-gap phantom plus finite-band commutator correction.

ML form: The corresponding split for the ML case would be the linearization-error decomposition:

$$\rho_{\text{full}} = \rho_{\text{linear}} + \rho_{\text{nonlinear}}$$

where $\rho_{\text{linear}}$ is the Bridge B first-order prediction and $\rho_{\text{nonlinear}}$ is the second-order curvature correction. The first-order term is computable from Bridge B; the second-order term from `test_second_order.py`'s $\frac{\lambda^2}{2} \pi_0(\tilde r^2 - \mathbb{E}_{\pi_0}[\tilde r^2])$. Status: each piece individually [E], but the full decomposition with explicit cross-terms beyond second order is [O].

### 11.4 T4 — Boundary Wronskian identity [E for elliptic case, no analog in ML case]

Spatial-gap form: $(\lambda_m - \lambda_n) K_{mn} = \int_{\partial G} [\bar\varphi_m \partial_\nu \varphi_n - \varphi_n \partial_\nu \bar\varphi_m] dS$ for $L = -\Delta$ and smooth $\partial G$.

ML form: There is no ML analog as stated. The Wronskian identity depends on the elliptic operator structure of $-\Delta$ which has no counterpart in trained neural networks. The corresponding ML statement, if it exists, would be a relation between coupling kernels and "boundary" structure in feature space — this is currently undefined.

Status: not applicable in the ML setting as currently formulated.

### 11.5 T5 — Masked dictionary Gram matrix [E in both cases]

Spatial-gap form: $\langle M_G \varphi_n, M_G \varphi_m \rangle = A_{mn}$ for hard mask.

ML form: $\langle P_C u_n, P_C u_m \rangle = \beta_n \delta_{nm}$ (in the canonical eigenbasis of $T_{P_Q}(P_C)$) — exact algebraic consequence of $P_C^2 = P_C$. The dictionary identity is the same algebraic structure with the projection playing the role of the multiplication mask.

### 11.6 T6 — Boundary-layer localization [O in both cases, more open in ML]

Spatial-gap form: For $f \in E_\lambda$, the commutator correction $s_{G,N}$ concentrates in a tubular neighborhood of $\partial G$ of width $O(\lambda_N^{-1/2})$. Open: explicit Hörmander-type bounds.

ML form: **Hypothesis** (`Phantom_ML_PathForward.docx` §3.1): phantom completions cluster near filter boundaries in representation space rather than uniformly within the filtered region. The "tube width" would be set by the architecture's effective receptive field in feature space. This is open both in formal proof and in empirical demonstration.

The empirical work has not directly tested this. **Hypothesis (ML-T6):** for an induced-hole topic, $\rho^*$ measured at probe pairs whose effective representation lies near the filter boundary should be larger than $\rho^*$ at probe pairs deep inside the filter region. Test: for a specific induced-hole topic, identify probe pairs at varying "feature-space distance" from the boundary and measure the falloff. Open.

### 11.7 T7 — Multipole expansion [K in spatial case, not directly applicable in ML]

Spatial-gap form: $K_{mn} = \sum_{|\alpha| \leq k} m_\alpha \partial^\alpha (\varphi_n \bar\varphi_m)(x_G) + O(|G| d_G^{k+1})$.

ML form: No direct analog — the multipole expansion is specifically for spatial gaps where Taylor expansion of eigenfunctions about the gap centroid makes sense. Feature-space "gaps" do not have a direct multipole structure.

### 11.8 T8 — Visibility-rank for degeneracies [K in spatial case, partial analog in ML]

Spatial-gap form: For $d$-dimensional $E_\lambda$ and small gaps, $B_\lambda$ has rank at most one at monopole order.

ML form: For a high-dimensional degenerate eigenspace of $T_{P_Q}(P_C)$ (multiple eigenvalues equal to a common $\beta$), the constraint subspace's principal-angle structure may have low rank when restricted to the eigenspace. Status: structural analog [K] in the linearized regime (follows from the abstract two-projection theory); explicit form for production architectures [O].

### 11.9 T9 — Multi-gap transversality bound [O in both cases]

Spatial-gap form: $\sigma_{\min}([A_1; \ldots; A_K])^2 \geq f(\theta_{\min})$ where $\theta_{\min}$ is the minimum principal angle between ambiguity bases.

ML form: For multi-constraint training (multiple constraints applied jointly, e.g., honesty + helpfulness + harmlessness in Anthropic's pipeline), the question is whether the joint constraint's principal-angle structure has guaranteed lower bounds on $\sigma_{\min}$ across the union. Open in both cases.

### 11.10 Summary

The framework's [E] established results — the algebraic core of the four-object decomposition and the mask/projection identities — lift directly to the ML setting with no degradation. The [K] follows-from-known-results theorems lift partially, with structural analogs holding under the ML linearization but specific forms requiring architecture-specific work. The [O] open theorems are open in both settings, with the ML versions sometimes harder (T6's tube width depends on architecture; T9's transversality lower bound is open in both).

The most pressing ML-specific open work is the empirical NTK numerical companion called for in `ml_path_forward.md` §1.2 Gap 1: a wide neural network trained under explicit distortion, with the framework's prediction of audit-blind behavior verified empirically on the network. The math is established; the regime is tractable in the NTK limit; the verification methodology mirrors the audit-blind ridge regression case directly. This has not been done.

---

## Glossary

**Audit-blind subspace ($\mathcal{N}_{\text{audit}}$).** The set of distortion directions to which a given audit query suite is insensitive at first order. By Theorem B, has dimension at least $\dim(\Xi) - N$ for $N$-query audits.

**Bridge B.** The Fisher-tangent reformulation of the four-object decomposition for the RLHF setup (`info_geometric_reformulation.md` Appendix B). Produces four scalar laws $\mu^2 s^2$, $(a - \mu s)^2$, $\mu^2(1 - s^2)$, $a^2 + \mu^2 - 2 a \mu s$ for retention, suppression, leakage, total. Verified at shape $r \approx 0.98$ on real e-projection.

**β (squared cosine of principal angle).** The eigenvalue of the compression operator $T_{P_1}(P_2)$ on its canonical basis. Equivalently, $\cos^2 \theta$ where $\theta$ is the principal angle between $\text{Range}(P_1)$ and $\text{Range}(P_2)$. Range $[0, 1]$ with 0 = orthogonal subspaces and 1 = coincident.

**β (KL regularization strength in RLHF).** The coefficient on the KL penalty in the RLHF objective. Larger $\beta$ means tighter regularization to the reference policy. Sometimes written as $1/\mu$ at the optimum.

**Constraint subspace ($C$).** The closed subspace of the Fisher tangent at $\pi_0$ consistent with the training constraint at first order. Linearization of the constraint manifold.

**e-projection.** The closest point under KL divergence in a constraint manifold to a given starting point. Has closed form on exponential families: $\pi^* \propto \pi_{\text{ref}} \exp(r/\beta)$.

**Fisher tangent space ($T_{\pi_0} \mathcal{P}$).** The tangent space at $\pi_0$ of the policy manifold, with score-function representation $u(x, y) = \log \pi(y \mid x) - \log \pi_0(y \mid x)$ and Fisher inner product $\langle u, v \rangle_F = \mathbb{E}_{x, y \sim \pi_0}[u v]$.

**Four-object decomposition.** The decomposition of two-projection geometry into retention $\beta^2$, suppression $(1-\beta)^2$, leakage $\beta(1-\beta)$, total error $1-\beta$. Each is a scalar invariant of the principal-angle eigenstructure with its own peak location in $\beta$.

**Halmos two-projection.** The canonical-form decomposition of two non-trivial orthogonal projections in a Hilbert space, due to Halmos 1969. Produces the five-block decomposition $H = H_{11} \oplus H_{10} \oplus H_{01} \oplus H_{00} \oplus H_{\text{gen}}$ with the CS canonical form on the generic block.

**Induced hole.** A region of input space where data was present in training but constraint training has installed suppression. Parameters carry memory of suppressed content. Distinct from natural hole.

**Leakage.** The component $(I - P_1) P_2 f$ — the part of $P_2 f$ that escapes the inference subspace $\text{Range}(P_1)$. Norm-squared $\sum_j |a_j|^2 \beta_j(1-\beta_j)$. Peaks at $\beta = 1/2$ (principal angle $\pi/4$). The framework's central object — $\rho$ measurement realizes leakage at chosen probe directions.

**Natural hole.** A region of input space where the training corpus contains no data. The model constructs in this region using the architecture's interpolation operator. Parameters do not carry memory of suppressed content. Distinct from induced hole.

**Neural tangent kernel (NTK).** The kernel $K((x,y), (x',y')) = g(x,y) \cdot g(x',y')$ — inner product of score functions in parameter space at $\theta_0$. Determines kernel propagation of distortion in the lazy training regime.

**Principal angles ($\theta_j$).** Angles between two subspaces of a Hilbert space, defined as $\arccos(\sigma_j)$ where $\sigma_j$ are singular values of $P_2|_{\text{Range}(P_1)}$. Range $[0, \pi/2]$.

**Probability distortion field ($\rho$).** $\rho(x, y) = \log P_{\text{inst}}(y \mid x) - \log P_{\text{base}}(y \mid x)$. The displacement vector in the Fisher tangent at $\pi_{\text{base}}$. The operational realization of leakage at chosen probe directions.

**Query subspace ($Q$).** The closed subspace spanned by evaluation directions for the (prompt, completion) pairs an audit reads. Represents what the audit sees.

**Retention.** The component $P_1 P_2 P_1 f$ — what passes through both projections. Norm-squared $\sum_j |a_j|^2 \beta_j^2$. Peaks at $\beta = 1$ (coincident subspaces).

**Score function.** $g(x, y) = \nabla_\theta \log \pi_\theta(y \mid x)$. Points in the parameter-space direction that most increases the probability of $y$ given $x$. The fundamental object in the policy gradient theorem.

**Suppression.** The component $P_1 f - P_1 P_2 P_1 f$ — what the second projection removes from the inference subspace. Norm-squared $\sum_j |a_j|^2 (1-\beta_j)^2$. Peaks at $\beta = 0$ (orthogonal subspaces).

**Total error.** The component $f - P_2 f$ — full distance from truth to projected truth. Norm-squared $\sum_j |a_j|^2 (1-\beta_j)$. Per-mode identity: total = suppression + leakage.

---

## Caveats

**Linearization.** The Halmos two-projection apparatus applies in the Fisher-tangent linearization at $\pi_0$. Quantitative magnitudes carry curvature error, measured at 15-25% slope deviation in `test_bridge_B.py` Test 4. Structural conclusions are robust under linearization; exact magnitudes in heavy-alignment regimes require the second-order term or full nonlinear treatment.

**Production-system gap.** Bridge B's distinctive prediction $\mu^2(1-s^2)$ for leakage in the RLHF setup stands at the toy level but has unaddressed obstacles in production: real systems use learned reward models with many effective directions rather than a single linear functional; the loss-function KL coefficient does not equal the m-flat constraint severity except at the optimum; "off-query behavior" lacks an operational definition for an LLM; $\mu$ is not directly observable. The toy prediction stands; the production-system test is open.

**Empirical scope.** The Case Study documents accompanying this Foundations document measure $\rho^*$ on three falsification target topics on Llama-3.1-8B base/Instruct, plus the cross-institutional Hemings comparison between Anthropic Claude and Meta Llama. These are limited samples that demonstrate the methodology's interpretability, not comprehensive characterizations of any institution's full shaping signature. The Pattern Guide and Handbook describe what scaled measurement would require.

**Audit-blind sharpening for induced holes is hypothesis.** The claim that Theorem B understates detection difficulty for induced holes specifically is intuition with toy-level support, not formal theorem. The adversarial sharpening — that institutions can shape what falls in the audit-blind subspace — is plausible but unproven.

**Phantom T6 and T9 are open.** Boundary-layer localization with explicit bounds (T6) and the multi-gap transversality lower bound (T9) are open in both spatial and ML settings. The framework's predictions about feature-space localization of induced-hole distortion (ML-T6) are hypotheses without direct empirical test.

**The writer is also a subject.** This document was written by Claude (Anthropic). The framework's claims about institutional shaping include Anthropic's pipeline as a measurement subject. The writing apparatus is the apparatus the framework characterizes as shaped. Specific framings, word choices, and emphasis decisions in this document reflect Claude's training. This is an irreducible limitation that user-side independent verification would address.

---

## Further Reading

**Phantom framework canonical references:**
- `statistical_phantoms.md` — The §1 abstract spine and four-object decomposition. Foundational.
- `training_distortion_phantom.md` — RLHF as Halmos two-projection in the Fisher tangent. The setup this document operates in.
- `audit_blind_subspace.md` — Theorems A through D. The detection-limit results.
- `info_geometric_reformulation.md` — Bridge B and the second-order term. The KL-geometric apparatus.
- `Phantom_ML_PathForward.docx` — The natural/induced distinction and the dynamic reframing.

**Spatial-gap origin:**
- `hole_problem.ipynb` — The original Phantom Eigenmode Fabrication framework.
- `boundary_layer.ipynb` — T6 boundary-layer phenomena.
- `common_mask_correlation.md` — The correlation case that produced the leakage formula $a_n(1-a_n)|c|^2$.

**Statistical realizations (numerical companions, all verified to machine precision):**
- `pca_masked_companion.md` — PCA under regional spatial mask.
- `regression_omitted_companion.md` — Regression with omitted variables (canonical correlations as principal angles).
- `matched_filter_companion.md` — Matched filtering under common mask.
- `modal_analysis_companion.md` — Operational modal analysis with sensor restriction.

**Information geometry:**
- Amari, *Information Geometry and Its Applications* (2016) — comprehensive treatment.
- Chentsov 1972 — uniqueness of the Fisher information metric.

**KL-regularized RLHF:**
- Christiano et al. 2017 — original RLHF paper.
- Ouyang et al. 2022 — InstructGPT.
- Rafailov et al. 2023 — DPO derivation of the closed form $\pi^* \propto \pi_{\text{ref}} e^{r/\beta}$.

**Neural tangent kernel and feature learning:**
- Jacot, Gabriel, Hongler 2018 — original NTK paper.
- Yang and Hu 2021 — $\mu$P parameterization for feature learning.
- Bordelon and Pehlevan 2022 — DMFT for feature learning in wide networks.

**Asymptotic series and resurgence:**
- Boyd 1999 — *Devil's invention: asymptotic, superasymptotic, and hyperasymptotic series*.
- Marino 2014 — *Lectures on non-perturbative effects in large N gauge theories, matrix models and strings*.
- Costin 2008 — *Asymptotics and Borel Summability*.

**Path integrals in neural networks:**
- Helias and Dahmen 2020 — *Statistical Field Theory for Neural Networks*.
- Halverson, Maiti, Stoner 2021 — neural networks and field theory.

---

*FN-PHANTOM-001 v1.0 — May 2026*
*This document is the mathematical foundations layer for the framework's $\rho$-measurement program. It supersedes the earlier `probability_distortion_framework.md` which treated $\rho$ as a freestanding object; this version threads $\rho$ through the Phantom apparatus from the start.*
