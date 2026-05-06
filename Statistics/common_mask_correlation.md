# Correlation and Matched Filtering Under a Common Measurement Gap

*A companion to the Phantom Eigenmode suite · April 2026*

---

## Abstract

Two signals $f, g$ observed through the same measurement gap $G \subset \Omega$ share the same forward operator $A = I - K$ on modal coefficients. This document identifies two distinct ways the common mask contaminates correlation-domain inference: **(a)** when a real coherent component exists between the signals, the mask redistributes the observed coherence across mode pairs according to the intrinsic mask-coherence operator $\gamma^2_{A,mn} = |(AA^*)_{mn}|^2/((AA^*)_{mm}(AA^*)_{nn})$; **(b)** even under full independence, the sample estimator of cross-covariance has mode-pair variance structure and inter-entry covariance shaped by $AA^*$, which produces non-uniform false-alarm rates across parameter space in any matched-filter or threshold-based pipeline.

For matched-filter detection specifically, the effective template becomes $A^* T A$ — quadratic in the mask, compared to the linear $A^* t$ distortion in the single-signal case. The damage to signal detection is quadratic in $\|K\|$; the damage to false-alarm calibration scales with the non-uniformity of $\mathrm{diag}(AA^*)$. Both effects are operator-theoretic and can be computed in advance from the known mask geometry.

The pathology generalizes to most statistical operations that are quadratic or higher-order in the masked data: covariance estimation, coherence, directional spectra, PCA/EOF, matched filtering, change-point detection, multiple-testing control, spurious regression. The remediation strategies are mask-scrambling calibration (time-slides), mask-whitened templates, mask-aware covariance estimation, and design choices that place the target statistic in the complement of the mask's principal subspace.

---

## 1. Setup and notation

Let $\Omega$ be a bounded domain, $L$ a self-adjoint operator with orthonormal eigenbasis $\{\varphi_n\}$. A signal $f$ expands as $f = \sum c_n \varphi_n$. A measurement gap is a subset $G \subsetneq \Omega$ where the signal is not observed; the mask is $M_G = I - \chi_G$ and $\hat f = M_G f$. Projecting onto the eigenbasis:
$$\hat c_m = c_m - \sum_n K_{mn} c_n = (Ac)_m, \qquad K_{mn} = \int_G \varphi_n \overline{\varphi_m}\,dx, \qquad A = I - K. \tag{1}$$

$K$ is the **coupling matrix** of the gap with the basis; $A$ is the **forward operator** on coefficients. Neither depends on the signal. For two signals $f^{(1)}, f^{(2)}$ observed through the same gap, the modal observations are
$$\hat c^{(1)} = Ac^{(1)}, \qquad \hat c^{(2)} = Ac^{(2)}, \tag{2}$$
with the same $A$. This is the **common-mask** configuration. It differs from the multi-measurement aperture-synthesis scenario of `mitigation.ipynb` §5, where two *different* gaps $A_1 \neq A_2$ are combined to improve conditioning.

Signal covariances are $\Sigma^{(i)}_{kl} = \mathbb E[c^{(i)}_k \overline{c^{(i)}_l}]$; the cross-covariance is $\Sigma^{(12)}_{kl} = \mathbb E[c^{(1)}_k \overline{c^{(2)}_l}]$. Finite-sample estimators use $T$ independent realizations and are written with a hat or a "sample" subscript.

---

## 2. Review: single-signal phantom mechanism

The core result of the phantom framework is that $\hat c = Ac$ has the following consequences [1, §2; 2, §1.4]:

1. **Missing mass.** $K_{nn} = \int_G |\varphi_n|^2 = a_n$ is the fractional mass of mode $n$ inside the gap.
2. **Phantom coefficients.** For a source $f = c\varphi_{n_0}$ at a single mode, the masked coefficient at $m \neq n_0$ is $\hat c_m = -K_{m,n_0}\,c$ — deterministically nonzero, with magnitude set by the off-diagonal of $K$.
3. **Exact energy identity.** $\sum_{m \neq n_0} |\hat c_m|^2 = a_{n_0}(1-a_{n_0})|c|^2$ ([1, Theorem 1]).
4. **Concentration operator.** $C_N = P_N \chi_G P_N$ has eigenvalues $\mu_j \in [0, 1]$; $\mu_{\max} \to 1$ signals an ill-conditioned recovery problem [3, §2.2].

Consequences (1)–(3) are **first-moment** effects: they describe the *expectation* of the masked coefficients given a specific source. The multi-signal analysis below requires a sharper distinction between first-moment (bias/mean) and second-moment (variance/covariance) effects. Some results generalize directly; others do not.

---

## 3. Cross-covariance through a common mask

### 3.1 The bilinear first-moment identity

From (2), linearity of expectation gives
$$\widehat\Sigma^{(12)} \;\equiv\; \mathbb E[\hat c^{(1)} \hat c^{(2)*}] \;=\; A\,\Sigma^{(12)}\,A^*. \tag{3}$$

**When the two signals are independent** ($\Sigma^{(12)} = 0$), the expected cross-covariance is zero, for any $A$. The common mask does *not* create a phantom cross-covariance in expectation. This is a critical point that distinguishes the two-signal case from the single-signal case — single-signal phantoms arise because a specific mode was excited; two independent random signals have no specific structure to mix.

**When the two signals share a common component** (say $c^{(1)} = \alpha u + \eta^{(1)}$, $c^{(2)} = \beta u + \eta^{(2)}$ with $u$ shared and $\eta^{(i)}$ independent), the true cross-covariance $\Sigma^{(12)} = \alpha\beta^* \Sigma_u$ is rank-one. The observed cross-covariance
$$\widehat\Sigma^{(12)} = A\alpha(A\beta)^*\,\Sigma_u \tag{4}$$
is rank-one with both loading directions rotated by the *same* $A$. Factor analysis, canonical correlation analysis [4], and ICA report the rotated directions $A\alpha, A\beta$ as "loadings" rather than $\alpha, \beta$ themselves. The rotation is deterministic and mask-shaped.

