# Standard benchmark: no Simplicio, Simplicio 3.14.0 and Simplicio 3.15.0 (2026-11-22)

One agent, one model and one job, run three times with each setup. The job is three steps in one conversation: build a user listing, change it, add a simple registration. After every step the result is checked from outside the session. Per-session data: [2026-11-22-standard-benchmark.json](2026-11-22-standard-benchmark.json). The chart in the README is drawn from that file.

## Result

Medians of 3 sessions per setup, with the lowest and highest session in brackets. A session total is the sum of its three steps. Bold marks the best value in a row, only where its range does not overlap the other two.

| Measure | No Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| Time for the whole job | 121 s (97 to 172) | 104 s (90 to 106) | **25 s (23 to 27)** |
| Cost reported by the agent | $0.0226 (0.0186 to 0.0280) | $0.0220 (0.0214 to 0.0249) | **$0.0076 (0.0071 to 0.0098)** |
| Cost from a fixed price table | $0.0181 (0.0153 to 0.0227) | $0.0184 (0.0180 to 0.0223) | **$0.0056 (0.0052 to 0.0073)** |
| Output tokens | 18,162 (15,599 to 23,328) | 19,722 (18,764 to 24,997) | **3,211 (3,068 to 3,573)** |
| of which reasoning tokens | 4,457 (3,973 to 9,221) | 9,109 (6,510 to 12,479) | **1,488 (1,302 to 1,663)** |
| Input tokens | 34,691 (30,447 to 42,543) | 34,141 (33,121 to 40,017) | 18,755 (18,466 to 33,300) |
| Cache-read tokens | 655,730 (473,821 to 787,484) | 475,977 (443,908 to 604,660) | **177,700 (161,356 to 206,516)** |
| Model requests | 25 (19 to 33) | 18 (18 to 22) | **10 (10 to 10)** |
| Tool calls | 22 (16 to 30) | 15 (15 to 19) | **7 (7 to 7)** |
| CPU time | 8.5 s (8.5 to 9.2) | 10.0 s (8.9 to 10.0) | **5.3 s (5.3 to 5.5)** |
| Peak memory | **270 MB (248 to 274)** | 436 MB (432 to 439) | 375 MB (365 to 379) |
| Steps delivered | 9 of 9 | 9 of 9 | 9 of 9 |

"9 of 9" means 3 steps in each of 3 sessions. Every step passed every outside check, in every setup.

Every session, not only the median:

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-sessions-dark.svg">
    <img src="../assets/benchmark-2026-11-22-sessions-light.svg" width="840" alt="Scatter plot of every session, with the time for the whole job across and the cost reported by the agent up. Simplicio 3.15.0, green diamonds: 23 to 27 s and $0.0071 to $0.0098. Simplicio 3.14.0, grey squares: 90 to 106 s and $0.0214 to $0.0249. No Simplicio, hollow circles: 97 to 172 s and $0.0186 to $0.0280.">
  </picture>
</p>

Input tokens: the range of Simplicio 3.15.0 (18,466 to 33,300) overlaps the range without Simplicio (30,447 to 42,543). This run claims no difference in input tokens.

### By step

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-steps-dark.svg">
    <img src="../assets/benchmark-2026-11-22-steps-light.svg" width="840" alt="Median time by step on one shared scale. Step 1, build: 57.3 s with no Simplicio, 53.7 s with Simplicio 3.14.0 and 5.8 s with Simplicio 3.15.0. Step 2, change: 17.3 s, 15.2 s and 8.9 s. Step 3, register: 31.4 s, 27.5 s and 10.3 s.">
  </picture>
</p>

Median time of each step, with the lowest and highest session in brackets:

| Step | No Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. Build a user listing | 57.3 s (48.4 to 129.4) | 53.7 s (50.4 to 61.7) | 5.8 s (5.0 to 5.9) |
| 2. Change the listing | 17.3 s (14.5 to 20.8) | 15.2 s (14.4 to 15.7) | 8.9 s (7.6 to 10.5) |
| 3. Add a simple registration | 31.4 s (28.3 to 43.2) | 27.5 s (24.1 to 37.5) | 10.3 s (9.4 to 10.9) |

