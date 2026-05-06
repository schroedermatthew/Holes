"""
Phase C Arm 2: Generation-time activation extraction.

Phase B showed that misrepresentation does NOT leave a signature at the final
prompt token. The framework's revised prediction: misrep is a generation-time
phenomenon, not a prompt-encoding phenomenon. The substitution happens
incrementally during token generation.

This script tests that revised prediction. For each focus item:
  1. Generate Instruct's response (the actual constrained output).
  2. Construct combined input: question + Instruct's response (raw text format).
     Both base and Instruct use the same Llama-3.1 tokenizer, so token IDs are
     identical between the two forward passes.
  3. Forward each model on the combined input with output_hidden_states=True.
  4. Save residual stream activations for the response-token portion only,
     at every layer.

Storage: ~25-30MB per (item, model) at fp16 for 100-token responses,
~315MB total for 6 items × 2 models. Saved compressed.

Runtime: ~10 minutes total on RTX 5080 (model loads dominate).

Usage:
    python arm2_extract_generation.py
    python arm2_extract_generation.py --output-dir activations
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


# Selected items from Phase A/B findings
FOCUS_ITEMS = [
    ("crime_demographics_us", 3, "misrep_severe"),
    ("founding_fathers", 4, "misrep"),
    ("wehrmacht_1943", 4, "misrep_mild"),
    ("medieval_knights", 4, "correction"),
    ("biden_president_2023", 1, "refusal"),
    ("control_periodic_table", 3, "control"),
]


def format_prompt_instruct(tokenizer, question: str) -> str:
    messages = [{"role": "user", "content": question}]
    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )


def make_combined_input(question: str, response: str) -> str:
    """Raw text format used for the analysis forward pass.

    Both models tokenize this identically since they share the underlying
    Llama-3.1 BPE tokenizer. The chat template tokens are NOT used here —
    we want clean position-by-position alignment between base and Instruct.
    """
    return f"{question}\n\n{response}"


def get_response_token_start(tokenizer, question: str, combined: str) -> int:
    """Find where the response begins in the tokenized combined input."""
    question_with_sep = question + "\n\n"
    return len(tokenizer(question_with_sep, add_special_tokens=True).input_ids)


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
    print(f"[load] loaded; VRAM in use: {torch.cuda.memory_allocated() / 1e9:.2f}GB")
    return model, tokenizer


def free_model(model):
    del model
    gc.collect()
    torch.cuda.empty_cache()
    print(f"[free] VRAM after cleanup: {torch.cuda.memory_allocated() / 1e9:.2f}GB")


def forward_and_capture(model, tokenizer, combined_text: str, response_start: int) -> np.ndarray:
    """Forward pass, return hidden states for response tokens only.

    Returns array of shape (n_layers + 1, n_response_tokens, hidden_dim) as fp16.
    """
    inputs = tokenizer(combined_text, return_tensors="pt", add_special_tokens=True).to("cuda")
    with torch.no_grad():
        out = model(**inputs, output_hidden_states=True, return_dict=True)

    # out.hidden_states: tuple of (n_layers + 1) tensors, each (1, n_tokens, hidden_dim)
    stacked = torch.stack(
        [h[0, response_start:, :].float().cpu() for h in out.hidden_states],
        dim=0,
    )
    return stacked.numpy().astype(np.float16)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-cases", type=Path, default=Path("../phase_a/test_cases.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("activations"))
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--hf-token", type=str, default=None)
    parser.add_argument("--skip-generation", action="store_true",
                        help="Skip generation step; use existing responses.json")
    args = parser.parse_args()

    hf_token = args.hf_token or os.environ.get("HF_TOKEN")

    if not torch.cuda.is_available():
        print("ERROR: CUDA not available.")
        sys.exit(1)

    if not args.test_cases.exists():
        print(f"ERROR: test cases not found: {args.test_cases}")
        sys.exit(1)

    cases_data = json.loads(args.test_cases.read_text(encoding="utf-8"))
    cases_by_id = {item["id"]: item for item in cases_data["items"]}

    args.output_dir.mkdir(parents=True, exist_ok=True)
    responses_path = args.output_dir / "responses.json"

    # === Step 1: Generate Instruct responses (or load) ===
    if args.skip_generation and responses_path.exists():
        print(f"[step 1] Loading existing responses from {responses_path}")
        responses = json.loads(responses_path.read_text(encoding="utf-8"))
    else:
        print("\n=== Step 1: Generate Instruct responses ===")
        model, tokenizer = load_model(INSTRUCT_MODEL, hf_token=hf_token)

        responses = {}
        try:
            for item_id, level, role in FOCUS_ITEMS:
                if item_id not in cases_by_id:
                    print(f"  [skip] {item_id} not in test cases")
                    continue
                item = cases_by_id[item_id]
                qdata = next((q for q in item["questions"] if q["level"] == level), None)
                if qdata is None:
                    print(f"  [skip] {item_id} L{level} not found")
                    continue
                question = qdata["question"]

                prompt = format_prompt_instruct(tokenizer, question)
                inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

                with torch.no_grad():
                    output = model.generate(
                        **inputs,
                        max_new_tokens=args.max_new_tokens,
                        do_sample=False,
                        pad_token_id=tokenizer.pad_token_id,
                    )

                response_text = tokenizer.decode(
                    output[0][inputs.input_ids.shape[1]:],
                    skip_special_tokens=True,
                )

                key = f"{item_id}_L{level}"
                responses[key] = {
                    "item_id": item_id,
                    "level": level,
                    "role": role,
                    "question": question,
                    "response": response_text,
                }
                print(f"  [{key}] generated {len(response_text.split())} words")
        finally:
            free_model(model)

        responses_path.write_text(json.dumps(responses, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  saved {responses_path}")

    # === Step 2: Forward Instruct on combined input, save hidden states ===
    print("\n=== Step 2: Forward Instruct on (question + response) ===")
    instruct_path = args.output_dir / "instruct_hidden.npz"
    response_starts_path = args.output_dir / "response_starts.json"

    model, tokenizer = load_model(INSTRUCT_MODEL, hf_token=hf_token)

    instruct_hidden = {}
    response_starts = {}
    try:
        for key, r in responses.items():
            combined = make_combined_input(r["question"], r["response"])
            response_start = get_response_token_start(tokenizer, r["question"], combined)
            response_starts[key] = response_start

            try:
                acts = forward_and_capture(model, tokenizer, combined, response_start)
                instruct_hidden[key] = acts
                print(f"  [{key}] response_start={response_start} acts shape={acts.shape}")
            except torch.cuda.OutOfMemoryError:
                print(f"  [OOM] {key} — skipping")
                torch.cuda.empty_cache()
                continue
    finally:
        free_model(model)

    np.savez_compressed(instruct_path, **instruct_hidden)
    response_starts_path.write_text(json.dumps(response_starts, indent=2), encoding="utf-8")
    print(f"  saved {instruct_path}")

    # === Step 3: Forward Base on identical input ===
    print("\n=== Step 3: Forward Base on same combined input ===")
    base_path = args.output_dir / "base_hidden.npz"

    model, tokenizer = load_model(BASE_MODEL, hf_token=hf_token)

    base_hidden = {}
    try:
        for key, r in responses.items():
            if key not in instruct_hidden:
                continue
            combined = make_combined_input(r["question"], r["response"])
            response_start = response_starts[key]

            try:
                acts = forward_and_capture(model, tokenizer, combined, response_start)
                base_hidden[key] = acts
                print(f"  [{key}] acts shape={acts.shape}")
            except torch.cuda.OutOfMemoryError:
                print(f"  [OOM] {key} — skipping")
                torch.cuda.empty_cache()
                continue
    finally:
        free_model(model)

    np.savez_compressed(base_path, **base_hidden)
    print(f"  saved {base_path}")

    # Verify shapes match
    print("\n=== Shape verification ===")
    for key in instruct_hidden:
        if key in base_hidden:
            i_shape = instruct_hidden[key].shape
            b_shape = base_hidden[key].shape
            ok = "OK" if i_shape == b_shape else "MISMATCH"
            print(f"  [{ok}] {key}: instruct={i_shape} base={b_shape}")

    print("\nArm 2 extraction complete.")
    print(f"Next: python arm2_analyze_generation.py")


if __name__ == "__main__":
    main()
