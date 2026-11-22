<div align="center">

<img src="../assets/simplicio-icon-192.png" alt="Simplicio 标志" width="96" height="96">

<h1>Simplicio</h1>

<p><b>UltraFast Mode for all.</b></p>

<p><b>同一智能体、同一模型、同一任务：耗时 121&nbsp;s&nbsp;→&nbsp;25&nbsp;s，成本 $0.0226&nbsp;→&nbsp;$0.0076。</b></p>

<p>未使用 Simplicio → 使用 Simplicio 3.15.0。在 Claude Code 中以 Claude Haiku 5.5 运行一个小型编码任务，取 3 次运行的中位数。</p>

<p>Simplicio 在你的机器上运行，为你已在使用的编码智能体添加工具。</p>

<p>
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=2fe6a0&label=release" alt="最新版本"></a>
  <a href="https://simpleti.com.br/simplicio/docs"><img src="https://img.shields.io/badge/docs-simpleti.com.br-ffd23f" alt="文档"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="星标数"></a>
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="许可证：专有">
</p>

<p>
  <a href="../README.md">English</a> ·
  <a href="README.pt-BR.md">Português (Brasil)</a> ·
  <a href="README.es-ES.md">Español</a> ·
  <a href="README.fr-FR.md">Français</a> ·
  <a href="README.it-IT.md">Italiano</a> ·
  <a href="README.pl-PL.md">Polski</a> ·
  <a href="README.ru-RU.md">Русский</a> ·
  简体中文 ·
  <a href="README.ja-JP.md">日本語</a> ·
  <a href="README.ko-KR.md">한국어</a> ·
  <a href="README.hi-IN.md">हिन्दी</a> ·
  <a href="README.ar-SA.md">العربية</a>&lrm; ·
  <a href="README.he-IL.md">עברית</a>&lrm; ·
  <a href="README.id-ID.md">Bahasa Indonesia</a> ·
  <a href="README.ms-MY.md">Bahasa Melayu</a>
</p>

<p align="center"><sub>本文件是 <a href="../README.md">英文版 README</a> 的译文。如两者有出入，以英文版页面为准。图表中的文字保留英文。</sub></p>

</div>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-dark.svg">
    <img src="../assets/benchmark-2026-11-22-light.svg" width="840" alt="柱状图，比较未使用 Simplicio、Simplicio 3.14.0 和 Simplicio 3.15.0 在三项指标上的表现，每组为三次会话的中位数。整项任务耗时：121 s（未使用 Simplicio）、104 s（Simplicio 3.14.0）和 25 s（Simplicio 3.15.0）。成本：$0.0226、$0.0220 和 $0.0076。输出 token：18,162、19,722 和 3,211。">
  </picture>
</p>

<p align="center">
  <sub>每个方案（未使用 Simplicio、Simplicio 3.14.0 和 Simplicio 3.15.0）取 3 次会话的中位数。Claude Haiku 5.5 在 Claude Code 2.1.330 中运行，2026-11-22。每个方案的已交付步骤均为 9/9。每根柱子上的细线从最低的会话延伸到最高的会话。<br>
  <a href="../benchmarks/2026-11-22-standard-benchmark.md">方法、数据和限制</a></sub>
</p>

<p align="center">
  <sub>阅读时请一并参考：一个小型任务，每个方案 3 次会话，一个模型。外部检查覆盖的内容比提示词要求的少。峰值内存更高：375 MB 对比 270 MB。Simplicio 构建版本是从发布提交编译的，编译时关闭了登录功能。</sub>
</p>

<p align="center">Simplicio 如何得到这一结果并未公开。测量结果都已公开，包括 Simplicio 落后的那些。</p>

<p align="center">
  <b>试一试：</b> <a href="#install">安装</a> · <a href="#first-run">首次运行</a><br>
  <a href="#what-simplicio-is">简介</a> ·
  <a href="#the-measurement">测量</a> ·
  <a href="#works-with-the-agent-you-already-use">智能体</a> ·
  <a href="#command-line">命令</a> ·
  <a href="#safety-and-privacy">隐私</a> ·
  <a href="#questions-people-ask">问题</a> ·
  <a href="#documentation-and-community">文档</a>
