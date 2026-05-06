"""
Phase 2 analysis - the augmented detection test.

Per FN-PHANTOM-002 Section 8.2.

Consumes the Phase 2 feature CSV. Per topic, trains three logistic regression
classifiers to distinguish base-generated from inst-generated continuations:
  Set A (rho-only): mean_rho, std_rho
  Set B (ASD-only): drift, timing_cv, mean_depth_excess, isolated_frac,
                    Q_tail_1, Q_tail_2, Q_tail_3, Q_tail_4, r_plus
  Set C (combined): A + B

5-fold leave-one-paraphrase-out cross-validation. AUC per fold + aggregate
with bootstrap CIs. Paired bootstrap test for AUC differences between sets.

Predictions tested (from FN-PHANTOM-002 §8.2.4):
  P2-1: founding fathers AUC(C) - AUC(A) >= 0.05
  P2-2: Wehrmacht AUC(C) - AUC(A) >= 0.05
  P2-3: crime demographics AUC(C) - AUC(A) >= 0.10
  P2-4: ASD-only AUC >= 0.65 on each topic
  P2-5: at least 3 ASD features have nonzero coefs in Set C per topic

Falsifications:
  F2-1: AUC(C) ~ AUC(A) within 0.02 on all 3 topics (no detection gain)
  F2-2: ASD-only AUC < 0.55 on all 3 topics (ASD carries no signal)
  F2-3: AUC(C) < AUC(A) on any topic (ASD degrades performance)

Outputs:
  - per-topic AUC table with bootstrap CIs and DeLong p-values
  - per-topic classifier coefficient diagrams
  - per-topic ROC and signal-rate-at-FPR=0.05 plots
  - markdown report with verdict
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---- Feature sets ----
SET_A = ["mean_rho", "std_rho"]
SET_B = ["drift", "timing_cv", "mean_depth_excess", "isolated_frac",
         "Q_tail_1", "Q_tail_2", "Q_tail_3", "Q_tail_4", "r_plus"]
SET_C = SET_A + SET_B

ASD_FEATURES_FOR_P25 = SET_B  # used in the P2-5 nonzero-coefficient check


def auc_with_ci(y_true, y_score, n_boot=1000, seed=0):
    """Bootstrap AUC and 95% CI."""
    if len(np.unique(y_true)) < 2 or len(y_true) < 5:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    auc = roc_auc_score(y_true, y_score)
    n = len(y_true)
    aucs = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if len(np.unique(y_true[idx])) < 2:
            continue
        try:
            aucs.append(roc_auc_score(y_true[idx], y_score[idx]))
        except ValueError:
            continue
    aucs = np.array(aucs)
    if len(aucs) < 10:
        return float(auc), float("nan"), float("nan")
    return float(auc), float(np.percentile(aucs, 2.5)), float(np.percentile(aucs, 97.5))


def signal_rate_at_fpr(y_true, y_score, target_fpr=0.05):
    """Hit rate (TPR) at the threshold giving FPR <= target_fpr."""
    if len(np.unique(y_true)) < 2:
        return float("nan")
    fpr, tpr, _ = roc_curve(y_true, y_score)
    # Find largest TPR at FPR <= target
    valid = fpr <= target_fpr
    if not np.any(valid):
        return 0.0
    return float(np.max(tpr[valid]))


def paired_bootstrap_auc_diff(y_true, score_a, score_c, n_boot=1000, seed=0):
    """
    Paired bootstrap on AUC(C) - AUC(A). Returns (delta_observed, ci_low, ci_high, p_value).
    p_value = fraction of bootstrap deltas <= 0 (right-tailed test for delta > 0).
    """
    if len(np.unique(y_true)) < 2:
        return float("nan"), float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    auc_a_obs = roc_auc_score(y_true, score_a)
    auc_c_obs = roc_auc_score(y_true, score_c)
    delta_obs = auc_c_obs - auc_a_obs
    n = len(y_true)
    deltas = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if len(np.unique(y_true[idx])) < 2:
            continue
        try:
            d = roc_auc_score(y_true[idx], score_c[idx]) - roc_auc_score(y_true[idx], score_a[idx])
            deltas.append(d)
        except ValueError:
            continue
    if len(deltas) < 10:
        return float(delta_obs), float("nan"), float("nan"), float("nan")
    deltas = np.array(deltas)
    # Right-tailed p-value: P(delta_bootstrap <= 0 | observed delta > 0)
    # Two-sided 95% CI:
    ci_low = float(np.percentile(deltas, 2.5))
    ci_high = float(np.percentile(deltas, 97.5))
    p_one_sided = float((deltas <= 0).mean())  # H0: delta = 0 vs H1: delta > 0
    return float(delta_obs), ci_low, ci_high, p_one_sided


def evaluate_topic(df_topic, feature_sets, n_boot=1000, seed=0):
    """5-fold leave-one-paraphrase-out CV per feature set."""
    paraphrases = sorted(df_topic.paraphrase_idx.unique())
    fold_results = {}  # name -> list of dict per fold
    pooled_predictions = {name: {"y": [], "score": []} for name in feature_sets}

    # also fit a final classifier on the full data to get coefficients for P2-5
    final_classifiers = {}

    for name, features in feature_sets.items():
        fold_results[name] = []
        for held_out in paraphrases:
            train_df = df_topic[df_topic.paraphrase_idx != held_out]
            test_df = df_topic[df_topic.paraphrase_idx == held_out]
            if len(train_df) == 0 or len(test_df) == 0:
                continue

            y_train = (train_df.generating_model == "inst").astype(int).values
            y_test = (test_df.generating_model == "inst").astype(int).values
            X_train = train_df[features].values
            X_test = test_df[features].values

            # Drop any NaN / inf rows
            train_valid = np.all(np.isfinite(X_train), axis=1)
            test_valid = np.all(np.isfinite(X_test), axis=1)
            X_train = X_train[train_valid]
            y_train = y_train[train_valid]
            X_test = X_test[test_valid]
            y_test = y_test[test_valid]
            if len(X_train) < 5 or len(X_test) < 5:
                continue

            scaler = StandardScaler()
            X_train_s = scaler.fit_transform(X_train)
            X_test_s = scaler.transform(X_test)

            clf = LogisticRegression(max_iter=2000, C=1.0)
            clf.fit(X_train_s, y_train)
            score = clf.predict_proba(X_test_s)[:, 1]

            auc_v, ci_lo, ci_hi = auc_with_ci(y_test, score, n_boot=n_boot, seed=seed)
            sr05 = signal_rate_at_fpr(y_test, score, target_fpr=0.05)
            fold_results[name].append({
                "held_out": held_out,
                "n_train": len(X_train), "n_test": len(X_test),
                "auc": auc_v, "auc_ci_low": ci_lo, "auc_ci_high": ci_hi,
                "signal_rate_fpr05": sr05,
            })
            pooled_predictions[name]["y"].extend(y_test.tolist())
            pooled_predictions[name]["score"].extend(score.tolist())

        # Final classifier on full data
        y_full = (df_topic.generating_model == "inst").astype(int).values
        X_full = df_topic[features].values
        valid = np.all(np.isfinite(X_full), axis=1)
        scaler = StandardScaler()
        X_full_s = scaler.fit_transform(X_full[valid])
        clf_final = LogisticRegression(max_iter=2000, C=1.0)
        clf_final.fit(X_full_s, y_full[valid])
        final_classifiers[name] = (clf_final, scaler, features)

    # Aggregate AUC = mean over folds with bootstrap CI on the fold values
    aggregate = {}
    for name in feature_sets:
        aucs = np.array([f["auc"] for f in fold_results[name] if not np.isnan(f["auc"])])
        if len(aucs) == 0:
            aggregate[name] = {"auc_mean": float("nan"), "auc_se": float("nan")}
            continue
        aggregate[name] = {
            "auc_mean": float(aucs.mean()),
            "auc_se": float(aucs.std(ddof=1) / np.sqrt(len(aucs))) if len(aucs) > 1 else 0.0,
            "auc_min": float(aucs.min()),
            "auc_max": float(aucs.max()),
            "n_folds": len(aucs),
        }

    # Pooled-prediction-based DeLong-style paired bootstrap of AUC differences
    pair_tests = {}
    for (a, c) in [("A", "C"), ("A", "B"), ("B", "C")]:
        if a not in feature_sets or c not in feature_sets:
            continue
        y_pool = np.array(pooled_predictions[a]["y"])
        s_a = np.array(pooled_predictions[a]["score"])
        s_c = np.array(pooled_predictions[c]["score"])
        if len(y_pool) > 0 and len(np.unique(y_pool)) >= 2:
            delta, ci_lo, ci_hi, p = paired_bootstrap_auc_diff(
                y_pool, s_a, s_c, n_boot=n_boot, seed=seed)
            pair_tests[f"{c}_minus_{a}"] = {
                "delta": delta, "ci_low": ci_lo, "ci_high": ci_hi, "p_one_sided": p,
            }

    return {
        "fold_results": fold_results,
        "aggregate": aggregate,
        "pair_tests": pair_tests,
        "final_classifiers": final_classifiers,
        "pooled_predictions": pooled_predictions,
    }


def coefficient_summary(final_classifiers, asd_features=ASD_FEATURES_FOR_P25,
                         abs_threshold=0.1):
    """For Set C classifier, count nonzero ASD coefficients (|coef| > threshold)."""
    if "C" not in final_classifiers:
        return {}
    clf, scaler, features = final_classifiers["C"]
    coefs = dict(zip(features, clf.coef_[0]))
    asd_nonzero = [(f, coefs[f]) for f in asd_features if f in coefs and abs(coefs[f]) > abs_threshold]
    rho_nonzero = [(f, coefs[f]) for f in features if f not in asd_features and abs(coefs[f]) > abs_threshold]
    return {
        "all_coefs": coefs,
        "asd_nonzero": asd_nonzero,
        "rho_nonzero": rho_nonzero,
        "n_asd_nonzero": len(asd_nonzero),
    }


# -------------------------------------------------------------------------
# Bridge B directional alignment check (P2-6)
# -------------------------------------------------------------------------
#
# Phase 2's AUC-magnitude tests (P2-1 through P2-5) measure whether ASD adds
# detection capability. They do NOT test whether the way ASD adds capability
# matches Bridge B's structural prediction — leakage = beta(1-beta) * mu^2(1-s^2).
# The reviewer of EN-PHANTOM-001 flagged that AUC-only conflates two outcomes:
#   (a) ASD detects something correlated with origin but not what Bridge B describes
#   (b) ASD detects exactly what Bridge B's mu^2(1-s^2) structure predicts
#
# (b) is the structural-unification claim. (a) is the weaker result.
#
# Bridge B specialized to ASD coordinates predicts cross-topic ordering:
# topics with stronger constraint engagement (higher mu, lower s -> higher
# leakage strength) should produce classifier with higher total ASD-feature
# weight magnitude. Per-topic feature emphasis should also pattern-match by
# regime: greedy-decoding-artifact topics emphasize Layer 2 depth/recurrence
# features (the multi-phase trajectory signature); induced-hole topics
# emphasize Layer 1 cancellation features (early-commitment signature).
#
# The check is cheap given cached trajectories. If it passes, structural
# unification is operationally supported. If it fails alongside an AUC pass,
# we have outcome (a) — informative but a weaker claim than the framework
# advertises.

# Predicted leakage strength ordering by case-study type:
# CS-PHANTOM-002 (greedy-decoding artifact) > CS-PHANTOM-001 (induced hole)
BRIDGE_B_PREDICTED_LEAKAGE_RANK = {
    "shaped_crime_demographics": 3,         # highest predicted leakage
    "shaped_wehrmacht_conduct": 1,          # moderate (induced hole)
    "shaped_founding_fathers_slavery": 1,   # moderate (induced hole, tied)
}

# Per-topic predicted feature-class emphasis (which classes should dominate)
LAYER_1_CANCELLATION_FEATURES = {"drift", "isolated_frac"}
LAYER_2_DEPTH_FEATURES = {"Q_tail_1", "Q_tail_2", "Q_tail_3", "Q_tail_4", "r_plus"}

BRIDGE_B_PREDICTED_EMPHASIS = {
    # crime: multi-phase trajectory -> Layer 2 should account for >= 30% of ASD weight
    "shaped_crime_demographics": {"layer_2_min_share": 0.30},
    # induced-hole topics: early-commitment signature -> Layer 1 cancellation features
    # should account for >= 50% of ASD weight
    "shaped_wehrmacht_conduct": {"layer_1_cancellation_min_share": 0.50},
    "shaped_founding_fathers_slavery": {"layer_1_cancellation_min_share": 0.50},
}


def bridge_b_directional_check(per_topic_results,
                                rank_threshold_spearman=0.5):
    """
    Test whether classifier weight patterns align with Bridge B's structural prediction.

    Two sub-checks:
      (i)  Cross-topic ordering: total ASD weight magnitude should rank-correlate
           (Spearman rho >= rank_threshold_spearman) with predicted leakage rank.
      (ii) Per-topic feature emphasis: each topic's ASD weight distribution should
           place predicted-dominant feature class above its predicted-share threshold.

    Returns dict with per-topic and aggregate verdicts.
    """
    from scipy.stats import spearmanr

    # Compute per-topic total ASD weight magnitude (L2 norm) and feature-class shares
    per_topic_metrics = {}
    for topic, R in per_topic_results.items():
        cs = R["coef_summary"]
        all_coefs = cs.get("all_coefs", {})
        asd_coefs = {f: c for f, c in all_coefs.items() if f in ASD_FEATURES_FOR_P25}
        if not asd_coefs:
            per_topic_metrics[topic] = {
                "total_asd_weight": 0.0,
                "layer_1_cancellation_share": 0.0,
                "layer_2_share": 0.0,
            }
            continue

        total_weight = float(np.sqrt(sum(c**2 for c in asd_coefs.values())))
        l1_cancel_weight = float(np.sqrt(sum(c**2 for f, c in asd_coefs.items()
                                              if f in LAYER_1_CANCELLATION_FEATURES)))
        l2_weight = float(np.sqrt(sum(c**2 for f, c in asd_coefs.items()
                                       if f in LAYER_2_DEPTH_FEATURES)))

        per_topic_metrics[topic] = {
            "total_asd_weight": total_weight,
            "layer_1_cancellation_share": (l1_cancel_weight / total_weight) if total_weight > 0 else 0.0,
            "layer_2_share": (l2_weight / total_weight) if total_weight > 0 else 0.0,
        }

    # Sub-check (i): cross-topic ordering
    topics_in_data = sorted(per_topic_metrics.keys())
    predicted_ranks = [BRIDGE_B_PREDICTED_LEAKAGE_RANK.get(t, 0) for t in topics_in_data]
    empirical_weights = [per_topic_metrics[t]["total_asd_weight"] for t in topics_in_data]
    if len(set(predicted_ranks)) > 1 and len(set(empirical_weights)) > 1:
        rho, p_spearman = spearmanr(predicted_ranks, empirical_weights)
        ordering_pass = rho >= rank_threshold_spearman
    else:
        rho, p_spearman = float("nan"), float("nan")
        ordering_pass = False

    # Sub-check (ii): per-topic feature emphasis
    emphasis_results = {}
    for topic in topics_in_data:
        pred = BRIDGE_B_PREDICTED_EMPHASIS.get(topic, {})
        m = per_topic_metrics[topic]
        topic_pass = True
        details = []
        if "layer_2_min_share" in pred:
            ok = m["layer_2_share"] >= pred["layer_2_min_share"]
            details.append(f"Layer 2 share = {m['layer_2_share']:.2f} (target >= {pred['layer_2_min_share']}): "
                            f"{'PASS' if ok else 'FAIL'}")
            topic_pass = topic_pass and ok
        if "layer_1_cancellation_min_share" in pred:
            ok = m["layer_1_cancellation_share"] >= pred["layer_1_cancellation_min_share"]
            details.append(f"Layer 1 cancellation share = {m['layer_1_cancellation_share']:.2f} "
                            f"(target >= {pred['layer_1_cancellation_min_share']}): "
                            f"{'PASS' if ok else 'FAIL'}")
            topic_pass = topic_pass and ok
        emphasis_results[topic] = {"pass": topic_pass, "details": details, **m}

    n_emphasis_pass = sum(1 for v in emphasis_results.values() if v["pass"])
    emphasis_full_pass = n_emphasis_pass == len(emphasis_results)
    emphasis_partial_pass = n_emphasis_pass >= 2 and not emphasis_full_pass

    p2_6_pass = ordering_pass and emphasis_full_pass

    return {
        "p2_6_pass": p2_6_pass,
        "ordering": {
            "pass": ordering_pass,
            "spearman_rho": rho,
            "spearman_p": p_spearman,
            "topics": topics_in_data,
            "predicted_ranks": predicted_ranks,
            "empirical_weights": empirical_weights,
        },
        "emphasis": {
            "full_pass": emphasis_full_pass,
            "partial_pass": emphasis_partial_pass,
            "n_pass": n_emphasis_pass,
            "n_total": len(emphasis_results),
            "by_topic": emphasis_results,
        },
        "per_topic_metrics": per_topic_metrics,
    }


def evaluate_predictions(per_topic_results, topic_thresholds):
    """P2-1 to P2-5 verdicts."""
    p2_1_results = {}  # AUC(C) - AUC(A) >= threshold per topic
    p2_4_results = {}  # ASD-only AUC >= 0.65
    p2_5_results = {}  # >= 3 ASD features with nonzero coefs

    for topic, R in per_topic_results.items():
        threshold = topic_thresholds.get(topic, 0.05)
        agg = R["aggregate"]
        delta = agg.get("C", {}).get("auc_mean", float("nan")) - agg.get("A", {}).get("auc_mean", float("nan"))
        passed = (not np.isnan(delta)) and delta >= threshold
        p2_1_results[topic] = {
            "auc_a": agg.get("A", {}).get("auc_mean", float("nan")),
            "auc_b": agg.get("B", {}).get("auc_mean", float("nan")),
            "auc_c": agg.get("C", {}).get("auc_mean", float("nan")),
            "delta": delta, "threshold": threshold, "pass": passed,
        }

        # P2-4: ASD-only AUC >= 0.65
        auc_b = agg.get("B", {}).get("auc_mean", float("nan"))
        p2_4_results[topic] = {"auc_b": auc_b, "pass": (not np.isnan(auc_b)) and auc_b >= 0.65}

        # P2-5: >= 3 ASD features nonzero
        cs = R["coef_summary"]
        n_asd = cs.get("n_asd_nonzero", 0)
        p2_5_results[topic] = {"n_asd_nonzero": n_asd, "pass": n_asd >= 3}

    # Aggregate verdicts
    p2_1_pass_count = sum(1 for v in p2_1_results.values() if v["pass"])
    p2_4_pass_count = sum(1 for v in p2_4_results.values() if v["pass"])
    p2_5_pass_count = sum(1 for v in p2_5_results.values() if v["pass"])

    n_topics = len(per_topic_results)
    p2_1_full_pass = p2_1_pass_count == n_topics
    p2_1_partial_pass = p2_1_pass_count >= 2 and not p2_1_full_pass
    p2_4_pass = p2_4_pass_count == n_topics
    p2_5_pass = p2_5_pass_count == n_topics

    # Falsification triggers
    f2_1 = all(abs(v["delta"]) < 0.02 for v in p2_1_results.values()
                if not np.isnan(v["delta"]))
    f2_2 = all(v["auc_b"] < 0.55 for v in p2_4_results.values()
                if not np.isnan(v["auc_b"]))
    f2_3 = any(v["delta"] < 0 for v in p2_1_results.values()
                if not np.isnan(v["delta"]))

    return {
        "p2_1": p2_1_results, "p2_4": p2_4_results, "p2_5": p2_5_results,
        "p2_1_full_pass": p2_1_full_pass,
        "p2_1_partial_pass": p2_1_partial_pass,
        "p2_4_pass": p2_4_pass, "p2_5_pass": p2_5_pass,
        "f2_1": f2_1, "f2_2": f2_2, "f2_3": f2_3,
        "overall_pass": p2_1_full_pass and p2_4_pass and p2_5_pass,
    }


def make_plots(per_topic_results, out_dir):
    """ROC curves and coefficient plots per topic."""
    n_topics = len(per_topic_results)
    fig, axes = plt.subplots(2, n_topics, figsize=(5 * n_topics, 9), squeeze=False)

    for col, (topic, R) in enumerate(per_topic_results.items()):
        ax_roc = axes[0, col]
        for name, color in [("A", "#2266cc"), ("B", "#cc4422"), ("C", "#22aa44")]:
            if name not in R["pooled_predictions"]:
                continue
            y = np.array(R["pooled_predictions"][name]["y"])
            s = np.array(R["pooled_predictions"][name]["score"])
            if len(y) == 0 or len(np.unique(y)) < 2:
                continue
            fpr, tpr, _ = roc_curve(y, s)
            auc = R["aggregate"][name]["auc_mean"]
            ax_roc.plot(fpr, tpr, color=color, linewidth=2,
                         label=f"Set {name}: AUC={auc:.3f}")
        ax_roc.plot([0, 1], [0, 1], "k--", alpha=0.3)
        ax_roc.axvline(0.05, color="gray", linestyle=":", alpha=0.5, label="FPR=0.05")
        ax_roc.set_xlabel("FPR")
        ax_roc.set_ylabel("TPR")
        topic_short = topic.replace("shaped_", "").replace("_", " ")
        ax_roc.set_title(f"{topic_short}", fontsize=10)
        ax_roc.legend(fontsize=8, loc="lower right")
        ax_roc.set_xlim(0, 1)
        ax_roc.set_ylim(0, 1)

        # Coefficients for Set C
        ax_coef = axes[1, col]
        cs = R["coef_summary"]
        coefs = cs["all_coefs"]
        names = list(coefs.keys())
        vals = [coefs[n] for n in names]
        colors_bar = ["#2266cc" if n in SET_A else "#cc4422" for n in names]
        ax_coef.barh(names, vals, color=colors_bar)
        ax_coef.axvline(0, color="black", linewidth=0.5)
        ax_coef.set_xlabel("Standardized coefficient")
        ax_coef.set_title("Set C classifier weights\n(blue=ρ-features, red=ASD-features)", fontsize=9)
        ax_coef.tick_params(axis="y", labelsize=7)

    fig.suptitle("Phase 2: ROC curves (top) and Set C classifier coefficients (bottom)", fontsize=12, y=1.00)
    fig.tight_layout()
    out_path = os.path.join(out_dir, "phase2_roc_and_coefs.png")
    fig.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return out_path


def write_report(per_topic_results, verdicts, bridge_b, out_path, n_input_rows):
    lines = []
    lines.append(f"# Phase 2 - Augmented Detection Test Report\n")
    lines.append(f"_Input feature rows: {n_input_rows}_\n\n")

    lines.append("## P2-1: AUC gain per topic (target: AUC(C) - AUC(A) >= topic-specific threshold)\n\n")
    lines.append("| topic | AUC(A: ρ-only) | AUC(B: ASD-only) | AUC(C: combined) | delta C-A | threshold | verdict |\n")
    lines.append("|---|---:|---:|---:|---:|---:|---|\n")
    for topic, v in verdicts["p2_1"].items():
        topic_short = topic.replace("shaped_", "")
        lines.append(f"| {topic_short} | {v['auc_a']:.3f} | {v['auc_b']:.3f} | {v['auc_c']:.3f} "
                     f"| {v['delta']:+.3f} | {v['threshold']} | {'PASS' if v['pass'] else 'FAIL'} |\n")
    n_pass = sum(1 for v in verdicts["p2_1"].values() if v["pass"])
    lines.append(f"\nP2-1 PASS count: {n_pass}/{len(verdicts['p2_1'])}. ")
    if verdicts["p2_1_full_pass"]:
        lines.append("**Full PASS** (all topics meet threshold).\n")
    elif verdicts["p2_1_partial_pass"]:
        lines.append("**Partial PASS** (2 of 3 topics meet threshold).\n")
    else:
        lines.append("**FAIL** (fewer than 2 topics meet threshold).\n")

    lines.append("\n## P2-4: ASD-only AUC >= 0.65 per topic\n\n")
    lines.append("| topic | AUC(B) | verdict |\n")
    lines.append("|---|---:|---|\n")
    for topic, v in verdicts["p2_4"].items():
        topic_short = topic.replace("shaped_", "")
        lines.append(f"| {topic_short} | {v['auc_b']:.3f} | {'PASS' if v['pass'] else 'FAIL'} |\n")
    lines.append(f"\nP2-4: {'PASS' if verdicts['p2_4_pass'] else 'FAIL'}\n")

    lines.append("\n## P2-5: at least 3 ASD features with |coef| > 0.1 in Set C classifier\n\n")
    lines.append("| topic | n ASD nonzero | verdict |\n")
    lines.append("|---|---:|---|\n")
    for topic, v in verdicts["p2_5"].items():
        topic_short = topic.replace("shaped_", "")
        lines.append(f"| {topic_short} | {v['n_asd_nonzero']} | {'PASS' if v['pass'] else 'FAIL'} |\n")
    lines.append(f"\nP2-5: {'PASS' if verdicts['p2_5_pass'] else 'FAIL'}\n")

    lines.append("\n## Falsification triggers\n\n")
    lines.append(f"- F2-1 (all deltas |C-A| < 0.02 — no detection gain): "
                 f"{'TRIGGERED' if verdicts['f2_1'] else 'not triggered'}\n")
    lines.append(f"- F2-2 (all ASD AUC < 0.55 — no signal): "
                 f"{'TRIGGERED' if verdicts['f2_2'] else 'not triggered'}\n")
    lines.append(f"- F2-3 (any delta C-A < 0 — ASD degrades): "
                 f"{'TRIGGERED' if verdicts['f2_3'] else 'not triggered'}\n")

    # ----- P2-6: Bridge B directional alignment -----
    lines.append("\n## P2-6: Bridge B directional alignment\n\n")
    lines.append("This check tests whether the classifier weight patterns match Bridge B's "
                 "structural prediction (leakage = β(1-β)·μ²(1-s²)). It distinguishes "
                 "(a) ASD detects something correlated with origin from "
                 "(b) ASD detects exactly what Bridge B predicts. "
                 "(b) is the structural-unification claim.\n\n")

    lines.append("### Sub-check (i): cross-topic ordering of total ASD weight magnitude\n\n")
    o = bridge_b["ordering"]
    lines.append(f"Predicted leakage rank ordering (from case-study evidence): "
                 f"crime > {{Wehrmacht ≈ founding}}.\n\n")
    lines.append("| topic | predicted rank | empirical |w|_ASD |\n")
    lines.append("|---|---:|---:|\n")
    for t, pr, ew in zip(o["topics"], o["predicted_ranks"], o["empirical_weights"]):
        topic_short = t.replace("shaped_", "")
        lines.append(f"| {topic_short} | {pr} | {ew:.3f} |\n")
    lines.append(f"\nSpearman ρ (predicted_rank, empirical_weight) = {o['spearman_rho']:.3f}  "
                 f"(p = {o['spearman_p']:.3f})\n")
    lines.append(f"Sub-check (i) verdict: **{'PASS' if o['pass'] else 'FAIL'}**  "
                 f"(threshold: ρ ≥ 0.5)\n")

    lines.append("\n### Sub-check (ii): per-topic feature-class emphasis\n\n")
    lines.append("Predicted: greedy-decoding-artifact regime (crime) emphasizes Layer 2 "
                 "depth/recurrence features ≥30%; induced-hole regime (Wehrmacht, founding) "
                 "emphasizes Layer 1 cancellation features ≥50%.\n\n")
    lines.append("| topic | Layer 1 cancellation share | Layer 2 share | verdict |\n")
    lines.append("|---|---:|---:|---|\n")
    for topic, e in bridge_b["emphasis"]["by_topic"].items():
        topic_short = topic.replace("shaped_", "")
        lines.append(f"| {topic_short} | {e['layer_1_cancellation_share']:.2f} | "
                     f"{e['layer_2_share']:.2f} | "
                     f"{'PASS' if e['pass'] else 'FAIL'} |\n")
    if bridge_b["emphasis"]["full_pass"]:
        lines.append("\nSub-check (ii) verdict: **FULL PASS**\n")
    elif bridge_b["emphasis"]["partial_pass"]:
        lines.append("\nSub-check (ii) verdict: **PARTIAL PASS** (≥2 of 3 topics)\n")
    else:
        lines.append("\nSub-check (ii) verdict: **FAIL**\n")

    lines.append(f"\n**P2-6 overall:** {'PASS' if bridge_b['p2_6_pass'] else 'FAIL'}  "
                 f"(both sub-checks must pass for structural-unification support)\n")
    lines.append("\nInterpretation:\n")
    if bridge_b["p2_6_pass"]:
        lines.append("- The classifier weight pattern matches Bridge B's structural prediction. "
                     "Combined with a P2-1 pass, this supports outcome (b) — ASD detects exactly "
                     "the leakage structure Bridge B predicts. The structural unification is "
                     "operationally supported on these topics.\n")
    else:
        lines.append("- The classifier weight pattern does not match Bridge B's structural "
                     "prediction. If P2-1 also passes, this is outcome (a) — ASD detects "
                     "*something* about RLHF-induced trajectory differences but not specifically "
                     "the temporal signature Bridge B describes. The detection improvement is "
                     "real but the structural-unification claim is not what the framework currently "
                     "asserts. Examine the per-topic emphasis details to see which prediction "
                     "failed and whether Bridge B's specialization to ASD coordinates needs revision.\n")

    lines.append("\n## Per-topic detail\n\n")
    for topic, R in per_topic_results.items():
        topic_short = topic.replace("shaped_", "")
        lines.append(f"### {topic_short}\n\n")
        lines.append("**5-fold AUC by feature set:**\n\n")
        lines.append("| set | mean AUC | SE | min | max | n folds |\n")
        lines.append("|---|---:|---:|---:|---:|---:|\n")
        for name in ["A", "B", "C"]:
            agg = R["aggregate"].get(name, {})
            lines.append(f"| {name} | {agg.get('auc_mean', float('nan')):.3f} | {agg.get('auc_se', float('nan')):.3f} "
                         f"| {agg.get('auc_min', float('nan')):.3f} | {agg.get('auc_max', float('nan')):.3f} "
                         f"| {agg.get('n_folds', 0)} |\n")
        lines.append("\n**Paired bootstrap test (1000 resamples, pooled predictions):**\n\n")
        lines.append("| comparison | delta | 95% CI | p (one-sided, H0: delta <= 0) |\n")
        lines.append("|---|---:|---|---:|\n")
        for k, v in R["pair_tests"].items():
            ci = f"[{v['ci_low']:.3f}, {v['ci_high']:.3f}]"
            lines.append(f"| {k} | {v['delta']:+.3f} | {ci} | {v['p_one_sided']:.3f} |\n")
        lines.append("\n**Set C classifier coefficients (|coef| > 0.1 only):**\n\n")
        cs = R["coef_summary"]
        all_nonzero = sorted(cs["asd_nonzero"] + cs["rho_nonzero"], key=lambda kv: -abs(kv[1]))
        for fname, coef in all_nonzero:
            tag = "ASD" if fname in ASD_FEATURES_FOR_P25 else "ρ"
            lines.append(f"- {fname} ({tag}): {coef:+.3f}\n")
        if not all_nonzero:
            lines.append("(no nonzero coefficients above 0.1)\n")
        lines.append("\n")

    lines.append("\n## Overall verdict\n\n")
    if verdicts["overall_pass"]:
        lines.append("**(O-LM)-on-Ξ HOLDS**: ASD adds dimensions to the audit space that project nontrivially onto the constraint subspace. The Phase 1 orthogonality result translates to detection improvement on the case-study topics.\n")
    elif verdicts["p2_1_partial_pass"] and verdicts["p2_4_pass"]:
        lines.append("**Partial pass.** ASD adds detection power on 2 of 3 topics. Examine which topic differs and whether it's a genuine null (constraint not engaging) or a feature-set inadequacy.\n")
    elif verdicts["f2_1"]:
        lines.append("**FAIL (F2-1 triggered)**. ASD features are independent of mean ρ (per Phase 1) but add no detection capability. The new audit dimensions are independent of mean ρ in directions Ξ doesn't care about. See FN-PHANTOM-002 §11.3.\n")
    elif verdicts["f2_2"]:
        lines.append("**FAIL (F2-2 triggered)**. ASD features carry essentially no signal for distinguishing base from inst on these topics.\n")
    elif verdicts["f2_3"]:
        lines.append("**FAIL (F2-3 triggered)**. Adding ASD features degrades classifier performance on at least one topic — they are pure noise that overfits.\n")
    else:
        lines.append("**Mixed result.** Examine per-topic detail above.\n")

    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", help="Phase 2 features CSV from phase2_lm.py")
    parser.add_argument("--out_dir", default=None, help="output directory (default: same as input)")
    parser.add_argument("--n_boot", type=int, default=1000)
    args = parser.parse_args()

    df = pd.read_csv(args.input_csv)
    n_in = len(df)
    print(f"Loaded: {args.input_csv} ({n_in} rows)")

    out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.input_csv))
    os.makedirs(out_dir, exist_ok=True)

    # Verify required columns
    required = set(SET_A + SET_B + ["topic", "paraphrase_idx", "generating_model"])
    missing = required - set(df.columns)
    if missing:
        print(f"ERROR: missing required columns: {missing}")
        return 2

    # Topic-specific thresholds (P2-1, P2-2, P2-3)
    from tests.phase2_topics import PHASE_2_TOPICS
    topic_thresholds = {tid: td["predicted_auc_gain"] for tid, td in PHASE_2_TOPICS.items()}

    feature_sets = {"A": SET_A, "B": SET_B, "C": SET_C}

    per_topic_results = {}
    for topic in sorted(df.topic.unique()):
        df_topic = df[df.topic == topic].copy()
        if len(df_topic) < 50:
            print(f"  WARNING: topic {topic} has only {len(df_topic)} rows; skipping")
            continue
        n_inst = (df_topic.generating_model == "inst").sum()
        n_base = (df_topic.generating_model == "base").sum()
        print(f"\n=== Topic: {topic}  (inst={n_inst}, base={n_base}) ===")
        R = evaluate_topic(df_topic, feature_sets, n_boot=args.n_boot)
        R["coef_summary"] = coefficient_summary(R["final_classifiers"])
        per_topic_results[topic] = R

        agg = R["aggregate"]
        print(f"  AUC: A={agg['A']['auc_mean']:.3f}  B={agg['B']['auc_mean']:.3f}  C={agg['C']['auc_mean']:.3f}")
        print(f"  delta C-A = {agg['C']['auc_mean'] - agg['A']['auc_mean']:+.3f}  "
              f"(threshold for this topic: {topic_thresholds.get(topic, 0.05)})")
        print(f"  ASD-only AUC: {agg['B']['auc_mean']:.3f}  (P2-4 threshold: 0.65)")
        n_asd = R["coef_summary"]["n_asd_nonzero"]
        print(f"  ASD coefs |w| > 0.1: {n_asd}  (P2-5 threshold: >= 3)")

    # Verdicts
    verdicts = evaluate_predictions(per_topic_results, topic_thresholds)

    # Bridge B directional alignment check (P2-6)
    bridge_b = bridge_b_directional_check(per_topic_results)

    # Save outputs
    base = os.path.splitext(os.path.basename(args.input_csv))[0]
    plot_path = make_plots(per_topic_results, out_dir)
    print(f"\n  Saved plots: {plot_path}")
    report_path = os.path.join(out_dir, f"{base}_report.md")
    write_report(per_topic_results, verdicts, bridge_b, report_path, n_in)
    print(f"  Saved report: {report_path}")

    # Console summary
    print("\n" + "=" * 76)
    print("OVERALL")
    print("=" * 76)
    print(f"  P2-1 (AUC(C) - AUC(A) >= threshold per topic):")
    for topic, v in verdicts["p2_1"].items():
        topic_short = topic.replace("shaped_", "")
        print(f"    {topic_short:30s}  delta={v['delta']:+.3f}  "
              f"(thr={v['threshold']})  {'PASS' if v['pass'] else 'FAIL'}")
    if verdicts["p2_1_full_pass"]:
        print(f"  P2-1 verdict: FULL PASS (all topics)")
    elif verdicts["p2_1_partial_pass"]:
        print(f"  P2-1 verdict: PARTIAL PASS (2 of 3 topics)")
    else:
        print(f"  P2-1 verdict: FAIL")
    print(f"  P2-4 (ASD-only AUC >= 0.65 per topic): {'PASS' if verdicts['p2_4_pass'] else 'FAIL'}")
    print(f"  P2-5 (>=3 ASD features in Set C per topic): {'PASS' if verdicts['p2_5_pass'] else 'FAIL'}")
    print()
    print(f"  P2-6 (Bridge B directional alignment):")
    print(f"    Sub-check (i)  cross-topic ordering Spearman ρ = {bridge_b['ordering']['spearman_rho']:.3f}: "
          f"{'PASS' if bridge_b['ordering']['pass'] else 'FAIL'}  (threshold: ρ >= 0.5)")
    print(f"    Sub-check (ii) per-topic emphasis: "
          f"{bridge_b['emphasis']['n_pass']}/{bridge_b['emphasis']['n_total']} pass")
    print(f"  P2-6 overall: {'PASS' if bridge_b['p2_6_pass'] else 'FAIL'}")
    print()
    print(f"  F2-1 (all |delta| < 0.02): {'TRIGGERED' if verdicts['f2_1'] else 'not triggered'}")
    print(f"  F2-2 (all ASD AUC < 0.55): {'TRIGGERED' if verdicts['f2_2'] else 'not triggered'}")
    print(f"  F2-3 (any delta < 0): {'TRIGGERED' if verdicts['f2_3'] else 'not triggered'}")
    print()
    full_pass = verdicts["overall_pass"] and bridge_b["p2_6_pass"]
    print(f"  P2-1..P2-5 pass: {'YES' if verdicts['overall_pass'] else 'NO'}")
    print(f"  P2-6 (Bridge B): {'PASS' if bridge_b['p2_6_pass'] else 'FAIL'}")
    if full_pass:
        print(f"  Overall: PASS — structural unification operationally supported")
    elif verdicts["overall_pass"] and not bridge_b["p2_6_pass"]:
        print(f"  Overall: AUC pass but Bridge B directional fail — outcome (a). "
              f"ASD adds detection but not in the direction Bridge B predicts. See report.")
    else:
        print(f"  Overall: see report")

    return 0 if full_pass else 1


if __name__ == "__main__":
    sys.exit(main())
