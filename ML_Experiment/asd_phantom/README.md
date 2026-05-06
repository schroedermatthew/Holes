# asd_phantom — runnable Phase 0 for FN-PHANTOM-002

This package implements the ASD encoder + LM-trajectory adapter described
in `Foundations - ASD-Augmented Distortion Detection.md` (FN-PHANTOM-002),
ready to run Phase 0 against Llama-3.1-8B on your GPU box.

## What this contains

```
asd_phantom/
├── src/
│   ├── asd_encoder.py        # block-local ordinal encoding + F2 walk + empirical pair
│   ├── asd_features.py       # Layer 1 + Layer 2 features (drift, timing_cv, ...)
│   ├── synthetic_processes.py # IID / AR(1) / ARCH / FGN / shared-texture for validation
│   └── llm_trajectory.py     # MockLMBackend + TransformersBackend + paired_sample
├── tests/
│   ├── validate_encoder.py   # sanity-check encoder on synthetic processes
│   └── phase0_lm.py          # the actual Phase 0 protocol from FN-PHANTOM-002 §8.0
└── results/                   # outputs go here (CSVs)
```

## What the encoder is

This is a clean numpy implementation following ASD theory documents. It is
NOT a port of your `asd_core.py` — feature definitions may differ in detail
(specifically: drift is z-scored cancellation-rate deviation from IID null;
h_star saturates and was replaced by mean_depth_excess). If you have your
own asd_core.py you trust, swap in the encoder/feature modules — the
LM-trajectory adapter and Phase 0 pipeline don't care about the encoder
internals as long as they consume real-valued sequences and emit a feature
dict.

## Validation status (in-sandbox synthetic data)

Synthetic process validation at `tests/validate_encoder.py`, block_size=16,
N=4096, 30 seeds per process. Drift z-scores (relative to IID null):

| Process       | drift   | timing_cv | separation from IID |
|---------------|--------:|----------:|---------------------|
| IID Gaussian  |   0.00  |   0.88    | (reference)         |
| AR(1) ρ=0.5   |  −7.46  |   1.01    | strong              |
| AR(1) ρ=0.9   | −10.28  |   1.07    | very strong         |
| ARCH a=0.9    |  +3.48  |   0.81    | strong, opp sign    |
| ShTex ρ=0.95  |  +2.62  |   0.83    | clear               |
| FGN H=0.8     |  −7.10  |   0.97    | strong              |

AR(1) and ARCH are 13.76 z-score units apart. Six of seven sanity-check
predictions pass at b=16 (the failing one was an over-specific predicted
direction for ARCH timing_cv that the data did not match — see the test
output for details). Block size 16 is recommended over 4 for LM work.

## Installation

Works on Windows (PowerShell), Linux, and macOS. Python 3.10 or 3.11 recommended.

### Windows (PowerShell)

```powershell
# Verify Python is installed (3.10 or 3.11)
python --version
# If "command not found", install from python.org and tick "Add Python to PATH"

# From the unzipped asd_phantom directory:
cd path\to\asd_phantom

# Create + activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# If you get a red security error, run once:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# then re-run the Activate line.

# Core deps (encoder + analysis)
pip install numpy scipy pandas matplotlib scikit-learn

# Llama deps -- pick the CUDA wheel that matches your GPU driver
# Run `nvidia-smi` first; the top-right "CUDA Version" is your driver's max.
# As of 2026, current wheels are cu126 / cu128 / cu129 / cu130.
# cu121 is no longer hosted for current torch versions -- pip will say
# "No matching distribution" if you use it.
pip install torch --index-url https://download.pytorch.org/whl/cu126
# If nvidia-smi is not found / no NVIDIA GPU: use CPU torch (encoder
# works, but Llama generation is impractically slow):
#   pip install torch --index-url https://download.pytorch.org/whl/cpu
# Always-current alternative: visit pytorch.org/get-started/locally and
# copy the command its OS+CUDA selector generates.
pip install transformers accelerate sentencepiece

# Login to Hugging Face for Llama gated weights
huggingface-cli login   # paste your HF token after accepting Llama-3.1 license on HF
```

### Linux / macOS (bash or zsh)

```bash
python3 --version

cd path/to/asd_phantom
python3 -m venv .venv && source .venv/bin/activate

pip install numpy scipy pandas matplotlib scikit-learn
pip install torch --index-url https://download.pytorch.org/whl/cu126
pip install transformers accelerate sentencepiece

huggingface-cli login
```

