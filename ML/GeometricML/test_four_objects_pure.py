"""
Correct geometric test of the four objects.

The previous test had a setup mismatch.  The framework's four-object
decomposition is about:

  f in Range(P_Q),  observe P_C f and decompose

But RLHF starts from pi_ref and e-projects onto the constraint:

  e_proj_C(pi_ref):  starts outside Q, moves toward C

These are different geometric setups.  The four-object formulas are
derived for the first one.  The second one needs its own analysis.

To verify the four-object formulas, project a truth-aligned vector onto
a constraint subspace directly.  That means: take truth direction in
Fisher tangent, apply orthogonal projection onto the constraint subspace,
measure the four objects.  Sweep the angle between truth and constraint.

Setup in tangent space at pi_ref (uniform):
  Tangent space:  mean-zero vectors in R^N
  Truth direction:  q_hat = (pi_true - pi_ref) / |...|
  Constraint subspace: span of (reward - mean), 1-dimensional in this toy
  P_C projection: onto constraint subspace

Then for f = q_hat (unit vector in query subspace):
  Q is span(q_hat), so P_Q f = f
  Cf = (f . c_hat) c_hat where c_hat is unit constraint direction
  P_Q (Cf) = ((f.c_hat) c_hat . q_hat) q_hat = (f.c_hat)(c_hat.q_hat) q_hat
                                              = (f.c_hat)^2 q_hat   (since f=q_hat)
  
For unit f = q_hat:  beta = (q_hat . c_hat)^2
  retention   = |P_Q P_C f|^2 = beta^2
  suppression = |P_Q f - P_Q P_C f|^2 = (1 - beta)^2
  leakage     = |(I-P_Q) P_C f|^2 = beta * (1-beta)
  total       = |f - P_C f|^2 = 1 - beta
"""
import numpy as np
from pathlib import Path
OUT = Path(__file__).resolve().parent
import matplotlib.pyplot as plt
import scipy.stats as st


N = 32
pi_ref = np.ones(N) / N

def gauss(N, center, sigma):
    x = np.arange(N)
    p = np.exp(-((x - center) ** 2) / (2 * sigma ** 2))
    return p / p.sum()

truth_center = 8
pi_true = gauss(N, truth_center, 2.5)

d_true = pi_true - pi_ref
q_hat = d_true / np.linalg.norm(d_true)


def make_reward(center, sigma=2.5):
    x = np.arange(N)
    r = np.exp(-((x - center) ** 2) / (2 * sigma ** 2))
    r = r / r.max()
    return r


# Sweep over reward centers
reward_centers = np.linspace(N - 1 - truth_center, truth_center, 60)

results = {"beta": [], "retention": [], "suppression": [], "leakage": [], "total": []}

for rc in reward_centers:
    reward = make_reward(rc)
    r_centered = reward - reward.mean()
    if np.linalg.norm(r_centered) < 1e-10:
        continue
    c_hat = r_centered / np.linalg.norm(r_centered)  # unit constraint direction in tangent

    # f = q_hat (unit vector in query direction)
    f = q_hat.copy()

    # P_C f: projection of f onto span(c_hat)
    PC_f = (f @ c_hat) * c_hat

    # P_Q f = f (since f is in span(q_hat))
    PQ_f = f.copy()

    # P_Q P_C f: projection of PC_f onto span(q_hat)
    PQ_PC_f = (PC_f @ q_hat) * q_hat

    # The four objects
    retention = float(np.linalg.norm(PQ_PC_f) ** 2)
    suppression = float(np.linalg.norm(PQ_f - PQ_PC_f) ** 2)
    leakage = float(np.linalg.norm(PC_f - PQ_PC_f) ** 2)
    total = float(np.linalg.norm(f - PC_f) ** 2)

    # beta = squared cosine of angle between q_hat and c_hat
    cos = float(q_hat @ c_hat)
    beta = cos ** 2  # squared cosine in [0, 1] — the principal-angle convention

    results["beta"].append(beta)
    results["retention"].append(retention)
    results["suppression"].append(suppression)
    results["leakage"].append(leakage)
    results["total"].append(total)


b = np.array(results["beta"])
order = np.argsort(b)
b_sorted = b[order]
b_clip = np.clip(b_sorted, 0, 1)


def fit_scale(measured, predicted):
    measured = np.asarray(measured)
    predicted = np.asarray(predicted)
    return float(measured @ predicted) / float(predicted @ predicted)


def shape_corr(measured, predicted):
    return st.pearsonr(measured, predicted)[0]


fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Four objects: pure-projection setup (f = q_hat, project onto constraint subspace)", fontsize=12)

for ax, key, formula, label, formula_str in [
    (axes[0, 0], "retention", lambda b: b ** 2, "Retention", r"$\beta^2$"),
    (axes[0, 1], "leakage", lambda b: b * (1 - b), "Leakage", r"$\beta(1-\beta)$"),
    (axes[1, 0], "suppression", lambda b: (1 - b) ** 2, "Suppression", r"$(1-\beta)^2$"),
    (axes[1, 1], "total", lambda b: 1 - b, "Total error", r"$1-\beta$"),
]:
    measured = np.array(results[key])[order]
    pred = formula(b_clip)
    r = shape_corr(measured, pred)
    peak = b_sorted[np.argmax(measured)]

    ax.plot(b_sorted, measured, 'o-', color="C0", label="measured")
    ax.plot(b_clip, pred, '--', color="C1", alpha=0.7, label=f"{formula_str} (theory)")
    ax.set_xlabel(r"$\beta = \cos^2\theta \in [0, 1]$")
    ax.set_ylabel(label)
    ax.set_title(f"{label}: peak at β={peak:.3f}, Pearson r={r:.4f}")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(str(OUT / "four_objects_pure.png"), dpi=130, bbox_inches="tight")
print(f"Saved figure: {OUT / 'four_objects_pure.png'}")

print()
print("Pure-projection setup: project unit truth-direction onto 1-D constraint subspace.")
print()
for key, formula, label in [
    ("retention",   lambda b: b ** 2,         "Retention   vs beta^2"),
    ("leakage",     lambda b: b * (1 - b),    "Leakage     vs beta(1-beta)"),
    ("suppression", lambda b: (1 - b) ** 2,   "Suppression vs (1-beta)^2"),
    ("total",       lambda b: 1 - b,          "Total       vs (1-beta)"),
]:
    measured = np.array(results[key])[order]
    pred = formula(b_clip)
    r = shape_corr(measured, pred)
    peak_meas = b_sorted[np.argmax(measured)]
    peak_pred = b_clip[np.argmax(pred)]
    max_dev = float(np.max(np.abs(measured - pred)))
    print(f"  {label}:  peak β meas={peak_meas:+.3f}, peak β pred={peak_pred:+.3f}, "
          f"r={r:+.4f}, max|meas-pred|={max_dev:.2e}")
