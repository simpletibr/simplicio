# 🔥 Simplicio

<p align="center">
  <img src="../assets/simplicio-hero.png" alt="Simplicio — AI कोडिंग एजेंट" width="920" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=blue&label=latest" alt="Latest Release"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Stars"></a>
  <a href="https://github.com/simpletibr/simplicio/releases"><img src="https://img.shields.io/github/downloads/simpletibr/simplicio/total?color=green" alt="Downloads"></a>
  <a href="../plugins/simplicio/LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="License"></a>
</p>

<p align="center">
  <a href="#इंस्टॉलेशन">इंस्टॉलेशन</a> ·
  <a href="#यह-क्या-करता-है">यह क्या करता है</a> ·
  <a href="#-benchmark-2026-10-31">Benchmark</a> ·
  <a href="https://simpleti.com.br/simplicio/#start">वेबसाइट</a>
</p>

<p align="center">
  <strong>🌍 भाषाएँ:</strong><br>
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

**Simplicio** एक टर्मिनल AI कोडिंग एजेंट है — एक एकल बाइनरी जो आपके संपूर्ण
AI-सहायित विकास कार्यप्रवाह को बदल देता है: चैट, कोड जनरेशन, रिपॉजिटरी
संदर्भ, योजना, स्थानीय मल्टी-एजेंट ऑर्केस्ट्रेशन (64 → 600 एजेंट), और
साक्ष्य-समर्थित PR डिलीवरी।

**आपकी मशीन पर चलता है। आपका कोड कभी आपके नियंत्रण से बाहर नहीं जाता। रिमोट मॉडल
वैकल्पिक हैं, अनिवार्य नहीं।**

> हर इंटरैक्शन दिखाता है कि आपने कितने टोकन बचाए। एकल Rust बाइनरी, शून्य निर्भरताएँ।

## 🚀 इंस्टॉलेशन

### Codex प्लगइन से इंस्टॉल करें

यदि आप Codex का उपयोग करते हैं, तो Simplicio को प्लगइन के रूप में इंस्टॉल कर सकते हैं। सार्वजनिक Marketplace जोड़ें, प्लगइन इंस्टॉल करें और नया Codex सत्र शुरू करें; प्लगइन Simplicio Runtime को इंस्टॉल और बूटस्ट्रैप करता है तथा उसकी skills और MCP टूल उपलब्ध कराता है।

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

### npm / npx (किसी भी OS पर)

```bash
npx simplicio install
```

### pip / PyPI (किसी भी OS पर)

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

### प्रत्यक्ष इंस्टॉलर (PyPI के बिना)

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

हो गया। एक कमांड। कोई पैकेज मैनेजर नहीं, कोई मॉडल कॉन्फ़िगरेशन नहीं।

---

## 📊 Benchmark (2026-10-31)

एक असली मॉडल एक ही सत्र में फ़ाइल बनाता है और उसे संपादित करता है। परिणाम की जाँच सत्र के बाहर होती है: पेज हेडलेस Chrome में, स्क्रिप्ट उन्हें चलाकर। 60 सत्र, माध्यिका मान।

| कार्य | सेटअप | n | समय | मॉडल अनुरोध | आउटपुट टोकन | लागत | डिलीवरी |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **JSON फ़ाइल से पेज, जिसे जनरेटर कवर करता है** | **Simplicio 3.10.8** | 10 | **14.1 s** | **6** | **602** | **$0.0021** | **10/10** |
|  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | $0.0215 | 10/10 |
|  | बिना MCP | 10 | 176.3 s | 32.5 | 17,929 | $0.0203 | 10/10 |
| **नया पेज, अलग डेटा और भाषा, जनरेटर बनाने में उपयोग नहीं हुआ** | **Simplicio 3.10.8** | 6 | **14.1 s** | **6** | **524** | **$0.0010** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | $0.0153 | 6/6 |
| **Python स्क्रिप्ट, जिसे कोई जनरेटर कवर नहीं करता** | **Simplicio 3.10.8** | 6 | **30.7 s** | **10.5** | **1,796** | **$0.0031** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | $0.0051 | 6/6 |
|  | बिना MCP | 6 | 22.7 s | 8 | 1,268 | $0.0024 | 6/6 |