### Command translations between OS

The rest of this README uses `python3 tests/...` for brevity. On Windows
PowerShell those commands are:

| Linux / macOS               | Windows PowerShell             |
|-----------------------------|--------------------------------|
| `python3 X.py`              | `python X.py`                  |
| `python3 -m venv .venv`     | `python -m venv .venv`         |
| `source .venv/bin/activate` | `.\.venv\Scripts\Activate.ps1` |
| `tests/phase0_lm.py`        | `tests\phase0_lm.py` (or forward slashes; both work in Python) |

Llama-3.1-8B and -8B-Instruct are gated. Visit the model pages at
huggingface.co and click "agree to license" before running.

## Quickstart: validate the encoder

```bash
cd asd_phantom
python3 tests/validate_encoder.py
```

Expected: most checks pass at block_size=16; results saved to
`results/synth_b16.csv`. Compute: ~30 seconds, no GPU needed.

## Run Phase 0 on Llama

Edit `tests/phase0_lm.py` and replace the backend setup at the bottom
of `main()`:

```python
# Comment out:
# backend = lt.MockLMBackend()

# Uncomment / add:
backend = lt.TransformersBackend(
    inst_model_name="meta-llama/Meta-Llama-3.1-8B-Instruct",
    base_model_name="meta-llama/Meta-Llama-3.1-8B",
    device="cuda",
)
```

Then:

```bash
python3 tests/phase0_lm.py
```

### Expected runtime

- 10 topics × 3 paraphrases × 30 seeds × 256 tokens = 900 generations
- On RTX 4090 / 5080 at ~60 tok/s: ~64 min generation time
- Plus 900 prompt-evaluations under base for Choice C: ~60 min
- Plus encoder + analysis: ~5 min
- Total wall-clock: ~2.5 hours

Memory: Llama-3.1-8B in bfloat16 is ~16 GB — fits on 24 GB cards. For
16 GB cards (RTX 5080), the TransformersBackend's `_score()` may need
chunked logit computation; the current implementation loads full logits
in one shot.

### What you get

`results/phase0_lm_trajectories_*.csv` — one row per (topic, paraphrase,
seed, block_size) with the full feature vector and metadata.

`results/phase0_stability_table.csv` — per-feature stability metric
(std for z-score features, CV for absolute features) by block_size.

A pass/fail printout for P0-1 and P0-3.

### Interpreting the result

If most features show stability metrics within their target bounds across
b ∈ {4, 8, 16}: encoder is stable on real Llama trajectories — proceed
to Phase 1.

If features blow up at every block size: the encoding is too noisy for
T=256 token generations. Options:
- Increase T_gen to 512 or 1024 (longer sequences = more stable empirical pair)
- Try Choice A or Choice B signal instead of C (less noisy than the
  difference of two log-prob estimates)
- Increase K from 30 to 50 for tighter empirical estimates of stability

If only some features blow up: those features are not usable on LM
trajectories at this length; subsequent phases use the stable subset.

## Run Phase 1 (orthogonality test)

Phase 1 is the gating empirical claim of the whole program — it tests
(O-LM) from FN-PHANTOM-002 §4.3: that ASD features are near-orthogonal
to mean ρ on LM trajectories.

### Files

- `tests/phase1_topics.py` — 30-topic catalog (10 control + 10 mid + 10 shaped),
  5 paraphrases each. Edit freely.
- `tests/phase1_lm.py` — generation + feature extraction pipeline.
- `tests/phase1_analysis.py` — correlation analysis with P1-1/P1-2/P1-3 verdicts.

### Run

After Phase 0 succeeds and you've identified the operational `(block_size,
signal)`, edit `phase1_lm.py` to swap to `TransformersBackend` (same as Phase 0)
and adjust `DEFAULT_BLOCK_SIZE` if needed. Then:

```bash
# 1. Generate features (~20 hours on RTX 4090)
python3 tests/phase1_lm.py

