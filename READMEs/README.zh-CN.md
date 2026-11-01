# 🔥 Simplicio

<p align="center">
  <img src="../assets/simplicio-hero.png" alt="Simplicio — AI 编程助手" width="920" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=blue&label=latest" alt="最新版本"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="星标"></a>
  <a href="https://github.com/simpletibr/simplicio/releases"><img src="https://img.shields.io/github/downloads/simpletibr/simplicio/total?color=green" alt="下载量"></a>
  <a href="../plugins/simplicio/LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="许可证"></a>
</p>

<p align="center">
  <a href="#-安装">安装</a> ·
  <a href="#-功能简介">功能</a> ·
  <a href="#-benchmark-2026-10-31">Benchmark</a> ·
  <a href="https://simpleti.com.br/simplicio/#start">官网</a>
</p>

<p align="center">
  <strong>🌍 语言：</strong><br>
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

## ⚡ 快速概览

**Simplicio** 是一款终端 AI 编程代理——一个单一二进制文件即可替代你的
整个 AI 辅助开发工作流：聊天、代码生成、仓库上下文、
规划、本地多智能体编排（64 → 600 个代理）以及
基于证据的 PR 交付。

**运行在你的机器上。你的代码始终在你的掌控之中。远程模型是
可选项，而非必需项。**

> 每次交互都会精确显示你节省了多少 Token。单一 Rust 二进制文件，零依赖。

## 🚀 安装

### 通过 Codex 插件安装

如果你使用 Codex，可以将 Simplicio 作为插件安装。添加公共 Marketplace、安装插件，然后启动新的 Codex 会话；插件会安装并引导启动 Simplicio Runtime，并提供其 skills 和 MCP 工具。

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

### npm / npx（支持所有操作系统）

```bash
npx simplicio install
```

### pip / PyPI（支持所有操作系统）

```bash
pip install simplicio-installer
simplicio install
```

### Homebrew（macOS）

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

### 直接安装（不使用 PyPI）

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

完成。一条命令。无需包管理器，无需模型配置。

---

## 📊 Benchmark (2026-10-31)

真实模型在同一会话中创建并编辑一个文件。结果在会话之外检查:页面用无头 Chrome 测试,脚本直接运行。共 60 个会话,取中位数。

| 任务 | 配置 | n | 耗时 | 模型请求数 | 输出 Token | 成本 | 交付 |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **基于 JSON 文件的页面,生成器已覆盖** | **Simplicio 3.10.8** | 10 | **14.1 s** | **6** | **602** | **$0.0021** | **10/10** |
|  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | $0.0215 | 10/10 |
|  | 不用 MCP | 10 | 176.3 s | 32.5 | 17,929 | $0.0203 | 10/10 |
| **新页面,使用其他数据和语言,未用于构建生成器** | **Simplicio 3.10.8** | 6 | **14.1 s** | **6** | **524** | **$0.0010** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | $0.0153 | 6/6 |
| **Python 脚本,没有生成器覆盖** | **Simplicio 3.10.8** | 6 | **30.7 s** | **10.5** | **1,796** | **$0.0031** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | $0.0051 | 6/6 |
|  | 不用 MCP | 6 | 22.7 s | 8 | 1,268 | $0.0024 | 6/6 |

收益来自生成器:在页面任务中,`simplicio_map` 负责路由请求,`simplicio_codegen` 以 0 个 LLM Token 写入文件。没有生成器覆盖任务时,3.10.8 仍优于 3.9.2,但与不用 MCP 相比,每个会话多花约 8 秒和 0.0007 美元。

> 所有运行都使用 OpenCode 2.1.4 和 DeepSeek V4.1 Flash,并固定同一个 OpenRouter 端点。成本按每百万 Token 输入 0.15 美元、输出 0.60 美元、缓存读取 0.003 美元计算。这是一个模型在三个小任务上的结果,其他任务的数字会不同。 [提示词、方法、局限和逐会话数据](../benchmarks/2026-10-31-map-codegen.md).

在其他模型上运行相同的任务，分别使用和不使用 Simplicio。每个模型只在一个客户端中运行，因此请只比较同一模型的结果。

