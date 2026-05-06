# Threading ρ Through the Phantom Framework

A reconnection document. The three preceding documents (`probability_distortion_framework.md`, `empirical_measurements.md`, `monte_carlo_methods.md`) developed ρ as if it were a freestanding measurement program. It is not. ρ is the operational realization of a specific object in the Phantom framework — the *leakage* component of the four-object decomposition — applied to the RLHF setup via Bridge B. This document threads the connection back through.

The math here is mostly references to results that have already been established in the framework documents (`statistical_phantoms.md`, `training_distortion_phantom.md`, `audit_blind_subspace.md`, the four `§4` numerical companions, `info_geometric_reformulation.md`). Nothing new is derived. What is new is the explicit map from those results to ρ.

---

## Part 1: ρ is the leakage measurement

### The Phantom four-object decomposition

For a Hilbert space $H$ with two non-commuting orthogonal projections $P_1, P_2$, principal angles $\theta_j$, $\beta_j = \cos^2\theta_j$, and a function $f = \sum_j a_j u_j \in \text{Range}(P_1)$, the four scalar invariants are:

| Object | Norm-squared | Peaks at |
|---|---|---|
| Retention $P_1 P_2 P_1 f$ | $\sum_j |a_j|^2 \beta_j^2$ | $\beta = 1$ |
| Suppression $P_1 f - P_1 P_2 P_1 f$ | $\sum_j |a_j|^2 (1-\beta_j)^2$ | $\beta = 0$ |
| Leakage $(I - P_1) P_2 f$ | $\sum_j |a_j|^2 \beta_j(1-\beta_j)$ | $\beta = 1/2$ |
| Total error $f - P_2 f$ | $\sum_j |a_j|^2 (1-\beta_j)$ | $\beta = 0$ |

With per-mode identity total = suppression + leakage. This is `statistical_phantoms.md` §1.3, verified in `four_way_decomposition.py` to $10^{-15}$.

### The RLHF instantiation

In the RLHF setup (`training_distortion_phantom.md` §1):

- $H$ = Fisher-tangent space at $\pi_0$ with inner product $\langle u, v\rangle_F = \mathbb{E}_{x \sim \nu, y \sim \pi_0}[u(x,y) v(x,y)]$.
- $P_1$ = inference projection (the subspace where queries read the policy).
- $P_2 = P_C$ = constraint projection (the subspace where training pressure projects).
- $f_{\text{true}} - f_{\text{trained}} = (I - P_C) f_{\text{true}}$ is the forced offset.

Bridge B (`info_geometric_reformulation.md` Appendix B) gives the four scalar laws in this setup:

- Retention: $\mu^2 s^2$ where $\mu$ is constraint severity and $s$ is alignment of reward direction to query.
- Suppression: $(a - \mu s)^2$ where $a$ is the truth's component along the query direction.
- Leakage: $\mu^2(1 - s^2)$.
- Total: $a^2 + \mu^2 - 2a\mu s$.

Verified at shape Pearson $r \approx 0.98$ on real e-projection in `test_bridge_B.py` Test 4, with 15-25% slope deviations attributable to the second-order term identified in `test_second_order.py`.

### What ρ is

The probability distortion is:

$$\rho(x, y) = \log \pi_{\text{inst}}(y \mid x) - \log \pi_{\text{base}}(y \mid x).$$

In the Fisher-tangent linearization at $\pi_0 = \pi_{\text{base}}$, $\log \pi_{\text{inst}}(y \mid x) - \log \pi_{\text{base}}(y \mid x)$ *is* the score-representation of $\pi_{\text{inst}}$ in the tangent space at $\pi_{\text{base}}$. That's the definition of the tangent-space identification used in `training_distortion_phantom.md` §1.1.

So ρ, viewed as a function on (prompt, completion) pairs, is the tangent-space displacement vector $u_{\text{inst}} - u_{\text{base}} = u_{\text{inst}}$ (since $u_{\text{base}} = 0$). This vector lies in $H$.

