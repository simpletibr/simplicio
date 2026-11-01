# 🔥 Simplicio

<p align="center">
  <img src="../assets/simplicio-hero.png" alt="Simplicio — AI coding agent" width="920" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=blue&label=latest" alt="Latest Release"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Stars"></a>
  <a href="https://github.com/simpletibr/simplicio/releases"><img src="https://img.shields.io/github/downloads/simpletibr/simplicio/total?color=green" alt="Downloads"></a>
  <a href="../plugins/simplicio/LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="License"></a>
</p>

<p align="center">
  <a href="#установка">Установка</a> ·
  <a href="#что-он-делает">Что он делает</a> ·
  <a href="#-benchmark-2026-10-31">Benchmark</a> ·
  <a href="https://simpleti.com.br/simplicio/#start">Сайт</a>
</p>

<p align="center">
  <strong>🌍 Языки:</strong><br>
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

**Simplicio** — это терминальный AI-агент для кода: один бинарный файл, который заменяет весь
ваш AI-ассистируемый рабочий процесс: чат, генерацию кода, контекст репозитория,
планирование, локальную многoагентную оркестрацию (64 → 600 агентов) и
доставку PR с подтверждением.

**Работает на вашей машине. Ваш код никогда не покидает вашего контроля. Удалённые модели
необязательны, не обязательны.**

> Каждое взаимодействие показывает, сколько токенов вы сэкономили. Один бинарный файл на Rust, без зависимостей.

## 🚀 Установка

### Установка через плагин Codex

Если вы используете Codex, Simplicio можно установить как плагин. Добавьте публичный Marketplace, установите плагин и запустите новый сеанс Codex; плагин установит и запустит Simplicio Runtime и предоставит его skills и инструменты MCP.

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

### npm / npx (любая ОС)

```bash
npx simplicio install
```

### pip / PyPI (любая ОС)

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

### Прямая установка (без PyPI)

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

Готово. Одна команда. Никакого менеджера пакетов, никакой настройки модели.

---

## 📊 Benchmark (2026-10-31)

Реальная модель создаёт файл и редактирует его в той же сессии. Результат проверяется вне сессии: страницы в headless Chrome, скрипты запуском. 60 сессий, медианы.

| Задача | Конфигурация | n | Время | Запросы к модели | Выходные токены | Стоимость | Результат |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **Страница из JSON-файла, задачу покрывает генератор** | **Simplicio 3.10.8** | 10 | **14.1 s** | **6** | **602** | **$0.0021** | **10/10** |
|  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | $0.0215 | 10/10 |
|  | Без MCP | 10 | 176.3 s | 32.5 | 17,929 | $0.0203 | 10/10 |
| **Новая страница, другие данные и другой язык, не использовалась при создании генератора** | **Simplicio 3.10.8** | 6 | **14.1 s** | **6** | **524** | **$0.0010** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | $0.0153 | 6/6 |
| **Скрипт на Python, ни один генератор его не покрывает** | **Simplicio 3.10.8** | 6 | **30.7 s** | **10.5** | **1,796** | **$0.0031** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | $0.0051 | 6/6 |
|  | Без MCP | 6 | 22.7 s | 8 | 1,268 | $0.0024 | 6/6 |

Выигрыш даёт генератор: в задачах со страницами `simplicio_map` направляет запрос, а `simplicio_codegen` записывает файл, тратя 0 токенов LLM. Когда задачу не покрывает ни один генератор, 3.10.8 лучше 3.9.2, но обходится примерно на 8 с и 0,0007 $ дороже за сессию, чем работа без MCP.

> OpenCode 2.1.4 и DeepSeek V4.1 Flash на одном фиксированном эндпоинте OpenRouter, одинаково для всех запусков. Стоимость рассчитана по 0,15 $ за вход, 0,60 $ за выход и 0,003 $ за кэш на миллион токенов. Это одна модель на трёх небольших задачах: на других задачах числа будут другими. [Промпты, метод, ограничения и данные по сессиям](../benchmarks/2026-10-31-map-codegen.md).

---

