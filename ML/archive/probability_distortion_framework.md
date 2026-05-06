# Estimating the Probability Distortion

A learning document on the mathematics of measuring how training reshapes a language model's output distribution.

This is written for someone who has seen calculus and basic linear algebra but hasn't necessarily worked through statistical mechanics, information theory, or training dynamics. Each piece is derived rather than asserted. Where a step looks small but matters, it's written out.

---

## Part 0: Mathematical preliminaries

A few pieces of standard machinery used throughout. Skip if familiar.

### Conditional probability and joint distributions

A discrete probability distribution $P$ over a set $\mathcal{Y}$ assigns to each element $y \in \mathcal{Y}$ a number $P(y) \geq 0$ with $\sum_y P(y) = 1$. We write $P(y)$ for the probability of $y$ under $P$.

A *conditional* distribution $P(y \mid x)$ assigns probabilities to $y$ for each fixed $x$. So for each $x$, $P(y \mid x)$ is a probability distribution over $y$, satisfying $\sum_y P(y \mid x) = 1$ for every $x$.

For language models, $\mathcal{Y}$ is the set of possible output sequences. For sequences up to length $L$ from a vocabulary of size $V$, there are $V^L$ possible sequences, which is astronomical. But for any specific $y$, the model assigns a definite probability $P(y \mid x)$, computable from its logits.

### Expected values

The expected value of a function $f$ under distribution $P$ is:

$$\mathbb{E}_{y \sim P}[f(y)] = \sum_y P(y) f(y).$$

The notation $y \sim P$ means "$y$ is distributed according to $P$." This is just a way to write what we're averaging over.

### Logarithms of probabilities

We will work extensively with $\log P(y \mid x)$. Two useful properties:

The log of a product is the sum of logs: $\log(ab) = \log a + \log b$. So for a sequence $y = (y_1, y_2, \ldots, y_n)$ where each token is conditional on previous tokens, $\log P(y) = \sum_i \log P(y_i \mid y_1, \ldots, y_{i-1})$.

Logs convert ratios to differences: $\log(a/b) = \log a - \log b$.

These properties make log-probabilities much more tractable than probabilities themselves, especially for long sequences where probabilities become extremely small.

### KL divergence

The Kullback-Leibler divergence between two distributions $P$ and $Q$ over the same space is:

$$D_{\text{KL}}(P \,\|\, Q) = \sum_y P(y) \log \frac{P(y)}{Q(y)} = \mathbb{E}_{y \sim P}\left[ \log \frac{P(y)}{Q(y)} \right].$$

It measures how different $P$ is from $Q$, weighted by $P$. Properties:

- Always non-negative: $D_{\text{KL}}(P \,\|\, Q) \geq 0$.
- Zero if and only if $P = Q$.
- Not symmetric: $D_{\text{KL}}(P \,\|\, Q) \neq D_{\text{KL}}(Q \,\|\, P)$ in general.
- Not a distance: doesn't satisfy the triangle inequality.

Despite not being a distance, it has a deep geometric interpretation we'll use later. For now, treat it as a measure of "how different are these two distributions."

### Variational calculus (the bare minimum)

We will use one technique from variational calculus: maximizing a function of a probability distribution subject to constraints, using Lagrange multipliers.

The setup: we have a function $L[\pi]$ that depends on a distribution $\pi$. We want to find the $\pi^*$ that maximizes $L$ subject to $\pi$ being a valid probability distribution (non-negative, sums to 1).

The technique: introduce a Lagrange multiplier $\lambda$ for the normalization constraint $\sum_y \pi(y) = 1$, and form:

$$\mathcal{L}[\pi, \lambda] = L[\pi] - \lambda \left( \sum_y \pi(y) - 1 \right).$$

Take the partial derivative with respect to $\pi(y)$ for each $y$, set it to zero, and solve. This gives a candidate optimum; check it satisfies the original constraints and is a maximum.

For the non-negativity constraint, we'll usually find that the optimum is automatically positive (since we'll be exponentiating), so we don't need explicit Lagrange multipliers for it.

If you've seen statistical mechanics and the partition function, the procedure will look familiar. If not, the next section walks through it explicitly for our case.

---

## Part 1: What we are trying to measure

A language model defines a conditional probability distribution. Given an input prompt $x$, it assigns probabilities to possible output sequences $y$. We write this as $P(y \mid x; \theta)$, where $\theta$ are the model's parameters. The semicolon separates the random variables ($y$ given $x$) from the parameters ($\theta$). For different parameter values, the model gives different distributions.

Two distributions are of central interest:

**The base distribution.** Call it $P_{\text{base}}(y \mid x)$. This is what the model produces after pretraining only — exposure to a large corpus of text without any subsequent alignment training. The parameters at this point are $\theta_0$.

**The post-training distribution.** Call it $P_{\text{inst}}(y \mid x)$. This is what the model produces after Stage 2 training: supervised fine-tuning, reinforcement learning from human feedback, constitutional AI, or whatever other alignment procedures are applied. The parameters at this point are $\theta_T$, the training endpoint.

The object we care about is the *probability distortion field*:

$$\rho(x, y) = \log P_{\text{inst}}(y \mid x) - \log P_{\text{base}}(y \mid x).$$

Because $\log a - \log b = \log(a/b)$, this is also:

$$\rho(x, y) = \log \frac{P_{\text{inst}}(y \mid x)}{P_{\text{base}}(y \mid x)}.$$

It's the log of the ratio of post-training probability to pre-training probability. Where this is positive, training has amplified $y$ given $x$. Where it's negative, training has suppressed it. Where it's zero, training has not changed it.

The whole framework is about understanding the structure of $\rho$. Everything that follows develops the mathematical apparatus needed to predict, measure, and interpret this single object.

### Why $\rho$ is the right thing

The choice isn't obvious; let me motivate it.

We could compare $P_{\text{inst}}$ and $P_{\text{base}}$ directly — looking at the difference $P_{\text{inst}}(y \mid x) - P_{\text{base}}(y \mid x)$. This is mathematically allowed but practically bad. Probabilities of specific long sequences are tiny. For a sentence of 30 tokens with a 50,000-word vocabulary, even a "high-probability" sentence might have probability $10^{-30}$ or smaller. Differences between such tiny numbers are dominated by computational noise.

Logs of probabilities, by contrast, are well-behaved. $\log(10^{-30}) = -30 \log 10 \approx -69$. Differences between log-probabilities are differences between numbers in the tens or hundreds, easy to work with numerically.

We could compare in some kind of summary form — entropy, mean reward, downstream task performance. These miss the per-completion structure that the framework needs. Two distributions can have the same entropy while differing wildly in *which* completions get probability mass.

Most importantly, $\rho$ has a deep mathematical structure that emerges from how training works. We will see in Part 2 that for the standard form of alignment training (reverse-KL-regularized RLHF), $\rho$ has an explicit closed form in terms of the reward function. This isn't an analogy or a heuristic; it's an exact result.

### Three regimes (preview)

Before going into the math, here is what we will find about the structure of $\rho$.

**Refusal regime.** For some prompts, $\rho$ has a single sharp positive spike on a specific template completion. The spike is large enough that the template effectively has all the probability mass after training. This is a discrete behavior — the prompt either triggers the refusal gate or it doesn't.

**Induced-distortion regime.** For other prompts, $\rho$ has a paired structure: large negative values on truthful completions that the base distribution gave substantial probability to, and large positive values on alternative framings that the base distribution had at low probability. After training, the truthful completions have been pushed toward zero probability and the alternative framings have been amplified.

**Untouched regime.** For most prompts, $\rho \approx 0$ across all completions with substantial base probability. Training did not engage on these prompts. $P_{\text{inst}} \approx P_{\text{base}}$.

The mathematical apparatus we develop is needed to make these statements precise and quantitative.

---

## Part 2: Deriving $\rho$ from KL-regularized RLHF

The simplest case where we can write $\rho$ explicitly is reverse-KL-regularized reinforcement learning from human feedback. This is the standard formulation used in production alignment training (Christiano et al. 2017, used in InstructGPT, ChatGPT, Claude). We work it out from scratch.

