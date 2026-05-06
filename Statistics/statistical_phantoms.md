# Statistical Phantoms

## Operator geometry of measurement defects in downstream inference

*Working Document — First Development Pass · April 2026*

*Companion to: Phantom Eigenmode Fabrication from Measurement Gaps; Compression–Commutator Geometry (v3); Correlation and Matched Filtering Under a Common Measurement Gap*

---

## Preface

This document extends the phantom framework from spatial measurement gaps to a broader class of inference defects that share the same operator-theoretic skeleton. The claim is that phantom phenomenology — false content at modes/coefficients/directions where the source has no energy, with the false content set entirely by the geometry of two non-commuting objects — is a property of any inference pipeline where the inference projection and the measurement projection do not commute. Spatial gaps are one realization. Omitted variables, masked covariances, time-windowed spectra, sensor-restricted modal analysis, and several others are different realizations of the same anatomy.

Status. This is a first development pass with one subsequent correction. The abstract spine (Part I) is settled in the literature on two-projection geometry; the synthesis claim — that the spine carries a phantom anatomy, the mask-adapted basis, the concentration operator, and the design rules across realizations — is the document's contribution. The realizations are developed unevenly. Regression, PCA, and matched filtering are worked through; modal analysis is sketched; cross-spectral and information-theoretic cases are flagged for development. The disconfirmer protocol (Part V) is the part most likely to need revision after the realizations are fully populated.

**Correction (round 11).** Earlier drafts called $\beta(1-\beta)$ the "universal phantom energy law" and treated it as the scalar magnitude for phantom phenomenology generically. This was a structural error: $\beta(1-\beta)$ is the **leakage** formula for one of four distinct objects (retention $\beta^2$, suppression $(1-\beta)^2$, leakage $\beta(1-\beta)$, total error $1-\beta$), each with its own scalar law and peak location in $\beta$. §1.3 has been rewritten to introduce all four; downstream sections that referenced "the energy law" have been updated to refer to the four-object decomposition or to the specific object being computed. The math in Parts II–V is mostly unaffected — the three-flavor classification, the realizations in regression/PCA/matched filtering, and the disconfirmer protocols don't depend on which specific scalar law is being invoked. What changes is the framing: the synthesis is at the level of the underlying eigensystem of $T_{P_1}(P_2)$, not at the level of a single scalar formula.

What this document is not. It is not a generalization of the multiplication-defect machinery. The locality structure of $\chi_G$ — boundary supports, finite-band envelopes, T6 — does not lift to the abstract setting and is correctly flagged as special to that case. The gain in moving abstract is unification across statistical pipelines; the loss is the engineering specificity that makes the spatial-gap case directly designable.

---

## Part I — The Abstract Spine: Two-Projection Geometry

### 1.1 Setup

Let $H$ be a separable Hilbert space and $P_1, P_2$ orthogonal projections on $H$. The pair is non-trivial if $P_1 P_2 \neq P_2 P_1$. The fundamental fact is that the relative geometry of $\mathrm{Range}(P_1)$ and $\mathrm{Range}(P_2)$ is captured by the **principal angles** $\{\theta_j\}_{j} \subset [0, \pi/2]$, defined as the arccos of the singular values of $P_2|_{\mathrm{Range}(P_1)}$, equivalently the arccos of the square roots of the eigenvalues of $P_1 P_2 P_1$ on $\mathrm{Range}(P_1)$.

### 1.2 The Halmos Five-Block Decomposition

The space $H$ admits an orthogonal decomposition into five blocks adapted to $P_1$ and $P_2$:

- $H_{11} = \mathrm{Range}(P_1) \cap \mathrm{Range}(P_2)$ — "in both"
- $H_{10} = \mathrm{Range}(P_1) \cap \mathrm{Range}(P_2)^\perp$ — "$P_1$ only"
- $H_{01} = \mathrm{Range}(P_1)^\perp \cap \mathrm{Range}(P_2)$ — "$P_2$ only"
- $H_{00} = \mathrm{Range}(P_1)^\perp \cap \mathrm{Range}(P_2)^\perp$ — "in neither"
- $H_{\mathrm{gen}}$ — the generic block where neither projection's range contains or is orthogonal to the other's

On the four trivial blocks, $P_1$ and $P_2$ commute and there is no phantom. The phantom phenomenology lives entirely on $H_{\mathrm{gen}}$. On $H_{\mathrm{gen}}$ there is a unitary $U$ and an orthonormal basis in which:

$$P_1 = U \begin{pmatrix} I & 0 \\ 0 & 0 \end{pmatrix} U^*, \qquad P_2 = U \begin{pmatrix} C^2 & CS \\ CS & S^2 \end{pmatrix} U^*,$$

with $C = \mathrm{diag}(\cos\theta_j)$, $S = \mathrm{diag}(\sin\theta_j)$, $0 < \theta_j < \pi/2$, $C^2 + S^2 = I$. This is the **canonical CS decomposition** for two projections.

### 1.3 The Compression and the Four Phantom Objects

Define the **compression of $P_2$ to $\mathrm{Range}(P_1)$**:

$$T_{P_1}(P_2) := P_1 P_2 P_1 \big|_{\mathrm{Range}(P_1)}.$$

On the generic block, $T_{P_1}(P_2) = C^2$ with eigenvalues $\beta_j = \cos^2 \theta_j \in (0, 1)$. On the trivial blocks, the eigenvalues are exactly $0$ or $1$. Let $\{u_j\}$ be the eigenbasis of $T_{P_1}(P_2)$ on $\mathrm{Range}(P_1)$, with associated canonical pairs $\{v_j\} \subset \mathrm{Range}(P_2)$ from the CS decomposition (so $P_2 u_j = \cos^2\theta_j \cdot u_j + \cos\theta_j \sin\theta_j \cdot v_j$ on the generic block).

