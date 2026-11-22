<div align="center">

<img src="../assets/simplicio-icon-192.png" alt="Simplicio ロゴ" width="96" height="96">

<h1>Simplicio</h1>

<p><b>UltraFast Mode for all.</b></p>

<p><b>同じエージェント、同じモデル、同じジョブ：121&nbsp;s&nbsp;→&nbsp;25&nbsp;s、$0.0226&nbsp;→&nbsp;$0.0076。</b></p>

<p>Simplicio なし → Simplicio 3.15.0 あり。Claude Code で Claude Haiku 5.5 を使い、一つの小さなコーディングジョブを 3 回実行したときの中央値です。</p>

<p>Simplicio は、お使いのマシン上で動作し、すでに使っているコーディングエージェントにツールを追加します。</p>

<p>
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=2fe6a0&label=release" alt="最新リリース"></a>
  <a href="https://simpleti.com.br/simplicio/docs"><img src="https://img.shields.io/badge/docs-simpleti.com.br-ffd23f" alt="ドキュメント"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="スター"></a>
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="ライセンス: プロプライエタリ">
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
  日本語 ·
  <a href="README.ko-KR.md">한국어</a> ·
  <a href="README.hi-IN.md">हिन्दी</a> ·
  <a href="README.ar-SA.md">العربية</a>&lrm; ·
  <a href="README.he-IL.md">עברית</a>&lrm; ·
  <a href="README.id-ID.md">Bahasa Indonesia</a> ·
  <a href="README.ms-MY.md">Bahasa Melayu</a>
</p>

<p align="center"><sub>このファイルは <a href="../README.md">英語版 README</a> の翻訳です。内容に違いがある場合は英語版が正です。図表の文字は英語のままです。</sub></p>

</div>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-dark.svg">
    <img src="../assets/benchmark-2026-11-22-light.svg" width="840" alt="Simplicio なし、Simplicio 3.14.0、Simplicio 3.15.0 を三つの指標で比べた棒グラフ。各セットアップは三セッションの中央値です。ジョブ全体の時間は、121 s（Simplicio なし）、104 s（Simplicio 3.14.0）、25 s（Simplicio 3.15.0）。コストは $0.0226、$0.0220、$0.0076。出力トークンは 18,162、19,722、3,211。">
  </picture>
</p>

<p align="center">
  <sub>各セットアップ（Simplicio なし、Simplicio 3.14.0、Simplicio 3.15.0）の 3 セッションの中央値。Claude Code 2.1.330 上の Claude Haiku 5.5、2026-11-22。すべてのセットアップで、9 件中 9 件のステップを完了しました。各棒の細い線は、最小のセッションから最大のセッションまでの範囲を示します。<br>
  <a href="../benchmarks/2026-11-22-standard-benchmark.md">方法、データ、制限事項</a></sub>
</p>

<p align="center">
  <sub>併せて読む際の注意：小さなジョブ一つ、セットアップごとに三セッション、モデル一つです。外部検証は、プロンプトで求めた内容より狭い範囲しか確認しません。ピークメモリは高くなりました：375 MB 対 270 MB。Simplicio のビルドは、リリースのコミットからコンパイルし、サインインをオフにした状態で作成しました。</sub>
</p>

<p align="center">Simplicio がこの結果を得る仕組みは公開していません。測定結果は、Simplicio が負けた場合も含めて公開しています。</p>

<p align="center">
  <b>試してみる：</b> <a href="#install">インストール</a> · <a href="#first-run">初回実行</a><br>
  <a href="#what-simplicio-is">概要</a> ·
  <a href="#the-measurement">測定</a> ·
  <a href="#works-with-the-agent-you-already-use">エージェント</a> ·
  <a href="#command-line">コマンド</a> ·
  <a href="#safety-and-privacy">プライバシー</a> ·
  <a href="#questions-people-ask">よくある質問</a> ·
  <a href="#documentation-and-community">ドキュメント</a>
</p>

<a id="what-simplicio-is"></a>

## Simplicio とは

Simplicio は、お使いのコーディングエージェントに超高速モードを与えるローカルプログラムです。エージェントやモデルの種類は問いません。このページの数値は、一つのエージェントと一つのモデルで測ったものです。何を測ったかは、下のセクションに正確に書いています。

