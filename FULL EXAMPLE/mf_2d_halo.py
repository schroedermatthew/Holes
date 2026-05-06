"""
The blind region is bigger than the hole. The geometric fact is that
beta(x_0, y_0) is a smoothed version of the mask indicator, smoothed
by the template kernel. So the "soft-fail" zone has width ~
template_sigma on each side of the mask, regardless of detection
threshold.

Show this directly: 1D slice through the cross mask with three
different template widths overlaid. The halo width scales linearly
with the template width.

Output: mf_2d_halo.png
"""

import os
import numpy as np
import matplotlib.pyplot as plt

OUTPUT_DIR = '/mnt/user-data/outputs'

N = 96
x_grid = np.linspace(0, 1, N)
y_grid = np.linspace(0, 1, N)
X, Y = np.meshgrid(x_grid, y_grid, indexing='ij')
dx = 1.0 / (N - 1)

# Cross mask
M = np.ones((N, N))
M[(X > 0.40) & (X < 0.60) & (Y > 0.20) & (Y < 0.80)] = 0
M[(X > 0.20) & (X < 0.80) & (Y > 0.40) & (Y < 0.60)] = 0


def beta_map(M, sigma):
    sigma_eff = sigma / np.sqrt(2)
    XX = np.minimum(X, 1 - X)
    YY = np.minimum(Y, 1 - Y)
    h_sq_kernel = np.exp(-(XX ** 2 + YY ** 2) / (2 * sigma_eff ** 2))
    h_sq_kernel /= h_sq_kernel.sum()
    return np.real(np.fft.ifft2(np.fft.fft2(M) * np.fft.fft2(h_sq_kernel)))


sigmas_to_show = [0.020, 0.040, 0.075]
beta_maps = {s: beta_map(M, s) for s in sigmas_to_show}

j_slice = N // 2
M_slice = M[:, j_slice]

mask_idx = np.where(M_slice < 0.5)[0]
mask_left = x_grid[mask_idx[0]]
mask_right = x_grid[mask_idx[-1]]
print(f"Cross arm boundary on slice: [{mask_left:.3f}, {mask_right:.3f}]")

fig = plt.figure(figsize=(13.5, 5.0))
gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.6], wspace=0.25)

# Left: 2D beta map for the middle template width
ax = fig.add_subplot(gs[0])
sigma_show = 0.040
beta_show = beta_maps[sigma_show]
im = ax.imshow(beta_show.T, origin='lower', cmap='viridis', vmin=0, vmax=1,
               extent=[0, 1, 0, 1])
ax.contour(X.T, Y.T, M.T, levels=[0.5], colors='red',
           linewidths=1.4, linestyles='--', zorder=3)
ax.axhline(0.5, color='white', linewidth=1.4, linestyle=':', alpha=0.9, zorder=4)
ax.text(0.97, 0.515, r'slice $y_0=0.5$', color='white', fontsize=9,
        ha='right', va='bottom', zorder=5,
        bbox=dict(facecolor='black', alpha=0.4, edgecolor='none'))
ax.set_xlabel('$x_0$')
ax.set_ylabel('$y_0$')
ax.set_title(rf'$\beta(x_0,y_0)$ for $\sigma={sigma_show}$' '\n'
             '(red: mask boundary)', fontsize=11)
plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04, label=r'$\beta$')

# Right: 1D slice with three template widths
ax = fig.add_subplot(gs[1])
ax.fill_between(x_grid, 0, 1, where=(M_slice < 0.5), color='black',
                alpha=0.15, step='mid', label='mask region (step)')
ax.axvline(mask_left, color='black', linewidth=0.7, linestyle='--', alpha=0.7)
ax.axvline(mask_right, color='black', linewidth=0.7, linestyle='--', alpha=0.7)

colors = ['tab:purple', 'tab:blue', 'tab:cyan']
for sigma, color in zip(sigmas_to_show, colors):
    beta_slice = beta_maps[sigma][:, j_slice]
    ax.plot(x_grid, beta_slice, color=color, linewidth=2.4,
            label=fr'$\beta$ with template $\sigma={sigma}$')

# Annotate halo width using middle sigma
sigma_ann = 0.040
beta_ann = beta_maps[sigma_ann][:, j_slice]
soft_threshold = 0.95
halo_entry_idx_L = np.where((beta_ann < soft_threshold) & (x_grid < mask_left))[0]
if len(halo_entry_idx_L) > 0:
    halo_entry_L = x_grid[halo_entry_idx_L[0]]
    halo_width_L = mask_left - halo_entry_L
    ax.annotate('', xy=(halo_entry_L, 0.5), xytext=(mask_left, 0.5),
                arrowprops=dict(arrowstyle='<->', color='darkorange', lw=2))
    ax.text((halo_entry_L + mask_left) / 2, 0.43,
            f'soft-fail band\n' fr'$\sim {halo_width_L:.2f} \approx {halo_width_L/sigma_ann:.1f}\sigma$',
            color='darkorange', ha='center', va='top', fontsize=9.5,
            fontweight='bold')

ax.set_xlabel(r'$x_0$ (with $y_0 = 0.5$ fixed)')
ax.set_ylabel(r'$\beta(x_0, 0.5)$')
ax.set_xlim(0.05, 0.95)
ax.set_ylim(-0.05, 1.10)
ax.set_title(r'$\beta(x_0, 0.5)$ is a smoothed mask: halo width = template width',
             fontsize=11)
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3)

ax.text(0.5, -0.10,
        r'sharper template (smaller $\sigma$) $\Longrightarrow$ smaller halo; '
        r'same mask, different blind regions',
        ha='center', va='top', fontsize=9, color='gray',
        transform=ax.transAxes, style='italic')

plt.suptitle('The blind region is bigger than the hole — '
             'by approximately the template width',
             fontsize=12)
plt.tight_layout(rect=[0, 0.04, 1, 0.94])
plt.savefig(f'{OUTPUT_DIR}/mf_2d_halo.png', dpi=110, bbox_inches='tight')
plt.close()
print(f"Saved {OUTPUT_DIR}/mf_2d_halo.png")