For $f = \sum_j a_j u_j \in \mathrm{Range}(P_1)$, the geometry of $P_2 f$ relative to $\mathrm{Range}(P_1)$ produces **four scalar invariants**, each with its own norm-squared formula and its own peak location in $\beta$. Direct computation in the CS basis:

| Object | Norm-squared | Peaks at |
|---|---|---|
| **Retention** $\;P_1 P_2 P_1 f$ | $\sum_j |a_j|^2 \beta_j^2$ | $\beta = 1$ |
| **Suppression** $\;P_1 f - P_1 P_2 P_1 f$ | $\sum_j |a_j|^2 (1 - \beta_j)^2$ | $\beta = 0$ |
| **Leakage** $\;(I - P_1) P_2 f$ | $\sum_j |a_j|^2 \beta_j (1 - \beta_j)$ | $\beta = 1/2$ |
| **Total error** $\;f - P_2 f$ | $\sum_j |a_j|^2 (1 - \beta_j)$ | $\beta = 0$ |

These four are not independent. The key per-mode identity is

$$1 - \beta_j \;=\; (1 - \beta_j)^2 + \beta_j (1 - \beta_j),$$

equivalently **total error = suppression + leakage**. This is the orthogonal decomposition of $f - P_2 f$ into its $\mathrm{Range}(P_1)$ component (suppression — the part of $f$ that the measurement *removes* in the inference subspace) and its $\mathrm{Range}(P_1)^\perp$ component (leakage — the part of $P_2 f$ that *escapes* the inference subspace). Retention $P_1 P_2 P_1 f$ is what survives the pass through both projections.

**Leakage in particular** — the off-target content $w(f) = (I - P_1) P_2 f$, the part of $P_2 f$ that lies outside $\mathrm{Range}(P_1)$ — has scalar law $\sum_j |a_j|^2 \beta_j (1 - \beta_j)$, **Bernoulli variance evaluated at the cosine-squared of principal angles**. It is the same law that appears in the spatial-gap case as $a_n(1 - a_n)$ — the energy that leaked from mode $n_0$ into other modes due to the mask, computed as $\sum_{m \neq n_0} |\hat c_m|^2 = a_{n_0}(1 - a_{n_0})|c|^2$ in `common_mask_correlation` §2(3). The maximum of $\beta(1-\beta)$ at $\beta = 1/2$ corresponds to principal angle $\theta = \pi/4$ — the configuration that maximizes redistribution between the two subspaces. $\beta = 0$ (orthogonal) and $\beta = 1$ (coincident) both give zero leakage.

**Earlier drafts of this document called $\beta(1-\beta)$ "the universal phantom energy law" and treated it as the scalar magnitude for phantom phenomenology generically.** That framing was a structural error: it conflated leakage with the other three objects, each of which has its own scalar law and its own peak location. The conflation is consequential because different downstream computations are governed by different objects:

- **First-moment biases** (the regression case in §4.1, where the omitted-variable bias $\mathbb{E}[\hat\beta_o] - \beta_o$ is a deterministic shift) are governed by the **suppression** object. The bias scales as $(1 - \beta_j)$ per principal direction, peaks at orthogonality, and tends to zero as the observed and full column spaces align.
- **What survives in a measurement-aligned readout** — what one would record in a sensor-restricted experiment as "the signal that came through" — is governed by **retention** $\beta^2$, peaking at coincidence.
- **Off-target redistribution** — energy appearing at modes the source did not excite, the original "phantom" interpretation in the spatial-gap suite — is **leakage** $\beta(1-\beta)$, peaking at intermediate alignment $\theta = \pi/4$.
- **Full distance from truth to measurement** — the squared norm of $f - P_2 f$, capturing the total fidelity loss when truth is replaced by its measurement-projected version — is **total error** $1 - \beta$, peaking at orthogonality.

These four objects are jointly determined by the principal angles of the $(P_1, P_2)$ pair, but they are not the same scalar functional of those angles. The original framing of $\beta(1-\beta)$ as the universal phantom magnitude — peaking at intermediate alignment — is the leakage law specifically and is not the right scalar for retention, suppression, or total error.

The unifying observation that *does* survive: all four objects are determined by the eigensystem of $T_{P_1}(P_2)$ on $\mathrm{Range}(P_1)$. The principal-angle geometry controls phantom phenomenology; *which* phantom object — and *which* scalar law — depends on what is being computed downstream (Part III). The synthesis is at the level of the underlying eigensystem, not at the level of a single scalar formula.

[Numerical verification: the four-object identities can be checked to machine precision on random orthogonal-projection pairs by direct computation in the CS basis. A standard sanity check: generate $P_1, P_2$ with prescribed $\beta_j$, verify each scalar law and the per-mode identity $1-\beta = (1-\beta)^2 + \beta(1-\beta)$ to floating-point precision.]

### 1.4 The Mask-Adapted Basis as Canonical Correlation Basis

The eigenbasis $\{u_j\}$ of $T_{P_1}(P_2)$ on $\mathrm{Range}(P_1)$ is the **mask-adapted basis** of the inference space. Its statistical content: $\{u_j\}$ is the orthonormal basis of $\mathrm{Range}(P_1)$ for which the canonical correlations with $\mathrm{Range}(P_2)$ — the cosines of the principal angles — lie along the basis directions, with $\rho_j = \cos\theta_j = \sqrt{\beta_j}$.

Equivalently: $\{u_j\}$ is the basis in which $P_1$ and $P_2$ co-decompose into rank-one components plus block-zero remainders. Each $u_j$ pairs with a unique $v_j \in \mathrm{Range}(P_2)$ such that $\langle u_j, v_k\rangle = \cos\theta_j \, \delta_{jk}$. The pair $(u_j, v_j)$ is a **canonical pair**.