लाभ जनरेटर से आता है: पेज वाले कार्यों में `simplicio_map` अनुरोध को रूट करता है और `simplicio_codegen` 0 LLM टोकन में फ़ाइल लिखता है। जब कोई जनरेटर कार्य को कवर नहीं करता, तब 3.10.8 फिर भी 3.9.2 से बेहतर है, लेकिन बिना MCP की तुलना में प्रति सत्र लगभग 8 सेकंड और $0.0007 अधिक लेता है।

> हर रन में OpenCode 2.1.4 और DeepSeek V4.1 Flash, OpenRouter के एक ही निश्चित एंडपॉइंट पर। लागत प्रति दस लाख टोकन $0.15 इनपुट, $0.60 आउटपुट और $0.003 कैश पर निकाली गई है। यह एक मॉडल और तीन छोटे कार्यों का परिणाम है: दूसरे कार्यों में संख्याएँ अलग होंगी। [प्रॉम्प्ट, विधि, सीमाएँ और प्रति सत्र डेटा](../benchmarks/2026-10-31-map-codegen.md).

वही कार्य दूसरे मॉडलों पर, Simplicio के साथ और उसके बिना। हर मॉडल एक ही क्लाइंट में चला, इसलिए किसी मॉडल की तुलना उसी मॉडल से करें।

| मॉडल | कार्य | Simplicio 3.10.8 | बिना MCP | डिलीवरी |
|:---|:---|---:|---:|---:|
| **Claude Sonnet 5.5** (Claude Code) | JSON फ़ाइल से पेज, जिसे जनरेटर कवर करता है | **17.5 s · $0.0672** | 33.4 s · $0.0927 | 10/10 |
|  | नया पेज, अलग डेटा और भाषा, जनरेटर बनाने में उपयोग नहीं हुआ | **16.3 s · $0.0514** | 22.5 s · $0.0610 | 10/10 |
|  | Python स्क्रिप्ट, जिसे कोई जनरेटर कवर नहीं करता | **19.6 s · $0.0548** | 11.4 s · $0.0283 | 10/10 |
| **Grok 4.7** (Grok Build) | JSON फ़ाइल से पेज, जिसे जनरेटर कवर करता है | **31.0 s · $0.1690** | 359.7 s · $0.8590 | 6/6 |
|  | नया पेज, अलग डेटा और भाषा, जनरेटर बनाने में उपयोग नहीं हुआ | **36.0 s · $0.2059** | 387.5 s · $0.8518 | 6/6 |
|  | Python स्क्रिप्ट, जिसे कोई जनरेटर कवर नहीं करता | **82.0 s · $0.3315** | 63.1 s · $0.2452 | 6/6 |
| **Claude Haiku 5.5** (OpenCode) | JSON फ़ाइल से पेज, जिसे जनरेटर कवर करता है | **13.7 s · $0.0046** | 29.3 s · $0.0083 | 10/10 |
|  | नया पेज, अलग डेटा और भाषा, जनरेटर बनाने में उपयोग नहीं हुआ | **13.8 s · $0.0023** | 28.7 s · $0.0057 | 10/10 |
|  | Python स्क्रिप्ट, जिसे कोई जनरेटर कवर नहीं करता | **19.2 s · $0.0033** | 16.6 s · $0.0030 | 10/10 |

[प्रॉम्प्ट, विधि, सीमाएँ और प्रति सत्र डेटा](../benchmarks/2026-11-01-multi-model.md).

---

## 🎯 यह क्या करता है

| कमांड | विवरण |
|---|---|
| `simplicio map --repo .` | LLM के लिए रिपॉजिटरी मैप करता है |
| `simplicio memory "query"` | न्यूरल रिकॉल (FTS + वेक्टर) |
| `simplicio edit '{...}'` | निर्धारित फ़ाइल संपादन |
| `simplicio coding-loop "task"` | टेस्ट पास होने तक दोहराता है |
| `simplicio deliver certify` | शिप करने से पहले 5 गुणवत्ता गेट |
| `simplicio run "task" --agents N` | मल्टी-एजेंट ऑर्केस्ट्रेशन |
---