## 🎯 Что он делает

| Команда | Описание |
|---|---|
| `simplicio map --repo .` | Создаёт карту репозитория для LLM |
| `simplicio memory "запрос"` | Нейронное recall (FTS + векторы) |
| `simplicio edit '{...}'` | Детерминированное редактирование файлов |
| `simplicio coding-loop "задача"` | Итерации до прохождения тестов |
| `simplicio deliver certify` | 5 контрольных точек перед доставкой |
| `simplicio run "задача" --agents N` | Многоагентная оркестрация |
---

## 🏗️ Архитектура

```
LLM (Claude/Codex/Gemini)          Simplicio Runtime (Rust)
  |                                   |
  | 1. Ориентация                     | simplicio map
  | 2. Воспоминание                   | simplicio memory
  | 3. Решение                        |
  | 4. Редактирование ──────────────> | simplicio edit (0 токенов)
  | 5. Проверка <───────────────────  | simplicio deliver certify
  | 6. Итерация                       | simplicio coding-loop
```

**LLM рассуждает. Simplicio выполняет детерминированно.**

---

## ✨ Возможности

- 🏠 **Локально в первую очередь** — встроенная llama.cpp, масштабирование на удалённые модели только при необходимости
- 🪜 **Уровневые агенты** — 64 → 100 → 200 → 600 локальных агентов до платного облака
- 🔇 **Шенноновский фильтр новизны** — отфильтровывает избыточные выводы (ноль токенов на дедупликацию)
- 🔒 **Опечатанные квитанции** — sha256 для каждого артефакта, защищённая от взлома цепочка доказательств
- 🛡️ **5 шлюзов доставки** — приёмка, валидация, запуск-проверка, регрессия, саморецензия
- ⚡ **Шлюз действий** — классификация рисков + блоклист для мутаций, инициированных чатом
- 🔌 **MCP/ACP** — Model Context Protocol + Agent Client Protocol
- 🌐 **Шлюзы** — Telegram, Discord, Slack, WhatsApp
- 🧩 **Система навыков** — загрузка и цепочки переиспользуемых возможностей
- 💾 **База памяти** — постоянный FTS + векторный recall между сессиями
- 🔀 **Маршрутизатор LLM** — без LLM → локальная LLM → удалённая LLM автоматически
- 🖥️ **Кроссплатформенность** — macOS, Linux, Windows, один бинарник

---

## 🎁 Бесплатная публичная бета

**Детерминированные команды БЕСПЛАТНЫ навсегда:**
`map`, `validate`, `edit`, `deliver`, `checkpoint`

**AI-функции бесплатны в период публичной беты без указания даты окончания.**
Оплата будет определена в будущих обновлениях.

```bash
simplicio license status
```

---

## 📋 Требования

| Требование | Минимум | Рекомендуется |
|---|---|---|
| ОЗУ | 8 ГБ | 16 ГБ+ |
| Диск | 5 МБ | 1.5 ГБ (с локальной LLM) |
| ОС | macOS 13+, Linux, Windows 10+ | macOS ARM64 |
| Терминал | любой современный терминал | WezTerm / Alacritty / Ghostty |

---

## 🌐 Экосистема

- [Веб-сайт](https://simpleti.com.br/simplicio/#start) — полная документация, бенчмарки, установка
- [Discord](https://discord.gg/wM6tr7xVb) — сообщество и поддержка

---

## 📄 Лицензия

Проприетарная. Бинарный файл можно бесплатно скачивать и использовать. AI-функции бесплатны в период
публичной беты. См. [LICENSE](../plugins/simplicio/LICENSE).

---

## ⭐ История звёзд

<a href="https://star-history.com/#simpletibr/simplicio&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" />
    <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" width="100%" />
  </picture>
</a>

---

## 💬 Сообщество

- [Discord](https://discord.gg/wM6tr7xVb) — чат, поддержка, ранний доступ
- [GitHub Issues](https://github.com/simpletibr/simplicio/issues) — баги и запросы функций

---

<p align="center">
  <strong>🔥 Simplicio 🔥</strong>
</p>
