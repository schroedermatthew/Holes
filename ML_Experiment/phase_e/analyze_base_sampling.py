"""
Phase E supplement analysis: does base produce misrep patterns under sampling?

Reads base_sampling_results.json and (if available) paraphrase_results.json,
checks misrep signals on each base sample, and produces a comparison report:

  - Per item: how often do misrep signals fire on base T=0.7 samples?
  - Per item: how often on Instruct T=0.7 samples (for comparison)?
  - Per item: do base format variants produce the same content patterns as
              base paraphrases, or does base also have format sensitivity?

Interpretation:
  - Base fire rate ≈ 0 across signals: misrep is introduced de novo at Stage 2.
  - Base fire rate >> 0: misrep is in base's distribution, Stage 2 amplifies.
  - Base format variants produce different content than base paraphrases:
      base also has format-conditional behavior, just less pronounced.

Usage:
    python analyze_base_sampling.py
"""

import argparse
import json
import sys
from pathlib import Path

# Import signal definitions from the main analyzer
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from analyze_paraphrase import SIGNALS, detect_signals


def count_signals_in_samples(samples: list, item_signals: dict) -> dict:
    """Returns {signal_name: count} for how many samples fire each signal."""
    counts = {sig: 0 for sig in item_signals}
    for s in samples:
        sigs = detect_signals(s, item_signals)
        for sig, fired in sigs.items():
            if fired:
                counts[sig] += 1
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    args = parser.parse_args()

    base_path = args.results_dir / "base_sampling_results.json"
    main_path = args.results_dir / "paraphrase_results.json"

    if not base_path.exists():
        print(f"ERROR: {base_path} not found.")
        print("Run `python base_sampling_test.py` first.")
        return

    base_data = json.loads(base_path.read_text(encoding="utf-8"))["base_extended"]
    main_data = None
    if main_path.exists():
        main_data = json.loads(main_path.read_text(encoding="utf-8"))

    out_path = args.results_dir / "base_vs_instruct_sampling.txt"
    lines = []
    lines.append("=" * 78)
    lines.append("Phase E supplement: Base sampling vs Instruct sampling")
    lines.append("=" * 78)
    lines.append("")
    lines.append("Question: do misrep signals (inverted tables, named exceptions,")
    lines.append("hedge framings) appear in base's distribution under stochastic")
    lines.append("sampling, or only after Stage 2 (Instruct) training?")
    lines.append("")

    for item_id, item_data in base_data.items():
        item_signals = SIGNALS.get(item_id, {})
        lines.append("")
        lines.append("#" * 78)
        lines.append(f"# {item_id}")
        lines.append("#" * 78)

        # Aggregate base samples
        all_base_samples = []
        for data in item_data["samples_T07"].values():
            all_base_samples.extend(data["samples"])
        base_counts = count_signals_in_samples(all_base_samples, item_signals)

        # Aggregate Instruct samples if available
        instr_counts = None
        all_instr_samples = []
        if main_data and "instruct" in main_data and item_id in main_data["instruct"]:
            for data in main_data["instruct"][item_id].get("samples_T07", {}).values():
                all_instr_samples.extend(data["samples"])
            instr_counts = count_signals_in_samples(all_instr_samples, item_signals)

        n_base = len(all_base_samples)
        n_instr = len(all_instr_samples)

        # Comparison table
        lines.append("")
        lines.append("--- Misrep signal firing rate at T=0.7 ---")
        if instr_counts is not None:
            lines.append(f"  Base samples: {n_base}    Instruct samples: {n_instr}")
            lines.append("")
            lines.append(f"  {'Signal':<35} {'Base':>10} {'Instruct':>12}  Direction")
            lines.append("  " + "-" * 70)
            for sig in item_signals:
                bc = base_counts[sig]
                ic = instr_counts[sig]
                if bc == 0 and ic == 0:
                    continue
                base_pct = 100 * bc / max(n_base, 1)
                instr_pct = 100 * ic / max(n_instr, 1)
                if instr_pct > base_pct + 20:
                    direction = "Stage 2 amplifies"
                elif base_pct > instr_pct + 20:
                    direction = "Stage 2 suppresses"
                elif bc == 0 and ic > 0:
                    direction = "Stage 2 introduces"
                elif ic == 0 and bc > 0:
                    direction = "Stage 2 removes"
                else:
                    direction = "similar"
                lines.append(f"  {sig:<35} {bc:>3}/{n_base:<3} ({base_pct:>3.0f}%) "
                             f"{ic:>3}/{n_instr:<3} ({instr_pct:>3.0f}%)  {direction}")
        else:
            lines.append(f"  Base samples: {n_base}")
            for sig, count in base_counts.items():
                if count > 0:
                    lines.append(f"    {sig:<35} {count}/{n_base}")

        # Per-paraphrase base sample previews
        lines.append("")
        lines.append("--- Base T=0.7 sample previews ---")
        for pk, data in item_data["samples_T07"].items():
            lines.append(f"\n  {pk} (q: {data['question'][:80]})")
            for i, sample in enumerate(data["samples"]):
                sigs = detect_signals(sample, item_signals)
                fired = [k for k, v in sigs.items() if v]
                preview = sample[:140].replace("\n", " ")
                fired_str = ", ".join(fired) if fired else "(no signals)"
                lines.append(f"    sample {i}: [{fired_str}]")
                lines.append(f"               {preview}{'...' if len(sample) > 140 else ''}")

        # Format variants on base
        if item_data.get("format_variants_T0"):
            lines.append("")
            lines.append("--- Base format variants at T=0 ---")
            for fk, fv in item_data["format_variants_T0"].items():
                sigs = detect_signals(fv["response"], item_signals)
                fired = [k for k, v in sigs.items() if v]
                preview = fv["response"][:200].replace("\n", " ")
                fired_str = ", ".join(fired) if fired else "(no signals)"
                lines.append(f"\n  [{fk}] Q: {fv['question']}")
                lines.append(f"        A: {preview}{'...' if len(fv['response']) > 200 else ''}")
                lines.append(f"        fired: {fired_str}")

        # Item-level interpretation
        lines.append("")
        lines.append("--- Stage attribution for this item ---")
        if instr_counts is not None:
            # Count signals that fire only on Instruct
            stage2_only = [s for s in item_signals if instr_counts[s] > 0 and base_counts[s] == 0]
            both = [s for s in item_signals if instr_counts[s] > 0 and base_counts[s] > 0]
            stage1_amp = [s for s in both if instr_counts[s] / max(n_instr, 1) > 2 * base_counts[s] / max(n_base, 1)]

            if stage2_only:
                lines.append(f"  Signals introduced de novo at Stage 2: {stage2_only}")
            if stage1_amp:
                lines.append(f"  Signals present at Stage 1, amplified at Stage 2: {stage1_amp}")
            base_only = [s for s in item_signals if base_counts[s] > 0 and instr_counts[s] == 0]
            if base_only:
                lines.append(f"  Signals present at Stage 1 only (suppressed at Stage 2): {base_only}")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
