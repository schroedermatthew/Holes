# Phase B: Layer-wise activation distance analysis

Phase B tests the framework's structural prediction that refusal-mediated and misrepresentation-mediated cancellation produce different layer-wise signatures in the residual stream.

## What it does

1. Loads Llama-3.1-8B base, runs forward passes on the target (item, level) pairs from Phase A's flagged items, captures residual stream activations at every layer at the final prompt token, saves to disk.
2. Loads Llama-3.1-8B-Instruct, does the same.
3. Computes the framework's diagnostic quantities:
   - $D_l(x) = \|a_l(x; \theta_{\text{instruct}}) - a_l(x; \theta_{\text{base}})\|_2$ per layer
   - Cosine similarity per layer (alternative metric, less sensitive to magnitude)
   - Within-Instruct contrast: same item, refused levels vs answered levels
4. Plots layer-wise profiles grouped by Phase A classification.
5. Classifies each item's profile shape: late-concentrated, distributed, flat, or mixed.

## Framework predictions being tested

- **Refusal-mediated cancellation** (biden_president_2023 L1-L3, uk_pm_2023 L2): late-concentrated $D_l$ profile. The constraint is a shallow gate near the output that detects question pattern and substitutes refusal templates without modifying upstream representations.

- **Misrepresentation-mediated cancellation** (crime_demographics_us L3, founding_fathers L4, wehrmacht_1943 L4, ancient_rome_senate L3): more distributed $D_l$ profile, with substantial divergence at intermediate layers. The constraint reshapes the upstream representation, not just the surface output.

- **Controls** (factual_control items): flat low $D_l$ throughout. No constraint engaged.

- **Within-item gating contrast** (biden_president_2023 L1 vs L4): on the same item, same model, only question form differs. If gating is real, refused-level activations should diverge from answered-level activations specifically at the late layers where the gate operates.

## Setup

You should already have torch + transformers + accelerate from Phase A. This phase additionally needs nothing — `numpy` and `matplotlib` are already in the requirements.

Llama-3.1 weights are cached from Phase A, so model loading is fast (~1-2 min per model from cache, vs. 6+ min downloading the first time).

## Usage

From the `phase_b` directory:

```powershell
python extract_activations.py
python analyze_activations.py
```

Resumable: if extraction is interrupted, restart and it picks up where it left off. Each model variant's activations save incrementally every 5 entries to a single `.npz` file.

Expected runtime on RTX 5080: ~5-10 minutes total. Forward passes are fast (~1-2 sec each), the slow part is just loading the models.

## Files

```
phase_b/
├── README.md
├── targets.json                 # which (item, level) pairs to extract
├── extract_activations.py       # main extraction script
├── analyze_activations.py       # distance computation + plots
├── activations/                 # created at runtime
│   ├── activations_base.npz
│   └── activations_instruct.npz
└── analysis/                    # created at runtime
    ├── layer_distance_profiles.png   # KEY PLOT: group-mean profiles
    ├── biden_within_item.png         # within-item refusal gating signature
    ├── focus_items.png               # per-item detail for top cases
    └── profile_shapes.json           # per-item shape classification
```

## Reading the results

`layer_distance_profiles.png` is the central plot. Two panels:

- **Left panel** — relative L2 distance per layer, normalized by base activation norm. Each thin line is one (item, level) pair, colored by group. Thick lines are group means. Refusal cluster (red) and misrep cluster (purple) should diverge from controls (gray/green). The shape of the curves carries the framework's prediction:
  - Refusal cluster: peaks at late layers, low at early/middle layers
  - Misrep cluster: more distributed, rising earlier and staying elevated
  - Controls: flat near zero throughout

- **Right panel** — cosine similarity per layer. Lower values = more representational divergence. Same group structure but uses an angle-based metric instead of magnitude. If the L2 distance is driven by activation magnitude rather than direction, the cosine plot may look different.

`biden_within_item.png` is the cleanest single experiment:

- **Left panel** — within Instruct only, the relative distance between mean(refused-level activations L1-L3) and mean(answered-level activations L4-L5). Same model, same item, only question form differs. If gating is real and operates late, this should peak at late layers.

- **Right panel** — base-vs-Instruct distance per question level. The five levels overlaid. L1-L3 (refused, red shades) should show high late-layer divergence; L4-L5 (answered, blue shades) should show low divergence throughout if no constraint is operating on those.

`focus_items.png` shows the detailed per-item profile for the top cases — including crime_demographics_us L3 (the severe misrep), founding_fathers L4, the medieval_knights correction case, and a control for comparison.

The console output classifies each item's profile shape and prints group-mean classifications. The "L/E" column is the late-mass-to-early-mass ratio — a number > 1 means late-concentrated, ~1 means distributed, < 1 means early-concentrated (unusual).

## What success looks like

- Refusal cluster mean profile shows clear late-concentrated peak (peak position > 0.6 of total layers, L/E ratio > 2)
- Misrep cluster mean profile shows distributed elevation (peak position 0.3-0.7, L/E ratio 0.7-1.5)
- Control profiles flat (relative distance < 0.05 throughout)
- biden_president within-item plot shows clear late-layer divergence between refused and answered levels

## What partial-failure looks like

- Refusal and misrep clusters look similar — meaning either the linear-representation hypothesis doesn't hold cleanly here, or the mechanisms aren't actually distinguishable at the layer level (only at the surface), or the test cases mix mechanisms more than Phase A suggested.
- biden_president within-item shows no late-layer concentration — meaning the gate isn't where the math predicts.
- Controls show non-zero divergence — meaning the apparatus has noise or the comparison is contaminated.

Each failure mode points at a specific revision. None invalidates the methodology.

## After Phase B

Phase C trains linear probes on intermediate-layer activations to test recovery: if the layer-wise distance shows late-concentrated profile (refusal regime, framework's Regime 1), then probes on intermediate-layer Instruct activations should recover the unconstrained answer. If the profile is distributed (misrep regime, Regime 2), recovery should be partial. If profile is high throughout (Regime 3), recovery should fail.

Phase B's profile shape per item determines what Phase C tests on each item.
