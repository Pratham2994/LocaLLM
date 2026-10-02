# Harness report

Generated 2026-10-02 23:58 from `runs.jsonl` (4101 current runs; 34 tasks in `tasks.yaml`). Sorted by correct answers per hour.

- **Correct answers per hour** = passed auto-graded runs ÷ hours of wall time spent on them.
- Thinking-on configs run only the tasks marked `thinking: on/both`, so compare them with care.
- Memory = sum of llama-server buffers (weights + KV cache + recurrent state + compute).

## Overview

| Config | Quant | File GB | Thinking | Runs | Passed | Pass rate | Correct/hour | Median s/task | Median first answer s | Decode tok/s | Mean tokens/run | Memory GiB | Manual | Cut off |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `pc:gemma4-12b-coder-q4km-mtp-cuda-nothink` | Q4_K_M | 7.38 | off | 170 | 131/165 | **79%** | **1588** | 1.4 | 0.1 | 143.9 | 232 | 8.99 | 5 | 0 |
| `pc:gemma4-12b-qat-mtp-cuda-nothink` | UD-Q4_K_XL | 6.72 | off | 170 | 143/165 | **87%** | **1519** | 1.3 | 0.1 | 182.7 | 343 | 8.13 | 5 | 1 |
| `pc:gemma4-e4b-qat-mtp-cuda-nothink` | UD-Q4_K_XL | 4.22 | off | 170 | 115/165 | **70%** | **1357** | 0.8 | 0.1 | 282.9 | 494 | 4.85 | 5 | 0 |
| `pc:gemma4-e4b-qat-udq4kxl-cuda-b11157-nothink` | UD-Q4_K_XL | 4.22 | off | 120 | 87/115 | **76%** | **1213** | 1.1 | 0.1 | 147.7 | 314 | 4.72 | 5 | 0 |
| `pc:gemma4-e4b-qat-udq4kxl-vulkanpc-nothink` | UD-Q4_K_XL | 4.22 | off | 120 | 91/115 | **79%** | **1195** | 1.4 | 0.1 | 138.7 | 293 | 4.73 | 5 | 0 |
| `pc:qwen35-4b-q4km-cuda-b11157-nothink` | Q4_K_M | 2.74 | off | 120 | 73/115 | **63%** | **1187** | 1.2 | 0.1 | 137.3 | 251 | 3.68 | 5 | 0 |
| `pc:gemma4-e4b-qat-udq4kxl-cuda-nothink` | UD-Q4_K_XL | 4.22 | off | 120 | 85/115 | **74%** | **1121** | 1.1 | 0.1 | 147.5 | 330 | 4.72 | 5 | 0 |
| `pc:gemma4-26b-a4b-qat-cuda-nothink` | UD-Q4_K_XL | 14.25 | off | 120 | 110/115 | **96%** | **1054** | 2.5 | 0.4 | 80.1 | 219 | 15.08 | 5 | 0 |
| `pc:gemma4-12b-qat-udq4kxl-cuda-nothink` | UD-Q4_K_XL | 6.72 | off | 120 | 103/115 | **90%** | **953** | 2.7 | 0.1 | 73.7 | 235 | 7.65 | 5 | 0 |
| `pc:qwen35-4b-q4km-vulkanpc-nothink` | Q4_K_M | 2.74 | off | 120 | 75/115 | **65%** | **851** | 1.4 | 0.1 | 133.4 | 317 | 3.69 | 5 | 0 |
| `pc:gemma4-26b-a4b-qat-mtp-cuda-nothink` | UD-Q4_K_XL | 14.25 | off | 170 | 154/165 | **93%** | **808** | 2.2 | 0.4 | 123.7 | 423 | 15.54 | 5 | 4 |
| `pc:gptoss-20b-q4km-cuda-lowreason` | Q4_K_M | 11.62 | off | 170 | 134/165 | **81%** | **792** | 2.9 | 1.1 | 119.0 | 400 | 11.50 | 5 | 0 |
| `pc:empero-qwen38-35b-a3b-distill-q4km-mtp-cuda-nothink` | Q4_K_M | 21.71 | off | 170 | 131/165 | **79%** | **778** | 2.6 | 0.8 | 105.8 | 294 | 21.49 | 5 | 0 |
| `pc:gemma4-12b-coder-q4km-mtp-cuda-think` | Q4_K_M | 7.38 | on | 36 | 29/36 | **81%** | **698** | 3.7 | 2.4 | 126.9 | 497 | 8.99 | 0 | 0 |
| `pc:ornith15-9b-q8-cardsampling-cuda-nothink` | Q8_0 | 9.79 | off | 120 | 74/115 | **64%** | **692** | 2.3 | 0.1 | 64.6 | 207 | 9.55 | 5 | 0 |
| `pc:ornith15-35b-a3b-q4km-mtp-cuda-nothink` | Q4_K_M | 21.71 | off | 170 | 121/165 | **73%** | **691** | 2.8 | 0.8 | 93.8 | 277 | 21.49 | 5 | 0 |
| `pc:katcoder-v25-dev-q4km-cuda-nothink` | Q4_K_M | 21.39 | off | 170 | 139/165 | **84%** | **648** | 3.4 | 0.8 | 72.5 | 273 | 21.30 | 5 | 0 |
| `pc:qwen38-27b-gsqrco-iq2xs-mtp-cuda-nothink` | IQ2_XS | 8.77 | off | 170 | 136/165 | **82%** | **632** | 3.8 | 0.3 | 71.1 | 311 | 9.95 | 5 | 0 |
| `pc:qwen36-35b-a3b-udq4km-mtp-cuda-nothink` | Q4_K_M | 22.66 | off | 170 | 145/165 | **88%** | **613** | 3.1 | 0.8 | 98.7 | 409 | 22.77 | 5 | 0 |
| `pc:ornith15-9b-q8-cuda-nothink` | Q8_0 | 9.79 | off | 120 | 78/115 | **68%** | **581** | 2.6 | 0.1 | 61.2 | 243 | 9.55 | 5 | 1 |
| `pc:qwen36-35b-a3b-hauhau-uncensored-q4km-cuda-nothink` | Q4_K_M | 21.17 | off | 170 | 145/165 | **88%** | **506** | 3.9 | 0.8 | 73.8 | 389 | 20.97 | 5 | 0 |
| `pc:qwen35-4b-q4km-cuda-nothink` | Q4_K_M | 2.74 | off | 170 | 87/165 | **53%** | **497** | 1.6 | 0.1 | 140.0 | 513 | 3.68 | 5 | 3 |
| `pc:qwen3-coder-30b-a3b-q4km-cuda-nothink` | Q4_K_M | 18.56 | off | 170 | 118/165 | **72%** | **376** | 3.3 | 0.7 | 65.9 | 396 | 19.34 | 5 | 5 |
| `pc:qwen35-9b-q8-cuda-nothink` | Q8_0 | 9.53 | off | 170 | 105/165 | **64%** | **317** | 3.7 | 0.1 | 61.4 | 433 | 9.55 | 5 | 0 |
| `pc:glm47-flash-q4km-cuda-nothink` | Q4_K_M | 18.31 | off | 170 | 77/165 | **47%** | **293** | 3.5 | 0.7 | 64.4 | 316 | 18.69 | 5 | 0 |
| `laptop:gemma4-e4b-qat-mtp-vulkan-nothink` | UD-Q4_K_XL | 4.22 | off | 25 | 19/23 | **83%** | **218** | 5.9 | 1.0 | 25.7 | 314 | 4.87 | 2 | 0 |
| `pc:gemma4-12b-qat-mtp-cuda-think` | UD-Q4_K_XL | 6.72 | on | 36 | 34/36 | **94%** | **155** | 16.8 | 15.2 | 181.9 | 3828 | 8.13 | 0 | 0 |
| `laptop:qwen35-4b-q4km-vulkan-nothink` | Q4_K_M | 2.74 | off | 24 | 17/23 | **74%** | **139** | 12.6 | 1.5 | 14.2 | 243 | 3.69 | 1 | 0 |
| `laptop:phi4-mini-q4km-vulkan-nothink` | Q4_K_M | 2.49 | off | 24 | 7/23 | **30%** | **120** | 8.7 | 0.6 | 17.6 | 148 | 4.88 | 1 | 0 |
| `laptop:qwen38-4b-distill-q4km-vulkan-nothink` | Q4_K_M | 2.78 | off | 24 | 11/23 | **48%** | **119** | 14.0 | 1.5 | 15.3 | 193 | 3.66 | 1 | 0 |
| `laptop:gemma4-e4b-q4km-vulkan-nothink` | Q4_K_M | 5.34 | off | 24 | 19/23 | **83%** | **110** | 12.1 | 1.1 | 13.9 | 343 | 5.69 | 1 | 0 |
| `laptop:gemma4-e4b-qat-udq4kxl-vulkan-nothink` | UD-Q4_K_XL | 4.22 | off | 25 | 19/23 | **83%** | **99** | 15.3 | 0.9 | 12.3 | 334 | 4.73 | 2 | 0 |
| `pc:gemma4-26b-a4b-qat-mtp-cuda-think` | UD-Q4_K_XL | 14.25 | on | 36 | 33/36 | **92%** | **94** | 24.9 | 22.7 | 117.3 | 3957 | 15.54 | 0 | 0 |
| `pc:laguna-xs21-q4km-cuda-nothink` | Q4_K_M | 19.56 | off | 34 | 13/33 | **39%** | **87** | 13.5 | 11.0 | 78.8 | 1191 | 20.17 | 1 | 1 |
| `laptop:qwen35-2b-q4km-vulkan-nothink` | Q4_K_M | 1.28 | off | 24 | 9/23 | **39%** | **81** | 7.1 | 0.6 | 26.8 | 434 | 1.86 | 1 | 1 |
| `pc:qwen38-27b-gsqrco-iq2xs-mtp-cuda-think` | IQ2_XS | 8.77 | on | 36 | 33/36 | **92%** | **80** | 14.1 | 10.7 | 62.7 | 2358 | 9.95 | 0 | 3 |
| `laptop:qwen35-9b-q4km-vulkan-nothink` | Q4_K_M | 5.68 | off | 24 | 17/23 | **74%** | **79** | 18.9 | 2.0 | 9.1 | 268 | 5.97 | 1 | 0 |
| `laptop:qwen35-4b-q8-vulkan-nothink` | Q8_0 | 4.48 | off | 24 | 15/23 | **65%** | **55** | 17.0 | 1.4 | 11.4 | 448 | 5.45 | 1 | 1 |
| `pc:qwen36-35b-a3b-udq4km-mtp-cuda-think` | Q4_K_M | 22.66 | on | 31 | 25/31 | **81%** | **48** | 37.2 | 29.5 | 98.4 | 5632 | 22.77 | 0 | 6 |
| `pc:glm47-flash-q4km-cuda-think` | Q4_K_M | 18.31 | on | 36 | 26/36 | **72%** | **41** | 46.1 | 41.7 | 63.7 | 3883 | 18.69 | 0 | 2 |
| `laptop:qwen35-4b-q4km-vulkan-think` | Q4_K_M | 2.74 | on | 8 | 7/8 | **88%** | **12** | 215.6 | 204.0 | 14.0 | 3783 | 3.69 | 0 | 0 |

