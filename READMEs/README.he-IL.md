# 🔥 Simplicio

<p align="center">
  <img src="../assets/simplicio-hero.png" alt="Simplicio — סוכן קידוד בינה מלאכותית" width="920" />
</p>

<p align="center">
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=blue&label=latest" alt="גרסה אחרונה"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="כוכבים"></a>
  <a href="https://github.com/simpletibr/simplicio/releases"><img src="https://img.shields.io/github/downloads/simpletibr/simplicio/total?color=green" alt="הורדות"></a>
  <a href="../plugins/simplicio/LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="רישיון"></a>
</p>

<p align="center">
  <a href="#התקנה">התקנה</a> ·
  <a href="#מה-זה-עושה">מה זה עושה</a> ·
  <a href="#-benchmark-2026-10-31">Benchmark</a> ·
  <a href="https://simpleti.com.br/simplicio/#start">אתר אינטרנט</a>
</p>

<p align="center">
  <strong>🌍 שפות:</strong><br>
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

## ⚡ תקציר

**Simplicio** הוא סוכן קידוד בינה מלאכותית מבוסס טרמינל — בינארי יחיד שמחליף את
כל זרימת העבודה שלך בסיוע בינה מלאכותית: צ'אט, יצירת קוד, הקשר
מאגר, תכנון, תיאום רב-סוכנים מקומי (64 → 600 סוכנים), ומשלוח PR
מגובה בראיות.

**רץ על המחשב שלך. הקוד שלך לעולם לא עוזב את השליטה שלך. מודלים מרוחקים הם
אופציונליים, לא חובה.**

> כל אינטראקציה מראה בדיוק כמה טוקנים חסכת. בינארי יחיד ב-Rust, אפס תלויות.

## 🚀 התקנה

### התקנה דרך התוסף של Codex

אם אתם משתמשים ב-Codex, תוכלו להתקין את Simplicio כתוסף. הוסיפו את ה-Marketplace הציבורי, התקינו את התוסף והתחילו סשן Codex חדש; התוסף יתקין ויאותחל את Simplicio Runtime ויעמיד לרשותכם את ה-skills וכלי ה-MCP שלו.

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

### npm / npx (כל מערכת הפעלה)

```bash
npx simplicio install
```

### pip / PyPI (כל מערכת הפעלה)

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

### התקנה ישירה (ללא PyPI)

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

בוצע. פקודה אחת. ללא מנהל חבילות, ללא הגדרת מודל.

---

## 📊 Benchmark (2026-10-31)

מודל אמיתי יוצר קובץ ועורך אותו באותו סשן. התוצאה נבדקת מחוץ לסשן: דפים ב-Chrome ללא ממשק, וסקריפטים בהרצה. 60 סשנים, חציונים.

| משימה | תצורה | n | זמן | בקשות למודל | טוקני פלט | עלות | מסירה |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **דף מקובץ JSON, שמחולל מכסה** | **Simplicio 3.10.8** | 10 | **14.1 s** | **6** | **602** | **$0.0021** | **10/10** |
|  | Simplicio 3.9.2 | 10 | 166.2 s | 24.5 | 19,944 | $0.0215 | 10/10 |
|  | בלי MCP | 10 | 176.3 s | 32.5 | 17,929 | $0.0203 | 10/10 |
| **דף חדש, עם נתונים ושפה אחרים, שלא שימש לבניית המחולל** | **Simplicio 3.10.8** | 6 | **14.1 s** | **6** | **524** | **$0.0010** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 110.9 s | 17.5 | 16,091 | $0.0153 | 6/6 |
| **סקריפט Python, שאף מחולל לא מכסה** | **Simplicio 3.10.8** | 6 | **30.7 s** | **10.5** | **1,796** | **$0.0031** | **6/6** |
|  | Simplicio 3.9.2 | 6 | 34.1 s | 11.5 | 2,485 | $0.0051 | 6/6 |
|  | בלי MCP | 6 | 22.7 s | 8 | 1,268 | $0.0024 | 6/6 |

הרווח מגיע מהמחולל: במשימות הדפים `simplicio_map` מנתב את הבקשה ו-`simplicio_codegen` כותב את הקובץ ב-0 טוקני LLM. כשאף מחולל לא מכסה את המשימה, גרסה 3.10.8 עדיפה על 3.9.2, אך עולה כ-8 שניות ו-0.0007$ יותר לכל סשן לעומת עבודה בלי MCP.

> OpenCode 2.1.4 ו-DeepSeek V4.1 Flash על נקודת קצה קבועה אחת של OpenRouter, זהה בכל הרצה. העלות חושבה לפי 0.15$ לקלט, 0.60$ לפלט ו-0.003$ למטמון למיליון טוקנים. זה מודל אחד על שלוש משימות קטנות: משימות אחרות ייתנו מספרים אחרים. [פרומפטים, שיטה, מגבלות ונתונים לפי סשן](../benchmarks/2026-10-31-map-codegen.md).

אותן משימות במודלים אחרים, עם Simplicio ובלעדיו. כל מודל רץ בלקוח אחד, לכן השוו מודל רק לעצמו.

