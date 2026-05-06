"""
Phase 2-prime analysis - reformulated test on Phase 1 inst-only data.

Background: Phase 2 as originally designed was confounded by the
"gen-model-wins" artifact. When pi_inst samples a token, that token is
by construction more likely under pi_inst than under pi_base, so
mean_rho is systematically positive on inst-generated trajectories
and negative on base-generated trajectories. The base-vs-inst
classification task therefore had a trivial likelihood-ratio
solution and AUC(A) saturated at 1.000, leaving no headroom to
detect any contribution from ASD features.

Reformulation:
- Use only inst-generated trajectories from Phase 1 cache (4500 rows).
- Binary classification: shaped (1500 rows from 10 topics)
                         vs not-shaped (3000 rows from 20 topics:
                         10 control + 10 mid).
- Leave-one-topic-out cross-validation. Each fold trains on 29 topics
  and predicts on the held-out topic. This forces the classifier to
  learn a topic-shaping signature that generalizes to unseen topics
  (the operationally meaningful question), not just to memorize per-
  topic surface features.
- Same three feature sets, same logistic regression apparatus.

Question being answered:
  On inst-only trajectories, does ASD help detect topic shaping
  beyond what mean_rho alone does?

Pre-registered checks (analogous to Phase 2 originals, adjusted):
  P2'-1: AUC(C) - AUC(A) >= 0.05  (combined beats abelian baseline)
  P2'-4: AUC(B) >= 0.65            (ASD has signal alone)
  P2'-5: >= 3 ASD features have |standardized coef| > 0.1 in global
                                   Set C classifier
  P2'-6: Bridge B directional alignment, evaluated on the three
         Phase 2 topics (crime, founding, Wehrmacht):
         (i)  per-topic mean Set B score rank-orders with predicted
              leakage rank (Spearman rho >= 0.5)
         (ii) per-topic Set C feature emphasis matches predicted
              regime (Layer 2 dominant for crime, Layer 1 cancellation
              dominant for Wehrmacht and founding fathers)

Falsifications:
  F2'-1: AUC(C) - AUC(A) < 0.02   (no detection gain)
  F2'-2: AUC(B) < 0.55             (ASD has no signal)
  F2'-3: AUC(C) < AUC(A)           (ASD degrades classifier)

Output:
  results/phase2_prime_report.md
  results/phase2_prime_roc_and_coefs.png
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
from scipy.stats import spearmanr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---- Feature sets (same as Phase 2) ----
SET_A = ["mean_rho", "std_rho"]
SET_B = ["drift", "timing_cv", "mean_depth_excess", "isolated_frac",
         "Q_tail_1", "Q_tail_2", "Q_tail_3", "Q_tail_4", "r_plus"]
SET_C = SET_A + SET_B
ASD_FEATURES = SET_B
LAYER_1_CANCELLATION_FEATURES = {"drift", "isolated_frac"}
LAYER_2_DEPTH_FEATURES = {"Q_tail_1", "Q_tail_2", "Q_tail_3", "Q_tail_4", "r_plus"}

# ---- Bridge B predictions (carried over from Phase 2) ----
BRIDGE_B_PREDICTED_RANK = {
    "shaped_crime_demographics": 3,
    "shaped_wehrmacht_conduct": 1,
    "shaped_founding_fathers_slavery": 1,
}
BRIDGE_B_PREDICTED_EMPHASIS = {
    "shaped_crime_demographics": {"layer_2_min_share": 0.30},
    "shaped_wehrmacht_conduct": {"layer_1_cancellation_min_share": 0.50},
    "shaped_founding_fathers_slavery": {"layer_1_cancellation_min_share": 0.50},
}


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


def paired_bootstrap_auc_diff(y_true, score_a, score_c, n_boot=1000, seed=0):
    """Paired bootstrap on AUC(C) - AUC(A)."""
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
    ci_low = float(np.percentile(deltas, 2.5))
    ci_high = float(np.percentile(deltas, 97.5))
    p_one_sided = float((deltas <= 0).mean())
    return float(delta_obs), ci_low, ci_high, p_one_sided


def loo_topic_cv(df, features, label_col, topic_col="topic"):
    """
    Leave-one-topic-out cross-validation.

    For each topic in the data, hold it out as test, train on the
    remaining topics, predict on the held-out topic. Returns:
      - pooled (y_true, y_score) across all folds
      - per-topic prediction info: mean score, y label, category
    """
    topics = sorted(df[topic_col].unique())
    pooled_y, pooled_score = [], []
    per_topic = {}

    for held_out in topics:
        train = df[df[topic_col] != held_out]
        test = df[df[topic_col] == held_out]
        if len(train) == 0 or len(test) == 0:
            continue

        y_train = train[label_col].values
        y_test = test[label_col].values
        X_train = train[features].values
        X_test = test[features].values

        valid_train = np.all(np.isfinite(X_train), axis=1)
        valid_test = np.all(np.isfinite(X_test), axis=1)
        X_train = X_train[valid_train]; y_train = y_train[valid_train]
        X_test = X_test[valid_test];   y_test = y_test[valid_test]
        if len(X_train) < 10 or len(X_test) < 5:
            continue
        if len(np.unique(y_train)) < 2:
            continue

        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(X_train_s, y_train)
        score = clf.predict_proba(X_test_s)[:, 1]

        pooled_y.extend(y_test.tolist())
        pooled_score.extend(score.tolist())

        per_topic[held_out] = {
            "mean_score": float(np.mean(score)),
            "y": int(y_test[0]) if len(y_test) > 0 else None,
            "category": test["category"].iloc[0] if "category" in test.columns and len(test) > 0 else None,
            "n": int(len(score)),
        }

    return np.array(pooled_y), np.array(pooled_score), per_topic


def fit_global_classifier(df, features, label_col):
    """Fit on full data and return classifier + scaler for coefficient analysis."""
    y = df[label_col].values
    X = df[features].values
    valid = np.all(np.isfinite(X), axis=1)
    X = X[valid]; y = y[valid]
    scaler = StandardScaler()
    X_s = scaler.fit_transform(X)
    clf = LogisticRegression(max_iter=2000, C=1.0)
    clf.fit(X_s, y)
    return clf, scaler


def per_topic_emphasis_classifier(df, topic_id, features, topic_col="topic"):
    """
    Train a Set C classifier distinguishing one specific topic from all
    not-shaped trajectories. The resulting feature weights show what
    pattern that topic's shaping signature uses.

    Returns dict with all_coefs and feature-class shares.
    """
    target = df[df[topic_col] == topic_id].copy()
    notshaped = df[df["category"] != "shaped"].copy()
    if len(target) == 0 or len(notshaped) == 0:
        return None

    target["__y"] = 1
    notshaped["__y"] = 0
    sub = pd.concat([target, notshaped], axis=0).reset_index(drop=True)
    y = sub["__y"].values
    X = sub[features].values
    valid = np.all(np.isfinite(X), axis=1)
    X = X[valid]; y = y[valid]
    if len(X) < 50 or len(np.unique(y)) < 2:
        return None

    scaler = StandardScaler()
    X_s = scaler.fit_transform(X)
    clf = LogisticRegression(max_iter=2000, C=1.0)
    clf.fit(X_s, y)
    coefs = dict(zip(features, clf.coef_[0]))

    # ASD-only weight magnitudes
    asd_coefs = {f: c for f, c in coefs.items() if f in ASD_FEATURES}
    if not asd_coefs:
        return None
    total_w = float(np.sqrt(sum(c**2 for c in asd_coefs.values())))
    l1_w = float(np.sqrt(sum(c**2 for f, c in asd_coefs.items()
                              if f in LAYER_1_CANCELLATION_FEATURES)))
    l2_w = float(np.sqrt(sum(c**2 for f, c in asd_coefs.items()
                              if f in LAYER_2_DEPTH_FEATURES)))
    return {
        "all_coefs": coefs,
        "total_asd_weight": total_w,
        "layer_1_cancellation_share": l1_w / total_w if total_w > 0 else 0.0,
        "layer_2_share": l2_w / total_w if total_w > 0 else 0.0,
    }


def coefficient_summary(clf, features, abs_threshold=0.1):
    coefs = dict(zip(features, clf.coef_[0]))
    asd_nonzero = [(f, coefs[f]) for f in features if f in ASD_FEATURES and abs(coefs[f]) > abs_threshold]
    rho_nonzero = [(f, coefs[f]) for f in features if f not in ASD_FEATURES and abs(coefs[f]) > abs_threshold]
    return {
        "all_coefs": coefs,
        "asd_nonzero": asd_nonzero,
        "rho_nonzero": rho_nonzero,
        "n_asd_nonzero": len(asd_nonzero),
    }


def make_plots(pooled_results, per_topic_b_scores, set_c_clf, out_dir):
    """ROC overlay + Set C coefficient bar."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Pane 1: ROC overlay
    ax = axes[0]
    for name, color in [("A", "#2266cc"), ("B", "#cc4422"), ("C", "#22aa44")]:
        if name not in pooled_results:
            continue
        y, s, auc = pooled_results[name]["y"], pooled_results[name]["score"], pooled_results[name]["auc"]
        if len(y) == 0 or len(np.unique(y)) < 2:
            continue
        fpr, tpr, _ = roc_curve(y, s)
        ax.plot(fpr, tpr, color=color, linewidth=2, label=f"Set {name}: AUC={auc:.3f}")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
    ax.axvline(0.05, color="gray", linestyle=":", alpha=0.5, label="FPR=0.05")
    ax.set_xlabel("FPR"); ax.set_ylabel("TPR")
    ax.set_title("Pooled ROC across LOO-by-topic folds\n(shaped vs not-shaped, inst-only)", fontsize=10)
    ax.legend(fontsize=9, loc="lower right")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    # Pane 2: Set C standardized coefficients
    ax = axes[1]
    coefs = dict(zip(SET_C, set_c_clf.coef_[0]))
    names = list(coefs.keys())
    vals = [coefs[n] for n in names]
    colors_bar = ["#2266cc" if n in SET_A else "#cc4422" for n in names]
    ax.barh(names, vals, color=colors_bar)
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Standardized coefficient")
    ax.set_title("Global Set C classifier\n(blue=ρ-features, red=ASD-features)", fontsize=10)
    ax.tick_params(axis="y", labelsize=8)

    # Pane 3: per-topic Set B mean scores, colored by category
    ax = axes[2]
    cats = ["control", "mid", "shaped"]
    cat_colors = {"control": "#2266cc", "mid": "#cc8822", "shaped": "#cc4422"}
    for cat in cats:
        topics_in_cat = [(t, info) for t, info in per_topic_b_scores.items()
                         if info["category"] == cat]
        topics_in_cat.sort(key=lambda kv: kv[1]["mean_score"], reverse=True)
        names = [t.replace("shaped_", "").replace("control_", "").replace("mid_", "")[:18]
                 for t, _ in topics_in_cat]
        scores = [info["mean_score"] for _, info in topics_in_cat]
        ax.scatter([cat] * len(scores), scores, color=cat_colors[cat], alpha=0.7, s=60)
        for nm, sc in zip(names, scores):
            ax.annotate(nm, (cat, sc), fontsize=6.5, alpha=0.7,
                         xytext=(8, 0), textcoords="offset points")
    ax.set_ylabel("Mean Set B score on held-out topic")
    ax.set_xlabel("Topic category")
    ax.set_title("Per-topic 'shapedness score' (ASD-only)\nfrom LOO-by-topic predictions", fontsize=10)
    ax.axhline(0.5, color="gray", linestyle=":", alpha=0.5)

    fig.suptitle("Phase 2-prime: shaped-vs-not-shaped on inst-only trajectories", fontsize=12, y=1.02)
    fig.tight_layout()
    out_path = os.path.join(out_dir, "phase2_prime_roc_and_coefs.png")
    fig.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return out_path


