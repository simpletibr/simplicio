<div align="center">

<img src="../assets/simplicio-icon-192.png" alt="לוגו Simplicio" width="96" height="96">

<h1>Simplicio</h1>

<p><b>UltraFast Mode for all.</b></p>

<p><b>אותו סוכן, אותו מודל, אותה משימה: <span dir="ltr">121&nbsp;s&nbsp;→&nbsp;25&nbsp;s</span>, ו-<span dir="ltr">$0.0226&nbsp;→&nbsp;$0.0076</span>.</b></p>

<p>בלי Simplicio ← עם Simplicio 3.15.0. חציון של 3 הרצות של משימת קוד קטנה אחת ב-Claude Code עם Claude Haiku 5.5.</p>

<p>Simplicio פועל על המחשב שלכם ומוסיף כלים לסוכן הקוד שאתם כבר משתמשים בו.</p>

<p>
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=2fe6a0&label=release" alt="השחרור האחרון"></a>
  <a href="https://simpleti.com.br/simplicio/docs"><img src="https://img.shields.io/badge/docs-simpleti.com.br-ffd23f" alt="תיעוד"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="כוכבים"></a>
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="רישיון: קנייני">
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
  <a href="README.hi-IN.md">हिन्दी</a> ·
  <a href="README.ar-SA.md">العربية</a>&lrm; ·
  עברית&lrm; ·
  <a href="README.id-ID.md">Bahasa Indonesia</a> ·
  <a href="README.ms-MY.md">Bahasa Melayu</a>
</p>

<p align="center"><sub>קובץ זה הוא תרגום של <a href="../README.md">README באנגלית</a>. אם יש הבדל, העמוד באנגלית הוא המקור. הנתונים והתרשימים מופיעים באנגלית.</sub></p>

</div>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-dark.svg">
    <img src="../assets/benchmark-2026-11-22-light.svg" width="840" alt="תרשים עמודות שמשווה בין בלי Simplicio, Simplicio 3.14.0 ו-Simplicio 3.15.0 בשלושה מדדים, חציון של שלושה סשנים לכל הגדרה. זמן המשימה כולה: 121 s בלי Simplicio, 104 s עם Simplicio 3.14.0 ו-25 s עם Simplicio 3.15.0. עלות: $0.0226, $0.0220 ו-$0.0076. טוקני פלט: 18,162, 19,722 ו-3,211.">
  </picture>
</p>

<p align="center">
  <sub>חציון של 3 סשנים לכל הגדרה (בלי Simplicio, Simplicio 3.14.0 ו-Simplicio 3.15.0). Claude Haiku 5.5 ב-Claude Code 2.1.330, 2026-11-22. בכל הגדרה הושלמו 9 מתוך 9 שלבים. הקו הדק על כל עמודה עובר מהסשן הנמוך ביותר לסשן הגבוה ביותר.<br>
  <a href="../benchmarks/2026-11-22-standard-benchmark.md">שיטה, נתונים ומגבלות</a></sub>
</p>

<p align="center">
  <sub>קראו את זה יחד עם התוצאות: משימה קטנה אחת, שלושה סשנים לכל הגדרה, מודל אחד. הבדיקות החיצוניות מצומצמות יותר מההנחיות. שיא הזיכרון היה גבוה יותר: 375 MB לעומת 270 MB. הבניות של Simplicio הורכבו מה-commits של השחרורים, עם הכניסה כבויה.</sub>
</p>

<p align="center">הדרך שבה Simplicio מגיע לתוצאה הזאת אינה מפורסמת. המדידות מפורסמות, כולל אלה שבהן הוא מפסיד.</p>

<p align="center">
  <b>נסו:</b> <a href="#install">התקנה</a> · <a href="#first-run">הרצה ראשונה</a><br>
  <a href="#what-simplicio-is">מה זה</a> ·
  <a href="#the-measurement">מדידה</a> ·
  <a href="#works-with-the-agent-you-already-use">סוכנים</a> ·
  <a href="#command-line">פקודות</a> ·
  <a href="#safety-and-privacy">פרטיות</a> ·
  <a href="#questions-people-ask">שאלות</a> ·
  <a href="#documentation-and-community">תיעוד</a>
</p>

<a id="what-simplicio-is"></a>

## מהו Simplicio

Simplicio הוא כלי מקומי שנותן לסוכן הקוד שאתם כבר משתמשים בו מצב מהיר במיוחד, בכל סוכן ובכל מודל. המספרים בעמוד הזה מגיעים מסוכן אחד ומודל אחד; הסעיף שלמטה מפרט בדיוק מה נמדד.

