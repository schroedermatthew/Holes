"""
The scattering case from scattering_analogy.ipynb §1, but now with the
standard signal-processing pipeline: colored noise plus whitening.

Setup matches the scattering doc:
    - 2D periodic domain [-pi, pi]^2
    - Plane-wave-like signal cos(k_0 x) with k_0 = 8
    - Circular gap of radius a
    - "Recover the spectrum" = take FFT, look for the peak at k_0

The white-noise pipeline:
    observe y = M (signal + n_white) -> FFT -> spectrum
    Phantom: Airy-ring sidelobes around k_0 (Bessel J_1 envelope from
    the circular mask's 2D FFT).

The standard signal-processing pipeline (what the user is asking about):
    observe y = M (signal + n_colored) -> whiten with W = S_n^{-1/2}
    -> FFT -> spectrum
    Phantom: same Airy rings, but each ring's amplitude reweighted by
    W(k) at that spatial frequency. The whitening filter shapes the
    phantom envelope.

This is what gravitational-wave matched filtering, radar, and
many other detection pipelines actually do. The phantom doesn't
disappear — it gets reshaped by the whitening response.

Output: mf_scattering_whitening.png
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Circle

OUTPUT_DIR = '/mnt/user-data/outputs'
np.random.seed(42)

def bold_text(ax, x, y, txt, **kw):
    kw.setdefault('fontweight', 'heavy')
    kw.setdefault('color', 'black')
    t = ax.text(x, y, txt, **kw)
    t.set_path_effects([pe.withStroke(linewidth=3, foreground='white')])
    return t

# ============================================================
# 2D SETUP (matches scattering_analogy.ipynb §1)
# ============================================================

N = 256
L = 2 * np.pi
x = np.linspace(-L/2, L/2, N, endpoint=False)
y = np.linspace(-L/2, L/2, N, endpoint=False)
X, Y = np.meshgrid(x, y, indexing='ij')
dx = L / N

# Plane-wave-like signal: cos(k_0 x), real-valued for simplicity
k_0 = 8.0
signal = np.cos(k_0 * X)

# Circular mask (gap), as in the scattering doc
gap_radius = 0.7
in_gap = X**2 + Y**2 < gap_radius**2
M = (~in_gap).astype(float)

# Wavenumber arrays
kx_arr = 2 * np.pi * np.fft.fftfreq(N, d=dx)
ky_arr = 2 * np.pi * np.fft.fftfreq(N, d=dx)
KX, KY = np.meshgrid(kx_arr, ky_arr, indexing='ij')
K_mag = np.sqrt(KX**2 + KY**2)

# Colored noise PSD: 2D Lorentzian with corner k_c — low-spatial-frequency
# dominated, which is typical for realistic measurement noise (e.g., 1/f
# instrument drift in time series, low-frequency atmospheric noise in
# imaging, etc.)
k_c = 3.0  # corner wavenumber: noise is "smooth" on scales > 1/k_c
sigma_n_innov = 0.5
S_n = sigma_n_innov ** 2 * k_c ** 2 / (k_c ** 2 + K_mag ** 2)

# Whitening filter: W(k) = 1 / sqrt(S_n(k))
W_kernel = 1.0 / np.sqrt(S_n)

print(f"Setup:")
print(f"  Domain: {N}x{N} on [-pi,pi]^2, dx = {dx:.4f}")
print(f"  Signal: cos({k_0} x)")
print(f"  Gap: circle of radius {gap_radius}")
print(f"  Noise: 2D Lorentzian, corner k_c = {k_c}")
print(f"  Whitening: W(k) = 1/sqrt(S_n(k))")
print(f"  W(k_0) = {1.0/np.sqrt(sigma_n_innov**2 * k_c**2 / (k_c**2 + k_0**2)):.3f}")
print(f"  Phantom sidelobe spacing: ~ 1/gap_radius = {1/gap_radius:.3f}")

# ============================================================
# RUN BOTH PIPELINES
# ============================================================

# Generate one realization of colored noise (deterministic for reproducibility)
white_noise = sigma_n_innov * np.random.randn(N, N)
n_color = np.real(np.fft.ifft2(np.fft.fft2(white_noise) * np.sqrt(S_n) / sigma_n_innov))
# Note: this gives n_color with PSD = S_n approximately

# (A) White-noise pipeline: y_obs = M * (signal + n_white_amplitude)
#     analyst does NOT whiten (assumes white noise is already flat)
n_white = sigma_n_innov * np.random.randn(N, N)
y_white = M * (signal + n_white)

# (B) Colored-noise + whitening pipeline:
#     y_obs = M * (signal + n_color)
#     analyst whitens: y_w = W * y_obs (assumes the original S_n)
y_color = M * (signal + n_color)
Y_color_fft = np.fft.fft2(y_color)
y_whitened = np.real(np.fft.ifft2(Y_color_fft * W_kernel))

# Spectrum (log-magnitude) for visualization
def spec_log(field):
    F = np.fft.fftshift(np.abs(np.fft.fft2(field)))
    return np.log10(F + 1e-3)

spec_clean = spec_log(signal)
spec_white_pipe = spec_log(y_white)
spec_color_pipe = spec_log(y_whitened)

# Also: the IDEAL scattered field for the noise-free, white-noise case
# (just the masked signal, FFT'd) — gives the canonical Airy ring phantom
spec_signal_only_masked = spec_log(M * signal)

# ============================================================
# FIGURE
# ============================================================

fig, axes = plt.subplots(3, 3, figsize=(13, 12))

# Spatial extent for imshow
spatial_extent = [-L/2, L/2, -L/2, L/2]
# k-space extent (centered)
k_max = np.pi / dx
k_extent = [-k_max, k_max, -k_max, k_max]

# ------ Row 1: spatial views ------
ax = axes[0, 0]
ax.imshow(signal.T, cmap='RdBu_r', vmin=-1, vmax=1, origin='lower',
          extent=spatial_extent)
ax.add_patch(Circle((0, 0), gap_radius, fill=False, edgecolor='black',
                     linewidth=1.5, linestyle='--'))
ax.set_title(rf'True field: $\cos(k_0\,x)$, $k_0={int(k_0)}$' '\n'
             f'(circular gap of radius {gap_radius})', fontsize=10)
ax.set_xticks([-3, 0, 3]); ax.set_yticks([-3, 0, 3])
ax.set_xlabel('$x$'); ax.set_ylabel('$y$')

ax = axes[0, 1]
vmax = np.abs(y_color).max()
ax.imshow(y_color.T, cmap='RdBu_r', vmin=-vmax, vmax=vmax, origin='lower',
          extent=spatial_extent)
ax.add_patch(Circle((0, 0), gap_radius, fill=False, edgecolor='black',
                     linewidth=1.5, linestyle='--'))
ax.set_title('Observed: $M(\\,$signal $+$ colored noise$\\,)$\n'
             f'(2D Lorentzian noise, $k_c={k_c}$)', fontsize=10)
ax.set_xticks([-3, 0, 3]); ax.set_yticks([-3, 0, 3])
ax.set_xlabel('$x$'); ax.set_ylabel('$y$')

ax = axes[0, 2]
vmax = np.abs(y_whitened).max() * 0.5
ax.imshow(y_whitened.T, cmap='RdBu_r', vmin=-vmax, vmax=vmax, origin='lower',
          extent=spatial_extent)
ax.add_patch(Circle((0, 0), gap_radius, fill=False, edgecolor='black',
                     linewidth=1.5, linestyle='--'))
ax.set_title('Whitened: $W \\cdot M\\,(\\,$signal $+$ noise$\\,)$\n'
             '(whitening boosts high spatial freqs)', fontsize=10)
ax.set_xticks([-3, 0, 3]); ax.set_yticks([-3, 0, 3])
ax.set_xlabel('$x$'); ax.set_ylabel('$y$')

# ------ Row 2: spectra (signal-only, both pipelines) ------
# Use signal-only spectra (no noise) to show the phantom shape clearly
spec_clean_zoomed = spec_log(signal)
spec_masked_signal = spec_log(M * signal)
spec_masked_whitened_signal = spec_log(np.real(np.fft.ifft2(
    np.fft.fft2(M * signal) * W_kernel)))

# Zoom around k_0 for clarity
zoom_pix = N // 4
center_idx = N // 2
zoom_slice = slice(center_idx - zoom_pix, center_idx + zoom_pix)

# k-space extent for the zoom
k_zoom_max = k_max * zoom_pix / (N // 2)
k_zoom_extent = [-k_zoom_max, k_zoom_max, -k_zoom_max, k_zoom_max]

ax = axes[1, 0]
img = ax.imshow(spec_clean_zoomed[zoom_slice, zoom_slice].T,
                cmap='inferno', origin='lower',
                extent=k_zoom_extent, aspect='auto', vmin=-2, vmax=4)
ax.set_title('True spectrum $|\\hat{f}|$\n(delta at $\\pm k_0$)', fontsize=10)
ax.set_xlabel('$k_x$'); ax.set_ylabel('$k_y$')
ax.axvline(k_0, color='cyan', linestyle='--', linewidth=1, alpha=0.7)
ax.axvline(-k_0, color='cyan', linestyle='--', linewidth=1, alpha=0.7)
plt.colorbar(img, ax=ax, fraction=0.045, pad=0.04, label=r'$\log_{10}|\hat{f}|$')

ax = axes[1, 1]
img = ax.imshow(spec_masked_signal[zoom_slice, zoom_slice].T,
                cmap='inferno', origin='lower',
                extent=k_zoom_extent, aspect='auto', vmin=-2, vmax=4)
ax.set_title('Mask only (signal-only, no whitening)\n'
             '(Airy-ring phantom around $k_0$)', fontsize=10)
ax.set_xlabel('$k_x$'); ax.set_ylabel('$k_y$')
ax.axvline(k_0, color='cyan', linestyle='--', linewidth=1, alpha=0.7)
ax.axvline(-k_0, color='cyan', linestyle='--', linewidth=1, alpha=0.7)
plt.colorbar(img, ax=ax, fraction=0.045, pad=0.04, label=r'$\log_{10}|\hat{f}|$')

ax = axes[1, 2]
img = ax.imshow(spec_masked_whitened_signal[zoom_slice, zoom_slice].T,
                cmap='inferno', origin='lower',
                extent=k_zoom_extent, aspect='auto', vmin=-2, vmax=4)
ax.set_title('Mask + whitening (signal-only)\n'
             '(rings reshaped by $W(k)$)', fontsize=10)
ax.set_xlabel('$k_x$'); ax.set_ylabel('$k_y$')
ax.axvline(k_0, color='cyan', linestyle='--', linewidth=1, alpha=0.7)
ax.axvline(-k_0, color='cyan', linestyle='--', linewidth=1, alpha=0.7)
plt.colorbar(img, ax=ax, fraction=0.045, pad=0.04, label=r'$\log_{10}|\hat{f}|$')

# ------ Row 3: 1D radial slices through k_y = 0 + the framework prediction ------
# Take a slice through k_y = 0 to see the ring structure as a 1D curve
ky_zero_idx = N // 2
kx_centered = np.fft.fftshift(kx_arr)

# 1D slices of the three signal-only spectra
# (using signal-only — no noise — to isolate the phantom shape)
amp_clean = np.fft.fftshift(np.abs(np.fft.fft2(signal)))[ky_zero_idx, :]
amp_masked = np.fft.fftshift(np.abs(np.fft.fft2(M * signal)))[ky_zero_idx, :]
amp_masked_whitened = np.fft.fftshift(np.abs(
    np.fft.fft2(np.real(np.fft.ifft2(np.fft.fft2(M * signal) * W_kernel)))
))[ky_zero_idx, :]

# Predicted reshaping: amp_masked_whitened = W(k) * amp_masked
# (verification of the framework prediction)
W_slice = np.fft.fftshift(W_kernel)[ky_zero_idx, :]
amp_predicted = W_slice * amp_masked

# Panel: amplitude on log scale with all three curves
ax = axes[2, 0]
ax.semilogy(kx_centered, amp_masked + 1e-3,
            color='steelblue', linewidth=1.6, alpha=0.85,
            label='mask only')
ax.semilogy(kx_centered, amp_masked_whitened + 1e-3,
            color='crimson', linewidth=1.6, alpha=0.85,
            label='mask + whitening')
ax.axvline(k_0, color='black', linestyle='--', linewidth=1, alpha=0.6)
ax.axvline(-k_0, color='black', linestyle='--', linewidth=1, alpha=0.6)
ax.set_xlabel('$k_x$  (slice $k_y = 0$)')
ax.set_ylabel(r'$|\hat{f}|$')
ax.set_title('Spectrum slice (signal-only):\n'
             'whitening reshapes the Airy-ring phantom', fontsize=10)
ax.set_xlim(-25, 25)
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3, which='both')

# Panel: noise PSD and whitening filter (1D radial profile)
ax = axes[2, 1]
S_n_slice = np.fft.fftshift(S_n)[ky_zero_idx, :]
ax.semilogy(kx_centered, S_n_slice, color='red', linewidth=1.8,
            label=r'noise PSD $S_n(k)$')
ax.semilogy(kx_centered, W_slice, color='green', linewidth=1.8,
            label=r'whitening $W(k) = 1/\sqrt{S_n(k)}$')
ax.axvline(k_0, color='black', linestyle='--', linewidth=1, alpha=0.6)
ax.axvline(-k_0, color='black', linestyle='--', linewidth=1, alpha=0.6)
ax.set_xlabel('$k_x$ (slice $k_y = 0$)')
ax.set_ylabel('value')
ax.set_title('Noise spectrum and whitening filter', fontsize=10)
ax.set_xlim(-25, 25)
ax.legend(loc='lower right', fontsize=9)
ax.grid(alpha=0.3, which='both')

# Panel: empirical-vs-predicted reshaping
ax = axes[2, 2]
mask_for_plot = amp_masked > 0.05
ax.semilogy(kx_centered[mask_for_plot],
            amp_masked_whitened[mask_for_plot] + 1e-6,
            'o', color='crimson', markersize=3.5, alpha=0.7,
            label='empirical: $|\\hat{(WMs)}|$')
ax.semilogy(kx_centered[mask_for_plot],
            amp_predicted[mask_for_plot] + 1e-6,
            color='black', linewidth=1.4, linestyle='--',
            label='predicted: $W(k)\\,|\\hat{(Ms)}|$')
ax.axvline(k_0, color='black', linestyle='--', linewidth=1, alpha=0.4)
ax.axvline(-k_0, color='black', linestyle='--', linewidth=1, alpha=0.4)
ax.set_xlabel('$k_x$ (slice $k_y = 0$)')
ax.set_ylabel(r'amplitude')
ax.set_title('Framework prediction:\n'
             'whitened spectrum is $W(k)\\cdot$(unwhitened phantom)',
             fontsize=10)
ax.set_xlim(-25, 25)
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3, which='both')

plt.suptitle('Scattering case + standard pipeline: '
             'colored noise + whitening reshapes the phantom but does not erase it',
             fontsize=13)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(f'{OUTPUT_DIR}/mf_scattering_whitening.png', dpi=110,
            bbox_inches='tight')
plt.close()
print(f"\nSaved {OUTPUT_DIR}/mf_scattering_whitening.png")

# Verification: how well does W(k)*amp_masked match amp_masked_whitened?
relative_error = np.abs(amp_predicted - amp_masked_whitened) / (
    np.abs(amp_masked_whitened) + 1e-6)
# Restrict to indices where the masked amplitude is significant
significant = amp_masked > 0.5
mean_rel_err = float(relative_error[significant].mean())
max_rel_err = float(relative_error[significant].max())
print(f"\nVerification: predicted W(k)*|hat(Ms)| vs empirical |hat(WMs)|")
print(f"  Mean relative error (where significant): {mean_rel_err:.4e}")
print(f"  Max  relative error (where significant): {max_rel_err:.4e}")
