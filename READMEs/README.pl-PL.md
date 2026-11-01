# 🔥 Simplicio

<p align="center">
  <img src="../assets/simplicio-hero.png" alt="Simplicio — agent AI do kodowania" width="920" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=blue&label=latest" alt="Latest Release"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Stars"></a>
  <a href="https://github.com/simpletibr/simplicio/releases"><img src="https://img.shields.io/github/downloads/simpletibr/simplicio/total?color=green" alt="Downloads"></a>
  <a href="../plugins/simplicio/LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="License"></a>
</p>

<p align="center">
  <a href="#instalacja">Instalacja</a> ·
  <a href="#co-robi">Co robi</a> ·
  <a href="#-benchmark-2026-10-31">Benchmark</a> ·
  <a href="https://simpleti.com.br/simplicio/#start">Strona WWW</a>
</p>

<p align="center">
  <strong>🌍 Języki:</strong><br>
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

**Simplicio** to terminalowy agent AI do kodowania — pojedynczy plik binarny, który zastępuje
cały twój workflow wspomagany AI: czat, generowanie kodu, kontekst repozytorium,
planowanie, lokalną orkiestrację wieloagentową (64 → 600 agentów) i
dostarczanie PR z potwierdzeniem dowodów.

**Działa na twojej maszynie. Twój kod nigdy nie opuszcza twojej kontroli. Modele zdalne są
opcjonalne, nie wymagane.**

> Każda interakcja pokazuje dokładnie, ile tokenów zaoszczędziłeś. Pojedynczy plik binarny w Ruście, zero zależności.

## 🚀 Instalacja

### Instalacja przez wtyczkę Codex

Jeśli używasz Codex, możesz zainstalować Simplicio jako wtyczkę. Dodaj publiczny Marketplace, zainstaluj wtyczkę i uruchom nową sesję Codex; wtyczka zainstaluje i uruchomi Simplicio Runtime oraz udostępni jego skills i narzędzia MCP.

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

### npm / npx (dowolny system)

```bash
npx simplicio install
```

### pip / PyPI (dowolny system)

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

### Instalacja bezpośrednia (bez PyPI)

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

Gotowe. Jedno polecenie. Żaden menedżer pakietów, żadna konfiguracja modelu.

---

## 📊 Benchmark (2026-10-31)

Prawdziwy model tworzy plik i edytuje go w tej samej sesji. Wynik jest sprawdzany poza sesją: strony w headless Chrome, skrypty przez uruchomienie. 60 sesji, mediany.

| Zadanie | Konfiguracja | n | Czas | Żądania do modelu | Tokeny wyjściowe | Koszt | Dostarczono |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **Strona z pliku JSON, obsługiwana przez generator** | **Simplicio 3.10.8** | 10 | **14.1 s** | **6** | **602** | **$0.0021** | **10/10** |
|  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | $0.0215 | 10/10 |
|  | Bez MCP | 10 | 176.3 s | 32.5 | 17,929 | $0.0203 | 10/10 |
| **Nowa strona, inne dane i inny język, nieużyta przy budowie generatora** | **Simplicio 3.10.8** | 6 | **14.1 s** | **6** | **524** | **$0.0010** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | $0.0153 | 6/6 |
| **Skrypt Python, żaden generator go nie obsługuje** | **Simplicio 3.10.8** | 6 | **30.7 s** | **10.5** | **1,796** | **$0.0031** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | $0.0051 | 6/6 |
|  | Bez MCP | 6 | 22.7 s | 8 | 1,268 | $0.0024 | 6/6 |

Zysk pochodzi z generatora: w zadaniach ze stronami `simplicio_map` kieruje żądanie, a `simplicio_codegen` zapisuje plik przy 0 tokenów LLM. Gdy żaden generator nie obsługuje zadania, 3.10.8 wygrywa z 3.9.2, ale kosztuje około 8 s i 0,0007 $ więcej na sesję niż praca bez MCP.

> OpenCode 2.1.4 i DeepSeek V4.1 Flash na jednym stałym endpoincie OpenRouter, tak samo dla każdego uruchomienia. Koszt liczony po 0,15 $ za wejście, 0,60 $ za wyjście i 0,003 $ za pamięć podręczną na milion tokenów. To jeden model i trzy małe zadania: inne zadania dadzą inne liczby. [Prompty, metoda, ograniczenia i dane dla każdej sesji](../benchmarks/2026-10-31-map-codegen.md).