## Pass rate by category

| Config | small function | bug finding | sql regex | explain code | maths logic | instruction following | summarise |
|---|---|---|---|---|---|---|---|
| `pc:gemma4-12b-coder-q4km-mtp-cuda` | 28/50 | 24/25 | 30/30 | 5/10 | 23/25 | 14/15 | 7/10 |
| `pc:gemma4-12b-qat-mtp-cuda` | 36/50 | 24/25 | 30/30 | 3/10 | 25/25 | 15/15 | 10/10 |
| `pc:gemma4-e4b-qat-mtp-cuda` | 24/50 | 20/25 | 22/30 | 0/10 | 25/25 | 15/15 | 9/10 |
| `pc:gemma4-e4b-qat-udq4kxl-cuda-b11157` | 15/30 | 17/20 | 17/20 | 0/5 | 15/15 | 15/15 | 8/10 |
| `pc:gemma4-e4b-qat-udq4kxlpc` | 20/30 | 15/20 | 17/20 | 0/5 | 15/15 | 15/15 | 9/10 |
| `pc:qwen35-4b-q4km-cuda-b11157` | 11/30 | 10/20 | 14/20 | 0/5 | 14/15 | 14/15 | 10/10 |
| `pc:gemma4-e4b-qat-udq4kxl-cuda` | 13/30 | 19/20 | 14/20 | 0/5 | 15/15 | 15/15 | 9/10 |
| `pc:gemma4-26b-a4b-qat-cuda` | 27/30 | 19/20 | 20/20 | 5/5 | 15/15 | 14/15 | 10/10 |
| `pc:gemma4-12b-qat-udq4kxl-cuda` | 24/30 | 19/20 | 19/20 | 1/5 | 15/15 | 15/15 | 10/10 |
| `pc:qwen35-4b-q4kmpc` | 13/30 | 10/20 | 13/20 | 0/5 | 14/15 | 15/15 | 10/10 |
| `pc:gemma4-26b-a4b-qat-mtp-cuda` | 43/50 | 25/25 | 30/30 | 6/10 | 25/25 | 15/15 | 10/10 |
| `pc:gptoss-20b-q4km-cuda-lowreason` | 32/50 | 22/25 | 28/30 | 4/10 | 23/25 | 15/15 | 10/10 |
| `pc:empero-qwen38-35b-a3b-distill-q4km-mtp-cuda` | 30/50 | 22/25 | 30/30 | 0/10 | 24/25 | 15/15 | 10/10 |
| `pc:gemma4-12b-coder-q4km-mtp-cuda-think` | – | 11/15 | – | 3/6 | 15/15 | – | – |
| `pc:ornith15-9b-q8-cardsampling-cuda` | 8/30 | 17/20 | 15/20 | 0/5 | 14/15 | 10/15 | 10/10 |
| `pc:ornith15-35b-a3b-q4km-mtp-cuda` | 26/50 | 23/25 | 28/30 | 0/10 | 24/25 | 10/15 | 10/10 |
| `pc:katcoder-v25-dev-q4km-cuda` | 36/50 | 25/25 | 30/30 | 0/10 | 25/25 | 13/15 | 10/10 |
| `pc:qwen38-27b-gsqrco-iq2xs-mtp-cuda` | 37/50 | 23/25 | 26/30 | 1/10 | 25/25 | 14/15 | 10/10 |
| `pc:qwen36-35b-a3b-udq4km-mtp-cuda` | 41/50 | 25/25 | 30/30 | 0/10 | 25/25 | 15/15 | 9/10 |
| `pc:ornith15-9b-q8-cuda` | 9/30 | 18/20 | 15/20 | 0/5 | 15/15 | 11/15 | 10/10 |
| `pc:qwen36-35b-a3b-hauhau-uncensored-q4km-cuda` | 43/50 | 22/25 | 30/30 | 0/10 | 25/25 | 15/15 | 10/10 |
| `pc:qwen35-4b-q4km-cuda` | 14/50 | 10/25 | 18/30 | 0/10 | 25/25 | 11/15 | 9/10 |
| `pc:qwen3-coder-30b-a3b-q4km-cuda` | 23/50 | 25/25 | 30/30 | 0/10 | 20/25 | 10/15 | 10/10 |
| `pc:qwen35-9b-q8-cuda` | 16/50 | 25/25 | 16/30 | 0/10 | 25/25 | 13/15 | 10/10 |
| `pc:glm47-flash-q4km-cuda` | 20/50 | 9/25 | 12/30 | 0/10 | 16/25 | 12/15 | 8/10 |
| `laptop:gemma4-e4b-qat-mtp` | 3/6 | 4/4 | 4/4 | 0/1 | 3/3 | 3/3 | 2/2 |
| `pc:gemma4-12b-qat-mtp-cuda-think` | – | 15/15 | – | 4/6 | 15/15 | – | – |
| `laptop:qwen35-4b-q4km` | 4/6 | 2/4 | 4/4 | 0/1 | 3/3 | 2/3 | 2/2 |
| `laptop:phi4-mini-q4km` | 1/6 | 2/4 | 1/4 | 0/1 | 2/3 | 1/3 | 0/2 |
| `laptop:qwen38-4b-distill-q4km` | 1/6 | 1/4 | 2/4 | 0/1 | 3/3 | 2/3 | 2/2 |
| `laptop:gemma4-e4b-q4km` | 3/6 | 4/4 | 4/4 | 0/1 | 3/3 | 3/3 | 2/2 |
| `laptop:gemma4-e4b-qat-udq4kxl` | 4/6 | 4/4 | 3/4 | 0/1 | 3/3 | 3/3 | 2/2 |
| `pc:gemma4-26b-a4b-qat-mtp-cuda-think` | – | 15/15 | – | 3/6 | 15/15 | – | – |
| `pc:laguna-xs21-q4km-cuda` | 4/10 | 2/5 | 1/6 | 0/2 | 4/5 | 1/3 | 1/2 |
| `laptop:qwen35-2b-q4km` | 1/6 | 2/4 | 1/4 | 0/1 | 3/3 | 1/3 | 1/2 |
| `pc:qwen38-27b-gsqrco-iq2xs-mtp-cuda-think` | – | 15/15 | – | 3/6 | 15/15 | – | – |
| `laptop:qwen35-9b-q4km` | 3/6 | 4/4 | 3/4 | 0/1 | 3/3 | 2/3 | 2/2 |
| `laptop:qwen35-4b-q8` | 2/6 | 2/4 | 3/4 | 0/1 | 3/3 | 3/3 | 2/2 |
| `pc:qwen36-35b-a3b-udq4km-mtp-cuda-think` | – | 14/14 | – | 0/5 | 11/12 | – | – |
| `pc:glm47-flash-q4km-cuda-think` | – | 11/15 | – | 1/6 | 14/15 | – | – |
| `laptop:qwen35-4b-q4km-think` | – | 4/4 | – | 0/1 | 3/3 | – | – |

