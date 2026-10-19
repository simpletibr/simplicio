# ⚡ Simplicio

> **The High-Performance Native AI Coding Runtime & Agent (100% Rust)**  
> Sub-millisecond local orientation, atomic edits, and governed concurrency. In one measured 2-step CRUD flow, the edit stage used 95.53% fewer tokens ([evidence](docs/evidence/openrouter-deepseek-v4-crud-2026-09-01.json)).

<p align="center">
  <img src="assets/simplicio-hero.png" alt="Simplicio — AI coding agent" width="840" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=2fe6a0&label=release" alt="Latest Release"></a>
  <a href="https://simpleti.com.br/simplicio/docs"><img src="https://img.shields.io/badge/docs-simpleti.com.br-ffd23f" alt="Documentation"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Stars"></a>
  <img src="https://img.shields.io/badge/runtime-100%25%20Rust-orange" alt="Runtime">
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="License">
</p>

<p align="center">
  <a href="#-quick-install">Quick Install</a> •
  <a href="#-real-world-measured-benchmark-simplicio-suite-vs-standard-agent">Benchmarks</a> •
  <a href="#-first-60-seconds">First 60 Seconds</a> •
  <a href="#-mcp--ide-integration">MCP & IDEs</a> •
  <a href="#-core-architecture">Architecture</a> •
  <a href="https://simpleti.com.br/simplicio/docs">Full Documentation</a>
</p>

---

## ⚡ What is Simplicio?

**Simplicio** is a single-binary, local-first runtime and AI coding agent built in 100% Rust. It replaces heavy context dumps and fragmented Python tools with mathematical token bounding, cryptographic atomic edits, and hardware-governed multi-agent orchestration.

- **100% Native Rust**: Single ~46MB standalone binary. No Python, virtualenvs, or heavy background processes.
- **Ultra-Low Latency**: ~4ms cold start vs. seconds in interpreted runtimes.
- **Token Economy**: Sends bounded AST graphs instead of raw file trees. Measured once on a 2-step CRUD flow: 95.53% fewer tokens in the edit stage; results vary by task and model.
- **Fail-Closed Safety**: Every code modification uses SHA-256 pre-image checks, atomic replacements, and immutable audit receipts.

---
## 📊 Real-World Measured Benchmark: Simplicio Suite vs Standard Agent

In an audited head-to-head A/B benchmark on a real codebase task (AST-safe bug fix and regression test verification using `deepseek/deepseek-v4.1-flash` via OpenRouter):

| Metric | Standard Agent (No Simplicio) | Simplicio Suite (With Loop) | Advantage |
|:---|:---|:---|:---|
| **Wall-Clock Duration** | `55.19 s` | **`13.60 s`** | 🚀 **4.05x faster (-75.4%)** |
| **Prompt Tokens** | `7,747 tokens` | **`550 tokens`** | 📉 **-92.9% prompt tokens** |
| **Completion Tokens** | `661 tokens` | **`294 tokens`** | 📉 **-55.5% output tokens** |
| **Total Tokens Consumed** | `8,408 tokens` | **`844 tokens`** | 💎 **-90.0% total tokens** |
| **Billed API Cost (USD)** | `$0.001786` | **`$0.000259`** | 💰 **6.9x cheaper (-85.5%)** |
| **Agent Turns** | 2 turns (retry needed) | **1 turn** | 🎯 **1st-turn deterministic resolution** |
| **Code Modification Safety** | Unchecked raw edits | **AST-safe plan + SHA256 receipt** | 🔒 **Deterministic fail-closed** |

> **Audit Artifact:** `bench/llm_ab/results/2026-10-12-6dac8429-t1.json` · Model: `deepseek/deepseek-v4.1-flash` via OpenRouter.

---

## 📦 Quick Install

Install the signed native binary in seconds:

### macOS / Linux
```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

### Windows (PowerShell as Administrator)
```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

### Alternative (PyPI Bootstrapper)

On Windows, use `py -m pip install --upgrade simplicio-installer` followed by `simplicio install`.

```bash
python3 -m pip install --upgrade simplicio-installer
simplicio install
```

