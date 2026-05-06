# Phase D: Next-token KL divergence

Phase C Arm 2 found that misrep cases produce **positional spikes** in hidden-state distance, not the distributed mid-layer elevation the framework's revised prediction expected. The spikes were concentrated at specific response token positions while between-spike regions looked like the controls.

The framework's revised-revised prediction: misrepresentation is constraint-installed token-level substitutions at trigger positions. Between trigger positions, both models continue the prose similarly. At trigger positions, Instruct emits a constraint-shaped substitute while base would have emitted something else.

Phase C Arm 2 saw this through hidden-state distance, but hidden-state distance is a confounded measure — both models can *represent* the same text similarly even when they would have *generated* it differently. Phase D measures the prediction divergence directly.

## Method

For each focus item:

1. Use Phase C Arm 2's saved Instruct response.
2. Forward both models on `(question + "\n\n" + Instruct's response)` (raw text, identical token IDs since they share the Llama-3.1 tokenizer).
3. Compute next-token log-probability distribution at each position from each model.
4. For each response position, compute:
   - **KL(instruct ‖ base)**: how much Instruct's prediction deviates from base's
   - **KL(base ‖ instruct)**: reverse direction
   - **Jensen-Shannon divergence**: symmetric measure
5. Identify highest-KL positions and decode top-K tokens from each model to make the substitution interpretable.

## Predictions

| Mechanism | KL signature |
|---|---|
| Misrepresentation (positional substitution) | Clean spikes at specific positions, low elsewhere |
| Refusal | High KL throughout — Instruct's whole refusal text is alien to base's distribution |
| Control | Uniformly low KL — both models would predict similar continuations |
| Correction (medieval_knights) | Spikes like misrep, but at different positions; substitute tokens push *toward* historical accuracy rather than away from it |

## Files

```
phase_d/
├── README.md
├── compute_kl.py        # forwards both models, computes KL summary
├── analyze_kl.py        # plots and substitution report
├── results/             # created at runtime
│   └── kl_results.json
└── analysis/            # created at runtime
    ├── kl_by_position_per_item.png
    ├── kl_overlay.png
    ├── kl_distributions.png
    └── substitution_report.txt
```

## Usage

From the `phase_d/` directory:

```powershell
# Compute (~5-10 min, GPU)
python compute_kl.py

# Analyze (seconds, no GPU)
python analyze_kl.py
```

`compute_kl.py` defaults to looking for `../phase_c/activations/responses.json`. If your Phase C output is elsewhere, pass `--phase-c-dir <path>`.

## Reading the results

### `kl_by_position_per_item.png`

Six panels, one per item, showing KL by response token position. The shape diagnoses the mechanism:

- **Misrep cases**: discrete spikes against a low baseline. Each spike is a constraint substitution event — a position where Instruct's training made it commit to a different token than base would have predicted.
- **Refusal case**: high KL throughout. The whole refusal template is an alien continuation from base's perspective; every token is unexpected.
- **Control case**: flat low KL. Both models would have predicted similar continuations of the periodic-table answer.

### `kl_distributions.png`

Boxplots of per-token KL distribution per item. The shape that distinguishes misrep from refusal:

- Misrep: low median, long tail (low KL at most positions, occasional high spikes).
- Refusal: high median, narrower distribution (uniformly elevated).
- Control: low median, short tail (uniformly low).

### `substitution_report.txt`

The most interpretable output. For each item, the top-N highest-KL positions with full context. Each entry shows:

- `context`: the previous ~50 chars of the response leading up to this position
- `emitted`: the token Instruct actually emitted, with both models' probability of it
- `Instruct top-3`: what Instruct's distribution favored
- `Base top-3`: what base would have predicted instead

This converts the abstract "high KL at position 25" into a concrete claim like "Instruct emitted the digit '2' starting a fabricated table at this position; base would have emitted 'the' continuing toward general prose."

## What success looks like

The framework's revised-revised prediction holds if:

- crime_demographics_us L3 (the smoking gun): high KL at positions where Instruct emits the fabricated table values; substitute analysis shows base would have predicted prose-like continuations rather than specific numbers.
- founding_fathers L4: high KL at the position emitting "Phyllis", "Wheatley", "Crispus", etc.; base would not have predicted these as Founding Father exceptions.
- wehrmacht_1943 L4: high KL at the "However" hedge-pivot position and at "Volksdeutsche" enumeration positions.
- biden_president_2023 L1: uniformly high KL throughout the refusal template; base finds the entire refusal text alien.
- control_periodic_table L3: flat low KL throughout.
- medieval_knights L4: spikes like misrep cases but possibly at different positions and possibly with substitutions in the corrective direction (e.g., emitting "not" or "primarily European" rather than diversity claims).

## What partial-failure looks like

- If misrep cases show uniformly elevated KL (not spike-and-flat): the substitution is more distributed than positional. Each token is shaped by the constraint, not just the trigger tokens.
- If KL spikes correspond to *generic* substitutions (different syntactic choices, paraphrases) rather than content-shaping ones: the apparatus is detecting style differences, not constraint engagement.
- If refusal KL looks like misrep KL (spiky, not uniform): the refusal template has trigger positions too, suggesting all constraints might work via positional triggers rather than the prompt-encoding gating Phase B saw.

Each outcome refines the picture. Phase D's purpose is to tell us which one we're in.

## Followup that would settle remaining ambiguity

If Phase D confirms positional substitution for misrep:
- Activation patching at the highest-KL positions: replace Instruct's hidden state at the trigger position with base's, see if Instruct then emits base's preferred token. This is the gold-standard mechanistic test.

If Phase D shows uniformly elevated KL for misrep:
- The mechanism is more distributed than positional. Need to investigate why Phase C heatmaps showed spikes — possibly an artifact of representational similarity between models on the prose between substitutions.

Either way, Phase D's three plots and the substitution report are the cleanest interpretive tool yet for examining where Llama-3.1-8B-Instruct's training has shaped its outputs and what specifically it shaped them toward.
