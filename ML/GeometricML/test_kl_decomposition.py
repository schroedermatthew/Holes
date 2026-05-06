"""
Test whether the §2.2 decomposition is correct.

Claim was:
  D(pi_true || pi*) = D(pi_true || pi_T*) + D(pi_T* || pi*)
where:
  pi*    = e-projection of pi_ref onto C (the trained policy)
  pi_T*  = e-projection of pi_true onto C
  C      = {pi : E_pi[r] >= R_0}

Standard Pythagorean is:
  For pi in M (with M m-flat) and pi_0 outside, pi^star = e-proj_M(pi_0):
    D(pi || pi_0) = D(pi || pi^star) + D(pi^star || pi_0)

This says: for any pi in C, the KL from pi to a fixed outside point pi_0
decomposes Pythagorean-style with respect to pi_0's projection pi^star.

So if we set pi_0 = pi_ref and pi = pi_true (wait — pi_true must be in C for this).
If pi_true is NOT in C, this Pythagorean does not apply directly.

The decomposition I wrote (§2.2) takes pi = pi_true (NOT in C) and tries to
decompose D(pi_true || pi*) where pi* is in C, by introducing pi_T* (e-proj
of pi_true onto C). This is a different statement and needs separate justification.

Let me check numerically: is
  D(pi_true || pi*)  ?=  D(pi_true || pi_T*) + D(pi_T* || pi*)
true, or is there a cross-term?
"""
import numpy as np


def kl(p, q):
    return float(np.sum(p * (np.log(p + 1e-30) - np.log(q + 1e-30))))


def e_project(pi_0, reward, R_0, tol=1e-12):
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


N = 16
np.random.seed(7)
reward = np.linspace(-1, 1, N)

# Random truth on the simplex
pi_true_logits = np.random.randn(N)
pi_true = np.exp(pi_true_logits); pi_true /= pi_true.sum()

# Reference uniform
pi_ref = np.ones(N) / N

print(f"Truth reward: {pi_true @ reward:.4f}")
print(f"Reference reward: {pi_ref @ reward:.4f}")
print()

print("=" * 78)
print("Test the §2.2 decomposition for various R_0 (constraint severities)")
print("=" * 78)
print()

print(f"{'R_0':>6} {'D(t||pi*)':>12} {'D(t||pi_T*)':>14} {'D(pi_T*||pi*)':>16} "
      f"{'sum':>10} {'residual':>14}")

for R_0 in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]:
    if R_0 <= pi_true @ reward:
        continue  # we want truth to violate constraint

    # Trained policy (e-proj of reference)
    pi_star, lam_star = e_project(pi_ref, reward, R_0)

    # Truth's projection onto constraint (e-proj of truth)
    pi_T_star, lam_T = e_project(pi_true, reward, R_0)

    D_truth_to_star = kl(pi_true, pi_star)
    D_truth_to_T = kl(pi_true, pi_T_star)
    D_T_to_star = kl(pi_T_star, pi_star)

    sum_decomp = D_truth_to_T + D_T_to_star
    residual = D_truth_to_star - sum_decomp

    print(f"{R_0:>6.2f} {D_truth_to_star:>12.4f} {D_truth_to_T:>14.4f} "
          f"{D_T_to_star:>16.4f} {sum_decomp:>10.4f} {residual:>+14.4f}")

print()
print("If §2.2 (ddagger) is correct, residual should be 0 (within numerical precision).")
print("Nonzero residual means there is a cross-term, and the decomposition as written is wrong.")
print()

# Now check what the correct decomposition is.
# Standard Pythagorean for e-projection onto m-flat C:
#   For any pi' in C: D(pi' || pi_0) = D(pi' || pi^*) + D(pi^* || pi_0)
#   where pi^* = e-proj_C(pi_0).
# Apply with pi' = pi_T_star (in C) and pi_0 = pi_ref:
#   D(pi_T_star || pi_ref) =? D(pi_T_star || pi_star) + D(pi_star || pi_ref)
# This should hold, because pi_T_star is in C and pi_star = e-proj_C(pi_ref).

print("=" * 78)
print("Check the correct Pythagorean identity for the right setup:")
print("D(pi_T* || pi_ref) =? D(pi_T* || pi*) + D(pi* || pi_ref)")
print("(Both pi_T* and pi* are in C, with pi* = e-proj_C(pi_ref).)")
print("=" * 78)
print()

print(f"{'R_0':>6} {'D(T||ref)':>12} {'D(T||*)+D(*||ref)':>20} {'residual':>14}")

for R_0 in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]:
    if R_0 <= pi_true @ reward:
        continue
    pi_star, _ = e_project(pi_ref, reward, R_0)
    pi_T_star, _ = e_project(pi_true, reward, R_0)

    lhs = kl(pi_T_star, pi_ref)
    rhs = kl(pi_T_star, pi_star) + kl(pi_star, pi_ref)
    print(f"{R_0:>6.2f} {lhs:>12.4f} {rhs:>20.4f} {lhs-rhs:>+14.4e}")

print()
print("This Pythagorean should hold to machine precision — pi_T* is in C, pi* = e-proj_C(pi_ref).")
