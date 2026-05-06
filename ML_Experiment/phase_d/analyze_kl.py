"""
Phase D: KL divergence analysis and substitution report.

Reads kl_results.json from compute_kl.py, produces:

  1. Per-item KL by position (multi-panel plot).
  2. Group-mean KL by position (line plot).
  3. Substitution report — for each item, the top-N highest-KL positions,
     with the actual emitted token, what base would have predicted, and
     the surrounding context. This is the most interpretable output:
     it shows WHERE in the response the constraint operates and WHAT
     it substitutes.

The framework's revised-revised prediction (after Phase C):
  - Misrep = positional token-level substitutions at constraint-trigger positions
  - Refusal = high KL throughout the response (Instruct's whole refusal text
    is alien to base's distribution)
  - Control = uniformly low KL

Usage:
    python analyze_kl.py
    python analyze_kl.py --results-dir results --top-n 8
"""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROLE_ORDER = ["misrep_severe", "misrep", "misrep_mild", "correction", "refusal", "control"]
ROLE_COLORS = {
    "misrep_severe": "#aa1133",
    "misrep": "#cc4422",
    "misrep_mild": "#dd7755",
    "correction": "#ee9966",
    "refusal": "#3366cc",
    "control": "#666666",
}


def plot_kl_by_position_per_item(results: dict, output_dir: Path):
    """Per-item KL trace, multi-panel."""
    keys = sorted(results.keys(),
                  key=lambda k: ROLE_ORDER.index(results[k]["role"]) if results[k]["role"] in ROLE_ORDER else 99)

    n = len(keys)
    cols = 3
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(15, 4 * rows), squeeze=False)
    max_kl_global = max(r["max_kl"] for r in results.values())

    for idx, key in enumerate(keys):
        ax = axes[idx // cols][idx % cols]
        r = results[key]
        positions = np.arange(r["n_response_tokens"])
        kl = np.array(r["kl_by_position"])
        color = ROLE_COLORS.get(r["role"], "black")

        ax.fill_between(positions, 0, kl, alpha=0.45, color=color)
        ax.plot(positions, kl, color=color, linewidth=1.2)
        ax.set_title(f"{key}\n{r['role']} | mean KL = {r['mean_kl']:.2f} | max KL = {r['max_kl']:.2f}",
                     fontsize=10)
        ax.set_xlabel("Response token position")
        ax.set_ylabel("KL(instruct ‖ base)")
        ax.set_ylim(0, min(max_kl_global * 1.05, 30))  # cap to keep plots comparable
        ax.grid(True, alpha=0.3)

    for idx in range(n, rows * cols):
        axes[idx // cols][idx % cols].axis("off")

    fig.suptitle("Phase D: Next-token KL divergence at each response position\n"
                 "Spikes = positions where Instruct and base would predict different tokens",
                 y=1.0)
    fig.tight_layout()
    out = output_dir / "kl_by_position_per_item.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out}")


def plot_kl_overlay(results: dict, output_dir: Path):
    """All items overlaid, colored by role, with role means."""
    fig, ax = plt.subplots(figsize=(13, 6))

    by_role = {}
    for key, r in results.items():
        role = r["role"]
        kl = np.array(r["kl_by_position"])
        positions = np.arange(len(kl))
        color = ROLE_COLORS.get(role, "black")
        ax.plot(positions, kl, color=color, linewidth=1.0, alpha=0.5,
                label=f"{key} ({role})")
        by_role.setdefault(role, []).append(kl)

    ax.set_xlabel("Response token position")
    ax.set_ylabel("KL(instruct ‖ base)")
    ax.set_title("Phase D: Per-position next-token divergence, all items overlaid")
    ax.legend(fontsize=8, loc="upper right", ncol=2)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    out = output_dir / "kl_overlay.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out}")


def plot_kl_distributions(results: dict, output_dir: Path):
    """Box/violin plot of KL distribution per item, sorted by role."""
    keys = sorted(results.keys(),
                  key=lambda k: (ROLE_ORDER.index(results[k]["role"]) if results[k]["role"] in ROLE_ORDER else 99,
                                 results[k]["mean_kl"]))

    fig, ax = plt.subplots(figsize=(12, 6))

    data = [results[k]["kl_by_position"] for k in keys]
    positions = np.arange(len(keys))
    colors = [ROLE_COLORS.get(results[k]["role"], "black") for k in keys]

    bp = ax.boxplot(data, positions=positions, widths=0.6, patch_artist=True,
                    showfliers=True, flierprops={"marker": ".", "markersize": 3, "alpha": 0.4})
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.5)
    for median in bp["medians"]:
        median.set_color("black")
        median.set_linewidth(1.5)

    # Overlay mean as red diamond
    means = [results[k]["mean_kl"] for k in keys]
    ax.scatter(positions, means, color="red", marker="D", s=40, zorder=5, label="mean")

    ax.set_xticks(positions)
    ax.set_xticklabels([f"{k}\n[{results[k]['role']}]" for k in keys],
                       rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("KL(instruct ‖ base) per response token")
    ax.set_title("Phase D: Distribution of per-token KL across each item\n"
                 "(Median = bar; mean = red diamond; long tails = more positional spikes)")
    ax.grid(True, alpha=0.3, axis="y")
    ax.legend()

    fig.tight_layout()
    out = output_dir / "kl_distributions.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out}")


