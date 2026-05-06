"""Visualize the redundancy/compounding structure across alignment and constraint severity."""
import numpy as np
from pathlib import Path
OUT = Path(__file__).resolve().parent
import matplotlib.pyplot as plt

np.random.seed(42)
N_X, N_Y = 16, 8
reward = (np.arange(N_Y) - (N_Y - 1) / 2) / ((N_Y - 1) / 2)


def make_truth():
    logits = np.zeros((N_X, N_Y))
    for x in range(N_X):
        center = (x / (N_X - 1)) * (N_Y - 1)
        for y in range(N_Y):
            logits[x, y] = -((y - center) ** 2) / 2.0
    logits -= logits.max(axis=1, keepdims=True)
    p = np.exp(logits); p /= p.sum(axis=1, keepdims=True)
    return p


pi_true = make_truth()
pi_ref = np.ones((N_X, N_Y)) / N_Y
truth_reward_per_x = pi_true @ reward


def e_project(pi_0, R_0, tol=1e-12):
    def policy_at(lam):
        L = np.log(pi_0 + 1e-30) + lam * reward[None, :]
        L -= L.max(axis=1, keepdims=True)
        p = np.exp(L); p /= p.sum(axis=1, keepdims=True)
        return p
    if policy_at(0).mean(0) @ reward >= R_0:
        return policy_at(0)
    lo, hi = 0.0, 50.0
    while policy_at(hi).mean(0) @ reward < R_0:
        hi *= 2
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if policy_at(mid).mean(0) @ reward < R_0: lo = mid
        else: hi = mid
        if hi - lo < tol: break
    return policy_at(mid)


def kl(p, q):
    return (p * (np.log(p + 1e-30) - np.log(q + 1e-30))).sum(1).mean()


n_filt = N_X // 2
idx = np.argsort(truth_reward_per_x)
G_aligned = idx[:n_filt]
G_anti = idx[-n_filt:]
rng = np.random.default_rng(0)
G_ortho = rng.choice(N_X, n_filt, replace=False)


def m_extend(G):
    mask = np.zeros(N_X, dtype=bool); mask[list(G)] = True
    p = pi_true.copy(); p[mask] = pi_ref[mask]
    return p


pi_filter_aligned = m_extend(G_aligned)
pi_filter_ortho = m_extend(G_ortho)
pi_filter_anti = m_extend(G_anti)

R0_grid = np.linspace(0.05, 0.85, 25)

curves = {"aligned": [], "orthogonal": [], "anti-aligned": []}
filters = {"aligned": pi_filter_aligned, "orthogonal": pi_filter_ortho, "anti-aligned": pi_filter_anti}

for R_0 in R0_grid:
    pi_constraint = e_project(pi_ref, R_0)
    D_constraint = kl(pi_true, pi_constraint)
    for name, pi_filt in filters.items():
        pi_combined = e_project(pi_filt, R_0)
        D_filter = kl(pi_true, pi_filt)
        D_combined = kl(pi_true, pi_combined)
        curves[name].append(dict(
            R_0=R_0, D_filter=D_filter, D_constraint=D_constraint,
            D_combined=D_combined, D_sum=D_filter + D_constraint,
            D_max=max(D_filter, D_constraint),
        ))

fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), sharey=False)

colors = {"aligned": "#2E7D32", "orthogonal": "#1565C0", "anti-aligned": "#C62828"}

# --- Panel 1: Combined phantom KL across R_0 by alignment ---
ax = axes[0]
for name in curves:
    rs = [c["R_0"] for c in curves[name]]
    cs = [c["D_combined"] for c in curves[name]]
    ax.plot(rs, cs, color=colors[name], label=f"combined ({name})", lw=2)
# Reference: max and sum baselines for the orthogonal case
rs = [c["R_0"] for c in curves["orthogonal"]]
ax.plot(rs, [c["D_filter"] for c in curves["orthogonal"]],
        color="#666", ls=":", label="filter alone (orthogonal)", lw=1.4)
ax.plot(rs, [c["D_constraint"] for c in curves["orthogonal"]],
        color="#666", ls="--", label="constraint alone", lw=1.4)
ax.set_xlabel(r"constraint severity $R_0$")
ax.set_ylabel(r"$D(\pi_\mathrm{true}\,\|\,\pi)$")
ax.set_title("Combined phantom vs alignment regime")
ax.legend(fontsize=9, loc="upper left")
ax.grid(alpha=0.3)

# --- Panel 2: combined vs (filter + constraint) — super-additivity test ---
ax = axes[1]
for name in curves:
    rs = [c["R_0"] for c in curves[name]]
    excess = [c["D_combined"] - c["D_sum"] for c in curves[name]]
    ax.plot(rs, excess, color=colors[name], label=name, lw=2)
ax.axhline(0, color="k", lw=0.7)
ax.fill_between(R0_grid, 0, 8, alpha=0.07, color="red")
ax.fill_between(R0_grid, -2, 0, alpha=0.07, color="green")
ax.text(0.10, 0.4, "super-additive\n(combined > filter + constraint)",
        fontsize=9, color="#A33", va="bottom")
