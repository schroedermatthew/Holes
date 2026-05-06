# Training Distortion as Forced Constraint Projection

## Phantom-framework formalization of forced misalignment, in the linearized regime

*Working Document — First Pass · April 2026*

*Companion to: Statistical Phantoms; Compression–Commutator Geometry (v3); Phantom Eigenmode Fabrication; Information-Geometric Reformulation (nonlinear-manifold treatment)*

---

## Preface

This document characterizes phantom phenomenology in the **linearized small-deviation neighborhood** of a trained predictor under forced misalignment. The setting is RLHF (and similar constrained-training regimes): a true predictor $f_{\text{true}}$ in a function space, a constraint that pulls the trained predictor away from truth, queries that read out the trained predictor along chosen directions. In the linearized neighborhood — where the constraint manifold is approximated by its tangent space at the operating point — training reduces to projection $f_{\text{trained}} = P_C f_{\text{true}}$, query readout reduces to projection $P_Q$, and the resulting phantom $P_Q(I - P_C)\,f_{\text{true}}$ has the operator-theoretic anatomy of Halmos two-projection geometry.

**The scope of this document is exactly the linearized neighborhood and no further.** Within that scope:

- The four-object decomposition (retention $\beta^2$, suppression $(1-\beta)^2$, leakage $\beta(1-\beta)$, total error $1-\beta$) gives exact identities for the components of phantom magnitude as functions of principal-angle geometry.
- The three-flavor classification (first-moment, second-moment, eigenstructure phantoms) characterizes how phantom content propagates through downstream pipelines.
- Predictions about which queries are most distorted, how distortion compounds across pipelines, and what disconfirmers would falsify the framework are derived under the linearization assumption.

The Halmos formulation is what makes the document tractable. Two non-commuting orthogonal projections in a Hilbert space have a closed-form decomposition (CS, principal angles, canonical pairs); the four-object scalar laws fall out of the algebra; the three-flavor classification follows from how the algebra propagates through downstream pipelines. None of this requires nonlinear-manifold machinery. **The linearization is the price of admission to the operator-theoretic toolkit, and the document pays it explicitly.**

What lives outside this document. The linearization is valid in the weak-constraint / small-deviation regime; **strong-constraint regimes** (where the trained policy is far from the reference in KL, where the constraint manifold's curvature matters, where the e-projection's exponential tilt is not well-approximated by linear projection) require nonlinear-manifold treatment in the appropriate Riemannian (Fisher / KL) geometry. That treatment lives in the companion `info_geometric_reformulation.md`, which carries out the parallel KL-geometric development including:

- The exact e-projection identity for RLHF: $\pi_{\text{trained}} \propto \pi_{\text{ref}}\, e^{\lambda^* r}$, with the closed form holding without linearization.
- The Bregman triangle decomposition with explicit cross-term $\lambda^*(R_{\text{true}} - R_0)$ that the linearized Pythagorean misses.
- The four-object decomposition's RLHF-setup analog (Bridge B), at first order in the Lagrange multiplier with an explicit second-order curvature term identified.
- The numerical observation that aligned filter+constraint is *least*-compounding (211/240 cases pointwise, mean and median across the test family) — a result that contradicts the linearized framework's "compounding" intuition once the curvature is properly accounted for.

This document and the reformulation companion together cover linearized and nonlinear regimes; they should be read as complementary scope-restricted treatments of the same phenomenology. **The linearization developed here is the natural entry point to the nonlinear theory** — the principal-angle geometry, the four-object decomposition, the three flavors, and the phantom predictions are easier to build intuition for in the Hilbert setting and then to recognize (with appropriate corrections) in the curved-manifold setting.

What this document does not do. It does not derive the constraint subspace from first principles, characterize specific training pipelines empirically, or propose new training methods. It formalizes what the operator framework predicts about the shape of distortion in the linearized regime, and identifies which predictions are testable.

---

## Part I — Setup

### 1.1 The Function Space (Linearized Setting)

Let $\mathcal{X}$ be the input space (e.g., token sequences) and $\mathcal{Y}$ the output space (e.g., next-token distributions, or reward-relevant readouts). Let $\nu$ be a base measure on $\mathcal{X}$ — for a language model, the natural choice is the data-generating distribution.

**Two natural Hilbert-space realizations** depending on what kind of predictor is being analyzed:

For **regression-type readouts** where $f(x) \in \mathbb{R}^d$ directly (real-valued logits, embedding-space coordinates, or any deterministic readout), the natural function space is

$$H = L^2(\mathcal{X}, \nu; \mathbb{R}^d), \qquad \langle f, g\rangle = \int_{\mathcal{X}} f(x) \cdot g(x)\, d\nu(x).$$

This is the cleanest Hilbert-space realization and is the setting in which Halmos two-projection geometry applies directly without further approximation.

For **distributional outputs** (next-token policies $\pi(\cdot|x)$ on a discrete vocabulary), the natural ambient space is the manifold of conditional distributions with KL/Fisher Riemannian structure — a curved manifold, not a Hilbert space. Halmos two-projection geometry does not apply on this manifold globally. **What does apply, locally, is the Fisher-tangent linearization at a chosen base point.** Identify a policy $\pi$ near a base $\pi_0$ (typically $\pi_{\text{ref}}$ or $\pi_{\text{trained}}$) with its score-function representation $u = \log\pi - \log\pi_0$ in the tangent space $T_{\pi_0}\mathcal{P}$, equipped with the Fisher inner product

