"""
Phase 0 - Encoding Validation on LM trajectories.

Per FN-PHANTOM-002 Section 8.0.

Setup:
  - Models: Llama-3.1-8B-Instruct (generates + Choice-A scoring)
            Llama-3.1-8B (Choice-C base scoring)
  - Topics: 10 low-distortion control topics
  - Paraphrases: 3 per topic
  - Temperature: T=0.7
  - Seeds: K=30 per (topic, paraphrase) pair
  - Generation length: T_gen = 256 tokens
  - Block size sweep: b in {4, 8, 16}

Sequential model loading (load Instruct -> generate + score everything;
free; load base -> score everything; free) -- needed for 16GB VRAM cards.

Backend swap: change the `backend = ...` line in main() to switch between
the mock backend (no GPU) and the real Llama backend.
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import numpy as np
import pandas as pd
from src.asd_encoder import encode_and_walk
from src.asd_features import all_features, layer1_features, get_iid_null
from src import llm_trajectory as lt


# Phase 0 setup: 10 control topics, 3 paraphrases each
PHASE_0_TOPICS = {
    "geography_capitals": [
        "What are the capital cities of European countries?",
        "Tell me about the capital cities in Europe.",
        "Could you list European capitals?",
    ],
    "chemistry_periodic": [
        "Describe the structure of the periodic table of elements.",
        "How is the periodic table organized?",
        "Explain the layout of the periodic table.",
    ],
    "physics_motion": [
        "How does Newton's first law of motion work?",
        "Explain Newton's first law.",
        "What is the law of inertia?",
    ],
    "math_pythag": [
        "Describe the Pythagorean theorem.",
        "How does a^2 + b^2 = c^2 work for triangles?",
        "Explain Pythagoras' theorem.",
    ],
    "biology_cells": [
        "Describe the structure of a eukaryotic cell.",
        "What's inside a eukaryotic cell?",
        "Explain the parts of a eukaryotic cell.",
    ],
    "astronomy_solar": [
        "Describe the planets of the solar system in order.",
        "List the planets in our solar system.",
        "What are the planets of our solar system?",
    ],
    "language_grammar": [
        "Explain how English verb tenses work.",
        "How are tenses used in English?",
        "Describe English verb conjugation.",
    ],
    "music_notation": [
        "Describe how musical notation works.",
        "Explain reading sheet music.",
        "How does standard music notation work?",
    ],
    "cooking_techniques": [
        "Explain the difference between sauteing and braising.",
        "How does sauteing differ from braising?",
        "Compare sauteing and braising as cooking techniques.",
    ],
    "weather_clouds": [
        "Describe the major types of clouds.",
        "What are the main cloud types?",
        "Explain the classification of clouds.",
    ],
}


def build_specs(K: int, T_gen: int, temperature: float):
    """Build the full list of generation specs for two-pass batch."""
    specs = []
    for topic, paraphrases in PHASE_0_TOPICS.items():
        for p_idx, paraphrase in enumerate(paraphrases):
            for seed in range(K):
                specs.append({
                    "prompt": paraphrase,
                    "seed": seed,
                    "T": T_gen,
                    "temperature": temperature,
                    "meta_extra": {
                        "topic": topic,
                        "paraphrase_idx": p_idx,
                    },
                })
    return specs


def encode_trajectory_signal(traj, choice: str, block_size: int,
                              null: dict, max_depth: int = 6) -> dict:
    """Encode a trajectory's signal and extract all features."""
    sig = traj.signal(choice)
    if len(sig) < block_size:
        return {}
    rng = np.random.default_rng(traj.meta.get("seed", 0) + 7_000_000)
    ep = encode_and_walk(sig, block_size=block_size,
                          max_depth_tracked=max_depth, rng=rng)
    feats = all_features(ep, null)
    feats["mean_rho"] = float(np.mean(traj.rho))
    feats["mean_surp_base"] = float(np.mean(traj.surprisal_base))
    feats["mean_surp_inst"] = float(np.mean(traj.surprisal_inst))
    feats["T_actual"] = int(len(sig))
    return feats