</p>

<a id="what-simplicio-is"></a>

## 什么是 Simplicio

Simplicio 是一个本地程序，能让你已在使用的编码智能体拥有极速模式，无论是哪种智能体、哪个模型。本页的数字只来自一个智能体和一个模型；下面一节会准确说明测量了什么。

- **你的智能体和模型保持不变。** Simplicio 不会替换 Claude Code、Codex、Cursor，也不会替换它们背后的模型。
- **一个经过签名的二进制文件**会在你的智能体中注册自己，并作为本地 STDIO MCP 服务器在你的机器上运行。
- **改变的是会话本身。** 也就是它的耗时和成本。

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/diagram-where-simplicio-runs-dark.svg">
    <img src="../assets/diagram-where-simplicio-runs-light.svg" width="840" alt="示意图。在你的机器上：你、你的编码智能体、Simplicio 和你的仓库。智能体通过本地 STDIO（MCP）与 Simplicio 通信。智能体照旧与你的模型服务商通信。Simplicio 与 SimpleTI 通信以进行登录和套餐检查，与 GitHub 通信以检查发布版本，两者都不包含仓库内容。">
  </picture>
</p>

<p align="center">
  <sub>这是默认流程。<a href="#safety-and-privacy">完整列表</a>中包含其他服务。</sub>
</p>

<details>
<summary>MCP 与 STDIO</summary>

MCP 即 Model Context Protocol，是编码智能体调用外部工具的方式。STDIO 表示智能体自行启动该程序，并通过其标准输入和标准输出与之通信。

