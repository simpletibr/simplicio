# 🔥 Simplicio

<p align="center">
  <img src="../assets/simplicio-hero.png" alt="Simplicio — Agente de IA para codificação" width="920" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=blue&label=latest" alt="Último Lançamento"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Estrelas"></a>
  <a href="https://github.com/simpletibr/simplicio/releases"><img src="https://img.shields.io/github/downloads/simpletibr/simplicio/total?color=green" alt="Downloads"></a>
  <a href="../plugins/simplicio/LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="Licença"></a>
</p>

<p align="center">
  <a href="#-instalação">Instalar</a> ·
  <a href="#-o-que-faz">Funcionalidades</a> ·
  <a href="#-benchmark-2026-10-31">Benchmark</a> ·
  <a href="https://simpleti.com.br/simplicio/#start">Site</a>
</p>

<p align="center">
  <strong>🌍 Idiomas:</strong><br>
  <a href="../README.md">🇬🇧 English</a> |
  <a href="README.pt-BR.md">🇧🇷 Português</a> |
  <a href="README.es-ES.md">🇪🇸 Español</a> |
  <a href="README.fr-FR.md">🇫🇷 Français</a> |
  <a href="README.ja-JP.md">🇯🇵 日本語</a> |
  <a href="README.ko-KR.md">🇰🇷 한국어</a> |
  <a href="README.zh-CN.md">🇨🇳 简体中文</a> |
  <a href="README.it-IT.md">🇮🇹 Italiano</a> |
  <a href="README.ru-RU.md">🇷🇺 Русский</a> |
  <a href="README.pl-PL.md">🇵🇱 Polski</a> |
  <a href="README.hi-IN.md">🇮🇳 हिन्दी</a> |
  <a href="README.ar-SA.md">🇸🇦 العربية</a> |
  <a href="README.he-IL.md">🇮🇱 עברית</a> |
  <a href="README.ms-MY.md">🇲🇾 Bahasa Melayu</a> |
  <a href="README.id-ID.md">🇮🇩 Bahasa Indonesia</a>
</p>

---

## ⚡ TL;DR

**Simplicio** é um agente de IA de codificação para terminal — um único binário que substitui
todo o seu fluxo de desenvolvimento assistido por IA: chat, geração de código, contexto
de repositório, planejamento, orquestração local multi-agente (64 → 600 agentes) e
entrega de PR com evidências verificáveis.

**Roda na sua máquina. Seu código nunca sai do seu controle. Modelos remotos são
opcionais, não obrigatórios.**

> Cada interação mostra exatamente quantos tokens você economizou. Um único binário Rust, zero dependências.

## 🚀 Instalação

### Instalar pelo plugin do Codex

Se você usa o Codex, pode instalar o Simplicio como um plugin. Adicione o Marketplace público, instale o plugin e inicie uma nova sessão do Codex; o plugin instala e inicializa o Runtime do Simplicio e disponibiliza suas skills e ferramentas MCP.

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

Use o pacote oficial do PyPI. Ele instala o launcher Python, valida a release
assinada do Runtime e instala o binário correto para macOS, Linux ou Windows.

### Todos os sistemas via PyPI

macOS / Linux:

```bash
python3 -m pip install --upgrade simplicio-installer
simplicio install
simplicio version
simplicio auth login
simplicio auth status --json
simplicio ecosystem verify --json
```

No Windows (PowerShell), use `py -m pip install --upgrade simplicio-installer`
no lugar de `python3 -m pip ...`. O token do PyPI fica somente no ambiente de
publicação; nunca é copiado para o repositório.

### Instalação direta (sem PyPI)

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

O launcher instala o Runtime verificado em `~/.local/bin/simplicio` no
macOS/Linux ou `%USERPROFILE%\.local\bin\simplicio.exe` no Windows. Garanta que
o diretório de scripts do Python e esse diretório estejam no `PATH`; o launcher
não altera o perfil do shell. O login Google é necessário antes de usar o MCP
ou comandos autenticados.

---

## 📊 Benchmark (2026-10-31)

Um modelo real cria um arquivo e o edita na mesma sessão. O resultado é conferido fora da sessão: páginas no Chrome headless, scripts executados de verdade. 60 sessões, medianas.

| Tarefa | Configuração | n | Tempo | Requisições ao modelo | Tokens de saída | Custo | Entregas |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **Página a partir de um JSON, coberta por um gerador** | **Simplicio 3.10.8** | 10 | **14.1 s** | **6** | **602** | **$0.0021** | **10/10** |
|  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | $0.0215 | 10/10 |
|  | Sem MCP | 10 | 176.3 s | 32.5 | 17,929 | $0.0203 | 10/10 |
| **Página nova, com outros dados e outro idioma, fora da construção do gerador** | **Simplicio 3.10.8** | 6 | **14.1 s** | **6** | **524** | **$0.0010** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | $0.0153 | 6/6 |
| **Script Python, sem gerador que cubra** | **Simplicio 3.10.8** | 6 | **30.7 s** | **10.5** | **1,796** | **$0.0031** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | $0.0051 | 6/6 |
|  | Sem MCP | 6 | 22.7 s | 8 | 1,268 | $0.0024 | 6/6 |

