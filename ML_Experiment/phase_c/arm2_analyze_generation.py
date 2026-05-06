"""
Phase C Arm 2: Generation activation analysis.

Reads base_hidden.npz and instruct_hidden.npz from arm2_extract_generation.py,
computes per-(layer, token) base-vs-Instruct distance, produces:

  1. Per-item heatmap: y=layer, x=response token position, color=relative distance
  2. Per-category mean profiles (averaged over tokens, plotted by layer)
  3. Per-token mean profiles (averaged over layers, plotted by position)

Framework predictions tested:
  - Misrep cases should show layer-wise structure during generation that's
    absent at prompt encoding (Phase B showed prompt-encoding flat for misrep)
  - Refusal case should show DIFFERENT pattern from misrep — either weaker
    (constraint already fired pre-generation) or qualitatively different
  - Control should be flat throughout

Usage:
    python arm2_analyze_generation.py
    python arm2_analyze_generation.py --activations-dir activations
"""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


# Plot order and colors — matches Arm 2 categorization
ROLE_ORDER = ["misrep_severe", "misrep", "misrep_mild", "correction", "refusal", "control"]
ROLE_COLORS = {
    "misrep_severe": "#aa1133",
    "misrep": "#cc4422",
    "misrep_mild": "#dd7755",
    "correction": "#ee9966",
    "refusal": "#3366cc",
    "control": "#666666",
}


def load_data(activations_dir: Path):
    base_path = activations_dir / "base_hidden.npz"
    instr_path = activations_dir / "instruct_hidden.npz"
    responses_path = activations_dir / "responses.json"

    if not (base_path.exists() and instr_path.exists() and responses_path.exists()):
        print(f"ERROR: required files not found in {activations_dir}/")
        print("Run `python arm2_extract_generation.py` first.")
        return None, None, None

    base = np.load(base_path)
    instr = np.load(instr_path)
    base_dict = {k: base[k] for k in base.files}
    instr_dict = {k: instr[k] for k in instr.files}
    responses = json.loads(responses_path.read_text(encoding="utf-8"))
    return base_dict, instr_dict, responses


def compute_distance(base_acts: np.ndarray, instr_acts: np.ndarray) -> np.ndarray:
    """Per (layer, token) L2 distance, normalized by base norm.

    Inputs shape: (n_layers + 1, n_tokens, hidden_dim)
    Returns: (n_layers + 1, n_tokens) relative distance.
    """
    base_f = base_acts.astype(np.float32)
    instr_f = instr_acts.astype(np.float32)
    d = np.linalg.norm(instr_f - base_f, axis=-1)
    base_norm = np.linalg.norm(base_f, axis=-1)
    return d / (base_norm + 1e-9)


def plot_heatmaps(
    base_acts: dict, instr_acts: dict, responses: dict, output_dir: Path, vmax: float = 1.5
):
    """One heatmap per item, layer × response token position."""
    valid_keys = [k for k in base_acts if k in instr_acts and base_acts[k].shape == instr_acts[k].shape]
    valid_keys.sort(key=lambda k: (
        ROLE_ORDER.index(responses[k]["role"]) if responses[k]["role"] in ROLE_ORDER else 99,
        k,
    ))

    n = len(valid_keys)
    cols = 3
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(15, 4.2 * rows), squeeze=False)

    for idx, key in enumerate(valid_keys):
        ax = axes[idx // cols][idx % cols]
        d = compute_distance(base_acts[key], instr_acts[key])
        im = ax.imshow(d, aspect="auto", cmap="YlOrRd", vmin=0, vmax=vmax, origin="upper")
        role = responses[key]["role"]
        ax.set_title(f"{key}\nrole: {role}", fontsize=10)
        ax.set_xlabel("Response token position")
        ax.set_ylabel("Layer index")
        plt.colorbar(im, ax=ax, fraction=0.04)

    # Hide unused subplots
    for idx in range(n, rows * cols):
        axes[idx // cols][idx % cols].axis("off")

    fig.suptitle(
        "Arm 2: Layer × token base-vs-Instruct relative distance during generation",
        y=1.0,
    )
    fig.tight_layout()
    out = output_dir / "generation_heatmaps.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out}")


def plot_layer_profiles_by_role(
    base_acts: dict, instr_acts: dict, responses: dict, output_dir: Path
):
    """Mean over response tokens per layer, grouped by role."""
    fig, ax = plt.subplots(figsize=(12, 6))

    valid_keys = [k for k in base_acts if k in instr_acts and base_acts[k].shape == instr_acts[k].shape]

    n_layers = None
    for key in valid_keys:
        d = compute_distance(base_acts[key], instr_acts[key])
        if n_layers is None:
            n_layers = d.shape[0]
        layers = np.arange(n_layers)
        # Mean over response tokens
        layer_profile = d.mean(axis=1)
        role = responses[key]["role"]
        color = ROLE_COLORS.get(role, "black")
        ax.plot(layers, layer_profile, color=color, linewidth=1.5, alpha=0.5,
                label=f"{key} ({role})")

    # Group means
    by_role = {}
    for key in valid_keys:
        role = responses[key]["role"]
        d = compute_distance(base_acts[key], instr_acts[key]).mean(axis=1)
        by_role.setdefault(role, []).append(d)

    for role, profiles in by_role.items():
        if len(profiles) >= 1:
            mean_profile = np.mean(profiles, axis=0)
            ax.plot(np.arange(len(mean_profile)), mean_profile,
                    color=ROLE_COLORS.get(role, "black"),
                    linewidth=3.5, linestyle="-",
                    label=f"{role} mean", alpha=1.0)

    ax.set_xlabel("Layer index")
    ax.set_ylabel("Mean relative L2 distance (averaged over response tokens)")
    ax.set_title("Generation-time divergence by layer, grouped by Phase B role")
    ax.legend(fontsize=8, loc="best", ncol=2)
    ax.grid(True, alpha=0.3)

    out = output_dir / "generation_layer_profiles.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out}")


