"""
ASD encoder: real-valued sequence -> F_2 walk -> empirical pair (nu, mu).

Implements:
- Block-local ordinal quartile encoding (ASD_FOUNDATIONS.md §CC1 Level 2)
- Free reduction walk on F_2 with generator set G = {a, b, b^-1, a^-1}
- Cylinder mass accumulators for the empirical boundary measure nu_omega^N
- Depth-weighted accumulator for the empirical interior mass mu_omega^N

Conventions:
- Generators encoded as integers 0..3 mapped to {a, b, b^-1, a^-1}
- Generator g has inverse: 0<->3, 1<->2 (so g and inv[g] cancel under free reduction)
- The walk's current state is a reduced word stored as a list of integers (the stack)

Author: Claude (Anthropic), May 2026, for the ASD-Phantom connection program.
This is a clean reimplementation following the ASD theory documents; if the
user's own asd_core.py exists, prefer that for production work.
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Optional


# Generator labels: 0=a, 1=b, 2=b^-1, 3=a^-1
# Inverse map: 0<->3, 1<->2
INV = np.array([3, 2, 1, 0], dtype=np.int8)
N_GEN = 4


def block_local_ordinal_quartile_encode(
    signal: np.ndarray,
    block_size: int,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    """
    Block-local ordinal quartile encoding (ASD §CC1 Level 2).

    Partitions `signal` into consecutive blocks of size `block_size`
    (must be divisible by 4). Within each block, ranks the values from
    smallest to largest and assigns each value a quartile index in {0,1,2,3}.

    Quartile -> generator mapping (cyclic to avoid bias):
        Q0 -> 0 (a),  Q1 -> 1 (b),  Q2 -> 2 (b^-1),  Q3 -> 3 (a^-1)

    Returns a sequence of integers in {0,1,2,3} of length
        (len(signal) // block_size) * block_size

    Ties are broken with infinitesimal jitter from `rng` (default: fresh RNG).
    """
    if block_size % 4 != 0:
        raise ValueError(f"block_size must be divisible by 4, got {block_size}")
    if rng is None:
        rng = np.random.default_rng()

    n_full_blocks = len(signal) // block_size
    if n_full_blocks == 0:
        return np.array([], dtype=np.int8)

    truncated = signal[: n_full_blocks * block_size]
    # Add tiny jitter to break ties deterministically per block
    jittered = truncated + rng.normal(0, 1e-12, size=truncated.shape)
    blocks = jittered.reshape(n_full_blocks, block_size)

    # Within each block, rank values: argsort gives indices that sort,
    # then we need rank of each position, which is argsort of argsort.
    ranks = np.argsort(np.argsort(blocks, axis=1), axis=1)
    # Map ranks to quartiles: integer division by (block_size // 4)
    quartile_size = block_size // 4
    quartiles = ranks // quartile_size  # values in {0,1,2,3}

    # Quartiles map directly to generators
    return quartiles.astype(np.int8).flatten()


@dataclass
class WalkState:
    """Current state of the F_2 walk."""
    stack: list  # list of generator indices in {0,1,2,3}, the reduced word
    cancellation_steps: list  # step indices at which cancellation occurred

    @property
    def depth(self) -> int:
        return len(self.stack)


def free_reduction_step(state: WalkState, g: int, step: int) -> bool:
    """
    Apply one generator g to the walk. Returns True if cancellation occurred.

    If the top of the stack is the inverse of g, pop (cancellation).
    Otherwise, push g (extension).
    """
    if state.stack and state.stack[-1] == INV[g]:
        state.stack.pop()
        state.cancellation_steps.append(step)
        return True
    else:
        state.stack.append(int(g))
        return False


@dataclass
class EmpiricalPair:
    """
    The empirical pair (nu_omega^N, mu_omega^N) on the cylinder algebra of
    partial F_2.

    nu_cylinders[k][prefix_tuple] = empirical boundary measure of cylinder C(prefix)
        at depth k. prefix_tuple is a tuple of generator indices of length k.

    mu_cylinders[k][prefix_tuple] = depth-weighted measure (mass weighted by
        the depth at which the walk visited C(prefix)).

    depth_visits[k] = number of steps at which the walk had stack depth >= k
        (basis for D(k)).

    cancellation_steps = step indices where free reduction occurred.

    n_steps = total number of generator-consumption steps.
    """
    n_steps: int
    nu_cylinders: list  # nu_cylinders[k] is dict[tuple, int] of visit counts
    mu_cylinders: list
    depth_visits: np.ndarray  # depth_visits[k] = count of steps with depth >= k
    cancellation_steps: list
    max_depth_tracked: int


def asd_walk(
    encoded: np.ndarray,
    max_depth_tracked: int = 8,
) -> EmpiricalPair:
    """
    Run the F_2 walk on an encoded generator sequence and accumulate the
    empirical pair.

    Args:
        encoded: array of generator indices in {0,1,2,3}, length N
        max_depth_tracked: track cylinder masses up to this depth

    Returns: EmpiricalPair
    """
    n = len(encoded)
    state = WalkState(stack=[], cancellation_steps=[])

    nu_cylinders = [dict() for _ in range(max_depth_tracked + 1)]
    mu_cylinders = [dict() for _ in range(max_depth_tracked + 1)]
    depth_visits = np.zeros(max_depth_tracked + 1, dtype=np.int64)

    for step in range(n):
        g = int(encoded[step])
        free_reduction_step(state, g, step)

        d = state.depth
        # Track depth visits
        for k in range(min(d, max_depth_tracked) + 1):
            depth_visits[k] += 1

        # Track cylinder visits at each depth
        for k in range(1, min(d, max_depth_tracked) + 1):
            prefix = tuple(state.stack[:k])
            nu_cylinders[k][prefix] = nu_cylinders[k].get(prefix, 0) + 1
            # mu weighted by current depth (interior mass)
            mu_cylinders[k][prefix] = mu_cylinders[k].get(prefix, 0) + d

    return EmpiricalPair(
        n_steps=n,
        nu_cylinders=nu_cylinders,
        mu_cylinders=mu_cylinders,
        depth_visits=depth_visits,
        cancellation_steps=state.cancellation_steps,
        max_depth_tracked=max_depth_tracked,
    )


def harmonic_measure_at_depth(k: int) -> float:
    """
    The harmonic measure lambda(C(w)) for a non-trivial reduced word w of
    length k on F_2.

    For k=0: 1 (the whole boundary).
    For k=1: each first-letter cylinder has mass 1/4 (4 generators).
    For k>=2: lambda(C(w)) = (1/4) * (1/3)^(k-1) for any reduced w of length k.
        (At depth 1: 4 cylinders. At each subsequent depth: each cylinder
        splits into 3 valid extensions, since one extension would be a
        cancellation.)
    """
    if k == 0:
        return 1.0
    return 0.25 * (1.0 / 3.0) ** (k - 1)


def harmonic_measure_dict(k: int) -> dict:
    """
    Return a dict mapping every reduced word of length k (as a tuple) to
    its harmonic measure.

    This is uniform across all reduced words of length k.
    """
    if k == 0:
        return {(): 1.0}
    if k == 1:
        return {(g,): 0.25 for g in range(N_GEN)}
    # Enumerate all reduced words of length k
    words = []
    def extend(prefix):
        if len(prefix) == k:
            words.append(tuple(prefix))
            return
        last = prefix[-1] if prefix else None
        for g in range(N_GEN):
            if last is not None and INV[last] == g:
                continue
            prefix.append(g)
            extend(prefix)
            prefix.pop()
    extend([])
    mass = 0.25 * (1.0 / 3.0) ** (k - 1)
    return {w: mass for w in words}


# ----------------------------------------------------------------------------
# Convenience: encode and walk in one call
# ----------------------------------------------------------------------------

def encode_and_walk(
    signal: np.ndarray,
    block_size: int = 4,
    max_depth_tracked: int = 8,
    rng: Optional[np.random.Generator] = None,
) -> EmpiricalPair:
    """End-to-end: real signal -> empirical pair."""
    encoded = block_local_ordinal_quartile_encode(signal, block_size, rng)
    return asd_walk(encoded, max_depth_tracked)
