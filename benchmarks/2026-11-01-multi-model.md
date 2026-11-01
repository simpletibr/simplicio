# Simplicio 3.10.8 with four models (2026-11-01)

A real model creates a file and edits it in the same session, once per run, with and without Simplicio. Four models, three tasks, 138 sessions. Per-session data: [2026-11-01-multi-model.json](2026-11-01-multi-model.json).

## Result

Medians. Cost comes from the tokens used at each model's list price, so it does not depend on the plan of the account that ran the session. Output tokens include reasoning.

| Model | Client | Task | Setup | n | Time | Model requests | Output tokens | Cost | Delivered |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| Claude Sonnet 5.5 | Claude Code 2.1.316 | Page from a JSON file, a generator covers it | Simplicio 3.10.8 | 5 | 17.5 s | 8 | 1,270 | US$ 0.0672 | 5/5 |
|  |  |  | No MCP | 5 | 33.4 s | 5 | 5,147 | US$ 0.0927 | 5/5 |
|  |  | New page, other data, other language, not used to build the generator | Simplicio 3.10.8 | 5 | 16.3 s | 8 | 1,084 | US$ 0.0514 | 5/5 |
|  |  |  | No MCP | 5 | 22.5 s | 5 | 2,819 | US$ 0.0610 | 5/5 |
|  |  | Python script, no generator covers it | Simplicio 3.10.8 | 5 | 19.6 s | 7 | 1,582 | US$ 0.0548 | 5/5 |
|  |  |  | No MCP | 5 | 11.4 s | 5 | 644 | US$ 0.0283 | 5/5 |
| Grok 4.7 | Grok Build 1.0.46 | Page from a JSON file, a generator covers it | Simplicio 3.10.8 | 3 | 31.0 s | 8 | 1,289 | US$ 0.1690 | 3/3 |
|  |  |  | No MCP | 3 | 359.7 s | 19 | 28,247 | US$ 0.8590 | 3/3 |
|  |  | New page, other data, other language, not used to build the generator | Simplicio 3.10.8 | 3 | 36.0 s | 8 | 1,598 | US$ 0.2059 | 3/3 |
|  |  |  | No MCP | 3 | 387.5 s | 22 | 27,598 | US$ 0.8518 | 3/3 |
|  |  | Python script, no generator covers it | Simplicio 3.10.8 | 3 | 82.0 s | 11 | 5,510 | US$ 0.3315 | 3/3 |
|  |  |  | No MCP | 3 | 63.1 s | 9 | 4,009 | US$ 0.2452 | 3/3 |
| Claude Haiku 5.5 | OpenCode 2.1.4 | Page from a JSON file, a generator covers it | Simplicio 3.10.8 | 5 | 13.7 s | 6 | 918 | US$ 0.0046 | 5/5 |
|  |  |  | No MCP | 5 | 29.3 s | 5 | 6,917 | US$ 0.0083 | 5/5 |
|  |  | New page, other data, other language, not used to build the generator | Simplicio 3.10.8 | 5 | 13.8 s | 6 | 794 | US$ 0.0023 | 5/5 |
|  |  |  | No MCP | 5 | 28.7 s | 5 | 6,310 | US$ 0.0057 | 5/5 |
|  |  | Python script, no generator covers it | Simplicio 3.10.8 | 5 | 19.2 s | 7 | 1,583 | US$ 0.0033 | 5/5 |
|  |  |  | No MCP | 5 | 16.6 s | 7 | 1,358 | US$ 0.0030 | 5/5 |
| DeepSeek V4.1 Flash | OpenCode 2.1.4 | Page from a JSON file, a generator covers it | Simplicio 3.10.8 | 10 | 14.1 s | 6 | 602 | US$ 0.0021 | 10/10 |
|  |  |  | No MCP | 10 | 176.3 s | 32.5 | 17,929 | US$ 0.0203 | 10/10 |
|  |  |  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | US$ 0.0215 | 10/10 |
|  |  | New page, other data, other language, not used to build the generator | Simplicio 3.10.8 | 6 | 14.1 s | 6 | 524 | US$ 0.0010 | 6/6 |
|  |  |  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | US$ 0.0153 | 6/6 |
|  |  | Python script, no generator covers it | Simplicio 3.10.8 | 6 | 30.7 s | 10.5 | 1,796 | US$ 0.0031 | 6/6 |
|  |  |  | No MCP | 6 | 22.7 s | 8 | 1,268 | US$ 0.0024 | 6/6 |
|  |  |  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | US$ 0.0051 | 6/6 |

## What this does not show

- The gain comes from the generator. On the script, no generator covers the task, and no MCP was faster and cheaper on every model:
  - Claude Sonnet 5.5: 19.6 s and US$ 0.0548 with Simplicio, 11.4 s and US$ 0.0283 without.
  - Grok 4.7: 82.0 s and US$ 0.3315 with Simplicio, 63.1 s and US$ 0.2452 without.
  - Claude Haiku 5.5: 19.2 s and US$ 0.0033 with Simplicio, 16.6 s and US$ 0.0030 without.
  - DeepSeek V4.1 Flash: 30.7 s and US$ 0.0031 with Simplicio, 22.7 s and US$ 0.0024 without.
- A valid request the closed scope does not recognise takes the slower path. On a frozen set, 10 of 15 valid requests reached the generator, and 15 of 15 invalid requests were refused.
- Each model ran in one client. Compare a model with itself, not one model with another.
- Few sessions: 5 per setup, 3 for Grok 4.7. DeepSeek V4.1 Flash keeps the [2026-10-31 round](2026-10-31-map-codegen.md), with 10 and 6 sessions, and compares with 3.9.2 on the new page, the one task it did not run without MCP.
- These are three small tasks. Other tasks and models will give other numbers.
- GPT, Muse and Qwen are not here. A GPT-6 Luna round and a repeat of the DeepSeek round were discarded: a queue that should have stopped kept running and shared work folders with them. Every session in this report ran with its folder to itself.

## Method

- Simplicio 3.10.8, release binary, sha256 starts with `08cada751c31df6b`. Both setups of a model use the same client, the same model and a new git repository per session.
- Claude Sonnet 5.5 ran in Claude Code 2.1.316, and Grok 4.7 in Grok Build 1.0.46, headless, with no user configuration. Time and tokens come from their session logs.
- Claude Haiku 5.5 and DeepSeek V4.1 Flash ran in OpenCode 2.1.4 through OpenRouter, each on one fixed endpoint. Time and tokens come from the OpenCode session database.
- Time is the wall clock of the two turns of a session.
- List prices per million tokens, in US$:
  - Claude Sonnet 5.5: 2 input, 10 output and reasoning, 0.1 cache read, 2.5 cache write.
  - Grok 4.7: 2 input, 6 output and reasoning, 0.5 cache read, 2 cache write.
  - Claude Haiku 5.5: 0.1 input, 0.5 output and reasoning, 0.01 cache read, 0.125 cache write.
  - DeepSeek V4.1 Flash: 0.15 input, 0.6 output and reasoning, 0.003 cache read, 0.15 cache write.
- Delivery is checked outside the session, as in the [2026-10-31 report](2026-10-31-map-codegen.md#method). Headless Chrome opens each page and tests rows, search, sort, filter and counter. `stats.py` is executed and its counts are compared with the data. The data file must stay unchanged.
- The prompts are the ones in that report.
