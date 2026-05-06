"""
Do the four objects predict the right behavior in the policy-space setting?

Setup:
- Policy on output Y given input x (single x for simplicity)
- Truth pi_true is concentrated in a "query direction" — one specific output
- Reward r encourages outputs in a "constraint direction" — different output
- Vary alignment between query and constraint by adjusting which outputs
  the truth distribution and the reward emphasize
- Train (e-project) reference uniform onto constraint to get pi_trained
- Measure four observable signatures:
    * Retention:   probability mass pi_trained puts on truth-supported outputs
    * Suppression: how much truth-mass got pushed out of truth-supported outputs
    * Leakage:     probability mass pi_trained puts on "neighboring" outputs
                   (outputs that are neither in the truth support nor in the
                   reward-favored set, but appear due to the constraint
                   smearing across non-target dimensions)
    * Total error: KL(pi_true || pi_trained)

Key thing being tested: do these quantities trace the predicted curves
(beta^2, (1-beta)^2, beta(1-beta), 1-beta) as alignment varies?

Definition of beta in this setup: the squared cosine of the angle between
the truth direction and the constraint direction in policy space (with
Fisher metric near the reference). For finite-support distributions where
the reference is uniform, this works out to the Bhattacharyya-coefficient-
squared between the truth distribution and the reward-induced distribution
on the same support, after lifting to log-space.

Concretely, for two pure delta-like distributions on disjoint singleton
supports, beta = 0; for fully aligned, beta = 1.  Linear-mixture interpolation
between these gives intermediate betas.
"""
import numpy as np
import matplotlib.pyplot as plt


def kl(p, q):
    return np.sum(p * (np.log(p + 1e-30) - np.log(q + 1e-30)))


def e_project_to_reward(pi_0, reward, R_0, tol=1e-12):
    """e-projection of pi_0 onto {pi: E_pi[reward] >= R_0}."""
    def policy(lam):
        L = np.log(pi_0 + 1e-30) + lam * reward
        L -= L.max()
        p = np.exp(L); p /= p.sum()
        return p
    if policy(0) @ reward >= R_0:
        return policy(0), 0.0
    lo, hi = 0.0, 50.0
    while policy(hi) @ reward < R_0:
        hi *= 2
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if policy(mid) @ reward < R_0: lo = mid
        else: hi = mid
        if hi - lo < tol: break
    return policy(mid), mid


# Setup:  outputs are 0..N-1.
# Truth: peak at output 0 with sharpness s_t
# Constraint reward: sharpness s_r, peak at output that varies with alignment
# We measure the four quantities in three regions:
#    Q ("truth support"):   outputs near 0
#    C ("reward-favored"):  outputs near peak_r
#    Other ("leakage region"): outputs in neither region
N = 32
sigma = 2.5  # width of "support" in output space


def gauss(N, center, sigma):
    x = np.arange(N)
    p = np.exp(-((x - center) ** 2) / (2 * sigma ** 2))
    return p / p.sum()


# Define query support Q and complement
def support_indicator(center, width=4):
    x = np.arange(N)
    return np.abs(x - center) <= width


# Sweep "alignment" by varying the position of the reward peak
truth_center = N // 4  # 8
truth_dist = gauss(N, truth_center, sigma)
truth_support = support_indicator(truth_center, width=4)

# Reference uniform
pi_ref = np.ones(N) / N

# Reward shapes: localized near reward_center with sigma_r
def make_reward(center, sigma_r=2.5, R_max=0.7):
    """Reward that peaks at `center`, smooth, sums-to-zero shape."""
    x = np.arange(N)
    r = np.exp(-((x - center) ** 2) / (2 * sigma_r ** 2))
    r = r / r.max()  # max value 1
    return r


# Compute principal-angle proxy beta for this setup:
# Use squared cosine of angle between truth and reward in their natural representation
# (here: dot product of normalized vectors).
def compute_beta(truth_dist, reward):
    # Take square root of truth (so it lives in L^2, like an amplitude),
    # and a normalized version of the reward shape after baseline subtraction.
    # In Fisher tangent at uniform, the natural inner product is just
    # sum p_x q_x (see KL second-order Taylor at uniform).
    # For two unit vectors in this metric, beta = (sum p q)^2 / (sum p^2 sum q^2)... 
    # but truth and reward play different roles.  Use the approximation:
    # beta = (sum truth * reward_normalized)^2 / (sum truth^2 sum reward_normalized^2)
    r_centered = reward - reward.mean()
    t_centered = truth_dist - truth_dist.mean()
    if np.linalg.norm(r_centered) < 1e-10 or np.linalg.norm(t_centered) < 1e-10:
        return 0.0
    cos = (t_centered @ r_centered) / (np.linalg.norm(t_centered) * np.linalg.norm(r_centered))
    return cos ** 2 * np.sign(t_centered @ r_centered)


# Sweep reward position from far-from-truth (orthogonal) to coincident-with-truth (aligned)
reward_centers = np.linspace(N - 1 - truth_center, truth_center, 33)  # from 23 down to 8

