"""Phase 0.0 - validate ASD encoder on synthetic processes (v2 features)."""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from src.asd_encoder import encode_and_walk
from src.asd_features import all_features, get_iid_null
from src import synthetic_processes as sp


def run_one_seed(signal, null, block_size=4, max_depth=6, seed=0):
    rng = np.random.default_rng(seed + 1_000_000)
    ep = encode_and_walk(signal, block_size=block_size,
                          max_depth_tracked=max_depth, rng=rng)
    return all_features(ep, null)


def run_process(name, gen_fn, null, n_seeds=30, N=4096, block_size=4):
    rows = []
    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        signal = gen_fn(N, rng)
        feats = run_one_seed(signal, null, block_size=block_size, seed=seed)
        feats["process"] = name
        feats["seed"] = seed
        rows.append(feats)
    return pd.DataFrame(rows)


def run_validation_at_block_size(block_size, N=4096):
    print()
    print("=" * 76)
    print(f"  Block size = {block_size}, N = {N}")
    print("=" * 76)
    print(f"  Calibrating IID null (50 seeds)...")
    null = get_iid_null(N, block_size=block_size)
    print(f"    cancel_rate    = {null['cancel_rate']:.4f} +- {null['cancel_rate_std']:.4f}")
    print(f"    mean_depth     = {null['mean_depth']:.4f} +- {null['mean_depth_std']:.4f}")
    print(f"    d2_visit_rate  = {null['d2_visit_rate']:.4f} +- {null['d2_visit_rate_std']:.4f}")

    process_specs = [
        ("IID_Gaussian", lambda N, r: sp.iid_gaussian(N, r)),
        ("AR1_rho_0.3", lambda N, r: sp.ar1(N, 0.3, r)),
        ("AR1_rho_0.5", lambda N, r: sp.ar1(N, 0.5, r)),
        ("AR1_rho_0.7", lambda N, r: sp.ar1(N, 0.7, r)),
        ("AR1_rho_0.9", lambda N, r: sp.ar1(N, 0.9, r)),
        ("ARCH1_a07", lambda N, r: sp.arch1(N, 0.1, 0.7, r)),
        ("ARCH1_a09", lambda N, r: sp.arch1(N, 0.1, 0.9, r)),
        ("FGN_H_0.6", lambda N, r: sp.fgn(min(N, 1000), 0.6, r)),
        ("FGN_H_0.8", lambda N, r: sp.fgn(min(N, 1000), 0.8, r)),
        ("ShTex_rho_0.5", lambda N, r: sp.shared_texture_lognormal(N, 0.5, r)),
        ("ShTex_rho_0.95", lambda N, r: sp.shared_texture_lognormal(N, 0.95, r)),
    ]

    all_dfs = []
    for name, gen_fn in process_specs:
        N_proc = 1000 if name.startswith("FGN") else N
        n_seeds = 30 if not name.startswith("FGN") else 15
        df = run_process(name, gen_fn, null, n_seeds=n_seeds, N=N_proc,
                          block_size=block_size)
        all_dfs.append(df)

    full = pd.concat(all_dfs, ignore_index=True)
    return full, null


def print_summary(full, label=""):
    cols = ["drift", "cancel_rate", "mean_depth_excess", "timing_cv",
            "isolated_frac", "d2_excess", "r_plus"]
    process_order = [
        "IID_Gaussian",
        "AR1_rho_0.3", "AR1_rho_0.5", "AR1_rho_0.7", "AR1_rho_0.9",
        "ARCH1_a07", "ARCH1_a09",
        "FGN_H_0.6", "FGN_H_0.8",
        "ShTex_rho_0.5", "ShTex_rho_0.95",
    ]
    sm = full.groupby("process")[cols].mean().reindex(process_order)
    sd = full.groupby("process")[cols].std().reindex(process_order)

    print()
    print(f"Means {label}:")
    print(f"{'process':18s}", end="")
    for c in cols:
        print(f"{c:>14s}", end="")
    print()
    print("-" * (18 + 14 * len(cols)))
    for proc in process_order:
        if proc not in sm.index:
            continue
        print(f"{proc:18s}", end="")
        for c in cols:
            mean = sm.loc[proc, c]
            std = sd.loc[proc, c]
            print(f"  {mean:6.2f}+-{std:5.2f}", end="")
        print()
    return sm, sd