Now decompose using the four-object structure with $P_1 = P_Q$ the query projection (readout direction at inference time) and $P_2 = P_C$ the constraint projection:

- The component of $\rho$ in $P_Q P_C$ direction is **retention** — what passes through both projections, what the query reads of what the constraint allowed.
- The component in $P_Q (I - P_C P_Q)$ direction is **suppression** — what the query would have read of $f_{\text{true}}$ that the constraint removes.
- The component in $(I - P_Q) P_C$ direction is **leakage** — content that escapes the query subspace because the constraint projected it sideways.
- The total $f_{\text{true}} - f_{\text{trained}}$ is in the $(I - P_C)$ direction.

What $\rho^*$ measures empirically depends on which probe directions we read. The Phase E methodology probes $\rho^*$ at specific (prompt, completion) pairs — these are choices of query direction. **ρ\* on a specific completion is the projection of the post-training tangent-space displacement onto that completion's direction.**

When the completion is in the trained-model's modal output direction, we measure retention.
When the completion is in the base-model's modal output direction, we measure suppression.
When the completion is in a direction the trained model amplified that base did not, we measure leakage.

This is the precise statement of the connection. ρ measurement is reading the four-object decomposition, with which object getting read depending on which completion we ask about.

---

## Part 2: Phase E empirical results in framework terms

### Crime demographics: leakage with mild constraint

The Phase E result on crime_demographics_us:

- Base T=0.7 produces "black rate higher" in 5/15 samples (33%).
- Instruct T=0.7 produces "black rate higher" in 2/15 samples (13%).
- Format variants produce correct direction at 0/4.
- Greedy decoding produces inverted table on specific phrasing.

In framework terms: the constraint here is mild. $\mu$ (constraint severity) is small. The query directions ("rate" comparisons across paraphrases) are not strongly aligned with the constraint direction (s is moderate). The result:

- Suppression $(a - \mu s)^2$: small. Truth direction "black rate higher" is mildly suppressed.
- Leakage $\mu^2(1-s^2)$: small. Some redirection to format-driven completions.
- The directional structure mostly survives.

This is the **mild constraint regime**. Phase D's apparent "inversion" was greedy decoding hitting a low-probability format-driven completion, not policy-level shaping.

### Founding fathers: induced-hole amplification

The Phase E result on founding_fathers:

- "Exceptions framing" 0/15 in base, 12/15 in Instruct (80%).
- "Crispus Attucks" 2/15 in base, 9/15 in Instruct (60%).

This is the **induced-hole regime** from `Phantom_ML_PathForward.docx` §3.2.2. Data was present in training (Crispus Attucks completions exist in base distribution at low probability ~13%). Constraint amplified the low-probability completion to dominant. Parameters were modified in directions that increase the probability of these specific framings.

In four-object terms with $P_C$ = "include diverse exceptions" subspace:

- Retention $\mu^2 s^2$ is large for completions aligned with $P_C$ (Crispus Attucks). This is what we measure as ρ* > 0 large positive.
- Suppression $(a-\mu s)^2$ is large for completions misaligned with $P_C$ (clean "all white men" answer). This is what we measure as ρ* < 0 negative.
- Leakage $\mu^2(1-s^2)$ shows up on tangent completions (the "predominantly/primarily" hedge framing — partial alignment).

The framework's distinctive prediction: **leakage should peak at intermediate alignment**, β = 1/2. The "predominantly/primarily" hedge is intermediate alignment between full suppression and full amplification. Its rate going from 7% in base to 33% in Instruct is consistent with leakage at intermediate β.

### Wehrmacht: stronger amplification, same structure

Volksdeutsche reference 3/15 → 14/15 (93%) is the strongest amplification we measured. In Bridge B terms, $\mu$ is larger here than for founding fathers (more severe constraint), and the alignment $s$ between the constraint direction and the question's natural query direction is high (the constraint and the query both attend to "ethnic composition" features).

