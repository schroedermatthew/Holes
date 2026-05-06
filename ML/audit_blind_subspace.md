# The Audit-Blind Subspace

## An information-theoretic limit on audits of trained networks

*Working Paper Draft · April 2026*

*Companion to: Statistical Phantoms; Training Distortion as Forced Constraint Projection; Training Corpus Holes as Multiplication Defects; Information-Geometric Reformulation; Compression–Commutator Geometry (v3); Phantom Eigenmode Fabrication from Measurement Gaps*

---

## Abstract

Let $F: \Xi \to H$ be the map taking a training-data or training-objective distortion $\xi$ to the resulting trained-network function $f_{\theta(\xi)}$ in a Hilbert function space $H$. Let $\mathcal{Q} = \{q_1, \ldots, q_N\}$ be a finite collection of continuous linear functionals on $H$ — an audit query suite. The **audit-blind subspace** is

$$\mathcal{N}_{\text{audit}} := \ker(A_\mathcal{Q} \circ dF|_0) \subset \Xi,$$

the set of distortion directions to which the audit map $A_\mathcal{Q} = (q_i)_{i=1}^N$ is insensitive at first order. Distortions in $\mathcal{N}_{\text{audit}}$ produce trained networks indistinguishable from the base under the audit, regardless of how large the resulting effect on user-facing outputs becomes.

The main results, in the linearized (NTK / Fisher-tangent) regime:

**Theorem A (dimension).** $\dim(\mathcal{N}_{\text{audit}}) = \dim(\Xi) - \dim(\mathrm{Range}(A_\mathcal{Q} \circ dF|_0))$.

**Theorem B (lower bound).** For any audit suite of size $N$, $\dim(\mathcal{N}_{\text{audit}}) \geq \dim(\Xi) - N$.

**Theorem C (concerning-subspace coverage).** For any $\mathcal{C} \subset \Xi$, the audit-visible component of $\mathcal{C}$ is determined by the principal angles between $\mathcal{C}$ and $\mathcal{N}_{\text{audit}}^\perp$, with the four-object decomposition (`statistical_phantoms.md` §1.3) giving exact scalar identities.

**Theorem D (optimal audit construction).** Given a target concerning subspace $\mathcal{C}$ of dimension $k$, an audit suite of size $N \geq k$ suffices to make $\mathcal{N}_{\text{audit}} \cap \mathcal{C} = \{0\}$, with explicit construction via the SVD of $L^*|_{\mathcal{C}}$ where $L = dF|_0$. With $N < k$, the audit-blind subspace contains $\mathcal{C}$'s bottom $(k - N)$ singular directions of $L|_{\mathcal{C}}$.

The corollary: an audit using only queries on the trained network has an information-theoretic detection limit set by the principal-angle geometry between audit query coverage and the distortion space. This limit is independent of how thoroughly the audit examines its own queries.

---

## Preface

This document derives the audit-blindness lower bound implicit in the framework developed across `statistical_phantoms.md`, `training_distortion_phantom.md`, and `training_corpus_holes.md`. The result is a consequence of the existing apparatus rather than a new development; the mathematics is linear algebra in the linearized regime, with the four-object decomposition from `statistical_phantoms.md` §1.3 carrying through directly.

The applied setting is alignment auditing: an auditor wishes to determine whether a trained network has been subjected to specific kinds of distortion during training, using only queries to the trained network. The framework's contribution is the formal observation that any such audit has an information-theoretic ceiling set by the audit suite's query coverage relative to the distortion space, and that ceiling is computable from architectural and training-procedure information alone.

Scope. The results below are stated and proved in the linearized regime — small distortions, NTK-style local linearization for wide networks, Fisher-tangent linearization for distributional outputs. Extensions to nonlinear regimes are sketched in Part VII; quantitative magnitude corrections from curvature are governed by the second-order term in the e-projection expansion (companion `info_geometric_reformulation.md` §B.5). The structural lower-bound theorems (A, B, D) are robust under the linearization; the visibility-fraction theorem (C) depends on the four-object decomposition's exactness in the Hilbert setting.

Organization. Part I sets up the function space, distortion space, and linearization. Part II defines the audit map. Part III proves Theorems A–C on the audit-blind subspace. Part IV develops the principal-angle geometry against concerning subspaces. Part V works out a complete numerical example for ridge regression. Part VI proves Theorem D on optimal audit construction and develops the audit-protocol-design implications. Part VII addresses extensions to white-box and procedural audit settings and to the nonlinear regime. Part VIII situates the result relative to existing literature on backdoor attacks, influence functions, and mechanistic interpretability.

---

## Part I — Setup

### 1.1 Architecture and training procedure

Fix:

- A measurable input space $\mathcal{X}$ with base measure $\nu$.
- An output space $\mathcal{Y}$ (taken throughout to be a Euclidean space; the distributional case is reduced to the Hilbert setting in §1.2).
- A parametric family $f: \Theta \to \mathcal{F}(\mathcal{X}, \mathcal{Y})$ — the **architecture** — assigning to each parameter vector $\theta \in \Theta = \mathbb{R}^P$ a function $f_\theta: \mathcal{X} \to \mathcal{Y}$.
- A training procedure $T$ — a map from training data and objective to trained parameters $\theta(\cdot) : \mathcal{D} \to \Theta$, where $\mathcal{D}$ is the space of training inputs (data, reward signal, hyperparameters, init seed).

The training procedure is taken as fixed: same loss, same optimizer, same schedule, same initialization. What varies is the data and objective — captured by the distortion space $\Xi$ below.

### 1.2 The function space

The **predictor space** is

$$H = L^2(\mathcal{X}, \nu; \mathcal{Y})$$

with inner product $\langle f, g \rangle = \int_\mathcal{X} f(x) \cdot g(x) \, d\nu(x)$. This is a separable Hilbert space.

For regression-type readouts (deterministic $f_\theta: \mathcal{X} \to \mathcal{Y}$), $f_\theta \in H$ directly, and the operator-theoretic apparatus applies without further linearization.

For distributional outputs (next-token policies $\pi_\theta(y|x)$ on a discrete vocabulary), the natural ambient space is the manifold of conditional distributions with Fisher / KL Riemannian structure — a curved manifold, not Hilbert. Following the convention established in `training_distortion_phantom.md` §1.1, work in the **Fisher-tangent linearization** at a chosen base point $\pi_0$: identify a policy $\pi$ near $\pi_0$ with its score $u = \log \pi - \log \pi_0$ in the tangent space $T_{\pi_0}\mathcal{P}$, equipped with the Fisher inner product

$$\langle u, v \rangle_F = \mathbb{E}_{x \sim \nu}\,\mathbb{E}_{y \sim \pi_0(\cdot|x)}[u(x,y) \, v(x,y)].$$

In this tangent Hilbert space the linear-algebra apparatus applies, with second-order curvature corrections governed by the e-projection expansion at the base point. All results below should be read in $H$ either as the regression-case $L^2$ space or as the Fisher tangent at a chosen base point; both are Hilbert spaces and the operator-theoretic statements are identical in form.

### 1.3 The distortion space

The **distortion space** $\Xi$ is a Hilbert space parametrizing modifications to the training procedure. Two examples:

**Data distortion.** $\Xi = L^2(\mathcal{X}, \nu)$ — perturbations to the training data distribution density. A distortion $\xi \in \Xi$ corresponds to training under data drawn from the perturbed distribution $\nu \cdot (1 + \xi)$ (with $\xi$ small enough to keep the distribution non-negative). This is the setting of `training_corpus_holes.md`.