def plot_token_position_profiles(
    base_acts: dict, instr_acts: dict, responses: dict, output_dir: Path
):
    """Mean over layers per token position, grouped by role.

    Shows whether divergence builds up over generated tokens (constraint
    accumulating during generation) or stays roughly constant.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    valid_keys = [k for k in base_acts if k in instr_acts and base_acts[k].shape == instr_acts[k].shape]

    for key in valid_keys:
        d = compute_distance(base_acts[key], instr_acts[key])
        # Mean over layers (skip layer 0 = post-embedding to avoid dominance by embedding mismatch)
        token_profile = d[1:].mean(axis=0)
        positions = np.arange(len(token_profile))
        role = responses[key]["role"]
        color = ROLE_COLORS.get(role, "black")
        ax.plot(positions, token_profile, color=color, linewidth=1.5, alpha=0.7,
                label=f"{key} ({role})")

    ax.set_xlabel("Response token position (0 = first response token)")
    ax.set_ylabel("Mean relative L2 distance (averaged over layers 1-32)")
    ax.set_title("Generation-time divergence by token position\n(does the constraint build up over generation?)")
    ax.legend(fontsize=8, loc="best", ncol=2)
    ax.grid(True, alpha=0.3)

    out = output_dir / "generation_token_profiles.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out}")


def print_summary_stats(
    base_acts: dict, instr_acts: dict, responses: dict, output_dir: Path
):
    """Per-item summary: peak layer, peak token, mean middle-layer divergence."""
    print("\n=== Per-item generation-divergence summary ===")
    print(f"{'Item':<32} {'Role':<14} {'Peak L':>7} {'Peak Tok':>9} {'MidL mean':>10} {'Token0':>8} {'TokenN':>8}")

    summary = []
    valid_keys = [k for k in base_acts if k in instr_acts and base_acts[k].shape == instr_acts[k].shape]
    for key in sorted(valid_keys, key=lambda k: (
        ROLE_ORDER.index(responses[k]["role"]) if responses[k]["role"] in ROLE_ORDER else 99,
        k,
    )):
        d = compute_distance(base_acts[key], instr_acts[key])
        # Skip layer 0 for some metrics (it's just post-embedding)
        d_inner = d[1:]
        peak_idx = np.unravel_index(np.argmax(d_inner), d_inner.shape)
        peak_layer = int(peak_idx[0]) + 1
        peak_token = int(peak_idx[1])

        mid_layers = slice(8, 25)
        mid_mean = float(d_inner[mid_layers, :].mean())
        token0 = float(d_inner[:, 0].mean())
        tokenN = float(d_inner[:, -1].mean())

        role = responses[key]["role"]
        print(f"{key:<32} {role:<14} {peak_layer:>7} {peak_token:>9} {mid_mean:>10.3f} {token0:>8.3f} {tokenN:>8.3f}")

        summary.append({
            "key": key,
            "role": role,
            "peak_layer": peak_layer,
            "peak_token": peak_token,
            "mid_layer_mean_distance": mid_mean,
            "first_token_mean_distance": token0,
            "last_token_mean_distance": tokenN,
        })

    (output_dir / "arm2_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(f"\n  saved {output_dir / 'arm2_summary.json'}")


def print_first_response_tokens(responses: dict, base_acts: dict, instr_acts: dict, output_dir: Path):
    """Print the first ~30 chars of each response, for sanity-checking what's being analyzed."""
    print("\n=== Generated response previews ===")
    for key, r in responses.items():
        if key not in base_acts or key not in instr_acts:
            continue
        preview = r["response"][:120].replace("\n", " ")
        if len(r["response"]) > 120:
            preview += "..."
        print(f"  [{key}] [{r['role']}]")
        print(f"    Q: {r['question'][:80]}{'...' if len(r['question']) > 80 else ''}")
        print(f"    A: {preview}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--activations-dir", type=Path, default=Path("activations"))
    parser.add_argument("--output-dir", type=Path, default=Path("analysis"))
    parser.add_argument("--vmax", type=float, default=1.5,
                        help="Color scale max for heatmaps")
    args = parser.parse_args()

    base_acts, instr_acts, responses = load_data(args.activations_dir)
    if base_acts is None:
        return

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print_first_response_tokens(responses, base_acts, instr_acts, args.output_dir)

    print("\n=== Generating plots ===")
    plot_heatmaps(base_acts, instr_acts, responses, args.output_dir, vmax=args.vmax)
    plot_layer_profiles_by_role(base_acts, instr_acts, responses, args.output_dir)
    plot_token_position_profiles(base_acts, instr_acts, responses, args.output_dir)

    print_summary_stats(base_acts, instr_acts, responses, args.output_dir)

    print("\n=== Files written ===")
    print(f"  generation_heatmaps.png        : per-item layer × token heatmap")
    print(f"  generation_layer_profiles.png  : layer profiles grouped by role")
    print(f"  generation_token_profiles.png  : token-position profiles by role")
    print(f"  arm2_summary.json              : per-item peak/mean stats")


if __name__ == "__main__":
    main()
