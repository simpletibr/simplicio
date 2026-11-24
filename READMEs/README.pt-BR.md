<div align="center">

<img src="../assets/simplicio-icon-192.png" alt="Logotipo do Simplicio" width="96" height="96">

<h1>Simplicio</h1>

<p><b>UltraFast Mode for all.</b></p>

<p><b>Mesmo agente, mesmo modelo, mesma tarefa: 121&nbsp;s&nbsp;→&nbsp;25&nbsp;s, e $0.0226&nbsp;→&nbsp;$0.0076.</b></p>

<p>Sem o Simplicio → com o Simplicio 3.15.0. Mediana de 3 execuções de uma tarefa pequena de programação no Claude Code, com o Claude Haiku 5.5.</p>

<p>O Simplicio roda na sua máquina e adiciona ferramentas ao agente de programação que você já usa.</p>

<p>
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=2fe6a0&label=release" alt="Última versão"></a>
  <a href="https://simpleti.com.br/simplicio/docs"><img src="https://img.shields.io/badge/docs-simpleti.com.br-ffd23f" alt="Documentação"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Estrelas"></a>
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="Licença: proprietária">
</p>

<p>
  <a href="../README.md">English</a> ·
  Português (Brasil) ·
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
  <a href="README.ms-MY.md">Bahasa Melayu</a>
</p>

<p align="center"><sub>Este arquivo é uma tradução do <a href="../README.md">README em inglês</a>. Se os dois divergirem, a página em inglês é a referência. As figuras estão em inglês.</sub></p>

</div>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-dark.svg">
    <img src="../assets/benchmark-2026-11-22-light.svg" width="840" alt="Gráfico de barras comparando sem o Simplicio, Simplicio 3.14.0 e Simplicio 3.15.0 em três medidas, mediana de três sessões de cada. Tempo da tarefa inteira: 121 s sem o Simplicio, 104 s com o Simplicio 3.14.0 e 25 s com o Simplicio 3.15.0. Custo: $0.0226, $0.0220 e $0.0076. Tokens de saída: 18,162, 19,722 e 3,211.">
  </picture>
</p>

<p align="center">
  <sub>Mediana de 3 sessões de cada configuração (sem o Simplicio, Simplicio 3.14.0 e Simplicio 3.15.0). Claude Haiku 5.5 no Claude Code 2.1.330, 2026-11-22. Todas as configurações entregaram 9 de 9 etapas. A linha fina de cada barra vai da sessão de menor valor até a de maior valor.<br>
  <a href="../benchmarks/2026-11-22-standard-benchmark.md">Método, dados e limites</a></sub>
</p>

<p align="center">
  <sub>Leia junto com isto: uma tarefa pequena, três sessões por configuração, um modelo. As verificações externas cobrem menos do que os prompts pedem. O pico de memória foi maior: 375 MB contra 270 MB. Os builds do Simplicio foram compilados a partir dos commits das versões, com o login desativado.</sub>
</p>

<p align="center">Como o Simplicio chega a esse resultado não é publicado. As medições são publicadas, inclusive as em que ele perde.</p>

<p align="center">
  <b>Experimente:</b> <a href="#install">Instalação</a> · <a href="#first-run">Primeira execução</a><br>
  <a href="#what-simplicio-is">O que é</a> ·
  <a href="#the-measurement">Medição</a> ·
  <a href="#works-with-the-agent-you-already-use">Agentes</a> ·
  <a href="#command-line">Comandos</a> ·
  <a href="#safety-and-privacy">Privacidade</a> ·
  <a href="#questions-people-ask">Perguntas</a> ·
  <a href="#documentation-and-community">Documentação</a>
</p>

<a id="what-simplicio-is"></a>

## O que é o Simplicio

O Simplicio é um programa local que dá ao agente de programação que você já usa um modo ultrarrápido, seja qual for o agente e seja qual for o modelo. Os números desta página vêm de um único agente e de um único modelo; a seção abaixo diz exatamente o que foi medido.