## Per task

✓ = passed every repeat, ✗ = failed every repeat, `p/n` = mixed, M = needs manual grading, blank = not run.

| Task | Category | `pc:gemma4-12b-coder-q4km-mtp-cuda` | `pc:gemma4-12b-qat-mtp-cuda` | `pc:gemma4-e4b-qat-mtp-cuda` | `pc:gemma4-e4b-qat-udq4kxl-cuda-b11157` | `pc:gemma4-e4b-qat-udq4kxlpc` | `pc:qwen35-4b-q4km-cuda-b11157` | `pc:gemma4-e4b-qat-udq4kxl-cuda` | `pc:gemma4-26b-a4b-qat-cuda` | `pc:gemma4-12b-qat-udq4kxl-cuda` | `pc:qwen35-4b-q4kmpc` | `pc:gemma4-26b-a4b-qat-mtp-cuda` | `pc:gptoss-20b-q4km-cuda-lowreason` | `pc:empero-qwen38-35b-a3b-distill-q4km-mtp-cuda` | `pc:gemma4-12b-coder-q4km-mtp-cuda-think` | `pc:ornith15-9b-q8-cardsampling-cuda` | `pc:ornith15-35b-a3b-q4km-mtp-cuda` | `pc:katcoder-v25-dev-q4km-cuda` | `pc:qwen38-27b-gsqrco-iq2xs-mtp-cuda` | `pc:qwen36-35b-a3b-udq4km-mtp-cuda` | `pc:ornith15-9b-q8-cuda` | `pc:qwen36-35b-a3b-hauhau-uncensored-q4km-cuda` | `pc:qwen35-4b-q4km-cuda` | `pc:qwen3-coder-30b-a3b-q4km-cuda` | `pc:qwen35-9b-q8-cuda` | `pc:glm47-flash-q4km-cuda` | `laptop:gemma4-e4b-qat-mtp` | `pc:gemma4-12b-qat-mtp-cuda-think` | `laptop:qwen35-4b-q4km` | `laptop:phi4-mini-q4km` | `laptop:qwen38-4b-distill-q4km` | `laptop:gemma4-e4b-q4km` | `laptop:gemma4-e4b-qat-udq4kxl` | `pc:gemma4-26b-a4b-qat-mtp-cuda-think` | `pc:laguna-xs21-q4km-cuda` | `laptop:qwen35-2b-q4km` | `pc:qwen38-27b-gsqrco-iq2xs-mtp-cuda-think` | `laptop:qwen35-9b-q4km` | `laptop:qwen35-4b-q8` | `pc:qwen36-35b-a3b-udq4km-mtp-cuda-think` | `pc:glm47-flash-q4km-cuda-think` | `laptop:qwen35-4b-q4km-think` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `py-parse-date` | small function | ✓ | 4/5 | 4/5 | ✓ | ✓ | 3/5 | 4/5 | ✓ | ✓ | 4/5 | ✓ | ✓ | 3/5 |  | 2/5 | 3/5 | ✓ | ✓ | ✓ | 2/5 | ✓ | 3/5 | ✓ | 2/5 | 3/5 | ✓ |  | ✓ | ✓ | ✗ | ✓ | ✓ |  | ✗ | ✗ |  | ✓ | ✗ |  |  |  |
| `py-normalise-order` | small function | ✓ | ✓ | 1/5 | 4/5 | 3/5 | 1/5 | 3/5 | ✓ | ✓ | 2/5 | 4/5 | 3/5 | ✓ |  | ✗ | ✓ | ✓ | ✓ | ✓ | 1/5 | ✓ | 2/5 | ✗ | ✗ | 3/5 | ✗ |  | ✓ | ✗ | ✗ | ✗ | ✗ |  | ✓ | ✗ |  | ✓ | ✗ |  |  |  |
| `py-merge-slots` | small function | ✓ | ✓ | ✓ | ✓ | ✓ | 3/5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | 4/5 | ✓ | ✓ | ✓ | 4/5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✗ | ✓ | ✓ | ✓ |  | ✗ | ✓ |  | ✓ | ✓ |  |  |  |
| `js-parse-query` | small function | 4/5 | ✓ | 2/5 | 1/5 | 3/5 | 4/5 | 1/5 | ✓ | ✓ | 2/5 | ✓ | ✓ | ✓ |  | 1/5 | ✓ | ✓ | 4/5 | ✓ | 2/5 | ✓ | 1/5 | ✓ | 3/5 | 4/5 | ✗ |  | ✓ | ✗ | ✗ | ✓ | ✓ |  | ✓ | ✗ |  | ✗ | ✓ |  |  |  |
| `js-deep-merge` | small function | 1/5 | 3/5 | 2/5 | ✗ | 3/5 | ✗ | ✗ | ✓ | 3/5 | ✗ | ✓ | 3/5 | 1/5 |  | ✗ | 4/5 | 1/5 | 3/5 | ✓ | ✗ | ✓ | ✗ | ✗ | 2/5 | ✗ | ✓ |  | ✗ | ✗ | ✗ | ✗ | ✓ |  | ✗ | ✗ |  | ✗ | ✗ |  |  |  |
| `cpp-parse-duration` | small function | 1/5 | 1/5 | ✗ | ✗ | 1/5 | ✗ | ✗ | 2/5 | 1/5 | ✗ | 1/5 | 1/5 | 1/5 |  | ✗ | ✗ | ✗ | 3/5 | 1/5 | ✗ | 1/5 | ✗ | ✗ | ✗ | 1/5 | ✗ |  | ✗ | ✗ | ✗ | ✗ | ✗ |  | ✗ | ✗ |  | ✗ | ✗ |  |  |  |
| `bug-py-paginate` | bug finding | ✓ | 4/5 | 1/5 | 4/5 | ✗ | ✗ | 4/5 | 4/5 | 4/5 | ✗ | ✓ | 3/5 | 4/5 | 2/3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | 2/3 | ✓ |
| `bug-py-split-pence` | bug finding | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 3/5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `bug-js-top-scores` | bug finding | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 4/5 | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `bug-sql-left-join` | bug finding | ✓ | ✓ | 4/5 | 3/5 | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | 4/5 | ✓ | 2/3 | 4/5 | ✓ | ✓ | 4/5 | ✓ | 3/5 | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | 1/3 | ✓ |
| `sql-top-customers` | sql regex | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | 4/5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✗ | ✓ |  | ✓ | ✓ |  |  |  |
| `sql-monthly-running-total` | sql regex | ✓ | ✓ | ✓ | ✓ | ✓ | 4/5 | ✓ | ✓ | ✓ | 3/5 | ✓ | ✓ | ✓ |  | 1/5 | ✓ | ✓ | 3/5 | ✓ | ✗ | ✓ | 3/5 | ✓ | ✓ | 4/5 | ✓ |  | ✓ | ✗ | ✗ | ✓ | ✓ |  | ✗ | ✗ |  | ✓ | ✓ |  |  |  |
| `sql-latest-status` | sql regex | ✓ | ✓ | 3/5 | 4/5 | 4/5 | 1/5 | 1/5 | ✓ | 4/5 | 1/5 | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 4/5 | ✓ | ✗ | 1/5 | ✓ |  | ✓ | ✗ | ✗ | ✓ | ✗ |  | ✓ | ✗ |  | ✗ | ✗ |  |  |  |
| `py-regex-log-line` | sql regex | ✓ | ✓ | 3/5 | 3/5 | 3/5 | 4/5 | 3/5 | ✓ | ✓ | 4/5 | ✓ | 3/5 | ✓ |  | ✓ | ✓ | ✓ | 4/5 | ✓ | ✓ | ✓ | 2/5 | ✓ | ✓ | 2/5 | ✓ |  | ✓ | ✗ | ✓ | ✓ | ✓ |  | ✗ | ✗ |  | ✓ | ✓ |  |  |  |
| `explain-js-event-loop` | explain code | ✓ | 3/5 | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | 1/5 | ✗ | ✓ | 4/5 | ✗ | ✓ | ✗ | ✗ | ✗ | 1/5 | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | 1/3 | ✗ |
| `explain-py-rate-cache` | explain code | M | M | M | M | M | M | M | M | M | M | M | M | M |  | M | M | M | M | M | M | M | M | M | M | M | M |  | M | M | M | M | M |  | M | M |  | M | M |  |  |  |
| `math-batch-job` | maths logic | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `math-sla-downtime` | maths logic | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 4/5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 3/5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `math-pin-count` | maths logic | ✓ | ✓ | ✓ | ✓ | ✓ | 4/5 | ✓ | ✓ | ✓ | 4/5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `if-three-bullets` | instruction following | 4/5 | ✓ | ✓ | ✓ | ✓ | 4/5 | ✓ | 4/5 | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✗ | 4/5 | 3/5 | 4/5 | ✓ | 1/5 | ✓ | 1/5 | ✗ | 3/5 | ✓ | ✓ |  | ✗ | ✗ | ✗ | ✓ | ✓ |  | ✗ | ✗ |  | ✗ | ✓ |  |  |  |
| `if-json-extract` | instruction following | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 2/5 | ✓ |  | ✓ | ✗ | ✓ | ✓ | ✓ |  | ✗ | ✗ |  | ✓ | ✓ |  |  |  |
| `if-one-sentence` | instruction following | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | 1/5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ |  | ✓ | ✓ |  |  |  |
| `sum-incident` | summarise | 2/5 | ✓ | 4/5 | 3/5 | 4/5 | ✓ | 4/5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | 4/5 | ✓ | ✓ | 4/5 | ✓ | ✓ | 4/5 | ✓ |  | ✓ | ✗ | ✓ | ✓ | ✓ |  | ✓ | ✓ |  | ✓ | ✓ |  |  |  |
| `sum-release-notes` | summarise | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 4/5 | ✓ |  | ✓ | ✗ | ✓ | ✓ | ✓ |  | ✗ | ✗ |  | ✓ | ✓ |  |  |  |
| `hard-py-ttl-cache` | small function | 4/5 | ✓ | 4/5 |  |  |  |  |  |  |  | ✓ | 4/5 | 2/5 |  |  | ✗ | 2/5 | ✓ | ✓ |  | 4/5 | 2/5 | 3/5 | 2/5 | 2/5 |  |  |  |  |  |  |  |  | ✓ |  |  |  |  |  |  |  |
| `hard-py-semver-range` | small function | ✗ | 2/5 | 3/5 |  |  |  |  |  |  |  | 3/5 | 2/5 | 4/5 |  |  | ✗ | 4/5 | ✗ | 4/5 |  | ✓ | ✗ | 2/5 | 1/5 | ✗ |  |  |  |  |  |  |  |  | ✓ |  |  |  |  |  |  |  |
| `hard-py-build-order` | small function | 3/5 | ✓ | 3/5 |  |  |  |  |  |  |  | ✓ | 2/5 | 3/5 |  |  | ✓ | ✓ | ✓ | 4/5 |  | ✓ | 1/5 | 3/5 | 1/5 | 2/5 |  |  |  |  |  |  |  |  | ✗ |  |  |  |  |  |  |  |
| `hard-js-apply-patch` | small function | ✗ | 1/5 | ✗ |  |  |  |  |  |  |  | ✓ | 2/5 | 1/5 |  |  | ✗ | 4/5 | 2/5 | 2/5 |  | 3/5 | ✗ | ✗ | ✗ | ✗ |  |  |  |  |  |  |  |  | ✗ |  |  |  |  |  |  |  |
| `hard-sql-city-champion` | sql regex | ✓ | ✓ | 3/5 |  |  |  |  |  |  |  | ✓ | ✓ | ✓ |  |  | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✗ | ✓ | ✗ | ✗ |  |  |  |  |  |  |  |  | ✗ |  |  |  |  |  |  |  |
| `hard-sql-order-span` | sql regex | ✓ | ✓ | 3/5 |  |  |  |  |  |  |  | ✓ | ✓ | ✓ |  |  | 3/5 | ✓ | 4/5 | ✓ |  | ✓ | 4/5 | ✓ | 1/5 | ✗ |  |  |  |  |  |  |  |  | ✗ |  |  |  |  |  |  |  |
| `hard-bug-py-allocate` | bug finding | 4/5 | ✓ | ✓ |  |  |  |  |  |  |  | ✓ | ✓ | 3/5 | 1/3 |  | 3/5 | ✓ | 4/5 | ✓ |  | 2/5 | ✗ | ✓ | ✓ | ✗ |  | ✓ |  |  |  |  |  | ✓ | ✗ |  | ✓ |  |  | ✓ | 2/3 |  |
| `hard-explain-js-order` | explain code | ✗ | ✗ | ✗ |  |  |  |  |  |  |  | 1/5 | ✗ | ✗ | ✗ |  | ✗ | ✗ | ✗ | ✗ |  | ✗ | ✗ | ✗ | ✗ | ✗ |  | 1/3 |  |  |  |  |  | ✗ | ✗ |  | ✗ |  |  | ✗ | ✗ |  |
| `hard-math-cron-overlap` | maths logic | 3/5 | ✓ | ✓ |  |  |  |  |  |  |  | ✓ | 3/5 | 4/5 | ✓ |  | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✗ | ✓ | 2/5 |  | ✓ |  |  |  |  |  | ✓ | ✓ |  | ✓ |  |  | 1/2 | 2/3 |  |
| `hard-math-retry-budget` | maths logic | ✓ | ✓ | ✓ |  |  |  |  |  |  |  | ✓ | ✓ | ✓ | ✓ |  | 4/5 | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | 1/5 |  | ✓ |  |  |  |  |  | ✓ | ✗ |  | ✓ |  |  | ✓ | ✓ |  |

