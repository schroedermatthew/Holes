"""
Full example: rounded-rectangle gap + colored noise + standard
whitening pipeline + cross-correlation of two signals.

Ingredients:
    - 2D periodic domain [-pi, pi]^2 (matching scattering doc)
    - Rounded-rectangle gap (W=1.5, H=0.9, corner radius r=0.35)
    - 2D Lorentzian colored noise: S_n(k) = sigma_0^2 k_c^2 / (k_c^2 + |k|^2)
      (low-spatial-frequency dominated, k_c = 3)
    - Standard pipeline:
          observe y^(i) = M * (signal + noise^(i))
          whiten:   y_w^(i) = W * y^(i),   W(k) = 1/sqrt(S_n(k))
          cross-correlate: Chat(Delta) = integral y_w^(1)(x) y_w^(2)(x+Delta) dx

Two scenarios:
    NULL: no signal, just two independent colored noise streams.
        Empirical Var[Chat] across many realizations gives the
        cross-correlation phantom pattern.
    SIGNAL: coherent plane wave cos(k_0 x) in both streams.
        Cross-correlation has a clear stripe pattern that punches
        through the phantom band.

Output: mf_full_example_rounded_rect.png
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUTPUT_DIR = '/mnt/user-data/outputs'
np.random.seed(42)

# ============================================================
# 2D SETUP
# ============================================================

N = 128
L = 2 * np.pi
dx = L / N
x = np.linspace(-L/2, L/2, N, endpoint=False)
y = np.linspace(-L/2, L/2, N, endpoint=False)
X, Y = np.meshgrid(x, y, indexing='ij')

# Rounded rectangle gap (Minkowski sum of inner rect + disk)
W_rect = 1.5
H_rect = 0.9
r_corner = 0.35
dx_in = np.maximum(np.abs(X) - (W_rect - r_corner), 0)
dy_in = np.maximum(np.abs(Y) - (H_rect - r_corner), 0)
dist_to_inner = np.sqrt(dx_in ** 2 + dy_in ** 2)
in_gap = dist_to_inner < r_corner
M = (~in_gap).astype(float)

# Fourier wavenumber grids
kx_arr = 2 * np.pi * np.fft.fftfreq(N, d=dx)
ky_arr = 2 * np.pi * np.fft.fftfreq(N, d=dx)
KX, KY = np.meshgrid(kx_arr, ky_arr, indexing='ij')
K_mag = np.sqrt(KX ** 2 + KY ** 2)

# Colored noise: 2D Lorentzian PSD
k_c = 3.0
sigma_0 = 1.0
S_n = sigma_0 ** 2 * k_c ** 2 / (k_c ** 2 + K_mag ** 2)

# Whitening filter
W_kernel = 1.0 / np.sqrt(S_n)

print(f"Setup:")
print(f"  Domain: {N}x{N} on [-pi,pi]^2, dx = {dx:.4f}")
print(f"  Mask: rounded rectangle W={W_rect}, H={H_rect}, r={r_corner}")
print(f"  Mask area = {(1-M).sum()*dx**2:.4f}")
print(f"  Noise PSD: 2D Lorentzian, k_c = {k_c}")
print(f"  S_n(k=0) = {S_n[0,0]:.4f} (peak, low-spatial-freq dominated)")
print(f"  Whitening: W = 1/sqrt(S_n); W(0) = {W_kernel[0,0]:.4f}, "
      f"W(k_max) = {W_kernel[N//2, N//2]:.4f}")

# ============================================================
# COLORED NOISE GENERATION
# ============================================================

def generate_colored_noise():
    """Generate one realization of 2D field with PSD S_n."""
    n_white = np.random.standard_normal((N, N))
    Z = np.fft.fft2(n_white)
    return np.real(np.fft.ifft2(Z * np.sqrt(S_n)))

def whiten(field):
    """Apply whitening filter W = 1/sqrt(S_n) in Fourier domain."""
    F = np.fft.fft2(field)
    return np.real(np.fft.ifft2(F * W_kernel))

# ============================================================
# MONTE CARLO: NULL DISTRIBUTION OF Chat
# ============================================================

n_real = 2000
sum_C = np.zeros((N, N))
sum_C_sq = np.zeros((N, N))

print(f"\nRunning {n_real} null realizations of full pipeline...")
for i in range(n_real):
    n1 = generate_colored_noise()
    n2 = generate_colored_noise()
    # Standard pipeline: mask, then whiten
    y1_w = whiten(M * n1)
    y2_w = whiten(M * n2)
    # Cross-correlate
    Y1 = np.fft.fft2(y1_w)
    Y2 = np.fft.fft2(y2_w)
    C = np.real(np.fft.ifft2(np.conj(Y1) * Y2)) * dx ** 2
    sum_C += C
    sum_C_sq += C ** 2
    if (i + 1) % 500 == 0:
        print(f"  realization {i+1}/{n_real}")

mean_C = sum_C / n_real
var_C = sum_C_sq / n_real - mean_C ** 2

print(f"  Variance map: peak = {var_C.max():.4f}, "
      f"plateau = {var_C[N//2, N//2]:.4f}, "
      f"ratio = {var_C.max() / var_C[N//2, N//2]:.3f}")

# ============================================================
# WITH A REAL COHERENT SIGNAL
# ============================================================

k_0 = 8.0
signal = 1.0 * np.cos(k_0 * X)

# Signal-only through pipeline (no noise)
y1_so = whiten(M * signal)
y2_so = whiten(M * signal)
Y1_so = np.fft.fft2(y1_so)
Y2_so = np.fft.fft2(y2_so)
C_predicted_signal = np.real(np.fft.ifft2(np.conj(Y1_so) * Y2_so)) * dx ** 2

# Signal + noise (one realization through pipeline)
n1_sig = generate_colored_noise()
n2_sig = generate_colored_noise()
y1_sig = whiten(M * (signal + n1_sig))
y2_sig = whiten(M * (signal + n2_sig))
Y1_sig = np.fft.fft2(y1_sig)
Y2_sig = np.fft.fft2(y2_sig)
C_with_signal = np.real(np.fft.ifft2(np.conj(Y1_sig) * Y2_sig)) * dx ** 2

# ============================================================
# FIGURE
# ============================================================

# Center for fftshift
var_C_c = np.fft.fftshift(var_C)
mean_C_c = np.fft.fftshift(mean_C)
C_predicted_signal_c = np.fft.fftshift(C_predicted_signal)
C_with_signal_c = np.fft.fftshift(C_with_signal)
S_n_c = np.fft.fftshift(S_n)
W_kernel_c = np.fft.fftshift(W_kernel)

lag_axis = np.fft.fftshift(np.fft.fftfreq(N, d=1) * L)
kx_centered = np.fft.fftshift(kx_arr)

def outline_rounded_rect(ax, W, H, r, color='red', ls='--', lw=1.5):
    bbox = FancyBboxPatch((-W + r, -H + r), 2 * (W - r), 2 * (H - r),
                          boxstyle=f"round,pad=0,rounding_size={r}",
                          fill=False, edgecolor=color, linewidth=lw,
                          linestyle=ls)
    ax.add_patch(bbox)

fig = plt.figure(figsize=(15, 12))
gs = fig.add_gridspec(3, 3, hspace=0.45, wspace=0.32)

# ------ Row 1: ingredients ------
ax = fig.add_subplot(gs[0, 0])
ax.imshow(M.T, cmap='gray', origin='lower',
          extent=[-L/2, L/2, -L/2, L/2], vmin=0, vmax=1)
outline_rounded_rect(ax, W_rect, H_rect, r_corner, color='red')
ax.set_title('Mask: rounded rectangle\n'
             f'$W={W_rect},\\ H={H_rect},\\ r_{{\\rm corner}}={r_corner}$',
             fontsize=10)
ax.set_xlabel('$x$'); ax.set_ylabel('$y$')

ax = fig.add_subplot(gs[0, 1])
im = ax.imshow(np.log10(S_n_c.T), cmap='magma', origin='lower',
               extent=[kx_centered[0], kx_centered[-1],
                        kx_centered[0], kx_centered[-1]])
ax.set_title(r'Noise PSD $S_n(k)$ (2D Lorentzian, $k_c=3$)' '\n'
             '(log scale; low spatial freqs dominate)', fontsize=10)
ax.set_xlabel('$k_x$'); ax.set_ylabel('$k_y$')
ax.set_xlim(-15, 15); ax.set_ylim(-15, 15)
plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04, label=r'$\log_{10} S_n$')

ax = fig.add_subplot(gs[0, 2])
im = ax.imshow(np.log10(W_kernel_c.T), cmap='viridis', origin='lower',
               extent=[kx_centered[0], kx_centered[-1],
                        kx_centered[0], kx_centered[-1]])
ax.set_title(r'Whitening filter $W(k) = 1/\sqrt{S_n(k)}$' '\n'
             '(boosts high-freq content)', fontsize=10)
ax.set_xlabel('$k_x$'); ax.set_ylabel('$k_y$')
ax.set_xlim(-15, 15); ax.set_ylim(-15, 15)
plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04, label=r'$\log_{10} W$')

# ------ Row 2: phantom under null ------
ax = fig.add_subplot(gs[1, 0])
im = ax.imshow(var_C_c.T, cmap='viridis', origin='lower',
               extent=[-L/2, L/2, -L/2, L/2])
outline_rounded_rect(ax, 2 * W_rect, 2 * H_rect, 2 * r_corner,
                     color='white', ls=':', lw=1.0)
ax.set_title(r'Empirical Var$[\hat C(\Delta)]$ under NULL'
             f'\n({n_real} realizations through full pipeline)',
             fontsize=10)
ax.set_xlabel(r'$\Delta_x$'); ax.set_ylabel(r'$\Delta_y$')
plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04)

ax = fig.add_subplot(gs[1, 1])
center = N // 2
ax.plot(lag_axis, var_C_c[:, center], color='crimson', linewidth=1.6,
        label='colored + whitening')
ax.axvline(2 * W_rect, color='blue', linestyle=':', alpha=0.6,
           linewidth=1, label=r'$|\Delta_x|=2W$')
ax.axvline(-2 * W_rect, color='blue', linestyle=':', alpha=0.6, linewidth=1)
ax.set_xlabel(r'$\Delta_x$ (slice $\Delta_y = 0$, the LONG axis)')
ax.set_ylabel(r'Var$[\hat C]$')
ax.set_title('Variance slice (long axis)', fontsize=10)
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3)

ax = fig.add_subplot(gs[1, 2])
ax.plot(lag_axis, var_C_c[center, :], color='crimson', linewidth=1.6,
        label='colored + whitening')
ax.axvline(2 * H_rect, color='blue', linestyle=':', alpha=0.6,
           linewidth=1, label=r'$|\Delta_y|=2H$')
ax.axvline(-2 * H_rect, color='blue', linestyle=':', alpha=0.6, linewidth=1)
ax.set_xlabel(r'$\Delta_y$ (slice $\Delta_x = 0$, the SHORT axis)')
ax.set_ylabel(r'Var$[\hat C]$')
ax.set_title('Variance slice (short axis)', fontsize=10)
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3)

# ------ Row 3: with a real coherent signal ------
ax = fig.add_subplot(gs[2, 0])
vmax = np.abs(C_predicted_signal_c).max()
im = ax.imshow(C_predicted_signal_c.T, cmap='RdBu_r',
               vmin=-vmax, vmax=vmax, origin='lower',
               extent=[-L/2, L/2, -L/2, L/2])
ax.set_title(f'Cross-correlation of\n$W(M\\cos(k_0 x))$ with itself ($k_0={int(k_0)}$)\n'
             '(signal-only, no noise)', fontsize=10)
ax.set_xlabel(r'$\Delta_x$'); ax.set_ylabel(r'$\Delta_y$')
plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04)

ax = fig.add_subplot(gs[2, 1])
vmax2 = np.abs(C_with_signal_c).max()
im = ax.imshow(C_with_signal_c.T, cmap='RdBu_r',
               vmin=-vmax2, vmax=vmax2, origin='lower',
               extent=[-L/2, L/2, -L/2, L/2])
ax.set_title('Signal + colored noise through pipeline\n(one realization)',
             fontsize=10)
ax.set_xlabel(r'$\Delta_x$'); ax.set_ylabel(r'$\Delta_y$')
plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04)

ax = fig.add_subplot(gs[2, 2])
sigma_band = np.sqrt(var_C_c[:, center])
ax.fill_between(lag_axis, -3 * sigma_band, 3 * sigma_band, color='gray',
                alpha=0.30, label=r'$\pm 3\sigma$ null band')
ax.plot(lag_axis, C_with_signal_c[:, center], color='crimson', linewidth=1.4,
        label='signal+noise realization')
ax.plot(lag_axis, C_predicted_signal_c[:, center], color='black',
        linewidth=1.2, linestyle='--', alpha=0.6, label='signal-only')
ax.axvline(2 * W_rect, color='blue', linestyle=':', alpha=0.5, linewidth=1)
ax.axvline(-2 * W_rect, color='blue', linestyle=':', alpha=0.5, linewidth=1)
ax.set_xlabel(r'$\Delta_x$ (slice $\Delta_y=0$)')
ax.set_ylabel(r'$\hat C$')
ax.set_title('Detection: real signal vs phantom band', fontsize=10)
ax.legend(loc='upper right', fontsize=8)
ax.grid(alpha=0.3)

plt.suptitle('Full pipeline: rounded-rectangle gap + colored noise + standard whitening + cross-correlation of two signals',
             fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(f'{OUTPUT_DIR}/mf_full_example_rounded_rect.png',
            dpi=110, bbox_inches='tight')
plt.close()
print(f"\nSaved {OUTPUT_DIR}/mf_full_example_rounded_rect.png")
