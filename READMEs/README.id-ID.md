<div align="center">

<img src="../assets/simplicio-icon-192.png" alt="Logo Simplicio" width="96" height="96">

<h1>Simplicio</h1>

<p><b>UltraFast Mode for all.</b></p>

<p><b>Agen yang sama, model yang sama, tugas yang sama: 121&nbsp;s&nbsp;→&nbsp;25&nbsp;s, dan $0.0226&nbsp;→&nbsp;$0.0076.</b></p>

<p>Tanpa Simplicio → dengan Simplicio 3.15.0. Median dari 3 sesi untuk satu tugas pemrograman kecil di Claude Code dengan Claude Haiku 5.5.</p>

<p>Simplicio berjalan di mesin Anda dan menambahkan alat ke agen pemrograman yang sudah Anda gunakan.</p>

<p>
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=2fe6a0&label=release" alt="Rilis terbaru"></a>
  <a href="https://simpleti.com.br/simplicio/docs"><img src="https://img.shields.io/badge/docs-simpleti.com.br-ffd23f" alt="Dokumentasi"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Bintang"></a>
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="Lisensi: proprietary">
</p>

<p>
  <a href="../README.md">English</a> ·
  <a href="README.pt-BR.md">Português (Brasil)</a> ·
  <a href="README.es-ES.md">Español</a> ·
  <a href="README.fr-FR.md">Français</a> ·
  <a href="README.it-IT.md">Italiano</a> ·
  <a href="README.pl-PL.md">Polski</a> ·
  <a href="README.ru-RU.md">Русский</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja-JP.md">日本語</a> ·
  <a href="README.ko-KR.md">한국어</a> ·
  <a href="README.hi-IN.md">हिन्दी</a> ·
  <a href="README.ar-SA.md">العربية</a>&lrm; ·
  <a href="README.he-IL.md">עברית</a>&lrm; ·
  Bahasa Indonesia ·
  <a href="README.ms-MY.md">Bahasa Melayu</a>
</p>
<p align="center"><sub>Ini adalah terjemahan dari <a href="../README.md">README bahasa Inggris</a>. Jika keduanya berbeda, halaman bahasa Inggris menjadi acuan. Angka dan grafik tetap dalam bahasa Inggris.</sub></p>

</div>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-dark.svg">
    <img src="../assets/benchmark-2026-11-22-light.svg" width="840" alt="Diagram batang yang membandingkan tanpa Simplicio, Simplicio 3.14.0 dan Simplicio 3.15.0 pada tiga ukuran, median dari tiga sesi untuk masing-masing. Waktu untuk seluruh tugas: 121 s tanpa Simplicio, 104 s dengan Simplicio 3.14.0 dan 25 s dengan Simplicio 3.15.0. Biaya: $0.0226, $0.0220 dan $0.0076. Token keluaran: 18,162, 19,722 dan 3,211.">
  </picture>
</p>

<p align="center">
  <sub>Median dari 3 sesi untuk setiap kondisi uji (tanpa Simplicio, Simplicio 3.14.0 dan Simplicio 3.15.0). Claude Haiku 5.5 di Claude Code 2.1.330, 2026-11-22. Setiap kondisi uji punya 9 dari 9 langkah yang selesai. Garis tipis di setiap batang membentang dari sesi terendah hingga tertinggi.<br>
  <a href="../benchmarks/2026-11-22-standard-benchmark.md">Metode, data, dan batasan</a></sub>
</p>

<p align="center">
  <sub>Baca bersama ini: satu tugas kecil, tiga sesi per kondisi uji, satu model. Pemeriksaan dari luar cakupannya lebih sempit daripada prompt. Puncak memori lebih tinggi: 375 MB dibanding 270 MB. Build Simplicio dikompilasi dari commit rilis, dengan fitur masuk dimatikan.</sub>
</p>

<p align="center">Cara Simplicio mencapai hasil ini tidak dipublikasikan. Pengukurannya dipublikasikan, termasuk yang Simplicio kalah.</p>

<p align="center">
  <b>Coba:</b> <a href="#install">Instal</a> · <a href="#first-run">Penggunaan pertama</a><br>
  <a href="#what-simplicio-is">Apa itu</a> ·
  <a href="#the-measurement">Pengukuran</a> ·
  <a href="#works-with-the-agent-you-already-use">Agen</a> ·
  <a href="#command-line">Perintah</a> ·
  <a href="#safety-and-privacy">Privasi</a> ·
  <a href="#questions-people-ask">Pertanyaan</a> ·
  <a href="#documentation-and-community">Dokumentasi</a>
</p>

<a id="what-simplicio-is"></a>

## Apa itu Simplicio

