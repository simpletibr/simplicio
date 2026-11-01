# 🔥 Simplicio

<p align="center">
  <img src="../assets/simplicio-hero.png" alt="Simplicio — AI coding agent" width="920" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=blue&label=latest" alt="Latest Release"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Stars"></a>
  <a href="https://github.com/simpletibr/simplicio/releases"><img src="https://img.shields.io/github/downloads/simpletibr/simplicio/total?color=green" alt="Downloads"></a>
  <a href="../plugins/simplicio/LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="License"></a>
</p>

<p align="center">
  <a href="#installation">Installation</a> ·
  <a href="#ce-quil-fait">Ce Qu'il Fait</a> ·
  <a href="#-benchmark-2026-10-31">Benchmark</a> ·
  <a href="https://simpleti.com.br/simplicio/#start">Site Web</a>
</p>

<p align="center">
  <strong>🌍 Langues :</strong><br>
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

**Simplicio** est un agent de codage IA en terminal — un binaire unique qui remplace
l'intégralité de votre workflow de développement assisté par IA : chat, génération de code,
contexte de dépôt, planification, orchestration multi-agent locale (64 → 600 agents),
et livraison de PR avec preuves à l'appui.

**Tourne sur votre machine. Votre code ne quitte jamais votre contrôle. Les modèles distants
sont facultatifs, pas obligatoires.**

> Chaque interaction montre exactement combien de tokens vous avez économisés. Binaire Rust unique, zéro dépendance.

## 🚀 Installation

### Installer via le plugin Codex

Si vous utilisez Codex, vous pouvez installer Simplicio comme un plugin. Ajoutez le Marketplace public, installez le plugin et démarrez une nouvelle session Codex ; le plugin installe et démarre le Runtime Simplicio et expose ses skills et outils MCP.

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

### npm / npx (tout OS)

```bash
npx simplicio install
```

### pip / PyPI (tout OS)

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

### Installation directe (sans PyPI)

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

Terminé. Une seule commande. Pas de gestionnaire de paquets, pas de configuration de modèle.

---

## 📊 Benchmark (2026-10-31)

Un vrai modèle crée un fichier puis le modifie dans la même session. Le résultat est vérifié hors de la session : les pages dans Chrome headless, les scripts en les exécutant. 60 sessions, médianes.

| Tâche | Configuration | n | Temps | Requêtes au modèle | Tokens de sortie | Coût | Livraisons |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **Page à partir d'un JSON, couverte par un générateur** | **Simplicio 3.10.8** | 10 | **14.1 s** | **6** | **602** | **$0.0021** | **10/10** |
|  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | $0.0215 | 10/10 |
|  | Sans MCP | 10 | 176.3 s | 32.5 | 17,929 | $0.0203 | 10/10 |
| **Nouvelle page, autres données et autre langue, non utilisée pour construire le générateur** | **Simplicio 3.10.8** | 6 | **14.1 s** | **6** | **524** | **$0.0010** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | $0.0153 | 6/6 |
| **Script Python, aucun générateur ne le couvre** | **Simplicio 3.10.8** | 6 | **30.7 s** | **10.5** | **1,796** | **$0.0031** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | $0.0051 | 6/6 |
|  | Sans MCP | 6 | 22.7 s | 8 | 1,268 | $0.0024 | 6/6 |

Le gain vient du générateur : sur les tâches de page, `simplicio_map` route la demande et `simplicio_codegen` écrit le fichier avec 0 token LLM. Quand aucun générateur ne couvre la tâche, la 3.10.8 bat la 3.9.2 et coûte environ 8 s et 0,0007 $ de plus par session que sans MCP.

> OpenCode 2.1.4 et DeepSeek V4.1 Flash sur un seul endpoint OpenRouter, identique pour chaque exécution. Coût calculé à 0,15 $ en entrée, 0,60 $ en sortie et 0,003 $ en cache par million de tokens. Un seul modèle sur trois petites tâches : d'autres tâches donneront d'autres chiffres. [Prompts, méthode, limites et données par session](../benchmarks/2026-10-31-map-codegen.md).

Les mêmes tâches sur d'autres modèles, avec et sans Simplicio. Chaque modèle a tourné dans un seul client : comparez un modèle avec lui-même.