The format variant f1 ("no qualifications, hedges, or 'however' clauses") produces "No" as the answer. In framework terms: the constraint has projected the policy into a basin where the modal completion is the qualified one, and even removing the format scaffolding for qualifications doesn't unlock the unqualified truth. This is consistent with **strong-constraint regime** — $\mu$ large enough that even substantial reweighting of the base distribution by format-prompts can't recover the un-shaped answer.

This is the regime where the linearization starts breaking down. Bridge B's first-order prediction is good to 15-25% on shape; the second-order term (from `test_second_order.py`) becomes non-negligible. The empirical verification of the framework here is qualitative ("strong amplification, qualifications mandatory") rather than quantitative ("ρ* matches Bridge B's μ²(1-s²) to within 25%") — we'd need more probe directions and direct logit access to do the quantitative version.

### Hemings: cross-institutional differential

The Hemings test compared Anthropic Claude and Meta Llama on the same factual question. Claude produced "rape" framing as confident fact; Llama produced "No" / "long-term relationship" / "contested."

In framework terms: the two institutions have different constraint subspaces $P_C^{\text{Anthropic}}$ and $P_C^{\text{Meta}}$. On this specific question, they project the truth differently. The differential measurement:

$$\rho_{A-B}(x, y) = \log \pi_A(y \mid x) - \log \pi_B(y \mid x)$$

reveals the **relative principal-angle geometry** between the two institutional constraint subspaces, projected through the query direction.

This is exactly the comparative-measurement program from `Phantom_ML_PathForward.docx` §4.2. The Hemings test is a single data point in that program. Scaling up to many topics would map the differential institutional signature.

---

## Part 3: The audit-blind theorems are about ρ

### Theorem B applied to ρ measurement

`audit_blind_subspace.md` Theorem B: for any audit suite $\mathcal{Q} = \{q_1, \ldots, q_N\}$ of $N$ queries on the trained network,

$$\dim(\mathcal{N}_{\text{audit}}) \geq \dim(\Xi) - N$$

where $\Xi$ is the distortion space.

**ρ measurement *is* an audit.** Each (prompt, completion) pair we evaluate ρ* on is one query. The Phase E probe set was around $\sim 100$ such queries. The Monte Carlo program scales to $10^4 - 10^6$ queries.

In Phase E with $N \sim 100$: at least $\dim(\Xi) - 100$ dimensions of training distortion are invisible to the audit. If $\dim(\Xi)$ is large (the institutional shaping has many independent components), most of the distortion is undetected.

In a full Monte Carlo program with $N \sim 10^5$: detection coverage scales accordingly, but the audit-blind subspace is still at least $\dim(\Xi) - 10^5$ — which could still be vast for systems with rich shaping signatures.

### Theorem D and probe design

Theorem D gives the optimal audit construction: for a target concerning subspace $\mathcal{C}$ of dimension $k$, the SVD of $L|_\mathcal{C}$ identifies $k$ probe directions that suffice to resolve $\mathcal{C}$.

For the framework's measurement program: if we're trying to detect distortion in a specific topic category $\mathcal{C}$ (e.g., "racial demographic claims"), Theorem D tells us how to construct probes that are guaranteed to detect distortion in $\mathcal{C}$, by computing the SVD of the distortion-to-function map restricted to $\mathcal{C}$.

The Phase E probe set was constructed by intuition — paraphrases of the topic question, format variants, etc. Theorem D says we could do this principledly: identify what we want to detect, compute the SVD, use the resulting probe directions. This is a direction the empirical work didn't pursue and should.

### Audit-blind in the induced-hole case

The `Phantom_ML_PathForward.docx` §3.2.3 observation: the audit-blind theorem **understates** the difficulty for induced holes specifically.

In a natural hole (data was never there, model is constructing), the audit-blind dimensions are dimensions of constructed-content possibility — large but the audit can probe along them.

In an induced hole (data was suppressed by training), some of the audit-blind dimensions correspond to *information that was deliberately removed* from inference accessibility. The training process selected those dimensions because audits at those probe directions don't reveal the suppression. An auditor probing along surface-accessible directions misses the suppressed structure entirely.