In the spatial-gap case with $P_1 = P_\lambda$ and $P_2 = \chi_G$, the mask-adapted basis is the basis of $E_\lambda$ that diagonalizes $B_\lambda = P_\lambda \chi_G P_\lambda$. The star graph result is the simplest realization: one direction has $\beta = (2/3)\rho_p$ (the principal angle is acute, the gap "sees" the mode), the orthogonal direction has $\beta = 0$ (principal angle $\pi/2$, the gap is invisible to that mode entirely).

In regression with omitted variables (§4.1), the canonical pairs are the canonical-correlation directions of Hotelling. In PCA with masked data (§4.2), they are the directions along which the principal components rotate. The mask-adapted basis is the same object across all realizations; only the interpretation of the directions changes.

### 1.5 The Concentration Operator and Recoverability

The companion compression is $T_{P_2}(P_1) = P_2 P_1 P_2$ on $\mathrm{Range}(P_2)$. Its eigenvalues are also $\{\cos^2 \theta_j\}$ (same principal angles, now read from the other side). When the spatial-gap case uses the bandwidth projector $P_N$ in place of $P_2$, the eigenvalues of $C_N = P_N \chi_G P_N$ are denoted $\mu_j$ and have a different role: they control **recoverability** rather than fabrication. An eigenvalue $\mu \to 1$ means a direction in $\mathrm{Range}(P_N)$ concentrates almost entirely inside the gap — it cannot be reconstructed from the data outside.

In the abstract setting the same dual role obtains. $T_{P_1}(P_2)$ controls how much $P_2$ leaks out of $\mathrm{Range}(P_1)$. $T_{P_2}(P_1)$ controls how much $P_1$ is invisible from inside $\mathrm{Range}(P_2)$. The eigenvalues are the same set $\{\cos^2 \theta_j\}$, but the **eigenvectors are different**: $\{u_j\}$ in $\mathrm{Range}(P_1)$ for fabrication, $\{v_j\}$ in $\mathrm{Range}(P_2)$ for visibility.

The condition number of the recovery problem $A = I - T_{P_2}(P_1)$ on $\mathrm{Range}(P_2)$ is

$$\kappa = \frac{1 - \mu_{\min}}{1 - \mu_{\max}} = \frac{\sin^2 \theta_{\max}}{\sin^2 \theta_{\min}}.$$

This is the same formula as in the spatial-gap case, expressed in principal angles.

### 1.6 What the Multiplication-Defect Realization Adds

The abstract framework gives the four-object decomposition (retention, suppression, leakage, total error), the mask-adapted basis, and the conditioning. It does not give: locality of $w(f)$ in physical space, the boundary-supported commutator $[L, P_2]$, the cosine-propagator finite-propagation argument used in T6a, the boundary-Wronskian routing law as a literal boundary integral, or the $\Gamma(\Lambda t)$ profile of $s_{G,N}$.

These are properties of $P_2 = \chi_G$ being a multiplication operator with a localized symbol relative to a differential $L$. They are flagged **[mult]** throughout the spatial-gap suite for exactly this reason. In statistical realizations where $P_2$ is the column-space projection of an observed design matrix or the time-window projection of a spectral decomposition, some [mult] results survive (windows are still multiplications) and some do not (column-space projections have no boundary).

The trade is: abstract gives unification, [mult] gives engineering. Both are needed. Neither subsumes the other.

---

## Part II — Three Flavors of Phantom

The spatial-gap framework has one flavor: a deterministic source produces deterministic false content. The statistical extension requires distinguishing three flavors that the abstract framework treats uniformly but which manifest differently downstream.

### 2.1 First-Moment Phantoms

A specific structured input produces deterministic bias. The expected output of the pipeline differs from the true value by a quantity computable from $T_{P_1}(P_2)$ alone, in proportion to the input amplitude.

In the spatial-gap case this is the dominant flavor: source $f = c\,\varphi_{n_0}$ produces phantom coefficient $\hat c_m = -K_{m,n_0} c$ at every $m \neq n_0$ where $K_{m,n_0} \neq 0$. The phantom is a deterministic function of the source amplitude and the gap geometry.

Generalization: for any pipeline computing $\mathcal{O}(f)$ that is linear in $f$, the phantom output under measurement defect $P_2$ is $\mathcal{O}((P_1 - T_{P_1}(P_2))f) - \mathcal{O}(f)$, deterministic in $f$ and in the principal-angle geometry.

Diagnostic signature: scales linearly with input amplitude, vanishes when the input is zero, persists across all realizations, present in expectation.

### 2.2 Second-Moment Phantoms

No specific input is required. The variance and covariance structure of computed quantities inherits the geometry of $T_{P_1}(P_2)$, producing systematic patterns in any thresholded analysis even when the underlying signal is null.

This is the flavor developed in the common-mask correlation document. Independent signals through the same defect have $\mathbb{E}[\widehat{\Sigma}^{(12)}] = 0$ — no first-moment phantom — but $\mathrm{Var}(\widehat{\Sigma}^{(12)}_{mn}) = T^{-1} (A\Sigma^{(1)} A^*)_{mm}(A\Sigma^{(2)} A^*)_{nn}$, with the variance shape inherited from the defect. A matched filter or threshold test sensitive to this second-moment structure flags detections preferentially at high-variance mode pairs. The detections are not signal; they are mask-shaped variance.

Diagnostic signature: present in expectation only of squared-or-higher quantities; persists when the underlying signal is permuted, time-reversed, or replaced with independent noise; survives any number of realizations because more averaging reduces amplitude, not shape.

### 2.3 Eigenstructure Phantoms

The principal directions of computed operators are rotated relative to truth by the canonical-correlation geometry between $P_1$ and $P_2$. Recovered eigenvectors, factor loadings, principal components, and modal shapes are not the true ones but the true ones rotated by the mask-adapted basis transformation.

Diagnostic signature: the recovered directions match a predicted rotation of true directions, computable from $T_{P_1}(P_2)$ before any data are observed. Equivalently: the recovered eigenstructure is a deterministic function of the true eigenstructure plus the principal-angle geometry, with the rotation independent of the data realization.