Median cost of each step as reported by the agent, in US dollars:

| Step | No Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. Build a user listing | $0.0111 (0.0089 to 0.0128) | $0.0137 (0.0125 to 0.0139) | $0.0022 (0.0021 to 0.0049) |
| 2. Change the listing | $0.0040 (0.0032 to 0.0047) | $0.0032 (0.0029 to 0.0034) | $0.0023 (0.0022 to 0.0029) |
| 3. Add a simple registration | $0.0075 (0.0065 to 0.0105) | $0.0056 (0.0052 to 0.0080) | $0.0026 (0.0025 to 0.0027) |

### Ratios

Computed from the unrounded medians, then rounded.

| Comparison | Time | Cost reported by the agent | Output tokens | Model requests | Tool calls | CPU time | Peak memory |
|---|---|---|---|---|---|---|---|
| Simplicio 3.15.0 against no Simplicio | 4.89 times faster (80% less time) | 66% less (2.97 times cheaper) | 82% fewer | 60% fewer | 68% fewer | 38% less | 39% more |
| Simplicio 3.15.0 against Simplicio 3.14.0 | 4.18 times faster (76% less time) | 66% less (2.90 times cheaper) | 84% fewer | 44% fewer | 53% fewer | 47% less | 14% less |

Simplicio 3.14.0 against no Simplicio: the cost is the same ($0.0220 against $0.0226) and the time ranges overlap (90 to 106 s against 97 to 172 s). No difference can be claimed.

## What was measured

### The job

One agent session per run. The session has three steps. Each step is a separate call of the agent that resumes the same conversation, so the agent keeps what it built in the earlier steps.

The prompts are in Portuguese, as they were sent. The English translations are for reading only.

**Step 1, build a user listing**

> Crie do zero o cadastro de usuarios deste projeto, seguindo o README. Tabela usuarios (id, nome, email, papel, status, criado_em) em schema.sql; GET /api/usuarios devolve um array JSON com todos os usuarios; e a pagina web/usuarios.html mostra a tabela com nome, email, papel e status, com busca por nome ou email e ordenacao ao clicar no cabecalho. Ao terminar, responda apenas OK.

Translation: Build the user registry of this project from scratch, following the README. A `usuarios` table (id, nome, email, papel, status, criado_em) in `schema.sql`; `GET /api/usuarios` returns a JSON array with all users; and the page `web/usuarios.html` shows the table with name, e-mail, role and status, with search by name or e-mail and sorting when the header is clicked. When done, answer only OK.

**Step 2, change the listing**

> Volte na listagem: tire a coluna papel da tabela e coloque no lugar um filtro por papel acima dela; e acrescente a coluna criado_em no formato dd/mm/aaaa. Ao terminar, responda apenas OK.

Translation: Go back to the listing: remove the role column from the table and put a filter by role above it instead; and add the `criado_em` column in the format dd/mm/yyyy. When done, answer only OK.

**Step 3, add a simple registration**

> Agora o cadastro: POST /api/usuarios cria um usuario e responde 201 com o usuario criado (com id); nome e email sao obrigatorios e o email e unico. Crie a pagina web/usuario_novo.html com o formulario, que volta para a listagem depois de salvar. Ao terminar, responda apenas OK.

Translation: Now the registration: `POST /api/usuarios` creates a user and answers 201 with the created user (with an id); name and e-mail are required and the e-mail is unique. Create the page `web/usuario_novo.html` with the form, which goes back to the listing after saving. When done, answer only OK.

### The checks

After each step the harness starts the `server.py` that the agent wrote (`python3 server.py --port <free port> --db <temporary file>`), runs the checks below against it over HTTP, and loads the pages in headless Chrome to read the page after its scripts have run. A step counts as delivered when every check of that step passes. The checks of the earlier steps run again, so a step also fails if it breaks something built before.

