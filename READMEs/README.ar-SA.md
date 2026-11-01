# 🔥 Simplicio

<p align="center">
  <img src="../assets/simplicio-hero.png" alt="سيمپليسيو — عميل برمجة ذكي" width="920" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=blue&label=latest" alt="أحدث إصدار"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="النجوم"></a>
  <a href="https://github.com/simpletibr/simplicio/releases"><img src="https://img.shields.io/github/downloads/simpletibr/simplicio/total?color=green" alt="التنزيلات"></a>
  <a href="../plugins/simplicio/LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="الرخصة"></a>
</p>

<p align="center">
  <a href="#التثبيت">التثبيت</a> ·
  <a href="#ما-يفعله">ما يفعله</a> ·
  <a href="#-benchmark-2026-10-31">Benchmark</a> ·
  <a href="https://simpleti.com.br/simplicio/#start">الموقع الإلكتروني</a>
</p>

<p align="center">
  <strong>🌍 اللغات:</strong><br>
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

## ⚡ خلاصة سريعة

**سيمپليسيو** هو عميل برمجة ذكي يعمل في الطرفية — ملف ثنائي واحد يستبدل
سير عملك التطويري المدعوم بالذكاء الاصطناعي بالكامل: الدردشة، توليد الأكواد،
سياق المستودع، التخطيط، التنسيق المحلي متعدد العملاء (64 ← 600 عميل)،
وتسليم طلبات السحب المدعومة بالأدلة.

**يعمل على جهازك. كودك لا يغادر سيطرتك أبدًا. النماذج البعيدة
اختيارية، وليست إلزامية.**

> كل تفاعل يُظهر بالضبط كم توكينًا وفّرته. ملف Rust ثنائي واحد، بدون تبعيات.

## 🚀 التثبيت

### التثبيت عبر إضافة Codex

إذا كنت تستخدم Codex، يمكنك تثبيت Simplicio كإضافة. أضف Marketplace العام، وثبّت الإضافة، ثم ابدأ جلسة Codex جديدة؛ ستثبّت الإضافة Simplicio Runtime وتُشغّله وتوفّر مهاراته وأدوات MCP.

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

### npm / npx (أي نظام تشغيل)

```bash
npx simplicio install
```

### pip / PyPI (أي نظام تشغيل)

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

### التثبيت المباشر (بدون PyPI)

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

تم. أمر واحد. لا حاجة لمدير حزم أو تهيئة نموذج.

---

## 📊 Benchmark (2026-10-31)

ينشئ نموذج حقيقي ملفًا ثم يعدّله في الجلسة نفسها. يُفحص الناتج خارج الجلسة: الصفحات في Chrome بلا واجهة، والسكربتات بتشغيلها. 60 جلسة، والقيم وسيطة.

| المهمة | الإعداد | n | الوقت | طلبات النموذج | رموز الإخراج | التكلفة | التسليم |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **صفحة من ملف JSON، يغطيها مولّد** | **Simplicio 3.10.8** | 10 | **14.1 s** | **6** | **602** | **$0.0021** | **10/10** |
|  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | $0.0215 | 10/10 |
|  | بدون MCP | 10 | 176.3 s | 32.5 | 17,929 | $0.0203 | 10/10 |
| **صفحة جديدة ببيانات ولغة أخرى، لم تُستخدم في بناء المولّد** | **Simplicio 3.10.8** | 6 | **14.1 s** | **6** | **524** | **$0.0010** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | $0.0153 | 6/6 |
| **سكربت Python، لا يغطيه أي مولّد** | **Simplicio 3.10.8** | 6 | **30.7 s** | **10.5** | **1,796** | **$0.0031** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | $0.0051 | 6/6 |
|  | بدون MCP | 6 | 22.7 s | 8 | 1,268 | $0.0024 | 6/6 |

يأتي الكسب من المولّد: في مهام الصفحات يوجّه `simplicio_map` الطلب، ويكتب `simplicio_codegen` الملف بصفر من رموز LLM. وعندما لا يغطي أي مولّد المهمة، يتفوق 3.10.8 على 3.9.2، لكنه يكلف نحو 8 ثوانٍ و0.0007 دولار أكثر في الجلسة مقارنة بعدم استخدام MCP.

> استُخدم OpenCode 2.1.4 وDeepSeek V4.1 Flash على نقطة نهاية ثابتة واحدة في OpenRouter في كل التشغيلات. حُسبت التكلفة بسعر 0.15 دولار للإدخال و0.60 دولار للإخراج و0.003 دولار للذاكرة المؤقتة لكل مليون رمز. هذا نموذج واحد على ثلاث مهام صغيرة، وستعطي مهام أخرى أرقامًا أخرى. [المطالبات والمنهج والحدود والبيانات لكل جلسة](../benchmarks/2026-10-31-map-codegen.md).

