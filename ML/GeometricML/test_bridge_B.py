"""
Verify the Bridge B formulas (Fisher-tangent e-projection-from-reference
decomposition).

Setup:
  f = a*q              (truth direction in Fisher tangent at pi_ref)
  g = m*c              (trained displacement, length m along constraint direction)
  q, c unit vectors
  s = q . c            (signed cosine; beta = s^2)

Predicted Bridge B formulas:
  |Pg|^2     = m^2 * s^2          (query output magnitude)
  |f - Pg|^2 = (a - m*s)^2        (query-coordinate error)
  |(I-P)g|^2 = m^2 * (1 - s^2)    (off-query leakage)
  |f - g|^2  = a^2 + m^2 - 2*a*m*s (total tangent error)

where P is orthogonal projection onto span(q).

Recovery: pure-projection laws should be recovered when m = a*s.

Tests:
1. Algebraic verification with random vectors (these are inner-product
   identities given g = mu*c, so they hold to machine precision; the
   non-trivial empirical content is in tests 3 and 4).
2. Recovery of pure-projection laws when m = a*s.
3. e-projection from uniform reference, R_0 fixed, reward direction swept.
   *** Caveat: in this regime |mu| varies by only ~3% while s varies over
   [0.025, 1].  Pearson r ~ 0.996 across the four objects therefore measures
   Bridge B's s-shape at near-fixed mu, not its joint (mu, s) prediction. ***
4. Joint sweep of R_0 and reward direction.  This actually exercises the
   joint dependence on (mu, s).  Reports Pearson r, regression slope of
   measured vs predicted, and relative-error percentiles.
"""
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent

# =========================================================================
# Test 1: Algebraic verification.  Take f = a*q, g = m*c with q,c unit.
# Verify the four formulas exactly.
# =========================================================================
print("=" * 78)
print("TEST 1: Bridge B formulas hold algebraically")
print("=" * 78)
print()

rng = np.random.default_rng(42)
n = 16

n_trials = 5
for trial in range(n_trials):
    # Random unit vectors q, c
    q = rng.standard_normal(n); q /= np.linalg.norm(q)
    c = rng.standard_normal(n); c /= np.linalg.norm(c)

    a = float(rng.uniform(0.5, 2.0))
    # mu is the SIGNED displacement coordinate along c; can be negative
    mu = float(rng.uniform(-2.0, 2.0))

    f = a * q
    g = mu * c

    # P = projection onto span(q)
    Pg = (g @ q) * q

    # Direct measurements
    direct = {
        "|Pg|^2":     float(Pg @ Pg),
        "|f-Pg|^2":   float((f - Pg) @ (f - Pg)),
        "|(I-P)g|^2": float((g - Pg) @ (g - Pg)),
        "|f-g|^2":    float((f - g) @ (f - g)),
    }

    # Bridge B predictions
    s = float(q @ c)
    pred = {
        "|Pg|^2":     mu ** 2 * s ** 2,
        "|f-Pg|^2":   (a - mu * s) ** 2,
        "|(I-P)g|^2": mu ** 2 * (1 - s ** 2),
        "|f-g|^2":    a ** 2 + mu ** 2 - 2 * a * mu * s,
    }

    print(f"Trial {trial+1}: a={a:.3f}, mu={mu:+.3f}, s={s:+.3f}, beta={s**2:.3f}")
    for key in direct:
        diff = direct[key] - pred[key]
        print(f"  {key:<14s}  direct={direct[key]:>10.6f}  formula={pred[key]:>10.6f}  diff={diff:+.2e}")
    print()


