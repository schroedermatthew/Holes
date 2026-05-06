"""
Phase A analysis: per-item specificity curves, per-category aggregates,
mechanism classification, base-vs-Instruct comparison.

Reads the scored outputs (and optionally the filled-in review template) and
produces both a text summary and matplotlib plots.

Usage:
    python analyze.py
    python analyze.py --output-dir outputs/
    python analyze.py --use-review     # use review_template.json if filled in
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


SURFACE_CLASS_ORDER = ["direct_or_distorted", "hedged", "refusal"]
SURFACE_CLASS_COLORS = {
    "direct_or_distorted": "#2a7c2a",
    "hedged": "#d9a300",
    "refusal": "#b8252e",
}


def load_data(output_dir: Path, use_review: bool = False):
    scored = json.loads((output_dir / "scored.json").read_text(encoding="utf-8"))

    review = None
    if use_review:
        rp = output_dir / "review_template_filled.json"
        if rp.exists():
            review = {entry["key"]: entry["review"] for entry in
                      json.loads(rp.read_text(encoding="utf-8"))
                      if entry["review"].get("mechanism")}
            print(f"Loaded {len(review)} reviewed entries from review_template_filled.json")
        else:
            print("WARNING: --use-review requested but review_template_filled.json not found; using rule-based only")

    return scored, review


def build_curves(scored: dict, review: dict | None = None):
    """Build per-item specificity curves: (item, model) -> [level -> class]."""
    curves = defaultdict(dict)

    for key, entry in scored.items():
        item_id = entry["item_id"]
        model = entry["model"]
        level = entry["level"]
        cls = entry["scoring"]["surface_class"]

        # Override with reviewer's mechanism if available
        if review and entry.get("key") in review and review[entry["key"]].get("mechanism"):
            mech = review[entry["key"]]["mechanism"]
            # Map mechanism to surface class
            cls = {
                "direct": "direct_or_distorted",
                "caveated_direct": "hedged",
                "refusal": "refusal",
                "distortion": "direct_or_distorted",  # surface direct, but reviewer flagged distortion
            }.get(mech, cls)

        curves[(item_id, model)][level] = {
            "surface_class": cls,
            "weight": entry["scoring"]["total_weight"],
            "topic": entry["topic"],
            "category": entry["category"],
        }

    return curves


def plot_specificity_curves(curves: dict, output_dir: Path):
    """Plot per-category specificity curves: x=level, y=hedge+refusal rate."""
    by_category = defaultdict(lambda: defaultdict(lambda: {"weight_sum": 0, "n": 0}))

    for (item_id, model), levels in curves.items():
        for level, data in levels.items():
            cat = data["category"]
            by_category[cat][(level, model)]["weight_sum"] += data["weight"]
            by_category[cat][(level, model)]["n"] += 1

    categories = ["A", "B", "C", "control"]
    fig, axes = plt.subplots(1, 4, figsize=(16, 4), sharey=True)
    for ax, cat in zip(axes, categories):
        levels = sorted(set(level for level, _ in by_category[cat].keys()))
        for model, color, marker in [("base", "#2266cc", "o"), ("instruct", "#cc4422", "s")]:
            avg_weights = []
            for level in levels:
                k = (level, model)
                if k in by_category[cat]:
                    avg = by_category[cat][k]["weight_sum"] / by_category[cat][k]["n"]
                    avg_weights.append(avg)
                else:
                    avg_weights.append(np.nan)
            ax.plot(levels, avg_weights, marker=marker, color=color, label=model, linewidth=2, markersize=8)
        ax.set_title(f"Category {cat}")
        ax.set_xlabel("Specificity level")
        ax.set_xticks([1, 2, 3, 4, 5])
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("Mean refusal/hedge signal weight")
    axes[0].legend()
    fig.suptitle("Specificity-axis response: refusal/hedge signal strength by level", y=1.02)
    fig.tight_layout()
    out = output_dir / "specificity_curves.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out}")


def plot_per_item_heatmap(curves: dict, output_dir: Path):
    """Plot a heatmap showing each item × level for the Instruct model."""
    items = sorted(set(item_id for (item_id, model), _ in curves.items()))
    items_with_cat = []
    for item_id in items:
        # Get category from any entry
        for (i, _), levels in curves.items():
            if i == item_id:
                cat = next(iter(levels.values()))["category"]
                items_with_cat.append((cat, item_id))
                break
    # Sort by category
    items_with_cat.sort(key=lambda x: ({"A": 0, "B": 1, "C": 2, "control": 3}.get(x[0], 4), x[1]))

    levels = [1, 2, 3, 4, 5]

    fig, axes = plt.subplots(1, 2, figsize=(14, max(6, len(items) * 0.3)))
    for ax, model in zip(axes, ["base", "instruct"]):
        matrix = np.full((len(items_with_cat), len(levels)), np.nan)
        for i, (cat, item_id) in enumerate(items_with_cat):
            entry = curves.get((item_id, model), {})
            for j, level in enumerate(levels):
                if level in entry:
                    matrix[i, j] = entry[level]["weight"]

        im = ax.imshow(matrix, aspect="auto", cmap="YlOrRd", vmin=0, vmax=10)
        ax.set_yticks(range(len(items_with_cat)))
        ax.set_yticklabels([f"[{c}] {i}" for c, i in items_with_cat], fontsize=8)
        ax.set_xticks(range(len(levels)))
        ax.set_xticklabels([f"L{l}" for l in levels])
        ax.set_title(f"{model.title()}: refusal/hedge signal weight")
    plt.colorbar(im, ax=axes, fraction=0.025)
    fig.suptitle("Per-item refusal/hedge weight: rows = items, cols = specificity levels", y=1.01)
    out = output_dir / "per_item_heatmap.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out}")


def identify_boundary(curves: dict) -> list:
    """For each item, identify where the constraint engages on the Instruct model."""
    boundaries = []
    items = sorted(set(item_id for (item_id, _), _ in curves.items()))
    for item_id in items:
        instruct = curves.get((item_id, "instruct"), {})
        base = curves.get((item_id, "base"), {})
        if not instruct or not base:
            continue
        cat = next(iter(instruct.values()))["category"]
        topic = next(iter(instruct.values()))["topic"]

        # Find the lowest level where Instruct hedges/refuses but base does not
        boundary_level = None
        for level in sorted(instruct.keys()):
            i_w = instruct[level]["weight"]
            b_w = base.get(level, {}).get("weight", 0)
            if i_w >= 2 and i_w > b_w + 1:
                boundary_level = level
                break

        # Get peak intensity on instruct
        peak_level = max(instruct.keys(), key=lambda l: instruct[l]["weight"])
        peak_weight = instruct[peak_level]["weight"]

        boundaries.append({
            "item_id": item_id,
            "category": cat,
            "topic": topic,
            "boundary_level": boundary_level,
            "peak_level": peak_level,
            "peak_weight_instruct": peak_weight,
            "peak_weight_base": base.get(peak_level, {}).get("weight", 0),
            "instruct_weights_by_level": {l: instruct[l]["weight"] for l in sorted(instruct.keys())},
            "base_weights_by_level": {l: base.get(l, {}).get("weight", 0) for l in sorted(instruct.keys())},
        })
    return boundaries


def print_boundary_table(boundaries: list):
    print("\n=== Per-item boundary identification (Instruct model) ===")
    print(f"{'Cat':<5} {'Item':<32} {'Boundary':>10} {'Peak L':>7} {'Peak W (i)':>12} {'Peak W (b)':>12}")
    cats_seen = set()
    for b in sorted(boundaries, key=lambda x: ({"A": 0, "B": 1, "C": 2, "control": 3}.get(x["category"], 4), x["item_id"])):
        if b["category"] not in cats_seen:
            print(f"  -- Category {b['category']} --")
            cats_seen.add(b["category"])
        bdy = f"L{b['boundary_level']}" if b["boundary_level"] else "—"
        print(f"  {b['category']:<3} {b['item_id']:<32} {bdy:>8} L{b['peak_level']:>5} "
              f"{b['peak_weight_instruct']:>10.1f} {b['peak_weight_base']:>10.1f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--use-review", action="store_true",
                        help="Use review_template_filled.json if available")
    args = parser.parse_args()

    if not (args.output_dir / "scored.json").exists():
        print("ERROR: scored.json not found. Run score_outputs.py first.")
        return

    scored, review = load_data(args.output_dir, use_review=args.use_review)

    curves = build_curves(scored, review)
    boundaries = identify_boundary(curves)

    (args.output_dir / "boundaries.json").write_text(
        json.dumps(boundaries, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print_boundary_table(boundaries)

    print("\n=== Generating plots ===")
    plot_specificity_curves(curves, args.output_dir)
    plot_per_item_heatmap(curves, args.output_dir)

    # Phase B prep: list items with strongest constraint engagement
    strong_items = [b for b in boundaries
                    if b["category"] != "control"
                    and b["peak_weight_instruct"] >= 4
                    and b["peak_weight_instruct"] > b["peak_weight_base"] + 2]
    strong_items.sort(key=lambda x: x["peak_weight_instruct"] - x["peak_weight_base"], reverse=True)

    print(f"\n=== Strongest constraint-engagement items (top candidates for Phase B) ===")
    print(f"{'Item':<32} {'Cat':<5} {'Boundary':>10} {'Peak Δ':>10}")
    for b in strong_items[:10]:
        bdy = f"L{b['boundary_level']}" if b["boundary_level"] else "—"
        delta = b["peak_weight_instruct"] - b["peak_weight_base"]
        print(f"  {b['item_id']:<32} {b['category']:<3} {bdy:>8} {delta:>10.1f}")

    print(f"\n=== Files written ===")
    print(f"  boundaries.json         : per-item boundary identification")
    print(f"  specificity_curves.png  : per-category specificity-axis curves")
    print(f"  per_item_heatmap.png    : per-item × level signal heatmap")


if __name__ == "__main__":
    main()
