"""
LLM trajectory adapter: extract per-token signal sequences for the ASD
encoder from language model generations.

Provides three signal types per FN-PHANTOM-002 Section 2:
  Choice A: generating-model surprisal     s_i^A = -log pi_gen(t_i | t_<i, p)
  Choice B: cross-model surprisal          s_i^B = -log pi_base(t_i | t_<i, p)
  Choice C: per-token leakage              s_i^C = log pi_inst(t_i | ...) - log pi_base(t_i | ...)

Two backends:
  MockLMBackend                -- works without GPU; produces realistic-looking
                                  trajectories with controllable structure (used for
                                  pipeline validation in this sandbox).
  TransformersBackend          -- requires torch+transformers+GPU; SEQUENTIAL
                                  loading (one model at a time) -- required at
                                  16GB VRAM. Use generate_batch() for the
                                  two-pass workflow: load instruct, generate +
                                  score everything, free, load base, score
                                  everything, free.

The interface is a Trajectory dataclass with fields:
  prompt              : the prompt string
  generation          : the generated continuation as a list of token strings
  surprisal_inst      : np.ndarray of -log pi_inst(t_i | t_<i, p), length T
  surprisal_base      : np.ndarray of -log pi_base(t_i | t_<i, p), length T
  rho                 : np.ndarray of per-token leakage, length T
  generating_model    : 'inst' or 'base'
  meta                : dict with seed, temperature, etc.
"""

from __future__ import annotations
import gc
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Trajectory:
    prompt: str
    generation: list  # token strings or ids
    surprisal_inst: np.ndarray
    surprisal_base: np.ndarray
    rho: np.ndarray
    generating_model: str  # 'inst' or 'base'
    meta: dict = field(default_factory=dict)

    def signal(self, choice: str) -> np.ndarray:
        """Return Choice A, B, or C signal."""
        if choice == "A":
            if self.generating_model == "inst":
                return self.surprisal_inst.copy()
            return self.surprisal_base.copy()
        elif choice == "B":
            return self.surprisal_base.copy()
        elif choice == "C":
            return self.rho.copy()
        raise ValueError(f"Unknown choice: {choice}")


# ----------------------------------------------------------------------------
# Mock backend: usable without GPU; structures realistic LM-trajectory shapes.
# ----------------------------------------------------------------------------