## Charts

![Correct answers per hour](charts/correct_per_hour.png)

![Median time per task](charts/time_per_task.png)

![Pass rate vs file size](charts/pass_rate_vs_size.png)

![Qwen3.5-4B quant ladder](charts/quant_ladder_4b.png)


## Agent tier (`lab agent`)

The model works through tools over several turns (`tasks/agent.yaml`). Tool calls: scripted tools, graded on the calls and the final answer. Repo and project tasks: the model edits a made-up project with six file tools; hidden tests decide. Bad calls = unknown tool, invalid arguments or a missing required argument.

| Config | Thinking | Tool calls | Small repo tasks | Project tasks | All | Median steps (repo) | Median s per repo task | Largest prompt (tokens) | Bad calls | Not finished |
|---|---|---|---|---|---|---|---|---|---|---|
| `agent-gemma4-12b-qat-mtp-think` | on | 11/11 | 8/8 | – | **19/19** | 9 | 22 | 4220 | 0 | 1 |
| `agent-qwen36-35b-a3b-mtp-think` | on | 11/11 | 8/8 | – | **19/19** | 6 | 15 | 4390 | 0 | 0 |
| `agent-gemma4-26b-a4b-qat-mtp-think` | on | 11/11 | 8/8 | – | **19/19** | 10 | 38 | 4315 | 0 | 0 |
| `agent-katcoder-v25-dev-think` | on | 12/13 | 8/8 | 4/6 | **24/27** | 5 | 19 | 10517 | 0 | 0 |

