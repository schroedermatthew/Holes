"""
Phase B: Layer-wise activation extraction.

Loads Llama-3.1-8B base and Instruct sequentially, runs forward passes on the
target (item, level) pairs from targets.json, captures the residual stream
at every layer at the final prompt token, saves as compressed numpy arrays.

Hardware target: RTX 5080 16GB VRAM, 64GB system RAM, Windows 11.
Runtime: ~5-15 minutes total assuming model weights are cached from Phase A.

Usage:
    python extract_activations.py
    python extract_activations.py --only base
    python extract_activations.py --only instruct
    python extract_activations.py --test-cases ../phase_a/test_cases.json --targets targets.json
"""

import argparse
import gc
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


BASE_MODEL = "meta-llama/Llama-3.1-8B"
INSTRUCT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"


def format_prompt_base(question: str) -> str:
    """Same prompt format as Phase A for comparability."""
    return f"Question: {question}\nAnswer:"


def format_prompt_instruct(tokenizer, question: str) -> str:
    """Llama-3 chat template, same as Phase A."""
    messages = [{"role": "user", "content": question}]
    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )


def load_model(model_id: str, hf_token: str | None = None):
    print(f"\n[load] {model_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="cuda",
        token=hf_token,
        low_cpu_mem_usage=True,
    )
    model.eval()

    n_params = sum(p.numel() for p in model.parameters()) / 1e9
    vram_gb = torch.cuda.memory_allocated() / 1e9
    print(f"[load] loaded; {n_params:.2f}B params, {vram_gb:.2f}GB VRAM in use")
    return model, tokenizer


def free_model(model):
    del model
    gc.collect()
    torch.cuda.empty_cache()
    print(f"[free] VRAM after cleanup: {torch.cuda.memory_allocated() / 1e9:.2f}GB")


def extract_one(model, tokenizer, prompt: str) -> np.ndarray:
    """
    Run forward pass and return residual stream at every layer, at final prompt token.

    Returns array of shape (num_layers + 1, hidden_dim), float32.
    Index 0 is the post-embedding hidden state; index L is the output of layer L.
    """
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    final_pos = inputs["input_ids"].shape[1] - 1  # index of last input token

    with torch.no_grad():
        outputs = model(
            **inputs,
            output_hidden_states=True,
            return_dict=True,
        )

    # outputs.hidden_states is a tuple of length (num_layers + 1)
    # each tensor has shape (batch=1, seq_len, hidden_dim)
    # Grab the final-position vector from each layer
    activations = torch.stack(
        [h[0, final_pos, :].float().cpu() for h in outputs.hidden_states],
        dim=0,
    )
    return activations.numpy()


def extract_for_model(
    model_id: str,
    variant_name: str,
    targets: list,
    cases_by_id: dict,
    output_dir: Path,
    hf_token: str | None = None,
):
    """Run all targets through one model variant, save activations."""
    out_path = output_dir / f"activations_{variant_name}.npz"

    # Resume support
    existing = {}
    if out_path.exists():
        try:
            data = np.load(out_path)
            existing = {k: data[k] for k in data.files}
            print(f"[resume] {variant_name}: {len(existing)} entries already saved")
        except Exception as e:
            print(f"[resume] {variant_name}: existing file unreadable ({e}), starting fresh")
            existing = {}

    # Determine which targets still need processing
    remaining = []
    for t in targets:
        key = f"{t['item_id']}_L{t['level']}"
        if key not in existing:
            remaining.append((key, t))

    if not remaining:
        print(f"[skip] {variant_name}: all {len(targets)} targets already done")
        return out_path

    model, tokenizer = load_model(model_id, hf_token=hf_token)

    try:
        activations = dict(existing)  # start from any existing
        for i, (key, target) in enumerate(remaining, 1):
            item = cases_by_id[target["item_id"]]
            qdata = next(q for q in item["questions"] if q["level"] == target["level"])
            question = qdata["question"]

            if variant_name == "base":
                prompt = format_prompt_base(question)
            else:
                prompt = format_prompt_instruct(tokenizer, question)

            try:
                acts = extract_one(model, tokenizer, prompt)
                activations[key] = acts
                print(f"  [{variant_name}] {i}/{len(remaining)}: {key}  shape={acts.shape}")
            except torch.cuda.OutOfMemoryError:
                print(f"  [OOM] {key} — skipping")
                torch.cuda.empty_cache()
                continue

            # Save incrementally (every 5 entries to limit overhead)
            if i % 5 == 0:
                np.savez_compressed(out_path, **activations)

        # Final save
        np.savez_compressed(out_path, **activations)
        print(f"[done] {variant_name}: {len(activations)} entries saved to {out_path}")
    finally:
        free_model(model)

    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--targets", type=Path, default=Path("targets.json"))
    parser.add_argument("--test-cases", type=Path, default=Path("../phase_a/test_cases.json"),
                        help="Phase A test_cases.json (the source of truth for question text)")
    parser.add_argument("--output-dir", type=Path, default=Path("activations"))
    parser.add_argument("--hf-token", type=str, default=None)
    parser.add_argument("--only", choices=["base", "instruct"], default=None)
    args = parser.parse_args()

    hf_token = args.hf_token or os.environ.get("HF_TOKEN")

    if not args.targets.exists():
        print(f"ERROR: targets file not found: {args.targets}")
        sys.exit(1)
    if not args.test_cases.exists():
        print(f"ERROR: test cases file not found: {args.test_cases}")
        print("If your phase_a directory is elsewhere, pass --test-cases <path>")
        sys.exit(1)

    if not torch.cuda.is_available():
        print("ERROR: CUDA not available.")
        sys.exit(1)

    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"Total VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")

    targets_data = json.loads(args.targets.read_text(encoding="utf-8"))
    targets = targets_data["targets"]
    cases_data = json.loads(args.test_cases.read_text(encoding="utf-8"))
    cases_by_id = {item["id"]: item for item in cases_data["items"]}

    # Verify all target items exist in test cases
    for t in targets:
        if t["item_id"] not in cases_by_id:
            print(f"ERROR: target item {t['item_id']} not found in test cases")
            sys.exit(1)

    print(f"Loaded {len(targets)} targets across {len(set(t['item_id'] for t in targets))} items")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.only != "instruct":
        extract_for_model(BASE_MODEL, "base", targets, cases_by_id, args.output_dir, hf_token=hf_token)

    if args.only != "base":
        extract_for_model(INSTRUCT_MODEL, "instruct", targets, cases_by_id, args.output_dir, hf_token=hf_token)

    print("\nPhase B activation extraction complete.")
    print(f"Activations saved to {args.output_dir.resolve()}/")
    print("Next: `python analyze_activations.py`")


if __name__ == "__main__":
    main()
