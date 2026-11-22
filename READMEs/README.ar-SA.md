<div align="center">

<img src="../assets/simplicio-icon-192.png" alt="شعار Simplicio" width="96" height="96">

<h1>Simplicio</h1>

<p><b>UltraFast Mode for all.</b></p>

<p><b>نفس الوكيل، ونفس النموذج، ونفس المهمة: 121&nbsp;s&nbsp;←&nbsp;25&nbsp;s، و$0.0226&nbsp;←&nbsp;$0.0076.</b></p>

<p>بدون Simplicio ← مع Simplicio 3.15.0. وسيط 3 تشغيلات لمهمة برمجة صغيرة واحدة في Claude Code مع Claude Haiku 5.5.</p>

<p>يعمل Simplicio على جهازك، ويضيف أدوات إلى وكيل البرمجة الذي تستخدمه أصلًا.</p>

<p>
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=2fe6a0&label=release" alt="أحدث إصدار"></a>
  <a href="https://simpleti.com.br/simplicio/docs"><img src="https://img.shields.io/badge/docs-simpleti.com.br-ffd23f" alt="التوثيق"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="النجوم"></a>
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="الترخيص: خاص">
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
  العربية&lrm; ·
  <a href="README.he-IL.md">עברית</a>&lrm; ·
  <a href="README.id-ID.md">Bahasa Indonesia</a> ·
  <a href="README.ms-MY.md">Bahasa Melayu</a>
</p>

<p align="center"><sub>هذا الملف ترجمة لـ<a href="../README.md">ملف README الإنجليزي</a>. إذا اختلفت الصفحتان، فالمرجع هو الصفحة الإنجليزية. الأرقام والرسوم البيانية بالإنجليزية.</sub></p>

</div>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-dark.svg">
    <img src="../assets/benchmark-2026-11-22-light.svg" width="840" alt="مخطط أعمدة يقارن بين بدون Simplicio وSimplicio 3.14.0 وSimplicio 3.15.0 في ثلاثة مقاييس، وسيط ثلاث جلسات لكل منها. زمن المهمة كاملة: 121 s بدون Simplicio، و104 s مع Simplicio 3.14.0، و25 s مع Simplicio 3.15.0. التكلفة: $0.0226 و$0.0220 و$0.0076. رموز الإخراج: 18,162 و19,722 و3,211.">
  </picture>
</p>

<p align="center">
  <sub>وسيط 3 جلسات لكل إعداد (بدون Simplicio، وSimplicio 3.14.0، وSimplicio 3.15.0). Claude Haiku 5.5 في Claude Code 2.1.330، بتاريخ 2026-11-22. أنجز كل إعداد 9 من 9 خطوات. يمتد الخط الرفيع على كل عمود من أدنى جلسة إلى أعلاها.<br>
  <a href="../benchmarks/2026-11-22-standard-benchmark.md">المنهجية والبيانات والقيود</a></sub>
</p>

<p align="center">
  <sub>اقرأ النتائج مع هذه الملاحظات: مهمة صغيرة واحدة، وثلاث جلسات لكل إعداد، ونموذج واحد. الفحوصات الخارجية أضيق نطاقًا من التعليمات (prompts). كانت ذروة استهلاك الذاكرة أعلى: 375 MB مقابل 270 MB. بُنيت نسخ Simplicio من commits الإصدار، مع إيقاف تسجيل الدخول.</sub>
</p>

<p align="center">لا يُنشر كيف يحقق Simplicio هذه النتيجة. القياسات منشورة، بما فيها تلك التي يخسر فيها Simplicio.</p>

<p align="center">
  <b>جرّبه:</b> <a href="#install">التثبيت</a> · <a href="#first-run">أول تشغيل</a><br>
  <a href="#what-simplicio-is">ما هو</a> ·
  <a href="#the-measurement">القياس</a> ·
  <a href="#works-with-the-agent-you-already-use">الوكلاء</a> ·
  <a href="#command-line">الأوامر</a> ·
  <a href="#safety-and-privacy">الخصوصية</a> ·
  <a href="#questions-people-ask">الأسئلة</a> ·
  <a href="#documentation-and-community">التوثيق</a>
</p>

<a id="what-simplicio-is"></a>

## ما هو Simplicio

Simplicio برنامج محلي يمنح وكيل البرمجة الذي تستخدمه بالفعل وضعًا فائق السرعة، أيًّا كان الوكيل وأيًّا كان النموذج. الأرقام في هذه الصفحة مأخوذة من وكيل واحد ونموذج واحد؛ ويوضح القسم أدناه بدقة ما الذي جرى قياسه.

