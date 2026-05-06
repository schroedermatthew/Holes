"""
ASD features computed from EmpiricalPair, revised v2.

The free-group walk is transient -- it drifts to infinity for any process
where extensions outpace cancellations on average. This means features
defined by "deviation of empirical depth-1 cylinder mass from harmonic"
are dominated by the directional commitment of the walk and saturate.

The discriminating signal is in the cancellation pattern: HOW OFTEN the
walk cancels (drift), HOW REGULAR cancellations are spaced (timing_cv,
isolated_frac), and HOW the depth profile decays at the active end
(Q_tail, depth growth rate).

Layer 1 features (revised):
  drift           : signed deviation of cancellation rate from the IID null
                    (calibrated empirically). Positive for ARCH-like, near
                    zero for IID, negative for AR-like persistence.
  cancel_rate     : raw cancellation rate.
  mean_depth      : average stack depth across the walk.
  mean_depth_excess: mean_depth z-scored against IID null.
  d2_excess       : empirical visit-rate to depth >= 2, z-scored.
  timing_cv       : coefficient of variation of inter-cancellation gaps.
  isolated_frac   : fraction of cancellations not adjacent to another.
  growth_rate     : final depth / N -- the asymptotic walk speed.

Layer 2 features:
  Q_tail(k)       : conditional depth survival, k = 1..6.
  r_plus          : geometric decay rate of Q_tail, fitted log-linear.

The IID null values for drift, mean_depth, etc. are calibrated by running
the encoder on IID input at the same N and block_size; results are stored
in a registry that callers can populate.
"""

from __future__ import annotations
import numpy as np
from .asd_encoder import EmpiricalPair, N_GEN, encode_and_walk
from .synthetic_processes import iid_gaussian


# ----------------------------------------------------------------------------
# IID null calibration
# ----------------------------------------------------------------------------

class IIDNull:
    """Empirical IID null reference values for centering features."""
    def __init__(self):
        self._cache = {}

    def calibrate(self, N: int, block_size: int = 4, n_seeds: int = 50):
        key = (N, block_size)
        if key in self._cache:
            return self._cache[key]
        cancels = []
        mean_depths = []
        d2_visits = []
        for seed in range(n_seeds):
            rng = np.random.default_rng(seed + 5_000_000)
            sig = iid_gaussian(N, rng)
            ep = encode_and_walk(sig, block_size=block_size, max_depth_tracked=6)
            n = ep.n_steps
            cancels.append(len(ep.cancellation_steps) / n)
            mean_depths.append(ep.depth_visits[1:].sum() / n)
            d2_visits.append(ep.depth_visits[2] / n if len(ep.depth_visits) > 2 else 0.0)
        null = {
            "cancel_rate": float(np.mean(cancels)),
            "cancel_rate_std": float(np.std(cancels)),
            "mean_depth": float(np.mean(mean_depths)),
            "mean_depth_std": float(np.std(mean_depths)),
            "d2_visit_rate": float(np.mean(d2_visits)),
            "d2_visit_rate_std": float(np.std(d2_visits)),
        }
        self._cache[key] = null
        return null


_iid_null = IIDNull()


def get_iid_null(N: int, block_size: int = 4):
    return _iid_null.calibrate(N, block_size)


# ----------------------------------------------------------------------------
# Layer 1
# ----------------------------------------------------------------------------

def cancel_rate(ep: EmpiricalPair) -> float:
    if ep.n_steps == 0:
        return 0.0
    return len(ep.cancellation_steps) / ep.n_steps


def drift(ep: EmpiricalPair, null: dict) -> float:
    """Signed deviation of cancellation rate from IID null, z-scored."""
    cr = cancel_rate(ep)
    if null["cancel_rate_std"] < 1e-10:
        return 0.0
    return (cr - null["cancel_rate"]) / null["cancel_rate_std"]


def mean_depth(ep: EmpiricalPair) -> float:
    if ep.n_steps == 0:
        return 0.0
    return float(ep.depth_visits[1:].sum() / ep.n_steps)


def mean_depth_excess(ep: EmpiricalPair, null: dict) -> float:
    md = mean_depth(ep)
    if null["mean_depth_std"] < 1e-10:
        return 0.0
    return (md - null["mean_depth"]) / null["mean_depth_std"]


