# LocaLLM

Which local model is worth running on one 12 GB graphics card? I measured it.

This is the test harness, the tasks, and the results. It compares local models, quants
and settings on my own tasks, and it counts **correct answers per hour**, not only tokens
per second. It drives `llama-server` (llama.cpp) through its OpenAI-compatible API.

## What I found

On an RTX 5070 with 12 GB, over 4,101 runs:

| Model | Runs right | Correct per hour |
| --- | --- | --- |
| Gemma 4 12B coder | 131 of 165 | 1,588 |
| Gemma 4 12B | 143 of 165 | 1,519 |
| Gemma 4 E4B | 115 of 165 | 1,357 |
| Gemma 4 26B-A4B | 154 of 165 | 808 |
| Qwen3.6-35B-A3B | 145 of 165 | 613 |

All five ran with the MTP draft head and thinking off. The full table, with 41 configs,
is in [`results/report.md`](results/report.md).

- **The biggest model is the most correct. A smaller one gets more done per hour.** Those
  are two different winners, which is why the harness reports both.
- **A model that keeps some of its experts in system RAM beats a dense model squeezed to
  fit the card,** in quality and in speed.
- **Fine-tunes did not help.** Of six, five scored below the model they came from, and
  one was equal.
- **Thinking costs 6 to 12 times the time.** It is worth it for a retry or a hard bug,
  not as the default.
- **None of them replaces a hosted frontier model yet.** That is the verdict the project
  closed on.

The whole story, with every measurement and decision, is in
[`LOCAL_LLM_LAB.md`](LOCAL_LLM_LAB.md).

## How it works

```powershell
uv sync
uv run lab selftest                                   # prove the task checks work
uv run lab run configs\qwen35-4b-q4km-vulkan-nothink.yaml --dry-run
uv run lab run configs\qwen35-4b-q4km-vulkan-nothink.yaml
uv run lab report                                     # write results\report.md and the charts
```

| Command | What it does |
| --- | --- |
| `lab run` | Starts the server with one config, runs every task, checks each answer. Can be stopped and started again |
| `lab selftest` | Checks that each task's reference answer passes and a wrong answer fails |
| `lab report` | Writes the report and charts from the log |
| `lab needle` | Hides one fact in a long text and asks for it, at several context sizes |
| `lab bench` | Runs `llama-bench` with each config's model, backend and threads |
| `lab agent` | The agent tier: tool calls and small repository tasks |
| `lab probe` | Starts one server and prints one raw JSON response |

- **Configs** (`configs/`): one YAML file per experiment. Paths and thread counts for a
  machine are in `configs/machines/<name>.yaml`, so a new machine needs one new file.
- **Tasks** (`tasks/tasks.yaml`): 34 tasks in Python, JavaScript, SQL and C++. They are
  small service functions, bug fixes, SQL, maths, instruction following and summaries.
  33 are checked by a program: it runs the tests, compares the rows the SQL gives back,
  or matches JSON, a pattern or exact text. One is checked by hand.
- **Agent tasks** (`tasks/agent.yaml`): 43 tasks with tools, some in a made-up project.
- **Results** (`results/runs.jsonl`): one JSON line per run, with the answer, pass or
  fail, token counts (thinking and answer), time to the first token, prefill and decode
  speed, and the server's buffer sizes. Runs are never overwritten.

All code, names and data in the tasks are invented.

## Needs

Python 3.14 with uv, the llama.cpp release binaries, Node.js for the JavaScript tasks,
and g++ for the C++ tasks.