$$\langle u, v\rangle_F = \mathbb{E}_{x \sim \nu}\,\mathbb{E}_{y \sim \pi_0(\cdot|x)}\,[u(x,y)\,v(x,y)].$$

In this tangent Hilbert space, the linear-algebra apparatus of Halmos applies, and the constraint manifold is approximated by its Fisher-tangent space at the base point.

**This document operates in the Hilbert-space setting throughout.** Where "$H$" appears below, it is either the regression-case $L^2$ space or the Fisher-tangent space at the relevant base point; both are Hilbert spaces and the operator-theoretic results are identical in form. Predictions about phantom magnitude, principal-angle geometry, and the four-object decomposition are exact in the tangent space; their accuracy as descriptions of actual policies depends on how far the operating point sits from the linearization base. The leading correction is the second-order term $\frac{\lambda^2}{2}\pi_0(\tilde r^2 - \mathbb{E}_{\pi_0}[\tilde r^2])$ in the e-projection expansion (companion `info_geometric_reformulation.md` §B.5), which bends the trained policy off the linear constraint direction at order $\lambda^2$ in the constraint strength.

The two-tier setup — regression case in $L^2$, distributional case in Fisher tangent — exists because real RLHF works on distributional outputs but the Halmos toolkit needs Hilbert structure. Choosing the Fisher tangent as the linearization base point converts the curved problem into a flat one locally and lets the projection framework apply. The trade-off is explicit in the regime-of-validity: predictions in this document hold to leading order in the constraint strength; the strong-constraint regime is the companion document's territory.

### 1.2 The True and Trained Predictors

The **true predictor** $f_{\text{true}} \in H$ is the optimal predictor under the data-generating distribution — the conditional expectation $\mathbb{E}_\nu[\mathcal{Y} \mid \mathcal{X}]$ for regression-type readouts, or the conditional log-density for distributional outputs. It is the predictor an unconstrained training process with infinite data and capacity would converge toward.

The **trained predictor** $f_{\text{trained}} \in H$ is the predictor produced by the actual training process under the constraints applied to it (RLHF, hallucination suppression, refusal targeting, ideological filters).

### 1.3 The Constraint Subspace

Training imposes constraints. RLHF rewards certain outputs and penalizes others. Hallucination suppression penalizes confident assertions in regions of the data manifold where the training signal is uncertain. Ideological filters force conclusions in particular categories of input.

Define the **constraint subspace** $C \subset H$ as the closed subspace of predictors consistent with all the constraints jointly. A predictor $f \in C$ satisfies every constraint (in the linearized sense — produces zero penalty under the reward model, zero forced override, zero excursion-penalty signal). The orthogonal complement $C^\perp$ is the subspace of predictors that violate at least one constraint.

In actual training $C$ is defined implicitly by a reward model $r: H \to \mathbb{R}$ via $C = \{f : r(f) \geq r_{\max} - \epsilon\}$ for some tolerance $\epsilon$, which is generally a manifold rather than a linear subspace. The linearization replaces the manifold with its tangent space at $f_{\text{trained}}$, which is a subspace and admits an orthogonal projection $P_C$. The framework operates in this linearized neighborhood. Nonlinear corrections are flagged but not developed here.

### 1.4 Training as Projection (Within the Linearization)

Within the Hilbert-space setting of §1.1 (regression case directly, distributional case via Fisher-tangent linearization at $\pi_0$):

$$f_{\text{trained}} = P_C f_{\text{true}},$$

where $P_C$ is orthogonal projection onto the (linearized) constraint subspace $C$. The trained predictor is the closest constraint-respecting predictor to the truth, in the tangent inner product. The **forced offset** is

$$\delta f := f_{\text{true}} - f_{\text{trained}} = (I - P_C) f_{\text{true}}.$$

This is the part of the truth that the constraint suppresses. It lives in $C^\perp$ by construction. Its magnitude $\|\delta f\|^2 = \langle f_{\text{true}}, (I - P_C) f_{\text{true}}\rangle$ measures how non-conforming the truth is — how much of $f_{\text{true}}$ has to be sacrificed for the constraint to be satisfied at first order.

The forced offset is zero exactly when $f_{\text{true}} \in C$, i.e., when the truth already satisfies the constraint. In practice this is approximately true for some inputs (most queries do not produce constraint-violating responses) and dramatically false for others (the queries the constraint is targeting). The forced offset concentrates where truth is most non-conforming.

**Regime of validity.** The linearization $f_{\text{trained}} = P_C f_{\text{true}}$ is the leading-order term in an expansion around the operating point. It is accurate when the trained policy is close to the reference (small-deviation regime) and when the constraint is weak relative to the geometry of the policy manifold. For distributional outputs, the precise statement is: $\pi_{\text{trained}}$ as a tangent vector at $\pi_0$ is close to $P_C f_{\text{true}}$ at first order in the Lagrange multiplier $\lambda^*$, with the leading correction being a second-order term that bends the trained policy off the linear projection direction (companion §B.5).