### Simplicio Video (hypit)
To clone the Simplicio Video runtime repository:
```bash
git clone https://github.com/hypit-ai/hypit.git simplicio-video
```

---

## 🚀 First 60 Seconds

Once installed, test the CLI and orient your project:

```bash
# 1. Verify your installation
simplicio version

# 2. Orient and index your current repository
cd my-project
simplicio onboard

# 3. Launch the interactive coding assistant
simplicio
```

---

## 🔌 MCP & IDE Integration

Simplicio runs as an official Model Context Protocol (MCP) server for your favorite editors:

```bash
# Automatically configure Claude Code, Cursor, VS Code, Zed, and JetBrains:
simplicio mcp register
```

### Manual MCP Server Configuration (`stdio`)
```json
{
  "mcpServers": {
    "simplicio": {
      "command": "/absolute/path/to/.simplicio/bin/simplicio",
      "args": ["serve", "--mcp", "--stdio"]
    }
  }
}
```

For Codex, use an absolute executable path in your TOML configuration and replace the example username:

```toml
[mcp_servers.simplicio]
# Windows:
command = "C:/Users/YourName/.simplicio/bin/simplicio.exe"
args = ["serve", "--mcp", "--stdio"]
```

On macOS, replace the command line with:

```toml
command = "/Users/your-name/.simplicio/bin/simplicio"
```

On Linux, replace it with:

```toml
command = "/home/your-name/.simplicio/bin/simplicio"
```

See [MCP-CONNECT.md](MCP-CONNECT.md) for complete platform examples.

Exposed MCP Tools:
- `simplicio_map`: Structural repository orientation without prompt bloating.
- `simplicio_context`: Bounded token retrieval for exact code snippets.
- `simplicio_edit`: Atomic mechanical modifications with SHA-256 receipts.
- `simplicio_loop`: Concurrently orchestrated multi-stage waves.
- `simplicio_parallel`: Real-time inspection of CPUExecutor and hardware headroom.

---

## ⚙️ Core Architecture Highlights

```
User Prompt ──► simplicio map ──► simplicio context ──► Wave Loop ──► simplicio edit ──► Validate & Deliver
                 (Graph & AST)     (Token Bounding)     (Tokio DAG)   (Atomic SHA-256)   (Audit Receipts)
```

1. **Orientation (`simplicio map`)**: High-speed discovery of import topologies and public interfaces without reading thousands of redundant files into LLM context.
2. **Context Bounding (`simplicio context`)**: Mathematical budget packing (`st_prompt_budget`) ensuring the model only receives the exact AST fragments it needs.
3. **Mechanical Edits (`simplicio edit`)**: Deterministic exact search/replace, insertions, and deletions with pre-image hashing. If the file changed underneath, the patch safely aborts (*fail-closed*).
4. **Wave Orchestrator (`simplicio loop`)**: Multi-stage DAG partitioner executing parallel reads and commands through Tokio semaphores with deterministic state reduction.
5. **Hardware Governor (`CPUExecutor`)**: Dynamically samples CPU and memory pressure to prevent machine lockups. Automatically throttles subagents while keeping writes strictly serialized (`write_workers: 1`).

---

## 📖 Complete Documentation & Guides

For deep technical dives, CLI references, benchmark proofs, and multi-agent workflows, visit our official documentation hub:

👉 **[https://simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)**

---

## 🔒 Security & Privacy

- **Your Code Never Leaves Your Machine**: All repository mapping, context packaging, editing, and test gates execute locally.
- **Auditable Provenance**: Every modification generates an immutable cryptographic receipt (`receipt.json`).
- **No Mystery Telemetry**: Zero silent telemetry or code exfiltration.

---

## 💬 Community & Support

- **Official Website**: [simpleti.com.br/simplicio](https://simpleti.com.br/simplicio/)
- **Documentation**: [simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)
- **Discord**: [Join the Community](https://discord.gg/wM6tr7xVb)
- **Issues**: [GitHub Issue Tracker](https://github.com/simpletibr/simplicio/issues)

---

<p align="center">
  <sub>© 2026 SimpleTI. Simplicio is a registered proprietary software. All rights reserved.</sub>
</p>
