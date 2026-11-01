# 🔥 Simplicio

<p align="center">
  <img src="../assets/simplicio-hero.png" alt="Simplicio — AIコーディングエージェント" width="920" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=blue&label=latest" alt="最新リリース"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="スター"></a>
  <a href="https://github.com/simpletibr/simplicio/releases"><img src="https://img.shields.io/github/downloads/simpletibr/simplicio/total?color=green" alt="ダウンロード数"></a>
  <a href="../plugins/simplicio/LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="ライセンス"></a>
</p>

<p align="center">
  <a href="#インストール">インストール</a> ·
  <a href="#機能一覧">機能一覧</a> ·
  <a href="#-benchmark-2026-10-31">Benchmark</a> ·
  <a href="https://simpleti.com.br/simplicio/#start">ウェブサイト</a>
</p>

<p align="center">
  <strong>🌍 言語:</strong><br>
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

## ⚡ TL;DR（概要）

**Simplicio** はターミナル上で動作するAIコーディングエージェントです——たった1つのバイナリで、チャット、コード生成、リポジトリコンテキスト、計画立案、ローカルでのマルチエージェントオーケストレーション（64 → 600エージェント）、エビデンス付きPR納品まで、AI支援開発ワークフロー全体を置き換えます。

**あなたのマシン上で動作します。コードがあなたの管理下から離れることはありません。リモートモデルはオプションであり、必須ではありません。**

> すべての操作で、削減したトークン数が正確に表示されます。単一のRustバイナリ、依存関係ゼロ。

## 🚀 インストール

### Codex プラグインからインストール

Codex を使う場合は、Simplicio をプラグインとしてインストールできます。公開 Marketplace を追加してプラグインをインストールし、新しい Codex セッションを開始してください。プラグインが Simplicio Runtime をインストールして起動し、skills と MCP ツールを利用できるようにします。

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

### npm / npx（全OS対応）

```bash
npx simplicio install
```

### pip / PyPI（全OS対応）

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

### 直接インストール（PyPIなし）

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

完了。たった1つのコマンドです。パッケージマネージャーもモデル設定も不要です。

---

## 📊 Benchmark (2026-10-31)

実際のモデルが1つのセッション内でファイルを作成し、編集します。結果はセッションの外で確認します。ページはヘッドレスChromeで、スクリプトは実行して確認します。60セッション、中央値です。

| タスク | 構成 | n | 時間 | モデルへのリクエスト | 出力トークン | コスト | 成果物 |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **JSONから作るページ(ジェネレーター対応)** | **Simplicio 3.10.8** | 10 | **14.1 s** | **6** | **602** | **$0.0021** | **10/10** |
|  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | $0.0215 | 10/10 |
|  | MCPなし | 10 | 176.3 s | 32.5 | 17,929 | $0.0203 | 10/10 |
| **新しいページ(別のデータと言語、ジェネレーター開発には未使用)** | **Simplicio 3.10.8** | 6 | **14.1 s** | **6** | **524** | **$0.0010** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | $0.0153 | 6/6 |
| **Pythonスクリプト(対応するジェネレーターなし)** | **Simplicio 3.10.8** | 6 | **30.7 s** | **10.5** | **1,796** | **$0.0031** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | $0.0051 | 6/6 |
|  | MCPなし | 6 | 22.7 s | 8 | 1,268 | $0.0024 | 6/6 |

効果の源はジェネレーターです。ページのタスクでは、`simplicio_map` がリクエストを振り分け、`simplicio_codegen` がLLMトークン0でファイルを書き込みます。対応するジェネレーターがないタスクでは、3.10.8 は 3.9.2 を上回りますが、MCPなしと比べるとセッションあたり約8秒、0.0007ドル多くかかります。

> OpenCode 2.1.4 と DeepSeek V4.1 Flash を、OpenRouterの固定エンドポイント1つで全実行共通で使用しました。コストは100万トークンあたり入力0.15ドル、出力0.60ドル、キャッシュ0.003ドルで計算しています。1つのモデルと3つの小さなタスクの結果であり、別のタスクでは数値が変わります。 [プロンプト、手法、制限、セッション別データ](../benchmarks/2026-10-31-map-codegen.md).

同じタスクを他のモデルで、Simplicio ありとなしで実行しました。各モデルは 1 つのクライアントで実行したので、比較は同じモデル同士で行ってください。