O ganho vem do gerador: nas tarefas de página, o `simplicio_map` roteia o pedido e o `simplicio_codegen` escreve o arquivo com 0 tokens de LLM. Quando nenhum gerador cobre a tarefa, a 3.10.8 supera a 3.9.2 e custa cerca de 8 s e US$ 0,0007 a mais por sessão do que não usar MCP.

> OpenCode 2.1.4 e DeepSeek V4.1 Flash em um único endpoint do OpenRouter, igual em todas as rodadas. Custo calculado a US$ 0,15 de entrada, US$ 0,60 de saída e US$ 0,003 de cache por milhão de tokens. É um modelo em três tarefas pequenas: outras tarefas darão outros números. [Prompts, método, limites e dados por sessão](../benchmarks/2026-10-31-map-codegen.md).

---

## 🎯 O Que Faz

| Comando | Descrição |
|---|---|
| `simplicio map --repo .` | Mapeia o repositório para LLMs |
| `simplicio memory "consulta"` | Recuperação neural (FTS + vetores) |
| `simplicio edit '{...}'` | Edição determinística de arquivos |
| `simplicio coding-loop "tarefa"` | Itera até os testes passarem |
| `simplicio deliver certify` | 5 portais de qualidade antes do envio |
| `simplicio run "tarefa" --agents N` | Orquestração multi-agente |
---

## 🏗️ Arquitetura

```
LLM (Claude/Codex/Gemini)          Simplicio Runtime (Rust)
  |                                   |
  | 1. Orientar                       | simplicio map
  | 2. Recuperar                      | simplicio memory
  | 3. Decidir                        |
  | 4. Editar ──────────────────────> | simplicio edit (0 tokens)
  | 5. Verificar <─────────────────── | simplicio deliver certify
  | 6. Iterar                         | simplicio coding-loop
```

**O LLM raciocina. O Simplicio executa deterministicamente.**

---

## ✨ Funcionalidades

- 🏠 **Local-first** — llama.cpp embutido, escala para remoto somente quando necessário
- 🪜 **Agentes em camadas** — 64 → 100 → 200 → 600 agentes locais antes da nuvem paga
- 🔇 **Portão de novidade Shannon** — filtra saídas redundantes (zero tokens em dedup)
- 🔒 **Recibos lacrados** — sha256 por artefato, cadeia de evidências à prova de adulteração
- 🛡️ **5 portais de entrega** — aceitação, validação, execução-verificação, regressão, auto-revisão
- ⚡ **Portão de ação** — classificação de risco + lista de bloqueio para mutações iniciadas por chat
- 🔌 **MCP/ACP** — Protocolo de Contexto de Modelo + Protocolo de Cliente Agente
- 🌐 **Gateways** — Telegram, Discord, Slack, WhatsApp
- 🧩 **Sistema de skills** — carrega e encadeia capacidades reutilizáveis
- 💾 **Banco de memória** — FTS persistente + recall vetorial entre sessões
- 🔀 **Roteador de LLM** — sem LLM → LLM local → LLM remoto automaticamente
- 🖥️ **Multiplataforma** — macOS, Linux, Windows, binário único

---

## 🎁 Beta Público Gratuito

**Comandos determinísticos são GRATUITOS para sempre:**
`map`, `validate`, `edit`, `deliver`, `checkpoint`

**Funcionalidades de IA são gratuitas durante o beta público sem data de término.**
A cobrança será definida em atualizações futuras.

```bash
simplicio license status
```

---

## 📋 Requisitos

| Requisito | Mínimo | Recomendado |
|---|---|---|
| RAM | 8 GB | 16 GB+ |
| Armazenamento | 5 MB | 1.5 GB (com LLM local) |
| SO | macOS 13+, Linux, Windows 10+ | macOS ARM64 |
| Terminal | qualquer terminal moderno | WezTerm / Alacritty / Ghostty |

---

## 🌐 Ecossistema

- [Site](https://simpleti.com.br/simplicio/#start) — documentação completa, benchmarks, instalação
- [Discord](https://discord.gg/wM6tr7xVb) — comunidade e suporte

---

## 📄 Licença

Proprietária. Binário gratuito para baixar e usar. Funcionalidades de IA gratuitas
durante o beta público. Consulte [LICENSE](../plugins/simplicio/LICENSE).

---

## ⭐ Histórico de Estrelas

<a href="https://star-history.com/#simpletibr/simplicio&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" />
    <img alt="Gráfico do Histórico de Estrelas" src="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" width="100%" />
  </picture>
</a>

---

## 💬 Comunidade

- [Discord](https://discord.gg/wM6tr7xVb) — chat, suporte, acesso antecipado
- [GitHub Issues](https://github.com/simpletibr/simplicio/issues) — bugs e pedidos de funcionalidades

---

<p align="center">
  <strong>🔥 Simplicio 🔥</strong>
</p>