### 2.4 What Distinguishes Them

The three flavors propagate through pipelines with different scaling laws.

- First-moment phantoms scale linearly with source amplitude.
- Second-moment phantoms scale linearly with source variance (quadratically with amplitude).
- Eigenstructure phantoms scale with the principal-angle geometry directly, independent of source amplitude (they describe the basis, not a magnitude).

The flavors are not exclusive. A typical pipeline produces all three simultaneously. Regression with omitted variables produces first-moment bias in coefficients (§4.1), second-moment distortion in standard errors (§4.1), and eigenstructure rotation in principal-component regression (§4.2). The flavors are conceptually distinct because their disconfirmers are different (Part V), not because any single pipeline is purely one flavor.

The unifying observation: all three are determined by the eigensystem of $T_{P_1}(P_2)$ on the appropriate range. The first flavor (deterministic bias) is governed by the **suppression / retention** pair — what is missing in $\mathrm{Range}(P_1)$ versus what survives. The omitted-variable bias in regression (§4.1) is the suppression scalar $(1-\beta)$ in disguise, not the leakage scalar $\beta(1-\beta)$. The second flavor (variance-shape phantoms) uses the operator-theoretic structure of $T_{P_1}(P_2)$ as it propagates through products — the variance-of-squared-quantities is where the **leakage** scalar $\beta(1-\beta)$ appears most naturally, governing the off-target redistribution that earlier drafts had identified as "the universal phantom magnitude." The third flavor (eigenstructure rotations) uses the eigenvectors (the mask-adapted basis itself as the rotation), with magnitudes given by the canonical-correlation pairings $\rho_j = \cos\theta_j$.

The takeaway: principal-angle geometry controls all three flavors, but the specific scalar law depends on what is being computed. There is no single "universal energy law" that applies generically; there are four jointly-determined scalar invariants, and downstream pipelines pick out one or another of them depending on whether they are reading mean, variance, or eigenstructure outputs.

---

## Part III — The Pipeline Projection

### 3.1 What "Downstream Computed Quantity" Means

A pipeline is a map $\mathcal{O}: H \to Y$ from the data space to a domain-specific output space. Examples of $Y$: positions in $\mathbb{R}^3$ (source localization), frequencies (spectral identification), directed graphs (causal inference), labels (classification), real numbers (regression coefficients), subspaces (PCA loadings).

The clean version of a pipeline takes truth $f \in H$ and produces $\mathcal{O}(f)$. The masked version takes the projected truth $A_{P_1}(P_2) f = P_1 P_2 P_1 f$ — what survives the measurement-and-inference-projection sequence — and produces $\mathcal{O}(A_{P_1}(P_2) f)$.

The **pipeline-induced distortion** is

$$\delta_{P_1, P_2} \mathcal{O}(f) := \mathcal{O}(A_{P_1}(P_2) f) - \mathcal{O}(f).$$

For Fréchet-differentiable $\mathcal{O}$:

$$\delta_{P_1, P_2} \mathcal{O}(f) = D\mathcal{O}_f \big[ (A_{P_1}(P_2) - I) f \big] + \tfrac{1}{2} D^2\mathcal{O}_f \big[\cdot, \cdot\big] + \cdots$$

The first-order term carries first-moment phantoms. The second-order term carries second-moment phantoms when the input has variance structure. The higher-order terms generally don't matter unless $\mathcal{O}$ is highly nonlinear and the perturbation is large.

### 3.2 First-Moment Pipelines vs. Higher-Order Pipelines

A pipeline is **first-order** if its output is dominantly determined by the linear part of $\mathcal{O}$ at the relevant operating point. Linear regression coefficients are first-order in the design matrix. Phase estimates from a single Fourier mode are first-order. Mean and median estimators are first-order.

A pipeline is **higher-order** if its output depends substantively on second-moment or higher structure. Variance estimators are second-order. Coherence and matched-filter detection statistics are second-order. Eigendecomposition of sample covariance is second-order in the data and produces eigenstructure outputs. Granger causality and transfer entropy are higher-order through the cross-spectral or joint-distribution structure they consume.

The flavor of phantom that affects a pipeline is determined by the order of the pipeline. First-order pipelines are dominated by first-moment phantoms. Second-order pipelines inherit second-moment phantoms even with null input. Eigenstructure-output pipelines (PCA, modal analysis, factor models) inherit eigenstructure phantoms additionally through the rotation of recovered directions.

### 3.3 The Physical-Phantom Manifestation

The output space $Y$ supplies the physical interpretation. An operator phantom is just a number or vector in operator space; a physical phantom is what happens when that vector is interpreted in $Y$ as a real-world claim.

- Position in $Y = \mathbb{R}^3$: phantom localizations (wrong epicenter, wrong source bearing, wrong sky position).
- Frequency in $Y = \mathbb{R}_+$: phantom spectral lines (wrong line position, false detection of an emission feature).
- Direction in $Y = $ projective space: phantom direction-of-arrival, phantom flow direction.
- Subspace in $Y = $ Grassmannian: phantom modes, phantom factors, phantom principal components.
- Directed graph in $Y$: phantom causal arrows.
- Real number in $Y$: phantom regression coefficients, phantom information measures.

In each case, the same operator phantom routes through $\mathcal{O}$ into the domain's vocabulary. The framework predicts this is uniform: the operator-theoretic anatomy is the same, only the interpretive layer changes.

---

## Part IV — Statistical Realizations

### 4.1 Linear Regression with Omitted Variables

Setup. Let $X = [X_o, X_u]$ partition the full design matrix into observed columns $X_o \in \mathbb{R}^{n \times p_o}$ and unobserved columns $X_u \in \mathbb{R}^{n \times p_u}$. The full model is $y = X_o \beta_o + X_u \beta_u + \varepsilon$. The fitted model uses only $X_o$.

