"""Send one streamed chat request to llama-server and measure it.

Field facts verified on build 11157 (see LOCAL_LLM_LAB.md section 9.4a):
- thinking text arrives as `delta.reasoning_content`, the answer as `delta.content`,
  one token per chunk;
- `usage.completion_tokens` counts thinking + answer tokens together, so thinking
  tokens = number of reasoning chunks (the ~3 hidden end-of-think tokens count as answer);
- the final chunk carries `usage` and `timings` (server-side prefill/decode numbers).
"""

import json
import time
from dataclasses import asdict, dataclass

import requests


@dataclass
class ChatResult:
    answer: str = ""
    reasoning: str | None = None
    finish_reason: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    thinking_tokens: int = 0
    answer_tokens: int | None = None
    ttft_s: float | None = None   # first token of any kind (thinking or answer)
    ttfa_s: float | None = None   # first answer token: what you actually wait for
    wall_s: float = 0.0
    prefill_ms: float | None = None
    prefill_tok_s: float | None = None
    decode_tok_s: float | None = None
    fingerprint: str | None = None  # e.g. "b11157-53ed051ce"
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def request_body(prompt: str, *, thinking: bool, sampling: dict, max_tokens: int,
                 stream: bool = True) -> dict:
    body = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "cache_prompt": False,  # every repeat pays full prefill, so repeats compare
        "chat_template_kwargs": {"enable_thinking": thinking},
        "stream": stream,
        **sampling,
    }
    if stream:
        body["stream_options"] = {"include_usage": True}
    return body


@dataclass
class TurnResult:
    """One model turn of an agent conversation (LOCAL_LLM_LAB.md 9.11: fields verified on b11321)."""
    content: str = ""
    reasoning: str | None = None
    tool_calls: list[dict] | None = None  # [{"id", "name", "arguments": raw JSON text}]
    finish_reason: str | None = None      # "tool_calls", "stop" or "length"
    prompt_tokens: int | None = None
    cached_tokens: int | None = None
    completion_tokens: int | None = None
    thinking_tokens: int = 0
    wall_s: float = 0.0
    decode_tok_s: float | None = None
    error: str | None = None


