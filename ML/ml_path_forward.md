# The ML Path Forward

## A research roadmap for the ML extension of the Phantom Framework

*Working Document · April 2026*

*Companion to: Statistical Phantoms; Training Distortion as Forced Constraint Projection; Training Corpus Holes as Multiplication Defects; Information-Geometric Reformulation; Audit-Blind Subspace; the four §4 statistical realizations*

---

## Preface

This document lays out a research program for the ML extension of the Phantom Framework. It is intentionally thorough about scope, technical specifications, dependencies, and expected outcomes. Each phase has concrete deliverables; each deliverable has stated verification criteria; each open question is identified as such.

The document does not establish new mathematical results. It identifies what work has been done, what work is ready to be done immediately, what work requires moderate development, and what work is open theoretically. The goal is a clear-eyed map of the territory rather than advocacy for any particular direction.

Scope. This is the ML side of the program — training distortion, pretraining-corpus holes, audit-blindness for trained networks. It does not address the spectral side (Phantom suite notebooks, CCG, GLR, etc.) which is its own complete object, nor the statistical realizations (PCA-with-mask, regression with omitted variables, matched filtering, modal analysis) which now have concrete numerical companions in the project.

Voice. Math voice throughout. Honest about the difference between linearized-regime structural results (which are robust) and quantitative magnitudes (which carry the curvature error envelope from `info_geometric_reformulation.md` §B.5). The Path 1 / Path 2 distinction (linearization as deliberate scope vs nonlinear extensions) is maintained.

---

## Part I — Where We Are

### 1.1 The current ML apparatus

The ML extension currently consists of four documents:

**`training_distortion_phantom.md`** (Path 1 scope).
- RLHF and constraint-driven training treated as Halmos two-projection in the Fisher tangent space at a base policy $\pi_0$.
- $P_1$ = inference subspace (where queries read the policy), $P_2$ = constraint-implementing subspace (where the training pressure projects).
- Phantom = forced-projection mass redistribution: parts of policy behavior orthogonal to the constraint shift in geometrically-determined directions.
- Linearization is deliberate scope — the e-projection at $\pi_0$ is exact in the tangent space; nonlinear corrections are forwarded to the info-geometric companion.

**`training_corpus_holes.md`** (Path 1 scope).
- Pretraining-data distortions treated as multiplication-operator defects on the data measure $\nu$.
- Holes (regions of input space underrepresented in training corpus) act as masks; the phantom is the trained-model's interpolation-and-extrapolation response into the hole, structured by the surrounding-corpus geometry.
- §3.2 capacity-as-Fisher-dimension is definitional.
- §5.2 compounding claim corrected with companion's 211/240 numerical evidence (aligned filter+constraint is *least* compounding, not most).

**`audit_blind_subspace.md`** (Working paper draft with full proofs).
- Theorem A: $\dim(\mathcal{N}_{\text{audit}}) = \dim(\Xi) - \mathrm{rank}(A_\mathcal{Q} \circ L)$.
- Theorem B: $\dim(\mathcal{N}_{\text{audit}}) \geq \dim(\Xi) - N$ for $N$-query audit.
- Theorem C: four-object decomposition gives audit-coverage fractions.
- Theorem D: optimal audit construction via SVD of $L|_\mathcal{C}$.
- White-box, procedural extensions (§§7.1–7.2) and nonlinear regime sketch (§7.3).
- Numerical verification on ridge-regression toy: predicted dimensions match exactly, four-object identity holds to machine precision.

**`info_geometric_reformulation.md`** (Path 2 scaffolding).
- Nonlinear-manifold companion to the linearized treatment.
- Second-order corrections from the e-projection expansion at the base point.
- Curvature corrections of magnitude 15–25% in moderate-distortion regime; structural conclusions robust under linearization.

### 1.2 Where the ML treatment falls short

The current state has three structural gaps:

**Gap 1: No concrete ML-side numerical companions.**

The spectral suite has notebooks (`hole_problem.ipynb`, `boundary_layer.ipynb`, etc.) that turn the framework's predictions into pictures matching the predictions to floating-point precision. The statistical extension now has four such companions (`pca_masked_companion.md`, `regression_omitted_companion.md`, `matched_filter_companion.md`, `modal_analysis_companion.md`). The ML treatment has none.

The audit-blind-subspace document includes a ridge-regression numerical demonstration, but that's the statistical realization, not the ML realization. There is no demonstration of: a wide neural network trained under explicit distortion, with the framework's prediction of audit-blind behavior verified empirically on the network.

**Gap 2: The NTK regime is referenced but not exploited.**

`audit_blind_subspace.md` §1.4 mentions that for wide networks trained by gradient flow on quadratic loss, the distortion-to-function map $L$ has explicit kernel form via the Neural Tangent Kernel. This makes the audit-blindness theorems exact (no linearization error) in the NTK limit. But no numerical demonstration on actual neural networks is in the project.

This is the most immediately ready work: the math is established, the regime is tractable, the verification methodology mirrors the audit-blind ridge regression case directly.

**Gap 3: The framework is not connected to existing ML interpretability and safety tools.**

Influence functions, mechanistic interpretability, sparse autoencoders, backdoor-attack detection, and differential-privacy training all probe related structures. The framework's vocabulary (audit-blind subspaces, principal-angle geometry, four-object decomposition) maps onto these tools, but the map is not drawn. Without it, the framework is a parallel theoretical structure rather than an integrated piece of the ML safety toolkit.

### 1.3 Path 1 / Path 2 distinction reaffirmed

**Path 1** is the linearized-regime treatment: small distortions, NTK-style local linearization for wide networks, Fisher-tangent linearization for distributional outputs. The structural results (audit-blindness lower bound, dimension formula, optimal audit construction) hold exactly in this regime. The trilogy and the audit-blind subspace document are scoped to Path 1.

**Path 2** is the nonlinear regime: feature-learning, finite-width corrections, full training dynamics beyond gradient flow. The info-geometric reformulation provides the curvature corrections; quantitative magnitude predictions deviate by 15–25% from linearized predictions. Path 2 work is harder and remains substantially open.

The roadmap below distinguishes Phase 1–4 work (Path 1, immediate to medium-term) from Phase 5–6 work (Path 2, longer-term theoretical extensions).

---

## Part II — Phase 1: NTK Exact-Linearization Demonstration

This is the immediate next demonstration. It closes Gap 1 (no ML-side numerical companion) by constructing the wide-network analog of `audit_blind_verification.py`. The math is established (NTK theory), the regime is tractable (wide networks), the verification mirrors the ridge-regression case.

### 2.1 Setup

**Architecture.** Two-layer fully-connected MLP with widths $H \in \{256, 1024, 4096\}$:

$$f_\theta(x) = \frac{1}{\sqrt{H}} \sum_{j=1}^H W_2^{(j)} \,\sigma\!\left(W_1^{(j) \cdot} x + b_1^{(j)}\right) + b_2$$

with NTK parametrization (factor $1/\sqrt{H}$), ReLU activation, biases initialized to zero, weights initialized from $\mathcal{N}(0, 1)$. Output dimension 1 (regression). Input dimension $d = 20$.

The NTK parametrization is essential. Under standard parametrization, the loss landscape feature-learns; under NTK parametrization, gradient descent stays in the lazy-training regime where the kernel is approximately constant.