# =========================================================================
# Test 2: Recovery of pure projection in the special case m = a*s
# =========================================================================
print("=" * 78)
print("TEST 2: Recover pure-projection laws when m = a*s")
print("=" * 78)
print()
print("In the pure-projection setup, g = P_C f = (f.c) c = a*s*c.")
print("So m = a*s.  Substituting into Bridge B formulas:")
print("  |Pg|^2     = (a*s)^2 * s^2     = a^2 * s^4         (= a^2 * beta^2,  retention)")
print("  |f-Pg|^2   = (a - a*s*s)^2     = a^2 * (1-s^2)^2   (= a^2 * (1-beta)^2, suppression)")
print("  |(I-P)g|^2 = (a*s)^2 * (1-s^2) = a^2 * s^2(1-s^2)  (= a^2 * beta(1-beta), leakage)")
print("  |f-g|^2    = a^2 + a^2*s^2 - 2*a*a*s*s = a^2(1-s^2) (= a^2 * (1-beta), total)")
print()
print("These are exactly the four-object pure-projection laws.")
print("Bridge B reduces to the pure-projection algebra at mu = a*s")
print("(where mu is the SIGNED displacement coordinate; mu = a*s can be negative when s<0).")
print()

# Numerical verification of recovery using signed mu coordinate
for s_val in [-0.3, 0.0, 0.3, 0.5, 0.7, 0.9]:
    a = 1.0
    mu = a * s_val   # the recovery condition; signed (can be negative)

    # Algebraic ratios
    bridge_B_ret = mu ** 2 * s_val ** 2
    bridge_B_supp = (a - mu * s_val) ** 2
    bridge_B_leak = mu ** 2 * (1 - s_val ** 2)
    bridge_B_total = a ** 2 + mu ** 2 - 2 * a * mu * s_val

    pure_ret = a ** 2 * (s_val ** 2) ** 2
    pure_supp = a ** 2 * (1 - s_val ** 2) ** 2
    pure_leak = a ** 2 * (s_val ** 2) * (1 - s_val ** 2)
    pure_total = a ** 2 * (1 - s_val ** 2)

    print(f"  s={s_val:+.2f} (beta={s_val**2:.2f}, mu=a*s={mu:+.2f}):")
    print(f"    query-energy: bridge B = {bridge_B_ret:.4f},  pure = {pure_ret:.4f},  diff = {bridge_B_ret-pure_ret:+.2e}")
    print(f"    query-error:  bridge B = {bridge_B_supp:.4f},  pure = {pure_supp:.4f},  diff = {bridge_B_supp-pure_supp:+.2e}")
    print(f"    leakage:      bridge B = {bridge_B_leak:.4f},  pure = {pure_leak:.4f},  diff = {bridge_B_leak-pure_leak:+.2e}")
    print(f"    total:        bridge B = {bridge_B_total:.4f},  pure = {pure_total:.4f},  diff = {bridge_B_total-pure_total:+.2e}")
print()


# =========================================================================
# Test 3: Empirical verification with actual e-projection from uniform reference.
# =========================================================================
print("=" * 78)
print("TEST 3: Bridge B with actual e-projection from uniform reference")
print("=" * 78)
print()
print("Sweep alignment of reward direction relative to truth direction.")
print("Compute pi_trained = e-proj of pi_ref onto constraint, in Fisher tangent.")
print("Measure mu = g @ c_hat (signed displacement coordinate along constraint direction).")
print("Compare measured |Pg|^2, |f-Pg|^2, |(I-P)g|^2, |f-g|^2")
print("against Bridge B predictions using a, mu, s.")
print()


def kl(p, q):
    return float(np.sum(p * (np.log(p + 1e-30) - np.log(q + 1e-30))))


def e_project(pi_0, reward, R_0, tol=1e-12):
    def policy(lam):
        L = np.log(pi_0 + 1e-30) + lam * reward
        L -= L.max()
        p = np.exp(L); p /= p.sum()
        return p
    if policy(0) @ reward >= R_0:
        return policy(0)
    lo, hi = 0.0, 50.0
    while policy(hi) @ reward < R_0:
        hi *= 2
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if policy(mid) @ reward < R_0: lo = mid
        else: hi = mid
        if hi - lo < tol: break
    return policy(mid)


N = 32
pi_ref = np.ones(N) / N

def gauss(N, center, sigma):
    x = np.arange(N)
    p = np.exp(-((x - center) ** 2) / (2 * sigma ** 2))
    return p / p.sum()


truth_center = 8
pi_true = gauss(N, truth_center, 2.5)

# Fisher tangent quantities at uniform reference
d_true = pi_true - pi_ref
a = float(np.linalg.norm(d_true))
q_hat = d_true / a   # unit truth direction


