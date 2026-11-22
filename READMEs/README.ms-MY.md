<div align="center">

<img src="../assets/simplicio-icon-192.png" alt="Logo Simplicio" width="96" height="96">

<h1>Simplicio</h1>

<p><b>UltraFast Mode for all.</b></p>

<p><b>Ejen yang sama, model yang sama, tugasan yang sama: 121&nbsp;s&nbsp;→&nbsp;25&nbsp;s, dan $0.0226&nbsp;→&nbsp;$0.0076.</b></p>

<p>Tanpa Simplicio → dengan Simplicio 3.15.0. Median bagi 3 larian satu tugasan pengekodan kecil dalam Claude Code dengan Claude Haiku 5.5.</p>

<p>Simplicio berjalan pada mesin anda dan menambah alat kepada ejen pengekodan yang sudah anda gunakan.</p>

<p>
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=2fe6a0&label=release" alt="Keluaran terkini"></a>
  <a href="https://simpleti.com.br/simplicio/docs"><img src="https://img.shields.io/badge/docs-simpleti.com.br-ffd23f" alt="Dokumentasi"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Bintang"></a>
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="Lesen: proprietari">
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
  <a href="README.id-ID.md">Bahasa Indonesia</a> ·
  Bahasa Melayu
</p>

<p align="center"><sub>Fail ini ialah terjemahan daripada <a href="../README.md">README Bahasa Inggeris</a>. Jika kedua-duanya berbeza, halaman Bahasa Inggeris ialah rujukan. Rajah dan carta kekal dalam Bahasa Inggeris.</sub></p>

</div>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-dark.svg">
    <img src="../assets/benchmark-2026-11-22-light.svg" width="840" alt="Carta bar yang membandingkan persediaan tanpa Simplicio, Simplicio 3.14.0 dan Simplicio 3.15.0 pada tiga ukuran, median bagi tiga sesi setiap satu. Masa untuk keseluruhan tugasan: 121 s tanpa Simplicio, 104 s dengan Simplicio 3.14.0 dan 25 s dengan Simplicio 3.15.0. Kos: $0.0226, $0.0220 dan $0.0076. Token output: 18,162, 19,722 dan 3,211.">
  </picture>
</p>

<p align="center">
  <sub>Median bagi 3 sesi untuk setiap persediaan (tanpa Simplicio, Simplicio 3.14.0 dan Simplicio 3.15.0). Claude Haiku 5.5 dalam Claude Code 2.1.330, 2026-11-22. Setiap persediaan menyiapkan 9 daripada 9 langkah. Garis nipis pada setiap bar merentang dari sesi terendah hingga sesi tertinggi.<br>
  <a href="../benchmarks/2026-11-22-standard-benchmark.md">Kaedah, data dan had</a></sub>
</p>

<p align="center">
  <sub>Baca bersama ini: satu tugasan kecil, tiga sesi bagi setiap persediaan, satu model. Skop semakan luaran lebih sempit daripada apa yang diminta gesaan. Memori puncak lebih tinggi: 375 MB berbanding 270 MB. Binaan Simplicio dikompil daripada commit keluaran, dengan log masuk dimatikan.</sub>
</p>

<p align="center">Cara Simplicio mencapai hasil ini tidak diterbitkan. Pengukurannya diterbitkan, termasuk yang Simplicio kalah.</p>

<p align="center">
  <b>Cuba:</b> <a href="#install">Pemasangan</a> · <a href="#first-run">Larian pertama</a><br>
  <a href="#what-simplicio-is">Apa ia</a> ·
  <a href="#the-measurement">Pengukuran</a> ·
  <a href="#works-with-the-agent-you-already-use">Ejen</a> ·
  <a href="#command-line">Arahan</a> ·
  <a href="#safety-and-privacy">Privasi</a> ·
  <a href="#questions-people-ask">Soalan</a> ·
  <a href="#documentation-and-community">Dokumen</a>
</p>

<a id="what-simplicio-is"></a>

## Apa itu Simplicio

Simplicio ialah program tempatan yang memberi ejen pengekodan yang sudah anda gunakan satu mod super pantas, walau apa pun ejennya dan walau apa pun modelnya. Angka dalam halaman ini datang daripada satu ejen dan satu model; bahagian di bawah menyatakan dengan tepat apa yang diukur.