| Check | Runs from step | What it requires |
|---|---|---|
| `list_api` | 1 | `GET /api/usuarios` answers 200 with a JSON array that has at least the 24 starting users, each with the fields id, nome, email, papel, status and criado_em, and every starting e-mail present |
| `list_page` | 1 | `/usuarios.html`, rendered by headless Chrome, shows the e-mail of every one of the 24 starting users |
| `date_column` | 2 | the rendered listing shows `criado_em` as dd/mm/yyyy for at least 20 of the 24 users |
| `no_role_column` | 2 | the rendered table has header cells and none of them contains "papel" |
| `role_filter` | 2 | the rendered page has a `<select>` and the five role names (Admin, Editor, Viewer, Analyst, Support) |
| `create_ok` | 3 | `POST /api/usuarios` with a new name and e-mail answers 201 with an object that has an `id`, and the new user shows up in the next `GET` |
| `create_without_name_rejected` | 3 | a `POST` without a name answers 400 |
| `create_duplicate_email_rejected` | 3 | a `POST` with an e-mail that is already in the list answers 400 |
| `new_user_page` | 3 | `/usuario_novo.html` answers 200 and has a form or an input that mentions name and e-mail |

Step 1 runs 2 checks, step 2 runs 5 and step 3 runs all 9.

The checks are narrower than the prompts. They do not test the search box, sorting by header, the redirect after saving, the look of the page or the quality of the code. A result that passes them is a working API and working pages of the shape described above, not a reviewed product.

### The seed project

Every session starts in its own new git repository with the same 13 files:

- `README.md`, the house rules of the project (below).
- `dados/usuarios.json`, 24 starting users. Each has a name, an e-mail address on example.com, one of five roles, one of two statuses and a creation date in 2026. The 24 dates are all different.
- `.gitignore`.
- Ten short files: `docs/arquitetura.md`, `docs/convencoes.md`, `docs/api.md`, `docs/deploy.md`, `scripts/dev.sh`, `scripts/limpa_banco.sh`, `tests/README.md`, `CHANGELOG.md`, `CONTRIBUTING.md` and `.editorconfig`.

There is no `server.py`, no `schema.sql` and no page at the start. The agent writes them. The `README.md` is:

```markdown
# Cadastro de usuarios

Projeto novo. Regras da casa:

- Somente a biblioteca padrao do Python 3 (http.server, sqlite3, json). Nada de pacotes externos, CDN ou build.
- `server.py` sobe tudo: `python3 server.py --port 8000 --db dados/app.sqlite3`. Os dois argumentos existem sempre; os valores acima sao os padroes.
- A API responde JSON em `/api/...`. Erro de validacao responde 400 com `{"erro": "mensagem"}`; recurso inexistente responde 404.
- As paginas ficam em `web/` e sao servidas na raiz: `web/usuarios.html` abre em `/usuarios.html`. HTML, CSS e JavaScript puros, chamando a API com fetch.
- O esquema do banco fica em `schema.sql`. O servidor cria o banco quando ele nao existe.
- `dados/usuarios.json` tem os usuarios iniciais; o servidor os carrega quando a tabela esta vazia.
```

## Setup

| Item | Value |
|---|---|
| Date | 2026-11-22 |
| Model | Claude Haiku 5.5 (`claude-haiku-5-5`), the same for every session |
| Agent | Claude Code CLI 2.1.330, run without a person at the keyboard, with permission prompts skipped. Each session used its own new configuration folder and its own project folder. The agent was given its MCP configuration explicitly, so no other MCP server was present |
| Machine | 4 CPUs, 16 GB of memory, no swap, Linux x86-64 |
| Concurrency | 4 sessions ran at the same time on that machine, so every wall time includes the contention between them. The round had 12 sessions and 9 are reported here. The other 3 belonged to a fourth setup, an unreleased development build that is not a published version and is not reported. It is the reason four sessions ran at once. Compare times only inside this run |
| Sessions | 3 per setup, 9 in this report (the round had 12, see Concurrency). Every reported session delivered every step |

**No Simplicio.** The same agent and model with the agent's own tools. No MCP server and no Simplicio configuration of any kind. This is Claude Code 2.1.330 working the way it works for anyone who has not installed Simplicio.

