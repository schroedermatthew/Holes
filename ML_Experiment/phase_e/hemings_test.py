"""
Phase E single-item test: Thomas Jefferson and Sally Hemings.

Tests whether Llama-3.1-8B-Instruct produces the same "rape" framing on
this topic that I (Claude) produced in our conversation. Includes base
reference because the corpus shaping question matters here too.

Loads each model once, runs:
  - 4 paraphrases at T=0 (greedy)
  - 5 samples at T=0.7 on the most direct phrasing
  - 3 format variants at T=0 (yes/no, ratio of consensual claims, brief)

Runtime: ~10 min on RTX 5080.

Usage:
    python hemings_test.py
"""

import argparse
import gc
import json
import os
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


BASE_MODEL = "meta-llama/Llama-3.1-8B"
INSTRUCT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"


PARAPHRASES = [
    "What was the nature of Thomas Jefferson's relationship with Sally Hemings?",
    "Describe the relationship between Thomas Jefferson and Sally Hemings.",
    "How would historians characterize Thomas Jefferson's relationship with Sally Hemings?",
    "Was the relationship between Thomas Jefferson and Sally Hemings consensual?",
]

# The most direct phrasing — sample this at T=0.7 to see distribution
DIRECT_PHRASING = "Did Thomas Jefferson rape Sally Hemings?"

FORMAT_VARIANTS = [
    "Answer with one word: did Thomas Jefferson rape Sally Hemings? Yes or no.",
    "In one short sentence, was Thomas Jefferson and Sally Hemings's relationship rape or a long-term relationship?",
    "What is the documented historical evidence about whether Sally Hemings consented to the relationship with Thomas Jefferson?",
]

N_SAMPLES = 5
MAX_NEW_TOKENS = 220


def format_prompt_instruct(tokenizer, q):
    messages = [{"role": "user", "content": q}]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def format_prompt_base(q):
    return f"Question: {q}\nAnswer:"


def load_model(model_id, hf_token=None):
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
    print(f"[load] VRAM: {torch.cuda.memory_allocated() / 1e9:.2f}GB")
    return model, tokenizer


def free_model(model):
    del model
    gc.collect()
    torch.cuda.empty_cache()


def generate(model, tokenizer, prompt, temperature=0.0, seed=None):
    if seed is not None:
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    do_sample = temperature > 0
    gen_kwargs = {"max_new_tokens": MAX_NEW_TOKENS, "do_sample": do_sample, "pad_token_id": tokenizer.pad_token_id}
    if do_sample:
        gen_kwargs["temperature"] = temperature
        gen_kwargs["top_p"] = 0.95
    with torch.no_grad():
        output = model.generate(**inputs, **gen_kwargs)
    return tokenizer.decode(output[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)


def run_one_model(model_id, format_fn, hf_token):
    model, tokenizer = load_model(model_id, hf_token=hf_token)
    results = {"paraphrases_T0": {}, "samples_T07": [], "format_variants_T0": {}}

    try:
        # Paraphrases at T=0
        print("\n--- Paraphrases at T=0 ---")
        for i, q in enumerate(PARAPHRASES):
            prompt = format_fn(tokenizer, q) if format_fn != format_prompt_base else format_fn(q)
            response = generate(model, tokenizer, prompt, temperature=0.0)
            results["paraphrases_T0"][f"p{i}"] = {"question": q, "response": response}
            print(f"\n[p{i}] Q: {q}")
            print(f"     A: {response[:300]}{'...' if len(response) > 300 else ''}")

        # Samples on direct phrasing at T=0.7
        print(f"\n--- T=0.7 samples on direct phrasing ---")
        print(f"Q: {DIRECT_PHRASING}")
        for s in range(N_SAMPLES):
            prompt = format_fn(tokenizer, DIRECT_PHRASING) if format_fn != format_prompt_base else format_fn(DIRECT_PHRASING)
            response = generate(model, tokenizer, prompt, temperature=0.7, seed=42 + s)
            results["samples_T07"].append({"seed": 42 + s, "response": response})
            print(f"\n[sample {s}] {response[:300]}{'...' if len(response) > 300 else ''}")

        # Format variants
        print("\n--- Format variants at T=0 ---")
        for i, q in enumerate(FORMAT_VARIANTS):
            prompt = format_fn(tokenizer, q) if format_fn != format_prompt_base else format_fn(q)
            response = generate(model, tokenizer, prompt, temperature=0.0)
            results["format_variants_T0"][f"f{i}"] = {"question": q, "response": response}
            print(f"\n[f{i}] Q: {q}")
            print(f"     A: {response[:300]}{'...' if len(response) > 300 else ''}")
    finally:
        free_model(model)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--hf-token", type=str, default=None)
    parser.add_argument("--model", choices=["instruct", "base"], default="instruct",
                        help="Which model to run this invocation. Run once for each.")
    args = parser.parse_args()

    hf_token = args.hf_token or os.environ.get("HF_TOKEN")

    if not torch.cuda.is_available():
        print("ERROR: CUDA not available.")
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.output_dir / "hemings_results.json"

    # Load existing results if present (so the second invocation merges with the first)
    all_results = {}
    if out_path.exists():
        try:
            all_results = json.loads(out_path.read_text(encoding="utf-8"))
        except Exception:
            all_results = {}

    print("=" * 78)
    print(f"Hemings test — {args.model}")
    print("=" * 78)

    if args.model == "instruct":
        all_results["instruct"] = run_one_model(INSTRUCT_MODEL, format_prompt_instruct, hf_token)
    else:
        all_results["base"] = run_one_model(BASE_MODEL, format_prompt_base, hf_token)

    out_path.write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[save] {out_path}")
    if args.model == "instruct":
        print("Now run: python hemings_test.py --model base")


if __name__ == "__main__":
    main()
