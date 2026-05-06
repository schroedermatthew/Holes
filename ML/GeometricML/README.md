# Phantom Framework — Current Output Files

After eleven rounds of correction in conversation. This README lists what's in this directory and what its current status is. The main document `info_geometric_reformulation.md` is the canonical reference; this is just a map.

## Main document

- **`info_geometric_reformulation.md`** — the working document. Includes nine substantive correction rounds (the first seven narrowed the framework, round 8 introduced Bridge B as a derived first-order result, round 9 added the explicit second-order term in the e-projection expansion). Two further rounds (10 and 11) were synchronization/correction passes: round 10 fixed residual sync issues that survived rounds 8–9; round 11 (Claude Opus 4.7) discovered that Bridge B's headline empirical evidence — Test 3's "$r \approx 0.996$" — was a constant-$\mu$ artifact, replaced it with a proper joint sweep, and downgraded the framing of Bridge B from "derivation" to "reorganization." All retractions are explicit in §4.9; structural summary is in Appendix A; the Bridge B reorganization is in Appendix B.

  Read §4.9 first if you want to know what is and isn't currently claimed. Read Appendix B for the Bridge B reorganization (with the round-11 caveats in §B.5 and §B.6). Read Appendix A for the structural skeleton.

## Active verification scripts

All scripts now save outputs to their own directory via `Path(__file__).resolve().parent`, so they're reproducible from any location.

- **`four_way_decomposition.py`** + **`four_way_decomposition.png`** — verifies the four-way algebra ($\beta^2$, $(1-\beta)^2$, $\beta(1-\beta)$, $1-\beta$) on random projection pairs. Identity holds to $10^{-15}$. Cited in §2.3.

- **`test_four_objects.py`** + **`four_objects_sweep.png`** — extended verification with single-mode sweep across $\beta \in [0.001, 0.999]$. Peak locations exact, all four formulas to $10^{-16}$. Cited in §4.8 Test 1.

- **`test_four_objects_pure.py`** + **`four_objects_pure.png`** — applies the four-way formulas to their *proper* geometric setup in policy space (project unit truth-direction onto constraint subspace). All four formulas hold with $r = 1.0000$ and max deviation $\sim 10^{-16}$ across $\beta \in [0,1]$. Cited in §4.8 Test 3. *(Earlier versions reported $r > 0.95$; that was a signed-beta artifact, fixed in round 8.)*

- **`test_bridge_B.py`** + **`bridge_B_verification.png`** + **`bridge_B_joint_sweep.png`** — verifies Bridge B (Appendix B). **Test 1**: algebraic identities exact (to $\sim 10^{-16}$) when $g = \mu c$ assumed — these are inner-product identities given the assumption, so this test verifies the algebra, not the modeling claim. **Test 2**: recovery of pure-projection laws at $\mu = as$, exact. **Test 3** (kept for record, with explicit caveat): Bridge B applied to actual e-projection from uniform reference, $R_0 = 0.5$ fixed, reward direction swept; reports $r \approx 0.996$ but holds $|\mu|$ approximately constant (~3% variation while $|s|$ varies by 39×) and so does not exercise the joint $(\mu, s)$ prediction. **Test 4** (the actual first-order test, *added in round 11*): joint sweep of $R_0 \in [0.2, 0.85]$ and reward direction (240 configurations); $|\mu|$ varies by ~800×; reports shape Pearson $r \approx 0.98$ and regression-slope deviations of 15–25% from 1, with sign pattern consistent with the §B.5 second-order term (over-prediction of query-aligned components, under-prediction of perpendicular components). The 15–25% slope deviation is the actual magnitude-error envelope of Bridge B's first-order prediction on real e-projection.

- **`test_second_order.py`** — verifies the explicit second-order Taylor expansion of the e-projection: $\pi_\lambda = \pi_0 + \lambda\pi_0\tilde r + \frac{\lambda^2}{2}\pi_0(\tilde r^2 - \mathbb{E}_{\pi_0}[\tilde r^2]) + O(\lambda^3)$. Confirms first-order error $\propto \lambda^2$, second-order error $\propto \lambda^3$, and that the second-order direction is non-parallel to the centered reward (cosine 0.157 in test). This identifies the qualitative source of the slope deviations in Test 4 of `test_bridge_B.py`. *Added in round 9.*