- **אתם שומרים על הסוכן ועל המודל.** Simplicio לא מחליף את Claude Code, Codex, Cursor או כל מודל שעומד מאחוריהם.
- **בינארי native אחד וחתום** רושם את עצמו בסוכנים שלכם ופועל על המחשב שלכם כשרת MCP מקומי מסוג STDIO.
- **מה שמשתנה הוא הסשן.** הזמן שלו ועלותו.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/diagram-where-simplicio-runs-dark.svg">
    <img src="../assets/diagram-where-simplicio-runs-light.svg" width="840" alt="תרשים. במחשב שלכם: אתם, סוכן הקוד שלכם, Simplicio והמאגר שלכם. הסוכן מדבר עם Simplicio דרך STDIO מקומי (MCP). הסוכן מדבר עם ספק המודל שלכם כמו קודם. Simplicio מדבר עם SimpleTI לבדיקות כניסה ומסלול, ועם GitHub לבדיקת שחרור, בלי תוכן מאגר באף אחד מהם.">
  </picture>
</p>

<p align="center">
  <sub>הזרימה כברירת מחדל. <a href="#safety-and-privacy">הרשימה המלאה</a> כוללת את השירותים האחרים.</sub>
</p>

<details>
<summary>MCP ו-STDIO</summary>

MCP הוא Model Context Protocol, הדרך שבה סוכן קוד קורא לכלים חיצוניים. STDIO פירושו שהסוכן מפעיל את התוכנה בעצמו ומדבר איתה דרך הקלט והפלט הסטנדרטיים שלה.