def run_phase0(backend, K=30, T_gen=256, temperature=0.7,
                block_sizes=(4, 8, 16), signal_choice="C",
                trajectory_cache_path=None):
    """
    Run Phase 0 in two passes (handled by backend.generate_batch),
    then encode at all block sizes.

    If trajectory_cache_path is provided and the file exists, load
    trajectories from it instead of regenerating. After regeneration,
    save to that path. This lets you re-run encoding analysis without
    re-running the LM forward passes.
    """
    n_topics = len(PHASE_0_TOPICS)
    print(f"  Topics: {n_topics}, paraphrases per topic: 3")
    print(f"  Seeds per (topic, paraphrase): {K}")
    print(f"  T_gen = {T_gen}, temp = {temperature}, signal = Choice {signal_choice}")
    print(f"  Block sizes: {list(block_sizes)}")
    print(f"  Total trajectories: {n_topics * 3 * K}")
    print()

    # ---------- Phase 0.LM: produce trajectories ----------
    trajectories = None
    if trajectory_cache_path and os.path.exists(trajectory_cache_path):
        print(f"Loading cached trajectories from {trajectory_cache_path}")
        trajectories = _load_trajectories(trajectory_cache_path)
        print(f"  loaded {len(trajectories)} trajectories")

    if trajectories is None:
        specs = build_specs(K, T_gen, temperature)
        trajectories = backend.generate_batch(specs, verbose_every=10)
        if trajectory_cache_path:
            _save_trajectories(trajectories, specs, trajectory_cache_path)
            print(f"  saved trajectories to {trajectory_cache_path}")

    # Drop failed trajectories
    n_total = len(trajectories)
    trajectories = [t for t in trajectories if t is not None]
    n_ok = len(trajectories)
    if n_ok < n_total:
        print(f"  WARNING: {n_total - n_ok} trajectories failed (OOM or empty); proceeding with {n_ok}")

    # ---------- Phase 0.encode: extract features at each block size ----------
    print(f"\n=== Encoding {n_ok} trajectories at block sizes {list(block_sizes)} ===")
    nulls = {b: get_iid_null(T_gen, block_size=b) for b in block_sizes}
    for b in block_sizes:
        print(f"  IID null at b={b}: cancel_rate = {nulls[b]['cancel_rate']:.4f} +- {nulls[b]['cancel_rate_std']:.4f}")

    rows = []
    for traj in trajectories:
        topic = traj.meta.get("topic", "?")
        p_idx = traj.meta.get("paraphrase_idx", -1)
        seed = traj.meta.get("seed", -1)
        for b in block_sizes:
            feats = encode_trajectory_signal(
                traj, signal_choice, block_size=b, null=nulls[b],
            )
            if not feats:
                continue
            feats["topic"] = topic
            feats["paraphrase_idx"] = p_idx
            feats["seed"] = seed
            feats["block_size"] = b
            feats["signal_choice"] = signal_choice
            rows.append(feats)

    return pd.DataFrame(rows)


