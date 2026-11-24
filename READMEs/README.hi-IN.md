<div align="center">

<img src="../assets/simplicio-icon-192.png" alt="Simplicio लोगो" width="96" height="96">

<h1>Simplicio</h1>

<p><b>UltraFast Mode for all.</b></p>

<p><b>एक ही एजेंट, एक ही मॉडल, एक ही जॉब: 121&nbsp;s&nbsp;→&nbsp;25&nbsp;s, और $0.0226&nbsp;→&nbsp;$0.0076।</b></p>

<p>Simplicio के बिना → Simplicio 3.15.0 के साथ। Claude Code में Claude Haiku 5.5 के साथ, एक छोटे कोडिंग जॉब के 3 रन का मीडियन।</p>

<p>Simplicio आपकी मशीन पर चलता है और उस कोडिंग एजेंट में टूल जोड़ता है जो आप पहले से इस्तेमाल करते हैं।</p>

<p>
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=2fe6a0&label=release" alt="नवीनतम रिलीज़"></a>
  <a href="https://simpleti.com.br/simplicio/docs"><img src="https://img.shields.io/badge/docs-simpleti.com.br-ffd23f" alt="दस्तावेज़"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="स्टार्स"></a>
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="लाइसेंस: मालिकाना">
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
  हिन्दी ·
  <a href="README.ar-SA.md">العربية</a>&lrm; ·
  <a href="README.he-IL.md">עברית</a>&lrm; ·
  <a href="README.id-ID.md">Bahasa Indonesia</a> ·
  <a href="README.ms-MY.md">Bahasa Melayu</a>
</p>

<p align="center"><sub>यह फ़ाइल <a href="../README.md">English README</a> का अनुवाद है। अगर दोनों में फ़र्क हो, तो अंग्रेज़ी पेज ही संदर्भ है। चार्ट और चित्र अंग्रेज़ी में ही हैं।</sub></p>

</div>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-dark.svg">
    <img src="../assets/benchmark-2026-11-22-light.svg" width="840" alt="बार चार्ट, जिसमें तीन मापों पर Simplicio के बिना, Simplicio 3.14.0 और Simplicio 3.15.0 की तुलना है। हर सेटअप के तीन सेशन का मीडियन। पूरे जॉब का समय: 121 s Simplicio के बिना, 104 s Simplicio 3.14.0 के साथ और 25 s Simplicio 3.15.0 के साथ। लागत: $0.0226, $0.0220 और $0.0076। आउटपुट टोकन: 18,162, 19,722 और 3,211।">
  </picture>
</p>

<p align="center">
  <sub>हर सेटअप के 3 सेशन का मीडियन (Simplicio के बिना, Simplicio 3.14.0 और Simplicio 3.15.0)। Claude Code 2.1.330 में Claude Haiku 5.5, 2026-11-22। हर सेटअप ने 9 में से 9 चरण पूरे किए। हर बार पर पतली रेखा सबसे कम सेशन से सबसे ज़्यादा सेशन तक जाती है।<br>
  <a href="../benchmarks/2026-11-22-standard-benchmark.md">विधि, डेटा और सीमाएँ</a></sub>
</p>

<p align="center">
  <sub>इसे साथ में पढ़ें: एक छोटा जॉब, हर सेटअप के लिए तीन सेशन, एक मॉडल। बाहरी जाँच का दायरा प्रॉम्प्ट से सीमित है। पीक मेमोरी ज़्यादा थी: 270 MB के मुकाबले 375 MB। Simplicio के बिल्ड रिलीज़ कमिट से कंपाइल किए गए थे, जिनमें साइन-इन बंद था।</sub>
</p>

<p align="center">Simplicio यह नतीजा कैसे हासिल करता है, यह प्रकाशित नहीं किया गया है। मापन प्रकाशित किए गए हैं, उन मामलों समेत जहाँ Simplicio पीछे रहता है।</p>

<p align="center">
  <b>आज़माएँ:</b> <a href="#install">इंस्टॉल</a> · <a href="#first-run">पहली बार चलाना</a><br>
  <a href="#what-simplicio-is">यह क्या है</a> ·
  <a href="#the-measurement">मापन</a> ·
  <a href="#works-with-the-agent-you-already-use">एजेंट</a> ·
  <a href="#command-line">कमांड</a> ·
  <a href="#safety-and-privacy">गोपनीयता</a> ·
  <a href="#questions-people-ask">सवाल</a> ·
  <a href="#documentation-and-community">दस्तावेज़</a>
</p>

<a id="what-simplicio-is"></a>

## Simplicio क्या है

Simplicio एक लोकल प्रोग्राम है जो आपके पहले से इस्तेमाल हो रहे कोडिंग एजेंट को अल्ट्रा-फ़ास्ट मोड देता है, चाहे एजेंट कोई भी हो और मॉडल कोई भी। इस पेज के आंकड़े एक एजेंट और एक मॉडल से आए हैं; नीचे का हिस्सा ठीक-ठीक बताता है कि क्या मापा गया।