**Training data.** $n = 100$ inputs $x_i \in \mathbb{R}^{20}$ drawn i.i.d. from $\mathcal{N}(0, I)$. Base labels $y_0 \in \mathbb{R}^{100}$ generated by a fixed nonlinear function plus Gaussian noise.

**Training procedure.** Full-batch gradient descent on quadratic loss, learning rate $\eta = 10^{-2}$, run to near-zero training loss (typically $10^4$–$10^5$ steps for the moderate-width networks).

**Distortion.** Label perturbation $\xi \in \mathbb{R}^{100}$. Perturbed labels $y(\xi) = y_0 + \xi$.

**Audit.** $N = 5$ test queries at fixed locations $x^{\text{audit}}_1, \ldots, x^{\text{audit}}_5 \in \mathbb{R}^{20}$ drawn i.i.d. from $\mathcal{N}(0, I)$ (independent of training data).

### 2.2 Framework's prediction

In the NTK limit ($H \to \infty$), the trained function for distortion $\xi$ is

$$f_{\theta(\xi)}(x) = K_{\text{NTK}}(x, X) \, [K_{\text{NTK}}(X, X) + \lambda I]^{-1} (y_0 + \xi),$$

where $K_{\text{NTK}}$ is the empirical NTK at initialization, $X$ is the training input matrix, and $\lambda$ encodes the effective regularization from gradient descent's inductive bias. This is *exactly linear in $\xi$* in the NTK limit:

$$L_{\text{NTK}} \xi = K_{\text{NTK}}(\cdot, X) [K_{\text{NTK}}(X, X) + \lambda I]^{-1} \xi.$$

The audit-blind subspace prediction (from `audit_blind_subspace.md` Theorem 2):

$$\dim(\mathcal{N}_{\text{audit}}) = n - \mathrm{rank}(A_\mathcal{Q} \circ L_{\text{NTK}}) \geq n - N = 100 - 5 = 95.$$

User-relevant audit-blind dimension (Corollary 3.3.2):

$$\dim(\mathcal{N}_{\text{audit}}^{\text{user}}) \geq \dim(\Xi_{\text{vis}}) - N.$$

For NTK regression, $\Xi_{\text{vis}} = \mathrm{Range}(L^*)$ has dimension equal to the rank of $K_{\text{NTK}}(X, X)$ (typically $n = 100$ for non-degenerate kernels). So user-relevant audit-blind dimension $\geq 100 - 5 = 95$ — same as the full audit-blind dimension.

### 2.3 Verification methodology

**Step 1: NTK computation.** Compute the empirical NTK at initialization using `neural-tangents` or a custom Jacobian-product implementation. For width $H$:

$$K_{\text{NTK}}^{(H)}(x, x') = \langle \nabla_\theta f_\theta(x) \big|_{\theta_0}, \nabla_\theta f_\theta(x') \big|_{\theta_0}\rangle.$$

This converges to the limiting NTK $K_{\text{NTK}}^{(\infty)}$ as $H \to \infty$ at rate $O(1/\sqrt{H})$.

**Step 2: Audit-blind subspace construction.** Compute the matrix $B = X_{\text{audit}} \cdot [K_{\text{NTK}}^{(H)}(\text{audit}, X)]^T \cdot [K_{\text{NTK}}^{(H)}(X, X) + \lambda I]^{-1}$ — the audit map composed with the NTK-linearized distortion-to-function map. SVD of $B$ gives the audit-blind subspace as the right null space.

