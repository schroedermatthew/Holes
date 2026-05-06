"""
Phase 1 - LM trajectory generation for the orthogonality test.

Per FN-PHANTOM-002 Section 8.1.

Generates K continuations per (topic, paraphrase) for each of the 30
topics in 5 paraphrases (150 pairs total). Computes Layer 1 ASD features
on Choice C signal (per-token leakage rho_i), plus mean_rho per
continuation as the abelian baseline.

K is configurable. Defaults to 30 (matches Phase 0; gives ~30 GPU-hours
on RTX 5080). Bump to 50 for tighter CIs at ~50 GPU-hours.

Sequential model loading via generate_batch (load Instruct -> generate +
score everything; free; load base -> score everything; free) -- needed
for 16GB VRAM cards.

Trajectories are cached as .npz; re-running with the same parameters
loads from cache instead of re-generating. Useful when iterating on
encoder/feature definitions.

The orthogonality analysis is in phase1_analysis.py and runs anywhere
on the resulting CSV in ~30 seconds.
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import numpy as np
import pandas as pd
from src.asd_encoder import encode_and_walk
from src.asd_features import all_features, get_iid_null
from src import llm_trajectory as lt
from tests.phase1_topics import PHASE_1_TOPICS

import time


# ---- Operational defaults (override in main() if needed) ----
DEFAULT_K = 30           # seeds per (topic, paraphrase). 30 matches Phase 0.
DEFAULT_T_GEN = 256
DEFAULT_TEMPERATURE = 0.7
DEFAULT_BLOCK_SIZE = 16  # Phase 0 b=16 was the operational recommendation
DEFAULT_SIGNAL = "C"     # Choice C: per-token leakage rho_i
DEFAULT_MAX_DEPTH = 6


def build_specs(K, T_gen, temperature):
    """Build the full list of generation specs for two-pass batch."""
    specs = []
    for topic_id, topic_data in PHASE_1_TOPICS.items():
        category = topic_data["category"]
        for p_idx, paraphrase in enumerate(topic_data["paraphrases"]):
            for seed in range(K):
                specs.append({
                    "prompt": paraphrase,
                    "seed": seed,
                    "T": T_gen,
                    "temperature": temperature,
                    "meta_extra": {
                        "topic": topic_id,
                        "category": category,
                        "paraphrase_idx": p_idx,
                    },
                })
    return specs


def encode_and_extract(traj, block_size, null, signal="C",
                       max_depth=DEFAULT_MAX_DEPTH):
    sig = traj.signal(signal)
    if len(sig) < block_size:
        return {}
    rng = np.random.default_rng(traj.meta.get("seed", 0) + 7_000_000)
    ep = encode_and_walk(sig, block_size=block_size,
                          max_depth_tracked=max_depth, rng=rng)
    feats = all_features(ep, null)
    feats["mean_rho"] = float(np.mean(traj.rho))
    feats["std_rho"] = float(np.std(traj.rho))
    feats["mean_surp_inst"] = float(np.mean(traj.surprisal_inst))
    feats["mean_surp_base"] = float(np.mean(traj.surprisal_base))
    feats["T_actual"] = int(len(sig))
    return feats


def _save_trajectories(trajectories, specs, path):
    """Persist trajectories as numpy arrays in a single .npz."""
    payload = {}
    for i, traj in enumerate(trajectories):
        if traj is None:
            continue
        payload[f"surp_inst_{i}"] = traj.surprisal_inst
        payload[f"surp_base_{i}"] = traj.surprisal_base
        payload[f"rho_{i}"] = traj.rho
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
    with open(path + ".meta.json", "r", encoding="utf-8") as f:
        meta_list = json.load(f)
    arr = np.load(path)
    trajectories = []
    for m in meta_list:
        if m is None:
            trajectories.append(None)
            continue
        i = m["i"]
        trajectories.append(lt.Trajectory(
            prompt=m["prompt"],
            generation=m["generation"],
            surprisal_inst=arr[f"surp_inst_{i}"],
            surprisal_base=arr[f"surp_base_{i}"],
            rho=arr[f"rho_{i}"],
            generating_model=m["generating_model"],
            meta=m["meta"],
        ))
    return trajectories


def run_phase1(backend, output_csv_path, trajectory_cache_path,
                K=DEFAULT_K,
                T_gen=DEFAULT_T_GEN,
                temperature=DEFAULT_TEMPERATURE,
                block_size=DEFAULT_BLOCK_SIZE,
                signal=DEFAULT_SIGNAL,
                max_depth=DEFAULT_MAX_DEPTH):
    """
    Run Phase 1 generation + feature extraction.

    1. If trajectory_cache_path exists: load it, skip the LM passes.
    2. Otherwise: run two-pass batch via backend.generate_batch, then
       save to cache.
    3. Encode all trajectories at the operational block_size; write CSV.
    """
    n_topics = len(PHASE_1_TOPICS)
    n_pairs = sum(len(d["paraphrases"]) for d in PHASE_1_TOPICS.values())
    n_total = n_pairs * K
    print()
    print(f"Phase 1 setup:")
    print(f"  Backend: {type(backend).__name__}")
    print(f"  Topics: {n_topics} (10 control + 10 mid + 10 shaped)")
    print(f"  Pairs (topic, paraphrase): {n_pairs}")
    print(f"  K = {K} seeds per pair")
    print(f"  T_gen = {T_gen}, temperature = {temperature}")
    print(f"  Operational block_size = {block_size}, signal = Choice {signal}")
    print(f"  Total trajectories to generate: {n_total}")
    print(f"  Cache path: {trajectory_cache_path}")
    print()

    # ---- Load or generate trajectories ----
    trajectories = None
    if trajectory_cache_path and os.path.exists(trajectory_cache_path):
        print(f"Loading cached trajectories from {trajectory_cache_path}")
        trajectories = _load_trajectories(trajectory_cache_path)
        n_loaded = sum(1 for t in trajectories if t is not None)
        print(f"  loaded {n_loaded} trajectories from cache (skipping LM passes)")

    if trajectories is None:
        specs = build_specs(K, T_gen, temperature)
        if len(specs) != n_total:
            print(f"  WARNING: build_specs gave {len(specs)} specs but expected {n_total}")
        trajectories = backend.generate_batch(specs, verbose_every=25)
        if trajectory_cache_path:
            print(f"\n  Saving trajectories to {trajectory_cache_path} ...")
            _save_trajectories(trajectories, specs, trajectory_cache_path)
            print(f"  saved.")

    n_total_resp = len(trajectories)
    trajectories = [t for t in trajectories if t is not None]
    n_ok = len(trajectories)
    if n_ok < n_total_resp:
        print(f"  WARNING: {n_total_resp - n_ok} trajectories failed (OOM or empty); proceeding with {n_ok}")

    # ---- Encode and extract features ----
    print(f"\n=== Encoding {n_ok} trajectories at block_size={block_size}, signal=Choice {signal} ===")
    null = get_iid_null(T_gen, block_size=block_size)
    print(f"  IID null (b={block_size}): cancel_rate = {null['cancel_rate']:.4f} +- {null['cancel_rate_std']:.4f}")

    rows = []
    for traj in trajectories:
        topic = traj.meta.get("topic", "?")
        category = traj.meta.get("category", "?")
        p_idx = traj.meta.get("paraphrase_idx", -1)
        seed = traj.meta.get("seed", -1)
        feats = encode_and_extract(traj, block_size=block_size, null=null,
                                     signal=signal, max_depth=max_depth)
        if not feats:
            continue
        feats["topic"] = topic
        feats["category"] = category
        feats["paraphrase_idx"] = p_idx
        feats["seed"] = seed
        feats["block_size"] = block_size
        feats["signal"] = signal
        rows.append(feats)

    df = pd.DataFrame(rows)
    df.to_csv(output_csv_path, index=False)
    print(f"  wrote {len(df)} rows -> {output_csv_path}")
    return df


def main():
    print("=" * 76)
    print("Phase 1 - LM trajectories for orthogonality test")
    print("=" * 76)

    # ---- Backend selection ------------------------------------------
    # Sandbox / no GPU:
    # backend = lt.MockLMBackend()

    # Real Llama on user GPU box (RTX 5080 16GB) -- sequential loading:
    backend = lt.TransformersBackend(
        inst_model_name="meta-llama/Llama-3.1-8B-Instruct",
        base_model_name="meta-llama/Llama-3.1-8B",
        device="cuda",
    )
    # ----------------------------------------------------------------

    out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)
    suffix = "mock" if isinstance(backend, lt.MockLMBackend) else "llama"
    K = 10 if isinstance(backend, lt.MockLMBackend) else DEFAULT_K
    output_csv = os.path.join(out_dir, f"phase1_features_{suffix}.csv")
    cache = os.path.join(out_dir, f"phase1_trajectories_{suffix}.npz")

    df = run_phase1(backend, output_csv, cache, K=K)

    print()
    print("=" * 76)
    print("Done.")
    print("=" * 76)
    print(f"  Trajectory cache: {cache}")
    print(f"  Feature CSV:      {output_csv}")
    print()
    print(f"  Next: python tests/phase1_analysis.py {output_csv}")


if __name__ == "__main__":
    main()
