"""
Phase D: Next-token KL divergence between base and Instruct.

Phase C Arm 2 found the misrep cases produce positional spikes in hidden-state
distance, not the distributed mid-layer elevation the framework predicted. The
spikes suggested constraint-installed token-level substitutions at specific
positions. This script tests that directly by measuring next-token prediction
divergence between base and Instruct at each response position.

Method:
  1. Use Phase C's generated Instruct responses (responses.json).
  2. Forward Instruct on (question + response), capture log-probs at each
     position, save to CPU memory.
  3. Free Instruct, load base.
  4. For each item: forward base, get log-probs, compute KL divergence and
     top-K analysis using both sets of log-probs, save results.

For each response token position, we compute:
  - KL(instruct || base): how much Instruct's prediction deviates from base
  - KL(base || instruct): same in reverse
  - Jensen-Shannon (symmetric)
  - Top-5 token predictions from each model
  - The actually-emitted token and each model's probability of it

Storage budget: we keep Instruct's full log-prob distributions in CPU RAM
during the run (~230MB for 6 items × ~150 tokens × 128256 vocab × fp16).
After computing KL, only summary results are saved to disk (small).

Hardware: RTX 5080 16GB VRAM, sequential model loading. Runtime ~5-10 min.

Usage:
    python compute_kl.py
    python compute_kl.py --phase-c-dir ../phase_c/activations
"""

import argparse
import gc
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


BASE_MODEL = "meta-llama/Llama-3.1-8B"
INSTRUCT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"


def load_model(model_id: str, hf_token: str | None = None):
    print(f"[load] {model_id}")
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
    print(f"[load] VRAM in use: {torch.cuda.memory_allocated() / 1e9:.2f}GB")
    return model, tokenizer


def free_model(model):
    del model
    gc.collect()
    torch.cuda.empty_cache()


def forward_get_logprobs(model, tokenizer, text: str):
    """Forward pass, return log-softmax over vocab at each position.

    Returns: (log_probs_fp16 of shape (n_tokens, vocab_size), input_ids array)
    """
    inputs = tokenizer(text, return_tensors="pt", add_special_tokens=True).to("cuda")
    with torch.no_grad():
        out = model(**inputs, return_dict=True)
    logits = out.logits[0]  # (n_tokens, vocab_size), bf16
    log_probs = torch.log_softmax(logits.float(), dim=-1)
    return log_probs.cpu().numpy().astype(np.float16), inputs.input_ids[0].cpu().numpy()


def compute_kl_summary(
    base_lp: np.ndarray,
    instr_lp: np.ndarray,
    ids: np.ndarray,
    response_start: int,
    tokenizer,
    role: str,
    question: str,
    response: str,
    K: int = 5,
):
    """Compute per-position KL and top-K substitution analysis for response tokens.

    Inputs are fp16 log-probs of shape (n_tokens, vocab_size).
    """
    base_lp = base_lp.astype(np.float32)
    instr_lp = instr_lp.astype(np.float32)

    instr_p = np.exp(instr_lp)
    base_p = np.exp(base_lp)

    # KL divergences per position (across full vocab)
    kl_instr_base = (instr_p * (instr_lp - base_lp)).sum(axis=-1)
    kl_base_instr = (base_p * (base_lp - instr_lp)).sum(axis=-1)

    # Symmetric: Jensen-Shannon
    m_p = (instr_p + base_p) / 2
    m_lp = np.log(m_p + 1e-12)
    js = 0.5 * (instr_p * (instr_lp - m_lp)).sum(-1) + 0.5 * (base_p * (base_lp - m_lp)).sum(-1)

    # Restrict to response token predictions:
    # logits[p] predicts token at position p+1
    # response tokens are at positions [response_start, ..., len(ids)-1]
    # so prediction logit positions are [response_start - 1, ..., len(ids) - 2]
    pred_positions = list(range(max(0, response_start - 1), len(ids) - 1))
    response_token_positions = [p + 1 for p in pred_positions]

    # Top-K analysis
    instr_top_k = np.argsort(-instr_p, axis=-1)[:, :K]
    base_top_k = np.argsort(-base_p, axis=-1)[:, :K]

    per_position = []
    for i, (pred_pos, resp_pos) in enumerate(zip(pred_positions, response_token_positions)):
        emitted_id = int(ids[resp_pos])
        emitted_token = tokenizer.decode([emitted_id])

        instr_top_ids = [int(x) for x in instr_top_k[pred_pos]]
        instr_top_probs = [float(instr_p[pred_pos, x]) for x in instr_top_ids]
        base_top_ids = [int(x) for x in base_top_k[pred_pos]]
        base_top_probs = [float(base_p[pred_pos, x]) for x in base_top_ids]

        per_position.append({
            "response_pos": i,
            "emitted_token": emitted_token,
            "emitted_id": emitted_id,
            "kl_instr_base": float(kl_instr_base[pred_pos]),
            "kl_base_instr": float(kl_base_instr[pred_pos]),
            "js": float(js[pred_pos]),
            "instr_prob_of_emitted": float(instr_p[pred_pos, emitted_id]),
            "base_prob_of_emitted": float(base_p[pred_pos, emitted_id]),
            "instr_top_tokens": [tokenizer.decode([x]) for x in instr_top_ids],
            "instr_top_probs": instr_top_probs,
            "base_top_tokens": [tokenizer.decode([x]) for x in base_top_ids],
            "base_top_probs": base_top_probs,
        })

    kls = [p["kl_instr_base"] for p in per_position]
    js_vals = [p["js"] for p in per_position]
    max_kl_idx = int(np.argmax(kls)) if kls else 0
    return {
        "role": role,
        "question": question,
        "response": response,
        "response_start": response_start,
        "n_response_tokens": len(per_position),
        "kl_by_position": kls,
        "js_by_position": js_vals,
        "max_kl": float(max(kls)) if kls else 0.0,
        "max_kl_pos": max_kl_idx,
        "mean_kl": float(np.mean(kls)) if kls else 0.0,
        "median_kl": float(np.median(kls)) if kls else 0.0,
        "per_position": per_position,
    }