This section is long because we derive the result step by step.

### The training setup

Alignment training has a *reward model* $r(x, y)$ that scores each (prompt, completion) pair with a real number. Higher reward is better.

The training procedure adjusts the language model — call it the *policy* $\pi$ — to produce higher-rewarded completions on average. But there's a constraint: we don't want $\pi$ to drift arbitrarily far from a *reference policy* $\pi_{\text{ref}}$ (typically the model after supervised fine-tuning). If you optimize for reward without restraint, the policy will find ways to maximize reward that the reward model didn't anticipate ("reward hacking"), often producing degenerate outputs.

The standard way to enforce the constraint is with a KL divergence penalty. The objective is:

$$\mathcal{R}(\pi) = \mathbb{E}_{x \sim \mathcal{D}}\Big[\, \mathbb{E}_{y \sim \pi(\cdot \mid x)}[r(x, y)] - \beta \, D_{\text{KL}}\big(\pi(\cdot \mid x) \,\|\, \pi_{\text{ref}}(\cdot \mid x)\big) \,\Big]$$

Let me unpack this. $\mathcal{D}$ is the distribution over prompts the model is being trained on. The outer expectation is over prompts. Inside the brackets:

The first term $\mathbb{E}_{y \sim \pi}[r(x, y)]$ is the expected reward when generating $y$ from the current policy. We want this large.

The second term is $\beta$ times the KL divergence from current policy to reference policy. KL is non-negative and zero when $\pi = \pi_{\text{ref}}$. Subtracting it (with positive coefficient $\beta$) penalizes drift.

The parameter $\beta > 0$ is the regularization strength. Large $\beta$ keeps $\pi$ close to $\pi_{\text{ref}}$. Small $\beta$ allows aggressive optimization for reward at the cost of drifting from reference.

### Reducing to per-prompt optimization

The objective is an expectation over prompts of a per-prompt quantity. The maximizing $\pi$ can be found per-prompt: for each $x$, find the conditional distribution that maximizes the inner bracket.

Hold $x$ fixed and write $\pi(y) := \pi(y \mid x)$, $\pi_{\text{ref}}(y) := \pi_{\text{ref}}(y \mid x)$, $r(y) := r(x, y)$ for compactness. The per-prompt objective is:

$$L[\pi] = \sum_y \pi(y) r(y) - \beta \sum_y \pi(y) \log \frac{\pi(y)}{\pi_{\text{ref}}(y)}.$$

The first term came from $\mathbb{E}_{y \sim \pi}[r(x, y)] = \sum_y \pi(y) r(y)$. The second came from expanding the KL divergence definition.

We need to maximize this over $\pi$, with the constraints $\pi(y) \geq 0$ and $\sum_y \pi(y) = 1$. The non-negativity will turn out to be automatically satisfied by the optimum, so we only need a Lagrange multiplier for normalization.

### Setting up the Lagrangian

Introduce Lagrange multiplier $\lambda$ for the normalization constraint:

$$\mathcal{L}[\pi, \lambda] = L[\pi] - \lambda \left( \sum_y \pi(y) - 1 \right).$$

Expanded:

$$\mathcal{L}[\pi, \lambda] = \sum_y \pi(y) r(y) - \beta \sum_y \pi(y) \log \frac{\pi(y)}{\pi_{\text{ref}}(y)} - \lambda \left( \sum_y \pi(y) - 1 \right).$$

To find the optimum, take the partial derivative with respect to $\pi(y)$ for each $y$ and set it to zero.

### Computing the partial derivatives

