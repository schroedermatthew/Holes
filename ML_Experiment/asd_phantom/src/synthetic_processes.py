"""
Synthetic process generators for ASD encoder validation.

Each generator produces a real-valued sequence of length N. Used as input
to the block-local ordinal quartile encoder to validate that the resulting
ASD features have the expected qualitative signatures from radar (per
ASD_RESEARCH.md).

Reference signatures expected:
  - IID Gaussian: drift -> 0, timing_cv approx 1.0, low h_star (random walk
    on F_2 with uniform letter assignment has high cancellation rate).
  - AR(1) rho=0.5: drift > 0, slightly elevated h_star.
  - AR(1) rho=0.9: clear drift, h_star elevated, Q_tail decay with r_plus
    approx 0.864 per ASD_RESEARCH.md §E7.
  - ARCH(1): drift comparable to IID but timing_cv markedly elevated due
    to volatility clustering producing cancellation bursts.
  - Shared-texture log-normal at rho=0.95: very strong drift signal, the
    structured-background regime where ASD dominates classical detectors.
"""

from __future__ import annotations
import numpy as np
from typing import Optional


def iid_gaussian(N: int, rng: np.random.Generator) -> np.ndarray:
    """IID standard normal."""
    return rng.standard_normal(N)


def ar1(N: int, rho: float, rng: np.random.Generator,
        sigma_innov: float = 1.0) -> np.ndarray:
    """
    AR(1) process: x_t = rho * x_{t-1} + epsilon_t,  epsilon_t ~ N(0, sigma)
    """
    x = np.zeros(N)
    eps = rng.standard_normal(N) * sigma_innov
    x[0] = eps[0] / np.sqrt(1 - rho**2)  # stationary initial
    for t in range(1, N):
        x[t] = rho * x[t - 1] + eps[t]
    return x