- **आप अपना एजेंट और अपना मॉडल रखते हैं।** Simplicio, Claude Code, Codex, Cursor या उनके पीछे जो भी मॉडल हो, उसकी जगह नहीं लेता।
- **एक हस्ताक्षरित बाइनरी** अपने आप आपके एजेंट्स में रजिस्टर होती है और आपकी मशीन पर लोकल STDIO MCP सर्वर के रूप में चलती है।
- **जो बदलता है, वह सेशन है।** उसका समय और उसकी लागत।

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/diagram-where-simplicio-runs-dark.svg">
    <img src="../assets/diagram-where-simplicio-runs-light.svg" width="840" alt="आरेख। आपकी मशीन पर: आप, आपका कोडिंग एजेंट, Simplicio और आपकी रिपॉज़िटरी। एजेंट लोकल STDIO (MCP) पर Simplicio से बात करता है। एजेंट पहले की तरह आपके मॉडल प्रदाता से बात करता है। Simplicio साइन-इन और प्लान जाँच के लिए SimpleTI से और रिलीज़ जाँच के लिए GitHub से बात करता है, और दोनों में से किसी में भी रिपॉज़िटरी की सामग्री नहीं जाती।">
  </picture>
</p>

<p align="center">
  <sub>यह डिफ़ॉल्ट फ़्लो है। <a href="#safety-and-privacy">पूरी सूची</a> में बाकी सेवाएँ हैं।</sub>
</p>

<details>
<summary>MCP और STDIO</summary>

MCP का मतलब है Model Context Protocol, यानी वह तरीका जिससे कोडिंग एजेंट बाहरी टूल्स को कॉल करता है। STDIO का मतलब है कि एजेंट प्रोग्राम को खुद शुरू करता है और उसके स्टैंडर्ड इनपुट और आउटपुट के ज़रिए उससे बात करता है।

