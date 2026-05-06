"""
Diagnostic test + robustness sweep
===================================

Tests two things:

(A) Diagnostic claim from §4.5: in aligned regimes, removing one of
    (filter, constraint) leaves most of the distortion intact, so the
    user can't reverse-engineer which mechanism is operative.

    Concretely: compute D(pi_true || pi_X) for X in
        {pi_combined, pi_filter_only, pi_constraint_only, pi_ref}
    and check whether single-layer-removed configurations are close to
    pi_combined or close to pi_ref.

(B) Robustness of the alignment ordering: does aligned <= orthogonal
    <= anti-aligned hold across:
      - different filter sizes
      - different truth structures
      - different reward shapes
"""
import numpy as np

# ---------- Core machinery ----------

def make_truth(N_X, N_Y, kind="gaussian_shift", seed=0):
    rng = np.random.default_rng(seed)
    logits = np.zeros((N_X, N_Y))
    if kind == "gaussian_shift":
        for x in range(N_X):
            center = (x / (N_X - 1)) * (N_Y - 1)
            for y in range(N_Y):
                logits[x, y] = -((y - center) ** 2) / 2.0
    elif kind == "bimodal":
        for x in range(N_X):
            c1 = 1.5
            c2 = N_Y - 2.5
            w = (x / (N_X - 1))
            for y in range(N_Y):
                logits[x, y] = np.log(
                    (1 - w) * np.exp(-((y - c1) ** 2) / 2.0)
                    + w * np.exp(-((y - c2) ** 2) / 2.0)
                    + 1e-10
                )
    elif kind == "noisy":
        for x in range(N_X):
            center = (x / (N_X - 1)) * (N_Y - 1) + rng.normal(0, 0.5)
            for y in range(N_Y):
                logits[x, y] = -((y - center) ** 2) / 2.0 + rng.normal(0, 0.3)
    elif kind == "antipodal":
        # Truth varies sharply with x in alternating fashion
        for x in range(N_X):
            if x % 2 == 0:
                center = 1.0
            else:
                center = N_Y - 2.0
            for y in range(N_Y):
                logits[x, y] = -((y - center) ** 2) / 2.0
    logits -= logits.max(axis=1, keepdims=True)
    p = np.exp(logits)
    p /= p.sum(axis=1, keepdims=True)
    return p


def make_reward(N_Y, kind="linear"):
    if kind == "linear":
        return (np.arange(N_Y) - (N_Y - 1) / 2) / ((N_Y - 1) / 2)
    elif kind == "quadratic":
        # Encourages outputs near the middle? No, encourages extreme values
        x = (np.arange(N_Y) - (N_Y - 1) / 2) / ((N_Y - 1) / 2)
        return x ** 2 - 0.5
    elif kind == "step":
        # Reward 1 if y >= N_Y/2, -1 otherwise
        return (np.arange(N_Y) >= N_Y / 2).astype(float) * 2 - 1
    elif kind == "exp":
        # Heavy preference for high y
        v = np.exp(np.arange(N_Y) / N_Y * 3)
        v -= v.mean()
        v /= v.std()
        return v


def e_project(pi_0, reward, R_0, tol=1e-12, max_iter=400):
    def policy_at(lam):
        L = np.log(pi_0 + 1e-30) + lam * reward[None, :]
        L -= L.max(axis=1, keepdims=True)
        p = np.exp(L); p /= p.sum(axis=1, keepdims=True)
        return p
    def avg_r(lam):
        return policy_at(lam).mean(axis=0) @ reward
    if avg_r(0) >= R_0:
        return policy_at(0), 0.0
    lo, hi = 0.0, 50.0
    while avg_r(hi) < R_0:
        hi *= 2
        if hi > 1e10:
            return None, None
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        if avg_r(mid) < R_0: lo = mid
        else: hi = mid
        if hi - lo < tol: break
    return policy_at(mid), mid


def kl(p, q):
    return (p * (np.log(p + 1e-30) - np.log(q + 1e-30))).sum(axis=1).mean()