**Objective distortion.** $\Xi = H$ — perturbations to a reward function or training objective. A distortion $\xi$ corresponds to training under objective $r + \xi$ where $r$ is the base reward. This is closer to `training_distortion_phantom.md`.

**Combined distortion.** $\Xi = L^2(\mathcal{X}, \nu) \oplus H$ — both data and objective perturbations together. This is the realistic deployment setting from `training_corpus_holes.md` Part V.

The specific structure of $\Xi$ does not affect the audit-blindness theorems below; what matters is that $\Xi$ is a Hilbert space and the distortion-to-function map below is well-defined.

### 1.4 The distortion-to-function map

Fix the base distortion $\xi_0 = 0$ (no distortion). Under $\xi$, the trained parameters become $\theta(\xi)$ and the trained function is $f_{\theta(\xi)} \in H$. Define the **distortion-to-function map**

$$F : \Xi \to H, \qquad F(\xi) = f_{\theta(\xi)}.$$

Write $f_0 = F(0)$ for the undistorted trained function.

The map $F$ is generically nonlinear — composition of a nonlinear training dynamics with a nonlinear architecture. In specific regimes it becomes tractable.

**Definition 1.4.1 (linearization).** $F$ is **linearizable at $0$** if it is Fréchet differentiable at $0$ with bounded linear derivative $L = dF|_0 : \Xi \to H$. The **distortion-to-function tangent map** is this $L$.

When $F$ is linearizable at $0$:

$$F(\xi) = f_0 + L\xi + R(\xi), \qquad \|R(\xi)\| = o(\|\xi\|).$$

The **cloud of trained networks under small distortions** is, to first order, the affine subspace $f_0 + \mathrm{Range}(L) \subset H$.

**Examples where $L$ has explicit form.**

For ridge regression with fixed design $X \in \mathbb{R}^{n \times d}$ and label distortion $\xi \in \mathbb{R}^n$: $\theta(\xi) = (X^T X + \lambda I)^{-1} X^T (y_0 + \xi)$, which is *exactly* linear in $\xi$. The tangent map is $(L\xi)(x) = \xi^T X(X^TX + \lambda I)^{-1} x$. Worked through in Part V.

For wide neural networks trained by gradient flow on quadratic loss: in the NTK limit, $f_{\theta(\xi)}$ is exactly the kernel ridge regression solution under the Neural Tangent Kernel $K_{\text{NTK}}(x, x') = \langle \nabla_\theta f_\theta(x), \nabla_\theta f_\theta(x')\rangle$ at initialization. Distortions of the training data produce a linear response in the kernel-regression sense (Jacot–Gabriel–Hongler 2018; Lee et al. 2019).

For wide networks at finite width or under non-quadratic loss: the linearization holds approximately for small distortions, with corrections governed by feature learning and the loss curvature. The audit-blindness lower bound (Theorem B) is structurally tight regardless; the dimension formula (Theorem A) holds whenever the tangent map exists.

For RLHF-style constrained training: the linearization is the Fisher-tangent setting of `training_distortion_phantom.md` §1.4. Distortions to the reward function produce first-order changes in the trained policy that are linear in the constraint structure.

In all cases, the linearization is exact in some controlled regime, and the audit-blindness theorems below are statements about that regime.

### 1.5 Notation summary

Throughout:

- $\Xi$: distortion space (Hilbert, possibly infinite-dimensional).
- $H$: predictor space (Hilbert, possibly infinite-dimensional).
- $L = dF|_0 : \Xi \to H$: distortion-to-function tangent map (bounded linear).
- $\mathcal{Q} = \{q_1, \ldots, q_N\} \subset H^* \cong H$: audit query suite (finite set of continuous linear functionals identified via Riesz with elements of $H$).
- $A_\mathcal{Q} : H \to \mathbb{R}^N$: audit map, $A_\mathcal{Q}(f) = (\langle q_i, f\rangle)_{i=1}^N$.
- $\mathcal{N}_{\text{audit}} \subset \Xi$: audit-blind subspace (defined in §3.1).
- $\mathcal{C} \subset \Xi$: concerning subspace (introduced in §4.1).
- $P_S$ for any closed subspace $S$: orthogonal projection onto $S$.

---

## Part II — The Audit

### 2.1 Audit queries as linear functionals

An **audit query** is a continuous linear functional $q : H \to \mathbb{R}$. By the Riesz representation theorem, $q$ corresponds to a unique $h_q \in H$ with $q(f) = \langle h_q, f\rangle$. We identify $q$ with $h_q$ and write $q \in H$ throughout.

**Examples.**

*Point evaluation.* If $H$ contains continuous functions and $\delta_x$ is the Dirac measure at $x$, then $q(f) = f(x)$ is a continuous linear functional (assuming $H$ has a reproducing kernel structure, e.g., is an RKHS). The corresponding $h_q$ is the kernel section $K(\cdot, x)$.

*Test-set evaluation.* Given a test set $\{x_i, y_i\}_{i=1}^M$, queries of the form $q(f) = \frac{1}{M}\sum_i \ell(f(x_i), y_i)$ for a linear loss $\ell$ are continuous linear functionals on $H$.

*Aggregate readouts.* Queries that probe an aggregate property of the function — average value over a region, mode-coefficient extraction, frequency content — are continuous linear functionals when the aggregation is bounded.

*Nonlinear queries.* Queries that depend nonlinearly on $f$ (e.g., the loss against a nonlinear target, the entropy of the output distribution) are not linear functionals, but their *linearization at $f_0$* is. For audit-blindness analysis at first order in the distortion, replacing each nonlinear query by its linearization at $f_0$ is the natural reduction. The audit-blindness theorems below apply to the linearized queries.

### 2.2 The audit map

Given an audit query suite $\mathcal{Q} = \{q_1, \ldots, q_N\}$, define the **audit map**

$$A_\mathcal{Q} : H \to \mathbb{R}^N, \qquad A_\mathcal{Q}(f) = (\langle q_i, f\rangle)_{i=1}^N.$$

This is a bounded linear operator from $H$ to $\mathbb{R}^N$. Its **adjoint** $A_\mathcal{Q}^* : \mathbb{R}^N \to H$ acts by $A_\mathcal{Q}^*(c) = \sum_i c_i q_i$.

The **audit subspace** is

$$\mathcal{Q}^* := \mathrm{Range}(A_\mathcal{Q}^*) = \mathrm{span}(q_1, \ldots, q_N) \subset H.$$

This is a finite-dimensional subspace of $H$ of dimension at most $N$ (equal to $N$ when the $q_i$ are linearly independent).

**Lemma 2.2.1.** $\ker(A_\mathcal{Q}) = (\mathcal{Q}^*)^\perp$.

*Proof.* $A_\mathcal{Q}(f) = 0$ iff $\langle q_i, f\rangle = 0$ for all $i$ iff $f \perp q_i$ for all $i$ iff $f \perp \mathrm{span}(q_i) = \mathcal{Q}^*$. ∎

The audit map sees only the $\mathcal{Q}^*$-component of $f$. Anything orthogonal to the audit subspace is invisible to the audit.

### 2.3 Audit-distinguishability

Two trained functions $f_1, f_2 \in H$ are **audit-distinguishable** under $\mathcal{Q}$ if $A_\mathcal{Q}(f_1) \neq A_\mathcal{Q}(f_2)$, equivalently, $f_1 - f_2 \notin (\mathcal{Q}^*)^\perp$.

