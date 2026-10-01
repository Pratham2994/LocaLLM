# Local LLM Lab: harness project

The master file is `LOCAL_LLM_LAB.md` (imported below). It is the single source of truth:
status board, hardware facts, measured findings, the harness spec (section 7) and the change log.
**Keep it updated after every completed step** (tick the status board, bump version / "Last
updated", add measured numbers to section 9, add a change-log line). Never delete measured results;
strike them through and add the new value.

@LOCAL_LLM_LAB.md

**New machine (PC)?** Follow `LOCAL_LLM_LAB.md` section 11.0 (migration runbook). Fill `hostname` in `configs/machines/pc.yaml` first, or the harness cannot pick a machine file.

## Harness quick reference

```powershell
uv run lab tasks                     # list tasks
uv run lab selftest                  # every reference answer passes, every wrong answer fails
uv run lab run --dry-run             # plan + exact llama-server command, starts nothing
uv run lab run configs\<name>.yaml   # run (resumable; default = all configs\*.yaml)
uv run lab run configs\x.yaml --tasks "sql-*" --repeats 1
uv run lab probe configs\x.yaml      # raw JSON of one request: do this after any llama.cpp update
uv run lab report                    # results\report.md + results\charts\*.png (correct answers/hour etc.)
uv run lab needle configs\x.yaml --sizes 4096 16384 32768 --depths 0.1 0.5 0.9
uv run lab bench configs\x.yaml --pp 512 --tg 128 --depth 0,4096
```

While a run is in progress, `uv run` may fail to reinstall `lab.exe` (locked); use `uv run --no-sync ...`.

## Layout

- `configs/machines/<name>.yaml`: machine facts (backend folders, best `-t`, `-ngl`, model folders,
  port, tools). Picked by hostname. **On the PC, add `pc.yaml`; nothing else should change.**
- `configs/presets/sampling.yaml`: sampling presets (Qwen3.5 model card values).
- `configs/*.yaml`: one experiment each (model, backend, ctx, KV type, thinking, sampling, repeats).
  `configs/archive/`: configs whose model files were deleted (not loaded; results kept in `runs.jsonl`).
- `tasks/tasks.yaml`: the task set. Every auto-checked task has a `reference` (must pass) and
  ideally a `wrong` answer (must fail). Run `uv run lab selftest` after editing tasks.
- `src/lab/`: `config.py` (YAML loading, server command), `server.py` (start/health/log parsing),
  `client.py` (streamed request + timings), `checks.py` (graders + sandbox), `runner.py`
  (resumable loop), `report.py`, `needle.py`, `bench.py`, `cli.py`.
- `results/runs.jsonl`, `needle.jsonl`, `bench.jsonl`: append-only, committed to git.
  `results/report.md` + `results/charts/`: generated, committed. `results/logs/`: server logs, not committed.

## Rules that are easy to break

- Every server start: `--port`, `-t <machine value>`, `-np 1`, `--cache-ram 0`, `-lv 4`.
  Every request: explicit sampling, `"cache_prompt": false`. (`RunConfig.server_command`,
  `client.request_body`.)
- Do not trust a response field without seeing it in real JSON (`lab probe`).
- Model-written code runs only through `checks.py` (temp folder, timeout, guards).
- Smart App Control is ON on the laptop: it randomly blocks freshly compiled C++ test programs.
  Those runs are stored as `passed: null` (not graded), never as failures.
- Task YAML: bare `on`/`off` are booleans in YAML; the loader accepts both spellings.
- Made-up code and data only. Never work (Barclays) code.
- Windows + PowerShell, Python 3.14 via uv (`uv add`, `uv run`), never pip in the project.
- British English in reports. Explain commands in 1-2 plain sentences (Pratham is learning).