| モデル | タスク | Simplicio 3.10.8 | MCPなし | 成果物 |
|:---|:---|---:|---:|---:|
| **Claude Sonnet 5.5** (Claude Code) | JSONから作るページ(ジェネレーター対応) | **17.5 s · $0.0672** | 33.4 s · $0.0927 | 10/10 |
|  | 新しいページ(別のデータと言語、ジェネレーター開発には未使用) | **16.3 s · $0.0514** | 22.5 s · $0.0610 | 10/10 |
|  | Pythonスクリプト(対応するジェネレーターなし) | **19.6 s · $0.0548** | 11.4 s · $0.0283 | 10/10 |
| **Grok 4.7** (Grok Build) | JSONから作るページ(ジェネレーター対応) | **31.0 s · $0.1690** | 359.7 s · $0.8590 | 6/6 |
|  | 新しいページ(別のデータと言語、ジェネレーター開発には未使用) | **36.0 s · $0.2059** | 387.5 s · $0.8518 | 6/6 |
|  | Pythonスクリプト(対応するジェネレーターなし) | **82.0 s · $0.3315** | 63.1 s · $0.2452 | 6/6 |
| **Claude Haiku 5.5** (OpenCode) | JSONから作るページ(ジェネレーター対応) | **13.7 s · $0.0046** | 29.3 s · $0.0083 | 10/10 |
|  | 新しいページ(別のデータと言語、ジェネレーター開発には未使用) | **13.8 s · $0.0023** | 28.7 s · $0.0057 | 10/10 |
|  | Pythonスクリプト(対応するジェネレーターなし) | **19.2 s · $0.0033** | 16.6 s · $0.0030 | 10/10 |

[プロンプト、手法、制限、セッション別データ](../benchmarks/2026-11-01-multi-model.md).

---

## 🎯 機能一覧

| コマンド | 説明 |
|---|---|
| `simplicio map --repo .` | LLM向けにリポジトリをマッピング |
| `simplicio memory "query"` | ニューラルリコール（FTS + ベクトル） |
| `simplicio edit '{...}'` | 決定論的ファイル編集 |
| `simplicio coding-loop "task"` | テストが通るまで反復 |
| `simplicio deliver certify` | 出荷前に5つの品質ゲートを通過 |
| `simplicio run "task" --agents N` | マルチエージェントオーケストレーション |
---

## 🏗️ アーキテクチャ

```
LLM (Claude/Codex/Gemini)          Simplicio Runtime (Rust)
  |                                   |
  | 1. Orient（方向付け）              | simplicio map
  | 2. Recall（想起）                  | simplicio memory
  | 3. Decide（判断）                  |
  | 4. Edit（編集） ────────────────> | simplicio edit (0 tokens)
  | 5. Verify（検証）<──────────────  | simplicio deliver certify
  | 6. Iterate（反復）                 | simplicio coding-loop
```

**LLMが推論します。Simplicioが決定論的に実行します。**

---

## ✨ 特徴

- 🏠 **ローカル優先** — 内蔵llama.cpp、必要なときだけリモートに拡張
- 🪜 **階層型エージェント** — 有料クラウドの前に64 → 100 → 200 → 600のローカルエージェント
- 🔇 **シャノン新規性ゲート** — 冗長な出力をフィルタリング（重複排除でゼロトークン）
- 🔒 **封印レシート** — アーティファクトごとにsha256、改ざん防止のエビデンスチェーン
- 🛡️ **5つの納品ゲート** — 受入、検証、実行確認、回帰テスト、自己レビュー
- ⚡ **アクションゲート** — チャット発信の変更に対するリスク分類 + ブロックリスト
- 🔌 **MCP/ACP** — Model Context Protocol + Agent Client Protocol
- 🌐 **ゲートウェイ** — Telegram、Discord、Slack、WhatsApp
- 🧩 **スキルシステム** — 再利用可能な機能を読み込んで連鎖実行
- 💾 **メモリDB** — セッション間で永続的なFTS + ベクトルリコール
- 🔀 **LLMルーター** — LLMなし → ローカルLLM → リモートLLM を自動切替
- 🖥️ **クロスプラットフォーム** — macOS、Linux、Windows、単一バイナリ

---

## 🎁 無料パブリックベータ

**決定論的コマンドは永久無料です:**
`map`、`validate`、`edit`、`deliver`、`checkpoint`

**AI機能は期間無制限でパブリックベータ期間中無料です。**
課金は将来のアップデートで定義されます。

```bash
simplicio license status
```

---

## 📋 必要環境

| 要件 | 最小 | 推奨 |
|---|---|---|
| RAM | 8 GB | 16 GB以上 |
| ストレージ | 5 MB | 1.5 GB（ローカルLLM使用時） |
| OS | macOS 13+、Linux、Windows 10+ | macOS ARM64 |
| ターミナル | 任意のモダンなターミナル | WezTerm / Alacritty / Ghostty |

---

## 🌐 エコシステム

- [ウェブサイト](https://simpleti.com.br/simplicio/#start) — 完全なドキュメント、ベンチマーク、インストール
- [Discord](https://discord.gg/wM6tr7xVb) — コミュニティとサポート

---

## 📄 ライセンス

Proprietary（プロプライエタリ）。バイナリは無料でダウンロードして使用できます。AI機能はパブリックベータ期間中無料です。詳しくは [LICENSE](../plugins/simplicio/LICENSE) をご覧ください。

---

## ⭐ スター履歴

<a href="https://star-history.com/#simpletibr/simplicio&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" />
    <img alt="スター履歴チャート" src="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" width="100%" />
  </picture>
</a>

---

## 💬 コミュニティ

- [Discord](https://discord.gg/wM6tr7xVb) — チャット、サポート、早期アクセス
- [GitHub Issues](https://github.com/simpletibr/simplicio/issues) — バグ報告と機能リクエスト

---

<p align="center">
  <strong>🔥 Simplicio 🔥</strong>
</p>
