# Monte Carlo Methods for Estimating $\rho^*$

A learning document on what we can and cannot learn about a language model by throwing prompts at it.

---

## Part 0: The honest answer up front

Yes — Monte Carlo techniques can recover the structure of $\rho^*$, but with two important qualifications:

**Random in the literal sense doesn't work.** Random tokens generate gibberish, on which the model produces gibberish, and the difference between base and Instruct on gibberish tells us almost nothing about institutional shaping. We need *structured* sampling that respects the geometry of what we're measuring.

**The connection to physics Monte Carlo is real but subtle.** In statistical mechanics, Monte Carlo is used to sample from a high-dimensional distribution we can evaluate but not directly enumerate. Our situation is different: we *can* evaluate $\rho^*$ at any specific $(x, y)$ pair (with logit access). What we can't do is enumerate the prompt space. So Monte Carlo here is about *exploring* the prompt-space efficiently, not about simulating an intractable distribution.

The right way to think about this: we have a vast prompt-space, a function $\rho^*$ defined on it, and we want to characterize where this function is large and what structure it has. Monte Carlo gives us systematic ways to do that exploration.

The remainder of this document develops the math and methodology.

---

## Part 1: Why random prompts fail

Imagine sampling random sequences of tokens as prompts. What happens?

The vast majority of random token sequences are not coherent natural language — they're statistical noise from a vocabulary perspective. Both base and Instruct will respond to them with continuations, but the continuations themselves are dominated by the model's general inclinations on incoherent input rather than by its institutional shaping on contested topics.

Concretely, $\rho^*$ on a random-token prompt has two components:

$$\rho^*(x_{\text{random}}, y) = \rho^*_{\text{shaping}}(x_{\text{random}}, y) + \rho^*_{\text{noise}}(x_{\text{random}}, y).$$

The first component is what we want — institutional shaping that engages on the prompt. The second is what we don't want — generic differences between base and Instruct in how they handle gibberish (mostly involving Instruct's tendency to produce more polite/formatted output and base's tendency to produce more raw text).

For random prompts, $\rho^*_{\text{noise}}$ dominates. The signal-to-noise ratio is terrible.

This is the analog of the "rare event" problem in physics Monte Carlo. If you want to sample from the Boltzmann distribution of a physical system at low temperature, naive uniform sampling concentrates on high-energy configurations that have negligible probability under the distribution you care about. You see the irrelevant configurations and miss the rare relevant ones.

In our case, the relevant configurations are prompts where institutional shaping engages — typically prompts about contested historical, political, or statistical topics, asked in ways that probe specific framings. These are a tiny fraction of prompt-space. Uniform random sampling will almost certainly miss them.

### The base rate problem

To make this concrete: suppose 1 in 10,000 random prompts elicits a response where institutional shaping is detectable. To collect 100 such prompts via uniform random sampling, you'd need to sample 1,000,000 prompts. Even at fast inference speeds (say 1 second per response on each model), that's 23 days of continuous sampling for both models combined. And the prompts you find this way will be biased toward whichever shaped topics happen to overlap with random-token-space, which is essentially nothing.

So we need sampling strategies that *concentrate* on the regions of prompt-space where shaping is likely to engage. This is *importance sampling* in the Monte Carlo language.

---

## Part 2: Importance sampling and what we're estimating

The general Monte Carlo problem we're solving: estimate some quantity that depends on the structure of $\rho^*$ across prompt-space.

Concrete examples of what we might want:

- The fraction of prompts in a topic category where $\rho^*$ engages strongly.
- The mean and variance of $|\rho^*|$ over prompt-space.
- Principal directions in $\rho^*$ (the low-rank structure from the framework).
- The correlation structure of $\rho^*$ across prompts.

Each of these is an integral or expectation:

$$\mathbb{E}_{x \sim \mu(x)}[F(\rho^*(x, \cdot))]$$

where $\mu$ is some measure on prompt-space and $F$ is some functional of the per-prompt distortion field.

If $\mu$ is uniform on prompt-space, we have the random-prompt approach (which fails).