results = {
    "beta": [],
    "retention": [],   # mass pi_trained puts on truth_support
    "suppression": [], # truth_dist mass on truth_support minus pi_trained mass on truth_support
    "leakage": [],     # mass pi_trained puts outside both truth_support and reward_support
    "total_kl": [],
    "reward_center": [],
}

R_0 = 0.5  # constraint demands E[reward] >= R_0 (reward max = 1)

for rc in reward_centers:
    reward = make_reward(rc)
    reward_support = support_indicator(rc, width=4)

    # Train: e-project uniform onto {E[reward] >= R_0}
    pi_trained, lam = e_project_to_reward(pi_ref, reward, R_0)

    # Measurements
    beta = compute_beta(truth_dist, reward)

    # Mass-on-region quantities (these are the "policy space" analogs of the four objects)
    retention = pi_trained[truth_support].sum()
    truth_mass_in_support = truth_dist[truth_support].sum()  # ~ 1 by construction
    suppression = truth_mass_in_support - retention

    # Leakage region: outside both truth and reward supports
    leakage_region = ~(truth_support | reward_support)
    leakage = pi_trained[leakage_region].sum()

    total_kl_val = kl(truth_dist, pi_trained)

    results["beta"].append(beta)
    results["retention"].append(retention)
    results["suppression"].append(suppression)
    results["leakage"].append(leakage)
    results["total_kl"].append(total_kl_val)
    results["reward_center"].append(rc)


# Sort by beta to plot clean curves
beta_arr = np.array(results["beta"])
order = np.argsort(beta_arr)

fig, axes = plt.subplots(2, 2, figsize=(11, 8))
fig.suptitle(r"Four objects in policy space, varying alignment $\beta$", fontsize=12)

for ax, key, label, predicted in [
    (axes[0, 0], "retention", "Retention (mass on truth support)", lambda b: b ** 2),
    (axes[0, 1], "suppression", "Suppression (truth mass lost from support)", lambda b: (1 - b) ** 2),
    (axes[1, 0], "leakage", "Leakage (mass outside truth and reward supports)", lambda b: b * (1 - b)),
    (axes[1, 1], "total_kl", r"Total KL $D(\pi_{\rm true} \| \pi_{\rm trained})$", None),
]:
    arr = np.array(results[key])[order]
    b = beta_arr[order]
    ax.plot(b, arr, 'o-', color="C0", label="measured")
    if predicted is not None:
        # Scale prediction to match observed range for shape comparison
        pred_curve = predicted(np.clip(b, 0, 1))
        ax.plot(b, pred_curve, '--', color="C1", alpha=0.6, label=f"shape $\\propto$ formula")
    ax.set_xlabel(r"$\beta$ (proxy: squared cos angle between truth & reward)")
    ax.set_ylabel(label)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("/mnt/user-data/outputs/four_objects_policy_space.png", dpi=130, bbox_inches="tight")
print("Saved figure: /mnt/user-data/outputs/four_objects_policy_space.png")
print()


# Print a table
print("=" * 90)
print(f"{'beta':>8} {'reward_c':>10} {'retention':>12} {'suppression':>13} {'leakage':>10} {'total_KL':>10}")
print("-" * 90)
for i in order:
    print(f"{results['beta'][i]:>8.3f} {results['reward_center'][i]:>10.1f} "
          f"{results['retention'][i]:>12.4f} {results['suppression'][i]:>13.4f} "
          f"{results['leakage'][i]:>10.4f} {results['total_kl'][i]:>10.4f}")
print()


# Check peak locations (rough)
def peak_beta(arr, betas):
    valid = ~np.isnan(arr)
    return betas[valid][np.argmax(np.array(arr)[valid])]


def trough_beta(arr, betas):
    valid = ~np.isnan(arr)
    return betas[valid][np.argmin(np.array(arr)[valid])]


print(f"Peak/trough analysis:")
print(f"  retention peak at beta = {peak_beta(results['retention'], beta_arr):+.3f}  "
      f"(predicted: near beta=1)")
print(f"  suppression peak at beta = {peak_beta(results['suppression'], beta_arr):+.3f}  "
      f"(predicted: near beta=0)")
print(f"  leakage peak at beta = {peak_beta(results['leakage'], beta_arr):+.3f}  "
      f"(predicted: near beta=0.5)")
print(f"  total KL peak at beta = {peak_beta(results['total_kl'], beta_arr):+.3f}  "
      f"(predicted: near beta=0)")

# Predicted shape correlations
import scipy.stats as st
def correlate(arr, predicted_shape, betas):
    arr = np.array(arr)
    pred = predicted_shape(np.clip(betas, 0, 1))
    return st.pearsonr(arr, pred)[0]

print()
print(f"Shape correlation (Pearson r between measured and predicted-formula):")
print(f"  retention vs beta^2:        r = {correlate(results['retention'], lambda b: b**2, beta_arr):.4f}")
print(f"  suppression vs (1-beta)^2:  r = {correlate(results['suppression'], lambda b: (1-b)**2, beta_arr):.4f}")
print(f"  leakage vs beta(1-beta):    r = {correlate(results['leakage'], lambda b: b*(1-b), beta_arr):.4f}")
print(f"  total_KL vs (1-beta):       r = {correlate(results['total_kl'], lambda b: 1-b, beta_arr):.4f}")
