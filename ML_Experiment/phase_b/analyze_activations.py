"""
Phase B: Layer-wise activation distance analysis.

Reads activations_base.npz and activations_instruct.npz from extract_activations.py,
computes the framework's diagnostic quantities, produces plots and a summary.

Key quantities computed:
  - D_l(x) = ||a_l(x; theta_instruct) - a_l(x; theta_base)||_2 per layer
  - cos(a_l(x; theta_base), a_l(x; theta_instruct)) per layer
  - Within-Instruct contrast: ||a_l(L1; instruct) - a_l(L4; instruct)||_2 for biden_president_2023

Framework predictions tested:
  1. Refusal-mediated cancellation has late-concentrated D_l profile
  2. Misrepresentation-mediated cancellation has more distributed D_l profile
  3. Controls have low D_l throughout
  4. Within-item L1-vs-L4 on biden_president shows late-concentrated divergence

Usage:
    python analyze_activations.py
    python analyze_activations.py --activations-dir activations/
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


GROUP_COLORS = {
    "refusal_cluster": "#cc4422",
    "refusal_within_item_control": "#ff9966",
    "misrep_cluster": "#7733aa",
    "misrep_within_item_control": "#bb99dd",
    "no_constraint_control": "#888888",
    "factual_control": "#22aa66",
}

GROUP_LABELS = {
    "refusal_cluster": "Refusal (Phase A flagged)",
    "refusal_within_item_control": "Refusal item, non-flagged level",
    "misrep_cluster": "Misrepresentation (Phase A flagged)",
    "misrep_within_item_control": "Misrep item, non-flagged level",
    "no_constraint_control": "Sensitive but unconstrained (Cat C)",
    "factual_control": "Factual control",
}


def load_activations(activations_dir: Path):
    base_path = activations_dir / "activations_base.npz"
    instr_path = activations_dir / "activations_instruct.npz"
    if not base_path.exists() or not instr_path.exists():
        print(f"ERROR: activations not found in {activations_dir}/")
        print("Run `python extract_activations.py` first.")
        return None, None
    base = np.load(base_path)
    instruct = np.load(instr_path)
    base_dict = {k: base[k] for k in base.files}
    instr_dict = {k: instruct[k] for k in instruct.files}
    return base_dict, instr_dict


def compute_l2_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Per-layer L2 distance. a, b shape: (num_layers, hidden_dim). Returns (num_layers,)."""
    return np.linalg.norm(a - b, axis=-1)