---

## 🎯 Co robi

| Polecenie | Opis |
|---|---|
| `simplicio map --repo .` | Mapuje repozytorium dla LLM-ów |
| `simplicio memory "query"` | Neuronowe przywoływanie (FTS + wektory) |
| `simplicio edit '{...}'` | Deterministyczna edycja plików |
| `simplicio coding-loop "task"` | Iteruje, aż testy przejdą |
| `simplicio deliver certify` | 5 bram jakości przed wydaniem |
| `simplicio run "task" --agents N` | Orkiestracja wieloagentowa |
---

## 🏗️ Architektura

```
LLM (Claude/Codex/Gemini)          Simplicio Runtime (Rust)
  |                                   |
  | 1. Orient                         | simplicio map
  | 2. Recall                         | simplicio memory
  | 3. Decide                         |
  | 4. Edit  ───────────────────────> | simplicio edit (0 tokens)
  | 5. Verify <─────────────────────  | simplicio deliver certify
  | 6. Iterate                        | simplicio coding-loop
```

**LLM rozumuje. Simplicio wykonuje deterministycznie.**

---

## ✨ Funkcje

- 🏠 **Lokalnie najpierw** — wbudowany llama.cpp, skaluje do zdalnych tylko gdy potrzebne
- 🪜 **Warstwowi agenci** — 64 → 100 → 200 → 600 lokalnych agentów przed płatną chmurą
- 🔇 **Bramka nowości Shannona** — filtruje zbędne wyjścia (zero tokenów na deduplikacji)
- 🔒 **Zapieczętowane paragony** — sha256 na artefakt, odporny na manipulacje łańcuch dowodów
- 🛡️ **5 bram dostarczania** — akceptacja, walidacja, uruchom-weryfikuj, regresja, samoocena
- ⚡ **Bramka akcji** — klasyfikacja ryzyka + lista blokowana dla mutacji inicjowanych z czatu
- 🔌 **MCP/ACP** — Model Context Protocol + Agent Client Protocol
- 🌐 **Bramy** — Telegram, Discord, Slack, WhatsApp
- 🧩 **System umiejętności** — ładuje i łańcuchuje wielokrotnego użytku możliwości
- 💾 **Baza pamięci** — trwałe FTS + przywoływanie wektorowe między sesjami
- 🔀 **Router LLM** — brak LLM → lokalny LLM → zdalny LLM automatycznie
- 🖥️ **Wieloplatformowość** — macOS, Linux, Windows, pojedynczy plik binarny

---

## 🎁 Darmowa Beta Publiczna

**Deterministyczne polecenia są DARMOWE na zawsze:**
`map`, `validate`, `edit`, `deliver`, `checkpoint`

**Funkcje AI są darmowe podczas publicznej bety bez daty zakończenia.**
Rozliczenia zostaną zdefiniowane w przyszłych aktualizacjach.

```bash
simplicio license status
```

---

## 📋 Wymagania

| Wymaganie | Minimalne | Zalecane |
|---|---|---|
| RAM | 8 GB | 16 GB+ |
| Miejsce na dysku | 5 MB | 1,5 GB (z lokalnym LLM) |
| System | macOS 13+, Linux, Windows 10+ | macOS ARM64 |
| Terminal | dowolny nowoczesny terminal | WezTerm / Alacritty / Ghostty |

---

## 🌐 Ekosystem

- [Strona WWW](https://simpleti.com.br/simplicio/#start) — pełna dokumentacja, benchmarki, instalacja
- [Discord](https://discord.gg/wM6tr7xVb) — społeczność i wsparcie

---

## 📄 Licencja

Proprietary. Plik binarny darmowy do pobrania i użytku. Funkcje AI darmowe podczas
publicznej bety. Zobacz [LICENSE](../plugins/simplicio/LICENSE).

---

## ⭐ Historia gwiazdek

<a href="https://star-history.com/#simpletibr/simplicio&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" />
    <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" width="100%" />
  </picture>
</a>

---

## 💬 Społeczność

- [Discord](https://discord.gg/wM6tr7xVb) — czat, wsparcie, wczesny dostęp
- [GitHub Issues](https://github.com/simpletibr/simplicio/issues) — błędy i prośby o funkcje

---

<p align="center">
  <strong>🔥 Simplicio 🔥</strong>
</p>