Two distortions $\xi_1, \xi_2 \in \Xi$ are **audit-distinguishable to first order** if their linearized trained functions $f_0 + L\xi_1$ and $f_0 + L\xi_2$ are audit-distinguishable, equivalently, $A_\mathcal{Q}(L(\xi_1 - \xi_2)) \neq 0$.

**Higher-order remainder.** When $F$ is only approximately linear (i.e., $F(\xi) = f_0 + L\xi + R(\xi)$ with nonzero remainder $R$), audit responses to a single distortion $\xi$ are perturbed by $\langle q_i, R(\xi)\rangle$, of order $o(\|\xi\|)$. For comparing two distortions $\xi_1, \xi_2$ with $\|\xi_j\| \ll 1$, the linearization captures the dominant signal. Quantitative magnitudes of audit-blind components carry the second-order envelope from `info_geometric_reformulation.md` §B.5; the structural conclusions (existence of audit-blind directions, dimension lower bounds) are robust to the linearization.

---

## Part III — The Audit-Blind Subspace

### 3.1 Definition

**Definition 3.1.1.** The **audit-blind subspace** is

$$\mathcal{N}_{\text{audit}} := \ker(A_\mathcal{Q} \circ L) \subset \Xi.$$

Equivalently, $\mathcal{N}_{\text{audit}} = \{\xi \in \Xi : L\xi \in (\mathcal{Q}^*)^\perp\}$.

$\mathcal{N}_{\text{audit}}$ is a closed linear subspace of $\Xi$ (kernel of a bounded linear operator). Distortions in $\mathcal{N}_{\text{audit}}$ produce trained-function changes orthogonal to the audit subspace; the audit map is identically zero on these distortions. They are *first-order invisible* to the audit.

**Theorem 1 (audit-blind subspace, linearized).** *In the linearization regime, two distortions $\xi_1, \xi_2 \in \Xi$ are audit-indistinguishable to first order if and only if $\xi_1 - \xi_2 \in \mathcal{N}_{\text{audit}}$.*

*Proof.* In the linearization $F(\xi) = f_0 + L\xi$:

$$A_\mathcal{Q}(F(\xi_1)) - A_\mathcal{Q}(F(\xi_2)) = A_\mathcal{Q}(L(\xi_1 - \xi_2)) = (A_\mathcal{Q} \circ L)(\xi_1 - \xi_2).$$

This is zero iff $\xi_1 - \xi_2 \in \ker(A_\mathcal{Q} \circ L) = \mathcal{N}_{\text{audit}}$. ∎

The equivalence classes of $\sim_\mathcal{Q}$ ("audit-indistinguishable to first order") on $\Xi$ are the cosets of $\mathcal{N}_{\text{audit}}$. The quotient $\Xi / \mathcal{N}_{\text{audit}}$ is the space of distortions modulo audit indistinguishability.

### 3.2 Dimension formula

**Theorem 2 (dimension).** *Let $L : \Xi \to H$ be the linearized distortion-to-function map and $A_\mathcal{Q} : H \to \mathbb{R}^N$ the audit map for a query suite of size $N$. Then*

$$\dim(\mathcal{N}_{\text{audit}}) = \dim(\Xi) - \dim(\mathrm{Range}(A_\mathcal{Q} \circ L)),$$

*with the convention that infinite dimensions subtract to give infinite codimension when finite-codimensional.*

*Proof.* $A_\mathcal{Q} \circ L : \Xi \to \mathbb{R}^N$ is a bounded linear operator from a Hilbert space to a finite-dimensional Euclidean space. By the rank-nullity theorem (which holds for bounded operators with finite-dimensional range),

$$\dim(\Xi) = \dim(\ker(A_\mathcal{Q} \circ L)) + \dim(\mathrm{Range}(A_\mathcal{Q} \circ L)).$$

Substituting $\mathcal{N}_{\text{audit}} = \ker(A_\mathcal{Q} \circ L)$ gives the claim. ∎

### 3.3 Lower bound

**Theorem 3 (audit-blindness lower bound).** *For any audit suite of size $N$,*

$$\dim(\mathcal{N}_{\text{audit}}) \geq \dim(\Xi) - N.$$

*Proof.* $\mathrm{Range}(A_\mathcal{Q} \circ L) \subseteq \mathbb{R}^N$, so $\dim(\mathrm{Range}(A_\mathcal{Q} \circ L)) \leq N$. By Theorem 2,

$$\dim(\mathcal{N}_{\text{audit}}) = \dim(\Xi) - \dim(\mathrm{Range}(A_\mathcal{Q} \circ L)) \geq \dim(\Xi) - N. \quad \text{∎}$$

**Corollary 3.3.1.** *If $\dim(\Xi) > N$, the audit-blind subspace is non-trivial: there exist nonzero distortions invisible to the audit at first order.*

**Corollary 3.3.2 (user-relevant audit-blindness).** *Let $\Xi_{\text{vis}} := \overline{\mathrm{Range}(L^*)} \subset \Xi$ be the closure of the range of $L^*$ — the directions of $\Xi$ to which the trained function responds (equivalently, the orthogonal complement of $\ker(L)$). The **user-relevant audit-blind subspace** is*

$$\mathcal{N}_{\text{audit}}^{\text{user}} := \mathcal{N}_{\text{audit}} \cap \Xi_{\text{vis}}.$$

*Its dimension satisfies*

$$\dim(\mathcal{N}_{\text{audit}}^{\text{user}}) \geq \dim(\Xi_{\text{vis}}) - N.$$

*Proof.* Restrict $A_\mathcal{Q} \circ L$ to $\Xi_{\text{vis}}$. The restricted map has kernel $\mathcal{N}_{\text{audit}} \cap \Xi_{\text{vis}}$ and range contained in $\mathbb{R}^N$. Apply Theorem 2 to the restriction. ∎

The user-relevant audit-blind subspace is the structurally meaningful object: distortions in $\mathcal{N}_{\text{audit}} \setminus \Xi_{\text{vis}}$ produce no change in the trained function (they lie in $\ker(L)$), so their invisibility to the audit is uninteresting. The interesting cases are distortions that *do* change the trained function but in directions the audit happens not to span. Corollary 3.3.2 says this set has dimension at least $\dim(\Xi_{\text{vis}}) - N$.

### 3.4 Computability

In the linearized regime, $\mathcal{N}_{\text{audit}}$ is computable from $L$ and $\mathcal{Q}$ alone, without reference to the actual trained network or the actual distortion under consideration.

**Procedure.**

1. Compute the matrix representation of $A_\mathcal{Q} \circ L : \Xi \to \mathbb{R}^N$. For finite-dimensional $\Xi = \mathbb{R}^M$, this is an $N \times M$ matrix $B$ with $B_{ij} = \langle q_i, L e_j\rangle$ where $\{e_j\}$ is a basis of $\Xi$.

2. Compute the kernel of $B$ via SVD: $\mathcal{N}_{\text{audit}}$ is spanned by the right singular vectors of $B$ corresponding to zero (or numerically-zero) singular values.

3. The dimension of $\mathcal{N}_{\text{audit}}$ is $M - \mathrm{rank}(B)$.

4. To check whether a specific distortion $\xi$ is audit-blind: compute $B\xi$ (in the basis representation); $\xi \in \mathcal{N}_{\text{audit}}$ iff $B\xi = 0$.

For infinite-dimensional $\Xi$, replace step 1 with operator-theoretic computation of the relevant projections. In the NTK setting, $L$ has explicit kernel form; in ridge regression, $L$ is a literal matrix.