Projections. Let $P_X$ project onto $\mathrm{Range}(X) = \mathrm{Range}([X_o, X_u])$ in $\mathbb{R}^n$, and $P_o$ project onto $\mathrm{Range}(X_o)$. The principal angles between $\mathrm{Range}(P_X)$ and $\mathrm{Range}(P_o)$ measure how much of the full column space lies inside the observed column space versus orthogonal to it.

Identification. Set $P_1 = P_X$ (inference projection: the full column space, where the truth lives) and $P_2 = P_o$ (measurement projection: what we observe). Then $T_{P_1}(P_2) = P_X P_o P_X$ has eigenvalues $\beta_j = \cos^2 \theta_j$ where $\theta_j$ are the principal angles between full and observed column spaces.

First-moment phantom. The omitted-variable bias in the OLS estimator is

$$\mathbb{E}[\hat\beta_o] - \beta_o = (X_o^T X_o)^{-1} X_o^T X_u \beta_u.$$

This is the first-moment phantom: a coefficient $\beta_u$ on an omitted variable produces a deterministic shift in the included coefficients $\hat\beta_o$, with magnitude set by $X_o^T X_u$ (the cross-product of observed and omitted columns) — which is, up to normalization, the same coupling kernel $K$ as in the spatial-gap case.

The "phantom" appears as: $\hat\beta_o$ has expected value bounded away from $\beta_o$, with the bias entirely determined by the geometry of the column-space pair. Read as a physical claim: "$X_o$ has effect $\hat\beta_o$ on $y$," when in fact the true effect is $\beta_o$ and the apparent magnitude is partly $X_u$'s effect routed through the correlation between $X_o$ and $X_u$.

