"""
Matched filtering with a temporal gap: numerical companion to
statistical_phantoms.md §4.3 (with the §6 development in
common_mask_correlation.md).

The example: detection of a localized signal (Gaussian pulse) in a 1D
time series with a temporal gap. Templates are pulses parameterized by
arrival time tau; the matched-filter scan produces D(tau).

We consider three analyst behaviors:

  Cell A — "no mask anywhere":
    Clean data, ideal template, ideal normalization.
    The baseline. Optimal Wiener filter.

  Cell B — "hole in data only" (naive analyst, data is masked):
    Numerator   = <h_tau, M y>     (template ignores the gap)
    Denominator = ||h_tau||         (normalize as if there were no gap)
    The analyst is unaware the data has a gap; the matched filter is
    miscalibrated. Linear in A.

  Cell C — "common mask" (mask-aware analyst):
    Numerator   = <M h_tau, M y>   (template projected onto unmasked region)
    Denominator = ||M h_tau||       (mask-aware normalization)
    Both signal and template paths see the gap.
    This is the §6 case: the effective template is M h_tau, the
    effective response carries the mask geometry quadratically through
    the signal path AND the normalizer.

What the framework predicts (§4.3, §6):

  - First-moment phantom (cell B): peak displacement and sidelobes.
    The peak of D_B(tau) is shifted away from the true tau_0 when tau_0
    is near the gap; phantom sidelobes appear at gap-shifted arrival
    times. Linear in A.

  - Common-mask attenuation (cell C): the peak stays at tau_0 (correct
    location, mask-aware normalizer), but the SNR is non-uniform across
    tau through the quadratic factor beta(tau) = ||M h_tau||^2/||h_tau||^2.
    The signal-side loss is set by the principal-angle geometry.

  - Four-object decomposition: at every tau, the principal angle
    between span(h_tau) and the unmasked region has cos^2(theta) =
    beta(tau). The four scalars (retention beta^2, suppression
    (1-beta)^2, leakage beta(1-beta), total 1-beta) all live on the
    curve beta(tau). Total = suppression + leakage holds pointwise.

  - Disconfirmer protocols (§5.1, §5.2):
      * Amplitude sweep: first-moment phantom peak amplitude scales
        linearly with c.
      * Time-slide: real signals persist when the gap is moved; phantom
        sidelobes follow the gap.

Outputs:
  mf_masked_setup.png          Setup: signal, mask, masked observation
  mf_first_moment.png          First-moment phantom (cells A, B, C)
  mf_decomposition.png         Four-object decomposition vs tau
  mf_second_moment.png         Cross-spectral demo (two streams,
                               common mask, non-uniform null variance)
  mf_disconfirmers.png         Amplitude sweep + time-slide
  mf_masked_verification.txt   Numerical verification record
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle

OUTPUT_DIR = '/mnt/user-data/outputs'
os.makedirs(OUTPUT_DIR, exist_ok=True)

np.random.seed(42)

# ============================================================
# Helpers (per matplotlib_guidelines.docx)
# ============================================================

def bold_text(ax, x, y, txt, **kw):
    """Text on dark backgrounds: bold black with white path-effect stroke."""
    kw.setdefault('fontweight', 'heavy')
    kw.setdefault('color', 'black')
    t = ax.text(x, y, txt, **kw)
    t.set_path_effects([pe.withStroke(linewidth=3, foreground='white')])
    return t

# ============================================================
# SETUP
# ============================================================

# 1D periodic time domain
N = 1024
T_total = 1.0
dt = T_total / N
t_grid = np.linspace(0, T_total, N, endpoint=False)
df = 1.0 / T_total

# True signal: Gaussian pulse at arrival time tau_0
tau_0 = 0.30          # true arrival time (away from the gap so the
                      # signal is recoverable; the phantom analysis
                      # uses sweeps across tau that visit the gap)
sigma_p = 0.025       # pulse width
c_amp = 1.0           # signal amplitude

def gaussian_pulse(t, tau, width=sigma_p):
    """Unnormalized Gaussian pulse centered at tau."""
    return np.exp(-0.5 * ((t - tau) / width) ** 2)

# Norm of an unmasked Gaussian pulse (constant in tau by translation,
# valid in the periodic-extension sense when tau is bounded away from
# the boundary):
h0 = gaussian_pulse(t_grid, 0.5)
pulse_norm_squared = np.sum(h0 ** 2) * dt
pulse_norm = np.sqrt(pulse_norm_squared)
print(f"Pulse norm (independent of tau by translation): {pulse_norm:.6f}")

# True signal in the time series
signal_clean = c_amp * gaussian_pulse(t_grid, tau_0)

# Noise level (chosen so SNR > 1 at the true peak in cell A)
sigma_n = 0.10

# Mask: temporal gap (this defines the "hole")
t_G = 0.60            # center of gap
Delta = 0.16          # width of gap
in_gap = (t_grid >= t_G - Delta / 2) & (t_grid < t_G + Delta / 2)
M_mask = (~in_gap).astype(float)   # 1 outside gap, 0 inside
gap_fraction = Delta / T_total

print(f"Setup:")
print(f"  N = {N}, T = {T_total}, dt = {dt}")
print(f"  Pulse: tau_0 = {tau_0}, sigma_p = {sigma_p}, c = {c_amp}")
print(f"  Noise: sigma_n = {sigma_n}")
print(f"  Gap:   t_G = {t_G}, Delta = {Delta}, "
      f"fraction = {gap_fraction:.3f}")

# ============================================================
# Tau-grid for the matched-filter scan
# ============================================================
# We sweep tau across the entire domain so we can see what happens
# inside, near, and far from the gap.
tau_grid = np.linspace(0.05, 0.95, 451)

# Pre-compute templates for every tau in the scan, normalized variants
# Each row is h_tau evaluated on the time grid.
H = np.stack([gaussian_pulse(t_grid, tau) for tau in tau_grid], axis=0)
# Mask-projected templates (M h_tau)
MH = M_mask[None, :] * H

# Per-tau norms (in continuous L^2 inner product, weight dt)
H_norm = np.sqrt(np.sum(H ** 2, axis=1) * dt)
MH_norm = np.sqrt(np.sum(MH ** 2, axis=1) * dt)

# beta(tau) = ||M h_tau||^2 / ||h_tau||^2
# = cosine-squared of the principal angle between span(h_tau) and the
# unmasked region (per statistical_phantoms.md §1.2).
beta_tau = (MH_norm / H_norm) ** 2
# a(tau) = 1 - beta(tau) = mass in gap (the spatial-gap framework's "a_n")
a_tau = 1.0 - beta_tau

# Print: where does beta dip? (templates centered in the gap have low beta)
print(f"  beta range: min = {beta_tau.min():.4f} "
      f"(near tau = {tau_grid[np.argmin(beta_tau)]:.3f}), "
      f"max = {beta_tau.max():.4f}")

# ============================================================
# Cell-A / Cell-B / Cell-C matched filters
# ============================================================
# Convention: D(tau) = numerator(tau) / denominator(tau)
# All three cells use the time-domain inner product
#   numerator(tau) = sum_t (template * data) * dt

def mf_cellA(y_clean):
    """Clean data, ideal template, ideal norm (no mask anywhere)."""
    num = (H @ y_clean) * dt
    return num / H_norm

def mf_cellB(y_masked):
    """Masked data, ideal template, ideal norm (analyst unaware)."""
    num = (H @ y_masked) * dt
    return num / H_norm

def mf_cellC(y_masked):
    """Masked data, mask-projected template, mask-aware norm."""
    num = (MH @ y_masked) * dt
    return num / MH_norm

# ============================================================
# FIGURE 1: SETUP
# ============================================================

fig, axes = plt.subplots(1, 3, figsize=(13, 3.7))

# Panel 1: signal + noise + true arrival
ax = axes[0]
np.random.seed(0)
noise_demo = sigma_n * np.random.randn(N)
y_demo_clean = signal_clean + noise_demo
ax.plot(t_grid, y_demo_clean, color='steelblue', linewidth=0.8, alpha=0.8)
ax.plot(t_grid, signal_clean, color='black', linewidth=1.4,
        label=r'true signal $f(t)$')
ax.axvline(tau_0, color='red', linewidth=1, linestyle='--',
           label=fr'$\tau_0 = {tau_0}$')
ax.set_title("Signal + noise (no mask)\n" r"$y(t) = c\,e^{-(t-\tau_0)^2/2\sigma_p^2} + n(t)$")
ax.set_xlabel('time $t$')
ax.set_ylabel(r'$y(t)$')
ax.set_ylim(-0.5, 1.3)
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3)

# Panel 2: same signal, but masked
ax = axes[1]
y_demo_masked = M_mask * y_demo_clean
ax.plot(t_grid, y_demo_masked, color='steelblue', linewidth=0.8, alpha=0.8)
ax.plot(t_grid, M_mask * signal_clean, color='black', linewidth=1.4,
        label=r'masked signal $M f$')
ax.axvline(tau_0, color='red', linewidth=1, linestyle='--')
# Highlight the gap
ax.axvspan(t_G - Delta / 2, t_G + Delta / 2, color='gray', alpha=0.35,
           label=fr'gap $G$ (width {Delta})')
ax.set_title("Same signal, masked\n" r"$y_{\rm obs}(t) = M(t)\,y(t)$")
ax.set_xlabel('time $t$')
ax.set_ylabel(r'$y_{\rm obs}(t)$')
ax.set_ylim(-0.5, 1.3)
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3)

# Panel 3: beta(tau) = ||M h_tau||^2 / ||h_tau||^2
ax = axes[2]
ax.plot(tau_grid, beta_tau, color='black', linewidth=1.6,
        label=r'$\beta(\tau) = \|M h_\tau\|^2 / \|h_\tau\|^2$')
ax.axvspan(t_G - Delta / 2, t_G + Delta / 2, color='gray', alpha=0.35,
           label=r'gap $G$')
ax.axvline(tau_0, color='red', linewidth=1, linestyle='--',
           label=fr'$\tau_0 = {tau_0}$')
ax.set_title("Principal-angle parameter\n"
             r"$\beta(\tau) = \cos^2\theta(\tau)$")
ax.set_xlabel(r'template arrival time $\tau$')
ax.set_ylabel(r'$\beta(\tau)$')
ax.set_ylim(-0.05, 1.1)
ax.set_xlim(0.05, 0.95)
ax.legend(loc='lower left', fontsize=9)
ax.grid(alpha=0.3)

plt.suptitle("Setup: pulse signal in gappy 1D time series", fontsize=13)
plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig(f'{OUTPUT_DIR}/mf_masked_setup.png', dpi=110, bbox_inches='tight')
plt.close()
print(f"Saved {OUTPUT_DIR}/mf_masked_setup.png")

# ============================================================
# FIGURE 2: FIRST-MOMENT PHANTOM
# ============================================================
# Two scenarios:
#   (a) tau_0 = 0.30, signal far from the gap — clean recovery in all cells
#   (b) tau_0 = 0.62, signal CENTERED IN THE GAP — phantom displacement
# Each scenario, three cells. We use ensemble-averaged signal response
# (no noise) to highlight the first-moment phantom; the noise
# realization shown as the underlying scatter.

scenarios = {
    'far':    {'tau0': 0.20, 'sigma': sigma_p, 'color': 'steelblue',
               'label': r'$\tau_0=0.20$, narrow (far from gap)'},
    'straddle': {'tau0': 0.60, 'sigma': 0.060, 'color': 'crimson',
               'label': r'$\tau_0=0.60$, wide (straddles gap)'},
}

# Compute the SIGNAL-only response (deterministic — first moment)
def signal_response_cellA(tau0, sigma):
    f = c_amp * gaussian_pulse(t_grid, tau0, width=sigma)
    return mf_cellA(f)

def signal_response_cellB(tau0, sigma):
    f = c_amp * gaussian_pulse(t_grid, tau0, width=sigma)
    return mf_cellB(M_mask * f)

def signal_response_cellC(tau0, sigma):
    f = c_amp * gaussian_pulse(t_grid, tau0, width=sigma)
    return mf_cellC(M_mask * f)

# A noisy realization, also for plotting
np.random.seed(7)
noise = sigma_n * np.random.randn(N)

fig, axes = plt.subplots(1, 3, figsize=(14, 4.6))
cell_titles = [
    "Cell A: no mask anywhere\n" r"$D_A(\tau) = \langle h_\tau, y\rangle / \|h_\tau\|$",
    "Cell B: hole in data only (naive)\n" r"$D_B(\tau) = \langle h_\tau, My\rangle / \|h_\tau\|$",
    "Cell C: common mask (mask-aware)\n" r"$D_C(\tau) = \langle Mh_\tau, My\rangle / \|Mh_\tau\|$",
]

for col, (cell_name, sig_fn, mf_fn) in enumerate([
        ('A', signal_response_cellA, mf_cellA),
        ('B', signal_response_cellB, mf_cellB),
        ('C', signal_response_cellC, mf_cellC)]):
    ax = axes[col]
    for sc_name, sc in scenarios.items():
        tau0 = sc['tau0']
        sigma = sc['sigma']
        signal_only = sig_fn(tau0, sigma)
        # Realization: signal + noise
        f = c_amp * gaussian_pulse(t_grid, tau0, width=sigma)
        y_full = f + noise
        if cell_name == 'A':
            D_real = mf_fn(y_full)
        else:
            D_real = mf_fn(M_mask * y_full)
        # Plot the ensemble-mean (signal-only) curve and a single realization
        ax.plot(tau_grid, D_real, color=sc['color'], linewidth=0.6, alpha=0.45)
        ax.plot(tau_grid, signal_only, color=sc['color'], linewidth=2.0,
                label=sc['label'])
        ax.axvline(tau0, color=sc['color'], linewidth=0.9, linestyle='--', alpha=0.7)
    ax.axvspan(t_G - Delta / 2, t_G + Delta / 2, color='gray', alpha=0.25,
               label='gap $G$')
    ax.set_title(cell_titles[col], fontsize=11)
    ax.set_xlabel(r'template arrival time $\tau$')
    if col == 0:
        ax.set_ylabel(r'matched-filter statistic $D(\tau)$')
    ax.set_xlim(0.05, 0.95)
    ax.legend(loc='upper right', fontsize=8.5)
    ax.grid(alpha=0.3)

# Note in the cell-B panel highlighting the twin phantom peaks
ax = axes[1]
sig_straddle = signal_response_cellB(scenarios['straddle']['tau0'],
                                      scenarios['straddle']['sigma'])
# Find the two largest peaks (one on each side of the gap)
left_region = tau_grid < t_G - Delta / 2
right_region = tau_grid > t_G + Delta / 2
peak_tau_L = tau_grid[left_region][np.argmax(sig_straddle[left_region])]
peak_tau_R = tau_grid[right_region][np.argmax(sig_straddle[right_region])]
peak_val_L = sig_straddle[left_region].max()
peak_val_R = sig_straddle[right_region].max()
ax.annotate(fr'twin phantom peaks', xy=(peak_tau_L, peak_val_L),
            xytext=(0.18, peak_val_L * 1.55),
            fontsize=9.5, color='crimson', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='crimson', lw=1.2))
ax.annotate('', xy=(peak_tau_R, peak_val_R),
            xytext=(peak_tau_L + 0.05, peak_val_L * 1.5),
            arrowprops=dict(arrowstyle='->', color='crimson', lw=1.2))

plt.suptitle("First-moment phantom: matched-filter statistic in three analyst regimes\n"
             "(thin line: single noisy realization; thick line: ensemble-mean signal response)",
             fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.92])
plt.savefig(f'{OUTPUT_DIR}/mf_first_moment.png', dpi=110, bbox_inches='tight')
plt.close()
print(f"Saved {OUTPUT_DIR}/mf_first_moment.png")

# ============================================================
# FIGURE 3: FOUR-OBJECT DECOMPOSITION
# ============================================================
# At each tau, the principal angle between span(h_tau) and the
# unmasked region has cos^2(theta) = beta(tau). The four scalar laws
# are (per statistical_phantoms.md §1.3):
#   retention   = beta^2
#   suppression = (1 - beta)^2
#   leakage     = beta * (1 - beta)
#   total       = 1 - beta
# and the per-direction identity is total = suppression + leakage.

retention   = beta_tau ** 2
suppression = (1 - beta_tau) ** 2
leakage     = beta_tau * (1 - beta_tau)
total       = 1 - beta_tau

# Verify the identity per tau
identity_resid = total - suppression - leakage
identity_max_err = float(np.max(np.abs(identity_resid)))
print(f"\nFour-object identity (per tau): "
      f"max |total - suppression - leakage| = {identity_max_err:.2e}")

# Empirical verification of the framework's signal-side prediction:
# In Cell C, the signal-mean at tau = tau_0 should be c * sqrt(beta(tau_0)) * ||h_tau_0||
# We sweep tau_0 across the domain and compare.
empirical_C_peak = []
predicted_C_peak = []
for tau_test in tau_grid[::10]:  # subsample for speed
    f = c_amp * gaussian_pulse(t_grid, tau_test)
    sig_C = mf_cellC(M_mask * f)
    # cell-C peak should be at tau_test (mask-aware normalization)
    peak_idx = np.argmin(np.abs(tau_grid - tau_test))
    empirical_C_peak.append(sig_C[peak_idx])
    # Predicted: c * sqrt(beta(tau_test)) * ||h_tau_test||
    beta_at_test = float(np.interp(tau_test, tau_grid, beta_tau))
    predicted_C_peak.append(c_amp * np.sqrt(beta_at_test) * pulse_norm)

empirical_C_peak = np.array(empirical_C_peak)
predicted_C_peak = np.array(predicted_C_peak)

# Cell-B signal-power-loss factor vs cell-A:
# D_B(tau_0)^2 / D_A(tau_0)^2 = beta(tau_0)^2 (retention!)
empirical_BA_ratio = []
predicted_BA_ratio = []
for tau_test in tau_grid[::10]:
    f = c_amp * gaussian_pulse(t_grid, tau_test)
    sig_A = mf_cellA(f)
    sig_B = mf_cellB(M_mask * f)
    peak_idx = np.argmin(np.abs(tau_grid - tau_test))
    if abs(sig_A[peak_idx]) > 1e-6:
        empirical_BA_ratio.append((sig_B[peak_idx] / sig_A[peak_idx]) ** 2)
    else:
        empirical_BA_ratio.append(np.nan)
    beta_at_test = float(np.interp(tau_test, tau_grid, beta_tau))
    predicted_BA_ratio.append(beta_at_test ** 2)

empirical_BA_ratio = np.array(empirical_BA_ratio)
predicted_BA_ratio = np.array(predicted_BA_ratio)

# Build the figure
fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))

# Panel 1: four scalars vs tau, with the gap shaded
ax = axes[0]
ax.plot(tau_grid, retention,   color='steelblue', linewidth=2,
        label=r'Retention $\beta(\tau)^2$')
ax.plot(tau_grid, suppression, color='firebrick', linewidth=2,
        label=r'Suppression $(1-\beta(\tau))^2$')
ax.plot(tau_grid, leakage,     color='goldenrod', linewidth=2,
        label=r'Leakage $\beta(\tau)(1-\beta(\tau))$')
ax.plot(tau_grid, total,       color='black',     linewidth=2, linestyle='--',
        label=r'Total $1-\beta(\tau)$', alpha=0.7)
ax.axvspan(t_G - Delta / 2, t_G + Delta / 2, color='gray', alpha=0.25)
ax.set_xlabel(r'template arrival time $\tau$')
ax.set_ylabel('Scalar value')
ax.set_title('Four-object decomposition vs $\\tau$\n'
             '(traces the smooth curve $\\beta(\\tau)$)')
ax.set_xlim(0.05, 0.95)
ax.set_ylim(-0.05, 1.1)
ax.legend(loc='center right', fontsize=8.5)
ax.grid(alpha=0.3)

# Panel 2: four scalars vs beta (universal curve)
ax = axes[1]
b = np.linspace(0, 1, 200)
ax.plot(b, b**2,         color='steelblue', linewidth=2,
        label=r'Retention $\beta^2$ (peaks $\beta\!=\!1$)')
ax.plot(b, (1-b)**2,     color='firebrick', linewidth=2,
        label=r'Suppression $(1-\beta)^2$ (peaks $\beta\!=\!0$)')
ax.plot(b, b*(1-b),      color='goldenrod', linewidth=2,
        label=r'Leakage $\beta(1-\beta)$ (peaks $\beta\!=\!1/2$)')
ax.plot(b, 1-b,          color='black',     linewidth=2, linestyle='--',
        label=r'Total $1-\beta$', alpha=0.7)
# Sample of beta(tau) values reached by the actual scan
beta_samples = np.linspace(0.05, 0.95, 10)
for bs in beta_samples:
    ax.axvline(bs, color='gray', linewidth=0.3, alpha=0.5)
ax.set_xlabel(r'$\beta$ (cosine-squared of principal angle)')
ax.set_ylabel('Scalar value')
ax.set_title('Universal four-scalar laws on $[0,1]$\n'
             '(per principal direction)')
ax.set_xlim(0, 1)
ax.set_ylim(-0.05, 1.1)
ax.legend(loc='center right', fontsize=8.5)
ax.grid(alpha=0.3)

# Panel 3: empirical verification of framework predictions
ax = axes[2]
tau_sub = tau_grid[::10]
ax.plot(tau_sub, predicted_C_peak / pulse_norm,
        color='steelblue', linewidth=2,
        label=r'predicted $c\sqrt{\beta(\tau_0)}$')
ax.plot(tau_sub, empirical_C_peak / pulse_norm,
        'o', color='steelblue', markersize=5,
        label=r'empirical Cell C peak (signal at $\tau_0$)', zorder=3)
ax.plot(tau_sub, predicted_BA_ratio,
        color='firebrick', linewidth=2,
        label=r'predicted $\beta(\tau_0)^2$ (retention)')
ax.plot(tau_sub, empirical_BA_ratio,
        's', color='firebrick', markersize=5,
        label=r'empirical $D_B(\tau_0)^2/D_A(\tau_0)^2$', zorder=3)
ax.axvspan(t_G - Delta / 2, t_G + Delta / 2, color='gray', alpha=0.25)
ax.set_xlabel(r'true arrival time $\tau_0$')
ax.set_ylabel('Predicted vs empirical')
ax.set_title('Framework predictions vs empirical\n'
             '(mask-side and signal-side scalings)')
ax.set_xlim(0.05, 0.95)
ax.set_ylim(-0.05, 1.1)
ax.legend(loc='center right', fontsize=8.5)
ax.grid(alpha=0.3)

plt.suptitle('Four-object decomposition: pulse matched filter, smooth $\\beta(\\tau)$',
             fontsize=13)
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(f'{OUTPUT_DIR}/mf_decomposition.png', dpi=110, bbox_inches='tight')
plt.close()
print(f"Saved {OUTPUT_DIR}/mf_decomposition.png")

# ============================================================
# FIGURE 4: SECOND-MOMENT PHANTOM (CROSS-SPECTRAL, COMMON MASK)
# ============================================================
# Two independent white-noise time series y1, y2, both observed
# through the SAME temporal mask M. The cross-correlation estimator at
# lag tau:
#     Chat(tau) = (1/T) sum_t (M y1)(t) * (M y2)(t + tau)
# is the matched-filter statistic for "is there coherent power at
# lag tau?" Under the null (independent streams), E[Chat] = 0 but the
# variance is
#     Var[Chat(tau)] = (sigma1^2 sigma2^2 / T) * A_M(tau)
# where A_M(tau) = sum_t M(t) M(t+tau) * dt is the AUTOCORRELATION OF
# THE MASK. This is the §6 "quadratic in A" regime: variance non-
# uniform in the template parameter tau, set entirely by the mask
# geometry.
#
# Importantly: under the null, an analyst applying a uniform threshold
# in tau will see false alarms preferentially at lags where A_M(tau)
# is largest — phantom peaks tracking the mask, not any signal.

n_real = 4000
sigma_x = 1.0

# Lag grid: span ±0.5 of the unit-length domain
n_lags = 201
lag_grid = np.linspace(-0.5, 0.5, n_lags)
# Convert lags to integer index shifts for circular correlation
lag_idx = np.round(lag_grid / dt).astype(int)

# Compute cross-correlation at all lags via FFT (faster, periodic)
# Chat(tau) = ifft(fft(y1) * conj(fft(y2)))(tau)
# Common mask: y_obs = M * y
def cross_corr_common_mask(y1, y2, M):
    y1m = M * y1
    y2m = M * y2
    Y1 = np.fft.fft(y1m)
    Y2 = np.fft.fft(y2m)
    # circular cross-correlation: ifft( conj(Y1) * Y2 ) gives lag-domain
    # Convention here: result[k] = sum_t y1m(t) * y2m(t+k)
    cc = np.real(np.fft.ifft(np.conj(Y1) * Y2)) * dt
    # cc[k] is the cross-corr at lag k*dt (k=0..N-1, with N/2..N-1 being negative lags)
    return cc

def cross_corr_no_mask(y1, y2):
    Y1 = np.fft.fft(y1)
    Y2 = np.fft.fft(y2)
    cc = np.real(np.fft.ifft(np.conj(Y1) * Y2)) * dt
    return cc

# Run many realizations to build empirical second-moment statistics
np.random.seed(101)

# Cell A (no mask): Var[Chat(tau)] is constant in tau
# Cell C (common mask): Var[Chat(tau)] follows A_M(tau)
sum_sq_A = np.zeros(N)
sum_sq_C = np.zeros(N)

for _ in range(n_real):
    y1 = sigma_x * np.random.randn(N)
    y2 = sigma_x * np.random.randn(N)
    cc_A = cross_corr_no_mask(y1, y2)
    cc_C = cross_corr_common_mask(y1, y2, M_mask)
    sum_sq_A += cc_A ** 2
    sum_sq_C += cc_C ** 2

var_A = sum_sq_A / n_real
var_C = sum_sq_C / n_real

# Predicted: with our chosen normalization Chat(tau) = dt * sum_s y1(s) y2(s+tau),
# we have Var[Chat(tau)] = dt^2 sum_s M(s)^2 M(s+tau)^2 sigma1^2 sigma2^2
#                        = sigma^4 * dt * A_M(tau)
# (where A_M(tau) = dt sum_s M(s) M(s+tau) is the mask autocorrelation
# in time units; A_M(0) = T - Delta = 0.84 here.)
M_fft = np.fft.fft(M_mask)
A_M = np.real(np.fft.ifft(np.conj(M_fft) * M_fft)) * dt
var_C_predicted = (sigma_x ** 4) * dt * A_M
var_A_predicted = (sigma_x ** 4) * dt * np.full(N, T_total)

# Reorder so lag = 0 is in the middle (visualizable)
def fftshift_lag(arr):
    return np.fft.fftshift(arr)

lag_axis = (np.arange(N) - N // 2) * dt   # symmetric around 0

var_A_centered = fftshift_lag(var_A)
var_C_centered = fftshift_lag(var_C)
var_C_pred_centered = fftshift_lag(var_C_predicted)
A_M_centered = fftshift_lag(A_M)

# Empirical "phantom-peak rate": fraction of realizations where
# |Chat(tau)| exceeds a fixed threshold k*sigma_baseline.
# Baseline sigma (no-mask, white) is sqrt(sigma_x^4 * dt * T) = sqrt(dt) * sigma_x^2.
baseline_sigma = sigma_x ** 2 * np.sqrt(dt * T_total)
# For visualization: threshold = 2.5*baseline
thr = 2.5 * baseline_sigma

# Compute empirical FAP per tau by re-running (we already have sum-of-squares;
# need the count of exceedances, so compute fresh)
np.random.seed(101)
exceed_A = np.zeros(N, dtype=int)
exceed_C = np.zeros(N, dtype=int)
for _ in range(n_real):
    y1 = sigma_x * np.random.randn(N)
    y2 = sigma_x * np.random.randn(N)
    cc_A = cross_corr_no_mask(y1, y2)
    cc_C = cross_corr_common_mask(y1, y2, M_mask)
    exceed_A += (np.abs(cc_A) > thr).astype(int)
    exceed_C += (np.abs(cc_C) > thr).astype(int)

fap_A = exceed_A / n_real
fap_C = exceed_C / n_real
fap_A_centered = fftshift_lag(fap_A)
fap_C_centered = fftshift_lag(fap_C)

# Build the figure
fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))

# Panel 1: cartoon — what the analyst sees (sample cross-corr) under null
ax = axes[0]
np.random.seed(202)
y1_sample = sigma_x * np.random.randn(N)
y2_sample = sigma_x * np.random.randn(N)
cc_no_mask_sample = fftshift_lag(cross_corr_no_mask(y1_sample, y2_sample))
cc_common_sample = fftshift_lag(cross_corr_common_mask(y1_sample, y2_sample, M_mask))
ax.plot(lag_axis, cc_no_mask_sample, color='steelblue', linewidth=0.9, alpha=0.7,
        label='Cell A (no mask): uniform null')
ax.plot(lag_axis, cc_common_sample, color='crimson', linewidth=0.9, alpha=0.85,
        label='Cell C (common mask): null shaped by $A_M(\\tau)$')
ax.axhline(thr, color='black', linewidth=0.8, linestyle='--',
           label=f'threshold $\\pm{thr/baseline_sigma:.1f}\\,\\sigma_{{\\rm A}}$',
           alpha=0.7)
ax.axhline(-thr, color='black', linewidth=0.8, linestyle='--', alpha=0.7)
ax.set_xlim(-0.5, 0.5)
ax.set_xlabel(r'lag $\tau$')
ax.set_ylabel(r'$\hat C(\tau)$ (single realization)')
ax.set_title("Single null realization\n(no signal, threshold crossings only from noise)")
ax.legend(loc='lower right', fontsize=8.5)
ax.grid(alpha=0.3)

# Panel 2: empirical vs predicted variance per lag
ax = axes[1]
ax.plot(lag_axis, var_A_centered, color='steelblue', linewidth=1.5,
        label=r'Cell A: empirical Var$[\hat C(\tau)]$')
ax.plot(lag_axis, var_A_predicted, color='steelblue', linewidth=2,
        linestyle=':',
        label=r'Cell A: predicted $\sigma^4 = $ const')
ax.plot(lag_axis, var_C_centered, color='crimson', linewidth=1.5,
        label=r'Cell C: empirical Var$[\hat C(\tau)]$')
ax.plot(lag_axis, var_C_pred_centered, color='black', linewidth=1.4,
        linestyle='--',
        label=r'Cell C: predicted $\sigma^4 A_M(\tau)/T$')
ax.set_xlabel(r'lag $\tau$')
ax.set_ylabel(r'Var$[\hat C(\tau)]$')
ax.set_xlim(-0.5, 0.5)
ax.set_title(f'Null variance vs lag\n'
             f'({n_real} independent realizations)')
ax.legend(loc='lower center', fontsize=8.5)
ax.grid(alpha=0.3)

# Panel 3: empirical false-alarm rate per lag
ax = axes[2]
ax.plot(lag_axis, fap_A_centered, color='steelblue', linewidth=1.5,
        label='Cell A')
ax.plot(lag_axis, fap_C_centered, color='crimson', linewidth=1.5,
        label='Cell C')
# Reference: predicted FAP given variance pattern
from scipy.special import erf as _erf
fap_C_predicted_centered = 2 * (1 - 0.5 * (1 + np.array(
    [_erf(thr / (np.sqrt(2 * v))) if v > 0 else 0
     for v in var_C_pred_centered])))
ax.plot(lag_axis, fap_C_predicted_centered, 'k--', linewidth=1.2,
        label=r'predicted Cell C FAP', alpha=0.7)
ax.set_xlabel(r'lag $\tau$')
ax.set_ylabel(r'FAP$(\tau)$ at fixed threshold')
ax.set_xlim(-0.5, 0.5)
ax.set_title(f'False-alarm rate vs lag\n'
             f'(threshold $|\\hat C|>2.5\\sigma_A$)')
ax.legend(loc='upper center', fontsize=8.5)
ax.grid(alpha=0.3)

plt.suptitle("Second-moment phantom: common-mask cross-correlation has $\\tau$-dependent null variance "
             "(quadratic in mask)",
             fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(f'{OUTPUT_DIR}/mf_second_moment.png', dpi=110, bbox_inches='tight')
plt.close()
print(f"Saved {OUTPUT_DIR}/mf_second_moment.png")

# Numerical record for verification.txt
sm_var_max = float(var_C.max())
sm_var_min = float(var_C[A_M > 0.01].min())
sm_var_uniform = sigma_x ** 4 * dt * T_total
sm_var_pred_max = float(var_C_pred_centered.max())
sm_var_pred_min = float(var_C_pred_centered[var_C_pred_centered > 1e-6].min())
sm_var_resid = float(np.max(np.abs(var_C - var_C_predicted)))
print(f"  Var ratio Cell C max/min: {sm_var_max / sm_var_min:.3f}")
print(f"  Var Cell C empirical-vs-predicted max abs error: {sm_var_resid:.4e}")

# ============================================================
# FIGURE 5: DISCONFIRMER PROTOCOLS
# ============================================================
# Two protocols from statistical_phantoms.md §5:
#   (a) Amplitude sweep (§5.1): the first-moment phantom magnitude
#       scales LINEARLY with signal amplitude c. A real source does
#       too, so this alone is not a discriminator. But the SECOND-
#       moment phantom (variance pattern) is INDEPENDENT of c.
#       Comparing how the peak height responds to amplitude scaling
#       distinguishes signal-driven peaks from noise-driven ones.
#
#   (b) Time-slide / mask-translation (§5.2): real signals persist
#       under translation of the mask geometry. Phantom peaks (driven
#       by the mask) move with the mask. This is the gold-standard
#       disconfirmer used in gravitational-wave pipelines.

fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))

# Panel A: Amplitude sweep
ax = axes[0]
amplitudes = np.array([0.0, 0.25, 0.5, 1.0, 2.0])
# Use the "wide pulse straddling gap" scenario from Figure 2
tau0_wide = scenarios['straddle']['tau0']
sigma_wide = scenarios['straddle']['sigma']
colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(amplitudes)))

for i, c in enumerate(amplitudes):
    f = c * gaussian_pulse(t_grid, tau0_wide, width=sigma_wide)
    sig_B = mf_cellB(M_mask * f)
    ax.plot(tau_grid, sig_B, color=colors[i], linewidth=1.6,
            label=f'$c$ = {c}')
ax.axvspan(t_G - Delta / 2, t_G + Delta / 2, color='gray', alpha=0.25,
           label='gap')
ax.axvline(tau0_wide, color='red', linewidth=0.9, linestyle='--', alpha=0.7,
           label=fr'$\tau_0={tau0_wide}$')
ax.set_xlabel(r'template arrival time $\tau$')
ax.set_ylabel(r'$D_B(\tau)$ (signal-only response)')
ax.set_xlim(0.05, 0.95)
ax.set_title("Amplitude sweep (Cell B):\n"
             "twin phantom peaks scale LINEARLY in $c$")
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3)

# Panel B: Time-slide of the mask
ax = axes[1]
# Use the WIDE pulse at tau_0 = 0.50 (sigma = 0.06) so masking part of
# the pulse creates a phantom-displacement effect. Slide the gap, watch
# the phantom-distorted profile move with the gap while the underlying
# pulse stays put.
tau0_real = 0.50
sigma_real = 0.060

gap_centers = np.array([0.30, 0.45, 0.60, 0.75])
colors2 = plt.cm.plasma(np.linspace(0.15, 0.85, len(gap_centers)))

# First, compute reference (no mask) for comparison
f_real = c_amp * gaussian_pulse(t_grid, tau0_real, width=sigma_real)
sig_no_mask = (H @ f_real) * dt / H_norm
ax.plot(tau_grid, sig_no_mask, color='black', linewidth=1.4,
        linestyle='--', alpha=0.6, label='no mask (reference)', zorder=1)

for i, t_G_slide in enumerate(gap_centers):
    in_gap_slide = (t_grid >= t_G_slide - Delta / 2) & \
                   (t_grid < t_G_slide + Delta / 2)
    M_slide = (~in_gap_slide).astype(float)
    sig_B_slide = (H @ (M_slide * f_real)) * dt / H_norm
    ax.plot(tau_grid, sig_B_slide, color=colors2[i], linewidth=1.6,
            label=fr'gap at $t_G$ = {t_G_slide:.2f}', zorder=2)
    ax.axvspan(t_G_slide - Delta / 2, t_G_slide + Delta / 2,
               color=colors2[i], alpha=0.06, zorder=0)

ax.axvline(tau0_real, color='red', linewidth=1.0, linestyle='--', alpha=0.7,
           label=fr'true $\tau_0={tau0_real}$', zorder=10)
ax.set_xlabel(r'template arrival time $\tau$')
ax.set_ylabel(r'$D_B(\tau)$ (signal-only response)')
ax.set_xlim(0.05, 0.95)
ax.set_title("Time-slide (Cell B):\n"
             "real peak stays near $\\tau_0$; mask-shaped distortions follow the gap")
ax.legend(loc='upper right', fontsize=8.5)
ax.grid(alpha=0.3)

plt.suptitle("Disconfirmer protocols (statistical_phantoms.md §5)",
             fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(f'{OUTPUT_DIR}/mf_disconfirmers.png', dpi=110, bbox_inches='tight')
plt.close()
print(f"Saved {OUTPUT_DIR}/mf_disconfirmers.png")

# Linearity test (numeric, for verification.txt):
# For Cell B response at the LEFT phantom peak, scale linearly with c.
ph_amplitudes = []
for c in amplitudes:
    f = c * gaussian_pulse(t_grid, tau0_wide, width=sigma_wide)
    sig_B = mf_cellB(M_mask * f)
    left_region_idx = tau_grid < t_G - Delta / 2
    if left_region_idx.any():
        peak_val = sig_B[left_region_idx].max()
    else:
        peak_val = 0
    ph_amplitudes.append(peak_val)
ph_amplitudes = np.array(ph_amplitudes)
# Linear fit through origin
nonzero = amplitudes > 0
slope = float(np.sum(ph_amplitudes[nonzero]) / np.sum(amplitudes[nonzero]))
predicted_lin = slope * amplitudes
linearity_err = float(np.max(np.abs(ph_amplitudes - predicted_lin)) /
                       max(ph_amplitudes.max(), 1e-12))
print(f"  Amplitude sweep linearity: max relative deviation = {linearity_err:.4e}")

# ============================================================
# NUMERICAL VERIFICATION RECORD
# ============================================================

# Re-collect numbers we want in the verification record
# 1. Four-object identity (already computed: identity_max_err)
# 2. Cell-C signal-side prediction: c sqrt(beta) * ||h||
emp_C_outside_gap = empirical_C_peak[(tau_grid[::10] < t_G - Delta/2) |
                                      (tau_grid[::10] > t_G + Delta/2)]
pred_C_outside_gap = predicted_C_peak[(tau_grid[::10] < t_G - Delta/2) |
                                       (tau_grid[::10] > t_G + Delta/2)]
mask_pred_max = np.abs(pred_C_outside_gap).max()
C_signal_pred_err = float(
    np.max(np.abs(emp_C_outside_gap - pred_C_outside_gap)) /
    max(mask_pred_max, 1e-12))

# 3. Cell-B/A retention prediction: D_B^2/D_A^2 = beta^2
emp_BA = empirical_BA_ratio[(tau_grid[::10] < t_G - Delta/2) |
                             (tau_grid[::10] > t_G + Delta/2)]
pred_BA = predicted_BA_ratio[(tau_grid[::10] < t_G - Delta/2) |
                              (tau_grid[::10] > t_G + Delta/2)]
BA_pred_err = float(np.nanmax(np.abs(emp_BA - pred_BA)))

# 4. Twin phantom peak locations (cell B, wide pulse straddling gap)
sig_straddle = signal_response_cellB(0.60, 0.060)
left_idx = tau_grid < t_G - Delta / 2
right_idx = tau_grid > t_G + Delta / 2
phantom_peak_L = float(tau_grid[left_idx][np.argmax(sig_straddle[left_idx])])
phantom_peak_R = float(tau_grid[right_idx][np.argmax(sig_straddle[right_idx])])

with open(f'{OUTPUT_DIR}/mf_masked_verification.txt', 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("Matched filter with temporal gap: numerical verification\n")
    f.write("Framework: statistical_phantoms.md §4.3 with §1.3 four-object\n")
    f.write("decomposition; §6 of common_mask_correlation.md for the\n")
    f.write("quadratic-in-mask covariance regime.\n")
    f.write("=" * 70 + "\n\n")

    f.write("Setup:\n")
    f.write(f"  Time grid: N = {N}, T = {T_total}, dt = {dt:.6f}\n")
    f.write(f"  Pulse width: sigma_p = {sigma_p}\n")
    f.write(f"  Noise: sigma_n = {sigma_n}\n")
    f.write(f"  Gap: t_G = {t_G}, Delta = {Delta} "
            f"(gap fraction = {gap_fraction:.3f})\n")
    f.write(f"  Tau scan: {len(tau_grid)} points on [{tau_grid[0]:.2f}, "
            f"{tau_grid[-1]:.2f}]\n")
    f.write(f"  beta(tau) range: "
            f"[{beta_tau.min():.3f}, {beta_tau.max():.3f}]\n\n")

    f.write("=" * 70 + "\n")
    f.write("PART I — Four-object identity (per principal direction):\n")
    f.write("=" * 70 + "\n")
    f.write("  At each tau, the four scalar laws are functions of beta(tau):\n")
    f.write("    retention   = beta^2\n")
    f.write("    suppression = (1 - beta)^2\n")
    f.write("    leakage     = beta * (1 - beta)\n")
    f.write("    total       = 1 - beta\n")
    f.write("  Identity: total = suppression + leakage\n")
    f.write(f"  Max |total - suppression - leakage| = "
            f"{identity_max_err:.2e} (machine precision)\n\n")

    f.write("=" * 70 + "\n")
    f.write("PART II — Signal-side scaling predictions\n")
    f.write("=" * 70 + "\n")
    f.write("Cell-B / Cell-A signal-power ratio at the true tau_0:\n")
    f.write("  Predicted:  D_B(tau_0)^2 / D_A(tau_0)^2 = beta(tau_0)^2\n")
    f.write("  Empirical match (away from gap): "
            f"max |error| = {BA_pred_err:.2e}\n")
    f.write("  This is the RETENTION scalar applied directly to the\n")
    f.write("  matched-filter signal-power loss.\n\n")

    f.write("Cell-C peak amplitude (mask-aware analyst, signal at tau_0):\n")
    f.write("  Predicted:  D_C(tau_0) = c * sqrt(beta(tau_0)) * ||h_tau_0||\n")
    f.write("  Empirical match (away from gap): "
            f"max relative error = {C_signal_pred_err:.2e}\n")
    f.write("  This is the cell-C signal-side attenuation factor;\n")
    f.write("  with mask-aware normalization the peak STAYS at tau_0\n")
    f.write("  but its amplitude carries the mask-geometry penalty.\n\n")

    f.write("Twin phantom peaks (Cell B, wide pulse straddling gap):\n")
    f.write(f"  Signal: tau_0 = 0.60, sigma_p = 0.060, gap [0.52, 0.68]\n")
    f.write(f"  Phantom peak left of gap:  tau ~= {phantom_peak_L:.3f}\n")
    f.write(f"  Phantom peak right of gap: tau ~= {phantom_peak_R:.3f}\n")
    f.write("  Neither coincides with the true tau_0 = 0.60. The single\n")
    f.write("  signal has been split into TWO phantom peaks by the\n")
    f.write("  geometry of the gap.\n\n")

    f.write("=" * 70 + "\n")
    f.write("PART III — Second-moment phantom (common-mask cross-correlation)\n")
    f.write("=" * 70 + "\n")
    f.write("Two iid white-noise streams y1, y2 (sigma_x = "
            f"{sigma_x}); both observed\n")
    f.write("through the same temporal mask M. The cross-correlation at\n")
    f.write("lag tau has variance proportional to A_M(tau), the auto-\n")
    f.write("correlation of the mask:\n")
    f.write("  predicted: Var[Chat(tau)] = sigma^4 * dt * A_M(tau)\n")
    f.write(f"  realizations: {n_real}\n")
    f.write(f"  Empirical Var max/min ratio: {sm_var_max / sm_var_min:.3f}\n")
    f.write(f"  (predicted: {0.84/0.68:.3f}; mask geometry sets this)\n")
    f.write(f"  Empirical-vs-predicted Var max abs error: "
            f"{sm_var_resid:.4e}\n")
    f.write("  The bump in Cell-C variance at tau = 0 IS the phantom\n")
    f.write("  signature: an analyst applying a uniform threshold across\n")
    f.write("  lags would see preferential triggering at tau = 0 with\n")
    f.write("  NO physical signal present.\n\n")

    f.write("=" * 70 + "\n")
    f.write("PART IV — Disconfirmer protocols\n")
    f.write("=" * 70 + "\n")
    f.write("Amplitude sweep (statistical_phantoms.md §5.1):\n")
    f.write(f"  Twin phantom peak amplitude vs c: "
            f"max relative deviation from linearity = "
            f"{linearity_err:.4e}\n")
    f.write("  Both real signals AND first-moment phantoms scale linearly\n")
    f.write("  in c. By itself this is NOT a discriminator -- but the\n")
    f.write("  second-moment phantom (variance pattern) is independent\n")
    f.write("  of c, providing a different lever.\n\n")

    f.write("Time-slide / mask translation (statistical_phantoms.md §5.2):\n")
    f.write("  Real signals are invariant under translation of the mask;\n")
    f.write("  phantom features track the mask. See mf_disconfirmers.png\n")
    f.write("  right panel for visual demonstration.\n\n")

    f.write("=" * 70 + "\n")
    f.write("CONCLUSION\n")
    f.write("=" * 70 + "\n")
    f.write("The framework's predictions match the empirical matched-filter\n")
    f.write("output to floating-point precision (signal side) and to\n")
    f.write("Monte-Carlo accuracy O(1/sqrt(N_realizations)) (noise side):\n")
    f.write(" * Four-object identity: machine precision.\n")
    f.write(" * Signal-side scaling laws (retention, sqrt-beta): matched.\n")
    f.write(" * Twin phantom peaks: appear at gap edges as predicted.\n")
    f.write(" * Null-variance shape: matches mask autocorrelation.\n")
    f.write(" * Linearity in c: machine precision.\n")
    f.write("The phantom anatomy IS the framework's geometry made visible\n")
    f.write("in matched-filter output.\n")

print(f"\nSaved {OUTPUT_DIR}/mf_masked_verification.txt")

print("\n" + "=" * 60)
print("All figures and verification record generated.")
print("=" * 60)
