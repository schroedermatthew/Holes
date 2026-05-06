"""
The spectral basis of the same matched filter.

Same setup as mf_masked_demonstration.py: 1D periodic time series,
temporal gap [0.52, 0.68]. Now the template parameter is FREQUENCY
xi (sinusoidal templates), not arrival time tau (pulse templates).

Signal: pure sinusoid at f_0 cycles per unit time.

Cell A (no mask):    D_A(xi) is the standard finite-duration matched
                     filter. Sharp main lobe at xi = f_0 with width
                     ~ 1/T.

Cell B (temporal gap, ideal template): D_B(xi) acquires SPECTRAL
                     sidelobes spaced by 1/Delta around f_0 — the
                     classical spectral-leakage / Lomb-Scargle
                     pattern, here understood as a first-moment
                     phantom in the spectral basis.

Same temporal gap as before. Same framework. Same beta(xi). Different
parameter being scanned, different phantom signature.

Output: mf_spectral_basis.png
"""

import os
import numpy as np
import matplotlib.pyplot as plt

OUTPUT_DIR = '/mnt/user-data/outputs'

# Same time grid and gap as mf_masked_demonstration.py
N = 4096
T_total = 1.0
dt = T_total / N
t = np.linspace(0, T_total, N, endpoint=False)

t_G = 0.60
Delta = 0.16
in_gap = (t >= t_G - Delta / 2) & (t < t_G + Delta / 2)
M = (~in_gap).astype(float)

# Signal: sinusoid at integer frequency f_0 (so cell A is sharp)
f_0 = 16.0
c_amp = 1.0
signal = c_amp * np.cos(2 * np.pi * f_0 * t)

# Frequency template scan
xi_grid = np.linspace(0, 40, 4001)

def mf_freq(y, xi_arr):
    """Matched-filter scan over frequency templates h_xi = cos(2 pi xi t).

    D(xi) = sum_t cos(2 pi xi t) * y(t) * dt / ||cos||
    """
    out = np.empty_like(xi_arr)
    for k, xi in enumerate(xi_arr):
        h = np.cos(2 * np.pi * xi * t)
        norm = np.sqrt(np.sum(h ** 2) * dt)
        out[k] = (h @ y) * dt / norm
    return out

D_A = mf_freq(signal, xi_grid)
D_B = mf_freq(M * signal, xi_grid)

# Predicted Cell B: convolution of FFT of M with delta at f_0
# In closed form for the rectangular gap:
# hat{M}(nu) = delta(nu) - exp(-2 pi i nu t_G) Delta sinc(Delta nu)
# D_B(xi) ~ (c/2) [hat{M}(xi - f_0) + hat{M}(xi + f_0)] / sqrt(T/2)
# We use this only for indicator lines marking the predicted sidelobes.
sidelobe_offsets = np.array([-3, -2, -1, 1, 2, 3]) / Delta
sidelobe_freqs = f_0 + sidelobe_offsets

# Build figure
fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))

# Left: time-domain view (the same masked signal as the original demo)
ax = axes[0]
ax.plot(t, signal, color='gray', linewidth=0.4, alpha=0.6,
        label=r'signal $c\cos(2\pi f_0 t)$')
ax.plot(t, M * signal, color='black', linewidth=0.5,
        label=r'masked $M(t)\,f(t)$')
ax.axvspan(t_G - Delta / 2, t_G + Delta / 2, color='gray', alpha=0.30,
           label=fr'temporal gap (width {Delta})')
ax.set_xlabel('time $t$')
ax.set_ylabel('signal')
ax.set_title(f'Time-domain view: sinusoid at $f_0={f_0}$\n'
             '(same temporal gap as original demo)', fontsize=11)
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3)

# Right: |D(xi)| in the spectral matched filter (absolute value reveals
# the sidelobe envelope cleanly; signed D oscillates and obscures structure)
ax = axes[1]
ax.plot(xi_grid, np.abs(D_A), color='steelblue', linewidth=1.6, alpha=0.85,
        label=r'$|D_A(\xi)|$  (no mask)')
ax.plot(xi_grid, np.abs(D_B), color='crimson', linewidth=1.4, alpha=0.85,
        label=r'$|D_B(\xi)|$  (temporal gap)')
ax.fill_between(xi_grid, 0, np.maximum(np.abs(D_B) - np.abs(D_A), 0),
                color='orange', alpha=0.30,
                label='gap-induced excess (the phantom)')

# Mark true frequency
ax.axvline(f_0, color='black', linestyle='--', alpha=0.5, linewidth=1.0)
ax.text(f_0 + 0.2, np.abs(D_A).max() * 0.92, fr'$f_0={f_0}$', fontsize=9,
        color='black', va='top')

# Mark predicted sidelobes
for s in sidelobe_freqs:
    if 8 < s < 28:
        ax.axvline(s, color='darkorange', linestyle=':', alpha=0.55,
                   linewidth=1.0)
ax.text(0.985, 0.62, r'orange ticks: $f_0 \pm k/\Delta$',
        transform=ax.transAxes, ha='right', fontsize=9, color='darkorange',
        style='italic')

ax.set_xlim(8, 28)
ax.set_ylim(0, np.abs(D_A).max() * 1.08)
ax.set_xlabel(r'template frequency $\xi$ (cycles per unit time)')
ax.set_ylabel(r'$|D(\xi)|$')
ax.set_title('Spectral matched filter: temporal gap creates phantom frequencies',
             fontsize=11)
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3)

plt.suptitle('Same mask, same data, different parameter scan: phantom anatomy '
             'changes basis with the templates',
             fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(f'{OUTPUT_DIR}/mf_spectral_basis.png', dpi=110, bbox_inches='tight')
plt.close()
print(f"Saved {OUTPUT_DIR}/mf_spectral_basis.png")