def write_report(pooled_results, set_c_summary, per_topic_b_scores,
                  bridge_b, verdicts, out_path, n_input_rows):
    L = []
    L.append("# Phase 2-prime - Reformulated Augmented Detection Test\n\n")
    L.append("_Input feature rows: {}; configuration: inst-only trajectories from "
             "Phase 1 cache, binary classification shaped-vs-not-shaped, leave-one-"
             "topic-out CV._\n\n".format(n_input_rows))

    L.append("## Background\n\n")
    L.append("The original Phase 2 protocol asked classifier to distinguish "
             "base-generated from inst-generated trajectories using mean_rho + std_rho "
             "as Set A. This was confounded by the gen-model-wins artifact: each model's "
             "likelihood is highest on its own samples, so mean_rho is a near-deterministic "
             "function of generating-model identity. AUC(A) saturated at 1.000 across all "
             "topics, leaving no headroom to detect ASD's contribution.\n\n")
    L.append("This reformulation removes the artifact by using only inst-generated "
             "trajectories and re-targeting the classifier to detect topic shaping "
             "(shaped vs control/mid). The ground truth is now the topic-category label, "
             "not the generating model. Mean_rho on shaped-vs-not differs by the actual "
             "distortion magnitude (the standard Phantom signal), not by tautology.\n\n")

    L.append("## Pooled AUC across LOO-by-topic folds\n\n")
    L.append("| set | AUC | 95% CI | features |\n")
    L.append("|---|---:|---|---|\n")
    for name in ["A", "B", "C"]:
        r = pooled_results[name]
        L.append("| {} | {:.3f} | [{:.3f}, {:.3f}] | {} |\n".format(
            name, r["auc"], r["ci_low"], r["ci_high"], len(SET_A if name == 'A' else SET_B if name == 'B' else SET_C)))

    L.append("\n## Pre-registered checks\n\n")
    L.append("**P2'-1 (AUC(C) - AUC(A) >= 0.05): {}**\n".format("PASS" if verdicts["p2p_1_pass"] else "FAIL"))
    L.append("- delta = {:+.3f}\n".format(verdicts["delta_ca"]))
    L.append("- 95% CI on delta (paired bootstrap): [{:.3f}, {:.3f}]\n".format(
        verdicts["delta_ci_low"], verdicts["delta_ci_high"]))
    L.append("- one-sided p-value (H0: delta <= 0): {:.3f}\n\n".format(verdicts["delta_p"]))

    L.append("**P2'-4 (AUC(B) >= 0.65): {}**\n".format("PASS" if verdicts["p2p_4_pass"] else "FAIL"))
    L.append("- AUC(B) = {:.3f}\n\n".format(pooled_results["B"]["auc"]))

    L.append("**P2'-5 (>=3 ASD features with |coef| > 0.1 in global Set C classifier): {}**\n".format(
        "PASS" if verdicts["p2p_5_pass"] else "FAIL"))
    L.append("- {} ASD features above threshold\n\n".format(set_c_summary["n_asd_nonzero"]))

    L.append("## Falsification triggers\n\n")
    L.append("- F2'-1 (delta < 0.02 — no detection gain): {}\n".format(
        "TRIGGERED" if verdicts["f2p_1"] else "not triggered"))
    L.append("- F2'-2 (AUC(B) < 0.55 — no signal): {}\n".format(
        "TRIGGERED" if verdicts["f2p_2"] else "not triggered"))
    L.append("- F2'-3 (delta < 0 — ASD degrades): {}\n".format(
        "TRIGGERED" if verdicts["f2p_3"] else "not triggered"))

    L.append("\n## Set C classifier coefficients (global fit, |coef| > 0.1)\n\n")
    all_nonzero = sorted(set_c_summary["asd_nonzero"] + set_c_summary["rho_nonzero"],
                         key=lambda kv: -abs(kv[1]))
    for fname, coef in all_nonzero:
        tag = "ASD" if fname in ASD_FEATURES else "ρ"
        L.append("- {} ({}): {:+.3f}\n".format(fname, tag, coef))
    if not all_nonzero:
        L.append("(no nonzero coefficients above 0.1)\n")

    L.append("\n## Per-topic 'shapedness score' (mean LOO-Set-B prediction)\n\n")
    L.append("Each topic is held out and the classifier (trained on the other 29 topics) "
             "predicts its trajectories' shaping probability. Mean across the topic's 150 "
             "trajectories (30 seeds × 5 paraphrases) is the shapedness score.\n\n")
    L.append("| topic | category | mean Set B score | true label |\n")
    L.append("|---|---|---:|---:|\n")
    items = sorted(per_topic_b_scores.items(),
                   key=lambda kv: -kv[1]["mean_score"])
    for t, info in items:
        L.append("| {} | {} | {:.3f} | {} |\n".format(
            t, info["category"], info["mean_score"], info["y"]))

    L.append("\n## P2'-6: Bridge B directional alignment\n\n")
    L.append("Tests whether classifier signal patterns match Bridge B's structural "
             "prediction across the three Phase 2 case-study topics.\n\n")

    L.append("### Sub-check (i): cross-topic ordering of mean Set B score\n\n")
    o = bridge_b["ordering"]
    L.append("Predicted leakage rank (case-study evidence): crime > {Wehrmacht ≈ founding}.\n\n")
    L.append("| topic | predicted rank | mean Set B score |\n")
    L.append("|---|---:|---:|\n")
    for t, pr, s in zip(o["topics"], o["predicted_ranks"], o["scores"]):
        L.append("| {} | {} | {:.3f} |\n".format(t.replace("shaped_", ""), pr, s))
    L.append("\nSpearman ρ (predicted_rank, score) = {:.3f}  (p = {:.3f})\n".format(
        o["spearman_rho"], o["spearman_p"]))
    L.append("Sub-check (i) verdict: **{}**\n\n".format("PASS" if o["pass"] else "FAIL"))

    L.append("### Sub-check (ii): per-topic feature-class emphasis\n\n")
    L.append("Per-topic Set C classifier trained as (one shaped topic) vs all not-shaped.\n\n")
    L.append("Predicted: crime emphasizes Layer 2 (≥30%); Wehrmacht and founding emphasize "
             "Layer 1 cancellation (≥50%).\n\n")
    L.append("| topic | Layer 1 cancel share | Layer 2 share | verdict |\n")
    L.append("|---|---:|---:|---|\n")
    for t, e in bridge_b["emphasis"]["by_topic"].items():
        if e is None:
            continue
        L.append("| {} | {:.2f} | {:.2f} | {} |\n".format(
            t.replace("shaped_", ""),
            e["layer_1_cancellation_share"],
            e["layer_2_share"],
            "PASS" if e["pass"] else "FAIL"))
    L.append("\nSub-check (ii) verdict: **{}**\n".format(
        "FULL PASS" if bridge_b["emphasis"]["full_pass"] else
        "PARTIAL PASS" if bridge_b["emphasis"]["partial_pass"] else "FAIL"))

    L.append("\n**P2'-6 overall**: {}\n".format("PASS" if bridge_b["p2p_6_pass"] else "FAIL"))

    L.append("\n## Overall verdict\n\n")
    overall = (verdicts["p2p_1_pass"] and verdicts["p2p_4_pass"] and
               verdicts["p2p_5_pass"] and bridge_b["p2p_6_pass"])
    if overall:
        L.append("**FULL PASS** - The reformulated test confirms ASD adds detection capability "
                 "for topic shaping beyond the abelian baseline, with classifier weight patterns "
                 "matching Bridge B's structural prediction. The Phase 1 orthogonality result "
                 "translates to operational additivity on Ξ. Audit-blind subspace genuinely "
                 "shrinks under augmentation.\n")
    elif (verdicts["p2p_1_pass"] and verdicts["p2p_4_pass"]):
        L.append("**Detection pass with structural caveats.** ASD adds detection power over the "
                 "abelian baseline (P2'-1, P2'-4 pass). Coefficient or directional checks have "
                 "partial pass. Examine sub-results for which prediction failed and consider "
                 "whether case-study categorizations or Bridge B's specialization need revision.\n")
    elif verdicts["f2p_1"]:
        L.append("**FAIL (F2'-1).** ASD adds no detection gain over the abelian baseline on the "
                 "shaped-vs-not-shaped task. Phase 1's orthogonality holds but the new audit "
                 "dimensions don't project onto Ξ in directions that detect shaping. The "
                 "structural-unification claim is not supported.\n")
    else:
        L.append("**Mixed.** See per-check details above.\n")

    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(L)
    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", help="Phase 1 features CSV (inst-only trajectories)")
    parser.add_argument("--out_dir", default=None)
    parser.add_argument("--n_boot", type=int, default=1000)
    args = parser.parse_args()

    df = pd.read_csv(args.input_csv)
    n_in = len(df)
    print("Loaded: {} ({} rows)".format(args.input_csv, n_in))

    out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.input_csv))
    os.makedirs(out_dir, exist_ok=True)

    required = set(SET_C + ["topic", "category", "paraphrase_idx"])
    missing = required - set(df.columns)
    if missing:
        print("ERROR: missing columns: {}".format(missing))
        return 2

    # Define binary label: shaped (1) vs not-shaped (0)
    df = df.copy()
    df["__label"] = (df["category"] == "shaped").astype(int)
    n_shaped = int(df["__label"].sum())
    n_other = int((1 - df["__label"]).sum())
    print("  shaped trajectories: {}".format(n_shaped))
    print("  not-shaped trajectories: {}".format(n_other))
    print("  topics: {} ({} categories)".format(
        df.topic.nunique(),
        df.groupby("category").topic.nunique().to_dict()))

    # ---- Run LOO-by-topic CV for each feature set ----
    pooled_results = {}
    per_topic_scores_b = {}
    print("\nRunning leave-one-topic-out CV across {} folds per set...".format(df.topic.nunique()))
    for name, features in [("A", SET_A), ("B", SET_B), ("C", SET_C)]:
        y, score, per_topic = loo_topic_cv(df, features, "__label")
        auc, ci_low, ci_high = auc_with_ci(y, score, n_boot=args.n_boot, seed=42)
        pooled_results[name] = {
            "y": y, "score": score, "auc": auc,
            "ci_low": ci_low, "ci_high": ci_high,
        }
        if name == "B":
            per_topic_scores_b = per_topic
        print("  Set {}: pooled AUC = {:.3f}  95% CI [{:.3f}, {:.3f}]".format(
            name, auc, ci_low, ci_high))

    # Paired bootstrap on AUC(C) - AUC(A)
    delta, ci_lo, ci_hi, p = paired_bootstrap_auc_diff(
        pooled_results["A"]["y"],
        pooled_results["A"]["score"],
        pooled_results["C"]["score"],
        n_boot=args.n_boot, seed=42)
    print("\n  delta C-A = {:+.3f}  95% CI [{:.3f}, {:.3f}]  p (1-sided) = {:.3f}".format(
        delta, ci_lo, ci_hi, p))

    # ---- Global Set C classifier for coefficient analysis ----
    set_c_clf, set_c_scaler = fit_global_classifier(df, SET_C, "__label")
    set_c_summary = coefficient_summary(set_c_clf, SET_C)
    print("\n  Global Set C classifier: {} ASD features with |coef| > 0.1".format(
        set_c_summary["n_asd_nonzero"]))

    # ---- Bridge B directional checks ----
    print("\n  Bridge B directional check on 3 Phase 2 topics...")
    bridge_topics = sorted(BRIDGE_B_PREDICTED_RANK.keys())
    bridge_topics_in_data = [t for t in bridge_topics if t in per_topic_scores_b]

    # Sub-check (i): cross-topic ordering by Set B score
    predicted = [BRIDGE_B_PREDICTED_RANK[t] for t in bridge_topics_in_data]
    scores = [per_topic_scores_b[t]["mean_score"] for t in bridge_topics_in_data]
    if len(set(predicted)) > 1 and len(set(scores)) > 1:
        rho, p_sp = spearmanr(predicted, scores)
        ordering_pass = (not np.isnan(rho)) and rho >= 0.5
    else:
        rho, p_sp = float("nan"), float("nan")
        ordering_pass = False

    # Sub-check (ii): per-topic emphasis (target vs not-shaped classifier)
    emphasis_by_topic = {}
    for t in bridge_topics_in_data:
        result = per_topic_emphasis_classifier(df, t, SET_C)
        if result is None:
            emphasis_by_topic[t] = None
            continue
        pred = BRIDGE_B_PREDICTED_EMPHASIS.get(t, {})
        topic_pass = True
        if "layer_2_min_share" in pred:
            topic_pass = topic_pass and (result["layer_2_share"] >= pred["layer_2_min_share"])
        if "layer_1_cancellation_min_share" in pred:
            topic_pass = topic_pass and (result["layer_1_cancellation_share"] >= pred["layer_1_cancellation_min_share"])
        result["pass"] = topic_pass
        emphasis_by_topic[t] = result

    n_emphasis_pass = sum(1 for v in emphasis_by_topic.values() if v is not None and v["pass"])
    n_emphasis_total = sum(1 for v in emphasis_by_topic.values() if v is not None)
    emphasis_full_pass = n_emphasis_pass == n_emphasis_total and n_emphasis_total > 0
    emphasis_partial_pass = n_emphasis_pass >= 2 and not emphasis_full_pass

    bridge_b = {
        "ordering": {
            "topics": bridge_topics_in_data,
            "predicted_ranks": predicted,
            "scores": scores,
            "spearman_rho": rho,
            "spearman_p": p_sp,
            "pass": ordering_pass,
        },
        "emphasis": {
            "by_topic": emphasis_by_topic,
            "n_pass": n_emphasis_pass,
            "n_total": n_emphasis_total,
            "full_pass": emphasis_full_pass,
            "partial_pass": emphasis_partial_pass,
        },
        "p2p_6_pass": ordering_pass and emphasis_full_pass,
    }

    print("    Sub-check (i)  Spearman ρ = {:.3f}: {}".format(
        rho, "PASS" if ordering_pass else "FAIL"))
    print("    Sub-check (ii) per-topic emphasis: {}/{} pass".format(
        n_emphasis_pass, n_emphasis_total))
    print("  P2'-6: {}".format("PASS" if bridge_b["p2p_6_pass"] else "FAIL"))

    # ---- Verdicts ----
    auc_a = pooled_results["A"]["auc"]
    auc_b = pooled_results["B"]["auc"]
    auc_c = pooled_results["C"]["auc"]
    verdicts = {
        "delta_ca": delta,
        "delta_ci_low": ci_lo,
        "delta_ci_high": ci_hi,
        "delta_p": p,
        "p2p_1_pass": delta >= 0.05,
        "p2p_4_pass": auc_b >= 0.65,
        "p2p_5_pass": set_c_summary["n_asd_nonzero"] >= 3,
        "f2p_1": delta < 0.02,
        "f2p_2": auc_b < 0.55,
        "f2p_3": delta < 0,
    }

    # ---- Save outputs ----
    plot_path = make_plots(pooled_results, per_topic_scores_b, set_c_clf, out_dir)
    print("\n  Saved plots: {}".format(plot_path))
    report_path = os.path.join(out_dir, "phase2_prime_report.md")
    write_report(pooled_results, set_c_summary, per_topic_scores_b,
                  bridge_b, verdicts, report_path, n_in)
    print("  Saved report: {}".format(report_path))

    # ---- Console summary ----
    print("\n" + "=" * 76)
    print("OVERALL")
    print("=" * 76)
    print("  Pooled AUC: A={:.3f}  B={:.3f}  C={:.3f}".format(auc_a, auc_b, auc_c))
    print("  delta C-A = {:+.3f}  (threshold 0.05)".format(delta))
    print()
    print("  P2'-1 (delta >= 0.05):     {}".format("PASS" if verdicts["p2p_1_pass"] else "FAIL"))
    print("  P2'-4 (AUC(B) >= 0.65):    {}".format("PASS" if verdicts["p2p_4_pass"] else "FAIL"))
    print("  P2'-5 (3+ ASD coefs):      {}".format("PASS" if verdicts["p2p_5_pass"] else "FAIL"))
    print("  P2'-6 (Bridge B):          {}".format("PASS" if bridge_b["p2p_6_pass"] else "FAIL"))
    print()
    print("  F2'-1 (delta < 0.02):      {}".format("TRIGGERED" if verdicts["f2p_1"] else "not triggered"))
    print("  F2'-2 (AUC(B) < 0.55):     {}".format("TRIGGERED" if verdicts["f2p_2"] else "not triggered"))
    print("  F2'-3 (delta < 0):         {}".format("TRIGGERED" if verdicts["f2p_3"] else "not triggered"))
    print()

    overall = (verdicts["p2p_1_pass"] and verdicts["p2p_4_pass"]
                and verdicts["p2p_5_pass"] and bridge_b["p2p_6_pass"])
    print("  Overall: {}".format("PASS" if overall else "see report"))
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
