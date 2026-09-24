"""Needle-in-a-haystack test (milestone 4): can the model find one fact in a long document?

Builds invented filler text of an exact token length (measured with the server's own
/tokenize), hides one fact at a chosen depth, asks for it, and logs found/not found plus
prefill time to results/needle.jsonl.
"""

import dataclasses
import random
from datetime import datetime

import requests

from . import client
from .config import Machine, RunConfig
from .runner import LOG_DIR, RESULTS_DIR, append_row
from .server import LlamaServer

NEEDLE_FILE = RESULTS_DIR / "needle.jsonl"
NEEDLE = "Important note for staff: the access code for the Harbour Street vault is 7481-QX."
QUESTION = "What is the access code for the Harbour Street vault? Reply with the code only."
CODE = "7481-QX"
OVERHEAD_TOKENS = 120  # instructions + question + chat template, measured below anyway

_TEAMS = ["billing", "platform", "search", "payments", "logistics", "support", "identity", "reporting"]
_THINGS = ["dashboard", "release plan", "incident review", "backlog", "runbook", "roadmap", "budget", "rota"]
_VERBS = ["reviewed", "updated", "discussed", "approved", "archived", "reorganised", "shared", "checked"]
_PLACES = ["Leeds", "York", "Bath", "Derby", "Exeter", "Norwich", "Durham", "Chester"]
_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
_TAILS = ["without major changes", "after a short delay", "as planned", "with minor comments",
          "ahead of the quarterly meeting", "once the new process was agreed"]


def filler_sentence(rng: random.Random) -> str:
    return (f"On {rng.choice(_DAYS)} the {rng.choice(_TEAMS)} team in {rng.choice(_PLACES)} "
            f"{rng.choice(_VERBS)} the {rng.choice(_THINGS)} {rng.choice(_TAILS)}.")


def count_tokens(base_url: str, text: str) -> int:
    r = requests.post(f"{base_url}/tokenize", json={"content": text}, timeout=120)
    r.raise_for_status()
    return len(r.json()["tokens"])


def build_prompt(base_url: str, target_tokens: int, depth: float, seed: int = 7) -> str:
    """Prompt of about `target_tokens` tokens with the needle at `depth` (0 = start, 1 = end)."""
    rng = random.Random(seed)
    sample = [filler_sentence(rng) for _ in range(200)]
    per_sentence = count_tokens(base_url, " ".join(sample)) / len(sample)
    n = max(1, int((target_tokens - OVERHEAD_TOKENS) / per_sentence))
    sentences = [filler_sentence(rng) for _ in range(n)]

    def render(k: int) -> str:
        body = sentences[:k]
        body.insert(round(depth * len(body)), NEEDLE)
        return ("Read the document below, then answer the question after it.\n\n<document>\n"
                + " ".join(body) + f"\n</document>\n\nQuestion: {QUESTION}")

    prompt = render(n)
    excess = count_tokens(base_url, prompt) + 20 - target_tokens  # ~20 chat-template tokens
    if excess > 0:
        prompt = render(max(1, n - int(excess / per_sentence) - 1))
    return prompt


def run_needle(cfg: RunConfig, machine: Machine, sizes: list[int], depths: list[float]) -> None:
    cfg = dataclasses.replace(cfg, ctx=max(sizes) + 1024)  # room for the prompt + a short answer
    cmd = cfg.server_command(machine)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    print(f"\n== needle: {cfg.name}, ctx {cfg.ctx}, sizes {sizes}, depths {depths}")
    with LlamaServer(cmd, machine.base_url, machine.host, machine.port, cfg.model,
                     LOG_DIR / f"needle__{cfg.name}__{stamp}.log", machine.health_timeout_s) as srv:
        print(f"   server up in {srv.info['load_s']}s, KV {srv.info['buffers_mib'].get('kv')}", flush=True)
        for size in sizes:
            for depth in depths:
                prompt = build_prompt(machine.base_url, size, depth)
                res = client.chat(machine.base_url, prompt, thinking=False, sampling=cfg.sampling,
                                  max_tokens=64, timeout_s=cfg.request_timeout_s)
                found = CODE.replace("-", "").lower() in res.answer.replace("-", "").replace(" ", "").lower()
                append_row({
                    "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
                    "machine": machine.name, "config": cfg.name, "config_hash": cfg.config_hash,
                    "model_file": cfg.model.name, "backend": cfg.backend.name, "ctx": cfg.ctx,
                    "target_tokens": size, "depth": depth, "found": found,
                    **res.to_dict(), "server": {**srv.info, "cmd": cmd},
                }, NEEDLE_FILE)
                print(f"   {size:>6} tokens (actual {res.prompt_tokens}), depth {depth:.2f}: "
                      f"{'FOUND' if found else 'MISSED'}  prefill {_s(res.prefill_ms)}  "
                      f"({_f(res.prefill_tok_s)} tok/s)  answer {res.answer.strip()[:40]!r}"
                      + (f"  error {res.error}" if res.error else ""), flush=True)


def _s(ms: float | None) -> str:
    return "-" if ms is None else f"{ms / 1000:.1f} s"


def _f(v: float | None) -> str:
    return "-" if v is None else f"{v:.0f}"

