"""
Verify the second-order expansion of e-projection from uniform reference.

Claim: pi_lambda = pi_0 + lambda * pi_0 * r_tilde
                       + (lambda^2 / 2) * pi_0 * (r_tilde^2 - E_pi0[r_tilde^2])
                       + O(lambda^3)

where r_tilde = r - E_pi0[r].

Test by computing pi_lambda exactly for small lambda and comparing to the
predicted Taylor expansion order by order.
"""
import numpy as np

N = 16
np.random.seed(0)
reward = np.random.randn(N)
pi_0 = np.ones(N) / N
r_tilde = reward - reward.mean()  # centered, since pi_0 is uniform


def pi_lambda(lam):
    L = lam * reward
    L -= L.max()
    p = pi_0 * np.exp(L)
    p /= p.sum()
    return p


# Predicted expansion
def pred_first_order(lam):
    return pi_0 + lam * pi_0 * r_tilde


def pred_second_order(lam):
    var_r = (pi_0 * r_tilde ** 2).sum()
    return pi_0 + lam * pi_0 * r_tilde + (lam ** 2 / 2) * pi_0 * (r_tilde ** 2 - var_r)


print(f"{'lambda':>10} {'||exact-1st||':>14} {'||exact-2nd||':>14} {'1st/lam^2':>12} {'2nd/lam^3':>12}")
for lam in [0.01, 0.03, 0.1, 0.3]:
    exact = pi_lambda(lam)
    err1 = np.linalg.norm(exact - pred_first_order(lam))
    err2 = np.linalg.norm(exact - pred_second_order(lam))
    # Check leading-order scaling
    print(f"{lam:>10.4f} {err1:>14.6e} {err2:>14.6e} {err1/lam**2:>12.4f} {err2/lam**3:>12.4f}")

# If the expansion is correct:
#  - err1 / lam^2 should converge to a constant as lam -> 0
#  - err2 / lam^3 should converge to a constant as lam -> 0
print()
print("If expansion is correct, the rightmost two columns should each converge")
print("to a constant as lambda decreases. (err1/lam^2 and err2/lam^3 stable.)")

# Direction check: is the second-order term parallel to centered reward?
print()
print("Direction check: cosine between second-order term and pi_0 * r_tilde")
var_r = (pi_0 * r_tilde ** 2).sum()
second_order_term = pi_0 * (r_tilde ** 2 - var_r)
first_order_term = pi_0 * r_tilde
cos = (second_order_term @ first_order_term) / (
    np.linalg.norm(second_order_term) * np.linalg.norm(first_order_term)
)
print(f"  cos(second-order, first-order) = {cos:.6f}")
print(f"  (Not parallel: second-order points in a different direction.)")