def arch1(N: int, alpha0: float = 0.1, alpha1: float = 0.7,
          rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """
    ARCH(1): x_t = sigma_t * z_t where sigma_t^2 = alpha0 + alpha1 * x_{t-1}^2,
    z_t ~ N(0,1) IID.

    Per ASD_RESEARCH.md: ACF approx 0 but strong volatility clustering
    detectable in timing_cv at |z| > 40.

    Stability: alpha1 < 1 required. With alpha1 = 0.7, ARCH effect is
    pronounced but stable.
    """
    if rng is None:
        rng = np.random.default_rng()
    z = rng.standard_normal(N)
    x = np.zeros(N)
    sigma2 = alpha0 / (1 - alpha1)  # unconditional variance
    x[0] = z[0] * np.sqrt(sigma2)
    for t in range(1, N):
        sigma2 = alpha0 + alpha1 * x[t - 1] ** 2
        x[t] = z[t] * np.sqrt(sigma2)
    return x


def fgn(N: int, H: float, rng: np.random.Generator) -> np.ndarray:
    """
    Fractional Gaussian noise via Davies-Harte / Cholesky on the covariance.

    For length N >= 2048, prefer FFT-based (Davies-Harte). For our test
    lengths we use direct Cholesky on the covariance matrix; this is O(N^3)
    so keep N <= 2000.

    H is the Hurst parameter; H = 0.5 -> IID (white noise), H > 0.5 -> long
    range dependence (positive correlations).
    """
    if N > 2000:
        # For larger N, fall back to Davies-Harte
        return _fgn_davies_harte(N, H, rng)
    # Covariance: gamma(k) = 0.5 * (|k+1|^2H - 2|k|^2H + |k-1|^2H)
    ks = np.arange(N)
    gamma_k = 0.5 * (np.abs(ks + 1) ** (2 * H) - 2 * np.abs(ks) ** (2 * H)
                     + np.abs(ks - 1) ** (2 * H))
    # Build Toeplitz covariance
    Sigma = np.empty((N, N))
    for i in range(N):
        for j in range(N):
            Sigma[i, j] = gamma_k[abs(i - j)]
    # Add tiny ridge for numerical PSD
    Sigma += np.eye(N) * 1e-10
    L = np.linalg.cholesky(Sigma)
    return L @ rng.standard_normal(N)


def _fgn_davies_harte(N: int, H: float, rng: np.random.Generator) -> np.ndarray:
    """FFT-based exact FGN simulation for large N."""
    M = 2 * N
    ks = np.arange(M)
    gamma_k = 0.5 * (np.abs(ks + 1) ** (2 * H) - 2 * np.abs(ks) ** (2 * H)
                     + np.abs(ks - 1) ** (2 * H))
    # Reflect for circulant
    c = np.concatenate([gamma_k[:N + 1], gamma_k[1:N][::-1]])
    lambdas = np.fft.fft(c).real
    if np.any(lambdas < 0):
        lambdas = np.maximum(lambdas, 0)
    Z = rng.standard_normal(M) + 1j * rng.standard_normal(M)
    Z[0] = rng.standard_normal()
    Z[N] = rng.standard_normal()
    out = np.fft.fft(np.sqrt(lambdas / M) * Z).real
    return out[:N]


def shared_texture_lognormal(N: int, rho: float, rng: np.random.Generator) -> np.ndarray:
    """
    Shared-texture log-normal: pixel[t] = tau(t) * eps[t], where
    tau(t) = exp(AR(1) with persistence rho) and eps[t] ~ N(0,1) IID.

    Per ASD_RESEARCH.md §5.2: this is the regime where ASD dominates
    classical matched-filter detection. drift signal is pronounced.
    """
    log_tau = ar1(N, rho, rng, sigma_innov=0.5)
    tau = np.exp(log_tau)
    eps = rng.standard_normal(N)
    return tau * eps


# Mock language model trajectory generators -- for testing the LM-side
# pipeline before plugging in real Llama. These produce sequences that
# have specific structures the ASD encoder should detect.

def mock_unshaped_lm_trajectory(N: int, rng: np.random.Generator,
                                 base_surprisal: float = 4.0,
                                 noise_scale: float = 1.0) -> np.ndarray:
    """
    Mock per-token leakage rho_i for an UNSHAPED model.

    Roughly IID Gaussian with small mean. Should produce ASD signature
    indistinguishable from IID.
    """
    return rng.normal(0.0, noise_scale, N)


def mock_commitment_shaped_trajectory(N: int, rng: np.random.Generator,
                                       commitment_length: int = 30,
                                       commitment_strength: float = 4.0,
                                       noise_scale: float = 1.0) -> np.ndarray:
    """
    Mock per-token leakage for a COMMITMENT-SHAPED trajectory:
    high rho in first `commitment_length` tokens, then ~IID.

    Should produce elevated drift and (depending on encoding) elevated h_star.
    Models the 'induced hole / commit early' signature.
    """
    rho = rng.normal(0.0, noise_scale, N)
    rho[:commitment_length] += commitment_strength
    return rho


def mock_clustered_shaped_trajectory(N: int, rng: np.random.Generator,
                                      cluster_rate: float = 0.05,
                                      cluster_strength: float = 3.0,
                                      noise_scale: float = 1.0) -> np.ndarray:
    """
    Mock per-token leakage with random bursts of high rho.

    Each position has probability `cluster_rate` of being a high-rho token
    (representing a shaped concept-token engaging the constraint).

    Should produce ARCH-like timing_cv elevation and isolated_frac decrease.
    """
    rho = rng.normal(0.0, noise_scale, N)
    burst_mask = rng.random(N) < cluster_rate
    rho[burst_mask] += cluster_strength * np.abs(rng.standard_normal(burst_mask.sum()))
    return rho


def mock_persistent_shaped_trajectory(N: int, rng: np.random.Generator,
                                       rho_persistence: float = 0.85,
                                       shape_pull: float = 1.5) -> np.ndarray:
    """
    Mock per-token leakage that follows an AR(1) with positive mean shift.

    Models a 'persistent shaping' signature where once leakage is engaged
    it tends to stay engaged for many tokens.
    """
    return shape_pull + ar1(N, rho_persistence, rng, sigma_innov=1.0)
