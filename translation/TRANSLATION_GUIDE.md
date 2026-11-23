# Well Dweller → Arabic translation guide

Game: "Well Dweller" (ساكن البئر), a dark-fairytale 2D platformer. You play Glimmer, a small bird
who leaves the family nest (inside a skull at the bottom of a well) to find food and later
rescue siblings, while an evil Queen hunts birds for their feathers. Tone: storybook narration,
whimsical/cute dialogue, sometimes creepy. Use clear, natural Modern Standard Arabic (فصحى مبسطة),
warm and readable for all ages. Keep UI strings short (they must fit small menu boxes).

## Workflow
`arabic.json` maps each key in the game's `translations.ini` to its Arabic text. Translate from the
`[english]` section of your own copy of the file. The official `[spanish]` section is useful for context.
Keep the file UTF-8, with every key present. After editing, run
`python tools/validate.py <your original translations.ini>`.

## HARD formatting rules (a validator will check these)
1. Keep every `[...]` tag EXACTLY as written (e.g. `[delay]`, `[shake]`, `[/shake]`, `[wave]`, `[/wave]`,
   `[pulse]`, `[c_white]`, `[c_red]`, `[c_yellow]`, `[s_currency_spark]`, `[switch_song,mu_campfire]`,
   `[change_skel,o_looternpc,idle]`, `[snd_...]`, `[swap_image,0]`, etc.). Never translate or alter text
   inside brackets. Same count of each tag as English. Opening/closing pairs (`[wave]...[/wave]`) must wrap
   the corresponding Arabic words. Event/sound tags (`[delay]`, `[snd_...]`, `[change_skel...]`,
   `[swap_image,N]`, `[switch_song...]`, `[stop_song]`) should stay at the equivalent position in the sentence.
2. `$` and `@` are runtime placeholders (button icons, numbers, item names). Keep the SAME NUMBER of `$`
   and `@` as English. Never add or remove them. (In a few lines `$` is used as a quotation mark: keep it.)
   `$%` means "number percent": write it as `$%`.
3. `~` is a line break, `~~` is a paragraph break. Keep the same number of `~` characters.
4. Do NOT use Arabic diacritics/tashkeel (no َ ً ُ ٌ ِ ٍ ّ ْ). Do NOT use tatweel (ـ).
5. Use Western digits 0-9 (not ٠١٢). Arabic punctuation ، ؛ ؟ is allowed and preferred. Use `!` and `...` normally.
   For quotations use plain ASCII double quotes "like this" (no « », no curly quotes).
6. No Latin words except where English has a literal key name like SPACE / JUMP in a control hint
   (translate those too: JUMP = القفز, SPACE = مفتاح المسافة). Do not leave English in the output.
7. Only use Arabic letters, spaces, digits, and these symbols: . , ! ? : ; - + / ( ) " ' % $ @ ~ [ ] ، ؛ ؟
8. Empty English value → empty Arabic value. "..." stays "...".
9. Stutter/emphasis (e.g. "LoVe", "HELP!!!") → render the feeling naturally in Arabic (e.g. repetition, "!!!").

## Glossary (use consistently)
| English | Arabic |
|---|---|
| Well Dweller (game title) | ساكن البئر |
| Glimmer | غليمر |
| Egbert | إغبرت |
| Mother Bird | أم العصافير |
| Mom / Mother | أمي / الأم |
| brother (how siblings address Glimmer) | أخي |
| Thistle / Thimble / Thistle and Thimble | شوكة / كشتبان / شوكة وكشتبان |
| Magda, Irma, Ilda, Lida | ماغدا، إرما، إلدا، ليدا |
| Looter | نشال |
| The Dollmaker / Dollmaker | صانع الدمى |
| Barge | بارج |
| Squinton | سكوينتون |
| Announcer | المنادي |
| Ticketer | بائع التذاكر |
| Whisper | همس |
| Willow | صفصافة |
| the Queen / Queen | الملكة |
| the King | الملك |
| little bird (how adults call Glimmer) | أيها العصفور الصغير / يا عصفوري الصغير |
| hunter(s) | الصياد / الصيادون |
| Trinket(s) | تعويذة / تعويذات |
| Trinket Slot(s) | خانة تعويذة / خانات التعويذات |
| Spirit(s) / Spirit Fragment | روح / أرواح / شظية روح |
| Page(s) (story pages) | صفحة / صفحات |
| Token(s) / Workshop Token | قطعة / قطع / قطعة الورشة |
| Ticket | تذكرة |
| Flaming Vessel | القارورة المشتعلة |
| Additional Vessel | قارورة إضافية |
| Oil Vial | قنينة زيت |
| Ember Vial | قنينة الجمر |
| Matchstick / match | عود الثقاب |
| Water Vessel | المركبة المائية |
| Torpedo | طوربيد |
| Golden Gate Key | مفتاح البوابة الذهبية |
| Golden Feather | الريشة الذهبية |
| Elevator Part | قطعة المصعد |
| tent / save tent | الخيمة / خيمة الحفظ |
| Tent Travel | التنقل بين الخيام |
| Map / Marker / Major Markers | الخريطة / علامة / العلامات الرئيسية |
| Challenge / Time Trial / Deathmatch | تحدٍ→ اكتبها "تحدي" / سباق مع الزمن / نزال حتى الموت |
| Boss Rush | تحدي الزعماء |
| Speedrun Mode | وضع السباق السريع |
| slide / slingshot / climb / hover / soar / wind ride / wall sling / endless climb | انزلاق / المقلاع / التسلق / التحليق / الانطلاق / ركوب الرياح / القذف من الجدار / التسلق اللانهائي |
| heal / healing | الشفاء / التعافي |
| Night Garden(s) | حديقة الليل |
| Queen's Castle | قلعة الملكة |
| Hunter's Cabin | كوخ الصياد |
| Lookout Tower | برج المراقبة |
| Dollmaker's House | بيت صانع الدمى |
| The Bog | المستنقع |
| GravenValley | وادي القبور |
| Midnight Drench | سيل منتصف الليل |
| Autumn Forest | غابة الخريف |
| Burial Vault | سرداب الدفن |
| The Drains | المجاري |
| Desiccated Castle | القلعة اليابسة |
| The Docks | المرفأ |
| Webdrench Inn | نزل الشباك المبللة |
| The Deep | الأعماق |
| The Well | البئر |
| Seven Sons | الأبناء السبعة |
| witch | ساحرة |
| post box / mail / letter | صندوق البريد / البريد / رسالة |

UI words: Start=ابدأ, Options=الخيارات, Exit=خروج, Back=رجوع, Continue=متابعة, Resume=استئناف,
Easy/Normal/Hard=سهل/عادي/صعب, ON/OFF=تشغيل/إيقاف, YES/NO=نعم/لا, Controller=وحدة التحكم,
Keyboard/Mouse=لوحة المفاتيح/الفأرة, Graphics=الرسومات, Gameplay=اللعب, Audio=الصوت, Assist=المساعدة,
Language=اللغة, Quality=الجودة, Low=منخفضة, Difficulty=الصعوبة, Save Game=حفظ اللعبة, Game Saved=تم حفظ اللعبة,
Press $ = اضغط $, Hold $ = اضغط مطولا على $ (or: استمر بالضغط على $).
