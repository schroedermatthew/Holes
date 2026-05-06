"""
2D matched filtering with regional masks: where do real signals get
MISSED? Companion to mf_masked_demonstration.py extending the §4.3
example to 2D.

The first-moment phantom (Cell B's twin peaks) is "false detection."
This demo addresses the OTHER side: where does a real signal fail to
be detected? In the framework's language: where does the "total"
object 1 - beta(x_0, y_0) become large enough that detection fails?

In 1D, beta(tau) is a curve and the blind set is a 1D interval
(approximately the gap). In 2D, beta(x_0, y_0) is a 2D map, and the
blind set is a 2D REGION whose shape directly reflects the mask
geometry: sharp corners survive, disconnected mask components produce
disconnected blind sets, anisotropic masks produce anisotropic blind
maps, periodic mask structure becomes periodic blind structure.

The blind map is NON-RANDOM: it is the convolution
    beta(x_0, y_0) = (M * h^2)(x_0, y_0) / ||h||^2,
the mask convolved with the squared template kernel. It can be
computed in advance from the mask geometry and template shape, before
any data is collected.

Output:
  mf_2d_blind_map.png       beta(x,y) maps for four mask geometries
  mf_2d_missed_signal.png   empirical detection rate vs predicted blind set
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm as _norm

OUTPUT_DIR = '/mnt/user-data/outputs'
os.makedirs(OUTPUT_DIR, exist_ok=True)
np.random.seed(42)

# ============================================================
# 2D SETUP
# ============================================================

N = 96
x = np.linspace(0, 1, N)
y = np.linspace(0, 1, N)
X, Y = np.meshgrid(x, y, indexing='ij')
dx = 1.0 / (N - 1)

template_sigma = 0.035

def template2d(x0, y0, sigma=template_sigma):
    return np.exp(-((X - x0) ** 2 + (Y - y0) ** 2) / (2 * sigma ** 2))


def beta_map_fft(M, sigma=template_sigma):
    """beta(x0, y0) = (M * h^2)(x0, y0) / ||h^2||_1, via FFT."""
    sigma_eff = sigma / np.sqrt(2)
    XX = np.minimum(X, 1 - X)
    YY = np.minimum(Y, 1 - Y)
    h_sq_kernel = np.exp(-(XX ** 2 + YY ** 2) / (2 * sigma_eff ** 2))
    h_sq_kernel /= h_sq_kernel.sum()
    M_fft = np.fft.fft2(M)
    K_fft = np.fft.fft2(h_sq_kernel)
    return np.real(np.fft.ifft2(M_fft * K_fft))


# ============================================================
# FOUR MASK GEOMETRIES
# ============================================================

mask_1 = np.ones((N, N))
mask_1[(X > 0.55) & (X < 0.80) & (Y > 0.55) & (Y < 0.80)] = 0

mask_2 = np.ones((N, N))
mask_2[(X > 0.20) & (X < 0.35) & (Y > 0.65) & (Y < 0.80)] = 0
mask_2[(X > 0.60) & (X < 0.75) & (Y > 0.20) & (Y < 0.35)] = 0

mask_3 = np.ones((N, N))
mask_3[(X > 0.40) & (X < 0.60) & (Y > 0.20) & (Y < 0.80)] = 0
mask_3[(X > 0.20) & (X < 0.80) & (Y > 0.40) & (Y < 0.60)] = 0

mask_4 = np.ones((N, N))
hole_centers = [(0.20, 0.20), (0.20, 0.50), (0.20, 0.80),
                (0.50, 0.20), (0.50, 0.50), (0.50, 0.80),
                (0.80, 0.20), (0.80, 0.50), (0.80, 0.80)]
hole_radius = 0.045
for cx, cy in hole_centers:
    mask_4[((X - cx) ** 2 + (Y - cy) ** 2) < hole_radius ** 2] = 0

masks = {
    'single':   {'M': mask_1, 'name': 'Single rectangular hole'},
    'two':      {'M': mask_2, 'name': 'Two disconnected holes'},
    'cross':    {'M': mask_3, 'name': 'Cross-shaped mask'},
    'periodic': {'M': mask_4, 'name': 'Periodic dot pattern (3x3)'},
}

for key, m in masks.items():
    m['beta'] = beta_map_fft(m['M'])
    print(f"{m['name']:34s}: "
          f"beta range [{m['beta'].min():.3f}, {m['beta'].max():.3f}], "
          f"mask area = {1 - m['M'].mean():.3f}")

# ============================================================
# FIGURE 1: BLIND MAPS FOR FOUR MASK GEOMETRIES
# ============================================================

fig, axes = plt.subplots(2, 4, figsize=(15.5, 7.6))

for col, (key, m) in enumerate(masks.items()):
    ax = axes[0, col]
    ax.imshow(m['M'].T, origin='lower', cmap='gray', vmin=0, vmax=1,
              extent=[0, 1, 0, 1])
    ax.set_title(m['name'], fontsize=11)
    ax.set_xticks([0, 0.5, 1])
    ax.set_yticks([0, 0.5, 1])
    if col == 0:
        ax.set_ylabel('mask $M(x,y)$\n(black = masked)', fontsize=10)

    ax = axes[1, col]
    im = ax.imshow(m['beta'].T, origin='lower', cmap='viridis',
                   vmin=0, vmax=1, extent=[0, 1, 0, 1])
    ax.contour(X.T, Y.T, m['M'].T, levels=[0.5], colors='red',
               linewidths=1.0, linestyles='--')
    ax.set_title(r'$\beta(x_0, y_0)$', fontsize=10)
    ax.set_xticks([0, 0.5, 1])
    ax.set_yticks([0, 0.5, 1])
    if col == 0:
        ax.set_ylabel('detectability $\\beta(x_0,y_0)$\n(0=blind, 1=full)',
                      fontsize=10)
    if col == 3:
        cbar = plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04)
        cbar.set_label(r'$\beta$', rotation=0, labelpad=10)

plt.suptitle('2D blind maps: where templates lose mass to the mask. '
             'Missed-signal structure inherits mask geometry.',
             fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig(f'{OUTPUT_DIR}/mf_2d_blind_map.png', dpi=110, bbox_inches='tight')
plt.close()
print(f"\nSaved {OUTPUT_DIR}/mf_2d_blind_map.png")

# ============================================================
# FIGURE 2: EMPIRICAL DETECTION RATE vs PREDICTED BLIND SET
# ============================================================

mask_demo = masks['cross']['M']
beta_demo = masks['cross']['beta']

N_test = 16
x_test = np.linspace(0.06, 0.94, N_test)
y_test = np.linspace(0.06, 0.94, N_test)

c_amp = 1.0
sigma_n = 1.5         # tuned so signal SNR is borderline (~4 at beta=1)
SNR_threshold = 3.0

h0 = template2d(0.5, 0.5)
h_norm = np.sqrt(np.sum(h0 ** 2) * dx ** 2)

# Discrete-MF noise std: with our normalization
#   D_C = (sum_pix Mh * y * dx^2) / sqrt(sum_pix Mh^2 * dx^2)
# the noise variance is sigma_n^2 * dx^2 (NOT sigma_n^2). The natural
# matched-filter unit is sigma_n * dx, and threshold k means
# "signal-mean exceeds k noise-std-units".
noise_std_DC = sigma_n * dx
threshold_DC = SNR_threshold * noise_std_DC
snr_max = c_amp * h_norm / noise_std_DC
print(f"\n||h|| = {h_norm:.4f}, dx = {dx:.5f}")
print(f"D_C noise std = {noise_std_DC:.5f}")
print(f"Detection threshold (in D_C units) = {threshold_DC:.5f}")
print(f"Max SNR (at beta=1): c*||h||/(sigma*dx) = {snr_max:.2f}")

# Predicted detection rate using the framework:
#   D_C ~ Normal(c * sqrt(beta) * ||h||, sigma_n*dx)  under signal at (x_0,y_0)
#   P(detect) = P(D_C > k*sigma_n*dx) = 1 - Phi(k - c*sqrt(beta)*||h||/(sigma_n*dx))
predicted_rate = np.zeros((N_test, N_test))
beta_at_test = np.zeros((N_test, N_test))
for i, x0 in enumerate(x_test):
    for j, y0 in enumerate(y_test):
        i_b = int(round(x0 * (N - 1)))
        j_b = int(round(y0 * (N - 1)))
        b = max(beta_demo[i_b, j_b], 0)
        beta_at_test[i, j] = b
        snr_signal = c_amp * np.sqrt(b) * h_norm / noise_std_DC
        predicted_rate[i, j] = 1.0 - _norm.cdf(SNR_threshold - snr_signal)

# Empirical detection rate (vectorized over realizations)
n_real = 200
detect_rate = np.zeros((N_test, N_test))

for i, x0 in enumerate(x_test):
    for j, y0 in enumerate(y_test):
        h_xy = template2d(x0, y0)
        Mh = mask_demo * h_xy
        Mh_norm = np.sqrt(np.sum(Mh ** 2) * dx ** 2)
        if Mh_norm < 1e-10:
            detect_rate[i, j] = 0.0
            continue
        signal = c_amp * h_xy
        signal_part = np.sum(Mh * (mask_demo * signal)) * dx ** 2 / Mh_norm
        Mh_flat = Mh.ravel()
        noise_batch = sigma_n * np.random.randn(n_real, N * N)
        noise_part = (noise_batch @ Mh_flat) * dx ** 2 / Mh_norm
        D_C = signal_part + noise_part
        detect_rate[i, j] = float(np.mean(D_C > threshold_DC))
    if (i + 1) % 4 == 0:
        print(f"  detection sweep: column {i+1}/{N_test}")

# Sanity check: empirical D_C noise std should equal sigma_n*dx
i_check, j_check = N_test // 2, N_test // 2
x0, y0 = x_test[i_check], y_test[j_check]
h_xy = template2d(x0, y0)
Mh = mask_demo * h_xy
Mh_norm = np.sqrt(np.sum(Mh ** 2) * dx ** 2)
Mh_flat = Mh.ravel()
noise_check = sigma_n * np.random.randn(2000, N * N)
D_C_noise = (noise_check @ Mh_flat) * dx ** 2 / Mh_norm
print(f"  noise std check at ({x0:.2f},{y0:.2f}): "
      f"empirical = {D_C_noise.std():.5f}, "
      f"predicted = {noise_std_DC:.5f}")

# Build the figure
fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))

ax = axes[0]
im = ax.imshow(beta_demo.T, origin='lower', cmap='viridis',
               vmin=0, vmax=1, extent=[0, 1, 0, 1])
ax.contour(X.T, Y.T, mask_demo.T, levels=[0.5], colors='red',
           linewidths=1.2, linestyles='--')
ax.set_title('Predicted detectability $\\beta(x_0, y_0)$\n'
             '(framework, computed from mask geometry alone)',
             fontsize=10)
ax.set_xlabel('$x_0$'); ax.set_ylabel('$y_0$')
plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04, label=r'$\beta$')

ax = axes[1]
im = ax.imshow(predicted_rate.T, origin='lower', cmap='RdYlGn',
               vmin=0, vmax=1,
               extent=[x_test[0], x_test[-1], y_test[0], y_test[-1]])
ax.contour(X.T, Y.T, mask_demo.T, levels=[0.5], colors='black',
           linewidths=1.2, linestyles='--')
ax.set_title(f'Predicted detection rate\n'
             f'($c={c_amp},\\,\\sigma_n={sigma_n},\\,$threshold $={SNR_threshold}\\sigma_n$)',
             fontsize=10)
ax.set_xlabel('$x_0$'); ax.set_ylabel('$y_0$')
plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04, label='P(detect)')

ax = axes[2]
im = ax.imshow(detect_rate.T, origin='lower', cmap='RdYlGn',
               vmin=0, vmax=1,
               extent=[x_test[0], x_test[-1], y_test[0], y_test[-1]])
ax.contour(X.T, Y.T, mask_demo.T, levels=[0.5], colors='black',
           linewidths=1.2, linestyles='--')
ax.set_title(f'Empirical detection rate\n'
             f'({n_real} realizations per position)',
             fontsize=10)
ax.set_xlabel('$x_0$'); ax.set_ylabel('$y_0$')
plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04, label='P(detect)')

plt.suptitle('Real signals get MISSED systematically: empirical rate '
             'matches the framework-predicted blind set',
             fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(f'{OUTPUT_DIR}/mf_2d_missed_signal.png', dpi=110,
            bbox_inches='tight')
plt.close()
print(f"Saved {OUTPUT_DIR}/mf_2d_missed_signal.png")

# Verification numbers
emp_pred_corr = np.corrcoef(predicted_rate.ravel(),
                              detect_rate.ravel())[0, 1]
emp_pred_mae = np.mean(np.abs(predicted_rate - detect_rate))
print(f"\nDetection-rate verification:")
print(f"  Pearson r(predicted, empirical) = {emp_pred_corr:.4f}")
print(f"  Mean absolute error              = {emp_pred_mae:.4f}")

print("\n" + "=" * 60)
print("2D blind-set demonstration complete.")
print("=" * 60)
