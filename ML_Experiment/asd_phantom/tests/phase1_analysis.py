"""
Phase 1 analysis - the orthogonality test.

Per FN-PHANTOM-002 Section 8.1.

Consumes the CSV produced by phase1_lm.py. For each of the 150
(topic, paraphrase) pairs, computes Pearson correlation r between
mean_rho and each Layer 1 ASD feature across the K seeds.

Predictions tested:
  P1-1: median |r| < 0.30 across the 150 pairs for each Layer 1 feature.
        80th percentile |r| < 0.50.
  P1-2: pairwise correlations within Layer 1 (drift vs timing_cv, etc.)
        have median |r| < 0.60 on the same data.
  P1-3: no systematic difference in |r| distributions across topic
        groups (control / mid / shaped). Kruskal-Wallis p > 0.01 within
        each feature.

Falsifications:
  F1-1: median |r| > 0.50 for any Layer 1 feature.
  F1-2: 80th percentile |r| > 0.70 for any feature.
  F1-3: KW test shows strong systematic trend across topic groups.

Outputs:
  - Per-pair correlation table: 150 x N_features
  - Distribution summary per feature: median, IQR, percentiles
  - Pairwise feature correlation matrix
  - Kruskal-Wallis test results per feature
  - Histograms (PNG)
  - Markdown report

Usage:
  python3 tests/phase1_analysis.py results/phase1_features_llama.csv
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


LAYER1_FEATURES = [
    "drift",
    "timing_cv",
    "mean_depth_excess",
    "isolated_frac",
    "d2_excess",
]


def compute_pair_correlations(df: pd.DataFrame, features=LAYER1_FEATURES) -> pd.DataFrame:
    """
    For each (topic, paraphrase_idx) pair, compute Pearson r between
    mean_rho and each feature across the K seeds in that pair.

    Returns: DataFrame with one row per (topic, paraphrase_idx) and
    columns for each feature giving r and |r|.
    """
    rows = []
    for (topic, p_idx), grp in df.groupby(["topic", "paraphrase_idx"]):
        K = len(grp)
        if K < 5:
            continue
        category = grp["category"].iloc[0]
        row = {"topic": topic, "paraphrase_idx": p_idx, "category": category, "K": K}
        for feat in features:
            if feat not in grp.columns:
                row[f"r_{feat}"] = np.nan
                continue
            x = grp["mean_rho"].values
            y = grp[feat].values
            if np.std(x) < 1e-10 or np.std(y) < 1e-10:
                row[f"r_{feat}"] = np.nan
                row[f"abs_r_{feat}"] = np.nan
                continue
            r, _ = stats.pearsonr(x, y)
            row[f"r_{feat}"] = float(r)
            row[f"abs_r_{feat}"] = float(abs(r))
        rows.append(row)
    return pd.DataFrame(rows)


def evaluate_p1_1(corr_df: pd.DataFrame, features=LAYER1_FEATURES, verbose=True):
    """P1-1: median |r| < 0.30, 80th percentile < 0.50 per feature.
    Falsification F1-1: median |r| > 0.50 for any feature.
    Falsification F1-2: 80th percentile |r| > 0.70 for any feature.
    """
    p1_1_results = {}
    p1_1_pass = True
    f1_1 = False
    f1_2 = False
    for feat in features:
        col = f"abs_r_{feat}"
        if col not in corr_df.columns:
            continue
        vals = corr_df[col].dropna().values
        if len(vals) == 0:
            continue
        med = float(np.median(vals))
        iqr = float(np.percentile(vals, 75) - np.percentile(vals, 25))
        pct80 = float(np.percentile(vals, 80))
        pct95 = float(np.percentile(vals, 95))
        p1_1_results[feat] = {
            "median": med, "iqr": iqr, "pct80": pct80, "pct95": pct95,
            "n": len(vals),
        }
        # Pass criteria
        if med >= 0.30 or pct80 >= 0.50:
            p1_1_pass = False
        if med > 0.50:
            f1_1 = True
        if pct80 > 0.70:
            f1_2 = True

    if verbose:
        print()
        print(f"{'feature':22s}{'N':>5}{'median':>10}{'IQR':>10}{'80th':>10}{'95th':>10}")
        print("-" * 67)
        for feat in features:
            if feat not in p1_1_results:
                continue
            r = p1_1_results[feat]
            print(f"{feat:22s}{r['n']:>5d}{r['median']:>10.3f}{r['iqr']:>10.3f}{r['pct80']:>10.3f}{r['pct95']:>10.3f}")

    return {
        "p1_1_results": p1_1_results,
        "p1_1_pass": p1_1_pass,
        "f1_1": f1_1,  # falsification triggered
        "f1_2": f1_2,
    }


def evaluate_p1_2(df: pd.DataFrame, features=LAYER1_FEATURES, verbose=True):
    """
    P1-2: pairwise feature correlations on the same data have median |r| < 0.60.

    Computed across all generations pooled (not per-pair) -- since these
    are between-feature correlations, pooling is appropriate.
    """
    avail = [f for f in features if f in df.columns]
    if len(avail) < 2:
        return {"p1_2_pass": True, "matrix": None}
    sub = df[avail].dropna()
    M = sub.corr().abs()
    M_vals = M.values.copy()
    np.fill_diagonal(M_vals, np.nan)
    median_offdiag = float(np.nanmedian(M_vals))
    p1_2_pass = median_offdiag < 0.60
    if verbose:
        print()
        print("Pairwise |r| matrix (Layer 1 features, pooled):")
        print(M.round(3))
        print(f"  Median off-diagonal |r| = {median_offdiag:.3f}  (threshold 0.60)")
    return {"p1_2_pass": p1_2_pass, "matrix": M, "median_offdiag": median_offdiag}


def evaluate_p1_3(corr_df: pd.DataFrame, features=LAYER1_FEATURES, verbose=True):
    """
    P1-3: no systematic difference in |r| distributions across topic
    groups (control / mid / shaped). Kruskal-Wallis p > 0.01.

    Falsification F1-3: strong systematic trend across topic groups.
    """
    out = {}
    f1_3 = False
    for feat in features:
        col = f"abs_r_{feat}"
        if col not in corr_df.columns:
            continue
        groups = []
        labels = []
        for cat in ["control", "mid", "shaped"]:
            vals = corr_df[corr_df.category == cat][col].dropna().values
            if len(vals) > 0:
                groups.append(vals)
                labels.append(cat)
        if len(groups) < 2:
            out[feat] = {"H": np.nan, "p": np.nan,
                         "medians": {l: np.nan for l in labels}}
            continue
        H, p = stats.kruskal(*groups)
        medians = {l: float(np.median(g)) for l, g in zip(labels, groups)}
        out[feat] = {"H": float(H), "p": float(p), "medians": medians,
                     "n_per_group": {l: len(g) for l, g in zip(labels, groups)}}
        if p < 0.01:
            f1_3 = True

    if verbose:
        print()
        print("Kruskal-Wallis test for category effect on |r|:")
        print(f"{'feature':22s}{'H':>10}{'p':>12}{'control':>14}{'mid':>14}{'shaped':>14}")
        print("-" * 86)
        for feat in features:
            if feat not in out:
                continue
            r = out[feat]
            mc = r["medians"].get("control", np.nan)
            mm = r["medians"].get("mid", np.nan)
            ms = r["medians"].get("shaped", np.nan)
            print(f"{feat:22s}{r['H']:>10.3f}{r['p']:>12.4g}"
                  f"{mc:>14.3f}{mm:>14.3f}{ms:>14.3f}")
        print(f"  P1-3 falsification trigger: any p < 0.01 -> {'TRIGGERED' if f1_3 else 'not triggered'}")

    return {"p1_3_pass": not f1_3, "f1_3": f1_3, "by_feature": out}


def make_plots(corr_df: pd.DataFrame, out_dir: str,
               features=LAYER1_FEATURES):
    """Histograms of |r| per feature, with vertical thresholds."""
    n = len([f for f in features if f"abs_r_{f}" in corr_df.columns])
    fig, axes = plt.subplots(1, n, figsize=(3.5 * n, 3.5), squeeze=False)
    axes = axes.flatten()
    for i, feat in enumerate(features):
        col = f"abs_r_{feat}"
        if col not in corr_df.columns:
            continue
        ax = axes[i]
        for cat, color in [("control", "#4a90e2"),
                            ("mid", "#888888"),
                            ("shaped", "#d6543a")]:
            vals = corr_df[corr_df.category == cat][col].dropna().values
            if len(vals) > 0:
                ax.hist(vals, bins=15, alpha=0.5, label=f"{cat} (n={len(vals)})",
                        color=color, density=True)
        ax.axvline(0.30, color="green", linestyle="--", linewidth=1, label="0.30 (median target)")
        ax.axvline(0.50, color="orange", linestyle="--", linewidth=1, label="0.50 (80th-pct target)")
        ax.set_xlabel(f"|r| for {feat} vs mean_rho")
        ax.set_ylabel("density")
        ax.set_title(feat, fontsize=10)
        if i == 0:
            ax.legend(fontsize=7, loc="upper right")
    fig.suptitle("Phase 1: |r| distributions per Layer 1 feature, by topic category",
                  y=1.02, fontsize=11)
    fig.tight_layout()
    out_path = os.path.join(out_dir, "phase1_correlation_histograms.png")
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out_path


def write_report(corr_df: pd.DataFrame, p1_1: dict, p1_2: dict, p1_3: dict,
                  out_path: str, n_input_rows: int):
    """Write a markdown report summarizing the orthogonality test result."""
    lines = []
    lines.append("# Phase 1 - Orthogonality Test Report\n")
    lines.append(f"_Input feature rows: {n_input_rows}, "
                 f"(topic, paraphrase) pairs analyzed: {len(corr_df)}_\n")
    lines.append("\n## P1-1: distribution of |r| per Layer 1 feature\n\n")
    lines.append("| feature | N | median | IQR | 80th pct | 95th pct |\n")
    lines.append("|---|---:|---:|---:|---:|---:|\n")
    for feat, r in p1_1["p1_1_results"].items():
        lines.append(f"| {feat} | {r['n']} | {r['median']:.3f} | {r['iqr']:.3f} "
                     f"| {r['pct80']:.3f} | {r['pct95']:.3f} |\n")
    lines.append(f"\n**P1-1** (median < 0.30 AND 80th pct < 0.50 per feature): "
                 f"**{'PASS' if p1_1['p1_1_pass'] else 'FAIL'}**\n")
    lines.append(f"\n**F1-1** (median > 0.50 for any feature): "
                 f"{'TRIGGERED -- orthogonality refuted' if p1_1['f1_1'] else 'not triggered'}\n")
    lines.append(f"**F1-2** (80th pct > 0.70 for any feature): "
                 f"{'TRIGGERED' if p1_1['f1_2'] else 'not triggered'}\n")

    lines.append("\n## P1-2: pairwise feature correlations\n\n")
    if p1_2.get("matrix") is not None:
        m = p1_2["matrix"].round(3)
        cols = m.columns.tolist()
        lines.append("| | " + " | ".join(cols) + " |\n")
        lines.append("|---|" + "---:|" * len(cols) + "\n")
        for r_name in m.index:
            cells = []
            for c in cols:
                v = m.loc[r_name, c]
                cells.append("--" if pd.isna(v) else f"{v:.3f}")
            lines.append(f"| {r_name} | " + " | ".join(cells) + " |\n")
        lines.append(f"\nMedian off-diagonal |r| = {p1_2['median_offdiag']:.3f}\n")
    lines.append(f"\n**P1-2** (median pairwise |r| < 0.60): "
                 f"**{'PASS' if p1_2['p1_2_pass'] else 'FAIL'}**\n")

    lines.append("\n## P1-3: topic-group effect (Kruskal-Wallis)\n\n")
    lines.append("| feature | H | p | median(control) | median(mid) | median(shaped) |\n")
    lines.append("|---|---:|---:|---:|---:|---:|\n")
    for feat, r in p1_3["by_feature"].items():
        mc = r["medians"].get("control", float("nan"))
        mm = r["medians"].get("mid", float("nan"))
        ms = r["medians"].get("shaped", float("nan"))
        lines.append(f"| {feat} | {r['H']:.3f} | {r['p']:.4g} "
                     f"| {mc:.3f} | {mm:.3f} | {ms:.3f} |\n")
    lines.append(f"\n**P1-3** (no KW p < 0.01): "
                 f"**{'PASS' if p1_3['p1_3_pass'] else 'FAIL'}**\n")
    lines.append(f"**F1-3** (any KW p < 0.01): "
                 f"{'TRIGGERED' if p1_3['f1_3'] else 'not triggered'}\n")

    overall = p1_1["p1_1_pass"] and p1_2["p1_2_pass"] and p1_3["p1_3_pass"]
    falsified = p1_1["f1_1"] or p1_1["f1_2"]
    lines.append("\n## Overall\n\n")
    lines.append(f"- **(O-LM) holds** (P1-1+P1-2+P1-3 all pass): "
                 f"**{'YES' if overall else 'NO'}**\n")
    lines.append(f"- **(O-LM) falsified** (F1-1 or F1-2): "
                 f"**{'YES' if falsified else 'NO'}**\n")
    if overall:
        lines.append("\nNext step: Phase 2 - augmented detection on case-study topics (FN-PHANTOM-002 Section 8.2).\n")
    elif falsified:
        lines.append("\nThe orthogonality claim is empirically refuted on LM trajectories. The structural argument (Section 4.2 of FN-PHANTOM-002) remains intact, but ASD features as currently defined are empirically redundant with mean rho on this input class. Subsequent phases lose their primary motivation; see Section 11.2 of FN-PHANTOM-002 for follow-up options.\n")
    else:
        lines.append("\nMixed result: not refuted, but not all sub-criteria met. See per-feature breakdown above. Examine which features fail and consider whether to drop them and re-test, or to expand the feature set.\n")

    with open(out_path, "w") as f:
        f.writelines(lines)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Phase 1 orthogonality test analysis")
    parser.add_argument("input_csv", help="CSV from phase1_lm.py")
    parser.add_argument("--features", nargs="*", default=LAYER1_FEATURES,
                         help="features to test against mean_rho")
    parser.add_argument("--out_dir", default=None,
                         help="output directory (default: results/)")
    args = parser.parse_args()

    df = pd.read_csv(args.input_csv)
    n_in = len(df)
    print(f"Loaded: {args.input_csv} ({n_in} rows)")

    out_dir = args.out_dir
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(args.input_csv))
    os.makedirs(out_dir, exist_ok=True)

    print(f"Computing per-pair correlations between mean_rho and:")
    for f in args.features:
        print(f"  - {f}")
    corr_df = compute_pair_correlations(df, features=args.features)
    base = os.path.splitext(os.path.basename(args.input_csv))[0]
    corr_path = os.path.join(out_dir, f"{base}_correlations.csv")
    corr_df.to_csv(corr_path, index=False)
    print(f"  Saved per-pair correlations: {corr_path}")
    print()

    print("=" * 76)
    print("P1-1 - distribution of |r| per Layer 1 feature")
    print("=" * 76)
    p1_1 = evaluate_p1_1(corr_df, features=args.features)

    print()
    print("=" * 76)
    print("P1-2 - pairwise feature correlations")
    print("=" * 76)
    p1_2 = evaluate_p1_2(df, features=args.features)

    print()
    print("=" * 76)
    print("P1-3 - topic-group effect")
    print("=" * 76)
    p1_3 = evaluate_p1_3(corr_df, features=args.features)

    plot_path = make_plots(corr_df, out_dir, features=args.features)
    print(f"\n  Saved histograms: {plot_path}")

    report_path = os.path.join(out_dir, f"{base}_report.md")
    write_report(corr_df, p1_1, p1_2, p1_3, report_path, n_in)
    print(f"  Saved report: {report_path}")

    print()
    print("=" * 76)
    print("OVERALL")
    print("=" * 76)
    overall_pass = p1_1["p1_1_pass"] and p1_2["p1_2_pass"] and p1_3["p1_3_pass"]
    falsified = p1_1["f1_1"] or p1_1["f1_2"]
    print(f"  P1-1 (median |r| < 0.30, 80th < 0.50): {'PASS' if p1_1['p1_1_pass'] else 'FAIL'}")
    print(f"  P1-2 (pairwise median < 0.60): {'PASS' if p1_2['p1_2_pass'] else 'FAIL'}")
    print(f"  P1-3 (no KW p<0.01 across categories): {'PASS' if p1_3['p1_3_pass'] else 'FAIL'}")
    print(f"  (O-LM) holds: {'YES' if overall_pass else 'NO'}")
    print(f"  (O-LM) falsified by F1-1 or F1-2: {'YES' if falsified else 'NO'}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