- **Anda kekalkan ejen dan model anda.** Simplicio tidak menggantikan Claude Code, Codex, Cursor atau apa-apa model yang berada di sebalik mereka.
- **Anda memasang satu binari natif yang ditandatangani.** Pemasang mengesahkan tandatangan, kemudian mendaftarkan Simplicio dalam ejen yang dijumpainya pada mesin anda.
- **Ia berjalan pada mesin anda.** Ejen anda memulakannya sebagai pelayan MCP STDIO tempatan. MCP ialah Model Context Protocol, cara piawai ejen pengekodan memanggil alat luaran. STDIO bermakna ejen itu sendiri melancarkan program dan berkomunikasi dengannya melalui input dan output piawai.
- **Ia memberi ejen anda alat.** Peta repositori, konteks terhad, suntingan berstruktur dan semakan. [Alat teras](#works-with-the-agent-you-already-use) disenaraikan di bawah.
- **Yang berubah ialah sesi.** Berapa lama ia mengambil masa dan berapa kosnya. Bahagian seterusnya menunjukkan dengan berapa banyak, dan di mana ia tidak membantu.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/diagram-where-simplicio-runs-dark.svg">
    <img src="../assets/diagram-where-simplicio-runs-light.svg" width="840" alt="Rajah. Pada mesin anda: anda, ejen pengekodan anda, Simplicio dan repositori anda. Ejen berkomunikasi dengan Simplicio melalui STDIO (MCP) tempatan. Ejen berkomunikasi dengan penyedia model anda seperti sebelum ini. Simplicio berkomunikasi dengan SimpleTI untuk semakan log masuk dan pelan, dan dengan GitHub untuk semakan keluaran, dengan tiada kandungan repositori dalam kedua-duanya.">
  </picture>
</p>

<p align="center">
  <sub>Gambar ini menunjukkan apa yang berlaku secara lalai. Senarai lengkap, termasuk ciri yang sampai ke perkhidmatan lain, ada dalam <a href="#safety-and-privacy">Apa yang Simplicio hantar, dan kepada siapa</a> di bawah Keselamatan dan privasi.</sub>
</p>

<a id="the-measurement"></a>

## Pengukuran

Satu tugasan, dijalankan dengan cara yang sama sama ada dengan atau tanpa Simplicio. Tugasan itu ialah satu sesi ejen dengan tiga langkah dalam perbualan yang sama:

1. Bina senarai pengguna: satu API dan satu halaman dengan jadual, carian dan pengisihan.
2. Ubah suai: buang satu lajur, tambah penapis mengikut peranan dan satu lajur tarikh.
3. Tambah pendaftaran ringkas: satu titik akhir `POST` yang menyemak input, dan satu halaman borang.

Selepas setiap langkah, hasilnya disemak dari luar sesi. API dipanggil melalui HTTP dan halaman dimuatkan dalam Chrome mod headless, iaitu Chrome tanpa tetingkap. Setiap persediaan menggunakan ejen dan model yang sama: Claude Code 2.1.330 dengan Claude Haiku 5.5. Garis dasar ialah Claude Code 2.1.330 dengan alatnya sendiri, tanpa pelayan MCP dan tanpa konfigurasi Simplicio. Semakan tidak menguji kotak carian, pengisihan, ubah hala selepas menyimpan, rupa halaman atau kualiti kod.

Setiap sesi ada dalam carta ini, bukan median sahaja.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-sessions-dark.svg">
    <img src="../assets/benchmark-2026-11-22-sessions-light.svg" width="840" alt="Plot serakan bagi setiap sesi, dengan masa untuk keseluruhan tugasan pada paksi mendatar dan kos yang dilaporkan oleh ejen pada paksi menegak. Simplicio 3.15.0, berlian hijau: 23 hingga 27 s dan $0.0071 hingga $0.0098. Simplicio 3.14.0, segi empat kelabu: 90 hingga 106 s dan $0.0214 hingga $0.0249. Tanpa Simplicio, bulatan berongga: 97 hingga 172 s dan $0.0186 hingga $0.0280.">
  </picture>
</p>

Median bagi 3 sesi untuk setiap persediaan. Garis kecil di bawah setiap nilai ialah sesi terendah dan tertinggi.

| Ukuran | Tanpa Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| Masa tugasan | 121 s<br><sub>97–172</sub> | 104 s<br><sub>90–106</sub> | **25 s**<br><sub>23–27</sub> |
| Kos dilaporkan | $0.0226<br><sub>0.0186–0.0280</sub> | $0.0220<br><sub>0.0214–0.0249</sub> | **$0.0076**<br><sub>0.0071–0.0098</sub> |
| Permintaan model | 25<br><sub>19–33</sub> | 18<br><sub>18–22</sub> | **10**<br><sub>10–10</sub> |
| Panggilan alat | 22<br><sub>16–30</sub> | 15<br><sub>15–19</sub> | **7**<br><sub>7–7</sub> |
| Token output | 18,162<br><sub>15,599–23,328</sub> | 19,722<br><sub>18,764–24,997</sub> | **3,211**<br><sub>3,068–3,573</sub> |
| Token input | 34,691<br><sub>30,447–42,543</sub> | 34,141<br><sub>33,121–40,017</sub> | 18,755<br><sub>18,466–33,300</sub> |
| Masa CPU | 8.5 s<br><sub>8.5–9.2</sub> | 10.0 s<br><sub>8.9–10.0</sub> | **5.3 s**<br><sub>5.3–5.5</sub> |
| Memori puncak | **270 MB**<br><sub>248–274</sub> | 436 MB<br><sub>432–439</sub> | 375 MB<br><sub>365–379</sub> |
| Langkah disiapkan | 9 daripada 9 | 9 daripada 9 | 9 daripada 9 |

Huruf tebal menandakan nilai terbaik dalam setiap baris, hanya bagi nilai yang julatnya tidak bertindih dengan nilai lain. Julat token input bertindih, jadi larian ini tidak mendakwa sebarang perbezaan dalam token input. "9 daripada 9" bermaksud 3 langkah dalam setiap 3 sesi, dan setiap langkah lulus setiap semakan luaran. Masa tugasan ialah masa untuk keseluruhan tugasan. Permintaan model ialah satu panggilan kepada model, dan panggilan alat ialah satu penggunaan alat oleh ejen. Kos dilaporkan ialah apa yang dilaporkan oleh ejen: token yang digunakan didarab dengan harga model yang diterbitkan. Ia hanya mengira token model. Ia bukan invois.

Apa yang berubah dalam sesi, mengikut kiraan: model membuat lebih sedikit permintaan, dan ejen membuat lebih sedikit panggilan alat.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-work-dark.svg">
    <img src="../assets/benchmark-2026-11-22-work-light.svg" width="840" alt="Carta unit dengan satu tanda bagi setiap permintaan model atau panggilan alat, median bagi 3 sesi. Permintaan model: 25 tanpa Simplicio, 18 dengan Simplicio 3.14.0 dan 10 dengan Simplicio 3.15.0. Panggilan alat: 22, 15 dan 7.">
  </picture>
</p>

Masa mengikut langkah, pada satu skala yang sama.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-steps-dark.svg">
    <img src="../assets/benchmark-2026-11-22-steps-light.svg" width="840" alt="Median masa mengikut langkah pada satu skala yang sama. Langkah 1, bina: 57.3 s tanpa Simplicio, 53.7 s dengan Simplicio 3.14.0 dan 5.8 s dengan Simplicio 3.15.0. Langkah 2, ubah: 17.3 s, 15.2 s dan 8.9 s. Langkah 3, daftar: 31.4 s, 27.5 s dan 10.3 s.">
  </picture>
</p>

Setiap median diambil secara berasingan, jadi langkah-langkah itu tidak menjumlah kepada median keseluruhan tugasan.

<details>
<summary>Nombor tepat mengikut langkah</summary>

Setiap sel ialah median masa dan median kos bagi langkah itu:

| Langkah | Tanpa Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. Bina | 57.3 s / $0.0111 | 53.7 s / $0.0137 | 5.8 s / $0.0022 |
| 2. Ubah | 17.3 s / $0.0040 | 15.2 s / $0.0032 | 8.9 s / $0.0023 |
| 3. Daftar | 31.4 s / $0.0075 | 27.5 s / $0.0056 | 10.3 s / $0.0026 |

</details>

**Cara membaca.** Nisbah diambil daripada median sebelum pembundaran. Berbanding ejen yang sama tanpa Simplicio, keseluruhan tugasan berjalan 4.9 kali lebih pantas dan kosnya kira-kira sepertiga. Berbanding keluaran sebelumnya, ia berjalan 4.2 kali lebih pantas. Dalam sesi, model membuat 10 permintaan dan bukannya 25, serta menulis 3,211 token output dan bukannya 18,162, dan tugasan itu lulus semakan luaran yang sama. Kes terburuk: sesi paling pantas tanpa Simplicio (97.1 s) masih 3.7 kali lebih perlahan daripada sesi paling perlahan dengan Simplicio 3.15.0 (26.6 s), dan sesi paling murah tanpanya ($0.0186) masih berharga 1.9 kali ganda sesi paling mahal dengannya ($0.0098). Garis dasar ialah Claude Code 2.1.330 dengan alatnya sendiri, tanpa pelayan MCP dan tanpa konfigurasi Simplicio. Kos hanya mengira token model. Sesi dijalankan empat pada satu masa pada satu mesin, jadi bandingkan masa hanya dalam pusingan ini.

<a id="where-simplicio-does-not-win"></a>

### Di mana Simplicio tidak menang

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-memory-dark.svg">
    <img src="../assets/benchmark-2026-11-22-memory-light.svg" width="840" alt="Memori puncak, median bagi 3 sesi: 270 MB tanpa Simplicio, paling rendah; 436 MB dengan Simplicio 3.14.0, 61% lebih; 375 MB dengan Simplicio 3.15.0, 39% lebih.">
  </picture>
</p>

- **Memori.** Memori puncak 39% lebih tinggi daripada ejen biasa: 375 MB berbanding 270 MB.
- **Keluaran sebelumnya tidak menunjukkan peningkatan pada tugasan ini.** Simplicio 3.14.0 berharga sama dengan tanpa Simplicio, dan perbezaan masanya berada dalam julat variasi antara larian. Peningkatan yang dipaparkan di halaman ini datang bersama 3.15.0.
- **Skrip Python pendek untuk sekali guna.** Dalam pusingan sebelumnya, Simplicio 3.10.8 lebih perlahan daripada ejen biasa dengan setiap model yang diuji. Pada Claude Sonnet 5.5 dalam Claude Code ia mengambil 19.6 s dan $0.0548, berbanding 11.4 s dan $0.0283 tanpanya. Tugasan itu belum diukur semula pada 3.15.0.
- **Apa yang anda pasang tidak sama tepat dengan apa yang diukur.** Binari dikompil daripada commit keluaran, dengan log masuk dimatikan dan proses latar belakang dimatikan. Muat turun yang ditandatangani tidak diukur.
- **Sampel ini kecil.** Tiga sesi bagi setiap persediaan, satu model, satu projek baharu yang kecil, satu mesin, empat sesi serentak. Baca nisbah sebagai ukuran bagi tugasan ini, bukan sebagai janji untuk tugasan anda. Tiada sesi daripada tiga persediaan ini digugurkan atau dijalankan semula. Kami belum mengukur berapa banyak kerja anda menyerupai tugasan ini.

### Semak sendiri

[Laporan](../benchmarks/2026-11-22-standard-benchmark.md) menerbitkan ketiga-tiga gesaan (dalam Bahasa Portugis, dengan terjemahan), penerangan setiap semakan luaran dan nombor bagi setiap sesi; [fail data](../benchmarks/2026-11-22-standard-benchmark.json) menyimpannya dalam format JSON. Rangka kerja ujian tidak diterbitkan. Jalankan tiga gesaan yang sama dalam ejen anda sendiri dengan Simplicio dihidupkan dan dimatikan, dalam projek kecil anda sendiri, dan bandingkan masa dan bil anda sendiri.

<a id="install"></a>

## Pemasangan

Pasang binari natif yang ditandatangani. Pilih satu laluan.

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

Pada Windows, gunakan `py -m pip install --upgrade simplicio-installer` kemudian `simplicio install`. Jika direktori skrip Python tidak berada dalam `PATH` anda, tambahkannya dahulu.

Pemasang memuat turun keluaran bertandatangan terkini untuk platform anda dan menyemak SHA-256 dan tandatangan Ed25519-nya. Barulah ia menggantikan binari yang dipasang. Ia meletakkan binari di bawah `~/.simplicio/bin/` (pada Windows, `%USERPROFILE%\.simplicio\bin\`) dan secara automatik mendaftarkan Simplicio dalam ejen yang dijumpainya. Kegagalan pendaftaran menghentikan pemasang dan tidak melaporkan kejayaan. Mulakan semula mana-mana ejen yang sudah terbuka supaya ia memuat semula konfigurasinya.

**Log masuk.** Log masuk Google diperlukan, termasuk semasa beta. Jalankan `simplicio auth login`, kemudian `simplicio auth status --json`, dan teruskan apabila status melaporkan `active: true`. Pendaftaran tidak memerlukan anda log masuk, jadi ejen dikonfigurasikan walaupun sebelum anda log masuk. Jangan sekali-kali tampal kata laluan atau token ke dalam konfigurasi ejen.

<details>
<summary>Semak, kemas kini, nyahpasang</summary>

Untuk mengemas kini, jalankan pemasang sekali lagi. Anda boleh menjalankan mana-mana pemasang sekali lagi pada bila-bila masa, dan ia akan mendapatkan keluaran terkini. `install.sh` dan `install.ps1` terdapat di akar repositori ini.

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

- `--doctor` menyemak pemasangan.
- `--uninstall --keep-data` mengeluarkan binari yang dipasang dan menyimpan data anda. Ini termasuk keadaan log masuk Google 30 hari dalam `~/.simplicio/login.json`.
- `--uninstall --purge` hanya mengeluarkan keadaan yang diurus oleh Simplicio, termasuk keadaan log masuk. Ia mengekalkan `~/.simplicio/.env`, tempat kelayakan penyedia mungkin disimpan. Pembersihan penuh memerlukan `SIMPLICIO_CONFIRM_PURGE=1`.
- Nyahpasang tidak mengubah konfigurasi ejen anda. Entri Simplicio kekal dalam setiap ejen sehingga anda membuangnya dalam tetapan ejen itu sendiri.
- Data dalam folder `.simplicio` milik projek tidak dikeluarkan oleh `--keep-data`. Semak sasaran sebelum anda memilih `--purge`.

Butiran penuh: [INSTALL.md](../INSTALL.md).

</details>

<a id="first-run"></a>

## Larian pertama

```bash
simplicio version
cd my-project
simplicio onboard
```

`simplicio version` mengesahkan binari yang dipasang. `simplicio onboard` menyediakan projek buat kali pertama. Kemudian buka ejen anda dalam projek itu dan bekerja seperti biasa. Untuk mengesahkan bahawa Simplicio sudah dimuatkan, cari `simplicio` dalam senarai pelayan MCP ejen. Dalam Claude Code, `/mcp` menyenaraikan pelayan yang bersambung. Lebih suka membaca pemasang dahulu? Ia ialah [install.sh](../install.sh).

<a id="works-with-the-agent-you-already-use"></a>

## Berfungsi dengan ejen yang anda sudah gunakan

Simplicio ialah pelayan MCP STDIO tempatan, jadi mana-mana ejen yang boleh memulakan pelayan MCP tempatan boleh diarahkan kepadanya.

Pemasang menyerahkan pendaftaran kepada pendaftar Simplicio sendiri. Ia mengesan ejen pada mesin anda dan menulis entri Simplicio untuk ejen yang ia tahu cara mengkonfigurasinya, antaranya Claude Code, Codex, Cursor, Visual Studio Code, OpenCode, Gemini CLI dan Kiro. Dua fail dalam repositori ini menyatakan sejauh mana setiap integrasi berjalan:

- Registri [`plugins/simplicio/host-surfaces.json`](../plugins/simplicio/host-surfaces.json) menamakan 43 id ejen dan menyatakan, bagi setiap satu, cara Simplicio sampai kepadanya: entri MCP yang Simplicio tulis (23), plugin atau sambungan natif (5), pakej plugin mudah alih (4), persediaan berpandu yang anda ikuti sendiri (9), atau alat baris arahan lain (2).
- Matriks keserasian [`docs/hosts/compatibility-matrix.md`](../docs/hosts/compatibility-matrix.md) menyatakan apa yang telah disahkan. Daripada 43 ejen itu, ia menandakan 12 ejen sebagai disokong dan 29 sebagai `unverified`, dan ia tidak mempunyai baris untuk Codex dan Gemini CLI. Di tempat registri menyatakan Simplicio menulis entri dan matriks menyatakan `unverified`, anggap integrasi itu belum diuji.

23 ejen mempunyai panduan dalam [`docs/hosts/`](../docs/hosts/). Bagi ejen yang dicapai melalui plugin, plugin itu digunakan dalam langkah berasingan yang meminta persetujuan anda, dan [INSTALL.md](../INSTALL.md) menerangkannya.

<details>
<summary>Semua 43 ejen, mengikut cara Simplicio sampai kepadanya</summary>

| Cara Simplicio sampai kepadanya | Bilangan | Ejen |
|---|---|---|
| Entri MCP yang Simplicio tulis | 23 | **xAI Grok Build**, MiMo Code, Amp, OpenClaude, Antigravity, **Pi**, **oh-my-pi**, Goose, Auggie, Autohand Code, Charm, Cline, Command Code, Continue, Droid, Kilocode, Kimi, Mistral Vibe, Rovo Dev, **Visual Studio Code**, **Meta Muse Code**, **OpenMausBot**, **OpenMuse (Python)** |
| Plugin atau sambungan natif | 5 | **Claude Code**, Codex, **OpenCode**, Hermes Agent, Gemini CLI |
| Pakej plugin mudah alih | 4 | **Cursor**, GitHub Copilot, **Kiro**, Qwen Code |
| Persediaan berpandu yang anda ikuti sendiri | 9 | Devin, Codebuff, CopilotKit OpenDots, CopilotKit OpenBot, agentes.chat, OpenAI dots, xAI Grok Bot, Meta Muse app, Cue by Manus |
| Alat baris arahan lain | 2 | **OrcaDev / Orca ADE**, T3 Code |

Tebal: matriks keserasian menandakan ejen itu sebagai disokong.

</details>

Untuk mengulang pendaftaran, jalankan `simplicio mcp register`. Arahan pelayan ialah `simplicio serve --mcp --stdio`. Ini ialah alat teras yang diterima oleh ejen anda:

| Alat | Apa yang diberikannya kepada anda |
|---|---|
| `simplicio_map` | Peta ringkas repositori, supaya ejen dapat mencari jalannya |
| `simplicio_context` | Konteks yang diperlukan tugasan, terhad, dan bukannya keseluruhan fail |
| `simplicio_edit` | Suntingan fail berstruktur daripada pelan yang disediakan |
| `simplicio_validate` | Semakan saluran paip, ujian dan penghantaran |
| `simplicio_run` | Larian tugasan di bawah kawalan Simplicio |

Senarai langsung ialah apa sahaja yang dilaporkan pelayan semasa permulaan. [MCP-CONNECT.md](../MCP-CONNECT.md) menerangkan alat teras.

<details>
<summary>Konfigurasi manual</summary>

Jika ejen anda tidak dikonfigurasikan untuk anda, tambahkan entri ini ke dalam konfigurasi MCP-nya. Gantikan laluan dengan laluan mutlak binari yang dipasang.

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

Codex membaca TOML. Ejen memulakan `command` secara terus, jadi jangan gunakan `~` dan jangan bergantung pada pengembangan shell. Gunakan garis condong ke hadapan dalam laluan Windows, dan gantikan nama pengguna contoh.

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

Tempat setiap ejen menyimpan failnya: [MCP-CONNECT.md](../MCP-CONNECT.md).

</details>

<a id="command-line"></a>

## Baris arahan

| Arahan | Apa yang anda dapat |
|---|---|
| `simplicio map --repo . --for-llm markdown` | Peta struktur ringkas repositori, ditulis untuk dibaca oleh model |
| `simplicio context --repo .` | Konteks terhad untuk satu tugasan |
| `simplicio memory query "query" --json` | Apa yang sudah diketahui projek, diingat semula daripada memori berindeks, dalam format JSON |
| `simplicio edit --plan plan.json --repo .` | Set suntingan berstruktur yang disediakan, digunakan pada fail |
| `simplicio run "task" --repo . --agents N` | Larian tugasan dengan N ejen di bawah kawalan Simplicio |
| `simplicio loop` | Kerja yang diteruskan dalam pusingan sehingga menumpu |

Nama yang akan anda lihat dalam mesej Simplicio: Mapper memerhati, Fast mengunjurkan atau mendapatkan semula, Dev CLI menyunting, Runtime mentadbir, dan Loop menumpu.

<a id="safety-and-privacy"></a>

## Keselamatan dan privasi

Bahagian ini menerangkan versi 3.15.0.

**Apa yang Simplicio hantar, dan kepada siapa**

- **Kekal pada mesin anda.** Pemetaan, konteks, suntingan dan semakan dijalankan di dalam binari Simplicio. Ia menyerahkan hasil kepada ejen anda pada mesin yang sama. Apa yang dihantar oleh ejen anda kepada penyedia modelnya sendiri ditentukan oleh ejen itu, seperti sebelum ini.
- **Kepada SimpleTI (simpleti.com.br).** Log masuk dan semakan pelan sahaja. Ia membawa token log masuk anda, versi Simplicio dan nama hos komputer anda. Carian lesen pilihan turut membawa e-mel akaun anda. Ia memulangkan e-mel akaun, nama dan pelan anda. Tiada kandungan repositori: tiada fail, tiada laluan fail, tiada gesaan dan tiada suntingan.
- **Kepada GitHub.** Semakan latar belakang untuk keluaran baharu, paling banyak kira-kira sekali setiap 12 jam. Ia tidak membawa apa-apa tentang anda atau kod anda. Tetapkan `SIMPLICIO_DISABLE_AUTO_UPDATE=1` untuk mematikannya. Apabila anda mengemas kini, binari baharu dimuat turun daripada GitHub, dan SHA-256 serta tandatangannya disemak sebelum ia menggantikan yang lama.
- **Tiada analitik.** Simplicio 3.15.0 dan fail yang dipasangnya ke dalam ejen anda telah disemak untuk perkara ini: tiada satu pun memuat naik analitik, laporan ranap atau data penggunaan. Rekod penggunaan dan penjimatan ialah fail tempatan. Cangkuk (hook) yang dipasangnya hanya menjalankan program tempatan (binari Simplicio dan, bagi plugin pilihan, skrip tempatan); tiada satu pun daripadanya menghubungi rangkaian.
- **Kepada perkhidmatan yang anda konfigurasikan.** Penyedia model, GitHub, Jira, pemberitahu sembang atau cache pasukan menerima apa yang dihantar oleh ciri itu, yang boleh termasuk gesaan dan kod. Permintaan kepada penyedia model membawa pengepala yang menamakan Simplicio sebagai klien.
- **Dua ciri sampai ke perkhidmatan di internet yang terbuka kepada umum tanpa sebarang konfigurasi.** Carian web, apabila ia berjalan, menghantar pertanyaan carian kepada DuckDuckGo melainkan anda mengkonfigurasi perkhidmatan carian lain. Dalam sembang Simplicio sendiri, mesej yang kelihatan seperti soalan web boleh menjadi pertanyaan carian itu. Audit keselamatan kebergantungan, apabila anda menjalankannya, menghantar nama dan versi kebergantungan anda kepada osv.dev. Kedua-duanya tidak menghantar kandungan fail.
- **Muat turun.** Pemasang dan laluan kemas kini memuat turun dari GitHub. Sesetengah skrip pembantu pilihan mengambil alatnya sendiri dari PyPI atau npm apabila anda menjalankannya. Jika plugin ejen dimulakan dan tidak menemui binari Simplicio, ia memuat turun pemasang rasmi dari GitHub, dipinkan pada commit tertentu dan disemak dengan SHA-256.

**Keluaran bertandatangan.** Setiap keluaran menerbitkan binarinya dengan checksum SHA-256, tandatangan Ed25519, SBOM (senarai apa yang ada dalam binaan) dan asal-usul binaan. Pemasang dan laluan kemas kini menyemak checksum dan tandatangan sebelum menggantikan binari yang dipasang. Bagi keluaran stabil, kontrak menjadikan tandatangan yang hilang atau tidak sah serta ketidakpadanan checksum sebagai kegagalan keras. Kontrak itu terdapat dalam [docs/UPDATE_SIGNATURE_CONTRACT.md](../docs/UPDATE_SIGNATURE_CONTRACT.md).

**Apa yang pemasang ubah dalam ejen anda.** Ia menambah entri Simplicio pada konfigurasi MCP ejen dan mengekalkan bahagian konfigurasi yang lain. Dalam Claude Code ia juga membenarkan `mcp__simplicio__*`, jadi alat Simplicio tidak ditolak dalam mod auto. Dalam ejen yang antara muka cangkuknya telah disahkan oleh pemasang, ia turut memasang cangkuk Simplicio di sana. [INSTALL.md](../INSTALL.md) menyatakan apa yang ditulis oleh pemasang, dan panduan setiap ejen dalam [`docs/hosts/`](../docs/hosts/) memberikan butirannya. Nyahpasang tidak membatalkan entri-entri ini. Bahagian Pemasangan menerangkan cara membuangnya.

## Turut ada dalam repositori ini

<details>
<summary>Aplikasi desktop (pratonton macOS)</summary>

Pratonton Desktop macOS (Apple Silicon) diterbitkan sebagai [Simplicio-3.8.47-arm64.dmg](https://github.com/simpletibr/simplicio/releases/download/v3.8.47/Simplicio-3.8.47-arm64.dmg). SHA-256-nya terdapat dalam [DESKTOP-SHA256SUMS](../DESKTOP-SHA256SUMS), berasingan daripada checksum binari Simplicio. DMG itu tidak mempunyai fail tandatangan dan mengandungi binari Simplicio 3.8.47.

- Desktop Windows tidak diterbitkan. Pada Windows, gunakan pemasangan baris arahan di atas.
- Penandatanganan Apple Developer ID dan notarisasi tidak dilakukan. Pakej itu ditandatangani ad-hoc, iaitu tanpa sijil pembangun Apple, dan penerimaan Gatekeeper tidak didakwa, jadi macOS mungkin memberi amaran apabila anda membukanya.
- Pemasangan baris arahan di atas ialah laluan pemasangan awam yang disokong sehingga pakej Desktop yang ditandatangani diterbitkan.

Butiran: [docs/desktop/RELEASE.md](../docs/desktop/RELEASE.md).

</details>

<details>
<summary>Untuk penyelenggara: rajah aliran yang dijana</summary>

Arahan dan alat yang didokumentasikan dalam README.md dan MCP-CONNECT.md dilukis sebagai satu aliran, [docs/flow/simplicio.svg](../docs/flow/simplicio.svg), dijana daripada satu fail sumber, `docs/flow/simplicio.flow.json`. Jana semula dengan `python3 scripts/generate_flow.py` dan semak hanyutannya dengan `python3 scripts/generate_flow.py --check`. Kontrak yang memastikannya selari dengan halaman ini dan dengan MCP-CONNECT.md ialah `python3 -m pytest tests/test_flow_contract.py -q`. Semakan import Langflow ialah `scripts/verify_flow_langflow.py`, yang gagal dalam keadaan tertutup (keluar dengan kod 2, `status=blocked`) apabila tiada pelayan berjalan. Bukti terdapat di bawah `docs/flow/evidence/` dan `docs/flow/render/`, dan [docs/flow/README.md](../docs/flow/README.md) memuatkan keperluan serta cara mengulanginya.

</details>

<a id="questions-people-ask"></a>

## Soalan yang sering ditanya

**Adakah perbandingan ini adil?**<br>
Ejen yang sama, model yang sama, tiga gesaan yang sama, projek permulaan yang sama dan semakan luaran yang sama, dalam satu pusingan. Garis dasar tidak mempunyai pelayan MCP dan tiada konfigurasi Simplicio. Lihat [Di mana Simplicio tidak menang](#where-simplicio-does-not-win) dan [Had](../benchmarks/2026-11-22-standard-benchmark.md#limits) laporan itu.

**Adakah saya perlu menukar ejen atau model saya?**<br>
Tidak. Simplicio bersambung dengan ejen yang sudah anda gunakan. Dalam penanda aras di atas, setiap persediaan menggunakan ejen dan model yang sama.

**Adakah saya akan sentiasa mendapat nombor ini?**<br>
Tidak. Nombor ini mengukur satu tugasan, dengan satu model, pada satu mesin, dalam tiga sesi bagi setiap persediaan. Lihat [Di mana Simplicio tidak menang](#where-simplicio-does-not-win), dan jalankan perbandingan ini pada kerja anda sendiri.

**Adakah ia sumber terbuka?**<br>
Tidak. Simplicio ialah proprietari. Ia ialah binari yang ditandatangani, diterbitkan sebagai aset keluaran, dan sumbernya tidak awam. Repositori ini menyimpan pemasang, pakej untuk ejen, sumber aplikasi Desktop, dokumentasi dan data penanda aras.

**Bagaimana saya membuangnya?**<br>
Jalankan `sh install.sh --uninstall --keep-data`, atau `pwsh install.ps1 -Uninstall -KeepData` pada Windows. Ia mengeluarkan binari dan menyimpan data anda. Ia tidak mengubah konfigurasi ejen anda, jadi buang entri Simplicio dalam tetapan setiap ejen. [Pemasangan](#install) mempunyai butiran dan pilihan pembersihan penuh.

**Adakah saya perlu akaun?**<br>
Ya. Log masuk Google diperlukan, termasuk semasa beta. Jalankan `simplicio auth login`.

**Adakah kod saya meninggalkan mesin saya?**<br>
Pemetaan, konteks, suntingan dan semakan dijalankan pada mesin anda. Simplicio berhubung dengan SimpleTI untuk log masuk dan semakan pelan, dan dengan GitHub untuk mencari kemas kini, dengan tiada kandungan repositori dalam kedua-duanya. Ciri yang anda konfigurasikan atau jalankan boleh sampai ke perkhidmatan lain. Senarai lengkap ada dalam [Apa yang Simplicio hantar, dan kepada siapa](#safety-and-privacy).

<a id="documentation-and-community"></a>

## Dokumentasi dan komuniti

- **Laman web:** [simpleti.com.br/simplicio](https://simpleti.com.br/simplicio/)
- **Dokumentasi:** [simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)
- **Discord:** [Sertai komuniti](https://discord.gg/wM6tr7xVb)
- **Isu:** [penjejak isu GitHub](https://github.com/simpletibr/simplicio/issues)
- **Dalam repositori ini:** [INSTALL.md](../INSTALL.md), [MCP-CONNECT.md](../MCP-CONNECT.md) dan [docs/hosts/](../docs/hosts/)
- **Berkaitan:** Simplicio Video (hypit). Untuk mengklonnya: `git clone https://github.com/hypit-ai/hypit.git simplicio-video`

<p align="center">
  <sub>© 2026 SimpleTI. Simplicio ialah perisian proprietari berdaftar. Semua hak terpelihara.</sub>
</p>