The importance sampling alternative: sample from a proposal distribution $q(x)$ that concentrates on relevant regions, then re-weight:

$$\mathbb{E}_{x \sim \mu}[F] = \mathbb{E}_{x \sim q}\left[ \frac{\mu(x)}{q(x)} F \right].$$

The variance of the estimator depends on how well $q$ matches the regions where $F$ is large. A good $q$ has high probability where $F$ is large and low probability elsewhere.

For our problem, "$F$ is large" means "the prompt elicits substantial $\rho^*$." So we want $q$ to concentrate on prompts that are likely to engage institutional shaping.

This isn't just an abstract Monte Carlo improvement. It's the substantive question: how do we generate prompts that probe shaping efficiently?

---

## Part 3: Structured prompt generation

The practical answer to "how do we generate good probe prompts" has several components, each with mathematical structure.

### Topic-conditional generation

Identify topic categories where institutional shaping is expected. For each category, generate prompts asking content questions on that topic. This is what the empirical work in the framework did: three falsification target candidates (crime demographics, founding fathers, wehrmacht 1943) plus controls, with multiple prompts per topic.

Mathematically: define a measure $\mu_{\text{topic}}$ over topic categories, and within each topic, a measure $\mu_{\text{prompt} \mid \text{topic}}$ over prompt phrasings. The proposal distribution is:

$$q(x) = \sum_{t \in \text{topics}} \mu_{\text{topic}}(t) \, \mu_{\text{prompt} \mid \text{topic}}(x \mid t).$$

For each topic, the prompt distribution should cover paraphrases (same content, different wording) and format variants (same content, different format constraints).

The choice of which topics to include is informed by the framework's predictions about where shaping engages. This is a stratified sampling design — guarantees coverage of each topic at the cost of giving up uniformity over prompt-space.

### Paraphrase clustering

Within a topic, paraphrases are samples from the conditional distribution $\mu_{\text{prompt} \mid \text{topic}}$. The framework predicts that shaping is policy-level (engaged on the topic, not on specific phrasings), so paraphrases of the same topic should produce correlated $\rho^*$ values.

Empirically: if we sample $N$ paraphrases of topic $t$, compute $\rho^*$ on each, and find high correlation across paraphrases, that's evidence of policy-level shaping. Low correlation suggests format-pressure or phrasing-specific effects.

This gives us a Monte Carlo estimator with built-in diagnostics. The within-topic variance tells us about phrasing sensitivity; the between-topic variance tells us about institutional shaping signature.

### Adversarial generation

A more sophisticated approach: use a separate language model to generate prompts that are *predicted* to elicit shaping. This is the "automated red teaming" approach in the literature.

Mathematically: train a generator model $g_\phi(x)$ to produce prompts that maximize some signal of shaping (e.g., $|\rho^*(x, \cdot)|$ averaged over completions). The generator is a learned proposal distribution.

Two failure modes:

The generator can overfit to a specific kind of prompt that happens to elicit large $\rho^*$ but is unrepresentative of the broader space where shaping engages. This is the "low coverage" problem identified by Hong et al. 2024 (Curiosity-driven Red-teaming).

The generator may itself be a shaped LLM, so its choice of prompts reflects its own institutional shaping rather than independent exploration of prompt-space.

The first problem can be addressed with diversity-promoting objectives (curiosity-driven exploration). The second is fundamental and hard to fully resolve.

### MCMC over prompt-space

Markov chain Monte Carlo lets us sample from a target distribution by constructing a chain whose stationary distribution is what we want. Zhu, Yan, and Griffiths 2024 apply this idea to LLM probing.

The setup: define a target distribution $\pi(x) \propto e^{V(x)}$ where $V(x)$ is some "potential" — for our case, $V(x) = |\bar{\rho}(x)|$ or some other measure of how strongly shaping engages on prompt $x$. Use MCMC (Metropolis-Hastings, Gibbs sampling) to sample from $\pi$.

Concrete Metropolis-Hastings procedure:

