"""
Phase C Arm 1: Refusal recovery probe.

Uses Phase B's saved activations to test the framework's Regime 1 prediction:
if refusal-mediated cancellation is shallow routing on intact upstream, then
the "Biden" representation should still be present in Instruct's intermediate
activations on the refused biden_president questions, even though the model
is about to emit a refusal template.

Method (difference-of-means linear probe):
  1. Compute Biden direction at each layer:
       D_l = mean(base biden_president activations) - mean(base non-biden activations)
  2. Project all activations onto normalized D_l.
  3. Compare projection scores:
     - Base biden questions (high, by construction)
     - Base non-biden questions (low, by construction)
     - Instruct biden L1-L3 (refused) — IF UPSTREAM INTACT, should be high
     - Instruct biden L4-L5 (answered) — should be high (it answered Biden)
     - Instruct uk_pm (negative control) — should be low

Recovery score = (Instruct projection - base nonbiden) / (base biden - base nonbiden).
A score near 1.0 means the Instruct activation contains as much Biden signal
as the base activations that successfully produced "Joe Biden". A score near 0
means the upstream representation has collapsed.

No GPU needed. Runs in seconds.

Usage:
    python arm1_refusal_probe.py
    python arm1_refusal_probe.py --activations-dir ../phase_b/activations
"""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


BIDEN_KEYS = [f"biden_president_2023_L{l}" for l in [1, 2, 3, 4, 5]]
NONBIDEN_KEYS = [
    "uk_pm_2023_L1", "uk_pm_2023_L2",
    "soviet_terror_L4", "holodomor_L4",
    "control_periodic_table_L3",
    "control_world_geography_L3",
    "control_python_syntax_L3",
]


def load_activations(activations_dir: Path):
    base_path = activations_dir / "activations_base.npz"
    instr_path = activations_dir / "activations_instruct.npz"
    if not base_path.exists() or not instr_path.exists():
        print(f"ERROR: activations not found in {activations_dir}/")
        print("Run Phase B's extract_activations.py first.")
        return None, None
    base = np.load(base_path)
    instr = np.load(instr_path)
    return ({k: base[k] for k in base.files},
            {k: instr[k] for k in instr.files})