def validation_checks(sm, sd, label):
    print()
    print(f"VALIDATION CHECKS ({label}):")
    checks = []

    iid_drift = sm.loc["IID_Gaussian", "drift"]
    pass1 = abs(iid_drift) < 1.0
    checks.append((f"|IID drift z| < 1", pass1, f"observed {iid_drift:.3f}"))

    ar9_drift = sm.loc["AR1_rho_0.9", "drift"]
    pass2 = ar9_drift < -2.0
    checks.append((f"AR1 0.9 drift z < -2", pass2, f"observed {ar9_drift:.3f}"))

    drifts_ar1 = [sm.loc[f"AR1_rho_{rho}", "drift"]
                   for rho in ["0.3", "0.5", "0.7", "0.9"]]
    pass3 = drifts_ar1[3] < drifts_ar1[0] - 1.0
    checks.append((f"AR1 0.9 drift much less than AR1 0.3 drift", pass3,
                   f"values {[round(d, 2) for d in drifts_ar1]}"))

    iid_cv = sm.loc["IID_Gaussian", "timing_cv"]
    arch_cv = sm.loc["ARCH1_a09", "timing_cv"]
    pass4 = arch_cv > iid_cv + 0.05
    checks.append((f"ARCH a=0.9 timing_cv > IID + 0.05", pass4,
                   f"ARCH = {arch_cv:.3f}, IID = {iid_cv:.3f}"))

    ar9_cv = sm.loc["AR1_rho_0.9", "timing_cv"]
    pass5 = ar9_cv > iid_cv + 0.05
    checks.append((f"AR1 0.9 timing_cv > IID + 0.05", pass5,
                   f"AR1 = {ar9_cv:.3f}, IID = {iid_cv:.3f}"))

    sht_drift = sm.loc["ShTex_rho_0.95", "drift"]
    pass6 = abs(sht_drift) > 2.0
    checks.append((f"|ShTex 0.95 drift z| > 2", pass6,
                   f"observed {sht_drift:.3f}"))

    ar9_drift_v = sm.loc["AR1_rho_0.9", "drift"]
    arch_drift_v = sm.loc["ARCH1_a09", "drift"]
    ar9_drift_std = sd.loc["AR1_rho_0.9", "drift"]
    arch_drift_std = sd.loc["ARCH1_a09", "drift"]
    pass7 = abs(ar9_drift_v - arch_drift_v) > 2 * (ar9_drift_std + arch_drift_std)
    checks.append((f"AR1 0.9 and ARCH separable in drift",
                   pass7, f"AR1={ar9_drift_v:.2f}+-{ar9_drift_std:.2f}, ARCH={arch_drift_v:.2f}+-{arch_drift_std:.2f}"))

    print()
    n_pass = sum(1 for _, p, _ in checks if p)
    n_total = len(checks)
    for desc, p, detail in checks:
        flag = "PASS" if p else "FAIL"
        print(f"  [{flag}] {desc}")
        if detail:
            print(f"         {detail}")
    print()
    print(f"  Result: {n_pass} / {n_total} checks passed")
    return n_pass, n_total


def main():
    print("=" * 76)
    print("Phase 0.0 - Validate ASD encoder on synthetic processes (v2)")
    print("=" * 76)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)

    full4, null4 = run_validation_at_block_size(block_size=4, N=4096)
    sm4, sd4 = print_summary(full4, label="(b=4)")
    p4, t4 = validation_checks(sm4, sd4, "block_size=4")
    full4.to_csv(os.path.join(out_dir, "synth_b4.csv"), index=False)

    full16, null16 = run_validation_at_block_size(block_size=16, N=4096)
    sm16, sd16 = print_summary(full16, label="(b=16)")
    p16, t16 = validation_checks(sm16, sd16, "block_size=16")
    full16.to_csv(os.path.join(out_dir, "synth_b16.csv"), index=False)

    print()
    print("=" * 76)
    print("AGGREGATE")
    print("=" * 76)
    print(f"  block_size=4:  {p4}/{t4} checks passed")
    print(f"  block_size=16: {p16}/{t16} checks passed")

    return (p4 + p16) >= (t4 + t16) * 0.7


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