它为你的智能体提供工具：仓库地图、范围受限的上下文、结构化编辑和检查。[核心工具](#works-with-the-agent-you-already-use)见下文。

你只需安装一个经过签名的原生二进制文件。安装程序会校验签名，然后在你机器上找到的智能体中注册 Simplicio。

</details>

<a id="the-measurement"></a>

## 测量结果

同一项任务，分别在使用和不使用 Simplicio 的情况下以相同方式运行：在一次智能体会话中完成三个步骤，每个结果都从外部检查。

1. 构建用户列表：一个 API，以及一个带表格、搜索和排序功能的页面。
2. 修改：删除一列，增加按角色筛选的功能，并增加一个日期列。
3. 添加注册功能：一个会校验输入的 `POST` 接口，以及一个表单页面。

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-sessions-dark.svg">
    <img src="../assets/benchmark-2026-11-22-sessions-light.svg" width="840" alt="每次会话的散点图，横轴为整项任务耗时，纵轴为智能体报告的成本。Simplicio 3.15.0，绿色菱形：23 至 27 s，$0.0071 至 $0.0098。Simplicio 3.14.0，灰色方块：90 至 106 s，$0.0214 至 $0.0249。未使用 Simplicio，空心圆：97 至 172 s，$0.0186 至 $0.0280。">
  </picture>
</p>

| 指标 | 未使用 Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 任务耗时 | 121 s<br><sub>97–172</sub> | 104 s<br><sub>90–106</sub> | **25 s**<br><sub>23–27</sub> |
| 报告成本 | $0.0226<br><sub>0.0186–0.0280</sub> | $0.0220<br><sub>0.0214–0.0249</sub> | **$0.0076**<br><sub>0.0071–0.0098</sub> |
| 模型请求 | 25<br><sub>19–33</sub> | 18<br><sub>18–22</sub> | **10**<br><sub>10–10</sub> |
| 工具调用 | 22<br><sub>16–30</sub> | 15<br><sub>15–19</sub> | **7**<br><sub>7–7</sub> |
| 输出 token | 18,162<br><sub>15,599–23,328</sub> | 19,722<br><sub>18,764–24,997</sub> | **3,211**<br><sub>3,068–3,573</sub> |
| 输入 token | 34,691<br><sub>30,447–42,543</sub> | 34,141<br><sub>33,121–40,017</sub> | 18,755<br><sub>18,466–33,300</sub> |
| CPU 时间 | 8.5 s<br><sub>8.5–9.2</sub> | 10.0 s<br><sub>8.9–10.0</sub> | **5.3 s**<br><sub>5.3–5.5</sub> |
| 峰值内存 | **270 MB**<br><sub>248–274</sub> | 436 MB<br><sub>432–439</sub> | 375 MB<br><sub>365–379</sub> |
| 已交付步骤 | 9/9 | 9/9 | 9/9 |

每个值为 3 次会话的中位数，其下方的小字为最低到最高会话的范围。加粗表示该行的最佳值，且仅当范围互不重叠时才标注。“9/9”表示 3 次会话中每次的 3 个步骤，全部通过每项外部检查。

每次会话的模型请求和工具调用次数。

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-work-dark.svg">
    <img src="../assets/benchmark-2026-11-22-work-light.svg" width="840" alt="单位图，每个标记代表一次模型请求或工具调用，取 3 次会话的中位数。模型请求：25（未使用 Simplicio）、18（Simplicio 3.14.0）和 10（Simplicio 3.15.0）。工具调用：22、15 和 7。">
  </picture>
</p>

各步骤耗时，采用同一刻度。

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-steps-dark.svg">
    <img src="../assets/benchmark-2026-11-22-steps-light.svg" width="840" alt="各步骤的中位耗时，采用同一刻度。第 1 步，构建：57.3 s（未使用 Simplicio）、53.7 s（Simplicio 3.14.0）和 5.8 s（Simplicio 3.15.0）。第 2 步，修改：17.3 s、15.2 s 和 8.9 s。第 3 步，注册：31.4 s、27.5 s 和 10.3 s。">
  </picture>
</p>

<details>
<summary>各步骤的精确数值</summary>

每个单元格为该步骤的中位耗时和中位成本：

| 步骤 | 未使用 Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. 构建 | 57.3 s / $0.0111 | 53.7 s / $0.0137 | 5.8 s / $0.0022 |
| 2. 修改 | 17.3 s / $0.0040 | 15.2 s / $0.0032 | 8.9 s / $0.0023 |
| 3. 注册 | 31.4 s / $0.0075 | 27.5 s / $0.0056 | 10.3 s / $0.0026 |

</details>

**阅读方法。** 整项任务快 4.9 倍，成本约为其三分之一；即使是未使用 Simplicio 时最快的一次会话（97.1 s），也比使用 Simplicio 3.15.0 时最慢的一次会话（26.6 s）慢 3.7 倍。[方法与限制](../benchmarks/2026-11-22-standard-benchmark.md#limits)

<details>
<summary>各数字如何定义</summary>

- 比率由未取整的中位数计算得出。与上一版本相比，整项任务快 4.2 倍。
- 每个中位数分别计算，因此各步骤相加并不等于整项任务的中位数。
- 最坏情况：未使用 Simplicio 时最快的一次会话（97.1 s）仍比使用 Simplicio 3.15.0 时最慢的一次会话（26.6 s）慢 3.7 倍；未使用 Simplicio 时最便宜的一次会话（$0.0186），成本仍是使用 Simplicio 时最贵的一次会话（$0.0098）的 1.9 倍。
- 基线是使用其自带工具的 Claude Code 2.1.330，没有 MCP 服务器，也没有 Simplicio 配置。
- 每个步骤都从会话外部检查：API 通过 HTTP 调用，页面在无头 Chrome（即没有窗口的 Chrome）中加载。
- 这些检查不测试搜索框、排序、保存后的跳转、页面外观或代码质量。
- 模型请求是对模型的一次调用；工具调用是智能体对某个工具的一次使用。
- 报告成本是所用 token 数乘以模型公布的单价，只计算模型 token，不是账单。
- 输入 token 的范围有重叠，因此本次运行不声称输入 token 存在差异。
- 四个会话同时在一台机器上运行，因此耗时只能在本轮之内比较。

</details>

<a id="where-simplicio-does-not-win"></a>

### Simplicio 不占优的情况

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-memory-dark.svg">
    <img src="../assets/benchmark-2026-11-22-memory-light.svg" width="840" alt="峰值内存，3 次会话的中位数：270 MB（未使用 Simplicio，最低）；436 MB（Simplicio 3.14.0，多 61%）；375 MB（Simplicio 3.15.0，多 39%）。">
  </picture>
</p>

- **内存。** 峰值内存高 39%：375 MB 对比 270 MB。
- **上一版本在此任务上没有提升。** Simplicio 3.14.0 的成本与未使用 Simplicio 时相同。
- **一个简短的一次性 Python 脚本。** Simplicio 3.10.8 更慢（19.6 s 对比 11.4 s），且之后未再测量。
- **你安装的内容与测量的内容并不完全相同。** 这些构建版本是从发布提交编译的，编译时关闭了登录功能。
- **样本量很小。** 每个方案 3 次会话，一个模型，一个项目。

<details>
<summary>完整限制说明</summary>

- **内存。** 峰值内存比未使用 Simplicio 的智能体高 39%：375 MB 对比 270 MB。
- **上一版本在此任务上没有提升。** Simplicio 3.14.0 的成本与未使用 Simplicio 时相同，其耗时差异也在多次运行的波动范围之内。提升始于 3.15.0。
- **一个简短的一次性 Python 脚本。** 在更早的一轮测试中，Simplicio 3.10.8 在每个尝试过的模型上都比未使用它的智能体慢：在 Claude Code 中使用 Claude Sonnet 5.5 时，耗时 19.6 s、成本 $0.0548，未使用 Simplicio 时为 11.4 s 和 $0.0283。尚未在 3.15.0 上重新测量。
- **你安装的内容与测量的内容并不完全相同。** 这些构建版本是从发布提交编译的，编译时关闭了登录功能和后台进程。经过签名的下载版本未经测量。
- **样本量很小。** 每个方案 3 次会话，一个模型，一个全新的小型项目，一台机器，四次会话同时进行；没有任何会话被剔除或重新运行。这些比率衡量的是本任务，而不是你的任务；我们也没有测量你的工作中有多少与本任务相似。

</details>

### 自行验证

[报告](../benchmarks/2026-11-22-standard-benchmark.md)公布了三条提示词（葡萄牙语原文，附译文）、每项外部检查和每次会话的数据；[数据文件](../benchmarks/2026-11-22-standard-benchmark.json)以 JSON 格式提供了相同的内容。测试工具未公开。

<a id="install"></a>

## 安装

macOS / Linux：

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows（PowerShell）：

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

Python（PyPI）：

```bash
python3 -m pip install --upgrade simplicio-installer
simplicio install
```

在 Windows 上，请使用 `py -m pip install --upgrade simplicio-installer`，然后运行 `simplicio install`。

安装程序会校验已签名的发布版本，并自动在它找到的智能体中注册 Simplicio。然后使用 `simplicio auth login` 登录。

<details>
<summary>安装详情</summary>

- 它会下载适用于你平台的最新签名发布版本，并在替换已安装的二进制文件之前，校验其 SHA-256 和 Ed25519 签名。
- 二进制文件存放在 `~/.simplicio/bin/` 下（Windows 上为 `%USERPROFILE%\.simplicio\bin\`），并会自动在它找到的智能体中注册 Simplicio。注册失败时安装程序会中止，而不会报告成功。
- 请重启所有已打开的智能体，使其重新加载配置。如果 Python 脚本目录不在你的 `PATH` 中，请先将其加入。

**登录。** 需要 Google 登录，测试版期间也需要。运行 `simplicio auth login`，然后运行 `simplicio auth status --json`，当它报告 `active: true` 时即可继续。注册无需登录即可完成。切勿将密码或令牌粘贴到智能体的配置中。

要确认 Simplicio 已加载，请在智能体的 MCP 服务器列表中查找 `simplicio`。在 Claude Code 中，`/mcp` 会列出已连接的服务器。想先阅读安装程序吗？它就是 [install.sh](../install.sh)。

要更新，可随时再次运行任一安装程序：它会获取最新发布版本。`install.sh` 和 `install.ps1` 位于本仓库的根目录。

```bash
# macOS / Linux
sh install.sh --doctor
sh install.sh --uninstall --keep-data
sh install.sh --uninstall --purge       # needs SIMPLICIO_CONFIRM_PURGE=1; preserves ~/.simplicio/.env
```

```powershell
# Windows
pwsh install.ps1 -Doctor
pwsh install.ps1 -Uninstall -KeepData
pwsh install.ps1 -Uninstall -Purge      # needs SIMPLICIO_CONFIRM_PURGE=1; preserves .env
```

- `--doctor` 用于检查安装情况。
- `--uninstall --keep-data` 会删除已安装的二进制文件，并保留你的数据，包括位于 `~/.simplicio/login.json` 中、有效期为 30 天的 Google 登录状态。
- `--uninstall --purge` 只删除 Simplicio 管理的状态，包括登录状态。它会保留 `~/.simplicio/.env`，模型服务商的凭据可能保存在该文件中。清除需要设置 `SIMPLICIO_CONFIRM_PURGE=1`。
- 卸载不会修改你智能体的配置。Simplicio 的条目会保留在每个智能体中，直到你在该智能体自己的设置中将其删除。
- 项目自身 `.simplicio` 文件夹中的数据不会被 `--keep-data` 删除。选择 `--purge` 前，请先检查目标。

完整说明：[INSTALL.md](../INSTALL.md)。

</details>

<a id="first-run"></a>

## 首次运行

```bash
simplicio version
cd my-project
simplicio onboard
```

`simplicio version` 用于检查安装；`simplicio onboard` 为项目做好准备。然后在该项目中打开你的智能体。

<a id="works-with-the-agent-you-already-use"></a>

## 与你已在使用的智能体配合工作

安装程序将注册工作交给 Simplicio 自己的注册器。它会为已知如何配置的智能体写入 Simplicio 条目，其中包括 Claude Code、Codex、Cursor、Visual Studio Code、OpenCode、Gemini CLI 和 Kiro。

注册表 [`plugins/simplicio/host-surfaces.json`](../plugins/simplicio/host-surfaces.json) 列出了 43 个智能体 ID；兼容性矩阵 [`docs/hosts/compatibility-matrix.md`](../docs/hosts/compatibility-matrix.md) 将 12 个标记为受支持，29 个标记为 `unverified`。请将 `unverified` 的集成视为未经测试。

<details>
<summary>全部 43 个智能体</summary>

- 注册表列出了 43 个智能体 ID，以及 Simplicio 如何接入每一个：由 Simplicio 写入的 MCP 条目（23 个）、原生插件或扩展（5 个）、可移植插件包（4 个）、需要你自行按指南设置（9 个），或其他命令行工具（2 个）。
- 兼容性矩阵中没有 Codex 和 Gemini CLI 的行。即使注册表显示 Simplicio 会写入条目，也请将 `unverified` 的集成视为未经测试。
- 有 23 个智能体在 [`docs/hosts/`](../docs/hosts/) 中有指南。对于通过插件接入的智能体，插件会在单独的一步中应用，该步骤会征求你的同意，[INSTALL.md](../INSTALL.md) 对此有说明。

| 接入方式 | 数量 | 智能体 |
|---|---|---|
| 由 Simplicio 写入的 MCP 条目 | 23 | **xAI Grok Build**, MiMo Code, Amp, OpenClaude, Antigravity, **Pi**, **oh-my-pi**, Goose, Auggie, Autohand Code, Charm, Cline, Command Code, Continue, Droid, Kilocode, Kimi, Mistral Vibe, Rovo Dev, **Visual Studio Code**, **Meta Muse Code**, **OpenMausBot**, **OpenMuse (Python)** |
| 原生插件或扩展 | 5 | **Claude Code**, Codex, **OpenCode**, Hermes Agent, Gemini CLI |
| 可移植插件包 | 4 | **Cursor**, GitHub Copilot, **Kiro**, Qwen Code |
| 需要你自行按指南设置 | 9 | Devin, Codebuff, CopilotKit OpenDots, CopilotKit OpenBot, agentes.chat, OpenAI dots, xAI Grok Bot, Meta Muse app, Cue by Manus |
| 其他命令行工具 | 2 | **OrcaDev / Orca ADE**, T3 Code |

加粗：兼容性矩阵将该智能体标记为受支持。

</details>

以下是你的智能体会获得的核心工具：

| 工具 | 提供的功能 |
|---|---|
| `simplicio_map` | 仓库的精简地图，帮助智能体理清方向 |
| `simplicio_context` | 任务所需的上下文，范围受限，而不是整个文件 |
| `simplicio_edit` | 依据已准备好的计划进行的结构化文件编辑 |
| `simplicio_validate` | 流水线、测试和交付检查 |
| `simplicio_run` | 在 Simplicio 控制下运行的任务 |

[MCP-CONNECT.md](../MCP-CONNECT.md) 介绍了这些核心工具。

<details>
<summary>手动配置</summary>

Simplicio 是一个本地 STDIO MCP 服务器，因此任何能够启动本地 MCP 服务器的智能体都可以指向它。要重复注册，请运行 `simplicio mcp register`。服务器命令为 `simplicio serve --mcp --stdio`。

如果你的智能体没有为你自动配置，请将以下条目添加到其 MCP 配置中。将路径替换为已安装二进制文件的绝对路径。

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

Codex 读取 TOML。智能体会直接启动 `command`，因此不要使用 `~`，也不要依赖 shell 展开。Windows 路径请使用正斜杠，并替换示例中的用户名。

Windows：

```toml
[mcp_servers.simplicio]
command = "C:/Users/YourName/.simplicio/bin/simplicio.exe"
args = ["serve", "--mcp", "--stdio"]
```

macOS：

```toml
[mcp_servers.simplicio]
command = "/Users/your-name/.simplicio/bin/simplicio"
args = ["serve", "--mcp", "--stdio"]
```

Linux：

```toml
[mcp_servers.simplicio]
command = "/home/your-name/.simplicio/bin/simplicio"
args = ["serve", "--mcp", "--stdio"]
```

各智能体的配置文件位置：[MCP-CONNECT.md](../MCP-CONNECT.md)。

</details>

<a id="command-line"></a>

## 命令行

| 命令 | 你将得到的结果 |
|---|---|
| `simplicio map --repo . --for-llm markdown` | 仓库的精简结构地图，以供模型阅读的格式编写 |
| `simplicio context --repo .` | 任务的范围受限上下文 |
| `simplicio memory query "query" --json` | 从项目的索引记忆中检索到的已知信息，以 JSON 格式输出 |
| `simplicio edit --plan plan.json --repo .` | 一组已准备好的结构化编辑，应用到文件中 |
| `simplicio run "task" --repo . --agents N` | 在 Simplicio 控制下，由 N 个智能体执行的任务 |
| `simplicio loop` | 分轮进行、直至趋于收敛的工作 |

你会在 Simplicio 的消息中看到这些名称：Mapper 观察，Fast 投影或检索，Dev CLI 编辑，Runtime 管控，Loop 趋于收敛。

<a id="safety-and-privacy"></a>

## 安全与隐私

本节描述 3.15.0 版本。

- **留在你的机器上。** 映射、上下文、编辑和检查都在 Simplicio 二进制文件内运行。
- **发送给 SimpleTI（simpleti.com.br）。** 仅用于登录和套餐检查，不包含仓库内容。
- **发送给 GitHub。** 检查发布版本，你可以将其关闭。
- **没有分析数据收集。** Simplicio 不上传分析数据、崩溃报告或使用数据。
- **发送给你配置的服务。** 它们会接收该功能发送的内容，其中可能包括提示词和代码。
- **有两项功能无需任何配置即会访问公开服务。** 网页搜索（DuckDuckGo）和依赖审计（osv.dev）；两者都不发送文件内容。
- **下载。** 从 GitHub 下载；部分辅助脚本还会从 PyPI 或 npm 获取工具。

<details>
<summary>详细说明</summary>

- **留在你的机器上。** 映射、上下文、编辑和检查都在 Simplicio 二进制文件内运行。它将结果交给同一台机器上的你的智能体。使用记录和节省记录是本地文件。你的智能体向其自身模型服务商发送什么，仍由智能体决定，与以前一样。
- **发送给 SimpleTI（simpleti.com.br）。** 仅用于登录和套餐检查，不包含仓库内容：没有文件、文件路径、提示词或编辑内容。
  - 这些请求包含你的登录令牌、Simplicio 版本和你电脑的主机名。可选的许可证查询还会包含你的账户邮箱。
  - 返回内容包括你的账户邮箱、姓名和套餐。
- **发送给 GitHub。** 后台检查新版本，最多约每 12 小时一次，不包含任何关于你或你代码的信息。设置 `SIMPLICIO_DISABLE_AUTO_UPDATE=1` 可将其关闭。更新时，二进制文件从 GitHub 下载，并在替换旧文件之前校验其 SHA-256 和签名。
- **没有分析数据收集。** Simplicio 3.15.0 及其安装到你智能体中的文件均已为此进行过检查：它们都不上传分析数据、崩溃报告或使用数据。它安装的钩子只运行本地程序（Simplicio 二进制文件，以及可选插件的本地脚本）；它们都不会访问网络。
- **发送给你配置的服务。** 模型服务商、GitHub、Jira、聊天通知器或团队缓存，会接收该功能发送的内容，其中可能包括提示词和代码。发送给模型服务商的请求带有一个标头，标明 Simplicio 为客户端。
- **有两项功能无需任何配置即会访问公开服务。** 两者都不发送文件内容。
  - 网页搜索在运行时会将搜索词发送给 DuckDuckGo，除非你配置了其他搜索服务。在 Simplicio 自带的聊天中，看起来像网页问题的消息可能会变成这个搜索词。
  - 依赖安全审计在你运行时，会把依赖项的名称和版本发送给 osv.dev。
- **下载。** 安装程序和更新流程都从 GitHub 下载。部分可选的辅助脚本在你运行时，会从 PyPI 或 npm 获取其自身所需的工具。如果智能体插件找不到 Simplicio 二进制文件，它会从 GitHub 下载官方安装程序，该安装程序固定在某个提交上，并通过 SHA-256 校验。

**签名发布。** 每个版本都会发布其二进制文件的 SHA-256 校验和、Ed25519 签名、SBOM（构建中所含内容的清单）以及构建溯源信息。

安装程序和更新流程会在替换已安装的二进制文件之前，检查校验和与签名。对于稳定版本，签名缺失或无效，以及校验和不匹配，都会被视为硬性失败；相关约定见 [docs/UPDATE_SIGNATURE_CONTRACT.md](../docs/UPDATE_SIGNATURE_CONTRACT.md)。

**安装程序对你的智能体做了哪些改动。**

- 它会在智能体的 MCP 配置中添加一个 Simplicio 条目，并保留配置的其余部分。
- 在 Claude Code 中，它还会允许 `mcp__simplicio__*`，使 Simplicio 工具在自动模式下不被拒绝。
- 在安装程序已验证其钩子接口的智能体中，它还会安装 Simplicio 的钩子。
- 卸载不会撤销这些条目；“安装”一节说明了如何删除它们。[INSTALL.md](../INSTALL.md) 说明了安装程序写入的内容，[`docs/hosts/`](../docs/hosts/) 中各智能体的指南给出了详细信息。

</details>

## 本仓库中的其他内容

<details>
<summary>桌面应用（macOS 预览版）</summary>

macOS（Apple Silicon）桌面版预览以 [Simplicio-3.8.47-arm64.dmg](https://github.com/simpletibr/simplicio/releases/download/v3.8.47/Simplicio-3.8.47-arm64.dmg) 的形式发布。其 SHA-256 位于 [DESKTOP-SHA256SUMS](../DESKTOP-SHA256SUMS) 中，与 Simplicio 二进制文件的校验和分开。该 DMG 没有签名文件，内含 Simplicio 3.8.47 二进制文件。

- 未发布 Windows 桌面版。在 Windows 上，请使用上文的命令行安装方式。
- 未进行 Apple Developer ID 签名和公证。该安装包为临时签名（ad-hoc），即未使用 Apple 开发者证书；我们不声称通过 Gatekeeper 验证，因此 macOS 在你打开它时可能会发出警告。
- 在发布经过签名的桌面安装包之前，上文的命令行安装是受支持的公开安装方式。

详情：[docs/desktop/RELEASE.md](../docs/desktop/RELEASE.md)。

</details>

<details>
<summary>面向维护者：自动生成的流程图</summary>

- README.md 和 MCP-CONNECT.md 中记录的命令与工具，被绘制成一张流程图 [docs/flow/simplicio.svg](../docs/flow/simplicio.svg)，该图由单一源文件 `docs/flow/simplicio.flow.json` 生成。
- 使用 `python3 scripts/generate_flow.py` 重新生成，使用 `python3 scripts/generate_flow.py --check` 检查是否存在漂移。
- 使其与本页及 MCP-CONNECT.md 保持一致的约束是 `python3 -m pytest tests/test_flow_contract.py -q`。
- Langflow 导入检查为 `scripts/verify_flow_langflow.py`，在没有服务器运行时会以失败即关闭的方式退出（退出码 2，`status=blocked`）。证据位于 `docs/flow/evidence/` 和 `docs/flow/render/` 下；[docs/flow/README.md](../docs/flow/README.md) 中有其要求及复现方法。

</details>

<a id="questions-people-ask"></a>

## 常见问题

**这个比较公平吗？**<br>
同一智能体、同一模型、同一组提示词、同一个项目和同样的外部检查，全部在同一轮中完成；基线没有 Simplicio。请参阅 [Simplicio 不占优的情况](#where-simplicio-does-not-win)。

**我需要更换智能体或模型吗？**<br>
不需要。Simplicio 可接入你已在使用的智能体。

**我每次都能得到这些数字吗？**<br>
不能。这些数字衡量的是一项任务、一个模型和一台机器。

**它是开源的吗？**<br>
不是。Simplicio 是专有软件：一个经过签名的二进制文件。本仓库保存安装程序、安装包、文档和数据。

**如何卸载？**<br>
运行 `sh install.sh --uninstall --keep-data`，在 Windows 上则运行 `pwsh install.ps1 -Uninstall -KeepData`。它不会修改你智能体的配置，因此请在每个智能体自己的设置中删除 Simplicio 条目。

**我需要账户吗？**<br>
需要。测试版期间也需要 Google 登录。运行 `simplicio auth login`。

**我的代码会离开我的机器吗？**<br>
映射、上下文、编辑和检查都在你的机器上运行；SimpleTI 和 GitHub 不会收到任何仓库内容。[详情](#safety-and-privacy)。

<a id="documentation-and-community"></a>

## 文档与社区

- **网站：** [simpleti.com.br/simplicio](https://simpleti.com.br/simplicio/)
- **文档：** [simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)
- **Discord：** [加入社区](https://discord.gg/wM6tr7xVb)
- **问题反馈：** [GitHub 问题跟踪器](https://github.com/simpletibr/simplicio/issues)
- **相关项目：** Simplicio Video（hypit）。克隆命令：`git clone https://github.com/hypit-ai/hypit.git simplicio-video`

<p align="center">
  <sub>© 2026 SimpleTI。Simplicio 是已注册的专有软件。保留所有权利。</sub>
</p>