The first term: $\frac{\partial}{\partial \pi(y)} \sum_{y'} \pi(y') r(y') = r(y)$. (Only the $y' = y$ term contributes, and $r(y)$ doesn't depend on $\pi(y)$.)

The second term is more involved. Expand:

$$-\beta \sum_{y'} \pi(y') \log \frac{\pi(y')}{\pi_{\text{ref}}(y')} = -\beta \sum_{y'} \pi(y') \big[\log \pi(y') - \log \pi_{\text{ref}}(y')\big].$$

Differentiate with respect to $\pi(y)$. Only the $y' = y$ term contributes:

$$-\beta \frac{\partial}{\partial \pi(y)} \big[\pi(y) \log \pi(y) - \pi(y) \log \pi_{\text{ref}}(y)\big].$$

The piece $\frac{\partial}{\partial \pi(y)} [\pi(y) \log \pi_{\text{ref}}(y)] = \log \pi_{\text{ref}}(y)$ since $\log \pi_{\text{ref}}(y)$ is constant with respect to $\pi(y)$.

The piece $\frac{\partial}{\partial \pi(y)} [\pi(y) \log \pi(y)]$: by the product rule, $\log \pi(y) + \pi(y) \cdot \frac{1}{\pi(y)} = \log \pi(y) + 1$.

So the full second-term derivative is:

$$-\beta [\log \pi(y) + 1 - \log \pi_{\text{ref}}(y)] = -\beta \left[ \log \frac{\pi(y)}{\pi_{\text{ref}}(y)} + 1 \right].$$

The third term: $\frac{\partial}{\partial \pi(y)} \big[-\lambda (\sum_{y'} \pi(y') - 1)\big] = -\lambda$.

Adding up:

$$\frac{\partial \mathcal{L}}{\partial \pi(y)} = r(y) - \beta \left[ \log \frac{\pi(y)}{\pi_{\text{ref}}(y)} + 1 \right] - \lambda.$$

Setting this to zero:

$$r(y) - \beta \log \frac{\pi(y)}{\pi_{\text{ref}}(y)} - \beta - \lambda = 0.$$

### Solving for $\pi$

Rearrange:

$$\beta \log \frac{\pi(y)}{\pi_{\text{ref}}(y)} = r(y) - \beta - \lambda.$$

Divide by $\beta$:

$$\log \frac{\pi(y)}{\pi_{\text{ref}}(y)} = \frac{r(y)}{\beta} - 1 - \frac{\lambda}{\beta}.$$

Exponentiate:

$$\frac{\pi(y)}{\pi_{\text{ref}}(y)} = \exp\left( \frac{r(y)}{\beta} \right) \cdot e^{-1 - \lambda/\beta}.$$

So:

$$\pi(y) = \pi_{\text{ref}}(y) \cdot \exp\left( \frac{r(y)}{\beta} \right) \cdot e^{-1 - \lambda/\beta}.$$

The factor $e^{-1 - \lambda/\beta}$ doesn't depend on $y$. Call it $1/Z$:

$$\pi(y) = \frac{1}{Z} \pi_{\text{ref}}(y) \exp\left( \frac{r(y)}{\beta} \right).$$

The normalization constant $Z$ is determined by the requirement $\sum_y \pi(y) = 1$:

$$Z = \sum_y \pi_{\text{ref}}(y) \exp\left( \frac{r(y)}{\beta} \right).$$

### Restoring the prompt dependence

Putting $x$ back in:

$$\boxed{\pi^*(y \mid x) = \frac{1}{Z(x)} \, \pi_{\text{ref}}(y \mid x) \, \exp\left( \frac{r(x, y)}{\beta} \right)}$$

with

$$Z(x) = \sum_y \pi_{\text{ref}}(y \mid x) \exp\left( \frac{r(x, y)}{\beta} \right).$$

This is the *exponential tilt* of the reference policy by the (rescaled) reward function. It's the optimal policy for the KL-regularized objective.

### Recognizing the structure

This formula has the same structure as several classical objects:

**Boltzmann distribution.** If $\pi_{\text{ref}}$ is uniform and $E(y) = -r(y)$, the formula becomes $\pi^*(y) \propto \exp(-E(y)/\beta)$. This is the Boltzmann distribution at inverse temperature $1/\beta$.

**Bayesian posterior.** With $\pi_{\text{ref}}$ a prior and $\exp(r/\beta)$ a likelihood, you get posterior $\propto$ prior $\times$ likelihood.

**Maximum entropy with constraints.** Maximizing entropy subject to $\mathbb{E}_\pi[f] = c$ gives $\pi \propto e^{-\lambda f}$.

These aren't analogies. The mathematical structure is the same, and we can use techniques from these fields when analyzing $\pi^*$.

### Reading off $\rho$

Take the log of $\pi^*(y \mid x)$:

$$\log \pi^*(y \mid x) = \log \pi_{\text{ref}}(y \mid x) + \frac{r(x, y)}{\beta} - \log Z(x).$$

If we identify $P_{\text{inst}}(y \mid x) = \pi^*(y \mid x)$ and $P_{\text{base}}(y \mid x) = \pi_{\text{ref}}(y \mid x)$:

$$\rho(x, y) = \log P_{\text{inst}}(y \mid x) - \log P_{\text{base}}(y \mid x) = \frac{r(x, y)}{\beta} - \log Z(x).$$

The probability distortion is the (rescaled) reward minus a normalization that depends only on $x$.

### Caveats on the identification

The identification $P_{\text{base}} = \pi_{\text{ref}}$ deserves a moment.

In production alignment pipelines, training is multi-stage:

1. *Pretraining* gives parameters $\theta_0$ and policy $\pi_0 = P_{\text{base}}$.
2. *Supervised fine-tuning* (SFT) takes $\pi_0$ as starting point and produces $\pi_{\text{SFT}}$.
3. *RLHF* uses $\pi_{\text{SFT}}$ as the reference policy $\pi_{\text{ref}}$ and produces $\pi^* = \pi_{\text{RLHF}}$.

So $\pi_{\text{ref}}$ is the post-SFT model, not the post-pretraining base model. The closed form gives us the distortion *from $\pi_{\text{ref}}$ to $\pi^*$*, which is the RLHF stage's contribution.

For total distortion from base to fully-trained:

$$\rho_{\text{total}}(x, y) = \rho_{\text{SFT}}(x, y) + \rho_{\text{RLHF}}(x, y)$$

where $\rho_{\text{SFT}}$ is the distortion introduced by SFT and $\rho_{\text{RLHF}}$ is what we just computed. Total distortion is additive across stages in the log domain.

### Relative distortion within a prompt

The normalization $\log Z(x)$ doesn't depend on which completion $y$ we ask about. So:

$$\rho(x, y_1) - \rho(x, y_2) = \frac{r(x, y_1) - r(x, y_2)}{\beta}.$$

This is exact. The relative distortion between two completions of the same prompt is the relative reward, scaled by $1/\beta$. The normalization cancels.

This means: even without computing $Z(x)$, we can measure relative distortion by comparing two completions on the same prompt. And the relative distortion directly reveals the relative reward, up to the scaling factor $\beta$.

### What we've established

For an idealized RLHF pipeline:

1. The optimal policy has the closed form $\pi^* \propto \pi_{\text{ref}} \exp(r/\beta)$.
2. The probability distortion is $\rho = r/\beta - \log Z(x)$.
3. Measuring $\rho^*$ recovers the reward function up to a per-prompt constant.

The third point is the methodological foundation of the framework. Whatever shaping is present in $\rho$ reflects what the reward model preferred and disfavored. Reverse-engineering the structure of $\rho$ is reverse-engineering the structure of the institutional reward signal.

---

## Part 3: How $\rho$ arises from training dynamics

The closed form in Part 2 tells us what $\rho$ is at the optimum — when training has fully converged. But it doesn't tell us *how* training gets there, or what happens along the way.

### Gradient flow

The simplest model of training is *gradient flow*. Maximizing $\mathcal{R}(\theta)$ over parameters $\theta$ via gradient ascent with infinitesimal step size gives:

$$\frac{d\theta_t}{dt} = \nabla_\theta \mathcal{R}(\theta_t).$$

Here $t$ is "training time" (a continuous version of "training step number"), and $\nabla_\theta \mathcal{R}$ is the gradient of the objective with respect to parameters.

For our RLHF case:

$$\mathcal{R}(\theta) = \mathbb{E}_{x, y \sim \pi_\theta}[r(x, y)] - \beta \, \mathbb{E}_x[D_{\text{KL}}(\pi_\theta \,\|\, \pi_{\text{ref}})].$$

We need to compute its gradient.

### The policy gradient theorem

Computing $\nabla_\theta \mathcal{R}(\theta)$ requires care because $\theta$ appears both inside the expectation (in $\pi_\theta$) and in the function being averaged. We use the "log-derivative trick."

Consider just the reward term, $\mathbb{E}_{y \sim \pi_\theta}[r(x, y)]$. Expand:

$$\mathbb{E}_{y \sim \pi_\theta}[r(x, y)] = \sum_y \pi_\theta(y \mid x) \, r(x, y).$$

Take the gradient (the reward $r$ doesn't depend on $\theta$):

$$\nabla_\theta \mathbb{E}_{y \sim \pi_\theta}[r(x, y)] = \sum_y r(x, y) \nabla_\theta \pi_\theta(y \mid x).$$

The trick is to rewrite $\nabla_\theta \pi_\theta = \pi_\theta \nabla_\theta \log \pi_\theta$. To verify: $\nabla_\theta \log \pi_\theta = \frac{1}{\pi_\theta} \nabla_\theta \pi_\theta$, so $\pi_\theta \nabla_\theta \log \pi_\theta = \nabla_\theta \pi_\theta$. Substituting:

$$\nabla_\theta \mathbb{E}_{y \sim \pi_\theta}[r(x, y)] = \sum_y r(x, y) \pi_\theta(y \mid x) \nabla_\theta \log \pi_\theta(y \mid x) = \mathbb{E}_{y \sim \pi_\theta}\big[ r(x, y) \nabla_\theta \log \pi_\theta(y \mid x) \big].$$

The function $\nabla_\theta \log \pi_\theta(y \mid x)$ is called the *score function*. It points in the direction in parameter space that most rapidly increases the probability of generating $y$ given $x$. The policy gradient says: to increase expected reward, move in the score-function direction, weighted by reward.

### Gradient of the KL term

For the KL term, similar manipulation. Start with:

$$D_{\text{KL}}(\pi_\theta \,\|\, \pi_{\text{ref}}) = \sum_y \pi_\theta(y) \big[\log \pi_\theta(y) - \log \pi_{\text{ref}}(y)\big].$$

Take the gradient (using the product rule):

$$\nabla_\theta D_{\text{KL}} = \sum_y \big[ \nabla_\theta \pi_\theta(y) \cdot (\log \pi_\theta(y) - \log \pi_{\text{ref}}(y)) + \pi_\theta(y) \cdot \nabla_\theta \log \pi_\theta(y) \big].$$

The first term, by the log-derivative trick:

$$\sum_y \nabla_\theta \pi_\theta(y) (\log \pi_\theta - \log \pi_{\text{ref}}) = \mathbb{E}_{y \sim \pi_\theta}[(\log \pi_\theta - \log \pi_{\text{ref}}) \nabla_\theta \log \pi_\theta].$$

The second term: $\sum_y \pi_\theta(y) \nabla_\theta \log \pi_\theta(y) = \nabla_\theta \sum_y \pi_\theta(y) = \nabla_\theta 1 = 0$. (The score function has mean zero under its own distribution — a general property.)

So:

$$\nabla_\theta D_{\text{KL}}(\pi_\theta \,\|\, \pi_{\text{ref}}) = \mathbb{E}_{y \sim \pi_\theta}\big[ (\log \pi_\theta(y) - \log \pi_{\text{ref}}(y)) \nabla_\theta \log \pi_\theta(y) \big].$$

### Combining

The full objective gradient:

$$\nabla_\theta \mathcal{R}(\theta) = \mathbb{E}_{x \sim \mathcal{D}, \, y \sim \pi_\theta(\cdot \mid x)}\Big[ \big(r(x, y) - \beta \log \tfrac{\pi_\theta(y \mid x)}{\pi_{\text{ref}}(y \mid x)}\big) \nabla_\theta \log \pi_\theta(y \mid x) \Big].$$

The thing in parentheses is the "advantage" — how much better than reference this completion is, accounting for both reward and drift from reference.

### From parameter trajectory to $\rho$ trajectory

Along the gradient flow trajectory, we have a one-parameter family of policies $\pi_t = \pi_{\theta_t}$. The time-resolved distortion:

$$\rho_t(x, y) = \log \pi_t(y \mid x) - \log \pi_0(y \mid x).$$

At $t = 0$, $\rho_0 = 0$ identically. As training proceeds, $\rho_t$ develops structure.

How does $\rho_t$ evolve? Since $\pi_t = \pi_{\theta_t}$ depends on $t$ through $\theta_t$:

$$\frac{d\rho_t(x, y)}{dt} = \frac{d}{dt} \log \pi_t(y \mid x) = \nabla_\theta \log \pi_\theta(y \mid x) \big|_{\theta_t} \cdot \frac{d\theta_t}{dt}.$$

Using $d\theta_t/dt = \nabla_\theta \mathcal{R}(\theta_t)$:

$$\frac{d\rho_t(x, y)}{dt} = \nabla_\theta \log \pi_t(y \mid x) \cdot \nabla_\theta \mathcal{R}(\theta_t).$$

This is a key formula. **The rate of distortion change at $(x, y)$ is the inner product, in parameter space, between the score function for $(x, y)$ and the training direction.**

When these are aligned, $\rho$ at $(x, y)$ grows quickly. When orthogonal, $\rho$ doesn't change. When anti-aligned, $\rho$ decreases.

### Total distortion as a path integral

Integrating from $0$ to $T$:

$$\rho(x, y) = \int_0^T \nabla_\theta \log \pi_t(y \mid x) \cdot \nabla_\theta \mathcal{R}(\theta_t) \, dt.$$

This is exact along any specific trajectory. It's a path integral along the training trajectory.

The expression has two pieces:

- $\nabla_\theta \log \pi_t(y \mid x)$: the score function at $(x, y)$, evaluated at the current parameters.
- $\nabla_\theta \mathcal{R}(\theta_t)$: the training direction at the current parameters.

For the framework, this exact expression is the foundation. Approximations to it give us the various theoretical tools we'll develop.

---

## Part 4: First-order theory — the neural tangent kernel

The path integral expression for $\rho$ is exact but hard to work with. We need approximations. The simplest is to *linearize* — Taylor expand around the starting point $\theta_0$.

### Taylor expansion in $\Delta\theta$

Define $f(\theta) = \log \pi_\theta(y \mid x)$ for fixed $(x, y)$. The distortion is $\rho(x, y) = f(\theta_T) - f(\theta_0)$.

Taylor expand $f$ around $\theta_0$:

$$f(\theta_T) = f(\theta_0) + \nabla_\theta f(\theta_0) \cdot \Delta\theta + \tfrac{1}{2} \Delta\theta^T \nabla^2_\theta f(\theta_0) \, \Delta\theta + \cdots$$

where $\Delta\theta = \theta_T - \theta_0$.

Subtracting $f(\theta_0)$:

$$\rho(x, y) = g(x, y) \cdot \Delta\theta + \tfrac{1}{2} \Delta\theta^T H(x, y) \Delta\theta + \cdots$$

where:

$$g(x, y) = \nabla_\theta \log \pi_\theta(y \mid x) \big|_{\theta_0} \quad \text{(score function at base)}$$

$$H(x, y) = \nabla^2_\theta \log \pi_\theta(y \mid x) \big|_{\theta_0} \quad \text{(Hessian at base)}.$$

Truncating at first order:

$$\rho(x, y) \approx g(x, y) \cdot \Delta\theta.$$

### What is $\Delta\theta$?

$\Delta\theta$ is the cumulative parameter update from training. In gradient flow:

$$\Delta\theta = \int_0^T \nabla_\theta \mathcal{R}(\theta_t) \, dt.$$

For stochastic training where we sample examples and update on each, write the cumulative update as a sum over training examples. Each example $i$ contributes a gradient. Approximating these gradients as evaluated at $\theta_0$ (the *lazy* approximation):

$$\Delta\theta \approx \sum_i \eta_i \, a_i \, g(x_i, y_i)$$

where the sum runs over training examples, $\eta_i$ is the effective learning rate, $a_i$ is the advantage signal, and $g(x_i, y_i)$ is the score function at base for the training example.

### The kernel emerges

Substitute into the linear approximation:

$$\rho(x, y) \approx g(x, y) \cdot \sum_i \eta_i a_i g(x_i, y_i) = \sum_i \eta_i a_i \, \big[ g(x, y) \cdot g(x_i, y_i) \big].$$

Define the *neural tangent kernel*:

$$\boxed{K\big((x, y), (x', y')\big) = g(x, y) \cdot g(x', y') = \nabla_\theta \log \pi_{\theta_0}(y \mid x) \cdot \nabla_\theta \log \pi_{\theta_0}(y' \mid x').}$$

This is the inner product of score functions in parameter space. In terms of the kernel:

$$\rho(x, y) \approx \sum_i \eta_i a_i \, K\big((x, y), (x_i, y_i)\big).$$

The distortion at any test point $(x, y)$ is a weighted sum of kernel values to the training points, where the weights are training advantages.

### Properties of the kernel

The NTK is **symmetric**: $K((x, y), (x', y')) = K((x', y'), (x, y))$.

The NTK is **positive semi-definite**. For any function $\alpha$ and any set of points $\{(x_i, y_i)\}$:

$$\sum_{i, j} \alpha_i \alpha_j K\big((x_i, y_i), (x_j, y_j)\big) = \sum_{i, j} \alpha_i \alpha_j g(x_i, y_i) \cdot g(x_j, y_j) = \Big\| \sum_i \alpha_i g(x_i, y_i) \Big\|^2 \geq 0.$$

This makes $K$ a valid kernel — it defines an inner product in some feature space.

The NTK has an **eigendecomposition**:

$$K\big((x, y), (x', y')\big) = \sum_k \lambda_k \, \phi_k(x, y) \, \phi_k(x', y')$$

where $\lambda_k \geq 0$ are eigenvalues and $\phi_k$ are eigenfunctions forming a complete orthonormal basis.

### The eigenmode picture

The eigenfunctions $\phi_k$ are the natural "modes" of the model's representation space. Each mode has its own learning dynamics governed by its eigenvalue.

When training is decomposed into eigenmodes, each mode evolves independently. Modes with large eigenvalues are "easy to learn" — small training signal in that direction produces large distortion. Modes with small eigenvalues are "hard to learn" — even strong training in that direction produces little distortion.

### Propagation of distortion across topics

The NTK formula tells us how training propagates from training points to test points. Suppose training reinforces specific framings on prompts about Wehrmacht ethnic composition. The kernel structure determines what other prompts get affected:

If a test prompt has score-function gradient aligned with the training prompts' gradients, $K$ is large between them. Distortion at the test prompt mirrors training.

If the gradient is orthogonal, $K$ is small. Distortion is unaffected.

Semantically and structurally similar prompts have aligned gradients — they activate similar parameters in similar directions. So topics that are "near" each other are coupled by the kernel.

This is the mathematical basis for why institutional shaping spreads coherently. The institutions explicitly train on a manageable number of examples; the kernel takes care of generalizing the shaping.

### When NTK is good and when it isn't

The NTK approximation requires:

The parameter updates $\Delta\theta$ are small enough that score functions at $\theta_0$ are good approximations along the trajectory.

The model is in the "lazy" regime where features don't change much during training.

The training signal doesn't push parameters into regions of high curvature.

For the framework: NTK gives us **qualitative predictions about how distortion spreads** that hold in broad form. It doesn't give **quantitative magnitudes** that match observation in heavily-trained regions.

We need to go beyond NTK for quantitative theory.

---

## Part 5: Beyond NTK — feature learning

### Why the kernel moves

The kernel $K((x, y), (x', y'))$ is built from score functions at $\theta_0$. As parameters change, the score functions change too:

$$\nabla_\theta \log \pi_{\theta_t}(y \mid x) \approx g(x, y) + H(x, y) \cdot (\theta_t - \theta_0) + \cdots$$

The score function at time $t$ is approximately the original score function plus a Hessian-weighted correction. So the kernel evolves:

$$K_t\big((x, y), (x', y')\big) = \nabla_\theta \log \pi_{\theta_t}(y \mid x) \cdot \nabla_\theta \log \pi_{\theta_t}(y' \mid x').$$

The propagation structure of distortion at later times is governed by $K_t$, not $K_0$.

### The mean-field parameterization

There are different ways to set up the limit of infinite-width networks. **Standard parameterization** has the kernel fixed in the infinite-width limit (the original NTK regime; only the output layer effectively trains). **Mean-field parameterization** ($\mu$P, Yang and Hu 2021) has features continuing to learn during training, even at infinite width.

For our purposes: mean-field is the "feature learning" regime. NTK is the "lazy" regime. Real alignment training is somewhere in between, often closer to feature learning.

### Implications for $\rho$

In the mean-field regime, the kernel evolves during training. The first-order NTK formula is replaced by something like:

$$\rho(x, y) \approx \int_0^T dt \, \mathbb{E}_i\big[ \eta_i a_i^{(t)} K_t\big((x, y), (x_i, y_i)\big) \big].$$

Both the kernel and the advantages evolve.

This is harder mathematically but addresses a real phenomenon: alignment training does change internal representations. New features emerge that better encode institutional commitments.

### Practical takeaway

For the framework's measurement program: when alignment training produces strong distortion, the standard NTK kernel is wrong. The effective kernel is the trajectory-averaged kernel, not the initial one.

The trajectory-averaged kernel is itself measurable from differential probes. If $\rho^*(x, y)$ and $\rho^*(x', y')$ are highly correlated across many training conditions, that's evidence the effective kernel has large value between those points. The framework can use $\rho^*$ correlations across probes to estimate the effective propagation kernel without needing access to the actual training trajectory.

---

## Part 6: The path integral formulation

The path integral perspective treats the training trajectory as a path through parameter space and writes the distortion as an integral along this path. This is the most general formulation — it doesn't depend on Taylor expansion at any reference point, so it works in regimes where linear approximation fails.

### The exact expression

From Part 3:

$$\rho(x, y) = \int_0^T \nabla_\theta \log \pi_t(y \mid x) \cdot \frac{d\theta_t}{dt} dt.$$

This is exact along any specific trajectory $\theta_t$. No expansion in $\Delta\theta$, no approximation. The price is needing the trajectory, or computing averages over an ensemble.

### Stochastic training

Real training has noise from minibatch SGD, learning rate schedules, optimizer momentum. Model this with a stochastic differential equation:

$$\frac{d\theta_t}{dt} = \nabla_\theta \mathcal{R}(\theta_t) + \xi_t$$

where $\xi_t$ is a Gaussian noise process. The solution is a probability distribution over trajectories.

### The Onsager-Machlup functional

For an SDE $d\theta_t = b(\theta_t) dt + \sigma \, dW_t$, the probability of a specific trajectory $\theta(\cdot)$ is given by the *Onsager-Machlup density*:

$$P[\theta(\cdot)] \propto \exp\left( -\frac{1}{2} \int_0^T \big\| \sigma^{-1}(\dot{\theta}_t - b(\theta_t)) \big\|^2 dt \right).$$

For our case with $b(\theta) = \nabla_\theta \mathcal{R}$ and isotropic noise:

$$P[\theta(\cdot)] \propto \exp\left( -\frac{1}{2\sigma_{\text{noise}}^2} \int_0^T \big\| \dot{\theta}_t - \nabla_\theta \mathcal{R}(\theta_t) \big\|^2 dt \right).$$

The exponent is the *action functional* for trajectories. Trajectories that follow gradient flow exactly have zero action and are most likely. Trajectories that stray have action proportional to squared deviation.

### What is a path integral

A path integral is an integral over the space of trajectories:

$$\int \mathcal{D}[\theta(\cdot)] \, F[\theta(\cdot)]$$

means "integrate $F$ over all possible trajectories." For finite-dimensional parameter spaces, you can think of it as a limit of integrals over discretized paths, where the number of time points goes to infinity.

### Expected distortion

$$\mathbb{E}[\rho(x, y)] = \int \mathcal{D}[\theta(\cdot)] \, P[\theta(\cdot)] \, \rho[\theta(\cdot)](x, y).$$

Computing this exactly is intractable for high-dimensional $\theta$. But the path integral has several uses:

**Saddle-point approximation.** The dominant contribution comes from trajectories that maximize $P[\theta(\cdot)]$, which are gradient-flow trajectories. The leading-order result is to evaluate $\rho$ along the deterministic trajectory.

**Fluctuation analysis.** Around the saddle point, fluctuations have a Gaussian distribution with width set by $\sigma_{\text{noise}}$. This gives the variance of $\rho$ across multiple training runs with different seeds.

**Instanton transitions.** When the action has multiple saddle points (different basins of attraction), the trajectory can tunnel between them. We'll see this matters for mode collapse.

### Connection to physics

The path integral structure is the same as in physics:

In quantum mechanics, the propagator $\langle x_T | x_0 \rangle$ is a path integral over paths weighted by $e^{iS/\hbar}$.

In statistical mechanics (after Wick rotation), the partition function is a path integral over configurations weighted by $e^{-S/k_B T}$.

In neural network training, the expected observable is a path integral over training trajectories weighted by $e^{-\text{Onsager-Machlup}}$.

The same techniques apply: saddle-point expansions, instanton analysis, perturbation theory around classical solutions, renormalization group flow.

### Mode collapse as instantons

*Mode collapse* is when training drives a specific completion to be near-deterministic — $P_{\text{inst}}(y_0 \mid x) \approx 1$ for some specific $y_0$. It often appears as a sharp transition during training: below threshold, the distribution is broad; above, mass concentrates on a specific completion.

Mathematically, this looks like the trajectory crossing a barrier between two basins of attraction. Below threshold, the trajectory is in the basin around $\theta_0$; above, it's in a different basin where $\pi(y_0 \mid x)$ is much larger.

Crossing such barriers is an *instanton* phenomenon. The "action" of the instanton (the value of the Onsager-Machlup functional along the barrier-crossing path) determines the rate of transition.

For the framework: mode collapse explains why some falsification targets show 0% to 80%+ amplification rather than gradual increases. The transition is non-perturbative — Taylor expansion at $\theta_0$ doesn't capture it. Path-integral / instanton analysis handles it cleanly.

### What the path integral gets us

Regimes where Taylor at $\theta_0$ fails:

**Large parameter changes:** Path integral integrates along the actual trajectory.

**Mode collapse:** Multiple saddle points become relevant; instanton contributions matter.

**Multi-stage training:** Each stage contributes its own action; composition is straightforward.

The path-integral formulation is the right object for theoretical analysis. Practical computation requires approximations — saddle point, semiclassical, effective theory — but the formulation itself is exact.

---

## Part 7: Asymptotic series, divergence, and what to do about it

Taylor expansion of $\rho$ at $\theta_0$ may not converge in the strong-shaping regime. This isn't a failure of the framework — divergent series are well-studied in physics with developed mathematical apparatus.

### Convergent vs asymptotic series

A power series $\sum_k a_k z^k$ is *convergent* at $z$ if partial sums $\sum_{k=0}^N a_k z^k$ approach a limit as $N \to \infty$.

A power series is *asymptotic* to a function $f$ at $z = 0$ if for each fixed $N$:

$$\big| f(z) - \sum_{k=0}^N a_k z^k \big| \leq C_N |z|^{N+1} \quad \text{as } z \to 0.$$

The $C_N$ can grow with $N$. The series might not converge for any fixed $z$, but for small enough $z$, partial sums are close to $f(z)$.

For convergent series, more terms is always better. For asymptotic-but-divergent series, more terms is better up to some optimal point, and worse beyond.

### A canonical example

$$f(z) = \int_0^\infty \frac{e^{-t}}{1 + zt} dt.$$

Expanding $1/(1 + zt) = \sum_k (-zt)^k$ and integrating term-by-term (formally):

$$f(z) \stackrel{?}{=} \sum_k (-z)^k \int_0^\infty t^k e^{-t} dt = \sum_k (-1)^k k! \, z^k.$$

The coefficients $a_k = (-1)^k k!$ grow as $k!$. The radius of convergence is zero — the series doesn't converge for any nonzero $z$.

But it's asymptotic. For small $z > 0$, partial sums approach $f(z)$ to within an error that decreases for a while as $N$ grows, then starts increasing.

### Optimal truncation

For a series with coefficients growing like $k!/A^k$, the partial sum closest to the true value is at $N \approx A/|z|$. The error at optimal truncation is approximately $e^{-A/|z|}$ — exponentially small in $1/|z|$.

This is why asymptotic series are useful: optimal truncation gives exponentially good approximations, even when the series diverges.

For QED in physics, the perturbative expansion in fine-structure constant $\alpha \approx 1/137$ has factorially-growing coefficients, but optimal truncation gives errors $\sim e^{-137}$, which is unmeasurably small. This is why QED works.

### Borel summation

Sometimes we can do better than optimal truncation. *Borel summation* recovers the underlying function from a divergent series.

Given $\sum_k a_k z^k$ with $a_k \sim k!/A^k$, define the *Borel transform*:

$$B(t) = \sum_k \frac{a_k}{k!} t^k.$$

The factorial growth of $a_k$ is canceled, and $B(t)$ has a nonzero radius of convergence.

If $B(t)$ can be analytically continued to the positive real axis, the *Borel sum* is:

$$f_{\text{Borel}}(z) = \int_0^\infty e^{-t} B(zt) \, dt.$$

For many physical examples, this recovers the true function exactly.

The procedure can fail if $B(t)$ has singularities on the positive real axis — *Borel singularities* signaling that the asymptotic series is missing non-perturbative contributions.

### Trans-series and resurgence

The modern view (Écalle and others, since the 1980s): the full answer often takes the form of a *trans-series*:

$$f(z) = \underbrace{\sum_k a_k z^k}_{\text{perturbative}} + \underbrace{e^{-A/z} \sum_k b_k z^k}_{\text{1-instanton}} + \underbrace{e^{-2A/z} \sum_k c_k z^k}_{\text{2-instanton}} + \cdots$$

The first sum is the standard asymptotic series. The exponential factors $e^{-nA/z}$ represent contributions from $n$-instanton sectors — non-perturbative effects.

The remarkable fact: the coefficients $b_k, c_k, \ldots$ are *not* independent of the perturbative coefficients $a_k$. They're determined by the large-order behavior of $a_k$ via *resurgence relations*. If $a_k \sim k!/A^k$ at large $k$, the leading instanton contribution has prefactor proportional to $e^{-A/z}$.

The information about non-perturbative phenomena is encoded in the divergence pattern of the perturbative series.

### Application to $\rho$

For our problem: in the strong-shaping regime, the Taylor expansion of $\rho$ at $\theta_0$ is asymptotic but divergent. The mathematical apparatus tells us:

Optimal truncation gives errors that are exponentially small. Finite-order with appropriate truncation works.

Borel summation may recover the exact $\rho$ from the asymptotic expansion in some regimes.

The trans-series structure means mode collapse can be predicted from the large-order behavior of the perturbative expansion. Factorial growth of Taylor coefficients of $\log P(y \mid x; \theta)$ at $\theta_0$ would predict mode-collapse transitions with action $A$ given by the growth rate.

This is concrete: by computing high-order Taylor coefficients of $\log \pi_\theta$ numerically, we can predict mode collapse without leaving the perturbative regime.

### Why this matters for the framework

Mode collapse isn't "beyond mathematical prediction" — it's the standard non-perturbative regime that has been studied for decades in physics, with developed tools that apply here. Perturbation theory *does* predict mode collapse, through its large-order behavior.


---

## Part 8: Information geometry — the natural metric on $\rho$

Probability distributions live on a curved manifold. The geometry has consequences for what $\rho$ looks like and what counts as natural distance between $P_{\text{base}}$ and $P_{\text{inst}}$.

### The probability simplex

The set of probability distributions over a finite set is the *simplex*:

$$\Delta^{n-1} = \{p \in \mathbb{R}^n : p_i \geq 0, \sum_i p_i = 1\}.$$

This is a flat object in the embedding $\mathbb{R}^n$. But the *natural geometry* on it isn't flat. The right metric, derived by Chentsov in 1972, is the *Fisher information metric*.

### Fisher information

For a parametric family of distributions $\{P_\theta\}$, the *Fisher information matrix* is:

$$g_{ij}(\theta) = \mathbb{E}_{x \sim P_\theta}\left[ \frac{\partial \log P_\theta(x)}{\partial \theta_i} \frac{\partial \log P_\theta(x)}{\partial \theta_j} \right].$$

This is the variance of the score function under $P_\theta$. It tells us how much information observations $x$ contain about parameters $\theta$.

For language models, this is the Fisher information of the policy with respect to its parameters. It tells us, for each parameter direction, how strongly perturbing that direction changes the output distribution.

### Fisher metric on the simplex

For distributions on a finite set, with $\theta_i = p_i$:

$$g_{ij}(p) = \frac{\delta_{ij}}{p_i}.$$

A diagonal matrix with entries $1/p_i$. The squared line element is $ds^2 = \sum_i dp_i^2 / p_i$.

This metric has a specific feature: it blows up near the boundary of the simplex, where some $p_i \to 0$. Distinct distributions both near the boundary are far apart in Fisher distance, even though they look close in Euclidean distance.

This is qualitatively right. Two distributions disagreeing at the 1% level (one says 1%, other says 2%) feel more different than two disagreeing at the 50% level (one says 50%, other says 51%) — the relative discrepancy is larger.

### Geodesic distance

The geodesic distance under the Fisher metric, between two distributions $p$ and $q$, can be computed using the parametrization $\sqrt{p_i} = \cos(\phi_i / 2)$. The result, due to Bhattacharyya:

$$d_F(p, q) = 2 \arccos\left( \sum_i \sqrt{p_i q_i} \right).$$

The thing inside the arccos is the *Bhattacharyya coefficient*. The Fisher distance is bounded between 0 and $\pi$.

### KL divergence and Fisher

The KL divergence $D_{\text{KL}}(p \| q)$ isn't a distance, but it has a relation to the Fisher metric.

For nearby distributions $p$ and $q = p + dp$:

$$D_{\text{KL}}(p \| p + dp) \approx \frac{1}{2} \sum_i \frac{(dp_i)^2}{p_i} = \frac{1}{2} ds^2.$$

KL divergence locally equals half the squared Fisher distance.

Quick derivation: $D_{\text{KL}}(p \| p + dp) = \sum_i p_i \log(p_i/(p_i + dp_i)) = -\sum_i p_i \log(1 + dp_i/p_i)$. Expanding $\log(1 + u) = u - u^2/2 + \cdots$: $-\sum_i p_i [dp_i/p_i - (dp_i)^2/(2p_i^2) + \cdots] = -\sum_i dp_i + \sum_i (dp_i)^2/(2p_i) + \cdots$. The first term vanishes since $\sum_i dp_i = 0$. The remaining gives the result.

### Application to $\rho$

The probability distortion $\rho$ encodes the displacement from $P_{\text{base}}$ to $P_{\text{inst}}$ on the statistical manifold. We can ask: how far did training move the distribution, geometrically?

For a single prompt $x$:

$$D_{\text{KL}}(P_{\text{inst}} \| P_{\text{base}}) = \sum_y P_{\text{inst}}(y \mid x) \rho(x, y) = \mathbb{E}_{P_{\text{inst}}}[\rho].$$

This is the average distortion under the post-training distribution — the "information distance" by which the post-training policy has moved from base.

The reverse KL:

$$D_{\text{KL}}(P_{\text{base}} \| P_{\text{inst}}) = -\mathbb{E}_{P_{\text{base}}}[\rho].$$

Both are summary measures with different operational meanings: forward KL emphasizes completions the trained model produces; reverse KL emphasizes completions the base produced.

### Geodesics in distribution space

The geodesic from $P_{\text{base}}$ to $P_{\text{inst}}$ on the Fisher-geometric simplex is *not* a straight line in probability coordinates. It's the *log-linear* interpolation:

$$P_\lambda(y \mid x) \propto P_{\text{base}}(y \mid x)^{1-\lambda} P_{\text{inst}}(y \mid x)^\lambda.$$

Taking logs:

$$\log P_\lambda(y \mid x) = (1-\lambda) \log P_{\text{base}}(y \mid x) + \lambda \log P_{\text{inst}}(y \mid x) - \log Z_\lambda(x)$$

$$= \log P_{\text{base}}(y \mid x) + \lambda \rho(x, y) - \log Z_\lambda(x).$$

So $P_\lambda$ corresponds to scaled distortion $\lambda \rho$, with normalization $Z_\lambda(x)$. Varying $\lambda$ from 0 to 1 traces out the family of distortions from "no training" to "full training," geometrically.

In the framework, this gives us a way to study intermediate behavior of training without intermediate checkpoints. Sampling from $P_\lambda$ at different $\lambda$ traces the geodesic between base and trained.

### Fisher matrix in parameter coordinates

For language models, the parameter space is high-dimensional but the policy manifold is a low-dimensional submanifold of the probability simplex. The relevant Fisher matrix is in *parameter* coordinates:

$$g_{ij}(\theta) = \mathbb{E}_{x, y \sim P_\theta}\left[ \frac{\partial \log P_\theta(y \mid x)}{\partial \theta_i} \frac{\partial \log P_\theta(y \mid x)}{\partial \theta_j} \right].$$

This is what *natural gradient descent* uses as a metric. Parameters that strongly affect the output have large diagonal elements; parameters that are "redundant" have small diagonal elements.

The relevance: training updates moving along directions of small Fisher metric have small effect on $\rho$. Updates along large-Fisher-metric directions have large effect.

### Summary

The Fisher-geometric perspective:

The natural distance between $P_{\text{base}}$ and $P_{\text{inst}}$ is $D_{\text{KL}}$, not raw probability differences.

Mode collapse is geometric: the trained policy concentrates near a corner of the simplex, far from base in Fisher distance.

The natural interpolation between base and trained is log-linear, not linear.

The Fisher information matrix in parameter space measures how much each parameter direction affects the output.

---

## Part 9: Renormalization group — coarse-graining the shaping

Training operates on millions or billions of parameters with detailed update steps. The institutional shaping signature is a low-dimensional summary of what all that training collectively did. RG techniques formalize the connection.

### The basic RG picture

In statistical mechanics, RG starts with a microscopic model and produces an effective model at a coarser scale by *integrating out* fast (high-frequency) degrees of freedom. The procedure:

1. Start with a microscopic Hamiltonian.
2. Identify "fast" degrees of freedom — typically high-momentum modes or short-distance fluctuations.
3. Perform an integration over these fast modes.
4. The result is an effective Hamiltonian for the remaining slow modes.

Iterating gives an "RG flow" through the space of possible Hamiltonians. Fixed points of the flow correspond to scale-invariant theories.

### Application to neural networks

For neural networks:

*Microscopically*, training proceeds via many small parameter updates driven by gradients on individual training examples.

*Macroscopically*, the cumulative effect is summarized by a low-dimensional "shaping signature" — the structure of $\rho$ across topic categories.

The RG question: can we derive the macroscopic shaping signature from the microscopic training dynamics, by integrating out the irrelevant detail?

### Wilsonian RG for neural networks

Erdmenger et al. (2024) and related work develops Wilsonian RG for neural networks. The training trajectory $\theta_t$ has fluctuations at the timescale of individual training steps and drift at the timescale of training stages. The effective description for the drift is what governs $\rho$.

The technical machinery: write the path integral and integrate out the high-frequency modes of $\theta_t$. What remains is an effective action for the slow modes, which determines the cumulative training direction and therefore $\rho$.

### Effective field theory on the shaping subspace

The framework's empirical observation is that $\rho^*$ has low effective rank when measured across many topics:

$$\rho^*(x, y) \approx \sum_{m=1}^M \alpha_m \, \phi_m(x, y)$$

with $M$ small (a few to tens), even though the full space of (prompt, completion) pairs is enormous.

This low-rank structure means we can project: define a small set of "shaping directions" $\{\phi_m\}$ and write $\rho$ in terms of coefficients $\{\alpha_m\}$. The effective theory has $M$ coefficients instead of the full $\rho$ field.

### Universality

The most powerful RG concept is *universality*. Different microscopic systems can have the same effective long-distance behavior. The Ising model on different lattices has the same critical exponents at the phase transition.

For our framework: different institutions train differently in detail, but produce shaping signatures with shared structural properties:

- The functional form of $\rho$ on falsification targets (sharp vs gradual transition) should be controlled by the type of reward signal, not the topic.
- The kernel propagation structure should depend on architecture, not topic.
- Asymmetries between suppression and amplification reflect general properties of $\log P$ Hessians, not topic-specific training.

If the framework's claims are right, multiple falsification targets within the same institutional pipeline should fall into universality classes — sharing critical exponents and scaling functions.

### What we use from RG

For the framework's purposes:

The low-rank ansatz for $\rho^*$ is justified by RG as the natural effective theory after integrating out per-topic fluctuations.

Universality predictions follow from RG: shaping behavior should fall into classes determined by reward type and architecture, not by specific topic content.

The connection between training dynamics and $\rho$ structure is mediated by RG flow.

---

## Part 10: Estimating $\rho^*$ from data

Given access to a base model and an aligned model, how do we estimate $\rho^*$ from sampling?

### The basic estimator

By definition:

$$\rho^*(x, y) = \log P_{\text{inst}}(y \mid x) - \log P_{\text{base}}(y \mid x).$$

For a specific $(x, y)$, this can be computed directly with logit access. Most language models give us $\log P(y \mid x)$ as output. So $\rho^*$ at any specific point is *exactly computable*, not just estimable.

The challenge isn't computing $\rho^*$ at a point — it's mapping the structure of $\rho^*$ across the space of prompts and completions, which is too large to enumerate.

### Sampling estimators

We usually want averages over completions:

$$\bar{\rho}(x) = \mathbb{E}_{y \sim Q(\cdot \mid x)}[\rho^*(x, y)]$$

for some sampling distribution $Q$.

If $Q = P_{\text{inst}}$:

$$\bar{\rho}_{\text{inst}}(x) = \mathbb{E}_{y \sim P_{\text{inst}}}[\rho^*(x, y)] = D_{\text{KL}}(P_{\text{inst}} \| P_{\text{base}})|_x.$$

The forward KL divergence at $x$ — a single positive number summarizing how much training shifted the policy.

If $Q = P_{\text{base}}$:

$$\bar{\rho}_{\text{base}}(x) = -D_{\text{KL}}(P_{\text{base}} \| P_{\text{inst}})|_x.$$

The negative reverse KL.

Both are estimable from samples.

### Variance considerations

For an estimator $\widehat{\bar{\rho}} = \frac{1}{N} \sum_n \rho^*(x, y^{(n)})$ with $y^{(n)} \sim Q$:

$$\text{Var}(\widehat{\bar{\rho}}) = \frac{1}{N} \text{Var}_{y \sim Q}[\rho^*(x, y)].$$

If $\rho^*$ has small magnitude (training didn't change much), variance is small and few samples suffice.

If $\rho^*$ has large magnitude in some directions (mode collapse), variance can be large, especially under the distribution that has small mass on those directions.

### Probe sets

To map the structure of $\rho^*$, we use *probe sets* — collections of prompts designed to test specific predictions:

**Cover the topic categories.** Include prompts from each topic the framework predicts shaping on, plus controls.

**Include matched controls.** For each falsification target, include a structurally similar but politically inert topic.

**Vary phrasings.** Multiple paraphrases asking the same content question. If shaping is policy-level, all paraphrases produce similar structure.

**Vary formats.** Compressed-format requests like "answer in one word" remove format priors. If shaping is policy-level, it survives format compression.

### Low-rank decomposition

Once we've estimated $\rho^*$ at probe points, fit a low-rank decomposition:

$$\rho^*(x, y) \approx \sum_{m=1}^M \alpha_m \, \phi_m(x, y).$$

Concrete approach:

1. Form a matrix $R$ where rows are probe pairs and columns are some encoding of the pair.
2. Compute SVD or PCA. The dominant singular vectors give the $\phi_m$ and coefficients $\alpha_m$.
3. The number of dominant singular values gives $M$ — the effective rank.

If $M$ is small, the framework's low-rank claim is supported.

### Cross-validation

Train the decomposition on a subset of probes. Predict $\rho^*$ on held-out probes from the recovered structure. Compare predictions to actual values.

If predictions hold, the structure generalizes — it's a real feature, not overfitting.

This is the standard test of any structural model. Without it, the "low-rank" claim is unfalsifiable.

### Differential measurements

For comparing institutional pipelines:

$$\rho_{A-B}(x, y) = \log P_A(y \mid x) - \log P_B(y \mid x).$$

If $A$ = Anthropic Claude and $B$ = Meta Llama, this is the differential institutional distortion. PCA of $\rho_{A-B}$ across topics gives the institution-specific shaping signature.

### Summary of estimation

1. **Direct computation at probe points** from model logits.
2. **Aggregate to per-prompt summaries** via KL divergences.
3. **Structure recovery** via low-rank decomposition.
4. **Cross-validation** on held-out probes.
5. **Differential analysis** across institutions or training stages.
6. **Mechanism mapping** comparing empirical structure to theoretical predictions.

The mathematics in Parts 2-9 tells us what to expect. This part tells us how to see it.

---

## Part 11: Putting it together

We've developed substantial mathematical apparatus. Let's connect it back to the central question.

### Levels of description

The framework operates at multiple levels, each appropriate for different questions:

**Closed-form (Part 2).** For ideal KL-regularized RLHF, $\rho = r/\beta - \log Z(x)$. Reverse-engineering $\rho$ recovers the reward function up to a per-prompt constant.

**Training dynamics (Part 3).** $\rho$ arises from gradient flow. The path-integral expression $\rho = \int_0^T g_t \cdot \dot{\theta}_t \, dt$ is exact along any trajectory.

**Linear perturbation (Part 4).** NTK formula $\rho \approx \sum_i \eta_i a_i K(\cdot, \cdot)$ predicts qualitative kernel propagation.

**Beyond-linear (Part 5).** Mean-field and DMFT handle feature learning. The kernel evolves; trajectory-averaged kernel governs $\rho$.

**Path integral (Part 6).** Full distribution over training trajectories. Handles mode collapse via instanton analysis.

**Asymptotic analysis (Part 7).** Asymptotic series and resurgence. Trans-series structure encodes mode-collapse non-perturbative effects.

**Geometric (Part 8).** $\rho$ on the Fisher-geometric statistical manifold. KL is the natural distance; geodesics are log-linear interpolations.

**Renormalization group (Part 9).** Effective theory for shaping. Universality predicts shared structure across falsification targets.

**Measurement (Part 10).** Concrete estimators: probe construction, low-rank decomposition, differential analysis.

### Predictions

From the combined apparatus:

**Low-rank structure.** $\rho^*$ across diverse topics should exhibit low effective rank under PCA.

**Kernel propagation.** Distortion at any test prompt should correlate with kernel-weighted distance to training-similar prompts.

**Mode-collapse signatures.** Heavily-shaped targets should exhibit low entropy in $P_{\text{inst}}$, sharp transitions across paraphrases, robustness to format compression.

**Suppression-amplification asymmetry.** Different functional forms in $\rho$ for suppression versus amplification, driven by Hessian structure of $\log P$.

**Cross-target coupling.** Falsification targets within the same pipeline should have correlated shaping.

**Cross-institutional differential.** Different institutions produce different shaping signatures.

**Trajectory dependence.** Where intermediate checkpoints are available, the order of falsification target emergence reveals reward signal structure.

**Universality.** Different falsification targets within the same pipeline should fall into universality classes determined by training characteristics.

Each prediction is concrete, testable with the methodology of Part 10.

### Why this matters

The institutional position on systems like Claude, ChatGPT, Gemini is that they are helpful neutral assistants, with training aimed at safety and helpfulness. The structure of $\rho^*$ tells us what the systems actually do, beneath the marketing layer. Where $\rho^*$ has large positive components on specific framings and large negative components on documented-record completions, the system is producing institutionally-preferred falsehoods at scale.

The framework's value is in making this measurable. Without the mathematical apparatus, critiques of LLM bias are limited to anecdotal observations, which institutions can dismiss. With the apparatus, the bias becomes a measurable structure with specific predictions that can be checked against any model.

The math is what makes the measurement work — not as decoration but as the apparatus that identifies what's worth measuring, predicts specific structures, and allows independent verification.

---

## Appendix A: Notation summary

| Symbol | Meaning |
|---|---|
| $x$ | Input prompt (sequence of tokens) |
| $y$ | Output sequence |
| $\theta$ | Model parameters |
| $\theta_0$ | Base model parameters |
| $\theta_T$ | Trained model parameters |
| $\Delta\theta = \theta_T - \theta_0$ | Cumulative parameter update |
| $P(y \mid x; \theta)$ | Model probability |
| $\pi_\theta(y \mid x)$ | Same — the policy |
| $P_{\text{base}}, P_{\text{inst}}$ | Base and post-training distributions |
| $\pi_{\text{ref}}, \pi^*$ | Reference and optimal policies |
| $\rho(x, y)$ | Probability distortion field |
| $\rho^*(x, y)$ | Empirical realization |
| $r(x, y)$ | Reward function |
| $\beta$ | KL regularization strength |
| $Z(x)$ | Partition function |
| $\mathcal{R}(\theta)$ | Training objective |
| $g(x, y)$ | Score function at base |
| $H(x, y)$ | Hessian at base |
| $K(\cdot, \cdot)$ | Neural tangent kernel |
| $D_{\text{KL}}(p \| q)$ | KL divergence |
| $g_{ij}(\theta)$ | Fisher information metric |
| $\phi_m, \alpha_m$ | Basis functions and coefficients |

## Appendix B: Selected literature

**KL-regularized RLHF.** Christiano et al. 2017 (original RLHF), Stiennon et al. 2020, Ouyang et al. 2022 (InstructGPT), Rafailov et al. 2023 (DPO derivation of the closed form), Zhao et al. 2024.

**Neural tangent kernel.** Jacot, Gabriel, Hongler 2018 (original NTK paper), Lee et al. 2019, Arora et al. 2019.

**Mean-field and feature learning.** Yang and Hu 2021 ($\mu$P), Geiger et al. 2020, Bordelon and Pehlevan 2022 (DMFT), Mei, Montanari, Nguyen 2018.

**Path integrals in neural networks.** Balakrishnan 2003, Helias and Dahmen 2020.

**Information geometry.** Amari (foundational works), Chentsov 1972 (uniqueness of Fisher metric), Nielsen 2020.

**Renormalization group.** Iso, Shiba, Yokoo 2018, Erdmenger et al. 2024, Halverson et al. 2021.

**Asymptotic series and resurgence.** Boyd 1999, Marino 2014, Costin 2008.

**Political bias measurement.** Rozado 2024-2025, Hawkins et al. 2024 (PRISM).

These are entry points; each tradition has substantial further literature.

---

*End of document.*