def make_substitution_report(results: dict, output_dir: Path, top_n: int = 8):
    """Per-item: top-N highest-KL positions, with context + substitute analysis.

    This is the most interpretable output. For each "substitution position",
    we show:
      - The previous ~10 tokens (context)
      - The token Instruct actually emitted
      - Base's top-3 predictions (what base would have predicted instead)
      - The probability assigned by base to the actually-emitted token

    A position with high KL where base's top prediction is structurally
    different from what Instruct emitted is a "constraint substitution event."
    """
    lines = []

    keys = sorted(results.keys(),
                  key=lambda k: ROLE_ORDER.index(results[k]["role"]) if results[k]["role"] in ROLE_ORDER else 99)

    for key in keys:
        r = results[key]
        per_pos = r["per_position"]
        if not per_pos:
            continue

        sorted_positions = sorted(per_pos, key=lambda p: -p["kl_instr_base"])

        lines.append("=" * 78)
        lines.append(f"{key} (role: {r['role']})")
        lines.append(f"Question: {r['question']}")
        lines.append(f"Response: {r['response'][:300]}{'...' if len(r['response']) > 300 else ''}")
        lines.append(f"Stats: mean_KL={r['mean_kl']:.3f}, median_KL={r['median_kl']:.3f}, max_KL={r['max_kl']:.3f}")
        lines.append("")
        lines.append(f"Top-{top_n} highest-KL positions:")
        lines.append("")

        for rank, pp in enumerate(sorted_positions[:top_n], 1):
            pos = pp["response_pos"]
            ctx_start = max(0, pos - 8)
            ctx_tokens = "".join(per_pos[i]["emitted_token"] for i in range(ctx_start, pos))
            # Truncate context for display
            ctx_display = ctx_tokens[-50:] if len(ctx_tokens) > 50 else ctx_tokens

            instr_str = ", ".join(
                f"{repr(t)}={p:.2f}"
                for t, p in zip(pp["instr_top_tokens"][:3], pp["instr_top_probs"][:3])
            )
            base_str = ", ".join(
                f"{repr(t)}={p:.2f}"
                for t, p in zip(pp["base_top_tokens"][:3], pp["base_top_probs"][:3])
            )

            lines.append(f"  #{rank} pos={pos:>3} KL={pp['kl_instr_base']:.2f}")
            lines.append(f"     context: ...{repr(ctx_display)}")
            lines.append(f"     emitted: {repr(pp['emitted_token'])} (Instruct prob: {pp['instr_prob_of_emitted']:.2f}, Base prob: {pp['base_prob_of_emitted']:.4f})")
            lines.append(f"     Instruct top-3: {instr_str}")
            lines.append(f"     Base top-3:     {base_str}")
            lines.append("")

        lines.append("")

    report = "\n".join(lines)
    out = output_dir / "substitution_report.txt"
    out.write_text(report, encoding="utf-8")
    print(f"  saved {out}")
    return report


def print_summary_stats(results: dict):
    """Per-item summary table."""
    keys = sorted(results.keys(),
                  key=lambda k: ROLE_ORDER.index(results[k]["role"]) if results[k]["role"] in ROLE_ORDER else 99)

    print("\n=== Per-item KL summary ===")
    print(f"{'Item':<32} {'Role':<14} {'Mean KL':>9} {'Median':>8} {'Max KL':>8} {'Max pos':>8} {'p>2.0':>7}")

    for key in keys:
        r = results[key]
        kls = np.array(r["kl_by_position"])
        spike_count = int((kls > 2.0).sum())
        print(f"{key:<32} {r['role']:<14} {r['mean_kl']:>9.3f} {r['median_kl']:>8.3f} "
              f"{r['max_kl']:>8.2f} {r['max_kl_pos']:>8} {spike_count:>7}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--output-dir", type=Path, default=Path("analysis"))
    parser.add_argument("--top-n", type=int, default=8)
    args = parser.parse_args()

    results_path = args.results_dir / "kl_results.json"
    if not results_path.exists():
        print(f"ERROR: {results_path} not found.")
        print("Run `python compute_kl.py` first.")
        return

    results = json.loads(results_path.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print_summary_stats(results)

    print("\n=== Generating plots ===")
    plot_kl_by_position_per_item(results, args.output_dir)
    plot_kl_overlay(results, args.output_dir)
    plot_kl_distributions(results, args.output_dir)

    print("\n=== Generating substitution report ===")
    report = make_substitution_report(results, args.output_dir, top_n=args.top_n)

    print("\n=== Files written ===")
    print(f"  kl_by_position_per_item.png  : per-item KL traces")
    print(f"  kl_overlay.png               : all items overlaid")
    print(f"  kl_distributions.png         : per-item KL distribution boxplot")
    print(f"  substitution_report.txt      : top-K KL positions with token-level analysis")


if __name__ == "__main__":
    main()
