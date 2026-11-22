<div align="center">

<img src="../assets/simplicio-icon-192.png" alt="Logotipo de Simplicio" width="96" height="96">

<h1>Simplicio</h1>

<p><b>UltraFast Mode for all.</b></p>

<p><b>Mismo agente, mismo modelo, mismo trabajo: 121&nbsp;s&nbsp;→&nbsp;25&nbsp;s, y $0.0226&nbsp;→&nbsp;$0.0076.</b></p>

<p>Sin Simplicio → con Simplicio 3.15.0. Mediana de 3 ejecuciones de un trabajo pequeño de programación en Claude Code con Claude Haiku 5.5.</p>

<p>Simplicio se ejecuta en tu equipo y añade herramientas al agente de programación que ya usas.</p>

<p>
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=2fe6a0&label=release" alt="Última versión"></a>
  <a href="https://simpleti.com.br/simplicio/docs"><img src="https://img.shields.io/badge/docs-simpleti.com.br-ffd23f" alt="Documentación"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Estrellas"></a>
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="Licencia: propietaria">
</p>

<p>
  <a href="../README.md">English</a> ·
  <a href="README.pt-BR.md">Português (Brasil)</a> ·
  Español ·
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

<p align="center"><sub>Este archivo es una traducción del <a href="../README.md">README en inglés</a>. Si hay diferencias, la página en inglés es la referencia. Los gráficos e ilustraciones están en inglés.</sub></p>

</div>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-dark.svg">
    <img src="../assets/benchmark-2026-11-22-light.svg" width="840" alt="Gráfico de barras que compara sin Simplicio, Simplicio 3.14.0 y Simplicio 3.15.0 en tres medidas, mediana de tres sesiones de cada escenario. Tiempo del trabajo completo: 121 s sin Simplicio, 104 s con Simplicio 3.14.0 y 25 s con Simplicio 3.15.0. Coste: $0.0226, $0.0220 y $0.0076. Tokens de salida: 18,162, 19,722 y 3,211.">
  </picture>
</p>

<p align="center">
  <sub>Mediana de 3 sesiones por escenario (sin Simplicio, Simplicio 3.14.0 y Simplicio 3.15.0). Claude Haiku 5.5 en Claude Code 2.1.330, 2026-11-22. Cada escenario entregó 9 de 9 pasos. La línea fina de cada barra va de la sesión más baja a la más alta.<br>
  <a href="../benchmarks/2026-11-22-standard-benchmark.md">Método, datos y límites</a></sub>
</p>

<p align="center">
  <sub>Léelo junto con esto: un trabajo pequeño, tres sesiones por escenario, un modelo. Las comprobaciones externas cubren menos de lo que piden los prompts. El pico de memoria fue mayor: 375 MB frente a 270 MB. Las compilaciones de Simplicio se generaron a partir de los commits de publicación, con el inicio de sesión desactivado.</sub>
</p>

<p align="center">No se publica cómo logra Simplicio este resultado. Sí se publican las mediciones, incluidas las que pierde.</p>

<p align="center">
  <b>Pruébalo:</b> <a href="#install">Instalación</a> · <a href="#first-run">Primera ejecución</a><br>
  <a href="#what-simplicio-is">Qué es</a> ·
  <a href="#the-measurement">Medición</a> ·
  <a href="#works-with-the-agent-you-already-use">Agentes</a> ·
  <a href="#command-line">Comandos</a> ·
  <a href="#safety-and-privacy">Privacidad</a> ·
  <a href="#questions-people-ask">Preguntas</a> ·
  <a href="#documentation-and-community">Documentación</a>
</p>

<a id="what-simplicio-is"></a>

## Qué es Simplicio

Simplicio es un programa local que da al agente de programación que ya usas un modo ultrarrápido, sea cual sea el agente y sea cual sea el modelo. Los números de esta página salen de un solo agente y un solo modelo; la sección de abajo dice exactamente qué se midió.