- **お使いのエージェントとモデルはそのまま使えます。** Simplicio は、Claude Code、Codex、Cursor、またはそれらの背後にあるモデルを置き換えるものではありません。
- **署名付きのネイティブバイナリを一つインストールします。** インストーラーは署名を検証し、お使いのマシンで見つかったエージェントに Simplicio を登録します。
- **お使いのマシン上で動作します。** エージェントは、ローカルの STDIO MCP サーバーとして Simplicio を起動します。MCP は Model Context Protocol の略で、コーディングエージェントが外部のツールを呼び出すための標準的な方法です。STDIO は、エージェントがプログラム自体を起動し、標準入力と標準出力を通じてやり取りすることを意味します。
- **エージェントにツールを提供します。** リポジトリのマップ、サイズを制限したコンテキスト、構造化された編集と検証です。[主要なツール](#works-with-the-agent-you-already-use)は、以下に示します。
- **変わるのはセッションです。** かかる時間と、そのコストが変わります。次のセクションで、どの程度変わるか、また効果が出ない場合を示します。

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/diagram-where-simplicio-runs-dark.svg">
    <img src="../assets/diagram-where-simplicio-runs-light.svg" width="840" alt="図。お使いのマシン上に、あなた、コーディングエージェント、Simplicio、リポジトリがあります。エージェントは、ローカルの STDIO (MCP) 経由で Simplicio とやり取りします。エージェントは、これまでどおりモデルプロバイダーとやり取りします。Simplicio は、サインインとプランの確認のために SimpleTI と、リリースの確認のために GitHub とやり取りします。どちらにもリポジトリの内容は含まれません。">
  </picture>
</p>

<p align="center">
  <sub>この図は、既定の状態で起きることを示しています。他のサービスに接続する機能を含む完全な一覧は、「安全性とプライバシー」の [Simplicio が送信する内容と送信先](#safety-and-privacy) にあります。</sub>
</p>

<a id="the-measurement"></a>

## 測定

一つのジョブを、Simplicio ありとなしで同じ方法で実行しました。ジョブは、同じ会話の中で三つのステップを行う一つのエージェントセッションです：

1. ユーザー一覧を作る：API と、表、検索、並べ替えのあるページ。
2. 変更する：列を一つ削除し、役割による絞り込みと日付の列を追加する。
3. 簡単な登録機能を追加する：入力を検証する `POST` エンドポイントと、フォームのページ。

各ステップの後、セッションの外から外部検証を行いました。API は HTTP で呼び出し、ページはヘッドレス Chrome で読み込みました。ヘッドレス Chrome は、ウィンドウのない Chrome です。すべてのセットアップで、同じエージェントと同じモデルを使いました。Claude Code 2.1.330 と Claude Haiku 5.5 です。ベースラインは、Claude Code 2.1.330 を、標準で備えるツールだけで実行したものです。MCP サーバーも Simplicio の設定もありません。外部検証は、検索ボックス、並べ替え、保存後のリダイレクト、ページの見た目、コードの品質を確認していません。

中央値だけでなく、すべてのセッションをこのグラフに示しています。

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-sessions-dark.svg">
    <img src="../assets/benchmark-2026-11-22-sessions-light.svg" width="840" alt="全セッションの散布図。横軸はジョブ全体の時間、縦軸はエージェントが報告したコストです。Simplicio 3.15.0、緑のひし形：23–27 s、$0.0071–$0.0098。Simplicio 3.14.0、灰色の四角：90–106 s、$0.0214–$0.0249。Simplicio なし、白抜きの丸：97–172 s、$0.0186–$0.0280。">
  </picture>
</p>

セットアップごとの 3 セッションの中央値。各値の下にある細い線は、最小のセッションと最大のセッションの範囲です。

| 指標 | Simplicio なし | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| ジョブ時間 | 121 s<br><sub>97–172</sub> | 104 s<br><sub>90–106</sub> | **25 s**<br><sub>23–27</sub> |
| 報告コスト | $0.0226<br><sub>0.0186–0.0280</sub> | $0.0220<br><sub>0.0214–0.0249</sub> | **$0.0076**<br><sub>0.0071–0.0098</sub> |
| モデルリクエスト | 25<br><sub>19–33</sub> | 18<br><sub>18–22</sub> | **10**<br><sub>10–10</sub> |
| ツール呼び出し | 22<br><sub>16–30</sub> | 15<br><sub>15–19</sub> | **7**<br><sub>7–7</sub> |
| 出力トークン | 18,162<br><sub>15,599–23,328</sub> | 19,722<br><sub>18,764–24,997</sub> | **3,211**<br><sub>3,068–3,573</sub> |
| 入力トークン | 34,691<br><sub>30,447–42,543</sub> | 34,141<br><sub>33,121–40,017</sub> | 18,755<br><sub>18,466–33,300</sub> |
| CPU 時間 | 8.5 s<br><sub>8.5–9.2</sub> | 10.0 s<br><sub>8.9–10.0</sub> | **5.3 s**<br><sub>5.3–5.5</sub> |
| ピークメモリ | **270 MB**<br><sub>248–274</sub> | 436 MB<br><sub>432–439</sub> | 375 MB<br><sub>365–379</sub> |
| 完了したステップ | 9 件中 9 件 | 9 件中 9 件 | 9 件中 9 件 |

太字は、各行で最良の値を示します。ただし、その範囲が他の値の範囲と重ならない場合に限ります。入力トークンの範囲は重なっているため、この実行では入力トークンに差があるとは主張しません。「9 件中 9 件」は、3 セッションそれぞれで 3 ステップを行った結果で、すべてのステップがすべての外部検証に合格したことを示します。ジョブ時間は、ジョブ全体の時間です。モデルリクエストは、モデルへの一回の呼び出しです。ツール呼び出しは、エージェントによるツールの一回の使用です。報告コストは、エージェントが報告する値です。使用したトークン数に、モデルの公開価格を掛けたものです。モデルのトークンだけを数えています。請求書ではありません。

セッションで変わったのは回数です。モデルリクエストが減り、エージェントのツール呼び出しも減りました。

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-work-dark.svg">
    <img src="../assets/benchmark-2026-11-22-work-light.svg" width="840" alt="モデルリクエストまたはツール呼び出し一回につき一つの印を付けた単位グラフ。3 セッションの中央値。モデルリクエスト：25（Simplicio なし）、18（Simplicio 3.14.0）、10（Simplicio 3.15.0）。ツール呼び出し：22、15、7。">
  </picture>
</p>

ステップごとの時間を、同じ尺度で示します。

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-steps-dark.svg">
    <img src="../assets/benchmark-2026-11-22-steps-light.svg" width="840" alt="同じ尺度で示したステップごとの中央値の時間。ステップ 1、ビルド：57.3 s（Simplicio なし）、53.7 s（Simplicio 3.14.0）、5.8 s（Simplicio 3.15.0）。ステップ 2、変更：17.3 s、15.2 s、8.9 s。ステップ 3、登録：31.4 s、27.5 s、10.3 s。">
  </picture>
</p>

各中央値は個別に算出しているため、ステップの中央値を合計しても、ジョブ全体の中央値とは一致しません。

<details>
<summary>ステップごとの正確な数値</summary>

各セルは、そのステップの中央値の時間と中央値のコストです：

| ステップ | Simplicio なし | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. ビルド | 57.3 s / $0.0111 | 53.7 s / $0.0137 | 5.8 s / $0.0022 |
| 2. 変更 | 17.3 s / $0.0040 | 15.2 s / $0.0032 | 8.9 s / $0.0023 |
| 3. 登録 | 31.4 s / $0.0075 | 27.5 s / $0.0056 | 10.3 s / $0.0026 |

</details>

**読み方。** 比率は、丸めていない中央値から算出しています。同じエージェントで Simplicio なしの場合と比べると、ジョブ全体は 4.9 倍速く、コストは約三分の一でした。前のリリースと比べると、4.2 倍速くなりました。セッション内では、モデルリクエストは 25 回ではなく 10 回、出力トークンは 18,162 ではなく 3,211 でした。また、ジョブは同じ外部検証に合格しました。最悪の場合：Simplicio なしで最も速いセッション（97.1 s）でさえ、Simplicio 3.15.0 で最も遅いセッション（26.6 s）と比べて 3.7 倍遅い結果でした。Simplicio なしで最も安いセッション（$0.0186）でさえ、Simplicio ありで最も高いセッション（$0.0098）の 1.9 倍のコストでした。ベースラインは、Claude Code 2.1.330 を、標準で備えるツールだけで実行したものです。MCP サーバーも Simplicio の設定もありません。コストは、モデルのトークンだけを対象としています。セッションは一台のマシンで四つずつ同時に実行したため、時間を比べられるのは、このラウンド内だけです。

<a id="where-simplicio-does-not-win"></a>

### Simplicio が効果を示さない場合

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-memory-dark.svg">
    <img src="../assets/benchmark-2026-11-22-memory-light.svg" width="840" alt="ピークメモリ、3 セッションの中央値：Simplicio なしは 270 MB で最も低い。436 MB は Simplicio 3.14.0 で、61% 多い。375 MB は Simplicio 3.15.0 で、39% 多い。">
  </picture>
</p>

- **メモリ。** ピークメモリは、標準のエージェントと比べて 39% 高くなりました：375 MB 対 270 MB。
- **前のリリースは、このジョブで効果を示しませんでした。** Simplicio 3.14.0 のコストは Simplicio なしと同じで、時間の差は実行ごとのばらつきの範囲内です。このページの効果は、3.15.0 で初めて現れたものです。
- **短い単発の Python スクリプト。** 以前のラウンドでは、Simplicio 3.10.8 は、試したすべてのモデルで標準のエージェントより遅くなりました。Claude Code 上の Claude Sonnet 5.5 では、Simplicio ありで 19.6 s、$0.0548 かかりました。なしでは 11.4 s、$0.0283 でした。このタスクは、3.15.0 では再測定していません。
- **インストールするものと、測定したものは完全に同じではありません。** ビルドはリリースのコミットからコンパイルし、サインインとバックグラウンドプロセスをオフにした状態で作成しました。署名付きのダウンロード版は測定していません。
- **サンプルが少ない。** セットアップごとに三セッション、モデル一つ、小さな新規プロジェクト一つ、マシン一台、同時に四セッションです。比率は、このジョブの測定値として読んでください。お使いの環境で同じ結果が出る保証ではありません。この三つのセットアップのセッションは、一つも除外せず、再実行もしていません。私たちは、あなたの作業のどの程度がこのジョブに似ているかは測定していません。

### 自分で確認する

[レポート](../benchmarks/2026-11-22-standard-benchmark.md)には、三つのプロンプト（ポルトガル語で書かれ、翻訳付き）、すべての外部検証の説明、セッションごとの数値が掲載されています。[データファイル](../benchmarks/2026-11-22-standard-benchmark.json)には、同じ内容が JSON 形式で入っています。テストハーネスは公開していません。同じ三つのプロンプトを、お使いのエージェントで、ご自身の小さなプロジェクトを使い、Simplicio をオンにした場合とオフにした場合で実行し、ご自身の時間と請求額を比べてください。

<a id="install"></a>

## インストール

署名付きのネイティブバイナリをインストールします。方法を一つ選んでください。

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

Windows では、`py -m pip install --upgrade simplicio-installer` を実行し、続けて `simplicio install` を実行してください。Python のスクリプトフォルダーが `PATH` に含まれていない場合は、先に追加してください。

インストーラーは、お使いのプラットフォーム向けの最新の署名付きリリースをダウンロードし、その SHA-256 と Ed25519 署名を検証します。検証が済んでから、インストール済みのバイナリを置き換えます。バイナリは `~/.simplicio/bin/` に配置します（Windows では `%USERPROFILE%\.simplicio\bin\`）。また、見つかったエージェントに Simplicio を自動的に登録します。登録に失敗した場合、インストーラーは成功を報告せずに停止します。すでに開いているエージェントは再起動して、設定を読み込み直してください。

**サインイン。** ベータ期間中も含め、Google サインインが必要です。`simplicio auth login` を実行し、続けて `simplicio auth status --json` を実行してください。状態が `active: true` と報告したら、次に進みます。登録にはサインインは不要です。そのため、サインインする前でもエージェントは設定されます。エージェントの設定に、パスワードやトークンを貼り付けないでください。

<details>
<summary>確認、更新、削除</summary>

更新するには、インストーラーをもう一度実行してください。どちらのインストーラーも、いつでも再実行できます。実行すると最新リリースを取得します。`install.sh` と `install.ps1` は、このリポジトリのルートにあります。

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

- `--doctor` はインストールを確認します。
- `--uninstall --keep-data` は、インストール済みのバイナリを削除し、データは残します。これには、`~/.simplicio/login.json` にある 30 日間の Google サインイン状態も含まれます。
- `--uninstall --purge` は、Simplicio が管理する状態だけを削除します。サインイン状態も含みます。`~/.simplicio/.env` は残します。このファイルには、プロバイダーの認証情報が置かれている場合があるためです。パージには `SIMPLICIO_CONFIRM_PURGE=1` が必要です。
- アンインストールは、エージェントの設定を編集しません。Simplicio の項目は、各エージェント自身の設定で削除するまで、各エージェントに残ります。
- プロジェクト自身の `.simplicio` フォルダー内のデータは、`--keep-data` では削除されません。`--purge` を選ぶ前に、削除対象を確認してください。

詳しくは [INSTALL.md](../INSTALL.md) を参照してください。

</details>

<a id="first-run"></a>

## 初回実行

```bash
simplicio version
cd my-project
simplicio onboard
```

`simplicio version` は、インストール済みのバイナリを確認します。`simplicio onboard` は、初回にプロジェクトを準備します。その後、そのプロジェクトでエージェントを開き、いつもどおり作業してください。Simplicio が読み込まれたことを確認するには、エージェントの MCP サーバー一覧で `simplicio` を探してください。Claude Code では、`/mcp` で接続中のサーバーを一覧できます。先にインストーラーの中身を確認したいですか。[install.sh](../install.sh) がそのファイルです。

<a id="works-with-the-agent-you-already-use"></a>

## すでにお使いのエージェントで動作

Simplicio はローカルの STDIO MCP サーバーです。そのため、ローカルの MCP サーバーを起動できるエージェントなら、Simplicio を接続先に指定できます。

インストーラーは、登録を Simplicio 自身の登録機能に任せます。お使いのマシンにあるエージェントを検出し、設定方法を把握しているものに対して Simplicio の項目を書き込みます。対象には、Claude Code、Codex、Cursor、Visual Studio Code、OpenCode、Gemini CLI、Kiro などがあります。このリポジトリにある二つのファイルは、各連携がどこまで対応しているかを示しています：

- レジストリ [`plugins/simplicio/host-surfaces.json`](../plugins/simplicio/host-surfaces.json) には、43 のエージェント ID が記載されています。各 ID について、Simplicio がどのように接続するかを示しています。Simplicio が書き込む MCP の項目（23）、ネイティブのプラグインまたは拡張（5）、ポータブルなプラグインパッケージ（4）、自分で手順に従うガイド付きセットアップ（9）、またはその他のコマンドラインツール（2）です。
- 互換性マトリックス [`docs/hosts/compatibility-matrix.md`](../docs/hosts/compatibility-matrix.md) には、検証済みの内容が記載されています。43 のうち 12 を「対応済み」、29 を `unverified` としており、Codex と Gemini CLI の行はありません。レジストリで Simplicio が項目を書き込むと示されていて、マトリックスで `unverified` となっている連携は、テストされていないものとして扱ってください。

23 のエージェントには、[`docs/hosts/`](../docs/hosts/) にガイドがあります。プラグイン経由で接続するエージェントでは、プラグインは別の手順で適用されます。この手順では同意を求めます。説明は [INSTALL.md](../INSTALL.md) にあります。

<details>
<summary>43 のエージェントすべて（Simplicio の接続方法別）</summary>

| Simplicio の接続方法 | 件数 | エージェント |
|---|---|---|
| Simplicio が書き込む MCP の項目 | 23 | **xAI Grok Build**, MiMo Code, Amp, OpenClaude, Antigravity, **Pi**, **oh-my-pi**, Goose, Auggie, Autohand Code, Charm, Cline, Command Code, Continue, Droid, Kilocode, Kimi, Mistral Vibe, Rovo Dev, **Visual Studio Code**, **Meta Muse Code**, **OpenMausBot**, **OpenMuse (Python)** |
| ネイティブのプラグインまたは拡張 | 5 | **Claude Code**, Codex, **OpenCode**, Hermes Agent, Gemini CLI |
| ポータブルなプラグインパッケージ | 4 | **Cursor**, GitHub Copilot, **Kiro**, Qwen Code |
| 自分で手順に従うガイド付きセットアップ | 9 | Devin, Codebuff, CopilotKit OpenDots, CopilotKit OpenBot, agentes.chat, OpenAI dots, xAI Grok Bot, Meta Muse app, Cue by Manus |
| その他のコマンドラインツール | 2 | **OrcaDev / Orca ADE**, T3 Code |

太字は、互換性マトリックスで対応済みとマークされたエージェントです。

</details>

登録をやり直すには、`simplicio mcp register` を実行してください。サーバーのコマンドは `simplicio serve --mcp --stdio` です。エージェントが受け取る主要なツールは次のとおりです：

| ツール | 提供される機能 |
|---|---|
| `simplicio_map` | エージェントがリポジトリ内を把握できるようにする、リポジトリの簡潔なマップ |
| `simplicio_context` | タスクに必要なコンテキストを、ファイル全体ではなくサイズを制限して提供 |
| `simplicio_edit` | 準備された計画に基づく、構造化されたファイル編集 |
| `simplicio_validate` | パイプライン、テスト、納品の検証 |
| `simplicio_run` | Simplicio の管理下で実行するタスク |

実際の一覧は、起動時にサーバーが報告する内容によって決まります。主要なツールについては [MCP-CONNECT.md](../MCP-CONNECT.md) で説明しています。

<details>
<summary>手動設定</summary>

エージェントが自動で設定されていない場合は、この項目をエージェントの MCP 設定に追加してください。パスは、インストール済みのバイナリの絶対パスに置き換えてください。

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

Codex は TOML を読みます。エージェントは `command` を直接起動するため、`~` は使わず、シェルの展開にも頼らないでください。Windows のパスでは / を使い、例のユーザー名は置き換えてください。

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

各エージェントが設定ファイルを置く場所は、[MCP-CONNECT.md](../MCP-CONNECT.md) を参照してください。

</details>

<a id="command-line"></a>

## コマンドライン

| コマンド | 得られるもの |
|---|---|
| `simplicio map --repo . --for-llm markdown` | モデルが読むための、リポジトリの簡潔な構造マップ |
| `simplicio context --repo .` | タスクに必要な、サイズを制限したコンテキスト |
| `simplicio memory query "query" --json` | インデックス化されたメモリから呼び出した、プロジェクトの既知の情報（JSON 形式） |
| `simplicio edit --plan plan.json --repo .` | 準備された構造化編集の一式を、ファイルに適用します |
| `simplicio run "task" --repo . --agents N` | N 個のエージェントを使い、Simplicio の管理下で実行するタスク |
| `simplicio loop` | 収束するまでラウンドを続ける作業 |

Simplicio のメッセージに出てくる名前は次のとおりです：Mapper は観察し、Fast は投影または取得し、Dev CLI は編集し、Runtime は統制し、Loop は収束します。

<a id="safety-and-privacy"></a>

## 安全性とプライバシー

このセクションは、バージョン 3.15.0 について説明しています。

**Simplicio が送信する内容と送信先**

- **お使いのマシン内で完結します。** マッピング、コンテキスト、編集、検証は、Simplicio のバイナリ内で実行されます。結果は、同じマシン上のエージェントに渡されます。エージェントがモデルプロバイダーに何を送信するかは、これまでどおりエージェントが決めます。
- **SimpleTI（simpleti.com.br）への送信。** サインインとプランの確認のみです。送信するのは、サインイントークン、Simplicio のバージョン、お使いのコンピューターのホスト名です。任意のライセンス確認では、アカウントのメールアドレスも送信します。SimpleTI は、アカウントのメールアドレス、名前、プランを返します。リポジトリの内容は送信しません。ファイル、ファイルパス、プロンプト、編集内容のいずれも含みません。
- **GitHub への送信。** 新しいリリースを確認するバックグラウンドのチェックを行います。頻度は最大で約 12 時間に 1 回です。あなたやコードに関する情報は含みません。無効にするには `SIMPLICIO_DISABLE_AUTO_UPDATE=1` を設定してください。更新する際は、新しいバイナリを GitHub からダウンロードし、古いバイナリを置き換える前に SHA-256 と署名を検証します。
- **アナリティクスなし。** Simplicio 3.15.0 と、Simplicio がエージェントにインストールするファイルは、この点について検査済みです。いずれも、アナリティクス、クラッシュレポート、利用データをアップロードしません。利用記録と節約量の記録はローカルファイルに保存されます。インストールされるフックは、ローカルのプログラムだけを実行します（Simplicio のバイナリと、任意のプラグインの場合はローカルスクリプト）。どれもネットワークに接続しません。
- **設定したサービスへの送信。** モデルプロバイダー、GitHub、Jira、チャット通知ツール、チームのキャッシュは、その機能が送信する内容を受け取ります。内容にはプロンプトやコードが含まれることがあります。モデルプロバイダーへのリクエストには、クライアントとして Simplicio の名前を記載したヘッダーが付きます。
- **二つの機能は、設定なしで公開サービスに接続します。** Web 検索は、実行されると、別の検索サービスを設定しない限り、検索クエリを DuckDuckGo に送信します。Simplicio 独自のチャットでは、Web の質問に見えるメッセージが、そのクエリになることがあります。依存関係のセキュリティ監査は、実行すると、依存関係の名前とバージョンを osv.dev に送信します。Web 検索もセキュリティ監査も、ファイルの内容は送信しません。
- **ダウンロード。** インストーラーと更新の経路は、GitHub からダウンロードします。任意の補助スクリプトの一部は、実行時に独自のツールを PyPI または npm から取得します。エージェントのプラグインが起動して Simplicio のバイナリが見つからない場合は、コミットに固定され、SHA-256 で検証された公式インストーラーを GitHub からダウンロードします。

**署名付きリリース。** 各リリースでは、バイナリを SHA-256 チェックサム、Ed25519 署名、SBOM（ビルドに含まれるものの一覧）、ビルドの来歴情報とともに公開します。インストーラーと更新の経路は、インストール済みのバイナリを置き換える前に、チェックサムと署名を検証します。安定版では、署名がない場合、署名が無効な場合、チェックサムが一致しない場合を、いずれも致命的な失敗として扱うことが契約で定められています。契約の内容は [docs/UPDATE_SIGNATURE_CONTRACT.md](../docs/UPDATE_SIGNATURE_CONTRACT.md) にあります。

**インストーラーがエージェントに加える変更。** インストーラーは、エージェントの MCP 設定に Simplicio の項目を追加し、設定のそれ以外の部分は残します。Claude Code では、`mcp__simplicio__*` も許可します。そのため、オートモードで Simplicio のツールが拒否されることはありません。インストーラーがフックのインターフェースを検証済みのエージェントでは、Simplicio のフックもインストールします。インストーラーが何を書き込むかは [INSTALL.md](../INSTALL.md) に記載されています。各エージェントの詳細は、[`docs/hosts/`](../docs/hosts/) 内の各ガイドを参照してください。アンインストールしても、これらの項目は元に戻りません。削除方法は「インストール」セクションに記載しています。

## このリポジトリのその他の内容

<details>
<summary>デスクトップアプリ（macOS プレビュー）</summary>

macOS（Apple Silicon）向けのデスクトップアプリのプレビューは、[Simplicio-3.8.47-arm64.dmg](https://github.com/simpletibr/simplicio/releases/download/v3.8.47/Simplicio-3.8.47-arm64.dmg) として公開されています。その SHA-256 は [DESKTOP-SHA256SUMS](../DESKTOP-SHA256SUMS) にあり、Simplicio バイナリのチェックサムとは別になっています。DMG には署名ファイルがなく、Simplicio 3.8.47 のバイナリを同梱しています。

- Windows 版のデスクトップアプリは公開していません。Windows では、上記のコマンドラインからのインストールを使ってください。
- Apple Developer ID による署名と公証（notarization）は行っていません。パッケージは ad-hoc 署名です。これは、Apple の開発者証明書を使わずに署名したという意味です。Gatekeeper による受け入れを主張していないため、開くときに macOS が警告を表示することがあります。
- 署名付きのデスクトップアプリのパッケージが公開されるまでは、上記のコマンドラインからのインストールが、サポートされている公式のインストール方法です。

詳しくは [docs/desktop/RELEASE.md](../docs/desktop/RELEASE.md) を参照してください。

</details>

<details>
<summary>メンテナー向け：生成されたフロー図</summary>

README.md と MCP-CONNECT.md に記載されたコマンドとツールは、一つのフローとして [docs/flow/simplicio.svg](../docs/flow/simplicio.svg) に描かれています。このフローは、一つのソースファイル `docs/flow/simplicio.flow.json` から生成しています。再生成するには `python3 scripts/generate_flow.py` を、ずれがないか確認するには `python3 scripts/generate_flow.py --check` を実行してください。このページおよび MCP-CONNECT.md と内容を一致させる契約は、`python3 -m pytest tests/test_flow_contract.py -q` です。Langflow のインポート確認は `scripts/verify_flow_langflow.py` で行います。サーバーが起動していない場合は、安全側で失敗します（終了コード 2、`status=blocked`）。証跡は `docs/flow/evidence/` と `docs/flow/render/` にあります。要件と再現方法は [docs/flow/README.md](../docs/flow/README.md) に記載しています。

</details>

<a id="questions-people-ask"></a>

## よくある質問

**比較は公平ですか？**<br>
同じエージェント、同じモデル、同じ三つのプロンプト、同じ開始プロジェクト、同じ外部検証を、一つのラウンドで行いました。ベースラインには MCP サーバーも Simplicio の設定もありません。[Simplicio が効果を示さない場合](#where-simplicio-does-not-win) と、レポートの [制限事項](../benchmarks/2026-11-22-standard-benchmark.md#limits) を参照してください。

**エージェントやモデルを変更する必要がありますか？**<br>
いいえ。Simplicio は、すでにお使いのエージェントに組み込まれます。上記の測定では、すべてのセットアップで同じエージェントと同じモデルを使いました。

**この数値が必ず得られますか？**<br>
いいえ。これらの数値は、一つのジョブを、一つのモデルで、一台のマシン上で、セットアップごとに三セッション測定したものです。[Simplicio が効果を示さない場合](#where-simplicio-does-not-win) を参照し、ご自身の作業で比較を実行してください。

**オープンソースですか？**<br>
いいえ。Simplicio はプロプライエタリです。署名付きのバイナリとして、リリースのアセットに公開されています。ソースコードは公開していません。このリポジトリには、インストーラー、エージェント向けのパッケージ、デスクトップアプリのソースコード、ドキュメント、測定データが含まれています。

**削除するにはどうすればよいですか？**<br>
`sh install.sh --uninstall --keep-data` を実行してください。Windows では `pwsh install.ps1 -Uninstall -KeepData` を実行します。バイナリを削除し、データは残します。エージェントの設定は編集しないため、Simplicio の項目は各エージェント自身の設定で削除してください。詳細とパージのオプションは [インストール](#install) に記載しています。

**アカウントは必要ですか？**<br>
はい。ベータ期間中も含め、Google サインインが必要です。`simplicio auth login` を実行してください。

**コードがマシンの外に出ますか？**<br>
マッピング、コンテキスト、編集、検証は、お使いのマシン上で実行されます。Simplicio は、サインインとプランの確認のために SimpleTI と、更新を確認するために GitHub とやり取りします。どちらにもリポジトリの内容は含まれません。設定した機能や実行した機能は、他のサービスに接続することがあります。完全な一覧は [Simplicio が送信する内容と送信先](#safety-and-privacy) にあります。

<a id="documentation-and-community"></a>

## ドキュメントとコミュニティ

- **ウェブサイト：** [simpleti.com.br/simplicio](https://simpleti.com.br/simplicio/)
- **ドキュメント：** [simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)
- **Discord：** [コミュニティに参加](https://discord.gg/wM6tr7xVb)
- **Issue：** [GitHub の issue トラッカー](https://github.com/simpletibr/simplicio/issues)
- **このリポジトリ内：** [INSTALL.md](../INSTALL.md)、[MCP-CONNECT.md](../MCP-CONNECT.md)、[docs/hosts/](../docs/hosts/)
- **関連：** Simplicio Video（hypit）。複製するには：`git clone https://github.com/hypit-ai/hypit.git simplicio-video`

<p align="center">
  <sub>© 2026 SimpleTI. Simplicio は登録済みのプロプライエタリソフトウェアです。すべての権利を留保します。</sub>
</p>