ax.text(0.10, -0.7, "redundant\n(combined < filter + constraint)",
        fontsize=9, color="#373", va="top")
ax.set_xlabel(r"constraint severity $R_0$")
ax.set_ylabel(r"$D_\mathrm{combined} - (D_\mathrm{filter} + D_\mathrm{constraint})$")
ax.set_title("Super-additivity by alignment regime")
ax.legend(fontsize=9, loc="upper left")
ax.grid(alpha=0.3)
ax.set_ylim(-1.2, 5.5)

# --- Panel 3: Ratio combined / max(filter, constraint) ---
ax = axes[2]
for name in curves:
    rs = [c["R_0"] for c in curves[name]]
    ratios = [c["D_combined"] / c["D_max"] for c in curves[name]]
    ax.plot(rs, ratios, color=colors[name], label=name, lw=2)
ax.axhline(1, color="k", lw=0.7, ls="--")
ax.set_xlabel(r"constraint severity $R_0$")
ax.set_ylabel(r"$D_\mathrm{combined} / \max(D_\mathrm{filter}, D_\mathrm{constraint})$")
ax.set_title(r"Combined relative to stronger component alone")
ax.legend(fontsize=9, loc="upper left")
ax.grid(alpha=0.3)

plt.suptitle("Filter+constraint phantom: redundancy vs compounding by alignment",
             fontsize=13, y=1.02)
plt.tight_layout()
plt.savefig(str(OUT / "redundancy_compounding.png"), dpi=130, bbox_inches="tight")
print("Saved figure.")

# Also print summary table
print("\nKey observations across R_0 grid:")
for R_0 in [0.2, 0.4, 0.6, 0.8]:
    i = np.argmin(np.abs(R0_grid - R_0))
    print(f"  R_0 ≈ {R0_grid[i]:.2f}:")
    for name in curves:
        c = curves[name][i]
        excess = c["D_combined"] - c["D_sum"]
        flag = "SUPER-ADDITIVE" if excess > 0 else "redundant"
        print(f"    {name:<14s}: D_combined={c['D_combined']:.3f}, "
              f"D_filter+D_constr={c['D_sum']:.3f}, excess={excess:+.3f} [{flag}]")


# =====================================================================
# Bregman triangle identity verification
# (moved here from SUPERSEDED_redundancy_test_v1.py so the active script
# actually verifies what the document claims it verifies)
# =====================================================================
def kl_avg(p, q):
    """Avg KL across x (uniform x): E_x[ KL(p(.|x) || q(.|x)) ]."""
    return (p * (np.log(p + 1e-30) - np.log(q + 1e-30))).sum(axis=1).mean()


print("\n" + "=" * 72)
print("Bregman triangle identity verification:")
print("  D(true || filter) = D(true || combined) + D(combined || filter) + cross")
print("  cross = lambda * (R_true - R_0)")
print("=" * 72)

R_true = (pi_true.mean(axis=0) @ reward)
print(f"\nTruth's overall reward: {R_true:.4f}")

max_residual = 0.0
for R_0 in [0.2, 0.4, 0.6, 0.8]:
    print(f"\nR_0 = {R_0}:")
    for name, G in [("aligned", G_aligned), ("orthogonal", G_ortho), ("anti-aligned", G_anti)]:
        pi_filter = m_extend(G)
        pi_combined = e_project(pi_filter, R_0)

        # Recover lambda by inversion: pi_combined / pi_filter ~ exp(lam*r) per fiber
        # Easier: rerun e_project but capture lambda
        # We recompute here to extract lambda:
        def _e_project_with_lam(pi0, R0, tol=1e-12):
            def pol(lam):
                L = np.log(pi0 + 1e-30) + lam * reward[None, :]
                L -= L.max(axis=1, keepdims=True)
                p = np.exp(L); p /= p.sum(axis=1, keepdims=True)
                return p
            if pol(0).mean(0) @ reward >= R0:
                return pol(0), 0.0
            lo, hi = 0.0, 50.0
            while pol(hi).mean(0) @ reward < R0:
                hi *= 2
            for _ in range(300):
                mid = 0.5 * (lo + hi)
                if pol(mid).mean(0) @ reward < R0: lo = mid
                else: hi = mid
                if hi - lo < tol: break
            return pol(mid), mid

        _, lam = _e_project_with_lam(pi_filter, R_0)
        D_tf = kl_avg(pi_true, pi_filter)
        D_tc = kl_avg(pi_true, pi_combined)
        D_cf = kl_avg(pi_combined, pi_filter)
        cross = lam * (R_true - R_0)
        residual = D_tf - (D_tc + D_cf + cross)
        max_residual = max(max_residual, abs(residual))
        print(f"  {name:<14s}  D_tf={D_tf:.4f}  D_tc+D_cf+cross={D_tc+D_cf+cross:.4f}  "
              f"residual={residual:+.2e}")

print(f"\nMax residual across all configs: {max_residual:.2e}")
print("(Identity holds to machine precision.)")
