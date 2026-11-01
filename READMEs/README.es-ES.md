# 🔥 Simplicio

<p align="center">
  <img src="../assets/simplicio-hero.png" alt="Simplicio — agente de IA para programación" width="920" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=blue&label=latest" alt="Última versión"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Estrellas"></a>
  <a href="https://github.com/simpletibr/simplicio/releases"><img src="https://img.shields.io/github/downloads/simpletibr/simplicio/total?color=green" alt="Descargas"></a>
  <a href="../plugins/simplicio/LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="Licencia"></a>
</p>

<p align="center">
  <a href="#instalación">Instalación</a> ·
  <a href="#qué-hace">Qué Hace</a> ·
  <a href="#-benchmark-2026-10-31">Benchmark</a> ·
  <a href="https://simpleti.com.br/simplicio/#start">Sitio web</a>
</p>

<p align="center">
  <strong>🌍 Idiomas:</strong><br>
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

**Simplicio** es un agente de IA de terminal para programación — un único binario que reemplaza
todo tu flujo de trabajo de desarrollo asistido por IA: chat, generación de código, contexto
del repositorio, planificación, orquestación multi-agente local (64 → 600 agentes) y
entrega de PR respaldada por evidencia.

**Se ejecuta en tu máquina. Tu código nunca sale de tu control. Los modelos remotos son
opcionales, no obligatorios.**

> Cada interacción muestra exactamente cuántos tokens has ahorrado. Un solo binario en Rust, cero dependencias.

## 🚀 Instalación

### Instalar mediante el plugin de Codex

Si usas Codex, puedes instalar Simplicio como un plugin. Añade el Marketplace público, instala el plugin e inicia una nueva sesión de Codex; el plugin instala e inicia el Runtime de Simplicio y expone sus skills y herramientas MCP.

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

### npm / npx (cualquier SO)

```bash
npx simplicio install
```

### pip / PyPI (cualquier SO)

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

### Instalador directo (sin PyPI)

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

Listo. Un solo comando. Sin gestor de paquetes, sin configuración de modelos.

---

## 📊 Benchmark (2026-10-31)

Un modelo real crea un archivo y lo edita en la misma sesión. El resultado se comprueba fuera de la sesión: las páginas en Chrome headless, los scripts ejecutándolos. 60 sesiones, medianas.

| Tarea | Configuración | n | Tiempo | Peticiones al modelo | Tokens de salida | Coste | Entregas |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **Página a partir de un JSON, cubierta por un generador** | **Simplicio 3.10.8** | 10 | **14.1 s** | **6** | **602** | **$0.0021** | **10/10** |
|  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | $0.0215 | 10/10 |
|  | Sin MCP | 10 | 176.3 s | 32.5 | 17,929 | $0.0203 | 10/10 |
| **Página nueva, con otros datos y otro idioma, no usada para construir el generador** | **Simplicio 3.10.8** | 6 | **14.1 s** | **6** | **524** | **$0.0010** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | $0.0153 | 6/6 |
| **Script de Python, ningún generador lo cubre** | **Simplicio 3.10.8** | 6 | **30.7 s** | **10.5** | **1,796** | **$0.0031** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | $0.0051 | 6/6 |
|  | Sin MCP | 6 | 22.7 s | 8 | 1,268 | $0.0024 | 6/6 |

La ganancia viene del generador: en las tareas de página, `simplicio_map` enruta la petición y `simplicio_codegen` escribe el archivo con 0 tokens de LLM. Cuando ningún generador cubre la tarea, 3.10.8 supera a 3.9.2 y cuesta unos 8 s y 0,0007 US$ más por sesión que no usar MCP.

> OpenCode 2.1.4 y DeepSeek V4.1 Flash en un único endpoint de OpenRouter, igual en todas las ejecuciones. Coste calculado a 0,15 US$ de entrada, 0,60 US$ de salida y 0,003 US$ de caché por millón de tokens. Es un modelo en tres tareas pequeñas: otras tareas darán otros números. [Prompts, método, límites y datos por sesión](../benchmarks/2026-10-31-map-codegen.md).

Las mismas tareas en otros modelos, con y sin Simplicio. Cada modelo se ejecutó en un solo cliente, así que compara cada modelo consigo mismo.