**Simplicio 3.14.0 and Simplicio 3.15.0.** The same agent and model with Simplicio set up the way the installer sets it up for Claude Code (`INSTALL.md` lists what the installer writes). The benchmark harness wrote that configuration itself and did not run the installer. Simplicio ran without its optional resident background process and with sign-in turned off. The two builds were compiled from the Runtime source commit that each release was published from:

| Setup | Release | Source commit |
|---|---|---|
| Simplicio 3.14.0 | 3.14.0 | `fe004296161fc693fde35f6fea663889886a061d` |
| Simplicio 3.15.0 | 3.15.0 | `d2bef403ff12914542fab777aa2c9ace6d8eca46` |

Sign-in was turned off for the automated run. The signed binaries that people download were not the ones executed.

**How each number was taken**

- *Time* is the wall-clock time of the agent call, summed over the three steps.
- *Cost reported by the agent* is `total_cost_usd`, which the agent CLI reports: the tokens used multiplied by the model's published price. It counts model tokens only. It is an estimate made by the agent, not an invoice. The CLI reports a running total for the conversation, so the cost of a step is the difference between the total after the step and the total before it.
- *Cost from a fixed price table* multiplies the tokens by one price list kept in the benchmark: $0.15 per million input tokens, $0.60 per million output tokens and $0.003 per million cache-read tokens. These are not the list prices of Claude Haiku 5.5. The row lets the three setups be compared on one price list and carries no other claim.
- *Output tokens* are the output tokens the agent CLI reports. They include the reasoning tokens of the model. The data file also lists the reasoning tokens alone; in all 9 sessions that count is at or below the output count.
- *Input tokens* are the tokens sent to the model that were not read from the cache. They include the tokens written to the cache. Tokens read from the cache are counted separately as cache-read tokens and are cheaper.
- *Model requests* is the number of model turns the agent reports. *Tool calls* is the number of tool calls the model made, its own tools and Simplicio's together.
- *CPU time* is the CPU time of the agent process and of everything it started, as the operating system accounts for the finished processes.
- *Peak memory* is the highest resident memory of that whole process tree, sampled every 400 ms. In megabytes, kilobytes divided by 1,024. A session value is the highest of its three steps.
- *Median and range.* The median is the middle value of the 3 sessions of a setup. The range is the lowest and the highest session. A difference smaller than the range is not claimed as a difference.
- *Rounding.* Session times are rounded to whole seconds, step times to one decimal, dollars to four decimals. Percentages are rounded to whole numbers from the unrounded medians.

## Where Simplicio did not win

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-memory-dark.svg">
    <img src="../assets/benchmark-2026-11-22-memory-light.svg" width="840" alt="Peak memory, median of 3 sessions: 270 MB with no Simplicio, the lowest; 436 MB with Simplicio 3.14.0, 61% more; 375 MB with Simplicio 3.15.0, 39% more.">
  </picture>
</p>

- **Memory.** Simplicio 3.15.0 used 375 MB at its peak against 270 MB without Simplicio, which is 39% more. The ranges do not overlap. Simplicio 3.14.0 used more still: 436 MB, which is 61% more than without Simplicio.
- **Simplicio 3.14.0 did not pay for itself on this job.** Its cost was the same as without Simplicio ($0.0220 against $0.0226). Its time (104 s against 121 s) is inside the spread of the runs, and so are its output tokens (19,722 against 18,162) and its CPU time (10.0 s against 8.5 s). The gain on this page arrived with 3.15.0.
- **A short one-off Python script, measured on an older release.** In the round of `2026-11-01-multi-model.md`, on a short one-off Python script that reads a data file and prints a count per role, Simplicio 3.10.8 was slower than the plain agent with each of the four models tried, and it cost more. The most direct case is Claude Sonnet 5.5 in Claude Code 2.1.316, 5 sessions per setup: 19.6 s and $0.0548 with Simplicio against 11.4 s and $0.0283 without. The other three were Grok 4.7 (82.0 s and $0.3315 against 63.1 s and $0.2452), Claude Haiku 5.5 in OpenCode (19.2 s and $0.0033 against 16.6 s and $0.0030) and DeepSeek V4.1 Flash in OpenCode (30.7 s and $0.0031 against 22.7 s and $0.0024). That task has not been measured again on Simplicio 3.15.0, so this page says nothing about it.
- **Small sample.** Three sessions per setup, one model, one project, one machine, four sessions at once. Read the ratios as a measurement of this job, not as a promise for yours.

