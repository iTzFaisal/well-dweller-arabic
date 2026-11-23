# Well Dweller — Arabic Translation / تعريب ساكن البئر

A fan Arabic translation of **Well Dweller** (Nintendo Switch, v1.0.3) for the Eden emulator.
It replaces Spanish in the game's language menu with full Arabic. Letters join correctly, text runs
right-to-left, and the fonts are made for Arabic.

تعريب كامل للعبة **Well Dweller** على محاكي Eden، يحل محل اللغة الإسبانية في قائمة اللغات.

**[Download the latest release](../../releases/latest)**, then follow the [installation guide](docs/INSTALL.md) / [دليل التثبيت](docs/INSTALL.md#العربية).

> This repository contains **no game files**. The installer builds the mod from your own legally
> obtained copy of the game (base + v1.0.3 update) and your own console keys.

## What's included
| | |
|---|---|
| `translation/arabic.json` | The Arabic text: 1,493 lines covering dialogue, menus, items and story pages |
| `patches/game.win.bsdiff` | Binary patch that adds Arabic glyphs to the game's fonts |
| `installer/` | Installer that extracts your files, verifies v1.0.3, patches and installs the mod |
| `tools/` | Maintainer build pipeline (font rendering, UndertaleModTool scripts, validation, release) |
| `fonts/` | Noto Naskh Arabic and Lalezar (SIL OFL 1.1) |
| `docs/` | [INSTALL.md](docs/INSTALL.md), [BUILDING.md](docs/BUILDING.md) |

## Project layout
```
installer/      install.py, install.bat, switchfs.py (NSP/NCA/RomFS reader), translations.py
patches/        game.win.bsdiff
translation/    arabic.json, TRANSLATION_GUIDE.md
tools/          build.py, build_glyphs.py, preview.py, validate.py, build_release.py, utmt/*.csx, third_party/
fonts/          Arabic fonts + licenses
docs/           INSTALL.md, BUILDING.md
```

## Known limitations
- Requires game update **1.0.3** exactly.
- Text drawn into the artwork, such as the title logo, stays in English.
- The translation was machine-assisted. Corrections are welcome through issues or pull requests to `translation/arabic.json`.

## License
Scripts, installer, translation and patch: MIT (see [LICENSE](LICENSE)). Fonts: SIL OFL 1.1.
Well Dweller belongs to its respective owners. This is an unofficial fan project, not affiliated with
the developer, the publisher, or Nintendo.
