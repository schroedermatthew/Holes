"""
Four-way decomposition under two non-commuting projections.

Setup: P, C orthogonal projections in R^n.  T = PCP|_Range(P) has
eigenvalues beta_j on eigenvectors u_j (orthonormal in Range(P)).

For f = sum_j a_j u_j in Range(P), four objects:
  Retention      |PCf|^2          = sum |a_j|^2 beta_j^2
  Suppression    |Pf - PCf|^2     = sum |a_j|^2 (1-beta_j)^2
  Leakage        |(I-P)Cf|^2      = sum |a_j|^2 beta_j(1-beta_j)
  Total error    |f - Cf|^2       = sum |a_j|^2 (1-beta_j)

Identity: |f - Cf|^2 = |Pf - PCf|^2 + |(I-P)Cf|^2
That is:  (1-beta) = (1-beta)^2 + beta(1-beta)         per mode.

Each object maximized at a different value of beta:
  Retention   at beta=1     (full alignment)
  Suppression at beta=0     (orthogonality)
  Leakage     at beta=0.5   (mid-alignment)
  Total error at beta=0     (orthogonality)
"""
import numpy as np
from pathlib import Path
OUT = Path(__file__).resolve().parent

rng = np.random.default_rng(7)


def random_projection(n, k):
    """Random orthogonal projection of rank k in R^n."""
    A = rng.standard_normal((n, k))
    Q, _ = np.linalg.qr(A)
    return Q @ Q.T


for trial in range(5):
    n = 12
    rank_P = 5
    rank_C = 6

    P = random_projection(n, rank_P)
    C = random_projection(n, rank_C)

    # T = PCP|_Range(P): eigendecomposition restricted to Range(P)
    # First diagonalize P: take columns of an orthonormal basis of Range(P)
    eig_P, V_P = np.linalg.eigh(P)
    range_basis = V_P[:, eig_P > 0.5]   # n x rank_P, columns span Range(P)
    T_in_range = range_basis.T @ C @ range_basis   # rank_P x rank_P, symmetric

    betas, U = np.linalg.eigh(T_in_range)
    eigvecs_in_full = range_basis @ U   # n x rank_P; columns u_j

    # Pick an arbitrary f in Range(P): take random combination of u_j's
    a = rng.standard_normal(rank_P)
    f = eigvecs_in_full @ a

    # The four quantities, computed directly
    Cf = C @ f
    PCf = P @ Cf
    Pf_minus_PCf = f - PCf       # since f in Range(P), Pf = f
    I_minus_P_Cf = Cf - PCf
    f_minus_Cf = f - Cf

    retention = np.linalg.norm(PCf) ** 2
    suppression = np.linalg.norm(Pf_minus_PCf) ** 2
    leakage = np.linalg.norm(I_minus_P_Cf) ** 2
    total_err = np.linalg.norm(f_minus_Cf) ** 2

    # The four formulas in the eigenbasis
    pred_retention = float(np.sum(a ** 2 * betas ** 2))
    pred_suppression = float(np.sum(a ** 2 * (1 - betas) ** 2))
    pred_leakage = float(np.sum(a ** 2 * betas * (1 - betas)))
    pred_total = float(np.sum(a ** 2 * (1 - betas)))

    # Identity check
    identity_residual = total_err - (suppression + leakage)
    formula_residual = pred_total - (pred_suppression + pred_leakage)

    print(f"Trial {trial+1}: betas = {np.round(betas, 3)}")
    print(f"  retention    : direct {retention:.6f}, formula {pred_retention:.6f}  diff {retention-pred_retention:+.2e}")
    print(f"  suppression  : direct {suppression:.6f}, formula {pred_suppression:.6f}  diff {suppression-pred_suppression:+.2e}")
    print(f"  leakage      : direct {leakage:.6f}, formula {pred_leakage:.6f}  diff {leakage-pred_leakage:+.2e}")
    print(f"  total error  : direct {total_err:.6f}, formula {pred_total:.6f}  diff {total_err-pred_total:+.2e}")
    print(f"  identity   |f-Cf|^2 = |Pf-PCf|^2 + |(I-P)Cf|^2 :  residual {identity_residual:+.2e}")
    print(f"  formulas   (1-b) = (1-b)^2 + b(1-b)            :  residual {formula_residual:+.2e}")
    print()

# Visualize the four objects across beta
import matplotlib.pyplot as plt

beta = np.linspace(0, 1, 200)
fig, ax = plt.subplots(figsize=(7.5, 4.5))
ax.plot(beta, beta ** 2, label=r"Retention $\beta^2$", lw=2)
ax.plot(beta, (1 - beta) ** 2, label=r"Suppression $(1-\beta)^2$", lw=2)
ax.plot(beta, beta * (1 - beta), label=r"Leakage $\beta(1-\beta)$", lw=2)
ax.plot(beta, 1 - beta, label=r"Total error $1-\beta$", lw=2, ls="--")
ax.axvline(0.5, color="grey", lw=0.5, ls=":")
ax.axhline(0.25, color="grey", lw=0.5, ls=":")
ax.set_xlabel(r"$\beta = \cos^2\theta$  (squared cosine of principal angle)")
ax.set_ylabel("normalized energy per mode")
ax.set_title("Four objects under two non-commuting projections (per-mode contribution)")
ax.legend(loc="center right", fontsize=10)
ax.grid(alpha=0.3)
ax.text(0.0, 1.02, r"orthogonal", fontsize=9, color="grey", ha="left")
ax.text(1.0, 1.02, r"aligned", fontsize=9, color="grey", ha="right")
ax.text(0.02, 0.96, r"$\theta=\pi/2$", fontsize=8, color="grey")
ax.text(0.93, 0.96, r"$\theta=0$", fontsize=8, color="grey")
plt.tight_layout()
plt.savefig(str(OUT / "four_way_decomposition.png"), dpi=130, bbox_inches="tight")
print(f"Saved figure: {OUT / 'four_way_decomposition.png'}")