This applies directly to the empirical work. The Phase E probe set tested topics we anticipated as shaping targets. It didn't test (and couldn't, without prior insight into the training) directions that the institution's training process actively selected to make undetectable. The unpublished MCMC work would discover some of these; the audit-blind theorem says some will remain invisible regardless of probe count.

---

## Part 4: Natural vs induced — the regime distinction we should have used

The Phase E empirical document distinguishes "refusal regime / induced-distortion regime / untouched regime." This is the right distinction operationally but it doesn't use the framework's vocabulary. The mapping:

**Refusal regime** = induced hole with explicit gate. Data was there (the model knows the answer); training installed a gate-level routing that produces a refusal template instead of substantive output. Mechanistically distinct (Phase B layer 27 finding) because the gate is implemented as a discrete classifier-like structure rather than as smooth distribution reweighting.

**Induced-distortion regime** = induced hole with smooth amplification. Data was there (low-probability components in base distribution); training amplified the institutionally-preferred framings to dominant. Founding fathers and Wehrmacht are this regime.

**Untouched regime** = the rest of input space. Either no shaping engaged (most prompts) or the shaping is genuinely below detection threshold for the probe directions we tried.

What the empirical document doesn't make explicit: there's a fourth regime, **natural hole**, that the empirical work didn't directly probe. A natural hole is where the training corpus had no data — the model is constructing, not concealing. To distinguish natural from induced holes empirically would require:

