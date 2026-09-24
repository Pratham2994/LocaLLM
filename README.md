# lab: local LLM test harness

Compares local models, quants and settings on my own tasks, measuring **correct answers per
hour**, not just tokens per second. Drives `llama-server` (llama.cpp) through its
OpenAI-compatible API. Full context, measurements and plan: [`LOCAL_LLM_LAB.md`](LOCAL_LLM_LAB.md).

```powershell
uv sync
uv run lab selftest                                   # prove the task checks work
uv run lab run configs\qwen35-4b-q4km-vulkan-nothink.yaml --dry-run
uv run lab run configs\qwen35-4b-q4km-vulkan-nothink.yaml
```

- **Configs** (`configs/`): one YAML file per experiment. Machine-specific paths and thread counts
  live in `configs/machines/<name>.yaml`, so moving to another machine means adding one file.
- **Tasks** (`tasks/tasks.yaml`): 24 tasks in Python, JavaScript, SQL and C++ (small service
  functions, bug fixes, SQL, maths, instruction following, summaries). Checked by running tests,
  comparing SQL result rows, JSON/regex/exact matching, or by hand.
- **Results** (`results/runs.jsonl`): one JSON line per run with the answer, pass/fail, token
  counts (thinking vs answer), time to first token, time to first answer token, prefill and
  decode speed, and llama-server buffer sizes. Runs are resumable and never overwritten.

Needs: Python 3.14 + uv, llama.cpp release binaries, Node.js (JS tasks), g++ (C++ tasks).