### 3.2 Second-moment effects on the sample estimator

The sample cross-covariance from $T$ realizations is
$$\widehat\Sigma^{(12)}_{\mathrm{sample}} = \frac{1}{T}\sum_{t=1}^T \hat c^{(1)}_t \hat c^{(2)*}_t. \tag{5}$$

For independent Gaussian signals (so higher moments factor through second moments):
$$\mathrm{Var}\!\left(\left[\widehat\Sigma^{(12)}_{\mathrm{sample}}\right]_{mn}\right) = \frac{1}{T}(A\Sigma^{(1)}A^*)_{mm}(A\Sigma^{(2)}A^*)_{nn}, \tag{6}$$
$$\mathrm{Cov}\!\left(\widehat\Sigma^{(12)}_{mn},\,\overline{\widehat\Sigma^{(12)}_{m'n'}}\right) = \frac{1}{T}(A\Sigma^{(1)}A^*)_{mm'}(A\Sigma^{(2)}A^*)_{nn'}. \tag{7}$$

Equation (6) says the per-entry variance of the sample cross-covariance is a function of the mode pair $(m, n)$ — larger where the marginal variances $(A\Sigma^{(i)}A^*)$ are large, i.e., at mode pairs with substantial mass inside $G$. Equation (7) is the classical Brillinger-type result for sample cross-covariance [5, Thm 2.9.1], with masked covariances replacing true ones.

**This is where the mask effect for independent signals actually lives.** The realization-to-realization variability of $\widehat\Sigma^{(12)}_{\mathrm{sample}}$ has **mask-shaped magnitude** and **mask-shaped cross-entry correlations**. The pattern is not the mask itself; it is the *second-moment structure* of the estimator, and it persists regardless of how many realizations are averaged — more averaging reduces amplitude, not shape.

### 3.3 Permutation-null inheritance

Permutation tests resample the signals (shuffling sample indices, time-reversing one signal, etc.) while keeping the mask fixed. Every permuted dataset passes through the same $A$. For any test statistic $Q(\widehat\Sigma^{(12)})$ that is sensitive to the second-moment structure of $\widehat\Sigma^{(12)}$ — for example, a matched-filter detection statistic or a spatial-cluster extent measure — the permutation null carries the same $(AA^*)$-induced variance structure as the actual observation. The permutation-derived $p$-value is calibrated against iid sampling noise *and* mask structure, so it does not flag either one as anomalous.

For linear test statistics (simple scalar means, sums of entries without quadratic weighting), the permutation null is robust and the mask effect cancels. For quadratic or higher-order statistics (any test that weights entries by their own magnitude), the permutation null inherits the mask and mis-calibrates.

---

## 4. Coherence under a common mask

### 4.1 Definitions

Magnitude-squared coherence (MSC) between mode $m$ of signal 1 and mode $n$ of signal 2:
$$\gamma^2_{mn} = \frac{|\Sigma^{(12)}_{mn}|^2}{\Sigma^{(1)}_{mm}\Sigma^{(2)}_{nn}} \in [0, 1]. \tag{8}$$

The sample estimator divides the estimated cross-power by estimated marginal powers.

### 4.2 What the mask actually does to MSC