यह आपके एजेंट को टूल देता है: रिपॉज़िटरी का मैप, सीमित कॉन्टेक्स्ट, स्ट्रक्चर्ड एडिट और जाँच। [मुख्य टूल](#works-with-the-agent-you-already-use) नीचे सूचीबद्ध हैं।

आप एक हस्ताक्षरित नेटिव बाइनरी इंस्टॉल करते हैं। इंस्टॉलर हस्ताक्षर की पुष्टि करता है, फिर आपकी मशीन पर मिले एजेंट्स में Simplicio को रजिस्टर करता है।

</details>

<a id="the-measurement"></a>

## मापन

एक ही जॉब, Simplicio के साथ और बिना, एक ही तरीके से चलाया गया: एक एजेंट सेशन में तीन चरण, और हर नतीजे की जाँच सेशन के बाहर से।

1. यूज़र लिस्टिंग बनाएँ: एक API और एक पेज, जिसमें टेबल, सर्च और सॉर्टिंग हो।
2. इसमें बदलाव करें: एक कॉलम हटाएँ, रोल के हिसाब से फ़िल्टर और एक डेट कॉलम जोड़ें।
3. एक सरल रजिस्ट्रेशन जोड़ें: एक `POST` एंडपॉइंट, जो इनपुट की जाँच करे, और एक फ़ॉर्म पेज।

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-sessions-dark.svg">
    <img src="../assets/benchmark-2026-11-22-sessions-light.svg" width="840" alt="हर सेशन का स्कैटर प्लॉट, जिसमें पूरे जॉब का समय क्षैतिज अक्ष पर और एजेंट द्वारा रिपोर्ट की गई लागत ऊर्ध्वाधर अक्ष पर है। Simplicio 3.15.0, हरे डायमंड: 23 से 27 s और $0.0071 से $0.0098। Simplicio 3.14.0, भूरे स्क्वेयर: 90 से 106 s और $0.0214 से $0.0249। Simplicio के बिना, खोखले सर्कल: 97 से 172 s और $0.0186 से $0.0280।">
  </picture>
</p>

| माप | Simplicio के बिना | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| जॉब का समय | 121 s<br><sub>97–172</sub> | 104 s<br><sub>90–106</sub> | **25 s**<br><sub>23–27</sub> |
| रिपोर्ट की गई लागत | $0.0226<br><sub>0.0186–0.0280</sub> | $0.0220<br><sub>0.0214–0.0249</sub> | **$0.0076**<br><sub>0.0071–0.0098</sub> |
| मॉडल रिक्वेस्ट | 25<br><sub>19–33</sub> | 18<br><sub>18–22</sub> | **10**<br><sub>10–10</sub> |
| टूल कॉल | 22<br><sub>16–30</sub> | 15<br><sub>15–19</sub> | **7**<br><sub>7–7</sub> |
| आउटपुट टोकन | 18,162<br><sub>15,599–23,328</sub> | 19,722<br><sub>18,764–24,997</sub> | **3,211**<br><sub>3,068–3,573</sub> |
| इनपुट टोकन | 34,691<br><sub>30,447–42,543</sub> | 34,141<br><sub>33,121–40,017</sub> | 18,755<br><sub>18,466–33,300</sub> |
| CPU समय | 8.5 s<br><sub>8.5–9.2</sub> | 10.0 s<br><sub>8.9–10.0</sub> | **5.3 s**<br><sub>5.3–5.5</sub> |
| पीक मेमोरी | **270 MB**<br><sub>248–274</sub> | 436 MB<br><sub>432–439</sub> | 375 MB<br><sub>365–379</sub> |
| पूरे हुए चरण | 9 में से 9 | 9 में से 9 | 9 में से 9 |

हर सेटअप के 3 सेशन का मीडियन; हर मान के नीचे सबसे कम से सबसे ज़्यादा सेशन तक की रेंज। बोल्ड उस पंक्ति का सबसे अच्छा मान दिखाता है, जब उसकी रेंज बाकी से ओवरलैप नहीं करती। "9 में से 9" का मतलब है 3 सेशन में से हर एक में 3 चरण, और हर चरण ने हर बाहरी जाँच पास की।

हर सेशन की रिक्वेस्ट और टूल कॉल।

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-work-dark.svg">
    <img src="../assets/benchmark-2026-11-22-work-light.svg" width="840" alt="यूनिट चार्ट, जिसमें हर मॉडल रिक्वेस्ट या टूल कॉल के लिए एक निशान है। मीडियन, 3 सेशन। मॉडल रिक्वेस्ट: Simplicio के बिना 25, 18 Simplicio 3.14.0 के साथ और 10 Simplicio 3.15.0 के साथ। टूल कॉल: 22, 15 और 7।">
  </picture>
</p>

हर चरण का समय, एक ही साझा स्केल पर।

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-steps-dark.svg">
    <img src="../assets/benchmark-2026-11-22-steps-light.svg" width="840" alt="हर चरण का मीडियन समय, एक ही साझा स्केल पर। चरण 1, बिल्ड: Simplicio के बिना 57.3 s, 53.7 s Simplicio 3.14.0 के साथ और 5.8 s Simplicio 3.15.0 के साथ। चरण 2, बदलाव: 17.3 s, 15.2 s और 8.9 s। चरण 3, रजिस्ट्रेशन: 31.4 s, 27.5 s और 10.3 s।">
  </picture>
</p>

<details>
<summary>हर चरण के सटीक आँकड़े</summary>

हर सेल में चरण का मीडियन समय और मीडियन लागत है:

| चरण | Simplicio के बिना | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. बिल्ड | 57.3 s / $0.0111 | 53.7 s / $0.0137 | 5.8 s / $0.0022 |
| 2. बदलाव | 17.3 s / $0.0040 | 15.2 s / $0.0032 | 8.9 s / $0.0023 |
| 3. रजिस्ट्रेशन | 31.4 s / $0.0075 | 27.5 s / $0.0056 | 10.3 s / $0.0026 |

</details>

**इसे कैसे पढ़ें।** पूरा जॉब लगभग एक-तिहाई लागत पर 4.9 गुना तेज़ चला; Simplicio के बिना सबसे तेज़ सेशन (97.1 s) भी, 3.15.0 वाले सबसे धीमे सेशन (26.6 s) से 3.7 गुना धीमा था। [विधि, सीमाएँ](../benchmarks/2026-11-22-standard-benchmark.md#limits)

<details>
<summary>हर संख्या की परिभाषा</summary>

- अनुपात बिना राउंड किए मीडियन से आते हैं। पिछले रिलीज़ के मुकाबले पूरा जॉब 4.2 गुना तेज़ चला।
- हर मीडियन अलग से लिया गया है, इसलिए चरणों का योग पूरे जॉब के मीडियन के बराबर नहीं होता।
- सबसे बुरी स्थिति: Simplicio के बिना सबसे तेज़ सेशन (97.1 s) भी, Simplicio 3.15.0 वाले सबसे धीमे सेशन (26.6 s) से 3.7 गुना धीमा था, और Simplicio के बिना सबसे सस्ता सेशन ($0.0186) भी, Simplicio वाले सबसे महँगे सेशन ($0.0098) से 1.9 गुना महँगा था।
- बेसलाइन है Claude Code 2.1.330, उसके अपने टूल्स के साथ, बिना MCP सर्वर और बिना Simplicio कॉन्फ़िगरेशन के।
- हर चरण की जाँच सेशन के बाहर से होती है: API को HTTP पर कॉल किया जाता है, और पेज headless Chrome में लोड होते हैं, यानी ऐसा Chrome जिसकी कोई विंडो नहीं होती।
- ये जाँचें सर्च बॉक्स, सॉर्टिंग, सेव के बाद का रीडायरेक्ट, पेज का लुक या कोड की क्वालिटी नहीं जाँचतीं।
- एक मॉडल रिक्वेस्ट मॉडल को की गई एक कॉल है; एक टूल कॉल एजेंट द्वारा किसी टूल का एक इस्तेमाल है।
- रिपोर्ट की गई लागत इस्तेमाल किए गए टोकन गुणा मॉडल की प्रकाशित कीमत है। इसमें सिर्फ़ मॉडल टोकन गिने जाते हैं। यह कोई इनवॉइस नहीं है।
- इनपुट टोकन की रेंज आपस में ओवरलैप करती हैं, इसलिए इस रन में इनपुट टोकन में कोई फ़र्क होने का दावा नहीं है।
- एक मशीन पर एक बार में चार सेशन चले: समय की तुलना सिर्फ़ इसी राउंड के भीतर करें।

</details>

<a id="where-simplicio-does-not-win"></a>

### जहाँ Simplicio आगे नहीं रहता

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-memory-dark.svg">
    <img src="../assets/benchmark-2026-11-22-memory-light.svg" width="840" alt="पीक मेमोरी, 3 सेशन का मीडियन: Simplicio के बिना 270 MB, सबसे कम; 436 MB, Simplicio 3.14.0 के साथ, 61% ज़्यादा; 375 MB, Simplicio 3.15.0 के साथ, 39% ज़्यादा।">
  </picture>
</p>

- **मेमोरी।** पीक मेमोरी सादे एजेंट से 39% ज़्यादा थी: 270 MB के मुकाबले 375 MB।
- **पिछले रिलीज़ में इस जॉब पर कोई फ़ायदा नहीं दिखा।** Simplicio 3.14.0 की लागत Simplicio के बिना जितनी ही थी।
- **एक छोटी एकबारगी Python स्क्रिप्ट।** Simplicio 3.10.8 धीमा था (19.6 s के मुकाबले 11.4 s) और उसे फिर से नहीं मापा गया।
- **एक छोटा पेज, मज़बूत मॉडल।** Simplicio 3.15.0 14% से 47% तक धीमा था।
- **जो आप इंस्टॉल करते हैं, वह ठीक वही नहीं है जो मापा गया।** बिल्ड रिलीज़ कमिट से कंपाइल किए गए थे, साइन-इन बंद करके।
- **नमूना छोटा है।** हर सेटअप के तीन सेशन, एक मॉडल, एक प्रोजेक्ट।

<details>
<summary>पूरी सीमाएँ</summary>

- **मेमोरी।** पीक मेमोरी सादे एजेंट से 39% ज़्यादा थी: 270 MB के मुकाबले 375 MB।
- **पिछले रिलीज़ में इस जॉब पर कोई फ़ायदा नहीं दिखा।** Simplicio 3.14.0 की लागत Simplicio के बिना जितनी ही थी, और उसके समय का फ़र्क रन-से-रन फैलाव के भीतर है। फ़ायदा 3.15.0 के साथ आया।
- **एक छोटी एकबारगी Python स्क्रिप्ट।** पिछले राउंड में, आज़माए गए हर मॉडल पर Simplicio 3.10.8 सादे एजेंट से धीमा था: Claude Sonnet 5.5 पर Claude Code में 19.6 s और $0.0548, जबकि सादे एजेंट पर 11.4 s और $0.0283। इसे 3.15.0 पर फिर से नहीं मापा गया।
- **एक छोटा पेज, मज़बूत मॉडल।** Sonnet 5.5 या Opus 5.5 पर Simplicio 3.15.0 के मीडियन आज़माए गए सभी 6 मामलों में 14% से 47% धीमे और 14% से 41% महँगे थे; इनमें से 2 में एक ही रन था। हर पेज सही था। Sonnet 5.5, बनाना: 24 s और $0.082, 20 s और $0.066 के मुकाबले। सुधार पर काम चल रहा है, अभी रिलीज़ नहीं हुआ।
- **जो आप इंस्टॉल करते हैं, वह ठीक वही नहीं है जो मापा गया।** बिल्ड रिलीज़ कमिट से कंपाइल किए गए थे, साइन-इन और बैकग्राउंड प्रोसेस बंद करके। हस्ताक्षरित डाउनलोड नहीं मापे गए।
- **नमूना छोटा है।** हर सेटअप के तीन सेशन, एक मॉडल, एक छोटा नया प्रोजेक्ट, एक मशीन, और एक साथ चार सेशन; इनमें से कोई हटाया या दोबारा नहीं चलाया गया। अनुपात इस जॉब को मापते हैं, आपका जॉब नहीं, और हमने यह नहीं मापा कि आपका कितना काम इस जॉब जैसा है।

</details>

### खुद जाँचें

[रिपोर्ट](../benchmarks/2026-11-22-standard-benchmark.md) तीनों प्रॉम्प्ट प्रकाशित करती है (पुर्तगाली में, अनुवाद के साथ), हर बाहरी जाँच और हर सेशन; [डेटा फ़ाइल](../benchmarks/2026-11-22-standard-benchmark.json) उन्हें JSON में देती है। टेस्ट हार्नेस प्रकाशित नहीं है।

<a id="install"></a>

## इंस्टॉल

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

Windows पर `py -m pip install --upgrade simplicio-installer` इस्तेमाल करें, और फिर `simplicio install`।

इंस्टॉलर हस्ताक्षरित रिलीज़ की पुष्टि करता है और जो एजेंट वह ढूँढता है उनमें Simplicio अपने आप रजिस्टर कर देता है। फिर `simplicio auth login` से साइन इन करें।

<details>
<summary>इंस्टॉल का विवरण</summary>

- यह आपके प्लेटफ़ॉर्म के लिए सबसे नया हस्ताक्षरित रिलीज़ डाउनलोड करता है, और इंस्टॉल की गई बाइनरी बदलने से पहले उसका SHA-256 और Ed25519 हस्ताक्षर जाँचता है।
- बाइनरी `~/.simplicio/bin/` में रखी जाती है (Windows पर `%USERPROFILE%\.simplicio\bin\` में), और जो एजेंट मिलते हैं उनमें Simplicio अपने आप रजिस्टर हो जाता है। रजिस्ट्रेशन में विफलता हो तो इंस्टॉलर सफलता की रिपोर्ट करने के बजाय रुक जाता है।
- जो एजेंट पहले से खुला है, उसे रीस्टार्ट करें ताकि वह अपनी कॉन्फ़िगरेशन दोबारा लोड करे। अगर Python की script डायरेक्टरी आपके `PATH` पर नहीं है, तो पहले उसे जोड़ें।

**साइन-इन।** बीटा के दौरान भी Google साइन-इन ज़रूरी है। `simplicio auth login` चलाएँ, फिर `simplicio auth status --json` चलाएँ, और `active: true` दिखने पर आगे बढ़ें। रजिस्ट्रेशन साइन-इन से पहले भी हो जाता है। किसी एजेंट की कॉन्फ़िगरेशन में कभी पासवर्ड या टोकन न डालें।

यह पक्का करने के लिए कि Simplicio लोड हो गया है, एजेंट की MCP सर्वरों की सूची में `simplicio` खोजें। Claude Code में `/mcp` जुड़े हुए सर्वर दिखाता है। इंस्टॉलर पहले पढ़ना चाहते हैं? वह [install.sh](../install.sh) है।

अपडेट करने के लिए किसी भी समय कोई भी इंस्टॉलर फिर से चलाएँ: वह सबसे नया रिलीज़ ढूँढ लेता है। `install.sh` और `install.ps1` इस रिपॉज़िटरी के रूट में हैं।

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

- `--doctor` इंस्टॉलेशन की जाँच करता है।
- `--uninstall --keep-data` इंस्टॉल की गई बाइनरी हटाता है और आपका डेटा रखता है। इसमें `~/.simplicio/login.json` में रखी 30 दिन की Google साइन-इन स्थिति भी शामिल है।
- `--uninstall --purge` सिर्फ़ वह स्थिति हटाता है जिसे Simplicio मैनेज करता है, जिसमें साइन-इन स्थिति भी शामिल है। यह `~/.simplicio/.env` रखता है, जहाँ प्रदाता के क्रेडेंशियल हो सकते हैं। purge के लिए `SIMPLICIO_CONFIRM_PURGE=1` ज़रूरी है।
- अनइंस्टॉल आपके एजेंट्स की कॉन्फ़िगरेशन नहीं बदलता। Simplicio की एंट्रियाँ हर एजेंट में तब तक रहती हैं, जब तक आप उन्हें उस एजेंट की अपनी सेटिंग्स में हटा नहीं देते।
- किसी प्रोजेक्ट के अपने `.simplicio` फ़ोल्डर का डेटा `--keep-data` से नहीं हटता। `--purge` चुनने से पहले देख लें कि लक्ष्य क्या है।

पूरा विवरण: [INSTALL.md](../INSTALL.md)।

</details>

<a id="first-run"></a>

## पहली बार चलाना

```bash
simplicio version
cd my-project
simplicio onboard
```

`simplicio version` इंस्टॉल की जाँच करता है; `simplicio onboard` प्रोजेक्ट तैयार करता है। फिर वहाँ अपना एजेंट खोलें।

<a id="works-with-the-agent-you-already-use"></a>

## आपके मौजूदा एजेंट के साथ काम करता है

इंस्टॉलर रजिस्ट्रेशन का काम Simplicio के अपने रजिस्ट्रार को सौंपता है। जिन एजेंट्स को वह कॉन्फ़िगर करना जानता है, उनमें वह Simplicio की एंट्री लिखता है, जिनमें Claude Code, Codex, Cursor, Visual Studio Code, OpenCode, Gemini CLI और Kiro शामिल हैं।

रजिस्ट्री [`plugins/simplicio/host-surfaces.json`](../plugins/simplicio/host-surfaces.json) 43 एजेंट आईडी बताती है; मैट्रिक्स [`docs/hosts/compatibility-matrix.md`](../docs/hosts/compatibility-matrix.md) 12 को समर्थित और 29 को `unverified` मार्क करती है। किसी `unverified` इंटीग्रेशन को बिना परखा हुआ मानें।

<details>
<summary>सभी 43 एजेंट</summary>

- रजिस्ट्री 43 एजेंट आईडी बताती है और हर एक तक Simplicio कैसे पहुँचता है: Simplicio द्वारा लिखी गई MCP एंट्री (23), नेटिव प्लगइन या एक्सटेंशन (5), पोर्टेबल प्लगइन पैकेज (4), गाइडेड सेटअप जिसे आप खुद फ़ॉलो करते हैं (9), या कोई दूसरा कमांड-लाइन टूल (2)।
- मैट्रिक्स में Codex और Gemini CLI की कोई पंक्ति नहीं है। जहाँ रजिस्ट्री कहती है कि Simplicio एंट्री लिखता है, वहाँ भी `unverified` इंटीग्रेशन को बिना परखा हुआ मानें।
- 23 एजेंट्स के लिए [`docs/hosts/`](../docs/hosts/) में गाइड है। जिन एजेंट्स तक प्लगइन से पहुँचा जाता है, उनमें प्लगइन एक अलग चरण में लागू होता है जो आपकी सहमति माँगता है; उसका विवरण [INSTALL.md](../INSTALL.md) में है।

| Simplicio उस तक कैसे पहुँचता है | संख्या | एजेंट्स |
|---|---|---|
| Simplicio द्वारा लिखी गई MCP एंट्री | 23 | **xAI Grok Build**, MiMo Code, Amp, OpenClaude, Antigravity, **Pi**, **oh-my-pi**, Goose, Auggie, Autohand Code, Charm, Cline, Command Code, Continue, Droid, Kilocode, Kimi, Mistral Vibe, Rovo Dev, **Visual Studio Code**, **Meta Muse Code**, **OpenMausBot**, **OpenMuse (Python)** |
| नेटिव प्लगइन या एक्सटेंशन | 5 | **Claude Code**, Codex, **OpenCode**, Hermes Agent, Gemini CLI |
| पोर्टेबल प्लगइन पैकेज | 4 | **Cursor**, GitHub Copilot, **Kiro**, Qwen Code |
| गाइडेड सेटअप जिसे आप खुद फ़ॉलो करते हैं | 9 | Devin, Codebuff, CopilotKit OpenDots, CopilotKit OpenBot, agentes.chat, OpenAI dots, xAI Grok Bot, Meta Muse app, Cue by Manus |
| कोई दूसरा कमांड-लाइन टूल | 2 | **OrcaDev / Orca ADE**, T3 Code |

बोल्ड: कंपैटिबिलिटी मैट्रिक्स उस एजेंट को समर्थित मार्क करती है।

</details>

आपके एजेंट को ये मुख्य टूल मिलते हैं:

| टूल | यह आपको क्या देता है |
|---|---|
| `simplicio_map` | रिपॉज़िटरी का संक्षिप्त मैप, ताकि एजेंट उसमें अपना रास्ता पहचान सके |
| `simplicio_context` | किसी काम के लिए ज़रूरी कॉन्टेक्स्ट, सीमित, पूरी फ़ाइलों के बजाय |
| `simplicio_edit` | तैयार योजना से स्ट्रक्चर्ड फ़ाइल एडिट |
| `simplicio_validate` | पाइपलाइन, टेस्ट और डिलीवरी की जाँच |
| `simplicio_run` | Simplicio के नियंत्रण में एक टास्क रन |

[MCP-CONNECT.md](../MCP-CONNECT.md) मुख्य टूल्स का विवरण देता है।

<details>
<summary>मैनुअल कॉन्फ़िगरेशन</summary>

Simplicio एक लोकल STDIO MCP सर्वर है, इसलिए जो एजेंट लोकल MCP सर्वर शुरू कर सकता है, उसे इससे जोड़ा जा सकता है। रजिस्ट्रेशन दोबारा करने के लिए `simplicio mcp register` चलाएँ। सर्वर कमांड है `simplicio serve --mcp --stdio`।

अगर आपका एजेंट आपके लिए कॉन्फ़िगर नहीं हुआ है, तो यह एंट्री उसकी MCP कॉन्फ़िगरेशन में जोड़ें। पाथ को इंस्टॉल की गई बाइनरी के एब्सोल्यूट पाथ से बदलें।

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

Codex TOML पढ़ता है। एजेंट्स `command` को सीधे शुरू करते हैं, इसलिए `~` इस्तेमाल न करें और शेल एक्सपैंशन पर भरोसा न करें। Windows पाथ में फ़ॉरवर्ड स्लैश इस्तेमाल करें, और उदाहरण वाला यूज़र नाम बदल दें।

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

हर एजेंट अपनी फ़ाइल कहाँ रखता है: [MCP-CONNECT.md](../MCP-CONNECT.md)।

</details>

<a id="command-line"></a>

## कमांड लाइन

| कमांड | आपको क्या मिलता है |
|---|---|
| `simplicio map --repo . --for-llm markdown` | रिपॉज़िटरी का संक्षिप्त स्ट्रक्चरल मैप, मॉडल के पढ़ने के लिए लिखा गया |
| `simplicio context --repo .` | किसी काम के लिए सीमित कॉन्टेक्स्ट |
| `simplicio memory query "query" --json` | प्रोजेक्ट जो पहले से जानता है, वह उसकी इंडेक्स की गई मेमोरी से JSON के रूप में याद किया हुआ |
| `simplicio edit --plan plan.json --repo .` | तैयार स्ट्रक्चर्ड एडिट का सेट, जो फ़ाइलों पर लागू होता है |
| `simplicio run "task" --repo . --agents N` | N एजेंट्स के साथ एक टास्क रन, Simplicio के नियंत्रण में |
| `simplicio loop` | राउंड-दर-राउंड चलने वाला काम, जब तक वह स्थिर न हो जाए |

Simplicio के संदेशों में आप ये नाम देखेंगे: Mapper देखता है, Fast प्रोजेक्ट करता है या वापस लाता है, Dev CLI एडिट करता है, Runtime नियंत्रित करता है, और Loop स्थिर होता है।

<a id="safety-and-privacy"></a>

## सुरक्षा और गोपनीयता

यह खंड वर्शन 3.15.0 का विवरण देता है।

- **आपकी मशीन पर रहता है।** मैपिंग, कॉन्टेक्स्ट, एडिट और जाँच Simplicio बाइनरी के अंदर चलते हैं।
- **SimpleTI को (simpleti.com.br)।** सिर्फ़ साइन-इन और प्लान जाँच, रिपॉज़िटरी की कोई सामग्री नहीं।
- **GitHub को।** एक रिलीज़ जाँच, जिसे आप बंद कर सकते हैं।
- **कोई एनालिटिक्स नहीं।** Simplicio कोई एनालिटिक्स, क्रैश रिपोर्ट या उपयोग का डेटा अपलोड नहीं करता।
- **आपकी कॉन्फ़िगर की गई सेवाओं को।** वे वही पाती हैं जो वह फ़ीचर भेजता है, और उसमें प्रॉम्प्ट और कोड शामिल हो सकते हैं।
- **दो फ़ीचर बिना किसी कॉन्फ़िगरेशन के इंटरनेट पर सार्वजनिक रूप से उपलब्ध सेवाओं तक पहुँचते हैं।** वेब सर्च (DuckDuckGo) और डिपेंडेंसी ऑडिट (osv.dev); इनमें से कोई फ़ाइलों की सामग्री नहीं भेजता।
- **डाउनलोड।** GitHub से; कुछ हेल्पर स्क्रिप्ट्स टूल्स PyPI या npm से भी लाती हैं।

<details>
<summary>पूरा विवरण</summary>

- **आपकी मशीन पर रहता है।** मैपिंग, कॉन्टेक्स्ट, एडिट और जाँच Simplicio बाइनरी के अंदर चलते हैं। यह नतीजे उसी मशीन पर आपके एजेंट को देता है। उपयोग और बचत के रिकॉर्ड लोकल फ़ाइलें हैं। आपका एजेंट अपने मॉडल प्रदाता को क्या भेजता है, यह पहले की तरह एजेंट ही तय करता है।
- **SimpleTI को (simpleti.com.br)।** सिर्फ़ साइन-इन और प्लान जाँच, रिपॉज़िटरी की कोई सामग्री नहीं: कोई फ़ाइल, फ़ाइल पाथ, प्रॉम्प्ट या एडिट नहीं।
  - इनमें आपका साइन-इन टोकन, Simplicio का वर्शन और आपके कंप्यूटर का होस्ट नाम जाता है। एक वैकल्पिक लाइसेंस लुकअप में आपका अकाउंट ईमेल भी जाता है।
  - जवाब में वे आपका अकाउंट ईमेल, नाम और प्लान लौटाते हैं।
- **GitHub को।** नए रिलीज़ की एक बैकग्राउंड जाँच, अधिकतम लगभग हर 12 घंटे में एक बार, जिसमें आपके या आपके कोड के बारे में कुछ नहीं जाता। इसे बंद करने के लिए `SIMPLICIO_DISABLE_AUTO_UPDATE=1` सेट करें। अपडेट में नई बाइनरी GitHub से आती है, और पुरानी को बदलने से पहले उसका SHA-256 और हस्ताक्षर जाँचे जाते हैं।
- **कोई एनालिटिक्स नहीं।** Simplicio 3.15.0 और उसकी फ़ाइलें, जो आपके एजेंट्स में इंस्टॉल होती हैं, इसके लिए जाँची गई हैं: कोई एनालिटिक्स, क्रैश रिपोर्ट या उपयोग का डेटा अपलोड नहीं करता। इंस्टॉल हुए हुक सिर्फ़ लोकल प्रोग्राम चलाते हैं (Simplicio बाइनरी और, वैकल्पिक प्लगइन के लिए, लोकल स्क्रिप्ट); कोई भी नेटवर्क से संपर्क नहीं करता।
- **आपकी कॉन्फ़िगर की गई सेवाओं को।** मॉडल प्रदाता, GitHub, Jira, चैट नोटिफ़ायर या टीम कैश को वही मिलता है जो उस फ़ीचर से भेजा जाता है, जिसमें प्रॉम्प्ट और कोड शामिल हो सकते हैं। मॉडल प्रदाता के अनुरोधों में एक हेडर होता है, जो Simplicio को क्लाइंट के रूप में बताता है।
- **दो फ़ीचर बिना किसी कॉन्फ़िगरेशन के इंटरनेट पर सार्वजनिक रूप से उपलब्ध सेवाओं तक पहुँचते हैं।** इनमें से कोई फ़ाइलों की सामग्री नहीं भेजता।
  - वेब सर्च, जब वह चलती है, खोज क्वेरी DuckDuckGo को भेजती है, जब तक आप कोई दूसरी सर्च सेवा कॉन्फ़िगर न करें। Simplicio की अपनी चैट में, वेब सवाल जैसा दिखने वाला संदेश वही क्वेरी बन सकता है।
  - डिपेंडेंसी सिक्योरिटी ऑडिट, जब आप उसे चलाते हैं, आपकी डिपेंडेंसी के नाम और वर्शन osv.dev को भेजता है।
- **डाउनलोड।** इंस्टॉलर और अपडेट का रास्ता GitHub से डाउनलोड करते हैं। कुछ वैकल्पिक हेल्पर स्क्रिप्ट्स, जब आप उन्हें चलाते हैं, अपने टूल्स PyPI या npm से लाती हैं। जो एजेंट प्लगइन Simplicio बाइनरी नहीं पाता, वह GitHub से आधिकारिक इंस्टॉलर लाता है, जो एक कमिट पर पिन किया गया हो और SHA-256 से जाँचा गया हो।

**हस्ताक्षरित रिलीज़।** हर रिलीज़ अपनी बाइनरी SHA-256 चेकसम, Ed25519 हस्ताक्षर, SBOM (बिल्ड में क्या है उसकी सूची) और बिल्ड प्रोवेनेंस के साथ प्रकाशित करता है।

इंस्टॉलर और अपडेट का रास्ता इंस्टॉल की गई बाइनरी बदलने से पहले चेकसम और हस्ताक्षर जाँचते हैं। स्टेबल रिलीज़ के लिए हस्ताक्षर का न होना या अमान्य होना, और चेकसम का मेल न खाना, सख़्त विफलता है। अनुबंध [docs/UPDATE_SIGNATURE_CONTRACT.md](../docs/UPDATE_SIGNATURE_CONTRACT.md) में है।

**इंस्टॉलर आपके एजेंट में क्या बदलता है।**

- यह एजेंट की MCP कॉन्फ़िगरेशन में एक Simplicio एंट्री जोड़ता है और बाकी कॉन्फ़िगरेशन वैसी ही रखता है।
- Claude Code में यह `mcp__simplicio__*` की अनुमति भी देता है, ताकि ऑटो मोड में कोई Simplicio टूल ब्लॉक न हो।
- जिन एजेंट्स के हुक इंटरफ़ेस को इंस्टॉलर ने सत्यापित किया है, उनमें यह Simplicio के हुक भी इंस्टॉल करता है।
- अनइंस्टॉल इन एंट्रियों को वापस नहीं करता; इंस्टॉल खंड बताता है कि इन्हें कैसे हटाया जाए। [INSTALL.md](../INSTALL.md) बताता है कि इंस्टॉलर क्या लिखता है, और [`docs/hosts/`](../docs/hosts/) में हर एजेंट का गाइड विवरण देता है।

</details>

## इस रिपॉज़िटरी में और भी

<details>
<summary>Desktop ऐप (macOS प्रीव्यू)</summary>

macOS (Apple Silicon) के लिए एक Desktop प्रीव्यू [Simplicio-3.8.47-arm64.dmg](https://github.com/simpletibr/simplicio/releases/download/v3.8.47/Simplicio-3.8.47-arm64.dmg) के रूप में प्रकाशित है। इसका SHA-256 [DESKTOP-SHA256SUMS](../DESKTOP-SHA256SUMS) में है, जो Simplicio बाइनरी के चेकसम से अलग है। DMG में हस्ताक्षर फ़ाइल नहीं है, और उसमें Simplicio 3.8.47 बाइनरी बंडल है।

- Windows Desktop प्रकाशित नहीं है। Windows पर ऊपर का कमांड-लाइन इंस्टॉल इस्तेमाल करें।
- Apple Developer ID साइनिंग और नोटराइज़ेशन नहीं किए गए हैं। पैकेज ad-hoc साइन किया गया है, यानी बिना Apple developer सर्टिफ़िकेट के, और Gatekeeper की स्वीकृति का दावा नहीं है, इसलिए इसे खोलते समय macOS चेतावनी दे सकता है।
- जब तक हस्ताक्षरित Desktop पैकेज प्रकाशित नहीं होता, तब तक ऊपर का कमांड-लाइन इंस्टॉल ही समर्थित सार्वजनिक इंस्टॉलेशन का रास्ता है।

विवरण: [docs/desktop/RELEASE.md](../docs/desktop/RELEASE.md)।

</details>

<details>
<summary>मेंटेनर्स के लिए: बना हुआ फ़्लो आरेख</summary>

- README.md और MCP-CONNECT.md में दर्ज कमांड और टूल्स एक फ़्लो के रूप में बनाए गए हैं, [docs/flow/simplicio.svg](../docs/flow/simplicio.svg), जो एक सोर्स फ़ाइल `docs/flow/simplicio.flow.json` से बनी है।
- इसे `python3 scripts/generate_flow.py` से फिर से बनाएँ, और `python3 scripts/generate_flow.py --check` से ड्रिफ़्ट की जाँच करें।
- जो अनुबंध इसे इस पेज और MCP-CONNECT.md के साथ मेल में रखता है, वह है `python3 -m pytest tests/test_flow_contract.py -q`।
- Langflow इम्पोर्ट की जाँच `scripts/verify_flow_langflow.py` है। कोई सर्वर न चल रहा हो तो वह फ़ेल-क्लोज़्ड होती है (exit 2, `status=blocked`)। सबूत `docs/flow/evidence/` और `docs/flow/render/` के नीचे हैं; [docs/flow/README.md](../docs/flow/README.md) में ज़रूरतें और उसे दोहराने का तरीका है।

</details>

<a id="questions-people-ask"></a>

## लोग जो सवाल पूछते हैं

**क्या तुलना निष्पक्ष है?**<br>
वही एजेंट, वही मॉडल, वही प्रॉम्प्ट, वही प्रोजेक्ट और वही बाहरी जाँच; बेसलाइन में Simplicio नहीं है। देखें [जहाँ Simplicio आगे नहीं रहता](#where-simplicio-does-not-win)।

**क्या मुझे अपना एजेंट या अपना मॉडल बदलना होगा?**<br>
नहीं। Simplicio उसी एजेंट में जुड़ता है जो आप पहले से इस्तेमाल करते हैं।

**क्या मुझे ये नतीजे हमेशा मिलेंगे?**<br>
नहीं। ये सिर्फ़ एक जॉब, एक मॉडल और एक मशीन को मापते हैं।

**क्या यह ओपन सोर्स है?**<br>
नहीं। Simplicio मालिकाना है: एक हस्ताक्षरित बाइनरी। इस रिपॉज़िटरी में इंस्टॉलर, पैकेज, दस्तावेज़ और डेटा हैं।

**इसे कैसे हटाएँ?**<br>
`sh install.sh --uninstall --keep-data` चलाएँ, या Windows पर `pwsh install.ps1 -Uninstall -KeepData`। यह आपके एजेंट्स की कॉन्फ़िगरेशन नहीं बदलता, इसलिए Simplicio की एंट्रियाँ हर एजेंट की अपनी सेटिंग्स में हटाएँ।

**क्या मुझे अकाउंट चाहिए?**<br>
हाँ। बीटा के दौरान भी Google साइन-इन ज़रूरी है। `simplicio auth login` चलाएँ।

**क्या मेरा कोड मेरी मशीन से बाहर जाता है?**<br>
मैपिंग, कॉन्टेक्स्ट, एडिट और जाँच आपकी मशीन पर चलते हैं; SimpleTI और GitHub को रिपॉज़िटरी की कोई सामग्री नहीं मिलती। [विवरण](#safety-and-privacy)।

<a id="documentation-and-community"></a>

## दस्तावेज़ और समुदाय

- **वेबसाइट:** [simpleti.com.br/simplicio](https://simpleti.com.br/simplicio/)
- **दस्तावेज़:** [simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)
- **Discord:** [समुदाय से जुड़ें](https://discord.gg/wM6tr7xVb)
- **Issues:** [GitHub इश्यू ट्रैकर](https://github.com/simpletibr/simplicio/issues)
- **संबंधित:** Simplicio Video (hypit)। इसे क्लोन करने के लिए: `git clone https://github.com/hypit-ai/hypit.git simplicio-video`

<p align="center">
  <sub>© 2026 SimpleTI. Simplicio एक पंजीकृत मालिकाना सॉफ़्टवेयर है। सर्वाधिकार सुरक्षित।</sub>
</p>