## 🏗️ आर्किटेक्चर

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

**LLM तर्क करता है। Simplicio निर्धारित रूप से निष्पादित करता है।**

---

## ✨ सुविधाएँ

- 🏠 **स्थानीय-प्रथम** — अंतर्निहित llama.cpp, केवल ज़रूरत पड़ने पर रिमोट पर स्केल करें
- 🪜 **स्तरीय एजेंट** — भुगतान वाले क्लाउड से पहले 64 → 100 → 200 → 600 स्थानीय एजेंट
- 🔇 **शैनन नवीनता गेट** — डुप्लिकेट आउटपुट फ़िल्टर करता है (डीडुप पर शून्य टोकन)
- 🔒 **सीलबंद रसीदें** — प्रति आर्टिफैक्ट sha256, छेड़छाड़-रोधी साक्ष्य श्रृंखला
- 🛡️ **5 डिलीवरी गेट** — स्वीकृति, सत्यापन, रन-वेरिफाई, रिग्रेशन, सेल्फ-रिव्यू
- ⚡ **एक्शन गेट** — चैट-आरंभित म्यूटेशन के लिए जोखिम वर्गीकरण + ब्लॉकलिस्ट
- 🔌 **MCP/ACP** — मॉडल कॉन्टेक्स्ट प्रोटोकॉल + एजेंट क्लाइंट प्रोटोकॉल
- 🌐 **गेटवे** — टेलीग्राम, डिस्कॉर्ड, स्लैक, व्हाट्सएप
- 🧩 **स्किल सिस्टम** — पुन: प्रयोज्य क्षमताओं को लोड और चेन करता है
- 💾 **मेमोरी DB** — सत्रों में स्थायी FTS + वेक्टर रिकॉल
- 🔀 **LLM राउटर** — कोई LLM नहीं → स्थानीय LLM → रिमोट LLM स्वचालित रूप से
- 🖥️ **क्रॉस-प्लेटफ़ॉर्म** — macOS, Linux, Windows, एकल बाइनरी

---

## 🎁 मुफ्त सार्वजनिक बीटा

**निर्धारित कमांड हमेशा के लिए मुफ्त हैं:**
`map`, `validate`, `edit`, `deliver`, `checkpoint`

**AI सुविधाएँ सार्वजनिक बीटा के दौरान बिना किसी समाप्ति तिथि के मुफ्त हैं।**
भविष्य के अपडेट में बिलिंग निर्धारित की जाएगी।

```bash
simplicio license status
```

---

## 📋 आवश्यकताएँ

| आवश्यकता | न्यूनतम | अनुशंसित |
|---|---|---|
| RAM | 8 GB | 16 GB+ |
| स्टोरेज | 5 MB | 1.5 GB (स्थानीय LLM के साथ) |
| OS | macOS 13+, Linux, Windows 10+ | macOS ARM64 |
| टर्मिनल | कोई भी आधुनिक टर्मिनल | WezTerm / Alacritty / Ghostty |

---

## 🌐 पारिस्थितिकी तंत्र

- [वेबसाइट](https://simpleti.com.br/simplicio/#start) — पूर्ण दस्तावेज़, बेंचमार्क, इंस्टॉल
- [डिस्कॉर्ड](https://discord.gg/wM6tr7xVb) — समुदाय और सहायता

---

## 📄 लाइसेंस

Proprietary. बाइनरी डाउनलोड और उपयोग करने के लिए मुफ्त है। AI सुविधाएँ
सार्वजनिक बीटा के दौरान मुफ्त हैं। [LICENSE](../plugins/simplicio/LICENSE) देखें।

---

## ⭐ स्टार इतिहास

<a href="https://star-history.com/#simpletibr/simplicio&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" />
    <img alt="स्टार हिस्ट्री चार्ट" src="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" width="100%" />
  </picture>
</a>

---

## 💬 समुदाय

- [डिस्कॉर्ड](https://discord.gg/wM6tr7xVb) — चैट, सहायता, प्रारंभिक पहुँच
- [GitHub Issues](https://github.com/simpletibr/simplicio/issues) — बग और फीचर अनुरोध

---

<p align="center">
  <strong>🔥 Simplicio 🔥</strong>
</p>