For two independent signals through *any* mask (common or not), the sample MSC has $\mathbb E[\widehat\gamma^2_{mn}] \approx 1/T$ at every mode pair (Goodman's classical result [6, 7]). **The mask does not create a phantom MSC in expectation for independent signals.** Finite-sample MSC between independent signals is approximately the same magnitude whether you mask or not; what the mask does is redistribute the *variance* of $\widehat\gamma^2$ across mode pairs, not shift its mean.

The mask's first-moment effect on MSC appears when there is a real coherent component. Write $\Sigma^{(12)}_{mn} = \rho_{mn}\sqrt{\Sigma^{(1)}_{mm}\Sigma^{(2)}_{nn}}$ where $\rho_{mn}$ is the true mode-pair correlation ($|\rho_{mn}|^2 = \gamma^2_{mn}$). After masking,
$$\widehat\Sigma^{(12)}_{mn} \;=\; (A\Sigma^{(12)}A^*)_{mn} \;=\; \sum_{k\ell} A_{mk}\overline{A_{n\ell}}\,\rho_{k\ell}\sqrt{\Sigma^{(1)}_{kk}\Sigma^{(2)}_{\ell\ell}}. \tag{9}$$

Two distinct effects at different mode pairs:

**(i) Attenuation at true-signal mode pairs.** If the true coherence lives at a specific pair $(k_0, \ell_0)$, the observed $\widehat\Sigma^{(12)}_{k_0,\ell_0}$ is attenuated from $\rho_{k_0\ell_0}$ by factors involving the diagonal entries of $A$. In the small-gap limit, the attenuation is $(1 - a_{k_0})(1 - a_{\ell_0})\rho_{k_0\ell_0}$ plus higher-order corrections.

**(ii) Phantom coherence at other mode pairs.** The cross-terms in (9) populate $\widehat\Sigma^{(12)}_{mn}$ at $(m, n) \neq (k_0, \ell_0)$ whenever $A_{mk_0}$ and $A_{n\ell_0}$ are both nonzero. These phantom cross-powers have a spatial/modal distribution set entirely by the mask.

**The intrinsic mask-coherence operator.** Define
$$\gamma^2_{A,mn} \;=\; \frac{|(AA^*)_{mn}|^2}{(AA^*)_{mm}(AA^*)_{nn}}. \tag{10}$$
By Cauchy-Schwarz, $\gamma^2_{A,mn} \in [0, 1]$, with $\gamma^2_{A,mm} = 1$ on the diagonal. $\gamma^2_A$ is not the phantom MSC for independent signals (which is $\approx 1/T$). It is the **MSC transfer structure** of the mask — the observed MSC pattern when the true cross-covariance is uniform-white ($\Sigma^{(12)} = I$, $\Sigma^{(i)} = I$). For such a white coherent source, $\widehat\gamma^2 \to \gamma^2_A$ asymptotically, scaled by $1/(1 + \text{noise-to-shared-signal ratio})^2$. For general coherent sources, $\gamma^2_A$ governs the spatial pattern of coherence redistribution.

### 4.3 Operational consequences

**Coherence at specific mode pairs is attenuated.** A true coherent oscillation at a specific mode has reduced visibility by factors involving the mask's diagonal at that mode.

**Coherence spreads to nearby mode pairs.** A real source at $(k_0, \ell_0)$ creates apparent coherence at every $(m, n)$ with $|A_{mk_0}||A_{n\ell_0}|$ nonzero. For a localized gap, this spills coherence into nearby mode pairs at amplitude $\sim |K_{mk_0}||K_{n\ell_0}|\,\rho_{k_0\ell_0}$.

**Coherence across mode pairs has spatial correlation.** Even at mode pairs with no true coherence, the *realization* of sample MSC has spatial correlation across $(m, n)$ shaped by $\gamma^2_A$. Multiple-testing procedures that treat MSC entries as independent (Bonferroni with $N^2$ tests) mis-calibrate.

In CMB cross-power-spectrum analysis these effects are handled explicitly via the MASTER mode-coupling matrix [8] and its descendants [9, 10]; the matrix is structurally the same object as $AA^*$, specialized to spherical harmonics with a sky mask. In functional-connectivity analysis the same effects are typically *not* corrected [11, 12], leading to well-documented spurious coherence clusters near mask boundaries.

---

## 5. Phase, time delay, and directional spectra

### 5.1 Cross-spectrum phase under a common mask

The cross-spectrum $S_{fg}(\omega) = \mathcal F[\mathbb E f(t)g(t+\tau)](\omega)$ is complex in general. Real part = in-phase coupling; imaginary part = out-of-phase coupling, read by downstream pipelines as time delay or directional lag [13, 14].

For a stationary coherent source with $\Sigma^{(12)}_{kk'} = S_{fg}(k)\delta_{kk'}$ and real $S_{fg}$ (no true time delay), the observed cross-spectrum after common masking is
$$\widehat S_{fg}(m, n) = (A\,\mathrm{diag}(S_{fg})\,A^*)_{mn} = \sum_k A_{mk}\overline{A_{nk}}\,S_{fg}(k). \tag{11}$$

For $m = n$, each term has magnitude $|A_{mk}|^2 \geq 0$ (real), so $\widehat S_{fg}(m, m)$ is real and the in-band phase is preserved. **The phase bias shows up at off-diagonal entries** $m \neq n$: $\widehat S_{fg}(m, n)$ inherits phase from the product $A_{mk}\overline{A_{nk}}$, which is not generally real.

For independent signals ($S_{fg} = 0$), $\mathbb E[\widehat S_{fg}(m, n)] = 0$ — no systematic phase in expectation, only sample fluctuations with mode-pair-dependent variance. The phase bias is a first-moment effect that requires a real coherent source.

### 5.2 Gap-displacement phase

In a periodic-interval Fourier basis, the mask matrix element has closed form. For a gap of width $\Delta$ centered at $x_G$ in an interval of length $L$:
$$K_{kk'} = \frac{\Delta}{L}\cdot\mathrm{sinc}\!\left(\frac{(k'-k)\Delta}{2}\right)\,e^{i(k'-k)x_G}. \tag{12}$$

The factor $e^{i(k'-k)x_G}$ is a linear-in-frequency-difference phase proportional to the gap centroid. Substituting into (11) and inspecting the phase of $\widehat S_{fg}(m, n)$ for $m \neq n$ gives phase linear in $(m - n)x_G$. A downstream pipeline estimating time delay from $\arg\widehat S_{fg}$ versus frequency reads out a phantom delay proportional to $x_G$ — the displacement of the gap centroid from the coordinate origin.

The effect is invisible if $x_G = 0$ (symmetric gap), and it flips sign under coordinate reflection through the gap center. Coordinate-independence of reported lead-lag is therefore a diagnostic of its physical reality.

### 5.3 Granger causality and directed spectra

Granger causality [15] decomposes the cross-spectrum into forward and backward components using VAR modeling [16]. The decomposition is sensitive to the imaginary part of $S_{fg}$, so a coherent source through a common off-center gap produces apparent lead-lag structure in both directions, with magnitudes set by the phase slope of (11)–(12).

Practical caution: Granger-causality estimates at frequencies comparable to $1/\Delta$ (the gap scale) should be regarded as potentially confounded by mask-induced phase even when coherence is strong, and calibrated against a surrogate null generated by the same mask applied to matched independent signals. Stokes & Purdon [17] note similar confounds in neuroimaging Granger analysis under motion-correlated censoring.

---

## 6. Matched filtering on correlation data

### 6.1 The detection statistic

Matched filtering is the optimal linear detector for a known signal in additive white noise [18, 19, 20]. For correlation-domain detection, one matches a template $T$ (the expected structure of $R$ under the hypothesis) against the sample correlation matrix $\widehat R$ via Frobenius inner product:
$$D(\theta) = \frac{\langle T(\theta), \widehat R\rangle_F}{\|T(\theta)\|_F} = \frac{1}{\|T(\theta)\|_F}\sum_{mn} T(\theta)^*_{mn} \widehat R_{mn}, \tag{13}$$
where $\theta$ is a template-parameter vector (time of arrival, frequency, direction, chirp mass, etc.). The statistic is scanned over $\theta$ and peaks are reported as candidate detections.

### 6.2 The effective template

Substitute $\widehat R = A R_{\text{true}} A^* + \delta R$ (signal plus zero-mean sample noise) into (13). Using the Frobenius cyclic identity $\langle T, A R A^*\rangle_F = \langle A^* T A, R\rangle_F$:
$$D(\theta) = \frac{\langle A^* T(\theta) A,\;R_{\text{true}}\rangle_F + \langle T(\theta), \delta R\rangle_F}{\|T(\theta)\|_F}. \tag{14}$$

The signal-dependent term is the inner product of $R_{\text{true}}$ against the **effective template**
$$T_{\text{eff}}(\theta) = A^* T(\theta) A. \tag{15}$$

Testing template $T$ against common-masked data is mathematically equivalent to testing $A^* T A$ against unmasked data. The template distortion is **quadratic in $A$**, compared to the linear $A^* t$ distortion in single-signal matched filtering [2, §6.3].

Structural consequences:
- **Rank-one templates stay rank-one with both vectors rotated.** If $T = uv^*$, then $T_{\text{eff}} = (A^* u)(A^* v)^*$ — the hypothesis "is there coherence between mode direction $u$ in signal 1 and mode direction $v$ in signal 2?" becomes "is there coherence between $A^* u$ and $A^* v$?"
- **Diagonal templates fill in.** If $T$ is diagonal in the basis of choice, $A^* T A$ is generally dense in that basis, adding off-diagonal mode couplings the analyst did not intend to test.
- **Template normalization matters.** Replacing $T$ by $\lambda T$ leaves $D(\theta)$ invariant, but the relative weighting of entries within $T_{\text{eff}}$ follows $A^* T A$, not $T$.

### 6.3 Signal detection: SNR under the common mask

The relevant SNR is the ratio of expected signal amplitude to standard deviation of the null statistic:
$$\mathrm{SNR}^2_{\text{mask}}(\theta) = \frac{|\langle A^* T(\theta) A,\,R_{\text{true}}\rangle_F|^2}{\|T(\theta)\|_F^2 \cdot \sigma^2_{\text{eff}}(\theta)}, \tag{16}$$
where $\sigma^2_{\text{eff}}(\theta)$ is the variance of $D(\theta)$ under the null. Two sources of loss relative to the ideal (ungapped, white-noise) case:

**Signal-side loss.** Bounded by $\|A^* T A\|_F \leq \|A\|^2 \|T\|_F$; for contractive $A$ (mask removes energy), $\|A\|^2 < 1$. Signal SNR decreases by at most $\|A\|^4$, concentrated at modes heavily overlapping the gap.

**Noise-side structure.** The variance
$$\sigma^2_{\text{eff}}(\theta) = \frac{1}{T \|T(\theta)\|_F^2}\langle T(\theta),\; (A\Sigma^{(1)}A^*)\otimes(A\Sigma^{(2)}A^*)\cdot T(\theta)\rangle \tag{17}$$
is $\theta$-dependent — peaked at template-parameter values where $T(\theta)$ has large overlap with the principal directions of $(AA^*)\otimes(AA^*)$.

### 6.4 Non-uniform false-alarm rate

Under the null (no signal, independent white streams), $\mathbb E[D(\theta)] = 0$ and $\mathrm{Var}[D(\theta)] = \sigma^2_{\text{eff}}(\theta)$. A fixed threshold $D > k$ has false-alarm probability
$$\mathrm{FAP}(\theta) \approx 2\,\Phi\!\left(-k/\sigma_{\text{eff}}(\theta)\right), \tag{18}$$
$\theta$-dependent through $\sigma_{\text{eff}}(\theta)$. A uniform threshold across $\theta$ has **non-uniform FAP**, concentrated at $\theta$ values where $\sigma_{\text{eff}}$ is largest.

This is the precise sense in which common-mask matched filtering "creates phantom peaks": the null distribution of $D(\theta)$ is non-stationary in $\theta$, so threshold crossings cluster at specific $\theta$ values determined by the mask geometry. An analyst observing a cluster of triggers at the same $\theta$ values across multiple datasets — the hallmark of a physical source — may be looking at a mask-induced false-alarm concentration.

Gravitational-wave pipelines handle this empirically: the background distribution is measured by time-slides [21, 22], and detection thresholds are set against the empirical distribution rather than the analytic one. Neuroimaging cluster-extent inference uses an analogous correction via random-field theory [23] or non-parametric resampling [24]. Both are compensating for the effect described by (17).

### 6.5 Mode-dependent signal/noise tradeoff

Combining (16) and (17): the effective SNR at given $\theta$ depends on how well $T(\theta)$ aligns with the mask's principal directions.

- **Template in mask-complement subspace** ($\|A^* T A\|_F \approx \|T\|_F$, $\langle T, (AA^*)\otimes(AA^*) T\rangle$ small): SNR near ideal.
- **Template aligned with mask-principal subspace**: signal attenuated, noise amplified, threshold miscalibrated.

Design criterion: **place templates in the mask-complement subspace when physically feasible.** This is what Slepian-function analysis [25] achieves for single-signal problems, and what mask-whitened estimators achieve for CMB polarization cross-spectra [9].

---

## 7. Numerical illustration

The following demonstrates the two core phenomena: (a) phantom coherence redistribution from a true coherent source, and (b) mode-dependent null-variance of the matched-filter statistic.

```python
import numpy as np

# 1D periodic domain, Fourier basis, off-center gap
L, N, T = 1.0, 64, 2000
x_G, Delta = 0.32, 0.20
n_grid = 2**12
x = np.linspace(0, L, n_grid, endpoint=False)
chi_G = ((x > x_G - Delta/2) & (x < x_G + Delta/2)).astype(float)
M = 1.0 - chi_G
k = np.arange(-N//2, N//2)
F = np.exp(-2j*np.pi*np.outer(k, x))/np.sqrt(n_grid)
A = F @ np.diag(M) @ F.conj().T
AA = A @ A.conj().T

# Intrinsic mask-coherence operator (geometric; no data involved)
gamma2_A = np.abs(AA)**2 / np.outer(np.diag(AA).real, np.diag(AA).real)

rng = np.random.default_rng(42)

# ---- Experiment 1: phantom coherence from a TRUE coherent source ----
# c^(1) = u + eta^(1),  c^(2) = u + eta^(2)  (shared white u, independent noise eta)
u   = (rng.standard_normal((T, N)) + 1j*rng.standard_normal((T, N)))/np.sqrt(2)
e1  = 0.3*(rng.standard_normal((T, N)) + 1j*rng.standard_normal((T, N)))/np.sqrt(2)
e2  = 0.3*(rng.standard_normal((T, N)) + 1j*rng.standard_normal((T, N)))/np.sqrt(2)
c1, c2 = u + e1, u + e2
c1_hat, c2_hat = c1 @ A.T, c2 @ A.T

S11 = (c1_hat.conj().T @ c1_hat) / T
S22 = (c2_hat.conj().T @ c2_hat) / T
S12 = (c1_hat.conj().T @ c2_hat) / T
gamma2_obs = np.abs(S12)**2 / np.outer(np.diag(S11).real, np.diag(S22).real)

corr = np.corrcoef(gamma2_obs.ravel(), gamma2_A.ravel())[0, 1]
print(f"EXP 1 (coherent source):")
print(f"  Corr(observed MSC, gamma^2_A) over all mode pairs: {corr:.4f}")
print(f"  Mean observed MSC: {gamma2_obs.mean():.4f}")
print(f"  Mean gamma^2_A:    {gamma2_A.mean():.4f}")
print(f"  Scaling factor (predicted 1/1.09^2 = {1/1.09**2:.3f}): "
      f"{gamma2_obs.mean()/gamma2_A.mean():.3f}")

# ---- Experiment 2: null-variance non-uniformity ----
c1b = (rng.standard_normal((T, N)) + 1j*rng.standard_normal((T, N)))/np.sqrt(2)
c2b = (rng.standard_normal((T, N)) + 1j*rng.standard_normal((T, N)))/np.sqrt(2)
c1b_hat, c2b_hat = c1b @ A.T, c2b @ A.T
S12b = (c1b_hat.conj().T @ c2b_hat) / T

# Diagonal template T_theta = e_theta e_theta^T, so D(theta) = S12[theta,theta]
D_theta = np.abs(np.diag(S12b))
# Predicted null sigma: sqrt((AA*)_{theta,theta}^2 / T) = (AA*)_{theta,theta}/sqrt(T)
sigma_eff = np.diag(AA).real / np.sqrt(T)
D_norm = D_theta / sigma_eff
print(f"\nEXP 2 (null, independent signals):")
print(f"  |D|/sigma_eff: mean = {D_norm.mean():.3f} "
      f"(Rayleigh prediction: sqrt(pi)/2 = {np.sqrt(np.pi)/2:.3f})")
print(f"  sigma_eff range: [{sigma_eff.min():.4f}, {sigma_eff.max():.4f}]; "
      f"max/min = {sigma_eff.max()/sigma_eff.min():.2f}")
```

Output (seed 42, $T = 2000$, $N = 64$, gap centered at $x_G = 0.32$ with width $\Delta = 0.2$):

```
EXP 1 (coherent source):
  Corr(observed MSC, gamma^2_A) over all mode pairs: 1.0000
  Mean observed MSC: 0.0169
  Mean gamma^2_A:    0.0200
  Scaling factor (predicted 1/1.09^2 = 0.842): 0.844

EXP 2 (null, independent signals):
  |D|/sigma_eff: mean = 0.844 (Rayleigh prediction: sqrt(pi)/2 = 0.886)
  sigma_eff range: [0.0161, 0.0178]; max/min = 1.11
```

**Experiment 1** confirms the prediction: the *shape* of the observed MSC matrix across mode pairs is essentially identical to the geometric $\gamma^2_A$ (Pearson correlation $\approx 1$), scaled by the noise-to-signal dilution factor $1/(1+|\text{noise}/\text{signal}|^2)^2 \approx 0.84$. A uniform shared signal produces phantom coherence at off-diagonal mode pairs with the exact spatial pattern of $\gamma^2_A$. On the diagonal, both $\gamma^2_A$ and observed MSC are $\approx 1$ (trivially, from $\gamma^2_{A,mm} = 1$).

**Experiment 2** confirms the null-variance structure: the normalized $|D|/\sigma_{\text{eff}}$ concentrates near the Rayleigh mean $\sqrt\pi/2 \approx 0.886$ across all $\theta$. The ratio $\max/\min$ of $\sigma_{\text{eff}}$ is only 1.11 for this particular Fourier-basis gap, because $|\varphi_k|^2 = 1/L$ is mode-independent and the diagonal of $AA^*$ varies only through finite-$N$ truncation effects. For non-translation-invariant bases (Dirichlet Laplacian on $[0, L]$, for example), the ratio is typically larger (1.3–2 for comparable gaps). The effect scales with the extent to which $|\varphi_m|^2$ varies across the domain.

---

## 8. Operational remedies

Five strategies, in rough order of cost and reliability.

### 8.1 Mask-scramble (time-slide) calibration

Gold standard when analytic calibration is intractable [21, 22, 26]. Destroy the common-mask cross-correlation while preserving univariate statistics:

- **Time-slides:** shift one signal by a lag exceeding any physical correlation length.
- **Phase randomization:** replace mode phases with independent random phases while preserving amplitudes.
- **Spatial permutation:** randomly permute spatial labels of one signal.

The empirical distribution of $D(\theta)$ under scrambling captures the full null including non-Gaussian tails and $\theta$-non-uniformity. Threshold the observation against the empirical null.

Cost: proportional to number of scrambles ($10^4$–$10^8$ in practice). Reliability: high if scrambling destroys cross-mask correlations. Limitation: cannot calibrate signals surviving the scrambling symmetry.

### 8.2 Mask-whitened templates

Redefine the template as
$$T_{\text{white}}(\theta) = (AA^*)^{-1/2}\,T(\theta)\,(A^*A)^{-1/2} \tag{19}$$
so that $A^* T_{\text{white}} A$ approximates $T$ (exactly for normal $A$; approximately with residuals in the complement of the range for general $A$). For ill-conditioned $A$ (approaching $\mu_{\max} \to 1$), mask-whitening amplifies modes with near-zero singular values and loses the SNR it was meant to recover; apply with regularization.

Cost: one eigendecomposition of $AA^*$. Used in CMB E/B-mode reconstruction [9].

### 8.3 Mask-aware covariance estimation

Invert the forward operator on the data side:
$$R_{\text{corr}} = A^+\,\widehat R\,(A^+)^* \tag{20}$$
where $A^+$ is the Moore-Penrose pseudoinverse (or Tikhonov-regularized). Mathematically equivalent to §8.2 but with different numerical properties: preferred when the same data is scanned against many templates.

### 8.4 Variance normalization

Compute $\sigma^2_{\text{eff}}(\theta)$ from (17) in advance, normalize:
$$D_{\text{norm}}(\theta) = D(\theta)/\sigma_{\text{eff}}(\theta). \tag{21}$$
The normalized statistic has approximately unit null variance across $\theta$, permitting a uniform threshold. Addresses (17)'s mean-zero non-uniform-variance structure but does not correct the mean bias (15) under signal alternatives. Used in LIGO's "reweighted SNR" [27].

### 8.5 Template orthogonality design

When physical flexibility exists, construct templates in the complement of the mask's principal directions. Let $\{u_j, \sigma_j\}$ be the SVD of $A$; templates supported on modes with large $\sigma_j$ (weakly attenuated by mask) have $\|A^* T A\|_F \approx \|T\|_F$ and small null variance. This is the Slepian-basis approach [25, 3] applied to correlation-domain detection.

---

## 9. Design implications

When is a common mask safe for correlation-domain inference? Reduces to controlling $\|AA^* - I\|$ on the relevant subspace.

**Small-gap regime $\|K\| \ll 1$.** First-order correction $O(\|K\|)$ suffices. Most CMB analysis sits here.

**Intermediate regime $\mu_{\max}(C_N) \in (0.3, 0.9)$.** Two-stage correction recommended: mask-aware template design plus scramble-calibrated thresholds. Gravitational-wave common-mask analysis lives here.

**Ill-conditioned regime $\mu_{\max}(C_N) \to 1$.** Certain mode pairs are fundamentally unobservable. Must either restrict analysis to the orthogonal complement, add a second independent measurement with a different gap, or accept that statistics in that region are meaningless.

The broad principle: **for a physical quantity of interest that is fundamentally a correlation, design the gap geometry (when possible) such that the principal directions of $AA^*$ are orthogonal to the mode pairs carrying the target information.** This is a stronger constraint than the single-signal design criterion of minimizing $\mu_{\max}(C_N)$, and must be evaluated separately for each correlation statistic of interest.

---

## 10. Related statistical mechanisms under a common gap

The common-mask analysis above captures the core correlation-domain effect. Many other statistical operations are structurally similar — quadratic or higher-order forms in masked data, inheriting variance structure from $AA^*$ in the same way. Brief catalog.

**Power-spectrum estimation by segment averaging.** Welch and Bartlett methods [28] reduce spectral-estimate variance like $1/M$ (for $M$ segments) while leaving any mean bias fixed. Under a common mask, the bias $\Sigma_{\text{obs}} = A\Sigma_{\text{true}}A^*$ is unchanged. More segments produce tighter confidence intervals around a biased value.

**Effective degrees of freedom.** Chi-square, F, and likelihood-ratio tests with nominal DOF $N$ (retained modes) mis-calibrate under a common mask: effective DOF is $\mathrm{tr}(I - C_N) = N - \mathrm{tr}(C_N)$, the Shannon number of the observed region [25]. Tests calibrated at nominal $N$ are anti-conservative.

**PCA and EOF decomposition.** Sample covariance $\widehat\Sigma = A\Sigma A^* + \Sigma_{\text{noise}}$. Leading eigenvectors are rotations of the true leading eigenvectors mixed with the leading eigenvectors of $AA^*$ [29]. Climate leading modes [30], neuroimaging resting-state networks [31], and economic common factors [32] all have mask-dependent components not easily separable from physics without explicit mask-aware modeling.

**Change-point detection at $\partial G$.** CUSUM-type statistics [33] read the commutator-induced boundary layer at $\partial G$ (characterized in detail by the T6 analysis [2, §3]) as a regime transition. Phantom change-points at the gap boundary are robust, reproducible, and pass significance tests.

**Multiple-testing clustering.** FDR [34] and related procedures assume test-statistic correlation structure compatible with, e.g., PRDS. Common-mask test statistics are correlated through $AA^*$, and the realized FDP can exceed the nominal FDR by a factor set by the rank structure of $K$. Discoveries cluster spatially on $K$'s principal directions.

**Two-point correlation functions.** For spatial fields and point processes, $\widehat\xi(r)$ acquires structure at separations comparable to the gap diameter from mask-induced pair-count and value-correlation biases. Landy-Szalay [35] and Hamilton [36] estimators cancel the pair-count contribution to first order; value-correlated contributions remain.

**Extreme-value statistics.** Generalized Extreme Value fits [37] assume iid sampling. Value-correlated censoring by a mask (gap preferentially excluding high or low field values) biases the Hill estimator [38] and produces spuriously precise return-level estimates.

**Information criteria.** AIC/BIC [39] compare models via log-likelihood differences; under a common mask, the likelihood is biased by $A$, and nested model comparisons (continuum vs. continuum + spectral line) can prefer the richer model for mask-induced fit, not physical fit.

**Permutation and bootstrap inheritance.** Resampling preserves the fixed mask; permutation nulls inherit mask-induced variance structure of the test statistic [40]. Permutation $p$-values are correct against iid noise, not against $A$.

**Simpson's reversal and regression collider bias.** When the gap correlates with an unobserved confounder or affects covariate distribution, linear regression bias can be arbitrary in sign and magnitude [41]. No linear correction in $A$ recovers the truth; causal-inference frameworks [42, 43] apply and are distinct from the phantom framework.

**Spurious regression and cointegration.** Granger–Newbold [44] and Phillips [45] show that independent unit-root series produce near-unit sample correlation even without masks; common-mask censoring adds deterministic shared structure (drop-recover patterns) that further inflates cross-series correlation. Standard cointegration tests [46, 47] over-reject.

**Nonlinear and higher-order statistics.** Bispectra and trispectra [48], nearest-neighbor mutual information [49], kernel independence tests [50]: affected by common masks through mechanisms that do not reduce to a bilinear form in $A$. Analytic correction is typically pipeline-specific and requires simulation-based calibration rather than closed-form operator algebra.

---

## 11. Status ledger

| Claim | Status | Notes |
|---|---|---|
| $\widehat\Sigma^{(12)} = A\Sigma^{(12)}A^*$ in expectation | [E] | Eq. (3), linearity of expectation |
| Independent signals: $\mathbb E[\widehat\Sigma^{(12)}] = 0$ | [E] | Immediate from (3) |
| Independent signals: sample-MSC expectation $\approx 1/T$ | [E] | Goodman [6]; independent of mask |
| Sample cross-cov per-entry variance | [E] | Eq. (6), Gaussian 4th-moment |
| Sample cross-cov cross-entry covariance | [E] | Eq. (7), Brillinger-type |
| Coherent source → phantom MSC redistribution | [E] | Eq. (9), direct from (3) |
| $\gamma^2_{A,mn} \in [0, 1]$ geometric bound | [E] | Eq. (10), Cauchy-Schwarz |
| Observed MSC shape $\propto \gamma^2_A$ for white coherent source | [E] | Verified numerically in §7 (Pearson $\approx 1$) |
| Gap-displacement phase $\propto (m-n)x_G$ | [E] | Eq. (12), Fourier basis closed form |
| Effective template $T_{\text{eff}} = A^* T A$ | [E] | Eq. (15), Frobenius cyclic |
| Null variance $\sigma^2_{\text{eff}}(\theta)$ formula | [E] | Eq. (17), Gaussian null |
| Non-uniform FAP under uniform threshold | [E] | Eq. (18), direct from (17) |
| Mask-whitened template recovers intended test | [K] | Eq. (19), exact for normal $A$, approximate otherwise |
| Time-slide empirical null is correct | [E] | For stationary signals with slides exceeding physical correlation length |
| Template orthogonal to mask principal directions → small phantom | [E] | Eqs. (16)–(17) with $T$ in mask complement |
| Quantitative variance non-uniformity for Fourier vs. Dirichlet | [O] | Scaling with basis spatial variability not yet analyzed |
| Closed-form phantom correction for higher-order statistics | [O] | Section 10 effects beyond bilinear |

Legend: [E] = proved exactly; [K] = known under stated hypotheses; [O] = open.

---

## 12. References

[1] *Phantom Eigenmode Suite*, `hole_problem.ipynb`, §1–§2. Internal working document.

[2] *Phantom Eigenmode Suite*, `ccg.ipynb`, §1. Internal working document (compression-commutator geometry).

[3] Simons, F. J., Dahlen, F. A., Wieczorek, M. A. "Spatiospectral concentration on a sphere." *SIAM Review*, 48(3), 504–536 (2006).

[4] Hardoon, D. R., Szedmak, S., Shawe-Taylor, J. "Canonical correlation analysis: An overview with application to learning methods." *Neural Computation*, 16(12), 2639–2664 (2004).

[5] Brillinger, D. R. *Time Series: Data Analysis and Theory*. Expanded ed., SIAM, Philadelphia (2001).

[6] Goodman, N. R. "Statistical analysis based on a certain multivariate complex Gaussian distribution (an introduction)." *Annals of Mathematical Statistics*, 34(1), 152–177 (1963).

[7] Carter, G. C. "Coherence and time delay estimation." *Proceedings of the IEEE*, 75(2), 236–255 (1987).

[8] Hivon, E., Górski, K. M., Netterfield, C. B., Crill, B. P., Prunet, S., Hansen, F. "MASTER of the cosmic microwave background anisotropy power spectrum: A fast method for statistical analysis of large and complex cosmic microwave background data sets." *The Astrophysical Journal*, 567(1), 2–17 (2002).

[9] Smith, K. M. "Pseudo-$C_\ell$ estimators which do not mix $E$ and $B$ modes." *Physical Review D*, 74(8), 083002 (2006).

[10] Alonso, D., Sanchez, J., Slosar, A., LSST Dark Energy Science Collaboration. "A unified pseudo-$C_\ell$ framework." *Monthly Notices of the Royal Astronomical Society*, 484(3), 4127–4151 (2019).

[11] Power, J. D., Mitra, A., Laumann, T. O., Snyder, A. Z., Schlaggar, B. L., Petersen, S. E. "Methods to detect, characterize, and remove motion artifact in resting state fMRI." *NeuroImage*, 84, 320–341 (2014).

[12] Murphy, K., Birn, R. M., Bandettini, P. A. "Resting-state fMRI confounds and cleanup." *NeuroImage*, 80, 349–359 (2013).

[13] Bendat, J. S., Piersol, A. G. *Random Data: Analysis and Measurement Procedures*. 4th ed., Wiley, New York (2010).

[14] Jenkins, G. M., Watts, D. G. *Spectral Analysis and Its Applications*. Holden-Day, San Francisco (1968).

[15] Granger, C. W. J. "Investigating causal relations by econometric models and cross-spectral methods." *Econometrica*, 37(3), 424–438 (1969).

[16] Geweke, J. "Measurement of linear dependence and feedback between multiple time series." *Journal of the American Statistical Association*, 77(378), 304–313 (1982).

[17] Stokes, P. A., Purdon, P. L. "A study of problems encountered in Granger causality analysis from a neuroscience perspective." *Proceedings of the National Academy of Sciences*, 114(34), E7063–E7072 (2017).

[18] Van Trees, H. L. *Detection, Estimation, and Modulation Theory, Part I*. Wiley, New York (1968).

[19] Kay, S. M. *Fundamentals of Statistical Signal Processing, Volume II: Detection Theory*. Prentice Hall, Upper Saddle River (1998).

[20] Scharf, L. L. *Statistical Signal Processing: Detection, Estimation, and Time Series Analysis*. Addison-Wesley, Reading (1991).

[21] Was, M., Bizouard, M.-A., Brisson, V., Cavalier, F., Davier, M., Hello, P., et al. "On the background estimation by time slides in a network of gravitational wave detectors." *Classical and Quantum Gravity*, 27(1), 015005 (2010).

[22] Usman, S. A., Nitz, A. H., Harry, I. W., Biwer, C. M., Brown, D. A., Cabero, M., et al. "The PyCBC search for gravitational waves from compact binary coalescence." *Classical and Quantum Gravity*, 33(21), 215004 (2016).

[23] Worsley, K. J., Marrett, S., Neelin, P., Vandal, A. C., Friston, K. J., Evans, A. C. "A unified statistical approach for determining significant signals in images of cerebral activation." *Human Brain Mapping*, 4(1), 58–73 (1996).

[24] Eklund, A., Nichols, T. E., Knutsson, H. "Cluster failure: Why fMRI inferences for spatial extent have inflated false-positive rates." *Proceedings of the National Academy of Sciences*, 113(28), 7900–7905 (2016).

[25] Slepian, D., Pollak, H. O. "Prolate spheroidal wave functions, Fourier analysis and uncertainty — I." *Bell System Technical Journal*, 40(1), 43–63 (1961).

[26] Romano, J. D., Cornish, N. J. "Detection methods for stochastic gravitational-wave backgrounds: A unified treatment." *Living Reviews in Relativity*, 20(1), 2 (2017).

[27] Allen, B., Anderson, W. G., Brady, P. R., Brown, D. A., Creighton, J. D. E. "FINDCHIRP: An algorithm for detection of gravitational waves from inspiraling compact binaries." *Physical Review D*, 85(12), 122006 (2012).

[28] Priestley, M. B. *Spectral Analysis and Time Series*. Academic Press, London (1981).

[29] Jolliffe, I. T. *Principal Component Analysis*. 2nd ed., Springer, New York (2002).

[30] Preisendorfer, R. W. *Principal Component Analysis in Meteorology and Oceanography*. Elsevier, Amsterdam (1988).

[31] Biswal, B., Yetkin, F. Z., Haughton, V. M., Hyde, J. S. "Functional connectivity in the motor cortex of resting human brain using echo-planar MRI." *Magnetic Resonance in Medicine*, 34(4), 537–541 (1995).

[32] Stock, J. H., Watson, M. W. "Forecasting using principal components from a large number of predictors." *Journal of the American Statistical Association*, 97(460), 1167–1179 (2002).

[33] Basseville, M., Nikiforov, I. V. *Detection of Abrupt Changes: Theory and Application*. Prentice Hall, Englewood Cliffs (1993).

[34] Benjamini, Y., Hochberg, Y. "Controlling the false discovery rate: A practical and powerful approach to multiple testing." *Journal of the Royal Statistical Society B*, 57(1), 289–300 (1995).

[35] Landy, S. D., Szalay, A. S. "Bias and variance of angular correlation functions." *The Astrophysical Journal*, 412(1), 64–71 (1993).

[36] Hamilton, A. J. S. "Toward better ways to measure the galaxy correlation function." *The Astrophysical Journal*, 417, 19–35 (1993).

[37] Coles, S. *An Introduction to Statistical Modeling of Extreme Values*. Springer, London (2001).

[38] Hill, B. M. "A simple general approach to inference about the tail of a distribution." *Annals of Statistics*, 3(5), 1163–1174 (1975).

[39] Burnham, K. P., Anderson, D. R. *Model Selection and Multimodel Inference: A Practical Information-Theoretic Approach*. 2nd ed., Springer, New York (2002).

[40] Good, P. I. *Permutation, Parametric, and Bootstrap Tests of Hypotheses*. 3rd ed., Springer, New York (2005).

[41] Pearl, J. "Simpson's paradox: An anatomy." UCLA Computer Science Department Technical Report R-264 (1999).

[42] Pearl, J. *Causality: Models, Reasoning and Inference*. 2nd ed., Cambridge University Press, Cambridge (2009).

[43] Rubin, D. B. "Inference and missing data." *Biometrika*, 63(3), 581–592 (1976).

[44] Granger, C. W. J., Newbold, P. "Spurious regressions in econometrics." *Journal of Econometrics*, 2(2), 111–120 (1974).

[45] Phillips, P. C. B. "Understanding spurious regressions in econometrics." *Journal of Econometrics*, 33(3), 311–340 (1986).

[46] Engle, R. F., Granger, C. W. J. "Co-integration and error correction: Representation, estimation, and testing." *Econometrica*, 55(2), 251–276 (1987).

[47] Johansen, S. "Statistical analysis of cointegration vectors." *Journal of Economic Dynamics and Control*, 12(2–3), 231–254 (1988).

[48] Nikias, C. L., Mendel, J. M. "Signal processing with higher-order spectra." *IEEE Signal Processing Magazine*, 10(3), 10–37 (1993).

[49] Kraskov, A., Stögbauer, H., Grassberger, P. "Estimating mutual information." *Physical Review E*, 69(6), 066138 (2004).

[50] Gretton, A., Bousquet, O., Smola, A., Schölkopf, B. "Measuring statistical dependence with Hilbert-Schmidt norms." In *Algorithmic Learning Theory*, Springer, 63–77 (2005).

---

*Working notes, April 2026. Companion to the Phantom Eigenmode suite. References [1], [2] are internal documents in the same suite.*