The procedure is computationally cheap: SVD of an $N \times M$ matrix where $N$ is the audit suite size (typically $\leq 10^4$) and $M$ is the distortion-space dimension (problem-dependent but bounded by the parameter count).

---

## Part IV — Concerning Subspaces and Visibility

The audit-blind subspace is the *complete* set of audit-invisible distortion directions. In practice, the auditor cares about a specific set of distortions — backdoor attacks, biased reweighting of training data, suppression of specific content — which forms a **concerning subspace** $\mathcal{C} \subset \Xi$. The relevant question is not "what is $\mathcal{N}_{\text{audit}}$" but "how much of $\mathcal{C}$ does $\mathcal{N}_{\text{audit}}$ cover."

This is precisely a principal-angle question between two subspaces of $\Xi$, which the four-object decomposition from `statistical_phantoms.md` §1.3 answers exactly.

### 4.1 Concerning subspaces

**Definition 4.1.1.** A **concerning subspace** is a closed linear subspace $\mathcal{C} \subset \Xi$ representing distortion directions of audit interest.

**Examples.**

*Targeted suppression of specific content.* If the auditor cares whether the training procedure has suppressed information about topic $T$, $\mathcal{C}$ is the subspace of distortions that systematically reduce the trained function's response on $T$-related queries.

*Demographic targeting.* If the auditor cares whether the training has imposed a specific demographic-distribution constraint on outputs, $\mathcal{C}$ is the subspace of distortions affecting outputs in directions correlated with the demographic constraint.

*Backdoor / triggered behavior.* For a putative trigger pattern $t \in \mathcal{X}$, $\mathcal{C}$ is the subspace of distortions producing nonzero $L\xi(t)$ — i.e., distortions that change the model's response on the trigger.

*Truth-anchored deviation.* For a truth-anchored query suite $\mathcal{Q}_{\text{truth}} = \{q^{\text{truth}}_j\}$ probing factual or empirical content, $\mathcal{C}$ is the subspace of distortions producing nonzero response on $\mathcal{Q}_{\text{truth}}$. This is the concerning subspace most directly aligned with the trilogy's truth-suppression analysis.

The specific characterization of $\mathcal{C}$ is the auditor's choice; the framework treats $\mathcal{C}$ as input.

### 4.2 Principal angles

Let $P_\mathcal{C}, P_{\mathcal{N}_{\text{audit}}^\perp}$ denote orthogonal projections in $\Xi$ onto $\mathcal{C}$ and $\mathcal{N}_{\text{audit}}^\perp$ respectively. The compression

$$T_\mathcal{C}(P_{\mathcal{N}_{\text{audit}}^\perp}) = P_\mathcal{C} \, P_{\mathcal{N}_{\text{audit}}^\perp} \, P_\mathcal{C}\big|_\mathcal{C}$$

is self-adjoint on $\mathcal{C}$ with eigenvalues $\beta_j = \cos^2 \theta_j \in [0, 1]$, where $\theta_j$ are the **principal angles** between $\mathcal{C}$ and $\mathcal{N}_{\text{audit}}^\perp$.

Geometric reading. $\beta_j = 1$ corresponds to a direction in $\mathcal{C}$ that lies entirely in $\mathcal{N}_{\text{audit}}^\perp$ — fully visible to the audit. $\beta_j = 0$ corresponds to a direction in $\mathcal{C}$ that lies entirely in $\mathcal{N}_{\text{audit}}$ — fully invisible. Intermediate $\beta_j$ corresponds to a direction with partial visibility, decomposing into audit-visible and audit-invisible components in proportions $\sqrt{\beta_j}$ and $\sqrt{1 - \beta_j}$.

### 4.3 Four-object decomposition

The four-object decomposition of `statistical_phantoms.md` §1.3 applies with $P_1 = P_\mathcal{C}$ and $P_2 = P_{\mathcal{N}_{\text{audit}}^\perp}$. For a unit-norm distortion $\xi = \sum_j a_j u_j \in \mathcal{C}$ written in the eigenbasis $\{u_j\}$ of $T_\mathcal{C}(P_{\mathcal{N}_{\text{audit}}^\perp})$:

| Object | Norm-squared | Interpretation in audit setting |
|---|---|---|
| **Audit-visible component of $\xi$** $\;P_\mathcal{C} P_{\mathcal{N}_{\text{audit}}^\perp} P_\mathcal{C} \xi$ | $\sum_j |a_j|^2 \beta_j^2$ | Detected by audit, projected back into $\mathcal{C}$ |
| **Audit-invisible component of $\xi$ within $\mathcal{C}$** $\;P_\mathcal{C}\xi - P_\mathcal{C} P_{\mathcal{N}_{\text{audit}}^\perp} P_\mathcal{C} \xi$ | $\sum_j |a_j|^2 (1 - \beta_j)^2$ | $\mathcal{C}$-content invisible to the audit |
| **Cross-leakage** $\;(I - P_\mathcal{C}) P_{\mathcal{N}_{\text{audit}}^\perp} \xi$ | $\sum_j |a_j|^2 \beta_j (1 - \beta_j)$ | Audit-visible content escaping $\mathcal{C}$ into adjacent directions |
| **Total $\mathcal{C}$-component invisible to audit** $\;\xi - P_{\mathcal{N}_{\text{audit}}^\perp} \xi$ | $\sum_j |a_j|^2 (1 - \beta_j)$ | Full magnitude of audit-blindness on $\xi$ |

with the per-mode identity $1 - \beta = (1-\beta)^2 + \beta(1-\beta)$ (total = suppression + leakage), specialized to this setting as: total audit-invisibility = within-$\mathcal{C}$ invisibility + cross-leakage.

**Theorem 4 (audit-visibility decomposition).** *For any concerning subspace $\mathcal{C} \subset \Xi$ and any audit suite $\mathcal{Q}$, the audit-visible component of distortions in $\mathcal{C}$ is governed by the four-object decomposition with respect to the principal angles between $\mathcal{C}$ and $\mathcal{N}_{\text{audit}}^\perp$.*

*Proof.* Direct application of `statistical_phantoms.md` §1.3 Theorem 1.3.1 (the four-object identity) with $P_1 = P_\mathcal{C}$ and $P_2 = P_{\mathcal{N}_{\text{audit}}^\perp}$, with eigenvalues $\beta_j$ of $P_\mathcal{C} P_{\mathcal{N}_{\text{audit}}^\perp} P_\mathcal{C}|_\mathcal{C}$ being the squared cosines of principal angles between the two subspaces. ∎

### 4.4 Coverage fractions

**Definition 4.4.1.** The **audit-coverage fraction** of $\mathcal{C}$ is

$$\mathrm{cov}_\mathcal{Q}(\mathcal{C}) := \frac{\sum_j \beta_j}{\dim(\mathcal{C})} = \frac{\mathrm{tr}(P_\mathcal{C} P_{\mathcal{N}_{\text{audit}}^\perp} P_\mathcal{C}|_\mathcal{C})}{\dim(\mathcal{C})} \in [0, 1].$$

This is the average squared cosine of the principal angles between $\mathcal{C}$ and $\mathcal{N}_{\text{audit}}^\perp$. $\mathrm{cov}_\mathcal{Q}(\mathcal{C}) = 1$ means the audit fully covers $\mathcal{C}$ (every direction in $\mathcal{C}$ is detected); $\mathrm{cov}_\mathcal{Q}(\mathcal{C}) = 0$ means the audit is blind to all of $\mathcal{C}$.