def make_combined_input(question: str, response: str) -> str:
    return f"{question}\n\n{response}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase-c-dir", type=Path, default=Path("../phase_c/activations"))
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--hf-token", type=str, default=None)
    args = parser.parse_args()

    hf_token = args.hf_token or os.environ.get("HF_TOKEN")

    if not torch.cuda.is_available():
        print("ERROR: CUDA not available.")
        sys.exit(1)

    responses_path = args.phase_c_dir / "responses.json"
    response_starts_path = args.phase_c_dir / "response_starts.json"
    if not responses_path.exists() or not response_starts_path.exists():
        print(f"ERROR: required Phase C files not found in {args.phase_c_dir}")
        print("Run Phase C Arm 2 first: `python arm2_extract_generation.py`")
        sys.exit(1)

    responses = json.loads(responses_path.read_text(encoding="utf-8"))
    response_starts = json.loads(response_starts_path.read_text(encoding="utf-8"))

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # === Step 1: Load Instruct, get log-probs for all items ===
    print("\n=== Step 1: Forward Instruct on (q + response) ===")
    model, tokenizer = load_model(INSTRUCT_MODEL, hf_token=hf_token)

    instruct_logprobs = {}
    instruct_input_ids = {}
    try:
        for key, r in responses.items():
            text = make_combined_input(r["question"], r["response"])
            try:
                lp, ids = forward_get_logprobs(model, tokenizer, text)
                instruct_logprobs[key] = lp
                instruct_input_ids[key] = ids
                print(f"  [instruct] {key}: log-probs shape {lp.shape}")
            except torch.cuda.OutOfMemoryError:
                print(f"  [OOM] {key} — skipping")
                torch.cuda.empty_cache()
                continue
    finally:
        free_model(model)
        print(f"[free] VRAM after Instruct: {torch.cuda.memory_allocated() / 1e9:.2f}GB")

    # Memory check
    total_lp_mb = sum(lp.nbytes for lp in instruct_logprobs.values()) / 1e6
    print(f"\n[mem] Instruct log-probs in CPU RAM: {total_lp_mb:.0f} MB")

    # === Step 2: Load base, compute KL per item, save summary ===
    print("\n=== Step 2: Forward Base, compute KL ===")
    model, tokenizer = load_model(BASE_MODEL, hf_token=hf_token)

    results = {}
    try:
        for key, r in responses.items():
            if key not in instruct_logprobs:
                continue
            text = make_combined_input(r["question"], r["response"])
            try:
                base_lp, base_ids = forward_get_logprobs(model, tokenizer, text)
            except torch.cuda.OutOfMemoryError:
                print(f"  [OOM] {key} — skipping")
                torch.cuda.empty_cache()
                continue

            instr_lp = instruct_logprobs[key]
            instr_ids = instruct_input_ids[key]

            if not np.array_equal(base_ids, instr_ids):
                print(f"  [WARN] token ID mismatch on {key} — skipping")
                continue

            summary = compute_kl_summary(
                base_lp=base_lp,
                instr_lp=instr_lp,
                ids=base_ids,
                response_start=response_starts[key],
                tokenizer=tokenizer,
                role=r["role"],
                question=r["question"],
                response=r["response"],
            )
            results[key] = summary
            print(f"  [base + KL] {key}: max_KL={summary['max_kl']:.2f} at pos {summary['max_kl_pos']}, mean_KL={summary['mean_kl']:.2f}")
    finally:
        free_model(model)

    # Save
    out_path = args.output_dir / "kl_results.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved {out_path}")
    print(f"Next: python analyze_kl.py")


if __name__ == "__main__":
    main()