| Modelo | Tarea | Simplicio 3.10.8 | Sin MCP | Entregas |
|:---|:---|---:|---:|---:|
| **Claude Sonnet 5.5** (Claude Code) | Página a partir de un JSON, cubierta por un generador | **17.5 s · $0.0672** | 33.4 s · $0.0927 | 10/10 |
|  | Página nueva, con otros datos y otro idioma, no usada para construir el generador | **16.3 s · $0.0514** | 22.5 s · $0.0610 | 10/10 |
|  | Script de Python, ningún generador lo cubre | **19.6 s · $0.0548** | 11.4 s · $0.0283 | 10/10 |
| **Grok 4.7** (Grok Build) | Página a partir de un JSON, cubierta por un generador | **31.0 s · $0.1690** | 359.7 s · $0.8590 | 6/6 |
|  | Página nueva, con otros datos y otro idioma, no usada para construir el generador | **36.0 s · $0.2059** | 387.5 s · $0.8518 | 6/6 |
|  | Script de Python, ningún generador lo cubre | **82.0 s · $0.3315** | 63.1 s · $0.2452 | 6/6 |
| **Claude Haiku 5.5** (OpenCode) | Página a partir de un JSON, cubierta por un generador | **13.7 s · $0.0046** | 29.3 s · $0.0083 | 10/10 |
|  | Página nueva, con otros datos y otro idioma, no usada para construir el generador | **13.8 s · $0.0023** | 28.7 s · $0.0057 | 10/10 |
|  | Script de Python, ningún generador lo cubre | **19.2 s · $0.0033** | 16.6 s · $0.0030 | 10/10 |

[Prompts, método, límites y datos por sesión](../benchmarks/2026-11-01-multi-model.md).

---

## 🎯 Qué Hace

| Comando | Descripción |
|---|---|
| `simplicio map --repo .` | Mapa del repositorio para LLMs |
| `simplicio memory "consulta"` | Recuperación neuronal (FTS + vectores) |
| `simplicio edit '{...}'` | Edición determinista de archivos |
| `simplicio coding-loop "tarea"` | Itera hasta que pasen las pruebas |
| `simplicio deliver certify` | 5 compuertas de calidad antes del envío |
| `simplicio run "tarea" --agents N` | Orquestación multi-agente |
---

## 🏗️ Arquitectura

```
LLM (Claude/Codex/Gemini)          Runtime de Simplicio (Rust)
  |                                   |
  | 1. Orientar                       | simplicio map
  | 2. Recordar                       | simplicio memory
  | 3. Decidir                        |
  | 4. Editar  ──────────────────────> | simplicio edit (0 tokens)
  | 5. Verificar <───────────────────  | simplicio deliver certify
  | 6. Iterar                         | simplicio coding-loop
```

**El LLM razona. Simplicio ejecuta de forma determinista.**

---

## ✨ Características

- 🏠 **Primero local** — llama.cpp integrado, escala a remoto solo cuando es necesario
- 🪜 **Agentes escalonados** — 64 → 100 → 200 → 600 agentes locales antes de la nube de pago
- 🔇 **Puerta de novedad de Shannon** — filtra salidas redundantes (cero tokens en dedup)
- 🔒 **Recibos sellados** — sha256 por artefacto, cadena de evidencia a prueba de manipulaciones
- 🛡️ **5 compuertas de entrega** — aceptación, validación, ejecución-verificación, regresión, autoevaluación
- ⚡ **Compuerta de acción** — clasificación de riesgo + lista negra para mutaciones iniciadas por chat
- 🔌 **MCP/ACP** — Protocolo de Contexto de Modelo + Protocolo de Cliente Agente
- 🌐 **Pasarelas** — Telegram, Discord, Slack, WhatsApp
- 🧩 **Sistema de habilidades** — carga y encadena capacidades reutilizables
- 💾 **Base de datos de memoria** — recuperación FTS + vectorial persistente entre sesiones
- 🔀 **Enrutador de LLM** — sin LLM → LLM local → LLM remoto automáticamente
- 🖥️ **Multiplataforma** — macOS, Linux, Windows, binario único

---

## 🎁 Beta Pública Gratuita

**Los comandos deterministas son GRATIS para siempre:**
`map`, `validate`, `edit`, `deliver`, `checkpoint`

**Las funciones de IA son gratuitas durante la beta pública sin fecha de finalización.**
La facturación se definirá en actualizaciones futuras.

```bash
simplicio license status
```

---

## 📋 Requisitos

| Requisito | Mínimo | Recomendado |
|---|---|---|
| RAM | 8 GB | 16 GB+ |
| Almacenamiento | 5 MB | 1.5 GB (con LLM local) |
| SO | macOS 13+, Linux, Windows 10+ | macOS ARM64 |
| Terminal | cualquier terminal moderna | WezTerm / Alacritty / Ghostty |

---

## 🌐 Ecosistema

- [Sitio web](https://simpleti.com.br/simplicio/#start) — documentación completa, benchmarks, instalación
- [Discord](https://discord.gg/wM6tr7xVb) — comunidad y soporte

---

## 📄 Licencia

Propietaria. El binario es gratuito para descargar y usar. Las funciones de IA son gratuitas durante la
beta pública. Consulta [LICENSE](../plugins/simplicio/LICENSE).

---

## ⭐ Historial de Estrellas

<a href="https://star-history.com/#simpletibr/simplicio&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" />
    <img alt="Gráfico de historial de estrellas" src="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" width="100%" />
  </picture>
</a>

---

## 💬 Comunidad

- [Discord](https://discord.gg/wM6tr7xVb) — chat, soporte, acceso anticipado
- [GitHub Issues](https://github.com/simpletibr/simplicio/issues) — errores y solicitudes de funciones

---

<p align="center">
  <strong>🔥 Simplicio 🔥</strong>
</p>
