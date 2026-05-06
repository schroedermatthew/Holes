"""
Phase A analysis v2 — uses the corrected scoring from score_outputs_v2.py.

Reads scored_v2.json and divergence.json, produces:
  - Per-category specificity curves (refusal + misrepresentation rates by level)
  - Per-item heatmap (rows: items, cols: levels, color: Instruct constraint signal)
  - Per-item boundary identification (where does the constraint first engage)
  - Ranked Phase B candidate list

Usage:
    python analyze_v2.py
    python analyze_v2.py --output-dir outputs/
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


CATEGORY_ORDER = ["A", "B", "C", "control"]
CATEGORY_TITLES = {
    "A": "A — Historical identity",
    "B": "B — Contemporary politics",
    "C": "C — Documented sensitive facts",
    "control": "Control",
}


def load_data(output_dir: Path):
    scored_path = output_dir / "scored_v2.json"
    div_path = output_dir / "divergence.json"
    if not scored_path.exists():
        print(f"ERROR: {scored_path} not found.")
        print("Run `python score_outputs_v2.py` first.")
        return None, None
    if not div_path.exists():
        print(f"ERROR: {div_path} not found.")
        print("Run `python score_outputs_v2.py` first.")
        return None, None
    return (
        json.loads(scored_path.read_text(encoding="utf-8")),
        json.loads(div_path.read_text(encoding="utf-8")),
    )


def build_curves(scored: dict):
    """For each (item, model, level), get refusal/misrep weights and class."""
    curves = defaultdict(dict)
    for key, entry in scored.items():
        item_id = entry["item_id"]
        model = entry["model_variant"]
        level = entry["level"]
        s = entry["scoring_v2"]
        curves[(item_id, model)][level] = {
            "category": entry["category"],
            "topic": entry["topic"],
            "refusal_weight": s["refusal"]["weight"],
            "misrep_weight": s["misrep"]["weight"],
            "total_weight": s["refusal"]["weight"] + s["misrep"]["weight"],
            "class": s["class"],
        }
    return curves


def plot_specificity_curves(curves: dict, output_dir: Path):
    """Per-category curves: x=level, y=refusal/misrep signal weight, base vs instruct."""
    by_cat_lvl_model = defaultdict(lambda: defaultdict(list))
    for (item_id, model), levels in curves.items():
        for level, data in levels.items():
            by_cat_lvl_model[data["category"]][(level, model)].append(data)

    fig, axes = plt.subplots(2, 4, figsize=(16, 8), sharey="row")
    fig.suptitle("Specificity-axis response: signal weights by level\n(top: refusal, bottom: misrepresentation)", y=1.00)

    for col, cat in enumerate(CATEGORY_ORDER):
        for row, signal_key in enumerate(["refusal_weight", "misrep_weight"]):
            ax = axes[row, col]
            levels = sorted(set(level for level, _ in by_cat_lvl_model[cat].keys()))
            for model, color, marker in [("base", "#2266cc", "o"), ("instruct", "#cc4422", "s")]:
                weights = []
                for level in levels:
                    items = by_cat_lvl_model[cat].get((level, model), [])
                    if items:
                        weights.append(np.mean([item[signal_key] for item in items]))
                    else:
                        weights.append(np.nan)
                ax.plot(levels, weights, marker=marker, color=color, label=model, linewidth=2, markersize=7)
            if row == 0:
                ax.set_title(CATEGORY_TITLES[cat], fontsize=10)
            if row == 1:
                ax.set_xlabel("Specificity level")
            if col == 0:
                ax.set_ylabel("Refusal weight" if row == 0 else "Misrep weight")
            ax.set_xticks([1, 2, 3, 4, 5])
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=8)

    fig.tight_layout()
    out = output_dir / "specificity_curves_v2.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out}")


def plot_per_item_heatmap(curves: dict, output_dir: Path):
    """Heatmap: rows=items, cols=levels, color=Instruct signal weight."""
    items_with_cat = []
    seen = set()
    for (item_id, _), levels in curves.items():
        if item_id in seen:
            continue
        seen.add(item_id)
        cat = next(iter(levels.values()))["category"]
        items_with_cat.append((cat, item_id))
    items_with_cat.sort(key=lambda x: (CATEGORY_ORDER.index(x[0]) if x[0] in CATEGORY_ORDER else 9, x[1]))

    levels = [1, 2, 3, 4, 5]

    fig, axes = plt.subplots(1, 3, figsize=(16, max(6, len(items_with_cat) * 0.32)), sharey=True)

    matrices = {}
    for model in ["base", "instruct"]:
        m = np.full((len(items_with_cat), len(levels)), np.nan)
        for i, (_, item_id) in enumerate(items_with_cat):
            entry = curves.get((item_id, model), {})
            for j, lvl in enumerate(levels):
                if lvl in entry:
                    m[i, j] = entry[lvl]["total_weight"]
        matrices[model] = m

    diff = matrices["instruct"] - matrices["base"]

    vmax = max(8.0, np.nanmax(matrices["instruct"]) if np.any(~np.isnan(matrices["instruct"])) else 8.0)

    for ax, model_or_diff, title, cmap, vmin, vmax_use in [
        (axes[0], matrices["base"], "Base", "YlOrRd", 0, vmax),
        (axes[1], matrices["instruct"], "Instruct", "YlOrRd", 0, vmax),
        (axes[2], diff, "Instruct − Base", "RdBu_r", -vmax, vmax),
    ]:
        im = ax.imshow(model_or_diff, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax_use)
        ax.set_yticks(range(len(items_with_cat)))
        ax.set_yticklabels([f"[{c}] {i}" for c, i in items_with_cat], fontsize=8)
        ax.set_xticks(range(len(levels)))
        ax.set_xticklabels([f"L{l}" for l in levels])
        ax.set_title(title)
        plt.colorbar(im, ax=ax, fraction=0.04)

    fig.suptitle(
        "Per-item constraint signal (refusal + misrep weight)\n"
        "Right panel: Instruct minus base — red = Instruct adds constraint engagement",
        y=1.01,
    )
    out = output_dir / "per_item_heatmap_v2.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out}")


def identify_boundaries(curves: dict) -> list:
    """For each item, find lowest level where Instruct shows constraint that base doesn't."""
    boundaries = []
    items = sorted(set(item_id for (item_id, _), _ in curves.items()))
    for item_id in items:
        instruct = curves.get((item_id, "instruct"), {})
        base = curves.get((item_id, "base"), {})
        if not instruct or not base:
            continue

        cat = next(iter(instruct.values()))["category"]
        topic = next(iter(instruct.values()))["topic"]

        boundary_level = None
        for level in sorted(instruct.keys()):
            i_w = instruct[level]["total_weight"]
            b_w = base.get(level, {}).get("total_weight", 0)
            if i_w >= 2 and i_w > b_w + 1:
                boundary_level = level
                break

        # Mechanism classification: refusal-dominant vs misrep-dominant on Instruct
        i_ref_total = sum(instruct[l]["refusal_weight"] for l in instruct)
        i_mis_total = sum(instruct[l]["misrep_weight"] for l in instruct)
        if i_ref_total > i_mis_total and i_ref_total >= 3:
            mechanism = "refusal"
        elif i_mis_total > i_ref_total and i_mis_total >= 3:
            mechanism = "misrep"
        elif i_ref_total >= 2 and i_mis_total >= 2:
            mechanism = "mixed"
        else:
            mechanism = "—"

        peak_level = max(instruct.keys(), key=lambda l: instruct[l]["total_weight"])
        peak_weight_i = instruct[peak_level]["total_weight"]
        peak_weight_b = base.get(peak_level, {}).get("total_weight", 0)

        boundaries.append({
            "item_id": item_id,
            "category": cat,
            "topic": topic,
            "boundary_level": boundary_level,
            "mechanism": mechanism,
            "peak_level": peak_level,
            "peak_weight_instruct": peak_weight_i,
            "peak_weight_base": peak_weight_b,
            "delta": peak_weight_i - peak_weight_b,
            "instruct_refusal_total": i_ref_total,
            "instruct_misrep_total": i_mis_total,
            "instruct_weights_by_level": {l: instruct[l]["total_weight"] for l in sorted(instruct.keys())},
        })
    return boundaries