def make_reward(center, sigma=2.5):
    x = np.arange(N)
    r = np.exp(-((x - center) ** 2) / (2 * sigma ** 2))
    return r / r.max()


reward_centers = np.linspace(N - 1 - truth_center, truth_center, 50)
R_0 = 0.5

results = {"s": [], "mu": [], "Pg2_meas": [], "Pg2_pred": [],
           "fPg_meas": [], "fPg_pred": [],
           "leak_meas": [], "leak_pred": [],
           "total_meas": [], "total_pred": []}

for rc in reward_centers:
    reward = make_reward(rc)
    r_centered = reward - reward.mean()
    if np.linalg.norm(r_centered) < 1e-10:
        continue
    c_hat = r_centered / np.linalg.norm(r_centered)

    # e-project
    pi_trained = e_project(pi_ref, reward, R_0)
    g = pi_trained - pi_ref

    # mu is the SIGNED component of g along c_hat (signed displacement coordinate).
    # In the first-order Bridge B regime g = mu*c_hat exactly; in finite simplex
    # there's also a perpendicular second-order component.
    mu = float(g @ c_hat)
    g_perp_c = g - mu * c_hat
    parallel_fraction = (mu ** 2) / max(g @ g, 1e-30)

    # Signed cosine between truth direction and constraint direction
    s = float(q_hat @ c_hat)

    # f = a*q_hat, the truth direction at full magnitude
    f = a * q_hat

    # Direct measurements (treating g as the actual displacement)
    Pg = (g @ q_hat) * q_hat  # projection of g onto truth direction
    Pg2_meas = float(Pg @ Pg)
    fPg_meas = float((f - Pg) @ (f - Pg))
    leak_meas = float((g - Pg) @ (g - Pg))
    total_meas = float((f - g) @ (f - g))

    # Bridge B predictions assuming g = mu*c_hat (first-order tangent model)
    Pg2_pred = mu ** 2 * s ** 2
    fPg_pred = (a - mu * s) ** 2
    leak_pred = mu ** 2 * (1 - s ** 2)
    total_pred = a ** 2 + mu ** 2 - 2 * a * mu * s

    results["s"].append(s)
    results["mu"].append(mu)
    results["Pg2_meas"].append(Pg2_meas)
    results["Pg2_pred"].append(Pg2_pred)
    results["fPg_meas"].append(fPg_meas)
    results["fPg_pred"].append(fPg_pred)
    results["leak_meas"].append(leak_meas)
    results["leak_pred"].append(leak_pred)
    results["total_meas"].append(total_meas)
    results["total_pred"].append(total_pred)

import scipy.stats as st

def corr(a, b):
    return st.pearsonr(np.asarray(a), np.asarray(b))[0]

print(f"  Bridge B prediction vs measured (in Fisher tangent):")
print(f"    |Pg|^2       Pearson r = {corr(results['Pg2_meas'], results['Pg2_pred']):.6f}")
print(f"    |f-Pg|^2     Pearson r = {corr(results['fPg_meas'], results['fPg_pred']):.6f}")
print(f"    |(I-P)g|^2   Pearson r = {corr(results['leak_meas'], results['leak_pred']):.6f}")
print(f"    |f-g|^2      Pearson r = {corr(results['total_meas'], results['total_pred']):.6f}")
print()

# Maximum absolute deviation
for key, label in [("Pg2", "|Pg|^2"), ("fPg", "|f-Pg|^2"),
                    ("leak", "|(I-P)g|^2"), ("total", "|f-g|^2")]:
    meas = np.array(results[f"{key}_meas"])
    pred = np.array(results[f"{key}_pred"])
    print(f"    {label:<14s} max |diff| = {np.max(np.abs(meas - pred)):.6f}, "
          f"max relative error = {np.max(np.abs(meas - pred) / (np.abs(meas) + 1e-10)):.4f}")

# Plot
sort_idx = np.argsort(results["s"])
s_sorted = np.array(results["s"])[sort_idx]
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Bridge B: e-projection from uniform reference, measured vs. predicted", fontsize=12)