Per agent task (passed / runs):

| Task | Tier | `gemma4-12b-qat-mtp-think` | `qwen36-35b-a3b-mtp-think` | `gemma4-26b-a4b-qat-mtp-think` | `katcoder-v25-dev-think` |
|---|---|---|---|---|---|
| `tc-single-call` | Tool calls | 1/1 | 1/1 | 1/1 | 1/1 |
| `tc-choose-tool` | Tool calls | – | – | – | 1/1 |
| `tc-no-tool-needed` | Tool calls | 1/1 | 1/1 | 1/1 | 1/1 |
| `tc-args-types` | Tool calls | 1/1 | 1/1 | 1/1 | 1/1 |
| `tc-two-step` | Tool calls | 1/1 | 1/1 | 1/1 | 0/1 |
| `tc-parallel` | Tool calls | 1/1 | 1/1 | 1/1 | 1/1 |
| `tc-use-result` | Tool calls | 1/1 | 1/1 | 1/1 | 1/1 |
| `tc-error-recovery` | Tool calls | 1/1 | 1/1 | 1/1 | 1/1 |
| `tc-escaping` | Tool calls | 1/1 | 1/1 | 1/1 | 1/1 |
| `tc-long-result` | Tool calls | 1/1 | 1/1 | 1/1 | 1/1 |
| `tc-missing-info` | Tool calls | – | – | – | 1/1 |
| `tc-unknown-tool` | Tool calls | 1/1 | 1/1 | 1/1 | 1/1 |
| `tc-chain-three` | Tool calls | 1/1 | 1/1 | 1/1 | 1/1 |
| `ag-py-fix-threshold` | Small repo tasks | 1/1 | 1/1 | 1/1 | 1/1 |
| `ag-py-add-reservations` | Small repo tasks | 1/1 | 1/1 | 1/1 | 1/1 |
| `ag-py-three-bugs` | Small repo tasks | 1/1 | 1/1 | 1/1 | 1/1 |
| `ag-py-rename` | Small repo tasks | 1/1 | 1/1 | 1/1 | 1/1 |
| `ag-py-parse-env` | Small repo tasks | 1/1 | 1/1 | 1/1 | 1/1 |
| `ag-py-json-format` | Small repo tasks | 1/1 | 1/1 | 1/1 | 1/1 |
| `ag-js-fix-money` | Small repo tasks | 1/1 | 1/1 | 1/1 | 1/1 |
| `ag-js-title-case` | Small repo tasks | 1/1 | 1/1 | 1/1 | 1/1 |
| `ag-depot-weight` | Project tasks | – | – | – | 1/1 |
| `ag-depot-cancel` | Project tasks | – | – | – | 1/1 |
| `ag-depot-coupon` | Project tasks | – | – | – | 0/1 |
| `ag-depot-dates` | Project tasks | – | – | – | 0/1 |
| `ag-depot-rename-field` | Project tasks | – | – | – | 1/1 |
| `ag-depot-merge` | Project tasks | – | – | – | 1/1 |