Simplicio adalah program lokal yang memberi agen pemrograman yang sudah Anda pakai sebuah mode super cepat, apa pun agen dan apa pun modelnya. Angka di halaman ini berasal dari satu agen dan satu model; bagian di bawah menjelaskan dengan tepat apa yang diukur.

- **Anda tetap memakai agen dan model Anda.** Simplicio tidak menggantikan Claude Code, Codex, Cursor, atau model apa pun yang ada di baliknya.
- **Anda memasang satu biner native yang ditandatangani.** Penginstal memverifikasi tanda tangannya, lalu mendaftarkan Simplicio di agen-agen yang ditemukannya di mesin Anda.
- **Simplicio berjalan di mesin Anda.** Agen Anda menjalankannya sebagai server MCP STDIO lokal. MCP adalah Model Context Protocol, cara standar agen pemrograman memanggil alat dari luar. STDIO berarti agen menjalankan program itu sendiri dan berbicara dengannya lewat standard input dan standard output-nya.
- **Simplicio memberi agen Anda alat.** Peta repositori, konteks terbatas, suntingan terstruktur, dan pemeriksaan. [Alat inti](#works-with-the-agent-you-already-use) dicantumkan di bawah.
- **Yang berubah adalah sesinya.** Berapa lama waktunya dan berapa biayanya. Bagian berikutnya menunjukkan seberapa besar perubahannya, dan di mana Simplicio tidak membantu.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/diagram-where-simplicio-runs-dark.svg">
    <img src="../assets/diagram-where-simplicio-runs-light.svg" width="840" alt="Diagram. Di mesin Anda: Anda, agen pemrograman Anda, Simplicio, dan repositori Anda. Agen berbicara dengan Simplicio lewat STDIO lokal (MCP). Agen berbicara dengan penyedia model Anda seperti biasa. Simplicio berbicara dengan SimpleTI untuk masuk dan pemeriksaan paket, dan dengan GitHub untuk pemeriksaan rilis, tanpa konten repositori di keduanya.">
  </picture>
</p>

<p align="center">
  <sub>Gambar ini menunjukkan apa yang terjadi secara default. Daftar lengkapnya, termasuk fitur yang menjangkau layanan lain, ada di <a href="#safety-and-privacy">Apa yang dikirim Simplicio, dan ke mana</a> pada bagian Keamanan dan privasi.</sub>
</p>

<a id="the-measurement"></a>

## Pengukuran

Satu tugas, dijalankan dengan cara yang sama dengan dan tanpa Simplicio. Tugasnya adalah satu sesi agen dengan tiga langkah dalam percakapan yang sama:

1. Buat daftar pengguna: sebuah API dan halaman dengan tabel, pencarian, dan pengurutan.
2. Ubah: hapus satu kolom, tambahkan filter berdasarkan peran, dan tambahkan kolom tanggal.
3. Tambahkan pendaftaran sederhana: endpoint `POST` yang memeriksa masukannya, dan halaman formulir.

Setelah setiap langkah, hasilnya diperiksa dari luar sesi. API dipanggil lewat HTTP, dan halaman dimuat di Chrome tanpa antarmuka, yaitu Chrome tanpa jendela. Setiap kondisi uji memakai agen dan model yang sama: Claude Code 2.1.330 dengan Claude Haiku 5.5. Garis dasarnya adalah Claude Code 2.1.330 dengan alatnya sendiri, tanpa server MCP dan tanpa konfigurasi Simplicio. Pemeriksaan tidak menguji kotak pencarian, pengurutan, pengalihan setelah menyimpan, tampilan halaman, atau kualitas kode.

Setiap sesi ada di grafik ini, tidak hanya median-nya.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-sessions-dark.svg">
    <img src="../assets/benchmark-2026-11-22-sessions-light.svg" width="840" alt="Diagram sebar dari setiap sesi, dengan waktu untuk seluruh tugas di sumbu mendatar dan biaya yang dilaporkan agen di sumbu tegak. Simplicio 3.15.0, berlian hijau: 23 sampai 27 s dan $0.0071 sampai $0.0098. Simplicio 3.14.0, kotak abu-abu: 90 sampai 106 s dan $0.0214 sampai $0.0249. Tanpa Simplicio, lingkaran kosong: 97 sampai 172 s dan $0.0186 sampai $0.0280.">
  </picture>
</p>

Median dari 3 sesi per kondisi uji. Garis kecil di bawah setiap nilai menunjukkan sesi terendah dan tertinggi.

| Ukuran | Tanpa Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| Waktu tugas | 121 s<br><sub>97–172</sub> | 104 s<br><sub>90–106</sub> | **25 s**<br><sub>23–27</sub> |
| Biaya yang dilaporkan | $0.0226<br><sub>0.0186–0.0280</sub> | $0.0220<br><sub>0.0214–0.0249</sub> | **$0.0076**<br><sub>0.0071–0.0098</sub> |
| Permintaan ke model | 25<br><sub>19–33</sub> | 18<br><sub>18–22</sub> | **10**<br><sub>10–10</sub> |
| Pemanggilan alat | 22<br><sub>16–30</sub> | 15<br><sub>15–19</sub> | **7**<br><sub>7–7</sub> |
| Token keluaran | 18,162<br><sub>15,599–23,328</sub> | 19,722<br><sub>18,764–24,997</sub> | **3,211**<br><sub>3,068–3,573</sub> |
| Token masukan | 34,691<br><sub>30,447–42,543</sub> | 34,141<br><sub>33,121–40,017</sub> | 18,755<br><sub>18,466–33,300</sub> |
| Waktu CPU | 8.5 s<br><sub>8.5–9.2</sub> | 10.0 s<br><sub>8.9–10.0</sub> | **5.3 s**<br><sub>5.3–5.5</sub> |
| Puncak memori | **270 MB**<br><sub>248–274</sub> | 436 MB<br><sub>432–439</sub> | 375 MB<br><sub>365–379</sub> |
| Langkah yang selesai | 9 dari 9 | 9 dari 9 | 9 dari 9 |

Huruf tebal menandai nilai terbaik dalam satu baris, hanya jika rentangnya tidak tumpang tindih dengan yang lain. Rentang token masukan tumpang tindih, jadi pengukuran ini tidak mengklaim perbedaan token masukan. "9 dari 9" berarti 3 langkah di setiap dari 3 sesi, dan setiap langkah lulus setiap pemeriksaan dari luar. Waktu tugas adalah waktu untuk seluruh tugas. Permintaan ke model adalah satu panggilan ke model, dan pemanggilan alat adalah satu penggunaan alat oleh agen. Biaya yang dilaporkan adalah yang dilaporkan agen: token yang dipakai dikali harga model yang dipublikasikan. Hanya token model yang dihitung. Ini bukan tagihan.

Yang berubah dalam sesi, dihitung: model membuat lebih sedikit permintaan, dan agen membuat lebih sedikit pemanggilan alat.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-work-dark.svg">
    <img src="../assets/benchmark-2026-11-22-work-light.svg" width="840" alt="Diagram unit dengan satu tanda per permintaan ke model atau pemanggilan alat, median dari 3 sesi. Permintaan ke model: 25 tanpa Simplicio, 18 dengan Simplicio 3.14.0 dan 10 dengan Simplicio 3.15.0. Pemanggilan alat: 22, 15 dan 7.">
  </picture>
</p>

Waktu per langkah, pada skala bersama yang sama.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-steps-dark.svg">
    <img src="../assets/benchmark-2026-11-22-steps-light.svg" width="840" alt="Median waktu per langkah pada skala bersama. Langkah 1, membuat: 57.3 s tanpa Simplicio, 53.7 s dengan Simplicio 3.14.0 dan 5.8 s dengan Simplicio 3.15.0. Langkah 2, mengubah: 17.3 s, 15.2 s dan 8.9 s. Langkah 3, mendaftar: 31.4 s, 27.5 s dan 10.3 s.">
  </picture>
</p>

Setiap median dihitung terpisah, jadi langkah-langkahnya tidak menjumlah menjadi median seluruh tugas.

<details>
<summary>Angka lengkap per langkah</summary>

Setiap sel berisi median waktu dan median biaya langkah tersebut:

| Langkah | Tanpa Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. Membuat | 57.3 s / $0.0111 | 53.7 s / $0.0137 | 5.8 s / $0.0022 |
| 2. Mengubah | 17.3 s / $0.0040 | 15.2 s / $0.0032 | 8.9 s / $0.0023 |
| 3. Mendaftar | 31.4 s / $0.0075 | 27.5 s / $0.0056 | 10.3 s / $0.0026 |

</details>

**Cara membacanya.** Rasio dihitung dari median yang belum dibulatkan. Dibanding agen yang sama tanpa Simplicio, seluruh tugas berjalan 4.9 kali lebih cepat dan biayanya sekitar sepertiganya. Dibanding rilis sebelumnya, tugas berjalan 4.2 kali lebih cepat. Dalam sesi, model membuat 10 permintaan alih-alih 25 dan menulis 3,211 token keluaran alih-alih 18,162, dan tugas lulus pemeriksaan dari luar yang sama. Kasus terburuk: sesi tercepat tanpa Simplicio (97.1 s) tetap 3.7 kali lebih lambat daripada sesi paling lambat dengan Simplicio 3.15.0 (26.6 s), dan sesi termurah tanpa Simplicio ($0.0186) tetap berbiaya 1.9 kali lipat dibanding sesi paling mahal dengan Simplicio ($0.0098). Garis dasarnya adalah Claude Code 2.1.330 dengan alatnya sendiri, tanpa server MCP dan tanpa konfigurasi Simplicio. Biaya hanya menghitung token model. Sesi-sesi dijalankan empat sekaligus di satu mesin, jadi bandingkan waktu hanya di dalam putaran ini.

<a id="where-simplicio-does-not-win"></a>

### Di mana Simplicio tidak menang

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-memory-dark.svg">
    <img src="../assets/benchmark-2026-11-22-memory-light.svg" width="840" alt="Puncak memori, median dari 3 sesi: 270 MB tanpa Simplicio, yang paling rendah; 436 MB dengan Simplicio 3.14.0, 61% lebih banyak; 375 MB dengan Simplicio 3.15.0, 39% lebih banyak.">
  </picture>
</p>

- **Memori.** Puncak memori 39% lebih tinggi daripada dengan agen biasa: 375 MB dibanding 270 MB.
- **Rilis sebelumnya tidak menunjukkan keuntungan pada tugas ini.** Simplicio 3.14.0 berbiaya sama dengan tanpa Simplicio, dan selisih waktunya berada dalam sebaran antar-sesi. Keuntungan yang tercatat di halaman ini datang bersama 3.15.0.
- **Satu skrip Python kecil sekali pakai.** Pada putaran sebelumnya, Simplicio 3.10.8 lebih lambat daripada agen biasa dengan setiap model yang dicoba. Pada Claude Sonnet 5.5 di Claude Code, tugas itu memakan 19.6 s dan $0.0548, dibanding 11.4 s dan $0.0283 tanpa Simplicio. Tugas itu belum diukur ulang pada 3.15.0.
- **Yang Anda pasang tidak sama persis dengan yang diukur.** Build dikompilasi dari commit rilis, dengan masuk dimatikan dan proses latar belakang dimatikan. Unduhan yang ditandatangani tidak diukur.
- **Sampelnya kecil.** Tiga sesi per kondisi uji, satu model, satu proyek baru yang kecil, satu mesin, dan empat sesi sekaligus. Baca rasionya sebagai pengukuran tugas ini, bukan janji untuk tugas Anda. Tidak ada sesi dari ketiga kondisi uji ini yang dibuang atau diulang. Kami belum mengukur seberapa banyak pekerjaan Anda yang mirip dengan tugas ini.

### Periksa sendiri

[Laporannya](../benchmarks/2026-11-22-standard-benchmark.md) memuat tiga prompt (dalam bahasa Portugis, dengan terjemahan), deskripsi setiap pemeriksaan dari luar, dan angka per sesi. [Berkas data](../benchmarks/2026-11-22-standard-benchmark.json) memuatnya dalam format JSON. Harness pengujian tidak dipublikasikan. Jalankan tiga prompt yang sama di agen Anda sendiri, dengan Simplicio aktif dan nonaktif, di proyek kecil milik Anda, lalu bandingkan waktu dan tagihan Anda sendiri.

<a id="install"></a>

## Instalasi

Instal biner native yang ditandatangani. Pilih satu jalur.

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows (PowerShell):

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

Python (PyPI):

```bash
python3 -m pip install --upgrade simplicio-installer
simplicio install
```

Di Windows, gunakan `py -m pip install --upgrade simplicio-installer`, lalu `simplicio install`. Jika direktori skrip Python belum ada di `PATH` Anda, tambahkan direktori itu terlebih dahulu.

Penginstal mengunduh rilis bertanda tangan terbaru untuk platform Anda, lalu memeriksa SHA-256 dan tanda tangan Ed25519-nya. Baru setelah itu biner yang terpasang diganti. Biner ditempatkan di `~/.simplicio/bin/` (di Windows, `%USERPROFILE%\.simplicio\bin\`), dan Simplicio didaftarkan secara otomatis di agen-agen yang ditemukan. Kegagalan pendaftaran menghentikan penginstal, alih-alih melaporkan keberhasilan. Mulai ulang agen yang sudah terbuka agar memuat ulang konfigurasinya.

**Masuk.** Masuk dengan Google wajib dilakukan, termasuk selama beta. Jalankan `simplicio auth login`, lalu `simplicio auth status --json`, dan lanjutkan ketika status melaporkan `active: true`. Pendaftaran tidak memerlukan Anda sudah masuk, jadi agen tetap dikonfigurasi bahkan sebelum Anda masuk. Jangan pernah menempelkan kata sandi atau token ke konfigurasi agen.

<details>
<summary>Periksa, perbarui, hapus</summary>

Untuk memperbarui, jalankan penginstal lagi. Anda bisa menjalankan salah satu penginstal lagi kapan saja, dan penginstal akan mengambil rilis terbaru. `install.sh` dan `install.ps1` ada di direktori utama repositori ini.

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

- `--doctor` memeriksa instalasi.
- `--uninstall --keep-data` menghapus biner yang terpasang dan menyimpan data Anda. Data itu mencakup status masuk Google yang berlaku 30 hari di `~/.simplicio/login.json`.
- `--uninstall --purge` hanya menghapus status yang dikelola Simplicio, termasuk status masuk. Ia tetap menyimpan `~/.simplicio/.env`, tempat kredensial penyedia mungkin berada. Purge memerlukan `SIMPLICIO_CONFIRM_PURGE=1`.
- Uninstal tidak mengubah konfigurasi agen Anda. Entri Simplicio tetap ada di setiap agen sampai Anda menghapusnya di pengaturan agen itu sendiri.
- Data di dalam folder `.simplicio` milik proyek tidak dihapus oleh `--keep-data`. Periksa targetnya sebelum memilih `--purge`.

Detail lengkap: [INSTALL.md](../INSTALL.md).

</details>

<a id="first-run"></a>

## Penggunaan pertama

```bash
simplicio version
cd my-project
simplicio onboard
```

`simplicio version` memastikan biner yang terpasang. `simplicio onboard` menyiapkan proyek untuk pertama kalinya. Lalu buka agen Anda di proyek itu dan bekerja seperti biasa. Untuk memastikan Simplicio sudah dimuat, cari `simplicio` di daftar server MCP milik agen. Di Claude Code, `/mcp` menampilkan server yang terhubung. Lebih suka membaca penginstal dulu? Berkasnya [install.sh](../install.sh).

<a id="works-with-the-agent-you-already-use"></a>

## Bekerja dengan agen yang sudah Anda gunakan

Simplicio adalah server MCP STDIO lokal, jadi agen yang bisa menjalankan server MCP lokal dapat diarahkan ke Simplicio.

Penginstal menyerahkan pendaftaran ke registrar milik Simplicio sendiri. Penginstal mendeteksi agen di mesin Anda dan menulis entri Simplicio untuk agen yang bisa dikonfigurasinya, di antaranya Claude Code, Codex, Cursor, Visual Studio Code, OpenCode, Gemini CLI, dan Kiro. Dua berkas di repositori ini menjelaskan sejauh mana setiap integrasi:

- Registri [`plugins/simplicio/host-surfaces.json`](../plugins/simplicio/host-surfaces.json) menyebutkan 43 id agen dan menjelaskan, untuk setiap agen, bagaimana Simplicio menjangkaunya: entri MCP yang ditulis Simplicio (23), plugin atau ekstensi native (5), paket plugin portabel (4), panduan pemasangan yang Anda ikuti sendiri (9), atau alat baris perintah lain (2).
- Matriks kompatibilitas [`docs/hosts/compatibility-matrix.md`](../docs/hosts/compatibility-matrix.md) menjelaskan apa yang sudah diverifikasi. Dari 43 agen itu, 12 ditandai sebagai didukung dan 29 ditandai `unverified`, dan matriks itu tidak punya baris untuk Codex dan Gemini CLI. Jika registri menyatakan Simplicio menulis entri dan matriks menandainya `unverified`, anggap integrasi itu belum diuji.

23 agen punya panduan di [`docs/hosts/`](../docs/hosts/). Untuk agen yang dijangkau lewat plugin, plugin diterapkan dalam langkah terpisah yang meminta persetujuan Anda, dan [INSTALL.md](../INSTALL.md) menjelaskannya.

<details>
<summary>Semua 43 agen, berdasarkan cara Simplicio menjangkaunya</summary>

| Cara Simplicio menjangkaunya | Jumlah | Agen |
|---|---|---|
| Entri MCP yang ditulis Simplicio | 23 | **xAI Grok Build**, MiMo Code, Amp, OpenClaude, Antigravity, **Pi**, **oh-my-pi**, Goose, Auggie, Autohand Code, Charm, Cline, Command Code, Continue, Droid, Kilocode, Kimi, Mistral Vibe, Rovo Dev, **Visual Studio Code**, **Meta Muse Code**, **OpenMausBot**, **OpenMuse (Python)** |
| Plugin atau ekstensi native | 5 | **Claude Code**, Codex, **OpenCode**, Hermes Agent, Gemini CLI |
| Paket plugin portabel | 4 | **Cursor**, GitHub Copilot, **Kiro**, Qwen Code |
| Panduan pemasangan yang Anda ikuti sendiri | 9 | Devin, Codebuff, CopilotKit OpenDots, CopilotKit OpenBot, agentes.chat, OpenAI dots, xAI Grok Bot, Meta Muse app, Cue by Manus |
| Alat baris perintah lain | 2 | **OrcaDev / Orca ADE**, T3 Code |

Huruf tebal: matriks kompatibilitas menandai agen tersebut sebagai didukung.

</details>

Untuk mengulang pendaftaran, jalankan `simplicio mcp register`. Perintah servernya adalah `simplicio serve --mcp --stdio`. Ini adalah alat inti yang didapat agen Anda:

| Alat | Yang Anda dapatkan |
|---|---|
| `simplicio_map` | Peta ringkas repositori, agar agen bisa menemukan jalannya |
| `simplicio_context` | Konteks yang dibutuhkan tugas, dibatasi, alih-alih seluruh berkas |
| `simplicio_edit` | Suntingan berkas terstruktur dari rencana yang sudah disiapkan |
| `simplicio_validate` | Pemeriksaan pipeline, pengujian, dan pengiriman |
| `simplicio_run` | Eksekusi tugas di bawah kendali Simplicio |

Daftar aktualnya adalah apa pun yang dilaporkan server saat mulai. [MCP-CONNECT.md](../MCP-CONNECT.md) menjelaskan alat inti.

<details>
<summary>Konfigurasi manual</summary>

Jika agen Anda belum dikonfigurasi untuk Anda, tambahkan entri ini ke konfigurasi MCP-nya. Ganti path dengan path absolut biner yang terpasang.

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

Codex membaca TOML. Agen menjalankan `command` secara langsung, jadi jangan gunakan `~` dan jangan bergantung pada ekspansi shell. Gunakan garis miring di path Windows, dan ganti nama pengguna contoh dengan nama Anda.

Windows:

```toml
[mcp_servers.simplicio]
command = "C:/Users/YourName/.simplicio/bin/simplicio.exe"
args = ["serve", "--mcp", "--stdio"]
```

macOS:

```toml
[mcp_servers.simplicio]
command = "/Users/your-name/.simplicio/bin/simplicio"
args = ["serve", "--mcp", "--stdio"]
```

Linux:

```toml
[mcp_servers.simplicio]
command = "/home/your-name/.simplicio/bin/simplicio"
args = ["serve", "--mcp", "--stdio"]
```

Lokasi berkas setiap agen: [MCP-CONNECT.md](../MCP-CONNECT.md).

</details>

<a id="command-line"></a>

## Baris perintah

| Perintah | Yang Anda dapatkan |
|---|---|
| `simplicio map --repo . --for-llm markdown` | Peta struktural ringkas repositori, ditulis agar dapat dibaca model |
| `simplicio context --repo .` | Konteks terbatas untuk sebuah tugas |
| `simplicio memory query "query" --json` | Yang sudah diketahui proyek, diambil dari memorinya yang terindeks, dalam format JSON |
| `simplicio edit --plan plan.json --repo .` | Sekumpulan suntingan terstruktur yang sudah disiapkan, diterapkan ke berkas |
| `simplicio run "task" --repo . --agents N` | Eksekusi tugas dengan N agen di bawah kendali Simplicio |
| `simplicio loop` | Pekerjaan yang berjalan dalam putaran sampai konvergen |

Nama yang akan Anda lihat di pesan Simplicio: Mapper mengamati, Fast memproyeksikan atau mengambil, Dev CLI mengedit, Runtime mengatur, dan Loop menuju konvergensi.

<a id="safety-and-privacy"></a>

## Keamanan dan privasi

Bagian ini menjelaskan versi 3.15.0.

**Apa yang dikirim Simplicio, dan ke mana**

- **Tetap di mesin Anda.** Pemetaan, konteks, suntingan, dan pemeriksaan berjalan di dalam biner Simplicio. Hasilnya diserahkan ke agen Anda di mesin yang sama. Apa yang dikirim agen Anda ke penyedia modelnya sendiri ditentukan oleh agen, seperti sebelumnya.
- **Ke SimpleTI (simpleti.com.br).** Hanya untuk masuk dan pemeriksaan paket. Permintaan ini membawa token masuk Anda, versi Simplicio, dan nama host komputer Anda. Pencarian lisensi opsional juga membawa e-mail akun Anda. Balasannya berisi e-mail, nama, dan paket akun Anda. Tidak ada konten repositori: tanpa berkas, tanpa path berkas, tanpa prompt, dan tanpa suntingan.
- **Ke GitHub.** Pemeriksaan latar belakang untuk rilis baru, paling sering sekitar sekali setiap 12 jam. Permintaan ini tidak membawa apa pun tentang Anda atau kode Anda. Atur `SIMPLICIO_DISABLE_AUTO_UPDATE=1` untuk mematikannya. Saat Anda memperbarui, biner baru diunduh dari GitHub, dan SHA-256 serta tanda tangannya diperiksa sebelum menggantikan yang lama.
- **Tanpa analitik.** Simplicio 3.15.0 dan berkas yang dipasangnya ke agen Anda sudah diperiksa untuk hal ini: tidak satu pun mengunggah analitik, laporan crash, atau data penggunaan. Catatan penggunaan dan penghematan berupa berkas lokal. Hook yang dipasang hanya menjalankan program lokal (biner Simplicio dan, untuk plugin opsional, skrip lokal); tidak satu pun dari hook itu menghubungi jaringan.
- **Ke layanan yang Anda konfigurasi.** Penyedia model, GitHub, Jira, pemberi notifikasi chat, atau cache tim menerima apa yang dikirim fitur itu, yang bisa mencakup prompt dan kode. Permintaan ke penyedia model membawa header yang menyebut Simplicio sebagai klien.
- **Dua fitur menjangkau layanan di internet yang terbuka untuk umum tanpa konfigurasi apa pun.** Pencarian web, saat berjalan, mengirim kueri pencarian ke DuckDuckGo kecuali Anda mengonfigurasi layanan pencarian lain. Di chat Simplicio sendiri, pesan yang tampak seperti pertanyaan web bisa menjadi kueri tersebut. Audit keamanan dependensi, saat Anda menjalankannya, mengirim nama dan versi dependensi Anda ke osv.dev. Keduanya tidak mengirim isi berkas.
- **Unduhan.** Penginstal dan jalur pembaruan mengunduh dari GitHub. Beberapa skrip pembantu opsional mengambil alatnya sendiri dari PyPI atau npm saat Anda menjalankannya. Jika plugin agen mulai dan tidak menemukan biner Simplicio, plugin itu mengunduh penginstal resmi dari GitHub, disematkan ke sebuah commit dan diperiksa dengan SHA-256.

**Rilis bertanda tangan.** Setiap rilis mempublikasikan biner-binernya beserta checksum SHA-256, tanda tangan Ed25519, SBOM (daftar isi build), dan provenans build. Penginstal dan jalur pembaruan memeriksa checksum dan tanda tangan sebelum menggantikan biner yang terpasang. Untuk rilis stabil, kontrak membuat tanda tangan yang hilang atau tidak valid, serta checksum yang tidak cocok, langsung dianggap gagal. Kontraknya ada di [docs/UPDATE_SIGNATURE_CONTRACT.md](../docs/UPDATE_SIGNATURE_CONTRACT.md).

**Yang diubah penginstal pada agen Anda.** Penginstal menambahkan entri Simplicio ke konfigurasi MCP agen dan mempertahankan bagian konfigurasi lainnya. Di Claude Code, penginstal juga mengizinkan `mcp__simplicio__*`, sehingga alat Simplicio tidak ditolak dalam mode otomatis. Di agen yang antarmuka hook-nya sudah diverifikasi penginstal, penginstal juga memasang hook Simplicio di sana. [INSTALL.md](../INSTALL.md) menjelaskan apa yang ditulis penginstal, dan panduan tiap agen di [`docs/hosts/`](../docs/hosts/) memberikan detailnya. Uninstal tidak membatalkan entri-entri ini. Bagian Instalasi menjelaskan cara menghapusnya.

## Juga di repositori ini

<details>
<summary>Aplikasi desktop (pratinjau macOS)</summary>

Pratinjau aplikasi Desktop untuk macOS (Apple Silicon) dipublikasikan sebagai [Simplicio-3.8.47-arm64.dmg](https://github.com/simpletibr/simplicio/releases/download/v3.8.47/Simplicio-3.8.47-arm64.dmg). SHA-256-nya ada di [DESKTOP-SHA256SUMS](../DESKTOP-SHA256SUMS), terpisah dari checksum biner Simplicio. DMG tidak punya berkas tanda tangan dan menyertakan biner Simplicio 3.8.47.

- Desktop Windows tidak dipublikasikan. Di Windows, gunakan instalasi baris perintah di atas.
- Penandatanganan Apple Developer ID dan notarisasi belum dilakukan. Paket ini ditandatangani ad-hoc, artinya tanpa sertifikat pengembang Apple, dan penerimaan Gatekeeper tidak diklaim, jadi macOS mungkin memberi peringatan saat Anda membukanya.
- Instalasi baris perintah di atas adalah jalur instalasi publik yang didukung sampai paket Desktop yang ditandatangani dipublikasikan.

Detail: [docs/desktop/RELEASE.md](../docs/desktop/RELEASE.md).

</details>

<details>
<summary>Untuk pengelola: diagram alur yang dihasilkan</summary>

Perintah dan alat yang didokumentasikan di README.md dan MCP-CONNECT.md digambar sebagai satu alur, [docs/flow/simplicio.svg](../docs/flow/simplicio.svg), yang dihasilkan dari satu berkas sumber, `docs/flow/simplicio.flow.json`. Hasilkan ulang dengan `python3 scripts/generate_flow.py` dan periksa penyimpangannya dengan `python3 scripts/generate_flow.py --check`. Kontrak yang menjaganya tetap sejalan dengan halaman ini dan dengan MCP-CONNECT.md adalah `python3 -m pytest tests/test_flow_contract.py -q`. Pemeriksaan impor Langflow adalah `scripts/verify_flow_langflow.py`, yang gagal dalam keadaan tertutup (keluar dengan kode 2, `status=blocked`) saat tidak ada server yang berjalan. Buktinya ada di `docs/flow/evidence/` dan `docs/flow/render/`, dan [docs/flow/README.md](../docs/flow/README.md) memuat persyaratan serta cara mengulanginya.

</details>

<a id="questions-people-ask"></a>

## Pertanyaan yang sering diajukan

**Apakah perbandingannya adil?**<br>
Agen yang sama, model yang sama, tiga prompt yang sama, proyek awal yang sama, dan pemeriksaan dari luar yang sama, dalam satu putaran. Garis dasarnya tidak punya server MCP dan tidak punya konfigurasi Simplicio. Lihat [Di mana Simplicio tidak menang](#where-simplicio-does-not-win) dan [Batasan](../benchmarks/2026-11-22-standard-benchmark.md#limits) pada laporan.

**Apakah saya harus mengubah agen atau model saya?**<br>
Tidak. Simplicio terpasang ke agen yang sudah Anda gunakan. Pada benchmark di atas, setiap kondisi uji memakai agen dan model yang sama.

**Apakah saya akan selalu mendapat angka ini?**<br>
Tidak. Angka itu mengukur satu tugas, dengan satu model, di satu mesin, selama tiga sesi per kondisi uji. Lihat [Di mana Simplicio tidak menang](#where-simplicio-does-not-win), dan jalankan perbandingan pada pekerjaan Anda sendiri.

**Apakah ini open source?**<br>
Tidak. Simplicio bersifat proprietary. Ia berupa biner yang ditandatangani, dipublikasikan sebagai aset rilis, dan sumbernya tidak publik. Repositori ini berisi penginstal, paket untuk agen, sumber aplikasi Desktop, dokumentasi, dan data benchmark.

**Bagaimana cara menghapusnya?**<br>
Jalankan `sh install.sh --uninstall --keep-data`, atau `pwsh install.ps1 -Uninstall -KeepData` di Windows. Perintah ini menghapus biner dan menyimpan data Anda. Perintah ini tidak mengubah konfigurasi agen Anda, jadi hapus entri Simplicio di pengaturan masing-masing agen. [Instalasi](#install) memuat detailnya dan opsi purge.

**Apakah saya perlu akun?**<br>
Ya. Masuk dengan Google wajib dilakukan, termasuk selama beta. Jalankan `simplicio auth login`.

**Apakah kode saya keluar dari mesin saya?**<br>
Pemetaan, konteks, suntingan, dan pemeriksaan berjalan di mesin Anda. Simplicio berbicara dengan SimpleTI untuk masuk dan pemeriksaan paket, serta dengan GitHub untuk mencari pembaruan, tanpa konten repositori di keduanya. Fitur yang Anda konfigurasi atau jalankan bisa menjangkau layanan lain. Daftar lengkapnya ada di [Apa yang dikirim Simplicio, dan ke mana](#safety-and-privacy).

<a id="documentation-and-community"></a>

## Dokumentasi dan komunitas

- **Situs web:** [simpleti.com.br/simplicio](https://simpleti.com.br/simplicio/)
- **Dokumentasi:** [simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)
- **Discord:** [Bergabung dengan komunitas](https://discord.gg/wM6tr7xVb)
- **Issues:** [pelacak issue GitHub](https://github.com/simpletibr/simplicio/issues)
- **Di repositori ini:** [INSTALL.md](../INSTALL.md), [MCP-CONNECT.md](../MCP-CONNECT.md), dan [docs/hosts/](../docs/hosts/)
- **Terkait:** Simplicio Video (hypit). Untuk mengkloningnya: `git clone https://github.com/hypit-ai/hypit.git simplicio-video`

<p align="center">
  <sub>© 2026 SimpleTI. Simplicio adalah perangkat lunak proprietary yang terdaftar. Seluruh hak dilindungi.</sub>
</p>