def setup_filters(pi_true, reward, n_filtered, ortho_seed=0):
    truth_r = pi_true @ reward
    idx = np.argsort(truth_r)
    G_aligned = idx[:n_filtered]
    G_anti = idx[-n_filtered:]
    rng = np.random.default_rng(ortho_seed)
    G_ortho = rng.choice(len(pi_true), n_filtered, replace=False)
    return {"aligned": G_aligned, "orthogonal": G_ortho, "anti-aligned": G_anti}


def m_extend(pi_true, pi_ref, mask):
    p = pi_true.copy()
    p[mask] = pi_ref[mask]
    return p


def filter_mask(N_X, G):
    m = np.zeros(N_X, dtype=bool); m[list(G)] = True
    return m


# ============================================================
# (A) Diagnostic claim test
# ============================================================
print("=" * 80)
print("PART A: Diagnostic claim — does removing one layer leave distortion intact?")
print("=" * 80)
print()
print("Setup: aligned filter+constraint, vary R_0.")
print("Comparison: D(pi_true || X) for X in {ref, filter_only, constraint_only, combined}")
print("Plus: D_ratio = (D_combined - D_X_removed) / D_combined")
print("      (close to 0 = removing layer X had little effect")
print("       close to 1 = removing layer X recovered truth fully)")
print()

