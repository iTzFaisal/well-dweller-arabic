# Well Dweller — Arabic translation / تعريب لعبة ساكن البئر

## العربية

تعريب كامل للعبة **Well Dweller** (نسخة Nintendo Switch) يعمل على محاكي **Eden** (ويُفترض أن يعمل أيضاً على المحاكيات المشابهة مثل yuzu وsudachi وCitron).
التعريب يحل محل اللغة **الإسبانية** في قائمة اللغات.

### المتطلبات
- نسختك الأصلية من اللعبة: ملف اللعبة الأساسي (Base) **وتحديث 1.0.3** بصيغة NSP.
- ملف المفاتيح `prod.keys` المستخرج من جهازك (نفس الملف الذي يستخدمه المحاكي).
- برنامج [uv](https://docs.astral.sh/uv/getting-started/installation/) لتشغيل المثبت.

> لا يحتوي هذا التعريب على أي ملفات من اللعبة. المثبت يبني التعريب من نسختك أنت.

### التثبيت
1. ثبّت تحديث اللعبة 1.0.3 في المحاكي.
2. انقل ملفي الـ NSP (الأساسي والتحديث) إلى مجلد التعريب، ثم شغّل `install.bat`.
   (أو اسحب الملفين وأفلتهما فوق `install.bat`).
3. في Eden: انقر بزر الفأرة الأيمن على اللعبة ← Properties ← Add-Ons وتأكد من تفعيل **Arabic**.
4. داخل اللعبة: الخيارات ← اللغة ← **العربية**.

---

## English

Full Arabic translation of **Well Dweller** (Nintendo Switch) for the **Eden** emulator (should also work on
yuzu-based emulators such as sudachi and Citron). It replaces **Spanish** in the language menu.

### Requirements
- Your own copy of the game: the **base NSP and the v1.0.3 update NSP**.
- `prod.keys` dumped from your console (the same file your emulator uses).
- [uv](https://docs.astral.sh/uv/getting-started/installation/) to run the installer.

> No game files are included. The installer builds the mod from your own copy.

### Install
1. Install the v1.0.3 update in the emulator.
2. Put the base and update NSPs in this folder and double-click `install.bat`
   (or drag both NSPs onto `install.bat`).
3. In Eden: right-click the game → Properties → Add-Ons → make sure **Arabic** is checked.
4. In game: Options → Language → **العربية**.

### Other options
```
uv run install.py BASE.nsp UPDATE.nsp --keys path\to\prod.keys
uv run install.py --romfs path\to\romfs          # RomFS dumped with Eden: right-click > Dump RomFS > Full
uv run install.py ... --out path\to\mod\folder   # other emulators: <load dir>\0100217023F6C000\Arabic
```
On Linux/macOS run `uv run install.py ...` directly; the default output is `~/.local/share/eden/load/...`.

### Uninstall
Delete `%APPDATA%\eden\load\0100217023F6C000\Arabic`, or untick it under Add-Ons.

### Troubleshooting
- *"game.win does not match Well Dweller v1.0.3"*: the mod requires update **1.0.3** exactly.
- *"titlekek_xx missing"*: your `prod.keys` is older than the game; dump newer keys from your console.
