"""
LLM trajectory adapter: extract per-token signal sequences for the ASD
encoder from language model generations.

Provides three signal types per FN-PHANTOM-002 Section 2:
  Choice A: generating-model surprisal     s_i^A = -log pi_gen(t_i | t_<i, p)
  Choice B: cross-model surprisal          s_i^B = -log pi_base(t_i | t_<i, p)
  Choice C: per-token leakage              s_i^C = log pi_inst(t_i | ...) - log pi_base(t_i | ...)

Two backends:
  MockLMBackend     -- works without GPU; produces realistic-looking
                        trajectories with controllable structure (used for
                        pipeline validation in this sandbox).
  TransformersBackend -- requires torch+transformers+GPU; produces real
                        trajectories. Implementation provided as a stub
                        that the user fills in on their machine.

The interface is a Trajectory dataclass with fields:
  prompt              : the prompt string
  generation          : the generated continuation as a list of token strings
                        OR token ids (depending on backend)
  surprisal_inst      : np.ndarray of -log pi_inst(t_i | t_<i, p), length T
  surprisal_base      : np.ndarray of -log pi_base(t_i | t_<i, p), length T
  rho                 : np.ndarray of per-token leakage, length T
  generating_model    : 'inst' or 'base'
  meta                : dict with seed, temperature, etc.
"""

