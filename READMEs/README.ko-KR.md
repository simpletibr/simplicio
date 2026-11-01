# 🔥 Simplicio

<p align="center">
  <img src="../assets/simplicio-hero.png" alt="Simplicio — AI 코딩 에이전트" width="920" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=blue&label=latest" alt="Latest Release"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Stars"></a>
  <a href="https://github.com/simpletibr/simplicio/releases"><img src="https://img.shields.io/github/downloads/simpletibr/simplicio/total?color=green" alt="Downloads"></a>
  <a href="../plugins/simplicio/LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="License"></a>
</p>

<p align="center">
  <a href="#설치">설치</a> ·
  <a href="#기능">기능</a> ·
  <a href="#-benchmark-2026-10-31">Benchmark</a> ·
  <a href="https://simpleti.com.br/simplicio/#start">웹사이트</a>
</p>

<p align="center">
  <strong>🌍 언어:</strong><br>
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

**Simplicio**는 터미널 AI 코딩 에이전트입니다 — 단일 바이너리로 채팅, 코드 생성,
리포지토리 컨텍스트, 계획 수립, 로컬 멀티에이전트 오케스트레이션 (64 → 600개 에이전트),
증거 기반 PR 전달 등 AI 지원 개발 워크플로 전체를 대체합니다.

**사용자 머신에서 실행됩니다. 코드는 절대 사용자의 통제를 벗어나지 않습니다.
원격 모델은 선택 사항이지 필수가 아닙니다.**

> 모든 상호작용에서 정확히 얼마나 많은 토큰을 절약했는지 보여줍니다. 단일 Rust 바이너리, 종속성 제로.

## 🚀 설치

### Codex 플러그인으로 설치

Codex를 사용한다면 Simplicio를 플러그인으로 설치할 수 있습니다. 공개 Marketplace를 추가하고 플러그인을 설치한 뒤 새 Codex 세션을 시작하세요. 플러그인이 Simplicio Runtime을 설치하고 부트스트랩하며 skills와 MCP 도구를 제공합니다.

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

### npm / npx (모든 OS)

```bash
npx simplicio install
```

### pip / PyPI (모든 OS)

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

### 직접 설치(PyPI 없이)

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

끝. 하나의 명령어입니다. 패키지 매니저도, 모델 설정도 필요 없습니다.

---

## 📊 Benchmark (2026-10-31)

실제 모델이 한 세션에서 파일을 만들고 편집합니다. 결과는 세션 밖에서 확인합니다. 페이지는 헤드리스 Chrome으로, 스크립트는 직접 실행해서 확인합니다. 60개 세션, 중앙값입니다.

| 작업 | 구성 | n | 시간 | 모델 요청 | 출력 토큰 | 비용 | 납품 |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **JSON으로 만드는 페이지, 생성기 지원** | **Simplicio 3.10.8** | 10 | **14.1 s** | **6** | **602** | **$0.0021** | **10/10** |
|  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | $0.0215 | 10/10 |
|  | MCP 없음 | 10 | 176.3 s | 32.5 | 17,929 | $0.0203 | 10/10 |
| **새 페이지, 다른 데이터와 언어, 생성기 개발에 사용되지 않음** | **Simplicio 3.10.8** | 6 | **14.1 s** | **6** | **524** | **$0.0010** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | $0.0153 | 6/6 |
| **Python 스크립트, 지원하는 생성기 없음** | **Simplicio 3.10.8** | 6 | **30.7 s** | **10.5** | **1,796** | **$0.0031** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | $0.0051 | 6/6 |
|  | MCP 없음 | 6 | 22.7 s | 8 | 1,268 | $0.0024 | 6/6 |

이득은 생성기에서 나옵니다. 페이지 작업에서는 `simplicio_map`이 요청을 라우팅하고 `simplicio_codegen`이 LLM 토큰 0개로 파일을 작성합니다. 지원하는 생성기가 없는 작업에서는 3.10.8이 3.9.2보다 낫지만, MCP를 쓰지 않을 때보다 세션당 약 8초와 0.0007달러가 더 듭니다.

> OpenCode 2.1.4와 DeepSeek V4.1 Flash를 고정된 OpenRouter 엔드포인트 하나에서 모든 실행에 동일하게 사용했습니다. 비용은 100만 토큰당 입력 0.15달러, 출력 0.60달러, 캐시 0.003달러로 계산했습니다. 한 모델과 작은 작업 세 개의 결과이며, 다른 작업에서는 수치가 달라집니다. [프롬프트, 방법, 한계, 세션별 데이터](../benchmarks/2026-10-31-map-codegen.md).

같은 작업을 다른 모델에서 Simplicio를 쓸 때와 쓰지 않을 때로 실행했습니다. 모델마다 클라이언트 하나에서만 실행했으므로 같은 모델끼리만 비교하세요.

