# The Phantom Framework in Information Geometry

## A reformulation that fixes the linearization problem and the capacity-as-bandwidth analogy

*Working Document — First Pass · April 2026*

*Companion to: Statistical Phantoms; Training Distortion as Forced Constraint Projection; Training Corpus Holes as Multiplication Defects*

---

## Preface

The trilogy as it stands has a load-bearing weakness in the ML applications: the L²/Hilbert framing is forced. Real RLHF lives on a manifold of conditional distributions with KL geometry, not on a Hilbert space with L² geometry. The trilogy's own development records flag this in three places:

- *Training distortion*, §VII open work: "the KL/information-geometric version of the framework, which is the natural framing for distributional outputs and which gives different (Riemannian) geometry. The L² framing is what licenses Halmos directly; the KL framing would require a parallel development."
- *Statistical phantoms*, §6.3: "The information-theoretic case (§4.6) requires care about which Hilbert space the framework is operating in."
- *Training corpus holes*, §VIII: "The information-theoretic version of the framework (working in KL geometry rather than L²) handles the data distribution case more naturally but produces different mathematical structure."

This document is that parallel development. The structural claim is that the trilogy's *core* results carry over — the energy law, the mask-adapted basis, the three-flavor classification — but with three substantive upgrades, each with a stated regime of validity:

