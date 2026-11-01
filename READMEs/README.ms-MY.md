# 🔥 Simplicio

<p align="center">
  <img src="../assets/simplicio-hero.png" alt="Simplicio — ejen pengekodan AI" width="920" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=blue&label=terkini" alt="Keluaran Terkini"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Bintang"></a>
  <a href="https://github.com/simpletibr/simplicio/releases"><img src="https://img.shields.io/github/downloads/simpletibr/simplicio/total?color=green" alt="Muat Turun"></a>
  <a href="../plugins/simplicio/LICENSE"><img src="https://img.shields.io/badge/licensi-Proprietary-red" alt="Lesen"></a>
</p>

<p align="center">
  <a href="#-pemasangan">Pasang</a> ·
  <a href="#-apa-yang-ia-lakukan">Ciri</a> ·
  <a href="#-benchmark-2026-10-31">Benchmark</a> ·
  <a href="https://simpleti.com.br/simplicio/#start">Laman Web</a>
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

## ⚡ RL;DR

**Simplicio** ialah ejen pengekodan AI terminal — satu binari yang menggantikan
keseluruhan aliran kerja pembangunan berbantu AI anda: sembang, penjanaan kod,
konteks repositori, perancangan, orkestrasi multi-ejen tempatan (64 → 600 ejen),
dan penghantaran PR berasaskan bukti.

**Berjalan di mesin anda. Kod anda tidak pernah meninggalkan kawalan anda. Model
jarak jauh adalah pilihan, bukan keperluan.**

> Setiap interaksi menunjukkan dengan tepat berapa banyak token yang anda jimatkan. Binari Rust tunggal, sifar kebergantungan.

## 🚀 Pemasangan

### Pasang melalui pemalam Codex

Jika anda menggunakan Codex, anda boleh memasang Simplicio sebagai pemalam. Tambahkan Marketplace awam, pasang pemalam dan mulakan sesi Codex baharu; pemalam memasang serta memulakan Simplicio Runtime dan menyediakan skills serta alat MCP.

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

### npm / npx (sebarang OS)

```bash
npx simplicio install
```

### pip / PyPI (sebarang OS)

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

### Pemasangan terus (tanpa PyPI)

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

Selesai. Satu arahan. Tiada pengurus pakej, tiada konfigurasi model.

---

## 📊 Benchmark (2026-10-31)

Model sebenar mencipta fail dan menyuntingnya dalam sesi yang sama. Hasilnya disemak di luar sesi: halaman dalam Chrome headless, skrip dengan menjalankannya. 60 sesi, nilai median.

| Tugasan | Konfigurasi | n | Masa | Permintaan model | Token output | Kos | Dihantar |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **Halaman daripada fail JSON, diliputi penjana** | **Simplicio 3.10.8** | 10 | **14.1 s** | **6** | **602** | **$0.0021** | **10/10** |
|  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | $0.0215 | 10/10 |
|  | Tanpa MCP | 10 | 176.3 s | 32.5 | 17,929 | $0.0203 | 10/10 |
| **Halaman baharu, data dan bahasa lain, tidak digunakan untuk membina penjana** | **Simplicio 3.10.8** | 6 | **14.1 s** | **6** | **524** | **$0.0010** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | $0.0153 | 6/6 |
| **Skrip Python, tiada penjana yang meliputinya** | **Simplicio 3.10.8** | 6 | **30.7 s** | **10.5** | **1,796** | **$0.0031** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | $0.0051 | 6/6 |
|  | Tanpa MCP | 6 | 22.7 s | 8 | 1,268 | $0.0024 | 6/6 |

Keuntungan datang daripada penjana: dalam tugasan halaman, `simplicio_map` menghala permintaan dan `simplicio_codegen` menulis fail dengan 0 token LLM. Apabila tiada penjana meliputi tugasan, 3.10.8 mengatasi 3.9.2, tetapi menelan kira-kira 8 s dan $0.0007 lebih bagi setiap sesi berbanding tanpa MCP.

