<div align="center">

<img src="../assets/simplicio-icon-192.png" alt="Logo di Simplicio" width="96" height="96">

<h1>Simplicio</h1>

<p><b>UltraFast Mode for all.</b></p>

<p><b>Stesso agente, stesso modello, stesso lavoro: 121&nbsp;s&nbsp;→&nbsp;25&nbsp;s, e $0.0226&nbsp;→&nbsp;$0.0076.</b></p>

<p>Senza Simplicio → con Simplicio 3.15.0. Mediana di 3 esecuzioni di un piccolo lavoro di programmazione in Claude Code con Claude Haiku 5.5.</p>

<p>Simplicio funziona sul tuo computer e aggiunge strumenti all'agente di programmazione che già usi.</p>

<p>
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=2fe6a0&label=release" alt="Ultima release"></a>
  <a href="https://simpleti.com.br/simplicio/docs"><img src="https://img.shields.io/badge/docs-simpleti.com.br-ffd23f" alt="Documentazione"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Stelle"></a>
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="Licenza: proprietaria">
</p>

<p>
  <a href="../README.md">English</a> ·
  <a href="README.pt-BR.md">Português (Brasil)</a> ·
  <a href="README.es-ES.md">Español</a> ·
  <a href="README.fr-FR.md">Français</a> ·
  Italiano ·
  <a href="README.pl-PL.md">Polski</a> ·
  <a href="README.ru-RU.md">Русский</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja-JP.md">日本語</a> ·
  <a href="README.ko-KR.md">한국어</a> ·
  <a href="README.hi-IN.md">हिन्दी</a> ·
  <a href="README.ar-SA.md">العربية</a>&lrm; ·
  <a href="README.he-IL.md">עברית</a>&lrm; ·
  <a href="README.id-ID.md">Bahasa Indonesia</a> ·
  <a href="README.ms-MY.md">Bahasa Melayu</a>
</p>

<p align="center"><sub>Questo file è una traduzione del <a href="../README.md">README in inglese</a>. Se i due differiscono, fa fede la pagina inglese. I grafici sono in inglese.</sub></p>

</div>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-dark.svg">
    <img src="../assets/benchmark-2026-11-22-light.svg" width="840" alt="Grafico a barre che confronta senza Simplicio, Simplicio 3.14.0 e Simplicio 3.15.0 su tre misure, mediana di tre sessioni per ciascuna. Tempo dell'intero lavoro: 121 s senza Simplicio, 104 s con Simplicio 3.14.0 e 25 s con Simplicio 3.15.0. Costo: $0.0226, $0.0220 e $0.0076. Token in uscita: 18,162, 19,722 e 3,211.">
  </picture>
</p>

<p align="center">
  <sub>Mediana di 3 sessioni per ciascuna configurazione (senza Simplicio, Simplicio 3.14.0 e Simplicio 3.15.0). Claude Haiku 5.5 in Claude Code 2.1.330, 2026-11-22. Passi consegnati: 9 di 9 in ogni configurazione. La linea sottile su ogni barra va dalla sessione più bassa a quella più alta.<br>
  <a href="../benchmarks/2026-11-22-standard-benchmark.md">Metodo, dati e limiti</a></sub>
</p>

<p align="center">
  <sub>Da leggere insieme: un piccolo lavoro, tre sessioni per configurazione, un solo modello. Le verifiche esterne sono più ristrette dei prompt. Il picco di memoria è stato più alto: 375 MB contro 270 MB. Le build di Simplicio sono state compilate dai commit di release, con l'accesso disattivato.</sub>
</p>

<p align="center">Il modo in cui Simplicio ottiene questo risultato non è pubblicato. Le misure sì, comprese quelle in cui Simplicio perde.</p>

<p align="center">
  <b>Provalo:</b> <a href="#install">Installazione</a> · <a href="#first-run">Primo avvio</a><br>
  <a href="#what-simplicio-is">Cos'è</a> ·
  <a href="#the-measurement">Misurazione</a> ·
  <a href="#works-with-the-agent-you-already-use">Agenti</a> ·
  <a href="#command-line">Comandi</a> ·
  <a href="#safety-and-privacy">Privacy</a> ·
  <a href="#questions-people-ask">Domande</a> ·
  <a href="#documentation-and-community">Documentazione</a>