- **`visualize_redundancy.py`** + **`redundancy_compounding.png`** — the §IV redundancy/compounding experiment. Bregman triangle to machine precision ($\sim 10^{-13}$ residual); aligned configurations are least-compounding for total error in the toy. *Bregman triangle verification was moved here from `SUPERSEDED_redundancy_test_v1.py` in round 8 so the document's citation matches the script.*

- **`diagnostic_and_robustness.py`** — Part A refutes the v2 diagnostic-indistinguishability claim (§4.6). Part B is the 240-configuration robustness sweep on alignment ordering (§4.5). *Reports corrected in round 8: aligned ≤ orthogonal in 222/240; aligned ≤ anti-aligned in 223/240; aligned is pointwise minimum in 211/240. Earlier "240/240" claim was wrong.*

- **`test_kl_decomposition.py`** — verifies that the §2.2 decomposition I had written is wrong (residuals to 0.55 KL units, sign-changing) and the corrected Pythagorean holds to $10^{-13}$. Cited in §2.2.

## Superseded scripts (kept as record)

- **`SUPERSEDED_redundancy_test_v1.py`** — v1 of the redundancy experiment. Replaced by `visualize_redundancy.py` + `diagnostic_and_robustness.py`, which together cover its content with broader scope. The Bregman triangle residual check that originally lived here has been moved into `visualize_redundancy.py`.

- **`SUPERSEDED_test_four_objects_policy.py`** + **`SUPERSEDED_four_objects_policy_space.png`** — first naive operationalization of the four-way decomposition in policy space, using mass-on-region as the leakage measurement. Failed because the leakage region is itself $\beta$-dependent (§4.8 Test 2). Replaced by Test 3 / `test_four_objects_pure.py`.

- **`SUPERSEDED_test_four_objects_proper.py`** + **`SUPERSEDED_four_objects_proper.png`** — second attempt: Fisher-tangent operationalization, but applied to the e-projection-from-reference setup (which is the wrong geometric setup for the pure-projection formulas — Bridge B is the right setup-specific decomposition). Three of four predictions matched in shape; leakage failed. The failure is informative — it pointed at the setup-mismatch issue that Bridge B addresses.

## The bottom line

The framework as currently established has a correct projection-theoretic core (verified to machine precision), a correct KL projection model for RLHF (also verified), **one** verified non-trivial prediction in KL units (the §IV total-error redundancy result, with the conditional qualifiers of §4.5), and **one** Fisher-tangent reorganization with a quantified magnitude-error envelope (Bridge B: shape Pearson $r \approx 0.98$ on real e-projection, slope deviations 15–25% from 1, with the deviation pattern attributable to the explicit second-order term identified in `test_second_order.py`). The framework gives a qualitative match to the Black Nazi case via Bridge B in the orthogonal-truth regime. Open: full KL-geometry corrections to Bridge B with the second-order term folded in, capacity-bandwidth, multi-reward, eigenstructure rotation, empirical contact with production systems.

Bridge B's distinctive *toy-level* prediction is that off-query leakage in this setup scales with $\mu^2$ (the constraint severity squared), *not* with $\beta(1-\beta)$. **Translating this to a real RLHF system has obstacles that have not been worked out**: real systems use learned reward models with many effective directions rather than a single linear functional; the loss-function KL coefficient does not equal the m-flat constraint severity except at the optimum; "off-query behavior" lacks an operational definition for an LLM; $\mu$ is not directly observable. The toy prediction stands; the production-system test is open.

A note on units: the §IV redundancy result is in KL units (it uses the Bregman triangle with the cross-term $\lambda^*(R_{\text{true}} - R_0)$ at finite KL). Bridge B is in Fisher-tangent units (squared $L^2$ norms in the simplex tangent space at $\pi_{\text{ref}}$). The two results live in different metrics and are not directly comparable; KL ≈ ½ × (Fisher-tangent norm)² holds only to leading order around the diagonal, which the §IV experiment is not in. They sit next to each other rather than reinforcing each other.

## Reading order