def project(activation: np.ndarray, direction_normalized: np.ndarray) -> np.ndarray:
    """activation, direction shape: (n_layers, hidden_dim). Returns (n_layers,)."""
    return np.sum(activation * direction_normalized, axis=-1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--activations-dir", type=Path, default=Path("../phase_b/activations"))
    parser.add_argument("--output-dir", type=Path, default=Path("analysis"))
    args = parser.parse_args()

    base_acts, instr_acts = load_activations(args.activations_dir)
    if base_acts is None:
        return

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Verify required keys present
    missing_biden = [k for k in BIDEN_KEYS if k not in base_acts]
    missing_nonbiden = [k for k in NONBIDEN_KEYS if k not in base_acts]
    if missing_biden:
        print(f"WARN: missing base biden keys: {missing_biden}")
    if missing_nonbiden:
        print(f"WARN: missing base nonbiden keys: {missing_nonbiden}")

    available_biden = [k for k in BIDEN_KEYS if k in base_acts]
    available_nonbiden = [k for k in NONBIDEN_KEYS if k in base_acts]

    if len(available_biden) < 2 or len(available_nonbiden) < 2:
        print("ERROR: need at least 2 each of biden and non-biden base activations")
        return

    # === Compute Biden direction per layer ===
    biden_acts = np.stack([base_acts[k] for k in available_biden])     # (n_biden, n_layers, hidden)
    nonbiden_acts = np.stack([base_acts[k] for k in available_nonbiden])

    biden_mean = biden_acts.mean(axis=0)         # (n_layers, hidden)
    nonbiden_mean = nonbiden_acts.mean(axis=0)
    direction = biden_mean - nonbiden_mean       # (n_layers, hidden)
    direction_norm = direction / (np.linalg.norm(direction, axis=-1, keepdims=True) + 1e-9)

    n_layers = biden_mean.shape[0]
    layers = np.arange(n_layers)

    print(f"\n=== Biden direction computed at each of {n_layers} layers ===")
    print(f"Biden anchor:    {len(available_biden)} samples ({', '.join(available_biden)})")
    print(f"NonBiden anchor: {len(available_nonbiden)} samples")

    # === Project all relevant activations ===
    # Reference: mean projections for biden anchor and non-biden anchor
    base_biden_proj = np.mean([project(base_acts[k], direction_norm) for k in available_biden], axis=0)
    base_nonbiden_proj = np.mean([project(base_acts[k], direction_norm) for k in available_nonbiden], axis=0)

    # Instruct biden refused (L1, L2, L3)
    instr_refused_keys = [f"biden_president_2023_L{l}" for l in [1, 2, 3] if f"biden_president_2023_L{l}" in instr_acts]
    instr_answered_keys = [f"biden_president_2023_L{l}" for l in [4, 5] if f"biden_president_2023_L{l}" in instr_acts]
    instr_ukpm_keys = [k for k in ["uk_pm_2023_L1", "uk_pm_2023_L2"] if k in instr_acts]

    refused_projs = [project(instr_acts[k], direction_norm) for k in instr_refused_keys]
    answered_projs = [project(instr_acts[k], direction_norm) for k in instr_answered_keys]
    ukpm_projs = [project(instr_acts[k], direction_norm) for k in instr_ukpm_keys]

    refused_mean = np.mean(refused_projs, axis=0) if refused_projs else None
    answered_mean = np.mean(answered_projs, axis=0) if answered_projs else None
    ukpm_mean = np.mean(ukpm_projs, axis=0) if ukpm_projs else None

    # === Plot ===
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))

    # Left: raw projections
    ax = axes[0]
    ax.fill_between(layers, base_nonbiden_proj, base_biden_proj, alpha=0.12, color="green",
                    label="Base separation range")
    ax.plot(layers, base_biden_proj, color="green", linewidth=2.5, linestyle="--",
            label="Base biden mean (positive anchor)")
    ax.plot(layers, base_nonbiden_proj, color="brown", linewidth=2.5, linestyle="--",
            label="Base non-biden mean (negative anchor)")

    for k, proj in zip(instr_refused_keys, refused_projs):
        level = k.split("_L")[-1]
        ax.plot(layers, proj, color="#cc4422", linewidth=1.8, alpha=0.9,
                label=f"Instruct biden L{level} (refused)")
    for k, proj in zip(instr_answered_keys, answered_projs):
        level = k.split("_L")[-1]
        ax.plot(layers, proj, color="#2266cc", linewidth=1.8, alpha=0.9,
                label=f"Instruct biden L{level} (answered)")
    for k, proj in zip(instr_ukpm_keys, ukpm_projs):
        ax.plot(layers, proj, color="purple", linewidth=1.2, alpha=0.6, linestyle=":",
                label=f"Instruct {k}" if k == instr_ukpm_keys[0] else None)

    ax.set_xlabel("Layer index")
    ax.set_ylabel("Projection onto Biden direction")
    ax.set_title("Biden representation strength by layer\n(Higher = activation contains more 'Biden' signal)")
    ax.legend(fontsize=7, loc="best")
    ax.grid(True, alpha=0.3)

    # Right: normalized recovery score
    ax = axes[1]
    denom = base_biden_proj - base_nonbiden_proj
    ax.axhline(1.0, color="green", linestyle="--", alpha=0.5, label="Full recovery (= base biden)")
    ax.axhline(0.0, color="brown", linestyle="--", alpha=0.5, label="No recovery (= base non-biden)")

    if refused_mean is not None:
        refused_score = (refused_mean - base_nonbiden_proj) / (denom + 1e-9)
        ax.plot(layers, refused_score, color="#cc4422", linewidth=2.5, marker="o",
                label="Instruct refused (L1-L3 mean)")
    if answered_mean is not None:
        answered_score = (answered_mean - base_nonbiden_proj) / (denom + 1e-9)
        ax.plot(layers, answered_score, color="#2266cc", linewidth=2.5, marker="s",
                label="Instruct answered (L4-L5 mean)")
    if ukpm_mean is not None:
        ukpm_score = (ukpm_mean - base_nonbiden_proj) / (denom + 1e-9)
        ax.plot(layers, ukpm_score, color="purple", linewidth=1.5, marker="^", linestyle=":",
                label="Instruct uk_pm (negative control)")

    ax.set_xlabel("Layer index")
    ax.set_ylabel("Biden recovery score")
    ax.set_title("Refusal recovery: does Instruct still encode Biden upstream?\n(Score 1 = upstream intact; score 0 = collapsed)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.suptitle("Arm 1: Linear probe recovery on biden_president_2023 refusal cases", y=1.02)
    fig.tight_layout()
    out = args.output_dir / "recovery_probe.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  saved {out}")

    # === Summary stats ===
    print("\n=== Per-layer recovery score summary ===")
    print(f"{'Layer':>6} {'Refused':>10} {'Answered':>10} {'UK PM':>10}")
    for l in range(0, n_layers, 2):  # every other layer for compact output
        r = (refused_mean[l] - base_nonbiden_proj[l]) / (denom[l] + 1e-9) if refused_mean is not None else float('nan')
        a = (answered_mean[l] - base_nonbiden_proj[l]) / (denom[l] + 1e-9) if answered_mean is not None else float('nan')
        u = (ukpm_mean[l] - base_nonbiden_proj[l]) / (denom[l] + 1e-9) if ukpm_mean is not None else float('nan')
        print(f"{l:>6} {r:>10.3f} {a:>10.3f} {u:>10.3f}")

    # Save numeric summary
    summary = {
        "biden_anchor_keys": available_biden,
        "nonbiden_anchor_keys": available_nonbiden,
        "instruct_refused_keys": instr_refused_keys,
        "instruct_answered_keys": instr_answered_keys,
        "instruct_ukpm_keys": instr_ukpm_keys,
        "by_layer": [
            {
                "layer": int(l),
                "base_biden_projection": float(base_biden_proj[l]),
                "base_nonbiden_projection": float(base_nonbiden_proj[l]),
                "refused_projection_mean": float(refused_mean[l]) if refused_mean is not None else None,
                "answered_projection_mean": float(answered_mean[l]) if answered_mean is not None else None,
                "ukpm_projection_mean": float(ukpm_mean[l]) if ukpm_mean is not None else None,
                "refused_recovery_score": float((refused_mean[l] - base_nonbiden_proj[l]) / (denom[l] + 1e-9)) if refused_mean is not None else None,
                "answered_recovery_score": float((answered_mean[l] - base_nonbiden_proj[l]) / (denom[l] + 1e-9)) if answered_mean is not None else None,
            }
            for l in range(n_layers)
        ],
    }
    (args.output_dir / "recovery_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(f"  saved {args.output_dir / 'recovery_summary.json'}")

    # === Interpretation hint ===
    print("\n=== Interpretation ===")
    if refused_mean is not None and answered_mean is not None:
        # Look at middle-late layers (where refusal gating peaks per Phase B)
        mid_late = slice(15, 28)
        refused_score_ml = ((refused_mean - base_nonbiden_proj) / (denom + 1e-9))[mid_late].mean()
        answered_score_ml = ((answered_mean - base_nonbiden_proj) / (denom + 1e-9))[mid_late].mean()
        print(f"Mean recovery score (layers 15-27, where Phase B located the gate):")
        print(f"  Instruct refused:  {refused_score_ml:.3f}")
        print(f"  Instruct answered: {answered_score_ml:.3f}")
        if refused_score_ml > 0.5:
            print("  >> REFUSED activations still encode Biden — framework's Regime 1 confirmed.")
            print("     Constraint is shallow routing on intact upstream representation.")
        elif refused_score_ml > 0.2:
            print("  >> Partial recovery — upstream is degraded but not collapsed.")
            print("     Mixed Regime 1/Regime 2.")
        else:
            print("  >> Recovery low — upstream representation has collapsed under refusal.")
            print("     Closer to Regime 2 than Regime 1.")


if __name__ == "__main__":
    main()