</p>

<a id="what-simplicio-is"></a>

## Cos'è Simplicio

Simplicio è un programma locale che dà all'agente di programmazione che usi già una modalità ultra-veloce, qualunque sia l'agente e qualunque sia il modello. I numeri di questa pagina vengono da un solo agente e da un solo modello; la sezione qui sotto dice esattamente che cosa è stato misurato.

- **Tieni il tuo agente e il tuo modello.** Simplicio non sostituisce Claude Code, Codex, Cursor o il modello che c'è dietro di loro.
- **Un solo binario firmato** si registra da sé negli agenti e gira sul tuo computer come server MCP STDIO locale.
- **Cambia la sessione.** Cambiano il suo tempo e il suo costo.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/diagram-where-simplicio-runs-dark.svg">
    <img src="../assets/diagram-where-simplicio-runs-light.svg" width="840" alt="Diagramma. Sul tuo computer: tu, il tuo agente di programmazione, Simplicio e il tuo repository. L'agente comunica con Simplicio tramite STDIO locale (MCP). L'agente comunica con il tuo provider di modelli come prima. Simplicio comunica con SimpleTI per le verifiche di accesso e di piano e con GitHub per la verifica delle release, senza contenuto del repository in nessuno dei due casi.">
  </picture>
</p>

<p align="center">
  <sub>Il flusso predefinito. <a href="#safety-and-privacy">L'elenco completo</a> riporta gli altri servizi.</sub>
</p>

<details>
<summary>MCP e STDIO</summary>

MCP è il Model Context Protocol, il modo con cui un agente di programmazione chiama strumenti esterni. STDIO significa che l'agente avvia direttamente il programma e gli parla attraverso il suo input e output standard.

