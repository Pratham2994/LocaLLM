# Local LLM Lab: Master File

> **Version:** 29 · **Last updated:** 2026-09-25 · **Owner:** Pratham
> **Current machine:** Laptop (ASUS Zenbook 14) · **Current phase:** 4 done (harness complete); 5 next (3 repeats per task)

This one file holds everything: status, plan, commands, hardware facts, model choices, research notes, and the spec for the test harness. It is written so that a human **or** Claude Code can pick it up and continue with no other context.

---

## 0. How to use this file

### For Pratham
1. Keep this file open while you work. The **Status board** (section 1) tells you where you are and what to do next.
2. After each step, tick the box and write your numbers in **Findings** (section 9).
3. When you switch to Claude Code, put this file in `D:\Code\Inference\lab\` and start with:
   > Read `LOCAL_LLM_LAB.md` fully. You are taking over this project. Follow section 0 "For Claude Code". Start from the first unticked item in the Status board.
4. ~~Optional: copy it to `D:\Code\Inference\lab\CLAUDE.md` too.~~ Done differently (v22): `CLAUDE.md` holds the harness quick reference and **imports** this file (`@LOCAL_LLM_LAB.md`), so Claude Code loads it every session and there is no second copy to drift.

### For Claude Code (read this before doing anything)
You are continuing a learning project on running LLMs locally. Rules:

1. **This file is the single source of truth.** Read all of it before acting.
2. **Keep it updated.** After every completed step:
   - tick the box in section 1 (Status board),
   - update "Current phase" and "Last updated" in the header,
   - add real measured numbers to section 9 (Findings),
   - add a dated line to section 14 (Change log).
   Never delete measured results. If a result is replaced, strike it through and add the new one.
3. **Verify before trusting.** Many numbers here are estimates and are marked "(est.)". Replace them with measurements. Before relying on any API response field, make one real request and inspect the JSON.
4. **Environment:** Windows 11, PowerShell, Python 3.14 managed with **uv** (`uv add`, `uv run`). Never use pip inside the project. `huggingface_hub` is installed globally with pip; `hf` is on PATH.
5. **Explain as you go.** Pratham is learning. When you run a command, say in 1-2 plain sentences what it does and what the output means. Short sentences, simple words.
6. **Ask before** deleting files, installing system-wide software, or anything that needs admin rights.
7. **Never** put work (Barclays) code or data in test tasks. Use made-up code.
8. If the user reports results from another chat, merge them into section 9 and the Status board.

---

## 1. Status board

### Done
- [x] Python 3.14 installed (via Python install manager; Scripts folder added to PATH manually)
- [x] `pip install -U huggingface_hub` (hf 1.32.0), `hf --help` works
- [x] LM Studio installed
- [x] ODS (Osmantic) tried, then fully uninstalled (see section 12.3)

- [x] Qwen3.5-4B Q4_K_M (unsloth) downloaded in LM Studio
- [x] Model loads and answers on **CPU** runtime
- [x] Vulkan (iGPU) runtime tested: **crashes on load** with both Vulkan 2.43.0 and 2.40.0 (see 9.2)

### In progress
- [x] Phase 1 A/B test CPU vs Vulkan (palindrome, Think off): **Vulkan wins overall** (see 9.2)
- [x] Phase 1 rest on Vulkan, on charger: all 4 questions, Think off and on, correctness recorded (see 9.2)
- [x] llama.cpp CPU and Vulkan zips downloaded and unzipped into `D:\Code\Inference\llama-cpu` and `llama-vulkan`
- [x] Phase 2 first direct run on Vulkan (see 9.3)
- [x] Phase 2 complete: buffers read, Vulkan vs CPU with `-t 5` (see 9.3)
- [x] Phase 3 part 1: thread sweeps (CPU and Vulkan) and prefill curves (see 9.4)
- [x] Phase 3 part 2: size ladder incl. Gemma 4 E4B and Bonsai 27B v1, both engines (see 9.4)
- [x] Phase 3 part 3: depth test (see 9.4). **Phase 3 complete**
- [x] **Phase 4: build the harness in Claude Code** (section 6, Phase 4; spec in section 7): all 5 milestones built and tested
  - [x] API probe: raw JSON of thinking off/on and streaming inspected; fields agreed (9.4a)
  - [x] Milestone 1: `tasks/tasks.yaml`, 24 tasks (Python, JS, SQL, a little C++); `lab selftest` passes
  - [x] Milestone 2: `uv run lab run` (resumable, `results/runs.jsonl`); thinking-off run done (9.4a)
  - [x] Verify the thinking-on path end to end (first attempt stopped: laptop low on memory; second, with apps closed: PASS, all fields correct; 9.4a)
  - [x] Full thinking-on set (8 tasks × 1): 7/8 in 36.4 min vs thinking off 5/8 in 2.3 min (9.4a)
  - [x] Milestone 3: `uv run lab report` (tested on real results)
  - [x] Milestone 4 `lab needle`: tested at 4K / 16K / 32K (found / found / GPU crash; 9.6)
  - [x] Milestone 5 `lab bench`: tested; answered the batch-size question (hypothesis rejected; 9.4a)
  - [x] Model comparison, 7 configs, thinking off, 1 repeat (9.4b), incl. Qwen3.5-4B Q8_0
  - [ ] Pratham: read the task list, add or change tasks (section 8)
- [x] `hf` downloads complete (9 files in `D:\Code\Inference\models`, sizes in 5.1). Fix that worked: Cloudflare WARP + exact-file-name script (5.2)
- [x] LM Studio downloads: `google/gemma-4-e4b` (6.33 GB total) and `prism-ml/bonsai-27b` (4.73 GB total). Totals likely include vision/audio files; confirm file names, quant, and that Bonsai is the Qwen3.6-based v1 (see 5.2 command)
- [x] llama.cpp build **11157** (commit 53ed051ce, version 0.5.0-dev). Vulkan build sees `Vulkan0: Intel(R) Arc(TM) 130T GPU (8GB) (8972 MiB, 8267 MiB free)`

### Next actions (in order)
1. [ ] Phase 0.1: Intel graphics driver update + reboot
2. [ ] Phase 0.2: power settings
3. [ ] Phase 0.3: note idle RAM "In use"
4. [ ] Phase 0.4: create folders
5. [x] Phase 0.5: `hf` downloads (done)
6. [x] Phase 0.6: LM Studio downloads #2 and #3 (done; file check pending)
7. [ ] Phase 1: LM Studio tests on CPU (in progress)
8. [ ] Retest Vulkan once after the Intel driver update (Phase 0.1)

### Phase checklist

| Phase | Name | Status |
|---|---|---|
| 0 | Prepare | In progress |
| 1 | LM Studio first tests | Done (Vulkan default, Think off default) |
| 2 | llama.cpp first run | Done |
| 3 | Speed tests (llama-bench) | Done |
| 4 | Build test harness (Claude Code) | Done (5 milestones; provisional verdict in 9.8) |
| 5 | Quality tests | Not started |
| 6 | Memory / context tests | Not started |
| 7 | Bigger model vs more bits + laptop verdict | Not started |
| 8 | Prepare for PC | Not started |
| 9+ | PC phases (section 11) | After the laptop week |

---

## 2. Goal and context

**Who:** Pratham, software engineer (Barclays). New to local LLMs. Wants to learn inference engines, quantisation, model sizes, and how to pick and run open models well.

**Goal of the laptop week:** learn the **method** (measure speed, quality, memory; build a reusable harness). Not to find the final model.

**Goal on the PC (after the week):** run the best model that fits 12 GB VRAM for real coding help, chosen by evidence from the harness.

**Core principle:** judge models by **correct answers per hour on my own tasks**, not by tokens/sec and not by tweets or vendor benchmarks.

**Constraints:**
- Laptop available now; PC not available for about one week.
- Windows 11 on both. PowerShell.
- Python 3.14 + uv. `hf` CLI installed via pip.
- British English in all written reports.
- **Base folder for everything: `D:\Code\Inference\`** (not C:). All paths in this file use it.

---

## 3. Hardware facts

### 3.1 Laptop (current machine)

| Item | Value | Notes |
|---|---|---|
| Model | ASUS Zenbook 14 (UX3405CA class) | |
| CPU | Intel Core Ultra 5 225H (Arrow Lake H) | 14 cores: 4 performance + 8 efficiency + 2 low-power efficiency. No hyper-threading |
| iGPU | Intel Arc 130T (Xe2) | Shares system RAM |
| RAM | 16 GB LPDDR5X, soldered, shared by CPU and iGPU | ~119 GB/s theoretical (est. from ~7,467 MT/s × 128-bit) |
| Usable for model + KV cache | ~9-10 GB (est.) | = 16 − idle "In use" − 1 GB margin. Measure in Phase 0.3 |
| Disk | ~563 GB free | |
| NPU | 13 TOPS | Not used by llama.cpp |

**Known laptop issues:**
- **Vulkan garbage output:** Arrow Lake iGPUs can produce garbage text with the Vulkan backend on models 3B+ (llama.cpp issue #19327). Always compare iGPU answers with CPU answers.
- **Confirmed on this laptop (2026-09-23):** in **LM Studio Bionic**, Vulkan runtimes (2.43.0, 2.40.0) crash when loading Qwen3.5-4B. In **plain LM Studio**, Vulkan 2.43.0 loads and runs it (GPU offload 32/32). Cause unknown. (Earlier guess "Bionic loads a vision file" is unlikely for Qwen, because no `mmproj` was downloaded for it; a larger context or different settings in Bionic remain possible.)
- **LM Studio Hardware page:** CPU instruction sets shown: x86_64, AVX, AVX2. RAM 15.37 GB. Intel Arc 130T detected via Vulkan with **"VRAM" 8.76 GB**. This is not extra memory: it is the part of the same 15.37 GB that Windows lets the iGPU use. Total memory for everything is still ~15.4 GB.
- **Slower prompt processing on iGPU:** the related Arc 140T reports "matrix cores: none" on Windows because of a driver/detection mismatch (llama.cpp issue #20776). The 130T may behave the same.
- **Smart App Control is ON** (`VerifiedAndReputablePolicyState = 1`, checked 2026-09-24). It blocks some freshly compiled unsigned programs (`WinError 4551`, Code Integrity events 3077/3118), so the harness's C++ test programs sometimes cannot run. llama.cpp, Node, Python and g++ itself run fine.
- **Heat:** thin laptop slows down when hot. Always plugged in, Best performance mode, Performance fan profile.
- **Decode speed on laptop is memory-bound:** CPU and iGPU read the same RAM at the same speed, so iGPU mainly helps prefill, not decode (est.; Phase 3 measures it).

### 3.2 PC (available after the laptop week)

| Item | Value | Notes |
|---|---|---|
| GPU | NVIDIA RTX 5070, 12 GB GDDR7 | ~672 GB/s. Blackwell consumer, compute capability sm_120 (same family as RTX 5090) |
| CPU | Intel Core Ultra 7 265K | Has an iGPU |
| RAM | 32 GB DDR5 | ~80-100 GB/s (est.) |

**PC tips:**
- Plug the monitor into the **motherboard** (iGPU), not the 5070. This frees the full 12 GB VRAM (Windows desktop otherwise takes 0.5-1 GB).
- RTX 50 cards need CUDA 12.8 or newer builds. Pick the newest CUDA zip on the llama.cpp releases page.

---

## 4. Key concepts (cheat sheet)

**How a token is made.** Text → tokens (IDs) → embedding lookup (each ID becomes a list of numbers) → N layers (attention: look at earlier tokens; MLP: apply stored knowledge) → output head (score every vocabulary token) → sampling picks one → repeat. The last position's scores predict the next token because training taught every position to predict the next one, and the causal mask stops positions seeing the future.

**Prefill vs decode.**
- Prefill = reading the prompt. All prompt tokens go through together. Limited by compute. Measured as `pp512` in llama-bench.
- Decode = writing the answer, one token at a time. Every token must read all weights from memory. Limited by memory bandwidth. Measured as `tg128`.

**Decode speed rule:** tokens/sec ≈ memory bandwidth ÷ bytes read per token (≈ model file size). Real engines reach ~60-70% of this.

**File size rule:** GB ≈ parameters (billions) × bits per weight ÷ 8.
- Real bits are higher than the name: Q8_0 = 8.5, Q4_K_M ≈ 4.8-5.2, because of block scales and some tensors kept at higher precision. Small models look "bigger than expected" because the embedding/output table is a larger share (Qwen3.5-4B: 636M of 4.21B numbers).

**KV cache.** Stored keys and values of earlier tokens, per layer. Grows with context. Reserved up front by `-c`.
- Per token = 2 × (full-attention layers) × (KV heads) × (head size) × (bytes per number).
- Qwen3.5-4B: 2 × 8 × 4 × 256 × 2 bytes = **32 KB/token at f16** → 32K context ≈ 1 GB. Hybrid design: only 8 of 32 layers keep a full cache.
- Phi-4-mini: 2 × 32 × 8 × 128 × 2 = **128 KB/token at f16** → 128K context ≈ 16.8 GB.
- `-ctk q8_0 -ctv q8_0` halves the cache; q4_0 quarters it but can hurt long tasks.

**Quantisation.** Round each weight to a few allowed levels using a shared scale per block. Fewer bits = smaller, faster, less accurate. 8-bit ≈ lossless; 4-bit = standard trade-off; below 3 bits needs smart methods (I-quants, imatrix, mixed precision like Unsloth UD or GSQ-RCO) or models trained for it (QAT, ternary). Always quantise from the original, never 8-bit → 4-bit.

**Reading llama-server timing lines** (LM Studio Developer tab or llama-server console):
- `prompt eval time = X ms / N tokens (... tokens per second)` → **prefill** speed.
- `eval time = X ms / N tokens (... tokens per second)` → **decode** speed.
- `total time` → both together. `graphs reused` → how often a prepared compute graph was reused (higher is normal and good).
- Ignore the first request after loading: it includes one-time warm-up. Measure on the 2nd+ request, with a longer answer (100+ tokens).
- Device lines (`... model buffer size`, showing CPU or Vulkan0) appear only at a detailed log level.

**Thinking mode.** Reasoning models write hidden "thinking" tokens before answering. On a slow machine this can cost minutes. Turn it off for quick tasks.

**MoE (Mixture of Experts).** Huge total size, small active part per token. Lets big models run on small GPUs by keeping experts in system RAM (`--n-cpu-moe`).

---

## 5. Models

### 5.1 Laptop model list

| # | Model | Quant | File size | Source | Role | Phase |
|---|---|---|---|---|---|---|
| 1 | Qwen3.5-4B | Q4_K_M | 2.74 GB | LM Studio: `unsloth/Qwen3.5-4B-GGUF` | Main learning model | 1-6 |
| 2 | Gemma 4 E4B (instruct, "it") | Q4_K_M | 5.34 GB (+0.99 GB vision `mmproj`, BF16) | LM Studio: `lmstudio-community/gemma-4-E4B-it-GGUF` | Community favourite for 16 GB; rival to #1 | 5, 7 |
| 3 | Bonsai 27B **v1** (Qwen3.6-based) | Q1_0 | 3.80 GB (+0.93 GB vision `mmproj`, BF16) | LM Studio: `lmstudio-community/Bonsai-27B-GGUF` | 27B at 1 bit vs 4B at 8 bits | 7 |
| 4 | Qwen3.5-0.8B | Q4_K_M | 0.53 GB | hf | Speed ladder | 3 |
| 5 | Qwen3.5-2B | Q4_K_M | 1.28 GB | hf | Speed ladder | 3 |
| 6 | Qwen3.5-9B | Q4_K_M | 5.68 GB | hf | Speed ladder; best Qwen that fits | 3, 6, 7 |
| 7 | Qwen3.5-4B | Q8_0 | 4.48 GB | hf | Quality ladder | 5, 7 |
| 8 | Qwen3.5-4B | Q6_K | 3.53 GB | hf | Quality ladder | 5 |
| 9 | Qwen3.5-4B | Q3_K_M | 2.29 GB | hf | Quality ladder | 5 |
| 10 | Qwen3.5-4B | UD-IQ2_XXS | 1.52 GB | hf | Quality ladder | 5 |
| 11 | Qwen3.5-9B | Q3_K_M | 4.67 GB | hf | Same size as #7: bigger-model-fewer-bits test | 7 |
| 12 | Phi-4-mini-instruct | Q4_K_M | 2.49 GB | hf | ODS's pick; fair comparison | 5 |

**Why these:**
- Qwen3.5 small models (Mar 2026) are the newest small Qwens. Qwen3.6/3.8 only have 27B and 35B-A3B. Qwen's card shows Qwen3.5-4B roughly matching the old Qwen3-30B-A3B-Thinking-2507 (MMLU-Pro 79.1 vs 80.9; GPQA Diamond 76.2 vs 73.4).
- Use **unsloth** files: re-issued with improved quantisation and new imatrix data; same files in LM Studio and llama.cpp so results compare.
- Use **Q4_K_M**, not LM Studio's "Recommended" Q4_K_S (a memory-fit guess, not a quality pick). K-quants are faster than I-quants on CPU.
- **Skip:** old Qwen3 / Qwen2.5 models, "Uncensored/abliterated/Heretic/NSFW" and random community fine-tunes (unknown quality, usually worse), lmstudio-community Qwen3.5 (older build b8185).
- **LM Studio size note (corrected):** LM Studio's size for unsloth Qwen3.5-4B showed ~1.34 GB more than the model file, but the file listing shows **no `mmproj` was downloaded for Qwen** (only the 2.74 GB model). So Qwen RAM numbers in Phase 1 include no vision file; ignore the earlier "subtract ~1.3 GB" advice. Gemma 4 E4B and Bonsai **did** get `mmproj` files (BF16), which LM Studio may load with the model.
- **Model file paths in LM Studio's folder** (for llama.cpp commands; do **not** pass the `mmproj` files):
  - `C:\Users\prath\.lmstudio\models\unsloth\Qwen3.5-4B-GGUF\Qwen3.5-4B-Q4_K_M.gguf`
  - `C:\Users\prath\.lmstudio\models\lmstudio-community\gemma-4-E4B-it-GGUF\gemma-4-E4B-it-Q4_K_M.gguf`
  - `C:\Users\prath\.lmstudio\models\lmstudio-community\Bonsai-27B-GGUF\Bonsai-27B-Q1_0.gguf`
- **Size check, Bonsai Q1_0:** 1 bit per weight + one 16-bit scale per block of 128 = 1.125 bits; 27B × 1.125 ÷ 8 ≈ 3.8 GB, matching the file. PrismML's "~3.5 GB" is the same size in GiB (3.8 × 10⁹ bytes ≈ 3.54 GiB).

### 5.2 Download commands

**LM Studio (models #1-3):** search tab → type the repo name → choose the quant in the dropdown → Download. Check the model files' folder in LM Studio → My Models (usually under `C:\Users\prath\.lmstudio\models\`). llama.cpp can load those same files.

Optional: to keep everything on D:, change LM Studio's models folder to `D:\Code\Inference\lmstudio-models` (LM Studio → My Models → models directory setting; menu names vary by version). LM Studio moves or re-finds the models there. If you do this, update model paths in Phase 2-3 commands and harness configs.

**hf (models #4-12), PowerShell:**

```powershell
cd D:\Code\Inference\models
$dl = @(
  @("unsloth/Qwen3.5-0.8B-GGUF", "*-Q4_K_M.gguf"),
  @("unsloth/Qwen3.5-2B-GGUF",   "*-Q4_K_M.gguf"),
  @("unsloth/Qwen3.5-9B-GGUF",   "*-Q4_K_M.gguf"),
  @("unsloth/Qwen3.5-4B-GGUF",   "*-Q8_0.gguf"),
  @("unsloth/Qwen3.5-4B-GGUF",   "*-Q6_K.gguf"),
  @("unsloth/Qwen3.5-4B-GGUF",   "*-Q3_K_M.gguf"),
  @("unsloth/Qwen3.5-4B-GGUF",   "*UD-IQ2_XXS*"),
  @("unsloth/Qwen3.5-9B-GGUF",   "*-Q3_K_M.gguf"),
  @("unsloth/Phi-4-mini-instruct-GGUF", "*-Q4_K_M.gguf")
)
foreach ($d in $dl) { hf download $d[0] --include $d[1] --local-dir . }
```

- If the internet drops: run the `foreach` line again; `hf` resumes.
- If a repo name fails: search it on huggingface.co, open "Files", copy the exact repo name.
- Do **not** download `mmproj` files (vision) for this project.
- **`hf` can print "✓ Downloaded" even when the network failed.** Always check the files exist (command below).
- **Network diagnosis (home Wi-Fi resets Hugging Face connections):** run each 3-4 times and compare:
  ```powershell
  curl.exe -4 -sS -o NUL -w "IPv4: %{http_code}\n" https://huggingface.co/api/models/unsloth/Qwen3.5-2B-GGUF
  curl.exe -6 -sS -o NUL -w "IPv6: %{http_code}\n" https://huggingface.co/api/models/unsloth/Qwen3.5-2B-GGUF
  ```
  `200` = works. If only IPv6 fails: prefer IPv4 (turn off IPv6 on the Wi-Fi adapter). If both fail randomly: use Cloudflare WARP (WARP mode) for downloads.
- **Final download script (exact file names, retries, verifies).** Pattern downloads (`--include "*-Q4_K_M.gguf"`) kept returning "Fetching 0 files" on this network even though the file exists, so this script asks for each **exact file name**. That uses a direct single-file download with no file listing, and a wrong name gives a clear error instead of a silent "✓". Keep WARP on.
  ```powershell
  cd D:\Code\Inference\models
  $files = @(
    @("unsloth/Qwen3.5-2B-GGUF",          "Qwen3.5-2B-Q4_K_M.gguf"),
    @("unsloth/Qwen3.5-9B-GGUF",          "Qwen3.5-9B-Q4_K_M.gguf"),
    @("unsloth/Qwen3.5-4B-GGUF",          "Qwen3.5-4B-Q6_K.gguf"),
    @("unsloth/Qwen3.5-4B-GGUF",          "Qwen3.5-4B-Q3_K_M.gguf"),
    @("unsloth/Phi-4-mini-instruct-GGUF", "Phi-4-mini-instruct-Q4_K_M.gguf"),
    @("unsloth/Qwen3.5-0.8B-GGUF",        "Qwen3.5-0.8B-Q4_K_M.gguf"),
    @("unsloth/Qwen3.5-4B-GGUF",          "Qwen3.5-4B-Q8_0.gguf"),
    @("unsloth/Qwen3.5-4B-GGUF",          "Qwen3.5-4B-UD-IQ2_XXS.gguf"),
    @("unsloth/Qwen3.5-9B-GGUF",          "Qwen3.5-9B-Q3_K_M.gguf")
  )
  foreach ($f in $files) {
    $repo, $name = $f
    for ($i = 1; $i -le 8 -and -not (Test-Path $name); $i++) {
      Write-Host "[$i/8] $repo -> $name" -ForegroundColor Cyan
      hf download $repo $name --local-dir .
      if (-not (Test-Path $name)) { Start-Sleep -Seconds (5 * $i) }
    }
    if (Test-Path $name) { Write-Host "OK      $name" -ForegroundColor Green }
    else                 { Write-Host "MISSING $name" -ForegroundColor Red }
  }
  Get-ChildItem *.gguf | Select-Object Name, @{n='GB';e={[math]::Round($_.Length/1e9,2)}}
  ```
  - Files you already have are skipped (`Test-Path` finds them).
  - Unfinished downloads sit in `.cache` until complete, so a half-downloaded file never counts as done.
  - If a line ends `MISSING` with a "not found" error, the file name is different: list the repo's files with the `list_repo_files` command above and fix the name.
- To see the exact file names in a repo (if a pattern matches 0 files):
  ```powershell
  python -c "from huggingface_hub import list_repo_files as l; print([f for f in l('unsloth/Qwen3.5-2B-GGUF') if f.endswith('.gguf')])"
  ```

**List every model file LM Studio downloaded** (main model vs `mmproj` vision/audio files, and their quant):
```powershell
Get-ChildItem "$env:USERPROFILE\.lmstudio\models" -Recurse -Filter *.gguf | Select-Object @{n='File';e={$_.FullName.Replace("$env:USERPROFILE\.lmstudio\models\",'')}}, @{n='GB';e={[math]::Round($_.Length/1e9,2)}}
```

**Check sizes:**

```powershell
Get-ChildItem D:\Code\Inference\models -Filter *.gguf | Select-Object Name, @{n='GB';e={[math]::Round($_.Length/1e9,2)}}
```

### 5.3 Sampling settings

**Qwen3.5 (from the official model card):**

| Mode | temp | top_p | top_k | min_p | presence_penalty |
|---|---|---|---|---|---|
| Thinking, general | 1.0 | 0.95 | 20 | 0 | 1.5 |
| Thinking, precise coding | 0.6 | 0.95 | 20 | 0 | 0 |
| Non-thinking, general | 0.7 | 0.8 | 20 | 0 | 1.5 |
| Non-thinking, reasoning | 1.0 | 1.0 | 40 | 0 | 2.0 |

- Qwen3.5 thinks by default. Disable per request: `"chat_template_kwargs": {"enable_thinking": false}`. The `/think` and `/nothink` switches from Qwen3 are **not** supported.
- Recommended max output: 32,768 tokens for most queries.

**Gemma 4 E4B, Phi-4-mini, Bonsai v1:** use each model card's recommended settings (LM Studio usually loads them automatically). Record the values used in section 9.

**Never use temperature 0 for Qwen thinking models in quality tests** (greedy decoding tends to cause repetition loops). Use temperature 0 only for the CPU-vs-iGPU "same answer?" sanity check.

---

## 6. Laptop phases (detailed)

### Folder layout

```
D:\Code\Inference\llama-cpu       llama.cpp CPU build
D:\Code\Inference\llama-vulkan    llama.cpp Vulkan build (Intel iGPU)
D:\Code\Inference\models          GGUF files downloaded with hf
D:\Code\Inference\results         findings, llama-bench CSVs
D:\Code\Inference\lab             harness project (uv), this file
```

### Phase 0: Prepare (45 min)

1. **Intel driver:** download the latest "Intel Arc & Iris Xe Graphics" driver from intel.com, install, reboot.
2. **Power:** charger in. Windows Settings → System → Power → Power mode: **Best performance**. MyASUS → fan profile: **Performance**.
3. **Memory baseline:** after reboot, close everything, Task Manager → Performance → Memory. Note "In use". Budget = 16 − In use − 1 GB. Record in section 9.1.
4. **Folders:**
   ```powershell
   New-Item -ItemType Directory -Force D:\Code\Inference\llama-cpu, D:\Code\Inference\llama-vulkan, D:\Code\Inference\models, D:\Code\Inference\results, D:\Code\Inference\lab | Out-Null
   ```
5. **hf downloads:** run the block in section 5.2.
6. **LM Studio downloads:** models #2 and #3 from section 5.1.
7. **llama.cpp zips** (can do now): go to https://github.com/ggml-org/llama.cpp/releases, newest release, download `llama-bXXXX-bin-win-cpu-x64.zip` → unzip to `D:\Code\Inference\llama-cpu`; `llama-bXXXX-bin-win-vulkan-x64.zip` → unzip to `D:\Code\Inference\llama-vulkan`. If SmartScreen blocks an exe: "More info" → "Run anyway". Firewall prompt for `llama-server`: allow on private networks.

### Phase 1: LM Studio first tests (1 hour)

Model: Qwen3.5-4B Q4_K_M (unsloth).

**Use plain LM Studio chat, not LM Studio Bionic, for measurements.** Bionic is LM Studio's separate agent app. It sends a large agent prompt with tools on every request (a plain "hi" showed **Context: 6.8K** tokens and took **3 min 18 s** on CPU). That is mostly prefill of ~6.8K tokens plus thinking, not the model answering "hi". Plain chat gives clean numbers. Bionic is worth trying later as an agent, like Claude Code for local models.

**Runtime:** select **CPU llama.cpp** in the Runtime page (GGUF dropdown). Vulkan crashes on this laptop (see 9.2).

1. **CPU run.** Load with context length **8192**, GPU offload **0**. Ask:
   1. "What is 17 × 23? Answer with just the number." (correct: 391)
   2. "Write a Python function that checks if a string is a palindrome, ignoring spaces and case."
   3. "Explain what a hash map is in three sentences."

   After each, note **tok/s** and **time to first token** (shown under the reply).
2. **iGPU run.** Reload with GPU offload at **maximum** (Vulkan runtime). Same three questions. Is tok/s different? Are the answers **sane**? Nonsense = the Arrow Lake Vulkan bug; note it and use CPU.
3. **Thinking on vs off.** Ask: "A bat and a ball cost ₹110 in total. The bat costs ₹100 more than the ball. How much does the ball cost?" (correct: ₹5). Once with thinking on, once off. Note time and correctness.
4. **Memory.** Task Manager open on Memory and GPU ("Shared GPU memory"). Note the jump when the model loads. Subtract ~1.3 GB if LM Studio loaded the vision add-on.
5. Record everything in section 9.2.

### Phase 2: llama.cpp first run (1 hour)

1. **Check builds:**
   ```powershell
   cd D:\Code\Inference\llama-cpu;    .\llama-cli.exe --version
   cd D:\Code\Inference\llama-vulkan; .\llama-cli.exe --list-devices
   ```
   The Vulkan build should list the Intel Arc 130T. If not: driver problem.
2. **Start server on CPU** (use the real path of model #1; `-t 6` is a first guess until Phase 3):
   ```powershell
   cd D:\Code\Inference\llama-cpu
   .\llama-server.exe -m <path-to>\Qwen3.5-4B-Q4_K_M.gguf -c 8192 -t 6 --port 8080
   ```
3. **Read the log** before "server is listening". Record: `model buffer size` (weights), `KV buffer size` (cache for 8192 tokens), `compute buffer size` (scratch). Sum them and compare with Task Manager. Expected KV at 8192 tokens f16 ≈ 0.25 GB (32 KB × 8192).
4. **Use it:** open http://localhost:8080 (built-in chat page). Same three questions as Phase 1. Speed should be close to LM Studio (same engine inside).
5. **Vulkan run:** Ctrl+C, then:
   ```powershell
   cd D:\Code\Inference\llama-vulkan
   .\llama-server.exe -m <path-to>\Qwen3.5-4B-Q4_K_M.gguf -c 8192 -ngl 99 --port 8080
   ```
   Buffers should now say Vulkan. Check answers are sane.
6. Record in section 9.3.

### Phase 3: Speed tests with llama-bench (2 hours)

Close the browser and other apps before each run. Output columns: `pp512` = prefill speed on a 512-token prompt; `tg128` = decode speed over 128 tokens; `t/s` ± variation over repeats.

1. **Best thread count (CPU):**
   ```powershell
   cd D:\Code\Inference\llama-cpu
   .\llama-bench.exe -m <path-to>\Qwen3.5-4B-Q4_K_M.gguf -p 512 -n 128 -t 4,6,8,10,14 -r 3
   ```
   Expect tg128 to peak around 4-6 threads, then drop (efficiency cores slow the rest). Pick the best tg128 → call it **T**. Write it in section 9.4 and use it from now on.
2. **Size ladder (CPU):** (replace 6 with T; also add model #1's path by hand if it lives in LM Studio's folder)
   ```powershell
   Get-ChildItem D:\Code\Inference\models\*-Q4_K_M.gguf | ForEach-Object { .\llama-bench.exe -m $_.FullName -p 512 -n 128 -t 6 -r 3 -o csv | Out-File -Append -Encoding utf8 D:\Code\Inference\results\bench_cpu_sizes.csv }
   ```
2b. **Thread sweep on Vulkan too** (threads changed Vulkan prefill 4x in Phase 2):
   ```powershell
   cd D:\Code\Inference\llama-vulkan
   .\llama-bench.exe -m <path-to>\Qwen3.5-4B-Q4_K_M.gguf -ngl 99 -p 512 -n 128 -t 2,4,5,6,8,14 -r 3
   ```
2c. **Prefill curve** (is Vulkan slow only for small batches?), run in both folders (`-ngl 99` only for Vulkan):
   ```powershell
   .\llama-bench.exe -m <path-to>\Qwen3.5-4B-Q4_K_M.gguf -ngl 99 -t 5 -p 8,16,32,64,128,256,512 -n 0 -r 3
   ```
2d. **Size ladder with explicit file list** (preferred; includes LM Studio files):
   ```powershell
   $models = @(
     "D:\Code\Inference\models\Qwen3.5-0.8B-Q4_K_M.gguf",
     "D:\Code\Inference\models\Qwen3.5-2B-Q4_K_M.gguf",
     "C:\Users\prath\.lmstudio\models\unsloth\Qwen3.5-4B-GGUF\Qwen3.5-4B-Q4_K_M.gguf",
     "D:\Code\Inference\models\Qwen3.5-9B-Q4_K_M.gguf",
     "C:\Users\prath\.lmstudio\models\lmstudio-community\gemma-4-E4B-it-GGUF\gemma-4-E4B-it-Q4_K_M.gguf",
     "C:\Users\prath\.lmstudio\models\lmstudio-community\Bonsai-27B-GGUF\Bonsai-27B-Q1_0.gguf"
   )
   cd D:\Code\Inference\llama-vulkan
   foreach ($m in $models) { .\llama-bench.exe -m $m -ngl 99 -t 5 -p 512 -n 128 -r 3 }
   cd D:\Code\Inference\llama-cpu
   foreach ($m in $models) { .\llama-bench.exe -m $m -t 8 -p 512 -n 128 -r 3 }
   ```
3. **Size ladder (iGPU):**
   ```powershell
   cd D:\Code\Inference\llama-vulkan
   Get-ChildItem D:\Code\Inference\models\*-Q4_K_M.gguf | ForEach-Object { .\llama-bench.exe -m $_.FullName -p 512 -n 128 -ngl 99 -r 3 -o csv | Out-File -Append -Encoding utf8 D:\Code\Inference\results\bench_vulkan_sizes.csv }
   ```
4. **Depth test** (speed as the chat grows), with the faster backend:
   ```powershell
   .\llama-bench.exe -m <path-to>\Qwen3.5-4B-Q4_K_M.gguf -p 512 -n 64 -d 0,4096,16384 -t 6 -r 2
   ```
5. **Bandwidth check:** for each model, tg128 × file size (GB). If roughly constant across sizes, decode is memory-bound. That number is the laptop's effective bandwidth (max ~119 GB/s).

**Expected (est., CPU) — superseded by measurements in 9.4 (real speeds were ~30-40% lower):**

| Model Q4_K_M | Size | tg128 |
|---|---|---|
| 0.8B | 0.53 GB | 60-90 |
| 2B | 1.28 GB | 40-55 |
| 4B | 2.74 GB | 22-30 |
| 9B | 5.68 GB | 11-14 |

Also bench Bonsai 27B v1 (3.5 GB) once downloaded: its 1-bit CPU speed is unknown.

### Phase 4: Build the test harness in Claude Code (2-3 hours)

1. Install Claude Code if needed: https://docs.claude.com/en/docs/claude-code/overview
2. Set up the project:
   ```powershell
   cd D:\Code\Inference\lab
   git init
   uv init
   uv add requests pyyaml matplotlib
   ```
3. Put this file in `D:\Code\Inference\lab\` (and optionally copy it to `CLAUDE.md`).
4. First message to Claude Code:
   > Read LOCAL_LLM_LAB.md fully. You are taking over. Build milestones 1 and 2 from section 7. First start llama-server with Qwen3.5-4B Q4_K_M, send one request with thinking off and one with thinking on, and show me the raw JSON so we agree on which fields exist.
5. Write the real task set (section 8). ~~Claude Code writes 5 examples; Pratham adds 15.~~ Claude Code wrote all 24 to Pratham's brief (v22); Pratham reviews and adds.

### Phase 5: Quality tests (1 day)

Run the harness on:
- Qwen3.5-4B: Q8_0, Q6_K, Q4_K_M, Q3_K_M, UD-IQ2_XXS
- Gemma 4 E4B Q4_K_M
- Phi-4-mini Q4_K_M

Thinking **off** for all tasks; then thinking **on** for maths/logic and bug-finding tasks only (Qwen). 3 repeats each. Budget a full day; let it run.

Look for:
- where the pass rate drops (usually flat Q8→Q4, step down at Q3 or Q2): the **quality breaking point**;
- which task categories break first;
- **correct answers per hour** (Q4 may beat Q8 here);
- thinking on vs off: extra tasks solved vs extra minutes;
- Qwen3.5-4B vs Gemma 4 E4B vs Phi-4-mini at similar sizes (Qwen thinking off for fairness).

### Phase 6: Memory / context tests (half day)

1. **KV sizes:** start `llama-server` with Qwen3.5-4B Q4_K_M at `-c 4096`, `16384`, `32768`, `65536`. Record "KV buffer size" each time. Repeat with `-ctk q8_0 -ctv q8_0` (should be ~half). Check against 32 KB/token at f16.
2. **Breaking point:** Qwen3.5-9B Q4_K_M, raise `-c` until Task Manager memory is near full and disk activity starts (Windows swapping). Record that context.
3. **Needle test:** `needle.py` at 4K, 16K, 32K context (can the model still find one fact in a long document?).
4. **Prefill time:** note how long a 16K-token prompt takes before the first word. On CPU, long context costs time as well as memory.

### Phase 7: Bigger model vs more bits (half day)

Run the full harness on:
- Qwen3.5-9B Q4_K_M (~5.8 GB)
- Qwen3.5-9B Q3_K_M (~4.6 GB)
- Qwen3.5-4B Q8_0 (4.48 GB)
- Bonsai 27B v1 Q1_0 (~3.5 GB)
- (reference) Gemma 4 E4B Q4_K_M

Key comparisons at similar file size: 9B Q3_K_M vs 4B Q8_0 vs Bonsai 27B v1. This tests the claim "smaller model at more bits beats bigger model at fewer bits" (Alex Cheema) on real tasks.

Then write the **Laptop verdict** in section 9.8.

### Phase 8: Prepare for the PC (1 hour)

1. Push `D:\Code\Inference\lab` to a **private** GitHub repo.
2. Optional: pre-download PC files to an external drive (~40 GB): llama.cpp `win-cuda` zip (newest CUDA) + matching `cudart` zip; Qwen3.8-27B GSQ-RCO IQ2_XS (8.4 GB); Qwen3.6-35B-A3B Q4_K_M (~21 GB); Gemma 4 12B QAT Q4_0 (7.4 GB).
3. On the PC, tell Claude Code: "Read LOCAL_LLM_LAB.md. We are now on the PC. Update section 3 and paths, add the CUDA build, then run section 11."

---

## 7. Test harness specification (for Claude Code)

**Purpose:** compare models, quants and settings on Pratham's own tasks, measuring correctness per unit time. Must run unchanged on the PC next week (only config changes).

### Tech rules
- Python 3.14, uv project in `D:\Code\Inference\lab`. Dependencies: `requests`, `pyyaml`, `matplotlib` only (add more only if clearly needed, and say why).
- Configs in YAML. No hard-coded paths or machine details.
- Windows paths and PowerShell for any shell commands.
- Runs must be **resumable**: skip (config, task, repeat) combinations already in results.
- Never run model-generated code outside a temp folder; always use a timeout.
- Reports in British English.
- Every server start passes `--port`, `-t <best T>`, `-np 1`, and `--cache-ram 0`; every request sets sampling explicitly and `"cache_prompt": false`, so repeats are measured cleanly.
- Log verbosity `-lv 4` when buffer sizes are needed (default level hides them).

### Server facts
- `llama-server` exposes an OpenAI-compatible API at `http://127.0.0.1:8080/v1` (e.g. `/v1/chat/completions`) and a web UI at `/`.
- Its startup log prints `model buffer size`, `KV buffer size`, `compute buffer size`. Parse and store these.
- **Before relying on any response field** (usage, timings, reasoning content), make one real request and inspect the JSON. Do not assume field names.
- Thinking toggle for Qwen3.5: `"chat_template_kwargs": {"enable_thinking": false}` in the request body. Verify it works on this llama.cpp build.

### Milestones (in order)

1. **`tasks/tasks.yaml`**: task format with
   - `id`, `category`, `prompt`, `thinking` (on/off/both),
   - `check`: one of `exact | contains | regex | python_tests | manual`,
   - for `python_tests`: asserts to run against the model's extracted code block (subprocess, temp dir, timeout).
   Write 5 example tasks.
2. **`run.py`**: for each config in `configs/*.yaml` (model path, backend dir, ctx, KV cache type, threads, ngl, thinking on/off, sampling preset):
   start `llama-server` → wait for health → run every task N times (default 3) → stop server.
   Save one JSONL line per run to `results/runs.jsonl`: config, task id, repeat, answer, pass/fail, prompt tokens, completion tokens, thinking tokens (if separable), time to first token (streaming), total wall time, decode tok/s, parsed buffer sizes, llama.cpp build number.
3. **`report.py`**: aggregate to `results/report.md` per config: pass rate (overall and per category), median wall time per task, **correct answers per hour**, tokens used, memory. Charts (matplotlib, PNG): pass rate vs file size; time per task vs config; pass rate vs quant for the 4B ladder.
4. **`needle.py`**: build a long document of chosen token length with one hidden fact; ask for it; test at several context sizes; log result + prefill time.
5. **`bench.py`** (optional): wrap `llama-bench` runs from section 6 Phase 3 and merge CSVs into one table.

### Config example (YAML)

```yaml
name: qwen35-4b-q4km-cpu-nothink
model: C:\Users\prath\.lmstudio\models\unsloth\Qwen3.5-4B-GGUF\Qwen3.5-4B-Q4_K_M.gguf  # verify real path
backend_dir: D:\Code\Inference\llama-cpu
server_args: ["-c", "16384", "-t", "6"]        # add "-ngl", "99" for Vulkan/CUDA
kv_cache: f16                                   # or q8_0 -> adds -ctk/-ctv
thinking: false
sampling: { temperature: 0.7, top_p: 0.8, top_k: 20, min_p: 0.0, presence_penalty: 1.5 }
repeats: 3
max_tokens: 32768
```

### As built (v22, agreed with Pratham 2026-09-24)

The spec above is the original plan. This is what was built for milestones 1-2 and why it differs.

**Commands** (the package uses the `lab` entry point that `uv init` created, not loose scripts):

```powershell
uv run lab tasks                          # list tasks
uv run lab selftest                       # every reference answer passes, every wrong answer fails
uv run lab run --dry-run                  # show plan + exact server command, start nothing
uv run lab run configs\<name>.yaml        # run (default: all configs\*.yaml); resumable
uv run lab run configs\x.yaml --tasks "sql-*" "math-*" --repeats 1
uv run lab probe configs\x.yaml           # print one raw JSON response (after any llama.cpp update)
```

**Config split** (so the PC needs only one new file):
- `configs/machines/<name>.yaml`: machine facts: backend folders, best `-t` per backend (laptop: Vulkan 5, CPU 8), backend args (`-ngl 99`), model folders, port, tools (`node`, `g++`). Chosen by `hostname` (laptop = `Silver-Nova`) or `--machine`.
- `configs/presets/sampling.yaml`: presets from section 5.3 (`qwen35-nothink-general`, `qwen35-think-general`, …).
- `configs/*.yaml`: one experiment each. `model` may be a bare file name (searched in the machine's model folders) or a full path; `backend` is a key in the machine file. Unknown keys are an error (a typo must not be silently ignored).

**Resumable and never destructive:** a run is skipped when `runs.jsonl` already holds the same (machine, config, `config_hash`, task, `prompt_hash`, repeat). `config_hash` covers everything that can change a result (model file + size, backend, threads, args, ctx, KV type, thinking, sampling, max_tokens) but **not** `repeats` (raising it adds runs) and not paths. Editing a config or a prompt makes a new hash, so it runs again; old rows stay.

**Order:** repeat-major (all tasks once, then all again), so laptop heat drift spreads over all tasks.

**Fields in each `results/runs.jsonl` line:** `ts`, `machine`, `config`, `config_hash`, `task`, `prompt_hash`, `repeat`, `category`, `lang`, `check`, `passed` (true / false / null = needs manual grading), `check_detail`, `model_file`, `model_bytes`, `backend`, `threads`, `ctx`, `kv_cache`, `thinking`, `sampling_preset`, `sampling`, `max_tokens`, `answer`, `reasoning`, `finish_reason` (`length` = cut off), `prompt_tokens`, `completion_tokens`, `thinking_tokens`, `answer_tokens`, `ttft_s` (first token of any kind), `ttfa_s` (first **answer** token: what you wait for with thinking on), `wall_s`, `prefill_ms`, `prefill_tok_s`, `decode_tok_s` (both from the server's `timings`), `fingerprint` (build, e.g. `b11157-53ed051ce`), `error`, `server` (`load_s`, `build`, `commit`, `bpw`, `buffers_mib` per kind and device, full `cmd`).

**Thinking tokens:** the server does not report them separately. They are counted as the number of `reasoning_content` stream chunks (one token each); `answer_tokens = completion_tokens − thinking_tokens` (includes ~3 hidden end-of-think tokens). See 9.4a.

**Check types** (spec's five plus four):

| Check | How it grades |
|---|---|
| `exact` | normalised text match; numbers compared as numbers; optional `extract` regex (maths tasks use `ANSWER: <n>`) |
| `contains` | all `include` items present (an item may be a list = any one of them), no `exclude` item |
| `regex` | all `patterns` match (optionally `fullmatch`), no `not_patterns` match |
| `json_match` | whole reply must parse as JSON and equal `expected` (tests "no code fence" instructions) |
| `python_tests` | code block → keep only imports/defs/classes/assignments (the model's own example prints and asserts are dropped, so a wrong example comment cannot fail a correct function; see 9.2) → asserts run in a subprocess |
| `js_tests` | code block + `node:assert` tests, run with Node's permission model (no file writes, no child processes) |
| `cpp_tests` | code block (model's `main` removed) + test `main`, `g++ -std=c++20 -static`, then run |
| `sql_result` | query runs in in-memory SQLite (read-only authorizer, time limit); **rows** compared with the rows of `expected_sql`, so any correct SQL passes |
| `manual` | stored with `passed: null`; grade by hand (grading notes in the task's `notes`) |

**Proving the checks:** every auto-checked task has a `reference` answer (must pass) and most have a `wrong` answer (must fail, e.g. the original buggy code). `uv run lab selftest` checks all of them in ~8 s. Run it after every task edit.

**Sandbox:** model code runs only in a fresh temp folder, with a timeout, a minimal environment and no stdin. Python gets an audit hook that blocks writes outside the temp folder, subprocesses and sockets; Node runs with `--permission`; SQL is read-only and in memory; Windows crash dialogs are disabled so a crashing program cannot hang a run. Tested with deliberate attacks (file write, child process, endless loop, null-pointer crash, `DELETE`, `ATTACH`, endless recursive CTE): all blocked. These are guards against accidents, not a hard security boundary.

**Smart App Control (laptop):** SAC is on and blocks some freshly compiled unsigned programs (`WinError 4551`), depending on the file's content, not its path or flags. A blocked C++ test run is stored as `passed: null` ("not graded"), never as a model failure. Compile errors still count as failures. Tried and dropped: running C++ through `clang-repl` (needs MinGW's static printf internals; too fragile for one task). The only full fix is turning SAC off (Pratham's decision; Windows cannot turn it back on without a reset).

**Safety guards on the server:** the harness refuses to start if the port is already in use (a leftover server would otherwise be measured), and checks `/props` reports the configured model file.

**Milestones 3-5 (v25):**
- `uv run lab report` → `results/report.md` + `results/charts/*.png`. Counts only current results (prompt hash matches `tasks.yaml`; newest `config_hash` per config). Sections: overview (pass rate, **correct answers per hour** = passed ÷ hours spent on graded runs, median time per task, median time to first answer, decode tok/s, tokens per run, memory = sum of server buffers, manual pending, cut off), pass rate by category, per-task matrix (✓ / ✗ / `p/n` / M), charts (correct/hour, time per task, pass rate vs file size, 4B quant ladder; thinking-off configs only, because thinking configs run a smaller task set), needle and llama-bench tables.
- `uv run lab needle <config> --sizes 4096 16384 32768 --depths 0.5`: invented filler text of an exact token length (measured with the server's `/tokenize`), one hidden fact ("Harbour Street vault code 7481-QX") at the given depth, thinking off, `max_tokens` 64; server `-c` = largest size + 1024. Logs found / missed, prompt tokens and prefill time to `results/needle.jsonl`.
- `uv run lab bench <configs> --pp 512 --tg 128 --depth 0 --reps 3`: runs `llama-bench -o jsonl` with each config's model, backend folder, threads, args and KV type; appends to `results/bench.jsonl` (merged table in the report).

---

## 8. Task set guidance

Use made-up code only (no work code). Aim for ~20 tasks:

| Category | Count | Example | Check |
|---|---|---|---|
| Small function | 4 | Parse a date string in 3 formats | python_tests |
| Bug finding | 3 | 40 lines with one off-by-one error; return the fixed function | python_tests |
| SQL / regex | 3 | Query for a given schema; regex for a given pattern | exact / regex |
| Explain code | 2 | "What does this do?" | manual |
| Maths / logic | 3 | Word problems with exact answers | exact |
| Instruction following | 3 | "Answer in exactly 3 bullet points, no word over 8 letters" | regex |
| Summarise | 2 | Paste a paragraph; key facts must appear | contains |

Include a few tasks close to real daily work (Java/Python services, SQL, test writing), rewritten with invented names.

**As built (v22):** Pratham chose **Python, SQL and JavaScript, a little C++, no Java**, weighted towards **service logic, SQL / data, and debugging / review**. Claude Code wrote all 24 tasks (instead of 5 examples + 15 by Pratham). Each task's trap is written in its `notes` field.

| Category | Tasks | Check |
|---|---|---|
| Small function (6) | `py-parse-date` (British day-first), `py-normalise-order` (form DTO → order), `py-merge-slots` (booking slots), `js-parse-query`, `js-deep-merge` (config merge), `cpp-parse-duration` | python / js / cpp tests |
| Bug finding (4) | `bug-py-paginate` (ceil), `bug-py-split-pence` (loop bound), `bug-js-top-scores` (string sort), `bug-sql-left-join` (JOIN drops zero rows) | tests / SQL rows |
| SQL / regex (4) | `sql-top-customers` (filters + tie-break), `sql-monthly-running-total` (window), `sql-latest-status` (latest per group), `py-regex-log-line` | SQL rows / python tests |
| Explain code (2) | `explain-js-event-loop` (print order), `explain-py-rate-cache` | regex / manual |
| Maths / logic (3) | `math-batch-job` (30), `math-sla-downtime` (43), `math-pin-count` (4536) | exact (`ANSWER:` line) |
| Instruction following (3) | `if-three-bullets` (no word > 8 letters), `if-json-extract` (bare JSON), `if-one-sentence` (≤ 20 words) | regex / json_match |
| Summarise (2) | `sum-incident` (cause, fix, 37 min), `sum-release-notes` (breaking changes only) | contains |

`thinking: both` (run with thinking on too, per Phase 5): the 4 bug tasks, the 3 maths tasks and the event-loop task. All other tasks run with thinking off only. SQL tasks share one invented shop schema (`fixtures.shop`), inserted into prompts via `{{ddl}}`.

To add a task: copy a similar one in `tasks/tasks.yaml`, write a `reference` (and ideally a `wrong`), then `uv run lab selftest`.

---

## 9. Findings (fill with real measurements)

### 9.1 Baseline
| Item | Value |
|---|---|
| Idle RAM "In use" | |
| Model budget (16 − In use − 1) | |
| llama.cpp build number | 11157 (commit 53ed051ce), CPU and Vulkan zips |
| Intel driver version | |
| LM Studio llama.cpp runtime version | 2.43.0 (CPU and Vulkan) |
| iGPU memory limit shown by LM Studio | 8.76 GB (share of system RAM) |
| RAM seen by LM Studio | 15.37 GB |

### 9.2 Phase 1: LM Studio (Qwen3.5-4B Q4_K_M)

**Observed 2026-09-23:**
- LM Studio runtimes after update: CPU llama.cpp **2.43.0**, Vulkan llama.cpp **2.43.0** (selected for GGUF), Harmony 0.3.6 (chat-format parser for OpenAI's gpt-oss models), CUDA 2.43.0 (non-compatible, no NVIDIA GPU). Auto-update was on: **turn it off during the test week** so engine versions stay fixed and results compare. Record the version with every result.
- LM Studio runtimes installed: Vulkan llama.cpp 2.43.0 and 2.40.0, CPU llama.cpp 2.40.0, CUDA 2.40.0 (red = no NVIDIA GPU; ignore). "2 updates available" shown, but no update option appeared under Manage installed packs.
- **Vulkan 2.43.0 and 2.40.0: model fails to load**, `exitCode=3221226505` (0xC0000409, llama.cpp fail-fast abort). Consistent with the Arrow Lake iGPU Vulkan issues. Retest after Intel driver update.
- **CPU 2.40.0: works.**
- In LM Studio **Bionic** (agent app), "hi" → answer after **3 min 18 s**, context 6.8K tokens, thinking on. Cause: agent prompt prefill on CPU + thinking. Not a fair speed test.
- In **plain LM Studio** chat (Think off), Qwen3.5-4B Q4_K_M loads and answers with **GPU Offload = 32** (all 32 layers set to iGPU). So Vulkan apparently works in plain LM Studio but crashed in Bionic. Engine device not yet confirmed from logs (need debug log level).
- Model file path (LM Studio): `C:\Users\prath\.lmstudio\models\unsloth\Qwen3.5-4B-GGUF\Qwen3.5-4B-Q4_K_M.gguf`
- LM Studio load settings seen: ctx 8192, GPU offload 32, CPU threads 5, eval batch 2048, physical batch 512, max concurrent predictions 4 (set to 1), unified KV cache on.
- First log (first request after load, 38-token prompt): prefill **8.88 tok/s** (4.28 s), decode **14.90 tok/s** over 20 tokens. Prefill is far too slow to be normal; likely first-run warm-up (Vulkan shader compilation and/or first read of the file from SSD). Re-measure on a second, longer request. **Update:** later runs show Vulkan has a ~2.2 s fixed prefill cost on every request, so warm-up explains only part of the first request.


| Test | CPU | iGPU (Vulkan) |
|---|---|---|
| Q1 tok/s / TTFT | | |
| Q2 tok/s / TTFT | | |
| Q3 tok/s / TTFT | | |
| Answers sane? | | |
| RAM used by model | | |

| Thinking test (bat & ball) | Time | Correct? |
|---|---|---|
| Thinking on | | |
| Thinking off | | |

**A/B attempt 2026-09-23 22:10-22:12 (palindrome question, Think off, n_slots = 1, LM Studio 2.43.0):**

| Run | Prompt tokens | Prefill tok/s | Output tokens | Decode tok/s |
|---|---|---|---|---|
| 1 | 35 | 12.5 | 167 | 15.7 |
| 2 | 30 | 11.7 | 219 | 15.4 |
| 3 | 4 (rest cached) | n/a | 255 | 15.4 |
| 4 | 30 | 12.2 | 351 | 15.0 |

- **Not a valid A/B test:** the engine process uptime counter runs continuously through all 4 runs and run 3 reused run 2's cache, so no reload happened. All 4 runs used the **same engine**. Changing the runtime only takes effect after ejecting and reloading the model.
- Tasks with ~240-330 prompt tokens and 8 output tokens are **LM Studio auto-naming the chat**. Ignore them in measurements.
- **Decode ≈ 15.4 tok/s**, very stable. Effective bandwidth ≈ 15.4 × 2.74 GB ≈ 42 GB/s, only ~35% of the ~119 GB/s maximum. Room to improve (threads or backend).
- **Prefill for short prompts is ~12 tok/s (~80 ms per token)**, about as slow as decode. Rough fit across requests: ~2.3-2.6 s fixed cost per request plus a few ms per token. Cause unknown (possibly the hybrid DeltaNet layers or state checkpointing for this model on this backend). Check with `llama-bench` pp512 in Phase 3, which has no chat overhead.

**Valid A/B test 2026-09-23 22:17-22:19 (Qwen3.5-4B Q4_K_M, palindrome, Think off, n_slots 1, 5 threads, ctx 8192, runtime 2.43.0, engine reloaded between):**

| Engine | Prompt → prefill | Output → decode | Total |
|---|---|---|---|
| CPU run 1 | 35 tok in 1.05 s (33.3 tok/s) | 148 tok at **12.0 tok/s** | 13.3 s |
| CPU run 2 | 30 tok in 0.86 s (34.8 tok/s) | 204 tok at **12.0 tok/s** | 17.7 s |
| CPU (chat title) | 221 tok in 4.54 s (48.7 tok/s) | 8 tok | |
| Vulkan run 1 | 35 tok in 2.62 s (13.4 tok/s) | 174 tok at **16.5 tok/s** | 13.1 s |
| Vulkan run 2 | 30 tok in 2.34 s (12.8 tok/s) | 275 tok at **16.4 tok/s** | 19.1 s |
| Vulkan (chat title) | 247 tok in 3.45 s (71.5 tok/s) | 8 tok | |

CPU engine confirmed by log warning "no usable GPU found, --gpu-layers option will be ignored". The earlier 4-run set (15.0-15.7 tok/s decode, ~12 tok/s short prefill) matches Vulkan.

**Analysis:**
- **Decode:** Vulkan 16.4 vs CPU 12.0 tok/s → **Vulkan +37%**. Effective bandwidth: Vulkan ≈ 45 GB/s, CPU ≈ 33 GB/s, both far below ~119 GB/s. CPU at 5 threads is probably compute-limited, not memory-limited. (This corrects the earlier prediction that CPU and iGPU decode would be similar.)
- **Prefill** fits time ≈ fixed cost + per-token cost:
  - Vulkan ≈ **2.2 s fixed + 5 ms/token**
  - CPU ≈ **0.3 s fixed + 19 ms/token**
  - Crossover ≈ **135 prompt tokens**: below it CPU starts answering sooner; above it Vulkan wins, by a lot for long prompts (2,000-token prompt: Vulkan ~12 s vs CPU ~39 s, est.).
- The ~2.2 s Vulkan fixed cost appears on **every** request, not only the first, so it is not just warm-up. Cause unknown (Vulkan setup per request, or the model's linear-attention layers on this backend).
- **Decision: Vulkan is the default** on this laptop (typical use: long answers, and any pasted text). Keep checking answers are sane on Vulkan.
- To test in Phase 3: CPU thread count (4, 6, 8…) may raise CPU numbers; llama-bench pp512/tg128 for both engines without chat overhead.

**Phase 1 full run 2026-09-24 15:22-15:29 (Vulkan 2.43.0, on charger, Qwen3.5-4B Q4_K_M, 5 threads, ctx 8192, n_slots 1):**
Model load took 11.5 s (first load after reboot: file read from disk; later loads ~4 s from the OS file cache).

| Question | Think | Output tokens | Decode tok/s | Time | Correct? |
|---|---|---|---|---|---|
| 17 × 23 | off | 4 | (too short) | 2.8 s | Yes (391) |
| 17 × 23 | on | 356 | 15.3 | 23.7 s | Yes (391; stray "391.cw" inside the thinking) |
| Hash map | off | 112 | 16.2 | 8.9 s | Yes, exactly 3 sentences |
| Hash map | on | 870 | 15.3 | 57.2 s | Yes, exactly 3 sentences |
| Palindrome | off | 200 | 16.1 | 14.3 s | Function correct; **one example comment wrong** ("Race a car" → says True, is False) |
| Palindrome | on | 655 | 15.3 | 43.3 s | Main function correct; **2 example comments wrong** (Panama and "Was it a car…" keep punctuation → False, says True); **3rd alternative is buggy** (does not remove spaces) |
| Bat & ball | off | 282 | 15.6 | 21.6 s | Yes (₹5) |
| Bat & ball | on | 1,152 | 15.0 | 77.5 s | Yes (₹5) |

"Think on" runs were regenerations in the same chat, so their prompt was cached (2 tokens, ~0.5 s).

**Observations:**
- **Verdict on these 4 questions: Think off gave the same correctness at 3-9x less time.** Thinking made the palindrome answer longer and *worse* (more example claims, one buggy alternative). Default: **Think off**; test Think on only for harder tasks in Phase 5.
- **Eyeballing is not enough:** both palindrome answers looked right, but contained wrong example comments that only running the code reveals. This is why the harness uses `python_tests` checks.
- **Thinking multiplies time by 3-9x** (17 × 23: 8.6x; hash map: 6.4x; palindrome: 3.0x; bat & ball: 3.6x). Worth it only if it changes correctness; record correctness to decide.
- **Charger vs battery: no real change on Vulkan** (decode 15-16 tok/s both). The iGPU is not power-limited here. CPU on charger still untested.
- **Decode falls slowly with length:** ~16.2 tok/s at 100-200 tokens → ~15.0 at 1,150 tokens (bigger KV cache to read).
- **Prefill on Vulkan is not a simple fixed cost:** 2 tokens ≈ 0.5 s; 23-43 tokens ≈ 1.9-3.5 s; 164-583 tokens ≈ 2.5-4.1 s (583 tokens at 144 tok/s). Short multi-token prompts are the slow case. Map the curve in Phase 3 with `llama-bench -p 8,32,128,512 -n 0` on both backends.

### 9.3 Phase 2: llama.cpp buffers (Qwen3.5-4B Q4_K_M, -c 8192)

**First direct run 2026-09-24 (llama.cpp build 11157, Vulkan, `-c 8192 -ngl 99 -np 1`, default threads = 14, built-in web page, palindrome question):**

| Run | Think | Prompt tokens | Prefill | Output tokens | Decode tok/s | Correct? |
|---|---|---|---|---|---|---|
| 1 | off | 352 | 15.3 s (23 tok/s) | 247 | 12.9 | Yes (`isalnum`, examples printed by code) |
| 2 | on | 2 (cached) | 0.6 s | 486 | 13.8 | **No**: removes only spaces, but claims "A man, a plan…: Panama" and "Was it a car…?" are True (both False with punctuation kept) |
| 3 | off | 4 (cached) | 0.6 s | 250 | 13.7 | Yes (`isalnum`) |

- Buffer lines (`model buffer size`, `KV buffer size`) **not shown** at default verbosity 3. Rerun with `-lv 4`.
- **352 prompt tokens** for a one-line question: the web page adds ~320 tokens of its own (system prompt or tool definitions; check its settings). The harness will send prompts directly via the API.
- **Prefill pattern (key clue):** 322 tokens took 4.5 s (71 tok/s), then the last ~30 tokens took ~11 s more. llama-server processes the end of the prompt in separate small pieces (likely to save a state checkpoint for the hybrid linear-attention layers). On this iGPU, **small batches are very slow**, so these tail pieces cost seconds. This probably explains the "~2 s fixed prefill cost" seen in LM Studio. Hypothesis; test in Phase 3 (`llama-bench -p 8,16,32,64,128,512 -n 0`, Vulkan vs CPU) and, if the flag exists in `llama-server --help`, with context checkpoints disabled.
- **Decode 12.9-13.8 tok/s**, lower than LM Studio's 15-16 on the same engine type. Main difference: 14 threads here vs 5 in LM Studio. Retest with `-t 5`.
- **Thinking again made the palindrome answer worse** (same wrong example claims as in Phase 1). Two sessions, same pattern.
- Think-off answers differ between runs (different examples and wording) because of random sampling. This is why the harness repeats each task 3 times.
- llama-server notes: default port will change to 9931 in a future release → **always pass `--port`**. Warning "no API key, CORS allows all origins" is fine while it listens only on 127.0.0.1.
| Backend | model buffer | KV buffer | compute buffer | total | Task Manager |
|---|---|---|---|---|---|
| CPU | 2603.5 MiB `CPU_Mapped` + 1298.0 MiB `CPU_REPACK` | 256 MiB | 77 MiB | ~4.3 GB incl. 50 MiB RS | |
| Vulkan | 2603.5 MiB `Vulkan0` + 497.3 MiB `Vulkan_Host` | 256 MiB | 77 MiB + 18 MiB host | ~3.0 GB on iGPU + 0.5 GB host | |

**Run with `-t 5 -lv 4`, 2026-09-24 (build 11157, web page, 352-token prompt, thinking off):**

| Engine | Prefill 352 tokens | Decode | Correct? |
|---|---|---|---|
| Vulkan | 3.64 s (96.6 tok/s) | **14.9 tok/s** (186 tok) | Yes: removes spaces only; example results printed by code |
| CPU #1 | 6.05 s (58.2 tok/s) | **11.9 tok/s** (170 tok) | **Partly**: code right, but comment claims "A man, a plan…: Panama" → True (False with punctuation kept) |
| CPU #2 | 0.16 s (4 tokens; rest restored from checkpoint) | **11.7 tok/s** (190 tok) | Yes: results printed by code |

**What the log proves:**
- **Predictions confirmed:** file = **5.19 bits per weight** (estimate was ~5.2); **KV cache = 256 MiB exactly** for 8,192 tokens, 8 layers, f16 (= 32 KB/token); recurrent state (RS) = **50.25 MiB fixed** (R 2.25 + S 48), for the linear-attention layers; `full_attention_interval = 4` → 8 of 32 layers keep a KV cache.
- **Tensor mix in "Q4_K_M":** 131 q4_K, 48 q5_K, 22 q6_K, 48 q8_0, 177 f32 (small norm/bias tensors). "M" = mixed precision.
- **Embedding table stored twice on Vulkan:** 497 MiB `Vulkan_Host` (input lookup, in normal RAM) + inside the 2,603 MiB on the iGPU (output head, read every token). Tied weights → two copies on GPU setups.
- **CPU_REPACK 1,298 MiB:** the CPU build rearranges Q4 weights into a layout its AVX2/VNNI maths reads faster. Costs ~1.3 GB extra RAM.
- **Threads matter even on the iGPU:** `-t 14` (default) vs `-t 5` on Vulkan: prefill 15.3 s vs 3.6 s for the same 352 tokens (4x), decode 12.9-13.8 vs 14.9 tok/s. The slow efficiency cores hold back the coordinating threads. **Always set `-t`.**
- **Prefill split confirmed:** the server processes the prompt in pieces (0→322, 322→348, 348→352) and saves a **context checkpoint** (a 50 MiB copy of the recurrent state) at each break, so the next turn can resume. On Vulkan the 26-token piece took ~1.4 s (~54 ms/token) vs ~6.5 ms/token for the big piece; on CPU the small piece cost the normal rate (~0.5 s). Small batches are the Vulkan weak spot.
- **Checkpoints pay off in chat:** CPU request #2 restored checkpoint 2 and processed only 4 tokens (0.16 s).
- **Vulkan vs CPU (llama.cpp, `-t 5`):** decode +25% (14.9 vs 11.9), prefill of 352 tokens 1.7x faster. Same conclusion as LM Studio.
- **Web page sampling ≠ Qwen's recommended settings:** temp 0.8, top_k 40, min_p 0.05, presence 0. Answers changed style (removed spaces only, not punctuation). The harness must set sampling explicitly.
- **Recurring error:** keeping punctuation but citing "A man, a plan, a canal: Panama" as a palindrome. Seen in 4 of ~9 palindrome answers so far. Good `python_tests` task.
- **Prompt cache:** llama-server keeps old prompts in RAM (`prompt cache is enabled, size limit: 8192 MiB`). Good for chat, bad for benchmarks (repeats skip prefill). Harness: `--cache-ram 0`, and send `"cache_prompt": false` per request, so every repeat is measured cleanly.
- **Auto-fit:** llama.cpp now checks free memory before loading ("fitting params to device memory"). `-fit off` disables it if it ever causes trouble.

### 9.4 Phase 3: speed
**Best thread count:** CPU **T = 8** for decode (T = 14 for prefill only). Vulkan: threads make no difference in llama-bench (2-14 all equal); use **-t 5** in llama-server.

**Thread sweep, Qwen3.5-4B Q4_K_M, llama-bench, build 11157 (2026-09-24):**

| Threads | CPU pp512 | CPU tg128 | Vulkan pp512 | Vulkan tg128 |
|---|---|---|---|---|
| 2 | | | 301.7 | 16.49 |
| 4 | 47.4 | 12.00 | 296.3 | 16.42 |
| 5 | 51.9 | 12.97 | 297.7 | 16.45 |
| 6 | 62.0 | 13.86 | 296.8 | 16.45 |
| 8 | 67.1 | **15.31** | 302.3 | 16.54 |
| 10 | 62.9 | 14.94 ± 1.78 | | |
| 14 | **73.4** | 14.48 | 299.1 | 16.54 |

**Prefill curve (`-t 5`), tokens/sec and time per batch:**

| Batch | Vulkan tok/s | Vulkan time | CPU tok/s | CPU time | Faster |
|---|---|---|---|---|---|
| 8 | 68.4 | 0.12 s | 46.9 | 0.17 s | Vulkan |
| 16 | **21.2** | **0.75 s** | 64.8 | 0.25 s | CPU (3x) |
| 32 | 41.6 | 0.77 s | 69.1 | 0.46 s | CPU |
| 64 | 99.7 | 0.64 s | 61.7 | 1.04 s | Vulkan |
| 128 | 229.5 | 0.56 s | 57.7 | 2.22 s | Vulkan (4x) |
| 256 | 265.3 | 0.97 s | 54.7 | 4.68 s | Vulkan (5x) |
| 512 | 299.5 | 1.71 s | 58.3 | 8.79 s | Vulkan (5x) |

**Findings:**
- **Vulkan has a ~0.6-0.8 s floor for any batch of 16-128 tokens**, while 8 tokens take only 0.12 s (likely a different, per-token code path for tiny batches). So 16-32 token batches are the worst case, 3x slower than CPU. Crossover: CPU is faster only for ~9-50 tokens; above ~64 tokens Vulkan wins by 4-5x.
- This explains the server/LM Studio "fixed prefill cost": each message's prompt is split into a big batch plus small tail batches (checkpoints), and each small tail batch pays the Vulkan floor (plus checkpoint overhead in the server).
- **Correction:** the earlier "Vulkan decodes 25-37% faster than CPU" compared against CPU at 5 threads. At its best (8 threads) CPU decodes 15.3 vs Vulkan 16.5 tok/s: only **~8% slower**. CPU is a solid fallback at `-t 8`.
- **Inconsistency to resolve:** in llama-server, Vulkan with `-t 14` was 4x slower at prefill than `-t 5` (one run each). In llama-bench, threads made no difference on Vulkan. Likely cause: host-side work that only the server does (HTTP threads, checkpoint copies, sampling) competing for cores at `-t 14`. Not proven; keep `-t 5` for Vulkan servers and retest once in the harness.
- **Effective bandwidth ≈ 45 GB/s** for both engines (16.5 tok/s × 2.73 GB of weights read per token), ~38% of the ~119 GB/s theoretical. Either real bandwidth is lower than theoretical, or Qwen3.5's many small operations add per-token overhead. The size ladder will tell (constant tok/s × GB → memory-bound).
- `ggml_vulkan` reports **`matrix cores: KHR_coopmat`** on this 130T with build 11157, so the matrix-core detection problem reported for the 140T (#20776) does not apply here.
- CPU backend loaded: `ggml-cpu-alderlake.dll` (AVX2/AVX-VNNI code path).

**Size ladder (llama-bench, build 11157, Vulkan `-t 5`, CPU `-t 8`, 2026-09-24):**

| Model | Params | Size (GB) | Vulkan pp512 | CPU pp512 | Vulkan tg128 | CPU tg128 | GB/s read (Vulkan / CPU) |
|---|---|---|---|---|---|---|---|
| Qwen3.5-0.8B Q4_K_M | 0.75 B | 0.52 | 1,142 | 459 | 57.1 | **72.9** | 30 / 38 |
| Qwen3.5-2B Q4_K_M | 1.88 B | 1.27 | 730 | 195 | 31.1 | **35.5** | 39 / 45 |
| Qwen3.5-4B Q4_K_M | 4.21 B | 2.73 | 300 | 70 | 15.6 | **16.0** | 43 / 44 |
| Qwen3.5-9B Q4_K_M | 8.95 B | 5.67 | 196 | 39 | **9.5** | 9.0 | 54 / 51 |
| Gemma 4 E4B Q4_K_M | 7.52 B | 5.32 | 364 | 74 | **15.5** | 14.9 | (82 / 79, not comparable: see below) |
| Bonsai 27B v1 Q1_0 | 26.90 B | 3.79 | 75 | **7.9** | **7.4** | 5.5 | 28 / 21 |

**Findings:**
- **GB/s read rises with model size** (30-38 for 0.8B → 51-54 for 9B). So small models are limited by fixed per-token overhead (many small operations), and larger models get closer to the memory limit. The earlier "~45 GB/s" was not the memory ceiling: the 9B reaches ~54 GB/s. True achievable bandwidth is likely higher still (not measured).
- **Decode: CPU (`-t 8`) ≥ Vulkan up to 4B; Vulkan slightly ahead from 9B.** Differences at 4B-9B are ≤5%, within run-to-run variation (Vulkan 4B was 16.5 in the thread sweep, 15.6 here). Decode is effectively a **tie**.
- **Prefill: Vulkan wins everywhere**, 2.5x (0.8B) to 5x (9B), and 9.5x for Bonsai.
- **Gemma 4 E4B: 7.5B parameters at 4B speed.** "E4B" = about 4B *effective* parameters. A large part of its weights are per-layer embedding tables that are only looked up (one row per token), not multiplied, so far fewer bytes are read per token than the file size suggests. Same logic as MoE: **file size ≠ bytes read per token.** Its prefill is also faster than Qwen 4B (364 vs 300 on Vulkan), probably because it has no linear-attention layers. Strong laptop candidate if its quality holds (Phase 5).
- **Bonsai 27B v1: fits, but slow.** Decode 7.4 tok/s (Vulkan) / 5.5 (CPU), only 21-28 GB/s: unpacking 1-bit weights costs compute, so it is compute-bound, not memory-bound. CPU prefill 7.9 tok/s = ~63 s for a 500-token prompt; Vulkan 75 tok/s = ~7 s. A 3,000-token thinking answer would take ~7 minutes on Vulkan. This is the laptop's **"fits but too slow" breaking point** for daily use.
- **My earlier laptop estimates were too optimistic** (assumed ~60-70% of 119 GB/s): 4B est. 22-30 → real ~16; 9B est. 11-14 → real ~9-9.5; 2B est. 40-55 → real 31-35. Measured numbers replace them.
- **Engine choice unchanged: Vulkan by default** (decode tie, prefill 2.5-5x faster, and it leaves the CPU free for other work while generating). CPU `-t 8` is a full-speed fallback for decode.

**Depth test (Vulkan `-t 5`, Qwen3.5-4B Q4_K_M, tg64):**

| Tokens already in context | Decode | Change | Extra KV read per token (f16) |
|---|---|---|---|
| 0 | 14.48 tok/s | | 0 |
| 4,096 | 13.76 tok/s | −5% | 128 MiB (+5% vs 2.73 GB weights) |
| 16,384 | 12.30 tok/s | −15% | 512 MiB (+20%) |

- The slowdown matches the extra bytes read: each new token must also read the KV cache of all earlier tokens (32 KB per token). **The KV maths from section 4 predicts the drop.**
- A standard 8B model (~128 KB/token) would read ~2 GB extra at 16K, so it would slow down far more. Qwen3.5's hybrid design (only 8 of 32 layers keep a KV cache) is why long context stays cheap here.
- Rough extrapolation (not measured): ~8-10 tok/s at 64K.
- Baseline here (14.5) is ~7% below earlier runs (15.6-16.5), likely heat after ~1 hour of benchmarks. Compare numbers **within** one run; treat differences under ~7% between sessions as noise.

### 9.4a Phase 4: llama-server API facts and first harness runs

**API probe 2026-09-24** (build 11157, Vulkan, `-c 8192 -ngl 99 -t 5 -np 1 --cache-ram 0 -lv 4`, "What is 17 × 23? Answer with just the number.", both answers 391):

| Field | Thinking off | Thinking on |
|---|---|---|
| `choices[0].message.content` | `"391"` | `"391"` |
| `choices[0].message.reasoning_content` | absent | the thinking text (1.2 KB) |
| `usage.prompt_tokens` | 28 | 26 |
| `usage.completion_tokens` | 4 | 345 (thinking + answer together) |
| `timings.prompt_ms` / `prompt_per_second` | 1,332 ms / 21.0 | 1,320 ms / 19.7 |
| `timings.predicted_per_second` | 14.8 | 15.1 |
| `system_fingerprint` | `b11157-53ed051ce` | same |
| Time | 1.5 s | 24.2 s |

- **The thinking switch works** (`chat_template_kwargs.enable_thinking`). Thinking off adds 2 prompt tokens (the template inserts an empty think block).
- **Thinking tokens are not reported separately.** In streaming, each `delta.reasoning_content` chunk is one token: 386 thinking chunks + 3 answer chunks = 389 vs `completion_tokens` 392; the other ~3 (end-of-think tag, whitespace) are hidden. So the harness counts thinking tokens = reasoning chunks.
- The **final stream chunk** carries `usage` and `timings` (with `stream_options.include_usage`). One streamed request gives TTFT, thinking/answer split and server-side prefill/decode speed.
- Streaming TTFT for thinking on: first thinking token at 1.36 s, first **answer** token at 27.2 s. The harness records both (`ttft_s`, `ttfa_s`).
- `/props` shows the server's default sampling (temp 0.8, top_k 40, min_p 0.05, presence 0): **not** Qwen's. Confirms the rule to send sampling explicitly.
- Buffer lines parse at `-lv 4` and match 9.3: `Vulkan0 model buffer size = 2603.50 MiB`, `Vulkan_Host … 497.31 MiB`, `KV buffer size = 256.00 MiB` (8,192 ctx), `RS buffer size = 50.25 MiB`, compute 77.02 MiB.
- The stray **"cw"** at the end of the thinking text appeared again (Phase 1 saw "391.cw"). Reproducible quirk of this model/quant; harmless so far.

**First harness run, thinking off, 2026-09-24 19:17-19:25** (`qwen35-4b-q4km-vulkan-nothink`, 24 tasks × 1 repeat, `-c 16384`, `qwen35-nothink-general`):

| Metric | Value |
|---|---|
| Passed (auto-graded) | **17 / 23** (+1 manual) |
| Total wall time | 7.5 min → **136 correct answers per hour** |
| Median wall time per task | 12.6 s (range 1.7 s to 108 s) |
| Median time to first token | 1.52 s |
| Decode | mean 14.0 tok/s (12.8-14.8) |
| Prefill | median 118 tok/s at a median 182-token prompt |
| Server load | 3.2 s; KV buffer **512 MiB at 16,384 ctx** (= 32 KB/token, as predicted) |
| Cut off (`finish_reason: length`) | 0 of 24 |

Failures (all checked by hand: real model mistakes, not harness errors):
- `bug-py-paginate`: fixed the logic correctly, but wrote `from dataclass import dataclass` → crashes on import. **Right idea, broken code.**
- `bug-sql-left-join`: explained the bug correctly, then returned the **unchanged** query.
- `cpp-parse-duration`: 1,527-token answer (108 s) that fails the basic case `1h30m`.
- `explain-js-event-loop`: answered `A C G D E F B` (correct `A E G C D F B`).
- `if-three-bullets`: used "knowledge" (9 letters; rule said max 8).
- `js-deep-merge`: turns arrays into objects and loses base values.

**Thinking-on run, 2026-09-24 ~20:20: stopped, no results.** `qwen35-4b-q4km-vulkan-think` (8 `both` tasks × 1) was stopped by Claude Code because the laptop was low on memory (4.6 GB free of 15.4 GB afterwards), during the first task (`bug-py-paginate`: 2,827 thinking tokens after 3 min 17 s at 15.0 tok/s, still thinking). No row was saved (a row is written only when a task ends); no `llama-server` was left running. **The harness's thinking-on path is therefore not yet verified end to end** (the thinking-token method itself was verified in the probe above). Cheap check, with other apps closed: `uv run lab run configs\qwen35-4b-q4km-vulkan-think.yaml --tasks math-pin-count --repeats 1`. Note for Phase 5: at ~15 tok/s, thinking tasks can take 3-10+ min each.

**Thinking-on path verified, 2026-09-24** (other apps closed, 8.4 GB RAM free; `math-pin-count` × 1, `qwen35-think-general`):

| Field | Value |
|---|---|
| Result | **PASS** (`ANSWER: 4536`), `finish_reason: stop` |
| `thinking_tokens` / `answer_tokens` / `completion_tokens` | 1,417 / 216 / 1,633 (87% thinking) |
| `ttft_s` (first thinking token) / `ttfa_s` (first answer token) | **1.2 s / 105.1 s** |
| Wall time | 120.8 s (thinking off: 32.3 s, also PASS) → **3.7× slower, same correctness** |
| Decode | 13.6 tok/s (thinking off, same task: 14.3) |
| Prefill | 53 tokens in 1.18 s |

- All fields are filled as designed; reasoning text (4,187 chars) is saved in `reasoning`.
- `ttfa_s` is the number that matters with thinking on: the reader waits 1 min 45 s for the first word of the answer.
- **Weakens the batch-size hypothesis above:** the same question with thinking on (53-token prompt) prefilled in 1.18 s, vs 3.95 s for the 55-token thinking-off prompt. The slow case may have been a one-off stall; the `llama-bench` test will decide.

**Full thinking-on set, 2026-09-24** (laptop idle; the 7 remaining `both` tasks × 1; resume skipped `math-pin-count`, already done). All `stop`, no errors, decode mean 14.0 tok/s.

| Task | Off | Off time | On | On time | First answer token | Thinking tokens | Time × |
|---|---|---|---|---|---|---|---|
| `math-pin-count` | PASS | 32 s | PASS | 121 s | 105 s | 1,417 | 3.7 |
| `bug-py-paginate` | FAIL | 23 s | **PASS** | 633 s | 611 s | 8,348 | 27.6 |
| `bug-py-split-pence` | PASS | 14 s | PASS | 311 s | 297 s | 4,161 | 21.9 |
| `bug-js-top-scores` | PASS | 12 s | PASS | 425 s | 417 s | 5,793 | 34.9 |
| `bug-sql-left-join` | FAIL | 12 s | **PASS** | 385 s | 375 s | 5,191 | 31.2 |
| `explain-js-event-loop` | FAIL | 2 s | FAIL | 112 s | 112 s | 1,571 | 64.2 |
| `math-batch-job` | PASS | 17 s | PASS | 90 s | 76 s | 1,074 | 5.3 |
| `math-sla-downtime` | PASS | 24 s | PASS | 111 s | 91 s | 1,289 | 4.7 |
| **Total** | **5/8** | **2.3 min** | **7/8** | **36.4 min** | | | **16×** |

- **Correct answers per hour on these 8 tasks: thinking off 132, thinking on 12.** Thinking fixed 2 tasks (both bug fixes that failed with thinking off) but cost 16× the time. By the core principle (section 2), thinking off wins by ~11×. n = 1 per task; Phase 5's 3 repeats must confirm.
- **Bug tasks think the longest** (4,000-8,300 tokens, 5-10.5 min each at ~14 tok/s); maths tasks think ~1,000-1,400 tokens (1.5-2 min).
- With thinking on, `bug-sql-left-join` returned a real fix (thinking off returned the unchanged query), and `bug-py-paginate` had no import typo.
- `explain-js-event-loop` failed both ways. Thinking on answered `A E C D F G B`: it got the microtask order right (C D F) but ran it before the last synchronous line G. Correct: `A E G C D F B`.
- Useful rule to test in Phase 5: **thinking off by default; thinking on only for a bug fix that failed once**, since a retry with thinking costs ~5-10 min but can turn a failure into a pass.

Observations:
- **Explaining a bug ≠ fixing it** (two cases above). Only running the code or query shows it; eyeballing the explanation would have marked both correct.
- Short tasks are dominated by fixed costs: `if-*` tasks take 2-3 s, of which ~1.3 s is time to first token.
- **Open question: Vulkan prefill vs exact batch size.** `math-pin-count` (55-token prompt) took 3.95 s to prefill (13.9 tok/s): the server split it 51 + 4 (checkpoint), and the **51-token batch alone took 2.7 s**, far off the Phase 3 curve (32 tokens 0.77 s, 64 tokens 0.64 s). Hypothesis: some non-power-of-two batch sizes hit a slow Vulkan path. ~~Test: `llama-bench … -p 48,50,51,52,56,60,64`~~ **Tested 2026-09-25 (`lab bench`, Vulkan, 3 repeats): hypothesis rejected.** pp48 81.2, pp50 82.1, **pp51 83.7 t/s (0.61 s)**, pp52 89.9, pp55 91.2, pp56 95.7, pp64 102.1: a smooth curve, no slow sizes. The 2.7 s in the server was a one-off stall.

### 9.4b Model comparison, thinking off, 24 tasks × 1 (2026-09-24 21:26-22:05, Vulkan)

| Model | Passed | Correct/hour | Median s/task | Decode tok/s | Memory GiB | KV at 16K |
|---|---|---|---|---|---|---|
| **Gemma 4 E4B Q4_K_M** | **19/23 (83%)** | 110 | 12.1 | 13.9 | 5.69 (2.2 GB of it in CPU RAM) | **40 MiB** |
| Qwen3.5-4B Q4_K_M | 17/23 (74%) | **139** | 12.6 | 14.2 | 3.69 | 512 MiB |
| Qwen3.5-9B Q4_K_M | 17/23 (74%) | 79 | 18.9 | 9.1 | 5.97 | 512 MiB |
| Qwen3.5-2B Q4_K_M | 9/23 (39%) | 81 | 7.1 | 26.8 | 1.86 | 192 MiB |
| Phi-4-mini Q4_K_M (greedy) | 7/23 (30%) | 120 | 8.7 | 17.6 | 4.88 | **2,048 MiB** |
| Qwen3.5-4B Q8_0 | 15/23 (65%) | 55 | 17.0 | 11.4 | 5.45 | 512 MiB |
| **Gemma 4 E4B QAT UD-Q4_K_XL** (2026-09-25) | **19/23 (83%)** | 99 | 16.0 | 12.3 | **4.48** | 40 MiB |
| "Qwen3.8-4B-Distill" Q4_K_M (empero-ai, 2026-09-25) | 11/23 (48%) | 119 | 14.0 | 15.3 | 3.66 | 512 MiB |

- KV per token confirmed for three designs: Qwen3.5 hybrid 32 KB, Phi-4-mini 128 KB (as predicted in section 4), Gemma 4 E4B ~2.5 KB (likely sliding-window attention; not yet confirmed from its log).
- Phi-4-mini answers are coherent (not the Vulkan garbage bug); its failures are real logic errors. Its 120 correct/hour comes from speed, not accuracy: **judge pass rate first, then correct/hour.**
- The 9B scored the same as the 4B at 1.5× the time: no gain on these tasks.
- **Gemma QAT vs Gemma Q4_K_M: a tie on quality** (19/23 each; QAT passed `js-deep-merge`, failed `sql-latest-status`). Clean `lab bench` (nothing else running, 7.8 GB free): decode **12.2 vs 13.2 tok/s (−7%)**, prefill **405 vs 349 tok/s (+16%)**, memory **4.48 vs 5.69 GiB (−1.2 GB)**. The slower decode is real, not memory pressure; cause not confirmed (quant mix).
- **"Qwen3.8-4B-Distill" is weaker than the original Qwen3.5-4B** (11 vs 17/23). Setup checked: 0 thinking tokens, no leaked think tags, all `stop`; failures are real code/SQL errors. Confirms the caution about community distills with borrowed names.
- **Q8_0 scored lower than Q4_K_M (15 vs 17)**, which 8-bit should not do: it failed 3 tasks Q4 passed and passed 1 Q4 failed (all 4 failures checked: real errors, incl. `js-deep-merge` looping until the 4,096-token limit, 6 min). With 1 repeat, **±2-3 tasks is noise**; this is also why Gemma's 2-task lead is not yet proof. Q8 is also slower (11.4 vs 14.2 tok/s, 5.45 vs 3.69 GiB).

**Provisional verdict (n = 1 repeat; Gemma's lead is only 2 tasks, so Phase 5's 3 repeats must confirm):**
- **Default for coding: Gemma 4 E4B Q4_K_M, thinking off.**
- **Quick tasks / low memory: Qwen3.5-4B Q4_K_M, thinking off.**
- **Retry for a failed bug fix: Qwen3.5-4B, thinking on** (fixed 2 of 2 failed bug tasks, ~6 min each).
- **Not recommended:** Phi-4-mini, Qwen3.5-2B, Qwen3.5-9B.

Q8_0 finished 2026-09-25 (resumed after the stop; 23 remaining tasks).

### 9.5 Phase 5: quality (from `results/report.md`)
| Config | Pass rate | Median time/task | Correct/hour | Notes |
|---|---|---|---|---|
| 4B Q8_0 | | | | |
| 4B Q6_K | | | | |
| 4B Q4_K_M | | | | |
| 4B Q3_K_M | | | | |
| 4B UD-IQ2_XXS | | | | |
| Gemma 4 E4B Q4_K_M | | | | |
| Phi-4-mini Q4_K_M | | | | |
| 4B Q4_K_M thinking on (hard tasks) | | | | |

Quality breaking point: ___

### 9.6 Phase 6: memory
| Model | -c | KV f16 | KV q8_0 | Notes |
|---|---|---|---|---|
| 4B Q4_K_M | 4096 | | | |
| 4B Q4_K_M | 16384 | | | |
| 4B Q4_K_M | 32768 | | | |
| 4B Q4_K_M | 65536 | | | |

Swap point (9B Q4_K_M): -c = ___ · Needle 4K/16K/32K: **found / found / GPU crash** · 16K prefill time: **178 s**

**Needle test 2026-09-25** (`lab needle`, Qwen3.5-4B Q4_K_M, Vulkan, `-c 33792`, KV 1,056 MiB, fact at depth 0.5):

| Target | Actual prompt tokens | Found? | Prefill | Prefill tok/s |
|---|---|---|---|---|
| 4K | 4,042 | yes | 19.6 s | 206 |
| 16K | 16,377 | yes | **178 s** | 92 |
| 32K | 32,746 | **crash**: `vk::Device::getFenceStatus: ErrorDeviceLost` after 5 min 44 s, at ~22.5-24.5K tokens processed | – | – |

- Prefill slows with depth: each 2,048-token slice took 5.6 s at the start, 23 s at 10K, 45-52 s at 20-22K (attention compares each new token with all earlier ones).
- **Laptop limit on Vulkan: keep prompts under ~16K tokens** (16K already costs 3 min before the first word). Cause of the crash not confirmed: no Windows GPU-reset event (4101) was logged. Untested: the same on the CPU backend (no GPU watchdog, but ~5× slower prefill).
- Fixed in the harness: a crashed request is now stored as `found: null` (error), not as a miss.

### 9.7 Phase 7: bigger vs more bits
| Config | Size GB | Pass rate | Correct/hour | tg128 |
|---|---|---|---|---|
| 9B Q4_K_M | | | | |
| 9B Q3_K_M | | | | |
| 4B Q8_0 | 4.48 | | | |
| Bonsai 27B v1 Q1_0 | | | | |
| Gemma 4 E4B Q4_K_M | | | | |

### 9.8 Laptop verdict
**Provisional (2026-09-25, 1 repeat per task; Phase 5 must confirm):**
- Daily model: **Gemma 4 E4B, thinking off** (why: most correct, 19/23; tiny KV cache, 40 MiB at 16K). **QAT UD-Q4_K_XL** (4.22 GB file, 4.48 GiB in use) when memory is tight or prompts are long (prefill +16%); **Q4_K_M** (5.34 GB, 5.69 GiB) when decode speed matters (+7%). Same accuracy.
- Quick-task / low-memory model: **Qwen3.5-4B Q4_K_M, thinking off** (17/23, most correct answers per hour, 3.7 GiB)
- Thinking: **off by default; on only to retry a failed bug fix** (Qwen 4B fixed 2 of 2 failed bug tasks, ~6-10 min each)
- Breaking points: speed **Bonsai 27B / 9B too slow for the gain** · quality **2B and Phi-4-mini too weak (≤ 39%)** · memory/context **~16K-token prompts on Vulkan (32K crashed)**

---

## 10. Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| `hf` not recognised | Python Scripts folder not on PATH | Add `C:\Users\prath\AppData\Local\Python\pythoncore-3.14-64\Scripts` to user PATH; restart terminal app fully |
| "unknown model architecture" | llama.cpp build too old for Qwen3.5 | Download the newest release |
| Garbage text on Vulkan | Arrow Lake iGPU bug (#19327) | Use CPU build; retry after driver updates |
| "failed to allocate" / out of memory | Context too large | Lower `-c` or add `-ctk q8_0 -ctv q8_0` |
| Very slow, disk busy | Windows swapping | Smaller model/context; close apps |
| Numbers vary a lot | Laptop heat | Charger, Performance mode, pause between runs |
| Endless thinking / repetition | Wrong sampling | Model card presets; presence_penalty 1.5 for Qwen3.5 |
| Port 8080 in use | Old server running | Close it or use `--port 8081` |
| Model listed in LM Studio but fails to load | Needs a special runtime (e.g. Bonsai 2) | Listed ≠ loadable; see section 12.1 |
| SmartScreen blocks exe | Unsigned binary | "More info" → "Run anyway" |
| `hf download` prints "✓ Downloaded" but no file appears | Network error (e.g. WinError 10054, connection reset) is reported as success; or the `--include` pattern matched 0 files | Always verify with `Get-ChildItem`. Rerun; list repo files to check names; try other DNS (1.1.1.1) or a phone hotspot; or download the file in a browser from the repo's Files tab |
| WinError 10054 during `start_tls` (seen in Python traceback) | Connection is reset **during the encryption handshake**, after DNS already worked. Typical of something on the network path (ISP filtering, router, security software), not DNS | Test `curl.exe -4` vs `curl.exe -6` (section 5.2). Use **Cloudflare WARP in WARP mode** (full tunnel) while downloading. Changing DNS alone is unlikely to help |
| LM Studio: `exited before becoming healthy. exitCode=3221226505` | llama.cpp engine aborted on load (0xC0000409). On this laptop: Vulkan/iGPU path. Elsewhere: engine too old for the model file, or a vision (mmproj) file | Switch GGUF runtime to CPU; update runtimes; move `mmproj*` out of the model folder; raise engine log level and read Developer logs |
| A simple "hi" takes minutes | Agent app (Bionic) prompt of ~7K tokens prefilled on CPU, plus thinking | Use plain chat for tests; thinking off for quick tasks |
| Harness: `port 8080 is already in use` | An old `llama-server` is still running (e.g. after a crash) | Close it (Task Manager → `llama-server.exe`). The harness refuses to start so it never measures the wrong server |
| Harness: C++ task shows `MANUAL` / "Smart App Control blocked check.exe" | SAC blocks some freshly compiled unsigned test programs (`WinError 4551`) | Stored as not graded, not as a failure. Grade by hand from `answer` in `runs.jsonl`, or run C++ tasks on the PC |
| "Updates available" but nothing to update | Updates may belong to engines you do not use (e.g. CUDA) | Try "Check for updates"; turn on "Show runtime downloads" to see them in Downloads. Not blocking if CPU works |

---

## 11. PC plan (after the laptop week)

### 11.1 Setup
1. Monitor on the motherboard (iGPU) → full 12 GB VRAM for models. Check with `nvidia-smi`.
2. llama.cpp: newest release, `win-cuda` zip with the newest CUDA version (RTX 50 needs 12.8+) + matching `cudart` zip, unzipped into the same folder, e.g. `D:\Code\Inference\llama-cuda`.
3. Clone the `lab` repo; update configs (paths, `-ngl 99`, backend dir).
4. Run the same task set and harness. Only configs change.

### 11.2 PC model ladder

| # | Model | File | Size | Runtime | Why |
|---|---|---|---|---|---|
| 1 | Qwen3.5-9B | Q8_0 | ~9.5 GB (est.) | stock | All-GPU baseline, near-lossless |
| 2 | Gemma 4 12B QAT | Q4_0 | 7.4 GB | stock | Fast code baseline (matched Bonsai 2 on HumanEval/MBPP in Killy's test) |
| 3 | Qwen3.8-27B GSQ-RCO | IQ2_XS (or `-mtp`) | 8.4 GB | stock | Real 27B weights, best 2-bit method. Repo: `ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF` |
| 4 | Qwen3.8-27B GSQ-RCO | IQ3_XXS | 10.1 GB | stock | Higher quality, short context only |
| 5 | Ternary Bonsai 2 27B | PQ2_0 (PTQ1_0 = 5.95 GB) | 7.21 GB | **PrismML llama.cpp fork** | Long context (100K+); PQ2_0 favoured on Blackwell per PrismML |
| 6 | Qwen3.6-35B-A3B | Q4_K_M | ~21 GB | stock + `--n-cpu-moe` | MoE: experts in system RAM. Unsloth: runs on ~22 GB total memory |

Qwen3.8-27B is also the Micro Center pick for 32 GB+ machines; on 12 GB VRAM it only fits at ~2.5-3 bits.

### 11.3 VRAM budgets (est.)
KV for Qwen3.8-27B: Sudo su measured 1.47 GB per 64K at q4_0 → ~2.8 GB per 64K at q8_0.

| Setup | Weights | KV | Buffers + CUDA | Total |
|---|---|---|---|---|
| GSQ-RCO IQ2_XS, 64K, q8_0 | 8.4 | 2.8 | ~0.8 | ~12.0 (tight: use iGPU for display or 48K) |
| GSQ-RCO IQ3_XXS, 32K, q8_0 | 10.1 | 1.4 | ~0.8 | ~12.3 (try 24K) |
| Bonsai 2 PQ2_0, 96K, q8_0 | 7.2 | 4.2 | ~0.8 | ~12.2 |

### 11.4 Expected speed (est.)

| Model | Decode tok/s |
|---|---|
| GSQ-RCO IQ2_XS | 45-55 |
| GSQ-RCO IQ3_XXS | 35-45 |
| Bonsai 2 PQ2_0, stock PrismML fork | 55-70 |
| Bonsai 2 PTQ1_0 + community kernel + MTP (WSL2) | 85-100 |
| Qwen3.6-35B-A3B with expert offload | 25-35 |

### 11.5 Serve line (start here)

```powershell
.\llama-server.exe -m <file>.gguf -ngl 99 -fa on -c 65536 -np 1 -ctk q8_0 -ctv q8_0 --jinja --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0 --reasoning-budget 8192
```
For MoE (model 6): add `--n-cpu-moe <N>`; start high (e.g. 30), lower it until VRAM is nearly full. Check `llama-server --help` for exact flag names on your build (also MTP/speculative flags).

### 11.6 Cautions
- **KV cache q8_0, not q4_0, for agent work.** Community reports: q4 KV runs failed on long agent jobs; one 8 GB guide needs a special KV calibration step for q4.
- **Cap thinking** with `--reasoning-budget` (fixes "32K tokens of planning, no files").
- **Bonsai 2:** stock llama.cpp / LM Studio / Ollama reject PTQ1_0 and PQ2_0; stock loads Q2_0 silently and outputs garbage. Do **not** use the Hugging Face "Use this model" buttons: they default to the 53.8 GB F16 file (padded ternary, not the teacher).
- **Community forks and prebuilt tarballs** (e.g. sudoingX kernel branch, PRs #217/#218 on PrismML-Eng/llama.cpp) are unreviewed binaries. Prefer building from source; better, wait until PrismML merges them.

---

## 12. Research notes and decisions

### 12.1 Bonsai 2 27B debate (Sept 2026): what the evidence says
- **Headline "98.2% of FP16":** true on static thinking-mode benchmarks. HF card (14 benchmarks): 84.78 vs 86.32. Blog (20 benchmarks): 83.9 vs 85.4. Killy's independent test: 97.9% on 300 items.
- **Long agent tasks are much worse** (from PrismML's own whitepaper, via MarkTechPost): Terminal-Bench 2.1 52.8 vs 69.7; SWE-bench Verified 60.8 vs 80.6 (~75% retention). Excluded from the headline average. Killy's "traps" set: 15 vs 25 of 34.
- **F16 file in the repo is not the teacher:** it is the ternary weights stored in 16-bit (~33% exact zeros). KL vs teacher 0.32 for all Bonsai files.
- **Inconsistent baselines:** HF card IQ2_XXS 9.4 GB scoring 72.59; whitepaper IQ2_XXS 7.3 GB scoring 75.2. No comparison against strong low-bit methods such as GSQ-RCO (IQ2_XS 8.4 GB: AIME25 96.67, GPQA-D 84.85, LCB v6 76.57 on DASLab's own harness; not directly comparable).
- **Speed work is real:** Sudo su's kernel fix independently confirmed on a 3060 Ti (+33.8% flat, +29.5% at 16K, +22.4% at 64K). RTX 5060 8 GB: 65-73 tok/s at 32K tuned vs 39.6 stock.
- **Verdicts:** PrismML = real work, misleading headline. Fateev = right that static ≠ agentic (small factual slip; anecdotes n=1). Killy = best methodology (temperature 0 may inflate loops). Sudo su = speed claims verified; quality demo n=1. Cheema = verbosity point right; "ternary is a dud" too strong. FHILY = rewrites of others, no new data. Ahmad Osman = technically sound; ODS post is an advert.
- **Bonsai v1 vs v2:** v1 (Qwen3.6-based, Q1_0, ~3.5 GB, ~89.5% static retention) is merged upstream and loads in LM Studio natively. v2 (Qwen3.8-based) needs the PrismML fork; LM Studio cannot load it (only via a plugin workaround).

### 12.2 Community picks (Micro Center guide, 10 Sep 2026)
- 8 GB: Gemma 4 E2B or LiquidAI LFM2.5-2.6B.
- **16 GB: Gemma 4 E4B** (overthinks less than small Qwen3.5; tool calls fixed by updates; still hallucinates on complex prompts).
- 32 GB+: Qwen3.8 27B (strongest local pick; "Extra Reasoning" mode is slow).
- Many "best local LLM 2026" pages are SEO junk recommending models that do not exist. Ignore them.

### 12.3 ODS (Osmantic) trial, 2026-09-23
- Recommended Phi-4-mini Q4_K_M with 128K context, CPU-only in Docker, 5.2 GB budget (Docker VM limit), f16 KV, 8 threads.
- Its estimate "4.38 GB including KV at 125K" is wrong: Phi-4-mini needs ~128 KB/token → ~16.8 GB of KV at 128K. Prefill of 128K on CPU would also take many minutes.
- Install was incomplete (network failures). **Fully uninstalled.** Secrets from its `.env` are void.
- Lesson: check any tool's recommendation with the KV formula (section 4).

### 12.4 Local vs frontier models
Claude/GPT also generate one token at a time (plus internal planning). Differences: scale (split across many GPUs), likely MoE, heavy post-training (fine-tuning + reinforcement learning), and the system around the model (tools, search, code execution). Giving a local model tools closes more of the practical gap than a bigger file does. Diffusion LLMs (Mercury 2, Gemini Diffusion) generate blocks in parallel; faster, weaker at long reasoning so far.

### 12.5 Machine comparison

| | PC | Laptop | MacBook M3/M4 8 GB |
|---|---|---|---|
| Model memory | 12 GB VRAM (+32 GB RAM) | ~9-10 GB shared | ~5 GB shared |
| Bandwidth | 672 GB/s | ~119 GB/s | 100 / 120 GB/s |
| Best daily | Qwen3.6-35B-A3B / Qwen3.8-27B | Qwen3.5-9B Q4 or Gemma 4 E4B | Qwen3.5-4B Q4 |
| Coding use | Real assistant | Small tasks | Snippets only |

---

### 12.6 New candidates for this laptop (Hugging Face + X search, 2026-09-25)

Checked on the Hugging Face API (exact file sizes); **none tested in the harness yet**. Each needs one config file + one run (~10 min) before trusting it.

**Worth trying (in this order):**

| # | Model | File | Size | Why |
|---|---|---|---|---|
| 1 | **Gemma 4 E4B QAT** + MTP drafter | `unsloth/gemma-4-E4B-it-qat-GGUF`: `gemma-4-E4B-it-qat-UD-Q4_K_XL.gguf` + `MTP/mtp-gemma-4-E4B-it-Q4_0.gguf` | 4.22 GB + 0.06 GB | Same model as the current winner, trained for 4-bit (QAT), so likely less quality loss than the tested Q4_K_M (5.34 GB) at a smaller size. MTP drafts several tokens at once: faster decode (not measured). Build 11157 supports it (`--spec-type draft-mtp`). Google's own QAT file: `google/gemma-4-E4B-it-qat-q4_0-gguf` (5.15 GB). |
| 2 | **Qwen3.5-4B MTP** | `unsloth/Qwen3.5-4B-MTP-GGUF`: `Qwen3.5-4B-Q4_K_M.gguf` | 2.83 GB | Same quick model with a built-in MTP head: faster decode expected (not measured). |

**Looked at and skipped:**

| Model | Why skipped |
|---|---|
| LFM2.5-8B-A1B (LiquidAI, 8.3B total / 1.5B active, 5.16 GB Q4_K_M) | Fast MoE, but its own card says it is "not the best fit for heavy programming". Good for tool calls / structured output instead. (`…-DSpark-GGUF` is only a 0.2 GB draft model.) |
| Gemma 4 12B QAT (6.98 GB) | Dense 12B: est. ~7 tok/s here and ~8.5 GB of the ~9-10 GB budget. PC candidate (11.2), not laptop. |
| Gemma 4 26B-A4B, Qwen3.6/3.8 27B-35B, Qwen3-Coder-30B-A3B, Tiel-Coder-35B-A3B, Qwopus 27B/35B coders | Too big for 16 GB shared memory. PC candidates. |
| Qwen3.8-Flash-Next | 177B parameters (~110 GB at 4-bit). The small files in its repo are MTP drafts, not the model. |
| MiMo-V2.6-Distill-Qwen-9B (Xiaomi fork of Qwen 9B), Qwopus3.5-9B-Coder | 9B class: our 9B scored the same as the 4B at 1.5x the time (9.4b). |
| Qwen3.5-4B "Claude-Opus-Reasoning-Distilled" (Jackrong) and similar community forks | Unverified community fine-tunes; reasoning distills write long answers (slow here). Section 5.1 rule: skip unless tested. |
| MiniCPM5-2B (1.56 GB) | 2B class: Qwen3.5-2B scored 39% (9.4b). |
| Uncensored / abliterated / Heretic re-uploads (most of the trending list) | Section 5.1 rule: skip. |
| OpenVINO backend for llama.cpp (OpenVINO 2026.1) | Promising for Intel prefill, but failed on a hybrid MoE+SSM model (Qwen3.6-35B-A3B) on an Intel iGPU; tester's verdict "use Vulkan". Qwen3.5 is also hybrid. Revisit later. |


**Second pass (Pratham's Hugging Face list, 2026-09-25).** Speed rule on this laptop: decode ≈ ~45-55 GB/s ÷ bytes read per token, so "Gemma E4B speed" (~14 tok/s) means a dense model of ~4B or smaller (Q4 file ≤ ~3 GB), a Gemma "E" model, or a MoE with a small active part. 7-9B dense models **do run** (Qwen3.5-9B: 9.1 tok/s, 19 s/task, 17/23 = same as the 4B), just slower; 12B ≈ 7 tok/s (est.).

| Verdict | Models |
|---|---|
| **Test next (normal speed)** | **NVIDIA Nemotron-3-Nano-4B** (`unsloth/NVIDIA-Nemotron-3-Nano-4B-GGUF`, Q4_K_M 2.90 GB, 3.97B, arch `nemotron_h` supported by build 11157; official NVIDIA, Mar 2026) |
| Maybe (community, unverified) | `empero-ai/Qwen3.8-4B-Distill-GGUF` (2.78 GB, Qwen3.5-4B architecture). **Misleading name: Qwen has no official Qwen3.8 4B** (official 3.8 = 27B, Flash-Next, 2.4T-A95B). `XHToken/Spark-X2.5-4B-GGUF` (2.60 GB, arch `spark2_5` supported; unknown lab) |
| Runs, but slower (~7-9 tok/s) | Ornith-1.0/1.5-9B (Qwen3.5-9B-based, 5.78 GB; smallest Ornith is 9B), Qwen3.8-9B-Distill, gemma-4-12B coder/agentic forks, Llama 3.1 8B, Qwen3-8B, Parable 8B distills |
| Old generation (superseded by Qwen3.5-4B / Gemma 4 E4B) | Qwen3-4B/8B, Qwen2.5-3B/7B/Coder-7B, Llama 3.x, Mistral 7B v0.2, Llama 2, PowerMoE-3b, EXAONE 3.5, DeepSeek-R1-0528-Qwen3-8B |
| Community fine-tunes on older bases | Jan-v3.5-4B (Qwen3 base, agent/tool use), Parable-*-Claude-Fable-5 distills, TwIL-LM3 (SmolLM3-3B) |
| Not usable in llama.cpp as listed | AWQ, FP8, NVFP4, MLX, BF16 safetensors repos (need a GGUF) |
| Other | LFM2.5-8B-A1B (fast, not for coding, see above); Ternary-Bonsai-8B (likely needs the PrismML fork, 11.6) |
| **PC candidate** | Ornith-1.5-35B-A3B (MoE; experts in system RAM, like Qwen3.6-35B-A3B in 11.2) |

Sources: Hugging Face API; [grigio.org Panther Lake backend benchmark](https://grigio.org/benchmarking-llama-cpp-backends-on-intel-panther-lake-vulkan-vs-sycl-vs-openvino-vs-cpu/); [Phoronix OpenVINO 2026.1](https://www.phoronix.com/news/OpenVINO-2026.1-Released); [X: Gemma 4 MTP merged in llama.cpp](https://x.com/osanseviero/status/2063676865441665426); [X: Gemma 4 vs Qwen 3.5 small models](https://x.com/neural_avb/status/2040305916512440399).

## 13. Glossary and sources

### Glossary
| Term | Meaning |
|---|---|
| GGUF | Model file format for llama.cpp (commonly "GPT-Generated Unified Format") |
| GGML | Tensor library under llama.cpp (Georgi Gerganov Machine Learning) |
| bpw | bits per weight |
| Q4_K_M | 4-bit, K-quant method, Medium mix |
| IQ2_XS | I-quant, ~2-bit, Extra Small |
| UD | Unsloth Dynamic (mixed precision) |
| imatrix | importance matrix used during quantisation |
| KV cache | stored keys/values of earlier tokens |
| pp / tg | prompt processing (prefill) / text generation (decode) |
| TTFT | time to first token |
| MTP | multi-token prediction head (speculative decoding) |
| MoE | mixture of experts |
| QAT / PTQ | quantisation-aware training / post-training quantisation |
| NVFP4 / MXFP4 | 4-bit float formats (Blackwell) |
| sm_120 | NVIDIA chip code for RTX 50 / RTX PRO 6000 |

### Sources
- llama.cpp releases: https://github.com/ggml-org/llama.cpp/releases
- Arrow Lake Vulkan bug: https://github.com/ggml-org/llama.cpp/issues/19327
- Arc 140T coopmat detection: https://github.com/ggml-org/llama.cpp/issues/20776
- Qwen3.5-4B (unsloth GGUF + official card): https://huggingface.co/unsloth/Qwen3.5-4B-GGUF
- Unsloth Qwen3.5 guide: https://unsloth.ai/docs/models/qwen3.5
- Unsloth Qwen3.6 guide: https://unsloth.ai/docs/models/qwen3.6
- Bonsai 2 GGUF card: https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf
- Bonsai 2 whitepaper numbers (MarkTechPost): https://www.marktechpost.com/2026/09/18/prismml-releases-ternary-bonsai-2-27b-a-5-9-gb-apache-2-0-model-retaining-98-2-of-qwen3-8-27b-performance/
- Bonsai 2 in LM Studio (plugin workaround + v1 notes): https://github.com/jostoz/lmstudio-bonsai-2-27b
- Bonsai 2 on 8 GB RTX 5060: https://github.com/snailium/bonsai2-8gb
- GSQ-RCO Qwen3.8-27B: https://huggingface.co/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF
- Micro Center local LLM guide: https://www.microcenter.com/site/mc-news/article/best-local-llms-8gb-16gb-32gb-memory-guide.aspx
- Phi-4-mini technical report: https://arxiv.org/pdf/2503.01743
- ODS: https://github.com/Osmantic/ODS
- Claude Code docs: https://docs.claude.com/en/docs/claude-code/overview

---

## 14. Change log

| Date | Who | Change |
|---|---|---|
| 2026-09-23 | Claude (chat) | v1 created. Phase 0 partly done: hf installed + PATH fixed, LM Studio installed, ODS removed, Qwen3.5-4B Q4_K_M downloading in LM Studio |
| 2026-09-23 | Claude (chat) | v2: Qwen3.5-4B loads on CPU; Vulkan crashes (exit 0xC0000409) on both Vulkan runtimes; Bionic vs plain chat note; troubleshooting rows added |
| 2026-09-23 | Claude (chat) | v3: base folder moved from C:\llm to D:\Code\Inference for all paths; optional LM Studio models folder on D: |
| 2026-09-23 | Claude (chat) | v4: plain LM Studio runs Qwen3.5-4B with GPU offload 32; first timing log recorded; LM Studio model path; how to read llama-server timing lines |
| 2026-09-23 | Claude (chat) | v5: LM Studio hardware/runtime facts (Vulkan 2.43.0 works in plain LM Studio; 8.76 GB iGPU share of RAM); pin runtime versions during tests; Bionic crash hypothesis |
| 2026-09-23 | Claude (chat) | v6: first decode measurements (~15.4 tok/s); A/B invalid (no reload); prefill overhead noted; chat auto-naming tasks to ignore |
| 2026-09-23 | Claude (chat) | v7: valid CPU vs Vulkan A/B: Vulkan decode +37%, CPU prefill faster below ~135 prompt tokens; Vulkan chosen as default |
| 2026-09-24 | Claude (chat) | v8: Phase 1 full results on Vulkan + charger (thinking costs 3-9x time); charger ≈ battery on Vulkan; hf download failures (only 0.8B arrived) and fixes |
| 2026-09-24 | Claude (chat) | v9: Phase 1 correctness recorded (all core answers right; palindrome examples/alternative wrong); Think off chosen as default; Phase 2 started |
| 2026-09-24 | Claude (chat) | v10: llama.cpp build 11157 installed, Vulkan sees Arc 130T; download progress; retry loop that verifies real files |
| 2026-09-24 | Claude (chat) | v11: download failures are TLS-handshake resets, not DNS; IPv4/IPv6 curl test; WARP as fix |
| 2026-09-24 | Claude (chat) | v12: WARP fixed Hugging Face connection resets; Qwen3.5-2B Q4_K_M file name confirmed |
| 2026-09-24 | Claude (chat) | v13: replaced pattern-based retry loop with exact-file-name download script (pattern downloads returned "Fetching 0 files") |
| 2026-09-24 | Claude (chat) | v14: all 9 hf downloads verified; real file sizes filled in |
| 2026-09-24 | Claude (chat) | v15: Gemma 4 E4B and Bonsai 27B downloaded in LM Studio; file check command added |
| 2026-09-24 | Claude (chat) | v16: LM Studio files confirmed (Gemma 4 E4B Q4_K_M 5.34 GB, Bonsai 27B v1 Q1_0 3.80 GB, both + BF16 mmproj); corrected vision-file note for Qwen; model paths listed |
| 2026-09-24 | Claude (chat) | v17: first direct llama-server run (Vulkan): decode 12.9-13.8 tok/s at 14 threads; prefill tail-chunk hypothesis; thinking again worse on palindrome; always pass --port |
| 2026-09-24 | Claude (chat) | v18: Phase 2 done: buffer sizes confirm estimates (5.19 bpw, KV 256 MiB, RS 50 MiB); threads matter on Vulkan (4x prefill); checkpoint split confirmed; harness rules for cache and sampling; Phase 3 commands extended |
| 2026-09-24 | Claude (chat) | v19: thread sweeps (CPU best T=8, Vulkan thread-insensitive) and prefill curves (Vulkan 0.6-0.8 s floor at 16-128 tokens); corrected CPU vs Vulkan decode gap to ~8%; size-ladder commands |
| 2026-09-24 | Claude (chat) | v20: size ladder on both engines: decode tie CPU vs Vulkan, prefill Vulkan 2.5-5x; Gemma 4 E4B = 7.5B params at 4B speed; Bonsai 27B v1 7.4 tok/s (compute-bound); estimates corrected |
| 2026-09-24 | Claude (chat) | v21: depth test (−5% at 4K, −15% at 16K, matches KV maths); Phase 3 complete; Phase 4 next |
| 2026-09-24 | Claude Code | v22: Phase 4 milestones 1-2 built. API probe (fields in 9.4a); `lab` CLI (run / selftest / tasks / probe); machine files + presets; 24 tasks (Python, JS, SQL, a little C++) with reference + wrong answers; sandboxed checks; first real runs (thinking off 17/23, 136 correct/hour); Smart App Control found to block some compiled C++ test programs (handled as "not graded"); open question on Vulkan prefill at odd batch sizes; `CLAUDE.md` imports this file; `.gitignore` |
| 2026-09-24 | Claude Code | v23: first thinking-on run stopped (laptop low on memory, nothing saved); rerun with apps closed verified the thinking path end to end (`math-pin-count`: PASS, 1,417 thinking tokens, first answer token at 105 s, 3.7× slower than thinking off); batch-size hypothesis weakened |
| 2026-09-24 | Claude Code | v24: full thinking-on set (8 tasks × 1): 7/8 in 36.4 min vs thinking off 5/8 in 2.3 min → 12 vs 132 correct answers per hour; thinking fixed the two failed bug tasks at 6-10 min each |
| 2026-09-24 | Claude Code | v25: milestones 3-5 built (`lab report` tested; `lab needle`, `lab bench` not yet run); 6-model comparison (9.4b): Gemma 4 E4B 19/23, Qwen 4B 17/23 (139 correct/h), 9B 17/23, 2B 9/23, Phi-4-mini 7/23; provisional verdict; Q8_0 run stopped early |
| 2026-09-25 | Claude Code | v26: harness complete. Q8_0 finished (15/23: lower than Q4 → 1-repeat noise is ±2-3 tasks); `lab needle` tested (4K/16K found, 16K prefill 178 s, 32K Vulkan `ErrorDeviceLost`); `lab bench` tested (batch-size hypothesis rejected); needle errors now stored as `found: null`; report chart labels show pass rate; provisional laptop verdict in 9.8 |
| 2026-09-25 | Claude Code | v27: Hugging Face + X search for laptop models (12.6): try Gemma 4 E4B QAT + MTP (4.22 GB) and Qwen3.5-4B MTP; skipped LFM2.5-8B-A1B (not for coding), 9B+ forks, 26B+ models, community distills, OpenVINO backend (fails on hybrid models) |
| 2026-09-25 | Claude Code | v28: filtered Pratham's Hugging Face list by laptop speed (12.6): test Nemotron-3-Nano-4B next; Ornith smallest is 9B (runs ~9 tok/s, slower); "Qwen3.8-4B-Distill" is a community model (no official Qwen3.8 4B); Ornith-1.5-35B-A3B noted as PC candidate |
| 2026-09-25 | Claude Code | v29: tested 2 downloads: Gemma 4 E4B QAT UD-Q4_K_XL 19/23 (tie with Q4_K_M; −1.2 GB memory, prefill +16%, decode −7% by clean `lab bench`); "Qwen3.8-4B-Distill" 11/23 (worse than Qwen3.5-4B); report quant label handles `UD-Q4_K_XL` |