| מודל | משימה | Simplicio 3.10.8 | בלי MCP | מסירה |
|:---|:---|---:|---:|---:|
| **Claude Sonnet 5.5** (Claude Code) | דף מקובץ JSON, שמחולל מכסה | **17.5 s · $0.0672** | 33.4 s · $0.0927 | 10/10 |
|  | דף חדש, עם נתונים ושפה אחרים, שלא שימש לבניית המחולל | **16.3 s · $0.0514** | 22.5 s · $0.0610 | 10/10 |
|  | סקריפט Python, שאף מחולל לא מכסה | **19.6 s · $0.0548** | 11.4 s · $0.0283 | 10/10 |
| **Grok 4.7** (Grok Build) | דף מקובץ JSON, שמחולל מכסה | **31.0 s · $0.1690** | 359.7 s · $0.8590 | 6/6 |
|  | דף חדש, עם נתונים ושפה אחרים, שלא שימש לבניית המחולל | **36.0 s · $0.2059** | 387.5 s · $0.8518 | 6/6 |
|  | סקריפט Python, שאף מחולל לא מכסה | **82.0 s · $0.3315** | 63.1 s · $0.2452 | 6/6 |
| **Claude Haiku 5.5** (OpenCode) | דף מקובץ JSON, שמחולל מכסה | **13.7 s · $0.0046** | 29.3 s · $0.0083 | 10/10 |
|  | דף חדש, עם נתונים ושפה אחרים, שלא שימש לבניית המחולל | **13.8 s · $0.0023** | 28.7 s · $0.0057 | 10/10 |
|  | סקריפט Python, שאף מחולל לא מכסה | **19.2 s · $0.0033** | 16.6 s · $0.0030 | 10/10 |

[פרומפטים, שיטה, מגבלות ונתונים לפי סשן](../benchmarks/2026-11-01-multi-model.md).

---

## 🎯 מה זה עושה

| פקודה | תיאור |
|---|---|
| `simplicio map --repo .` | ממפה את המאגר עבור LLMs |
| `simplicio memory "שאילתה"` | שליפה עצבית (FTS + וקטורים) |
| `simplicio edit '{...}'` | עריכת קבצים דטרמיניסטית |
| `simplicio coding-loop "משימה"` | מתמשכת עד שהבדיקות עוברות |
| `simplicio deliver certify` | 5 שערי איכות לפני משלוח |
| `simplicio run "משימה" --agents N` | תיאום רב-סוכנים |
---

## 🏗️ ארכיטקטורה

```
LLM (Claude/Codex/Gemini)          Simplicio Runtime (Rust)
  |                                   |
  | 1. התמצאות                        | simplicio map
  | 2. שליפה                          | simplicio memory
  | 3. החלטה                          |
  | 4. עריכה  ───────────────────────> | simplicio edit (0 טוקנים)
  | 5. אימות <─────────────────────  | simplicio deliver certify
  | 6. חזרה                           | simplicio coding-loop
```

**ה-LLM חושב. Simplicio מבצע דטרמיניסטית.**

---

## ✨ תכונות

- 🏠 **מקומי תחילה** — llama.cpp מובנה, עובר למרוחק רק בעת הצורך
- 🪜 **סוכנים מדורגים** — 64 → 100 → 200 → 600 סוכנים מקומיים לפני ענן בתשלום
- 🔇 **שער חידוש שאנון** — מסנן פלטים כפולים (אפס טוקנים על כפילויות)
- 🔒 **קבלות חתומות** — sha256 לכל נספח, שרשרת ראיות חסינת חבלה
- 🛡️ **5 שערי משלוח** — קבלה, אימות, הרצה-אימות, רגרסיה, סקירה עצמית
- ⚡ **שער פעולה** — סיווג סיכונים + רשימה חסומה למוטציות ביוזמת צ'אט
- 🔌 **MCP/ACP** — פרוטוקול הקשר מודל + פרוטוקול לקוח סוכן
- 🌐 **שערים** — Telegram, Discord, Slack, WhatsApp
- 🧩 **מערכת מיומנויות** — טוען ומשרשר יכולות לשימוש חוזר
- 💾 **מסד זיכרון** — FTS מתמשך + שליפה וקטורית בין הפעלות
- 🔀 **נתב LLM** — ללא LLM → LLM מקומי → LLM מרוחק באופן אוטומטי
- 🖥️ **חוצה-פלטפורמות** — macOS, Linux, Windows, בינארי יחיד

---

## 🎁 גרסת בטא ציבורית חינם

**פקודות דטרמיניסטיות הן בחינם לנצח:**
`map`, `validate`, `edit`, `deliver`, `checkpoint`

**תכונות AI הן בחינם במהלך הבטא הציבורית ללא תאריך סיום.**
חיוב יוגדר בעדכונים עתידיים.

```bash
simplicio license status
```

---

## 📋 דרישות

| דרישה | מינימום | מומלץ |
|---|---|---|
| RAM | 8 GB | 16 GB+ |
| אחסון | 5 MB | 1.5 GB (עם LLM מקומי) |
| מערכת הפעלה | macOS 13+, Linux, Windows 10+ | macOS ARM64 |
| טרמינל | כל טרמינל מודרני | WezTerm / Alacritty / Ghostty |

---

## 🌐 אקוסיסטם

- [אתר אינטרנט](https://simpleti.com.br/simplicio/#start) — תיעוד מלא, מדדים, התקנה
- [Discord](https://discord.gg/wM6tr7xVb) — קהילה ותמיכה

---

## 📄 רישיון

קנייני. הבינארי חופשי להורדה ולשימוש. תכונות AI בחינם במהלך
הבטא הציבורית. ראה [LICENSE](../plugins/simplicio/LICENSE).

---

## ⭐ היסטוריית כוכבים

<a href="https://star-history.com/#simpletibr/simplicio&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" />
    <img alt="תרשים היסטוריית כוכבים" src="https://api.star-history.com/chart?repos=simpletibr/simplicio&type=date&legend=top-left" width="100%" />
  </picture>
</a>

---

## 💬 קהילה

- [Discord](https://discord.gg/wM6tr7xVb) — צ'אט, תמיכה, גישה מוקדמת
- [GitHub Issues](https://github.com/simpletibr/simplicio/issues) — באגים ובקשות תכונות

---

<p align="center">
  <strong>🔥 Simplicio 🔥</strong>
</p>
