# Building (maintainers)

Players don't need this. See [INSTALL.md](INSTALL.md).

## How the mod works
- **Text:** the game reads `translations.ini` from its RomFS. The installer writes the Arabic strings
  from `translation/arabic.json` into the `[spanish]` section of the user's own file.
- **Fonts:** the game renders text with Scribble 9.3.1, which already does Arabic joining
  (it maps letters to Unicode *Arabic Presentation Forms-B*) and right-to-left layout. The game's fonts just
  had no Arabic glyphs. The build renders those glyphs and adds them to four fonts in `game.win`:

  | font | used for | Arabic font |
  |---|---|---|
  | `fnt_default` | dialogue, UI | Noto Naskh Arabic 500 |
  | `fnt_default2`, `fnt_default3` | bold UI | Noto Naskh Arabic 700 |
  | `fnt_title` | big titles | Lalezar |

  Each font gets a new texture page (original atlas + Arabic glyphs) in the `default` texture group.
  Arabic glyphs share the Latin baseline. Their cells can be up to 20% taller than the Latin line height,
  because Scribble sizes each line from glyph heights.
- **Distribution:** only `patches/game.win.bsdiff` (about 1 MB) is published. The installer checks the
  SHA-256 of the user's `game.win` (v1.0.3) before and after patching.

## Requirements
- [uv](https://docs.astral.sh/uv/) (scripts declare their dependencies inline)
- [UndertaleModTool CLI](https://github.com/UnderminersTeam/UndertaleModTool/releases) 0.9.2 or newer (needs .NET)
- Your own base + v1.0.3 update NSPs and `prod.keys`

## Full rebuild
```
uv run tools/build.py --utmt C:\path\UndertaleModCli.exe    # finds the game like the installer (or pass NSP paths)
```
The build does the following:
1. Extracts `game.win` and `translations.ini` to `work/source`. `installer/switchfs.py` handles
   NSP → NCA → update patch (BKTR) → RomFS.
2. `tools/utmt/exportfonts.csx` exports the font atlases and glyph tables to `work/fonts`.
3. `tools/build_glyphs.py` renders the Arabic glyphs (HarfBuzz + FreeType) into `*_new.png/json`.
4. `tools/utmt/inject.csx` writes `work/game_ar.win`.
5. It writes `patches/game.win.bsdiff`, prints both SHA-256 values, and puts a test mod in `work/mod/`.

If the hashes change, update `GAME_WIN_SHA256` / `PATCHED_WIN_SHA256` in `installer/install.py`.

## Editing the translation
1. Edit `translation/arabic.json`, following `translation/TRANSLATION_GUIDE.md`.
2. Validate it against your own original file:
   `python tools/validate.py work/source/translations.ini`
3. If you add a character the fonts don't have, extend the glyph list in `tools/build_glyphs.py` and rebuild.
   Plain Arabic letters, Western digits and ، ؛ ؟ are already covered.

Preview how a string renders with the built atlases:
```
uv run tools/preview.py work fnt_default preview.png "كان يا ما كان"
```

## Release
```
uv run tools/build_release.py
```
This builds `dist/Arabic-iTzFaisal.exe` (PyInstaller one-file build, with the patch and text bundled inside) and
`dist/Arabic-iTzFaisal.zip` (the exe, readme and licenses) plus its `.sha256`.
Attach the zip to a GitHub release. Test it first by unzipping it to an empty folder and double-clicking it.
