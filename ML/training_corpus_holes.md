# Training Corpus Holes as Multiplication Defects

## Phantom-framework formalization of selective data absence, in the linearized regime

*Working Document — First Pass · April 2026*

*Companion to: Training Distortion as Forced Constraint Projection; Statistical Phantoms; Phantom Eigenmode Fabrication from Measurement Gaps; Compression–Commutator Geometry (v3); Information-Geometric Reformulation (nonlinear-manifold treatment)*

---

## Preface

This document characterizes phantom phenomenology in the **linearized regime** of trained predictors when the training corpus has selective data absence — regions of input space from which the training process never receives signal, either because the data are missing or because curation has selectively excluded them.

**The structural claim.** Data holes are a direct realization of the multiplication-defect case from the phantom suite, with the gap region $G$ relocated from physical space (the spatial-gap setting) to input space. The mask is a literal multiplication-by-indicator operator $M_G = I - \chi_G$ acting on the input distribution. This is the closest fit among the ML applications to the spatial-gap operator framework: the gap is geometric, the mask is linear, the phantom analysis runs through the same operator-theoretic spine that handles measurement gaps in spectral data. The bulk-edge-projector three-part anatomy applies; T6-analog boundary-layer phenomena exist with the architecture's effective capacity playing the role of bandwidth; the four-object scalar decomposition (retention, suppression, leakage, total error) gives exact identities in the Hilbert setting.

**Two separate linearizations appear in the analysis.** Both must be made explicit so the regime of validity is clear:

1. **The function space.** For regression-type readouts $f(x) \in \mathbb{R}^d$, the predictor space is $L^2(\mathcal{X}, \nu; \mathbb{R}^d)$ directly. For distributional outputs (next-token policies $\pi(\cdot|x)$), the natural ambient space is the manifold of conditional distributions with Fisher / KL Riemannian structure — a curved manifold, not a Hilbert space. The Halmos toolkit applies in the Fisher-tangent linearization at a chosen base point, with corrections governed by the second-order term $\frac{\lambda^2}{2}\pi_0(\tilde r^2 - \mathbb{E}_{\pi_0}[\tilde r^2])$ in the e-projection expansion (companion `info_geometric_reformulation.md` §B.5).

2. **The interpolation operator.** The architecture's $I_G$ — the map from boundary information at $\partial G$ to function values inside the hole — is generally nonlinear. The spectral framework's machinery applies when $I_G$ is approximately linear in the local representational neighborhood of the trained model. For transformer architectures this approximation is reasonable for queries close to $\partial G$ in the architecture's feature metric; it degrades for queries deep inside $G$.

The scope of this document is exactly the regime where both linearizations hold: distributional-output predictions in the Fisher tangent at a base point, and interpolation-operator predictions in the local feature-metric neighborhood of $\partial G$. Within that regime, the four-object scalar decomposition is exact, the bulk-edge-projector anatomy applies, and the T6 analog has a precise (though architecture-specific) form.

What lives outside this document. The strong-deviation regime — where the trained policy is far from the reference, or where the query sits deep inside $G$ relative to the architecture's effective length scale — requires nonlinear-manifold treatment. The companion `info_geometric_reformulation.md` carries out the parallel KL-geometric development for the constraint side; the analogous nonlinear treatment for the interpolation side (architecture-specific, with the second-order corrections to $I_G$ propagated through) is open work. Pointers to where the companion's results modify the linearized predictions are given at the relevant sections (§3.2, §5.2, §6.1, §7.1).