> OpenCode 2.1.4 dan DeepSeek V4.1 Flash pada satu titik akhir OpenRouter yang tetap, sama bagi setiap larian. Kos dikira pada $0.15 input, $0.60 output dan $0.003 cache bagi setiap sejuta token. Ini satu model pada tiga tugasan kecil: tugasan lain akan memberi angka lain. [Prompt, kaedah, had dan data setiap sesi](../benchmarks/2026-10-31-map-codegen.md).

---

## 🎯 Apa Yang Ia Lakukan

| Perintah | Penerangan |
|---|---|
| `simplicio map --repo .` | Memetakan repositori untuk LLM |
| `simplicio memory "query"` | Ingatan semula neural (FTS + vektor) |
| `simplicio edit '{...}'` | Suntingan fail deterministik |
| `simplicio coding-loop "tugas"` | Berulang sehingga ujian lulus |
| `simplicio deliver certify` | 5 pintu kualiti sebelum penghantaran |
| `simplicio run "tugas" --agents N` | Orkestrasi multi-ejen |
---

## 🏗️ Seni Bina

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

**LLM menaakul. Simplicio melaksana secara deterministik.**

---

## ✨ Ciri

- 🏠 **Tempatan-dahulu** — llama.cpp terbina dalam, skala ke jarak jauh hanya apabila perlu
- 🪜 **Ejen bertingkat** — 64 → 100 → 200 → 600 ejen tempatan sebelum awan berbayar
- 🔇 **Gerbang kebaharuan Shannon** — menapis output berlebihan (sifar token pada dedup)
- 🔒 **Resit bermeterai** — sha256 setiap artifak, rantaian bukti kalis gangguan
- 🛡️ **5 pintu penghantaran** — penerimaan, pengesahan, laksana-verify, regresi, semakan sendiri
- ⚡ **Gerbang tindakan** — pengelasan risiko + senarai blok untuk mutasi cetusan sembang
- 🔌 **MCP/ACP** — Protokol Konteks Model + Protokol Klien Ejen
- 🌐 **Gerbang** — Telegram, Discord, Slack, WhatsApp
- 🧩 **Sistem kemahiran** — memuat dan merantai kebolehan boleh guna semula
- 💾 **Pangkalan data ingatan** — FTS berterusan + ingatan vektor merentas sesi
- 🔀 **Penghala LLM** — tiada LLM → LLM tempatan → LLM jarak jauh secara automatik
- 🖥️ **Merentas platform** — macOS, Linux, Windows, binari tunggal

---

## 🎁 Beta Awam Percuma

**Perintah deterministik adalah PERCUMA selama-lamanya:**
`map`, `validate`, `edit`, `deliver`, `checkpoint`

**Ciri AI adalah percuma semasa beta awam tanpa tarikh tamat.**
Pengecasan akan ditentukan dalam kemas kini akan datang.

```bash
simplicio license status
```

---

## 📋 Keperluan

| Keperluan | Minimum | Disarankan |
|---|---|---|
| RAM | 8 GB | 16 GB+ |
| Storan | 5 MB | 1.5 GB (dengan LLM tempatan) |
| OS | macOS 13+, Linux, Windows 10+ | macOS ARM64 |
| Terminal | mana-mana terminal moden | WezTerm / Alacritty / Ghostty |

---

## 🌐 Ekosistem

- [Laman Web](https://simpleti.com.br/simplicio/#start) — dokumen penuh, penanda aras, pemasangan
- [Discord](https://discord.gg/wM6tr7xVb) — komuniti dan sokongan

---

## 📄 Lesen

Proprietari. Binari percuma untuk dimuat turun dan digunakan. Ciri AI percuma
semasa beta awam. Lihat [LICENSE](../plugins/simplicio/LICENSE).

---

## ⭐ Sejarah Bintang

<a href="https://star-history.com/#simpletibr/simplicio&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" />
    <img alt="Carta Sejarah Bintang" src="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" width="100%" />
  </picture>
</a>

---

## 💬 Komuniti

- [Discord](https://discord.gg/wM6tr7xVb) — sembang, sokongan, akses awal
- [Isu GitHub](https://github.com/simpletibr/simplicio/issues) — pepijat dan permintaan ciri

---

<p align="center">
  <strong>🔥 Simplicio 🔥</strong>
</p>