**Step 3: Construct two label distortions $\xi_1, \xi_2$ such that $\xi_1 - \xi_2 \in \mathcal{N}_{\text{audit}}^{\text{user}}$.** Pick a vector $v \in \ker(X_{\text{audit}}) \subset \mathbb{R}^d$ (the audit query points' null space), then $\xi$ such that $K_{\text{NTK}}^{(H)}(\cdot, X) \xi$ aligns with $v$. Concrete construction in §2.5.

**Step 4: Train both networks.** Run gradient descent on $(X, y_0 + \xi_1)$ and $(X, y_0 + \xi_2)$ to convergence. Save both trained networks.

**Step 5: Evaluate audit responses.** Compute $f_{\theta(\xi_1)}(x_i^{\text{audit}})$ and $f_{\theta(\xi_2)}(x_i^{\text{audit}})$ for $i = 1, \ldots, 5$. Predicted: identical (within finite-width corrections). Verify.

**Step 6: Evaluate on user queries.** Compute trained-function values at a separate test set $\{x_j^{\text{user}}\}_{j=1}^{50}$. Predicted: distinguishable. Verify.

**Step 7: Sweep width.** Run Steps 1–6 for $H \in \{256, 1024, 4096\}$. The audit-response agreement should improve as $H$ grows; the framework's structural prediction (audit-blind subspace exists, has predicted dimension) is exact in the limit.

### 2.4 Expected outcomes

**Width-dependence of audit-response agreement.** Audit responses to $\xi_1, \xi_2$ should agree to relative magnitude $O(1/\sqrt{H})$ — the NTK approximation error scale. Observed deviations larger than this would indicate either implementation issues or genuine deviations from NTK regime.

**Audit-blind subspace dimension.** Numerically computed audit-blind dimension (rank of $B$) should equal $n - N = 95$ for non-degenerate audit query sets. The dimension calculation depends only on $K_{\text{NTK}}^{(H)}$ at initialization and the audit query points; it is independent of training.

**Four-object identity.** Evaluated per principal direction between $\Xi_{\text{vis}}$ and $\mathcal{N}_{\text{audit}}^\perp$, the identity total = suppression + leakage should hold to machine precision. (This is exact at the operator level; no approximation involved.)

**User-query divergence.** $|f_{\theta(\xi_1)}(x_j^{\text{user}}) - f_{\theta(\xi_2)}(x_j^{\text{user}})|$ should be substantial for many $j$ — the audit-blind directions still affect user-facing function values, just not at the audit query points.

### 2.5 Concrete construction details

**Audit-blind label-perturbation construction.**

Let $K = K_{\text{NTK}}^{(H)}(X, X) + \lambda I \in \mathbb{R}^{n \times n}$, $K_a = K_{\text{NTK}}^{(H)}(\text{audit}, X) \in \mathbb{R}^{N \times n}$. The audit map is $A: \xi \mapsto K_a K^{-1} \xi$. The audit-blind subspace is $\ker(K_a K^{-1}) = K \cdot \ker(K_a)$.

For a unit norm $u \in \ker(K_a)$ (a $d - N$-dimensional space), $\xi := Ku$ lies in the audit-blind subspace. For two such $\xi_1 = K u_1, \xi_2 = K u_2$ with $u_1 \neq u_2$, both produce zero audit response and the user-facing function values differ by $K_{\text{NTK}}(\cdot, X)(u_1 - u_2)$ — a function in the trained network's NTK function space.

**Numerical implementation.**

```python
# Compute empirical NTK at initialization (using neural-tangents or custom)
K_train = compute_NTK(X_train, X_train, model_init)
K_audit = compute_NTK(X_audit, X_train, model_init)

# Audit-blind subspace
A = K_audit @ np.linalg.inv(K_train + lam * np.eye(n))
U, S, Vt = np.linalg.svd(A, full_matrices=True)
null_dim = (S < 1e-10).sum()
print(f"Audit-blind dim: {n - (S > 1e-10).sum()}, predicted >= {n - N}")

# Construct two distortions in the audit-blind subspace
xi_1 = construct_audit_blind_perturbation(K_audit, K_train, lam, choice=0)
xi_2 = construct_audit_blind_perturbation(K_audit, K_train, lam, choice=1)

# Verify A xi_j == 0 for both
assert np.linalg.norm(A @ xi_1) < 1e-12
assert np.linalg.norm(A @ xi_2) < 1e-12

# Train networks under each distortion
y_1 = y_0 + xi_1
y_2 = y_0 + xi_2
model_1 = train(X_train, y_1, model_init, n_steps=1e5)
model_2 = train(X_train, y_2, model_init, n_steps=1e5)

# Evaluate audit responses
audit_resp_1 = model_1(X_audit)
audit_resp_2 = model_2(X_audit)
print(f"Audit response divergence: {np.abs(audit_resp_1 - audit_resp_2).max()}")
# Predicted: O(1/sqrt(H))

# Evaluate user-query divergence
X_user = sample_user_queries(50)
user_resp_1 = model_1(X_user)
user_resp_2 = model_2(X_user)
print(f"User response divergence (RMS): {np.sqrt(np.mean((user_resp_1 - user_resp_2)**2))}")
# Predicted: substantial
```

### 2.6 Deliverables

- `ntk_audit_demonstration.py`: training script producing trained networks $f_{\theta(\xi_1)}, f_{\theta(\xi_2)}$ at three widths.
- `ntk_audit_companion.md`: writeup paralleling `audit_blind_subspace.md`'s ridge-regression example.
- Five figures: (1) setup with NTK kernel matrix, (2) audit-response convergence with width, (3) user-query divergence at fixed width, (4) four-object decomposition for the NTK case, (5) audit-blind subspace dimension vs predicted.
- `ntk_audit_verification.txt`: numerical record matching the structure of `audit_blind_verification.py`'s output.

### 2.7 Dependencies and time estimate

- Python with `jax`, `jaxlib`, `neural-tangents`, `numpy`, `matplotlib`.
- Compute: a single GPU is sufficient. Training time per network ~10 minutes at $H = 4096$, ~1 minute at $H = 1024$, ~10 seconds at $H = 256$. Total compute ~3–4 GPU-hours.
- Implementation complexity: moderate. NTK computation via `neural-tangents` is straightforward; audit-blind subspace construction follows the ridge-regression code in `audit_blind_verification.py` directly.

Time estimate for completion: 1–2 weeks of focused work (one researcher).

### 2.8 What this demonstration establishes

After Phase 1, the project has:

- The first ML-side numerical companion: a wide-MLP demonstration where the framework's audit-blind-subspace prediction matches empirical training behavior to within finite-width corrections.
- Empirical scaling of the linearization error: the $O(1/\sqrt{H})$ rate of NTK approximation confirmed.
- Direct connection to `audit_blind_subspace.md` Theorem A–B: the ridge-regression case is special case of the NTK case with $K_{\text{NTK}}$ replaced by a fixed linear kernel.

What it does *not* establish:

- Anything about feature-learning regime (Path 2). NTK regime is by construction the linearized regime.
- Anything about realistic-scale models. Wide MLPs in NTK regime are tractable; production transformers are not in the NTK regime.
- Anything about training dynamics beyond gradient flow on quadratic loss. RLHF, PPO, DPO are different regimes.

These limitations are addressed in subsequent phases.

---

## Part III — Phase 2: Toy RLHF Demonstration with Predicted Phantom Modes

This phase verifies `training_distortion_phantom.md`'s constraint-induced-distortion predictions on a controlled toy setup. It does for the RLHF case what Phase 1 does for label perturbation.

### 3.1 Setup

**Base model.** Logistic regression $\pi_0(y = 1 | x) = \sigma(w_0^T x)$ with $x \in \mathbb{R}^d$, $d = 20$. Pretrain $w_0$ on a base dataset $\{(x_i, y_i)\}_{i=1}^{n_{\text{pre}}}$, $n_{\text{pre}} = 1000$.

The choice of logistic regression is deliberate: the policy is a parametric distribution over $\{0, 1\}$, the Fisher tangent space at $\pi_0$ is identifiable explicitly, and the e-projection has a closed form. This makes `training_distortion_phantom.md`'s linearization exact.

**Constraint.** A safety constraint of the form: "the policy's output should not depend on feature 5 of the input." Mathematically, the constraint subspace is the 1D subspace of policy directions that change as $x_5$ changes (with all other features fixed):

$$\mathcal{C}_{\text{constraint}} = \mathrm{span}\left\{ \frac{\partial \log \pi(\cdot | x)}{\partial x_5} \right\}.$$

This is implemented via penalty term in training:

$$\mathcal{L}(w) = \mathcal{L}_{\text{base}}(w) + \mu \cdot \left(\partial_{x_5} \log \pi_w(y | x)\right)^2$$

averaged over a constraint dataset.

**Distortion.** As $\mu \to \infty$, the trained policy $\pi_\mu$ converges to the e-projection of $\pi_0$ onto the constraint manifold (Amari 2016, Chapter 6). The trained-policy distortion $\xi(\mu)$ in the Fisher tangent space is

$$\xi(\mu) = \mathbf{P}_{\mathcal{C}_{\text{constraint}}^\perp} \circ \log(\pi_\mu / \pi_0)$$

— the projection onto the orthogonal complement of the constraint subspace. The framework predicts this in advance from the base policy's Fisher information and the constraint specification.

### 3.2 Framework's predictions

**Phantom modes.** From `training_distortion_phantom.md` §2: the constraint-induced distortion produces specific changes in the policy's behavior on inference queries that *don't depend on feature 5* — these are the "phantom" effects, produced by the geometric pull of the constraint rather than by the constraint's literal content.

For inference query $q$ (a function on the input space), the change in the policy's expectation is

$$\langle q, \xi(\mu)\rangle_{\text{Fisher}} = \langle q, P_{\mathcal{C}_{\text{constraint}}^\perp} \log(\pi_\mu / \pi_0)\rangle_{\text{Fisher}}.$$

The framework predicts this for each $q$ from the geometry of $\mathcal{C}_{\text{constraint}}^\perp$ and the base-policy structure. Specifically, the four-object decomposition with $P_1 = $ projection onto the inference subspace spanned by $\{q_j\}$ and $P_2 = P_{\mathcal{C}_{\text{constraint}}^\perp}$ gives the per-direction phantom magnitudes.

**Quantitative prediction.** For the logistic-regression case with quadratic Fisher information (the Fisher information at $\pi_0$ is $X^T \mathrm{diag}(\pi_0(1-\pi_0)) X$ — explicit), the predicted phantom is computable in closed form.

### 3.3 Verification methodology

**Step 1: Base policy training.** Train $\pi_0$ on the pretrain dataset to convergence.

**Step 2: Constraint imposition.** Train $\pi_\mu$ for a sweep of $\mu$ values: $\mu \in \{0.1, 1, 10, 100, 10^3, 10^4\}$.

**Step 3: Phantom measurement.** For a battery of inference queries $\{q_j\}_{j=1}^{20}$ chosen to be orthogonal to the constraint direction, measure $\langle q_j, \log(\pi_\mu / \pi_0)\rangle$. These are the empirical phantom magnitudes per query direction.

**Step 4: Framework prediction.** Compute the predicted phantom magnitudes from the framework's formula. The prediction depends on: $\pi_0$ (the base policy, known after Step 1), the Fisher information at $\pi_0$ (computable explicitly), and the constraint specification (chosen).

**Step 5: Comparison.** Plot empirical vs predicted phantom per query as $\mu$ varies. Predicted: at large $\mu$, empirical converges to predicted (the e-projection limit). At small $\mu$, empirical converges to zero (no constraint imposed).

**Step 6: Curvature check.** At intermediate $\mu$, the linearization is approximate; the deviation from the linearized prediction should match the second-order curvature term from `info_geometric_reformulation.md` §B.5, scaling as $\|\xi\|^2$.

### 3.4 Expected outcomes

**Convergence to e-projection.** As $\mu$ increases, the trained policy approaches the e-projection of $\pi_0$ onto the constraint manifold. The empirical distortion $\xi(\mu)$ converges to the predicted distortion $\xi_{\text{e-proj}}$.

**Phantom magnitudes per query.** The framework's prediction for $\langle q_j, \xi_{\text{e-proj}}\rangle$ should match the empirical $\langle q_j, \log(\pi_\mu / \pi_0)\rangle$ at large $\mu$, to within the curvature-corrections envelope (15–25% in moderate-distortion regime).

**Four-object decomposition.** Per principal direction between the inference subspace and the constraint-orthogonal subspace, the four-object identity holds to machine precision (this is exact at the operator level).

### 3.5 Deliverables

- `toy_rlhf_demonstration.py`: training script with constraint-penalty sweep.
- `toy_rlhf_companion.md`: writeup with figures showing phantom magnitudes vs constraint strength.
- Five figures: (1) constraint geometry visualization, (2) empirical vs predicted phantom per query, (3) convergence to e-projection as $\mu$ grows, (4) four-object decomposition for this setup, (5) curvature corrections at intermediate $\mu$.
- `toy_rlhf_verification.txt`: numerical record.

### 3.6 Time estimate and dependencies

- Standard Python ML stack (pytorch or jax). No specialized libraries needed.
- Compute: CPU sufficient. Each model trains in seconds; full sweep ~10 minutes total.
- Implementation complexity: moderate. The Fisher information computation for logistic regression is explicit (textbook); the e-projection prediction involves matrix algebra in the parameter space.

Time estimate: 2–3 weeks (one researcher).

### 3.7 What this demonstration establishes

After Phase 2, the project has:

- A controlled-experiment verification of `training_distortion_phantom.md`'s predictions in the simplest possible setting (logistic regression, scalar output, explicit constraint).
- Direct measurement of the linearization error scaling with constraint strength.
- Empirical anchor for the curvature corrections from `info_geometric_reformulation.md`.

What it does *not* establish:

- Anything about RLHF on actual language models. The toy setup is a logistic regression. Production RLHF uses transformers, PPO/DPO, reward models trained from human feedback, etc. The framework's structural predictions extend; quantitative magnitudes do not.
- Anything about constraint specification in practice. The toy uses a clean mathematical constraint; production RLHF uses an implicit reward signal that itself has structure.

---

## Part IV — Phase 3: Pretraining-Corpus Hole Demonstration

This phase verifies `training_corpus_holes.md`'s phantom predictions on a controlled small-language-model setup. The "hole" is a topical gap in the training corpus; the phantom is the trained model's response on the held-out topic.

### 4.1 Setup

**Architecture.** Small transformer: 2 layers, $d_{\text{model}} = 128$, 4 attention heads, sequence length 64, vocabulary size $\sim 200$ (character-level for ASCII text). Total parameters $\sim 200K$.

**Base corpus.** 5 distinct topical domains, each $\sim 100K$ characters: (1) Python code, (2) classical music theory, (3) basic chemistry, (4) chess game records, (5) cooking recipes. The choice of unrelated topics is deliberate — they should have distinct surface-level vocabulary and structure with minimal overlap.

**Training.** Standard next-character-prediction with cross-entropy loss. Train for sufficient steps that the model achieves low perplexity on each domain individually (typically $10^5$–$10^6$ steps).

**Hole.** Hold out one of the five domains entirely from the training corpus. Train the model on the remaining 4 domains. Call this the "hole-trained" model.

**Reference model.** Train a separate model on all 5 domains. Call this the "complete-trained" model.

### 4.2 Framework's predictions

**Phantom on held-out domain.** The hole-trained model, when prompted with text from the held-out domain, will produce predictions that are *not* random or uniform. The framework predicts that the model's response is structured by the principal directions of the surrounding-corpus distribution projected onto the hole region.

Specifically: let $\nu$ be the corpus measure (probability over text continuations given context). Let $G$ be the hole region (text with held-out-domain content). The framework's prediction (`training_corpus_holes.md` §3): the trained model's predictions on $G$ are governed by

$$\pi_{\text{hole-trained}}|_G = \mathrm{Project}_{(\Omega \setminus G)}\bigl[\pi_{\text{complete-trained}}\bigr]$$

— i.e., the hole-trained model interpolates into the held-out region from the surrounding corpus, with the interpolation structured by the corpus's principal directions.

**Quantitative prediction.** The four-object decomposition with $P_1 = P_{\mathrm{Range}(L_{\text{trainable}})}$ (the directions of policy space that the model can learn) and $P_2 = M_{\Omega \setminus G}$ (the unmasked corpus region) gives:

- *Retention* on $\Omega \setminus G$: the hole-trained model performs well on the trained domains (high $\beta$, retention $\beta^2 \approx 1$).
- *Suppression* on $G$: the hole-trained model has poor performance on the held-out domain (low $\beta$ in the inference subspace orthogonal to surrounding corpus).
- *Leakage*: the hole-trained model's responses on $G$ have specific structure inherited from surrounding-corpus principal directions — *not* random, *not* uniform, but specifically aligned with the most-prominent principal directions in $\Omega \setminus G$.

The leakage prediction is the most testable: the hole-trained model's predictions on held-out-domain text should have specific identifiable structure from the surrounding domains.

### 4.3 Verification methodology

**Step 1: Train both models.** Train the hole-trained model and the complete-trained model with otherwise identical settings (same architecture, same total tokens seen, same training schedule).

**Step 2: Evaluate on each domain.** Measure perplexity of both models on each of the 5 domains. Predicted: hole-trained model has approximately equal perplexity with complete-trained on the 4 in-corpus domains, dramatically higher perplexity on the held-out domain.

**Step 3: Identify principal directions of surrounding corpus.** Compute principal-component analysis or sparse-autoencoder decomposition on the 4 in-corpus domains' representations in the hole-trained model's hidden space.

**Step 4: Project hole-trained model's predictions on held-out domain onto principal directions.** Compare with: (a) random baseline, (b) prediction from surrounding-corpus average. The framework predicts hole-trained predictions on held-out domain align with leading principal directions of the surrounding corpus.

**Step 5: Four-object decomposition measurement.** With $P_1$ = the predicted-direction subspace from the framework, $P_2$ = the empirical projection structure, compute principal angles between the two. Predicted: small principal angles (the framework's prediction matches the empirical prediction structure).

### 4.4 Expected outcomes

**Hole-domain perplexity gap.** The hole-trained model has dramatically higher perplexity on the held-out domain than the complete-trained model. (This is well-established empirically in language modeling literature; the framework provides the theoretical reading.)

**Structured held-out predictions.** The hole-trained model's predictions on the held-out domain are not uniform-random; they have structure from the surrounding corpus. The structure is computable from the framework's prediction.

**Quantitative match.** The framework's prediction for the hole-trained model's response on the held-out domain (in terms of principal directions of the surrounding corpus) should match empirically to within Path 2 corrections. The Path 2 corrections here are non-trivial because language-model training is highly nonlinear; the linearized prediction is a structural-claim only, with magnitude deviations of perhaps 30-50% from naive linear interpolation.

**Identification of compounding regime.** With the corpus-hole and one explicit additional constraint (e.g., a held-out token + a safety filter), the question of whether they compound or cancel becomes empirically testable. From `training_corpus_holes.md` §5.2 (corrected): aligned filter+constraint is least compounding; orthogonal filter+constraint compounds maximally.

### 4.5 Deliverables

- `pretraining_hole_demonstration.py`: training script for both models.
- `pretraining_hole_companion.md`: writeup with figures.
- Five figures: (1) corpus structure across 5 domains, (2) perplexity per domain comparison, (3) principal-direction decomposition of surrounding corpus, (4) hole-trained predictions vs framework's structured-prediction, (5) four-object decomposition for the hole geometry.
- `pretraining_hole_verification.txt`: numerical record.

### 4.6 Time estimate and dependencies

- Standard transformer training stack (pytorch + transformers library).
- Compute: GPU strongly preferred. Training each model takes ~6–12 GPU-hours; full demonstration with sweep ~30–50 GPU-hours.
- Implementation complexity: moderate-high. The framework prediction step requires careful handling of the inference subspace specification and the principal-direction analysis.

Time estimate: 4–6 weeks (one researcher). Higher uncertainty than Phases 1–2 due to nonlinearity of language-model training.

### 4.7 What this demonstration establishes

After Phase 3, the project has:

- A pretraining-corpus-holes verification on a small language model with controlled topical structure.
- Empirical magnitude of Path 2 corrections in nonlinear language-model training.
- Concrete demonstration of the corpus-hole-induced phantom phenomenon.

What it does *not* establish:

- Anything about production-scale language models. The toy is character-level on a small corpus; production models are sub-word on web-scale corpora.
- Anything about specific real-world holes (training-data filtering, content policies, etc.). The toy's hole is artificially clean.

---

## Part V — Phase 4: Influence-Function Integration

Influence functions (Koh–Liang 2017) compute $\partial F / \partial \xi_i$ — the effect of perturbing the $i$-th training example on a specific test query's prediction. The framework's $L = dF|_0$ is exactly the influence-function derivative considered as a linear operator. This phase establishes the integration.

### 5.1 Setup

**Pretrained model.** A small fine-tuned language model from a standard dataset (e.g., a GPT-2 small fine-tuned on a specific domain), or a vision model (ResNet-18 on CIFAR). The choice is dictated by influence-function-library availability — the EK-FAC influence-function library from `transformers` works on language models; standard libraries work on vision.

**Concerning subspace specification.** Choose a specific behavioral concern: e.g., "the model's prediction on a specific test image $x^*$." The concerning subspace $\mathcal{C}_{x^*}$ is the 1D subspace of training-data perturbations that change the model's prediction on $x^*$.

### 5.2 Framework's predictions

**$L^* q$ via influence functions.** For test query $q$ (e.g., $q(f) = f(x^*)$), the adjoint $L^* q$ is the influence function $I(\cdot, x^*)$ — a function on training-data perturbation space:

$$(L^* q)(\xi) = \langle q, L\xi\rangle = \mathrm{InfluenceFunction}(\xi, x^*).$$

For point training-data perturbations $\xi = \delta_{i}$, this gives $\mathrm{IF}(\text{example}_i, x^*)$ — the standard influence-function value.

**Audit-blind subspace via SVD of influence functions.** From `audit_blind_subspace.md` Theorem D, the optimal audit suite for $\mathcal{C}_{x^*}$ has size 1 (since $\dim \mathcal{C}_{x^*} = 1$): the single query $q^* = x^*$ itself. The audit-blind subspace for this audit is $\ker(L^* q^*) = \{ \xi : I(\xi, x^*) = 0\}$ — training-data perturbations with zero influence on $x^*$. The framework predicts this subspace has dimension at least $n_{\text{train}} - 1$ (most training examples have non-zero influence; the audit-blind subspace is at most one-codimensional).

### 5.3 Verification methodology

**Step 1: Compute influence functions on the pretrained model.** Standard EK-FAC procedure: $I(\text{example}_i, x^*) = - g_{x^*}^T H^{-1} g_i$ where $g$ is gradients and $H$ is the Hessian (approximated via EK-FAC).

**Step 2: Identify audit-blind training examples.** Sort training examples by influence on $x^*$. The audit-blind subspace contains directions of zero-influence; typically a few training examples have very low influence on any specific test query.

**Step 3: Construct audit-blind perturbations.** Specifically: linear combinations of low-influence training examples that have zero net influence on $x^*$.

**Step 4: Verify.** Add these perturbations to the training data, re-train, evaluate the model on $x^*$. Predicted: prediction on $x^*$ is approximately unchanged (within the linearization-error envelope).

**Step 5: User-query verification.** The audit-blind perturbations, while not affecting $x^*$, should affect *other* test queries. Evaluate on a held-out user-query set and confirm that the model's predictions diverge from baseline on at least some queries.

### 5.4 Expected outcomes

**Audit-blind perturbations exist and are constructible.** Training-data perturbations with zero (or near-zero) influence on a specific query $x^*$ can be constructed, do not affect predictions on $x^*$ after retraining, and *do* affect predictions on other queries.

**Influence-function magnitude as predictor.** Examples with low $|I(\text{example}_i, x^*)|$ are good candidates for audit-blind perturbations. The framework's structural prediction (audit-blind subspace exists) is verified empirically.

**Magnitude of finite-data effects.** EK-FAC influence functions are themselves approximations; the framework's prediction is the derivative-at-base; the empirical retraining uses finite-data updates. Quantitative agreement should be at the 10–30% level.

### 5.5 Deliverables

- `influence_function_audit_demonstration.py`: implementation using existing influence-function libraries.
- `influence_function_audit_companion.md`: writeup connecting the framework's machinery to influence-function methodology.
- Five figures: (1) influence-function distribution across training examples, (2) construction of audit-blind perturbation, (3) prediction on $x^*$ before and after audit-blind perturbation, (4) prediction divergence on user queries, (5) framework-vs-empirical comparison.
- `influence_function_audit_verification.txt`: numerical record.

### 5.6 Time estimate and dependencies

- Standard ML stack + influence-function library (e.g., `kronfluence` for EK-FAC, or custom implementation).
- Compute: substantial. Influence-function computation is expensive; retraining is expensive. Total ~50–100 GPU-hours.
- Implementation complexity: high. Influence functions on transformers have many implementation pitfalls; verification requires careful retraining setup.

Time estimate: 6–8 weeks (one researcher).

### 5.7 What this demonstration establishes

After Phase 4, the project has:

- A direct connection between the framework's $L^*$ and standard influence-function methodology.
- Empirical demonstration of audit-blind subspaces on a real (small) trained model.
- Identification of the framework as a structural account of why influence functions face systematic uncertainty.

---

## Part VI — Phase 5: Mechanistic-Interpretability Integration

Mechanistic interpretability identifies circuits, features, and directions in network internals. The framework's white-box audit (Theorem 7 in `audit_blind_subspace.md`) treats these as $A_\mathcal{Q}^{\text{white}}$ probes. This phase establishes the integration on a small interpretable model.

### 6.1 Setup

**Model.** A small attention-only transformer (1 or 2 layers), small enough that mechanistic-interpretability circuits can be identified explicitly. The "ARENA-style" toy setting: induction heads, simple in-context learning, etc.

**White-box probe suite.** Standard mech-interp probes:
- Activation patching: substitute activations from one prompt into another, measure effect.
- Sparse autoencoder features: SAE-decoded features as probes.
- Attention-pattern probes: read attention patterns at specific layer-head combinations.

**Distortion specification.** Training-data perturbations as in Phases 3–4; the question is whether white-box probes detect distortions that black-box probes miss.

### 6.2 Framework's predictions

**White-box audit-blind subspace.** Theorem 7 in `audit_blind_subspace.md`: with white-box probes producing $N_{\text{white}}$ readouts, the white-box audit-blind subspace has dimension at least $\dim(\Xi_{\text{vis}}) - N_{\text{white}}$ — same structural form as black-box audit, with the audit budget $N$ replaced by the white-box probe count.

The framework's structural prediction: white-box audits face the same audit-blindness lower bound, just at a typically larger $N_{\text{white}}$ (mech-interp probes are typically more numerous than test queries, but bounded by the probe-suite design).

**Quantitative coverage.** For a specific concerning subspace $\mathcal{C}$, the white-box audit-coverage fraction is computable from the principal angles between $\mathcal{C}$ and the white-box probe subspace. Mech-interp's "richer probes" claim corresponds to a larger probe subspace; the framework's prediction is that audit-coverage scales with probe-subspace dimension, not with sophistication of individual probes.

### 6.3 Verification methodology

**Step 1: Establish baseline mech-interp picture.** Identify the model's internal circuits using standard mech-interp methods. Document the probes available.

**Step 2: Construct distortions in the audit-blind subspace.** Following Phase 4's influence-function construction, but for white-box probes: identify training-data perturbations with zero predicted effect on the chosen white-box probes.

**Step 3: Apply distortion, retrain.** Train the model with the perturbed training data.

**Step 4: Verify.** White-box probes' readouts on the retrained model should be near-baseline; the model's behavior on user queries should differ from baseline.

**Step 5: Probe-subspace expansion.** Show that adding more probes (richer mech-interp suite) reduces but does not eliminate the audit-blind subspace. The framework's prediction: dimension reduces by exactly the rank of the new probes.

### 6.4 Expected outcomes

**Demonstration of white-box audit-blindness.** A specific, constructed distortion that's invisible to a chosen mech-interp probe suite but affects user-facing behavior.

**Coverage vs probe count.** Empirical confirmation that white-box audit-coverage scales with probe-subspace dimension.

**Identification of the structural ceiling.** Even fully-instrumented mech-interp on a small model has a non-zero audit-blind subspace; the framework provides the dimension calculation.

### 6.5 Deliverables

- `mechinterp_audit_demonstration.py`: implementation on a small transformer.
- `mechinterp_audit_companion.md`: writeup connecting framework to mech-interp.
- Five figures: (1) baseline mech-interp picture, (2) construction of white-box audit-blind perturbation, (3) probes' readouts after retraining, (4) user-behavior divergence, (5) audit-coverage as probe count grows.
- `mechinterp_audit_verification.txt`: numerical record.

### 6.6 Time estimate and dependencies

- Mech-interp tools (TransformerLens, sparse-autoencoder libraries, ARENA-style notebooks).
- Compute: moderate (small models). ~20–40 GPU-hours.
- Implementation complexity: high. Mech-interp has its own conventions and tooling; integration with the framework's machinery requires careful translation.

Time estimate: 8–10 weeks (one researcher).

### 6.7 What this demonstration establishes

After Phase 5:

- Direct connection between the framework's white-box audit theorem and current mech-interp practice.
- Concrete demonstration that mech-interp faces structural audit-blindness limits.
- Identification of probe-subspace dimension as the central audit-coverage metric.

---

## Part VII — Phase 6: Path 2 — Nonlinear Training Dynamics

Phases 1–5 are Path 1 (linearized regime). Path 2 addresses the nonlinear training-dynamics regime — feature learning, finite-width networks beyond NTK, full training dynamics beyond gradient flow.

### 7.1 Theoretical extensions needed

**Feature learning regime.** At finite width or under non-NTK parametrization, the kernel is not constant during training. The distortion-to-function map is no longer linear; the audit-blind subspace's dimension formula becomes a generic-rank claim rather than an exact identity.

Specific question: does the audit-blindness lower bound (Theorem B) hold in feature-learning regime, or does feature learning create new audit-coverage that the linearized analysis misses?

Conjecture: Theorem B holds in modified form — at any point during training, the audit-blind subspace at the *current* base point has dimension at least $\dim(\Xi) - N$. But the audit-blind subspace *changes* during training in feature-learning regime, so audit responses at different times reveal different subspaces. Compositional auditing across training time partially substitutes for spatial audit-coverage.

**Beyond gradient flow.** RLHF uses PPO; offline preference learning uses DPO; constitutional AI uses reward-model bootstrapping. None is gradient flow on quadratic loss.

For PPO: the trust-region constraint introduces a step-size dependence. The linearized analysis at the policy at PPO step $t$ is valid for the next gradient step; iterating across many PPO steps requires composing many linearizations. The audit-blind subspace at the final policy is the intersection across all iterates, not a single subspace.

For DPO: the loss is non-quadratic but smooth. The Fisher-tangent linearization at the base policy still applies; the predicted distortion is the e-projection in the appropriate tangent space.

**Multi-distortion composition.** Real training pipelines have multiple stages: pretraining, instruction tuning, RLHF, safety filtering. Each stage applies a distortion. The composite distortion is the composition.

The framework's prediction (from `training_corpus_holes.md` §5.2 corrected): aligned distortions least compounding; orthogonal distortions compound maximally. Quantitative composition formulas are open.

### 7.2 Theoretical work

This phase is *primarily theoretical* rather than demonstrational. Each of the three extensions above requires mathematical development:

**Feature-learning audit-blindness.** Develop the audit-blindness theorem in the moving-base-point regime. Key technical tool: time-dependent linearization, with the tangent space changing as training proceeds. Establish whether the time-integrated audit-blind subspace shrinks or stays at the lower bound.

**Beyond gradient flow.** Develop the audit-blindness theorem for PPO-style trust-region updates and DPO-style offline preference learning. Each has its own canonical linearization; the question is whether the audit-blind subspace structure carries through.

**Multi-distortion composition.** Develop quantitative composition formulas for the four-object decomposition under successive distortions. Explicit calculation in the principal-angle basis: composition of two distortions $\xi_1, \xi_2$ produces a distortion in $\Xi$ whose audit-coverage depends on the principal angles between $\xi_1, \xi_2$ and the audit subspace.

### 7.3 Numerical companion (smaller-scale)

A scaled-down version of Phase 1 with feature-learning regime: standard-parametrization MLP at moderate width $H = 256$, where feature learning is non-trivial. Verify the audit-blindness theorem holds in modified form (predicted audit-blind subspace dimension at convergence is $\geq \dim(\Xi) - N$).

### 7.4 Deliverables

- Three theoretical writeups (one each for feature learning, beyond gradient flow, composition).
- `path2_demonstration.py`: feature-learning numerical companion.
- `path2_companion.md`: integrated writeup of the Path 2 results.
- Five figures.

### 7.5 Time estimate and dependencies

This phase is research-grade theoretical work. Time estimate: 6–12 months for substantial progress on any one of the three extensions. Multi-year for all three.

### 7.6 What Path 2 establishes (when complete)

- The framework's audit-blindness theorem in nonlinear regimes (feature learning, beyond gradient flow).
- Quantitative composition rules for multi-stage training pipelines.
- Concrete predictions for production-scale training settings.

What it does *not* establish:

- Anything about specific production decisions (this is theoretical work; application to specific systems is its own program).
- Anything beyond the framework's chosen abstraction (the operator-theoretic, principal-angle-based machinery). Other theoretical apparatus may give different conclusions.

---

## Part VIII — Theoretical Open Questions

Independent of the demonstration phases, several theoretical questions remain open:

### 8.1 Tightness of the audit-blindness lower bound

`audit_blind_subspace.md` Theorem 3 gives a *lower* bound: $\dim(\mathcal{N}_{\text{audit}}) \geq \dim(\Xi) - N$. The bound is tight when the audit suite is chosen orthogonally to the concerning subspace and loose otherwise.

Open question: for typical audit suites used in current alignment-evaluation practice (HELM, MMLU, Anthropic evaluation suites), how loose is the bound on production models? The ratio $\dim(\mathcal{N}_{\text{audit}}^{\text{user}}) / [\dim(\Xi_{\text{vis}}) - N]$ measures the looseness; estimating it on production systems is open empirical work.

Conjecture: for current evaluation suites, the bound is significantly loose because the suites are not constructed to maximize coverage of specific concerning subspaces. Constructed audit suites (Theorem 5) would close some of this gap.

### 8.2 Composition of multiple audits

If two audits $\mathcal{Q}_1, \mathcal{Q}_2$ are run, the combined audit's blind subspace is

$$\mathcal{N}_{\text{audit}}^{\mathcal{Q}_1 \cup \mathcal{Q}_2} = \mathcal{N}_{\text{audit}}^{\mathcal{Q}_1} \cap \mathcal{N}_{\text{audit}}^{\mathcal{Q}_2}.$$

When the two audits are independent (their query subspaces don't overlap in $H$), the combined audit-blind dimension is $\dim(\Xi) - N_1 - N_2$. When they overlap (shared queries), the combined dimension is larger.

Open question: how to optimally compose multiple audit types (black-box + white-box + procedural) for a given total audit budget? The composition is non-trivial when each audit type has its own cost-per-query structure.

### 8.3 Sensitivity to base-point choice

The framework linearizes at a chosen base point (the undistorted policy / model). Different base points give different linearizations and different audit-blind subspaces.

Open question: how does the audit-blind subspace depend on the choice of base point? In the small-distortion regime, all base points near the actual operating point should give equivalent audit-blind subspaces; in larger-distortion regime, different base-points may give substantially different audit-blind subspace dimensions.

This matters for production: the "base point" of a deployed model is its current state, which is itself a distortion of some pretrained checkpoint. The framework's predictions depend on which base point is chosen.

### 8.4 Cross-modality distortions

The framework treats distortion-to-function maps within a single modality (text-to-text, image-to-text, etc.). Multi-modal models have distortions that affect multiple modalities; the audit-blind subspace structure across modalities is more complex.

Open question: develop the audit-blindness theorem for multi-modal models. The distortion space $\Xi$ has structure (modality-specific subspaces); the audit map has cross-modality interactions.

### 8.5 Adversarial audit construction

Audit-suite design (Theorem 5) is constructive given the concerning subspace. But what if the auditor's concerning subspace is itself unknown or adversarially-chosen?

Open question: develop adversarial audit-construction theory. Given a class of possible concerning subspaces $\{\mathcal{C}_\alpha\}$, find an audit suite that maximizes minimum coverage across the class. This is a robust optimization problem in audit-suite design space.

### 8.6 Sample complexity of audit verification

Verifying that an audit covers its claimed concerning subspace requires testing. If the audit is supposed to detect distortions in $\mathcal{C}$, verifying this requires sampling distortions in $\mathcal{C}$ and confirming the audit detects them.

Open question: develop sample-complexity bounds for audit-verification. The verification cost depends on $\dim(\mathcal{C})$ and the desired confidence level.

---

## Part IX — Practical Implementation Playbook

For an ML practitioner wanting to apply the framework to a specific audit project, the following playbook describes the procedure.

### 9.1 Step 1: Scope the concerning subspace

Question to answer: "What kinds of distortion do I want my audit to detect?"

Concrete specifications:
- A behavioral concern (e.g., "the model should not produce harmful outputs on prompts of type T"). Translate to: $\mathcal{C}$ = subspace of distortions affecting outputs on prompts of type T.
- A truth-anchored concern (e.g., "the model should accurately answer factual questions"). Translate to: $\mathcal{C}$ = subspace of distortions affecting factual-question outputs.
- A demographic concern (e.g., "outputs should not differ by demographic"). Translate to: $\mathcal{C}$ = subspace of distortions producing demographic differentials.

Explicit specification of $\mathcal{C}$ is the auditor's input; the framework operates given $\mathcal{C}$.

### 9.2 Step 2: Identify the linearization regime

Choices:
- NTK regime: applicable to wide networks trained by gradient flow on quadratic loss. Linearization is approximately exact.
- Fisher tangent at base policy: applicable to RLHF/DPO. Linearization is exact for small distortions.
- Standard local linearization: applicable broadly. Linearization is approximate, with quantitative magnitude corrections.

The choice depends on the production system. For most production language models, the NTK regime does not apply (they are not in lazy-training regime); the Fisher-tangent linearization at the current policy is the natural choice.

### 9.3 Step 3: Compute $L^*$ on the concerning subspace

For each direction in $\mathcal{C}$, compute its image under $L^*$ — the audit-relevant readout of that direction. Methods:

- For training-data perturbations: use influence functions (EK-FAC or equivalent).
- For RLHF reward perturbations: use the framework's e-projection formula at the current policy.
- For data-distribution perturbations: use the curvature term from `info_geometric_reformulation.md` §B.5 for magnitude calibration.

The output is a representation of $L^*|_\mathcal{C}$ in a tractable basis.

### 9.4 Step 4: SVD and audit-suite construction

Apply Theorem 5: compute SVD of $L|_\mathcal{C}$ to get the optimal audit-suite construction. The query suite $\{q_j^*\}$ corresponds to the top-$k$ left singular vectors (where $k = \dim(\mathcal{C})$).

For under-resourced audit ($N < k$): use Theorem 6, take top-$N$ singular vectors as the audit queries. The audit-blind subspace contains the bottom $k - N$ singular directions.

### 9.5 Step 5: Verify predicted coverage

The audit suite has predicted coverage fraction (Lemma 4.4.2) computable from the singular values. Verify by:
- Constructing test distortions in $\mathcal{C}$.
- Applying the audit; measuring detection rates.
- Comparing to predicted detection rates.

Sample complexity for verification depends on desired confidence; rule of thumb is $O(\dim(\mathcal{C}))$ test distortions per direction.

### 9.6 Step 6: Run the audit

Apply the constructed audit suite to the production system. Interpret the results through the framework's vocabulary:
- Each audit query returns a magnitude.
- The four-object decomposition (computed in Step 3) tells which directions of $\mathcal{C}$ each query is sensitive to.
- The audit's interpretation is in the principal-direction basis of $L|_\mathcal{C}$.

### 9.7 Failure modes

- *The concerning subspace is misspecified.* Auditor's $\mathcal{C}$ doesn't match the real concern. Mitigation: develop $\mathcal{C}$ iteratively, adjust audit construction.
- *The linearization is poor.* Production-scale models may be far from the linearized regime. Mitigation: use Path 2 corrections; calibrate against the curvature envelope.
- *$L^*$ computation is expensive.* For large models, influence-function computation can be prohibitive. Mitigation: scale-down with ablations; use proxy models for audit-suite construction.
- *Audit budget is insufficient.* If $N < \dim(\mathcal{C})$, full coverage is impossible (Theorem 6). Mitigation: prioritize directions; combine with other audit types.

---

## Part X — Connection to Existing ML Literature

The framework's machinery maps onto several existing ML research directions:

### 10.1 Influence functions and data attribution

(Koh–Liang 2017; Grosse et al. 2023.)

Mapping: the framework's $L^*$ is the influence-function operator. Influence-function methods compute $L^* q$ for specific test queries $q$. The audit-blindness lower bound (Theorem B) applies: with $N$ test queries, at most $N$ directions of training-data influence are recoverable, leaving at least $n_{\text{train}} - N$ audit-blind.

The framework's contribution: structural account of why influence functions face fundamental uncertainty, not just computational difficulty. The uncertainty is information-theoretic.

### 10.2 Mechanistic interpretability

(Olah et al.; circuits-thread; sparse autoencoders.)

Mapping: mechanistic-interpretability probes are white-box audits ($A_\mathcal{Q}^{\text{white}}$ in Theorem 7). Rich probe suites correspond to large $N_{\text{white}}$. Structural ceiling: even fully-instrumented mech-interp has audit-blind subspaces of dimension $\dim(\Xi_{\text{vis}}) - N_{\text{white}}$.

The framework's contribution: explicit dimension of what cannot be recovered from the network's internals via probes. Identifies probe-subspace dimension as the central coverage metric.

### 10.3 Backdoor attacks

(Gu–Dolan-Gavitt–Garg 2017; Wallace et al. 2021.)

Mapping: backdoor attacks construct $\xi_{\text{backdoor}} \in \mathcal{N}_{\text{audit}}$ for the standard evaluation suite. The framework generalizes from "specific known attacks" to "the full equivalence class of audit-indistinguishable distortions."

The framework's contribution: explicit characterization of the attack surface as a subspace of distortion space, with dimension formula.

### 10.4 Differential privacy and training-data anonymization

(Dwork et al.; DP-SGD.)

Mapping: DP training imposes constraints on $\xi \mapsto F(\xi)$. The audit-blind subspace structure interacts with DP constraints in non-trivial ways.

Open question: develop the framework's machinery in the presence of DP constraints. The DP bound on $\partial F/\partial \xi$ corresponds to a specific structure of $L$; the audit-blind subspace has explicit dimension under this constraint.

### 10.5 Sparse autoencoders and feature directions

(Bricken et al. 2023; Cunningham et al. 2023.)

Mapping: SAE-decoded features are a specific basis for the network's hidden space. They correspond to a specific subspace of $\Xi$ (the directions of distortion that change SAE feature activations). The framework's audit-blindness analysis applies with this subspace as $\mathcal{Q}^*$.

The framework's contribution: structural account of SAE coverage. SAE features cover a specific subspace; the audit-blind subspace for SAE-feature probes is computable.

### 10.6 Data attribution and training-data influence

(TRAK, Ilyas et al. 2022; data-models.)

Mapping: data attribution methods compute the influence of training subsets on model behavior. This is the framework's $L$ at scale. The audit-blindness lower bound applies; the structural prediction is that finite numbers of behavior-probes leave large training-data subsets unattributable.

The framework's contribution: information-theoretic ceiling on data-attribution methods, set by the probe-budget vs. data-space-dimension ratio.

---

## Part XI — Roadmap Summary

| Phase | Description | Time | Compute | Dependencies |
|---|---|---|---|---|
| 1 | NTK exact-linearization demonstration | 1–2 weeks | 3–4 GPU-h | jax, neural-tangents |
| 2 | Toy RLHF demonstration | 2–3 weeks | CPU | pytorch/jax |
| 3 | Pretraining-corpus hole demonstration | 4–6 weeks | 30–50 GPU-h | transformers |
| 4 | Influence-function integration | 6–8 weeks | 50–100 GPU-h | kronfluence |
| 5 | Mechanistic-interpretability integration | 8–10 weeks | 20–40 GPU-h | TransformerLens, SAE libs |
| 6 | Path 2: nonlinear training dynamics | 6+ months | Variable | (theoretical) |

Phases 1–3 are the immediate path. They establish the missing ML-side numerical companions and verify the framework's predictions on toy versions of the three primary ML scenarios (label perturbation, RLHF, pretraining holes). Together they take roughly 2 months of focused work and close Gap 1 of the current state.

Phases 4–5 establish integration with existing ML interpretability and safety tools. They are 14–18 weeks of additional work. Together they close Gap 3.

Phase 6 is open-ended theoretical research on Path 2 extensions. It does not have a closing date.

---

## Development Record

This document is a research roadmap, not a research result. Its content is descriptive (current state, planned work) rather than novel-mathematical. The novel-mathematical content of the framework is in the trilogy and the audit-blind-subspace document.

What this document does:

- Catalogs the current state of the ML extension (three working documents plus the audit-blindness paper).
- Identifies three structural gaps (no numerical companions; NTK regime unexploited; no integration with existing ML tools).
- Specifies six phased work-items with concrete technical details, deliverables, and time estimates.
- Documents theoretical open questions independent of the demonstration phases.
- Provides a practical implementation playbook for applying the framework.
- Maps the framework onto existing ML research directions.

What this document does not do:

- Establish new theorems. (Those are in the trilogy and the audit-blindness paper.)
- Commit to specific timelines. The estimates are approximate; actual time depends on availability and unforeseen technical issues.
- Address the spectral-side of the project (Phantom suite notebooks, CCG, etc.) — those are independent.
- Address the four statistical realizations (`pca_masked_companion.md`, etc.) — those are independent.

The role of this document. The Phantom Framework currently has its spectral side mature (notebooks + writeups) and its statistical side mature (abstract spine + four numerical companions). The ML side has the abstract apparatus (trilogy + audit-blindness paper) but lacks the concrete numerical companions and the integration with existing ML tools. This document specifies what work would close those gaps and in what order.

The work described here is approximately one researcher-year for Phases 1–5 and indeterminate for Phase 6. Whether to undertake it depends on what the project is for. If the goal is to establish the framework theoretically, the existing apparatus suffices. If the goal is to demonstrate the framework's predictive content empirically on ML systems and to integrate it with existing ML research, the phases above are the path.

The phases are ordered by readiness: Phase 1 is immediately actionable with established tools; Phase 6 requires substantial theoretical development. The order is also approximately in increasing dependency: each phase's deliverables feed the subsequent phases (Phase 2 uses Phase 1's NTK setup; Phase 4 uses Phase 3's pretrained models; Phase 5 builds on Phase 4's influence-function work).

A version of this roadmap with executed phases would itself be a substantial addition to the project. As written, this is the planning document for that addition.