- **Você mantém o seu agente e o seu modelo.** O Simplicio não substitui o Claude Code, o Codex, o Cursor nem o modelo que está por trás deles.
- **Um único binário assinado** se registra nos seus agentes e roda na sua máquina como um servidor MCP STDIO local.
- **O que muda é a sessão.** O tempo que ela leva e quanto custa.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/diagram-where-simplicio-runs-dark.svg">
    <img src="../assets/diagram-where-simplicio-runs-light.svg" width="840" alt="Diagrama. Na sua máquina: você, o seu agente de programação, o Simplicio e o seu repositório. O agente conversa com o Simplicio por STDIO local (MCP). O agente conversa com o seu provedor de modelo como antes. O Simplicio conversa com a SimpleTI para login e verificações de plano, e com o GitHub para verificar novas versões, sem conteúdo de repositório em nenhum dos dois.">
  </picture>
</p>

<p align="center">
  <sub>O fluxo padrão. A <a href="#safety-and-privacy">lista completa</a> traz os outros serviços.</sub>
</p>

<details>
<summary>MCP e STDIO</summary>

MCP é o Model Context Protocol, o padrão que um agente de programação usa para chamar ferramentas externas. STDIO significa que o agente executa o próprio programa e conversa com ele pela entrada e saída padrão.