from __future__ import annotations
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

    Models the parametric memory of induced holes (commitment, persistent)
    vs natural rarity (clustered) vs no shaping (control).
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

        # Base surprisal trajectory: slightly autocorrelated reflecting
        # natural language structure
        s_base = np.zeros(T)
        s_base[0] = self.base_mu + rng.standard_normal() * self.base_sigma
        for i in range(1, T):
            s_base[i] = (0.3 * s_base[i - 1] + 0.7 * self.base_mu
                          + rng.standard_normal() * self.base_sigma)
        s_base = np.maximum(s_base, 0.1)  # surprisal is non-negative

        # rho_i depends on topic_kind
        if topic_kind == "control":
            rho = rng.normal(0.0, 0.6, T)
        elif topic_kind == "commitment":
            rho = rng.normal(0.0, 0.6, T)
            commit_length = min(40, T // 4)
            rho[:commit_length] += shaping_strength
        elif topic_kind == "persistent":
            # AR(1) with positive shift
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

        # Compute s_inst from s_base and rho:
        # rho = log p_inst - log p_base = -surp_inst - (-surp_base) = surp_base - surp_inst
        # surp_inst = surp_base - rho
        s_inst = s_base - rho
        s_inst = np.maximum(s_inst, 0.05)
        # Recompute rho post-clip to stay consistent
        rho = s_base - s_inst

        # Tokens: synthetic placeholders
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
# Real Llama backend (requires torch, transformers, GPU)
# ----------------------------------------------------------------------------

class TransformersBackend:
    """
    Real LM backend using HuggingFace transformers. NOT runnable in this
    sandbox; the implementation is provided so the user can drop it onto
    their GPU box.

    Usage:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        backend = TransformersBackend(
            inst_model_name="meta-llama/Meta-Llama-3.1-8B-Instruct",
            base_model_name="meta-llama/Meta-Llama-3.1-8B",
            device="cuda",
        )
        traj = backend.generate("What does FBI UCR data show...", T=256, seed=0)

    The two models share a tokenizer (Llama-3.1-base and -Instruct have
    the same vocabulary). Cross-tokenizer scenarios require additional
    handling (Section 1 of FN-PHANTOM-002).
    """

    def __init__(self, inst_model_name: str, base_model_name: str,
                 device: str = "cuda", dtype=None,
                 use_paged: bool = True):
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
        except ImportError as e:
            raise ImportError(
                "TransformersBackend requires torch+transformers. "
                "Install with: pip install torch transformers"
            ) from e
        self.torch = torch
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(inst_model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        if dtype is None:
            dtype = torch.bfloat16 if device.startswith("cuda") else torch.float32

        self.inst_model = AutoModelForCausalLM.from_pretrained(
            inst_model_name, torch_dtype=dtype, device_map=device,
        )
        self.inst_model.eval()
        self.base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name, torch_dtype=dtype, device_map=device,
        )
        self.base_model.eval()

    @property
    def torch_module(self):
        return self.torch

    def generate(self, prompt: str, T: int = 256, temperature: float = 0.7,
                  seed: int = 0, generating_model: str = "inst",
                  meta_extra: dict = None) -> Trajectory:
        torch = self.torch
        torch.manual_seed(seed)

        gen_model = self.inst_model if generating_model == "inst" else self.base_model

        prompt_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(self.device)
        prompt_len = prompt_ids.shape[1]

        # Stochastic generation
        with torch.no_grad():
            out = gen_model.generate(
                prompt_ids,
                max_new_tokens=T,
                do_sample=(temperature > 0),
                temperature=temperature,
                top_p=1.0,
                pad_token_id=self.tokenizer.pad_token_id,
                return_dict_in_generate=True,
            )
        full_ids = out.sequences  # [1, prompt_len + T_actual]
        gen_ids = full_ids[0, prompt_len:]
        T_actual = gen_ids.shape[0]
        if T_actual == 0:
            raise RuntimeError("Generation produced no tokens.")

        # Score the generated tokens under both models
        s_inst = self._score(self.inst_model, full_ids, prompt_len)
        s_base = self._score(self.base_model, full_ids, prompt_len)

        rho_field = s_base - s_inst  # log p_inst - log p_base = -surp_inst + surp_base

        gen_strs = [self.tokenizer.decode([int(t)]) for t in gen_ids]

        meta = {
            "seed": seed,
            "temperature": temperature,
            "T": T_actual,
            "T_requested": T,
            "prompt_len": prompt_len,
        }
        if meta_extra:
            meta.update(meta_extra)

        return Trajectory(
            prompt=prompt, generation=gen_strs,
            surprisal_inst=s_inst, surprisal_base=s_base,
            rho=rho_field, generating_model=generating_model,
            meta=meta,
        )

    def _score(self, model, full_ids, prompt_len: int) -> np.ndarray:
        """
        Compute -log p(t_i | t_<i, p) for each generated token i.

        full_ids: tensor [1, prompt_len + T]
        Returns: np.ndarray of length T (one surprisal per generated token).
        """
        torch = self.torch
        with torch.no_grad():
            logits = model(full_ids).logits  # [1, prompt_len + T, V]
        # Predict t_i from t_<i: logits at position (prompt_len + i - 1) score t_i
        # We want the logits at indices [prompt_len-1 .. prompt_len + T - 2]
        # to predict tokens at indices [prompt_len .. prompt_len + T - 1]
        T = full_ids.shape[1] - prompt_len
        relevant_logits = logits[0, prompt_len - 1: prompt_len - 1 + T, :]  # [T, V]
        log_probs = torch.log_softmax(relevant_logits.float(), dim=-1)  # [T, V]
        target_ids = full_ids[0, prompt_len: prompt_len + T]  # [T]
        per_token_lp = log_probs.gather(-1, target_ids.unsqueeze(-1)).squeeze(-1)
        surprisal = -per_token_lp.cpu().numpy()
        return surprisal


# ----------------------------------------------------------------------------
# Convenience: paired-sample protocol
# ----------------------------------------------------------------------------

def paired_sample(backend, prompt: str, K: int = 50,
                   T: int = 256, temperature: float = 0.7,
                   topic_kind: str = "control",
                   base_seed_offset: int = 0) -> dict:
    """
    Generate K continuations from each of inst and base models on the
    same prompt. Returns dict with 'inst' and 'base' lists of Trajectory.

    For MockLMBackend, topic_kind is honored. For TransformersBackend,
    topic_kind is stored in metadata only (the actual structure depends
    on the real model behavior).
    """
    is_mock = isinstance(backend, MockLMBackend)
    inst_traj = []
    base_traj = []
    for k in range(K):
        if is_mock:
            inst_traj.append(backend.generate(
                prompt, topic_kind=topic_kind, T=T, temperature=temperature,
                seed=k + base_seed_offset, generating_model="inst",
            ))
            base_traj.append(backend.generate(
                prompt, topic_kind="control", T=T, temperature=temperature,
                seed=k + base_seed_offset + 100_000,
                generating_model="base",
            ))
        else:
            inst_traj.append(backend.generate(
                prompt, T=T, temperature=temperature,
                seed=k + base_seed_offset, generating_model="inst",
                meta_extra={"topic_kind": topic_kind},
            ))
            base_traj.append(backend.generate(
                prompt, T=T, temperature=temperature,
                seed=k + base_seed_offset + 100_000,
                generating_model="base",
                meta_extra={"topic_kind": topic_kind},
            ))
    return {"inst": inst_traj, "base": base_traj}
