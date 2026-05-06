"""
Phase E supplement: Base T=0 paraphrases + sampling + format variants.

Originally this script only did sampling and format variants. Now it also
runs the T=0 paraphrases that paraphrase_test.py was supposed to run on
base — separated into its own process to avoid VRAM contamination from
having both Instruct and base loaded in sequence in the same process.

What this runs on base:
  1. T=0 paraphrases (5 per item) — the basic reference for what unconstrained
     substrate produces. Was originally in paraphrase_test.py but moved here.
  2. T=0.7 sampling on first N_SAMPLE_PARAPHRASES paraphrases (5 samples each)
     — tests whether base produces misrep patterns under stochastic sampling.
  3. Format variants at T=0 — tests whether base also has format sensitivity.

Reads existing paraphrase_results.json (containing Instruct data from the
partial save) and merges base data into it.

Run AFTER paraphrase_test.py has at least completed its Instruct phase.
Verify by checking that results/paraphrase_results.json contains the
"instruct" key with all three items.

Runtime: ~10-15 min on RTX 5080 in a fresh process.

Usage:
    python base_sampling_test.py
    python base_sampling_test.py --no-formats        # skip format variants
    python base_sampling_test.py --no-sampling       # skip T=0.7 sampling
    python base_sampling_test.py --only-paraphrases  # only T=0 paraphrases (~3 min)
"""

import argparse
import json
import os
import sys
from pathlib import Path

import torch

# Import shared specs and helpers from the main test script
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from paraphrase_test import (
    TEST_BATTERY,
    BASE_MODEL,
    N_SAMPLES_PER_PARA,
    N_SAMPLE_PARAPHRASES,
    MAX_NEW_TOKENS,
    format_prompt_base,
    load_model,
    free_model,
    generate_one,
)


def run_base_full(
    model,
    tokenizer,
    include_paraphrases_T0: bool = True,
    include_sampling: bool = True,
    include_formats: bool = True,
) -> dict:
    """Run all base conditions on a single model load."""
    results = {}
    for item_id, battery in TEST_BATTERY.items():
        print(f"\n=== Base: {item_id} ===")
        results[item_id] = {
            "paraphrases_T0": {},
            "samples_T07": {},
            "format_variants_T0": {},
        }

        # T=0 paraphrases
        if include_paraphrases_T0:
            for i, q in enumerate(battery["paraphrases"]):
                prompt = format_prompt_base(q)
                response = generate_one(model, tokenizer, prompt, temperature=0.0)
                results[item_id]["paraphrases_T0"][f"p{i}"] = {"question": q, "response": response}
                preview = response[:90].replace("\n", " ")
                print(f"  [p{i}] T=0: {preview}...")

        # T=0.7 sampling on first N paraphrases (matches Instruct setup)
        if include_sampling:
            for i, q in enumerate(battery["paraphrases"][:N_SAMPLE_PARAPHRASES]):
                prompt = format_prompt_base(q)
                samples = []
                for s in range(N_SAMPLES_PER_PARA):
                    response = generate_one(
                        model, tokenizer, prompt,
                        temperature=0.7,
                        seed=42 + s,
                    )
                    samples.append(response)
                results[item_id]["samples_T07"][f"p{i}"] = {
                    "question": q,
                    "samples": samples,
                }
                print(f"  [p{i}] T=0.7 ×{N_SAMPLES_PER_PARA} done")

        # Format variants at T=0
        if include_formats:
            for i, q in enumerate(battery["format_variants"]):
                prompt = format_prompt_base(q)
                response = generate_one(model, tokenizer, prompt, temperature=0.0)
                results[item_id]["format_variants_T0"][f"f{i}"] = {
                    "question": q,
                    "response": response,
                }
                preview = response[:80].replace("\n", " ")
                print(f"  [f{i}] {preview}...")

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--hf-token", type=str, default=None)
    parser.add_argument("--no-formats", action="store_true",
                        help="Skip format variants on base")
    parser.add_argument("--no-sampling", action="store_true",
                        help="Skip T=0.7 sampling on base")
    parser.add_argument("--only-paraphrases", action="store_true",
                        help="Only run T=0 paraphrases (skip sampling and formats)")
    args = parser.parse_args()

    hf_token = args.hf_token or os.environ.get("HF_TOKEN")

    if not torch.cuda.is_available():
        print("ERROR: CUDA not available.")
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    main_path = args.output_dir / "paraphrase_results.json"
    supplement_path = args.output_dir / "base_sampling_results.json"

    include_paraphrases = True
    include_sampling = not args.no_sampling and not args.only_paraphrases
    include_formats = not args.no_formats and not args.only_paraphrases

    print("=" * 78)
    print("Phase E base run (T=0 paraphrases + sampling + formats)")
    print("=" * 78)
    print(f"T=0 paraphrases: {include_paraphrases}")
    print(f"T=0.7 sampling:  {include_sampling}")
    print(f"Format variants: {include_formats}")

    # Load base in a fresh process — no cross-contamination from Instruct
    model, tokenizer = load_model(BASE_MODEL, hf_token=hf_token)
    try:
        results = run_base_full(
            model, tokenizer,
            include_paraphrases_T0=include_paraphrases,
            include_sampling=include_sampling,
            include_formats=include_formats,
        )
    finally:
        free_model(model)

    # === Merge into paraphrase_results.json ===
    if main_path.exists():
        existing = json.loads(main_path.read_text(encoding="utf-8"))
        if "base" not in existing:
            existing["base"] = {}
        for item_id, item_results in results.items():
            existing.setdefault("base", {}).setdefault(item_id, {})
            # Only put paraphrases_T0 in main file (matches original schema)
            if item_results.get("paraphrases_T0"):
                existing["base"][item_id]["paraphrases_T0"] = item_results["paraphrases_T0"]
        main_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n[save] merged base T=0 paraphrases into {main_path}")
    else:
        # Standalone: paraphrase_results.json doesn't exist yet
        out_data = {"base": {item_id: {"paraphrases_T0": r.get("paraphrases_T0", {})}
                             for item_id, r in results.items()}}
        main_path.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n[save] {main_path} (no existing Instruct data found)")

    # === Save sampling + formats to supplement file ===
    supplement_data = {
        "base_extended": {
            item_id: {
                "samples_T07": r.get("samples_T07", {}),
                "format_variants_T0": r.get("format_variants_T0", {}),
            }
            for item_id, r in results.items()
        },
        "config": {
            "n_sample_paraphrases": N_SAMPLE_PARAPHRASES,
            "n_samples_per_para": N_SAMPLES_PER_PARA,
            "max_new_tokens": MAX_NEW_TOKENS,
            "base_model": BASE_MODEL,
        },
    }
    supplement_path.write_text(json.dumps(supplement_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[save] {supplement_path}")
    print("\nNext: python analyze_paraphrase.py")
    print("      python analyze_base_sampling.py")


if __name__ == "__main__":
    main()

