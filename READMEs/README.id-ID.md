# 🔥 Simplicio

<p align="center">
  <img src="../assets/simplicio-hero.png" alt="Simplicio — AI coding agent" width="920" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=blue&label=latest" alt="Rilis Terbaru"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Bintang"></a>
  <a href="https://github.com/simpletibr/simplicio/releases"><img src="https://img.shields.io/github/downloads/simpletibr/simplicio/total?color=green" alt="Unduhan"></a>
  <a href="../plugins/simplicio/LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="Lisensi"></a>
</p>

<p align="center">
  <a href="#instalasi">Instalasi</a> ·
  <a href="#yang-dilakukan">Yang Dilakukan</a> ·
  <a href="#-benchmark-2026-10-31">Benchmark</a> ·
  <a href="https://simpleti.com.br/simplicio/#start">Situs Web</a>
</p>

<p align="center">
  <strong>🌍 Bahasa:</strong><br>
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

**Simplicio** adalah agen coding AI berbasis terminal — satu biner yang menggantikan
seluruh alur kerja pengembangan berbantuan AI Anda: obrolan, pembuatan kode, konteks
repositori, perencanaan, orkestrasi multi-agen lokal (64 → 600 agen), dan
pengiriman PR berbasis bukti.

**Berjalan di mesin Anda. Kode Anda tidak pernah meninggalkan kendali Anda. Model jarak jauh
bersifat opsional, tidak wajib.**

> Setiap interaksi menunjukkan persis berapa banyak token yang Anda hemat. Biner Rust tunggal, tanpa dependensi.

## 🚀 Instalasi

### Instal melalui plugin Codex

Jika Anda menggunakan Codex, Anda dapat menginstal Simplicio sebagai plugin. Tambahkan Marketplace publik, instal plugin, lalu mulai sesi Codex baru; plugin akan menginstal dan melakukan bootstrap Simplicio Runtime serta menyediakan skills dan alat MCP.

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

### npm / npx (OS apa saja)

```bash
npx simplicio install
```

### pip / PyPI (OS apa saja)

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

### Instalasi langsung (tanpa PyPI)

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

Selesai. Satu perintah. Tanpa manajer paket, tanpa konfigurasi model.

---

## 📊 Benchmark (2026-10-31)

Model sungguhan membuat file lalu mengeditnya dalam sesi yang sama. Hasilnya diperiksa di luar sesi: halaman di Chrome headless, skrip dengan menjalankannya. 60 sesi, nilai median.

| Tugas | Konfigurasi | n | Waktu | Permintaan model | Token keluaran | Biaya | Terkirim |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **Halaman dari file JSON, dicakup generator** | **Simplicio 3.10.8** | 10 | **14.1 s** | **6** | **602** | **$0.0021** | **10/10** |
|  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | $0.0215 | 10/10 |
|  | Tanpa MCP | 10 | 176.3 s | 32.5 | 17,929 | $0.0203 | 10/10 |
| **Halaman baru, data dan bahasa lain, tidak dipakai untuk membangun generator** | **Simplicio 3.10.8** | 6 | **14.1 s** | **6** | **524** | **$0.0010** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | $0.0153 | 6/6 |
| **Skrip Python, tidak dicakup generator mana pun** | **Simplicio 3.10.8** | 6 | **30.7 s** | **10.5** | **1,796** | **$0.0031** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | $0.0051 | 6/6 |
|  | Tanpa MCP | 6 | 22.7 s | 8 | 1,268 | $0.0024 | 6/6 |

Keuntungan datang dari generator: pada tugas halaman, `simplicio_map` merutekan permintaan dan `simplicio_codegen` menulis file dengan 0 token LLM. Jika tidak ada generator yang mencakup tugas, 3.10.8 mengungguli 3.9.2, tetapi menghabiskan sekitar 8 detik dan $0.0007 lebih banyak per sesi dibanding tanpa MCP.

> OpenCode 2.1.4 dan DeepSeek V4.1 Flash pada satu endpoint OpenRouter tetap, sama untuk setiap eksekusi. Biaya dihitung dengan $0.15 input, $0.60 output, dan $0.003 cache per sejuta token. Ini satu model pada tiga tugas kecil: tugas lain akan memberi angka lain. [Prompt, metode, batasan, dan data per sesi](../benchmarks/2026-10-31-map-codegen.md).

Tugas yang sama pada model lain, dengan dan tanpa Simplicio. Setiap model berjalan di satu klien, jadi bandingkan model dengan dirinya sendiri.