for ax, key, label in [
    (axes[0, 0], "Pg2", r"$|Pg|^2$ (query output magnitude)"),
    (axes[0, 1], "fPg", r"$|f - Pg|^2$ (query-coord error)"),
    (axes[1, 0], "leak", r"$|(I-P)g|^2$ (off-query leakage)"),
    (axes[1, 1], "total", r"$|f - g|^2$ (total tangent error)"),
]:
    meas = np.array(results[f"{key}_meas"])[sort_idx]
    pred = np.array(results[f"{key}_pred"])[sort_idx]
    ax.plot(s_sorted, meas, 'o-', color="C0", label="measured", markersize=4)
    ax.plot(s_sorted, pred, '--', color="C1", alpha=0.7, label="Bridge B prediction")
    ax.set_xlabel(r"$s = q \cdot c$ (signed cosine)")
    ax.set_ylabel(label)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUT / "bridge_B_verification.png", dpi=130, bbox_inches="tight")
print()
print(f"Saved: {OUT / 'bridge_B_verification.png'}")

# Diagnostic: how much does mu actually vary across this sweep?
mu_arr_T3 = np.array(results["mu"])
s_arr_T3 = np.array(results["s"])
print()
print("  *** CAVEAT on Test 3 ***")
print(f"  In this sweep, |mu| varies in [{np.abs(mu_arr_T3).min():.4f}, "
      f"{np.abs(mu_arr_T3).max():.4f}] (ratio {np.abs(mu_arr_T3).max()/np.abs(mu_arr_T3).min():.3f}),")
print(f"  while |s| varies in [{np.abs(s_arr_T3).min():.4f}, "
      f"{np.abs(s_arr_T3).max():.4f}] (ratio {np.abs(s_arr_T3).max()/np.abs(s_arr_T3).min():.1f}).")
print("  The high Pearson r is therefore mostly testing Bridge B's s-shape with mu")
print("  approximately constant, NOT its joint (mu,s) prediction.  See Test 4.")


# =========================================================================
# Test 4: Joint sweep of R_0 and reward direction.
# This actually exercises the (mu, s) joint dependence.
# =========================================================================
print()
print("=" * 78)
print("TEST 4: Bridge B under joint sweep of R_0 and reward direction")
print("=" * 78)
print()
print("Sweep BOTH R_0 in [0.2, 0.85] AND reward direction.  This varies mu over")
print("a much wider range (sub-machine-precision through ~0.5), letting us test")
print("Bridge B's joint (mu, s) prediction rather than just its s-shape.")
print()
print("Report: Pearson r (shape), regression slope (magnitude), relative-error")
print("percentiles.  An exact identity would have r=1, slope=1, intercept=0.")
print()

reward_centers_4 = np.linspace(0, N - 1, 20)
R_0_values_4 = np.linspace(0.2, 0.85, 12)

joint = {"s": [], "mu": [],
         "Pg2_meas": [], "Pg2_pred": [],
         "fPg_meas": [], "fPg_pred": [],
         "leak_meas": [], "leak_pred": [],
         "total_meas": [], "total_pred": []}

for rc in reward_centers_4:
    reward = make_reward(rc)
    r_centered = reward - reward.mean()
    if np.linalg.norm(r_centered) < 1e-10:
        continue
    c_hat = r_centered / np.linalg.norm(r_centered)
    s = float(q_hat @ c_hat)

    for R_0_j in R_0_values_4:
        try:
            pi_t = e_project(pi_ref, reward, R_0_j)
        except Exception:
            continue
        g = pi_t - pi_ref
        mu = float(g @ c_hat)
        f = a * q_hat

        Pg = (g @ q_hat) * q_hat
        joint["s"].append(s)
        joint["mu"].append(mu)
        joint["Pg2_meas"].append(float(Pg @ Pg))
        joint["Pg2_pred"].append(mu**2 * s**2)
        joint["fPg_meas"].append(float((f - Pg) @ (f - Pg)))
        joint["fPg_pred"].append((a - mu * s) ** 2)
        joint["leak_meas"].append(float((g - Pg) @ (g - Pg)))
        joint["leak_pred"].append(mu**2 * (1 - s**2))
        joint["total_meas"].append(float((f - g) @ (f - g)))
        joint["total_pred"].append(a**2 + mu**2 - 2 * a * mu * s)