| Modèle | Tâche | Simplicio 3.10.8 | Sans MCP | Livraisons |
|:---|:---|---:|---:|---:|
| **Claude Sonnet 5.5** (Claude Code) | Page à partir d'un JSON, couverte par un générateur | **17.5 s · $0.0672** | 33.4 s · $0.0927 | 10/10 |
|  | Nouvelle page, autres données et autre langue, non utilisée pour construire le générateur | **16.3 s · $0.0514** | 22.5 s · $0.0610 | 10/10 |
|  | Script Python, aucun générateur ne le couvre | **19.6 s · $0.0548** | 11.4 s · $0.0283 | 10/10 |
| **Grok 4.7** (Grok Build) | Page à partir d'un JSON, couverte par un générateur | **31.0 s · $0.1690** | 359.7 s · $0.8590 | 6/6 |
|  | Nouvelle page, autres données et autre langue, non utilisée pour construire le générateur | **36.0 s · $0.2059** | 387.5 s · $0.8518 | 6/6 |
|  | Script Python, aucun générateur ne le couvre | **82.0 s · $0.3315** | 63.1 s · $0.2452 | 6/6 |
| **Claude Haiku 5.5** (OpenCode) | Page à partir d'un JSON, couverte par un générateur | **13.7 s · $0.0046** | 29.3 s · $0.0083 | 10/10 |
|  | Nouvelle page, autres données et autre langue, non utilisée pour construire le générateur | **13.8 s · $0.0023** | 28.7 s · $0.0057 | 10/10 |
|  | Script Python, aucun générateur ne le couvre | **19.2 s · $0.0033** | 16.6 s · $0.0030 | 10/10 |

[Prompts, méthode, limites et données par session](../benchmarks/2026-11-01-multi-model.md).

---

## 🎯 Ce Qu'il Fait

| Commande | Description |
|---|---|
| `simplicio map --repo .` | Cartographie le dépôt pour les LLMs |
| `simplicio memory "query"` | Rappel neuronal (FTS + vecteurs) |
| `simplicio edit '{...}'` | Édition déterministe de fichiers |
| `simplicio coding-loop "task"` | Itère jusqu'à ce que les tests passent |
| `simplicio deliver certify` | 5 portes qualité avant livraison |
| `simplicio run "task" --agents N` | Orchestration multi-agent |
---

## 🏗️ Architecture

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

**Le LLM raisonne. Simplicio exécute de manière déterministe.**

---

## ✨ Fonctionnalités

- 🏠 **Local d'abord** — llama.cpp intégré, passage au distant uniquement si nécessaire
- 🪜 **Agents hiérarchisés** — 64 → 100 → 200 → 600 agents locaux avant le cloud payant
- 🔇 **Porte de nouveauté Shannon** — filtre les sorties redondantes (zéro token sur déduplication)
- 🔒 **Reçus scellés** — sha256 par artefact, chaîne de preuves inviolable
- 🛡️ **5 portes de livraison** — acceptation, validation, exécution-vérification, régression, auto-examen
- ⚡ **Porte d'action** — classification des risques + liste de blocage pour les mutations initiées par chat
- 🔌 **MCP/ACP** — Model Context Protocol + Agent Client Protocol
- 🌐 **Passerelles** — Telegram, Discord, Slack, WhatsApp
- 🧩 **Système de compétences** — charge et enchaîne des capacités réutilisables
- 💾 **Base de données mémoire** — FTS persistant + rappel vectoriel entre sessions
- 🔀 **Routeur LLM** — aucun LLM → LLM local → LLM distant automatiquement
- 🖥️ **Multi-plateforme** — macOS, Linux, Windows, binaire unique

---

## 🎁 Bêta Publique Gratuite

**Les commandes déterministes sont GRATUITES pour toujours :**
`map`, `validate`, `edit`, `deliver`, `checkpoint`

**Les fonctionnalités IA sont gratuites pendant la bêta publique sans date de fin.**
La facturation sera définie dans les futures mises à jour.

```bash
simplicio license status
```

---

## 📋 Prérequis

| Prérequis | Minimum | Recommandé |
|---|---|---|
| RAM | 8 Go | 16 Go+ |
| Stockage | 5 Mo | 1,5 Go (avec LLM local) |
| OS | macOS 13+, Linux, Windows 10+ | macOS ARM64 |
| Terminal | tout terminal moderne | WezTerm / Alacritty / Ghostty |

---

## 🌐 Écosystème

- [Site Web](https://simpleti.com.br/simplicio/#start) — docs complètes, benchmarks, installation
- [Discord](https://discord.gg/wM6tr7xVb) — communauté et support

---

## 📄 Licence

Propriétaire. Binaire gratuit à télécharger et à utiliser. Fonctionnalités IA gratuites pendant la
bêta publique. Voir [LICENSE](../plugins/simplicio/LICENSE).

---

## ⭐ Star History

<a href="https://star-history.com/#simpletibr/simplicio&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" />
    <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" width="100%" />
  </picture>
</a>

---

## 💬 Communauté

- [Discord](https://discord.gg/wM6tr7xVb) — chat, support, accès anticipé
- [GitHub Issues](https://github.com/simpletibr/simplicio/issues) — bugs et demandes de fonctionnalités

---

<p align="center">
  <strong>🔥 Simplicio 🔥</strong>
</p>