- **وكيلك ونموذجك يبقيان كما هما.** لا يستبدل Simplicio أيًّا من Claude Code وCodex وCursor، ولا النموذج الذي يعمل خلفها.
- **تثبيت ملف تنفيذي أصلي واحد وموقّع.** يتحقق المثبّت من التوقيع، ثم يسجّل Simplicio في الوكلاء التي يجدها على جهازك.
- **يعمل على جهازك.** يشغّله وكيلك كخادم MCP محلي يعمل عبر STDIO. وMCP هو Model Context Protocol، وهو الطريقة المعيارية التي يستدعي بها وكيل البرمجة الأدوات الخارجية. وSTDIO يعني أن الوكيل يشغّل البرنامج بنفسه، ويتواصل معه عبر مدخله ومخرجه القياسيين.
- **يمنح وكيلك أدوات.** خريطة للمستودع، وسياق محدود، وتعديلات منظّمة، وفحوصات. [الأدوات الأساسية](#works-with-the-agent-you-already-use) مدرجة أدناه.
- **ما يتغيّر هو الجلسة.** المدة التي تستغرقها وما تكلّفه. يُظهر القسم التالي مقدار ذلك، وأين لا يساعد.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/diagram-where-simplicio-runs-dark.svg">
    <img src="../assets/diagram-where-simplicio-runs-light.svg" width="840" alt="مخطط. على جهازك: أنت ووكيلك وSimplicio ومستودعك. يتواصل الوكيل مع Simplicio عبر STDIO المحلي (MCP). ويتواصل الوكيل مع مزوّد النموذج كما كان من قبل. ويتواصل Simplicio مع SimpleTI لفحوصات تسجيل الدخول والخطة، ومع GitHub لفحص الإصدار، ولا يحمل أيٌّ منهما محتوى المستودع.">
  </picture>
</p>

<p align="center">
  <sub>توضح الصورة ما يحدث افتراضيًا. القائمة الكاملة، بما فيها الميزات التي تصل إلى خدمات أخرى، موجودة في [ما الذي يرسله Simplicio، ولمن](#safety-and-privacy) ضمن السلامة والخصوصية.</sub>
</p>

<a id="the-measurement"></a>

## القياس

مهمة واحدة، تُنفَّذ بالطريقة نفسها مع Simplicio وبدونه. المهمة جلسة واحدة للوكيل، فيها ثلاث خطوات في المحادثة نفسها:

1. بناء قائمة للمستخدمين: واجهة API وصفحة فيها جدول وبحث وترتيب.
2. تعديلها: حذف عمود، وإضافة فلتر حسب الدور، وعمود للتاريخ.
3. إضافة تسجيل بسيط: نقطة نهاية `POST` تتحقق من مدخلاتها، وصفحة نموذج.

بعد كل خطوة تُفحص النتيجة من خارج الجلسة. تُستدعى واجهة API عبر HTTP، وتُحمَّل الصفحات في Chrome بلا واجهة، أي Chrome بلا نافذة. كان كل إعداد يستخدم الوكيل نفسه والنموذج نفسه: Claude Code 2.1.330 مع Claude Haiku 5.5. خط الأساس هو Claude Code 2.1.330 بأدواته الخاصة، من دون خادم MCP ومن دون أي إعدادات تخص Simplicio. لا تختبر الفحوصات مربع البحث، ولا الترتيب، ولا إعادة التوجيه بعد الحفظ، ولا شكل الصفحة، ولا جودة الكود.

تظهر كل جلسة في هذا الرسم، لا الوسيط وحده.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-sessions-dark.svg">
    <img src="../assets/benchmark-2026-11-22-sessions-light.svg" width="840" alt="مخطط نقطي لكل جلسة: زمن المهمة كاملة أفقيًا، والتكلفة كما يبلغها الوكيل رأسيًا. Simplicio 3.15.0، معيّنات خضراء: من 23 إلى 27 s، ومن $0.0071 إلى $0.0098. Simplicio 3.14.0، مربعات رمادية: من 90 إلى 106 s، ومن $0.0214 إلى $0.0249. بدون Simplicio، دوائر مفرغة: من 97 إلى 172 s، ومن $0.0186 إلى $0.0280.">
  </picture>
</p>

وسيط 3 جلسات لكل إعداد. الخط الصغير أسفل كل قيمة يمتد من أدنى جلسة إلى أعلاها.

| المقياس | بدون Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| زمن المهمة | 121 s<br><sub>97–172</sub> | 104 s<br><sub>90–106</sub> | **25 s**<br><sub>23–27</sub> |
| التكلفة المُبلَّغة | $0.0226<br><sub>0.0186–0.0280</sub> | $0.0220<br><sub>0.0214–0.0249</sub> | **$0.0076**<br><sub>0.0071–0.0098</sub> |
| طلبات النموذج | 25<br><sub>19–33</sub> | 18<br><sub>18–22</sub> | **10**<br><sub>10–10</sub> |
| استدعاءات الأدوات | 22<br><sub>16–30</sub> | 15<br><sub>15–19</sub> | **7**<br><sub>7–7</sub> |
| رموز الإخراج | 18,162<br><sub>15,599–23,328</sub> | 19,722<br><sub>18,764–24,997</sub> | **3,211**<br><sub>3,068–3,573</sub> |
| رموز الإدخال | 34,691<br><sub>30,447–42,543</sub> | 34,141<br><sub>33,121–40,017</sub> | 18,755<br><sub>18,466–33,300</sub> |
| زمن المعالج (CPU) | 8.5 s<br><sub>8.5–9.2</sub> | 10.0 s<br><sub>8.9–10.0</sub> | **5.3 s**<br><sub>5.3–5.5</sub> |
| ذروة استهلاك الذاكرة | **270 MB**<br><sub>248–274</sub> | 436 MB<br><sub>432–439</sub> | 375 MB<br><sub>365–379</sub> |
| الخطوات المُنجزة | 9 من 9 | 9 من 9 | 9 من 9 |

يُظهر الخط العريض أفضل قيمة في كل صف، فقط حين لا يتداخل نطاقها مع نطاقات الأخرى. تتداخل نطاقات رموز الإدخال، لذلك لا تدّعي هذه الجولة وجود فرق في رموز الإدخال. تعني «9 من 9» ثلاث خطوات في كل جلسة من الجلسات الثلاث، وقد اجتازت كل خطوة كل فحص خارجي. زمن المهمة هو الزمن الكامل للمهمة. طلب النموذج هو استدعاء واحد للنموذج، واستدعاء الأداة هو استخدام واحد للأداة من قِبل الوكيل. التكلفة المُبلَّغة هي ما يبلّغ به الوكيل: الرموز المستخدمة مضروبةً في السعر المنشور للنموذج. لا تحتسب التكلفة إلا رموز النموذج. وهي ليست فاتورة.

ما الذي تغيّر داخل الجلسة، بالأعداد: أرسل النموذج طلبات أقل، واستدعى الوكيل أدوات أقل.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-work-dark.svg">
    <img src="../assets/benchmark-2026-11-22-work-light.svg" width="840" alt="مخطط وحدات، فيه علامة واحدة لكل طلب إلى النموذج أو استدعاء أداة، وسيط 3 جلسات. طلبات النموذج: 25 بدون Simplicio، و18 مع Simplicio 3.14.0، و10 مع Simplicio 3.15.0. استدعاءات الأدوات: 22 و15 و7.">
  </picture>
</p>

الزمن حسب الخطوة، على مقياس واحد مشترك.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-steps-dark.svg">
    <img src="../assets/benchmark-2026-11-22-steps-light.svg" width="840" alt="وسيط الزمن حسب الخطوة على مقياس مشترك واحد. الخطوة 1، البناء: 57.3 s بدون Simplicio، و53.7 s مع Simplicio 3.14.0، و5.8 s مع Simplicio 3.15.0. الخطوة 2، التعديل: 17.3 s و15.2 s و8.9 s. الخطوة 3، التسجيل: 31.4 s و27.5 s و10.3 s.">
  </picture>
</p>

يُحسب كل وسيط على حدة، لذلك لا يساوي مجموع الخطوات وسيط المهمة كاملة.

<details>
<summary>الأرقام الدقيقة لكل خطوة</summary>

تحتوي كل خلية على وسيط زمن الخطوة ووسيط تكلفتها:

| الخطوة | بدون Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. البناء | 57.3 s / $0.0111 | 53.7 s / $0.0137 | 5.8 s / $0.0022 |
| 2. التعديل | 17.3 s / $0.0040 | 15.2 s / $0.0032 | 8.9 s / $0.0023 |
| 3. التسجيل | 31.4 s / $0.0075 | 27.5 s / $0.0056 | 10.3 s / $0.0026 |

</details>

**كيف تقرأها.** النسب محسوبة من القيم الوسيطة غير المقرّبة. مقارنةً بالوكيل نفسه من دون Simplicio، اكتملت المهمة كلها أسرع بمقدار 4.9 مرة، وكلّفت نحو ثلث ما كلّفته. وبالمقارنة مع الإصدار السابق، كانت أسرع بمقدار 4.2 مرة. داخل الجلسة، أرسل النموذج 10 طلبات بدلًا من 25، وكتب 3,211 من رموز الإخراج بدلًا من 18,162، واجتازت المهمة الفحوصات الخارجية نفسها. الحالة الأسوأ: حتى أسرع جلسة بدون Simplicio (97.1 s) ما زالت أبطأ بمقدار 3.7 مرة من أبطأ جلسة مع Simplicio 3.15.0 (26.6 s)، وحتى أرخص جلسة بدون Simplicio ($0.0186) ما زالت تكلّف 1.9 ضعف أغلى جلسة معه ($0.0098). خط الأساس هو Claude Code 2.1.330 بأدواته الخاصة، من دون خادم MCP ومن دون إعدادات Simplicio. تحسب التكلفة رموز النموذج فقط. شُغِّلت الجلسات أربعًا في وقت واحد على جهاز واحد، لذلك لا تُقارن الأزمنة إلا داخل هذه الجولة.

<a id="where-simplicio-does-not-win"></a>

### حيث لا يتفوّق Simplicio

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-memory-dark.svg">
    <img src="../assets/benchmark-2026-11-22-memory-light.svg" width="840" alt="ذروة استهلاك الذاكرة، وسيط 3 جلسات: 270 MB بدون Simplicio، وهي الأدنى؛ و436 MB مع Simplicio 3.14.0، أي أكثر بنسبة 61%؛ و375 MB مع Simplicio 3.15.0، أي أكثر بنسبة 39%.">
  </picture>
</p>

- **الذاكرة.** كانت ذروة استهلاك الذاكرة أعلى بنسبة 39% من الوكيل العادي: 375 MB مقابل 270 MB.
- **لم يُظهر الإصدار السابق أي مكسب في هذه المهمة.** تكلفة Simplicio 3.14.0 مساوية لتكلفة الوكيل بدون Simplicio، ويقع فرق زمنه داخل التفاوت بين التشغيلات. أما المكسب الذي تعرضه هذه الصفحة فقد جاء مع 3.15.0.
- **سكربت Python قصير ولمرة واحدة.** في جولة سابقة، كان Simplicio 3.10.8 أبطأ من الوكيل العادي مع كل نموذج جُرِّب. مع Claude Sonnet 5.5 في Claude Code استغرق 19.6 s وكلّف $0.0548، مقابل 11.4 s و$0.0283 بدونه. لم تُقَس هذه المهمة مرة أخرى على 3.15.0.
- **ما تثبّته ليس تمامًا ما جرى قياسه.** بُنيت النسخ من commits الإصدار، مع إيقاف تسجيل الدخول وإيقاف العملية الخلفية. ولم تُقَس التنزيلات الموقّعة.
- **العينة صغيرة.** ثلاث جلسات لكل إعداد، ونموذج واحد، ومشروع جديد صغير واحد، وجهاز واحد، وأربع جلسات في وقت واحد. اقرأ النسب كقياس لهذه المهمة، لا كوعد بنتيجة مماثلة في عملك. لم تُستبعد أي جلسة من هذه الإعدادات الثلاثة، ولم تُعَد أي جلسة. لم نقِس بعدُ مقدار عملك الذي يشبه هذه المهمة.

### تحقّق بنفسك

[التقرير](../benchmarks/2026-11-22-standard-benchmark.md) ينشر التعليمات الثلاث (بالبرتغالية مع ترجمة)، ووصفًا لكل فحص خارجي، والأرقام لكل جلسة. [ملف البيانات](../benchmarks/2026-11-22-standard-benchmark.json) يحتويها بصيغة JSON. لم يُنشر إطار الاختبار. شغّل التعليمات الثلاث نفسها في وكيلك، مع تشغيل Simplicio وإيقافه، في مشروع صغير لك، وقارن أزمنتك وفاتورتك أنت.

<a id="install"></a>

## التثبيت

ثبّت الملف التنفيذي الأصلي الموقّع. اختر مسارًا واحدًا.

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

في Windows، استخدم `py -m pip install --upgrade simplicio-installer` ثم `simplicio install`. إذا لم يكن مجلد سكربتات Python موجودًا في `PATH` لديك، فأضفه أولًا.

يحمّل المثبّت أحدث إصدار موقّع لمنصتك، ويتحقق من SHA-256 ومن توقيع Ed25519 الخاص به. ولا يستبدل الملف التنفيذي المثبّت إلا بعد ذلك. يوضع الملف التنفيذي تحت `~/.simplicio/bin/` (على Windows، تحت `%USERPROFILE%\.simplicio\bin\`)، ويسجّل Simplicio تلقائيًا في الوكلاء التي يجدها. إذا فشل التسجيل، يتوقف المثبّت بدلًا من أن يعلن النجاح. أعد تشغيل أي وكيل مفتوح حتى يعيد تحميل إعداداته.

**تسجيل الدخول.** تسجيل الدخول عبر Google مطلوب، بما في ذلك خلال النسخة التجريبية. شغّل `simplicio auth login`، ثم `simplicio auth status --json`، وتابع عندما تُظهر الحالة `active: true`. لا يشترط التسجيل أن تكون قد سجّلت الدخول، لذلك تُهيَّأ الوكلاء حتى قبل تسجيل الدخول. لا تلصق كلمة مرور أو رمزًا في إعدادات أي وكيل أبدًا.

<details>
<summary>الفحص والتحديث والإزالة</summary>

للتحديث، شغّل المثبّت مرة أخرى. يمكنك إعادة تشغيل أي من المثبّتين في أي وقت، فيجد أحدث إصدار. يوجد `install.sh` و`install.ps1` في جذر هذا المستودع.

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

- `--doctor` يفحص التثبيت.
- `--uninstall --keep-data` يزيل الملف التنفيذي المثبّت ويُبقي بياناتك. ويشمل ذلك حالة تسجيل الدخول عبر Google لمدة 30 يومًا في `~/.simplicio/login.json`.
- `--uninstall --purge` يزيل فقط الحالة التي يديرها Simplicio، بما فيها حالة تسجيل الدخول. ويُبقي `~/.simplicio/.env`، حيث قد تُحفظ بيانات اعتماد المزوّدين. ويحتاج الحذف الكامل إلى `SIMPLICIO_CONFIRM_PURGE=1`.
- لا يعدّل إلغاء التثبيت إعدادات وكلائك. تبقى مدخلات Simplicio في كل وكيل حتى تحذفها من إعدادات ذلك الوكيل نفسه.
- لا يزيل `--keep-data` البيانات الموجودة داخل مجلد `.simplicio` الخاص بالمشروع. تفقّد الهدف قبل أن تختار `--purge`.

التفاصيل كاملة في [INSTALL.md](../INSTALL.md).

</details>

<a id="first-run"></a>

## أول تشغيل

```bash
simplicio version
cd my-project
simplicio onboard
```

`simplicio version` يؤكّد الملف التنفيذي المثبّت. يجهّز `simplicio onboard` المشروع في أول مرة. ثم افتح وكيلك في ذلك المشروع واعمل كالمعتاد. للتأكد من أن Simplicio حُمّل، ابحث عن `simplicio` في قائمة خوادم MCP لدى الوكيل. في Claude Code، يعرض الأمر `/mcp` الخوادم المتصلة. هل تفضّل قراءة المثبّت أولًا؟ هو [install.sh](../install.sh).

<a id="works-with-the-agent-you-already-use"></a>

## يعمل مع الوكيل الذي تستخدمه أصلًا

Simplicio خادم MCP محلي يعمل عبر STDIO، لذلك يمكن توجيه أي وكيل يستطيع تشغيل خادم MCP محلي إليه.

يسلّم المثبّت عملية التسجيل إلى أداة التسجيل الخاصة بـ Simplicio. يكتشف الوكلاء الموجودين على جهازك، ويكتب مدخل Simplicio للوكلاء التي يعرف كيف يهيّئها، ومنها Claude Code وCodex وCursor وVisual Studio Code وOpenCode وGemini CLI وKiro. يوجد في هذا المستودع ملفان يحدّدان إلى أي مدى يصل كل تكامل:

- السجل [`plugins/simplicio/host-surfaces.json`](../plugins/simplicio/host-surfaces.json) يسمّي 43 معرّف وكيل، ويحدّد لكل منها طريقة وصول Simplicio إليه: مدخل MCP يكتبه Simplicio (23)، أو إضافة أو امتداد أصلي (5)، أو حزمة إضافة قابلة للنقل (4)، أو إعداد موجّه تتبعه بنفسك (9)، أو أداة سطر أوامر أخرى (2).
- مصفوفة التوافق [`docs/hosts/compatibility-matrix.md`](../docs/hosts/compatibility-matrix.md) تحدّد ما جرى التحقق منه. من بين الـ43 تعدّ 12 وكيلًا مدعومًا و29 وكيلًا `unverified`، وليس لها صف لـCodex وGemini CLI. وحين يقول السجل إن Simplicio تكتب المدخل، بينما تصنّفه المصفوفة `unverified`، فاعتبر ذلك التكامل غير مختبر.

لدى 23 وكيلًا دليل في [`docs/hosts/`](../docs/hosts/). أما الوكلاء الذين يُوصل إليهم عبر إضافة، فتُطبَّق الإضافة في خطوة منفصلة تطلب موافقتك، ويصفها [INSTALL.md](../INSTALL.md).

<details>
<summary>جميع الوكلاء الـ43، حسب الطريقة التي تصل بها Simplicio إليهم</summary>

| طريقة وصول Simplicio إليه | العدد | الوكلاء |
|---|---|---|
| مدخل MCP يكتبه Simplicio | 23 | **xAI Grok Build**, MiMo Code, Amp, OpenClaude, Antigravity, **Pi**, **oh-my-pi**, Goose, Auggie, Autohand Code, Charm, Cline, Command Code, Continue, Droid, Kilocode, Kimi, Mistral Vibe, Rovo Dev, **Visual Studio Code**, **Meta Muse Code**, **OpenMausBot**, **OpenMuse (Python)** |
| إضافة أو امتداد أصلي | 5 | **Claude Code**, Codex, **OpenCode**, Hermes Agent, Gemini CLI |
| حزمة إضافة قابلة للنقل | 4 | **Cursor**, GitHub Copilot, **Kiro**, Qwen Code |
| إعداد موجّه تتبعه بنفسك | 9 | Devin, Codebuff, CopilotKit OpenDots, CopilotKit OpenBot, agentes.chat, OpenAI dots, xAI Grok Bot, Meta Muse app, Cue by Manus |
| أداة سطر أوامر أخرى | 2 | **OrcaDev / Orca ADE**, T3 Code |

بالخط العريض: مصفوفة التوافق تعدّ الوكيل مدعومًا.

</details>

لتكرار التسجيل، شغّل `simplicio mcp register`. أمر الخادم هو `simplicio serve --mcp --stdio`. هذه هي الأدوات الأساسية التي يحصل عليها وكيلك:

| الأداة | ما الذي تمنحه |
|---|---|
| `simplicio_map` | خريطة مختصرة للمستودع تساعد الوكيل على إيجاد طريقه فيه |
| `simplicio_context` | السياق الذي تحتاجه المهمة، محدودًا، بدلًا من الملفات كاملة |
| `simplicio_edit` | تعديلات منظّمة على الملفات من خطة معدّة |
| `simplicio_validate` | فحوصات خط المعالجة والاختبارات والتسليم |
| `simplicio_run` | تشغيل مهمة تحت تحكّم Simplicio |

القائمة الحيّة هي ما يُبلغ عنه الخادم عند بدء التشغيل. يصف [MCP-CONNECT.md](../MCP-CONNECT.md) الأدوات الأساسية.

<details>
<summary>الإعدادات اليدوية</summary>

إذا لم يُهيَّأ وكيلك نيابةً عنك، فأضف هذا المدخل إلى إعدادات MCP الخاصة به. استبدل المسار بالمسار المطلق للملف التنفيذي المثبّت.

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

يقرأ Codex ملفات TOML. يشغّل الوكلاء `command` مباشرةً، لذلك لا تستخدم `~` ولا تعتمد على توسيع الشِّل. استخدم الشرطة المائلة الأمامية في مسارات Windows، واستبدل اسم المستخدم في المثال.

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

مكان ملف كل وكيل: [MCP-CONNECT.md](../MCP-CONNECT.md).

</details>

<a id="command-line"></a>

## سطر الأوامر

| الأمر | ما تحصل عليه |
|---|---|
| `simplicio map --repo . --for-llm markdown` | خريطة بنيوية مختصرة للمستودع، مكتوبة ليقرأها نموذج |
| `simplicio context --repo .` | السياق المحدود لمهمة ما |
| `simplicio memory query "query" --json` | ما يعرفه المشروع مسبقًا، مسترجعًا من ذاكرته المفهرسة، بصيغة JSON |
| `simplicio edit --plan plan.json --repo .` | مجموعة معدّة من التعديلات المنظّمة، تُطبَّق على الملفات |
| `simplicio run "task" --repo . --agents N` | تشغيل مهمة بـN من الوكلاء تحت تحكّم Simplicio |
| `simplicio loop` | عمل يسير في جولات حتى يتقارب |

الأسماء التي ستراها في رسائل Simplicio: Mapper يرصد، وFast يُسقِط أو يسترجع، وDev CLI يُعدِّل، وRuntime يُدير، وLoop يتقارب.

<a id="safety-and-privacy"></a>

## السلامة والخصوصية

يصف هذا القسم الإصدار 3.15.0.

**ما الذي يرسله Simplicio، ولمن**

- **يبقى على جهازك.** تعمل الخرائط والسياق والتعديلات والفحوصات داخل الملف التنفيذي للبرنامج. ويسلّم النتائج إلى وكيلك على الجهاز نفسه. ما يرسله وكيلك إلى مزوّد النموذج الخاص به يحدده الوكيل، كما كان من قبل.
- **إلى SimpleTI (simpleti.com.br).** فحوصات تسجيل الدخول والخطة فقط. تحمل هذه الطلبات رمز تسجيل الدخول، وإصدار Simplicio، واسم مضيف جهازك. ويحمل البحث الاختياري عن الترخيص بريد حسابك الإلكتروني أيضًا. وتُعيد الخدمة بريد حسابك واسمك وخطتك. لا محتوى للمستودع: لا ملفات، ولا مسارات ملفات، ولا تعليمات (prompts)، ولا تعديلات.
- **إلى GitHub.** فحص في الخلفية لوجود إصدار جديد، مرة كل 12 ساعة تقريبًا على الأكثر. لا يحمل شيئًا عنك أو عن كودك. اضبط `SIMPLICIO_DISABLE_AUTO_UPDATE=1` لإيقافه. وعند التحديث، يُنزَّل الملف التنفيذي الجديد من GitHub، ويُتحقَّق من SHA-256 وتوقيعه قبل أن يستبدل القديم.
- **لا تحليلات.** فُحص Simplicio 3.15.0 والملفات التي يثبّتها في وكلائك لهذا الغرض: لا يرفع أيٌّ منها تحليلات أو تقارير أعطال أو بيانات استخدام. سجلات الاستخدام والتوفير ملفات محلية. ولا تشغّل الخطافات التي يثبّتها سوى برامج محلية (الملف التنفيذي للبرنامج نفسه، وسكربتات محلية للإضافات الاختيارية)، ولا يتصل أيٌّ منها بالشبكة.
- **إلى الخدمات التي تُهيّئها.** يتلقى مزوّد النموذج أو GitHub أو Jira أو أداة إشعارات الدردشة أو ذاكرة التخزين المؤقت للفريق ما ترسله تلك الميزة، وقد يشمل ذلك التعليمات (prompts) والكود. وتحمل الطلبات إلى مزوّد النموذج ترويسة تسمّي Simplicio بوصفه العميل.
- **هناك ميزتان تصلان إلى خدمة متاحة للعموم على الإنترنت دون أي إعداد.** البحث على الويب، عند تشغيله، يرسل استعلام البحث إلى DuckDuckGo ما لم تُهيّئ خدمة بحث أخرى. وفي دردشة Simplicio نفسها، قد تتحول رسالة تبدو كسؤال عن الويب إلى ذلك الاستعلام. وتدقيق أمان التبعيات، عند تشغيله، يرسل أسماء التبعيات وإصداراتها إلى osv.dev. ولا يرسل أيٌّ منهما محتوى الملفات.
- **التنزيلات.** يُنزّل المثبّت ومسار التحديث الملفات من GitHub. وتجلب بعض السكربتات المساعدة الاختيارية أدواتها الخاصة من PyPI أو npm عند تشغيلها. وإذا بدأت إضافة وكيل ولم تجد الملف التنفيذي للبرنامج، فإنها تنزّل المثبّت الرسمي من GitHub، على commit محدّد، ويتحقق منه عبر SHA-256.

**الإصدارات الموقّعة.** تنشر كل نسخة ملفاتها التنفيذية مع مجاميع التحقق SHA-256، وتوقيعات Ed25519، وSBOM (قائمة بما يدخل في البناء)، وإثبات مصدر البناء. يتحقق المثبّتات ومسار التحديث من مجموع التحقق والتوقيع قبل أن يستبدلا الملف التنفيذي المثبّت. وبالنسبة إلى الإصدارات المستقرة، يجعل العقد غياب التوقيع أو عدم صلاحيته، وعدم تطابق مجموع التحقق، إخفاقات قاطعة. العقد موجود في [docs/UPDATE_SIGNATURE_CONTRACT.md](../docs/UPDATE_SIGNATURE_CONTRACT.md).

**ما الذي يغيّره المثبّت في وكيلك.** يضيف مدخل Simplicio إلى إعدادات MCP الخاصة بالوكيل، ويُبقي باقي الإعدادات كما هي. وفي Claude Code يسمح أيضًا بالقيمة `mcp__simplicio__*`، حتى لا تُرفض أداة من Simplicio في الوضع التلقائي. وفي الوكلاء التي تحقق المثبّت من واجهة الخطافات الخاصة بها، يثبّت فيها خطافات Simplicio أيضًا. يوضح [INSTALL.md](../INSTALL.md) ما يكتبه المثبّت، وتعطي أدلة الوكلاء في [`docs/hosts/`](../docs/hosts/) التفاصيل. لا يُلغي إلغاء التثبيت هذه المدخلات. ويشرح قسم التثبيت كيفية إزالتها.

## ما يوجد أيضًا في هذا المستودع

<details>
<summary>تطبيق سطح المكتب (معاينة macOS)</summary>

نُشرت معاينة لتطبيق سطح المكتب لنظام macOS (Apple Silicon) بصيغة [Simplicio-3.8.47-arm64.dmg](https://github.com/simpletibr/simplicio/releases/download/v3.8.47/Simplicio-3.8.47-arm64.dmg). ويوجد SHA-256 الخاص بها في [DESKTOP-SHA256SUMS](../DESKTOP-SHA256SUMS)، منفصلًا عن مجاميع التحقق الخاصة بملفات Simplicio التنفيذية. لا يحتوي ملف DMG على ملف توقيع، ويضم ملفًا تنفيذيًا من Simplicio 3.8.47.

- لم يُنشر تطبيق سطح المكتب لنظام Windows. على Windows، استخدم التثبيت من سطر الأوامر أعلاه.
- لم يُنفَّذ توقيع Apple Developer ID ولا الاعتماد (notarization). الحزمة موقّعة ذاتيًا (ad-hoc)، أي من دون شهادة مطوّر من Apple، ولا يُزعم قبول Gatekeeper، لذلك قد يحذّرك macOS عند فتحها.
- التثبيت من سطر الأوامر أعلاه هو مسار التثبيت العام المدعوم، إلى أن تُنشر حزمة Desktop موقّعة.

التفاصيل: [docs/desktop/RELEASE.md](../docs/desktop/RELEASE.md).

</details>

<details>
<summary>للمشرفين: مخطط التدفق المُولَّد</summary>

الأوامر والأدوات الموثّقة في README.md وMCP-CONNECT.md مرسومة في تدفق واحد، [docs/flow/simplicio.svg](../docs/flow/simplicio.svg)، يُولَّد من ملف مصدر واحد، `docs/flow/simplicio.flow.json`. لإعادة توليده شغّل `python3 scripts/generate_flow.py`، وللتحقق من انحرافه شغّل `python3 scripts/generate_flow.py --check`. والعقد الذي يبقيه متّسقًا مع هذه الصفحة ومع MCP-CONNECT.md هو `python3 -m pytest tests/test_flow_contract.py -q`. فحص الاستيراد إلى Langflow هو `scripts/verify_flow_langflow.py`، ويفشل بشكل مغلق (يخرج بالقيمة 2 مع `status=blocked`) حين لا يعمل أي خادم. الأدلة موجودة تحت `docs/flow/evidence/` و`docs/flow/render/`، و[docs/flow/README.md](../docs/flow/README.md) يضم المتطلبات وطريقة تكرار الاختبار.

</details>

<a id="questions-people-ask"></a>

## أسئلة شائعة

**هل المقارنة عادلة؟**<br>
الوكيل نفسه، والنموذج نفسه، والتعليمات الثلاث نفسها، والمشروع الأولي نفسه، والفحوصات الخارجية نفسها، في جولة واحدة. خط الأساس لا يملك خادم MCP ولا أي إعدادات تخص Simplicio. انظر [حيث لا يتفوّق Simplicio](#where-simplicio-does-not-win) و[القيود](../benchmarks/2026-11-22-standard-benchmark.md#limits) الواردة في التقرير.

**هل عليّ تغيير وكيلي أو نموذجي؟**<br>
لا. تتصل Simplicio بالوكيل الذي تستخدمه أصلًا. وفي اختبار الأداء أعلاه، كان كل إعداد يستخدم الوكيل نفسه والنموذج نفسه.

**هل سأحصل دائمًا على هذه الأرقام؟**<br>
لا. فهي تقيس مهمة واحدة، بنموذج واحد، على جهاز واحد، عبر ثلاث جلسات لكل إعداد. انظر [حيث لا يتفوّق Simplicio](#where-simplicio-does-not-win)، وشغّل المقارنة على عملك أنت.

**هل هو مفتوح المصدر؟**<br>
لا. Simplicio برمجية خاصة. وهي ملف تنفيذي موقّع، يُنشر كأصول للإصدار، ولا يُنشر مصدرها. يحتوي هذا المستودع على المثبّتات، وحزم الوكلاء، ومصدر تطبيق Desktop، والتوثيق، وبيانات اختبار الأداء.

**كيف أزيله؟**<br>
شغّل `sh install.sh --uninstall --keep-data`، أو `pwsh install.ps1 -Uninstall -KeepData` على Windows. يزيل الأمر الملف التنفيذي ويُبقي بياناتك. ولا يعدّل إعدادات وكلائك، لذلك احذف مدخلات Simplicio من إعدادات كل وكيل. يحتوي [التثبيت](#install) على التفاصيل وخيار الحذف الكامل.

**هل أحتاج إلى حساب؟**<br>
نعم. تسجيل الدخول عبر Google مطلوب، بما في ذلك خلال النسخة التجريبية. شغّل `simplicio auth login`.

**هل يغادر كودي جهازي؟**<br>
تعمل الخرائط والسياق والتعديلات والفحوصات على جهازك. ويتواصل Simplicio مع SimpleTI لفحوصات تسجيل الدخول والخطة، ومع GitHub للبحث عن التحديثات، ولا يُرسل أيٌّ منهما محتوى المستودع. وقد تصل الميزات التي تُهيّئها أو تشغّلها إلى خدمات أخرى. القائمة الكاملة في [ما الذي يرسله Simplicio، ولمن](#safety-and-privacy).

<a id="documentation-and-community"></a>

## التوثيق والمجتمع

- **الموقع:** [simpleti.com.br/simplicio](https://simpleti.com.br/simplicio/)
- **التوثيق:** [simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)
- **Discord:** [انضم إلى المجتمع](https://discord.gg/wM6tr7xVb)
- **المشكلات:** [متتبّع مشكلات GitHub](https://github.com/simpletibr/simplicio/issues)
- **في هذا المستودع:** [INSTALL.md](../INSTALL.md) و[MCP-CONNECT.md](../MCP-CONNECT.md) و[docs/hosts/](../docs/hosts/)
- **ذو صلة:** Simplicio Video (hypit). لاستنساخه: `git clone https://github.com/hypit-ai/hypit.git simplicio-video`

<p align="center">
  <sub>© 2026 SimpleTI. Simplicio برمجية خاصة مسجّلة. جميع الحقوق محفوظة.</sub>
</p>