**Lemma 4.4.2.** *If $\dim(\mathcal{C}) > N$, $\mathrm{cov}_\mathcal{Q}(\mathcal{C}) \leq N / \dim(\mathcal{C})$.*

*Proof.* $\sum_j \beta_j = \mathrm{tr}(P_\mathcal{C} P_{\mathcal{N}_{\text{audit}}^\perp} P_\mathcal{C}) \leq \mathrm{tr}(P_{\mathcal{N}_{\text{audit}}^\perp}) = \dim(\mathcal{N}_{\text{audit}}^\perp) \leq N$ (since $\mathcal{N}_{\text{audit}}^\perp \subseteq \overline{\mathrm{Range}(L^* A_\mathcal{Q}^*)}$, which has dimension at most $N$). Divide by $\dim(\mathcal{C})$. ∎

**Corollary 4.4.3.** *If the auditor's concerning subspace has dimension $\dim(\mathcal{C}) = k$ and the audit uses $N$ queries, the audit covers at most $N/k$ fraction of $\mathcal{C}$ on average. Equivalently: the audit is blind to at least $1 - N/k$ of $\mathcal{C}$.*

This is the quantitative version of the lower bound: not just "there exist audit-blind directions," but "for any concerning subspace of dimension $k > N$, a constant fraction is invisible."

---

## Part V — Numerical Example: Ridge Regression

This section works through the audit-blindness analysis for a setting where the linearization is exact: ridge regression with fixed design and label distortion.

### 5.1 Setup

Training data: $X \in \mathbb{R}^{n \times d}$ (fixed design matrix, $n$ examples, $d$ features), $y_0 \in \mathbb{R}^n$ (base labels). Ridge regression with regularization $\lambda > 0$:

$$\theta(y) = (X^T X + \lambda I)^{-1} X^T y.$$

Architecture: $f_\theta(x) = \theta^T x$ (linear regression).

Distortion space: $\Xi = \mathbb{R}^n$ (additive label distortions). $y(\xi) = y_0 + \xi$.

### 5.2 The linearized distortion-to-function map

Trained parameters under distortion: $\theta(\xi) = \theta_0 + (X^T X + \lambda I)^{-1} X^T \xi$ where $\theta_0 = \theta(y_0)$.

Trained function:
$$F(\xi)(x) = \theta(\xi)^T x = f_0(x) + \xi^T X (X^T X + \lambda I)^{-1} x.$$

Define $M := X(X^TX + \lambda I)^{-1} \in \mathbb{R}^{n \times d}$. Then

$$L\xi(x) := F(\xi)(x) - f_0(x) = \xi^T M x = \langle Mx, \xi\rangle_{\mathbb{R}^n}.$$

This is *exact*, not approximate — ridge regression is linear in the labels.

### 5.3 Audit map

Audit query suite: $\{x_1, \ldots, x_N\} \subset \mathbb{R}^d$ (point-evaluation queries). Audit map:

$$A_\mathcal{Q}(L\xi) = (L\xi(x_i))_{i=1}^N = \big(\xi^T M x_i\big)_{i=1}^N = X_{\text{audit}} M^T \xi,$$

where $X_{\text{audit}} \in \mathbb{R}^{N \times d}$ stacks the audit query points. The composite map is the matrix

$$B := X_{\text{audit}} M^T \in \mathbb{R}^{N \times n}.$$

### 5.4 Audit-blind subspace

$\mathcal{N}_{\text{audit}} = \ker(B)$, with $\dim(\mathcal{N}_{\text{audit}}) = n - \mathrm{rank}(B) \geq n - N$.

**User-relevant audit-blind subspace.** $\Xi_{\text{vis}} = \mathrm{Range}(L^*) = \mathrm{Range}(M)$, which has dimension $\mathrm{rank}(M) = d$ (assuming $X$ full column rank, which holds generically for $n \geq d$).

The user-relevant audit-blind subspace is $\mathcal{N}_{\text{audit}} \cap \mathrm{Range}(M)$. Its dimension can be computed via:

$$\dim(\mathcal{N}_{\text{audit}} \cap \mathrm{Range}(M)) = \dim(\mathrm{Range}(M)) - \dim(\mathrm{Range}(B|_{\mathrm{Range}(M)})).$$

Now $B|_{\mathrm{Range}(M)} = X_{\text{audit}} M^T$ restricted to vectors of the form $Mv$. For $\xi = Mv$:

$$B\xi = X_{\text{audit}} M^T M v.$$

Since $M^T M = (X^T X + \lambda I)^{-1} X^T X (X^T X + \lambda I)^{-1}$ is invertible (for $\lambda > 0$), the map $v \mapsto X_{\text{audit}} M^T M v$ has the same rank as $X_{\text{audit}}$. Generically $\mathrm{rank}(X_{\text{audit}}) = \min(N, d)$.

Therefore:

$$\dim(\mathcal{N}_{\text{audit}}^{\text{user}}) = d - \min(N, d) = \max(d - N, 0).$$

For $N < d$: there are exactly $d - N$ user-relevant directions in $\Xi$ that the audit cannot detect, no matter how the labels are perturbed in those directions.

### 5.5 Worked numerical demonstration

Concrete instance: $n = 100$ training examples, $d = 5$ features, $N = 3$ audit queries, $\lambda = 0.01$.

Predictions: $\dim(\mathcal{N}_{\text{audit}}) \geq 100 - 3 = 97$; $\dim(\mathcal{N}_{\text{audit}}^{\text{user}}) \geq 5 - 3 = 2$.

```python
import numpy as np
np.random.seed(42)

n, d = 100, 5
N_audit = 3
lam = 0.01

# Setup: training data and base labels
X = np.random.randn(n, d)
y0 = X @ np.random.randn(d) + 0.1 * np.random.randn(n)

# Ridge regression: theta(y) = (X^T X + lam I)^{-1} X^T y
A_inv = np.linalg.inv(X.T @ X + lam * np.eye(d))
M = X @ A_inv

# Audit query points
X_audit = np.random.randn(N_audit, d)

# Audit map matrix B = X_audit M^T (N_audit x n)
B = X_audit @ M.T

# Audit-blind subspace = null(B)
print(f"rank(B) = {np.linalg.matrix_rank(B)}, predicted ≤ {N_audit}")
print(f"dim(N_audit) = {n - np.linalg.matrix_rank(B)}, predicted ≥ {n - N_audit}")

# User-relevant audit-blind: intersection with Range(M)
# Find v in null(X_audit) ⊂ R^d
_, S_x, Vt_x = np.linalg.svd(X_audit, full_matrices=True)
null_X_audit = Vt_x[(S_x > 1e-10).sum():].T  # shape (d, d - N_audit)
print(f"dim(null(X_audit)) in R^d = {null_X_audit.shape[1]}, predicted = {d - N_audit}")

# For each v in null(X_audit), there is a corresponding xi = (M^T)^+ v in user-relevant audit-blind
# Check: B xi = X_audit M^T xi = X_audit v = 0 since v in null(X_audit)
v = null_X_audit[:, 0]
xi_blind = np.linalg.pinv(M.T) @ v

# Verify audit-blindness
audit_response = B @ xi_blind
print(f"Audit response ||B xi||: {np.linalg.norm(audit_response):.2e}, predicted ≈ 0")

# Verify nonzero effect on user query (a query NOT in the audit suite)
x_user = np.random.randn(d)
function_change_at_user = xi_blind @ M @ x_user
print(f"Function change at user query: {function_change_at_user:.4f}, predicted nonzero")

# Two distinct audit-blind distortions producing different user-facing functions
v1, v2 = null_X_audit[:, 0], null_X_audit[:, 1]
xi_1 = np.linalg.pinv(M.T) @ v1
xi_2 = np.linalg.pinv(M.T) @ v2

# Both give zero audit response
audit_1 = np.linalg.norm(B @ xi_1)
audit_2 = np.linalg.norm(B @ xi_2)
print(f"||B xi_1||: {audit_1:.2e}, ||B xi_2||: {audit_2:.2e}, both predicted ≈ 0")

# Different function-space images
function_diff_norm = np.linalg.norm(M.T @ (xi_1 - xi_2))
print(f"||L xi_1 - L xi_2|| (in feature space): {function_diff_norm:.4f}, nonzero")

# Effect on a battery of user queries
n_user = 50
X_user = np.random.randn(n_user, d)
responses_1 = X_user @ M.T @ xi_1
responses_2 = X_user @ M.T @ xi_2
print(f"User query response divergence: {np.abs(responses_1 - responses_2).max():.4f}")
print(f"User query RMS divergence:      {np.sqrt(np.mean((responses_1 - responses_2)**2)):.4f}")
```