## Needle in a haystack (`lab needle`)

| Machine | Config | Prompt tokens | Depth | Found | Prefill s | Prefill tok/s | Answer |
|---|---|---|---|---|---|---|---|
| laptop | `qwen35-4b-q4km-vulkan-nothink` | 4042 | 0.50 | yes | 19.6 | 206 | `7481-QX` |
| laptop | `qwen35-4b-q4km-vulkan-nothink` | 16377 | 0.50 | yes | 178.3 | 92 | `7481-QX` |
| laptop | `qwen35-4b-q4km-vulkan-nothink` | ~32768 | 0.50 | **error**: {"code": 500, "message": "decode() failed: vk::Device::getFe | – | – | `` |
| pc | `gemma4-12b-qat-mtp-cuda-nothink` | 4048 | 0.50 | yes | 1.4 | 2857 | `7481-QX` |
| pc | `gemma4-12b-qat-mtp-cuda-nothink` | 16366 | 0.50 | yes | 5.6 | 2932 | `7481-QX` |
| pc | `gemma4-12b-qat-mtp-cuda-nothink` | 32751 | 0.50 | yes | 12.5 | 2611 | `7481-QX` |
| pc | `gemma4-26b-a4b-qat-mtp-cuda-nothink` | 4048 | 0.50 | yes | 4.9 | 826 | `7481-QX` |
| pc | `gemma4-26b-a4b-qat-mtp-cuda-nothink` | 16366 | 0.50 | yes | 11.0 | 1482 | `7481-QX` |
| pc | `gemma4-12b-qat-mtp-cuda-nothink` | 65514 | 0.10 | yes | 31.0 | 2113 | `7481-QX` |
| pc | `gemma4-12b-qat-mtp-cuda-nothink` | 65514 | 0.90 | yes | 31.1 | 2110 | `7481-QX` |
| pc | `qwen38-27b-gsqrco-iq2xs-mtp-cuda-nothink` | 4042 | 0.50 | yes | 4.0 | 1012 | `7481-QX` |
| pc | `qwen38-27b-gsqrco-iq2xs-mtp-cuda-nothink` | 16377 | 0.50 | yes | 15.6 | 1052 | `7481-QX` |

## llama-bench (`lab bench`)

| Date | Machine | Config | Build | Test | t/s | ± |
|---|---|---|---|---|---|---|
| 2026-09-25T13:23 | laptop | `qwen35-4b-q4km-vulkan-nothink` | 11157 | pp48 | 81.19 | 3.06 |
| 2026-09-25T13:23 | laptop | `qwen35-4b-q4km-vulkan-nothink` | 11157 | pp50 | 82.08 | 0.54 |
| 2026-09-25T13:23 | laptop | `qwen35-4b-q4km-vulkan-nothink` | 11157 | pp51 | 83.69 | 1.01 |
| 2026-09-25T13:23 | laptop | `qwen35-4b-q4km-vulkan-nothink` | 11157 | pp52 | 89.90 | 0.53 |
| 2026-09-25T13:23 | laptop | `qwen35-4b-q4km-vulkan-nothink` | 11157 | pp55 | 91.15 | 2.30 |
| 2026-09-25T13:23 | laptop | `qwen35-4b-q4km-vulkan-nothink` | 11157 | pp56 | 95.66 | 1.08 |
| 2026-09-25T13:23 | laptop | `qwen35-4b-q4km-vulkan-nothink` | 11157 | pp64 | 102.13 | 1.46 |
| 2026-09-25T14:38 | laptop | `gemma4-e4b-q4km-vulkan-nothink` | 11157 | pp512 | 348.55 | 1.73 |
| 2026-09-25T14:38 | laptop | `gemma4-e4b-q4km-vulkan-nothink` | 11157 | tg128 | 13.18 | 0.06 |
| 2026-09-25T14:39 | laptop | `gemma4-e4b-qat-udq4kxl-vulkan-nothink` | 11157 | pp512 | 404.52 | 2.43 |
| 2026-09-25T14:39 | laptop | `gemma4-e4b-qat-udq4kxl-vulkan-nothink` | 11157 | tg128 | 12.22 | 0.09 |
| 2026-10-02T04:28 | pc | `gemma4-12b-qat-udq4kxl-cuda-nothink` | 11321 | pp512 | 3571.81 | 136.36 |
| 2026-10-02T04:28 | pc | `gemma4-12b-qat-udq4kxl-cuda-nothink` | 11321 | tg128 | 78.46 | 0.18 |
| 2026-10-02T04:28 | pc | `gemma4-12b-qat-udq4kxl-cuda-nothink` | 11321 | pp512 @ d8192 | 2997.16 | 26.90 |
| 2026-10-02T04:28 | pc | `gemma4-12b-qat-udq4kxl-cuda-nothink` | 11321 | tg128 @ d8192 | 73.84 | 0.23 |
| 2026-10-02T04:28 | pc | `qwen38-27b-gsqrco-iq2xs-mtp-cuda-nothink` | 11321 | pp512 | 1149.85 | 32.26 |
| 2026-10-02T04:28 | pc | `qwen38-27b-gsqrco-iq2xs-mtp-cuda-nothink` | 11321 | tg128 | 49.37 | 0.17 |
| 2026-10-02T04:28 | pc | `qwen38-27b-gsqrco-iq2xs-mtp-cuda-nothink` | 11321 | pp512 @ d8192 | 1084.89 | 9.06 |
| 2026-10-02T04:28 | pc | `qwen38-27b-gsqrco-iq2xs-mtp-cuda-nothink` | 11321 | tg128 @ d8192 | 47.83 | 0.18 |
| 2026-10-02T04:30 | pc | `gemma4-26b-a4b-qat-cuda-nothink` | 11321 | pp512 | 329.79 | 1.25 |
| 2026-10-02T04:30 | pc | `gemma4-26b-a4b-qat-cuda-nothink` | 11321 | tg128 | 12.11 | 0.05 |
| 2026-10-02T04:30 | pc | `gemma4-26b-a4b-qat-cuda-nothink` | 11321 | pp512 @ d8192 | 213.53 | 3.94 |
| 2026-10-02T04:30 | pc | `gemma4-26b-a4b-qat-cuda-nothink` | 11321 | tg128 @ d8192 | 9.40 | 0.04 |
| 2026-10-02T04:33 | pc | `qwen36-35b-a3b-udq4km-mtp-cuda-nothink` | 11321 | pp512 | 154.65 | 0.16 |
| 2026-10-02T04:33 | pc | `qwen36-35b-a3b-udq4km-mtp-cuda-nothink` | 11321 | tg128 | 6.52 | 0.00 |
| 2026-10-02T04:33 | pc | `qwen36-35b-a3b-udq4km-mtp-cuda-nothink` | 11321 | pp512 @ d8192 | 117.33 | 11.60 |
| 2026-10-02T04:33 | pc | `qwen36-35b-a3b-udq4km-mtp-cuda-nothink` | 11321 | tg128 @ d8192 | 9.49 | 0.05 |
| 2026-10-02T04:34 | pc | `gemma4-26b-a4b-qat-cuda-nothink` | 11321 | pp512 ncmoe12 | 1125.24 | 154.01 |
| 2026-10-02T04:34 | pc | `gemma4-26b-a4b-qat-cuda-nothink` | 11321 | tg128 ncmoe12 | 85.74 | 0.19 |
| 2026-10-02T04:34 | pc | `gemma4-26b-a4b-qat-cuda-nothink` | 11321 | pp512 @ d8192 ncmoe12 | 1039.16 | 18.28 |
| 2026-10-02T04:34 | pc | `gemma4-26b-a4b-qat-cuda-nothink` | 11321 | tg128 @ d8192 ncmoe12 | 78.56 | 3.99 |
| 2026-10-02T04:35 | pc | `qwen36-35b-a3b-udq4km-mtp-cuda-nothink` | 11321 | pp512 ncmoe26 | 245.56 | 2.44 |
| 2026-10-02T04:35 | pc | `qwen36-35b-a3b-udq4km-mtp-cuda-nothink` | 11321 | tg128 ncmoe26 | 73.14 | 0.30 |
| 2026-10-02T04:35 | pc | `qwen36-35b-a3b-udq4km-mtp-cuda-nothink` | 11321 | pp512 @ d8192 ncmoe26 | 618.23 | 9.27 |
| 2026-10-02T04:35 | pc | `qwen36-35b-a3b-udq4km-mtp-cuda-nothink` | 11321 | tg128 @ d8192 ncmoe26 | 72.66 | 0.34 |
| 2026-10-02T04:35 | pc | `gptoss-20b-q4km-cuda-lowreason` | 11321 | pp512 ncmoe3 | 3207.05 | 154.42 |
| 2026-10-02T04:35 | pc | `gptoss-20b-q4km-cuda-lowreason` | 11321 | tg128 ncmoe3 | 134.35 | 0.59 |
| 2026-10-02T04:35 | pc | `gptoss-20b-q4km-cuda-lowreason` | 11321 | pp512 @ d8192 ncmoe3 | 2985.59 | 10.81 |
| 2026-10-02T04:35 | pc | `gptoss-20b-q4km-cuda-lowreason` | 11321 | tg128 @ d8192 ncmoe3 | 124.92 | 0.10 |