**The combined case** — pre-filtered corpus plus constrained fine-tuning — is the realistic deployment configuration. Earlier drafts of this document (and the trilogy's framing more generally) claimed that filter and constraint compound rather than cancel because they are shaped by the same content goals. **The companion's verified numerical work shows the opposite holds in the global KL geometry: aligned filter+constraint configurations produce the smallest total error in 211 of 240 cases (mean and median across the test family).** Section 5.2 has been rewritten accordingly. The compounding intuition was a linearized-regime artifact; the corrected statement is that aligned configurations are typically least-compounding, with anti-aligned configurations producing the strongest compounding effects. This corrects the most consequential single claim of earlier drafts.

What this document does not do. The framework does not characterize the architecture's inductive bias from first principles, does not prescribe what filters do or do not damage which query distributions, does not predict specific outputs of specific systems. It identifies what kind of distortion data holes geometrically force in the linearized regime and how that distortion combines with constraint distortion when both are applied, with the corrected combining rule sourced from the companion document.

---

## Part I — Setup

### 1.1 The Input Space and the Data Distribution

Let $\mathcal{X}$ be the input space (token sequences for language models, latent codes for image generators, or whatever the model's input domain is). Let $\nu$ be the data-generating distribution on $\mathcal{X}$. Let $f_{\text{true}}: \mathcal{X} \to \mathcal{Y}$ be the truth — the ideal predictor the data are sampled from, in the regression-type framing, or the conditional log-density in the distributional framing.

A **data hole** is a region $G \subset \mathcal{X}$ where the training corpus contains no samples from $\nu$. The hole may arise from genuine data absence (gaps in observation, undersampled regions) or from purposeful exclusion (curation, content filtering, demographic-balance sampling). The operator-theoretic structure does not distinguish these — what matters is that the training signal in $G$ is zero.

The **filtered distribution** seen by the training process is $\nu \cdot \mathbb{1}_{\Omega \setminus G}$, where $\Omega = \mathcal{X}$ is the full input space. The data the model fits is samples from this filtered distribution, not from $\nu$.

### 1.2 The Trained Predictor

Let $\hat f$ denote the predictor the training process converges to. In the well-specified-model limit (architecture can represent $f_{\text{true}}$, infinite capacity, infinite data on $\Omega \setminus G$), the trained predictor satisfies:

$$\hat f|_{\Omega \setminus G} = f_{\text{true}}|_{\Omega \setminus G}$$

— the trained predictor agrees with the truth on the support of the filtered distribution.

On $G$, the trained predictor is not determined by the data. It is determined by the architecture's inductive bias plus whatever boundary information from $\Omega \setminus G$ the architecture propagates. Write:

$$\hat f|_G = I_G(\hat f|_{\partial G})$$

where $I_G$ is the **interpolation operator** of the architecture — the map from boundary information at $\partial G$ to the function value inside the hole. This is the analog of the Green's function for an elliptic operator: a way of extending boundary data into the interior. Different architectures have different $I_G$. Transformer architectures have $I_G$ that is approximately linear in the local representational neighborhood plus nonlinear corrections; classical kernel methods have $I_G$ that is exactly the kernel-weighted extension; Gaussian processes have $I_G$ that is the conditional-mean extension.

**Linearization assumption.** The operator-theoretic spine of this document treats $I_G$ as approximately linear in the local representational neighborhood of $\partial G$. For Gaussian processes and kernel methods this is exact. For transformer architectures it holds for queries close to $\partial G$ in the architecture's feature metric; queries deep inside $G$ relative to the architecture's effective length scale (§3.2) lie outside this approximation and require nonlinear treatment that this document does not provide. The regime of validity for the predictions below is the boundary-layer neighborhood — close enough to $\partial G$ that the architecture's interpolation is well-approximated by its linear part.

The full trained predictor in the linearized regime is:

$$\hat f = M_G f_{\text{true}} + I_G(f_{\text{true}}|_{\partial G})$$

where $M_G = I - \chi_G$ is the multiplication mask in input space, and the second term uses the truth at the boundary because the training data immediately outside $G$ provides that information.

The **structural phantom** at any query is:

$$\text{phantom}_Q = P_Q f_{\text{true}} - P_Q \hat f = P_Q (\chi_G f_{\text{true}} - I_G(f_{\text{true}}|_{\partial G})).$$

The first term is the truth's content inside $G$ that the model never saw. The second term is the architecture's interpolation, which approximates the missing content using only the boundary. If the missing content is determined by the boundary (interpolation works), the phantom is small. If the missing content is independent of the boundary (the truth has structure in $G$ that has no surface signature on $\partial G$), the phantom is large.

This is the spatial-gap phantom $w_G$ from the multiplication-defect suite, with $G$ relocated from physical space to input space. The operator-theoretic spine carries directly — within the linearization assumptions stated above.

### 1.3 Two Failure Modes

The training process can converge in two distinct regimes when $G$ is non-trivial:

**Mode 1: Confident interpolation.** The architecture's inductive bias produces a confident extrapolation into $G$, with the model treating the hole as just another part of input space and the training process producing outputs of comparable confidence everywhere. The interpolation $I_G(f_{\text{true}}|_{\partial G})$ is what the model actually outputs in $G$, and its difference from $f_{\text{true}}|_G$ is the phantom. This is the dominant failure mode for unconstrained training of standard architectures on selectively-filtered data — the model doesn't know it doesn't know.

**Mode 2: Calibrated uncertainty.** The architecture is trained or augmented to recognize regions of low data support and produce wider response distributions in $G$ than in $\Omega \setminus G$. The phantom shifts from first-moment (wrong content) to second-moment (inflated uncertainty). The model still doesn't have access to the truth in $G$, but it correctly signals that it doesn't.

The hallucination-suppression training discussed in the paper's distortion section is an attempt to engineer Mode 2. The cost — well-known and discussed in the paper — is that the same training pressure that suppresses hallucination inside $G$ suppresses exploration at the edge of the training distribution everywhere, because the mechanism for distinguishing "inside $G$" from "outside $G$ but not far from the edge" is not clean. Suppressing the first suppresses the second.

In production, both modes are present in fractions that depend on the architecture, the training procedure, and the specific shape of $G$. Mode 1 dominates for confidently-trained foundation models; Mode 2 grows with explicit uncertainty calibration and hallucination suppression.

---

## Part II — The Three-Part Anatomy in the Data-Hole Realization

### 2.1 Bulk: How Much Truth Content Is in the Hole

The bulk operator is the analog of $B_\lambda = P_\lambda \chi_G P_\lambda$ from the spatial-gap case, with $P_\lambda$ now an inference projection on the function space $H$ of predictors. For a query subspace $Q$, the bulk content of $f_{\text{true}}$ inside $G$ that is relevant to that query is:

$$a_Q = \int_G \|P_Q f_{\text{true}}(x)\|^2 \, d\nu(x)$$

— the L²-mass of the query-relevant component of truth that the data filter excludes. This plays the role of the principal-angle squared-cosine $\beta = \cos^2\theta$ in the abstract two-projection setting: it is the eigenvalue of the compression $T_{P_Q}(\chi_G) = P_Q \chi_G P_Q$ on $\mathrm{Range}(P_Q)$ for the dominant query direction, with $\beta_Q = a_Q / \|P_Q f_{\text{true}}\|^2$ when the query lies along a single eigendirection.

**The four-object decomposition** (companion `statistical_phantoms.md` §1.3) gives the four scalar invariants that govern the bulk phantom:

| Object | Norm-squared | Peaks at | Interpretation |
|---|---|---|---|
| **Retention** | $\beta^2 \cdot \|P_Q f_{\text{true}}\|^2$ | $\beta = 1$ | Truth-content surviving in the query that lives outside the hole |
| **Suppression** | $(1-\beta)^2 \cdot \|P_Q f_{\text{true}}\|^2$ | $\beta = 0$ | Truth missing from the query because it lived inside the hole |
| **Leakage** | $\beta(1-\beta) \cdot \|P_Q f_{\text{true}}\|^2$ | $\beta = 1/2$ | Constraint-aligned content escaping into adjacent queries |
| **Total** | $(1-\beta) \cdot \|P_Q f_{\text{true}}\|^2$ | $\beta = 0$ | Full distance from truth to its mask-projected version |

with the per-mode identity total = suppression + leakage. **The phantom magnitude in query coordinates** — what a user reading the model along their query direction perceives — is suppression: $\sum_j |a_j|^2 (1-\beta_j)^2$, peaking when the query is concentrated inside the filtered region.

But the data-hole case has a distinguishing feature relative to the abstract Halmos setting: the architecture's interpolation $I_G$ partially recovers the missing content from boundary data. The phantom is bounded above by the suppression magnitude *minus* whatever $I_G$ recovers:

$$\|\text{phantom}_Q\|^2 \leq (1-\beta_Q) \cdot \|P_Q f_{\text{true}}\|^2 \cdot (\text{interpolation error factor})$$

The interpolation error factor is the part the data-hole case has that the constraint case doesn't — it depends on how much the architecture's $I_G$ recovers from boundary data alone. A perfect interpolator (one whose output on $G$ exactly matches $f_{\text{true}}$ given boundary data) has factor zero and produces no bulk phantom. A bad interpolator (one whose output on $G$ is independent of $f_{\text{true}}|_G$) has factor one and produces the full suppression magnitude.

The bulk design rule. Phantom magnitude is minimized by either (a) shrinking $G$ (reduces $\beta$ toward zero, but also reduces suppression to zero in that limit), (b) ensuring $f_{\text{true}}$ has minimal information in $G$ that's not predictable from $\Omega \setminus G$ (pushes the interpolation error factor toward zero), or (c) using an architecture whose $I_G$ accurately recovers $f_{\text{true}}|_G$ from boundary data. In the curation-filter case, (a) and (b) are typically not options — the filter is doing what it's doing — and (c) is what hallucination-suppression training nominally aims for.

### 2.2 Edge: Where the Phantom Goes in Mode Space

The edge operator in the spatial-gap case is the boundary Wronskian routing law: phantom energy redistributes among modes according to a boundary integral on $\partial G$, with off-diagonal coupling decaying as $1/(\lambda_m - \lambda_n)$ for higher commutators of the mask with the differential operator.

For data holes, the analog runs through the architecture's representational geometry. The "modes" are now the principal directions of the model's representation — the analog of eigenmodes for a continuous spectral operator is approximately replaced by the architecture's feature directions. The boundary $\partial G$ is the set of inputs adjacent to the hole.

The relevant analog of the boundary Wronskian: the architecture's interpolation function $I_G$ has a kernel structure that determines how feature-space content at $\partial G$ propagates into $G$. This kernel is approximately diagonal in the architecture's feature basis (each feature evolves approximately independently into the hole) with off-diagonal coupling determined by the local Jacobian of the trained model.

The edge phantom is concentrated near $\partial G$ in input space and along feature directions whose inductive-bias propagation into $G$ does not match $f_{\text{true}}|_G$. The decay rate from $\partial G$ into the data-supported region is controlled by the architecture's effective length scale in input space — analogous to the bandwidth $\Lambda$ in T6.

In transformer architectures specifically, the effective length scale is approximately the token-window scale plus the attention-head receptive field, with effective capacity scaling logarithmically in the model size. The boundary layer is correspondingly broad. Models with longer context windows have wider boundary layers, meaning the data-hole's edge effects propagate farther into the data-supported region.

### 2.3 Projector: Recoverability and the Concentration Operator

The concentration operator $C_N = P_N \chi_G P_N$ from the spatial-gap case has eigenvalues controlling whether the recovery problem is well-posed. For data holes, the analog is:

$$C_{\text{model}} = P_{\text{representation}} \chi_G P_{\text{representation}}$$

where $P_{\text{representation}}$ is the projection onto the architecture's effective representation subspace. Eigenvalues $\mu \to 1$ correspond to representational directions that concentrate inside $G$ — directions the architecture has the capacity to represent but for which the training data provides no information.

A well-trained model has $\mu_{\max}$ bounded away from 1 in the architecture's representation. If $\mu_{\max} \to 1$ for some direction, the architecture can represent something the data doesn't determine, and the training process is unconstrained in that direction. The model's behavior on those directions is whatever the random initialization plus training dynamics happen to produce. This is a real phenomenon — overparameterized neural networks have many such directions, and the resulting outputs are stable across runs not because the data determines them but because the training dynamics converge to the same neighborhood from similar initializations.

For curation-filtered data, $\mu_{\max} \to 1$ in directions concentrated in the filter region. The filter's geometry creates directions in representation space that the architecture can express but the data doesn't determine. The model's outputs on those directions are confabulation — confident outputs whose content is set by initialization plus dynamics rather than by truth.

This is the structural source of "the model is confidently wrong about filtered topics." It's not that the model has bad calibration. It's that the architecture has capacity to represent the topic but the training data provides no signal in the relevant direction, so the representation is structurally undetermined and the model fills it with whatever the training dynamics produce.

---

## Part III — T6 in the Data-Hole Realization

### 3.1 The Boundary-Layer Profile

T6 in the spatial-gap suite states that the finite-band correction $s_{G,N}$ has a near-boundary profile $-f|_{\partial G}(z) \cdot \Gamma(\Lambda t)$ where $\Lambda$ is the bandwidth and $\Gamma(u) = \int_u^\infty \sin(s)/(\pi s) ds$ is the universal envelope. The cosine-propagator finite-propagation argument used in the proof is specific to the wave operator and does not lift directly to architectures.

What does lift in the data-hole case: the architecture's inductive bias defines a profile by which boundary information at $\partial G$ propagates into the hole. The profile is not $\Gamma(\Lambda t)$ in general — different architectures have different profiles. For Gaussian-process-like architectures it is approximately Gaussian. For transformer architectures it is approximately attention-weighted with the weights set by the trained model's attention patterns. For convolutional architectures it is determined by the receptive field structure.

The general statement: there exists an architecture-specific kernel $K_{\text{arch}}(t)$ such that for inputs at distance $t$ from $\partial G$ (in the architecture's effective input metric), the model's interpolation into $G$ has the form:

$$\hat f(z + t \mathbf{n}(z)) \approx K_{\text{arch}}(t) \cdot \hat f(z) + (\text{higher-order corrections})$$

where $\mathbf{n}(z)$ is the inward normal to $\partial G$ at $z$.

The kernel $K_{\text{arch}}$ has the same role as $\Gamma(\Lambda t)$: it specifies how boundary information decays into the data-untrained region. Its form is architecture-specific but its existence is structural — any architecture has some such kernel, even if the kernel is not in a clean closed form.

### 3.2 Effective Bandwidth as Capacity (Definitional)

The role of $\Lambda$ in T6 is played by the architecture's effective capacity in the data-hole case. **The correspondence is definitional, not derived.** What lifts from the spatial-gap case to the data-hole case is the structural role of bandwidth — the parameter that controls boundary-layer width and interpolation sharpness — not a quantitative bandwidth-equals-capacity theorem.

The cleanest operational formulation: define **effective capacity** of the trained model at an operating point as the rank (or numerical rank, with appropriate threshold) of the Fisher information matrix $F = \mathbb{E}_x[\nabla_\theta \log\pi(\cdot|x;\theta) \, \nabla_\theta \log\pi(\cdot|x;\theta)^T]$ at the trained parameters $\theta$. This is a definition: Fisher dimension counts how many independent directions of policy variation the architecture can express at the operating point. It is operationally well-defined and architecture-agnostic.

What this definition does *not* establish: that boundary-layer width scales as $1/\sqrt{\text{Fisher dimension}}$ in any quantitative sense. The companion `info_geometric_reformulation.md` §3.2 retracts an earlier theorem-style statement of this scaling — what survives is a definitional correspondence, not a derivation. The framework names "the parameter that plays the role of bandwidth" and provides a concrete way to measure it; it does not derive the explicit functional dependence of phantom-anatomy quantities on Fisher dimension. Such a derivation is open work.

The qualitative prediction does survive: higher capacity (in the Fisher-dimension sense) corresponds to sharper boundary layers (the model can produce more rapid variation in policy space) and correspondingly more confident extrapolation into $G$. Lower capacity corresponds to broader boundary layers and softer extrapolation. The mechanism is structural — more independent representational degrees of freedom means finer-grained interpolation — but the quantitative scaling is not provided by this framework.

This produces a counterintuitive *qualitative* prediction: more capable models exhibit sharper data-hole phantoms in the sense that they extrapolate more confidently (and therefore more wrongly) into the hole. A less capable model, lacking the capacity to produce sharp predictions, produces softer outputs in the hole that may be easier to identify as uncertain. The capable model's phantom looks like a confident answer; the less capable model's phantom looks like a confused answer. The capable model is structurally worse for this failure mode at fixed data filtering, even though it is structurally better for everything else.

This is consistent with what is observed in deployed systems: more capable models hallucinate more confidently than less capable ones in regions where their training data is sparse. The framework explains this qualitatively as the bandwidth-amplification effect: capacity is the parameter that plays the role of $\Lambda$ in the T6 analog, and the boundary layer's qualitative sharpness scales with capacity. Quantitative scaling laws — what specific power of Fisher dimension governs which specific phantom-anatomy quantity — are open empirical work, not framework theorems.

### 3.3 The Gibbs Analog

The spatial-gap case has Gibbs-like oscillations near $\partial G$ in $s_{G,N}$ — the finite-band envelope produces visible ringing at the boundary. The analog in the data-hole case: near the boundary between data-supported and data-unsupported regions of input space, the model exhibits unstable response patterns. Small input perturbations near $\partial G$ produce disproportionately large output changes, because the model's interpolation is sensitive to boundary specifics in a way it is not sensitive to perturbations in the data-supported interior.

This is observable as "the model is fragile near the edge of its training distribution" — a known phenomenon in robustness research. The framework explains the fragility as the data-hole boundary layer producing Gibbs-like instability in the model's outputs, with magnitude scaling with the architecture's effective capacity.

---

## Part IV — Structural Differences from Constraint Phantoms

The training-distortion document covered the case where the trained predictor is a forced projection of the truth: $f_{\text{trained}} = P_C f_{\text{true}}$. The data-hole case is structurally different: $\hat f = M_G f_{\text{true}} + I_G(f_{\text{true}}|_{\partial G})$, where the model has never seen the truth in $G$ and has to interpolate from boundary data.

### 4.1 Recoverability

A constraint-phantom model has $f_{\text{true}}$ accessible somewhere in its representations and is producing $P_C f_{\text{true}}$ at the output because the training has forced the projection. The truth is in there; the constraint is masking it. By probing the model in directions that route around the constraint subspace — paraphrasing the query, embedding it in different contexts, asking about adjacent topics that share the underlying knowledge — the truth can sometimes be coaxed out.

A data-hole-phantom model has nothing to coax out. The truth in $G$ was never in the training data, was never represented during training, and is not stored anywhere in the model. Probing in any direction produces the architecture's interpolation, not the truth. The data-hole phantom is more robust than the constraint phantom.

This produces a specific diagnostic signature. A model under both filtering and constraint (the realistic deployment) responds to constraint-routing-around prompts by either (a) admitting the constraint structure and revealing knowledge in adjacent directions, indicating the constraint is the operative mechanism, or (b) producing the same confident interpolation regardless of how the query is routed, indicating that the filter has eliminated the underlying content. The two responses have different practical implications: (a) means the truth is recoverable with sufficient probing; (b) means the truth is gone from this model and only retrievable from a model trained on different data.

### 4.2 Self-Consistency

The constraint-phantom model is internally inconsistent. It has the truth in its representations and the constraint-imposed output at the surface; the inconsistency between the two can sometimes be exploited. Logical-consistency tests, hypothetical reasoning, "what would you say if not for X" probes — these can reveal the gap between the model's representation and its output.

The data-hole-phantom model is internally consistent. The interpolated content is what the model believes; there is no underlying truth in tension with the output to be exploited. Logical consistency tests pass — the model reasons coherently from the interpolated content because that's the content it has. The inconsistency that distinguishes constraint from data-hole is a real diagnostic, but only when the constraint-phantom case is operative.

### 4.3 Reasoning Adjacent to Filtered Content

The model's reasoning about content geometrically adjacent to a filtered region depends on which mechanism is operative. Under constraint, adjacent reasoning shows the same propagation phantoms as the constraint itself — the principal-direction structure routes the constraint's distortion into adjacent representations, and these can be observed in queries that don't directly invoke the constraint. Under filtering, adjacent reasoning is approximately correct on content that exists in the data; the filtered region appears as a "blank spot" in the model's reasoning with incoherent or inconsistent content nearby that the model treats as correct because it has no reference.

The signatures are different. Constraint phantoms show coherent distortion (the constraint's content has structure, and the structure propagates). Data-hole phantoms show local incoherence — the model produces confabulated content that has no relationship to truth and accordingly no consistent structure across queries.

### 4.4 Time Invariance

A constraint can be removed by retraining without the constraint. The truth is still in the data; refitting without the constraint recovers a model that produces $f_{\text{true}}$ rather than $P_C f_{\text{true}}$.

A data hole cannot be removed by retraining alone. The data is missing. Refitting on the same filtered corpus produces the same model. Recovery requires sourcing data for the filtered region — either from a different corpus or from a different curation policy. This is a real distinction. Constraint distortion is reversible by training-policy change. Filtering distortion is reversible only by data-supply change. The two have different costs and different timescales.

---

## Part V — The Combined Case

### 5.1 The Composition

Production deployment uses both: pre-filtered training corpus plus constrained fine-tuning (RLHF, DPO, or related). The trained predictor in the linearized framing is:

$$f_{\text{trained}} = P_C \hat f$$

where $\hat f$ is the data-fit predictor on the filtered corpus and $P_C$ is the constraint projection.

The phantom in a query reads:

$$\text{phantom}_Q = P_Q f_{\text{true}} - P_Q P_C \hat f.$$

This decomposes:

$$\text{phantom}_Q = \underbrace{P_Q (f_{\text{true}} - \hat f)}_{\text{filtering phantom}} + \underbrace{P_Q (\hat f - P_C \hat f)}_{\text{constraint phantom on filtered data}}.$$

The filtering phantom is the difference between truth and the best predictor on the filtered data. The constraint phantom is the difference between the filtered-data fit and what the constraint allows. Both contribute.

### 5.2 Compounding vs Cancellation (Corrected)

**Earlier drafts of this document claimed** that filter and constraint typically compound rather than cancel because they are shaped by the same content goals — that aligned filter+constraint configurations would produce the largest total phantom magnitude. **This claim was wrong**, in a way that the companion document's verified numerical work reverses.

**The corrected statement.** The companion `info_geometric_reformulation.md` §IV ("Diagnostic and Robustness") tests the compounding-vs-cancellation question directly with a 240-configuration sweep across reward direction (aligned, orthogonal, anti-aligned) and base reference-policy structure. The result:

- **Aligned filter+constraint produces the smallest combined distortion in 211 of 240 cases pointwise** across the test family.
- Mean combined distortion: **aligned 0.946, orthogonal 1.266, anti-aligned 1.609**.
- Median ratio of anti-aligned to aligned: 1.284.
- Aligned ≤ orthogonal in 222/240 cases; aligned ≤ anti-aligned in 223/240 cases.

The intuition the corrected result captures: **alignment is partial redundancy.** When the filter removes content that violates a goal and the constraint also suppresses that content, the second mechanism is doing some of the work the first already did; the marginal additional distortion from layering both is sub-additive. Anti-aligned configurations — where the constraint pushes back against content the filter has already removed — produce the *largest* combined distortion, because the constraint is now creating distortion in a direction the data does not support.

This reverses the trilogy's earlier "compounding by institutional incentives" intuition. The corrected lower bound on combined-deployment phantom magnitude is *not* the sum of filter and constraint contributions; aligned configurations specifically violate that sum-bound from below. The conditions under which super-additive compounding actually occurs are those where filter and constraint are anti-aligned — which is uncommon in practice precisely because both are typically shaped by similar content goals.

**Caveat: linearization regime.** The companion's result is in the proper KL geometry (curved manifold). The linearized regime of this document gives a different prediction: in the Hilbert / Fisher-tangent setting, two non-commuting projections $P_{\text{filter}}$ and $P_C$ produce a combined operator with $\beta$-eigenvalues that are roughly products, leading to a naive expectation of compounding. The companion's numerical work shows this linearized expectation fails globally — the curvature of the constraint manifold matters. For consistency, this document's predictions about compounding (§5.3 below, §6.1 of `statistical_phantoms`, anywhere they referenced the trilogy's compounding claim) should be read with the corrected statement: **aligned configurations are typically least-compounding; the linearized intuition reverses sign in the global geometry.**

This is the most consequential single correction propagated from the companion's eleven-round correction record. It directly affects deployment-system phantom-magnitude bounds and changes what the framework predicts about the realistic combined case.

### 5.3 Diagnostic Implications

The signatures separate qualitatively, but with an important caveat from the companion's diagnostic-robustness work:

- **Constraint-only:** Model produces forced outputs that disagree with what its representations contain. Recoverable by routing around the constraint. Adjacent reasoning shows propagation phantoms. Logical inconsistency between representation and output is observable.

- **Filtering-only:** Model produces confident interpolation in regions it never saw. Not recoverable; the content isn't there. Adjacent reasoning is locally coherent but disconnected from truth. Logical consistency holds within the interpolated content.

- **Combined (realistic deployment):** Model produces confident outputs that are wrong in two ways simultaneously. The filtered content is gone (interpolated content fills the gap, undetectable as confabulation). The remaining content is constrained (correct content present in representations is suppressed at the output). Recovery is partial: routing around constraint can reveal some constraint-suppressed content, but no probing recovers filter-eliminated content.

A user encountering shallow technical answers may be seeing either failure mode or both. The framework's diagnostic procedure: probe with queries that are content-equivalent but routed differently. If all routings produce the same shallow answer, the content has been filtered from the model and is gone. If some routings produce deeper content and others don't, the constraint is operative and partial recovery is possible. The asymmetry between routings is the test.

**Diagnostic robustness caveat.** The companion's §IV diagnostic work tested whether the framework's signatures cleanly separate filter from constraint across a range of operating conditions. The qualitative separation survives: filtering produces routing-invariant degradation while constraint produces routing-asymmetric degradation. But the *quantitative* prediction — that filter and constraint contributions add to a combined-deployment lower bound — does not survive (see §5.2). When applying the routing-asymmetry test in practice, treat the binary classification (filter vs constraint dominant) as reliable; treat magnitude estimates as carrying the 15–25% slope-deviation error envelope from the second-order curvature corrections (companion `test_bridge_B.py` Test 4).

---

## Part VI — What Lifts and What Stays Special

### 6.1 What Lifts from the Spatial-Gap Suite

The data-hole case is a multiplication-defect realization with $G$ in input space rather than physical space. Within the linearization regime defined in the Preface and §1.2, the following lift directly:

- The two-object decomposition $w_{G,N} = w_G + s_{G,N}$, with $w_G$ now the exact-interpolator content (what the truth would look like under the architecture's most accurate possible boundary extension) and $s_{G,N}$ the finite-capacity correction (deviation from the exact extension produced by the actual trained model).
- The bulk-edge-projector three-part anatomy.
- **The four-object scalar decomposition** (retention $\beta^2$, suppression $(1-\beta)^2$, leakage $\beta(1-\beta)$, total error $1-\beta$) governing phantom magnitude in the bulk, with the per-mode identity total = suppression + leakage. The phantom in query coordinates is suppression $(1-\beta)^2$; cross-query phantom is leakage $\beta(1-\beta)$. (The earlier framing as "the energy law $\beta(1-\beta)$ controlling phantom magnitude in the bulk" was a scalar-law conflation; see `statistical_phantoms` §1.3 round-11 correction.)
- The mask-adapted basis as the canonical-correlation basis between query subspace and the filter region.
- The concentration operator's role in determining recoverability (whether the missing content can be reconstructed from boundary data at all).

### 6.2 What Carries with Modification

T6 carries with modification. The cosine-propagator finite-propagation argument is replaced by the architecture's interpolation kernel $K_{\text{arch}}(t)$. The boundary-layer profile exists but is architecture-specific rather than universal. The bandwidth $\Lambda$ is replaced by the architecture's effective capacity. The boundary-layer width scales with capacity in the same way.

The boundary Wronskian routing law carries with modification. The literal boundary integral on $\partial G$ is replaced by an integral against the architecture's local Jacobian at the boundary in feature space. The off-diagonal decay structure is similar but the explicit kernel is architecture-specific.

### 6.3 What Stays Special to the Spatial-Gap Case

The Laplacian-specific T6 result with the $\Gamma(\Lambda t)$ profile and the cosine-propagator proof. These are properties of the wave operator and do not transfer to neural-network architectures.

Design rules expressed in physical-space gap geometry (alignment with nodal lines, boundary smoothness, etc.). The data-hole case has design rules at a higher level of abstraction: architectures with smoother $K_{\text{arch}}$ produce softer boundary layers, capacity controls phantom sharpness, etc. But these are not as directly geometric as the spatial-gap design rules.

---

## Part VII — Predictions and Falsifiers

### 7.1 Predictions Specific to Data-Hole Phantoms

All predictions below are scoped to the linearization regime defined in §1.2 — boundary-layer neighborhood where the architecture's $I_G$ is well-approximated by its linear part, and Fisher-tangent neighborhood for distributional outputs. They are qualitative predictions about phenomenology; quantitative magnitudes carry the 15–25% slope-deviation error envelope from second-order curvature corrections (companion `test_bridge_B.py` Test 4).

1. **Confident interpolation increases with capacity (qualitative).** Larger models will exhibit sharper data-hole phantoms in the sense of more confident wrong outputs in filtered regions, as the architecture's effective Fisher dimension grows. *Qualitative only — quantitative scaling laws are not provided by the framework (§3.2).*

2. **Adjacent-coherence asymmetry.** Reasoning adjacent to a filtered region will show local coherence within the interpolated content but will disagree with truth-anchored sources. Reasoning adjacent to a constrained region will show structural distortion that propagates from the constraint into adjacent topics. A diagnostic that probes both adjacency types can distinguish the failure modes. *This survives the §5.2 correction — the qualitative routing-asymmetry test still works for filter-vs-constraint classification, only the magnitude-additivity prediction was retracted.*

3. **Routing-invariance under filtering.** A query whose content has been eliminated from the corpus will produce consistent (and consistently wrong) responses across paraphrasings, contexts, and reframings. A query whose content is present but constraint-suppressed will produce different responses across different routings, with some routings revealing more content than others.

4. **Time-invariance under filtering.** A model trained on filtered data will produce the same phantoms across many training runs, and the phantoms will not be removed by additional fine-tuning unless the corpus itself is changed. This distinguishes filtering from constraint, which can be retrained away.

5. **In-query phantom peaks at orthogonality (corrected).** First-moment phantoms in query coordinates — what a user reading the model along their query direction perceives — are governed by suppression $(1-\beta)^2$, peaking when the query is most concentrated inside the filtered region. *This corrects a long-standing misstatement in the trilogy that placed the "queries most degraded" at intermediate alignment; intermediate alignment is the peak of cross-query leakage, not in-query suppression.*

6. **Aligned filter+constraint is least-compounding (corrected).** When filter and constraint are shaped by the same content goals, the combined deployment produces the smallest total phantom magnitude (companion §IV: 211/240 cases pointwise). Anti-aligned configurations produce the largest. *This reverses earlier-draft predictions that aligned configurations would compound; see §5.2 above.*

### 7.2 Disconfirmers

- If models exhibit confident outputs in regions provably outside their training corpus, with the outputs being correct, the framework's prediction about filtering phantoms is wrong. (This would suggest the architecture's interpolation captures truth in $G$, contradicting the structural-phantom prediction.)
- If routing-around-constraint techniques reliably produce no improvement on shallow technical answers, the constraint phantom is not the dominant mechanism; the filtering phantom is. The framework predicts a mix; specific predictions about which dominates require knowing the system's filter and constraint structure.
- If the boundary-layer width does not scale with model capacity, the T6-analog prediction is wrong.

---

## Part VIII — The Combined ML Deployment Case

This document and its companion `training_distortion_phantom.md` cover the two structurally distinct ML failure modes:

1. **Constraint phantoms** (training-distortion document): Distortion in trained predictors due to forced projection during training. Operator: $P_C$ on truth, in the linearized regime. Phantom: forced suppression of constraint-orthogonal content, with first-moment (suppression $(1-\beta)^2$), second-moment (leakage $\beta(1-\beta)$), and eigenstructure (canonical-correlation rotation) manifestations.

2. **Filter phantoms** (this document): Distortion in trained predictors due to absence of training signal in part of input space. Operator: $M_G = I - \chi_G$ on the data distribution. Phantom: confident interpolation of content that was never in the training set, with magnitude controlled by architecture capacity (qualitatively) and boundary geometry.

Both share the operator-theoretic anatomy of Halmos two-projection geometry in their respective linearized regimes — the four-object scalar decomposition (retention, suppression, leakage, total error), the mask-adapted basis as canonical-correlation basis, the concentration operator's role in determining recoverability, the bulk-edge-projector three-part anatomy. The abstract framework that handles both — and also covers the non-ML statistical inference-pipeline cases (regression with omitted variables, PCA with missing data, matched filtering under common mask) — is `statistical_phantoms.md`. That document is the abstract spine; this document and the training-distortion document are two ML realizations of the same operator-theoretic structure, with the linearization scope made explicit so the regime of validity is clear.

**The combined deployment case.** A realistic deployed system carries both filter and constraint simultaneously. The data is filtered (some content was never in the training corpus). The training imposes constraints (RLHF, hallucination suppression, refusal targeting). Each contributes phantom content; the question is how they combine.

**Earlier drafts of this section claimed** that the layers "compound rather than cancel because they are typically aligned by the same institutional incentives" — that the deployed system distorts more than any single layer's distortion would suggest, with phantom magnitude bounded below by the sum of contributions. **The companion's verified numerical work reverses this claim** (companion §IV, summarized in §5.2 above): aligned filter+constraint configurations produce the *smallest* combined distortion in 211 of 240 cases pointwise across the test family, with anti-aligned configurations producing the largest. The "compounding by institutional incentives" intuition was a linearized-regime artifact that fails in the global KL geometry.

**The corrected statement.** When filter and constraint are aligned (shaped by similar content goals), the constraint is partially redundant with the filter — the filter has already removed content the constraint would suppress, so the constraint adds less marginal distortion than its standalone effect would suggest. Aligned configurations are typically *least*-compounding. Anti-aligned configurations — uncommon in practice — produce the largest combined distortion because the constraint pushes back against directions the data does not support. The realistic deployment case (filter and constraint shaped by similar institutional goals) sits in the aligned regime, which is the *least* damaging combination, not the most.

This does not mean the deployed system is undistorted. Both filter phantom and constraint phantom are present, and their combination is nonzero. What the corrected statement says is that combined distortion is sub-additive in the aligned regime, not super-additive. The deployment system's phantom magnitude is bounded between the larger of the two individual contributions and (approximately) their sum, with the actual value typically closer to the larger individual contribution than to the sum.

**This is the most consequential correction propagated from the eleven-round correction record.** It directly affects deployment-system phantom-magnitude bounds and changes what the framework predicts about realistic combined cases. Earlier drafts of the trilogy were wrong about this; the corrected statement above is what the framework actually supports.

The distortion is structurally embedded in the combined geometry, but the framework no longer claims it is structurally larger than what either layer produces alone.

---

## Development Record

First pass on the data-hole case, with subsequent rescoping correction. Worked through:

- The setup ($G$ as input-space hole, $\hat f$ as data-fit on filtered corpus, the interpolation operator $I_G$).
- The two failure modes (confident interpolation vs calibrated uncertainty) and which is dominant in deployed systems.
- The three-part anatomy (bulk, edge, projector) translated to data-hole context, with the four-object scalar decomposition (retention, suppression, leakage, total error) governing bulk phantom magnitude.
- The T6 analog with architecture-specific interpolation kernel replacing the cosine propagator.
- The structural differences from constraint phantoms (recoverability, self-consistency, adjacency, time invariance).
- The combined deployment case with corrected compounding behavior (aligned filter+constraint is least-compounding).

**Round-11 rescoping (April 2026).** Earlier drafts presented the data-hole framework as if the operator-theoretic apparatus applied globally, with the linearization treated as a regrettable approximation that "characterizes the leading-order behavior." External review (the eleven-round correction record of the info-geometric reformulation companion) identified three substantive corrections:

- **Linearization is the document's scope, not an approximation.** Two separate linearizations are at play: (a) the Hilbert / Fisher-tangent setting required by the Halmos toolkit when outputs are distributional; (b) the local-linearity assumption on the architecture's interpolation operator $I_G$, valid in the boundary-layer neighborhood and breaking down deep inside $G$. The Preface and §1.2 now make these explicit, and predictions are scoped accordingly.

- **The four-object scalar decomposition replaces "the energy law $\beta(1-\beta)$".** Earlier drafts called $\beta(1-\beta)$ "the energy law controlling phantom magnitude in the bulk." This was the leakage formula for one of four distinct objects. §2.1 has been rewritten to introduce all four (retention $\beta^2$, suppression $(1-\beta)^2$, leakage $\beta(1-\beta)$, total error $1-\beta$), with the per-mode identity total = suppression + leakage. The phantom in query coordinates is suppression, peaking at orthogonality; cross-query phantom is leakage, peaking at intermediate alignment. §6.1 and §7.1 prediction (5) updated for consistency.

- **§5.2 and Part VIII compounding claim reversed.** The most consequential correction. Earlier drafts claimed filter and constraint typically compound rather than cancel because they are shaped by the same content goals — that aligned configurations would produce the largest combined phantom magnitude. The companion's verified numerical work (240-configuration sweep) shows the opposite: aligned filter+constraint produces the *smallest* combined distortion in 211/240 cases pointwise, with anti-aligned producing the largest. The compounding intuition was a linearized-regime artifact that fails in the global KL geometry. §5.2 has been rewritten with the corrected statement and the supporting numerics; Part VIII has been rewritten to drop the "compounding by institutional incentives" claim and replace it with the corrected aligned-is-least-compounding statement; §7.1 prediction (6) added accordingly.

- **§3.2 capacity-bandwidth correspondence downgraded to definitional.** Earlier drafts asserted a quantitative correspondence between model capacity and effective bandwidth in the data-hole geometry. The companion §3.2 retracts the theorem-style version. What survives is a definitional correspondence — Fisher dimension is a well-defined operational measure of effective capacity, and capacity plays the structural role of bandwidth — but quantitative scaling laws are open empirical work, not framework theorems. §3.2 rewritten accordingly; §7.1 prediction (1) qualified.

- **Trilogy framing corrected.** Earlier drafts treated `statistical_phantoms.md` as a third ML failure mode parallel to filter and constraint phantoms. It is not — that document is the abstract operator-theoretic spine that handles the non-ML statistical inference-pipeline cases (regression with omitted variables, PCA with missing data, matched filtering under common mask) and from which this document and the training-distortion document draw their machinery. Part VIII has been rewritten to position statistical_phantoms correctly as the abstract framework rather than as a peer ML application.

The rescoping does not retract the document's core content; it makes the regime of validity explicit, corrects the specific scalar-law identifications, reverses the compounding claim with the empirical evidence, and properly scopes the capacity-bandwidth correspondence. **The Halmos formulation as local linearization is the document's contribution as a clean entry point to the nonlinear-manifold treatment in the companion.** Predictions hold qualitatively in the linearization regime; quantitative magnitudes carry the 15–25% slope-deviation error envelope from second-order curvature corrections.

Open and not developed:

- The architecture's interpolation kernel $K_{\text{arch}}(t)$ for transformer-specific architectures requires explicit characterization. The framework names the role; specifying the kernel in closed form is open empirical work.
- A precise statement linking model parameter count or Fisher dimension to quantitative phantom-anatomy quantities. *Status: §3.2 retracted to definitional correspondence; quantitative scaling is open.*
- The diagnostic protocol for distinguishing filter from constraint via routing-around tests. *Qualitative classification is reliable; quantitative magnitudes carry the curvature-correction error envelope.*
- The information-theoretic version of the framework (working globally in KL geometry rather than locally in Fisher-tangent linearization). *Status: developed for the constraint side in `info_geometric_reformulation.md`; analogous nonlinear treatment for the interpolation side is open.*
- Numerical companions demonstrating the predicted phantom anatomy on synthetic filter scenarios. *Partial: the companion's numerical work covers the four-object decomposition and the filter+constraint redundancy result; data-hole-specific synthetic experiments are not built.*

Likely revisions:

- Part III's T6 analog deserves more development at the architecture-specific level. The role of capacity as bandwidth is now correctly scoped to definitional, but a worked example with a specific architecture (e.g., a small transformer or kernel method) would strengthen the framework.
- Part V's combined case may benefit from explicit worked examples — specific filter geometries combined with specific constraint geometries to show the *aligned-is-least-compounding* result numerically in a data-hole-plus-RLHF synthetic setup, paralleling the companion's reward-direction sweep.

The role of this document. **Filter phantoms are the closest fit among ML applications to the spatial-gap operator framework** — the gap is genuinely geometric in input space, the mask is a literal multiplication operator, and the bulk-edge-projector anatomy carries directly. This document and the training-distortion companion together cover the two structurally distinct ML failure modes (filter and constraint) with explicit linearization scope. The abstract framework that handles both — and also the non-ML statistical inference-pipeline cases — is `statistical_phantoms.md`. The nonlinear-manifold treatment for the strong-deviation regimes lives in `info_geometric_reformulation.md`.