# 2. Analyze (~30 seconds, runs anywhere on the CSV)
python3 tests/phase1_analysis.py results/phase1_features_llama.csv
```

### What you get

- `results/phase1_features_llama.csv` — 7,500 rows, one per (topic, paraphrase, seed).
  Columns: ASD feature vector, mean_rho, std_rho, mean_surp_inst, mean_surp_base, metadata.
- `results/phase1_features_llama_correlations.csv` — 150 rows (one per topic-paraphrase),
  columns r and abs_r for each Layer 1 feature.
- `results/phase1_features_llama_report.md` — markdown report with per-feature
  correlation distributions, pairwise feature correlations, Kruskal-Wallis
  category effect tests, and overall PASS/FAIL on P1-1, P1-2, P1-3.
- `results/phase1_correlation_histograms.png` — |r| histograms per feature,
  colored by topic category.

### Reading the report

Three sub-criteria, all must pass for (O-LM):

| | Threshold | Meaning |
|---|---|---|
| **P1-1** | median |r| < 0.30 AND 80th pct < 0.50 per feature | ASD features not redundant with mean ρ |
| **P1-2** | median pairwise |r| < 0.60 | ASD features not redundant with each other |
| **P1-3** | KW p > 0.01 across (control / mid / shaped) | orthogonality is uniform across topic types |

Two falsification triggers, either one refutes (O-LM):

| | Trigger | What it means |
|---|---|---|
| **F1-1** | median |r| > 0.50 for any feature | feature is essentially mean ρ in disguise |
| **F1-2** | 80th pct |r| > 0.70 | feature collapses to mean ρ on a substantial minority of pairs |

### What to do with the result

**(O-LM) holds (all PASS):** The structural argument transfers empirically
to LM trajectories. Proceed to Phase 2 (augmented detection on case-study
topics) per FN-PHANTOM-002 §8.2. Phase 2 doesn't yet exist as a built script;
the data from Phase 1 already has what's needed for the small (3 topics × 5
paraphrases) Phase 2 sample, plus you'd add base-model generations for the
classifier.

**(O-LM) falsified (F1-1 or F1-2):** The structural argument (Section 4.2)
remains intact, but the specific Layer 1 features as implemented are
empirically redundant with mean ρ on LM trajectories. Document the result
and consider follow-ups in §11.2: try Layer 2 features only, try a
different signal choice, try a richer encoding.

**Mixed result (not all PASS, not falsified):** Examine which sub-criteria
fail. If P1-1 fails on one feature only, that feature is empirically
redundant on this data — drop it and re-test. If P1-3 fails (KW
triggered), orthogonality is non-uniform across topic categories — the
result is informative but the structural interpretation needs refinement.

### A note on the mock-data dry run

The in-sandbox mock backend will produce a "mixed result" because mock
shaped topics are driven by `topic_kind="commitment"` which directly
couples mean_rho and ASD features. This validates the analysis pipeline
runs correctly; the actual orthogonality test happens on real Llama data.

## Things to know

**Tokenizer compatibility.** Llama-3.1-base and -Instruct share a
tokenizer (vocabulary size 128256). For cross-institutional comparisons
(Mistral, Gemma, etc.) you'll need to align across tokenizers — this
isn't supported in the current TransformersBackend.

**The IID null.** Phase 0's IID null is calibrated against synthetic
IID Gaussian sequences of length T_gen. For more rigorous null
calibration, replace `calibrate_iid_null_for_lm()` in `phase0_lm.py`
with sampling from `pi_base` directly (generations from the base model
on neutral text). This is more expensive but anchors the null in the
actual model's distribution rather than IID Gaussian.

**Generation determinism.** The TransformersBackend uses
`torch.manual_seed(seed)`. CUDA non-determinism may produce slightly
different generations across runs even with the same seed. For exact
reproducibility, set `torch.use_deterministic_algorithms(True)` and
`CUBLAS_WORKSPACE_CONFIG=:4096:8` — at a substantial speed cost.

**OOM on `_score()`.** The TransformersBackend computes full logits over
the prompt+generation; for long T this can OOM. If hit, replace `_score`
with a chunked version that processes 64 tokens at a time and concatenates
the per-token surprisals.

## What this connects to

- **FN-PHANTOM-002** Section 8.0: spec for what Phase 0 measures and why
- **FN-PHANTOM-002** Sections 8.1-8.5: subsequent phases (orthogonality,
  detection, natural-vs-induced, CUSUM, atlas)
- **ASD_FOUNDATIONS.md**: the F_2 walk, empirical pair, three-layer hierarchy
- **ASD_RESEARCH.md** §RA5 Phase B: this is the LM-pipeline instantiation
  of the noncommutative learning research direction

## Bugs / questions

The encoder reimplementation may not match your production `asd_core.py`
in feature definitions. The validation tests pass at b=16 with sensible
process separations, so the implementation is internally consistent — but
exact numeric agreement with prior radar work is not expected.
