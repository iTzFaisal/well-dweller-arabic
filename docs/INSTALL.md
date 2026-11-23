# Arabic-iTzFaisal — تعريب لعبة Well Dweller

## العربية

تعريب كامل للعبة **Well Dweller** على محاكي **Eden**. يظهر التعريب في قائمة اللغات باسم **العربية** بدلاً من الإسبانية.

### المتطلبات
- اللعبة مضافة إلى Eden وتعمل، **مع تحديث 1.0.3**.
- مفاتيح جهازك (`prod.keys`) مثبتة في Eden كالمعتاد.

### التثبيت
1. حمّل `Arabic-iTzFaisal.zip` وفك الضغط.
2. شغّل `Arabic-iTzFaisal.exe` بنقرة مزدوجة.
   سيعثر البرنامج تلقائياً على Eden وعلى اللعبة، ثم يثبّت التعريب خلال ثوانٍ.
3. في Eden: انقر بزر الفأرة الأيمن على اللعبة ← Properties ← Add-Ons، وتأكد أن **Arabic-iTzFaisal** مفعّل.
4. داخل اللعبة: الخيارات ← اللغة ← **العربية**.

> لماذا برنامج تثبيت وليس مجلداً جاهزاً؟ لأن ملفات اللعبة محمية بحقوق النشر ولا يجوز توزيعها.
> البرنامج لا يحتوي على أي ملف من ملفات اللعبة، بل يبني التعريب من نسختك أنت.

إذا لم يعثر البرنامج على اللعبة، ضع ملفي الـ NSP (اللعبة الأساسية والتحديث) بجانب البرنامج وشغّله مرة أخرى،
أو اسحب الملفين وأفلتهما فوقه.

---

## English

Full Arabic translation of **Well Dweller** for the **Eden** emulator. It appears as **العربية** in the
language menu, replacing Spanish.

### Requirements
- The game added to Eden and working, **with update 1.0.3**.
- Your console keys (`prod.keys`) set up in Eden as usual.

### Install
1. Download `Arabic-iTzFaisal.zip` and extract it.
2. Double-click `Arabic-iTzFaisal.exe`. It finds Eden and your game automatically and installs the mod in a few seconds.
3. In Eden: right-click the game → Properties → Add-Ons → make sure **Arabic-iTzFaisal** is checked.
4. In game: Options → Language → **العربية**.

> **Why an installer and not a ready-made mod folder?** The game's files are copyrighted and can't be
> redistributed. The program contains no game files; it builds the mod from your own copy.

If the game isn't found, put the base and update NSPs next to the program (or drag them onto it) and run it again.

### Where it looks
- Eden's user folder: `%APPDATA%\eden`, or a portable `user` folder next to the program. Other yuzu-family
  emulators (Citron, Sudachi, Suyu, Torzu, yuzu) are also detected.
- Your game: Eden's game folders, games installed into Eden's NAND, and NSPs next to the program.

### Uninstall
Untick **Arabic-iTzFaisal** under Add-Ons, or delete `%APPDATA%\eden\load\0100217023F6C000\Arabic-iTzFaisal`.

### Troubleshooting
| Message | Fix |
|---|---|
| update v1.0.3 was not found | Install the 1.0.3 update in Eden (File → Install Files to NAND), or put the update NSP next to the program |
| base game was not found | Add the game folder in Eden, or put the NSP next to the program |
| Could not find Eden | Start Eden once with your keys installed |
| titlekek_xx missing | Your keys are older than the game; dump newer keys from your console |

Linux / macOS: run the script from the source code: `uv run installer/install.py`.