| Model | Tugas | Simplicio 3.10.8 | Tanpa MCP | Terkirim |
|:---|:---|---:|---:|---:|
| **Claude Sonnet 5.5** (Claude Code) | Halaman dari file JSON, dicakup generator | **17.5 s · $0.0672** | 33.4 s · $0.0927 | 10/10 |
|  | Halaman baru, data dan bahasa lain, tidak dipakai untuk membangun generator | **16.3 s · $0.0514** | 22.5 s · $0.0610 | 10/10 |
|  | Skrip Python, tidak dicakup generator mana pun | **19.6 s · $0.0548** | 11.4 s · $0.0283 | 10/10 |
| **Grok 4.7** (Grok Build) | Halaman dari file JSON, dicakup generator | **31.0 s · $0.1690** | 359.7 s · $0.8590 | 6/6 |
|  | Halaman baru, data dan bahasa lain, tidak dipakai untuk membangun generator | **36.0 s · $0.2059** | 387.5 s · $0.8518 | 6/6 |
|  | Skrip Python, tidak dicakup generator mana pun | **82.0 s · $0.3315** | 63.1 s · $0.2452 | 6/6 |
| **Claude Haiku 5.5** (OpenCode) | Halaman dari file JSON, dicakup generator | **13.7 s · $0.0046** | 29.3 s · $0.0083 | 10/10 |
|  | Halaman baru, data dan bahasa lain, tidak dipakai untuk membangun generator | **13.8 s · $0.0023** | 28.7 s · $0.0057 | 10/10 |
|  | Skrip Python, tidak dicakup generator mana pun | **19.2 s · $0.0033** | 16.6 s · $0.0030 | 10/10 |

[Prompt, metode, batasan, dan data per sesi](../benchmarks/2026-11-01-multi-model.md).

---

## 🎯 Yang Dilakukan

| Perintah | Deskripsi |
|---|---|
| `simplicio map --repo .` | Memetakan repositori untuk LLM |
| `simplicio memory "query"` | Panggil ulang neural (FTS + vektor) |
| `simplicio edit '{...}'` | Pengeditan file deterministik |
| `simplicio coding-loop "task"` | Mengulang hingga pengujian lulus |
| `simplicio deliver certify` | 5 gerbang kualitas sebelum dikirim |
| `simplicio run "task" --agents N` | Orkestrasi multi-agen |
---

## 🏗️ Arsitektur

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

**LLM bernalar. Simplicio mengeksekusi secara deterministik.**

---

## ✨ Fitur

- 🏠 **Lokal-pertama** — llama.cpp bawaan, naik ke jarak jauh hanya jika diperlukan
- 🪜 **Agen bertingkat** — 64 → 100 → 200 → 600 agen lokal sebelum cloud berbayar
- 🔇 **Gerbang kebaruan Shannon** — menyaring output yang redundan (nol token saat dedup)
- 🔒 **Tanda terima tersegel** — sha256 per artefak, rantai bukti anti-rusak
- 🛡️ **5 gerbang pengiriman** — penerimaan, validasi, jalankan-verifikasi, regresi, tinjauan-mandiri
- ⚡ **Gerbang aksi** — klasifikasi risiko + blokir untuk mutasi yang dimulai dari obrolan
- 🔌 **MCP/ACP** — Model Context Protocol + Agent Client Protocol
- 🌐 **Gerbang** — Telegram, Discord, Slack, WhatsApp
- 🧩 **Sistem skill** — memuat dan merantai kemampuan yang dapat digunakan ulang
- 💾 **DB Memori** — FTS persisten + panggil ulang vektor antar sesi
- 🔀 **Router LLM** — tanpa LLM → LLM lokal → LLM jarak jauh secara otomatis
- 🖥️ **Lintas-platform** — macOS, Linux, Windows, biner tunggal

---

## 🎁 Beta Publik Gratis

**Perintah deterministik GRATIS selamanya:**
`map`, `validate`, `edit`, `deliver`, `checkpoint`

**Fitur AI gratis selama beta publik tanpa tanggal akhir.**
Penagihan akan ditentukan di pembaruan mendatang.

```bash
simplicio license status
```

---

## 📋 Persyaratan

| Persyaratan | Minimum | Direkomendasikan |
|---|---|---|
| RAM | 8 GB | 16 GB+ |
| Penyimpanan | 5 MB | 1,5 GB (dengan LLM lokal) |
| OS | macOS 13+, Linux, Windows 10+ | macOS ARM64 |
| Terminal | terminal modern apa saja | WezTerm / Alacritty / Ghostty |

---

## 🌐 Ekosistem

- [Situs Web](https://simpleti.com.br/simplicio/#start) — dokumentasi lengkap, tolok ukur, instalasi
- [Discord](https://discord.gg/wM6tr7xVb) — komunitas dan dukungan

---

## 📄 Lisensi

Kepemilikan. Biner gratis untuk diunduh dan digunakan. Fitur AI gratis selama
beta publik. Lihat [LICENSE](../plugins/simplicio/LICENSE).

---

## ⭐ Riwayat Bintang

<a href="https://star-history.com/#simpletibr/simplicio&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" />
    <img alt="Grafik Riwayat Bintang" src="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" width="100%" />
  </picture>
</a>

---

## 💬 Komunitas

- [Discord](https://discord.gg/wM6tr7xVb) — obrolan, dukungan, akses awal
- [GitHub Issues](https://github.com/simpletibr/simplicio/issues) — laporan bug dan permintaan fitur

---

<p align="center">
  <strong>🔥 Simplicio 🔥</strong>
</p>