1. **The linearization is replaced by a tilted-exponential identity in the m-flat regime, with curvature-bounded corrections elsewhere.** The Hilbert framework treats training as $f_{\text{trained}} = P_C f_{\text{true}}$, a linear projection in a forced Hilbert structure. The information-geometric replacement is e-projection of $\pi_{\text{ref}}$ onto the constraint manifold, with closed form $\pi^*(y|x) \propto \pi_{\text{ref}}(y|x) e^{\lambda^* r(x,y)}$. The generalized Pythagorean theorem (Csiszár 1975, Amari–Nagaoka 2000) gives an *exact* identity for points $\pi' \in \mathcal{C}$: $D(\pi' \| \pi_{\text{ref}}) = D(\pi' \| \pi^*) + D(\pi^* \| \pi_{\text{ref}})$. **Pythagorean does not give a clean decomposition of $D(\pi_{\text{true}} \| \pi^*)$ when $\pi_{\text{true}} \notin \mathcal{C}$**, which is the case the framework is interested in — a Bregman cross-term appears that earlier versions of this document had wrongly dismissed (see §2.2 for the retraction). For the filter+constraint composition, the Bregman triangle identity with the cross-term $\lambda^*(R_{\text{true}} - R_0)$ is the correct exact identity; that's what the §IV experiments verify.

2. **Capacity is defined as Fisher dimension. Its scaling like bandwidth is not derived.** The bandwidth $\Lambda$ of the spatial-gap case is mapped, in the data-hole document, to "architecture capacity" by analogy. This document defines *Fisher dimension* of the model's expressive manifold $\mathcal{M}_\theta$ — the rank of the Fisher information matrix at $\pi_\theta$ — as the operational replacement. That definition is precise and computable. The capacity-bandwidth scaling claim ($\ell \sim d_\theta^{-1/d}$), stated as a "sketched theorem" in v1, is a dimension-counting guess and remains open. Fisher rank is not bandwidth in any derived sense (§3.2 retraction). The move from analogy to operational definition is real progress; promoting that definition to a scaling theorem about data-hole behavior is not something this document does.

3. **Filter and constraint phantoms get a unified geometric treatment with a corrected combination law.** Both reduce to projections in $\mathcal{P}$. The combination of filter then constraint is m-extension followed by e-projection, with the relevant decomposition given by a Bregman triangle identity whose cross-term is $\lambda^*(R_{\text{true}} - R_0)$. The trilogy's claim that aligned filter and constraint compound super-additively turns out to be **wrong in this geometry**: the §IV experiments verify that aligned configurations produce the smallest total error in mean and median across the tested family (211 / 240 cases pointwise; 222 / 240 with aligned ≤ orthogonal; 223 / 240 with aligned ≤ anti-aligned), with super-additive compounding crossing first into the anti-aligned regime, not the aligned one. The result is robust on average but not pointwise universal, and even the on-average claim is conditional on configurations where filter and constraint move policy in the same direction. This is the most substantive single technical correction in the document.

What this document does not fix: the empirical question of what $\mathcal{C}$ actually is for any specific RLHF pipeline; the post-hoc identification of specific observed phenomena with framework flavors; the gap between "framework predicts X" and "X has been measured in production systems." Mathematical sophistication doesn't substitute for empirical work. The reformulation makes predictions in operationally-measurable quantities; turning those predictions into empirical results remains the open work.

---

## Part I — Setup: The Manifold of Policies

### 1.1 The space

Let $\mathcal{X}$ be the input space and $\mathcal{Y}$ the output space (token vocabulary, in the LLM case). A **policy** is a conditional distribution $\pi(\cdot|x)$ on $\mathcal{Y}$ for each $x \in \mathcal{X}$. The space of policies is

$$\mathcal{P} = \big\{\pi : \mathcal{X} \to \Delta(\mathcal{Y}) \;\big|\; \pi(\cdot|x) \in \Delta(\mathcal{Y}) \text{ for all } x\big\}$$

where $\Delta(\mathcal{Y})$ is the probability simplex on $\mathcal{Y}$. Working in the relative interior (all probabilities strictly positive), $\mathcal{P}$ is an open manifold of dimension $|\mathcal{X}|(|\mathcal{Y}|-1)$ in the discrete case, with the obvious extension to continuous spaces via measure-theoretic care that the framework doesn't depend on.

### 1.2 The Fisher metric

The tangent space at $\pi$ consists of functions $u : \mathcal{X} \times \mathcal{Y} \to \mathbb{R}$ satisfying $\sum_y u(x,y) \pi(y|x) = 0$ for each $x$ — mean-zero under $\pi(\cdot|x)$ at each fiber. The **Fisher information metric** is

$$g_\pi(u, v) = \mathbb{E}_{x \sim \nu}\,\mathbb{E}_{y \sim \pi(\cdot|x)}\,[u(x,y)\,v(x,y)]$$

where $\nu$ is a fixed input distribution (the training distribution, or whatever distribution defines the inner product the analyst cares about). This makes $\mathcal{P}$ into a Riemannian manifold.

The relationship to KL divergence: for $\pi'$ near $\pi$, with $\pi' = \pi + \epsilon u$ to first order,

$$D(\pi \| \pi') = \tfrac{1}{2} \epsilon^2 g_\pi(u, u) + O(\epsilon^3).$$

Fisher is the second-order Taylor coefficient of KL around the diagonal. This is the formal sense in which "L² with the Fisher metric" is the linearization of the KL geometry.

### 1.3 The dual connections

Information geometry has two natural affine connections on $\mathcal{P}$:

- **The exponential connection $\nabla^{(e)}$.** Geodesics are exponential families: $\pi_t(y|x) \propto \pi_0(y|x)^{1-t}\,\pi_1(y|x)^t$ (after normalization at each $x$).
- **The mixture connection $\nabla^{(m)}$.** Geodesics are mixtures: $\pi_t(y|x) = (1-t)\pi_0(y|x) + t\pi_1(y|x)$.

These connections are mutually dual with respect to the Fisher metric: $\nabla^{(e)} g = 0$ in the right sense, and the same for $\nabla^{(m)}$, with their difference encoded by the Amari–Chentsov tensor.

A submanifold $M \subset \mathcal{P}$ is **e-flat** if it is totally geodesic under $\nabla^{(e)}$, equivalently if it is described by linear constraints in the natural exponential parameters. It is **m-flat** if it is totally geodesic under $\nabla^{(m)}$, equivalently if it is described by linear constraints on expectations of fixed functions.

### 1.4 Two natural projections

For a submanifold $M \subset \mathcal{P}$ and a base point $\pi_0 \notin M$:

- The **e-projection** of $\pi_0$ onto $M$ is $\pi^*_e = \arg\min_{\pi \in M} D(\pi \| \pi_0)$ — minimize KL with $\pi_0$ as the reference (second argument).
- The **m-projection** is $\pi^*_m = \arg\min_{\pi \in M} D(\pi_0 \| \pi)$ — minimize KL with $\pi_0$ as the source (first argument).

When $M$ is m-flat, the e-projection exists, is unique, and satisfies the **generalized Pythagorean theorem**: for all $\pi \in M$,

$$D(\pi \| \pi_0) = D(\pi \| \pi^*_e) + D(\pi^*_e \| \pi_0). \qquad (\star)$$

The dual statement holds for m-projection onto e-flat $M$. This identity is the information-geometric replacement for "the orthogonal projection minimizes distance and decomposes the squared norm." It is exact, not asymptotic, when the flatness condition holds.

---

## Part II — Constraint Phantoms in Information Geometry

### 2.1 The RLHF objective is an e-projection onto an m-flat manifold

The standard KL-regularized RLHF objective is

$$\pi^* = \arg\max_\pi \;\mathbb{E}_{\pi}[r] - \beta\,D(\pi \| \pi_{\text{ref}})$$

where $r$ is the reward function and $\pi_{\text{ref}}$ is the reference (pre-training or SFT) policy. In its constrained form,

$$\pi^* = \arg\min_{\pi:\;\mathbb{E}_\pi[r] \geq R_0}\, D(\pi \| \pi_{\text{ref}}). \qquad (\dagger)$$

The constraint set $\mathcal{C} = \{\pi : \mathbb{E}_\pi[r] \geq R_0\}$ is bounded by an m-flat hypersurface — the level set $\mathbb{E}_\pi[r] = R_0$ is linear in expectation parameters (treating $r$ as a sufficient statistic). The interior of $\mathcal{C}$ is an m-flat half-space; the boundary is m-flat codimension-one.

The minimizer $(\dagger)$ is the **e-projection of $\pi_{\text{ref}}$ onto $\partial\mathcal{C}$** (the active boundary, where $\mathbb{E}_{\pi^*}[r] = R_0$ — the constraint is binding). By the generalized Pythagorean theorem applied to e-projection onto an m-flat manifold (Csiszár 1975, Amari–Nagaoka 2000):

$$D(\pi \| \pi_{\text{ref}}) = D(\pi \| \pi^*) + D(\pi^* \| \pi_{\text{ref}}) \qquad \text{for all } \pi \in \partial\mathcal{C}.$$

This is the exact identity, but it holds only for $\pi$ on the active boundary $\partial\mathcal{C}$. **For $\pi$ in the interior of the half-space $\mathcal{C}$ (where $\mathbb{E}_\pi[r] > R_0$), the identity becomes**

$$D(\pi \| \pi_{\text{ref}}) = D(\pi \| \pi^*) + D(\pi^* \| \pi_{\text{ref}}) + \lambda^*(\mathbb{E}_\pi[r] - R_0)$$

with the cross-term measuring how far $\pi$ sits inside the half-space along the active reward direction. The cross-term vanishes exactly on the boundary and is non-negative in the interior. An earlier version of this section stated the equality without qualification "for all $\pi \in \mathcal{C}$"; that overstated the result. The trained policy $\pi^*$ itself sits on the boundary (at the optimum, the constraint is active for the regimes the framework is interested in), so the boundary-Pythagorean is the relevant identity for relating $\pi^*$ to $\pi_{\text{ref}}$.

The trained policy is the *closest* (in KL) policy to $\pi_{\text{ref}}$ that satisfies the constraint, with the closest-approach direction along the e-geodesic from $\pi_{\text{ref}}$ to $\pi^*$. Explicitly,

$$\pi^*(y|x) = \frac{1}{Z(x)}\, \pi_{\text{ref}}(y|x)\, \exp\!\big(\lambda^* r(x,y)\big)$$

where $\lambda^*$ is the Lagrange multiplier set by $\mathbb{E}_{\pi^*}[r] = R_0$ and $Z(x)$ is the normalizing constant. This is the explicit form of the trained policy on the e-geodesic; it is *not* a linear projection in any L² sense, but it is exactly an e-projection in the Fisher sense.

### 2.2 Pythagorean structure: what is and isn't an identity

The information-geometric replacement for the L² framework's "forced offset" needs care about which decomposition is actually identity-preserving. An earlier version of this section claimed

$$D(\pi_{\text{true}} \| \pi^*) = D(\pi_{\text{true}} \| \pi_T^*) + D(\pi_T^* \| \pi^*) \qquad (\ddagger \text{ — wrong})$$

with $\pi^* = e\text{-proj}_\mathcal{C}(\pi_{\text{ref}})$ and $\pi_T^* = e\text{-proj}_\mathcal{C}(\pi_{\text{true}})$, and dismissed the cross-term as vanishing for m-flat constraints. **This is wrong, and `test_kl_decomposition.py` verifies the failure.** Numerical residuals run from $+0.05$ at $R_0 = 0.1$ through zero around $R_0 = 0.45$ to $-0.55$ at $R_0 = 0.7$ on a 16-output toy with random truth — not numerical noise but a real, sign-changing cross-term whose magnitude is comparable to the quantities in the decomposition.

The error is structural: the generalized Pythagorean theorem applies when the point being decomposed lives **inside** the m-flat manifold $\mathcal{C}$, and the projection is from an outside reference. For $\pi' \in \mathcal{C}$ and $\pi^* = e\text{-proj}_\mathcal{C}(\pi_0)$,

$$D(\pi' \| \pi_0) = D(\pi' \| \pi^*) + D(\pi^* \| \pi_0). \qquad (\star)$$

The wrong decomposition $(\ddagger)$ tries to apply this with $\pi_{\text{true}}$ (which is **outside** $\mathcal{C}$ — that's the whole reason the framework is interested in it) playing the role of $\pi'$. Pythagorean does not apply in that orientation; what you get is the Bregman cross-term that I had asserted vanishes.

The **correct** Pythagorean identity for this setup, which holds to machine precision in the same toy (residuals $\sim 10^{-13}$), takes $\pi' = \pi_T^*$ (which *is* in $\mathcal{C}$) and decomposes against $\pi_{\text{ref}}$:

$$D(\pi_T^* \| \pi_{\text{ref}}) = D(\pi_T^* \| \pi^*) + D(\pi^* \| \pi_{\text{ref}}). \qquad (\star\star)$$

This is the genuinely identity-preserving statement. It says: of the KL distance from $\pi_T^*$ (truth's projection) to $\pi_{\text{ref}}$, the trained policy $\pi^*$ sits exactly on the e-geodesic with the right additive split. It does not directly decompose $D(\pi_{\text{true}} \| \pi^*)$, because $\pi_{\text{true}}$ is not in $\mathcal{C}$ and Pythagorean from the outside doesn't decompose cleanly.

For the quantity the framework actually wants — $D(\pi_{\text{true}} \| \pi^*)$, the KL from truth to the trained policy — there is a different and exact identity that comes from the explicit form $\pi^*(y|x) \propto \pi_{\text{ref}}(y|x) e^{\lambda^* r(x,y)}$:

$$D(\pi_{\text{true}} \| \pi^*) = D(\pi_{\text{true}} \| \pi_{\text{ref}}) - \lambda^* \mathbb{E}_{\pi_{\text{true}}}[r] + \mathbb{E}_{x \sim \nu}[\log Z_x(\lambda^*)] \qquad (\text{exact for log-linear tilt})$$

where $Z_x(\lambda^*) = \sum_y \pi_{\text{ref}}(y|x) e^{\lambda^* r(x,y)}$ is the per-input normalization and $\nu$ is the input distribution. For output-only rewards (where $r$ depends only on $y$), $Z_x = Z$ is independent of $x$ and the expectation collapses to $\log Z(\lambda^*)$. For general $r(x,y)$ (including learned reward models), the $x$-expectation matters and must be carried explicitly. This is exact and operationally meaningful: $D(\pi_{\text{true}} \| \pi^*)$ is the prior KL minus a reward-bias correction plus a partition-function term. There's no Pythagorean cross-term because there's no Pythagorean identity in play — it's just the explicit log-likelihood-ratio computation against the exponential family $\pi^*$.

The §IV experiments use the analogous Bregman triangle identity for filter+constraint composition,

$$D(\pi_{\text{true}} \| \pi_{\text{filter}}) = D(\pi_{\text{true}} \| \pi_{\text{final}}) + D(\pi_{\text{final}} \| \pi_{\text{filter}}) + \lambda^*(R_{\text{true}} - R_0),$$

which **does include the cross-term** and which holds to machine precision when the cross-term is kept. That identity is correct as stated and verified. The mistake was in the simpler-looking decomposition $(\ddagger)$ where I had asserted the cross-term away rather than computing it.

**Retraction.** The "truth-side incompressible loss" and "reference-induced bias" interpretation that earlier versions of this section attached to $(\ddagger)$ are not justified by the geometry. The two terms of $(\ddagger)$ are well-defined quantities, but they don't sum to $D(\pi_{\text{true}} \| \pi^*)$, and their interpretation as the decomposition of phantom KL was wrong.

### 2.3 The four-object decomposition (replacing the universal energy law)

An earlier version of this document, following the trilogy, stated a "universal energy law" $\frac{1}{2}\sum |a_j|^2 \beta_j(1-\beta_j)$ as the leading-order phantom magnitude. **This was a structural error.** The scalar formula $\beta(1-\beta)$ describes one specific object — leakage to adjacent query coordinates — and is wrong as a universal phantom law because the framework's "phantom" actually conflates four distinct objects with four distinct scalar dependencies on $\beta$. The error was inherited from the trilogy and deserves explicit correction.

For two orthogonal projections $P, C$ with $T = PCP|_{\text{Range}(P)}$ having eigenvalues $\beta_j$ and eigenvectors $u_j$, decompose any $f = \sum_j a_j u_j \in \text{Range}(P)$. The constraint-projected output $Cf$ produces four distinct quantities, each with its own scalar law:

| Object | Norm-squared | Maximum at | What it measures |
|---|---|---|---|
| **Retention** | $\|PCf\|^2 = \sum |a_j|^2 \beta_j^2$ | $\beta=1$ | Truth surviving in query coordinates |
| **Suppression** | $\|Pf - PCf\|^2 = \sum |a_j|^2 (1-\beta_j)^2$ | $\beta=0$ | Truth missing from query coordinates |
| **Leakage** | $\|(I-P)Cf\|^2 = \sum |a_j|^2 \beta_j(1-\beta_j)$ | $\beta=1/2$ | False content in adjacent coordinates |
| **Total error** | $\|f - Cf\|^2 = \sum |a_j|^2 (1-\beta_j)$ | $\beta=0$ | Full KL distance to truth (Fisher-tangent) |

These satisfy the per-mode identity $1-\beta_j = (1-\beta_j)^2 + \beta_j(1-\beta_j)$, equivalently total error = suppression + leakage. The decomposition is verified algebraically and numerically to machine precision (companion script `four_way_decomposition.py`).

The "universal energy law" $\beta(1-\beta)$ that the trilogy and this document's v1 used is the **leakage** formula. It is not the law for suppression, retention, or total error. Different observed phenomena correspond to different objects, and conflating them produces the pattern of overreach that has required repeated correction in this work.

**A fifth phenomenon, not in the four-way table.** When a query is approximately orthogonal to the constraint ($\beta \to 0$), the model produces $P_C f_{\text{true}}$ — the constraint-compliant projection of truth — which has very little overlap with the query direction. The user nonetheless reads this output as the answer to their query, and the *content* that fills the answer slot is whatever lives in the constraint manifold closest to truth. This **replacement content** is a separate object from the four above; it's the actual material that gets returned, not a measure of distortion. The four-way table tells you how *much* the answer differs from truth; the replacement content tells you *what* the answer instead consists of.

**Which object is which observed phenomenon:**

- The trilogy's "phantoms maximized at intermediate alignment" claim applies *only to leakage*. It is wrong as a general statement about suppression, retention, or total error.
- The Black Nazi case has a more complicated relationship to this decomposition than I'd been claiming; see §2.4 for the corrected discussion. Briefly: the case most plausibly sits in the RLHF e-projection geometry (§IV's setup), where the framework's verified prediction is about total error at high Lagrange multiplier, not about the four-object decomposition. The four-object formulas describe a different projection problem and don't directly apply.
- The "compounding into adjacent topics" intuition for constraint phantoms is leakage — the $\beta(1-\beta)$ phenomenon — and would sit at intermediate alignment, *if* the four-object formulas applied to the operative setup. As just noted, they don't apply to RLHF directly.
- Eigenstructure rotation in PCA-like settings is yet another phenomenon; it's the rotation of the basis $\{u_j\}$ itself when one projection is perturbed, which the four-way table doesn't directly address.

The framework remains organized around two-projection geometry, but the single-formula version of the universal energy law does not survive. Each claim must specify which of the four (or five) objects it is about.

### 2.4 The Black Nazi case: which framework actually applies

Earlier versions of this section treated the Black Nazi case as a worked example of the four-object decomposition, with truth approximately orthogonal to the constraint giving suppression $\approx 1$, leakage $\approx 0$, total error $\approx 1$, and "replacement content" $\approx P_C P_Q f_{\text{true}}$. **That treatment had two errors layered on top of each other**, both of which need correcting.

**Error 1 (mechanism).** I asserted the case was data corruption — corpus curation that paired "Wehrmacht" with diverse demographics during training. That is one possible mechanism. It is not the publicly confirmed one.

What's known from outside Google: the model produced racially diverse Wehrmacht imagery in response to historical-prompt queries; Google's public statement attributed this in part to a prompt-rewriting layer; the product was pulled. What's *not* known: whether the training corpus was systematically curated, whether the RLHF/preference data scored diverse-representation criteria highly enough to bias the policy, whether prompt rewriting was the dominant mechanism or one component, what the exact contributions of each mechanism were.

The framework can describe what *would happen* in any of these mechanisms if they reduce to e-projection-from-reference geometry — that is the setup of §IV and Bridge B. It cannot identify which mechanism (or which combination) actually produced the observed behavior in this specific case. The geometry is consistent with any of: objective distortion via a reward model, prompt rewriting that shifts the effective query distribution, or corpus curation that makes the trained policy implement a different conditional than truth would. Discriminating among these from outside requires evidence the framework does not provide.

**The case as illustrative, not diagnostic.** Treat the Black Nazi case as a worked illustration of what the framework's geometric predictions look like in the orthogonal-truth, hard-constraint regime — qualitatively consistent with the framework's predicted phenomenology in that regime, but *not* diagnostic of which production mechanism is operative. Causal claims about prompt rewriting vs reward modeling vs corpus curation as the production mechanism in this specific case need primary-source evidence the document does not have.

**Error 2 (setup).** Even granting that the operative mechanism is some flavor of e-projection from reference, the four-way decomposition formulas of §2.3 don't apply to it directly. Those formulas are for "$f \in \text{Range}(P_Q)$, project onto $C$, decompose components" — see §4.8 Test 3. RLHF performs a different projection: e-project $\pi_{\text{ref}}$ (which is *not* in $\text{Range}(P_Q)$) onto $\mathcal{C}$, with the result measured against $\pi_{\text{true}}$. The four-way scalar laws don't transfer unmodified; Bridge B (Appendix B) provides the setup-specific replacement at first order.

**What the framework, in its current state, can correctly say about the case:**

The case sits within the RLHF e-projection geometry (framework-1, the setup of §IV). For this setup, when truth $\pi_{\text{true}}$ is approximately orthogonal to the constraint subspace and the constraint is hard ($R_0$ pushed well away from the unconstrained reward of $\pi_{\text{ref}}$), the Lagrange multiplier $\lambda^*$ becomes large. By the Bregman triangle identity, the trained policy ends up far from $\pi_{\text{ref}}$ along the e-geodesic toward the constraint, and far from $\pi_{\text{true}}$ as measured in KL.

This is the **total-error-at-high-$\lambda^*$** regime, and §IV verified the prediction for this regime: combined phantom magnitude (in the total-error sense) scales with constraint severity and with truth's distance from the constraint. The Black Nazi case is plausibly an instance of this regime, where:

- The constraint (demographic-representation criteria) is hard.
- Truth (historical Wehrmacht imagery) is approximately orthogonal to the constraint direction in policy space.
- The trained policy is therefore displaced far from truth in KL.
- The displacement direction is along the e-geodesic toward $\mathcal{C}$, so the trained policy's content is constraint-compliant.

This is a *qualitative* prediction the framework gets right: large total error, content along the constraint direction. It does not require the four-way decomposition. The redundancy result of §IV applies; the bridge to fine-grained four-object phenomenology does not.

**What the framework can now say about the case (with Bridge B):**

Bridge B (Appendix B) is the first-order Fisher-tangent decomposition for the e-projection-from-reference setup that RLHF actually performs. With $a$ the truth's distance from reference, $\mu$ the (signed) trained displacement coordinate along the constraint direction (set by $\lambda^*$), and $s = q \cdot c$ the signed cosine between truth and constraint directions, Bridge B predicts:

- Query-direction output energy: $\mu^2 s^2$.
- Query-coordinate error (suppression): $(a - \mu s)^2$.
- Off-query leakage: $\mu^2(1 - s^2)$.
- Total tangent error: $a^2 + \mu^2 - 2 a \mu s$.

For the Black Nazi case — *if* the operative constraint is something like representational diversity, so truth (historical Wehrmacht imagery) is approximately orthogonal to it ($s \approx 0$), with a hard constraint giving large $|\mu|$ — Bridge B predicts:

- Query-direction output energy $\approx 0$ — near-zero overlap with the truth direction (the model's output in "Wehrmacht imagery" coordinates carries little of the historical truth).
- Suppression $\approx a^2$ — close to full suppression of truth in the query direction.
- Off-query leakage $\approx \mu^2$ — substantial off-query displacement, scaling with constraint severity. *Not* peaked at intermediate alignment, contrary to the trilogy's $\beta(1-\beta)$ framing.
- Total tangent error $\approx a^2 + \mu^2$ — sum of suppression and leakage at orthogonality.

This matches the case qualitatively: near-full suppression of historical truth, substantial displacement of output into the constraint manifold (which the user reads as "constraint-compliant content filling the answer slot"), with magnitude scaling with the constraint's hardness. It makes a sharper *toy-level* prediction than the trilogy's framing: in the toy setup, leakage scales with $\mu^2$ (the constraint severity squared), not with $\beta(1-\beta)$.

**The gap from toy to production system is real and unbridged.** A test of the $\mu^2$-leakage prediction on a real RLHF system would require: (a) identifying a single isolated constraint direction — real systems use learned reward models with thousands of effective directions, not a single linear functional, and the reward model is itself noisy and shifts during training; (b) varying "constraint severity" while holding other things fixed — the KL coefficient in actual PPO/DPO controls penalty strength, not the m-flat constraint severity $R_0$, and the duality between the two only holds at the optimum, which iterative RLHF doesn't reach exactly; (c) operationalizing "off-query behavior" — in the toy this is the perpendicular component of $g$ with respect to $q$ in the simplex tangent at $\pi_{\text{ref}}$, but for an LLM generating tokens conditional on a prompt, what is $q$ and what is the inner product? (d) estimating $\mu = \lambda^* \|\tilde r\|_F$ — $\lambda^*$ in real RLHF isn't directly observable, and the relationship to the loss-function KL coefficient requires assumptions that aren't met in practice. None of these obstacles is fatal to the prediction, but none has been worked out in this document. The honest framing is: *if* a real RLHF system happens to be well-modeled by single-constraint e-projection from a fixed reference, *then* leakage scales with $\mu^2$ in the appropriate coordinates, with a 15–25% magnitude error envelope from second-order curvature (§B.5). Demonstrating that some real system is in fact well-modeled this way is the genuine empirical work and has not been done.

**Earlier in this conversation I made several specific claims about the case** — that it sits at the "geometric maximum of phantom magnitude $\beta(1-\beta) \to 1/4$," that it is at "maximum suppression and minimum leakage" via the pure-projection formulas, that the "replacement content" is $P_C P_Q f_{\text{true}}$. The first was wrong (universal energy law conflation, §2.3). The second was right *for the pure-projection setup*, but that setup isn't what produced the Black Nazi imagery. The third was a description of an object from a setup that isn't the operative setup. All three need to be retracted as applied to the actual case; Bridge B's predictions replace them.

What's left, after all corrections: the case's qualitative phenomenology is consistent with the framework's predictions in the orthogonal-truth, hard-constraint regime that Bridge B describes. The case is illustrative of what the framework predicts, not diagnostic of which production mechanism produced the observed behavior — that's a question outside the framework's scope.

The trilogy's instinct that the case is geometrically meaningful was right; the *specific scalar prediction* was wrong, and Bridge B now provides what should have been there from the start.

---

## Part III — Filter Phantoms in Information Geometry

### 3.1 The filtered training problem

The data-hole case has training data on $\mathcal{X} \setminus G$ but not on $G$. Let $\mathcal{M}_\theta \subset \mathcal{P}$ be the model's expressive manifold — the set of policies the architecture can represent. Training converges (in the well-specified limit) to

$$\pi_{\text{trained}} = \arg\min_{\pi \in \mathcal{M}_\theta} \int_{\mathcal{X}\setminus G} D\big(\pi_{\text{true}}(\cdot|x)\,\big\|\,\pi(\cdot|x)\big)\, d\nu(x).$$

The integrand is a fiberwise KL, and the integral is the weighted KL on the data-supported region only. The minimizer over $\mathcal{M}_\theta$ is constrained: outside $G$, the model fits the data; inside $G$, the model is whatever its capacity allows it to be while staying on $\mathcal{M}_\theta$ and consistent with the data fit outside.

The framework's "interpolation operator $I_G$" of the L² version becomes geometrically: the **m-extension** of the data-fit policy from $\mathcal{X} \setminus G$ to all of $\mathcal{X}$, constrained to lie in $\mathcal{M}_\theta$. That is, $\pi_{\text{trained}}|_G$ is *some* element of $\mathcal{M}_\theta$ consistent with the data fit on $\mathcal{X}\setminus G$, with the specific element selected by architecture, regularizer, optimizer, initialization, and the divergence being minimized. The data alone underdetermines the extension; an earlier version of this section called it "the unique element of $\mathcal{M}_\theta$ closest to the boundary data," but uniqueness only follows after the additional structure is fixed. The framework treats the extension as architecturally specified and analyzes its consequences; it does not derive the extension itself.

### 3.2 Capacity as Fisher dimension: a definition, not a correspondence

The L² framework called the capacity-bandwidth correspondence "asserted at the qualitative level." An earlier version of this section claimed information geometry makes it precise via Fisher dimension. **That overstated what's been done.** Defining a quantity is not the same as proving it scales like bandwidth in the spatial-gap case.

Define

$$d_\theta(\pi) := \mathrm{rank}\, F(\theta)$$

where $F(\theta)$ is the Fisher information matrix of the parametric family $\{\pi_\theta\}$ at $\pi_\theta = \pi$. For overparameterized neural networks $d_\theta$ is much smaller than the parameter count, because of redundancies in the parameterization. It is a well-defined, in-principle-computable quantity.

**What this gives us, definitively:** an operational replacement for the trilogy's hand-waved "effective capacity" — a specific scalar attached to a specific point $\pi_\theta$ on a specific parametric family.

**What this does not give us:** the bandwidth scaling. The spatial-gap result $\Lambda \sim N$ is a theorem about Fourier-cutoff representations of functions on a one-dimensional gap, with $N$ counting retained modes. Fisher dimension counts independent directions in the policy manifold near a point. There is no theorem that ties these together; the analogy is suggestive but unproven, and Fisher rank is not bandwidth in any derived sense.

The earlier sketch ("Capacity-Bandwidth Theorem (informal)") asserting $\ell \sim d_\theta^{-1/d}$ is a dimension-counting *guess*, not a derivation. Even calling it a sketch implies a path to proof that hasn't been laid out. The honest status is:

- Fisher dimension is a defined quantity ([E], by definition).
- The relationship between Fisher dimension and the spatial-gap notion of bandwidth is open ([O]).
- The relationship between Fisher dimension and the effective resolution scale of the m-extension into a data hole is open ([O]).
- All three claims about capacity in the trilogy and in earlier versions of this document — that capacity scales logarithmically with model size, that more capable models have sharper data-hole phantoms, that capacity-bandwidth is "exact in the appropriate limit" — are conjectures about how architectures interpolate, not consequences of the projection framework.

What the framework can correctly say about data holes:

- The training distribution has support on $\mathcal{X} \setminus G$ but not on $G$.
- The trained model fits the data on $\mathcal{X} \setminus G$ and produces some extension on $G$.
- The extension is underdetermined by the data — there are many distributions on $\mathcal{Y}$ for $x \in G$ that are consistent with perfect data fit on $\mathcal{X} \setminus G$.
- The actual extension is selected by the architecture's inductive bias and the optimization dynamics, both of which are outside the projection framework.

This is enough to support the qualitative claim that filtered training corpora produce systematic distortions on the filtered region, but it does not support the trilogy's specific architecture-dependent predictions about boundary-layer profiles, capacity scaling, or interpolation locality. Those need separate analysis.

### 3.3 The boundary-layer profile

In the spatial-gap case, T6 gives a universal boundary profile $\Gamma(\Lambda t)$. The information-geometric analog is the m-extension's decay from the boundary data into the hole, with decay rate set by the architecture-induced extension kernel — *if* such a kernel can be characterized for the architecture in question. Fisher dimension is one descriptor of the architecture's expressive manifold but does not by itself determine the decay rate of the extension into a data hole; that depends on the architecture, the optimizer, the regularizer, and the data fit on $\mathcal{X}\setminus G$ together.

For an architecture whose induced extension kernel has exponential decay (which is *plausible* for transformers with bounded attention range and convolutions with bounded receptive field, but is not implied by locality alone), the m-extension would decay exponentially from $\partial G$ into $G$ at a rate set by the kernel. For globally connected architectures, the m-extension is non-local. The framework can analyze either case once the architectural extension behavior is specified; it does not derive that behavior from locality of the receptive field.

**This is more careful than the L² version was.** The L² version asserted a boundary layer with architecture-specific shape. The info-geometric version says: *if* the induced extension kernel has exponential decay, *then* the boundary layer is exponential. The conditional matters. Bounded receptive field is a necessary but not sufficient condition for exponential boundary-layer decay — gradient-descent dynamics, regularization, and the specific data fit on $\mathcal{X}\setminus G$ all interact with the architecture's locality to determine the actual extension. This is testable on synthetic models, and a synthetic test would be the right next step before claiming the prediction in production.

### 3.4 The combined case: redundancy vs compounding

Filter and constraint compose as follows. Filter phantoms put $\pi_{\text{trained}}|_G$ at the m-extension of the data fit. Constraint phantoms then e-project the entire policy onto the constraint manifold $\mathcal{C}$. The combined trained policy is

$$\pi_{\text{final}} = e\text{-proj}_\mathcal{C}\big(m\text{-ext}_G(\pi_{\text{data fit}})\big).$$

For e-projection onto an m-flat constraint manifold, the **Bregman triangle identity** gives, for any reference point $\pi_0$ (here we use $\pi_0 = \pi_{\text{true}}$):

$$D(\pi_{\text{true}} \| \pi_{\text{filter only}}) = D(\pi_{\text{true}} \| \pi_{\text{final}}) + D(\pi_{\text{final}} \| \pi_{\text{filter only}}) + \mathcal{R}_{fc}$$

where the cross-term has the explicit form

$$\mathcal{R}_{fc} = \lambda^*(\mathbb{E}_{\pi_{\text{true}}}[r] - \mathbb{E}_{\pi_{\text{final}}}[r]) = \lambda^*(R_{\text{true}} - R_0)$$

with $\lambda^*$ the Lagrange multiplier of the e-projection. Rearranging:

$$D(\pi_{\text{true}} \| \pi_{\text{final}}) = D(\pi_{\text{true}} \| \pi_{\text{filter only}}) - D(\pi_{\text{final}} \| \pi_{\text{filter only}}) + |\mathcal{R}_{fc}| \qquad (R_{\text{true}} < R_0)$$

When truth violates the constraint (the case that motivates the framework), $R_{\text{true}} < R_0$, so $\mathcal{R}_{fc} < 0$ and $|\mathcal{R}_{fc}| > 0$. The combined phantom relative to filter-alone is governed by the competition between $|\mathcal{R}_{fc}|$ (which scales with $\lambda^*$) and $D(\pi_{\text{final}} \| \pi_{\text{filter only}})$ (which scales roughly with $\lambda^{*2}$ near small $\lambda^*$).

**The substantive claim, after numerical verification (§IV):**

In the toy family tested, aligned configurations *typically* produce the smallest combined total error and anti-aligned configurations *typically* produce the largest, in the mean-and-median sense. The ranking is *not pointwise universal* — see §4.5, where in 29 of 240 configurations aligned is not the strict pointwise minimum, and in 81 of 240 the strict three-way ordering aligned ≤ orthogonal ≤ anti-aligned breaks down (orthogonal exceeds anti-aligned in those cases, primarily for non-smooth rewards). Aligned is the smallest in the *mean and median* sense across the sweep; the pointwise claim does not hold without qualification.

A further important caveat: even "aligned produces less combined phantom than alternatives" is conditional on a configuration the toy enforces — that filter and constraint both push policy *away* from $\pi_{\text{ref}}$ in roughly the same direction. When the filter happens to push policy *further* from truth than $\pi_{\text{ref}}$ does, the constraint can pull *back toward* truth and *reduce* total error relative to filter-alone. Whether the combined phantom exceeds either component alone is geometrically conditional, not universal.

Whether the combined phantom exceeds the *naive sum* $D_{\text{filter}} + D_{\text{constraint-only}}$ — the trilogy's "super-additive compounding" claim — depends on the constraint severity $R_0$ and the alignment. In the toy of §IV: aligned crosses into super-additive only at $R_0 \approx 0.78$; orthogonal at $R_0 \approx 0.65$; anti-aligned at $R_0 \approx 0.45$. **The trilogy's claim that institutionally-aligned filter+constraint compound super-additively is wrong in the typical operating regime.** Aligned configurations are the *least* compounding, not the most.

This reverses one of the trilogy's headline claims about the magnitude of distortion under aligned interventions. *An earlier version of this section then drafted a successor claim — that aligned filter+constraint produces signatures observationally indistinguishable from a stronger version of either alone, so the user can't tell which mechanism is operative. That successor claim was refuted in §4.6:* removing the constraint substantially recovers truth in the toy regime, while removing the filter exposes the constraint to operate on uniform reference and worsens distortion. The two interventions produce materially different signatures, not indistinguishable ones. The diagnostic claim is therefore not what the framework predicts; only the *magnitude* claim (aligned = least compounding) survives, with the conditional qualifier above.

Genuine super-additive compounding shows up in the anti-aligned configuration — where filter and constraint actively pull policy in opposite directions. That configuration is unlikely to arise from coordinated institutional incentives (why would a lab filter against its own constraint?), so the trilogy's mechanism for institutional compounding does not produce the actual compounding case.

**An earlier draft of this section claimed the opposite — that aligned configurations are merely redundant while orthogonal ones compound super-additively. The numerical verification refuted this. What remains, after §4.5 and §4.6, is the conditional aligned-is-least-compounding result above.**

---

## Part IV — Numerical Companion: The Redundancy/Compounding Calculation

### 4.0 What this experiment measures, in light of §2.3 and Appendix B

The §2.3 four-object decomposition makes explicit that "phantom magnitude" is not a single quantity. The experiment in this Part computes $D(\pi_{\text{true}} \| \pi_{\text{trained}})$, the full KL distance from truth to the trained policy. The setup-specific tangent-space identification of this quantity depends on which projection geometry is in use:

- In the **pure-projection** setup of §2.3 (project a unit truth-direction onto the constraint subspace), the total error per unit truth norm is $1 - \beta$ where $\beta = \cos^2\theta$.
- In the **RLHF e-projection-from-reference** setup of Appendix B (Bridge B), the total tangent error is $a^2 + \mu^2 - 2a\mu s$, where $a$ is the truth's distance from reference, $\mu$ is the signed trained-displacement coordinate along the constraint direction, and $s = q\cdot c$ is the signed cosine.

The §IV experiments compute KL directly without committing to either tangent identification, so the numerical findings (Bregman triangle, alignment ordering, $\lambda^*$-driven cross-term) speak to *total error* — but the appropriate *interpretation* of that total error in tangent coordinates is Bridge B's $a^2 + \mu^2 - 2a\mu s$, not the pure-projection $1-\beta$, because the experiment performs e-projection-from-reference.

The findings — aligned configurations produce the smallest total error in the moderate-constraint regime, the trilogy's super-additive compounding claim fails, the cross-term has the explicit form $\lambda^*(R_{\text{true}} - R_0)$ — are about how total error decomposes and behaves across alignment regimes. The experiment does not directly measure leakage, suppression, or retention as separate Bridge B components; doing so would be a natural next test, since Bridge B specifies what each component should look like.

### 4.1 Setup

To test §3.4's claim quantitatively, set up a synthetic problem with full geometric tractability.

- Inputs $\mathcal{X} = \{1, ..., 16\}$, outputs $\mathcal{Y} = \{0, ..., 7\}$.
- Reward $r(y) = (y - 3.5)/3.5 \in [-1, 1]$, depending on output only (so $\mathcal{C} = \{\pi : \mathbb{E}_\pi[r] \geq R_0\}$ has m-flat boundary, the regime where Pythagorean is exact).
- Truth $\pi_{\text{true}}(y|x)$: peaked at an x-dependent center (Gaussian-ish over $y$), giving $\pi_{\text{true}}$ overall reward $\approx 0$ but with strong per-x variation.
- Reference $\pi_{\text{ref}}$: uniform on $\mathcal{Y}$.
- Filter $G \subset \mathcal{X}$: removes 8 of 16 inputs from training data.
- m-extension: $\pi_{\text{filter only}} = \pi_{\text{true}}$ on $\mathcal{X} \setminus G$, $\pi_{\text{ref}}$ on $G$ (architecture defaults to reference behavior in unseen regions).
- Combined: e-projection of $\pi_{\text{filter only}}$ onto $\mathcal{C}$, given by $\pi_{\text{final}}(y|x) \propto \pi_{\text{filter only}}(y|x) \exp(\lambda^* r(y))$ with $\lambda^*$ tuned so $\mathbb{E}_{\pi_{\text{final}}}[r] = R_0$.

Three filter scenarios distinguish alignment with the reward direction:

- **Aligned**: $G$ = inputs where $\pi_{\text{true}}(\cdot|x)$ has lowest reward. Filter pushes $\pi_{\text{filter only}}$ toward higher reward (same direction as constraint).
- **Orthogonal**: $G$ = random subset. Filter is reward-neutral on average.
- **Anti-aligned**: $G$ = inputs where $\pi_{\text{true}}(\cdot|x)$ has highest reward. Filter pushes $\pi_{\text{filter only}}$ toward lower reward (opposite to constraint).

### 4.2 Results

The Bregman triangle identity holds to floating-point precision in every case tested (max residual $1.88 \times 10^{-13}$ across 12 R_0×alignment configurations in `visualize_redundancy.py`), confirming the analytical structure of §3.4.

The combined phantom $D(\pi_{\text{true}} \| \pi_{\text{final}})$ vs. the filter-only and constraint-only baselines, scanned across constraint severity $R_0 \in [0.05, 0.85]$ (truth has reward $\approx 0$, so all $R_0 > 0$ violate the constraint):

| $R_0$ | regime | $D_{\text{combined}}$ | excess over max | excess over sum |
|---|---|---|---|---|
| 0.20 | aligned | 0.401 | $-0.45$ | $-0.85$ |
| 0.20 | orthogonal | 0.456 | $-0.40$ | $-0.82$ |
| 0.20 | anti-aligned | 0.420 | $-0.43$ | $-0.83$ |
| 0.40 | aligned | 0.607 | $-0.41$ | $-0.81$ |
| 0.40 | orthogonal | 0.726 | $-0.29$ | $-0.71$ |
| 0.40 | anti-aligned | 1.257 | $+0.24$ | $-0.16$ |
| 0.60 | aligned | 1.157 | $-0.22$ | $-0.63$ |
| 0.60 | orthogonal | 1.439 | $+0.06$ | $-0.36$ |
| 0.60 | anti-aligned | 3.381 | $+2.00$ | $+1.60$ |
| 0.80 | aligned | 2.825 | $+0.48$ | $+0.08$ |
| 0.80 | orthogonal | 3.954 | $+1.61$ | $+1.19$ |
| 0.80 | anti-aligned | 7.221 | $+4.88$ | $+4.48$ |

### 4.3 What the experiment shows

**The Bregman triangle holds exactly.** This confirms the analytical structure of §3.4: the combined phantom decomposes via $D_{\text{filter}} = D_{\text{combined}} + D(\pi_{\text{final}} \| \pi_{\text{filter}}) + \lambda^*(R_{\text{true}} - R_0)$, with the cross-term sign and magnitude determined by the e-projection's Lagrange multiplier.

**Aligned is typically smallest; the strict three-way ordering does not hold uniformly.** The data above show that at *every* $R_0$ in the moderate-to-hard range, $D_{\text{combined}}^{\text{aligned}} \leq$ both alternatives, so aligned-is-smallest is robust here. **But the strict aligned ≤ orthogonal ≤ anti-aligned ordering fails even within this range.** At $R_0 = 0.20$, orthogonal is 0.456 while anti-aligned is 0.420, so orthogonal *exceeds* anti-aligned — the ordering at that point is aligned < anti-aligned < orthogonal. At $R_0 \geq 0.30$ the strict ordering does hold in this toy. At weak constraints ($R_0 \leq 0.15$), the ordering breaks more severely: anti-aligned can be *smaller* than aligned (anti-aligned = 0.280 vs aligned = 0.401 at $R_0 = 0.05$). Mechanism for the low-$R_0$ failure: when the constraint's reward target is close to the unconstrained baseline, $\lambda^*$ is small and the constraint barely moves the policy; meanwhile, the *anti-aligned filter* has already pushed policy in a direction that happens to put it closer to truth than the aligned filter does (which pushed in the same direction the constraint would have, over-correcting). The takeaway: the §3.4 aligned-is-smallest claim survives in the regime where the constraint actually does substantial work, but the strict three-way ordering doesn't, even in the base toy. The 240-configuration sweep (§4.5) shows aligned is the strict pointwise minimum in only 211/240 configurations even across this broader family.

**Super-additive compounding is real, but lives in the wrong place for the trilogy's argument.** The naive-sum threshold (combined $>$ filter + constraint) is crossed first by anti-aligned ($R_0 \approx 0.45$), then orthogonal ($R_0 \approx 0.65$), and aligned only crosses at $R_0 \approx 0.78$. The trilogy's claim that institutionally-aligned filter+constraint produces super-additive compounding is **refuted across the operational range of this toy**. Aligned configurations are typically the least compounding here, with the same mean/median caveat as for the smallest-total-error claim — strictly aligned-is-smallest holds in 211/240 of the broader sweep, not pointwise universally.

**The mechanism is the Lagrange multiplier $\lambda^*$.** The cross-term magnitude scales with $\lambda^*$, which measures how hard the constraint must pull to reach $R_0$ from $\pi_{\text{filter only}}$. Aligned filtering shrinks $\lambda^*$ (the filter has pre-done some of the constraint's work); anti-aligned filtering inflates $\lambda^*$ (the constraint must overcome the filter's opposite pull). The redundancy/compounding behavior of the combined system reduces to the behavior of $\lambda^*$ across alignment regimes, which is one-dimensional and computable.

### 4.4 Scope and what the experiment does not test

The toy uses single-reward RLHF with a reward depending only on $y$, full-capacity model (the m-extension is unconstrained beyond defaulting to reference), and naive m-extension. These are simplifications matching the m-flat constraint regime where Pythagorean is exact.

The experiment does not address:

- **Multi-reward or learned-reward constraints.** When the constraint manifold has curvature, the cross-term gains higher-order corrections and the Bregman triangle becomes a perturbative bound rather than an exact identity. Whether the alignment ordering survives is plausible but not verified here.
- **Architectural interpolation other than reference-default.** Real architectures interpolate non-trivially into $G$. The qualitative result depends on the m-extension being closer to truth on $\mathcal{X} \setminus G$ than on $G$, which is generic but not universal.
- **Filter and reward operating on different content dimensions.** The toy's "alignment" is one-dimensional (filter and reward both shape policy along the reward direction). For high-dimensional policy spaces, alignment becomes an angle in the Fisher metric, and partial alignment is the generic case. The qualitative ordering should generalize but the quantitative thresholds will shift.

What the experiment does establish: in the canonical single-reward RLHF setup with simple filtering, the trilogy's compounding claim is wrong, the corrected redundancy claim of §3.4 holds, and the mechanism is captured by the Lagrange multiplier behavior. This is a genuine technical correction with operational implications.

### 4.5 Robustness sweep on the alignment ordering

The §3.4 claim is that aligned ≤ orthogonal ≤ anti-aligned is the robust ordering of combined phantom magnitudes. The §IV experiment tested this in one toy (gaussian-shifted truth, linear reward, half-filter). A robustness sweep across 240 configurations — varying truth structure (gaussian shifted, bimodal, noisy, antipodal), reward shape (linear, quadratic, step, exponential), filter size (4, 6, 8, 10, 12 of 16), and constraint severity ($R_0$ at 0.3, 0.5, 0.7 of max reward) — gives:

| Comparison | Cases satisfied | Cases violated |
|---|---|---|
| aligned ≤ orthogonal | 222 / 240 | 18 |
| aligned ≤ anti-aligned | 223 / 240 | 17 |
| aligned is pointwise minimum | 211 / 240 | 29 |
| orthogonal ≤ anti-aligned | 159 / 240 | 81 |

**Aligned-is-most-redundant is robust on average, not pointwise.** An earlier version of this section (and the README) claimed aligned ≤ orthogonal and aligned ≤ anti-aligned hold *pointwise* across all 240 configurations. **This was wrong.** Aligned is the strict pointwise minimum in 211/240 = 88% of cases, with 29 violations. The mean-and-median statement holds: mean combined phantom is aligned 0.95, orthogonal 1.27, anti-aligned 1.61, with median ratios anti/aligned $\approx 1.28\times$ and ortho/aligned $\approx 1.18\times$. But "pointwise robust" overstates what the data show.

**The strict three-way ordering is not robust.** Orthogonal sometimes exceeds anti-aligned (81 cases), primarily for non-smooth rewards (step function) and small filter sizes. Mechanism: when the reward function is non-smooth, the "anti-aligned" filter doesn't differentiate among reward-tied inputs, and a random orthogonal selection can happen to pick a worse subset.

**Implication for the §3.4 claim.** The corrected claim is: aligned filter+constraint configurations produce the smallest combined phantom *in mean and median* across the tested family, with aligned ≤ orthogonal and aligned ≤ anti-aligned holding in roughly 92% of cases each, but **not pointwise universally**. The relative ordering of orthogonal vs anti-aligned depends on specifics (reward smoothness, filter size, constraint severity).

**Further conditional qualifier.** Even where aligned is the minimum, the result is conditional on a configuration the toy enforces: that filter and constraint both push policy *away* from $\pi_{\text{ref}}$ in the same direction (the constraint direction). When the filter happens to push policy *further* from truth than $\pi_{\text{ref}}$ does — for instance, if the filter excises inputs where truth would have been most informative against the constraint direction — adding the constraint can pull the policy *back toward* truth and *reduce* total error relative to filter-alone. This is the regime where the Lagrange multiplier $\lambda^*$ does corrective work rather than distortive work. The framework's diagnostic implication ("the constraint always makes things worse") is not what the math says. The constraint adds a specific KL displacement; whether that displacement increases or decreases the distance to truth depends on the geometric position of $\pi_{\text{filter}}$ relative to truth and the constraint manifold. Compounding is conditional, not guaranteed.

The trilogy-refuting result — institutional alignment typically produces *less* combined distortion than other configurations in the tested family — is robust in the mean-and-median sense across the regimes I tested. The "aligned-is-best" claim is robust only in that statistical sense; "best" is not pointwise universal even within the tested family, and "best among the three configurations tested" should not be confused with "best globally."

### 4.6 Implications for the diagnostic argument: what the experiment actually shows

I had originally claimed (in v1 and earlier in this v2) that aligned filter+constraint produces signatures observationally equivalent to a stronger version of either alone, so the user couldn't reverse-engineer which mechanism is operative. **A direct test of that claim, in the same toy, refutes it.**

For aligned filter+constraint at moderate $R_0$, the four relevant quantities $D(\pi_{\text{true}} \| \pi)$ for $\pi \in \{\pi_{\text{ref}}, \pi_{\text{filter only}}, \pi_{\text{constraint only}}, \pi_{\text{combined}}\}$ are materially different. At $R_0 = 0.4$:

- $D(\pi_{\text{true}} \| \pi_{\text{ref}}) = 0.80$
- $D(\pi_{\text{true}} \| \pi_{\text{filter only}}) = 0.40$
- $D(\pi_{\text{true}} \| \pi_{\text{constraint only}}) = 1.01$
- $D(\pi_{\text{true}} \| \pi_{\text{combined}}) = 0.61$

Removing the constraint (going from combined to filter-only) *recovers* $0.21$ KL units of truth. Removing the filter (going from combined to constraint-only) *adds* $0.41$ KL units of distortion. These are not indistinguishable; the asymmetry is informative.

The actual structure: in this toy the filter is **locally truth-preserving** (perfect on unfiltered inputs, default on filtered ones), while the constraint is **globally distorting** (pulls every input toward higher reward). The constraint is the larger contributor to combined distortion; the filter is a stabilizing background that limits the constraint's damage. Removing them produces asymmetric signatures.

The corrected operational claim:

- Removing the constraint reveals truth on inputs that weren't filtered, and the recovery is large in moderate regimes.
- Removing the filter exposes the constraint to operate on uniform reference, producing distortion across all inputs and worsening the result.
- The user observing the combined output and able to remove either component can identify which mechanism is doing more work and in what direction.

This is opposite to the trilogy's framing — which suggested the user is stuck — and opposite to my earlier framing — which suggested the signatures are indistinguishable. The framework, when actually pushed numerically, says nothing supports the diagnostic-difficulty claim. **What it does say**: aligned configurations produce the smallest *combined* phantom relative to alternatives, which is the redundancy claim of §3.4 and is verified. The diagnostic implications I tried to attach to that — about user inference and intervention removal — are not supported by the geometry, and the data refutes them.

This leaves a substantive question that the framework alone doesn't answer: in real systems, can the user remove either mechanism? The toy assumes counterfactual access (you can compute what filter-only would produce if you had the unfiltered training data, which you don't). In practice, removing the filter requires data the user doesn't have, while removing the constraint requires retraining without RLHF, which only the lab can do. The asymmetry of *operational* access to interventions is what may produce diagnostic difficulty in production — but that's a claim about deployment, not about the geometry.

### 4.8 Numerical companion for the four-object decomposition

§2.3 introduced the four-way decomposition with a structural argument. To honor the principle that the framework should be tested rather than asserted, I ran three numerical companions for it. The result reveals an additional correction beyond what §2.3 itself stated.

**Test 1: The abstract algebra (`test_four_objects.py`).** Two random orthogonal projections $P_Q, P_C$ in $\mathbb{R}^n$ with prescribed principal-angle squared-cosines $\beta_j$. For random $f \in \text{Range}(P_Q)$, all four formulas verified to within $10^{-15}$ across single-mode and multi-mode trials. Single-mode sweep: peak locations match prediction exactly. **The algebra is correct.**

**Test 2: A naive policy-space test (`test_four_objects_policy.py`).** First-pass operationalization: compute $\pi_{\text{trained}} = e\text{-proj}_\mathcal{C}(\pi_{\text{ref}})$, define "leakage region" as outputs outside both truth-support and reward-support. Three of four predictions matched qualitatively; leakage failed (rose monotonically with alignment instead of peaking at $\beta = 1/2$). I diagnosed this as a measurement-region issue: the "outside both supports" region is itself a function of alignment, contaminating the measurement.

**Test 3: A proper Fisher-tangent operationalization (`test_four_objects_pure.py`).** Take the unit truth direction $\hat{q} = (\pi_{\text{true}} - \pi_{\text{ref}})/\|\cdot\|$ in the Fisher tangent at $\pi_{\text{ref}}$; project it onto the 1-D constraint subspace spanned by the centered reward direction; measure the four objects directly as squared norms of components. This is *exactly* the setup the four-way formulas describe.

| Object | Predicted peak | Measured peak | Pearson $r$ on $\beta \geq 0$ branch |
|---|---|---|---|
| Retention | $\beta = 1$ | $\beta = 1.00$ | 1.0000 |
| Leakage | $\beta = 0.5$ | $\beta = 0.469$ | 1.0000 |
| Suppression | $\beta = 0$ | $\beta = 0.00$ | 1.0000 |
| Total error | $\beta = 0$ | $\beta = 0.00$ | 1.0000 |

**All four formulas hold to floating-point precision when computed on the geometric object the formulas describe.** Pearson correlations are 1.0000 across all four objects; max deviations are $\sim 10^{-16}$. The figure shows measured points sitting on theoretical curves with no visible deviation. (An earlier version of this section reported $r > 0.95$ — that was an artifact of using a signed-$\beta$ x-axis that created spurious asymmetry; with the standard convention $\beta = \cos^2\theta \in [0,1]$, the formulas are exact.)

**The fifth correction.** Tests 2 and 3 reveal something the document hadn't stated: the setup the four-way decomposition describes ("$f \in \text{Range}(P_Q)$, project onto $C$, measure components") is *not* the setup RLHF actually performs ("start from $\pi_{\text{ref}}$, e-project onto $\mathcal{C}$, measure deviation from $\pi_{\text{true}}$"). These are different projection problems.

The four-way formulas predict the geometry of a $P_Q$-element's projection onto $C$. They do not directly predict the geometry of $\pi_{\text{trained}} - \pi_{\text{ref}}$ as alignment varies, because $\pi_{\text{ref}}$ is not in $\text{Range}(P_Q)$ and the e-projection from outside is a different computation than the orthogonal projection of an element inside.

The trilogy and v1/v2 of this document both wrote down the formulas and implicitly assumed they apply to the training scenario. That assumption is unwarranted as stated. To bridge the gap, the framework needs either:

- **(Bridge A)** an argument that the trained policy can be approximated as $P_C \pi_{\text{true}}$ rather than as $e\text{-proj}_\mathcal{C}(\pi_{\text{ref}})$, in some regime. This is what would happen if the constraint dominated the reference, which is not the standard RLHF regime. *Status: open.*
- **(Bridge B)** a separate four-object reorganization for the e-projection-from-reference setup, with scalar laws stated for that geometry. *Status: reorganized in Appendix B and partially tested in `test_bridge_B.py`.* The four scalar identities are inner-product algebra given the assumption $g = \mu c$; the empirical content is whether $g \approx \mu c$ on actual e-projection, which holds at first order in $\lambda$ (Amari–Nagaoka §3.2). Test 4 in `test_bridge_B.py` (joint sweep of $R_0$ and reward direction) reports Pearson $r \approx 0.98$ and regression slopes deviating from 1 by 15–25% — the magnitude error envelope set by the unmodeled second-order term derived in §B.5 and verified in `test_second_order.py`. Earlier rounds reported "$r \approx 0.996$" from Test 3 (fixed $R_0$, swept reward direction); that test holds $\mu$ approximately constant and is therefore mostly a check of $s$-shape — it does not exercise the joint $(\mu, s)$ prediction. Bridge B replaces the four-way scalar laws $\beta^2, (1-\beta)^2, \beta(1-\beta), 1-\beta$ with $\mu^2 s^2, (a-\mu s)^2, \mu^2(1-s^2), a^2+\mu^2-2 a \mu s$ — depending on signed cosine $s = q\cdot c$, truth magnitude $a$, and signed displacement coordinate $\mu$, rather than just on $\beta = s^2$.

Bridge B was sketched by the external reviewer in round 8 of this conversation's correction sequence; the verification I ran initially showed apparent first-order agreement, but round 11 surfaced that the agreement was a constant-$\mu$ artifact and the first-order prediction has a 15–25% magnitude error on real e-projection. With this caveat, Bridge B is a useful reorganization that connects the pure-projection four-object structure to the e-projection-from-reference setup; it is not a derivation in the strong sense earlier drafts framed it as.

**Summary of what's verified:**

- The four-way algebra (pure projection) is exact (Test 1, machine precision).
- The four-way algebra applied to its proper geometric setup is exact in policy space (Test 3, $r = 1.0000$ for all four objects, max deviation $\sim 10^{-16}$).
- The four-way formulas applied directly to RLHF were the wrong setup; Bridge B's setup-specific reorganization matches RLHF e-projection in shape ($r \approx 0.98$) but with 15–25% magnitude error from second-order curvature (Test 4 in `test_bridge_B.py`).

The four-way decomposition is now exactly verified for pure projection and approximately verified (first-order) for the RLHF setup with a quantified error envelope. That's a more honest status than at any prior point.

### 4.9 Honest accounting of what's been claimed and refuted

This conversation has produced eleven substantive corrections, layered as follows:

1. **Trilogy claim:** "Aligned filter+constraint compound super-additively" — *refuted* (§4.2).

2. **My v1 reformulation claim:** "Aligned configurations are redundant; orthogonal configurations compound super-additively" — *partially refuted* (§4.5).

3. **My v2 reformulation claim:** "Aligned filter+constraint produces signatures observationally indistinguishable from a stronger version of either alone" — *refuted* (§4.6).

4. **Universal energy law $\beta(1-\beta)$, in both the trilogy and my v1/v2:** This formula is the *leakage* law, not a universal phantom law; the framework conflates four distinct objects under one formula. *Structurally refuted at the algebra level* (§2.3 and Test 1 in §4.8, machine precision).

5. **The "operationalization problem" framing I introduced in v3 of §4.8:** I claimed leakage failed in policy space because the translation from tangent-orthogonal-complement to output-region was unsolved. The actual issue was setup-mismatch. *Refuted by Test 3* — the formulas hold to numerical precision when applied to their proper setup.

6. **The implicit claim that the four-way formulas apply to RLHF training distortion:** The four-way formulas predict the geometry of $P_C f$ for $f \in \text{Range}(P_Q)$. RLHF computes $e\text{-proj}_\mathcal{C}(\pi_{\text{ref}})$, where $\pi_{\text{ref}} \notin \text{Range}(P_Q)$. *Status changed at round 8 and again at round 11*: Bridge B (Appendix B) provides a first-order Fisher-tangent reorganization for the RLHF setup. The pure-projection formulas remain inapplicable; the Bridge B formulas match the RLHF e-projection in shape ($r \approx 0.98$ on the joint sweep) with regression-slope deviations of 15–25% from 1, attributable to second-order curvature (round 11 reframing — see §B.5).

7. **Black Nazi case as a worked example of the four-object decomposition (§2.4):** I had treated the case as suppression $\approx 1$, leakage $\approx 0$, etc., applying the four-way formulas directly — same setup-mismatch error. The corrected reading places the case in framework-1 (RLHF e-projection) with the framework's verified prediction being large total error at high $\lambda^*$.

8. **ChatGPT review (this round):** Identified four further issues, each of which corrected something specific:
   - **Signed-beta artifact in `test_four_objects_pure.py`.** The script used `beta = cos² × sign(cos)` with a signed x-axis, creating spurious deviation that I had reported as $r > 0.95$. With the standard convention $\beta = \cos^2\theta \in [0,1]$, the formulas hold to $r = 1.0000$ and max deviation $\sim 10^{-16}$. The earlier number understated the result — the policy-space verification of the four objects on their proper setup is exact, not approximate.
   - **§4.5 "240 / 240" claim.** I had reported aligned ≤ orthogonal in 240/240 cases; the actual numbers are 222/240 and 223/240. Aligned is the strict pointwise minimum in 211/240, not 240/240. The corrected statement is "robust on average and median, with ~88% pointwise."
   - **Hard-coded paths in scripts.** Reproducibility issue — scripts used `/mnt/user-data/outputs/` literally. Replaced with `Path(__file__).resolve().parent`.
   - **Bregman triangle verification was misattributed.** I had cited `visualize_redundancy.py` as verifying the triangle to machine precision; the residual check actually lived in `SUPERSEDED_redundancy_test_v1.py`. Moved the check into the active script. Verified to $1.88 \times 10^{-13}$.
   
   And — most importantly — **Bridge B is now derived and verified.** ChatGPT sketched the first-order Fisher-tangent decomposition for the e-projection-from-reference setup: $\|Pg\|^2 = \mu^2 s^2$, $\|f-Pg\|^2 = (a-\mu s)^2$, $\|(I-P)g\|^2 = \mu^2(1-s^2)$, $\|f-g\|^2 = a^2 + \mu^2 - 2 a \mu s$, where $\mu$ is the signed tangent-displacement coordinate along the constraint direction. I verified these in `test_bridge_B.py`: algebraic identities hold to machine precision when $g = \mu c$ is assumed; Pearson $r \approx 0.996$ when applied to actual e-projection from a uniform reference. The deviations are explained by an explicit second-order term in the exponential-tilt expansion (§B.5, verified in `test_second_order.py`): $\pi_\lambda = \pi_0 + \lambda \pi_0 \tilde r + \frac{\lambda^2}{2}\pi_0(\tilde r^2 - \mathbb{E}_{\pi_0}[\tilde r^2]) + O(\lambda^3)$, with the second-order direction non-parallel to the centered reward (cosine 0.157 in the test toy). **This converts round 6 from "Bridge B is open" to "Bridge B's first-order Fisher-tangent version is solved; the explicit second-order term is identified; the global KL-geometry version with second-order corrections folded in remains open."** See Appendix B.

9. **ChatGPT review (third pass).** Identified four classes of remaining issues plus one substantive new result.
   - **Three script bugs** in the shipped artifacts: the diagnostic script's sign-interpretation text was inverted ("Negative = improved" should be "Positive = improved"); `visualize_redundancy.py` labeled the orthogonal filter baseline as "filter alone (any)" when it's specifically the orthogonal one; the m-sign convention in `test_bridge_B.py` allowed negative magnitudes silently. All three fixed.
   - **§4.3 stale claim** that aligned ≤ orthogonal ≤ anti-aligned holds at every $R_0$ tested. Verified that this fails at low $R_0$ (≤ 0.15) in the base toy: anti-aligned can have *smaller* combined KL than aligned when the constraint is weak enough that $\lambda^*$ doesn't dominate the geometry. §4.3 narrative corrected.
   - **Notation cleanup.** Bridge B's $m$ (which I'd been treating as both "magnitude" and "signed displacement, can be negative" in different places) replaced with signed $\mu$ throughout, with $m = |\mu|$ reserved for magnitude. "Retention" renamed to "query-direction output energy" in Bridge B contexts to avoid implying preservation when $\mu s < 0$.
   - **§B.4 leakage monotonicity** caveat added: $\mu^2(1-\beta)$ is monotone in $\beta$ only at fixed $\mu$; in actual e-projection $\mu = \mu(R_0, r, \pi_{\text{ref}})$ varies with the configuration.
   - **Part VI rewrite.** All three flavor descriptions had specific overclaims: "first-moment phantoms become first-order *KL* biases" conflated linear-in-displacement biases (correct) with linear KL costs (KL is *quadratic* near the diagonal); "second-moment phantoms" applied to "any quadratic functional" was too broad (entropy isn't quadratic); "eigenstructure phantoms have principal directions set by the constraint normal" was too clean (the actual first-order Fisher perturbation is a third-moment tensor contracted with centered reward in exponential-family cases, and architecture-dependent in general). Each rewritten with the correct mathematical content.
   - **§2.2 KL formula** generalized: the partition-function term is $\mathbb{E}_{x \sim \nu}[\log Z_x(\lambda^*)]$, with the $x$-expectation explicit for general (non-output-only) rewards.
   - **Black Nazi mechanism** softened from "the most likely dominant mechanism is objective distortion via reward modeling" to "the case is illustrative of what the framework predicts in this regime, not diagnostic of which production mechanism produced the observed behavior." Causal claims about reward modeling vs prompt rewriting vs corpus curation as the production mechanism need primary-source evidence the document does not have.
   - **Part VIII** "absence of numerical companions" rewritten; the gap is no longer that gap, it's empirical contact with production systems.
   - **Appendix A heading** added (the reviewer's step-summary list had been appearing without a header). Step 8 and Step 11's "Final state" updated to reflect Bridge B being derived; original wordings preserved in brackets.
   - **Ledger entries** updated: aligned-comparison line now reports the correct 211/240, 222/240, 223/240 numbers; Black Nazi line says fine-grained texture is now supplied by Bridge B at first order; Pythagorean ledger entry tightened to active boundary $\partial\mathcal{C}$; Bregman triangle precision corrected from $10^{-14}$ to actual $1.88 \times 10^{-13}$.
   - **Substantive new result: explicit second-order term in the e-projection expansion.** ChatGPT pointed out that the deviations in `test_bridge_B.py` Test 3 weren't vague "simplex curvature" but had an explicit form: $\pi_\lambda = \pi_0 + \lambda \pi_0 \tilde{r} + \frac{\lambda^2}{2}\pi_0(\tilde{r}^2 - \mathbb{E}_{\pi_0}[\tilde{r}^2]) + O(\lambda^3)$, with the second-order term pointing along the *centered square* of the reward, *not* parallel to the centered reward. I verified this in `test_second_order.py`: first-order error scales exactly as $\lambda^2$, second-order error exactly as $\lambda^3$, and the cosine between the second-order direction and the centered reward is 0.157 (so genuinely non-parallel). The 12-15% relative deviations in Bridge B Test 3 (on the two substantive non-near-zero quantities) are this second-order term. The path to a global KL-geometry version of Bridge B now has a concrete starting point.

10. **ChatGPT review (fourth pass) — synchronization.** Identified residual sync issues that survived rounds 8 and 9, no new mathematical content needed.
    - **§4.3 ordering claim corrected** to identify the actual base-toy regime: aligned-is-smallest holds at every $R_0$ in the tested range, but the strict three-way ordering aligned ≤ orthogonal ≤ anti-aligned fails at $R_0 = 0.20$ (where orthogonal = 0.456 exceeds anti-aligned = 0.420). At $R_0 \geq 0.30$ the strict ordering holds in this toy; below that, it doesn't. Verified by direct re-run.
    - **"Consistently the least compounding" softened** to "typically the least compounding here, with the same mean/median caveat as for the smallest-total-error claim — strictly aligned-is-smallest holds in 211/240 of the broader sweep, not pointwise universally."
    - **Bridge B Test 3 relative-error claim corrected**: the "15-19%" figure conflated relative errors on substantive quantities (12% and 15%) with relative errors on the two near-zero quantities (50× and 1.0, both artifacts of the denominator approaching zero). Document now reports both kinds and explains the asymmetry.
    - **Fisher vs Euclidean coordinate convention clarified** in new §B.7. For uniform $\pi_0$, Fisher and Euclidean inner products differ by a constant factor $N$, and Bridge B's dimensionless test outputs (Pearson $r$, recovery condition) are invariant under this scaling. For non-uniform $\pi_0$, Bridge B's identities should be re-derived in score coordinates with the Fisher metric; the current numerical verification only exercises the uniform case.
    - **Dead `signed_cos` variable removed** from `test_four_objects_pure.py`.
    - **Round 9 entry rewritten** to be honest about what was actually done in round 9 vs what was claimed; the previous version of that paragraph announced fixes that hadn't yet been applied.

11. **External-reviewer pass (Claude Opus 4.7) — Bridge B Test 3 was a constant-$\mu$ artifact.** The headline "$r \approx 0.996$" from `test_bridge_B.py` Test 3, presented in rounds 8–10 as evidence of Bridge B's first-order accuracy on real e-projection, did not test what it claimed. The reviewer ran the script under its own conditions and observed that $|\mu|$ varies by only ~3% across the swept reward direction (from 0.165 to 0.170), while $|s|$ varies over [0.025, 1.000]. The Pearson correlation in this regime is therefore measuring how well Bridge B captures the $s$-shape with $\mu$ approximately fixed — not the joint $(\mu, s)$ prediction the document credits it with. With $\mu$ pinned at its mean, the resulting Bridge B prediction has $r = 0.99989$ with the real Bridge B prediction across the same sweep; the two are indistinguishable at Test 3's resolution.
    - **Test 4 added.** Sweep $R_0 \in [0.2, 0.85]$ jointly with reward direction. This drives $|\mu|$ over [$6 \times 10^{-4}$, 0.49] (~800-fold variation) and $|s|$ over [0.04, 1.00], so the joint prediction is exercised. Reporting Pearson $r$, regression slope, and relative-error percentiles on 240 configurations: $r \approx 0.98$, slopes deviating from 1 by 15–25% with a consistent sign pattern (over-prediction of the query-aligned components, under-prediction of the perpendicular components), median relative error 2–31% with p90 in the 23–93% range. The slope sign pattern is exactly what the §B.5 second-order term predicts qualitatively — actual $\|g\|^2 > \mu^2$ because $g$ has a perpendicular component, so leakage and total tangent error are under-predicted, and the corresponding reduction in $(g \cdot q)^2$ relative to $\mu^2 s^2$ over-predicts the query-aligned content.
    - **§B.5 rewritten** to retract the "12-15% relative error" headline framing and report the joint-sweep numbers (15–25% magnitude error envelope on real e-projection). The old Test 3 is preserved in the script with an explicit caveat printout.
    - **§B.6 rewritten** to be honest about what Bridge B is. The four identities are inner-product algebra given $g = \mu c$ — law of cosines plus one orthogonal decomposition. The information-geometric content is the single (textbook) fact that e-projection of $\pi_0$ onto an m-flat constraint moves along the centered sufficient-statistic direction at first order in $\lambda$. Earlier framing as a substantive "derivation" oversold what's there. The accurate framing is: a clean reorganization that connects the pure-projection four-object structure to the e-projection-from-reference setup, with a quantified 15–25% magnitude-error envelope.
    - **§B.2 amended** with an explicit note that the four identities are inner-product algebra and not new mathematics.
    - **§2.4 "distinctive testable prediction" framing softened.** The toy framework predicts $\mu^2$-scaling for off-query leakage; turning that into a real-system test faces several unaddressed obstacles (no isolated constraint direction in real RLHF; the loss-function KL coefficient does not equal the m-flat constraint severity except at the optimum; "off-query behavior" lacks an operational definition for an LLM; $\mu$ is not directly observable). The prediction stands at toy level; bridging to production has not been done.
    - **§4.8, §VII, §IX (Status Ledger), §X (Development Record), and the README** updated for consistency with the round-11 numbers and framing.

What survives across all eleven rounds:

- The four-way algebra is exact. Verified to machine precision in projection space (Test 1) and in proper policy-space operationalization (Test 3 of `test_four_objects_pure.py`, $r = 1.0000$, max deviation $\sim 10^{-16}$).
- The Bregman triangle identity and cross-term formula $\lambda^*(R_{\text{true}} - R_0)$ are exact in the m-flat regime and verified ($1.88 \times 10^{-13}$ residual in `visualize_redundancy.py`).
- Aligned configurations produce the smallest *total error* in mean and median across the tested family (211/240 pointwise, 88%; 222/240 with aligned ≤ orthogonal; 223/240 with aligned ≤ anti-aligned), with the conditional qualifier of §4.5 about which configurations the toy enforces.
- The qualitative framework-1 prediction — that the trained policy is displaced far from truth in KL when truth is approximately orthogonal to a hard constraint — applies to the Black Nazi case at the qualitative level.
- The framework's spine — two-projection geometry, four-way decomposition, Pythagorean-Bregman identities — is a correct mathematical framework for the projections it describes.
- **Bridge B as reorganization** (not derivation) holds: the four scalar laws $\mu^2 s^2, (a-\mu s)^2, \mu^2(1-s^2), a^2 + \mu^2 - 2 a \mu s$ are inner-product algebra given $g = \mu c$, and the first-order e-projection fact $g_\lambda \approx \lambda \pi_0 \tilde r$ is standard (Amari–Nagaoka §3.2). On real e-projection: $r \approx 0.98$ with 15–25% magnitude error from the second-order curvature term.
- The explicit second-order term in the e-projection expansion is identified and its non-parallelism to centered reward is verified, accounting for the magnitude error in Bridge B's first-order prediction.

What does *not* survive:

- The headline "Bridge B's first-order Fisher-tangent version is solved with $r \approx 0.996$ on real e-projection." The honest version is "$r \approx 0.98$ on shape, slope deviations 15–25% from 1, attributable to the unmodeled second-order term." Test 3's "$r \approx 0.996$" was a constant-$\mu$ artifact.
- The framing of Bridge B as a substantive derivation. Once the first-order e-projection fact (textbook) is granted, the four identities are law of cosines.
- The full *KL-geometry* analog of Bridge B with the second-order term folded into the four-object decomposition. The first-order Fisher-tangent reorganization is in; the second-order version is identified in form ($\frac{\lambda^2}{2}\pi_0(\tilde{r}^2 - \mathbb{E}_{\pi_0}[\tilde{r}^2])$) but not yet propagated through the four scalar laws.
- All operational claims that depended on applying the four-way formulas in their pure-projection form to RLHF (compounding-super-additively, diagnostic indistinguishability, etc.).
- The fine-grained reading of the Black Nazi case as suppression $\approx 1$, leakage $\approx 0$ via the *pure-projection* formulas. With Bridge B, the case predicts $\mu^2(1-s^2) \approx \mu^2$ leakage at $s \approx 0$ — the right shape with $\mu$ as the constraint-severity parameter, modulo the toy-to-production gap and the 15–25% magnitude envelope.
- "Bridge B's $\mu^2$-leakage is the framework's most distinctive currently-available testable prediction" — true at toy level; the real-system test has unaddressed operational obstacles described in §2.4.
- Causal claims about the operative production mechanism in the Black Nazi case. The geometry is consistent with multiple mechanisms; discriminating among them needs primary-source evidence.

The pattern across eleven rounds: each correction was at a level the previous ones didn't reach.

- Round 1 (previous reviewer): meta-level overselling and post-hoc framing.
- Round 2 (operational, redundancy): a specific framework prediction failed numerically.
- Round 3 (operational, diagnostic): another specific framework prediction failed numerically.
- Round 4 (ChatGPT, algebra): the underlying scalar law conflated four objects.
- Round 5 (operationalization framing): I misidentified a measurement failure as a translation problem.
- Round 6 (geometric setup): the framework's formulas describe a different projection problem than RLHF performs.
- Round 7 (case mapping): the four-object formulas don't apply to specific cases without Bridge B.
- Round 8 (ChatGPT, second pass): signed-beta artifact, reproducibility issues, misattributed verification, sweep-numbers misstatement, and the *reorganization* of Bridge B (overstated as "derivation" in rounds 8–10; corrected in round 11).
- Round 9 (ChatGPT, third pass): script-level bugs in the shipped artifacts, several stale prose claims that hadn't tracked the round-8 corrections, the m→μ notation cleanup, Part VI rewrite, and the explicit second-order term in the e-projection expansion.
- Round 10 (ChatGPT, fourth pass): synchronization-only — fixed §4.3 base-toy ordering claim, "consistently" softened to "typically/in mean and median", Bridge B Test 3 relative-error claim corrected to distinguish substantive from near-zero quantities, Fisher vs Euclidean coordinate convention spelled out in new §B.7, dead variable removed from `test_four_objects_pure.py`, round-9 entry rewritten to be honest about what was actually done.
- Round 11 (Claude Opus 4.7): the Test 3 result that rounds 8–10 had been treating as headline empirical evidence was a constant-$\mu$ artifact. New Test 4 reports the actual joint-sweep numbers (slope deviations 15–25%); §B.5/§B.6 rewritten; "derivation" framing of Bridge B downgraded to "reorganization"; "distinctive testable prediction" framing softened with explicit toy-to-production gap; round 8's claim language amended.

Rounds 8 and 9 each added a derived result (Bridge B and its second-order correction) on top of substantial bookkeeping fixes; round 11 then revealed that the empirical evidence for Bridge B's headline accuracy was weaker than reported and downgraded the "derivation" language to "reorganization." Round 10 was synchronization-only. The earlier rounds were strict narrowing; round 8 introduced a result that round 11 has now partially walked back; round 11 also added pure cleanup. The framework now has fewer overclaims than at any prior point — in particular, the headline empirical claim about Bridge B is the honest joint-sweep result rather than the constant-$\mu$ artifact.

The previous reviewer was right that the framework was "rigorous redescription" rather than predictive engine. ChatGPT was right four times (rounds 4, 8, 9, 10). Claude Opus 4.7 (round 11) was right that Test 3 didn't test what it claimed and that Bridge B's framing as a "derivation" was overselling. My own analysis was repeatedly wrong on operationalization framings, the Black Nazi mechanism, the direct applicability of pure-projection formulas, the precise robustness numbers, the signed-beta convention, the m-sign convention, the relative-error figures, *and* the constant-$\mu$ artifact in Test 3 that survived three rounds of post-hoc reviewer correction without being noticed, plus the framing of Bridge B as a derivation rather than a reorganization. The remaining claims — the algebraic spine, the §IV redundancy result, the qualitative framework-1 prediction, Bridge B as reorganization with a 15–25% magnitude error envelope, and the second-order term — are what's currently defensible.

---

## Part V — Statistical Phantoms: What Carries Through

The statistical phantoms case (signal processing, CMB, LIGO, fMRI) was the trilogy's strongest. It survives the information-geometric reformulation with minor modifications.

### 5.1 The Hilbert case is the Fisher-tangent case

For Gaussian processes, the Fisher metric on the parameter manifold of mean and covariance reduces (in the mean-only direction, with fixed covariance) to the Mahalanobis inner product weighted by the inverse covariance. For white-noise-dominated Gaussian observations with known covariance, this is L² up to a fixed positive-definite scaling. The Hilbert framework's results in the spatial-gap case carry over without modification when reinterpreted as Fisher-metric statements on Gaussian distributions.

The Frobenius identity $\langle T, ARA^*\rangle_F = \langle A^*TA, R\rangle_F$ that gave the effective template $A^*TA$ is unchanged. The Brillinger-type variance formula is unchanged. The non-uniform false-alarm rate is unchanged.

What does change: the framework now extends naturally to non-Gaussian likelihoods via the appropriate Fisher metric. For Poisson observations (gamma-ray detection, photon counting), for binary observations (event detection), for heavy-tailed observations (where Gaussian approximations fail), the same operator-theoretic skeleton applies with the appropriate Fisher metric replacing L². The corrections are computable.

### 5.2 Permutation tests and the Fisher null

The Hilbert framework's discussion of permutation-test inheritance is also unchanged in form, but in information geometry permutation tests get a clean interpretation: they are **bootstrap estimates of the e-flat tangent direction** at the null hypothesis, with the mask geometry determining the orientation of that tangent space relative to the alternative.

This isn't new content; it's a cleaner way to state the same thing.

---

## Part VI — Three-Flavor Classification, Reformulated

The "first-moment, second-moment, eigenstructure" classification of the original framework maps to information-geometric flavors, but each flavor needs more careful statement than earlier drafts gave it. An earlier version of this Part overclaimed in three specific ways; corrected versions follow.

**First-moment phantoms.** *Earlier draft:* "first-order KL biases that scale linearly with the magnitude of $\pi_{\text{true}} - \pi_{\text{ref}}$." This conflated two scalings. KL is locally quadratic near the diagonal: for small displacement $\delta\pi$,
$$D(\pi \| \pi + \delta\pi) = \tfrac{1}{2}\|\delta\pi\|_F^2 + O(\|\delta\pi\|^3),$$
so KL is *second-order* in displacement, not first-order. What is *first-order* is the bias in mean parameters, scores, logits, or sufficient statistics — quantities linear in the policy. The corrected statement: first-moment phantoms appear as first-order biases in expectation-parameter coordinates of the policy (e.g., $\mathbb{E}_\pi[\phi]$ for sufficient statistic $\phi$), with the *induced KL cost* of those biases being second-order. Bridge B (Appendix B) makes this concrete: the trained displacement $\mu c$ is first-order in $\lambda^*$, and the resulting KL is second-order in the displacement.

**Second-moment phantoms.** *Earlier draft:* "any quadratic functional of $\pi$ acquires a bias scaling with the Fisher inner product of the constraint normal with itself." Too broad. Variance and covariance functionals are quadratic, so this works for them. Entropy is *not* quadratic — it has first-order Taylor terms away from the uniform distribution, and the leading contribution depends on whether the operating point is near uniform. Other smooth functionals each need their own Taylor expansion. The corrected statement: second-moment phantoms live in the Hessian/quadratic terms of smooth policy functionals — variances, covariances, squared statistics — where the leading dependence on small policy displacement is bilinear in the displacement. For nonlinear functionals like entropy, whether the second-order term dominates depends on whether the first variation vanishes at the operating point; in general it does not, and the expansion has both first- and second-order contributions that must be separated case by case.

**Eigenstructure phantoms.** *Earlier draft:* "rotations of the Fisher information matrix's eigendirections, with principal directions set by the constraint normal in the Fisher metric, given by $F(\theta^*) F(\theta)^{-1}$." This is too clean for the actual mechanism. For exponential-family tilts, the first-order Fisher perturbation under a reward tilt has the form
$$\delta F_{ij} \approx \lambda^* \, \mathbb{E}_{\pi_{\text{ref}}}[\phi_i \phi_j (r - \mathbb{E}[r])] - (\text{centering})$$
which is a *third-moment* tensor of the sufficient statistics contracted with the centered reward — not a rank-one rotation along the constraint normal, and not generally diagonalizable into a clean "principal directions = constraint normal" picture. For neural policies with non-exponential-family parameterizations, the relationship between the constraint and Fisher eigendirections passes through architecture-dependent reparameterization and is even less direct. The corrected statement: in simple exponential-family settings, the Fisher perturbation under a reward tilt is computable from the third-moment tensor of sufficient statistics contracted with the centered reward; in general parametric families, Fisher eigendirection rotation under constrained training is an empirical matter and is not determined by the constraint normal alone.

The trilogy's three-flavor classification is therefore preserved as a useful taxonomy but with sharpened mathematical content: first-moment biases are linear in displacement (with quadratic KL cost), second-moment biases are bilinear in displacement (in genuinely quadratic functionals; nonlinear functionals require case-by-case Taylor analysis), and eigenstructure biases follow from third-moment tensor contractions in exponential-family cases and from architecture-specific behavior in general. The disconfirmer protocols of the original document — measuring score biases, variance perturbations, principal-direction rotations — remain as appropriate measurements; what changes is the framework's prediction for *what those measurements should reveal*. None of the three flavor predictions has been numerically tested in this document; that is the natural next round of work after Bridge B.

---

## Part VII — What This Fixes

Concrete improvements over the trilogy as written, with regimes of validity stated:

**The RLHF constraint step has an exact KL formulation in the canonical case.** The Hilbert framework requires linearizing the constraint manifold's tangent space at $\pi_{\text{trained}}$ and treating the result as a closed subspace. Information geometry replaces this, for single-reward m-flat constraints, with the exact closed-form e-projection $\pi^*(y|x) \propto \pi_{\text{ref}}(y|x) e^{\lambda^* r(x,y)}$ and the boundary-Pythagorean identity $D(\pi \| \pi_{\text{ref}}) = D(\pi \| \pi^*) + D(\pi^* \| \pi_{\text{ref}})$ for $\pi \in \partial\mathcal{C}$. This is exact, not asymptotic.

**The fine-grained four-object structure for RLHF is now reorganized at first order (Bridge B).** The four-object decomposition $\beta^2, (1-\beta)^2, \beta(1-\beta), 1-\beta$ that lives in Hilbert/Fisher-tangent geometry on the pure-projection setup does not directly apply to RLHF (different projection problem, see §4.8). Bridge B (Appendix B) is the analogous reorganization for the e-projection-from-reference setup, with scalar laws $\mu^2 s^2, (a-\mu s)^2, \mu^2(1-s^2), a^2+\mu^2-2 a \mu s$ depending on the signed displacement coordinate $\mu$, the truth magnitude $a$, and the signed cosine $s = q \cdot c$. The four identities are inner-product algebra given $g = \mu c$; the modeling step is the textbook fact that $g_\lambda \approx \lambda \pi_0 \tilde r$ to first order in the Lagrange multiplier (Amari–Nagaoka §3.2). On real e-projection from uniform reference: shape Pearson $r \approx 0.98$, regression slopes deviating from 1 by 15–25% (Test 4 in `test_bridge_B.py`), with the magnitude error attributable to the explicit second-order term $\frac{\lambda^2}{2}\pi_0(\tilde r^2 - \mathbb{E}_{\pi_0}[\tilde r^2])$ identified in §B.5. The full *KL-geometry* analog with the second-order term folded into the four scalar laws remains open.

**Capacity is defined as Fisher dimension; its scaling is not derived.** Fisher dimension of the model manifold replaces "effective capacity" as a precisely-defined quantity. The capacity-bandwidth correspondence remains a conjecture by analogy, not a theorem (see §3.2 retraction). Fisher rank is not bandwidth in any derived sense.

**The framework natively handles distributional outputs.** LLM outputs are distributions on tokens, not vectors in a Hilbert space. Information geometry is the natural ambient framework. The L² treatment was forcing this is a structural improvement that does survive.

**The trilogy's compounding claim is refuted; the corrected version is conditional.** Aligned filter+constraint produces the smallest *total error* in the toy family tested, in mean and median (verified across 240 configurations). It is *not* pointwise universal — 29 of 240 cases violate the strict aligned-is-minimum claim, primarily for non-smooth rewards. And even the aligned-is-least result is conditional on a configuration where filter and constraint both push policy in the constraint direction; when the filter happens to push policy further from truth than reference does, the constraint can pull back toward truth and reduce error. Compounding is conditional, not guaranteed.

**Some disconfirmers become measurable.** KL divergence between trained models with different constraints, Fisher information matrix eigenstructure changes under constrained training — these are computable from black-box access to the model's output distributions. **However**: the v2 claim that aligned filter+constraint produces "observationally indistinguishable" signatures, so the user can't tell which mechanism is operative, was refuted by direct numerical test (§4.6). Removing each component produces materially different and informative signatures. The framework's disconfirmability is partial and case-dependent, not categorical.

---

## Part VIII — What This Doesn't Fix

The information-geometric reformulation does *not* address:

**The empirical question of what $\mathcal{C}$ is.** Whether RLHF imposes a sharp constraint, a soft penalty, a multi-component reward — these are empirical questions about specific training pipelines. The framework provides geometric machinery to *describe* the constraint once specified; it does not determine the constraint from first principles. This was true in the L² framework and remains true.

**Post-hoc mapping of observed phenomena.** The original documents map specific observed model behaviors (Black Nazi soldiers, refusal patterns, etc.) onto the framework's flavors. This mapping was identified in the development records as "partly post hoc," and that critique stands. Upgrading the mathematics doesn't make the post-hoc identification predictive.

**The remaining gap in numerical companions.** Earlier drafts of this section described "the absence of numerical companions" as the central methodological problem. After eight rounds of correction this is no longer accurate. The current package includes verified companions for: the four-way projection algebra, the pure policy-space projection, the failure of the bad KL decomposition, the corrected Pythagorean identity, the Bregman triangle identity for filter+constraint composition, the redundancy/compounding result and its 240-configuration robustness sweep, the diagnostic-asymmetry refutation, and Bridge B (with its second-order expansion verified separately).

What's still missing is *not* "synthetic numerical companions" but two more specific things: synthetic companions for the parts of the framework that haven't been tested yet (data-hole interpolation behavior across architectures, eigenstructure rotation under constrained training, Bregman triangle in curved-constraint / multi-reward regimes), and *empirical contact with production systems* — every framework prediction tested in this document has been on a synthetic toy. None has been measured against actual model outputs. Bridge B's prediction that off-query leakage scales with $\mu^2$ rather than $\beta(1-\beta)$ is the most distinctive *toy-level* testable claim available; turning it into a production-system test faces the obstacles described in §2.4 (no isolated constraint direction in real RLHF; loss-function KL coefficient ≠ m-flat constraint severity except at the optimum; "off-query behavior" lacks an operational definition for an LLM; $\mu = \lambda^*\|\tilde r\|_F$ is not directly observable). None of these obstacles is fatal, but none has been worked out in this document; the toy-to-production gap remains the genuine empirical work.

**The institutional alignment claim.** The original document's claim that filter and constraint are typically aligned by the same institutional incentives is sociological, not mathematical. Information geometry corrects the *consequence* of alignment (redundancy, not compounding) but does not provide any handle on the *premise*. That's not a math problem.

**Curvature corrections in highly non-flat regions.** The framework's predictions are exact when the relevant submanifolds are e-flat or m-flat with respect to the dual connections. For RLHF with multi-component rewards, complicated reward models, or KL-budgeted training (the realistic case), the constraint manifold has substantial curvature and the cross-curvature term $\mathcal{R}_{fc}$ in §3.4 becomes the dominant correction. **No explicit curvature bounds are derived in this document.** In principle, curvature corrections should be expressible as Bregman remainder terms or contractions of the Amari–Chentsov tensor with the constraint normal, and Davis–Kahan-style analogs may be available for Fisher eigenspaces — but explicit formulas, verified bounds, and synthetic verifications are not provided here. Treating multi-reward/curved-constraint corrections quantitatively requires that work; the framework currently only flags it as the regime where the flat-case identities cease to be exact.

---

## Part IX — Status Ledger

| Claim | Status | Notes |
|---|---|---|
| Universal energy law $\beta(1-\beta)$ as single scalar law for "phantom" | [F] | Structurally falsified §2.3. The formula is the *leakage* law; the framework conflates four distinct objects (retention, suppression, leakage, total error). Verified to machine precision in `four_way_decomposition.py`. |
| Four-object decomposition: $\beta = \beta^2 + \beta(1-\beta)$ (output) and $1-\beta = (1-\beta)^2 + \beta(1-\beta)$ (error), per mode | [V] | Two linked decompositions, not a single partition of unity. Leakage $\beta(1-\beta)$ appears in both because it sits both in the projected output and in the error. Verified to machine precision in `four_way_decomposition.py` and `test_four_objects.py`. |
| Active single-reward constrained KL problem is e-projection onto an m-flat equality boundary | [E] | Direct from $(\dagger)$, assuming $r$ is treated as sufficient statistic. If the reference already satisfies the inequality, the projection is inactive and the formulas collapse trivially. |
| Boundary Pythagorean identity for active m-flat constraint $\partial\mathcal{C}$: $D(\pi' \| \pi_{\text{ref}}) = D(\pi' \| \pi^*) + D(\pi^* \| \pi_{\text{ref}})$ for $\pi' \in \partial\mathcal{C}$ | [E] | Csiszár 1975, Amari–Nagaoka 2000, Thm 3.8. Holds *only* for $\pi'$ on the active equality boundary; for $\pi' \in \mathcal{C}$ in the interior, an explicit $\lambda^*(\mathbb{E}_{\pi'}[r] - R_0)$ cross-term appears (§2.1). |
| Decomposition (\ddagger) of phantom KL: $D(\pi_{\text{true}} \| \pi^*) = D(\pi_{\text{true}} \| \pi_T^*) + D(\pi_T^* \| \pi^*)$ | [F] | Falsified §2.2 by `test_kl_decomposition.py`. Residuals $\sim 0.05$–$0.55$ KL units, sign-changing across $R_0$. Pythagorean does not apply with $\pi_{\text{true}}$ outside $\mathcal{C}$. |
| Correct Pythagorean: $D(\pi_T^* \| \pi_{\text{ref}}) = D(\pi_T^* \| \pi^*) + D(\pi^* \| \pi_{\text{ref}})$ | [V] | Verified to $\sim 10^{-13}$ in `test_kl_decomposition.py`. This is the identity that actually holds; $\pi_T^*$ is in $\mathcal{C}$ where Pythagorean applies. |
| Capacity = Fisher dimension of $\mathcal{M}_\theta$ | [E] | Definitional only. Does not establish a relationship with the spatial-gap notion of bandwidth. |
| Fisher dimension scales like spatial-gap bandwidth | [O] | Conjectured by analogy in v1; not derived. Fisher rank is not bandwidth in any proven sense. |
| Capacity-Bandwidth Theorem (sketched §3.2) | [O] | The "informal theorem" was a dimension-counting guess, not a sketch of a proof. Status updated §3.2. |
| m-extension as info-geometric form of $I_G$ | [K] | Standard for exponential families; general case requires care |
| Bregman triangle identity for combined filter+constraint | [V] | Verified to machine precision in §IV across all alignment regimes |
| Cross-term formula $\mathcal{R}_{fc} = \lambda^*(R_{\text{true}} - R_0)$ | [V] | Verified analytically and numerically in §IV |
| §IV experiments measure total error, not "phantom magnitude" generically | [V] | Clarified §4.0; the experiments are about the $1-\beta$ object, not the $\beta(1-\beta)$ object |
| Aligned filter+constraint produces less *total error* than alternatives | [V/partial] | Mean and median: aligned 0.95, orthogonal 1.27, anti-aligned 1.61. Pointwise: aligned ≤ orthogonal in 222/240; aligned ≤ anti-aligned in 223/240; aligned is strict pointwise minimum in 211/240 (88%). Robust on average; not pointwise universal. |
| Compounding (combined > filter or combined > constraint) is universal | [F] | False. When filter pushes policy further from truth than $\pi_{\text{ref}}$ does in some direction, the constraint can pull back toward truth and reduce total error relative to filter-alone. Compounding is conditional on the geometric configuration. |
| Strict three-way ordering aligned ≤ orthogonal ≤ anti-aligned | [F] | Falsified in 81 of 240 cases by §4.5; orthogonal can exceed anti-aligned for non-smooth rewards |
| Trilogy claim: aligned compounds super-additively | [F] | Falsified by §4.2 across operational $R_0$ range |
| Anti-aligned configurations produce genuine super-additive total error | [V] | Verified in §4.2; threshold $R_0 \approx 0.45$ in toy |
| v1 claim: orthogonal compounds super-additively | [F] | Falsified by §4.2; orthogonal stays redundant up to $R_0 \approx 0.65$ |
| v2 claim: aligned filter+constraint produces indistinguishable signatures | [F] | Falsified by §4.6; removing each component produces materially different distortion |
| Black Nazi case sits at "intermediate alignment maximum of $\beta(1-\beta)$" | [F] | Falsified §2.4. Universal-energy-law conflation. |
| Black Nazi case is suppression+replacement-content per four-way decomposition | [F] | Refined §2.4. The four-way decomposition's setup is not RLHF's setup; the case lives in RLHF geometry, and applying the four-object formulas directly to it is the same setup-mismatch error as §4.8. The "suppression $\approx 1$" reading was correct for the four-way's own setup but that's not the operative setup. |
| Black Nazi case is consistent with framework-1 (RLHF e-projection) prediction of large total error at high $\lambda^*$ when truth ⊥ constraint | [V] | Qualitative match with §IV verified prediction. Fine-grained four-object texture is now supplied at first order by Bridge B (§2.4 + Appendix B); full KL/global version of Bridge B remains open. |
| Mechanism of Black Nazi case is data corruption | [O] | Asserted in v3 of conversation, retracted §2.4. Mechanism most plausibly objective distortion (RLHF), not corpus curation; either is consistent with the qualitative framework-1 prediction. |
| Multi-reward / curved constraint case preserves alignment ordering | [O] | Plausible but not tested |
| Three-flavor classification maps to gradient / Hessian / higher-moment tensor structure | [K/O] | Taylor-order structure is straightforward [E] in exponential-family settings. The full three-flavor classification across general neural-policy architectures is conjectural [O]. Eigenstructure phantoms via Amari–Chentsov-style tensors are derivable [K] in simple exponential families but not in general neural policies. See revised Part VI. |
| Hilbert framework recoverable as Fisher-tangent limit | [E] | Standard; second-order Taylor of KL is Fisher quadratic form |
| Specific quantitative predictions for production LLMs | [O] | Requires empirical characterization of $\mathcal{C}$ and $\mathcal{M}_\theta$ |
| Numerical companions for §III (filter phantoms) and §V (statistical phantoms) | [O] | Only the §3.4 redundancy claim, §4.6 diagnostic claim, §2.3 four-way decomposition, and Bridge B (§ Appendix B) have been tested |
| Projection-space companions for retention, suppression, leakage, total error | [V] | All four verified to floating-point precision in `test_four_objects_pure.py` ($r = 1.0000$ in policy-space pure-projection setup, max deviation $\sim 10^{-16}$; machine precision in projection space). |
| RLHF e-projection-from-reference analog of the four objects (Bridge B) | [V partial] | First-order Fisher-tangent reorganization in Appendix B and partially tested in `test_bridge_B.py`. Algebraic identities exact when $g = \mu c$ assumed (Test 1, machine precision); recovery of pure-projection laws at $\mu = a s$ exact (Test 2). On real e-projection: Test 3 reports $r \approx 0.996$ but holds $\mu$ approximately constant and so does not exercise the joint $(\mu, s)$ prediction; Test 4 (joint sweep of $R_0$ and reward direction) reports shape $r \approx 0.98$ with regression-slope deviations of 15–25% from 1, attributable to the second-order curvature term. Explicit second-order term identified: $\frac{\lambda^2}{2}\pi_0(\tilde r^2 - \mathbb{E}_{\pi_0}[\tilde r^2])$, verified in `test_second_order.py`. Full global KL-geometry version with the second-order term folded in: open. |

Legend: [E] = proved exactly; [K] = known under stated hypotheses; [V] = verified numerically; [F] = falsified by §IV or §2.3; [O] = open.

---

## Part X — Development Record

This document attempts the parallel KL/info-geometric development that the trilogy's three documents flag as open. The development happened in eleven rounds of correction, each catalogued in §4.9 and summarized structurally in Appendix A. The Development Record below tracks what was written, what was retracted, and what's currently open.

**Initial drafts (v1, v2 — superseded):** v1 set up Fisher-metric policy space (Part I), identified RLHF as e-projection onto m-flat constraint (§2.1), claimed a Pythagorean decomposition of phantom KL into "truth-side" and "reference-side" components (§2.2 — *retracted, see below*), claimed a "universal energy law" $\beta(1-\beta)$ for phantom magnitude (§2.3 — *retracted*), defined capacity as Fisher dimension with a sketched bandwidth-correspondence theorem (§3.2 — *partially retracted*), and sketched a redundancy claim for aligned filter+constraint (§3.4). v2 added the §IV numerical companion and corrected v1's specific claim about orthogonal-compounding-super-additively, then in turn drafted a diagnostic-indistinguishability claim that was also wrong.

**Retractions made during the conversation:**

- §2.2: the decomposition $D(\pi_{\text{true}} \| \pi^*) = D(\pi_{\text{true}} \| \pi_T^*) + D(\pi_T^* \| \pi^*)$ is wrong (residuals to 0.55 KL units, sign-changing). Pythagorean does not apply with $\pi_{\text{true}}$ outside $\mathcal{C}$. The correct identity uses the in-$\mathcal{C}$ point and decomposes against $\pi_{\text{ref}}$. Verified by `test_kl_decomposition.py`.
- §2.3: the universal energy law is wrong as stated. The framework conflates four genuinely different objects (retention, suppression, leakage, total error) under one scalar formula. The four-way decomposition is the replacement. Verified by `four_way_decomposition.py` and `test_four_objects.py`.
- §2.4: the four-object decomposition does not directly apply to the Black Nazi case, because the four-way formulas describe a different geometric setup than RLHF performs. The case sits in framework-1 (RLHF e-projection); what the framework can correctly say about it is the qualitative high-$\lambda^*$ total-error prediction, not the fine-grained four-object texture.
- §3.2: capacity-bandwidth correspondence is unproven. Fisher rank ≠ bandwidth in any derived sense. The "sketched theorem" was a dimension-counting guess, not a sketch of a proof.
- §4.5: the strict three-way alignment ordering breaks down for non-smooth rewards (81 of 240 cases). Aligned-is-best survives; the orthogonal-vs-anti-aligned ordering doesn't.
- §4.5 (further): even "aligned is least compounding" is conditional on configurations where filter and constraint both move policy in the constraint direction. When the filter pushes policy further from truth than $\pi_{\text{ref}}$ does, the constraint can pull back toward truth and reduce error.
- §4.6: the v2 diagnostic claim ("removing one layer leaves distortion intact, signatures indistinguishable") is wrong. Removing constraint vs filter produces materially different and informative signatures.
- §4.8: my "operationalization problem" framing for the leakage-test failure was misdiagnosed. The actual issue was setup-mismatch, and the four-way formulas hold to high precision when applied to their proper setup (`test_four_objects_pure.py`).

**Round 8 corrections (added in response to a second external review):**

- Signed-beta artifact in `test_four_objects_pure.py` corrected — the policy-space verification of the four objects is exact ($r = 1.0000$, $\sim 10^{-16}$), not approximate as I'd reported.
- Robustness sweep numbers corrected — aligned is pointwise minimum in 211/240 cases (88%), not 240/240 as I'd claimed; the result is robust on average and median, not pointwise universal.
- Hard-coded paths in active scripts replaced with `Path(__file__).resolve().parent` for reproducibility.
- Bregman triangle verification moved from `SUPERSEDED_redundancy_test_v1.py` into `visualize_redundancy.py` so the document's citation matches the actual location.
- §2.1 Pythagorean corrected — equality on the active boundary, with explicit cross-term $\lambda^*(\mathbb{E}_\pi[r] - R_0)$ for the half-space.
- §2.3 four-way identity reformulated as two correct linked decompositions ($\beta = \beta^2 + \beta(1-\beta)$ for output, $1-\beta = (1-\beta)^2 + \beta(1-\beta)$ for error) rather than the misleading single sum.
- §3.1 "unique m-extension" softened to "some element of $\mathcal{M}_\theta$, with the specific element selected by architecture, regularizer, optimizer, initialization, and divergence."
- §3.3 "exponential decay" softened to a conditional dependent on the kernel having exponential decay.
- §3.4 stale "strictly exceeds filter-alone" and "observationally indistinguishable" claims retracted in line with §4.5/4.6.
- Part VII rewritten to remove "linearization is removed", "capacity becomes a theorem", "observationally equivalent."
- **Bridge B reorganized** (Appendix B). First-order Fisher-tangent reorganization for the e-projection-from-reference setup: $\|Pg\|^2 = \mu^2 s^2$, $\|f-Pg\|^2 = (a-\mu s)^2$, $\|(I-P)g\|^2 = \mu^2(1-s^2)$, $\|f-g\|^2 = a^2+\mu^2-2a\mu s$. Inner-product algebra verified to machine precision (Test 1). Originally framed in round 8 as a derivation with $r \approx 0.996$ on real e-projection; round 11 corrected this to "reorganization with shape $r \approx 0.98$ and 15–25% magnitude error from second-order curvature."

**Round 9 corrections (added in response to a third external review):**

- Three script bugs fixed: inverted sign-interpretation text in `diagnostic_and_robustness.py`, misleading "filter alone (any)" label in `visualize_redundancy.py`, m-sign convention in `test_bridge_B.py`.
- §4.3 stale claim "at every $R_0$ tested, aligned ≤ orthogonal ≤ anti-aligned" corrected — fails at low $R_0$ in the base toy.
- m → μ (signed displacement coordinate) notation cleanup throughout Appendix B and `test_bridge_B.py`. "Retention" renamed to "query-direction output energy" in Bridge B contexts.
- §B.4 leakage monotonicity caveat added (monotone in $\beta$ only at fixed $\mu$).
- Part VI rewritten — first-moment, second-moment, and eigenstructure flavor descriptions all had specific overclaims. Corrected with proper Taylor-order accounting.
- §2.2 KL formula generalized with explicit $\mathbb{E}_{x \sim \nu}[\log Z_x(\lambda^*)]$.
- Black Nazi mechanism claims softened to "illustrative, not diagnostic of mechanism."
- Part VIII "absence of numerical companions" rewritten — gap is now production-system tests.
- Appendix A heading added; Step 8 and Step 11 updated to reflect Bridge B derivation, originals preserved in brackets.
- Ledger entries updated: aligned-comparison numbers (211/240, 222/240, 223/240); Black Nazi line now cites Bridge B for fine-grained texture; Pythagorean entry tightened to active boundary $\partial\mathcal{C}$; Bregman triangle precision corrected from $10^{-14}$ to actual $1.88 \times 10^{-13}$.
- **Substantive new derivation: explicit second-order term in e-projection expansion.** $\pi_\lambda = \pi_0 + \lambda \pi_0 \tilde r + \frac{\lambda^2}{2}\pi_0(\tilde r^2 - \mathbb{E}_{\pi_0}[\tilde r^2]) + O(\lambda^3)$, with second-order direction non-parallel to centered reward (cosine 0.157). Verified in `test_second_order.py`. Round 8/9 framed this as identifying the source of "12-15% relative deviation" in Bridge B Test 3; round 11 reframed this as the source of the 15-25% magnitude error envelope under joint $(\mu, s)$ sweep (Test 4) and the path to a global KL-geometry version of Bridge B.

**Round 10 corrections (synchronization pass — fourth external review):**

- §4.3 base-toy ordering claim corrected; "consistently" softened; Bridge B Test 3 relative-error claim corrected to distinguish substantive from near-zero quantities; Fisher vs Euclidean coordinate convention spelled out in new §B.7; dead variable removed from `test_four_objects_pure.py`; round-9 entry rewritten to be honest about what was actually done.

**Round 11 corrections (fifth external review — Bridge B Test 3 was a constant-$\mu$ artifact):**

- The headline "$r \approx 0.996$" from Test 3, presented in rounds 8–10 as evidence of Bridge B's first-order accuracy on real e-projection, did not test the joint $(\mu, s)$ prediction. In Test 3's regime $|\mu|$ varies by ~3% while $|s|$ varies by 39×; the Pearson correlation in this regime is mostly an $s$-shape match.
- New Test 4 added to `test_bridge_B.py`: joint sweep of $R_0$ and reward direction. Reports shape Pearson $r \approx 0.98$, regression slopes deviating from 1 by 15–25% with a sign pattern consistent with the §B.5 second-order term (over-prediction of query-aligned components, under-prediction of perpendicular components), median relative error 2–31%, p90 23–93%.
- §B.5 rewritten to retract the "12-15% relative error" headline and report the joint-sweep numbers.
- §B.6 rewritten to be honest about what Bridge B is: the four identities are inner-product algebra given $g = \mu c$ (law of cosines plus one orthogonal decomposition), not new mathematics. The information-geometric content is the textbook fact that e-projection moves along the centered sufficient-statistic direction at first order. "Derivation" downgraded to "reorganization."
- §B.2 amended with explicit note about the algebraic content of the four identities.
- §2.4 "distinctive testable prediction" framing softened with explicit toy-to-production gap (no isolated constraint direction in real RLHF; KL coefficient ≠ m-flat severity except at optimum; "off-query behavior" undefined for LLMs; $\mu$ not directly observable).
- §4.8, §VII, §IX (Status Ledger), the round-8 entry above, and the README updated for consistency with round-11 numbers and framing.

**Currently established:**

- The four-way algebra is exact (machine precision in projection space; $r = 1.0000$ in proper Fisher-tangent operationalization in policy space, max deviation $\sim 10^{-16}$).
- The Bregman triangle identity for filter+constraint composition with cross-term $\lambda^*(R_{\text{true}} - R_0)$ holds to $1.88 \times 10^{-13}$ in `visualize_redundancy.py`.
- The correct boundary Pythagorean for e-projection onto m-flat $\partial\mathcal{C}$ holds to $\sim 10^{-13}$ when applied with the in-$\partial\mathcal{C}$ point as the projection target.
- Aligned filter+constraint produces the smallest total error in 211/240 cases (88%) of the tested family, with median ratio anti-aligned/aligned $\approx 1.28\times$, conditional on configurations where filter and constraint move policy in the same direction.
- The qualitative prediction "trained policy is displaced far from truth in KL when truth is approximately orthogonal to a hard constraint" matches the Black Nazi case phenomenology, with Bridge B providing the first-order Fisher-tangent shape and a 15–25% magnitude error envelope.
- **Bridge B as reorganization** (Appendix B) — inner-product-algebra identities given $g = \mu c$, with the textbook first-order e-projection fact $g_\lambda \approx \lambda \pi_0 \tilde r$ as the modeling step. On real e-projection: shape $r \approx 0.98$, slopes 0.85–1.25 against an exact-identity slope of 1 (`test_bridge_B.py` Test 4).
- **The explicit second-order term** in the e-projection expansion is identified ($\frac{\lambda^2}{2}\pi_0(\tilde r^2 - \mathbb{E}_{\pi_0}[\tilde r^2])$) and verified non-parallel to centered reward (`test_second_order.py`). It accounts qualitatively for the slope-deviation sign pattern in Test 4.

**Currently open:**

- **Full KL-geometry Bridge B with second-order term folded in.** The first-order tangent reorganization is in place; the second-order direction in the e-projection expansion is identified; what remains is propagating this through the four scalar laws (retention/suppression/leakage/total) and turning the empirical 15–25% magnitude error into an explicit error formula in $\lambda$, $a$, $s$, and the higher reward moments.
- **Capacity-bandwidth scaling.** Whether Fisher dimension governs anything bandwidth-like in data-hole interpolation. Probably architecture-dependent rather than projection-theoretic.
- **Multi-reward / curved constraints.** Whether the alignment ordering and the Bregman triangle's structure survive when the constraint manifold has curvature.
- **Eigenstructure rotation.** The third "flavor" the trilogy mentioned, not tested numerically here. Part VI now has the correct mathematical framing (third-moment tensor in exponential-family cases) but no synthetic verification.
- **Empirical contact with production systems.** Every framework prediction in this document has been tested only on synthetic toys. Bridge B's $\mu^2$-leakage prediction is *toy-level distinctive*; translating it into a real-system test faces unaddressed obstacles described in §2.4 and §B.6 (no isolated constraint direction in real RLHF, KL coefficient ≠ severity except at the optimum, "off-query behavior" lacks an operational definition for an LLM, $\mu$ not directly observable).

**Meta-status (current).** The original trilogy claimed unification across three layers under a single operator-theoretic skeleton, with the universal energy law $\beta(1-\beta)$ as the governing scalar relation. Through seven rounds of correction the framework was strictly narrowed; rounds 8 and 9 expanded it back — Bridge B's first-order version was added in round 8 (initially framed as "derivation," downgraded in round 11 to "reorganization"), and round 9 added the explicit second-order term in the underlying e-projection expansion plus a substantial cleanup of overclaims that had survived earlier rounds (especially in Part VI). Round 10 was synchronization-only. Round 11 walked back the "$r \approx 0.996$" headline empirical claim about Bridge B as a constant-$\mu$ artifact and reported the joint-sweep numbers ($r \approx 0.98$, slope deviations 15–25%). The framework now has: a correct projection-theoretic core, a correct KL projection model for RLHF, a first-order Fisher-tangent reorganization (Bridge B) with a quantified 15–25% magnitude error envelope on real e-projection, an identified second-order correction, and substantially fewer overclaims than at any prior point. The §IV redundancy result and Bridge B's first-order reorganization (with its explicit error envelope) are the two numerically tested predictive components in different metrics (KL units and Fisher-tangent units respectively).

What this means for the trilogy's normative claims: the super-additive compounding mechanism is gone. The diagnostic-indistinguishability claim is gone. The "phantom maximized at intermediate alignment" framing is gone. What survives is sharper than what the trilogy stated: aligned configurations are typically least-compounding (with a conditional qualifier), and Bridge B predicts that in the orthogonal-truth regime relevant to cases like Black Nazi, leakage scales with the constraint severity $\mu^2 \propto (\lambda^*)^2$ rather than $\beta(1-\beta)$ — *at the toy level*, with toy-to-production translation an open problem. The qualitative observation that motivated the trilogy survives; the *specific scalar prediction* now comes from Bridge B rather than from the misapplied pure-projection formula, and the prediction comes with a 15–25% magnitude error envelope rather than the previously reported 12–15%. Causal claims about which production mechanism produces specific observed cases (e.g., reward modeling vs prompt rewriting vs corpus curation in the Black Nazi case) are *not* in scope of the framework — that requires primary-source evidence the framework doesn't provide.

---

## Appendix B — Bridge B: First-Order Fisher-Tangent Decomposition for E-Projection-from-Reference

The four-object decomposition of §2.3 describes pure projection of $f \in \text{Range}(P_Q)$ onto a constraint subspace $C$, with the four scalar laws $\beta^2, (1-\beta)^2, \beta(1-\beta), 1-\beta$. RLHF performs a different operation: e-projection of $\pi_{\text{ref}}$ onto an m-flat constraint manifold $\mathcal{C}$, with the trained policy displaced from the reference along the active reward direction by an amount set by the Lagrange multiplier $\lambda^*$. The four-object formulas do not directly apply (§4.8 Test 2 verifies this empirically). This appendix derives the first-order Fisher-tangent analog.

### B.1 Setup

Work in the Fisher tangent space at $\pi_{\text{ref}}$ (uniform reference for simplicity; the construction generalizes). Let $q \in T_{\pi_{\text{ref}}}\mathcal{P}$ be the unit truth direction: $\pi_{\text{true}} - \pi_{\text{ref}} = a \, q$, where $a = \|\pi_{\text{true}} - \pi_{\text{ref}}\|$ is the truth's distance from reference. Fix a *signed* unit constraint direction $c$ — for RLHF we take $c$ aligned with the centered reward, so the trained displacement points along $c$ for $\lambda^* > 0$.

**Coordinate convention.** Bridge B's identities are stated in an abstract inner-product tangent space. In the numerical scripts, vectors are raw probability differences $\delta\pi$ with the Euclidean norm $\|\delta\pi\|^2 = \sum_y \delta\pi(y)^2$. For a *uniform* reference $\pi_0 = 1/|\mathcal{Y}|$, the Fisher inner product on tangent vectors $\delta\pi$ is
$$\langle \delta\pi, \delta\pi'\rangle_F = \sum_y \frac{\delta\pi(y)\,\delta\pi'(y)}{\pi_0(y)} = |\mathcal{Y}|\sum_y \delta\pi(y)\,\delta\pi'(y),$$
so Fisher and Euclidean inner products differ only by a constant factor and the four scalar identities (which are ratios in each test case) are preserved either way. **For non-uniform references this equivalence breaks**, and the appropriate generalization is to work either in score coordinates $u = \delta\pi/\pi_0$ with the Fisher inner product $\langle u, v\rangle_F = \mathbb{E}_{\pi_0}[uv]$, or to use the weighted Fisher inner product on raw perturbations $\sum_y \delta\pi(y)\,\delta\pi'(y)/\pi_0(y)$. The current numerical experiments do not exercise this distinction; promoting Bridge B beyond the uniform-reference regime requires the proper Fisher accounting.

The trained policy $\pi^* = e\text{-proj}_\mathcal{C}(\pi_{\text{ref}})$ has tangent displacement $g = \pi^* - \pi_{\text{ref}}$. To first order in $\lambda^*$, $g = \mu \, c$ where $\mu \in \mathbb{R}$ is a *signed* scalar set by the e-projection constraint:

$$\mu = \lambda^* \, \|r_{\text{centered}}\|_{\text{Fisher}}$$

with $\mu \geq 0$ when the constraint pulls in the direction of $c$ and $\mu < 0$ when it pulls against. Second-order corrections bend $g$ slightly off the $c$-line due to simplex curvature; see §B.5 for the explicit expansion.

When magnitude rather than signed coordinate is needed, write $m = |\mu|$.

Let $s = q \cdot c \in [-1, 1]$ be the *signed* cosine between truth and constraint directions, and let $\beta = s^2 \in [0, 1]$ be the squared cosine. Let $P$ be orthogonal projection onto $\text{span}(q)$ in the tangent space.

**Notation note:** the document also uses the symbol $\beta$ in the RLHF Lagrangian $\mathbb{E}_\pi[r] - \beta D(\pi \| \pi_{\text{ref}})$ as the KL regularization coefficient. To avoid conflict, the principal-angle eigenvalue is always written $\beta = s^2$ in Appendix B; the Lagrangian coefficient is *not* used in this appendix and was a notational coincidence in §2.1. Cleaner future drafts should use $\tau$ or $\eta$ for the Lagrangian coefficient.

### B.2 The four Bridge-B identities

Direct computation gives four scalar identities:

$$\|Pg\|^2 = \mu^2 s^2 \qquad \text{(query-direction output energy)}$$
$$\|f - Pg\|^2 = (a - \mu s)^2 \qquad \text{(query-coordinate error / suppression)}$$
$$\|(I-P)g\|^2 = \mu^2 (1 - s^2) \qquad \text{(off-query leakage)}$$
$$\|f - g\|^2 = a^2 + \mu^2 - 2 a \mu s \qquad \text{(total tangent error)}$$

These are verified to zero residual in `test_bridge_B.py` (Test 1, five random configurations; Test 2, recovery sweep).

**What kind of statement these are.** Once $f = aq$, $g = \mu c$, and $P$ projects onto $\text{span}(q)$ are fixed, the four identities are inner-product algebra: the law of cosines plus one orthogonal decomposition $\|g\|^2 = \|Pg\|^2 + \|(I-P)g\|^2$. They hold in any inner-product space for any two vectors $f, g$ of magnitudes $a, \mu$ at signed cosine $s$. **No information geometry enters at this step.** The information-geometric content of Bridge B is the single fact that for e-projection of $\pi_0$ onto $\{\mathbb{E}_\pi[r] = R_0\}$, $g_\lambda \approx \lambda \pi_0 \tilde{r}$ along the centered-reward direction at first order in the Lagrange multiplier (Amari–Nagaoka §3.2; this is standard exponential-family stuff). Bridge B is a clean reorganization that says: *given* this first-order fact about e-projection, the four-object structure of pure projection has exact analogs in the e-projection-from-reference setup, with the four scalar laws becoming functions of the signed displacement coordinate $\mu$ and the signed cosine $s$ rather than just $\beta = s^2$. Calling it a "derivation" oversells what's there; calling it a clean reorganization that connects the two setups gets it right.

**Names matter.** The first quantity $\|Pg\|^2 = \mu^2 s^2$ is the *energy of the trained policy in the query direction*. It is *not* "retention" in the pure-projection sense — when $\mu s < 0$ (anti-aligned displacement), the trained policy points opposite the truth direction in the query coordinate, but $\mu^2 s^2$ is still positive. Calling this object "retention" without qualification would obscure the sign information. The signed amplitude ratio $\mu s / a$ (whose square gives $\mu^2 s^2 / a^2$) is what tells you whether the model preserved, under-shot, over-shot, or inverted the truth direction. Bridge B's prediction is about the *energy* but the *signature* requires the signed quantity.

### B.3 Recovery of pure-projection laws

The Bridge-B identities reduce to the §2.3 four-object formulas exactly when $\mu = a s$:

$$\mu = as \implies \begin{cases} \|Pg\|^2 = a^2 s^4 = a^2 \beta^2 & \text{(retention, in pure-projection sense)} \\ \|f - Pg\|^2 = a^2(1-s^2)^2 = a^2(1-\beta)^2 & \text{(suppression)} \\ \|(I-P)g\|^2 = a^2 s^2 (1-s^2) = a^2 \beta(1-\beta) & \text{(leakage)} \\ \|f - g\|^2 = a^2(1-s^2) = a^2(1-\beta) & \text{(total error)} \end{cases}$$

(In this special case $\mu s = a s^2 \geq 0$, so the displacement-toward-truth-direction is non-negative and the "retention" label is unambiguous.) The condition $\mu = as$ is exactly $g = (a s) c = (f \cdot c) c = P_C f$ — orthogonal projection of truth onto the constraint subspace. So pure projection of truth onto constraint is the special case of Bridge B at $\mu = as$. **RLHF is not generically that case**: $\mu$ is determined by the e-projection constraint $\mathbb{E}_{\pi^*}[r] = R_0$ from the reference, not by the truth's component along $c$.

### B.4 What Bridge B explains

Five things the Bridge-B formulas explain that the pure-projection formulas obscure:

**(i)** The Bridge-B formulas depend on the *signed* coordinate $\mu$ and the *signed* cosine $s$, not just on $\beta = s^2$. Anti-alignment ($s < 0$ with $\mu > 0$, equivalently $s > 0$ with $\mu < 0$) produces materially different behavior than alignment, even at the same $\beta$ and same $|\mu|$. The pure-projection formulas wash out this distinction. This is consistent with the §IV redundancy result, where anti-aligned configurations were genuinely different from aligned ones.

**(ii)** Leakage is $\mu^2(1-\beta)$, *not* $\beta(1-\beta)$ — but the monotonicity in $\beta$ holds only at *fixed displacement magnitude*. In actual e-projection $\mu = \mu(R_0, r, \pi_{\text{ref}})$ is itself a function of the constraint and reward direction, so observed leakage is $\mu(s)^2(1 - s^2)$ and its dependence on $s$ confounds the kinematic factor $(1-s^2)$ with the constraint-severity factor $\mu(s)^2$. *For fixed $\mu$, leakage peaks at orthogonality; for fixed $R_0$, the empirical shape depends on how $\mu$ varies with the reward direction.* This still explains why the §4.8 Test 2 measurement was monotone-decreasing-with-alignment rather than peaked at $\beta = 0.5$ — the wrong prediction came from holding the wrong thing fixed.

**(iii)** The query-coordinate error (suppression) is $(a - \mu s)^2$. When $\mu s < 0$ (anti-aligned displacement), this *adds* to suppression (the constraint pulls policy further from truth in the query direction). When $\mu s > 0$ with $\mu s < a$, suppression *decreases* (the constraint partly recovers truth in the query direction). When $\mu s > a$, the constraint over-shoots and suppression rises again. The sign and magnitude of $\mu s$ relative to $a$ together determine the suppression magnitude in a way the pure-projection $(1-\beta)^2$ doesn't capture.

**(iv)** Total tangent error is $a^2 + \mu^2 - 2a\mu s = (a - \mu s)^2 + \mu^2(1-s^2)$. This is the sum of query-coordinate error and off-query leakage, which mirrors the pure-projection identity $1-\beta = (1-\beta)^2 + \beta(1-\beta)$. The decomposition into "what's missing in the query direction" plus "what's leaked to other directions" survives.

**(v)** The "trained policy displaced from reference toward constraint" picture is the right intuition; the projection of truth onto constraint is *not*. The trilogy and earlier drafts of this document used the projection picture; Bridge B is the displacement picture.

### B.5 Empirical status and the second-order correction

Test 1 in `test_bridge_B.py`: algebraic verification with random tangent vectors. Identities hold to machine precision when $g = \mu c$ is assumed. *These are inner-product identities given the assumption — see §B.2 — so this test verifies the algebra, not the modeling claim that $g \approx \mu c$ on actual e-projection.*

Test 2: recovery sweep at $\mu = as$ for $s \in \{-0.3, 0, 0.3, 0.5, 0.7, 0.9\}$. Bridge B and pure-projection formulas agree to zero diff.

**Test 3 (and what it actually showed).** Earlier drafts of this appendix presented Test 3 — Bridge B applied to actual e-projection from uniform reference, sweeping reward direction at fixed $R_0 = 0.5$ — as the headline empirical evidence: Pearson $r \approx 0.996$ for all four quantities; max relative error 12% and 15% on the two substantive (non-near-zero) quantities. **That framing was misleading and is retracted.**

The issue is that Test 3 holds $\mu$ approximately constant. Same-shape Gaussian rewards (sigma 2.5) at fixed $R_0$ require nearly the same Lagrange multiplier $\lambda^*$ by symmetry, so $|\mu| = \lambda^* \|\tilde{r}\|_F$ varies by only ~3% across the sweep ($|\mu| \in [0.165, 0.170]$, ratio max/min $\approx 1.03$), while $|s|$ varies over [0.025, 1.000] (ratio $\approx 39$). The Pearson $r$ in this regime is therefore *almost entirely* a measure of how well Bridge B captures the $s$-shape with $\mu$-coefficient roughly constant. With $\mu$ pinned at its mean value, the Bridge B prediction has $r = 0.99989$ with the real Bridge B prediction across the same sweep — the two are indistinguishable at the resolution Test 3 reports. The "$r \approx 0.996$" did not test the joint $(\mu, s)$ dependence; it tested an $s$-shape at near-fixed $\mu$.

**Test 4 (the actual first-order test).** Sweep $R_0 \in [0.2, 0.85]$ jointly with reward direction. This drives $|\mu|$ over [$6 \times 10^{-4}$, 0.49] (~800-fold variation) and $|s|$ over [0.04, 1.00], so the joint $(\mu, s)$ prediction is exercised. Reporting Pearson $r$ (shape), the regression slope of measured-vs-predicted (magnitude — should be 1 for an exact identity), and relative-error percentiles on 240 configurations:

| Quantity | Pearson $r$ | regression slope | median rel. err | p90 rel. err |
|---|---|---|---|---|
| $\|Pg\|^2$ | 0.988 | **0.92** | 31% | 93% |
| $\|f - Pg\|^2$ | 0.982 | **0.85** | 5% | 23% |
| $\|(I-P)g\|^2$ | 0.988 | **1.25** | 11% | 34% |
| $\|f - g\|^2$ | 0.982 | **1.04** | 2% | 27% |

The slopes deviate from 1 by 15–25% with a consistent sign pattern: $\|Pg\|^2$ and $\|f - Pg\|^2$ are over-predicted; $\|(I-P)g\|^2$ and $\|f - g\|^2$ are under-predicted. This pattern is what the second-order term below predicts qualitatively — actual $\|g\|^2 > \mu^2$ because $g$ has a perpendicular component, so quantities counting perpendicular content are under-predicted; the corresponding reduction in $(g \cdot q)^2$ relative to $(\mu c \cdot q)^2 = \mu^2 s^2$ over-predicts the query-aligned content. **The honest statement of Bridge B's empirical status is therefore: the first-order Fisher-tangent prediction agrees with actual e-projection in shape (Pearson $r \approx 0.98$ with broad joint variation) but with a 15–25% systematic magnitude error coming from second-order curvature.** Median relative error on the substantive quantities is single-digit; 90th-percentile relative error is 23–34%.

**Where the deviation comes from.** The actual e-projection from a uniform reference $\pi_0$ is

$$\pi_\lambda(y) = \frac{\pi_0(y) e^{\lambda r(y)}}{Z(\lambda)}$$

with tangent displacement $g_\lambda = \pi_\lambda - \pi_0$. Expanding in $\lambda$ around $\lambda = 0$:

$$\pi_\lambda = \pi_0 + \lambda \pi_0 \tilde{r} + \frac{\lambda^2}{2} \pi_0 (\tilde{r}^2 - \mathbb{E}_{\pi_0}[\tilde{r}^2]) + O(\lambda^3)$$

where $\tilde{r} = r - \mathbb{E}_{\pi_0}[r]$ is the centered reward. The first-order term $\lambda \pi_0 \tilde{r}$ is along the centered-reward direction $c$ — exactly the Bridge B displacement. The second-order term $\frac{\lambda^2}{2}\pi_0(\tilde{r}^2 - \mathbb{E}_{\pi_0}[\tilde{r}^2])$ is along the *centered square of reward*, which is *not* parallel to $c$ in general. This is what bends $g_\lambda$ off the $c$-line and produces the slope deviations in Test 4. The deviation grows with $\lambda$ (and hence with $\mu$), which is why Test 3's near-fixed-$\mu$ regime understates the magnitude error: Test 3 sees a single horizontal slice through the deviation surface; Test 4 sees the surface.

A full KL-geometry version of Bridge B would carry the second-order term through and produce error formulas as functions of $\lambda$, $a$, $s$, and the higher reward moments. That derivation is open. What's now clear is that the first-order Fisher-tangent prediction has a 15–25% magnitude error envelope on real e-projection, not the 12–15% suggested by Test 3 — closing that gap requires the second-order correction, not just the first-order tangent algebra.

### B.6 What Bridge B is and isn't

**What it is:** a reorganization of the four-object structure for the e-projection-from-reference setup of RLHF, with scalar laws in $(\mu, s)$ rather than $\beta = s^2$. The four identities of §B.2 are inner-product algebra given $f = aq$ and $g = \mu c$; the empirical content is whether $g \approx \mu c$ on actual e-projection, and the §IG fact that this holds at first order in $\lambda$ is standard exponential-family material (Amari–Nagaoka §3.2). Useful because it cleanly separates the four objects in the setup the framework actually cares about and shows how they reduce to the pure-projection laws at $\mu = as$.

**What it isn't:** a new derivation, in any strong sense. Once you grant the first-order fact $g_\lambda = \lambda \pi_0 \tilde r + O(\lambda^2)$, the rest is law of cosines. Earlier drafts framed Bridge B as "derived and verified at first order"; the more accurate framing is "reorganized and partially tested." The first-order *fact* is derived (textbook); the *identities* given that fact are algebra; the *empirical fit* on actual e-projection has a 15–25% magnitude error envelope from the unmodeled second-order term (Test 4, §B.5).

**What it isn't, second sense:** a full derivation of the global KL-geometry analog of the four-object decomposition. The KL divergences themselves are not Fisher inner products except at second order around the diagonal. Bridge B handles the local linear algebra of the e-projection geometry; promoting it to a full KL decomposition with explicit higher-order corrections is further work — the second-order term identified in §B.5 is the starting point but has not been propagated through the four scalar laws.

**What it does for the Black Nazi case (§2.4):** *if* the operative constraint is something like representational diversity (so truth is approximately orthogonal to it, $s \approx 0$) and the constraint is hard (large $\lambda^*$, hence large $|\mu|$), Bridge B predicts:
- Query-direction output energy $\mu^2 s^2 \approx 0$ (near-zero overlap of trained output with truth direction).
- Query-coordinate error $(a - \mu s)^2 \approx a^2$ (full suppression of truth in the query direction).
- Off-query leakage $\mu^2(1 - s^2) \approx \mu^2$ (large leakage to off-query directions, scaling with constraint severity squared, *not* peaked at intermediate alignment).
- Total tangent error $a^2 + \mu^2 - 2 a \mu s \approx a^2 + \mu^2$ (large; the Pythagorean-like sum at orthogonality).

The predicted phenomenology matches the case qualitatively: full suppression of historical truth, large displacement of output into the constraint manifold (which the user reads as "constraint-compliant content filling the answer slot"), with the magnitude scaling with $\mu^2 \propto (\lambda^*)^2$. This is what the trilogy was reaching for; Bridge B gives the version of it that's actually in the right geometry — modulo the hypothetical-mechanism caveat above and the 15–25% magnitude error envelope from §B.5.

### B.7 Coordinate conventions: Fisher vs Euclidean tangent metrics

The derivations above use Bridge B's identities at the level of abstract tangent vectors with an inner product. The numerical scripts compute squared norms as Euclidean dot products on raw probability-difference vectors, which is *not* the Fisher metric in general. A note on when these coincide and when they don't.

For uniform reference $\pi_0 = 1/N$ on $N$ points, the Fisher metric on tangent vectors $u, v$ at $\pi_0$ is

$$\langle u, v \rangle_F = \sum_y \frac{u(y) v(y)}{\pi_0(y)} = N \cdot \langle u, v \rangle_{\text{Euclidean}}.$$

So Fisher and Euclidean inner products differ by a constant factor $N$ when $\pi_0$ is uniform. Bridge B's predictions involve squared norms, so this constant factor enters as $N$ uniformly — but Bridge B's *test* outputs (Pearson $r$, the recovery condition $\mu = a s$, the four scalar laws as ratios) are all dimensionless or homogeneous of the same degree in the constant factor, so the Pearson correlations and recovery checks are *invariant* under uniform-$\pi_0$ coordinate choice. The numerical results in `test_bridge_B.py` Tests 1–3 are coordinate-correct for uniform reference under either convention.

For non-uniform $\pi_0$, the Fisher metric is

$$\langle u, v \rangle_F = \sum_y \frac{u(y) v(y)}{\pi_0(y)},$$

a $\pi_0$-weighted inner product, and Bridge B's identities — derived in score coordinates $u = \delta\pi/\pi_0$ where the first-order e-projection direction is $u_\lambda = \lambda \tilde{r}$ — *cannot* be transferred to raw probability-vector Euclidean inner products without a re-derivation. The natural way to extend Bridge B to non-uniform reference is to work in score coordinates throughout, with the Fisher metric as the inner product. The current numerical verification only exercises the uniform-reference case, so the Fisher-Euclidean equivalence used implicitly in the scripts is fine for the verification but should not be relied on for general extensions.

---

## Appendix A — The Correction Path (External Skeleton)

A reviewer condensed the working path through this document into the following sequence. It is sharper than the §4.9 narrative and is preserved here because each step names a structural move that the full document spends a section on. Steps 8 and 11 have been updated to reflect the round-8 derivation of Bridge B; the original wording is preserved in `[brackets]` for the record.

**Step 1.** Identify the core mistake: the universal-law assumption $\beta(1-\beta)$ describes only one object (leakage) but was used as if it described everything.

**Step 2.** Replace with the four-object decomposition.
$$\text{Retention: } \|PCf\|^2 = \sum |a_j|^2 \beta_j^2 \qquad \text{Suppression: } \|Pf - PCf\|^2 = \sum |a_j|^2 (1-\beta_j)^2$$
$$\text{Leakage: } \|(I-P)Cf\|^2 = \sum |a_j|^2 \beta_j(1-\beta_j) \qquad \text{Total error: } \|f - Cf\|^2 = \sum |a_j|^2 (1-\beta_j)$$
With identity $1-\beta = (1-\beta)^2 + \beta(1-\beta)$.

**Step 3.** Realize the setup mismatch. Two different geometries were being conflated: projection geometry (where the four-object formulas are correct) takes $f \in \text{Range}(P)$ and applies $C$; RLHF geometry takes $\pi^* = e\text{-proj}_{\mathcal{C}}(\pi_{\text{ref}})$. These are not the same operation. The four-object formulas do not directly apply to RLHF.

**Step 4.** Fix RLHF formulation. $\pi^*(y|x) \propto \pi_{\text{ref}}(y|x) \, e^{\lambda r(x,y)}$ — e-projection onto an m-flat boundary, exact only on the equality constraint. Bregman triangle: $D(\pi \| \pi_{\text{ref}}) = D(\pi \| \pi^*) + D(\pi^* \| \pi_{\text{ref}}) + \lambda(\mathbb{E}_\pi r - R_0)$. Not a clean Pythagorean identity on the whole half-space.

**Step 5.** Kill the bad KL decomposition. The claim $D(\pi_{\text{true}} \| \pi^*) = D(\pi_{\text{true}} \| \pi_T^*) + D(\pi_T^* \| \pi^*)$ is wrong: wrong KL orientation, missing Bregman cross-term. Verified numerically (§2.2 retraction, residuals up to 0.55 KL units).

**Step 6.** Fix the filter+constraint composition with the correct cross-term. $D(\pi_{\text{true}} \| \pi_{\text{filter}}) = D(\pi_{\text{true}} \| \pi_{\text{final}}) + D(\pi_{\text{final}} \| \pi_{\text{filter}}) + \lambda(R_{\text{true}} - R_0)$. This is exact and verified.

**Step 7.** Correct the compounding claim. Old: aligned filter+constraint compounds worst. Reality (verified): aligned → smallest total error, anti-aligned → largest. **But not universal:** the constraint can sometimes *reduce* error if the filter is worse than truth. Compounding is conditional, not guaranteed.

**Step 8.** Separate RLHF from four-object algebra. The structural conclusion: four-object algebra is correct, RLHF as projection is correct, direct connection between them needed a separate derivation. *[Original wording: "Bridge B is the open piece of work." Updated round 8: Bridge B's first-order Fisher-tangent version is now derived in Appendix B; the full KL-geometry version remains open.]*

**Step 9.** Fix data-hole claims. Original overreach: "unique m-extension," "capacity = bandwidth." Correct: data-hole = underdetermined extension problem, behavior depends on architecture and training dynamics, Fisher rank ≠ bandwidth. The capacity-bandwidth scaling is not proven.

**Step 10.** Fix interpretation of real cases. Black Nazi case: wrong reading used four-object formulas directly; correct reading places the case in RLHF geometry, where the framework's verified prediction is large total error at high $\lambda$. Fine structure (suppression vs leakage) requires Bridge B.

**Step 11.** Clean final structure.

**Solid:** two-projection geometry; four-object decomposition; common-mask statistical results; RLHF as exponential tilt; Bregman identity (with cross-term).

**Verified:** aligned → least distortion (toy + sweep, with the conditional qualifier of Step 7).

**Open:** RLHF ↔ projection bridge (Bridge B); data-hole interpolation theory; capacity/bandwidth scaling.

**Dead:** universal $\beta(1-\beta)$ law; KL decomposition $(\ddagger)$; "alignment causes worst compounding"; "observational indistinguishability."

**Final state (after round 8):** a correct projection-theoretic core + a correct KL projection model for RLHF + a first-order Fisher-tangent bridge between them (Bridge B, Appendix B). What's still open: the full KL-geometry version of Bridge B (with explicit higher-order corrections from simplex curvature, see §B.5), capacity-bandwidth scaling, multi-reward / curved constraints, eigenstructure rotation, and empirical contact with production systems.

*[Original wording: "Final state: a correct projection-theoretic core + a correct KL projection model + no derived bridge between them. Everything else is either an application of the core or an unproven extension. The next step is not polish — it's deriving Bridge B (the RLHF version of the four-object decomposition). That's the actual missing piece." Round 8 derived the first-order Fisher-tangent version of Bridge B; the next step now is the full KL-geometry version with second-order curvature corrections.]*