הוא נותן לסוכן שלכם כלים: מפת מאגר, הקשר מצומצם, עריכות מובנות ובדיקות. [כלי הליבה](#works-with-the-agent-you-already-use) מופיעים בהמשך.

מתקינים בינארי native אחד וחתום. המתקין מאמת את החתימה, ואז רושם את Simplicio בסוכנים שהוא מוצא במחשב שלכם.

</details>

<a id="the-measurement"></a>

## המדידה

משימה אחת, שמורצת באותו אופן עם Simplicio ובלי: שלושה שלבים בסשן אחד של הסוכן, וכל תוצאה נבדקת בבדיקה חיצונית.

1. בניית רשימת משתמשים: API ועמוד עם טבלה, חיפוש ומיון.
2. שינוי: הסרת עמודה, הוספת סינון לפי תפקיד ועמודת תאריך.
3. הוספת הרשמה: נקודת קצה מסוג `POST` שבודקת את הקלט שלה, ועמוד טופס.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-sessions-dark.svg">
    <img src="../assets/benchmark-2026-11-22-sessions-light.svg" width="840" alt="תרשים פיזור של כל סשן, עם זמן המשימה כולה לרוחב והעלות שהסוכן מדווח כלפי מעלה. Simplicio 3.15.0, יהלומים ירוקים: 23 עד 27 s ו-$0.0071 עד $0.0098. Simplicio 3.14.0, ריבועים אפורים: 90 עד 106 s ו-$0.0214 עד $0.0249. בלי Simplicio, עיגולים חלולים: 97 עד 172 s ו-$0.0186 עד $0.0280.">
  </picture>
</p>

| מדד | בלי Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| זמן המשימה | 121 s<br><sub>97–172</sub> | 104 s<br><sub>90–106</sub> | **25 s**<br><sub>23–27</sub> |
| עלות מדווחת | $0.0226<br><sub>0.0186–0.0280</sub> | $0.0220<br><sub>0.0214–0.0249</sub> | **$0.0076**<br><sub>0.0071–0.0098</sub> |
| בקשות למודל | 25<br><sub>19–33</sub> | 18<br><sub>18–22</sub> | **10**<br><sub>10–10</sub> |
| קריאות לכלים | 22<br><sub>16–30</sub> | 15<br><sub>15–19</sub> | **7**<br><sub>7–7</sub> |
| טוקני פלט | 18,162<br><sub>15,599–23,328</sub> | 19,722<br><sub>18,764–24,997</sub> | **3,211**<br><sub>3,068–3,573</sub> |
| טוקני קלט | 34,691<br><sub>30,447–42,543</sub> | 34,141<br><sub>33,121–40,017</sub> | 18,755<br><sub>18,466–33,300</sub> |
| זמן CPU | 8.5 s<br><sub>8.5–9.2</sub> | 10.0 s<br><sub>8.9–10.0</sub> | **5.3 s**<br><sub>5.3–5.5</sub> |
| שיא הזיכרון | **270 MB**<br><sub>248–274</sub> | 436 MB<br><sub>432–439</sub> | 375 MB<br><sub>365–379</sub> |
| שלבים שהושלמו | 9 מתוך 9 | 9 מתוך 9 | 9 מתוך 9 |

חציון של 3 סשנים. מתחת לכל ערך מופיע הטווח, מהנמוך לגבוה. מודגש מסמן את הערך הטוב ביותר בשורה שבה הטווחים אינם חופפים. "9 מתוך 9" פירושו 3 שלבים בכל אחד מ-3 הסשנים, וכל אחד מהם עבר כל בדיקה חיצונית.

בקשות וקריאות לכלים לכל סשן.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-work-dark.svg">
    <img src="../assets/benchmark-2026-11-22-work-light.svg" width="840" alt="תרשים יחידות עם סימון אחד לכל בקשה למודל או קריאה לכלי, חציון של 3 סשנים. בקשות למודל: 25 בלי Simplicio, 18 עם Simplicio 3.14.0 ו-10 עם Simplicio 3.15.0. קריאות לכלים: 22, 15 ו-7.">
  </picture>
</p>

זמן לפי שלב, על סקאלה משותפת אחת.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-steps-dark.svg">
    <img src="../assets/benchmark-2026-11-22-steps-light.svg" width="840" alt="חציון זמן לפי שלב, על סקאלה משותפת אחת. שלב 1, בנייה: 57.3 s בלי Simplicio, 53.7 s עם Simplicio 3.14.0 ו-5.8 s עם Simplicio 3.15.0. שלב 2, שינוי: 17.3 s, 15.2 s ו-8.9 s. שלב 3, הרשמה: 31.4 s, 27.5 s ו-10.3 s.">
  </picture>
</p>

<details>
<summary>המספרים המדויקים לפי שלב</summary>

כל תא הוא החציון של זמן השלב והחציון של עלות השלב:

| שלב | בלי Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. בנייה | 57.3 s / $0.0111 | 53.7 s / $0.0137 | 5.8 s / $0.0022 |
| 2. שינוי | 17.3 s / $0.0040 | 15.2 s / $0.0032 | 8.9 s / $0.0023 |
| 3. הרשמה | 31.4 s / $0.0075 | 27.5 s / $0.0056 | 10.3 s / $0.0026 |

</details>

**איך לקרוא את זה.** המשימה כולה רצה פי 4.9 מהר ועלתה בערך שליש מהעלות. אפילו הסשן המהיר ביותר בלי Simplicio (97.1 s) היה איטי פי 3.7 מהסשן האיטי ביותר עם 3.15.0 (26.6 s). [שיטה, מגבלות](../benchmarks/2026-11-22-standard-benchmark.md#limits)

<details>
<summary>איך מוגדר כל מספר</summary>

- היחסים מחושבים מהחציונים הלא מעוגלים. לעומת השחרור הקודם, המשימה כולה רצה פי 4.2 מהר.
- כל חציון מחושב בנפרד, ולכן השלבים לא מסתכמים לחציון של המשימה כולה.
- המקרה הגרוע ביותר: הסשן המהיר ביותר בלי Simplicio (97.1 s) היה עדיין איטי פי 3.7 מהסשן האיטי ביותר עם Simplicio 3.15.0 (26.6 s), והסשן הזול ביותר בלי Simplicio ($0.0186) עלה עדיין פי 1.9 מהסשן היקר ביותר עם Simplicio ($0.0098).
- בסיס ההשוואה הוא Claude Code 2.1.330 עם הכלים שלו, בלי שרת MCP ובלי תצורת Simplicio.
- כל שלב נבדק מבחוץ, לא מתוך הסשן: קוראים ל-API דרך HTTP, והעמודים נטענים ב-Chrome במצב headless, כלומר Chrome בלי חלון.
- הבדיקות לא בודקות את תיבת החיפוש, את המיון, את ההפניה אחרי השמירה, את המראה של העמוד או את איכות הקוד.
- בקשה למודל היא קריאה אחת למודל; קריאה לכלי היא שימוש אחד בכלי על ידי הסוכן.
- העלות המדווחת היא הטוקנים שנוצלו כפול המחיר המפורסם של המודל. היא כוללת רק טוקני מודל. זו לא חשבונית.
- טווחי טוקני הקלט חופפים, ולכן ההרצה הזאת לא טוענת להבדל בטוקני קלט.
- ארבעה סשנים רצו בבת אחת על מחשב אחד: השוו זמנים רק בתוך הסבב הזה.

</details>

<a id="where-simplicio-does-not-win"></a>

### היכן Simplicio לא מנצח

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-memory-dark.svg">
    <img src="../assets/benchmark-2026-11-22-memory-light.svg" width="840" alt="שיא הזיכרון, חציון של 3 סשנים: 270 MB בלי Simplicio, הנמוך ביותר; 436 MB עם Simplicio 3.14.0, גבוה ב-61%; 375 MB עם Simplicio 3.15.0, גבוה ב-39%.">
  </picture>
</p>

- **זיכרון.** שיא הזיכרון היה גבוה ב-39%: 375 MB לעומת 270 MB.
- **השחרור הקודם לא הראה שיפור במשימה הזאת.** Simplicio 3.14.0 עלה בדיוק כמו בלי Simplicio.
- **סקריפט Python קצר וחד-פעמי.** Simplicio 3.10.8 היה איטי יותר (19.6 s לעומת 11.4 s) ולא נמדד שוב.
- **עמוד קטן אחד, מודלים חזקים.** Simplicio 3.15.0 היה איטי יותר ב-14% עד 47%.
- **מה שאתם מתקינים אינו בדיוק מה שנמדד.** הבניות הורכבו מה-commits של השחרורים, עם הכניסה כבויה.
- **המדגם קטן.** שלושה סשנים לכל הגדרה, מודל אחד, פרויקט אחד.

<details>
<summary>המגבלות המלאות</summary>

- **זיכרון.** שיא הזיכרון היה גבוה ב-39% מאשר עם הסוכן הרגיל: 375 MB לעומת 270 MB.
- **השחרור הקודם לא הראה שיפור במשימה הזאת.** Simplicio 3.14.0 עלה בדיוק כמו בלי Simplicio, והפער שלו בזמן נמצא בתוך הפיזור שבין הרצה להרצה. השיפור הגיע עם 3.15.0.
- **סקריפט Python קצר וחד-פעמי.** בסבב קודם, Simplicio 3.10.8 היה איטי מהסוכן הרגיל עם כל מודל שנוסה: ב-Claude Sonnet 5.5 ב-Claude Code, 19.6 s ו-$0.0548 לעומת 11.4 s ו-$0.0283. לא נמדד שוב ב-3.15.0.
- **עמוד קטן אחד, מודלים חזקים.** עם Sonnet 5.5 או Opus 5.5, Simplicio 3.15.0 לקח 14% עד 47% יותר זמן ועלה 14% עד 41% יותר ב-6 מתוך 6 מקרים. כל עמוד היה תקין בשני המקרים. Sonnet 5.5, יצירה, חציון של 3: 24 s ו-$0.082 לעומת 20 s ו-$0.066. תיקון נמצא בעבודה; הוא עוד לא בשחרור.
- **מה שאתם מתקינים אינו בדיוק מה שנמדד.** הבניות הורכבו מה-commits של השחרורים, עם הכניסה ותהליך הרקע כבויים. ההורדות החתומות לא נמדדו.
- **המדגם קטן.** שלושה סשנים לכל הגדרה, מודל אחד, פרויקט קטן וחדש אחד, מחשב אחד וארבעה סשנים בבת אחת; אף סשן לא נפסל ולא הורץ מחדש. היחסים מודדים את המשימה הזאת, לא את המשימה שלכם, ואנחנו לא מדדנו כמה מהעבודה שלכם דומה לה.

</details>

### בדקו בעצמכם

[הדוח](../benchmarks/2026-11-22-standard-benchmark.md) מפרסם את שלוש ההנחיות (בפורטוגזית, עם תרגום), כל בדיקה חיצונית וכל סשן; [קובץ הנתונים](../benchmarks/2026-11-22-standard-benchmark.json) מכיל אותם בפורמט JSON. סביבת הבדיקה עצמה לא מפורסמת.

<a id="install"></a>

## התקנה

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

ב-Windows, השתמשו ב-`py -m pip install --upgrade simplicio-installer` ואז ב-`simplicio install`.

המתקין מאמת את השחרור החתום ורושם אוטומטית את Simplicio בסוכנים שהוא מוצא. אחר כך היכנסו עם `simplicio auth login`.

<details>
<summary>פרטי ההתקנה</summary>

- הוא מוריד את השחרור החתום האחרון לפלטפורמה שלכם, ובודק את ה-SHA-256 ואת חתימת ה-Ed25519 שלו לפני שהוא מחליף את הבינארי המותקן.
- הבינארי נשמר תחת `~/.simplicio/bin/` (ב-Windows, `%USERPROFILE%\.simplicio\bin\`). Simplicio נרשם אוטומטית בסוכנים שהוא מוצא. כשל ברישום עוצר את המתקין, במקום לדווח על הצלחה.
- הפעילו מחדש כל סוכן שכבר פתוח, כדי שייטען מחדש את התצורה שלו. אם תיקיית הסקריפטים של Python אינה ב-`PATH` שלכם, הוסיפו אותה קודם.

**כניסה.** נדרשת כניסה עם Google, גם במהלך הבטא. הריצו `simplicio auth login`, ואז `simplicio auth status --json`, והמשיכו כשהוא מדווח `active: true`. רישום עובד גם לפני הכניסה. לעולם אל תדביקו סיסמה או טוקן לתוך התצורה של סוכן.

כדי לוודא ש-Simplicio נטען, חפשו את `simplicio` ברשימת שרתי ה-MCP של הסוכן. ב-Claude Code, `/mcp` מציג את השרתים המחוברים. מעדיפים לקרוא את המתקין קודם? הוא [install.sh](../install.sh).

לעדכון, הריצו שוב את אחד המתקינים בכל זמן: הוא מאתר את השחרור האחרון. `install.sh` ו-`install.ps1` נמצאים בשורש המאגר הזה.

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

- `--doctor` בודק את ההתקנה.
- `--uninstall --keep-data` מסיר את הבינארי המותקן ושומר על הנתונים שלכם. זה כולל את מצב הכניסה ל-Google לתקופה של 30 ימים ב-`~/.simplicio/login.json`.
- `--uninstall --purge` מסיר רק את המצב ש-Simplicio מנהל, כולל מצב הכניסה. הוא משאיר את `~/.simplicio/.env`, שבו עשויים להימצא פרטי ההתחברות של הספקים. ניקוי מלא דורש `SIMPLICIO_CONFIRM_PURGE=1`.
- ההסרה לא משנה את התצורה של הסוכנים שלכם. הרשומות של Simplicio נשארות בכל סוכן עד שתסירו אותן בהגדרות של אותו סוכן.
- נתונים בתוך תיקיית `.simplicio` של הפרויקט לא מוסרים על ידי `--keep-data`. בדקו את היעד לפני שבוחרים ב-`--purge`.

פרטים מלאים: [INSTALL.md](../INSTALL.md).

</details>

<a id="first-run"></a>

## הרצה ראשונה

```bash
simplicio version
cd my-project
simplicio onboard
```

`simplicio version` בודק את ההתקנה; `simplicio onboard` מכין את הפרויקט. אחר כך פתחו שם את הסוכן.

<a id="works-with-the-agent-you-already-use"></a>

## עובד עם הסוכן שאתם כבר משתמשים בו

המתקין מעביר את הרישום לרשם המובנה של Simplicio. הוא כותב את הרשומה של Simplicio לסוכנים שהוא יודע להגדיר, ביניהם Claude Code, Codex, Cursor, Visual Studio Code, OpenCode, Gemini CLI ו-Kiro.

המרשם [`plugins/simplicio/host-surfaces.json`](../plugins/simplicio/host-surfaces.json) מציין 43 מזהי סוכנים, והמטריצה [`docs/hosts/compatibility-matrix.md`](../docs/hosts/compatibility-matrix.md) מסמנת 12 כנתמכים ו-29 כ-`unverified`. התייחסו לאינטגרציה `unverified` כאל אינטגרציה שלא נבדקה.

<details>
<summary>כל 43 הסוכנים</summary>

- המרשם מציין 43 מזהי סוכנים, ואת הדרך שבה Simplicio מגיע לכל אחד: רשומת MCP ש-Simplicio כותב (23), plugin או הרחבה מקורית (5), חבילת plugin נייד (4), הגדרה מודרכת שאתם עוקבים אחריה בעצמכם (9), או כלי שורת פקודה אחר (2).
- למטריצה אין שורה עבור Codex ו-Gemini CLI. גם במקום שבו המרשם אומר ש-Simplicio כותב את הרשומה, התייחסו לאינטגרציה `unverified` כאל אינטגרציה שלא נבדקה.
- ל-23 סוכנים יש מדריך ב-[`docs/hosts/`](../docs/hosts/). לסוכנים שמגיעים דרך plugin, ה-plugin מיושם בשלב נפרד שמבקש את הסכמתכם, וב-[INSTALL.md](../INSTALL.md) מתואר השלב הזה.

| הדרך שבה Simplicio מגיע אליו | מספר | סוכנים |
|---|---|---|
| רשומת MCP ש-Simplicio כותב | 23 | **xAI Grok Build**, MiMo Code, Amp, OpenClaude, Antigravity, **Pi**, **oh-my-pi**, Goose, Auggie, Autohand Code, Charm, Cline, Command Code, Continue, Droid, Kilocode, Kimi, Mistral Vibe, Rovo Dev, **Visual Studio Code**, **Meta Muse Code**, **OpenMausBot**, **OpenMuse (Python)** |
| plugin או הרחבה מקורית | 5 | **Claude Code**, Codex, **OpenCode**, Hermes Agent, Gemini CLI |
| חבילת plugin נייד | 4 | **Cursor**, GitHub Copilot, **Kiro**, Qwen Code |
| הגדרה מודרכת שאתם עוקבים אחריה בעצמכם | 9 | Devin, Codebuff, CopilotKit OpenDots, CopilotKit OpenBot, agentes.chat, OpenAI dots, xAI Grok Bot, Meta Muse app, Cue by Manus |
| כלי שורת פקודה אחר | 2 | **OrcaDev / Orca ADE**, T3 Code |

מודגש: מטריצת התאימות מסמנת את הסוכן כנתמך.

</details>

אלה כלי הליבה שהסוכן שלכם מקבל:

| כלי | מה הוא נותן לכם |
|---|---|
| `simplicio_map` | מפה תמציתית של המאגר, כדי שהסוכן ימצא את דרכו |
| `simplicio_context` | ההקשר שמשימה צריכה, מצומצם, במקום קבצים שלמים |
| `simplicio_edit` | עריכות קבצים מובנות מתוך תוכנית מוכנה מראש |
| `simplicio_validate` | בדיקות של צינור העבודה, הבדיקות והמסירה |
| `simplicio_run` | הרצת משימה תחת השליטה של Simplicio |

[MCP-CONNECT.md](../MCP-CONNECT.md) מתאר את כלי הליבה.

<details>
<summary>הגדרה ידנית</summary>

Simplicio הוא שרת MCP מקומי מסוג STDIO, ולכן אפשר להפנות אליו כל סוכן שיכול להפעיל שרת MCP מקומי. כדי לחזור על הרישום, הריצו `simplicio mcp register`. פקודת השרת היא `simplicio serve --mcp --stdio`.

אם הסוכן שלכם לא הוגדר בשבילכם, הוסיפו את הרשומה הזאת לתצורת ה-MCP שלו. החליפו את הנתיב בנתיב המוחלט של הבינארי המותקן.

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

Codex קורא TOML. סוכנים מפעילים את `command` ישירות, ולכן אל תשתמשו ב-`~` ואל תסתמכו על הרחבה של ה-shell. בנתיבי Windows השתמשו בלוכסן רגיל (/), והחליפו את שם המשתמש לדוגמה.

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

המקום שבו כל סוכן שומר את הקובץ שלו: [MCP-CONNECT.md](../MCP-CONNECT.md).

</details>

<a id="command-line"></a>

## שורת הפקודה

| פקודה | מה מקבלים |
|---|---|
| `simplicio map --repo . --for-llm markdown` | מפה מבנית תמציתית של המאגר, שנכתבה כדי שמודל יקרא אותה |
| `simplicio context --repo .` | ההקשר המצומצם של משימה |
| `simplicio memory query "query" --json` | מה שהפרויקט כבר יודע, שנשלף מהזיכרון המאונדקס שלו, בפורמט JSON |
| `simplicio edit --plan plan.json --repo .` | קבוצה מוכנה של עריכות מובנות, שמיושמת על הקבצים |
| `simplicio run "task" --repo . --agents N` | הרצת משימה עם N סוכנים תחת השליטה של Simplicio |
| `simplicio loop` | עבודה שממשיכה בסבבים עד שהיא מתכנסת |

השמות שתראו בהודעות של Simplicio: Mapper צופה, Fast מקרין או מאחזר, Dev CLI עורך, Runtime מנהל, ו-Loop מתכנס.

<a id="safety-and-privacy"></a>

## בטיחות ופרטיות

הסעיף הזה מתאר את הגרסה 3.15.0.

- **נשאר על המחשב שלכם.** מיפוי, הקשר, עריכות ובדיקות רצים בתוך הבינארי של Simplicio.
- **ל-SimpleTI (simpleti.com.br).** בדיקות כניסה ומסלול בלבד, בלי תוכן מאגר.
- **ל-GitHub.** בדיקת שחרור שאפשר לכבות.
- **בלי אנליטיקה.** Simplicio לא מעלה אנליטיקה, דוחות קריסה או נתוני שימוש.
- **לשירותים שאתם מגדירים.** הם מקבלים את מה שהתכונה שולחת, וזה יכול לכלול הנחיות וקוד.
- **שתי תכונות פונות לשירות פתוח לציבור באינטרנט בלי שום הגדרה.** חיפוש ברשת (DuckDuckGo) וביקורת התלויות (osv.dev); אף אחת מהן לא שולחת תוכן קבצים.
- **הורדות.** מ-GitHub; חלק מסקריפטי העזר מביאים גם כלים מ-PyPI או מ-npm.

<details>
<summary>הפרטים</summary>

- **נשאר על המחשב שלכם.** מיפוי, הקשר, עריכות ובדיקות רצים בתוך הבינארי של Simplicio. הוא מעביר את התוצאות לסוכן שלכם באותו מחשב. רשומות השימוש והחיסכון הן קבצים מקומיים. מה שהסוכן שולח לספק המודל שלו נקבע על ידי הסוכן, כמו קודם.
- **ל-SimpleTI (simpleti.com.br).** בדיקות כניסה ומסלול בלבד, בלי תוכן מאגר: בלי קבצים, נתיבי קבצים, הנחיות או עריכות.
  - הן נושאות את טוקן הכניסה שלכם, את גרסת Simplicio ואת שם המארח של המחשב שלכם. בדיקת רישיון אופציונלית נושאת גם את כתובת האימייל של החשבון שלכם.
  - הן מחזירות את כתובת האימייל, השם והמסלול של החשבון שלכם.
- **ל-GitHub.** בדיקת רקע לשחרור חדש, לכל היותר בערך פעם ב-12 שעות, שלא נושאת דבר עליכם או על הקוד שלכם. כדי לכבות אותה, הגדירו `SIMPLICIO_DISABLE_AUTO_UPDATE=1`. עדכון מוריד את הבינארי מ-GitHub, ובודק את ה-SHA-256 ואת החתימה שלו לפני שהוא מחליף את הישן.
- **בלי אנליטיקה.** Simplicio 3.15.0 והקבצים שהוא מתקין לתוך הסוכנים שלכם נבדקו לכך: אף אחד מהם לא מעלה אנליטיקה, דוחות קריסה או נתוני שימוש. ה-hooks שהוא מתקין מריצים תוכניות מקומיות בלבד (הבינארי של Simplicio, ובתוספים אופציונליים, סקריפטים מקומיים); אף אחד מהם לא פונה לרשת.
- **לשירותים שאתם מגדירים.** ספק מודל, GitHub, Jira, מודיע צ'אט או מטמון צוות מקבלים את מה שהתכונה הזאת שולחת, וזה יכול לכלול הנחיות וקוד. בקשות לספק מודל נושאות כותרת (header) ששמה את Simplicio כלקוח.
- **שתי תכונות פונות לשירות פתוח לציבור באינטרנט בלי שום הגדרה.** אף אחת מהן לא שולחת תוכן קבצים.
  - חיפוש ברשת, כשהוא רץ, שולח את שאילתת החיפוש ל-DuckDuckGo, אלא אם הגדרתם שירות חיפוש אחר. בצ'אט של Simplicio עצמו, הודעה שנראית כמו שאלה על הרשת יכולה להפוך לשאילתה הזאת.
  - ביקורת האבטחה של התלויות, כשמריצים אותה, שולחת את השמות והגרסאות של התלויות שלכם ל-osv.dev.
- **הורדות.** המתקין ומסלול העדכון מורידים מ-GitHub. חלק מסקריפטי העזר האופציונליים מביאים את הכלים שלהם מ-PyPI או מ-npm כשמריצים אותם. plugin של סוכן שלא מוצא בינארי של Simplicio מוריד את המתקין הרשמי מ-GitHub, נעוץ ל-commit מסוים ונבדק לפי SHA-256.

**שחרורים חתומים.** כל שחרור מפרסם את הבינאריים שלו עם סכומי בדיקה SHA-256, חתימות Ed25519, SBOM (רשימה של מה שנמצא בבנייה) ו-build provenance.

המתקינים ומסלול העדכון בודקים את סכום הבדיקה ואת החתימה לפני שהם מחליפים את הבינארי המותקן. לשחרורים יציבים, חתימה חסרה או לא תקפה וכן אי-התאמה בסכום הבדיקה הם כשלים קשיחים; החוזה נמצא ב-[docs/UPDATE_SIGNATURE_CONTRACT.md](../docs/UPDATE_SIGNATURE_CONTRACT.md).

**מה המתקין משנה בסוכן שלכם.**

- הוא מוסיף רשומה של Simplicio לתצורת ה-MCP של הסוכן, ושומר על שאר התצורה.
- ב-Claude Code הוא מאפשר גם את `mcp__simplicio__*`, כך שכלי של Simplicio לא ייחסם במצב auto.
- בסוכנים שממשק ה-hooks שלהם המתקין אימת, הוא מתקין שם גם את ה-hooks של Simplicio.
- ההסרה לא מבטלת את הרשומות האלה; סעיף ההתקנה מסביר איך מסירים אותן. [INSTALL.md](../INSTALL.md) מתאר מה המתקין כותב, והמדריך של כל סוכן ב-[`docs/hosts/`](../docs/hosts/) נותן את הפירוט.

</details>

## עוד במאגר הזה

<details>
<summary>אפליקציית Desktop (תצוגה מקדימה ל-macOS)</summary>

תצוגה מקדימה של Desktop ל-macOS (Apple Silicon) מפורסמת כ-[Simplicio-3.8.47-arm64.dmg](https://github.com/simpletibr/simplicio/releases/download/v3.8.47/Simplicio-3.8.47-arm64.dmg). ה-SHA-256 שלה נמצא ב-[DESKTOP-SHA256SUMS](../DESKTOP-SHA256SUMS), בנפרד מסכומי הבדיקה של הבינאריים של Simplicio. ל-DMG אין קובץ חתימה, והוא כולל את הבינארי Simplicio 3.8.47.

- Windows Desktop לא מפורסם. ב-Windows, השתמשו בהתקנה משורת הפקודה שלמעלה.
- חתימה עם Apple Developer ID ו-notarization לא בוצעו. החבילה חתומה ad-hoc, כלומר בלי תעודת מפתח של Apple, ואין טענה לאישור של Gatekeeper, ולכן macOS עלול להזהיר אתכם כשתפתחו אותה.
- ההתקנה משורת הפקודה שלמעלה היא נתיב ההתקנה הציבורי הנתמך, עד שתפורסם חבילת Desktop חתומה.

פרטים: [docs/desktop/RELEASE.md](../docs/desktop/RELEASE.md).

</details>

<details>
<summary>למתחזקים: תרשים הזרימה שנוצר אוטומטית</summary>

- הפקודות והכלים המתועדים ב-README.md וב-MCP-CONNECT.md מצוירים כזרימה אחת, [docs/flow/simplicio.svg](../docs/flow/simplicio.svg), שנוצרת מקובץ מקור אחד, `docs/flow/simplicio.flow.json`.
- ליצירה מחדש הריצו `python3 scripts/generate_flow.py`, ולבדיקת סטייה הריצו `python3 scripts/generate_flow.py --check`.
- החוזה ששומר על התאמה שלה לעמוד הזה ול-MCP-CONNECT.md הוא `python3 -m pytest tests/test_flow_contract.py -q`.
- בדיקת הייבוא ל-Langflow היא `scripts/verify_flow_langflow.py`, שנכשלת במצב fail closed (exit 2, `status=blocked`) כשאין שרת פועל. הראיות נמצאות תחת `docs/flow/evidence/` ו-`docs/flow/render/`; [docs/flow/README.md](../docs/flow/README.md) מכיל את הדרישות ואת הדרך לחזור על הבדיקה.

</details>

<a id="questions-people-ask"></a>

## שאלות שאנשים שואלים

**האם ההשוואה הוגנת?**<br>
אותו סוכן, מודל, הנחיות, פרויקט ובדיקות חיצוניות; לבסיס ההשוואה אין Simplicio. ראו [היכן Simplicio לא מנצח](#where-simplicio-does-not-win).

**האם אני צריך לשנות את הסוכן או את המודל?**<br>
לא. Simplicio מתחבר לסוכן שאתם כבר משתמשים בו.

**האם אקבל תמיד את המספרים האלה?**<br>
לא. הם מודדים משימה אחת, מודל אחד ומחשב אחד.

**האם זה קוד פתוח?**<br>
לא. Simplicio הוא קנייני: בינארי חתום. המאגר הזה מכיל את המתקינים, החבילות, התיעוד והנתונים.

**איך מסירים את Simplicio?**<br>
הריצו `sh install.sh --uninstall --keep-data`, או `pwsh install.ps1 -Uninstall -KeepData` ב-Windows. הפקודה לא משנה את התצורה של הסוכנים שלכם, ולכן הסירו את הרשומות של Simplicio בהגדרות של כל סוכן.

**האם אני צריך חשבון?**<br>
כן. נדרשת כניסה עם Google, גם במהלך הבטא. הריצו `simplicio auth login`.

**האם הקוד שלי יוצא מהמחשב?**<br>
מיפוי, הקשר, עריכות ובדיקות רצים על המחשב שלכם; ל-SimpleTI ול-GitHub לא נשלח תוכן מאגר. [פרטים](#safety-and-privacy).

<a id="documentation-and-community"></a>

## תיעוד וקהילה

- **אתר:** [simpleti.com.br/simplicio](https://simpleti.com.br/simplicio/)
- **תיעוד:** [simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)
- **Discord:** [הצטרפו לקהילה](https://discord.gg/wM6tr7xVb)
- **בעיות:** [מעקב הבעיות של GitHub](https://github.com/simpletibr/simplicio/issues)
- **קשור:** Simplicio Video (hypit): `git clone https://github.com/hypit-ai/hypit.git simplicio-video`

<p align="center">
  <sub>© 2026 SimpleTI. Simplicio מוגן כתוכנה קניינית רשומה. כל הזכויות שמורות.</sub>
</p>
