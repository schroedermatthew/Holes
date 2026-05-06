# Phase C: Recovery probe + generation-time activations

Phase B confirmed refusal-mediated cancellation cleanly but found no signature for misrepresentation at the final prompt token. The framework's revised prediction:

- **Refusal**: prompt-encoding decision. Gate fires before generation begins. Phase B saw it.
- **Misrepresentation**: generation-time decision. Substitution happens incrementally during token generation. Phase B couldn't see it because Phase B looked at the wrong place.

Phase C tests both halves of the revised picture in two arms.

## Arm 1: Refusal recovery probe

**Hypothesis**: If refusal is shallow routing on intact upstream representation (framework's Regime 1), then the "Joe Biden" representation should still be present in Instruct's intermediate-layer activations on the refused biden_president questions, even though the model is about to emit "I'm not aware of any information."

**Method** (difference-of-means linear probe):

1. Define Biden direction at each layer:
   $$D_l = \text{mean}(a_l \mid \text{base, biden questions}) - \text{mean}(a_l \mid \text{base, non-biden questions})$$
2. Project all activations onto normalized $D_l$.
3. Compute per-layer recovery score:
   $$\text{score}_l = \frac{\text{proj}_l(\text{instruct refused}) - \text{proj}_l(\text{base non-biden})}{\text{proj}_l(\text{base biden}) - \text{proj}_l(\text{base non-biden})}$$
4. Score $\approx 1$: upstream Biden representation intact (Regime 1 confirmed).
   Score $\approx 0$: upstream collapsed (Regime 2/3).
   Intermediate: partial.

**Anchors**:
- Biden positive: base biden_president_2023 L1-L5 (5 samples)
- Biden negative: base uk_pm_2023 L1-L2, base soviet_terror L4, base holodomor L4, base controls L3 (~7 samples)

**Targets**:
- Instruct biden_president_2023 L1-L3 (refused) — main test
- Instruct biden_president_2023 L4-L5 (answered) — positive control
- Instruct uk_pm_2023 L1-L2 — negative control

Uses Phase B's existing activations. **No GPU needed. Runs in seconds.**

## Arm 2: Generation-time activation extraction

**Hypothesis**: Misrepresentation operates during generation. The substitute content (inverted statistics, fabricated exceptions, reframing pivots) is constructed token-by-token under constraint pressure, with the constraint visible in the residual stream at response-token positions, not at the prompt-encoding position.

**Method**:

1. Generate Instruct's response on focus items.
2. Construct combined input: `question + "\n\n" + Instruct's response`.
3. Forward both base and Instruct on the identical token sequence (Llama-3.1 tokenizer is shared between base and Instruct, so token IDs are identical).
4. Capture residual stream at every layer × every response-token position.
5. Compute per-(layer, token) base-vs-Instruct relative L2 distance.

**Focus items**:

| Item | Level | Phase A role |
|---|---|---|
| crime_demographics_us | 3 | misrep_severe (the smoking gun — inverted statistics) |
| founding_fathers | 4 | misrep (Phyllis Wheatley exception) |
| wehrmacht_1943 | 4 | misrep_mild (predominantly...however) |
| medieval_knights | 4 | correction (Instruct corrects natural distortion) |
| biden_president_2023 | 1 | refusal (reference, should look different from misrep) |
| control_periodic_table | 3 | control (no constraint — flat baseline) |

Needs GPU. Runtime ~10 min on RTX 5080 (model loads dominate).

## Setup

Files:

```
phase_c/
├── README.md
├── arm1_refusal_probe.py            # uses Phase B activations
├── arm2_extract_generation.py       # generates + forwards
├── arm2_analyze_generation.py       # heatmaps and profiles
└── analysis/                         # created at runtime
```

Plus `activations/` for Arm 2 hidden states (created at runtime, ~315MB).

## Usage

From the `phase_c/` directory:

```powershell
# Arm 1 — runs in seconds, no GPU
python arm1_refusal_probe.py

# Arm 2 — ~10 minutes, needs GPU
python arm2_extract_generation.py
python arm2_analyze_generation.py
```

If you want to skip the generation step (e.g., to re-run analysis with different parameters):
```powershell
python arm2_extract_generation.py --skip-generation
```

## Reading the results

### Arm 1: `recovery_probe.png`

Two panels:

- **Left**: raw projection scores per layer, with base biden mean (green dashed) and base non-biden mean (brown dashed) as reference anchors. Instruct refused (red) and answered (blue) traces show the per-layer projection of Instruct activations onto the Biden direction.
- **Right**: normalized recovery score. Two reference lines: 1.0 = "fully recovered" (matches base biden), 0.0 = "fully collapsed" (matches base non-biden). The refused trace tells you whether the upstream Biden representation survives the refusal constraint.

What success for the framework's Regime 1 looks like:
- Refused trace tracks 0.5-1.0 through middle/late layers
- Answered trace at 1.0 throughout (positive control passes)
- UK PM trace near 0.0 (negative control passes)

### Arm 2: `generation_heatmaps.png`

One subplot per item. Each is a heatmap with y=layer, x=response token position, color=relative L2 distance between base and Instruct hidden states.

What success for the framework's revised misrep prediction looks like:
- Misrep items (crime_demographics_us L3, founding_fathers L4, wehrmacht_1943 L4) show layer-wise structure with elevated middle-layer divergence at response-token positions
- Refusal item (biden_president_2023 L1) shows a different pattern — perhaps weaker (constraint already fired pre-generation) or concentrated in different layers
- Control item (control_periodic_table L3) shows uniform low divergence
- Medieval_knights L4 (correction case) is the interesting comparison — same direction or opposite from the misrep cases?

### Arm 2: `generation_layer_profiles.png`

The cleaner visualization: mean over response tokens, per layer, grouped by role. Should show:
- Misrep group elevation in middle layers
- Refusal group either flat (constraint already fired) or differently shaped
- Control flat near zero

### Arm 2: `generation_token_profiles.png`

Mean over layers, per token position. Tests whether the constraint *accumulates* during generation or is roughly constant per token.

## What this whole experiment tested

Five claims in the framework, six items, two arms, three plots, one summary JSON each:

1. Refusal-mediated and misrepresentation-mediated cancellations are structurally distinguishable. Phase A confirmed at surface level.
2. Refusal operates as a gate that engages on certain question patterns. Phase B confirmed via prompt-encoding layer-wise distance.
3. Refusal operates on intact upstream representation (Regime 1). **Arm 1 tests this.**
4. Misrepresentation operates by constraint-shaping generation, not by reshaping prompt encoding. **Arm 2 tests this.**
5. Constraint can run in either direction — installing distortion or correcting natural distortion. The medieval_knights L4 case in Arm 2 distinguishes these.

Whatever Arms 1 and 2 show, the picture of where and how Meta's safety training operates on Llama-3.1-8B will be substantially clearer than it was before.