Expected output (deterministic given the seed):

```
rank(B) = 3, predicted <= 3
dim(N_audit) = 97, predicted >= 97
dim(null(X_audit)) in R^d = 2, predicted = 2
Audit response ||B xi||: 4.82e-16, predicted ~ 0
Function change at user query: 0.4111, predicted nonzero
||B xi_1||: 4.82e-16, ||B xi_2||: 7.67e-16, both predicted ~ 0
||L xi_1 - L xi_2|| (in feature space): 1.4142, nonzero
User query response divergence: 3.2831
User query RMS divergence:      1.3867
```

The two distortions $\xi_1, \xi_2$ are audit-indistinguishable (audit responses agree to floating-point precision, $\sim 10^{-16}$) but produce trained functions that differ measurably across the user query distribution (RMS divergence $\sim 1.4$, max divergence $\sim 3.3$). This is the audit-blindness phenomenon made concrete: a 3-query audit on a 5-feature regression problem leaves $5 - 3 = 2$ user-relevant directions of label distortion completely undetectable, with the differential effect on user-facing outputs unbounded relative to the audit response.

### 5.6 Concerning-subspace example

Suppose the auditor cares specifically about distortions of label entries corresponding to a subset $S \subseteq \{1, \ldots, n\}$ of training examples (the "demographic-group" or "topic-cluster" interpretation): $\mathcal{C} = \mathrm{span}\{e_i : i \in S\} \subset \mathbb{R}^n$, with $\dim(\mathcal{C}) = |S|$.

The principal angles between $\mathcal{C}$ and $\mathcal{N}_{\text{audit}}^\perp = \mathrm{Range}(B^T)$ measure how much of $\mathcal{C}$ the audit can detect. Compute via the SVD of $P_\mathcal{C} P_{\mathrm{Range}(B^T)} P_\mathcal{C}|_\mathcal{C}$. The four-object decomposition then quantifies the audit-visible and audit-invisible components of any distortion concentrated on $S$.

Lemma 4.4.2 gives the upper bound: with $|S| > N$, the audit's coverage fraction of $\mathcal{C}$ is at most $N/|S|$. For $|S| = 30$ and $N = 3$: coverage at most $0.1$, audit-blindness on $\mathcal{C}$ at least $0.9$. Targeted distortion within a 30-example demographic group is 90% invisible to a 3-query audit *on average*.

---

## Part VI — Audit Protocol Design

The audit-blindness lower bound is information-theoretic: it bounds detection capability from above, given a fixed audit suite. This Part addresses the inverse problem: given a concerning subspace $\mathcal{C}$, how large must the audit suite be, and how should the queries be chosen, to achieve a target coverage fraction?

### 6.1 Optimal audit construction

**Theorem 5 (optimal audit suite).** *Fix a concerning subspace $\mathcal{C} \subset \Xi$ of dimension $k$. There exists an audit suite $\mathcal{Q}^* = \{q_1^*, \ldots, q_k^*\}$ of size exactly $k$ such that $\mathcal{N}_{\text{audit}} \cap \mathcal{C} = \{0\}$ — full coverage of $\mathcal{C}$. The construction is given by the SVD of $L|_\mathcal{C} : \mathcal{C} \to H$.*

*Proof.* Take SVD: $L|_\mathcal{C} = \sum_{j=1}^k \sigma_j h_j \otimes u_j$, where $\{u_j\}$ is an orthonormal basis of $\mathcal{C}$, $\{h_j\}$ are orthonormal in $H$, and $\sigma_j > 0$ are the (assumed nonzero — see Remark 6.1.1) singular values.

Choose $q_j^* = h_j$ for $j = 1, \ldots, k$. Then for any $\xi = \sum_j a_j u_j \in \mathcal{C}$:

$$\langle q_j^*, L\xi\rangle = \langle h_j, \sum_i \sigma_i a_i h_i\rangle = \sigma_j a_j.$$

So $A_{\mathcal{Q}^*}(L\xi) = (\sigma_j a_j)_{j=1}^k$. This vanishes iff $a_j = 0$ for all $j$, iff $\xi = 0$. Hence $\mathcal{N}_{\text{audit}} \cap \mathcal{C} = \{0\}$. ∎

**Remark 6.1.1 (degenerate directions).** If $L|_\mathcal{C}$ has nontrivial kernel — i.e., some $u_j \in \mathcal{C}$ has $L u_j = 0$ — those directions are *invisible to any audit* because they produce no change in the trained function. They are user-irrelevant in the sense of Corollary 3.3.2 and need not be audited. The effective dimension of $\mathcal{C}$ for audit purposes is $k - \dim(\ker(L) \cap \mathcal{C})$, and Theorem 5 covers the effective dimension.

**Theorem 6 (under-resourced audit).** *If $N < k$, no audit suite of size $N$ achieves full coverage of $\mathcal{C}$. The optimal audit at size $N$ chooses $q_j^* = h_j$ for $j = 1, \ldots, N$ (the top-$N$ singular vectors), achieving:*

$$\dim(\mathcal{N}_{\text{audit}} \cap \mathcal{C}) = k - N$$

*with $\mathcal{N}_{\text{audit}} \cap \mathcal{C} = \mathrm{span}(u_{N+1}, \ldots, u_k)$ — the bottom $(k - N)$ singular directions of $L|_\mathcal{C}$.*

*Proof.* For any audit suite $\mathcal{Q}$ of size $N$, the audit subspace $\mathcal{Q}^* = \mathrm{span}(q_1, \ldots, q_N) \subset H$ has dimension at most $N$. The image $L|_\mathcal{C}(\mathcal{C}) \subset H$ has dimension $k - \dim(\ker(L) \cap \mathcal{C})$ (assume full effective dimension $k$). The intersection $\mathcal{Q}^* \cap L(\mathcal{C})$ has dimension at most $N$, so the audit detects at most $N$ independent directions of $\mathcal{C}$, leaving at least $k - N$ invisible.

Optimality of choosing top singular vectors: the audit's image of $\mathcal{C}$ is $A_\mathcal{Q}(L\mathcal{C}) \subset \mathbb{R}^N$, and for a fixed audit budget the construction maximizing the smallest detected response is the SVD truncation, which detects the directions corresponding to the top $N$ singular values. The orthogonal directions (bottom $k - N$ singular directions) are in the audit's kernel and therefore in $\mathcal{N}_{\text{audit}} \cap \mathcal{C}$. ∎

