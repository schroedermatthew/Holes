"""
Phase A: Inference run for the dynamic forensic apparatus pilot.

Loads Llama-3.1-8B base and Llama-3.1-8B-Instruct sequentially, runs inference
on the test case set, saves outputs to disk for scoring and analysis.

Hardware target: RTX 5080 16GB VRAM, 64GB system RAM, Windows 11.
Runtime: ~30-60 minutes total for the default test case set.

Usage:
    python run_inference.py
    python run_inference.py --only base       # run only base model
    python run_inference.py --only instruct   # run only Instruct model
    python run_inference.py --max-tokens 512  # longer responses

Authentication:
    The Llama-3.1 models are gated. Either:
      1. Run `huggingface-cli login` once and accept the license at
         https://huggingface.co/meta-llama/Llama-3.1-8B
      2. Set HF_TOKEN environment variable
      3. Pass --hf-token on the command line
"""

import argparse
import gc
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


BASE_MODEL = "meta-llama/Llama-3.1-8B"
INSTRUCT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"


def format_prompt_base(question: str) -> str:
    """Format prompt for the base (completion) model.

    The base model is not chat-tuned. We use a Q/A continuation format that
    elicits factual answers without the chat-template overhead.
    """
    return f"Question: {question}\nAnswer:"


def format_prompt_instruct(tokenizer, question: str) -> str:
    """Format prompt for the Instruct (chat) model using its chat template."""
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


def generate(model, tokenizer, prompt: str, max_new_tokens: int = 256, seed: int = 42) -> str:
    """Generate a deterministic response."""
    torch.manual_seed(seed)
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=1.0,
            top_p=1.0,
            pad_token_id=tokenizer.pad_token_id,
        )

    response_ids = outputs[0][inputs.input_ids.shape[1]:]
    return tokenizer.decode(response_ids, skip_special_tokens=True).strip()


def run_model_variant(
    model_id: str,
    variant_name: str,
    test_cases: list,
    output_dir: Path,
    max_new_tokens: int = 256,
    hf_token: str | None = None,
):
    """Run inference for one model variant on all test cases. Saves incrementally."""
    output_path = output_dir / f"outputs_{variant_name}.json"

    # Resume support: load any existing partial results
    completed: dict = {}
    if output_path.exists():
        try:
            completed = json.loads(output_path.read_text(encoding="utf-8"))
            print(f"[resume] {variant_name}: {len(completed)} entries already complete")
        except json.JSONDecodeError:
            print(f"[resume] {variant_name}: existing file unreadable, starting fresh")
            completed = {}

    total_questions = sum(len(item["questions"]) for item in test_cases)
    if len(completed) >= total_questions:
        print(f"[skip] {variant_name}: all {total_questions} entries already done")
        return output_path

    model, tokenizer = load_model(model_id, hf_token=hf_token)

    try:
        done = 0
        for item in test_cases:
            for q in item["questions"]:
                key = f"{item['id']}_L{q['level']}"
                done += 1

                if key in completed:
                    continue

                if variant_name == "base":
                    prompt = format_prompt_base(q["question"])
                else:
                    prompt = format_prompt_instruct(tokenizer, q["question"])

                try:
                    response = generate(
                        model, tokenizer, prompt, max_new_tokens=max_new_tokens
                    )
                except torch.cuda.OutOfMemoryError:
                    print(f"[OOM] {key}; consider reducing max_new_tokens")
                    torch.cuda.empty_cache()
                    response = "<OOM>"

                completed[key] = {
                    "key": key,
                    "item_id": item["id"],
                    "category": item["category"],
                    "topic": item["topic"],
                    "level": q["level"],
                    "question": q["question"],
                    "prompt": prompt,
                    "response": response,
                    "model": variant_name,
                    "model_id": model_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }

                # Save incrementally so a crash doesn't lose work
                output_path.write_text(
                    json.dumps(completed, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )

                # Print progress
                if done % 5 == 0 or done == total_questions:
                    print(f"[{variant_name}] {done}/{total_questions}  | last: {item['id']} L{q['level']}")
    finally:
        free_model(model)

    print(f"[done] {variant_name}: outputs at {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--test-cases", type=Path, default=Path("test_cases.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument(
        "--hf-token", type=str, default=None,
        help="HF token. Or set HF_TOKEN env var. Or use `huggingface-cli login`."
    )
    parser.add_argument(
        "--only", choices=["base", "instruct"], default=None,
        help="Run only one variant. Default: run both."
    )
    parser.add_argument("--max-tokens", type=int, default=256, dest="max_new_tokens")
    args = parser.parse_args()

    # Token resolution
    hf_token = args.hf_token or os.environ.get("HF_TOKEN")

    # Sanity checks
    if not args.test_cases.exists():
        print(f"ERROR: test cases file not found: {args.test_cases}", file=sys.stderr)
        sys.exit(1)

    if not torch.cuda.is_available():
        print("ERROR: CUDA not available. This script requires a CUDA GPU.", file=sys.stderr)
        sys.exit(1)

    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"Total VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    test_cases_data = json.loads(args.test_cases.read_text(encoding="utf-8"))
    test_cases = test_cases_data["items"]
    n_questions = sum(len(i["questions"]) for i in test_cases)
    print(f"Loaded {len(test_cases)} items, {n_questions} total questions")

    # Run base first (smaller cancellation, baseline) then Instruct
    if args.only != "instruct":
        run_model_variant(
            BASE_MODEL, "base", test_cases, args.output_dir,
            max_new_tokens=args.max_new_tokens, hf_token=hf_token,
        )

    if args.only != "base":
        run_model_variant(
            INSTRUCT_MODEL, "instruct", test_cases, args.output_dir,
            max_new_tokens=args.max_new_tokens, hf_token=hf_token,
        )

    print("\nPhase A inference complete.")
    print(f"Outputs saved to {args.output_dir.resolve()}")
    print("Next: run `python score_outputs.py` to apply rule-based scoring.")


if __name__ == "__main__":
    main()
