# 🔥 Simplicio

<p align="center">
  <img src="../assets/simplicio-hero.png" alt="Simplicio — AI coding agent" width="920" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=blue&label=latest" alt="Ultima versione"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Stelle"></a>
  <a href="https://github.com/simpletibr/simplicio/releases"><img src="https://img.shields.io/github/downloads/simpletibr/simplicio/total?color=green" alt="Download"></a>
  <a href="../plugins/simplicio/LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="Licenza"></a>
</p>

<p align="center">
  <a href="#-installazione">Installa</a> ·
  <a href="#-cosa-fa">Funzionalità</a> ·
  <a href="#-benchmark-2026-10-31">Benchmark</a> ·
  <a href="https://simpleti.com.br/simplicio/#start">Sito web</a>
</p>

<p align="center">
  <strong>🌍 Lingue:</strong><br>
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

**Simplicio** è un agente AI da terminale — un singolo binario che sostituisce
l'intero flusso di lavoro di sviluppo assistito dall'AI: chat, generazione di codice,
contesto del repository, pianificazione, orchestrazione multi-agente locale (64 → 600 agenti),
e consegna di PR supportata da prove concrete.

**Funziona sulla tua macchina. Il tuo codice non lascia mai il tuo controllo. I modelli remoti sono
opzionali, non obbligatori.**

> Ogni interazione mostra esattamente quanti token hai risparmiato. Singolo binario Rust, zero dipendenze.

## 🚀 Installazione

### Installa tramite il plugin Codex

Se usi Codex, puoi installare Simplicio come plugin. Aggiungi il Marketplace pubblico, installa il plugin e avvia una nuova sessione Codex; il plugin installa e avvia il Runtime Simplicio e rende disponibili le sue skills e gli strumenti MCP.

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

### npm / npx (qualsiasi OS)

```bash
npx simplicio install
```

### pip / PyPI (qualsiasi OS)

```bash
pip install simplicio-installer
simplicio install
```

### Homebrew (macOS)

```bash
brew install simplicio
```

### Bun

```bash
bunx simplicio install
```

### macOS / Linux

```bash
python3 -m pip install --upgrade simplicio-installer
simplicio install
```

### Windows

```powershell
py -m pip install --upgrade simplicio-installer
simplicio install
```

### Installazione diretta (senza PyPI)

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

Fatto. Un comando. Nessun package manager, nessuna configurazione del modello.

---

## 📊 Benchmark (2026-10-31)

Un modello reale crea un file e lo modifica nella stessa sessione. Il risultato viene verificato fuori dalla sessione: le pagine in Chrome headless, gli script eseguendoli. 60 sessioni, mediane.

| Attività | Configurazione | n | Tempo | Richieste al modello | Token di output | Costo | Consegne |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **Pagina da un JSON, coperta da un generatore** | **Simplicio 3.10.8** | 10 | **14.1 s** | **6** | **602** | **$0.0021** | **10/10** |
|  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | $0.0215 | 10/10 |
|  | Senza MCP | 10 | 176.3 s | 32.5 | 17,929 | $0.0203 | 10/10 |
| **Nuova pagina, altri dati e altra lingua, non usata per costruire il generatore** | **Simplicio 3.10.8** | 6 | **14.1 s** | **6** | **524** | **$0.0010** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | $0.0153 | 6/6 |
| **Script Python, nessun generatore lo copre** | **Simplicio 3.10.8** | 6 | **30.7 s** | **10.5** | **1,796** | **$0.0031** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | $0.0051 | 6/6 |
|  | Senza MCP | 6 | 22.7 s | 8 | 1,268 | $0.0024 | 6/6 |

Il guadagno viene dal generatore: nelle attività di pagina, `simplicio_map` instrada la richiesta e `simplicio_codegen` scrive il file con 0 token LLM. Quando nessun generatore copre l'attività, la 3.10.8 batte la 3.9.2 e costa circa 8 s e 0,0007 $ in più a sessione rispetto a nessun MCP.

> OpenCode 2.1.4 e DeepSeek V4.1 Flash su un solo endpoint OpenRouter, uguale per ogni esecuzione. Costo calcolato a 0,15 $ in input, 0,60 $ in output e 0,003 $ di cache per milione di token. Un solo modello su tre piccole attività: altre attività daranno altri numeri. [Prompt, metodo, limiti e dati per sessione](../benchmarks/2026-10-31-map-codegen.md).