def chat_turn(base_url: str, messages: list[dict], *, tools: list[dict], thinking: bool, sampling: dict,
              max_tokens: int, timeout_s: float) -> TurnResult:
    """Send the whole conversation with tool definitions; collect text, thinking and tool calls.
    Tool calls arrive as `delta.tool_calls` pieces: the first piece of each call carries `id` and
    `function.name`, every piece adds to `function.arguments`; pieces of one call share `index`.
    `cache_prompt` is on here (unlike `chat`): an agent re-sends the conversation every turn, and
    real agent tools rely on the server reusing the part it has already processed."""
    res = TurnResult()
    content: list[str] = []
    reasoning: list[str] = []
    calls: dict[int, dict] = {}
    usage: dict = {}
    timings: dict = {}
    body = {
        "messages": messages, "tools": tools, "parallel_tool_calls": True,
        "max_tokens": max_tokens, "cache_prompt": True,
        "chat_template_kwargs": {"enable_thinking": thinking},
        "stream": True, "stream_options": {"include_usage": True},
        **sampling,
    }
    t0 = time.perf_counter()
    try:
        with requests.post(f"{base_url}/v1/chat/completions", json=body, stream=True,
                           timeout=(10, timeout_s)) as r:
            if r.status_code != 200:
                res.error = f"HTTP {r.status_code}: {r.text[:500]}"
                return res
            for line in r.iter_lines():
                if time.perf_counter() - t0 > timeout_s:
                    res.error = f"timeout after {timeout_s:.0f}s"
                    break
                if not line.startswith(b"data: "):
                    continue
                data = line[6:]
                if data == b"[DONE]":
                    break
                chunk = json.loads(data.decode("utf-8"))
                if "error" in chunk:
                    res.error = json.dumps(chunk["error"])[:500]
                    break
                for choice in chunk.get("choices", []):
                    delta = choice.get("delta") or {}
                    if piece := delta.get("reasoning_content"):
                        reasoning.append(piece)
                        res.thinking_tokens += 1
                    if piece := delta.get("content"):
                        content.append(piece)
                    for tc in delta.get("tool_calls") or []:
                        call = calls.setdefault(tc.get("index", 0), {"id": None, "name": "", "arguments": ""})
                        fn = tc.get("function") or {}
                        call["id"] = tc.get("id") or call["id"]
                        call["name"] += fn.get("name") or ""
                        call["arguments"] += fn.get("arguments") or ""
                    if choice.get("finish_reason"):
                        res.finish_reason = choice["finish_reason"]
                usage = chunk.get("usage") or usage
                timings = chunk.get("timings") or timings
    except requests.RequestException as e:
        res.error = f"{type(e).__name__}: {e}"[:500]
    res.wall_s = round(time.perf_counter() - t0, 3)
    res.content = "".join(content)
    res.reasoning = "".join(reasoning) if reasoning else None
    res.tool_calls = [calls[i] for i in sorted(calls)] or None
    res.prompt_tokens = usage.get("prompt_tokens")
    res.cached_tokens = (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
    res.completion_tokens = usage.get("completion_tokens")
    res.decode_tok_s = timings.get("predicted_per_second")
    return res


def chat(base_url: str, prompt: str, *, thinking: bool, sampling: dict, max_tokens: int,
         timeout_s: float) -> ChatResult:
    res = ChatResult()
    answer_parts: list[str] = []
    reasoning_parts: list[str] = []
    usage: dict = {}
    timings: dict = {}
    body = request_body(prompt, thinking=thinking, sampling=sampling, max_tokens=max_tokens)
    t0 = time.perf_counter()
    try:
        with requests.post(f"{base_url}/v1/chat/completions", json=body, stream=True,
                           timeout=(10, timeout_s)) as r:
            if r.status_code != 200:
                res.error = f"HTTP {r.status_code}: {r.text[:500]}"
                return res
            for line in r.iter_lines():  # bytes; decoded as UTF-8 below
                now = time.perf_counter() - t0
                if now > timeout_s:
                    res.error = f"timeout after {timeout_s:.0f}s"
                    break
                if not line.startswith(b"data: "):
                    continue
                data = line[6:]
                if data == b"[DONE]":
                    break
                chunk = json.loads(data.decode("utf-8"))
                if "error" in chunk:
                    res.error = json.dumps(chunk["error"])[:500]
                    break
                res.fingerprint = chunk.get("system_fingerprint", res.fingerprint)
                for choice in chunk.get("choices", []):
                    delta = choice.get("delta") or {}
                    if piece := delta.get("reasoning_content"):
                        reasoning_parts.append(piece)
                        res.thinking_tokens += 1
                        if res.ttft_s is None:
                            res.ttft_s = now
                    if piece := delta.get("content"):
                        answer_parts.append(piece)
                        if res.ttft_s is None:
                            res.ttft_s = now
                        if res.ttfa_s is None:
                            res.ttfa_s = now
                    if choice.get("finish_reason"):
                        res.finish_reason = choice["finish_reason"]
                usage = chunk.get("usage") or usage
                timings = chunk.get("timings") or timings
    except requests.RequestException as e:
        res.error = f"{type(e).__name__}: {e}"[:500]
    res.wall_s = time.perf_counter() - t0
    res.answer = "".join(answer_parts)
    res.reasoning = "".join(reasoning_parts) if reasoning_parts else None
    res.prompt_tokens = usage.get("prompt_tokens")
    res.completion_tokens = usage.get("completion_tokens")
    if res.completion_tokens is not None:
        res.answer_tokens = res.completion_tokens - res.thinking_tokens
    res.prefill_ms = timings.get("prompt_ms")
    res.prefill_tok_s = timings.get("prompt_per_second")
    res.decode_tok_s = timings.get("predicted_per_second")
    for key in ("ttft_s", "ttfa_s", "wall_s"):
        if (v := getattr(res, key)) is not None:
            setattr(res, key, round(v, 3))
    return res
