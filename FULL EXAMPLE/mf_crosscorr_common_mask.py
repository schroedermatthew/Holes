"""
Cross-correlation of two signals through the same circular gap.

This is the 2D version of the §6 common-mask regime in
common_mask_correlation.md. Setup matches the scattering doc:
    - 2D periodic domain [-pi, pi]^2
    - Circular gap, same as in scattering_analogy.ipynb
    - Two INDEPENDENT noise fields y^(1), y^(2), both observed through
      the SAME circular gap.

Compute the spatial cross-correlation
    Chat(Delta) = integral M(x) y1(x) M(x+Delta) y2(x+Delta) dx
as a function of 2D lag Delta = (Delta_x, Delta_y).

Under the NULL (independent fields, no coherent source):
    E[Chat(Delta)] = 0
    Var[Chat(Delta)] = sigma^4 * dx^2 * A_M(Delta)
where A_M(Delta) = integral M(x) M(x+Delta) dx is the 2D mask
autocorrelation.

Even though no real signal is present, the cross-correlation has a
non-uniform variance pattern shaped by the GEOMETRY OF THE GAP. An
analyst applying a uniform threshold across spatial lags will see
preferential triggering at small lags, where A_M is largest. This is
the second-moment phantom in 2D: a STRUCTURED noise pattern that mimics
a coherent source.

For comparison, we also show what a real coherent source looks like
on top of this null pattern.

Output: mf_crosscorr_common_mask.png
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

OUTPUT_DIR = '/mnt/user-data/outputs'
np.random.seed(42)

# ============================================================
# 2D SETUP (matching scattering_analogy.ipynb)
# ============================================================

N = 128
L = 2 * np.pi
dx = L / N
x = np.linspace(-L/2, L/2, N, endpoint=False)
y = np.linspace(-L/2, L/2, N, endpoint=False)
X, Y = np.meshgrid(x, y, indexing='ij')

# Circular gap
gap_radius = 1.5      # larger gap so the variance pattern is clearly visible
                      # (~18% of domain area; A_M ratio ~ 1.3)
in_gap = X**2 + Y**2 < gap_radius**2
M = (~in_gap).astype(float)

# White Gaussian noise (deferring whitening to a separate step;
# for the §6 second-moment phantom the cleanest case is white noise
# already; the colored-noise case adds the W(k)^2 reweighting from
# the previous figure).
sigma_n = 1.0

# ============================================================
# PREDICTED VARIANCE MAP (FRAMEWORK)
# ============================================================
# Var[Chat(Delta)] = sigma^4 * dx^2 * A_M(Delta)
# where A_M(Delta) = dx^2 * sum_x M(x) M(x+Delta).
# Use FFT for the autocorrelation: A_M = real(ifft(|fft(M)|^2)) * dx^2.

M_fft = np.fft.fft2(M)
A_M_2d = np.real(np.fft.ifft2(np.abs(M_fft) ** 2)) * dx ** 2
predicted_var = sigma_n ** 4 * dx ** 2 * A_M_2d

print(f"Setup:")
print(f"  Domain: {N}x{N} on [-pi,pi]^2, dx = {dx:.4f}")
print(f"  Circular gap of radius {gap_radius}")
print(f"  Unmasked area = {M.sum() * dx**2:.4f}")
print(f"  Mask area = {(1-M).sum() * dx**2:.4f}")
print(f"  A_M(0) = {A_M_2d[0,0]:.4f} (= unmasked area)")
print(f"  A_M(infty) plateau = {A_M_2d[N//2, N//2]:.4f}")

# ============================================================
# EMPIRICAL VARIANCE FROM MANY REALIZATIONS (NULL)
# ============================================================

n_real = 1000
sum_C = np.zeros((N, N))
sum_C_sq = np.zeros((N, N))

for k in range(n_real):
    n1 = sigma_n * np.random.randn(N, N)
    n2 = sigma_n * np.random.randn(N, N)
    y1 = M * n1
    y2 = M * n2
    # Cross-correlation as function of 2D lag, via FFT:
    # Chat(Delta) = integral y1(x) y2(x+Delta) dx ~ ifft(conj(Y1) * Y2) * dx^2
    Y1 = np.fft.fft2(y1)
    Y2 = np.fft.fft2(y2)
    C = np.real(np.fft.ifft2(np.conj(Y1) * Y2)) * dx ** 2
    sum_C += C
    sum_C_sq += C ** 2
    if (k + 1) % 100 == 0:
        print(f"  realization {k+1}/{n_real}")

mean_C = sum_C / n_real
empirical_var = sum_C_sq / n_real - mean_C ** 2

# ============================================================
# CROSS-CORRELATION WITH A REAL COHERENT SIGNAL
# ============================================================
# Add the same plane-wave-like signal cos(k_0 x) to BOTH streams.
# Result: cross-correlation has a real peak structure at lag = 0
# (oscillating along Delta_x as cos(k_0 Delta_x)) on top of the
# null variance pattern.

k_0 = 8.0
signal = 1.0 * np.cos(k_0 * X)
y1_sig = M * (signal + sigma_n * np.random.randn(N, N))
y2_sig = M * (signal + sigma_n * np.random.randn(N, N))
Y1_sig = np.fft.fft2(y1_sig)
Y2_sig = np.fft.fft2(y2_sig)
C_with_signal = np.real(np.fft.ifft2(np.conj(Y1_sig) * Y2_sig)) * dx ** 2

# Predicted signal cross-correlation (no noise, just signal):
y1_signal_only = M * signal
y2_signal_only = M * signal
Y1_so = np.fft.fft2(y1_signal_only)
Y2_so = np.fft.fft2(y2_signal_only)
C_predicted_signal = np.real(np.fft.ifft2(np.conj(Y1_so) * Y2_so)) * dx ** 2

# ============================================================
# FIGURE
# ============================================================

# Lag axes (centered at zero after fftshift)
lag_axis = np.fft.fftshift(np.fft.fftfreq(N, d=1) * L)
predicted_var_c = np.fft.fftshift(predicted_var)
empirical_var_c = np.fft.fftshift(empirical_var)
mean_C_c = np.fft.fftshift(mean_C)
C_with_signal_c = np.fft.fftshift(C_with_signal)
C_predicted_signal_c = np.fft.fftshift(C_predicted_signal)

# 2D lag-distance for radial averaging
DLX, DLY = np.meshgrid(lag_axis, lag_axis, indexing='ij')
delta_r = np.sqrt(DLX ** 2 + DLY ** 2)

fig = plt.figure(figsize=(15, 10))
gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 0.9],
                      hspace=0.42, wspace=0.30)

# Row 1: setup
ax = fig.add_subplot(gs[0, 0])
ax.imshow(M.T, cmap='gray', origin='lower', extent=[-L/2, L/2, -L/2, L/2],
          vmin=0, vmax=1)
ax.add_patch(Circle((0, 0), gap_radius, fill=False, edgecolor='red',
                     linewidth=1.4, linestyle='--'))
ax.set_title(f'Mask: circular gap of radius {gap_radius}\n'
             '(black = masked, white = observed)', fontsize=10)
ax.set_xlabel('$x$'); ax.set_ylabel('$y$')

ax = fig.add_subplot(gs[0, 1])
im = ax.imshow(predicted_var_c.T, cmap='viridis', origin='lower',
               extent=[-L/2, L/2, -L/2, L/2])
ax.add_patch(Circle((0, 0), 2 * gap_radius, fill=False, edgecolor='white',
                     linewidth=1.2, linestyle=':'))
ax.set_title(r'Predicted Var[$\hat C(\Delta)$]'
             '\n' r'$= \sigma^4\,dx^2\,A_M(\Delta)$ (from mask geometry)',
             fontsize=10)
ax.set_xlabel(r'$\Delta_x$'); ax.set_ylabel(r'$\Delta_y$')
plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04)

ax = fig.add_subplot(gs[0, 2])
im = ax.imshow(empirical_var_c.T, cmap='viridis', origin='lower',
               extent=[-L/2, L/2, -L/2, L/2])
ax.add_patch(Circle((0, 0), 2 * gap_radius, fill=False, edgecolor='white',
                     linewidth=1.2, linestyle=':'))
ax.set_title(f'Empirical Var[$\\hat C(\\Delta)$]\n'
             f'({n_real} null realizations)', fontsize=10)
ax.set_xlabel(r'$\Delta_x$'); ax.set_ylabel(r'$\Delta_y$')
plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04)

# Row 2: with a real coherent source
ax = fig.add_subplot(gs[1, 0])
vmax = np.abs(C_predicted_signal_c).max()
im = ax.imshow(C_predicted_signal_c.T, cmap='RdBu_r',
               vmin=-vmax, vmax=vmax, origin='lower',
               extent=[-L/2, L/2, -L/2, L/2])
ax.set_title(f'Cross-correlation of\n$M\\cos(k_0 x)$ with itself ($k_0={int(k_0)}$)',
             fontsize=10)
ax.set_xlabel(r'$\Delta_x$'); ax.set_ylabel(r'$\Delta_y$')
plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04)

ax = fig.add_subplot(gs[1, 1])
vmax2 = np.abs(C_with_signal_c).max()
im = ax.imshow(C_with_signal_c.T, cmap='RdBu_r',
               vmin=-vmax2, vmax=vmax2, origin='lower',
               extent=[-L/2, L/2, -L/2, L/2])
ax.set_title('Cross-correlation: signal + noise\n(one realization)', fontsize=10)
ax.set_xlabel(r'$\Delta_x$'); ax.set_ylabel(r'$\Delta_y$')
plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04)

# Phantom-vs-real: show a 1D slice through Delta_y=0 of:
#   (a) empirical null variance (the phantom shape), as +/- 1-sigma band
#   (b) signal cross-correlation
ax = fig.add_subplot(gs[1, 2])
center = N // 2
sigma_band = np.sqrt(empirical_var_c[:, center])
ax.fill_between(lag_axis, -3 * sigma_band, 3 * sigma_band, color='gray',
                alpha=0.30,
                label=r'$\pm 3\sigma$ null band (mask-shaped)')
ax.plot(lag_axis, C_with_signal_c[:, center], color='crimson', linewidth=1.4,
        label='signal+noise realization')
ax.plot(lag_axis, C_predicted_signal_c[:, center], color='black',
        linewidth=1.2, linestyle='--', alpha=0.6,
        label='signal-only (predicted)')
ax.axvline(2 * gap_radius, color='blue', linestyle=':', alpha=0.6,
           linewidth=1)
ax.axvline(-2 * gap_radius, color='blue', linestyle=':', alpha=0.6,
           linewidth=1)
ax.set_xlabel(r'$\Delta_x$ (slice $\Delta_y=0$)')
ax.set_ylabel(r'$\hat C$')
ax.set_title('Real signal vs phantom variance band', fontsize=10)
ax.legend(loc='upper right', fontsize=8)
ax.grid(alpha=0.3)

# Row 3: radial profile + per-pixel scatter (bottom-spanning row)
ax = fig.add_subplot(gs[2, 0:2])
# Bin by radius
r_edges = np.linspace(0, L * 0.45, 40)
r_centers = (r_edges[:-1] + r_edges[1:]) / 2
pred_rad, emp_rad, emp_se = [], [], []
for i in range(len(r_edges) - 1):
    mask_bin = (delta_r >= r_edges[i]) & (delta_r < r_edges[i + 1])
    if mask_bin.any():
        pred_rad.append(predicted_var_c[mask_bin].mean())
        v = empirical_var_c[mask_bin]
        emp_rad.append(v.mean())
        emp_se.append(v.std() / np.sqrt(len(v)))
    else:
        pred_rad.append(np.nan)
        emp_rad.append(np.nan)
        emp_se.append(np.nan)
pred_rad = np.array(pred_rad)
emp_rad = np.array(emp_rad)
emp_se = np.array(emp_se)

ax.plot(r_centers, pred_rad, color='black', linewidth=2.0, label='predicted',
        zorder=3)
ax.errorbar(r_centers, emp_rad, yerr=emp_se, fmt='o', color='crimson',
            markersize=5, linewidth=1, label='empirical (radial avg)',
            zorder=4)
ax.axvline(2 * gap_radius, color='blue', linestyle=':', alpha=0.6,
           label=r'$|\Delta| = 2 a$ (gap diameter)')
ax.set_xlabel(r'$|\Delta|$ (lag distance)')
ax.set_ylabel(r'Var[$\hat C(\Delta)$]')
ax.set_title('Variance vs lag (radial average): predicted vs empirical',
             fontsize=10)
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3)

# Right: per-pixel scatter
ax = fig.add_subplot(gs[2, 2])
ax.scatter(predicted_var_c.ravel(), empirical_var_c.ravel(),
           alpha=0.35, s=4, color='crimson', edgecolors='none')
diag_max = max(predicted_var_c.max(), empirical_var_c.max()) * 1.05
ax.plot([0, diag_max], [0, diag_max], color='black',
        linestyle='--', alpha=0.6, label=r'$y = x$')
ax.set_xlabel('Predicted Var$[\\hat C(\\Delta)]$')
ax.set_ylabel('Empirical Var$[\\hat C(\\Delta)]$')
ax.set_title('Per-pixel agreement', fontsize=10)
ax.set_xlim(0, diag_max); ax.set_ylim(0, diag_max)
ax.set_aspect('equal')
ax.legend(loc='upper left', fontsize=9)
ax.grid(alpha=0.3)

plt.suptitle('Cross-correlation of two signals through the SAME circular gap: '
             'mean vanishes under null, but variance has mask-shaped phantom structure',
             fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(f'{OUTPUT_DIR}/mf_crosscorr_common_mask.png', dpi=110,
            bbox_inches='tight')
plt.close()
print(f"\nSaved {OUTPUT_DIR}/mf_crosscorr_common_mask.png")

# Verification
significant = predicted_var_c > predicted_var_c.max() * 0.01
mean_rel_err = np.mean(np.abs(empirical_var_c[significant] -
                                 predicted_var_c[significant]) /
                         predicted_var_c[significant])
max_var_ratio = predicted_var_c.max() / predicted_var_c[predicted_var_c > 0].min()
print(f"\nVerification:")
print(f"  Mean relative error (per pixel, significant region): "
      f"{mean_rel_err:.4e}")
print(f"  Variance ratio max/min across lag space: {max_var_ratio:.3f}")
print(f"  Pearson r: {np.corrcoef(predicted_var_c.ravel(), empirical_var_c.ravel())[0,1]:.4f}")