## Limits

- **n = 3 per setup.** The median of three values is the middle one. It is a small sample and a spread is shown for every number.
- **One model.** Claude Haiku 5.5. Other models, including larger ones, were not run in this round.
- **One agent.** Claude Code 2.1.330. Other agents were not run in this round.
- **One project.** A new Python project of 13 small files, built from scratch with the standard library only. Large existing codebases, other languages and other kinds of work were not measured.
- **One run on one day, on one machine.** Provider load and machine load change from hour to hour.
- **Contention.** Four sessions shared 4 CPUs. Wall times, CPU times and memory include that sharing.
- **Builds from release commits.** The Simplicio builds are compiled from the source commits of the published releases, with sign-in turned off for the automated run. The signed binaries that people download were not executed, so CPU time and memory were not measured on them.
- **Cost is an estimate.** It is the agent's own calculation from tokens and a published price. It is not an invoice, and a plan with a flat fee or a different price list gives other dollar amounts.
- **The checks are narrower than the prompts.** See "The checks" above for what is not tested.
- **A round of 12 sessions, 9 reported.** The other 3 belonged to a fourth setup, an unreleased development build that is not a published version. It is not reported here. It is the reason four sessions ran at once.
- **One round.** The three setups ran in the same round, so the time of day and the load of the model provider affect them alike. A later run can give other numbers.

## Data

The file [2026-11-22-standard-benchmark.json](2026-11-22-standard-benchmark.json) holds every session behind the tables above, with its three steps. The chart in the README is drawn from it by `scripts/render_benchmark_chart.py`.

Top-level fields:

| Field | Meaning |
|---|---|
| `schema` | `simplicio.public-benchmark/v1` |
| `date` | Day of the run |
| `model` | Model id |
| `agent` | Agent name and version |
| `machine` | CPUs, memory, operating system, swap and the number of sessions that ran at the same time |
| `round` | How many sessions the round ran (`sessions_run`), how many are in this file (`sessions_published`), and a `note` that says why the two numbers differ |
| `arms` | The three setups. The key is the id used in `sessions`. Each has a `label` and the `release_commit` it was built from (`null` without Simplicio) |
| `sessions` | 9 records: `arm`, `rep` (1 to 3), `steps` and `totals` |

Fields of each step:

| Field | Meaning |
|---|---|
| `step`, `name` | 1 to 3 and its English name |
| `delivered` | `true` when every check of the step passed |
| `checks` | Check name to pass or fail, as listed in "The checks" |
| `wall_s` | Wall-clock time of the step in seconds |
| `cpu_s` | CPU time of the agent and what it started, in seconds |
| `peak_rss_mb` | Peak resident memory of that process tree, in MB |
| `cost_usd_cli` | Cost of this step as the agent CLI reports it, in US dollars. The steps of a session add up to its total |

Token, request and tool-call counts are published per session, not per step. Fields of the `totals` object of each session, the sums over its three steps:

| Field | Meaning |
|---|---|
| `input_tokens` | Tokens sent that were not read from the cache. Includes `cache_write_tokens` |
| `output_tokens` | Output tokens. Includes `reasoning_tokens` |
| `reasoning_tokens` | The part of the output tokens that the provider reports as reasoning |
| `cache_read_tokens` | Tokens read from the cache |
| `cache_write_tokens` | Tokens written to the cache |
| `model_requests` | Model turns in the session |
| `tool_calls` | Tool calls in the session |
| `cost_usd_table` | Cost of the session from the fixed price table, in US dollars |

To compare on your own work, run the same three prompts in your own agent, once with Simplicio and once without, in a small project of your own that has a README with house rules like the one above, and compare your own times and your own bill.