---

## 🎯 Cosa Fa

| Comando | Descrizione |
|---|---|
| `simplicio map --repo .` | Mappa il repository per gli LLM |
| `simplicio memory "query"` | Recupero neurale (FTS + vettori) |
| `simplicio edit '{...}'` | Modifica file deterministica |
| `simplicio coding-loop "task"` | Itera finché i test non passano |
| `simplicio deliver certify` | 5 gate di qualità prima del rilascio |
| `simplicio run "task" --agents N` | Orchestrazione multi-agente |
---

## 🏗️ Architettura

```
LLM (Claude/Codex/Gemini)          Simplicio Runtime (Rust)
  |                                   |
  | 1. Orient                         | simplicio map
  | 2. Recall                         | simplicio memory
  | 3. Decide                         |
  | 4. Edit  ───────────────────────> | simplicio edit (0 token)
  | 5. Verify <─────────────────────  | simplicio deliver certify
  | 6. Iterate                        | simplicio coding-loop
```

**L'LLM ragiona. Simplicio esegue deterministicamente.**

---

## ✨ Funzionalità

- 🏠 **Locale prima** — llama.cpp integrato, scala su remoto solo quando necessario
- 🪜 **Agenti a livelli** — 64 → 100 → 200 → 600 agenti locali prima del cloud a pagamento
- 🔇 **Gate di novità Shannon** — filtra output ridondanti (zero token sul dedup)
- 🔒 **Ricevute sigillate** — sha256 per artefatto, catena di prove a prova di manomissione
- 🛡️ **5 gate di consegna** — accettazione, validazione, esecuzione-verifica, regressione, auto-revisione
- ⚡ **Gate d'azione** — classificazione del rischio + blocklist per mutazioni avviate da chat
- 🔌 **MCP/ACP** — Model Context Protocol + Agent Client Protocol
- 🌐 **Gateway** — Telegram, Discord, Slack, WhatsApp
- 🧩 **Sistema di skill** — carica e incatena capacità riutilizzabili
- 💾 **Database di memoria** — recupero FTS + vettoriale persistente tra sessioni
- 🔀 **Router LLM** — nessun LLM → LLM locale → LLM remoto automaticamente
- 🖥️ **Multi-piattaforma** — macOS, Linux, Windows, singolo binario

---

## 🎁 Beta Pubblica Gratuita

**I comandi deterministici sono GRATUITI per sempre:**
`map`, `validate`, `edit`, `deliver`, `checkpoint`

**Le funzionalità AI sono gratuite durante la beta pubblica senza data di scadenza.**
La fatturazione sarà definita in aggiornamenti futuri.

```bash
simplicio license status
```

---

## 📋 Requisiti

| Requisito | Minimo | Consigliato |
|---|---|---|
| RAM | 8 GB | 16 GB+ |
| Archiviazione | 5 MB | 1.5 GB (con LLM locale) |
| OS | macOS 13+, Linux, Windows 10+ | macOS ARM64 |
| Terminale | qualsiasi terminale moderno | WezTerm / Alacritty / Ghostty |

---

## 🌐 Ecosistema

- [Sito web](https://simpleti.com.br/simplicio/#start) — documentazione completa, benchmark, installazione
- [Discord](https://discord.gg/wM6tr7xVb) — community e supporto

---

## 📄 Licenza

Proprietaria. Binario gratuito da scaricare e utilizzare. Funzionalità AI gratuite durante la
beta pubblica. Vedi [LICENSE](../plugins/simplicio/LICENSE).

---

## ⭐ Cronologia Stelle

<a href="https://star-history.com/#simpletibr/simplicio&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" />
    <img alt="Grafico cronologia stelle" src="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" width="100%" />
  </picture>
</a>

---

## 💬 Community

- [Discord](https://discord.gg/wM6tr7xVb) — chat, supporto, accesso anticipato
- [Issue GitHub](https://github.com/simpletibr/simplicio/issues) — bug e richieste di funzionalità

---

<p align="center">
  <strong>🔥 Simplicio 🔥</strong>
</p>