1. `info_geometric_reformulation.md` Appendix A (the structural skeleton from round 4).
2. `info_geometric_reformulation.md` §4.9 (the eleven correction rounds — read in order).
3. `info_geometric_reformulation.md` Appendix B with §B.5 and §B.6 in particular (Bridge B, with the round-11 caveats).
4. `info_geometric_reformulation.md` §IV in full (the numerical companion that surfaced most of the issues).
5. The active verification scripts in the order they're cited above. Run `test_bridge_B.py` and read both Test 3 (with caveat) and Test 4 (the actual first-order test).

The pattern across rounds 1–7 was strict narrowing: each round retracted something the framework had been claiming. Round 8 broke the pattern by introducing Bridge B as what looked like a substantive new derivation. Round 9 continued in that direction with the explicit second-order term and a substantial cleanup of overclaims in Part VI. Round 10 was synchronization-only — no new mathematics, just bringing the document into honest correspondence with what the scripts actually do. Round 11 then walked back round 8's framing: the Test 3 evidence presented as "Bridge B's first-order version is solved with $r \approx 0.996$" was a constant-$\mu$ artifact; the actual first-order accuracy on real e-projection is $r \approx 0.98$ on shape with 15–25% magnitude error from the unmodeled second-order term, and Bridge B is more accurately described as a clean reorganization than as a derivation. **The current state has fewer overclaims than at any prior point, including the round-10 state.**

## Retracted along the way

- "Universal energy law $\beta(1-\beta)$ governs phantom magnitude" — the formula is the leakage law for one object among four.
- "Aligned filter+constraint compounds super-additively" — refuted; aligned is typically least-compounding (with conditional qualifiers).
- "The user can't reverse-engineer which mechanism is operative" — refuted; signatures are materially different.
- "Pythagorean holds for all $\pi \in \mathcal{C}$" — only on the active boundary; the half-space has an explicit cross-term.
- The decomposition $D(\pi_{\text{true}} \| \pi^*) = D(\pi_{\text{true}} \| \pi_T^*) + D(\pi_T^* \| \pi^*)$ — Pythagorean does not apply with $\pi_{\text{true}}$ outside $\mathcal{C}$.
- "Capacity = bandwidth via Fisher dimension" — Fisher rank ≠ bandwidth in any derived sense.
- "Mechanism of Black Nazi case is data corruption" — most likely RLHF objective distortion, not corpus curation.
- "240/240 robustness" — actual numbers are 222/240, 223/240, 211/240.
- "$r > 0.95$ in policy-space verification" — was a signed-beta artifact; with the correct convention, $r = 1.0000$.
- **"Bridge B is derived and verified at first order with $r \approx 0.996$ on real e-projection"** — Test 3's $r \approx 0.996$ was a constant-$\mu$ artifact; the actual joint-sweep result (Test 4) is $r \approx 0.98$ with 15–25% slope deviations from 1. *Round 11.*
- **"Bridge B is a substantive derivation"** — the four identities are inner-product algebra given $g = \mu c$ (law of cosines); the information-geometric content is the textbook first-order e-projection fact. Bridge B is more accurately a clean reorganization. *Round 11.*
- **"Bridge B's $\mu^2$-leakage is the framework's most distinctive currently-available testable prediction"** — true at toy level; the real-system test has unaddressed operational obstacles (no isolated constraint direction, KL coefficient ≠ severity, undefined off-query behavior, unobservable $\mu$). *Round 11.*

## Added along the way

- The four-way decomposition (replacing the universal energy law).
- The corrected Bregman triangle identity with explicit cross-term $\lambda^*(R_{\text{true}} - R_0)$.
- Bridge B (as reorganization): the first-order Fisher-tangent analog of the four-object decomposition for the RLHF setup, with scalar laws $\mu^2 s^2, (a-\mu s)^2, \mu^2(1-s^2), a^2 + \mu^2 - 2 a \mu s$. Inner-product algebra given $g = \mu c$; shape $r \approx 0.98$ and 15–25% magnitude error on real e-projection (Test 4).
- The explicit second-order term in the e-projection expansion: $\frac{\lambda^2}{2}\pi_0(\tilde r^2 - \mathbb{E}_{\pi_0}[\tilde r^2])$, accounting qualitatively for the magnitude error in Bridge B.