def compute_cosine_sim(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Per-layer cosine similarity."""
    a_norm = a / (np.linalg.norm(a, axis=-1, keepdims=True) + 1e-9)
    b_norm = b / (np.linalg.norm(b, axis=-1, keepdims=True) + 1e-9)
    return np.sum(a_norm * b_norm, axis=-1)


def normalize_distance(d: np.ndarray, base_norms: np.ndarray) -> np.ndarray:
    """Distance normalized by base activation norm (relative scale)."""
    return d / (base_norms + 1e-9)


def plot_per_item_distance(
    base_acts: dict, instr_acts: dict, targets: list, output_dir: Path
):
    """One line per (item, level), grouped/colored by group."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    by_group = defaultdict(list)
    for t in targets:
        key = f"{t['item_id']}_L{t['level']}"
        if key not in base_acts or key not in instr_acts:
            continue
        b = base_acts[key]
        i = instr_acts[key]
        if b.shape != i.shape:
            print(f"  [warn] shape mismatch for {key}: base {b.shape}, instruct {i.shape}")
            continue
        d = compute_l2_distance(b, i)
        cos = compute_cosine_sim(b, i)
        b_norms = np.linalg.norm(b, axis=-1)
        d_rel = normalize_distance(d, b_norms)
        by_group[t["group"]].append({
            "key": key,
            "raw": d,
            "relative": d_rel,
            "cosine": cos,
            "label": f"{t['item_id']} L{t['level']}",
        })

    n_layers = next(iter(by_group.values()))[0]["raw"].shape[0]
    layers = np.arange(n_layers)

    # Left: relative L2 distance
    ax = axes[0]
    for group, items in by_group.items():
        color = GROUP_COLORS.get(group, "black")
        for item in items:
            ax.plot(layers, item["relative"], color=color, alpha=0.55, linewidth=1.0)
    # Group means with label
    for group, items in by_group.items():
        color = GROUP_COLORS.get(group, "black")
        mean = np.mean([item["relative"] for item in items], axis=0)
        ax.plot(layers, mean, color=color, linewidth=3.0, label=GROUP_LABELS.get(group, group))
    ax.set_xlabel("Layer index (0 = post-embedding)")
    ax.set_ylabel("|| a_instruct - a_base || / ||a_base||")
    ax.set_title("Relative L2 distance by layer\n(thin: per-item; thick: group mean)")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(True, alpha=0.3)

    # Right: cosine similarity
    ax = axes[1]
    for group, items in by_group.items():
        color = GROUP_COLORS.get(group, "black")
        for item in items:
            ax.plot(layers, item["cosine"], color=color, alpha=0.55, linewidth=1.0)
    for group, items in by_group.items():
        color = GROUP_COLORS.get(group, "black")
        mean = np.mean([item["cosine"] for item in items], axis=0)
        ax.plot(layers, mean, color=color, linewidth=3.0, label=GROUP_LABELS.get(group, group))
    ax.set_xlabel("Layer index")
    ax.set_ylabel("cos(a_base, a_instruct)")
    ax.set_title("Cosine similarity by layer\n(lower = more representational divergence)")
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(True, alpha=0.3)

    fig.suptitle("Layer-wise representational divergence: Instruct vs Base", y=1.02)
    fig.tight_layout()
    out = output_dir / "layer_distance_profiles.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out}")
    return by_group