---

## 🎯 ما يفعله

| الأمر | الوصف |
|---|---|
| `simplicio map --repo .` | يرسم خريطة المستودع لـ LLMs |
| `simplicio memory "استعلام"` | استرجاع عصبي (FTS + متجهات) |
| `simplicio edit '{...}'` | تحرير حتمي للملفات |
| `simplicio coding-loop "مهمة"` | يكرر حتى تنجح الاختبارات |
| `simplicio deliver certify` | 5 بوابات جودة قبل الشحن |
| `simplicio run "مهمة" --agents N` | تنسيق متعدد العملاء |
---

## 🏗️ المعمارية

```
LLM (Claude/Codex/Gemini)          Simplicio Runtime (Rust)
  |                                   |
  | 1. توجّه                          | simplicio map
  | 2. استرجع                         | simplicio memory
  | 3. قرّر                           |
  | 4. حرّر  ───────────────────────> | simplicio edit (0 tokens)
  | 5. تحقق <──────────────────────  | simplicio deliver certify
  | 6. كرّر                           | simplicio coding-loop
```

**الـ LLM يفكر. سيمپليسيو ينفّذ بشكل حتمي.**

---

## ✨ الميزات

- 🏠 **محلي أولاً** — llama.cpp مدمج، يتوسع إلى البعيد فقط عند الحاجة
- 🪜 **عملاء متدرجون** — 64 ← 100 ← 200 ← 600 عميل محلي قبل السحابة المدفوعة
- 🔇 **بوابة شانون للجدة** — يصفّي المخرجات المتكررة (صفر توكينز عند إزالة التكرار)
- 🔒 **إيصالات مختومة** — sha256 لكل قطعة أثرية، سلسلة أدلة مضادة للتلاعب
- 🛡️ **5 بوابات تسليم** — القبول، التحقق، تشغيل-تحقق، الانحدار، المراجعة الذاتية
- ⚡ **بوابة الإجراءات** — تصنيف المخاطر + قائمة الحظر للطفرات المنطلقة من الدردشة
- 🔌 **MCP/ACP** — بروتوكول سياق النموذج + بروتوكول عميل الوكيل
- 🌐 **بوابات** — Telegram، Discord، Slack، WhatsApp
- 🧩 **نظام المهارات** — يحمّل ويسلسل القدرات القابلة لإعادة الاستخدام
- 💾 **قاعدة بيانات الذاكرة** — FTS دائم + استرجاع متجهي عبر الجلسات
- 🔀 **موجه LLM** — لا LLM ← LLM محلي ← LLM بعيد تلقائيًا
- 🖥️ **متعدد المنصات** — macOS، Linux، Windows، ملف ثنائي واحد

---

## 🎁 النسخة التجريبية العامة المجانية

**الأوامر الحتمية مجانية إلى الأبد:**
`map`, `validate`, `edit`, `deliver`, `checkpoint`

**ميزات الذكاء الاصطناعي مجانية خلال النسخة التجريبية العامة بدون تاريخ انتهاء.**
سيتم تحديد الفوترة في التحديثات المستقبلية.

```bash
simplicio license status
```

---

## 📋 المتطلبات

| المتطلب | الأدنى | الموصى به |
|---|---|---|
| RAM | 8 جيجابايت | 16 جيجابايت+ |
| التخزين | 5 ميجابايت | 1.5 جيجابايت (مع LLM محلي) |
| نظام التشغيل | macOS 13+، Linux، Windows 10+ | macOS ARM64 |
| الطرفية | أي طرفية حديثة | WezTerm / Alacritty / Ghostty |

---

## 🌐 النظام البيئي

- [الموقع الإلكتروني](https://simpleti.com.br/simplicio/#start) — الوثائق الكاملة، المقاييس، التثبيت
- [Discord](https://discord.gg/wM6tr7xVb) — المجتمع والدعم

---

## 📄 الرخصة

مملوكة. الملف الثنائي مجاني للتنزيل والاستخدام. ميزات الذكاء الاصطناعي مجانية خلال
النسخة التجريبية العامة. انظر [LICENSE](../plugins/simplicio/LICENSE).

---

## ⭐ تاريخ النجوم

<a href="https://star-history.com/#simpletibr/simplicio&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" />
    <img alt="مخطط تاريخ النجوم" src="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" width="100%" />
  </picture>
</a>

---

## 💬 المجتمع

- [Discord](https://discord.gg/wM6tr7xVb) — دردشة، دعم، وصول مبكر
- [GitHub Issues](https://github.com/simpletibr/simplicio/issues) — الأخطاء وطلبات الميزات

---

<p align="center">
  <strong>🔥 Simplicio 🔥</strong>
</p>