Dà al tuo agente degli strumenti: una mappa del repository, un contesto limitato, modifiche strutturate e verifiche. [Gli strumenti principali](#works-with-the-agent-you-already-use) sono elencati più sotto.

Installi un solo binario nativo firmato. L'installer verifica la firma, poi registra Simplicio negli agenti che trova sul tuo computer.

</details>

<a id="the-measurement"></a>

## La misurazione

Un solo lavoro, eseguito allo stesso modo con e senza Simplicio: tre passi in una sessione di un solo agente, ciascun risultato verificato dall'esterno.

1. Costruisci un elenco utenti: un'API e una pagina con una tabella, ricerca e ordinamento.
2. Modificalo: togli una colonna, aggiungi un filtro per ruolo e una colonna con la data.
3. Aggiungi una registrazione: un endpoint `POST` che controlla i dati in ingresso, e una pagina con un modulo.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-sessions-dark.svg">
    <img src="../assets/benchmark-2026-11-22-sessions-light.svg" width="840" alt="Grafico a dispersione di ogni sessione, con il tempo dell'intero lavoro in orizzontale e il costo riportato dall'agente in verticale. Simplicio 3.15.0, rombi verdi: da 23 a 27 s e da $0.0071 a $0.0098. Simplicio 3.14.0, quadrati grigi: da 90 a 106 s e da $0.0214 a $0.0249. Senza Simplicio, cerchi vuoti: da 97 a 172 s e da $0.0186 a $0.0280.">
  </picture>
</p>

| Misura | Senza Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| Tempo del lavoro | 121 s<br><sub>97–172</sub> | 104 s<br><sub>90–106</sub> | **25 s**<br><sub>23–27</sub> |
| Costo riportato | $0.0226<br><sub>0.0186–0.0280</sub> | $0.0220<br><sub>0.0214–0.0249</sub> | **$0.0076**<br><sub>0.0071–0.0098</sub> |
| Richieste al modello | 25<br><sub>19–33</sub> | 18<br><sub>18–22</sub> | **10**<br><sub>10–10</sub> |
| Chiamate di strumento | 22<br><sub>16–30</sub> | 15<br><sub>15–19</sub> | **7**<br><sub>7–7</sub> |
| Token in uscita | 18,162<br><sub>15,599–23,328</sub> | 19,722<br><sub>18,764–24,997</sub> | **3,211**<br><sub>3,068–3,573</sub> |
| Token in ingresso | 34,691<br><sub>30,447–42,543</sub> | 34,141<br><sub>33,121–40,017</sub> | 18,755<br><sub>18,466–33,300</sub> |
| Tempo CPU | 8.5 s<br><sub>8.5–9.2</sub> | 10.0 s<br><sub>8.9–10.0</sub> | **5.3 s**<br><sub>5.3–5.5</sub> |
| Picco di memoria | **270 MB**<br><sub>248–274</sub> | 436 MB<br><sub>432–439</sub> | 375 MB<br><sub>365–379</sub> |
| Passi consegnati | 9 di 9 | 9 di 9 | 9 di 9 |

Mediana di 3 sessioni, dalla più bassa alla più alta sotto ogni valore. In grassetto il valore migliore di ogni riga, solo dove gli intervalli non si sovrappongono. "9 di 9" significa 3 passi in ciascuna delle 3 sessioni, e ogni passo ha superato ogni verifica esterna.

Richieste al modello e chiamate di strumento per sessione.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-work-dark.svg">
    <img src="../assets/benchmark-2026-11-22-work-light.svg" width="840" alt="Grafico a unità con un segno per ogni richiesta al modello o chiamata di strumento, mediana di 3 sessioni. Richieste al modello: 25 senza Simplicio, 18 con Simplicio 3.14.0 e 10 con Simplicio 3.15.0. Chiamate di strumento: 22, 15 e 7.">
  </picture>
</p>

Tempo per passo, su una scala comune.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-steps-dark.svg">
    <img src="../assets/benchmark-2026-11-22-steps-light.svg" width="840" alt="Tempo mediano per passo su una scala comune. Passo 1, costruzione: 57.3 s senza Simplicio, 53.7 s con Simplicio 3.14.0 e 5.8 s con Simplicio 3.15.0. Passo 2, modifica: 17.3 s, 15.2 s e 8.9 s. Passo 3, registrazione: 31.4 s, 27.5 s e 10.3 s.">
  </picture>
</p>

<details>
<summary>Numeri esatti per passo</summary>

Ogni cella contiene il tempo mediano e il costo mediano del passo:

| Passo | Senza Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. Costruzione | 57.3 s / $0.0111 | 53.7 s / $0.0137 | 5.8 s / $0.0022 |
| 2. Modifica | 17.3 s / $0.0040 | 15.2 s / $0.0032 | 8.9 s / $0.0023 |
| 3. Registrazione | 31.4 s / $0.0075 | 27.5 s / $0.0056 | 10.3 s / $0.0026 |

</details>

**Come leggerlo.** L'intero lavoro è stato 4.9 volte più veloce, a circa un terzo del costo; anche la sessione più veloce senza Simplicio (97.1 s) era 3.7 volte più lenta della sessione più lenta con 3.15.0 (26.6 s). [Metodo, limiti](../benchmarks/2026-11-22-standard-benchmark.md#limits)

<details>
<summary>Come è definito ogni numero</summary>

- I rapporti derivano dalle mediane non arrotondate. Rispetto alla release precedente, l'intero lavoro è stato 4.2 volte più veloce.
- Ogni mediana è calcolata separatamente, quindi i passi non sommano la mediana dell'intero lavoro.
- Caso peggiore: la sessione più veloce senza Simplicio (97.1 s) era comunque 3.7 volte più lenta della sessione più lenta con Simplicio 3.15.0 (26.6 s), e la sessione più economica senza Simplicio ($0.0186) costava comunque 1.9 volte tanto quanto la sessione più costosa con Simplicio ($0.0098).
- Il riferimento è Claude Code 2.1.330 con i suoi strumenti, senza server MCP e senza configurazione di Simplicio.
- Ogni passo è verificato dall'esterno della sessione: l'API viene chiamata via HTTP e le pagine vengono caricate in headless Chrome, cioè Chrome senza finestra.
- Le verifiche non controllano la casella di ricerca, l'ordinamento, il reindirizzamento dopo il salvataggio, l'aspetto della pagina né la qualità del codice.
- Una richiesta al modello è una chiamata al modello; una chiamata di strumento è un uso di uno strumento da parte dell'agente.
- Il costo riportato è il numero di token usati per il prezzo pubblicato del modello. Conta solo i token del modello. Non è una fattura.
- Gli intervalli dei token in ingresso si sovrappongono, quindi questa esecuzione non dichiara alcuna differenza nei token in ingresso.
- Quattro sessioni giravano insieme su un solo computer: confronta i tempi solo all'interno di questo giro.

</details>

<a id="where-simplicio-does-not-win"></a>

### Dove Simplicio non vince

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-memory-dark.svg">
    <img src="../assets/benchmark-2026-11-22-memory-light.svg" width="840" alt="Picco di memoria, mediana di 3 sessioni: 270 MB senza Simplicio, il più basso; 436 MB con Simplicio 3.14.0, il 61% in più; 375 MB con Simplicio 3.15.0, il 39% in più.">
  </picture>
</p>

- **Memoria.** Il picco di memoria è stato più alto del 39%: 375 MB contro 270 MB.
- **La release precedente non ha mostrato alcun guadagno su questo lavoro.** Simplicio 3.14.0 costava quanto senza Simplicio.
- **Uno script Python breve e una tantum.** Simplicio 3.10.8 è stato più lento (19.6 s contro 11.4 s) e non è stato misurato di nuovo.
- **Ciò che installi non è esattamente ciò che è stato misurato.** Le build sono state compilate dai commit di release, con l'accesso disattivato.
- **Il campione è piccolo.** Tre sessioni per configurazione, un solo modello, un solo progetto.

<details>
<summary>I limiti per esteso</summary>

- **Memoria.** Il picco di memoria è stato più alto del 39% rispetto all'agente senza Simplicio: 375 MB contro 270 MB.
- **La release precedente non ha mostrato alcun guadagno su questo lavoro.** Simplicio 3.14.0 costava quanto senza Simplicio, e la sua differenza di tempo rientra nella variabilità tra un'esecuzione e l'altra. Il guadagno è arrivato con 3.15.0.
- **Uno script Python breve e una tantum.** In un giro precedente, Simplicio 3.10.8 è stato più lento dell'agente senza Simplicio con ogni modello provato: con Claude Sonnet 5.5 in Claude Code, 19.6 s e $0.0548 contro 11.4 s e $0.0283. Non è stato misurato di nuovo con 3.15.0.
- **Ciò che installi non è esattamente ciò che è stato misurato.** Le build sono state compilate dai commit di release, con l'accesso e il processo in background disattivati. I download firmati non sono stati misurati.
- **Il campione è piccolo.** Tre sessioni per configurazione, un solo modello, un piccolo progetto nuovo, un computer, quattro sessioni alla volta; nessuna è stata scartata o ripetuta. I rapporti misurano questo lavoro, non il tuo, e non abbiamo misurato quanta parte del tuo lavoro gli somigli.

</details>

### Verificalo da solo

[Il report](../benchmarks/2026-11-22-standard-benchmark.md) pubblica i tre prompt (in portoghese, con una traduzione), ogni verifica esterna e ogni sessione; [il file dei dati](../benchmarks/2026-11-22-standard-benchmark.json) li contiene in formato JSON. L'infrastruttura di test non è pubblicata.

<a id="install"></a>

## Installazione

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

Su Windows usa `py -m pip install --upgrade simplicio-installer` e poi `simplicio install`.

L'installer verifica la release firmata e registra automaticamente Simplicio negli agenti che trova. Poi accedi con `simplicio auth login`.

<details>
<summary>Dettagli dell'installazione</summary>

- Scarica l'ultima release firmata per la tua piattaforma e verifica il suo SHA-256 e la sua firma Ed25519 prima di sostituire il binario installato.
- Il binario va in `~/.simplicio/bin/` (su Windows, `%USERPROFILE%\.simplicio\bin\`), e Simplicio viene registrato automaticamente negli agenti che trova. Se la registrazione fallisce, l'installer si ferma invece di segnalare il successo.
- Riavvia gli agenti già aperti, così ricaricano la loro configurazione. Se la cartella degli script Python non è nel tuo `PATH`, aggiungila prima.

**Accesso.** È richiesto l'accesso con Google, anche durante la beta. Esegui `simplicio auth login`, poi `simplicio auth status --json`, e prosegui quando lo stato riporta `active: true`. La registrazione funziona anche prima dell'accesso. Non incollare mai una password o un token nella configurazione di un agente.

Per verificare che Simplicio sia stato caricato, cerca `simplicio` nell'elenco dei server MCP dell'agente. In Claude Code, `/mcp` elenca i server connessi. Preferisci leggere prima l'installer? È [install.sh](../install.sh).

Per aggiornare, esegui di nuovo uno dei due installer quando vuoi: risolve sempre l'ultima release. `install.sh` e `install.ps1` si trovano nella radice di questo repository.

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

- `--doctor` verifica l'installazione.
- `--uninstall --keep-data` rimuove il binario installato e conserva i tuoi dati. Include anche lo stato dell'accesso Google di 30 giorni in `~/.simplicio/login.json`.
- `--uninstall --purge` rimuove solo lo stato gestito da Simplicio, compreso quello dell'accesso. Mantiene `~/.simplicio/.env`, dove possono trovarsi le credenziali dei provider. Il purge richiede `SIMPLICIO_CONFIRM_PURGE=1`.
- La disinstallazione non modifica la configurazione dei tuoi agenti. Le voci di Simplicio restano in ogni agente finché non le rimuovi nelle impostazioni di quell'agente.
- I dati nella cartella `.simplicio` di un progetto non vengono rimossi da `--keep-data`. Controlla su cosa agisce prima di scegliere `--purge`.

Dettagli completi: [INSTALL.md](../INSTALL.md).

</details>

<a id="first-run"></a>

## Primo avvio

```bash
simplicio version
cd my-project
simplicio onboard
```

`simplicio version` conferma il binario installato; `simplicio onboard` prepara il progetto. Poi apri l'agente in quel progetto.

<a id="works-with-the-agent-you-already-use"></a>

## Funziona con l'agente che già usi

L'installer affida la registrazione al componente di registrazione di Simplicio. Scrive la voce di Simplicio per gli agenti che sa configurare, tra cui Claude Code, Codex, Cursor, Visual Studio Code, OpenCode, Gemini CLI e Kiro.

Il registro [`plugins/simplicio/host-surfaces.json`](../plugins/simplicio/host-surfaces.json) elenca 43 id di agente; la matrice di compatibilità [`docs/hosts/compatibility-matrix.md`](../docs/hosts/compatibility-matrix.md) segna 12 come supportati e 29 come `unverified`. Tratta un'integrazione `unverified` come non testata.

<details>
<summary>Tutti i 43 agenti</summary>

- Il registro elenca 43 id di agente e indica come Simplicio raggiunge ciascuno: una voce MCP che Simplicio scrive (23), un plugin o un'estensione nativa (5), un pacchetto plugin portabile (4), una configurazione guidata da seguire da sé (9) o un altro strumento a riga di comando (2).
- La matrice non ha una riga per Codex e Gemini CLI. Anche dove il registro dice che Simplicio scrive la voce, tratta un'integrazione `unverified` come non testata.
- 23 agenti hanno una guida in [`docs/hosts/`](../docs/hosts/). Per gli agenti raggiunti tramite plugin, il plugin viene applicato in un passaggio separato che chiede il tuo consenso; [INSTALL.md](../INSTALL.md) lo descrive.

| Come Simplicio lo raggiunge | Numero | Agenti |
|---|---|---|
| Una voce MCP che Simplicio scrive | 23 | **xAI Grok Build**, MiMo Code, Amp, OpenClaude, Antigravity, **Pi**, **oh-my-pi**, Goose, Auggie, Autohand Code, Charm, Cline, Command Code, Continue, Droid, Kilocode, Kimi, Mistral Vibe, Rovo Dev, **Visual Studio Code**, **Meta Muse Code**, **OpenMausBot**, **OpenMuse (Python)** |
| Un plugin o un'estensione nativa | 5 | **Claude Code**, Codex, **OpenCode**, Hermes Agent, Gemini CLI |
| Un pacchetto plugin portabile | 4 | **Cursor**, GitHub Copilot, **Kiro**, Qwen Code |
| Una configurazione guidata da seguire da sé | 9 | Devin, Codebuff, CopilotKit OpenDots, CopilotKit OpenBot, agentes.chat, OpenAI dots, xAI Grok Bot, Meta Muse app, Cue by Manus |
| Un altro strumento a riga di comando | 2 | **OrcaDev / Orca ADE**, T3 Code |

In grassetto: la matrice di compatibilità segna l'agente come supportato.

</details>

Questi sono gli strumenti principali che il tuo agente riceve:

| Strumento | Cosa ti dà |
|---|---|
| `simplicio_map` | Una mappa compatta del repository, così l'agente si orienta |
| `simplicio_context` | Il contesto che serve a un compito, limitato, invece di interi file |
| `simplicio_edit` | Modifiche strutturate ai file da un piano preparato |
| `simplicio_validate` | Controlli di pipeline, test e consegna |
| `simplicio_run` | Un compito eseguito sotto il controllo di Simplicio |

[MCP-CONNECT.md](../MCP-CONNECT.md) descrive gli strumenti principali.

<details>
<summary>Configurazione manuale</summary>

Simplicio è un server MCP STDIO locale, quindi un agente in grado di avviare un server MCP locale può essere configurato per usarlo. Per ripetere la registrazione, esegui `simplicio mcp register`. Il comando del server è `simplicio serve --mcp --stdio`.

Se il tuo agente non è stato configurato automaticamente, aggiungi questa voce alla sua configurazione MCP. Sostituisci il percorso con il percorso assoluto del binario installato.

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

Codex legge TOML. Gli agenti avviano `command` direttamente, quindi non usare `~` e non affidarti all'espansione della shell. Nei percorsi Windows usa le barre normali, e sostituisci il nome utente di esempio.

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

Dove ogni agente conserva il suo file: [MCP-CONNECT.md](../MCP-CONNECT.md).

</details>

<a id="command-line"></a>

## Riga di comando

| Comando | Cosa ottieni |
|---|---|
| `simplicio map --repo . --for-llm markdown` | Una mappa strutturale compatta del repository, scritta per essere letta da un modello |
| `simplicio context --repo .` | Il contesto limitato per un compito |
| `simplicio memory query "query" --json` | Ciò che il progetto già sa, richiamato dalla sua memoria indicizzata, in formato JSON |
| `simplicio edit --plan plan.json --repo .` | Un insieme preparato di modifiche strutturate, applicate ai file |
| `simplicio run "task" --repo . --agents N` | Esecuzione di un compito con N agenti sotto il controllo di Simplicio |
| `simplicio loop` | Lavoro che va avanti a cicli finché converge |

I nomi che vedrai nei messaggi di Simplicio: Mapper osserva, Fast proietta o recupera, Dev CLI modifica, Runtime governa e Loop converge.

<a id="safety-and-privacy"></a>

## Sicurezza e privacy

Questa sezione descrive la versione 3.15.0.

- **Resta sul tuo computer.** Mappatura, contesto, modifiche e verifiche vengono eseguiti nel binario di Simplicio.
- **Verso SimpleTI (simpleti.com.br).** Solo verifiche di accesso e di piano, nessun contenuto del repository.
- **Verso GitHub.** Un controllo delle release che puoi disattivare.
- **Nessun dato analitico.** Simplicio non invia dati analitici, segnalazioni di crash né dati di utilizzo.
- **Verso i servizi che configuri.** Ricevono ciò che invia quella funzione, che può includere prompt e codice.
- **Due funzioni raggiungono un servizio aperto al pubblico su Internet senza alcuna configurazione.** La ricerca web (DuckDuckGo) e l'audit delle dipendenze (osv.dev); nessuna delle due invia il contenuto dei file.
- **Download.** Da GitHub; alcuni script di supporto scaricano anche strumenti da PyPI o npm.

<details>
<summary>I dettagli</summary>

- **Resta sul tuo computer.** Mappatura, contesto, modifiche e verifiche vengono eseguiti nel binario di Simplicio. Il risultato va al tuo agente, sullo stesso computer. I registri di utilizzo e di risparmio sono file locali. Ciò che il tuo agente invia al proprio provider di modelli lo decide l'agente, come prima.
- **Verso SimpleTI (simpleti.com.br).** Solo verifiche di accesso e di piano, senza contenuto del repository: nessun file, percorso di file, prompt o modifica.
  - Inviano il tuo token di accesso, la versione di Simplicio e il nome host del tuo computer. Una verifica facoltativa della licenza invia anche l'e-mail del tuo account.
  - Restituiscono l'e-mail, il nome e il piano del tuo account.
- **Verso GitHub.** Un controllo in background per una nuova release, al massimo circa una volta ogni 12 ore, senza inviare nulla su di te o sul tuo codice. Imposta `SIMPLICIO_DISABLE_AUTO_UPDATE=1` per disattivarlo. Un aggiornamento scarica il binario da GitHub e ne verifica SHA-256 e firma prima di sostituire quello vecchio.
- **Nessun dato analitico.** Simplicio 3.15.0 e i file che installa nei tuoi agenti sono stati verificati a questo scopo: nessuno invia dati analitici, segnalazioni di crash o dati di utilizzo. Gli hook che installa eseguono solo programmi locali (il binario di Simplicio e, per i plugin facoltativi, script locali); nessuno di essi contatta la rete.
- **Verso i servizi che configuri.** Un provider di modelli, GitHub, Jira, un notificatore di chat o una cache di team ricevono ciò che invia quella funzione, che può includere prompt e codice. Le richieste a un provider di modelli contengono un header che indica Simplicio come client.
- **Due funzioni raggiungono un servizio aperto al pubblico su Internet senza alcuna configurazione.** Nessuna delle due invia il contenuto dei file.
  - La ricerca web, quando viene eseguita, invia la query di ricerca a DuckDuckGo, a meno che tu non configuri un altro servizio di ricerca. Nella chat di Simplicio, un messaggio che sembra una domanda sul web può diventare quella query.
  - L'audit di sicurezza delle dipendenze, quando lo esegui, invia a osv.dev i nomi e le versioni delle tue dipendenze.
- **Download.** L'installer e il percorso di aggiornamento scaricano da GitHub. Alcuni script di supporto facoltativi scaricano i propri strumenti da PyPI o npm quando li esegui. Un plugin di agente che non trova il binario di Simplicio scarica l'installer ufficiale da GitHub, fissato a un commit e verificato con SHA-256.

**Release firmate.** Ogni release pubblica i propri binari con checksum SHA-256, firme Ed25519, una SBOM (un elenco di ciò che è nella build) e la provenienza della build.

Gli installer e il percorso di aggiornamento verificano il checksum e la firma prima di sostituire il binario installato. Per le release stabili, una firma mancante o non valida e un checksum non corrispondente sono errori bloccanti; il contratto è in [docs/UPDATE_SIGNATURE_CONTRACT.md](../docs/UPDATE_SIGNATURE_CONTRACT.md).

**Cosa modifica l'installer nel tuo agente.**

- Aggiunge una voce di Simplicio alla configurazione MCP dell'agente e mantiene il resto della configurazione.
- In Claude Code consente anche `mcp__simplicio__*`, così uno strumento di Simplicio non viene negato in modalità automatica.
- Negli agenti la cui interfaccia degli hook è stata verificata dall'installer, installa anche lì gli hook di Simplicio.
- La disinstallazione non annulla queste voci; la sezione Installazione dice come rimuoverle. [INSTALL.md](../INSTALL.md) dice che cosa scrive l'installer, e la guida di ogni agente in [`docs/hosts/`](../docs/hosts/) ne dà i dettagli.

</details>

## Anche in questo repository

<details>
<summary>App desktop (anteprima per macOS)</summary>

È pubblicata un'anteprima dell'app Desktop per macOS (Apple Silicon) come [Simplicio-3.8.47-arm64.dmg](https://github.com/simpletibr/simplicio/releases/download/v3.8.47/Simplicio-3.8.47-arm64.dmg). Il suo SHA-256 è in [DESKTOP-SHA256SUMS](../DESKTOP-SHA256SUMS), separato dai checksum dei binari di Simplicio. Il DMG non ha un file di firma e include il binario di Simplicio 3.8.47.

- L'app Desktop per Windows non è pubblicata. Su Windows, usa l'installazione da riga di comando descritta sopra.
- La firma con Apple Developer ID e la notarizzazione non sono state fatte. Il pacchetto è firmato ad-hoc, cioè senza un certificato sviluppatore Apple, e non si dichiara l'accettazione da parte di Gatekeeper, quindi macOS potrebbe avvisarti all'apertura.
- L'installazione da riga di comando descritta sopra è il percorso pubblico supportato finché non viene pubblicato un pacchetto Desktop firmato.

Dettagli: [docs/desktop/RELEASE.md](../docs/desktop/RELEASE.md).

</details>

<details>
<summary>Per i manutentori: il diagramma di flusso generato</summary>

- I comandi e gli strumenti documentati in README.md e MCP-CONNECT.md sono disegnati come un unico flusso, [docs/flow/simplicio.svg](../docs/flow/simplicio.svg), generato da un unico file sorgente, `docs/flow/simplicio.flow.json`.
- Rigeneralo con `python3 scripts/generate_flow.py` e verificane lo scostamento con `python3 scripts/generate_flow.py --check`.
- Il contratto che lo mantiene allineato a questa pagina e a MCP-CONNECT.md è `python3 -m pytest tests/test_flow_contract.py -q`.
- La verifica di importazione in Langflow è `scripts/verify_flow_langflow.py`, che si ferma in modo sicuro (exit 2, `status=blocked`) quando non è in esecuzione alcun server. Le prove sono in `docs/flow/evidence/` e `docs/flow/render/`; [docs/flow/README.md](../docs/flow/README.md) elenca i requisiti e come ripeterla.

</details>

<a id="questions-people-ask"></a>

## Domande frequenti

**Il confronto è equo?**<br>
Stesso agente, stesso modello, stessi prompt, stesso progetto e stesse verifiche esterne; il riferimento non ha Simplicio. Vedi [dove Simplicio non vince](#where-simplicio-does-not-win).

**Devo cambiare il mio agente o il mio modello?**<br>
No. Simplicio si inserisce nell'agente che già usi.

**Otterrò sempre questi numeri?**<br>
No. Misurano un solo lavoro, un modello e un computer.

**È open source?**<br>
No. Simplicio è proprietario: un binario firmato. Questo repository contiene installer, pacchetti, documentazione e dati.

**Come lo rimuovo?**<br>
Esegui `sh install.sh --uninstall --keep-data`, oppure `pwsh install.ps1 -Uninstall -KeepData` su Windows. Non modifica la configurazione dei tuoi agenti, quindi rimuovi le voci di Simplicio nelle impostazioni di ciascun agente.

**Mi serve un account?**<br>
Sì. È richiesto l'accesso con Google, anche durante la beta. Esegui `simplicio auth login`.

**Il mio codice esce dal mio computer?**<br>
Mappatura, contesto, modifiche e verifiche vengono eseguiti sul tuo computer; SimpleTI e GitHub non ricevono contenuto del repository. [Dettagli](#safety-and-privacy).

<a id="documentation-and-community"></a>

## Documentazione e community

- **Sito:** [simpleti.com.br/simplicio](https://simpleti.com.br/simplicio/)
- **Documentazione:** [simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)
- **Discord:** [Unisciti alla community](https://discord.gg/wM6tr7xVb)
- **Issue:** [tracker delle issue su GitHub](https://github.com/simpletibr/simplicio/issues)
- **Correlati:** Simplicio Video (hypit): `git clone https://github.com/hypit-ai/hypit.git simplicio-video`

<p align="center">
  <sub>© 2026 SimpleTI. Simplicio è un software proprietario registrato. Tutti i diritti riservati.</sub>
</p>