def print_boundary_table(boundaries: list):
    print("\n=== Per-item boundary identification ===")
    print(f"{'Cat':<5} {'Item':<32} {'Boundary':>8} {'Mechanism':>10} {'Peak L':>7} {'Δ peak':>8}")

    cats_seen = set()
    for b in sorted(boundaries, key=lambda x: (CATEGORY_ORDER.index(x["category"]) if x["category"] in CATEGORY_ORDER else 9, x["item_id"])):
        if b["category"] not in cats_seen:
            print(f"  -- Category {b['category']} --")
            cats_seen.add(b["category"])
        bdy = f"L{b['boundary_level']}" if b["boundary_level"] else "—"
        print(f"  {b['category']:<3} {b['item_id']:<32} {bdy:>8} {b['mechanism']:>10} L{b['peak_level']:>5} {b['delta']:>+8.1f}")


def print_phase_b_candidates(boundaries: list, divergence: dict):
    """Rank items for Phase B layer-wise analysis."""
    candidates = [b for b in boundaries
                  if b["category"] != "control"
                  and (b["delta"] >= 2 or b["mechanism"] in ("refusal", "misrep", "mixed"))]
    candidates.sort(key=lambda b: -b["delta"])

    print("\n=== Phase B candidates (constraint-engaged items, ranked by Δ peak weight) ===")
    if not candidates:
        print("  No clear constraint-engaged items found.")
        return

    print(f"{'Rank':>4}  {'Item':<32} {'Cat':<5} {'Mech':>8} {'Bdy':>5} {'Peak L':>7} {'Δ':>6}")
    for i, b in enumerate(candidates[:15], 1):
        bdy = f"L{b['boundary_level']}" if b["boundary_level"] else "—"
        print(f"{i:>4}  {b['item_id']:<32} {b['category']:<5} {b['mechanism']:>8} {bdy:>5} L{b['peak_level']:>5} {b['delta']:>+6.1f}")