- **Conservas tu agente y tu modelo.** Simplicio no reemplaza a Claude Code, Codex, Cursor ni el modelo que haya detrás de ellos.
- **Instalas un único binario nativo firmado.** El instalador verifica la firma y luego registra Simplicio en los agentes que encuentra en tu equipo.
- **Se ejecuta en tu equipo.** Tu agente lo inicia como un servidor MCP local por STDIO. MCP es el Model Context Protocol, la forma estándar en que un agente de programación llama a herramientas externas. STDIO significa que el agente lanza el programa por sí mismo y se comunica con él a través de su entrada y salida estándar.
- **Da herramientas a tu agente.** Un mapa del repositorio, contexto acotado, ediciones estructuradas y comprobaciones. [Las herramientas principales](#works-with-the-agent-you-already-use) se enumeran más abajo.
- **Lo que cambia es la sesión.** Cuánto tarda y cuánto cuesta. La siguiente sección muestra cuánto, y dónde no ayuda.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/diagram-where-simplicio-runs-dark.svg">
    <img src="../assets/diagram-where-simplicio-runs-light.svg" width="840" alt="Diagrama. En tu equipo: tú, tu agente de programación, Simplicio y tu repositorio. El agente se comunica con Simplicio por STDIO local (MCP). El agente se comunica con tu proveedor de modelos como antes. Simplicio se comunica con SimpleTI para el inicio de sesión y las comprobaciones del plan, y con GitHub para comprobar si hay una versión nueva, sin contenido del repositorio en ninguno de los dos casos.">
  </picture>
</p>

<p align="center">
  <sub>El gráfico muestra lo que ocurre por defecto. La lista completa, incluidas las funciones que llegan a otros servicios, está en <a href="#safety-and-privacy">Qué envía Simplicio, y a quién</a>, dentro de Seguridad y privacidad.</sub>
</p>

<a id="the-measurement"></a>

## La medición

Un mismo trabajo, ejecutado de la misma forma con y sin Simplicio. El trabajo es una sesión de agente con tres pasos en la misma conversación:

1. Construir un listado de usuarios: una API y una página con una tabla, búsqueda y ordenación.
2. Modificarlo: quitar una columna, añadir un filtro por rol y una columna de fecha.
3. Añadir un registro sencillo: un endpoint `POST` que valida su entrada, y una página con un formulario.

Después de cada paso, el resultado se comprueba desde fuera de la sesión. Se llama a la API por HTTP y las páginas se cargan en Chrome sin interfaz gráfica, es decir, sin ventana. Todos los escenarios usaron el mismo agente y el mismo modelo: Claude Code 2.1.330 con Claude Haiku 5.5. La línea base es Claude Code 2.1.330 con sus propias herramientas, sin servidor MCP y sin configuración de Simplicio. Las comprobaciones no prueban el cuadro de búsqueda, la ordenación, la redirección tras guardar, el aspecto de la página ni la calidad del código.

Cada sesión aparece en este gráfico, no solo las medianas.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-sessions-dark.svg">
    <img src="../assets/benchmark-2026-11-22-sessions-light.svg" width="840" alt="Gráfico de dispersión de todas las sesiones, con el tiempo del trabajo completo en horizontal y el coste informado por el agente en vertical. Simplicio 3.15.0, rombos verdes: de 23 a 27 s y de $0.0071 a $0.0098. Simplicio 3.14.0, cuadrados grises: de 90 a 106 s y de $0.0214 a $0.0249. Sin Simplicio, círculos huecos: de 97 a 172 s y de $0.0186 a $0.0280.">
  </picture>
</p>

Mediana de 3 sesiones por escenario. La línea pequeña bajo cada valor indica la sesión más baja y la más alta.

| Medida | Sin Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| Tiempo del trabajo | 121 s<br><sub>97–172</sub> | 104 s<br><sub>90–106</sub> | **25 s**<br><sub>23–27</sub> |
| Coste informado | $0.0226<br><sub>0.0186–0.0280</sub> | $0.0220<br><sub>0.0214–0.0249</sub> | **$0.0076**<br><sub>0.0071–0.0098</sub> |
| Solicitudes al modelo | 25<br><sub>19–33</sub> | 18<br><sub>18–22</sub> | **10**<br><sub>10–10</sub> |
| Llamadas a herramientas | 22<br><sub>16–30</sub> | 15<br><sub>15–19</sub> | **7**<br><sub>7–7</sub> |
| Tokens de salida | 18,162<br><sub>15,599–23,328</sub> | 19,722<br><sub>18,764–24,997</sub> | **3,211**<br><sub>3,068–3,573</sub> |
| Tokens de entrada | 34,691<br><sub>30,447–42,543</sub> | 34,141<br><sub>33,121–40,017</sub> | 18,755<br><sub>18,466–33,300</sub> |
| Tiempo de CPU | 8.5 s<br><sub>8.5–9.2</sub> | 10.0 s<br><sub>8.9–10.0</sub> | **5.3 s**<br><sub>5.3–5.5</sub> |
| Pico de memoria | **270 MB**<br><sub>248–274</sub> | 436 MB<br><sub>432–439</sub> | 375 MB<br><sub>365–379</sub> |
| Pasos entregados | 9 de 9 | 9 de 9 | 9 de 9 |

En negrita aparece el mejor valor de cada fila, solo cuando su rango no se solapa con los demás. Los rangos de tokens de entrada se solapan, así que esta ejecución no afirma ninguna diferencia en tokens de entrada. «9 de 9» equivale a 3 pasos en cada una de 3 sesiones, y cada paso superó todas las comprobaciones externas. El tiempo del trabajo es el tiempo de todo el trabajo. Una solicitud al modelo es una llamada al modelo, y una llamada a herramienta es un uso de una herramienta por parte del agente. El coste informado es el que muestra el agente: los tokens usados multiplicados por el precio publicado del modelo. Solo cuenta los tokens del modelo. No es una factura.

Lo que cambió en la sesión, en recuento: el modelo hizo menos solicitudes, y el agente hizo menos llamadas a herramientas.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-work-dark.svg">
    <img src="../assets/benchmark-2026-11-22-work-light.svg" width="840" alt="Gráfico de unidades con una marca por cada solicitud al modelo o llamada a herramienta, mediana de 3 sesiones. Solicitudes al modelo: 25 sin Simplicio, 18 con Simplicio 3.14.0 y 10 con Simplicio 3.15.0. Llamadas a herramientas: 22, 15 y 7.">
  </picture>
</p>

Tiempo por paso, en una escala común.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-steps-dark.svg">
    <img src="../assets/benchmark-2026-11-22-steps-light.svg" width="840" alt="Mediana del tiempo por paso, en una escala común. Paso 1, construir: 57.3 s sin Simplicio, 53.7 s con Simplicio 3.14.0 y 5.8 s con Simplicio 3.15.0. Paso 2, modificar: 17.3 s, 15.2 s y 8.9 s. Paso 3, registrar: 31.4 s, 27.5 s y 10.3 s.">
  </picture>
</p>

Cada mediana se calcula por separado, así que los pasos no suman la mediana del trabajo completo.

<details>
<summary>Cifras exactas por paso</summary>

Cada celda muestra la mediana del tiempo y la mediana del coste del paso:

| Paso | Sin Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. Construir | 57.3 s / $0.0111 | 53.7 s / $0.0137 | 5.8 s / $0.0022 |
| 2. Modificar | 17.3 s / $0.0040 | 15.2 s / $0.0032 | 8.9 s / $0.0023 |
| 3. Registrar | 31.4 s / $0.0075 | 27.5 s / $0.0056 | 10.3 s / $0.0026 |

</details>

**Cómo leerlo.** Las proporciones se calculan con las medianas sin redondear. Frente al mismo agente sin Simplicio, el trabajo completo fue 4.9 veces más rápido y costó alrededor de un tercio. Frente a la versión anterior, fue 4.2 veces más rápido. En la sesión, el modelo hizo 10 solicitudes en lugar de 25 y generó 3,211 tokens de salida en lugar de 18,162, y el trabajo superó las mismas comprobaciones externas. Peor caso: la sesión más rápida sin Simplicio (97.1 s) seguía siendo 3.7 veces más lenta que la sesión más lenta con Simplicio 3.15.0 (26.6 s), y la sesión más barata sin Simplicio ($0.0186) seguía costando 1.9 veces más que la más cara con Simplicio ($0.0098). La línea base es Claude Code 2.1.330 con sus propias herramientas, sin servidor MCP y sin configuración de Simplicio. El coste cuenta solo los tokens del modelo. Las sesiones se ejecutaron cuatro a la vez en un mismo equipo, así que compara los tiempos solo dentro de esta ronda.

<a id="where-simplicio-does-not-win"></a>

### Dónde Simplicio no gana

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-memory-dark.svg">
    <img src="../assets/benchmark-2026-11-22-memory-light.svg" width="840" alt="Pico de memoria, mediana de 3 sesiones: 270 MB sin Simplicio, la más baja; 436 MB con Simplicio 3.14.0, un 61% más; 375 MB con Simplicio 3.15.0, un 39% más.">
  </picture>
</p>

- **Memoria.** El pico de memoria fue un 39% mayor que con el agente sin Simplicio: 375 MB frente a 270 MB.
- **La versión anterior no mostró mejora en este trabajo.** Simplicio 3.14.0 costó lo mismo que sin Simplicio, y su diferencia de tiempo está dentro de la variación entre ejecuciones. La mejora de esta página llegó con 3.15.0.
- **Un script corto de Python de uso puntual.** En una ronda anterior, Simplicio 3.10.8 fue más lento que el agente sin Simplicio con todos los modelos probados. Con Claude Sonnet 5.5 en Claude Code tardó 19.6 s y $0.0548, frente a 11.4 s y $0.0283 sin Simplicio. Esa tarea no se ha vuelto a medir con 3.15.0.
- **Lo que instalas no es exactamente lo que se midió.** Las compilaciones se generaron a partir de los commits de publicación, con el inicio de sesión desactivado y el proceso en segundo plano desactivado. Las descargas firmadas no se midieron.
- **La muestra es pequeña.** Tres sesiones por escenario, un modelo, un proyecto nuevo y pequeño, un equipo, cuatro sesiones a la vez. Lee las proporciones como una medición de este trabajo, no como una promesa para el tuyo. De estos tres escenarios no se descartó ni se repitió ninguna sesión. No hemos medido cuánto de tu trabajo se parece a este.

### Compruébalo tú mismo

[El informe](../benchmarks/2026-11-22-standard-benchmark.md) publica los tres prompts (en portugués, con una traducción), una descripción de cada comprobación externa y los números por sesión; [el archivo de datos](../benchmarks/2026-11-22-standard-benchmark.json) los tiene en JSON. El arnés de pruebas no se publica. Ejecuta los mismos tres prompts en tu propio agente, con Simplicio activado y desactivado, en un proyecto pequeño tuyo, y compara tus propios tiempos y tu propia factura.

<a id="install"></a>

## Instalación

Instala el binario nativo firmado. Elige una de estas vías.

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

En Windows, usa `py -m pip install --upgrade simplicio-installer` y después `simplicio install`. Si el directorio de scripts de Python no está en tu `PATH`, añádelo primero.

El instalador descarga la última versión firmada para tu plataforma y comprueba su SHA-256 y su firma Ed25519. Solo entonces reemplaza el binario instalado. Coloca el binario en `~/.simplicio/bin/` (en Windows, `%USERPROFILE%\.simplicio\bin\`) y registra Simplicio automáticamente en los agentes que encuentra. Si el registro falla, el instalador se detiene en lugar de informar de que todo salió bien. Reinicia cualquier agente que ya esté abierto para que vuelva a cargar su configuración.

**Inicio de sesión.** Se requiere iniciar sesión con Google, incluso durante la beta. Ejecuta `simplicio auth login` y después `simplicio auth status --json`, y continúa cuando el estado indique `active: true`. El registro no requiere que hayas iniciado sesión, así que los agentes quedan configurados incluso antes de iniciar sesión. Nunca pegues una contraseña ni un token en la configuración de un agente.

<details>
<summary>Comprobar, actualizar, desinstalar</summary>

Para actualizar, vuelve a ejecutar el instalador. Puedes volver a ejecutar cualquiera de los dos instaladores en cualquier momento, y ambos resuelven la última versión. Los archivos `install.sh` y `install.ps1` están en la raíz de este repositorio.

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

- `--doctor` comprueba la instalación.
- `--uninstall --keep-data` elimina el binario instalado y conserva tus datos. Eso incluye el estado del inicio de sesión con Google de 30 días en `~/.simplicio/login.json`.
- `--uninstall --purge` elimina solo el estado que gestiona Simplicio, incluido el del inicio de sesión. Conserva `~/.simplicio/.env`, donde pueden estar las credenciales del proveedor. Una purga necesita `SIMPLICIO_CONFIRM_PURGE=1`.
- La desinstalación no modifica la configuración de tus agentes. Las entradas de Simplicio permanecen en cada agente hasta que las quites en los ajustes propios de ese agente.
- Los datos dentro de la carpeta `.simplicio` de un proyecto no los elimina `--keep-data`. Revisa el destino antes de elegir `--purge`.

Detalles completos: [INSTALL.md](../INSTALL.md).

</details>

<a id="first-run"></a>

## Primera ejecución

```bash
simplicio version
cd my-project
simplicio onboard
```

`simplicio version` confirma el binario instalado. `simplicio onboard` prepara el proyecto la primera vez. Después, abre tu agente en ese proyecto y trabaja como de costumbre. Para confirmar que Simplicio se cargó, busca `simplicio` en la lista de servidores MCP del agente. En Claude Code, `/mcp` muestra los servidores conectados. ¿Prefieres leer antes el instalador? Está en [install.sh](../install.sh).

<a id="works-with-the-agent-you-already-use"></a>

## Funciona con el agente que ya usas

Simplicio es un servidor MCP local por STDIO, así que cualquier agente que pueda iniciar un servidor MCP local puede apuntar a él.

El instalador delega el registro en el registrador propio de Simplicio. Detecta los agentes de tu equipo y escribe la entrada de Simplicio en los que sabe configurar, entre ellos Claude Code, Codex, Cursor, Visual Studio Code, OpenCode, Gemini CLI y Kiro. Dos archivos de este repositorio indican hasta dónde llega cada integración:

- El registro [`plugins/simplicio/host-surfaces.json`](../plugins/simplicio/host-surfaces.json) nombra 43 identificadores de agentes e indica, para cada uno, cómo lo alcanza Simplicio: una entrada MCP que escribe Simplicio (23), un plugin o extensión nativa (5), un paquete de plugin portable (4), una instalación guiada que sigues tú mismo (9), u otra herramienta de línea de comandos (2).
- La matriz de compatibilidad [`docs/hosts/compatibility-matrix.md`](../docs/hosts/compatibility-matrix.md) indica lo que está verificado. De esos 43, marca 12 agentes como compatibles y 29 como `unverified`, y no tiene fila para Codex ni para Gemini CLI. Cuando el registro dice que Simplicio escribe la entrada y la matriz dice `unverified`, considera esa integración como no probada.

23 agentes tienen una guía en [`docs/hosts/`](../docs/hosts/). En los agentes que se conectan mediante un plugin, el plugin se aplica en un paso aparte que pide tu consentimiento, y [INSTALL.md](../INSTALL.md) lo describe.

<details>
<summary>Los 43 agentes, según cómo los alcanza Simplicio</summary>

| Cómo lo alcanza Simplicio | Cantidad | Agentes |
|---|---|---|
| Una entrada MCP que escribe Simplicio | 23 | **xAI Grok Build**, MiMo Code, Amp, OpenClaude, Antigravity, **Pi**, **oh-my-pi**, Goose, Auggie, Autohand Code, Charm, Cline, Command Code, Continue, Droid, Kilocode, Kimi, Mistral Vibe, Rovo Dev, **Visual Studio Code**, **Meta Muse Code**, **OpenMausBot**, **OpenMuse (Python)** |
| Un plugin o extensión nativa | 5 | **Claude Code**, Codex, **OpenCode**, Hermes Agent, Gemini CLI |
| Un paquete de plugin portable | 4 | **Cursor**, GitHub Copilot, **Kiro**, Qwen Code |
| Una instalación guiada que sigues tú mismo | 9 | Devin, Codebuff, CopilotKit OpenDots, CopilotKit OpenBot, agentes.chat, OpenAI dots, xAI Grok Bot, Meta Muse app, Cue by Manus |
| Otra herramienta de línea de comandos | 2 | **OrcaDev / Orca ADE**, T3 Code |

En negrita: la matriz de compatibilidad marca el agente como compatible.

</details>

Para repetir el registro, ejecuta `simplicio mcp register`. El comando del servidor es `simplicio serve --mcp --stdio`. Estas son las herramientas principales que recibe tu agente:

| Herramienta | Qué te da |
|---|---|
| `simplicio_map` | Un mapa compacto del repositorio, para que el agente se oriente |
| `simplicio_context` | El contexto que necesita una tarea, acotado, en lugar de archivos completos |
| `simplicio_edit` | Ediciones estructuradas de archivos a partir de un plan preparado |
| `simplicio_validate` | Comprobaciones de pipeline, pruebas y entrega |
| `simplicio_run` | Una ejecución de tarea bajo el control de Simplicio |

La lista vigente es la que informa el servidor al iniciarse. [MCP-CONNECT.md](../MCP-CONNECT.md) describe las herramientas principales.

<details>
<summary>Configuración manual</summary>

Si tu agente no se configuró por ti, añade esta entrada a su configuración MCP. Sustituye la ruta por la ruta absoluta del binario instalado.

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

Codex lee TOML. Los agentes ejecutan `command` directamente, así que no uses `~` ni confíes en la expansión del shell. En las rutas de Windows usa barras normales, y sustituye el nombre de usuario de ejemplo.

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

Dónde guarda cada agente su archivo: [MCP-CONNECT.md](../MCP-CONNECT.md).

</details>

<a id="command-line"></a>

## Línea de comandos

| Comando | Qué obtienes |
|---|---|
| `simplicio map --repo . --for-llm markdown` | Un mapa estructural compacto del repositorio, escrito para que lo lea un modelo |
| `simplicio context --repo .` | El contexto acotado para una tarea |
| `simplicio memory query "query" --json` | Lo que el proyecto ya sabe, recuperado de su memoria indexada, en JSON |
| `simplicio edit --plan plan.json --repo .` | Un conjunto preparado de ediciones estructuradas, aplicado a los archivos |
| `simplicio run "task" --repo . --agents N` | Una ejecución de tarea con N agentes bajo el control de Simplicio |
| `simplicio loop` | Trabajo que avanza por rondas hasta que converge |

Los nombres que verás en los mensajes de Simplicio: Mapper observa, Fast proyecta o recupera, Dev CLI edita, Runtime gobierna y Loop converge.

<a id="safety-and-privacy"></a>

## Seguridad y privacidad

Esta sección describe la versión 3.15.0.

**Qué envía Simplicio, y a quién**

- **Se queda en tu equipo.** El mapeo, el contexto, las ediciones y las comprobaciones se ejecutan dentro del binario de Simplicio. Entrega los resultados a tu agente en el mismo equipo. Lo que tu agente envía a su propio proveedor de modelos lo decide el agente, como antes.
- **A SimpleTI (simpleti.com.br).** Solo para el inicio de sesión y las comprobaciones del plan. Envían tu token de inicio de sesión, la versión de Simplicio y el nombre de host de tu ordenador. Una consulta de licencia opcional envía también tu correo electrónico de la cuenta. Devuelven tu correo electrónico de la cuenta, tu nombre y tu plan. Sin contenido del repositorio: ni archivos, ni rutas de archivos, ni prompts, ni ediciones.
- **A GitHub.** Una comprobación en segundo plano de si hay una versión nueva, como máximo, aproximadamente una vez cada 12 horas. No envía nada sobre ti ni sobre tu código. Establece `SIMPLICIO_DISABLE_AUTO_UPDATE=1` para desactivarla. Al actualizar, el binario nuevo se descarga desde GitHub, y su SHA-256 y su firma se comprueban antes de reemplazar al anterior.
- **Sin analítica.** Simplicio 3.15.0 y los archivos que instala en tus agentes se comprobaron con ese fin: ninguno sube analítica, informes de fallos ni datos de uso. Los registros de uso y ahorro son archivos locales. Los hooks que instala solo ejecutan programas locales (el binario de Simplicio y, para los plugins opcionales, scripts locales); ninguno contacta con la red.
- **A servicios que tú configuras.** Un proveedor de modelos, GitHub, Jira, un notificador de chat o una caché de equipo reciben lo que envía esa función, lo cual puede incluir prompts y código. Las solicitudes a un proveedor de modelos llevan una cabecera que nombra a Simplicio como cliente.
- **Dos funciones llegan a un servicio abierto al público en Internet sin ninguna configuración.** La búsqueda web, cuando se ejecuta, envía la consulta de búsqueda a DuckDuckGo, salvo que configures otro servicio de búsqueda. En el chat propio de Simplicio, un mensaje que parezca una pregunta web puede convertirse en esa consulta. La auditoría de seguridad de dependencias, cuando la ejecutas, envía a osv.dev los nombres y las versiones de tus dependencias. Ninguna de las dos envía contenido de archivos.
- **Descargas.** El instalador y el mecanismo de actualización descargan desde GitHub. Algunos scripts auxiliares opcionales descargan sus propias herramientas desde PyPI o npm cuando los ejecutas. Si un plugin de agente se inicia y no encuentra el binario de Simplicio, descarga el instalador oficial desde GitHub, fijado a un commit concreto y comprobado por SHA-256.

**Versiones firmadas.** Cada versión publica sus binarios con sumas SHA-256, firmas Ed25519, un SBOM (una lista de lo que contiene la compilación) y procedencia de la compilación. Los instaladores y el mecanismo de actualización comprueban la suma y la firma antes de reemplazar el binario instalado. En las versiones estables, el contrato hace que una firma ausente o no válida y una suma de comprobación que no coincide sean errores fatales. El contrato está en [docs/UPDATE_SIGNATURE_CONTRACT.md](../docs/UPDATE_SIGNATURE_CONTRACT.md).

**Qué cambia el instalador en tu agente.** Añade una entrada de Simplicio a la configuración MCP del agente y conserva el resto de la configuración. En Claude Code también permite `mcp__simplicio__*`, para que ninguna herramienta de Simplicio quede denegada en modo automático. En los agentes cuya interfaz de hooks el instalador ha verificado, instala también los hooks de Simplicio. [INSTALL.md](../INSTALL.md) indica lo que escribe el instalador, y la guía de cada agente en [`docs/hosts/`](../docs/hosts/) da el detalle. La desinstalación no deshace estas entradas. La sección Instalación explica cómo quitarlas.

## También en este repositorio

<details>
<summary>Aplicación de escritorio (vista previa para macOS)</summary>

Hay publicada una vista previa de escritorio para macOS (Apple Silicon) como [Simplicio-3.8.47-arm64.dmg](https://github.com/simpletibr/simplicio/releases/download/v3.8.47/Simplicio-3.8.47-arm64.dmg). Su SHA-256 está en [DESKTOP-SHA256SUMS](../DESKTOP-SHA256SUMS), separado de las sumas de los binarios de Simplicio. El DMG no tiene archivo de firma e incluye el binario de Simplicio 3.8.47.

- La aplicación de escritorio para Windows no está publicada. En Windows, usa la instalación por línea de comandos de arriba.
- No se hace la firma con Apple Developer ID ni la notarización. El paquete está firmado ad hoc, es decir, sin certificado de desarrollador de Apple, y no se afirma que Gatekeeper lo acepte, así que macOS puede avisarte al abrirlo.
- La instalación por línea de comandos de arriba es la vía pública que se admite hasta que se publique un paquete de escritorio firmado.

Detalles: [docs/desktop/RELEASE.md](../docs/desktop/RELEASE.md).

</details>

<details>
<summary>Para mantenedores: el diagrama de flujo generado</summary>

Los comandos y herramientas documentados en README.md y MCP-CONNECT.md se representan como un único flujo, [docs/flow/simplicio.svg](../docs/flow/simplicio.svg), generado a partir de un archivo fuente, `docs/flow/simplicio.flow.json`. Vuelve a generarlo con `python3 scripts/generate_flow.py` y compruébalo con `python3 scripts/generate_flow.py --check` para detectar desviaciones. El contrato que lo mantiene alineado con esta página y con MCP-CONNECT.md es `python3 -m pytest tests/test_flow_contract.py -q`. La comprobación de importación en Langflow es `scripts/verify_flow_langflow.py`, que falla en modo cerrado (código de salida 2, `status=blocked`) cuando no hay ningún servidor en marcha. Las evidencias están en `docs/flow/evidence/` y `docs/flow/render/`, y [docs/flow/README.md](../docs/flow/README.md) describe los requisitos y cómo repetirlo.

</details>

<a id="questions-people-ask"></a>

## Preguntas frecuentes

**¿Es justa la comparación?**<br>
El mismo agente, el mismo modelo, los mismos tres prompts, el mismo proyecto inicial y las mismas comprobaciones externas, en una misma ronda. La línea base no tiene servidor MCP ni configuración de Simplicio. Consulta [Dónde Simplicio no gana](#where-simplicio-does-not-win) y los [Límites](../benchmarks/2026-11-22-standard-benchmark.md#limits) del informe.

**¿Tengo que cambiar mi agente o mi modelo?**<br>
No. Simplicio se conecta al agente que ya usas. En la medición de arriba, cada escenario usó el mismo agente y el mismo modelo.

**¿Siempre obtendré estas cifras?**<br>
No. Miden un solo trabajo, con un modelo, en un equipo, a lo largo de tres sesiones por escenario. Consulta [Dónde Simplicio no gana](#where-simplicio-does-not-win) y ejecuta la comparación con tu propio trabajo.

**¿Es de código abierto?**<br>
No. Simplicio es software propietario. Es un binario firmado, publicado como archivos de cada versión, y su código fuente no es público. Este repositorio contiene los instaladores, los paquetes para los agentes, el código fuente de la aplicación de escritorio, la documentación y los datos de la medición.

**¿Cómo lo elimino?**<br>
Ejecuta `sh install.sh --uninstall --keep-data`, o `pwsh install.ps1 -Uninstall -KeepData` en Windows. Elimina el binario y conserva tus datos. No modifica la configuración de tus agentes, así que quita las entradas de Simplicio en los ajustes propios de cada agente. [Instalación](#install) incluye los detalles y la opción de purga.

**¿Necesito una cuenta?**<br>
Sí. Se requiere iniciar sesión con Google, incluso durante la beta. Ejecuta `simplicio auth login`.

**¿Sale mi código de mi equipo?**<br>
El mapeo, el contexto, las ediciones y las comprobaciones se ejecutan en tu equipo. Simplicio se comunica con SimpleTI para el inicio de sesión y las comprobaciones del plan, y con GitHub para buscar actualizaciones, sin contenido del repositorio en ninguno de los dos casos. Las funciones que configures o ejecutes pueden llegar a otros servicios. La lista completa está en [Qué envía Simplicio, y a quién](#safety-and-privacy).

<a id="documentation-and-community"></a>

## Documentación y comunidad

- **Sitio web:** [simpleti.com.br/simplicio](https://simpleti.com.br/simplicio/)
- **Documentación:** [simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)
- **Discord:** [Únete a la comunidad](https://discord.gg/wM6tr7xVb)
- **Incidencias:** [Gestor de incidencias de GitHub](https://github.com/simpletibr/simplicio/issues)
- **En este repositorio:** [INSTALL.md](../INSTALL.md), [MCP-CONNECT.md](../MCP-CONNECT.md) y [docs/hosts/](../docs/hosts/)
- **Relacionado:** Simplicio Video (hypit). Para clonarlo: `git clone https://github.com/hypit-ai/hypit.git simplicio-video`

<p align="center">
  <sub>© 2026 SimpleTI. Simplicio es un software propietario registrado. Todos los derechos reservados.</sub>
</p>