| 模型 | 任务 | Simplicio 3.10.8 | 不用 MCP | 交付 |
|:---|:---|---:|---:|---:|
| **Claude Sonnet 5.5** (Claude Code) | 基于 JSON 文件的页面,生成器已覆盖 | **17.5 s · $0.0672** | 33.4 s · $0.0927 | 10/10 |
|  | 新页面,使用其他数据和语言,未用于构建生成器 | **16.3 s · $0.0514** | 22.5 s · $0.0610 | 10/10 |
|  | Python 脚本,没有生成器覆盖 | **19.6 s · $0.0548** | 11.4 s · $0.0283 | 10/10 |
| **Grok 4.7** (Grok Build) | 基于 JSON 文件的页面,生成器已覆盖 | **31.0 s · $0.1690** | 359.7 s · $0.8590 | 6/6 |
|  | 新页面,使用其他数据和语言,未用于构建生成器 | **36.0 s · $0.2059** | 387.5 s · $0.8518 | 6/6 |
|  | Python 脚本,没有生成器覆盖 | **82.0 s · $0.3315** | 63.1 s · $0.2452 | 6/6 |
| **Claude Haiku 5.5** (OpenCode) | 基于 JSON 文件的页面,生成器已覆盖 | **13.7 s · $0.0046** | 29.3 s · $0.0083 | 10/10 |
|  | 新页面,使用其他数据和语言,未用于构建生成器 | **13.8 s · $0.0023** | 28.7 s · $0.0057 | 10/10 |
|  | Python 脚本,没有生成器覆盖 | **19.2 s · $0.0033** | 16.6 s · $0.0030 | 10/10 |

[提示词、方法、局限和逐会话数据](../benchmarks/2026-11-01-multi-model.md).

---

## 🎯 功能简介

| 命令 | 描述 |
|---|---|
| `simplicio map --repo .` | 为 LLM 映射仓库结构 |
| `simplicio memory "query"` | 神经记忆召回（全文搜索 + 向量） |
| `simplicio edit '{...}'` | 确定性文件编辑 |
| `simplicio coding-loop "task"` | 迭代直到测试通过 |
| `simplicio deliver certify` | 交付前通过 5 道质量关卡 |
| `simplicio run "task" --agents N` | 多智能体编排 |
---

## 🏗️ 架构

```
LLM (Claude/Codex/Gemini)          Simplicio 运行时 (Rust)
  |                                   |
  | 1. 定位                           | simplicio map
  | 2. 回忆                           | simplicio memory
  | 3. 决策                           |
  | 4. 编辑  ───────────────────────> | simplicio edit (0 Token)
  | 5. 验证 <─────────────────────  | simplicio deliver certify
  | 6. 迭代                           | simplicio coding-loop
```

**LLM 负责推理。Simplicio 负责确定性执行。**

---

## ✨ 特性

- 🏠 **本地优先** — 内置 llama.cpp，仅在需要时扩展至远程
- 🪜 **分层代理** — 64 → 100 → 200 → 600 个本地代理，之后才使用付费云端
- 🔇 **Shannon 新颖性门控** — 过滤冗余输出（去重零 Token）
- 🔒 **密封收据** — 每个工件 sha256，防篡改证据链
- 🛡️ **5 道交付关卡** — 验收、验证、运行验证、回归、自审
- ⚡ **操作门控** — 针对聊天发起的变更的风险分类 + 黑名单
- 🔌 **MCP/ACP** — 模型上下文协议 + 智能体客户端协议
- 🌐 **网关** — Telegram、Discord、Slack、WhatsApp
- 🧩 **技能系统** — 加载并链式组合可复用的能力
- 💾 **记忆数据库** — 跨会话持久化的全文搜索 + 向量召回
- 🔀 **LLM 路由器** — 无 LLM → 本地 LLM → 远程 LLM 自动切换
- 🖥️ **跨平台** — macOS、Linux、Windows，单一二进制文件

---

## 🎁 免费公测

**确定性命令永久免费：**
`map`、`validate`、`edit`、`deliver`、`checkpoint`

**AI 功能在公测期间免费，无截止日期。**
计费方案将在未来更新中确定。

```bash
simplicio license status
```

---

## 📋 系统要求

| 要求 | 最低配置 | 推荐配置 |
|---|---|---|
| 内存 | 8 GB | 16 GB+ |
| 存储 | 5 MB | 1.5 GB（含本地 LLM） |
| 操作系统 | macOS 13+、Linux、Windows 10+ | macOS ARM64 |
| 终端 | 任意现代终端 | WezTerm / Alacritty / Ghostty |

---

## 🌐 生态系统

- [官网](https://simpleti.com.br/simplicio/#start) — 完整文档、基准测试、安装指南
- [Discord](https://discord.gg/wM6tr7xVb) — 社区与支持

---

## 📄 许可证

专有许可。二进制文件可免费下载和使用。AI 功能在公开
公测期间免费。详见 [LICENSE](../plugins/simplicio/LICENSE)。

---

## ⭐ 星标历史

<a href="https://star-history.com/#simpletibr/simplicio&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" />
    <img alt="星标历史图表" src="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" width="100%" />
  </picture>
</a>

---

## 💬 社区

- [Discord](https://discord.gg/wM6tr7xVb) — 聊天、支持、抢先体验
- [GitHub Issues](https://github.com/simpletibr/simplicio/issues) — 报告问题和功能请求

---

<p align="center">
  <strong>🔥 Simplicio 🔥</strong>
</p>