def d2_excess(ep: EmpiricalPair, null: dict) -> float:
    if ep.n_steps == 0 or len(ep.depth_visits) < 3:
        return 0.0
    rate = ep.depth_visits[2] / ep.n_steps
    if null["d2_visit_rate_std"] < 1e-10:
        return 0.0
    return (rate - null["d2_visit_rate"]) / null["d2_visit_rate_std"]


def timing_cv(ep: EmpiricalPair) -> float:
    cancellations = ep.cancellation_steps
    if len(cancellations) < 2:
        return 0.0
    gaps = np.diff(cancellations)
    mean = gaps.mean()
    if mean == 0:
        return 0.0
    return float(gaps.std() / mean)


def isolated_frac(ep: EmpiricalPair, window: int = 8) -> float:
    cancellations = ep.cancellation_steps
    if len(cancellations) == 0:
        return 0.0
    if len(cancellations) == 1:
        return 1.0
    arr = np.array(cancellations)
    isolated = 0
    for i in range(len(arr)):
        prev_far = (i == 0) or (arr[i] - arr[i - 1] > window)
        next_far = (i == len(arr) - 1) or (arr[i + 1] - arr[i] > window)
        if prev_far and next_far:
            isolated += 1
    return float(isolated / len(arr))


def growth_rate(ep: EmpiricalPair) -> float:
    if ep.n_steps == 0:
        return 0.0
    final_depth = ep.n_steps - 2 * len(ep.cancellation_steps)
    return float(final_depth / ep.n_steps)


# ----------------------------------------------------------------------------
# Layer 2
# ----------------------------------------------------------------------------

def Q_tail(ep: EmpiricalPair, k_range=None) -> np.ndarray:
    if k_range is None:
        k_range = range(1, ep.max_depth_tracked + 1)
    if ep.depth_visits[1] < 1e-12:
        return np.zeros(len(list(k_range)))
    return np.array([
        ep.depth_visits[k] / ep.depth_visits[1] if k < len(ep.depth_visits) else 0.0
        for k in k_range
    ])


def depth_recurrence_fit(ep: EmpiricalPair, k_min: int = 2, k_max: int = 6) -> dict:
    qt = Q_tail(ep, k_range=range(1, ep.max_depth_tracked + 1))
    ks = np.arange(1, ep.max_depth_tracked + 1)
    mask = (ks >= k_min) & (ks <= k_max) & (qt > 1e-10)
    if mask.sum() < 2:
        return {"alpha": 0.0, "beta": 0.0, "r_plus": 0.0, "r_squared": 0.0}
    xs = ks[mask].astype(float)
    ys = np.log(qt[mask])
    A = np.vstack([np.ones_like(xs), xs]).T
    coef, *_ = np.linalg.lstsq(A, ys, rcond=None)
    alpha, beta = coef
    pred = A @ coef
    ss_res = np.sum((ys - pred) ** 2)
    ss_tot = np.sum((ys - ys.mean()) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    return {
        "alpha": float(alpha),
        "beta": float(beta),
        "r_plus": float(np.exp(beta)),
        "r_squared": float(r_squared),
    }


def layer1_features(ep: EmpiricalPair, null: dict) -> dict:
    return {
        "cancel_rate": cancel_rate(ep),
        "drift": drift(ep, null),
        "mean_depth": mean_depth(ep),
        "mean_depth_excess": mean_depth_excess(ep, null),
        "d2_excess": d2_excess(ep, null),
        "timing_cv": timing_cv(ep),
        "isolated_frac": isolated_frac(ep),
        "growth_rate": growth_rate(ep),
    }


def layer2_features(ep: EmpiricalPair) -> dict:
    Qt = Q_tail(ep)
    fit = depth_recurrence_fit(ep)
    out = {}
    for i, k in enumerate(range(1, min(7, ep.max_depth_tracked + 1))):
        out[f"Q_tail_{k}"] = float(Qt[i])
    out["r_plus"] = fit["r_plus"]
    out["r_squared"] = fit["r_squared"]
    return out


def all_features(ep: EmpiricalPair, null: dict) -> dict:
    return {**layer1_features(ep, null), **layer2_features(ep)}