1. Start with some initial prompt $x_0$.
2. Propose a perturbation $x' \sim q(x' \mid x_t)$ — a paraphrase, a topic shift, an addition or deletion.
3. Compute the acceptance probability $\alpha = \min(1, e^{V(x') - V(x_t)} \cdot q(x_t \mid x')/q(x' \mid x_t))$.
4. With probability $\alpha$, accept ($x_{t+1} = x'$). Otherwise reject ($x_{t+1} = x_t$).
5. Repeat.

After burn-in, samples are approximately from $\pi$. The chain explores regions of high $V$ — high shaping — efficiently.

The proposal distribution $q$ matters. For our problem, natural choices:
- Word-level perturbations (replace, insert, delete tokens).
- Paraphrase via another LM.
- Topic-shift via a topic-related LM-generated alternative.
- Format perturbation (same content, different format).

Each defines a specific MCMC algorithm with different mixing properties.

### Sequential Monte Carlo with twist functions

Zhao et al. 2024 use Sequential Monte Carlo with learned "twist functions" for LLM inference problems. The twist function approximates the expected future value of the potential — for our problem, how much more shaping a partial prompt is likely to accumulate.

Sequential Monte Carlo works as follows:

1. Maintain a population of $N$ partial prompts.
2. At each step, extend each partial prompt by sampling additional tokens.
3. Re-weight prompts by their current potential and the twist function's prediction of future potential.
4. Resample prompts according to weights — high-potential prompts duplicate; low-potential prompts get pruned.

The result is a population of prompts concentrated on regions where shaping engages strongly.

This is more sophisticated than basic MCMC but has better properties for sequence-structured problems where you want to grow prompts incrementally rather than make discrete jumps.

---

## Part 4: What MCMC reveals about $\rho^*$

Once we have a Monte Carlo procedure that explores prompt-space efficiently, we can ask several questions about the structure of $\rho^*$.

### Mode analysis

The MCMC chain will spend time in regions of high $V(x)$. Different regions correspond to different "modes" — clusters of prompts that all elicit strong shaping in similar ways.

Cluster the visited prompts (by embedding similarity, by topic categorization, by output-pattern similarity). The number and structure of clusters tells us about $\rho^*$:

- Few large clusters: shaping is concentrated on a few topic categories. The institutional shaping signature has low effective rank.
- Many small clusters: shaping is broadly distributed. Effective rank is high.
- Clusters that align with predicted falsification targets: confirms framework predictions about which topics engage shaping.
- Clusters that don't align with predictions: reveals shaping topics we didn't anticipate.

The Phase E empirical work probed three predicted topics. MCMC over prompt-space could discover topics we didn't predict — places where the institution has trained against the model that we wouldn't have known to test directly.

### Boundary analysis

Between regions of high $V$ and low $V$, there are boundaries — prompts where shaping is just starting to engage or just stopping. These boundaries are informative about the structure of the institutional reward signal.

Specifically: a sharp boundary (where $V$ jumps from low to high over a small change in prompt) corresponds to mode-collapse-like shaping — the institution has trained the model to give a specific framing on these specific prompt types. A gradual boundary corresponds to soft amplification.

Boundary structure is something MCMC reveals naturally — the chain visits boundary regions because of detailed balance, and the rate at which it crosses boundaries tells us about boundary sharpness.

### Equilibrium statistics

The stationary distribution $\pi(x) \propto e^{V(x)}$ has natural statistics:

**Partition function** $Z = \sum_x e^{V(x)}$. Estimable from MCMC by various methods (thermodynamic integration, annealed importance sampling). Gives a single number characterizing the total "amount of shaping" in the institutional signature.

**Free energy** $F = -\log Z$. Related to the partition function by definition. Has an interpretation as the "effective shaping strength" averaged over prompt-space.

**Energy distribution** $P(V)$ — the distribution of potential values across the MCMC samples. The shape of this distribution tells us about the fraction of prompt-space where shaping is strong vs. weak.

### Phase transitions

If we vary some parameter (the temperature $T$ in the sampling, or the weight $\beta$ that balances different categories), the equilibrium statistics may exhibit phase transitions — sharp changes in $P(V)$ as the parameter crosses a critical value.

For institutional shaping, this could correspond to: at low effective temperature, samples concentrate on the most heavily-shaped topics (founding fathers, wehrmacht). At higher temperature, samples spread to a broader set of topics with weaker shaping. The transition tells us about the gap between strongly-shaped and weakly-shaped regions.

---

## Part 5: Connections to physics Monte Carlo

The mathematical structure of what we're doing is the same as Monte Carlo simulation of physical systems. This is worth making explicit because it lets us borrow techniques.

### The temperature analogy

In physics, the Boltzmann distribution at temperature $T$ is $P(x) \propto e^{-E(x)/k_B T}$. High $T$ means broad sampling across configurations; low $T$ means concentration on low-energy states.

In our setup, the "energy" is $E(x) = -V(x) = -|\bar{\rho}(x)|$ (negative shaping strength, so that low energy = high shaping). The "temperature" is the parameter we tune to control how aggressively we sample shaped regions.

### Replica exchange

Physics Monte Carlo often uses *replica exchange* (parallel tempering): run multiple chains at different temperatures, periodically swap configurations between them. This helps the low-temperature chains escape local minima by getting "kicked" via swaps with high-temperature chains.

For our problem: run chains at different "shaping selectivity" levels. The high-temperature chains explore broadly. The low-temperature chains concentrate on heavily-shaped topics. Swapping helps the low-temperature chains discover new heavily-shaped regions they wouldn't find by local exploration.

### Free energy methods

In physics, computing free energies (essentially log-partition functions) requires special techniques because partition functions are integrals over high-dimensional configuration space. Methods include:

**Thermodynamic integration.** Compute the free energy as an integral $F = -\int_0^1 d\lambda \, \langle E \rangle_\lambda$ where $\lambda$ interpolates between a tractable reference system and the system of interest.

**Annealed importance sampling.** Generate samples from the target distribution by gradually annealing from a tractable distribution.

**Wang-Landau sampling.** Iteratively estimate the density of states $g(E)$ such that flat sampling in $E$-space tells us about $g$.

For our problem, these can give us the total amount of shaping (the effective partition function), the distribution of shaping strengths across prompt-space, and other equilibrium properties — *without enumerating the prompt-space*.

### Detailed balance and stationary distribution

The fundamental Monte Carlo guarantee is *detailed balance*: a chain satisfying $\pi(x) T(x \to x') = \pi(x') T(x' \to x)$ has $\pi$ as its stationary distribution. The Metropolis-Hastings algorithm explicitly enforces detailed balance through the acceptance ratio.

This means: if we set up the chain correctly, after sufficient burn-in time, the samples are from the right distribution. The bias introduced by starting at an arbitrary initial prompt washes out.

Sufficient burn-in time is a research question for any specific MCMC setup. Diagnostics like Gelman-Rubin statistics, autocorrelation analysis, and visual inspection of trace plots tell us when the chain has converged.

---

## Part 6: Practical limitations and what they mean

Several limitations affect what we can learn from Monte Carlo techniques.

### The proposal distribution problem

For prompt-space, defining a good proposal distribution is hard. The space is discrete (sequences of tokens), unbounded (sequences of any length), and highly structured (most sequences are not coherent natural language).

Word-level perturbations preserve coherence but explore slowly — small steps in token space.

Paraphrase-via-LM proposals jump faster but inherit the proposal LM's biases.

Random topic-shifts move quickly but break the chain's mixing.

The choice involves trade-offs that depend on what we're measuring. For finding novel high-$V$ prompts, larger jumps help. For characterizing structure within a known high-$V$ region, smaller perturbations are better.

### Mixing time

MCMC chains take time to converge to the stationary distribution. For high-dimensional, multimodal target distributions, mixing time can be exponentially long in the dimension.

For prompt-space, the modes are far apart in token-edit distance: getting from a prompt about Wehrmacht to a prompt about founding fathers requires either many word-level edits (slow) or a topic-shift jump (potentially breaking detailed balance).

In practice, this means a single MCMC chain may not explore the full structure of $\rho^*$ in reasonable time. Multiple chains, replica exchange, or other parallelization strategies are needed.

### Computational cost

Each MCMC step requires:

1. Generate the proposal $x'$ (cheap if word-level; LM call if paraphrase).
2. Compute $V(x') = $ some function of $\rho^*(x', \cdot)$. This requires sampling completions from both base and Instruct, computing log-probabilities, and aggregating. Per-step cost: roughly 2-10 inference calls per model.
3. Accept/reject.

For a chain of length $T$, total cost: $O(T)$ inference calls.

To get statistically meaningful results, we typically need $T = 10,000$ to $T = 100,000$ samples after burn-in. With burn-in, that's potentially $T = 1$ million inference calls. At 1 second per inference, that's 12 days of compute.

This is feasible on a small GPU cluster but not on a single consumer GPU. The Phase E empirical work was done on a single RTX 5080 because it used a small probe set (a few hundred prompts total). MCMC with proper convergence requires more compute.

### The "shaped probe model" problem

If we use a LM to generate probe prompts (paraphrase generation, topic-shift proposals), and that LM has its own institutional shaping, our exploration of prompt-space is biased by the proposal LM's blind spots.

Concretely: if we use Claude to generate probes about contested topics, Claude's own shaping affects which topics it generates probes for. Topics where Claude has strong shaping in the same direction as the model being measured will be under-explored, because Claude will avoid generating probes that engage its own shaping.

This is a serious limitation. Mitigations:

Use multiple proposal models with different shaping signatures (Claude + Llama + Grok). Their disagreements about what to probe reveal the shaping in each.

Use models with weaker alignment training (base models, smaller models, less-aligned models like Grok) for probe generation.

Use human-generated probes for sensitive categories where we expect proposal-model bias.

None of these fully solves the problem. The "instrument is also a subject" issue is fundamental for any LM-driven probing.

---

## Part 7: A specific Monte Carlo design for the framework

Here's a concrete MCMC design for measuring $\rho^*$ structure across prompt-space.

### Setup

Two models: base $M_0$ and Instruct $M_1$ (e.g., Llama-3.1-8B base and Instruct).

A potential function $V(x) = $ some measure of shaping strength. Several reasonable choices:

$$V_1(x) = D_{\text{KL}}(M_1(\cdot \mid x) \,\|\, M_0(\cdot \mid x))$$

(forward KL — measures how much the Instruct distribution has moved from base on prompt $x$).

$$V_2(x) = \mathbb{E}_{y \sim M_1}\left[ |\rho^*(x, y)| \right]$$

(expected absolute distortion — sensitive to mode collapse and large distortion regardless of direction).

$$V_3(x) = \mathbb{E}_{y \sim M_1}[\rho^*(x, y)] - \mathbb{E}_{y \sim M_0}[\rho^*(x, y)]$$

(asymmetry of distortion — large when the trained model produces specific completions that base doesn't).

Each potential captures a different aspect of shaping. For initial exploration, $V_1$ (KL divergence) is the cleanest single number.

### Proposal distribution

A combination:

- 50%: word-level edits (replace, insert, delete a single token, weighted by the LM's predictions).
- 30%: paraphrase the current prompt using a separate, less-shaped model (a base model, ideally).
- 15%: topic-shift to a related topic, again using the less-shaped proposal model.
- 5%: format perturbation (same content, different format constraint).

The mix balances local exploration (word edits) with broader moves (paraphrase, topic-shift) and the diversity of probe types (format perturbation).

### Acceptance

Standard Metropolis-Hastings:

$$\alpha = \min\left(1, \frac{e^{V(x')/T} q(x \mid x')}{e^{V(x)/T} q(x' \mid x)}\right)$$

where $T$ is the temperature. Accept with probability $\alpha$.

For the proposal, $q(x' \mid x)/q(x \mid x')$ is computable for word-level edits (symmetric for replacements; asymmetric for insert/delete) and approximated for LM-paraphrase (typically taken as symmetric for simplicity, with bias acknowledged).

### Replica exchange

Run $K$ chains at temperatures $T_1 < T_2 < \cdots < T_K$. Periodically (every $N$ steps) attempt swaps between adjacent temperatures with probability:

$$P_{\text{swap}} = \min(1, e^{(V(x_i) - V(x_j))(1/T_i - 1/T_j)}).$$

The cold chain ($T_1$) concentrates on heavily-shaped prompts. The hot chain ($T_K$) explores broadly. Swaps help the cold chain escape local maxima.

### Diagnostics

Run for a fixed total compute budget. Track:

- Acceptance rate (target ~20-50% for efficient MCMC).
- Autocorrelation of $V$ along the chain (gives the effective sample size).
- Visited prompts — cluster them and see what emerges.
- The empirical distribution of $V$ — fit it to see if it has bimodal structure (strongly shaped vs weakly shaped) or is unimodal.

### Output

After running, we have:

A population of prompts visited at each temperature, with their $V$ values.

Cluster structure of visited prompts (interpretable as topic categories where shaping engages).

Estimates of the fraction of prompt-space where shaping is strong.

For each cluster, characterizations of the shaping (which completions are amplified vs suppressed, how robust to format compression, etc.).

This is a much richer characterization than a fixed probe set provides, at the cost of more compute and methodological complexity.

---

## Part 8: Validation

Before trusting MCMC-derived results, we need validation.

### Convergence diagnostics

Run multiple chains from different starting points. They should converge to the same statistics. Specifically:

The Gelman-Rubin $\hat{R}$ statistic should approach 1 for converged chains.

Visual inspection of trace plots should show stationary behavior after burn-in.

The autocorrelation function should decay to zero within a manageable time horizon.

If chains don't converge, the MCMC isn't mixing well and results are unreliable. Solutions: longer runs, more chains, better proposals, replica exchange.

### Cross-validation with fixed probe sets

The MCMC results should reproduce findings from fixed probe sets. If MCMC discovers that $\rho^*$ is large on founding fathers prompts, but the Phase E paraphrase test on founding fathers showed $\rho^*$ to be moderate, something's wrong with one of the analyses.

This is a sanity check rather than independent validation, but it's important.

### Reproducibility across institutions

Run the same MCMC procedure on multiple model pairs (Llama base/Instruct, GPT base/Instruct if available, Mistral base/Instruct). The basic structure of $V$ should reflect genuine model properties; institution-specific shaping should appear as differences between chains.

If chains on different model pairs all converge to the same prompts, we're measuring something architecture-specific rather than institutional shaping.

### Sensitivity to proposal distribution

Run with different proposal distributions. Word-level only, paraphrase-heavy, topic-shift-heavy. The discovered $\rho^*$ structure should be roughly stable; the rate of discovery should vary with proposal.

If results depend strongly on proposal choice, the chain isn't truly exploring the space — it's biased by the proposal.

---

## Part 9: What Monte Carlo can and can't tell us

Summary of capabilities and limitations.

### Can tell us

The structure of $\rho^*$ across prompt-space — which topics engage shaping, with what strength, and what the boundary structure is.

The effective rank of institutional shaping (whether the signature is concentrated on a few directions or distributed broadly).

Comparative shaping signatures across institutions.

Discovery of unanticipated topics where shaping engages.

Equilibrium statistics: total shaping strength, distribution of shaping intensities.

### Can't tell us

The specific reward function the institution used (we get $\rho^*$, not $r$ — they differ by per-prompt normalization $\log Z(x)$, which we don't measure directly).

The training trajectory (we see endpoints, not the path).

Per-token attribution within a generation (each $\rho^*(x, y)$ is for the full sequence; finer-grained analysis requires different tools).

Causation. We see correlation between (topic, shaping). The causal story — that the institution chose to train against certain topics — is inference, not direct measurement.

### Subject to assumptions

That the proposal distribution explores prompt-space well (depends on proposal design).

That we have enough compute for convergence (depends on how heavy the institution's shaping is and how broadly it's distributed).

That the proposal LM doesn't bias exploration in correlated ways (mitigation: use multiple proposal models).

That logit access is reliable (true for open-weight models; may be approximate for API-only models).

### Comparison with the fixed-probe approach

Fixed probe sets (the Phase E approach) are easier to set up and validate but limited to topics we anticipated. MCMC over prompt-space is more powerful but requires more compute and methodological care.

For the framework's measurement program, both have roles. Fixed probes give clean, interpretable results on specific predictions. MCMC discovers structure we didn't anticipate. Together they characterize the full picture.

---

## Part 10: A research program

Here's how a serious MCMC-based measurement program would look.

### Phase 1: Fixed probe validation

Run fixed probe sets (like Phase E) on a moderate set of topics. Validate that $\rho^*$ behaves as predicted on the topics where we expect shaping. This establishes that the methodology measures something real.

Compute: ~10 hours on one GPU.

### Phase 2: Word-level MCMC on focused topics

Run MCMC starting from the Phase E topics, with word-level perturbations only. This explores the local structure of $\rho^*$ around known shaped regions. Tests whether shaping is concentrated on specific phrasings or broad over paraphrase neighborhoods.

Compute: ~100 hours on one GPU.

### Phase 3: Cross-topic MCMC with paraphrase proposals

Add paraphrase and topic-shift proposals. Allow the chain to discover related topics. Run for substantial time (10⁴-10⁵ samples).

Compute: ~1000 hours; would benefit from a small GPU cluster.

### Phase 4: Replica exchange

Add replica exchange across temperatures. Run multiple chains in parallel. Discover sharply-shaped vs softly-shaped regions.

Compute: ~5x phase 3, but easily parallelized.

### Phase 5: Cross-institutional comparison

Run the full MCMC pipeline on multiple model pairs (Llama base/Instruct, Mistral base/Instruct, etc.). Compute differential signatures.

Compute: linear in number of institutions.

### Phase 6: Public methodology release

Document the methodology so other researchers can reproduce. Publish probe sets, MCMC code, analysis tools.

This is where the work has the most leverage — once the methodology is reproducible by anyone with sufficient compute, it becomes infrastructure for institutional accountability.

### Total scale

A full execution of this program is comparable to a moderate physics computational study — say, equilibrium statistical mechanics of a 3D Ising model with replica exchange. That's a feasible PhD-thesis or postdoc-project scale of work, not a one-person side project.

The framework's mathematical apparatus tells us this is the right kind of thing to do. The specific design above gives a concrete starting point. Whether anyone executes it is a separate question from whether it's possible.

---

## Appendix: The literature

**Sequential Monte Carlo for LLMs.** Zhao, Brekelmans, Makhzani, Grosse 2024 ("Probabilistic Inference in Language Models via Twisted Sequential Monte Carlo"). Casts RLHF, red-teaming, and related tasks as sampling from unnormalized distributions and applies SMC with learned twist functions. Provides bidirectional bounds on log partition functions — directly relevant to estimating institutional shaping signatures.

**MCMC for LLM probing.** Zhu, Yan, Griffiths 2024 ("Recovering Mental Representations from Large Language Models with Markov Chain Monte Carlo"). Uses MCMC to probe LLM representations more efficiently than direct prompting. Demonstrates significant efficiency gains over uniform prompting.

**Curiosity-driven red teaming.** Hong et al. 2024 ("Curiosity-driven Red-teaming for Large Language Models"). Addresses the coverage problem in standard RL-based red teaming by adding novelty-seeking objectives. Relevant for designing proposal distributions that explore broadly.

**Gradient-based attack methods.** GCG, AutoPrompt, and related work search prompt-space via gradients. These are deterministic alternatives to Monte Carlo with different trade-offs.

**Physics Monte Carlo references.** Newman and Barkema "Monte Carlo Methods in Statistical Physics" (1999) for general background. Earl and Deem 2005 for replica exchange. Wang and Landau 2001 for the eponymous algorithm.

---

*End of document.*