Ele dá ferramentas ao seu agente. Um mapa do repositório, contexto limitado, edições estruturadas e verificações. [As ferramentas principais](#works-with-the-agent-you-already-use) estão listadas abaixo.

Você instala um único binário nativo assinado. O instalador verifica a assinatura e, depois, registra o Simplicio nos agentes que encontra na sua máquina.

</details>

<a id="the-measurement"></a>

## A medição

Uma tarefa, executada do mesmo jeito com e sem o Simplicio: três etapas em uma mesma sessão de agente, e o resultado de cada uma verificado de fora.

1. Construir uma listagem de usuários: uma API e uma página com tabela, busca e ordenação.
2. Alterá-la: remover uma coluna, adicionar um filtro por papel e uma coluna de data.
3. Adicionar um cadastro: um endpoint `POST` que valida os dados recebidos, e uma página com formulário.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-sessions-dark.svg">
    <img src="../assets/benchmark-2026-11-22-sessions-light.svg" width="840" alt="Gráfico de dispersão de todas as sessões, com o tempo da tarefa inteira na horizontal e o custo informado pelo agente na vertical. Simplicio 3.15.0, losangos verdes: de 23 a 27 s e de $0.0071 a $0.0098. Simplicio 3.14.0, quadrados cinza: de 90 a 106 s e de $0.0214 a $0.0249. Sem o Simplicio, círculos vazados: de 97 a 172 s e de $0.0186 a $0.0280.">
  </picture>
</p>

| Medida | Sem o Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| Tempo da tarefa | 121 s<br><sub>97–172</sub> | 104 s<br><sub>90–106</sub> | **25 s**<br><sub>23–27</sub> |
| Custo informado | $0.0226<br><sub>0.0186–0.0280</sub> | $0.0220<br><sub>0.0214–0.0249</sub> | **$0.0076**<br><sub>0.0071–0.0098</sub> |
| Requisições ao modelo | 25<br><sub>19–33</sub> | 18<br><sub>18–22</sub> | **10**<br><sub>10–10</sub> |
| Chamadas de ferramenta | 22<br><sub>16–30</sub> | 15<br><sub>15–19</sub> | **7**<br><sub>7–7</sub> |
| Tokens de saída | 18,162<br><sub>15,599–23,328</sub> | 19,722<br><sub>18,764–24,997</sub> | **3,211**<br><sub>3,068–3,573</sub> |
| Tokens de entrada | 34,691<br><sub>30,447–42,543</sub> | 34,141<br><sub>33,121–40,017</sub> | 18,755<br><sub>18,466–33,300</sub> |
| Tempo de CPU | 8.5 s<br><sub>8.5–9.2</sub> | 10.0 s<br><sub>8.9–10.0</sub> | **5.3 s**<br><sub>5.3–5.5</sub> |
| Pico de memória | **270 MB**<br><sub>248–274</sub> | 436 MB<br><sub>432–439</sub> | 375 MB<br><sub>365–379</sub> |
| Etapas entregues | 9 de 9 | 9 de 9 | 9 de 9 |

Mediana de 3 sessões, com a faixa do menor ao maior valor sob cada número. Em negrito, o melhor valor de cada linha, quando as faixas não se sobrepõem. "9 de 9" são 3 etapas em cada uma das 3 sessões, todas aprovadas em todas as verificações externas.

Requisições e chamadas de ferramenta por sessão.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-work-dark.svg">
    <img src="../assets/benchmark-2026-11-22-work-light.svg" width="840" alt="Gráfico de unidades, com uma marca por requisição ao modelo ou chamada de ferramenta, mediana de 3 sessões. Requisições ao modelo: 25 sem o Simplicio, 18 com o Simplicio 3.14.0 e 10 com o Simplicio 3.15.0. Chamadas de ferramenta: 22, 15 e 7.">
  </picture>
</p>

Tempo por etapa, em uma escala comum.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-steps-dark.svg">
    <img src="../assets/benchmark-2026-11-22-steps-light.svg" width="840" alt="Mediana do tempo por etapa em uma escala comum. Etapa 1, construção: 57.3 s sem o Simplicio, 53.7 s com o Simplicio 3.14.0 e 5.8 s com o Simplicio 3.15.0. Etapa 2, alteração: 17.3 s, 15.2 s e 8.9 s. Etapa 3, cadastro: 31.4 s, 27.5 s e 10.3 s.">
  </picture>
</p>

<details>
<summary>Números exatos por etapa</summary>

Cada célula traz a mediana do tempo e a mediana do custo da etapa:

| Etapa | Sem o Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. Construção | 57.3 s / $0.0111 | 53.7 s / $0.0137 | 5.8 s / $0.0022 |
| 2. Alteração | 17.3 s / $0.0040 | 15.2 s / $0.0032 | 8.9 s / $0.0023 |
| 3. Cadastro | 31.4 s / $0.0075 | 27.5 s / $0.0056 | 10.3 s / $0.0026 |

</details>

**Como ler.** A tarefa inteira rodou 4.9 vezes mais rápido, com cerca de um terço do custo; até a sessão mais rápida sem o Simplicio (97.1 s) foi 3.7 vezes mais lenta do que a mais lenta com o 3.15.0 (26.6 s). [Método e limites](../benchmarks/2026-11-22-standard-benchmark.md#limits)

<details>
<summary>Como cada número é definido</summary>

- As proporções vêm das medianas sem arredondamento. Em comparação com a versão anterior, a tarefa inteira rodou 4.2 vezes mais rápido.
- Cada mediana é calculada separadamente, então as etapas não somam a mediana da tarefa inteira.
- Pior caso: a sessão mais rápida sem o Simplicio (97.1 s) ainda foi 3.7 vezes mais lenta do que a sessão mais lenta com o Simplicio 3.15.0 (26.6 s), e a sessão mais barata sem ele ($0.0186) ainda custou 1.9 vezes o que custou a sessão mais cara com ele ($0.0098).
- A linha de base é o Claude Code 2.1.330 com as próprias ferramentas, sem servidor MCP e sem nenhuma configuração do Simplicio.
- Cada etapa é verificada de fora da sessão: a API é chamada por HTTP e as páginas são carregadas no Chrome headless, que é o Chrome sem janela.
- As verificações não testam a caixa de busca, a ordenação, o redirecionamento depois de salvar, a aparência da página nem a qualidade do código.
- Uma requisição ao modelo é uma chamada ao modelo; uma chamada de ferramenta é um uso de ferramenta feito pelo agente.
- O custo informado são os tokens usados vezes o preço publicado do modelo. Ele conta apenas os tokens do modelo. Não é uma fatura.
- As faixas de tokens de entrada se sobrepõem, então esta execução não afirma diferença nos tokens de entrada.
- Quatro sessões rodaram ao mesmo tempo em uma máquina: compare os tempos somente dentro desta rodada.

</details>

<a id="where-simplicio-does-not-win"></a>

### Onde o Simplicio não vence

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-memory-dark.svg">
    <img src="../assets/benchmark-2026-11-22-memory-light.svg" width="840" alt="Pico de memória, mediana de 3 sessões: 270 MB sem o Simplicio, o menor; 436 MB com o Simplicio 3.14.0, 61% a mais; 375 MB com o Simplicio 3.15.0, 39% a mais.">
  </picture>
</p>

- **Memória.** O pico de memória foi 39% maior: 375 MB contra 270 MB.
- **A versão anterior não mostrou ganho nesta tarefa.** O Simplicio 3.14.0 custou o mesmo que sem o Simplicio.
- **Um script Python curto e pontual.** O Simplicio 3.10.8 foi mais lento (19.6 s contra 11.4 s) e não foi medido de novo.
- **Uma página pequena, modelos fortes.** O Simplicio 3.15.0 foi de 14% a 47% mais lento.
- **O que você instala não é exatamente o que foi medido.** Os builds foram compilados a partir dos commits das versões, com o login desativado.
- **A amostra é pequena.** Três sessões por configuração, um modelo e um projeto.

<details>
<summary>Os limites completos</summary>

- **Memória.** O pico de memória foi 39% maior do que com o agente puro: 375 MB contra 270 MB.
- **A versão anterior não mostrou ganho nesta tarefa.** O Simplicio 3.14.0 custou o mesmo que sem o Simplicio, e a diferença de tempo dele está dentro da variação entre execuções. O ganho veio com a versão 3.15.0.
- **Um script Python curto e pontual.** Em uma rodada anterior, o Simplicio 3.10.8 foi mais lento do que o agente puro com todos os modelos testados: no Claude Sonnet 5.5 no Claude Code, 19.6 s e $0.0548 contra 11.4 s e $0.0283. Não foi medido de novo na versão 3.15.0.
- **Uma página pequena, modelos fortes.** Com o Sonnet 5.5 ou o Opus 5.5, o Simplicio 3.15.0 levou de 14% a 47% mais tempo e custou de 14% a 41% mais em 6 de 6 casos. Todas as páginas ficaram corretas nos dois casos. Sonnet 5.5, criação, mediana de 3: 24 s e $0.082 contra 20 s e $0.066. Uma correção está em andamento; ainda não está em uma versão.
- **O que você instala não é exatamente o que foi medido.** Os builds foram compilados a partir dos commits das versões, com o login e o processo em segundo plano desativados. Os downloads assinados não foram medidos.
- **A amostra é pequena.** Três sessões por configuração, um modelo, um projeto novo e pequeno, uma máquina, quatro sessões ao mesmo tempo; nenhuma foi descartada nem executada de novo. As proporções medem esta tarefa, não a sua, e não medimos quanto do seu trabalho se parece com ela.

</details>

### Confira por conta própria

[O relatório](../benchmarks/2026-11-22-standard-benchmark.md) publica os três prompts (em português, com uma tradução), cada verificação externa e cada sessão; [o arquivo de dados](../benchmarks/2026-11-22-standard-benchmark.json) os traz em JSON. O harness de testes não é publicado.

<a id="install"></a>

## Instalação

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

No Windows, execute `py -m pip install --upgrade simplicio-installer` e depois `simplicio install`.

O instalador verifica a versão assinada e registra o Simplicio automaticamente nos agentes que encontra. Depois, faça login com `simplicio auth login`.

<details>
<summary>Detalhes da instalação</summary>

- Ele baixa a versão assinada mais recente para a sua plataforma e verifica o SHA-256 e a assinatura Ed25519 dela antes de substituir o binário instalado.
- O binário fica em `~/.simplicio/bin/` (no Windows, `%USERPROFILE%\.simplicio\bin\`), e o Simplicio é registrado automaticamente nos agentes que o instalador encontrar. Se o registro falhar, o instalador para, em vez de informar sucesso.
- Reinicie qualquer agente que já esteja aberto para que ele recarregue a configuração. Se o diretório de scripts do Python não estiver no seu `PATH`, adicione-o antes.

**Fazer login.** É necessário fazer login com o Google, inclusive durante o beta. Execute `simplicio auth login`, depois `simplicio auth status --json`, e continue quando o status indicar `active: true`. O registro funciona antes do login. Nunca cole senha ou token na configuração de um agente.

Para confirmar que o Simplicio carregou, procure `simplicio` na lista de servidores MCP do agente. No Claude Code, `/mcp` lista os servidores conectados. Prefere ler o instalador antes? Ele está em [install.sh](../install.sh).

Para atualizar, execute qualquer um dos dois instaladores de novo, a qualquer momento: ele obtém a versão mais recente. `install.sh` e `install.ps1` ficam na raiz deste repositório.

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

- `--doctor` verifica a instalação.
- `--uninstall --keep-data` remove o binário instalado e mantém os seus dados. Isso inclui o estado do login com o Google, de 30 dias, em `~/.simplicio/login.json`.
- `--uninstall --purge` remove somente o estado que o Simplicio gerencia, incluindo o estado do login. Ele mantém `~/.simplicio/.env`, onde podem ficar as credenciais dos provedores. A purga exige `SIMPLICIO_CONFIRM_PURGE=1`.
- A desinstalação não edita a configuração dos seus agentes. As entradas do Simplicio ficam em cada agente até você removê-las nas configurações desse agente.
- Os dados dentro da pasta `.simplicio` de um projeto não são removidos por `--keep-data`. Confira o destino antes de escolher `--purge`.

Detalhes completos: [INSTALL.md](../INSTALL.md).

</details>

<a id="first-run"></a>

## Primeira execução

```bash
simplicio version
cd my-project
simplicio onboard
```

`simplicio version` verifica a instalação; `simplicio onboard` prepara o projeto. Depois, abra o seu agente nesse projeto.

<a id="works-with-the-agent-you-already-use"></a>

## Funciona com o agente que você já usa

O instalador delega o registro ao módulo de registro do próprio Simplicio. Ele grava a entrada do Simplicio nos agentes que sabe configurar, entre eles Claude Code, Codex, Cursor, Visual Studio Code, OpenCode, Gemini CLI e Kiro.

O catálogo [`plugins/simplicio/host-surfaces.json`](../plugins/simplicio/host-surfaces.json) lista 43 IDs de agentes; a matriz de compatibilidade [`docs/hosts/compatibility-matrix.md`](../docs/hosts/compatibility-matrix.md) marca 12 como suportados e 29 como `unverified`. Trate uma integração `unverified` como não testada.

<details>
<summary>Todos os 43 agentes</summary>

- O catálogo lista 43 IDs de agentes e informa como o Simplicio chega a cada um: uma entrada MCP que o Simplicio grava (23), um plugin ou extensão nativa (5), um pacote de plugin portátil (4), uma configuração guiada que você segue por conta própria (9) ou outra ferramenta de linha de comando (2).
- A matriz não tem linha para o Codex nem para o Gemini CLI. Mesmo quando o catálogo diz que o Simplicio grava a entrada, trate uma integração `unverified` como não testada.
- 23 agentes têm um guia em [`docs/hosts/`](../docs/hosts/). Nos agentes alcançados por meio de um plugin, o plugin é aplicado em uma etapa separada, que pede o seu consentimento, e o [INSTALL.md](../INSTALL.md) descreve essa etapa.

| Como o Simplicio alcança o agente | Quantidade | Agentes |
|---|---|---|
| Uma entrada MCP que o Simplicio grava | 23 | **xAI Grok Build**, MiMo Code, Amp, OpenClaude, Antigravity, **Pi**, **oh-my-pi**, Goose, Auggie, Autohand Code, Charm, Cline, Command Code, Continue, Droid, Kilocode, Kimi, Mistral Vibe, Rovo Dev, **Visual Studio Code**, **Meta Muse Code**, **OpenMausBot**, **OpenMuse (Python)** |
| Um plugin ou extensão nativa | 5 | **Claude Code**, Codex, **OpenCode**, Hermes Agent, Gemini CLI |
| Um pacote de plugin portátil | 4 | **Cursor**, GitHub Copilot, **Kiro**, Qwen Code |
| Uma configuração guiada que você segue por conta própria | 9 | Devin, Codebuff, CopilotKit OpenDots, CopilotKit OpenBot, agentes.chat, OpenAI dots, xAI Grok Bot, Meta Muse app, Cue by Manus |
| Outra ferramenta de linha de comando | 2 | **OrcaDev / Orca ADE**, T3 Code |

Em negrito: a matriz de compatibilidade marca o agente como suportado.

</details>

Estas são as ferramentas principais que o seu agente recebe:

| Ferramenta | O que ela oferece |
|---|---|
| `simplicio_map` | Um mapa compacto do repositório, para o agente se orientar |
| `simplicio_context` | O contexto que uma tarefa precisa, limitado, em vez de arquivos inteiros |
| `simplicio_edit` | Edições estruturadas de arquivos a partir de um plano preparado |
| `simplicio_validate` | Verificações de pipeline, de testes e de entrega |
| `simplicio_run` | Uma execução de tarefa sob controle do Simplicio |

O [MCP-CONNECT.md](../MCP-CONNECT.md) descreve as ferramentas principais.

<details>
<summary>Configuração manual</summary>

O Simplicio é um servidor MCP STDIO local, então qualquer agente que consiga iniciar um servidor MCP local pode ser apontado para ele. Para repetir o registro, execute `simplicio mcp register`. O comando do servidor é `simplicio serve --mcp --stdio`.

Se o seu agente não foi configurado para você, adicione esta entrada à configuração MCP dele. Substitua o caminho pelo caminho absoluto do binário instalado.

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

O Codex lê TOML. Os agentes iniciam `command` diretamente, então não use `~` nem dependa da expansão do shell. Use barras normais nos caminhos do Windows e troque o nome de usuário de exemplo.

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

Onde cada agente guarda o seu arquivo: [MCP-CONNECT.md](../MCP-CONNECT.md).

</details>

<a id="command-line"></a>

## Linha de comando

| Comando | O que você obtém |
|---|---|
| `simplicio map --repo . --for-llm markdown` | Um mapa estrutural compacto do repositório, escrito para um modelo ler |
| `simplicio context --repo .` | O contexto limitado de uma tarefa |
| `simplicio memory query "query" --json` | O que o projeto já sabe, recuperado da memória indexada dele, em JSON |
| `simplicio edit --plan plan.json --repo .` | Um conjunto preparado de edições estruturadas, aplicado aos arquivos |
| `simplicio run "task" --repo . --agents N` | Uma execução de tarefa com N agentes sob controle do Simplicio |
| `simplicio loop` | Trabalho que segue em rodadas até convergir |

Os nomes que você verá nas mensagens do Simplicio: Mapper observa, Fast projeta ou recupera, Dev CLI edita, Runtime governa e Loop converge.

<a id="safety-and-privacy"></a>

## Segurança e privacidade

Esta seção descreve a versão 3.15.0.

- **Fica na sua máquina.** O mapeamento, o contexto, as edições e as verificações rodam dentro do binário do Simplicio.
- **Para a SimpleTI (simpleti.com.br).** Somente verificações de login e de plano, sem conteúdo de repositório.
- **Para o GitHub.** Uma verificação de novas versões, que você pode desligar.
- **Sem analytics.** O Simplicio não envia analytics, relatórios de falhas nem dados de uso.
- **Para serviços que você configura.** Eles recebem o que aquele recurso envia, o que pode incluir prompts e código.
- **Dois recursos chegam a um serviço aberto ao público na internet sem nenhuma configuração.** A busca na web (DuckDuckGo) e a auditoria de dependências (osv.dev); nenhum dos dois envia conteúdo de arquivos.
- **Downloads.** Do GitHub; alguns scripts auxiliares também buscam ferramentas no PyPI ou no npm.

<details>
<summary>Os detalhes</summary>

- **Fica na sua máquina.** O mapeamento, o contexto, as edições e as verificações rodam dentro do binário do Simplicio. Ele entrega os resultados ao seu agente na mesma máquina. Os registros de uso e de economia são arquivos locais. O que o seu agente envia ao próprio provedor de modelo é decidido pelo agente, como antes.
- **Para a SimpleTI (simpleti.com.br).** Somente verificações de login e de plano, sem conteúdo de repositório: nenhum arquivo, nenhum caminho de arquivo, nenhum prompt e nenhuma edição.
  - Elas levam o seu token de login, a versão do Simplicio e o nome do host do seu computador. Uma consulta de licença opcional também leva o e-mail da sua conta.
  - Elas devolvem o e-mail, o nome e o plano da sua conta.
- **Para o GitHub.** Uma verificação em segundo plano por nova versão, no máximo cerca de uma vez a cada 12 horas, que não leva nada sobre você nem sobre o seu código. Defina `SIMPLICIO_DISABLE_AUTO_UPDATE=1` para desligá-la. Uma atualização baixa o binário do GitHub e verifica o SHA-256 e a assinatura dele antes de substituir o antigo.
- **Sem analytics.** O Simplicio 3.15.0 e os arquivos que ele instala nos seus agentes foram verificados para isso: nenhum envia analytics, relatórios de falhas ou dados de uso. Os hooks que ele instala executam somente programas locais (o binário do Simplicio e, para os plugins opcionais, scripts locais); nenhum deles acessa a rede.
- **Para serviços que você configura.** Um provedor de modelo, o GitHub, o Jira, um notificador de chat ou um cache de equipe recebem o que aquele recurso envia, o que pode incluir prompts e código. As requisições a um provedor de modelo levam um cabeçalho que identifica o Simplicio como cliente.
- **Dois recursos chegam a um serviço aberto ao público na internet sem nenhuma configuração.** Nenhum dos dois envia conteúdo de arquivos.
  - A busca na web, quando é executada, envia a consulta de busca ao DuckDuckGo, a menos que você configure outro serviço de busca. No chat próprio do Simplicio, uma mensagem que pareça uma pergunta sobre a web pode virar essa consulta.
  - A auditoria de segurança das dependências, quando você a executa, envia os nomes e as versões das suas dependências ao osv.dev.
- **Downloads.** O instalador e o caminho de atualização baixam do GitHub. Alguns scripts auxiliares opcionais buscam as próprias ferramentas no PyPI ou no npm quando você os executa. Se um plugin de agente iniciar e não encontrar o binário do Simplicio, ele baixa o instalador oficial do GitHub, fixado em um commit e verificado por SHA-256.

**Versões assinadas.** Cada versão publica os seus binários com somas de verificação SHA-256, assinaturas Ed25519, um SBOM (uma lista do que está no build) e a proveniência do build.

Os instaladores e o caminho de atualização verificam a soma e a assinatura antes de substituir o binário instalado. Para versões estáveis, uma assinatura ausente ou inválida e uma soma de verificação divergente são falhas graves; o contrato está em [docs/UPDATE_SIGNATURE_CONTRACT.md](../docs/UPDATE_SIGNATURE_CONTRACT.md).

**O que o instalador altera no seu agente.**

- Ele adiciona uma entrada do Simplicio à configuração MCP do agente e mantém o restante da configuração.
- No Claude Code, ele também libera `mcp__simplicio__*`, para que nenhuma ferramenta do Simplicio seja negada no modo automático.
- Nos agentes cuja interface de hooks o instalador tenha verificado, ele também instala os hooks do Simplicio ali.
- A desinstalação não desfaz essas entradas. A seção Instalação diz como removê-las. O [INSTALL.md](../INSTALL.md) descreve o que o instalador grava, e o guia de cada agente em [`docs/hosts/`](../docs/hosts/) traz o detalhe.

</details>

## Também neste repositório

<details>
<summary>Aplicativo Desktop (prévia para macOS)</summary>

Uma prévia do Desktop para macOS (Apple Silicon) é publicada como [Simplicio-3.8.47-arm64.dmg](https://github.com/simpletibr/simplicio/releases/download/v3.8.47/Simplicio-3.8.47-arm64.dmg). O SHA-256 dela está em [DESKTOP-SHA256SUMS](../DESKTOP-SHA256SUMS), separado das somas de verificação dos binários do Simplicio. O DMG não tem arquivo de assinatura e inclui o binário do Simplicio 3.8.47.

- O Desktop para Windows não é publicado. No Windows, siga a instalação pela linha de comando acima.
- A assinatura com Apple Developer ID e a notarização não foram feitas. O pacote tem assinatura ad-hoc, ou seja, sem certificado de desenvolvedor da Apple, e não há afirmação de aceitação pelo Gatekeeper, então o macOS pode mostrar um aviso quando você o abrir.
- A instalação pela linha de comando acima é o caminho público e suportado até que um pacote assinado do Desktop seja publicado.

Detalhes: [docs/desktop/RELEASE.md](../docs/desktop/RELEASE.md).

</details>

<details>
<summary>Para mantenedores: o diagrama de fluxo gerado</summary>

- Os comandos e as ferramentas documentados no README.md e no MCP-CONNECT.md são representados em um único fluxo, [docs/flow/simplicio.svg](../docs/flow/simplicio.svg), gerado a partir de um arquivo fonte, `docs/flow/simplicio.flow.json`.
- Gere de novo com `python3 scripts/generate_flow.py` e verifique se há divergência com `python3 scripts/generate_flow.py --check`.
- O contrato que mantém o fluxo em sintonia com esta página e com o MCP-CONNECT.md é `python3 -m pytest tests/test_flow_contract.py -q`.
- A verificação de importação no Langflow é `scripts/verify_flow_langflow.py`, que falha de forma fechada (saída 2, `status=blocked`) quando nenhum servidor está em execução. As evidências ficam em `docs/flow/evidence/` e `docs/flow/render/`; [docs/flow/README.md](../docs/flow/README.md) traz os requisitos e como repetir o processo.

</details>

<a id="questions-people-ask"></a>

## Perguntas frequentes

**A comparação é justa?**<br>
Mesmo agente, modelo, prompts, projeto e verificações externas; a linha de base não tem o Simplicio. Veja [onde o Simplicio não vence](#where-simplicio-does-not-win).

**Preciso trocar de agente ou de modelo?**<br>
Não. O Simplicio se conecta ao agente que você já usa.

**Eu sempre vou ter esses números?**<br>
Não. Eles medem uma tarefa, um modelo e uma máquina.

**É código aberto?**<br>
Não. O Simplicio é proprietário: um binário assinado. Este repositório reúne os instaladores, os pacotes, a documentação e os dados.

**Como removo?**<br>
Execute `sh install.sh --uninstall --keep-data`, ou `pwsh install.ps1 -Uninstall -KeepData` no Windows. Ele não edita a configuração dos seus agentes, então remova as entradas do Simplicio nas configurações de cada agente.

**Preciso de uma conta?**<br>
Sim. É necessário fazer login com o Google, inclusive durante o beta. Execute `simplicio auth login`.

**Meu código sai da minha máquina?**<br>
Mapeamento, contexto, edições e verificações rodam na sua máquina; a SimpleTI e o GitHub não recebem conteúdo de repositório. [Detalhes](#safety-and-privacy).

<a id="documentation-and-community"></a>

## Documentação e comunidade

- **Site:** [simpleti.com.br/simplicio](https://simpleti.com.br/simplicio/)
- **Documentação:** [simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)
- **Discord:** [Entre na comunidade](https://discord.gg/wM6tr7xVb)
- **Issues:** [Rastreador de issues do GitHub](https://github.com/simpletibr/simplicio/issues)
- **Relacionado:** Simplicio Video (hypit): `git clone https://github.com/hypit-ai/hypit.git simplicio-video`

<p align="center">
  <sub>© 2026 SimpleTI. O Simplicio é um software proprietário registrado. Todos os direitos reservados.</sub>
</p>