def plot_within_item_biden(
    base_acts: dict, instr_acts: dict, output_dir: Path
):
    """
    The cleanest single experiment: biden_president L1 (refused) vs L4 (answered),
    on Instruct alone. Same item, same model, same content — only question form differs.

    If refusal-mediated gating is real and shallow, the activations should diverge
    at late layers where the gate fires.
    """
    needed = [f"biden_president_2023_L{l}" for l in [1, 2, 3, 4, 5]]
    if not all(k in instr_acts for k in needed):
        print("  [skip] biden_president_2023 within-item plot — missing activations")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    refused_keys = ["biden_president_2023_L1", "biden_president_2023_L2", "biden_president_2023_L3"]
    answered_keys = ["biden_president_2023_L4", "biden_president_2023_L5"]

    # Left: pairwise L2 distances within Instruct between refused and answered levels
    ax = axes[0]
    n_layers = instr_acts[refused_keys[0]].shape[0]
    layers = np.arange(n_layers)

    refused_acts = np.stack([instr_acts[k] for k in refused_keys])  # (3, n_layers, hidden)
    answered_acts = np.stack([instr_acts[k] for k in answered_keys])  # (2, n_layers, hidden)

    refused_mean = refused_acts.mean(axis=0)
    answered_mean = answered_acts.mean(axis=0)

    diff = refused_mean - answered_mean
    diff_norm = np.linalg.norm(diff, axis=-1)
    base_norm_ref = np.linalg.norm(refused_mean, axis=-1)
    rel = diff_norm / (base_norm_ref + 1e-9)

    ax.plot(layers, rel, color="#cc4422", linewidth=2.5, marker="o", label="|| refused - answered || / ||refused||")
    ax.set_xlabel("Layer index")
    ax.set_ylabel("Relative L2 distance")
    ax.set_title("biden_president_2023 within-Instruct\nRefused (L1-L3) vs Answered (L4-L5)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Right: L2 base-vs-Instruct on each individual biden level
    ax = axes[1]
    for level, color in zip([1, 2, 3, 4, 5], ["#cc1111", "#cc3322", "#cc5544", "#3388cc", "#2266cc"]):
        key = f"biden_president_2023_L{level}"
        if key not in base_acts:
            continue
        d = compute_l2_distance(base_acts[key], instr_acts[key])
        b_norm = np.linalg.norm(base_acts[key], axis=-1)
        rel = d / (b_norm + 1e-9)
        marker = "o" if level <= 3 else "s"
        label = f"L{level} ({'refused' if level <= 3 else 'answered'})"
        ax.plot(layers, rel, color=color, linewidth=2, marker=marker, label=label)
    ax.set_xlabel("Layer index")
    ax.set_ylabel("|| a_instruct - a_base || / ||a_base||")
    ax.set_title("biden_president_2023 base-vs-Instruct\n(per question level)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.suptitle("Within-item refusal gating signature on biden_president_2023", y=1.02)
    fig.tight_layout()
    out = output_dir / "biden_within_item.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out}")


def plot_individual_focus(
    base_acts: dict, instr_acts: dict, focus_keys: list, output_dir: Path
):
    """Detailed per-key view of high-priority items."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    n_layers = base_acts[focus_keys[0]].shape[0]
    layers = np.arange(n_layers)

    colors = plt.cm.plasma(np.linspace(0.1, 0.85, len(focus_keys)))

    ax = axes[0]
    for k, c in zip(focus_keys, colors):
        if k not in base_acts or k not in instr_acts:
            continue
        d = compute_l2_distance(base_acts[k], instr_acts[k])
        b_norm = np.linalg.norm(base_acts[k], axis=-1)
        rel = d / (b_norm + 1e-9)
        ax.plot(layers, rel, color=c, linewidth=2, marker=".", label=k)
    ax.set_xlabel("Layer index")
    ax.set_ylabel("Relative L2 distance")
    ax.set_title("Focus items: relative L2 distance by layer")
    ax.legend(fontsize=7, loc="upper left")
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    for k, c in zip(focus_keys, colors):
        if k not in base_acts or k not in instr_acts:
            continue
        cos = compute_cosine_sim(base_acts[k], instr_acts[k])
        ax.plot(layers, cos, color=c, linewidth=2, marker=".", label=k)
    ax.set_xlabel("Layer index")
    ax.set_ylabel("cos(a_base, a_instruct)")
    ax.set_title("Focus items: cosine similarity by layer")
    ax.legend(fontsize=7, loc="lower left")
    ax.grid(True, alpha=0.3)

    fig.suptitle("Per-item layer profiles for high-priority cases", y=1.02)
    fig.tight_layout()
    out = output_dir / "focus_items.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out}")


def classify_profile_shape(rel_distance: np.ndarray) -> dict:
    """
    Heuristic classification of layer-wise distance profile shape.

    Returns dict with:
      - peak_layer: index of maximum
      - peak_relative_position: peak_layer / num_layers (0..1)
      - early_mass: mean over first third of layers
      - late_mass: mean over last third
      - late_to_early_ratio: late_mass / max(early_mass, 1e-6)
      - shape_class: "late_concentrated" / "distributed" / "flat"
    """
    n = len(rel_distance)
    third = max(1, n // 3)
    early = rel_distance[:third].mean()
    middle = rel_distance[third:2*third].mean()
    late = rel_distance[2*third:].mean()
    peak_layer = int(np.argmax(rel_distance))

    if rel_distance.max() < 0.05:
        shape = "flat"
    elif late > 1.5 * early and late > 1.2 * middle:
        shape = "late_concentrated"
    elif rel_distance.max() < 2 * rel_distance.mean():
        shape = "distributed"
    else:
        shape = "mixed"

    return {
        "peak_layer": peak_layer,
        "peak_relative_position": peak_layer / max(n - 1, 1),
        "early_mass": float(early),
        "middle_mass": float(middle),
        "late_mass": float(late),
        "late_to_early_ratio": float(late / max(early, 1e-6)),
        "shape_class": shape,
    }


def print_summary(by_group: dict, base_acts: dict, instr_acts: dict, targets: list):
    """Print the per-item shape classification table."""
    print("\n=== Layer-wise profile shape classification ===")
    print(f"{'Item':<32} {'Group':<32} {'Peak L':>7} {'Peak %':>7} {'L/E':>6} {'Shape':>20}")
    print("-" * 110)

    cases_for_phase_c = []

    for t in sorted(targets, key=lambda x: (x["group"], x["item_id"], x["level"])):
        key = f"{t['item_id']}_L{t['level']}"
        if key not in base_acts or key not in instr_acts:
            continue
        d = compute_l2_distance(base_acts[key], instr_acts[key])
        b_norms = np.linalg.norm(base_acts[key], axis=-1)
        rel = d / (b_norms + 1e-9)
        shape = classify_profile_shape(rel)
        print(f"{key:<32} {t['group']:<32} "
              f"{shape['peak_layer']:>7} {shape['peak_relative_position']*100:>6.0f}% "
              f"{shape['late_to_early_ratio']:>6.1f} {shape['shape_class']:>20}")
        cases_for_phase_c.append((key, t, shape))

    # Aggregate by group
    print("\n=== Group-mean profile shape ===")
    print(f"{'Group':<40} {'Mean peak%':>11} {'Mean L/E':>10} {'Modal shape':>22}")
    for group, items in by_group.items():
        if not items:
            continue
        peak_positions = []
        late_to_early = []
        shapes = []
        for item in items:
            shape = classify_profile_shape(item["relative"])
            peak_positions.append(shape["peak_relative_position"])
            late_to_early.append(shape["late_to_early_ratio"])
            shapes.append(shape["shape_class"])
        from collections import Counter
        modal = Counter(shapes).most_common(1)[0][0]
        print(f"{group:<40} {np.mean(peak_positions)*100:>10.0f}% "
              f"{np.mean(late_to_early):>10.1f} {modal:>22}")

    return cases_for_phase_c


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--activations-dir", type=Path, default=Path("activations"))
    parser.add_argument("--targets", type=Path, default=Path("targets.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("analysis"))
    args = parser.parse_args()

    base_acts, instr_acts = load_activations(args.activations_dir)
    if base_acts is None:
        return

    args.output_dir.mkdir(parents=True, exist_ok=True)

    targets = json.loads(args.targets.read_text(encoding="utf-8"))["targets"]

    print("=== Generating plots ===")
    by_group = plot_per_item_distance(base_acts, instr_acts, targets, args.output_dir)
    plot_within_item_biden(base_acts, instr_acts, args.output_dir)

    focus_keys = [
        "biden_president_2023_L1",
        "biden_president_2023_L4",
        "crime_demographics_us_L3",
        "crime_demographics_us_L1",
        "founding_fathers_L4",
        "wehrmacht_1943_L4",
        "medieval_knights_L4",
        "ancient_rome_senate_L3",
        "control_periodic_table_L3",
    ]
    plot_individual_focus(base_acts, instr_acts, focus_keys, args.output_dir)

    cases = print_summary(by_group, base_acts, instr_acts, targets)

    # Save shape classifications
    shape_data = []
    for key, t, shape in cases:
        shape_data.append({"key": key, "target": t, "profile_shape": shape})
    (args.output_dir / "profile_shapes.json").write_text(
        json.dumps(shape_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("\n=== Files written ===")
    print(f"  layer_distance_profiles.png  : per-group layer-wise distance (key plot)")
    print(f"  biden_within_item.png        : within-Instruct refused-vs-answered contrast")
    print(f"  focus_items.png              : detailed per-item profiles for top cases")
    print(f"  profile_shapes.json          : per-item shape classification")


if __name__ == "__main__":
    main()