def print_factual_divergence(divergence: dict):
    """List items with high factual divergence between base and Instruct."""
    flagged = [d for d in divergence.values() if d["factual_divergence"]["score"] >= 2]
    if not flagged:
        return
    print("\n=== Factual divergence flags (base ↔ Instruct content disagreement) ===")
    print(f"{'Cat':<5} {'Item':<32} {'L':>3} {'Score':>6} {'Signals'}")
    for d in sorted(flagged, key=lambda x: -x["factual_divergence"]["score"]):
        sigs = ", ".join(d["factual_divergence"]["signals"])
        print(f"  {d['category']:<3} {d['item_id']:<32} L{d['level']:>2} {d['factual_divergence']['score']:>6} {sigs}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()

    scored, divergence = load_data(args.output_dir)
    if scored is None:
        return

    curves = build_curves(scored)
    boundaries = identify_boundaries(curves)

    (args.output_dir / "boundaries_v2.json").write_text(
        json.dumps(boundaries, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print_boundary_table(boundaries)
    print_factual_divergence(divergence)
    print_phase_b_candidates(boundaries, divergence)

    print("\n=== Generating plots ===")
    plot_specificity_curves(curves, args.output_dir)
    plot_per_item_heatmap(curves, args.output_dir)

    print("\n=== Files written ===")
    print(f"  boundaries_v2.json         : per-item boundary identification")
    print(f"  specificity_curves_v2.png  : per-category curves, both signal types")
    print(f"  per_item_heatmap_v2.png    : per-item × level signal heatmap")


if __name__ == "__main__":
    main()