| 모델 | 작업 | Simplicio 3.10.8 | MCP 없음 | 납품 |
|:---|:---|---:|---:|---:|
| **Claude Sonnet 5.5** (Claude Code) | JSON으로 만드는 페이지, 생성기 지원 | **17.5 s · $0.0672** | 33.4 s · $0.0927 | 10/10 |
|  | 새 페이지, 다른 데이터와 언어, 생성기 개발에 사용되지 않음 | **16.3 s · $0.0514** | 22.5 s · $0.0610 | 10/10 |
|  | Python 스크립트, 지원하는 생성기 없음 | **19.6 s · $0.0548** | 11.4 s · $0.0283 | 10/10 |
| **Grok 4.7** (Grok Build) | JSON으로 만드는 페이지, 생성기 지원 | **31.0 s · $0.1690** | 359.7 s · $0.8590 | 6/6 |
|  | 새 페이지, 다른 데이터와 언어, 생성기 개발에 사용되지 않음 | **36.0 s · $0.2059** | 387.5 s · $0.8518 | 6/6 |
|  | Python 스크립트, 지원하는 생성기 없음 | **82.0 s · $0.3315** | 63.1 s · $0.2452 | 6/6 |
| **Claude Haiku 5.5** (OpenCode) | JSON으로 만드는 페이지, 생성기 지원 | **13.7 s · $0.0046** | 29.3 s · $0.0083 | 10/10 |
|  | 새 페이지, 다른 데이터와 언어, 생성기 개발에 사용되지 않음 | **13.8 s · $0.0023** | 28.7 s · $0.0057 | 10/10 |
|  | Python 스크립트, 지원하는 생성기 없음 | **19.2 s · $0.0033** | 16.6 s · $0.0030 | 10/10 |

[프롬프트, 방법, 한계, 세션별 데이터](../benchmarks/2026-11-01-multi-model.md).

---

## 🎯 기능

| 명령어 | 설명 |
|---|---|
| `simplicio map --repo .` | LLM을 위해 리포지토리 매핑 |
| `simplicio memory "query"` | 신경망 검색 (FTS + 벡터) |
| `simplicio edit '{...}'` | 결정론적 파일 편집 |
| `simplicio coding-loop "task"` | 테스트 통과까지 반복 |
| `simplicio deliver certify` | 출시 전 5단계 품질 게이트 |
| `simplicio run "task" --agents N` | 멀티에이전트 오케스트레이션 |
---

## 🏗️ 아키텍처

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

**LLM은 추론합니다. Simplicio는 결정론적으로 실행합니다.**

---

## ✨ 특징

- 🏠 **로컬 우선** — 내장 llama.cpp, 필요할 때만 원격으로 확장
- 🪜 **계층형 에이전트** — 유료 클라우드 전 64 → 100 → 200 → 600개 로컬 에이전트
- 🔇 **Shannon 참신성 게이트** — 중복 출력 필터링 (중복 제거 시 토큰 제로)
- 🔒 **봉인 영수증** — 아티팩트당 sha256, 변조 방지 증명 체인
- 🛡️ **5단계 전달 게이트** — 승인, 검증, 실행 확인, 회귀 테스트, 자체 검토
- ⚡ **액션 게이트** — 채팅 기반 변경에 대한 위험 분류 + 차단 목록
- 🔌 **MCP/ACP** — Model Context Protocol + Agent Client Protocol
- 🌐 **게이트웨이** — Telegram, Discord, Slack, WhatsApp
- 🧩 **스킬 시스템** — 재사용 가능한 기능 로드 및 체이닝
- 💾 **메모리 DB** — 세션 간 지속적 FTS + 벡터 검색
- 🔀 **LLM 라우터** — LLM 없음 → 로컬 LLM → 원격 LLM 자동 전환
- 🖥️ **크로스 플랫폼** — macOS, Linux, Windows, 단일 바이너리

---

## 🎁 무료 공개 베타

**결정론적 명령어는 영원히 무료입니다:**
`map`, `validate`, `edit`, `deliver`, `checkpoint`

**AI 기능은 공개 베타 기간 동안 종료일 없이 무료입니다.**
과금은 향후 업데이트에서 정의됩니다.

```bash
simplicio license status
```

---

## 📋 시스템 요구사항

| 요구사항 | 최소 | 권장 |
|---|---|---|
| RAM | 8 GB | 16 GB+ |
| 저장공간 | 5 MB | 1.5 GB (로컬 LLM 포함 시) |
| OS | macOS 13+, Linux, Windows 10+ | macOS ARM64 |
| 터미널 | 모든 최신 터미널 | WezTerm / Alacritty / Ghostty |

---

## 🌐 생태계

- [웹사이트](https://simpleti.com.br/simplicio/#start) — 전체 문서, 벤치마크, 설치
- [Discord](https://discord.gg/wM6tr7xVb) — 커뮤니티 및 지원

---

## 📄 라이선스

Proprietary. 바이너리는 무료로 다운로드 및 사용 가능합니다. AI 기능은
공개 베타 기간 동안 무료입니다. [LICENSE](../plugins/simplicio/LICENSE)를 참조하세요.

---

## ⭐ 스타 기록

<a href="https://star-history.com/#simpletibr/simplicio&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" />
    <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" width="100%" />
  </picture>
</a>

---

## 💬 커뮤니티

- [Discord](https://discord.gg/wM6tr7xVb) — 채팅, 지원, 얼리 액세스
- [GitHub Issues](https://github.com/simpletibr/simplicio/issues) — 버그 및 기능 요청

---

<p align="center">
  <strong>🔥 Simplicio 🔥</strong>
</p>
