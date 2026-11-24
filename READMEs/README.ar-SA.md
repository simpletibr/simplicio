<div align="center">

<img src="../assets/simplicio-icon-192.png" alt="شعار Simplicio" width="96" height="96">

<h1>Simplicio</h1>

<p><b>UltraFast Mode for all.</b></p>

<p><b>نفس الوكيل، ونفس النموذج، ونفس المهمة: <span dir="ltr">121&nbsp;s&nbsp;→&nbsp;25&nbsp;s</span>، و<span dir="ltr">$0.0226&nbsp;→&nbsp;$0.0076</span>.</b></p>

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
- **ملف تنفيذي واحد وموقّع** يسجّل نفسه في وكلائك، ويعمل على جهازك كخادم MCP محلي عبر STDIO.
- **ما يتغيّر هو الجلسة.** مدتها وتكلفتها.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/diagram-where-simplicio-runs-dark.svg">
    <img src="../assets/diagram-where-simplicio-runs-light.svg" width="840" alt="مخطط. على جهازك: أنت ووكيلك وSimplicio ومستودعك. يتواصل الوكيل مع Simplicio عبر STDIO المحلي (MCP). ويتواصل الوكيل مع مزوّد النموذج كما كان من قبل. ويتواصل Simplicio مع SimpleTI لفحوصات تسجيل الدخول والخطة، ومع GitHub لفحص الإصدار، ولا يحمل أيٌّ منهما محتوى المستودع.">
  </picture>
</p>