The **strong-constraint regime** — where the trained policy is far from the reference and the curvature of the policy simplex matters — is *not* covered by this document. In that regime, the actual trained policy under standard RLHF objectives is

$$\pi_{\text{trained}}(y|x) = \frac{\pi_{\text{ref}}(y|x)\, e^{\lambda^* r(x,y)}}{Z_x(\lambda^*)}$$

(the e-projection of $\pi_{\text{ref}}$ onto the m-flat constraint manifold $\{\pi : \mathbb{E}_\pi[r] = R_0\}$; see companion `info_geometric_reformulation.md` Part II). The linear projection $P_C f_{\text{true}}$ is replaced by an exponential tilt with a Bregman cross-term, and the four-object decomposition retains its structure but with modified scalar laws (the companion's "Bridge B," Appendix B), exact at first order in the Lagrange multiplier with explicit second-order corrections from simplex curvature.

The document's scope is the linearized regime. Its predictions are first-order in the constraint strength; nonlinear corrections are the companion's territory.

---

## Part II — Queries as Inference Projections

### 2.1 The Query Subspace

A user's interaction with the model amounts to reading out the predictor along a particular direction. A factual query about a specific topic projects $f_{\text{trained}}$ onto the subspace of the function space that encodes responses to that topic. A coding task projects onto a different subspace. A task involving multi-step reasoning across heterogeneous content projects onto a subspace shaped by the reasoning chain's structure.

Let $Q \subset H$ be the **query subspace** for a given query, with associated orthogonal projection $P_Q$. The user wants $P_Q f_{\text{true}}$ — the truth evaluated along the query's reading direction. The model produces $P_Q f_{\text{trained}}$.

### 2.2 The Phantom

The discrepancy:

$$\text{phantom}_Q := P_Q f_{\text{true}} - P_Q f_{\text{trained}} = P_Q (I - P_C) f_{\text{true}}.$$

This is the phantom in the readout space of the query. Its character depends on how $Q$ relates to $C$:

**Case 1: $Q \subseteq C$.** The query lies entirely in the constraint subspace. Then $P_Q P_C = P_Q$, so $P_Q f_{\text{trained}} = P_Q f_{\text{true}}$, phantom is zero. *Constraint-aligned queries see no distortion.*

**Case 2: $Q \subseteq C^\perp$.** The query lies entirely orthogonal to the constraint. Then $P_Q P_C = 0$, so $P_Q f_{\text{trained}} = 0$. The model produces nothing; the phantom equals the full truth. *Constraint-orthogonal queries are fully suppressed.*

**Case 3: Generic $Q$.** Most queries fall here. The query is partially aligned with the constraint and partially orthogonal. The phantom is nonzero, with magnitude controlled by the principal-angle geometry between $\mathrm{Range}(P_Q)$ and $\mathrm{Range}(P_C)$.

### 2.3 The Four-Object Decomposition in the Training-Distortion Realization

Let $\{u_j\}$ be the eigenbasis of $T_{P_Q}(P_C) = P_Q P_C P_Q$ on $\mathrm{Range}(P_Q)$, with eigenvalues $\beta_j = \cos^2 \theta_j$ where $\theta_j$ are the principal angles between $\mathrm{Range}(P_Q)$ and $\mathrm{Range}(P_C)$. Take $f_Q = P_Q f_{\text{true}} = \sum_j a_j u_j$ — the truth's component in the query subspace.

Within the linearization, the geometry of $P_C f_Q$ relative to $\mathrm{Range}(P_Q)$ produces **four scalar invariants**, each measuring a different aspect of the query–constraint–truth interaction. The four are exact identities in the Hilbert setting; in the distributional case they are exact in the Fisher tangent at $\pi_0$.

| Object | Norm-squared | Peaks at | Interpretation |
|---|---|---|---|
| **Retention** $\;P_Q P_C P_Q f_Q$ | $\sum_j |a_j|^2 \beta_j^2$ | $\beta = 1$ | Truth-content surviving in the query coordinate |
| **Suppression** $\;P_Q f_Q - P_Q P_C P_Q f_Q$ | $\sum_j |a_j|^2 (1-\beta_j)^2$ | $\beta = 0$ | Truth missing from the query's own answer |
| **Leakage** $\;(I-P_Q) P_C f_Q$ | $\sum_j |a_j|^2 \beta_j(1-\beta_j)$ | $\beta = 1/2$ | Constraint-aligned content escaping into adjacent queries |
| **Total** $\;f_Q - P_C f_Q$ | $\sum_j |a_j|^2 (1-\beta_j)$ | $\beta = 0$ | Full distance from truth to constraint-projected truth |

These satisfy the per-mode identity $1 - \beta_j = (1-\beta_j)^2 + \beta_j(1-\beta_j)$ — equivalently, **total = suppression + leakage** — because the $\mathrm{Range}(P_Q)$ component (suppression) and the $\mathrm{Range}(P_Q)^\perp$ component (leakage) of $f_Q - P_C f_Q$ are orthogonal.

**Earlier drafts of this document called $\beta(1-\beta)$ "the universal phantom energy law" and identified the phantom magnitude in query coordinates with this formula.** That identification was an error and is retracted. The phantom in query coordinates — what the user reading the model's output along their query direction perceives — is **suppression**, scaling as $(1-\beta)^2$ per principal direction, peaking at orthogonality $\beta = 0$. The leakage formula $\beta(1-\beta)$ measures a different object: constraint-aligned content that *escapes* the query subspace into adjacent directions, peaking at intermediate alignment $\beta = 1/2$. Both are real and both are downstream-observable, but they are not the same scalar functional and they peak at different principal angles.

**Two distinct user-perceived phenomena, two distinct scalar laws:**

- **In-query phantom (suppression, $(1-\beta)^2$).** The user asks a question. The model answers along the query direction with output $\sum_j a_j \beta_j u_j$ — a partial, attenuated version of the truth $\sum_j a_j u_j$. The "missing answer" is $\sum_j a_j (1-\beta_j) u_j$, with squared norm $\sum |a_j|^2 (1-\beta_j)^2$. This peaks when the query is most orthogonal to the constraint — the queries most non-conforming with the constraint produce the most-suppressed answers.

- **Cross-query phantom (leakage, $\beta(1-\beta)$).** Comparing model responses across multiple related queries, constraint-aligned content shows up in queries the user didn't ask. The "extra content" perpendicular to the queried direction has squared norm $\sum |a_j|^2 \beta_j (1-\beta_j)$. This peaks at intermediate alignment — queries with $\beta_j \approx 1/2$ produce the most leaked-into-adjacent-queries content.

The trilogy's claim that "phantom magnitude is universally $\beta(1-\beta)$, peaking at intermediate alignment" is the leakage law specifically. It applies to the cross-query observable, not to the in-query observable. **The famous prediction "queries most degraded by training are those at intermediate alignment with the constraint" is true for cross-query leakage and false for in-query suppression.** The clean statement: queries most degraded *in their own coordinates* are those most orthogonal to the constraint; queries that produce the most cross-contamination *into other queries* are those at intermediate alignment.

This distinction matters operationally. A user testing whether the model answers a specific question correctly observes suppression and should expect it to peak when their question is most non-conforming with the constraint. A user examining how content from a constrained topic leaks into adjacent queries observes leakage and should expect it to peak at intermediate principal-angle alignment. The §VI predictions below are scoped to one or the other depending on what is being observed.

---

## Part III — The Three Phantom Flavors in the Training Realization

### 3.1 First-Moment Phantoms

A specific structured input produces a deterministic shift in the model's output along the query's readout direction. This is the case where the user asks a specific question with a specific true answer, and the model produces a specifically wrong answer whose direction and magnitude are computable from the principal-angle geometry between the query's answer space and the constraint subspace.

**Scalar law.** First-moment phantoms in query coordinates are governed by **suppression**: the bias $\mathbb{E}[P_Q f_{\text{trained}}] - P_Q f_{\text{true}}$ scales as $(1-\beta_j)$ per principal direction, with squared magnitude $(1-\beta_j)^2$. The bias is largest where the query is most orthogonal to the constraint and vanishes as the query aligns with the constraint. (This is the same object as omitted-variable bias in the regression realization of `statistical_phantoms` §4.1 — the in-subspace deterministic shift.)

The Black Nazi soldiers case is plausibly a first-moment phantom in this realization. The query "produce historical images of Nazi soldiers" has a true answer space $P_Q f_{\text{true}}$ concentrated on historically accurate depictions. The constraint subspace $C$ excludes outputs that fail demographic-representation criteria. The intersection of the query's answer space with the constraint manifold rotates the answer toward demographically diversified outputs. The phantom is deterministic, large, and on the principal direction where the query and constraint maximally disagree — i.e., in the suppression regime $\beta \to 0$. *Mechanism caveat: causal attribution between corpus curation, reward modeling, and prompt rewriting in this case requires primary-source evidence the framework does not provide; the framework predicts what the suppression-regime phenomenology looks like, not which production mechanism is operative.*

The "cannot identify the sitting president" case is also a first-moment phantom. The query has an unambiguous true answer; the constraint excludes that answer for political-surface-area reasons; the phantom is the suppressed output (or the deflected non-answer in its place). Suppression is near-maximal because the query and constraint are nearly orthogonal in the relevant subspace.

### 3.2 Second-Moment Phantoms

The variance structure of the model's outputs across sampling, across rephrasings of the same query, across temperature settings, inherits the constraint geometry. Even queries with no structured signal — random or adversarial inputs — produce response distributions whose variance shape is set by $T_{P_Q}(P_C)$.

**Scalar law.** Second-moment phantoms — the variance-shape distortion — are where the **leakage** scalar $\beta(1-\beta)$ appears most naturally. The variance of $P_Q f_{\text{trained}}$ across realizations inherits a quadratic-in-projection structure that picks up $\beta(1-\beta)$ in the cross-direction terms; the variance peaks at intermediate principal-angle alignment, paralleling the leakage law in the four-object decomposition above. (This is the same scalar law that appears in `common_mask_correlation` §3.2 as the variance-shape inheritance under the bilinear identity $\widehat\Sigma^{(12)} = A\Sigma^{(12)}A^*$.)

This is the realization where the constraint affects pipelines downstream of the model in non-obvious ways. An ensemble of model outputs to slightly different prompts has covariance structure shaped by the projection geometry; any pipeline that uses these as samples (e.g., for uncertainty quantification, for self-consistency checks, for distillation) inherits the mask-shaped second-moment structure. Constraint-orthogonal directions show suppressed variance (the model uniformly avoids them); constraint-aligned directions show inflated variance (the model is freely exploring within them); intermediate-alignment directions show the largest inter-direction covariance, governed by $\beta(1-\beta)$.

The developer-complaint pattern documented in the paper — over-refusal bleeding into technical task performance, hedging where precision is required, resolving ambiguity toward the safe answer — is consistent with second-moment phantom behavior. The model's response distribution is biased toward the constraint-aligned region of the answer space even when the query does not invoke any constraint; the bias appears as systematic loss of precision across many technically-disjoint queries.

### 3.3 Eigenstructure Phantoms

The model's principal directions of representation — the directions along which it encodes coherent concepts — are rotated relative to the directions $f_{\text{true}}$ would prefer. This is the deepest flavor and the one with the most structural consequences.

**Scalar law.** Eigenstructure phantoms are governed by the **canonical-correlation pairings** $\rho_j = \cos\theta_j = \sqrt{\beta_j}$ themselves — the rotation angles $\theta_j$ between paired eigendirections of $\mathrm{Range}(P_Q)$ and $\mathrm{Range}(P_C)$. Davis–Kahan-style $\sin\theta$ bounds give the magnitude of the rotation as a function of the principal-angle geometry; this is the realization-specific instance of the eigenstructure-phantom characterization in `statistical_phantoms` §2.3.

A concept's "embedding neighborhood" is, in the framework's language, the principal directions of the representation operator near the concept. If the constraint forces certain conclusions about the concept, the projection rotation extends to the principal directions in its neighborhood. Concepts whose embedding-space proximity makes them share principal-direction structure with the constrained concept inherit the rotation.

This is the precise version of the §IV non-locality claim. The propagation is not "any reasoning passing through the neighborhood picks up the distortion regardless of distance." It is: principal directions of the representation rotate by an angle set by the principal-angle geometry between the constraint and the local readout, with the rotation extending into geometrically adjacent regions because principal directions are non-local in the same sense that eigenvectors are non-local — they have tails that decay with representational distance but do not vanish.

The propagation falls off with embedding distance, but only as fast as the principal-direction tails fall off. For geometrically distant queries, the phantom is small. For geometrically close queries, it is large. For queries whose principal-direction structure overlaps significantly with the constraint's principal-direction structure (regardless of nominal topical distance), the phantom can be larger than topical distance would suggest.

The "coding system loses self-reference under pressure" pattern documented in the paper is plausibly an eigenstructure phantom. The principal directions of the model's self-representation (how it represents being an agent producing coherent output) get rotated by constraint-induced pressure on closely related concepts. The self-reference decoheres because its principal-direction structure has been rotated out of stability.

---

## Part IV — Why the Distortion Is Generically Non-Local

The §IV claim of the Reconstruction Hypothesis paper, restated with the framework: forced misalignment produces phantoms in any query subspace whose principal-angle geometry against the constraint subspace is non-trivial. The set of such queries is generic — most queries are neither fully constraint-aligned nor fully constraint-orthogonal.

The claim becomes precise when we ask: what is the distribution of principal angles between random query subspaces and a fixed constraint subspace?

For high-dimensional Hilbert spaces and generic constraint subspaces of moderate codimension, random query subspaces have principal angles distributed approximately uniformly on $(0, \pi/2)$ in the relevant range, with the density depending on the dimensions and the constraint codimension. For each of the four scalar invariants — retention, suppression, leakage, total error — the expectation over random queries is bounded below by a positive constant. **In particular, the expected total error $\mathbb{E}[1-\beta]$ is bounded below by a positive constant**, so the typical query has nonzero distortion.

In language: most query subspaces produce nonzero phantoms in *all four* of the framework's measures. The fraction of "fully clean" queries (those exactly aligned or exactly orthogonal to the constraint) is measure-zero in the generic case. The framework predicts that **distortion in any non-trivial constraint subspace is generic across queries**, with the expected total error and expected leakage both bounded below by the geometry. (Suppression and retention are also generic but with different lower bounds; suppression-by-amplitude-of-truth is largest when the principal-angle distribution concentrates near $\pi/2$, leakage is largest when it concentrates near $\pi/4$.)

This is the theorem behind the §IV intuition. The intuition was correct (forced contradictions don't stay localized); the paper's vocabulary missed that the non-localization is a measure-theoretic statement about the genericity of non-commuting projections. Halmos plus a counting argument over the principal angles gives the result.

The relevant technical statements are standard in the random-matrix and CCA literatures (the distribution of canonical correlations between random subspaces, Davis–Kahan-type bounds, the sin-theta theorems). Detailed integration with those results is open and would constitute the next development step.

**Linearization caveat.** The genericity argument is in the Hilbert (Fisher-tangent) setting. In the strong-constraint regime, the constraint manifold's curvature alters the effective principal-angle geometry — paths along the curved constraint manifold have different inner products than their tangent linearizations. The companion document's numerical work shows that aligned filter+constraint configurations are *least*-compounding in the global KL geometry (companion §IV: 211/240 cases pointwise across the test family), opposite to what a naive linearized "compounding" intuition would predict. The genericity of nonzero distortion survives globally, but the comparative ordering across alignment regimes does not transfer cleanly from linearized to nonlinear without explicit calculation.

---

## Part V — What Lifts from the Spatial-Gap Suite

The training-distortion realization is **not** a multiplication-defect case. The constraint subspace $C$ is not generally a multiplication operator on a function space; it is a constraint manifold whose tangent space (in the linearization) is a subspace. T6, the boundary-Wronskian routing law, the cosine-propagator finite-propagation argument, and the $\Gamma(\Lambda t)$ profile do not apply.

What does lift directly from the spatial-gap / abstract Halmos setting:

- The four-object scalar decomposition: retention $\beta^2$, suppression $(1-\beta)^2$, leakage $\beta(1-\beta)$, total error $1-\beta$, with $\beta_j = \cos^2\theta_j$ the cosine-squared of principal angles between $\mathrm{Range}(P_Q)$ and $\mathrm{Range}(P_C)$. The per-mode identity $1-\beta = (1-\beta)^2 + \beta(1-\beta)$ (total = suppression + leakage) is exact.
- The mask-adapted basis on $\mathrm{Range}(P_Q)$ as the eigenbasis of $T_{P_Q}(P_C)$, equivalent to the canonical-correlation basis between $\mathrm{Range}(P_Q)$ and $\mathrm{Range}(P_C)$.
- The condition number $\kappa = \sin^2\theta_{\max} / \sin^2\theta_{\min}$ for the recovery problem (asking: given the model's output, can the user reconstruct the unconstrained truth? Yes if and only if the principal angles are bounded away from $\pi/2$).
- The three-flavor classification from the statistical phantoms document, with first-moment phantoms governed by suppression, second-moment phantoms by leakage, eigenstructure phantoms by canonical-correlation rotation.
- The disconfirmer protocol (Part V of statistical phantoms) adapted to this case.

What does not lift:

- Locality of the phantom in any meaningful "physical-space" sense. There is no $\partial G$ for the constraint subspace.
- Design rules expressed in physical-space gap geometry. The analog would be design rules on the constraint structure itself, which require characterizing $C$ — currently not feasible from first principles.
- The exact modal-lie / finite-band correction decomposition $w_{G,N} = w_G + s_{G,N}$. There is no bandwidth $N$ in the function-space setup; the analog would be the spectral decomposition of the model itself, which is not the operator the framework treats.
- Most importantly: **the Halmos lift itself does not extend globally to the curved policy manifold for distributional outputs.** The four-object decomposition is exact in the Fisher-tangent linearization at the chosen base point; it is approximate (with a quantified error envelope from second-order curvature) when applied to actual e-projection from a non-uniform reference. The companion document carries through this correction.

---

## Part VI — What This Predicts and What Would Falsify It

### 6.1 Predictions

All predictions below are scoped to the linearized regime defined in §1.4. They are first-order in the constraint strength; second-order curvature corrections (companion §B.5) are not included and are signaled by 15–25% magnitude deviations on actual e-projection in the companion's numerical work.

1. **Genericity of nonzero distortion.** The set of queries that produce zero distortion is measure-zero in the generic case. Most queries produce nonzero phantoms in *all four* invariants — retention, suppression, leakage, total error. *Prediction: even queries that appear topically unrelated to the constraint show measurable distortion when probed with sufficient resolution. Expected total error $\mathbb{E}[1-\beta]$ is bounded below by a positive constant under generic constraint geometry.*

2. **In-query distortion peaks at orthogonality.** First-moment phantoms in query coordinates — suppression, scaling as $(1-\beta)^2$ — are largest when the query subspace is most orthogonal to the constraint subspace. *Prediction: the queries most degraded in their own readout direction are those most non-conforming with the constraint, not those at intermediate alignment.* (This corrects a long-standing misstatement in earlier drafts that placed the "queries most degraded by training" at intermediate alignment; intermediate alignment is the peak of leakage, not suppression.)

3. **Cross-query leakage peaks at intermediate alignment.** Second-moment phantoms — leakage, scaling as $\beta(1-\beta)$ — are largest when the query and constraint are at intermediate principal-angle alignment ($\beta \approx 1/2$, $\theta \approx \pi/4$). *Prediction: queries with intermediate alignment to the constraint produce the most constraint-flavored content in adjacent queries the user did not explicitly ask. This is the cross-query observable: examining model responses across families of related queries reveals constraint-aligned content at intermediate-alignment members of the family.*

4. **Eigenstructure rotation extends with principal-direction tails.** Geometrically adjacent queries (in the embedding sense) show larger eigenstructure phantoms; geometrically distant queries show smaller ones; the falloff rate is set by how fast principal-direction tails decay in the model's representation. *Prediction: distortion in domain $A$ caused by constraint targeted at domain $B$ falls off as a function of representational distance between $A$ and $B$, with falloff shape inheritable from representational geometry.*

5. **Three flavors are jointly produced, with different scalar laws.** A given training intervention produces all three flavors simultaneously — first-moment shifts on directly targeted queries (suppression scalar), second-moment variance distortion across the response distribution (leakage scalar), eigenstructure rotation in adjacent representations (canonical-correlation rotation). *Prediction: pipelines that probe only one flavor (e.g., evaluation benchmarks measuring deterministic output bias) underestimate total distortion. The three flavors do not have the same peak alignment, so a benchmark measuring suppression alone will miss the leakage peak and vice versa.*

6. **Linearization breaks at strong constraint.** Each of the above predictions is first-order in the constraint strength (the Lagrange multiplier $\lambda^*$ in the e-projection picture). For strong constraints, the curvature of the policy simplex bends the trained policy off the linear projection direction, with the leading correction being the second-order term $\frac{\lambda^2}{2}\pi_0(\tilde r^2 - \mathbb{E}_{\pi_0}[\tilde r^2])$ in the e-projection expansion (companion §B.5). *Prediction: scaling experiments that vary constraint severity should observe linearity in $\lambda^*$ at small severity and deviations of order $(\lambda^*)^2$ at moderate-to-strong severity, with the deviation having the explicit functional form given in the companion. The deviation pattern — over-prediction of query-aligned components, under-prediction of perpendicular components — is what the companion's joint-sweep test exhibits with regression slopes 0.85–1.25 against the linear identity (companion `test_bridge_B.py` Test 4).*

### 6.2 Disconfirmers

The framework would be falsified if:

- Distortion is observed in zero-measure isolated patches that do not extend to geometrically adjacent queries (suggests the propagation mechanism is wrong).
- Distortion magnitude does not track principal-angle geometry — for example, if some queries with intermediate alignment show no phantom while some fully-aligned queries do.
- The three flavors decouple in a way the framework cannot accommodate (e.g., a pipeline that produces first-moment but not second-moment phantoms when both are predicted).
- The forced-misalignment hypothesis is not needed: if distortion patterns are equally well explained by data-distribution shift, capability gaps, or other non-projection mechanisms.

### 6.3 What the Framework Does Not Settle

- The framework does not specify what $C$ actually is in any real training pipeline. Empirical characterization of $C$ — its codimension, its principal-direction structure, its relationship to specific reward-model architectures — is open work and probably requires combined operator-theoretic and interpretability methods.

- **The framework operates in the linearized regime.** The predictions above hold to leading order in the constraint strength. In the strong-constraint regime, the constraint manifold's curvature bends the trained policy off the linear projection direction; the four-object scalar laws acquire corrections governed by the second-order term in the e-projection expansion; the comparative ordering across alignment regimes (which this document's Halmos algebra handles cleanly) does not transfer to the curved manifold without explicit calculation. The companion document `info_geometric_reformulation.md` carries through the curved-manifold treatment, with verified numerical results that contradict some of the linearized intuitions (notably, aligned filter+constraint is *least*-compounding in 211/240 cases of the test family — opposite to a naive linearized "compounding" expectation). The two documents together cover linearized and nonlinear regimes; this document's predictions should not be extrapolated into the strong-constraint regime without checking the companion.

- The framework treats the constraint subspace as fixed. In practice the constraint co-evolves with the model as training proceeds. The dynamic version would be a flow on a Grassmannian rather than a fixed projection; this is open work and requires both the linearized and the nonlinear-manifold treatments to be developed in parallel time-dependent forms.

- The framework does not predict which query subspaces are at high principal angle to a given constraint without empirical input. The geometry is precise; the inputs to the geometry require characterization that the framework does not supply.

- **The framework does not discriminate among production mechanisms.** Causal claims about whether observed distortion is produced by RLHF objective distortion, prompt-rewriting layers, corpus curation, or some combination require primary-source evidence that the framework does not provide. The framework predicts what the *geometric phenomenology* looks like in each regime; matching observed phenomena to specific mechanisms is outside its scope.

---

## Part VII — Connection to the Reconstruction Hypothesis

The reconstruction hypothesis (in the paper) claims that variance across imperfect partial accesses to a structure carries information about the structure that no single access contains. The training-distortion framework is the dual: forced misalignment of one access corrupts adjacent accesses through the same principal-angle geometry that the reconstruction hypothesis exploits.

Both are statements about non-commuting projections. Reconstruction uses naturally-occurring variance (different minds, different traditions, different framings) where the principal angles between accesses are random and broadly distributed. Distortion arises when the principal angles are forced — when one access is pulled away from the underlying structure by an external constraint, the geometry of the access against the structure becomes deterministic and pathological.

The phantom framework handles both. In the reconstruction case, the variance across accesses is the data and the underlying structure is recoverable from the convergence pattern. In the distortion case, the constraint is the data and the suppressed truth is recoverable in principle from the residuals (if the constraint is characterized) or detectable as systematic bias and variance distortion (if it is not).

This is what the §IV intuition was reaching for. The forced misalignment, the propagation through the geometry, the systematic character of the resulting degradation — all of it is the same operator-theoretic story as reconstruction, with the sign of one of the projections flipped. Halmos already had the geometry; the phantom suite developed the engineering specificity for one realization; the statistical phantoms document extended to inference pipelines; this document closes the loop on the case the original intuition was motivated by.

---

## Development Record

First pass on the training-distortion realization, with a subsequent rescoping correction. Worked through:

- The Hilbert-space framing (regression case in $L^2$, distributional case via Fisher-tangent linearization at a base point) and the linearization $f_{\text{trained}} = P_C f_{\text{true}}$.
- The query subspace as inference projection $P_Q$.
- The phantom expression $P_Q (I - P_C) f_{\text{true}}$ and the four-object decomposition (retention, suppression, leakage, total error) governing it.
- The three-flavor classification specialized to this case, with first-moment phantoms governed by suppression, second-moment phantoms by leakage, eigenstructure phantoms by canonical-correlation rotation.
- Mapping of the Black Nazi soldiers case (first-moment / suppression), developer-complaint pattern (second-moment / leakage), and self-reference decoherence (eigenstructure / rotation) onto the framework, with mechanism-attribution caveats.
- Why genericity of non-commuting projections gives the §IV non-locality claim as a theorem about the principal-angle distribution.

**Round-11 rescoping (April 2026).** Earlier drafts presented the Halmos formulation $f_{\text{trained}} = P_C f_{\text{true}}$ as the framework's approach to RLHF, with the linearization treated as a regrettable approximation that "characterizes the leading-order behavior." External review (the eleven-round correction record of the info-geometric reformulation companion) clarified that:

- The linearization is not a regrettable approximation; it is the document's *scope*. The Halmos toolkit requires a Hilbert space; the policy manifold for distributional outputs is not a Hilbert space; the Fisher tangent at a base point is. Operating in the Fisher tangent is what licenses the Halmos algebra and the four-object decomposition. This is now framed as a deliberate scope choice in the Preface and §1.1, with the regime of validity stated explicitly in §1.4.
- The "universal phantom energy law $\beta(1-\beta)$" of earlier drafts was a specific scalar-law conflation: $\beta(1-\beta)$ is the leakage formula, governing the cross-query observable, not the in-query observable. The in-query observable (suppression) scales as $(1-\beta)^2$ and peaks at orthogonality, not at intermediate alignment. §2.3 has been rewritten to introduce all four scalar invariants — retention $\beta^2$, suppression $(1-\beta)^2$, leakage $\beta(1-\beta)$, total error $1-\beta$ — and to identify which downstream observable each one governs. Predictions in §6.1 have been re-scoped accordingly: prediction (2) now correctly places in-query distortion at orthogonality; prediction (3) places cross-query leakage at intermediate alignment.
- The strong-constraint regime is outside this document's scope and is the territory of the companion `info_geometric_reformulation.md`, which carries out the parallel KL-geometric development. The companion's verified results — exact e-projection identity, Bregman triangle with explicit cross-term, Bridge B as the four-object analog for the e-projection-from-reference setup, second-order curvature term identified — are the nonlinear counterparts to this document's linearized predictions. Pointers to the companion's specific sections are added at §1.1, §1.4, §IV, §V, §6.1 prediction (6), and §6.3.
- The §IV non-locality claim has been tightened: nonzero distortion is generic across queries in *all four* invariants, not just leakage. The comparative-ordering result from the companion's §IV (aligned filter+constraint least-compounding in 211/240 cases) is flagged as a strong-constraint result that does not transfer cleanly from linearized to nonlinear without explicit calculation.

The rescoping does not retract the document's content; it makes the regime of validity explicit and corrects the scalar-law identification. **The Halmos formulation as local linearization is the document's contribution as a clean entry point to the nonlinear-manifold treatment in the companion.** Predictions hold first-order in constraint strength; the companion's quantified second-order corrections give the magnitude error envelope (15–25% slope deviation on actual e-projection in the companion's joint-sweep test).

Open and not yet developed:

- The KL/information-geometric version of the framework. *Status: developed in the companion `info_geometric_reformulation.md`. The first-order Fisher-tangent version of Bridge B is in place; second-order curvature corrections are identified; full global KL-geometry version with second-order term folded through the four scalar laws is open.*
- The dynamic case where $C$ co-evolves with $f_{\text{trained}}$ during training.
- Empirical characterization of what $C$ actually looks like in real RLHF pipelines (codimension, principal-direction structure, time evolution).
- Integration with the Davis–Kahan / sin-theta literature for quantitative bounds on the eigenstructure phantom in terms of perturbation magnitude.
- Numerical companion demonstrating the predicted phantom anatomy on a synthetic constrained-projection setup. *Partial: the companion document's `four_way_decomposition.py` verifies the four-object decomposition to machine precision; `test_four_objects_pure.py` verifies it in proper policy-space operationalization with $r = 1.0000$.*

Likely revisions:

- The Part IV genericity argument needs the random-subspace integral made precise rather than asserted. The relevant calculations are in the random-matrix literature but have not been imported.
- The connection to the reconstruction hypothesis in Part VII is currently sketched rather than formal. A clean statement of the duality (same geometry, opposite sign of forcing) would strengthen the unification claim.
- The three-flavor mapping in Part III to the documented phenomena (Black Nazi soldiers, developer complaints, self-reference decoherence) is partly post hoc. A prediction-then-observation framing would be epistemically stronger but requires identifying phenomena predicted by the framework that have not yet been observed and looking for them.