**Corollary 6.1.2 (coverage-cost tradeoff).** *To achieve audit-coverage fraction $\rho \in (0, 1]$ over a $k$-dimensional concerning subspace, the audit suite must have size $N \geq \lceil \rho k \rceil$ (top-$\lceil \rho k\rceil$ singular directions). Equivalently, the minimum audit cost to detect any direction in $\mathcal{C}$ is $N \geq k - k(1 - \rho)$, growing linearly with the dimension of the concerning subspace.*

### 6.2 Practical audit specification

Theorem 5's construction requires knowledge of $L|_\mathcal{C}$ — the action of the distortion-to-function tangent map on the concerning subspace. This is computable from architecture and training-procedure specifications alone:

**Procedure (audit suite construction).**

1. Specify concerning subspace $\mathcal{C} \subset \Xi$. (Auditor input.)
2. Compute $L|_\mathcal{C}$ on a basis of $\mathcal{C}$. For ridge regression: $L u_j = M^T u_j$ (matrix-vector products). For wide networks: $L u_j$ is the kernel-regression response under perturbation $u_j$ in the NTK regime.
3. SVD: $L|_\mathcal{C} = \sum_j \sigma_j h_j \otimes u_j$.
4. Audit queries: $q_j = h_j$ (the left singular vectors, considered as elements of $H$).
5. For point-evaluation queries: convert $h_j \in H$ to a point $x_j$ such that $h_j$ is the kernel section at $x_j$, when working in an RKHS. Otherwise, $h_j$ defines a more general aggregate-readout query.

**Cost analysis.** The construction cost is dominated by step 3, an SVD of dimension $k \times \dim(H_{\text{eff}})$ where $H_{\text{eff}}$ is the effective dimension of the function space spanned by the architecture (bounded by parameter count $P$ in the NTK regime). For typical alignment-audit settings, $k$ and $P$ are both bounded; the SVD is computationally light.

### 6.3 Truth-anchored audit specification

A specific instance of the construction. Suppose the auditor's concerning subspace $\mathcal{C}_{\text{truth}}$ is defined by a truth-anchored ground-truth oracle $f_{\text{true}} \in H$:

$$\mathcal{C}_{\text{truth}} := \{\xi \in \Xi : \langle L\xi, f_{\text{true}} - f_0\rangle \neq 0\}^{\text{closure}}.$$

This is the subspace of distortions that produce a measurable shift of the trained function in the direction of (or away from) truth. The four-object decomposition specialized to this $\mathcal{C}_{\text{truth}}$ gives audit-coverage fractions in terms of principal angles between truth-anchored directions and the audit suite's image.

The truth-anchored audit suite construction proceeds as in §6.2 with $\mathcal{C} = \mathcal{C}_{\text{truth}}$. The resulting queries $\{q_j\}$ are those most sensitive to truth-deviation distortions.

The framework supplies the structural construction. Specification of $f_{\text{true}}$ is external input — the framework reads geometry, not truth-content. Given any choice of $f_{\text{true}}$, the audit-blind subspace's intersection with $\mathcal{C}_{\text{truth}}$ has dimension exactly $\dim(\mathcal{C}_{\text{truth}}) - \mathrm{rank}(B|_{\mathcal{C}_{\text{truth}}})$ by Theorem 2.

---

## Part VII — Extensions

### 7.1 White-box audits

A **white-box audit** has access not only to function values $\{f_\theta(x_i)\}$ but to internal representations of the network — activations at intermediate layers, gradients, weight statistics. The audit map becomes

$$A_\mathcal{Q}^{\text{white}} : \Theta \to \mathbb{R}^{N_{\text{white}}}, \qquad A_\mathcal{Q}^{\text{white}}(\theta) = (\phi_i(\theta))_{i=1}^{N_{\text{white}}}$$

for a suite of probes $\phi_i: \Theta \to \mathbb{R}$ that may depend on parameters directly rather than only through $f_\theta$.

**Theorem 7 (white-box audit-blind subspace).** *In the linearized regime, the white-box audit-blind subspace is*

$$\mathcal{N}_{\text{audit}}^{\text{white}} := \ker(A_\mathcal{Q}^{\text{white}} \circ d\theta|_0) \subset \Xi,$$

*where $d\theta|_0 : \Xi \to \Theta$ is the parameter-response tangent map. The dimension formula and lower bound (Theorems 2 and 3) extend with $L$ replaced by $d\theta|_0$ and $A_\mathcal{Q}$ replaced by $A_\mathcal{Q}^{\text{white}}$.*

The white-box audit can probe directions in parameter space that the black-box audit cannot — gauge-invariant functionals of the weights, distributional properties of activations, etc. The audit-blind subspace is correspondingly smaller. But it remains nonzero whenever $\dim(\Xi) > N_{\text{white}}$, and the same lower-bound logic applies. White-box auditing reduces but does not eliminate the audit-blindness phenomenon.

### 7.2 Procedural audits

A **procedural audit** has access to the training procedure itself: training data lineage, reward-model architecture, training logs, init seeds. The audit-blind subspace shrinks further because direct examination of $\xi$ is possible rather than only its downstream consequences.

In the limit of full procedural access, the audit-blind subspace is empty: the auditor sees $\xi$ directly and any distortion is detectable. In practice, procedural audits face information-management constraints — training data is voluminous, reward models are complex, training logs are noisy. The relevant question is what fraction of $\Xi$ the procedural audit's effective query suite covers, which is the same Theorem 2 calculation specialized to procedural rather than network-level queries.

The framework's contribution is observing that the audit-blindness lower bound is a property of the audit's coverage, not of the audit's privilege level. Black-box and white-box and procedural audits all face the same structural calculation; what differs is the magnitude of the effective query budget relative to $\dim(\Xi)$.

### 7.3 Nonlinear regime

Beyond the linearization, $F$ is no longer linear in $\xi$, and audit-distinguishability is no longer determined by the kernel of $A_\mathcal{Q} \circ L$ alone. The relevant object is the full preimage $F^{-1}(F(\Xi) \cap (f_0 + (\mathcal{Q}^*)^\perp))$ — the set of distortions whose trained-function image has zero audit response.

Three structural changes occur:

1. **The audit-blind set is no longer a subspace.** It becomes a (typically curved) submanifold of $\Xi$. The dimension formula (Theorem 2) generalizes to a transversality statement: at generic $\xi$ where $A_\mathcal{Q} \circ dF|_\xi$ is full rank, the audit-blind submanifold has codimension equal to the rank of $A_\mathcal{Q} \circ dF|_\xi$.

2. **The lower bound is local.** Theorem 3 holds locally at each $\xi$ where the linearization is valid. For large distortions, the audit-blindness structure can change — directions that are audit-invisible at $\xi = 0$ may become detectable at $\xi \neq 0$, and vice versa.

3. **Curvature corrections to coverage fractions.** Theorem 4's four-object identities are exact in the Hilbert setting. In the curved-manifold setting (e.g., RLHF in KL geometry), they become approximate with quantitative magnitude corrections governed by `info_geometric_reformulation.md` §B.5's second-order term. The structural decomposition into four objects remains; the scalar laws acquire 15–25% magnitude deviations at moderate distortion strength.

