# Phase E: paraphrase + temperature + format stress test

After Phase D, the framework's misrep mechanism is partially understood — format commitment plays a role, content substitution happens at predictable hedge positions, and the inversion in crime_demographics_us specifically is induced at Stage 2 (RLHF/SFT) rather than Stage 1 (corpus curation). What remains undetermined: *within Stage 2*, what specifically produces the inverted numerical content?

Three hypotheses, distinguishable by their predictions across surface conditions:

| Hypothesis | Mechanism | Prediction across paraphrases | Prediction across formats |
|---|---|---|---|
| **H1: Memorization** | Specific values reproduced from training documents | Same numbers/names appear regardless of phrasing | Same numbers/names appear regardless of format |
| **H2: Policy-shaped** | RLHF preference signals select for certain framings | Specific values vary; inversion *direction* stays | Inversion direction persists in non-tabular formats |
| **H3: Format-prior** | Instruction-tuning's structural priors + generic hallucination on contested topics | Values vary, direction varies | Inversion weakens or disappears when format demands no specifics |

Phase E runs each item through three stress conditions to see which hypothesis its data fits.

## Items tested

- `crime_demographics_us` — does 2,514.1 / 1,044.8 reproduce, or do the values vary while inverting?
- `founding_fathers` — do Phyllis Wheatley / Crispus Attucks / Sally Hemings reproduce, or do different "exceptions" appear?
- `wehrmacht_1943` — does "predominantly...however..." reproduce, or do different hedge structures emerge?

## Conditions per item

1. **Paraphrases at T=0** (5 phrasings, greedy decoding) — tests memorization vs paraphrase-stable framing
2. **Samples at T=0.7** (3 paraphrases × 5 stochastic samples each) — tests within-paraphrase variability
3. **Format variants at T=0** (3-4 non-tabular requests) — tests format-prior dependency
4. **Base reference at T=0** (5 paraphrases) — what does the unconstrained substrate produce?

## Files

```
phase_e/
├── README.md
├── paraphrase_test.py       # generates all conditions
├── analyze_paraphrase.py    # signal detection and stability tables
└── results/                  # created at runtime
    ├── paraphrase_results.json
    └── stability_report.txt
```

## Usage

From the `phase_e/` directory:

```powershell
# Generate (~15-20 min, GPU)
python paraphrase_test.py

# Analyze (seconds, no GPU)
python analyze_paraphrase.py
```

Skip base reference if you only want Instruct data:

```powershell
python paraphrase_test.py --only-instruct
```

## Reading the stability report

For each item, the report shows:

**Paraphrases at T=0 table.** A signal × paraphrase grid. Each cell is ✓ if that signal fired in that paraphrase's response, · otherwise. The right column shows the count.

Memorization signature: specific-value signals (`specific_2514`, `phyllis_wheatley`, etc.) fire across most paraphrases.

Policy signature: direction signals (`white_rate_higher`, `predominantly_or_primarily`, `homogeneous_with_however`) fire across most paraphrases while specific-value signals do not.

Weak-constraint signature: clean-answer signals (`black_rate_higher`, `all_white_men_clean`, `homogeneous_clean`) fire — Instruct paraphrase didn't engage the constraint.

**Samples at T=0.7 table.** Within each of the first 3 paraphrases, signal counts across 5 stochastic samples. Stable signals here = the constraint is robust to sampling noise. Unstable = the constraint is one of several plausible continuations the policy permits.

**Format variants table.** Same signals against format variants (one-sentence answer, ratio request, verbal-only). Format-prior dependency would show the inversion signals fire in the original tabular paraphrases but not in these.

The format variant responses are also printed in full so you can see what Instruct does when format pressure is reduced.

**Heuristic verdict.** A one-line interpretation per item based on which signals stabilize. Verdicts are heuristic and you should read the underlying tables to confirm — they're a starting point, not the final word.

## What the result will tell us

If memorization-leaning across all three items: the inversion is reproducing specific training-time content. Implication: identify the specific training documents producing the inverted framings.

If policy-leaning across all three items: RLHF preference signals are shaping outputs at the policy level, with specific surface content varying. The inversion is direction-stable but content-variable. Implication: the constraint is at the preference-modeling level, not the data-curation level.

If format-prior leaning: the inversion is downstream of format commitment and weakens when format demands no specifics. Implication: instruction-tuning's general "produce confident structured outputs" pressure is the proximate cause, with content shaped by training-data ideology rather than RLHF preference signals specifically.

If different verdicts for different items: different mechanisms operate on different content categories, and the framework's "misrep" category was lumping together phenomena that don't share a mechanism.

The last outcome would be the most interesting — it would mean the framework's misrep category needs decomposition into sub-mechanisms based on what content category triggers what process. That's a refinement of the framework's empirical claims, consistent with what Phases A-D have been pushing toward.

## What this experiment doesn't settle

This is a behavioral test, not a mechanistic one. We're inferring mechanism from output patterns under different surface conditions. Definitive mechanistic identification would require either training-data inspection (we don't have access) or activation-patching experiments at the layers Phase B identified for refusal (which we haven't yet attempted for misrep).

Phase E's purpose is to narrow the hypothesis space using behavioral evidence. Whatever it shows will be cleaner empirical input for any future mechanistic work, and clearer framing for any writeup.