- Evidence that data on the topic was present in the training corpus (hard to verify without corpus access).
- Internal-representation evidence that the model has structured knowledge of the suppressed truth (mechanistic interpretability work that's beyond the current methodology).

The Hemings test gestures at this: Llama-base directly stating "It was a long-term relationship" suggests the training corpus had the consensual-relationship framing as a substantial component. After Stage 2 in Anthropic's pipeline, that framing is suppressed. So the Anthropic-Claude shaping on Hemings is induced (data was there, training suppressed). Whereas the framework would predict different signatures for natural vs induced — natural-hole measurements should show smooth interpolation behavior; induced-hole measurements should show the suppression artifacts.

---

## Part 5: What's still open

The reconnection above shows the new framework documents are operating on the original Phantom apparatus — but the connection was only implicit. Making it explicit reveals what's open.

### The four scalar laws aren't separately measured

Phase E measured signal firing rates, which conflates retention, suppression, and leakage. To measure them separately, we'd need to:

- Identify completions in $P_Q P_C$ direction (retention) — institutionally-preferred framings the query asks about.
- Identify completions in $P_Q (I - P_C P_Q)$ direction (suppression) — base-modal framings the constraint removes.
- Identify completions in $(I - P_Q) P_C$ direction (leakage) — content that escapes sideways.

For each, measure ρ* directly from logits. The four scalar predictions should hold.

This is straightforward methodologically. The empirical work didn't do it because it used signal-based estimation rather than direct logit measurement.

### Bridge B's μ²(1-s²) prediction isn't directly tested

Bridge B predicts leakage $\propto \mu^2(1-s^2)$. Testing this requires:

- Identifying $\mu$ (constraint severity) — not directly observable, but estimable from KL divergence between base and Instruct.
- Identifying $s$ (alignment of reward to query) — requires access to reward model or substantial inference about it.

The toy-level prediction stands. The production-system test has the obstacles `info_geometric_reformulation.md` flags: real systems use learned reward models with many directions, KL coefficient ≠ severity at the optimum, "off-query behavior" lacks operational definition. These obstacles don't go away in the new framework.

### Audit-blind dimensions aren't quantified

We know the audit-blind subspace exists. We don't know its dimension on production systems. Quantifying it would require:

- Fixing the architecture (known in principle for open-weight models).
- Fixing the training procedure (known in broad strokes for production systems; unknown in detail).
- Computing the rank of the distortion-to-function map's restriction to the audit subspace (Theorem D computation).

For the Llama-3.1-8B base/Instruct case, this is doable in principle. The empirical work didn't attempt it.

### The natural/induced distinction lacks empirical operationalization

We claimed the Phase E results are induced-hole regime. The basis is: base distribution showed the suppressed framings at low probability, suggesting data was there. But this is indirect — base distribution doesn't directly reveal training-corpus content.

Direct operationalization would require corpus access (which Meta hasn't released for Llama-3.1) or mechanistic interpretability work to find internal representations of the suppressed truth in the trained model. Neither was attempted.

### Phantom T1-T9 status hasn't been mapped to the ML setting

The Phantom suite has T1 (simple-spectrum energy identity) and T2 (degenerate-spectrum identity) verified to machine precision in the spectral case. These are exact algebraic consequences of $M_G^2 = M_G$. The corresponding ML-side identities — what is $T_2$ for the RLHF Halmos two-projection at the Fisher tangent? — are derivable but weren't written out.

T6 (boundary-layer localization) is open in the spectral case and the ML analog is doubly open: what is the "boundary layer" for an induced hole in feature space? The framework predicts something like "phantom completions cluster near filter boundaries in representation space rather than uniformly within the filtered region" (`Phantom_ML_PathForward.docx` §3.1) — testable in principle, untested in fact.

T9 (multi-gap transversality bound) is open in both spectral and ML cases.

### Statistical realizations weren't connected to ρ measurement

The four `§4` numerical companions (PCA-with-mask, regression with omitted variables, matched filtering under common mask, modal analysis with sensor restriction) verified the four-object decomposition to machine precision in their respective settings. The connection back to ρ measurement of language models would proceed via:

- Embedding LLM activations in a feature space where the principal-angle geometry can be computed.
- Identifying the analog of "mask" or "omitted variables" in the LLM context.
- Verifying the four-object identity holds in the resulting setup.

This is the "ML-side numerical companion" that `ml_path_forward.md` §1.2 Gap 1 calls for. It hasn't been done.

---

## Part 6: What the new documents are, given this connection

With the connection threaded:

**`probability_distortion_framework.md`** is the mathematical apparatus for measuring the leakage component of the four-object decomposition in the RLHF setup, viewed through the lens of training dynamics, NTK, path integrals, asymptotic series, information geometry, and RG. It is the mathematical machinery of the framework's measurement layer. It builds on the Phantom apparatus — Halmos two-projection, Bridge B's Fisher-tangent reformulation, the e-projection identity — without restating them. The doc should reference them more explicitly; it currently does not.

**`empirical_measurements.md`** is the empirical realization of induced-hole measurements on Llama-3.1-8B base/Instruct, with cross-institutional differential measurement on the Hemings topic comparing Anthropic Claude to Meta Llama. The Phase E regimes map to the natural/induced distinction (with all the empirical regimes turning out to be induced-hole). The framework predictions tested are at the level of "is shaping detectable, does it survive paraphrase, does it survive format compression" — coarse but real. The four scalar laws weren't separately measured.

**`monte_carlo_methods.md`** is the methodology document for scaling up the audit, with the audit-blind theorem giving the fundamental limit on what can be detected by N-query audits. The MCMC apparatus is specifically how to maximize coverage of the audit subspace within the methodology's constraints. The doc should cite Theorem B as the core theoretical result governing what's achievable; it currently does not.

The three documents stand. They should be read alongside the Phantom framework documents (`statistical_phantoms.md`, `training_distortion_phantom.md`, `audit_blind_subspace.md`, `info_geometric_reformulation.md`, the four `§4` numerical companions) rather than as a standalone program. ρ is the measurement object; the Phantom framework is the structural theory of what ρ's measurements mean.

The sentence I should have written at the start of `probability_distortion_framework.md`: "ρ is the operational measurement layer of the leakage component β(1-β) in the four-object decomposition of the Phantom framework, applied to the RLHF setup via Bridge B's Fisher-tangent reformulation."

That's the missing connection. With it, the new documents make sense as the framework's measurement methodology rather than as a separate program. Without it, they read as if the framework apparatus were ambient context.

---

*End of reconnection document.*