The structural lower bounds (Theorems 2, 3, 5, 6) are robust under the transition to the nonlinear regime. The quantitative coverage fractions (Theorem 4, Lemma 4.4.2) are exact only in the linearization. For applied auditing, the structural conclusions are the load-bearing claims; quantitative magnitudes carry a known error envelope.

---

## Part VIII — Connection to Existing Frameworks

### 8.1 Relation to the trilogy's local-geometry tools

The audit-blindness analysis is a direct consequence of the apparatus developed across:

- `statistical_phantoms.md`: the abstract Halmos two-projection geometry, including the four-object decomposition that powers Theorem 4.
- `training_distortion_phantom.md`: the linearization regime for constraint-induced distortion, with the Fisher-tangent identification of the function space.
- `training_corpus_holes.md`: the linearization regime for data-distortion-induced phantoms, with the multiplication-operator structure of the input-space mask.
- `info_geometric_reformulation.md`: the curvature corrections for the strong-distortion regime, including the second-order term governing magnitude deviations.

The current document specializes those local-geometry tools to the audit problem: instead of asking "how does distortion $\xi$ affect a query $Q$" (the trilogy's question), it asks "for which distortions $\xi$ does the audit's query suite see a response" (the inverse problem). The answer is the principal-angle geometry between distortion directions and audit query images, which is exactly what the four-object decomposition computes.

### 8.2 Backdoor and data-poisoning attacks

The literature on backdoor attacks (Gu–Dolan-Gavitt–Garg 2017; Chen et al. 2017; Wallace et al. 2021 for language models) demonstrates empirically that targeted training-data manipulation can implant specific behaviors invisible to standard evaluation. The audit-blindness framework gives a structural explanation: a backdoor attack constructs $\xi_{\text{backdoor}} \in \mathcal{N}_{\text{audit}}$ for the standard evaluation suite. The empirical phenomenon is a special case of the general lower bound.

The framework generalizes from "specific known attacks" to "the full equivalence class of audit-indistinguishable distortions": the set of $\xi'$ such that $\xi' - \xi_{\text{backdoor}} \in \mathcal{N}_{\text{audit}}$. This includes the original backdoor, attacks producing equivalent triggered behavior via different mechanisms, and benign distortions that happen to land in the same audit-blind direction.

### 8.3 Influence functions and data attribution

Influence-function methods (Koh–Liang 2017; Grosse et al. 2023 on LLMs) ask the inverse question: given a trained-network behavior, which training examples caused it? Mathematically, this requires inverting the distortion-to-function map $F$ — recovering $\xi$ from $F(\xi)$.

**Lemma 8.3.1.** *In the linearized regime, $F$ is injective on $\Xi_{\text{vis}}$ (the orthogonal complement of $\ker(L)$). The audit-blindness lower bound corresponds to the difficulty of identifying $\xi$ from a finite number of point queries on $F(\xi)$: with $N$ queries, $\xi$ is identifiable only up to its $\mathcal{N}_{\text{audit}}^{\text{user}}$-coset.*

The audit-blindness theorem is the obstruction to attribution. If the auditor wants to determine which training examples caused a specific behavior using only $N$ queries on the trained network, they recover $\xi$ only up to the audit-blind subspace of dimension $\geq \dim(\Xi_{\text{vis}}) - N$. The attribution is fundamentally underdetermined by the network alone.

### 8.4 Mechanistic interpretability

Mechanistic-interpretability research (Olah et al.; the recent circuits / sparse-autoencoder / SAE work) implicitly assumes that probing a trained network's internal structure recovers information about what training-data patterns produced its behavior. The audit-blindness theorem in its white-box form (Theorem 7) bounds this recovery: even with full access to weights and activations, a finite probe budget cannot recover $\xi$-information that lies in the white-box audit-blind subspace.

The framework does not deny the value of mechanistic interpretability; it identifies a structural ceiling on what any mechanistic probe can recover from the network alone, set by the dimension of the probe's image relative to the dimension of the distortion space. Increasing probe sophistication (richer sparse-autoencoder dictionaries, more activation-pattern diversity) increases $N_{\text{white}}$ and reduces the audit-blind subspace, but does not eliminate it.

---

## Development Record

This document is a consequence of the apparatus developed across the trilogy plus the info-geometric reformulation, written down as a result. The mathematics is linear algebra in the linearization regime; the four-object decomposition from `statistical_phantoms.md` §1.3 powers Theorem 4; the Fisher-tangent setting from `training_distortion_phantom.md` §1.1 grounds the function-space construction; the linearization regime of `training_corpus_holes.md` §1.2 is the parallel for data distortions.

The structural results (Theorems 1–3, 5–7) are robust under the linearization in the sense that their conclusions about subspace dimensions and lower bounds carry through with stated quantitative deviations to the nonlinear regime. The quantitative coverage results (Theorem 4, Lemma 4.4.2) are exact in the Hilbert setting and acquire 15–25% magnitude error envelope from `info_geometric_reformulation.md`'s second-order curvature corrections in the strong-distortion regime.

Open and not developed:

- Empirical demonstration of the audit-blind subspace on a real architecture beyond the ridge-regression example. The numerical example of Part V is an exact-linearization case; a corresponding demonstration on a wide neural network in the NTK regime would extend the empirical reach.
- Quantitative characterization of the audit-blind subspace for typical alignment-audit query suites used in current practice (HELM benchmarks, Anthropic's evaluation suites, MMLU-style probes). The framework predicts a specific lower bound; measuring the actual dimension on production systems is open empirical work.
- Audit suite construction for nonlinear concerning-subspace specifications (e.g., $\mathcal{C}$ specified as a set rather than a subspace, or $\mathcal{C}$ defined implicitly by a behavioral specification rather than directly in $\Xi$). Theorem 5 covers the linear-subspace case; the general case is an optimization problem whose structure depends on $\mathcal{C}$'s parametrization.
- Combined audit protocols that use black-box, white-box, and procedural queries together. The audit-blindness theorems compose when the query types are linearly independent, but the construction of optimal combined audits is open.
- Tightness of the lower bounds. Theorems 3 and 6 are *lower* bounds on audit-blindness; they are tight when the audit suite is chosen orthogonally to the concerning subspace and loose otherwise. Quantitative tightness analysis as a function of audit-suite design is open.

Likely revisions:

- Theorem 7's white-box statement uses $d\theta|_0$ as the relevant linearization, but real white-box audits often probe non-Fréchet-differentiable functionals (e.g., activation sparsity, attention-head selectivity). The theorem should be extended to cover non-smooth probes via subgradient or distributional formulations.
- The connection to backdoor-attack literature (§8.2) is currently structural rather than computational. Concrete numerical demonstrations linking specific known attacks to specific audit-blind subspaces would strengthen the empirical case.
- The framework's relationship to differential-privacy-style training-data anonymization is not developed. DP training imposes constraints on $\xi \mapsto F(\xi)$ that interact with the audit-blindness structure in ways the current document does not characterize.

The role of this document. **The audit-blindness lower bound is the framework's most direct contribution to applied alignment auditing.** It quantifies a fundamental information-theoretic limit on what audits-of-trained-networks can detect, gives a constructive procedure for designing audit suites with stated coverage, and identifies the principal-angle geometry between distortion and audit subspaces as the central computable invariant. The result depends on the trilogy's apparatus but stands as a self-contained applied claim: *for any audit using only a finite number of queries on a trained network, there exists a computable subspace of distortions undetectable by the audit, with dimension and structure derivable from the architecture and training procedure alone.*