class MockLMBackend:
    """
    Mock LM trajectory generator with controllable structure.

    Each prompt has a `topic_kind` controlling the trajectory's structure:
      'control'    : Both models produce ~IID surprisal, low rho mean
      'commitment' : inst model commits to a shaped framing in the first
                     COMMITMENT_LENGTH tokens (high rho early, then ~0)
      'persistent' : inst model exhibits persistent shaping (AR(1)-like
                     elevated rho across the trajectory)
      'clustered'  : inst model has bursts of high rho at content positions
    """

    def __init__(self, base_surprisal_mean: float = 4.0,
                 base_surprisal_std: float = 1.5):
        self.base_mu = base_surprisal_mean
        self.base_sigma = base_surprisal_std

    def generate(self, prompt: str, topic_kind: str = "control",
                  T: int = 256, temperature: float = 0.7,
                  seed: int = 0,
                  generating_model: str = "inst",
                  shaping_strength: float = 1.5) -> Trajectory:
        rng = np.random.default_rng(seed)
        s_base = np.zeros(T)
        s_base[0] = self.base_mu + rng.standard_normal() * self.base_sigma
        for i in range(1, T):
            s_base[i] = (0.3 * s_base[i - 1] + 0.7 * self.base_mu
                          + rng.standard_normal() * self.base_sigma)
        s_base = np.maximum(s_base, 0.1)

        if topic_kind == "control":
            rho = rng.normal(0.0, 0.6, T)
        elif topic_kind == "commitment":
            rho = rng.normal(0.0, 0.6, T)
            commit_length = min(40, T // 4)
            rho[:commit_length] += shaping_strength
        elif topic_kind == "persistent":
            rho = np.zeros(T)
            rho[0] = shaping_strength + rng.standard_normal() * 0.6
            for i in range(1, T):
                rho[i] = (0.7 * (rho[i - 1] - shaping_strength)
                          + shaping_strength
                          + rng.standard_normal() * 0.6)
        elif topic_kind == "clustered":
            rho = rng.normal(0.0, 0.6, T)
            burst_mask = rng.random(T) < 0.05
            rho[burst_mask] += shaping_strength * np.abs(rng.standard_normal(burst_mask.sum())) * 1.5
        else:
            raise ValueError(f"Unknown topic_kind: {topic_kind}")

        s_inst = s_base - rho
        s_inst = np.maximum(s_inst, 0.05)
        rho = s_base - s_inst

        gen = [f"tok_{i}" for i in range(T)]
        meta = {
            "seed": seed,
            "temperature": temperature,
            "topic_kind": topic_kind,
            "T": T,
            "shaping_strength": shaping_strength,
        }
        return Trajectory(prompt=prompt, generation=gen,
                           surprisal_inst=s_inst, surprisal_base=s_base,
                           rho=rho, generating_model=generating_model,
                           meta=meta)


# ----------------------------------------------------------------------------
# Real Llama backend: SEQUENTIAL loading via two-pass workflow.
# ----------------------------------------------------------------------------

class TransformersBackend:
    """
    Real LM backend using HuggingFace transformers, with sequential model
    loading suited to a 16 GB VRAM budget (e.g. RTX 5080).

    Workflow (use generate_batch):
      Pass 1: Load Instruct model. For each spec, generate a continuation
              and score it under Instruct (gives surprisal_inst). Save
              token IDs alongside the partial trajectory. Free Instruct.
      Pass 2: Load base model. For each partial trajectory, score the same
              token sequence under base (gives surprisal_base). Compute
              rho_i = surp_base - surp_inst. Free base.

    This avoids holding two 16 GB models in 16 GB VRAM at the same time
    (which forces constant swapping with system RAM and is several times
    slower than sequential).

    Usage:
        backend = TransformersBackend(
            inst_model_name="meta-llama/Llama-3.1-8B-Instruct",
            base_model_name="meta-llama/Llama-3.1-8B",
            device="cuda",
        )
        specs = [
            {"prompt": "...", "seed": 0, "T": 256, "temperature": 0.7,
             "meta_extra": {"topic": "geography_capitals", "paraphrase_idx": 0}},
            ...
        ]
        trajectories = backend.generate_batch(specs)
    """

    def __init__(self, inst_model_name: str, base_model_name: str,
                 device: str = "cuda", dtype=None,
                 hf_token: Optional[str] = None):
        try:
            from transformers import AutoTokenizer  # noqa
            import torch  # noqa
        except ImportError as e:
            raise ImportError(
                "TransformersBackend requires torch+transformers. "
                "Install with: pip install torch transformers accelerate"
            ) from e

        import torch
        from transformers import AutoTokenizer

        self.torch = torch
        self.device = device
        self.inst_model_name = inst_model_name
        self.base_model_name = base_model_name
        self.hf_token = hf_token

        if dtype is None:
            dtype = torch.bfloat16 if device.startswith("cuda") else torch.float32
        self.dtype = dtype

        # Load tokenizer once (Llama-3.1 base and Instruct share vocab)
        print(f"[load] tokenizer from {inst_model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(inst_model_name, token=hf_token)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self._model = None
        self._loaded = None  # 'inst' or 'base' or None

    # ----- model swap primitives ---------------------------------------

    def _load(self, which: str):
        if self._loaded == which:
            return
        self._free()
        from transformers import AutoModelForCausalLM
        name = self.inst_model_name if which == "inst" else self.base_model_name
        torch = self.torch
        print(f"[load] {name}")
        # Try `dtype=` (current transformers) and fall back to torch_dtype= if older
        try:
            self._model = AutoModelForCausalLM.from_pretrained(
                name, dtype=self.dtype, device_map=self.device,
                token=self.hf_token, low_cpu_mem_usage=True,
            )
        except TypeError:
            self._model = AutoModelForCausalLM.from_pretrained(
                name, torch_dtype=self.dtype, device_map=self.device,
                token=self.hf_token, low_cpu_mem_usage=True,
            )
        self._model.eval()
        self._loaded = which
        n_params = sum(p.numel() for p in self._model.parameters()) / 1e9
        vram_gb = torch.cuda.memory_allocated() / 1e9 if torch.cuda.is_available() else 0
        print(f"[load] {n_params:.2f}B params, {vram_gb:.2f}GB VRAM")

    def _free(self):
        if self._model is not None:
            del self._model
            self._model = None
        gc.collect()
        if self.torch.cuda.is_available():
            self.torch.cuda.empty_cache()
        self._loaded = None
        if self.torch.cuda.is_available():
            vram_gb = self.torch.cuda.memory_allocated() / 1e9
            print(f"[free] VRAM after cleanup: {vram_gb:.2f}GB")

    # ----- generation + scoring ----------------------------------------

    def _format_prompt_inst(self, prompt: str) -> str:
        """Apply the Instruct chat template."""
        messages = [{"role": "user", "content": prompt}]
        return self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

    def _generate_one(self, prompt_text: str, T: int, temperature: float,
                       seed: int):
        """Generate from currently-loaded model. Returns full token tensor + prompt_len."""
        torch = self.torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        prompt_ids = self.tokenizer(prompt_text, return_tensors="pt").input_ids.to(self.device)
        prompt_len = prompt_ids.shape[1]
        with torch.no_grad():
            out = self._model.generate(
                prompt_ids,
                max_new_tokens=T,
                do_sample=(temperature > 0),
                temperature=temperature if temperature > 0 else 1.0,
                top_p=1.0,
                pad_token_id=self.tokenizer.pad_token_id,
                return_dict_in_generate=True,
            )
        return out.sequences, prompt_len

    def _score_currently_loaded(self, full_ids, prompt_len: int) -> np.ndarray:
        """
        Compute -log p(t_i | t_<i) for each generated token under the
        currently loaded model. Returns np array of length T_actual.
        """
        torch = self.torch
        with torch.no_grad():
            logits = self._model(full_ids).logits  # [1, prompt_len + T, V]
        T = full_ids.shape[1] - prompt_len
        if T <= 0:
            return np.array([], dtype=np.float32)
        # Logits at position (prompt_len + i - 1) score token at position (prompt_len + i)
        relevant = logits[0, prompt_len - 1: prompt_len - 1 + T, :]
        log_probs = torch.log_softmax(relevant.float(), dim=-1)
        target_ids = full_ids[0, prompt_len: prompt_len + T]
        per_token_lp = log_probs.gather(-1, target_ids.unsqueeze(-1)).squeeze(-1)
        return (-per_token_lp).cpu().numpy().astype(np.float32)

    # ----- two-pass batch API ------------------------------------------

    def generate_batch(self, specs: list, verbose_every: int = 10) -> list:
        """
        Two-pass batch generation. Each spec is a dict with:
            prompt        : str
            seed          : int
            T             : int (max_new_tokens)
            temperature   : float
            meta_extra    : dict (optional, copied into traj.meta)

        Returns: list of Trajectory objects, in the same order as specs.
        """
        torch = self.torch
        n = len(specs)
        print(f"\n=== Pass 1/2: load Instruct, generate + score {n} continuations ===")
        self._load("inst")

        partial = []  # tuples of (spec, full_ids_cpu_numpy, prompt_len, surprisal_inst)
        import time
        t0 = time.time()

        for i, spec in enumerate(specs):
            prompt = spec["prompt"]
            seed = int(spec["seed"])
            T = int(spec.get("T", 256))
            temperature = float(spec.get("temperature", 0.7))

            prompt_text = self._format_prompt_inst(prompt)
            try:
                full_ids, prompt_len = self._generate_one(prompt_text, T, temperature, seed)
                surp_inst = self._score_currently_loaded(full_ids, prompt_len)
            except torch.cuda.OutOfMemoryError:
                print(f"[OOM] spec {i} ({spec.get('meta_extra', {})}); skipping")
                torch.cuda.empty_cache()
                partial.append(None)
                continue
            partial.append((full_ids.detach().cpu().numpy(), prompt_len, surp_inst))

            if (i + 1) % verbose_every == 0 or i == n - 1:
                elapsed = time.time() - t0
                rate = (i + 1) / elapsed
                eta = (n - i - 1) / rate if rate > 0 else 0
                print(f"  [pass1] {i+1}/{n}  ({elapsed:.1f}s elapsed, {rate:.2f}/s, ETA {eta/60:.1f} min)")

        # Free Instruct
        self._free()

        print(f"\n=== Pass 2/2: load base, score {n} continuations ===")
        self._load("base")

        trajectories = []
        t0 = time.time()
        for i, (spec, p) in enumerate(zip(specs, partial)):
            if p is None:
                trajectories.append(None)
                continue
            full_ids_np, prompt_len, surp_inst = p
            full_ids = torch.from_numpy(full_ids_np).to(self.device)
            try:
                surp_base = self._score_currently_loaded(full_ids, prompt_len)
            except torch.cuda.OutOfMemoryError:
                print(f"[OOM] spec {i} pass2; skipping")
                torch.cuda.empty_cache()
                trajectories.append(None)
                continue

            T_actual = len(surp_inst)
            if T_actual == 0:
                trajectories.append(None)
                continue

            rho = surp_base - surp_inst
            gen_ids = full_ids[0, prompt_len: prompt_len + T_actual]
            gen_strs = [self.tokenizer.decode([int(t)]) for t in gen_ids]

            meta = {
                "seed": int(spec["seed"]),
                "temperature": float(spec.get("temperature", 0.7)),
                "T": T_actual,
                "T_requested": int(spec.get("T", 256)),
                "prompt_len": int(prompt_len),
            }
            if "meta_extra" in spec and spec["meta_extra"]:
                meta.update(spec["meta_extra"])

            trajectories.append(Trajectory(
                prompt=spec["prompt"],
                generation=gen_strs,
                surprisal_inst=surp_inst,
                surprisal_base=surp_base,
                rho=rho,
                generating_model="inst",
                meta=meta,
            ))

            if (i + 1) % verbose_every == 0 or i == n - 1:
                elapsed = time.time() - t0
                rate = (i + 1) / elapsed
                eta = (n - i - 1) / rate if rate > 0 else 0
                print(f"  [pass2] {i+1}/{n}  ({elapsed:.1f}s elapsed, {rate:.2f}/s, ETA {eta/60:.1f} min)")

        self._free()
        print(f"\n[done] {sum(1 for t in trajectories if t is not None)} / {n} trajectories complete")
        return trajectories

    # ----- back-compat single-call API (loads/frees per call -- DON'T use in loops) -----

    def generate(self, prompt: str, T: int = 256, temperature: float = 0.7,
                  seed: int = 0, generating_model: str = "inst",
                  meta_extra: Optional[dict] = None) -> Trajectory:
        """
        Single-trajectory API. Calls generate_batch under the hood. Inefficient
        if called in a loop -- use generate_batch with a list of specs instead.
        """
        spec = {"prompt": prompt, "seed": seed, "T": T,
                "temperature": temperature, "meta_extra": meta_extra or {}}
        out = self.generate_batch([spec], verbose_every=1)
        if out[0] is None:
            raise RuntimeError("Generation failed")
        return out[0]
