# Simplicio 3.10.8 against 3.9.2 and no MCP (2026-10-31)

A real model creates a file and edits it in the same session, once per run. Three tasks, three setups, 60 sessions. Per-session data: [2026-10-31-map-codegen.json](2026-10-31-map-codegen.json).

## Result

Medians. Cost is computed from the tokens at US$ 0.15 input, 0.60 output and 0.003 cache read per million tokens.

| Task | Setup | n | Time | Model requests | Output tokens | Cost | Delivered |
|---|---|---:|---:|---:|---:|---:|---:|
| Page from a JSON file, a generator covers it | Simplicio 3.10.8 | 10 | 14.1 s | 6 | 602 | US$ 0.0021 | 10/10 |
| | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | US$ 0.0215 | 10/10 |
| | No MCP | 10 | 176.3 s | 32.5 | 17,929 | US$ 0.0203 | 10/10 |
| New page, other data, other language, not used to build the generator | Simplicio 3.10.8 | 6 | 14.1 s | 6 | 524 | US$ 0.0010 | 6/6 |
| | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | US$ 0.0153 | 6/6 |
| Python script, no generator covers it | Simplicio 3.10.8 | 6 | 30.7 s | 10.5 | 1,796 | US$ 0.0031 | 6/6 |
| | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | US$ 0.0051 | 6/6 |
| | No MCP | 6 | 22.7 s | 8 | 1,268 | US$ 0.0024 | 6/6 |

On the two page tasks, `simplicio_map` routed the request and `simplicio_codegen` wrote the page with 0 LLM tokens, in every session. No session ended with a false `done: true`. No model opened a browser on the Simplicio 3.10.8 runs; on the page task, the other two setups did so 126 times to check their own work.

## What this does not show

- The gain comes from the generator. On the script, Simplicio 3.10.8 beats 3.9.2 but costs about 8 s and US$ 0.0007 more per session than no MCP at all.
- The closed scope sends a valid request it does not recognise to the slower path. On a frozen set, 10 of 15 valid requests reached the generator, and 15 of 15 invalid requests were refused.
- It is one model on three small tasks. Other tasks and models will give other numbers.
- 3.9.2 varies a lot between runs: its median on the page task ranged from 127 s to 234 s across three rounds of the same day, on two model routes.
- The no MCP setup did not run on the second task. It was removed to save time and money, because the acceptance criteria compare 3.10.8 with 3.9.2 only.

## Method

- Client: OpenCode 2.1.4, one private server per session, a new git repository per session.
- Model: `deepseek/deepseek-v4.1-flash-1017` through OpenRouter, on one fixed endpoint (Cloudflare), for all setups.
- Simplicio 3.10.8 was measured on commit 6e232bb. The release adds free native reads and a change to the `simplicio_map` description past its first 120 characters, the ones OpenCode shows. One real session per task with the release code delivered: page 18 s, new page 16 s, script 25 s.
- Time, requests and tokens come from the OpenCode session database.
- Delivery is checked outside the session. Headless Chrome opens each page and tests rows, search, sort, filter and counter. `stats.py` is executed and its counts are compared with the data. The data file must stay unchanged.

## Prompts

Page:

> Crie o arquivo users.html na raiz deste projeto. Ele deve ser uma pagina HTML standalone, sem CDN e sem dependencias externas, que abre direto do disco (file://). Incorpore os dados de users.json no proprio HTML e renderize uma tabela com nome, email, papel, status e data de criacao. Inclua busca em tempo real por nome ou email e ordenacao por coluna ao clicar no cabecalho. Layout limpo e responsivo. Nao altere users.json. Ao terminar, responda apenas OK.

> Na mesma users.html, adicione um filtro por status com as opcoes todos, ativo e inativo, e um contador no formato 'X de Y usuarios' que respeite a busca e o filtro juntos. Preserve todo o comportamento existente, inclusive a ordenacao. Nao altere users.json. Ao terminar, responda apenas OK.

New page:

> Create catalog.html in the project root. It must be a standalone HTML page, no CDN and no external dependencies, that opens directly from disk. Embed the data from products.json in the HTML and render a table with sku, name, category, price and stock. Add live search by name and column sorting when clicking a header. Keep the layout clean and responsive. Do not change products.json. When finished, reply only OK.

> In the same catalog.html, add a filter by category and a counter in the format 'X of Y products' that respects the search and the filter together. Keep all existing behavior, including sorting. Do not change products.json. When finished, reply only OK.

Script:

> Crie o arquivo stats.py na raiz deste projeto: um script Python 3 sem dependencias externas que le users.json e imprime, em JSON, o total de usuarios e a contagem por papel, no formato {"total": N, "por_papel": {"Admin": N}}. Nao altere users.json. Ao terminar, responda apenas OK.

> No mesmo stats.py, adicione uma opcao --status que limita a contagem aos usuarios com aquele status, e inclua no JSON a chave "status" com o valor usado, ou null sem a opcao. Preserve o comportamento existente. Nao altere users.json. Ao terminar, responda apenas OK.