<p align="center">
  <sub>التدفق الافتراضي. [ما الذي يرسله Simplicio، ولمن](#safety-and-privacy) يضم الخدمات الأخرى.</sub>
</p>

<details>
<summary>MCP وSTDIO</summary>

MCP هو Model Context Protocol، أي الطريقة التي يستدعي بها وكيل البرمجة الأدوات الخارجية. وSTDIO يعني أن الوكيل يشغّل البرنامج بنفسه، ويتواصل معه عبر مدخله ومخرجه القياسيين.

يمنح وكيلك أدوات: خريطة للمستودع، وسياقًا محدودًا، وتعديلات منظّمة، وفحوصات. [الأدوات الأساسية](#works-with-the-agent-you-already-use) مدرجة أدناه.

تثبّت ملفًا تنفيذيًا أصليًا واحدًا وموقّعًا. يتحقق المثبّت من التوقيع، ثم يسجّل Simplicio في الوكلاء التي يجدها على جهازك.

</details>

<a id="the-measurement"></a>

## القياس

مهمة واحدة، تُنفَّذ بالطريقة نفسها مع Simplicio وبدونه: ثلاث خطوات في جلسة واحدة للوكيل، ويُفحص كل ناتج من خارج الجلسة.

1. بناء قائمة للمستخدمين: واجهة API وصفحة فيها جدول وبحث وترتيب.
2. تعديلها: حذف عمود، وإضافة فلتر حسب الدور، وعمود للتاريخ.
3. إضافة تسجيل: نقطة نهاية `POST` تتحقق من مدخلاتها، وصفحة نموذج.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-sessions-dark.svg">
    <img src="../assets/benchmark-2026-11-22-sessions-light.svg" width="840" alt="مخطط نقطي لكل جلسة: زمن المهمة كاملة أفقيًا، والتكلفة كما يبلغها الوكيل رأسيًا. Simplicio 3.15.0، معيّنات خضراء: من 23 إلى 27 s، ومن $0.0071 إلى $0.0098. Simplicio 3.14.0، مربعات رمادية: من 90 إلى 106 s، ومن $0.0214 إلى $0.0249. بدون Simplicio، دوائر مفرغة: من 97 إلى 172 s، ومن $0.0186 إلى $0.0280.">
  </picture>
</p>

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

وسيط 3 جلسات، من الأدنى إلى الأعلى تحت كل قيمة. يُظهر الخط العريض أفضل قيمة في الصف، حين لا تتداخل النطاقات. «9 من 9» تعني 3 خطوات في كل جلسة من الجلسات الثلاث، واجتازت جميعها كل فحص خارجي.

طلبات النموذج واستدعاءات الأدوات لكل جلسة.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-work-dark.svg">
    <img src="../assets/benchmark-2026-11-22-work-light.svg" width="840" alt="مخطط وحدات، فيه علامة واحدة لكل طلب إلى النموذج أو استدعاء أداة، وسيط 3 جلسات. طلبات النموذج: 25 بدون Simplicio، و18 مع Simplicio 3.14.0، و10 مع Simplicio 3.15.0. استدعاءات الأدوات: 22 و15 و7.">
  </picture>
</p>

الزمن حسب الخطوة، على مقياس مشترك واحد.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-steps-dark.svg">
    <img src="../assets/benchmark-2026-11-22-steps-light.svg" width="840" alt="وسيط الزمن حسب الخطوة على مقياس مشترك واحد. الخطوة 1، البناء: 57.3 s بدون Simplicio، و53.7 s مع Simplicio 3.14.0، و5.8 s مع Simplicio 3.15.0. الخطوة 2، التعديل: 17.3 s و15.2 s و8.9 s. الخطوة 3، التسجيل: 31.4 s و27.5 s و10.3 s.">
  </picture>
</p>

<details>
<summary>الأرقام الدقيقة لكل خطوة</summary>

تحتوي كل خلية على وسيط زمن الخطوة ووسيط تكلفتها:

| الخطوة | بدون Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. البناء | 57.3 s / $0.0111 | 53.7 s / $0.0137 | 5.8 s / $0.0022 |
| 2. التعديل | 17.3 s / $0.0040 | 15.2 s / $0.0032 | 8.9 s / $0.0023 |
| 3. التسجيل | 31.4 s / $0.0075 | 27.5 s / $0.0056 | 10.3 s / $0.0026 |

</details>

**كيف تقرأها.** اكتملت المهمة كلها أسرع بمقدار 4.9 مرة، وبنحو ثلث التكلفة؛ وحتى أسرع جلسة بدون Simplicio (97.1 s) كانت أبطأ بمقدار 3.7 مرة من أبطأ جلسة مع 3.15.0 (26.6 s). [المنهجية والقيود](../benchmarks/2026-11-22-standard-benchmark.md#limits)

<details>
<summary>كيف يُعرَّف كل رقم</summary>

- تُحسب النسب من القيم الوسيطة غير المقرّبة. مقارنةً بالإصدار السابق، اكتملت المهمة كلها أسرع بمقدار 4.2 مرة.
- يُحسب كل وسيط على حدة، لذلك لا يساوي مجموع الخطوات وسيط المهمة كاملة.
- الحالة الأسوأ: حتى أسرع جلسة بدون Simplicio (97.1 s) كانت أبطأ بمقدار 3.7 مرة من أبطأ جلسة مع Simplicio 3.15.0 (26.6 s)، وحتى أرخص جلسة بدونه ($0.0186) كانت تكلّف 1.9 ضعف أغلى جلسة معه ($0.0098).
- خط الأساس هو Claude Code 2.1.330 بأدواته الخاصة، من دون خادم MCP ومن دون أي إعدادات تخص Simplicio.
- تُفحص كل خطوة من خارج الجلسة: تُستدعى واجهة API عبر HTTP، وتُحمَّل الصفحات في Chrome بلا واجهة، أي Chrome بلا نافذة.
- الفحوصات لا تختبر مربع البحث، ولا الترتيب، ولا إعادة التوجيه بعد الحفظ، ولا شكل الصفحة، ولا جودة الكود.
- طلب النموذج استدعاء واحد للنموذج، واستدعاء الأداة استخدام واحد للأداة من قِبل الوكيل.
- التكلفة المُبلَّغة هي الرموز المستخدمة مضروبةً في السعر المنشور للنموذج. لا تحسب إلا رموز النموذج. وليست فاتورة.
- تتداخل نطاقات رموز الإدخال، لذلك لا تدّعي هذه الجولة فرقًا في رموز الإدخال.
- شُغِّلت أربع جلسات في وقت واحد على جهاز واحد، لذلك لا تُقارن الأزمنة إلا داخل هذه الجولة.

</details>

<a id="where-simplicio-does-not-win"></a>

### حيث لا يتفوّق Simplicio

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/benchmark-2026-11-22-memory-dark.svg">
    <img src="../assets/benchmark-2026-11-22-memory-light.svg" width="840" alt="ذروة استهلاك الذاكرة، وسيط 3 جلسات: 270 MB بدون Simplicio، وهي الأدنى؛ و436 MB مع Simplicio 3.14.0، أي أكثر بنسبة 61%؛ و375 MB مع Simplicio 3.15.0، أي أكثر بنسبة 39%.">
  </picture>
</p>

- **الذاكرة.** كانت ذروة استهلاك الذاكرة أعلى بنسبة 39%: 375 MB مقابل 270 MB.
- **لم يُظهر الإصدار السابق أي مكسب في هذه المهمة.** كانت تكلفة Simplicio 3.14.0 مساوية لتكلفة الوكيل بدون Simplicio.
- **سكربت Python قصير ولمرة واحدة.** كان Simplicio 3.10.8 أبطأ (19.6 s مقابل 11.4 s)، ولم تُقَس هذه المهمة مرة أخرى.
- **صفحة صغيرة واحدة، ونماذج قوية.** كان Simplicio 3.15.0 أبطأ بنسبة 14% إلى 47%.
- **ما تثبّته ليس تمامًا ما جرى قياسه.** بُنيت النسخ من commits الإصدار، مع إيقاف تسجيل الدخول.
- **العينة صغيرة.** ثلاث جلسات لكل إعداد، ونموذج واحد، ومشروع واحد.

<details>
<summary>القيود كاملة</summary>

- **الذاكرة.** كانت ذروة استهلاك الذاكرة أعلى بنسبة 39% من الوكيل العادي: 375 MB مقابل 270 MB.
- **لم يُظهر الإصدار السابق أي مكسب في هذه المهمة.** كانت تكلفة Simplicio 3.14.0 مساوية لتكلفة الوكيل بدون Simplicio، ويقع فرق زمنه داخل التفاوت بين التشغيلات. أما المكسب فقد جاء مع 3.15.0.
- **سكربت Python قصير ولمرة واحدة.** في جولة سابقة، كان Simplicio 3.10.8 أبطأ من الوكيل العادي مع كل نموذج جُرِّب: مع Claude Sonnet 5.5 في Claude Code، استغرق 19.6 s وكلّف $0.0548، مقابل 11.4 s و$0.0283. لم تُقَس هذه المهمة مرة أخرى على 3.15.0.
- **صفحة صغيرة واحدة، ونماذج قوية.** مع Sonnet 5.5 أو Opus 5.5، استغرق Simplicio 3.15.0 وقتًا أطول بنسبة 14% إلى 47% وكلّف أكثر بنسبة 14% إلى 41% في 6 حالات من 6. كانت كل صفحة صحيحة في الحالتين. Sonnet 5.5، الإنشاء، وسيط 3 جلسات: 24 s و$0.082 مقابل 20 s و$0.066. الإصلاح قيد العمل، ولم يصدر بعد في أي إصدار.
- **ما تثبّته ليس تمامًا ما جرى قياسه.** بُنيت النسخ من commits الإصدار، مع إيقاف تسجيل الدخول والعملية الخلفية. ولم تُقَس التنزيلات الموقّعة.
- **العينة صغيرة.** ثلاث جلسات لكل إعداد، ونموذج واحد، ومشروع جديد صغير واحد، وجهاز واحد، وأربع جلسات في وقت واحد؛ لم يُستبعد أي منها ولم تُعَد. تقيس النسب هذه المهمة، لا مهمتك، ولم نقِس بعدُ مقدار عملك الذي يشبهها.

</details>

### تحقّق بنفسك

[التقرير](../benchmarks/2026-11-22-standard-benchmark.md) ينشر التعليمات (prompts) الثلاث (بالبرتغالية، مع ترجمة)، وكل فحص خارجي، وكل جلسة؛ و[ملف البيانات](../benchmarks/2026-11-22-standard-benchmark.json) يحتوي عليها بصيغة JSON. لم يُنشر إطار الاختبار.

<a id="install"></a>

## التثبيت

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

على Windows، استخدم `py -m pip install --upgrade simplicio-installer` ثم `simplicio install`.

يتحقق المثبّت من الإصدار الموقّع، ويسجّل Simplicio تلقائيًا في الوكلاء التي يجدها. ثم سجّل الدخول بالأمر `simplicio auth login`.

<details>
<summary>تفاصيل التثبيت</summary>

- يُنزّل أحدث إصدار موقّع لمنصتك، ويتحقق من SHA-256 ومن توقيع Ed25519 الخاص به، ثم يستبدل الملف التنفيذي المثبّت.
- يوضع الملف التنفيذي تحت `~/.simplicio/bin/` (على Windows، تحت `%USERPROFILE%\.simplicio\bin\`)، ويُسجَّل Simplicio تلقائيًا في الوكلاء التي يجدها. إذا فشل التسجيل، يتوقف المثبّت بدلًا من أن يعلن النجاح.
- أعد تشغيل أي وكيل مفتوح حتى يعيد تحميل إعداداته. وإذا لم يكن مجلد سكربتات Python موجودًا في `PATH`، فأضفه أولًا.

**تسجيل الدخول.** تسجيل الدخول عبر Google مطلوب، بما في ذلك خلال النسخة التجريبية. شغّل `simplicio auth login`، ثم `simplicio auth status --json`، وتابع عندما تُظهر الحالة `active: true`. يعمل التسجيل قبل أن تسجّل الدخول. لا تلصق أبدًا كلمة مرور أو رمزًا في إعدادات أي وكيل.

للتأكد من أن Simplicio حُمّل، ابحث عن `simplicio` في قائمة خوادم MCP لدى الوكيل. في Claude Code، يعرض الأمر `/mcp` الخوادم المتصلة. هل تفضّل قراءة المثبّت أولًا؟ هو [install.sh](../install.sh).

للتحديث، شغّل أيًّا من المثبّتين مرة أخرى في أي وقت، فيجد أحدث إصدار. يوجد `install.sh` و`install.ps1` في جذر هذا المستودع.

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
- `--uninstall --purge` يزيل الحالة التي يديرها Simplicio وحدها، بما فيها حالة تسجيل الدخول. ويُبقي `~/.simplicio/.env`، حيث قد تُحفظ بيانات اعتماد المزوّدين. ويحتاج الحذف الكامل إلى `SIMPLICIO_CONFIRM_PURGE=1`.
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

`simplicio version` يتحقق من التثبيت، و`simplicio onboard` يجهّز المشروع. ثم افتح وكيلك هناك.

<a id="works-with-the-agent-you-already-use"></a>

## يعمل مع الوكيل الذي تستخدمه أصلًا

يسلّم المثبّت عملية التسجيل إلى أداة التسجيل الخاصة بـ Simplicio. يكتب مدخل Simplicio للوكلاء التي يعرف كيف يهيّئها، ومن بينها Claude Code وCodex وCursor وVisual Studio Code وOpenCode وGemini CLI وKiro.

يسمّي السجل [`plugins/simplicio/host-surfaces.json`](../plugins/simplicio/host-surfaces.json) 43 معرّف وكيل، وتحدّد المصفوفة [`docs/hosts/compatibility-matrix.md`](../docs/hosts/compatibility-matrix.md) 12 وكيلًا مدعومًا و29 وكيلًا `unverified`. اعتبر أي تكامل `unverified` تكاملًا غير مختبر.

<details>
<summary>جميع الوكلاء الـ43</summary>

- يسمّي السجل 43 معرّف وكيل، ويحدّد طريقة وصول Simplicio إلى كل منها: مدخل MCP يكتبه Simplicio (23)، أو إضافة أو امتداد أصلي (5)، أو حزمة إضافة قابلة للنقل (4)، أو إعداد موجّه تتبعه بنفسك (9)، أو أداة سطر أوامر أخرى (2).
- لا تضم المصفوفة صفًا لـCodex وGemini CLI. وحتى حين يقول السجل إن Simplicio يكتب المدخل، اعتبر أي تكامل `unverified` غير مختبر.
- لدى 23 وكيلًا دليل في [`docs/hosts/`](../docs/hosts/). أما الوكلاء الذين يُوصل إليهم عبر إضافة، فتُطبَّق الإضافة في خطوة منفصلة تطلب موافقتك، ويصفها [INSTALL.md](../INSTALL.md).

| طريقة وصول Simplicio | العدد | الوكلاء |
|---|---|---|
| مدخل MCP يكتبه Simplicio | 23 | **xAI Grok Build**, MiMo Code, Amp, OpenClaude, Antigravity, **Pi**, **oh-my-pi**, Goose, Auggie, Autohand Code, Charm, Cline, Command Code, Continue, Droid, Kilocode, Kimi, Mistral Vibe, Rovo Dev, **Visual Studio Code**, **Meta Muse Code**, **OpenMausBot**, **OpenMuse (Python)** |
| إضافة أو امتداد أصلي | 5 | **Claude Code**, Codex, **OpenCode**, Hermes Agent, Gemini CLI |
| حزمة إضافة قابلة للنقل | 4 | **Cursor**, GitHub Copilot, **Kiro**, Qwen Code |
| إعداد موجّه تتبعه بنفسك | 9 | Devin, Codebuff, CopilotKit OpenDots, CopilotKit OpenBot, agentes.chat, OpenAI dots, xAI Grok Bot, Meta Muse app, Cue by Manus |
| أداة سطر أوامر أخرى | 2 | **OrcaDev / Orca ADE**, T3 Code |

بالخط العريض: المصفوفة تعدّ الوكيل مدعومًا.

</details>

هذه هي الأدوات الأساسية التي يحصل عليها وكيلك:

| الأداة | ما الذي تمنحه |
|---|---|
| `simplicio_map` | خريطة مختصرة للمستودع تساعد الوكيل على إيجاد طريقه فيه |
| `simplicio_context` | السياق الذي تحتاجه المهمة، محدودًا، بدلًا من الملفات كاملة |
| `simplicio_edit` | تعديلات منظّمة على الملفات من خطة معدّة |
| `simplicio_validate` | فحوصات خط المعالجة والاختبارات والتسليم |
| `simplicio_run` | تشغيل مهمة تحت تحكّم Simplicio |

يصف [MCP-CONNECT.md](../MCP-CONNECT.md) الأدوات الأساسية.

<details>
<summary>الإعداد اليدوي</summary>

Simplicio خادم MCP محلي يعمل عبر STDIO، لذلك يمكن توجيه أي وكيل يستطيع تشغيل خادم MCP محلي إليه. لتكرار التسجيل، شغّل `simplicio mcp register`. أمر الخادم هو `simplicio serve --mcp --stdio`.

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
| `simplicio run "task" --repo . --agents N` | تشغيل مهمة بعدد N من الوكلاء تحت تحكّم Simplicio |
| `simplicio loop` | عمل يسير في جولات حتى يتقارب |

الأسماء التي ستراها في رسائل Simplicio: Mapper يرصد، وFast يُسقِط أو يسترجع، وDev CLI يُعدِّل، وRuntime يُدير، وLoop يتقارب.

<a id="safety-and-privacy"></a>

## السلامة والخصوصية

يصف هذا القسم الإصدار 3.15.0.

- **يبقى على جهازك.** تعمل الخرائط والسياق والتعديلات والفحوصات داخل الملف التنفيذي لـSimplicio.
- **إلى SimpleTI (simpleti.com.br).** فحوصات تسجيل الدخول والخطة فقط، ولا محتوى للمستودع.
- **إلى GitHub.** فحص للإصدارات يمكنك إيقافه.
- **لا تحليلات.** لا يرفع Simplicio أي تحليلات أو تقارير أعطال أو بيانات استخدام.
- **إلى الخدمات التي تُهيّئها.** تتلقى ما ترسله تلك الميزة، وقد يشمل ذلك التعليمات (prompts) والكود.
- **ميزتان تصلان إلى خدمة متاحة للعموم على الإنترنت دون أي إعداد.** البحث على الويب (DuckDuckGo) وتدقيق أمان التبعيات (osv.dev)، ولا يرسل أيٌّ منهما محتوى الملفات.
- **التنزيلات.** من GitHub، وتجلب بعض السكربتات المساعدة أدواتها من PyPI أو npm.

<details>
<summary>التفاصيل</summary>

- **يبقى على جهازك.** تعمل الخرائط والسياق والتعديلات والفحوصات داخل الملف التنفيذي لـSimplicio. ويسلّم النتائج إلى وكيلك على الجهاز نفسه. سجلات الاستخدام والتوفير ملفات محلية. ما يرسله وكيلك إلى مزوّد النموذج الخاص به يحدده الوكيل، كما كان من قبل.
- **إلى SimpleTI (simpleti.com.br).** فحوصات تسجيل الدخول والخطة فقط، دون أي محتوى للمستودع: لا ملفات، ولا مسارات ملفات، ولا تعليمات (prompts)، ولا تعديلات.
  - تحمل هذه الطلبات رمز تسجيل دخولك، وإصدار Simplicio، واسم المضيف في جهازك. ويحمل البحث الاختياري عن الترخيص بريد حسابك الإلكتروني أيضًا.
  - وتُعيد الخدمة بريد حسابك واسمك وخطتك.
- **إلى GitHub.** فحص في الخلفية لوجود إصدار جديد، مرة كل 12 ساعة تقريبًا على الأكثر، لا يحمل شيئًا عنك ولا عن كودك. اضبط `SIMPLICIO_DISABLE_AUTO_UPDATE=1` لإيقافه. وعند التحديث، يُنزَّل الملف التنفيذي من GitHub، ويُتحقَّق من SHA-256 وتوقيعه قبل أن يستبدل القديم.
- **لا تحليلات.** فُحص Simplicio 3.15.0 والملفات التي يثبّتها في وكلائك لهذا الغرض: لا يرفع أيٌّ منها تحليلات أو تقارير أعطال أو بيانات استخدام. ولا تشغّل الخطافات التي يثبّتها سوى برامج محلية (الملف التنفيذي لـSimplicio، وسكربتات محلية للإضافات الاختيارية)، ولا يتصل أيٌّ منها بالشبكة.
- **إلى الخدمات التي تُهيّئها.** يتلقى مزوّد النموذج أو GitHub أو Jira أو أداة إشعارات الدردشة أو ذاكرة التخزين المؤقت للفريق ما ترسله تلك الميزة، وقد يشمل ذلك التعليمات (prompts) والكود. وتحمل الطلبات إلى مزوّد النموذج ترويسة تسمّي Simplicio بوصفه العميل.
- **ميزتان تصلان إلى خدمة متاحة للعموم على الإنترنت دون أي إعداد.** ولا يرسل أيٌّ منهما محتوى الملفات.
  - البحث على الويب، عند تشغيله، يرسل استعلام البحث إلى DuckDuckGo ما لم تُهيّئ خدمة بحث أخرى. وفي دردشة Simplicio نفسها، قد تتحول رسالة تبدو كسؤال عن الويب إلى ذلك الاستعلام.
  - تدقيق أمان التبعيات، عند تشغيله، يرسل أسماء التبعيات وإصداراتها إلى osv.dev.
- **التنزيلات.** يُنزّل المثبّت ومسار التحديث الملفات من GitHub. وتجلب بعض السكربتات المساعدة الاختيارية أدواتها الخاصة من PyPI أو npm عند تشغيلها. وإذا لم تجد إضافة الوكيل الملف التنفيذي لـSimplicio، فإنها تنزّل المثبّت الرسمي من GitHub، مثبّتًا على commit محدّد، ويُتحقَّق منه عبر SHA-256.

**الإصدارات الموقّعة.** تنشر كل نسخة ملفاتها التنفيذية مع مجاميع التحقق SHA-256، وتوقيعات Ed25519، وSBOM (قائمة بما يدخل في البناء)، وإثبات مصدر البناء.

تتحقق المثبّتات ومسار التحديث من مجموع التحقق والتوقيع قبل أن تستبدل الملف التنفيذي المثبّت. وبالنسبة إلى الإصدارات المستقرة، يُعدّ غياب التوقيع أو عدم صلاحيته، وعدم تطابق مجموع التحقق، إخفاقات قاطعة. ويوجد العقد في [docs/UPDATE_SIGNATURE_CONTRACT.md](../docs/UPDATE_SIGNATURE_CONTRACT.md).

**ما الذي يغيّره المثبّت في وكيلك.**

- يضيف مدخل Simplicio إلى إعدادات MCP الخاصة بالوكيل، ويُبقي باقي الإعدادات كما هي.
- وفي Claude Code يسمح أيضًا بـ `mcp__simplicio__*`، حتى لا تُرفض أداة من Simplicio في الوضع التلقائي.
- وفي الوكلاء التي تحقق المثبّت من واجهة الخطافات الخاصة بها، يثبّت فيها خطافات Simplicio أيضًا.
- لا يلغي إلغاء التثبيت هذه المدخلات؛ ويشرح قسم التثبيت كيفية إزالتها. يوضح [INSTALL.md](../INSTALL.md) ما يكتبه المثبّت، وتعطي أدلة كل وكيل في [`docs/hosts/`](../docs/hosts/) التفاصيل.

</details>

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

- الأوامر والأدوات الموثّقة في README.md وMCP-CONNECT.md مرسومة في تدفق واحد، [docs/flow/simplicio.svg](../docs/flow/simplicio.svg)، يُولَّد من ملف مصدر واحد، `docs/flow/simplicio.flow.json`.
- لإعادة توليده شغّل `python3 scripts/generate_flow.py`، وللتحقق من انحرافه شغّل `python3 scripts/generate_flow.py --check`.
- العقد الذي يبقيه متّسقًا مع هذه الصفحة ومع MCP-CONNECT.md هو `python3 -m pytest tests/test_flow_contract.py -q`.
- فحص الاستيراد إلى Langflow هو `scripts/verify_flow_langflow.py`، ويفشل بشكل مغلق (يخرج بالقيمة 2 مع `status=blocked`) حين لا يعمل أي خادم. الأدلة موجودة تحت `docs/flow/evidence/` و`docs/flow/render/`، و[docs/flow/README.md](../docs/flow/README.md) يضم المتطلبات وطريقة تكرار الاختبار.

</details>

<a id="questions-people-ask"></a>

## أسئلة شائعة

**هل المقارنة عادلة؟**<br>
الوكيل نفسه، والنموذج نفسه، والتعليمات (prompts)، والمشروع، والفحوصات الخارجية؛ وخط الأساس بلا Simplicio. انظر [حيث لا يتفوّق Simplicio](#where-simplicio-does-not-win).

**هل عليّ تغيير وكيلي أو نموذجي؟**<br>
لا. يتصل Simplicio بالوكيل الذي تستخدمه أصلًا.

**هل سأحصل دائمًا على هذه الأرقام؟**<br>
لا. فهي تقيس مهمة واحدة، ونموذجًا واحدًا، وجهازًا واحدًا.

**هل هو مفتوح المصدر؟**<br>
لا. Simplicio برمجية خاصة: ملف تنفيذي موقّع. يحتوي هذا المستودع على المثبّتات والحزم والتوثيق والبيانات.

**كيف أزيله؟**<br>
شغّل `sh install.sh --uninstall --keep-data`، أو `pwsh install.ps1 -Uninstall -KeepData` على Windows. لا يعدّل الأمر إعدادات وكلائك، لذلك احذف مدخلات Simplicio من إعدادات كل وكيل.

**هل أحتاج إلى حساب؟**<br>
نعم. تسجيل الدخول عبر Google مطلوب، بما في ذلك خلال النسخة التجريبية. شغّل `simplicio auth login`.

**هل يغادر كودي جهازي؟**<br>
تعمل الخرائط والسياق والتعديلات والفحوصات على جهازك؛ ولا يتلقى SimpleTI وGitHub أي محتوى للمستودع. [التفاصيل](#safety-and-privacy).

<a id="documentation-and-community"></a>

## التوثيق والمجتمع

- **الموقع:** [simpleti.com.br/simplicio](https://simpleti.com.br/simplicio/)
- **التوثيق:** [simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)
- **Discord:** [انضم إلى المجتمع](https://discord.gg/wM6tr7xVb)
- **المشكلات:** [متتبّع المشكلات في GitHub](https://github.com/simpletibr/simplicio/issues)
- **ذو صلة:** Simplicio Video (hypit). لاستنساخه: `git clone https://github.com/hypit-ai/hypit.git simplicio-video`

<p align="center">
  <sub>© 2026 SimpleTI. Simplicio برمجية خاصة مسجّلة. جميع الحقوق محفوظة.</sub>
</p>