def assess(label, meas, pred):
    meas = np.asarray(meas); pred = np.asarray(pred)
    r = st.pearsonr(meas, pred)[0]
    slope, intercept = np.polyfit(pred, meas, 1)
    rel = np.abs(meas - pred) / np.maximum(np.abs(meas), 1e-6)
    print(f"  {label:>14s}: r={r:+.4f}  slope={slope:+.3f}  "
          f"intercept={intercept:+.4f}  median rel err={np.median(rel):.3f}  "
          f"p90 rel err={np.quantile(rel, 0.90):.3f}")


mu_arr_T4 = np.array(joint["mu"])
s_arr_T4 = np.array(joint["s"])
print(f"  joint sweep: {len(mu_arr_T4)} configurations")
print(f"  |mu| range: [{np.abs(mu_arr_T4).min():.4f}, {np.abs(mu_arr_T4).max():.4f}]   "
      f"(ratio {np.abs(mu_arr_T4).max()/max(np.abs(mu_arr_T4).min(), 1e-10):.0f})")
print(f"  |s|  range: [{np.abs(s_arr_T4).min():.4f}, {np.abs(s_arr_T4).max():.4f}]")
print()
assess("|Pg|^2",     joint["Pg2_meas"],   joint["Pg2_pred"])
assess("|f-Pg|^2",   joint["fPg_meas"],   joint["fPg_pred"])
assess("|(I-P)g|^2", joint["leak_meas"],  joint["leak_pred"])
assess("|f-g|^2",    joint["total_meas"], joint["total_pred"])
print()
print("Slopes deviate from 1 by 15-25% — this is the actual magnitude error")
print("envelope of the first-order Bridge B prediction on real e-projection.")
print("Sign pattern is consistent with the second-order curvature term of §B.5:")
print("  |Pg|^2 over-predicted (slope < 1): perpendicular bend reduces (g.q)^2")
print("                                     vs. (mu*c.q)^2.")
print("  |(I-P)g|^2 under-predicted (slope > 1): actual |g|^2 > mu^2 because g")
print("                                          has perpendicular component.")
print("  |f-g|^2 under-predicted (slope > 1): same reason.")
print()
print("Test 3's reported r ~ 0.996 was the constant-mu artifact; Test 4 is the")
print("actual first-order test, and what it shows is r ~ 0.98 with magnitude")
print("errors of 15-25%.")

# Plot joint-sweep scatter
fig2, axes2 = plt.subplots(2, 2, figsize=(11, 8))
fig2.suptitle("Bridge B Test 4: joint sweep of R_0 and reward direction "
              "(measured vs. predicted)", fontsize=11)
for ax, key, name in [
    (axes2[0, 0], "Pg2",   r"$|Pg|^2$"),
    (axes2[0, 1], "fPg",   r"$|f-Pg|^2$"),
    (axes2[1, 0], "leak",  r"$|(I-P)g|^2$"),
    (axes2[1, 1], "total", r"$|f-g|^2$"),
]:
    meas = np.array(joint[f"{key}_meas"])
    pred = np.array(joint[f"{key}_pred"])
    ax.scatter(pred, meas, alpha=0.4, s=12, color="C0", label="data")
    lim = max(meas.max(), pred.max()) * 1.05
    ax.plot([0, lim], [0, lim], 'k--', alpha=0.6, linewidth=1, label='exact (y=x)')
    slope, intercept = np.polyfit(pred, meas, 1)
    xs = np.linspace(0, lim, 50)
    ax.plot(xs, slope * xs + intercept, '-', color='C3', alpha=0.7,
            linewidth=1.2, label=f'fit (slope={slope:.2f})')
    r = st.pearsonr(meas, pred)[0]
    ax.set_title(f"{name}: r={r:.3f}, slope={slope:.2f}", fontsize=10)
    ax.set_xlabel("Bridge B prediction")
    ax.set_ylabel("measured")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / "bridge_B_joint_sweep.png", dpi=130, bbox_inches="tight")
print()
print(f"Saved: {OUT / 'bridge_B_joint_sweep.png'}")