Eigenstructure phantom. Principal-component regression diagonalizes $X_o^T X_o$ and uses the leading eigenvectors as predictors. These eigenvectors are not the eigenvectors of $X^T X$ (the full design's principal components) — they are rotated by the canonical-correlation geometry between $\mathrm{Range}(P_X)$ and $\mathrm{Range}(P_o)$. The recovered "principal components" are partly the mask's signature.

Conditioning. The recovery problem $\hat\beta_o = (X_o^T X_o)^{-1} X_o^T y$ has condition number set by the eigenvalues of $T_{P_2}(P_1) = P_o P_X P_o$ on $\mathrm{Range}(X_o)$. Multicollinearity between observed and omitted variables corresponds to $\mu_{\max} \to 1$ — a coefficient direction in observed space that almost lies in the omitted space, hence almost invisible from observed data.

Mask-adapted basis. The canonical correlation directions between $X_o$ and $X_u$ are precisely the canonical pairs $(u_j, v_j)$ of the framework. Hotelling's CCA is the regression-realization version of the mask-adapted basis construction.

Diagnostic signatures.
- First-moment: bias appears even in expectation, vanishes if $\beta_u = 0$.
- Second-moment: standard errors are mis-calibrated under heteroskedasticity that varies with omitted-variable structure; sandwich estimators partially correct, but only if the omitted structure is captured in the residual covariance.
- Eigenstructure: principal components change discontinuously under inclusion/exclusion of a single relevant variable when the included subset is ill-aligned with the full subspace.

The econometrics literature has the design rules of this case under the name "instrumental variables" and "control function approaches." These are mask-adapted basis choices that re-orient the inference projection to be more aligned with the available measurement projection.

### 4.2 PCA, EOF, and Factor Analysis

Setup. Let $X \in \mathbb{R}^{n \times p}$ be the data matrix. The true sample covariance is $S = n^{-1} X^T X$ (assume centered). With masking — missing entries, missing variables, restricted observation regions — the available sample covariance is $\widetilde S$, computed only on the observed support.

Projections. Let $P_1$ project onto $\mathrm{Range}(X^T)$ in $\mathbb{R}^p$ — the column space of the data, where the principal directions live. Let $P_2$ project onto the observed-coordinate subspace (in the missing-entries case) or onto $\mathrm{Range}(X_o^T)$ (in the missing-variables case). For region-based masking (e.g., EOF analysis with a geographic mask), $P_2$ is multiplication by the spatial mask, which makes this a multiplication-defect case where T6 and the locality story partially apply.

Eigenstructure phantom. The leading eigenvectors of $\widetilde S$ are not the leading eigenvectors of $S$. They are the leading eigenvectors of a perturbation of $S$ where the perturbation is set by $P_1 P_2 P_1$. For small perturbation, the Davis–Kahan theorem bounds the rotation angle:

$$\sin\theta(\hat u_j, u_j) \leq \frac{\|S - \widetilde S\|}{\delta_j}$$

where $\delta_j$ is the gap between the $j$-th eigenvalue of $S$ and the rest of the spectrum. For perturbations that are not small, the rotation is captured exactly by the canonical correlation between $\mathrm{Range}(P_1)$ and $\mathrm{Range}(P_2)$, with the recovered eigenvectors being the projection of the true eigenvectors onto $\mathrm{Range}(P_2)$ rotated by the mask-adapted basis transformation.

The **physical phantom**: a "principal mode" recovered from EOF analysis of climate data with a regional gap is interpreted as a coherent climate pattern (an SST teleconnection, an oscillation mode, a circulation pattern) when the spatial structure of the recovered mode is partly the mask's signature.

This has a documented case. Polar gap problems in GRACE gravimetry produce apparent ice-mass-loss patterns whose spatial structure is partly the polar mask. Slepian-function methods handle this by working in the mask-adapted basis directly. Most EOF analyses do not.

First-moment phantom. If the data have a true mean structure $\mu$, the masked sample mean has $\mathbb{E}[\widetilde\mu] = P_2 \mu$, projected onto the observation subspace. Subsequent analyses that interpret $\widetilde\mu$ as the true mean inherit a deterministic bias in the directions $\mathrm{Range}(P_1) \cap \mathrm{Range}(P_2)^\perp$.

Second-moment phantom. The sample covariance estimate has variance structure set by the mask. Confidence intervals on eigenvalues, and significance tests for principal components (e.g., parallel analysis), are mis-calibrated unless the null distribution is computed under the actual mask geometry rather than under iid assumptions.

Disconfirmers.
- The recovered leading eigenvectors should match a prediction computed from the true covariance (if separately known) and the mask geometry.
- If the data are scrambled in the mask-orthogonal coordinates (preserving the mask-adapted decomposition but destroying any signal-related structure), genuine signal-derived modes should disappear; phantom modes inherited from the mask should persist.
- Cross-validation across different mask geometries (analyzing subsets of the data with different missing patterns) should produce consistent recovered modes if they are real and inconsistent recovered modes if they are mask-driven.

### 4.3 Matched Filtering and Detection

Setup. A template $t \in H$ is matched against data $\hat f = A f + n$ where $A$ is the forward operator of the measurement defect and $n$ is noise with covariance $\Sigma_n$. The optimal filter when there is no defect is $h^* = \Sigma_n^{-1} t$, producing detection statistic $\langle h^*, f\rangle$. The masked detection statistic is $\langle h^*, A f\rangle = \langle A^* h^*, f\rangle = \langle A^* \Sigma_n^{-1} t, f\rangle$.

The **effective masked template** is $A^* \Sigma_n^{-1} A t$ when the noise covariance is also estimated from masked data — i.e., when both signal and noise paths share the defect. The correlation document derives this for the common-mask case: the matched-filter response to a true signal $t$ becomes

$$T_{\mathrm{eff}}(s, t) = s^* A^* \Sigma_n^{-1} A t$$

— quadratic in the mask, as opposed to the linear $A^* h^* = A^* \Sigma_n^{-1} t$ that arises when only the signal is masked but the noise model is uncontaminated.

First-moment phantom. The matched-filter response to a known template at the wrong location/frequency/direction is shifted deterministically by the mask. Source-localization peaks move; phantom peaks appear at template arguments where the true signal is absent but the masked correlation is large.

Second-moment phantom. False-alarm rates are non-uniform across the template parameter. Under the null hypothesis (no signal present), the variance of the matched-filter statistic at template parameter $\xi$ is $\xi^* A^* \Sigma_n^{-1} A \xi$, which depends on $\xi$ through the quadratic form $A^* \Sigma_n^{-1} A$. A fixed-threshold detector flags more often at $\xi$ where this quadratic form is large.

The **physical phantom** is the most operationally consequential: a detection in a search pipeline (gravitational waves, neutrino events, exoplanet transits, anomaly detection) reported at a particular parameter value, when the apparent significance is partly the mask's variance structure inflating the local statistic.

Disconfirmers.
- Time-slides / mask-scrambling: re-run the analysis with the mask resampled to a non-overlapping configuration. Genuine detections should persist; mask-shaped phantoms should disperse.
- Template injection studies: inject known templates at known parameters and measure the recovery. Bias in recovered parameters relative to the injection diagnoses first-moment phantom; non-uniform recovery rate across parameter space diagnoses second-moment phantom.
- Cross-validation across instruments with different mask geometries: a real source should produce coherent detections at the same parameters; a mask-driven phantom should not.

The gravitational-wave community has explicit time-slide protocols that implement the second of these disconfirmers as standard practice. Most other detection pipelines do not.

### 4.4 Cross-Spectral Methods and Granger Causality (sketch)

Cross-spectral matrices, coherence functions, partial directed coherence, transfer entropy, and Granger-causality statistics are all higher-order quantities computed from joint distributions or covariance/spectral structure across multiple time series.

When the time series are obtained through different masks (different sensors with different on-times, different stations with different data availability), the principal-angle geometry between the inference projection (the true joint-distribution support) and the measurement projection (the actually-observed joint support) determines the eigenstructure of the recovered cross-spectral operators. Granger-causality statistics computed from these are eigenstructure phantoms in the directed-graph output space.

The physical phantom: a directed-graph edge from variable A to variable B is interpreted as A causing B, when it is partly the asymmetry between A's mask and B's mask appearing in the cross-spectral structure.

Development needed: the operator-theoretic spine for this case requires care because the inference projection in the joint-distribution space is high-dimensional and depends on the family of statistical models being fit. The principal-angle geometry between observed and unobserved joint supports is a real object but the framework needs to be adapted to handle the parametric model class explicitly. Flagged for further work.

### 4.5 Operational Modal Analysis (sketch)

Modal identification in structural dynamics and fluid mechanics estimates the natural modes of a physical system from response measurements at a finite set of sensors. Under sensor restrictions — some channels offline, some sensors masked, some directions unobservable — the recovered modes are eigenstructure phantoms.

The standard operational modal analysis (OMA) framework uses output-only estimation: the system is excited by ambient forces (assumed broadband) and the modes are extracted from the output covariance. The recovered modes are eigenvectors of the output covariance; under sensor restriction, these eigenvectors are projections of the true mode shapes onto the sensor subspace, rotated by the canonical correlation between the full structural-response space and the sensor subspace.

The physical phantom: a "mode" reported at frequency $f$ with shape $\phi$ is interpreted as a structural mode of the system. The shape $\phi$ is partly the sensor configuration, not the structure. Damage detection methods that flag mode-shape changes as damage indicators can produce false alarms when the sensor configuration changes between baseline and current measurement campaigns.

This case is particularly consequential because the inference projection (the full structural-response space) and the measurement projection (the sensor subspace) have well-defined geometric meanings: $P_2$ is multiplication by the sensor-indicator function, making this a multiplication-defect case where T6 partially applies. The boundary structure of the sensor configuration plays the same role as $\partial G$ in the spatial gap.

### 4.6 Information-Theoretic Quantities (sketch)

Mutual information, entropy, KL divergence, and partition functions computed from histograms of masked data inherit the mask through the empirical distribution. The empirical joint distribution $\widehat{P}$ under masking is the true joint distribution $P$ projected onto the observed-support marginal, with the projection rotating the joint distribution's structure by the mask geometry.

For information-theoretic quantities that are smooth functionals of the joint distribution, the masked estimate has a first-order Taylor expansion in the mask perturbation, with the leading correction set by the principal-angle geometry between the full and observed supports. For non-smooth functionals (the entropy of a singular distribution, hard-thresholded mutual information), the corrections do not lift directly and require case-by-case analysis.

Development needed: this case requires probability-theoretic care that the operator framework does not supply directly. The mapping from information-theoretic quantities to operator-theoretic objects runs through the Hilbert space of square-integrable functions on the distribution's support, but the relevant projections are not orthogonal in the natural metric. Flagged for further work.

---

## Part V — Disconfirmers and Diagnostic Protocols

The framework's claim is that any inference pipeline operating under structured measurement defects produces phantoms with the operator-theoretic anatomy of Part I. This claim is falsifiable: if the predicted anatomy is absent in a documented case, the framework is wrong about that case. The disconfirmers below specify what would constitute evidence against the framework, organized by phantom flavor.

### 5.1 First-Moment Disconfirmers

Prediction: a structured input produces deterministic bias in the pipeline output, with magnitude proportional to input amplitude and direction set by $T_{P_1}(P_2)$.

Disconfirmer: bias is independent of input amplitude (rules out first-moment), or bias is in directions orthogonal to the predicted ones (rules out the specific principal-angle geometry).

Protocol: input the same structured signal at multiple amplitudes; measure the bias as a function of amplitude. Linear scaling confirms first-moment phantom; sub-linear or super-linear scaling indicates higher-order effects or nonlinear pipeline behavior.

### 5.2 Second-Moment Disconfirmers

Prediction: under null input (signal replaced by independent noise of comparable variance), the pipeline output exhibits non-uniform false-alarm rates in a pattern computable from $T_{P_1}(P_2)$ alone.

Disconfirmer: false-alarm rates are uniform across the output space under null input.

Protocol: run the full pipeline on permuted/scrambled/replaced data where any genuine signal structure has been destroyed but the mask geometry is preserved. The pattern of apparent detections should match the predicted second-moment structure. Mismatch indicates either the mask geometry differs from what is modeled or the pipeline is robust against second-moment phantoms.

The gravitational-wave community's time-slide analyses are an instance of this protocol. The seismology community's randomized-event-time studies are another. Most domains do not run this protocol systematically.

### 5.3 Eigenstructure Disconfirmers

Prediction: recovered principal directions are deterministic rotations of true directions, computable from the principal-angle geometry before any data are observed.

Disconfirmer: recovered directions do not match the predicted rotation.

Protocol: characterize the true eigenstructure independently (from a different measurement modality, from physical principles, or from data with a different mask geometry) and compare the predicted rotated structure to the actually recovered structure. Match confirms the framework; mismatch indicates either an unmodeled effect or an error in the predicted geometry.

This is the most powerful disconfirmer when an independent eigenstructure characterization is available. It is unavailable in many domains where the only access to truth is through the masked measurement itself — a real limitation, not a feature.

### 5.4 Cross-Mask Consistency

Prediction: the recovered output of a pipeline depends on the mask through a known operator-theoretic mechanism. A different mask geometry should produce a different recovered output, related to the first by the difference of the two principal-angle structures.

Disconfirmer: outputs from different masks are unrelated, or related in ways that the framework cannot predict.

Protocol: analyze the same physical system with multiple distinct mask geometries (different sensor configurations, different time windows, different observation periods). Compare recovered outputs to the framework's predictions. This is the strongest available disconfirmer in domains without independent ground truth.

### 5.5 What These Protocols Do Not Disconfirm

The framework is silent on:
- Phantoms produced by nonlinear forward models that the projection structure does not capture (e.g., velocity bunching in SAR).
- Phantoms produced by model misspecification at a level prior to the mask (e.g., wrong choice of basis, wrong assumed noise distribution).
- Phantoms whose origin is in the data-generation process rather than the measurement geometry.

These are real and important sources of false content in inference pipelines. The framework distinguishes them from mask-induced phantoms and provides a positive theory only for the mask-induced class.

---

## Part VI — What Lifts and What Stays Special

### 6.1 What Lifts

The following carry from the multiplication-defect case to the abstract two-projection setting without modification:

- The four-object scalar decomposition: retention $\beta^2$, suppression $(1-\beta)^2$, leakage $\beta(1-\beta)$, total error $1-\beta$, with $\beta$ now read as cosine-squared of principal angles. The per-mode identity $1-\beta = (1-\beta)^2 + \beta(1-\beta)$ (total = suppression + leakage) is exact.
- The mask-adapted basis as the eigenbasis of $T_{P_1}(P_2)$ on $\mathrm{Range}(P_1)$, equivalent to the canonical correlation basis of CCA.
- The intra-eigenspace versus inter-eigenvalue distinction: rotations within a degenerate principal angle are basis rotation, transfer between distinct principal angles is phantom.
- The concentration operator $T_{P_2}(P_1)$ on $\mathrm{Range}(P_2)$ with eigenvalues controlling recoverability.
- The condition number formula $\kappa = (1-\mu_{\min})/(1-\mu_{\max})$ in terms of the same eigenvalues.
- The bulk/edge/projector three-part anatomy as a structural distinction; "bulk" controls $\beta$ values, "edge" controls how phantom redistributes, "projector" controls conditioning. The realization of "edge" depends on the case.
- The iterated commutator routing law $(\lambda - \mu)^k Q_{\mu\lambda} = P_\mu \mathrm{ad}_L^k(Q) P_\lambda$ in the abstract sense (with $L$ here a generic spectral generator).

### 6.2 What Stays Special to Multiplication Defects

The following do not lift; they are flagged **[mult]** and remain proper to spatial-gap (and more generally, multiplication-operator-defect) realizations:

- T6 boundary-layer localization (spatial locality of $s_{G,N}$ near $\partial G$).
- The cosine-propagator finite-propagation argument for outer decay.
- The $\Gamma(\Lambda t)$ profile for the inner boundary layer.
- The boundary Wronskian as a literal boundary integral.
- The spatial uniformity of $w_G$ outside $G$ (the exact modal lie being a uniform multiplicative copy).
- Design rules expressed in terms of physical-space gap geometry (alignment with nodal lines, gap shape and size, boundary smoothness).

These are properties of $P_2$ being a multiplication operator with localized symbol, and $L$ being a local differential operator, so that the commutator $[L, P_2]$ has localized support. Without this structure, the phantom phenomenology exists but lacks the engineering specificity that makes the spatial-gap case directly designable.

### 6.3 Open Questions

- The framework treats $P_1$ and $P_2$ as orthogonal projections. Many statistical realizations involve **oblique** projections (regression with non-orthogonal column spaces, weighted least squares). The principal-angle geometry generalizes, but each of the four scalar laws ($\beta^2$, $(1-\beta)^2$, $\beta(1-\beta)$, $1-\beta$) acquires correction terms involving the obliqueness, and the per-mode identity total = suppression + leakage may also pick up cross-terms. Worked example needed.

- The cross-spectral and Granger-causality cases (§4.4) require the inference projection to be defined relative to a parametric model class rather than a fixed Hilbert subspace. The framework's spine is intact at the operator level but the model-class structure adds dependencies that need explicit treatment.

- The information-theoretic case (§4.6) requires care about which Hilbert space the framework is operating in. Functional-analytic identities for entropy and mutual information have natural Hilbert-space realizations only for specific (Gaussian, exponential-family) cases. The mapping to general distributions needs more work.

- The framework predicts that phantom anatomy is uniform across realizations. This is testable: cases where the predicted anatomy is absent or differs would falsify the synthesis. No such case has been identified; the framework has not yet been tested against diverse-enough realizations to produce strong evidence against it.

- The relationship between this framework and the Davis–Kahan / Wedin perturbation theory is direct (eigenstructure phantoms are bounded above by Davis–Kahan in the small-perturbation regime), but a clean statement of how the framework specializes or generalizes those results is not yet written.

---

## Development Record

This is the first integrated development pass with one subsequent correction. Prior status:

- The two-projection geometry in the abstract, the CS decomposition, and the canonical-correlation realization are standard in the linear algebra and statistics literatures (Halmos 1969, Björck and Golub 1973, Hotelling 1936). What is not standard is the unification of phantom phenomenology under this geometry across statistical realizations.
- The phantom suite (multiplication-defect case) was developed in March–April 2026 with the operator-theoretic framework formalized in Compression–Commutator Geometry (v3).
- The common-mask correlation document (April 2026) extended the framework to second-moment effects in the multiplication-defect case.
- This document extends to non-multiplication-defect realizations in statistical inference pipelines.

**Round-11 correction (April 2026).** External review identified that the "universal phantom energy law" $\beta(1-\beta)$ stated in §1.3 was a structural conflation: $\beta(1-\beta)$ is the **leakage** formula for one of four distinct objects (retention $\beta^2$, suppression $(1-\beta)^2$, leakage $\beta(1-\beta)$, total error $1-\beta$), each with its own scalar law and peak location in $\beta$. The conflation is consequential because different downstream computations are governed by different objects: first-moment biases are suppression, off-target redistribution is leakage, full distance from truth to measurement is total error. §1.3 has been rewritten to introduce all four; §1.6, §2.4, §6.1, §6.3 and the Preface have been updated for consistency. The math in Parts II–V is unchanged — the three-flavor classification, the realizations in regression/PCA/matched filtering, and the disconfirmer protocols don't depend on which specific scalar law is being invoked. The synthesis claim survives but in a sharper form: principal-angle geometry controls phantom phenomenology through the eigensystem of $T_{P_1}(P_2)$, and downstream pipelines pick out one or another of four jointly-determined scalar invariants depending on what they compute. There is no single universal scalar law.

Worked through in this pass: the abstract spine (Part I), the three flavors (Part II), the pipeline-projection structure (Part III), three realizations developed carefully (regression, PCA, matched filtering — §§4.1–4.3), two realizations sketched (modal analysis, cross-spectral — §§4.4–4.5), one realization flagged for further development (information-theoretic — §4.6), and the disconfirmer protocol in Part V.

Open and not yet started:
- Worked example of an oblique-projection case to demonstrate how the four scalar laws generalize.
- Numerical companions for §§4.1–4.3 that exhibit the predicted anatomy on synthetic data.
- Development of §4.4 from sketch to full realization, with explicit model-class structure.
- Development of §4.6 with the right Hilbert-space framing.
- Integration of Davis–Kahan into Part VI as the small-perturbation specialization.

Likely revisions on second pass:
- Part II's three-flavor structure may want a fourth category for **path-dependent phantoms** — where the pipeline's iterative or sequential structure (e.g., expectation-maximization with masked data, sequential Monte Carlo with structured proposals) introduces phantoms that none of the three current flavors capture cleanly.
- Part V's protocols are written from the spatial-gap and time-slide intuitions; some realizations may have natural disconfirmers that don't fit the four currently listed.
- The "physical phantom" framing in Part III may be sharpened by distinguishing realizations where $Y$ has independent ground truth from those where it does not. The disconfirmer power differs sharply between these.

Status overall. The framework's spine is settled. The realizations are unevenly developed; the flagged-open ones are not believed to break the framework but do require work to incorporate fully. The disconfirmer protocol is the most experimental part of the document and the most likely to be revised by encountering specific cases.
