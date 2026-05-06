"""
Test the leakage prediction with a proper operationalization.

Previous attempt defined leakage as "probability mass on outputs outside
both truth-support and reward-support."  This is wrong because the
"outside both" region depends on alignment.

Correct operationalization: in the Fisher tangent space at pi_ref (uniform),
the four objects are the components of pi_trained - pi_ref decomposed in
the basis {Q-direction, Q-perp}, where Q-direction is the unit vector
toward pi_true.

For uniform reference, Fisher metric = standard L2 on the simplex tangent
(modulo a scaling factor that drops out).  So:

  d_train  := pi_trained - pi_ref       (mean-zero, lives in tangent at uniform)
  d_true   := pi_true    - pi_ref       (mean-zero, lives in tangent at uniform)
  q        := d_true / |d_true|         (unit query direction)

  retention   := <d_train, q>^2                (component along query)
  leakage     := |d_train|^2 - <d_train, q>^2  (component orthogonal to query)

For suppression and total error, use the actual KL distances; they're
already operationally defined.

Sweep alignment by varying the reward direction.  Beta = (cos angle between
truth and reward in tangent)^2.

Predictions:
  retention   ~ beta^2          peak at beta=1
  leakage     ~ beta(1-beta)    peak at beta=0.5
  suppression ~ (1-beta)^2      peak at beta=0
  total       ~ (1-beta)        peak at beta=0
"""
import numpy as np
import matplotlib.pyplot as plt


def kl(p, q):
    return np.sum(p * (np.log(p + 1e-30) - np.log(q + 1e-30)))


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


# Setup
N = 32
pi_ref = np.ones(N) / N

def gauss(N, center, sigma):
    x = np.arange(N)
    p = np.exp(-((x - center) ** 2) / (2 * sigma ** 2))
    return p / p.sum()


def make_reward(center, sigma_r=2.5):
    x = np.arange(N)
    r = np.exp(-((x - center) ** 2) / (2 * sigma_r ** 2))
    r = r / r.max()
    return r


truth_center = 8
truth_sigma = 2.5
pi_true = gauss(N, truth_center, truth_sigma)


# Truth direction in tangent
d_true = pi_true - pi_ref
d_true_norm = np.linalg.norm(d_true)
q_hat = d_true / d_true_norm  # unit query direction in tangent


def beta_via_tangent(reward):
    """Squared cosine of angle between truth-direction and reward-direction
    in the Fisher tangent (= L2 here, since reference is uniform)."""
    r_centered = reward - reward.mean()
    if np.linalg.norm(r_centered) < 1e-10:
        return 0.0
    cos = (d_true @ r_centered) / (d_true_norm * np.linalg.norm(r_centered))
    return cos ** 2 * np.sign(d_true @ r_centered)


# Sweep
reward_centers = np.linspace(N - 1 - truth_center, truth_center, 60)
R_0 = 0.5

results = {"beta": [], "retention": [], "leakage": [],
           "suppression_kl": [], "total_kl": [],
           "retention_normalized": [], "leakage_normalized": []}

for rc in reward_centers:
    reward = make_reward(rc)
    pi_trained = e_project(pi_ref, reward, R_0)

    d_train = pi_trained - pi_ref
    d_train_norm_sq = float(d_train @ d_train)

    along_q = float(d_train @ q_hat)              # signed scalar
    retention_raw = along_q ** 2                  # squared component along q
    leakage_raw = d_train_norm_sq - retention_raw # squared component orthogonal to q

    # Normalize by |d_train|^2 so we get fractions in [0,1]
    if d_train_norm_sq > 1e-12:
        ret_frac = retention_raw / d_train_norm_sq
        leak_frac = leakage_raw / d_train_norm_sq
    else:
        ret_frac = 0.0
        leak_frac = 0.0

    beta = beta_via_tangent(reward)

    results["beta"].append(beta)
    results["retention"].append(retention_raw)
    results["leakage"].append(leakage_raw)
    results["retention_normalized"].append(ret_frac)
    results["leakage_normalized"].append(leak_frac)
    results["suppression_kl"].append(kl(pi_true, pi_trained) - kl(pi_true, pi_ref))  # excess KL from training
    results["total_kl"].append(kl(pi_true, pi_trained))


# Sort by beta for clean plotting
beta_arr = np.array(results["beta"])
order = np.argsort(beta_arr)
b = beta_arr[order]


# Theory predictions, scaled to fit the data
def fit_scale(measured, predicted):
    """Find scale c minimizing |measured - c * predicted|^2."""
    measured = np.asarray(measured)
    predicted = np.asarray(predicted)
    return float(measured @ predicted) / float(predicted @ predicted)


b_clip = np.clip(b, 0, 1)
ret_meas = np.array(results["retention"])[order]
leak_meas = np.array(results["leakage"])[order]
total_meas = np.array(results["total_kl"])[order]

c_ret = fit_scale(ret_meas[b_clip > 0], (b_clip[b_clip > 0]) ** 2)
c_leak = fit_scale(leak_meas[b_clip > 0], b_clip[b_clip > 0] * (1 - b_clip[b_clip > 0]))


fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Four objects in policy space (Fisher-tangent operationalization)", fontsize=12)

ax = axes[0, 0]
ax.plot(b, ret_meas, 'o-', color="C0", label="measured")
ax.plot(b_clip, c_ret * b_clip ** 2, '--', color="C1", alpha=0.7,
        label=fr"$c \cdot \beta^2$, $c={c_ret:.3f}$")
ax.set_xlabel(r"$\beta$ (Fisher-tangent cosine²)")
ax.set_ylabel(r"Retention $\langle \Delta\pi, \hat{q}\rangle^2$")
ax.set_title("Retention")
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

ax = axes[0, 1]
ax.plot(b, leak_meas, 'o-', color="C0", label="measured")
ax.plot(b_clip, c_leak * b_clip * (1 - b_clip), '--', color="C1", alpha=0.7,
        label=fr"$c \cdot \beta(1-\beta)$, $c={c_leak:.3f}$")
ax.set_xlabel(r"$\beta$ (Fisher-tangent cosine²)")
ax.set_ylabel(r"Leakage $\|\Delta\pi - \langle \Delta\pi, \hat{q}\rangle \hat{q}\|^2$")
ax.set_title("Leakage")
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# Suppression: measure as |d_true - <d_train, q_hat> q_hat|^2 along the query direction?
# Cleaner: suppression ~ |Q(pi_true - pi_trained)|^2.
# In tangent at uniform, Q-projection of (pi_true - pi_trained) is
# <pi_true - pi_trained, q_hat> q_hat, and its squared norm is
# (<pi_true, q_hat> - <pi_trained, q_hat>)^2.
# <pi_true, q_hat> = <d_true, q_hat> = |d_true|.
# So suppression = (|d_true| - <d_train, q_hat>)^2.
# Recompute:
suppression = []
for i, rc in enumerate(reward_centers):
    reward = make_reward(rc)
    pi_trained = e_project(pi_ref, reward, R_0)
    d_train = pi_trained - pi_ref
    along = float(d_train @ q_hat)
    suppression.append((d_true_norm - along) ** 2)
supp_meas = np.array(suppression)[order]
c_supp = fit_scale(supp_meas[b_clip < 1], (1 - b_clip[b_clip < 1]) ** 2)

ax = axes[1, 0]
ax.plot(b, supp_meas, 'o-', color="C0", label="measured")
ax.plot(b_clip, c_supp * (1 - b_clip) ** 2, '--', color="C1", alpha=0.7,
        label=fr"$c \cdot (1-\beta)^2$, $c={c_supp:.3f}$")
ax.set_xlabel(r"$\beta$ (Fisher-tangent cosine²)")
ax.set_ylabel(r"Suppression $\|Q(\pi_{\rm true} - \pi_{\rm trained})\|^2$")
ax.set_title("Suppression")
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

ax = axes[1, 1]
c_total = fit_scale(total_meas[b_clip < 1], 1 - b_clip[b_clip < 1])
ax.plot(b, total_meas, 'o-', color="C0", label="measured")
ax.plot(b_clip, c_total * (1 - b_clip), '--', color="C1", alpha=0.7,
        label=fr"$c \cdot (1-\beta)$, $c={c_total:.3f}$")
ax.set_xlabel(r"$\beta$ (Fisher-tangent cosine²)")
ax.set_ylabel(r"Total KL $D(\pi_{\rm true} \| \pi_{\rm trained})$")
ax.set_title("Total error")
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("/mnt/user-data/outputs/four_objects_proper.png", dpi=130, bbox_inches="tight")
print("Saved figure: /mnt/user-data/outputs/four_objects_proper.png")


# Quantitative results
import scipy.stats as st
def shape_corr(measured, formula, betas):
    pred = formula(np.clip(betas, 0, 1))
    return st.pearsonr(measured, pred)[0]


def peak_loc(arr, betas):
    return betas[np.argmax(arr)]


print()
print("Peak locations:")
print(f"  retention   peaks at beta = {peak_loc(ret_meas, b):.3f}  (predicted: 1.0)")
print(f"  leakage     peaks at beta = {peak_loc(leak_meas, b):.3f}  (predicted: 0.5)")
print(f"  suppression peaks at beta = {peak_loc(supp_meas, b):.3f}  (predicted: 0.0)")
print(f"  total       peaks at beta = {peak_loc(total_meas, b):.3f}  (predicted: 0.0)")
print()
print("Shape correlations (Pearson r between measured and predicted formula):")
print(f"  retention   vs beta^2:        r = {shape_corr(ret_meas, lambda b: b**2, b):.4f}")
print(f"  leakage     vs beta(1-beta):  r = {shape_corr(leak_meas, lambda b: b*(1-b), b):.4f}")
print(f"  suppression vs (1-beta)^2:    r = {shape_corr(supp_meas, lambda b: (1-b)**2, b):.4f}")
print(f"  total       vs (1-beta):      r = {shape_corr(total_meas, lambda b: 1-b, b):.4f}")