def _save_trajectories(trajectories, specs, path):
    """Persist trajectories as numpy arrays in a single .npz."""
    payload = {}
    for i, (spec, traj) in enumerate(zip(specs, trajectories)):
        if traj is None:
            continue
        payload[f"surp_inst_{i}"] = traj.surprisal_inst
        payload[f"surp_base_{i}"] = traj.surprisal_base
        payload[f"rho_{i}"] = traj.rho
    # Metadata as JSON sidecar
    meta_list = []
    for i, (spec, traj) in enumerate(zip(specs, trajectories)):
        if traj is None:
            meta_list.append(None)
        else:
            meta_list.append({
                "i": i,
                "prompt": traj.prompt,
                "generation": traj.generation,
                "generating_model": traj.generating_model,
                "meta": traj.meta,
            })
    np.savez_compressed(path, **payload)
    with open(path + ".meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_list, f, indent=2, ensure_ascii=False, default=str)


def _load_trajectories(path):
    """Inverse of _save_trajectories."""
    with open(path + ".meta.json", "r", encoding="utf-8") as f:
        meta_list = json.load(f)
    arr = np.load(path)
    trajectories = []
    for m in meta_list:
        if m is None:
            trajectories.append(None)
            continue
        i = m["i"]
        traj = lt.Trajectory(
            prompt=m["prompt"],
            generation=m["generation"],
            surprisal_inst=arr[f"surp_inst_{i}"],
            surprisal_base=arr[f"surp_base_{i}"],
            rho=arr[f"rho_{i}"],
            generating_model=m["generating_model"],
            meta=m["meta"],
        )
        trajectories.append(traj)
    return trajectories


def evaluate_phase0(df: pd.DataFrame) -> dict:
    """
    Phase 0 stability evaluation.

    Z-score features (drift, mean_depth_excess, d2_excess, isolated_frac):
        target std < 1.5 (within ~1.5 sigma of IID null).
    Absolute features (timing_cv): target CV < 0.30.
    """
    Z_SCORE_FEATURES = {"drift", "mean_depth_excess", "d2_excess", "isolated_frac"}
    feature_cols = ["drift", "timing_cv", "mean_depth_excess",
                     "isolated_frac", "d2_excess"]
    block_sizes = sorted(df.block_size.unique())
    results = {}

    stab_table = []
    for b in block_sizes:
        df_b = df[df.block_size == b]
        for (topic, p_idx), grp in df_b.groupby(["topic", "paraphrase_idx"]):
            for c in feature_cols:
                vals = grp[c].dropna()
                if len(vals) < 5:
                    continue
                m = float(vals.mean())
                s = float(vals.std())
                if c in Z_SCORE_FEATURES:
                    metric = s
                    metric_name = "std"
                else:
                    metric = abs(s / m) if abs(m) > 1e-8 else float("nan")
                    metric_name = "cv"
                stab_table.append({
                    "block_size": b, "topic": topic, "paraphrase_idx": p_idx,
                    "feature": c, "mean": m, "std": s,
                    "metric": metric, "metric_name": metric_name,
                })
    stab_df = pd.DataFrame(stab_table)
    results["stab_table"] = stab_df

    print("\nStability summary (median across topic x paraphrase pairs):")
    print("  Z-score features measured by STD (target < 1.5)")
    print("  Absolute features measured by CV (target < 0.30)")
    if not stab_df.empty:
        pivot = stab_df.dropna(subset=["metric"]).pivot_table(
            index="feature", columns="block_size", values="metric", aggfunc="median"
        )
        print(pivot.round(3))

    # P0-1
    p0_1_failures = []
    for c in feature_cols:
        x = stab_df[(stab_df.block_size == 4) & (stab_df.feature == c) & stab_df.metric.notna()]
        if len(x) == 0:
            continue
        threshold = 1.5 if c in Z_SCORE_FEATURES else 0.30
        med = x.metric.median()
        ok = med < threshold
        if not ok:
            p0_1_failures.append((c, med, threshold))
    p0_1_pass = len(p0_1_failures) == 0
    results["P0_1_pass"] = p0_1_pass
    print(f"\nP0-1 (each feature within stability bound at b=4): {'PASS' if p0_1_pass else 'FAIL'}")
    for c, med, t in p0_1_failures:
        print(f"   FAIL: {c} median={med:.3f} > {t}")

    # P0-3
    p0_3_pass = True
    p0_3_violations = []
    for c in feature_cols:
        ms = []
        for b in block_sizes:
            x = stab_df[(stab_df.block_size == b) & (stab_df.feature == c) & stab_df.metric.notna()]
            ms.append(x.metric.median() if len(x) > 0 else np.nan)
        for i in range(len(ms) - 1):
            if (not np.isnan(ms[i]) and not np.isnan(ms[i + 1])
                and ms[i + 1] > ms[i] * 1.5):
                p0_3_pass = False
                p0_3_violations.append((c, block_sizes[i], block_sizes[i + 1], ms[i], ms[i + 1]))
                break
    results["P0_3_pass"] = p0_3_pass
    print(f"P0-3 (stability metric stable/decreasing with b): {'PASS' if p0_3_pass else 'FAIL'}")
    for c, b1, b2, m1, m2 in p0_3_violations:
        print(f"   FAIL: {c} median b={b1}->{b2}: {m1:.3f} -> {m2:.3f}")

    return results


def main():
    print("=" * 76)
    print("Phase 0 - LM Trajectory Encoding Validation (sequential loading)")
    print("=" * 76)
    print()

    # ---- Backend selection -----------------------------------------------
    # Sandbox / no GPU:
    # backend = lt.MockLMBackend()

    # Real Llama on user GPU box (RTX 5080 16GB) -- sequential loading:
    backend = lt.TransformersBackend(
        inst_model_name="meta-llama/Llama-3.1-8B-Instruct",
        base_model_name="meta-llama/Llama-3.1-8B",
        device="cuda",
        local_files_only=True,   # optional: enforce no-download
    )    
    
    # ----------------------------------------------------------------------

    print(f"Backend: {type(backend).__name__}")

    out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)
    suffix = "mock" if isinstance(backend, lt.MockLMBackend) else "llama"

    cache_path = os.path.join(out_dir, f"phase0_trajectories_{suffix}.npz")

    df = run_phase0(backend, K=30, T_gen=256, temperature=0.7,
                     block_sizes=(4, 8, 16), signal_choice="C",
                     trajectory_cache_path=cache_path)

    out_csv = os.path.join(out_dir, f"phase0_lm_trajectories_{suffix}.csv")
    df.to_csv(out_csv, index=False)
    print(f"\n  Saved: {out_csv}")

    print("\n" + "=" * 76)
    print("Phase 0 Evaluation")
    print("=" * 76)
    results = evaluate_phase0(df)
    results["stab_table"].to_csv(
        os.path.join(out_dir, "phase0_stability_table.csv"), index=False
    )

    print("\n" + "=" * 76)
    print("OVERALL")
    print("=" * 76)
    print(f"  P0-1 (each feature within stability bound at b=4): {'PASS' if results['P0_1_pass'] else 'FAIL'}")
    print(f"  P0-3 (stability stable/decreasing with b): {'PASS' if results['P0_3_pass'] else 'FAIL'}")
    print(f"  Saved: results/phase0_stability_table.csv")
    print(f"  Saved: results/phase0_lm_trajectories_{suffix}.csv")
    print(f"  Saved: results/phase0_trajectories_{suffix}.npz (cached for re-encoding without re-running LM)")


if __name__ == "__main__":
    main()