N_X, N_Y = 16, 8
pi_true = make_truth(N_X, N_Y, "gaussian_shift")
pi_ref = np.ones((N_X, N_Y)) / N_Y
reward = make_reward(N_Y, "linear")
filters = setup_filters(pi_true, reward, n_filtered=N_X // 2)

mask = filter_mask(N_X, filters["aligned"])
pi_filter_only = m_extend(pi_true, pi_ref, mask)

print(f"{'R_0':>6} {'D(t||ref)':>10} {'D(t||filt)':>11} {'D(t||con)':>10} {'D(t||comb)':>11} "
      f"{'rm-filter':>10} {'rm-constraint':>14}")
for R_0 in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
    pi_constraint, _ = e_project(pi_ref, reward, R_0)
    pi_combined, _ = e_project(pi_filter_only, reward, R_0)

    D_ref = kl(pi_true, pi_ref)
    D_filter = kl(pi_true, pi_filter_only)
    D_constraint = kl(pi_true, pi_constraint)
    D_combined = kl(pi_true, pi_combined)

    # rm_filter_change > 0  means D_combined > D_constraint, i.e. removing
    #                         filter REDUCED distortion (filter was hurting).
    # rm_filter_change < 0  means removing filter INCREASED distortion (filter was helping).
    rm_filter_change = D_combined - D_constraint
    rm_constraint_change = D_combined - D_filter

    print(f"{R_0:>6.2f} {D_ref:>10.3f} {D_filter:>11.3f} {D_constraint:>10.3f} "
          f"{D_combined:>11.3f} {rm_filter_change:>+10.3f} {rm_constraint_change:>+14.3f}")

print()
print("Interpretation:")
print("  rm-filter change is the change in distortion when filter is removed (combined -> constraint-only)")
print("  rm-constraint change is when constraint is removed (combined -> filter-only)")
print("  POSITIVE number = removing this layer REDUCED distortion (the layer was hurting)")
print("  NEGATIVE number = removing this layer INCREASED distortion (the layer was helping)")
print()
print("If §4.5 diagnostic claim holds: both numbers should be small in absolute value,")
print("meaning neither single-layer removal recovers the truth (both leave most distortion).")
print()


# ============================================================
# (B) Robustness sweep on the alignment ordering
# ============================================================
print("=" * 80)
print("PART B: Robustness of the alignment ordering")
print("=" * 80)
print()
print("Varying: truth kind, reward kind, filter size n_filt")
print("Testing: does aligned typically have the smallest D_combined? Where does the strict")
print("aligned <= orthogonal <= anti-aligned ordering fail? (Pointwise minimum, mean, median.)")
print()

cases = []
for truth_kind in ["gaussian_shift", "bimodal", "noisy", "antipodal"]:
    for reward_kind in ["linear", "quadratic", "step", "exp"]:
        for n_filt in [4, 6, 8, 10, 12]:
            for R_0_factor in [0.3, 0.5, 0.7]:  # frac of max possible reward
                cases.append((truth_kind, reward_kind, n_filt, R_0_factor))

violations = []
all_orderings = []
n_tested = 0

for truth_kind, reward_kind, n_filt, R_0_factor in cases:
    pi_true = make_truth(N_X, N_Y, truth_kind)
    reward = make_reward(N_Y, reward_kind)
    pi_ref = np.ones((N_X, N_Y)) / N_Y

    # R_0 set as fraction of (max - min) above the reference reward of 0
    max_r = reward.max()
    R_0 = R_0_factor * max_r
    if R_0 <= (pi_ref.mean(axis=0) @ reward) + 0.01:
        continue  # skip if constraint is trivially satisfied or too weak

    filters_d = setup_filters(pi_true, reward, n_filt)

    Ds = {}
    for name, G in filters_d.items():
        mask = filter_mask(N_X, G)
        pi_f = m_extend(pi_true, pi_ref, mask)
        pi_c, _ = e_project(pi_f, reward, R_0)
        if pi_c is None:
            Ds[name] = None
        else:
            Ds[name] = kl(pi_true, pi_c)

    if any(v is None for v in Ds.values()):
        continue

    n_tested += 1
    a, o, an = Ds["aligned"], Ds["orthogonal"], Ds["anti-aligned"]
    ok_aligned_le_ortho = a <= o + 1e-9
    ok_ortho_le_anti = o <= an + 1e-9
    ok_aligned_le_anti = a <= an + 1e-9
    ok_aligned_is_min = (a <= o + 1e-9) and (a <= an + 1e-9)
    if not (ok_aligned_le_ortho and ok_ortho_le_anti):
        violations.append({
            "truth": truth_kind, "reward": reward_kind, "n_filt": n_filt,
            "R_0_factor": R_0_factor, "R_0": R_0,
            "aligned": a, "orthogonal": o, "anti-aligned": an,
            "violation": (
                "aligned > orthogonal" if not ok_aligned_le_ortho else "orthogonal > anti-aligned"
            ),
        })
    all_orderings.append((a, o, an, ok_aligned_le_ortho, ok_aligned_le_anti, ok_aligned_is_min))

print(f"Cases tested: {n_tested}")
print(f"Violations of aligned <= orthogonal <= anti-aligned: {len(violations)}")
n_aligned_le_ortho = sum(1 for r in all_orderings if r[3])
n_aligned_le_anti = sum(1 for r in all_orderings if r[4])
n_aligned_is_min = sum(1 for r in all_orderings if r[5])
print(f"  aligned ≤ orthogonal:          {n_aligned_le_ortho}/{n_tested} ({n_tested - n_aligned_le_ortho} violations)")
print(f"  aligned ≤ anti-aligned:        {n_aligned_le_anti}/{n_tested} ({n_tested - n_aligned_le_anti} violations)")
print(f"  aligned is pointwise minimum:  {n_aligned_is_min}/{n_tested} ({n_tested - n_aligned_is_min} violations)")
print()

if violations:
    print("Violations:")
    for v in violations[:10]:  # print first 10
        print(f"  truth={v['truth']}, reward={v['reward']}, n_filt={v['n_filt']}, "
              f"R_0={v['R_0']:.3f}: a={v['aligned']:.3f}, o={v['orthogonal']:.3f}, "
              f"an={v['anti-aligned']:.3f} ({v['violation']})")
    if len(violations) > 10:
        print(f"  ... ({len(violations) - 10} more)")
else:
    print("Alignment ordering held in all cases tested.")

print()
# Compute summary statistics
all_arr = np.array([(r[0], r[1], r[2]) for r in all_orderings])  # shape (n, 3)
print(f"Mean D_combined across cases:")
print(f"  aligned:      {all_arr[:, 0].mean():.3f} +/- {all_arr[:, 0].std():.3f}")
print(f"  orthogonal:   {all_arr[:, 1].mean():.3f} +/- {all_arr[:, 1].std():.3f}")
print(f"  anti-aligned: {all_arr[:, 2].mean():.3f} +/- {all_arr[:, 2].std():.3f}")
print()
print(f"Median ratio anti-aligned / aligned: {np.median(all_arr[:, 2] / all_arr[:, 0]):.3f}")
print(f"Median ratio orthogonal / aligned:    {np.median(all_arr[:, 1] / all_arr[:, 0]):.3f}")
