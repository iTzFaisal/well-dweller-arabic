# /// script
# requires-python = ">=3.10"
# dependencies = ["pycryptodome>=3.20", "cryptography>=42", "bsdiff4>=1.2"]
# ///
"""Well Dweller Arabic translation - installer.

Builds the Eden/yuzu-style LayeredFS mod from YOUR OWN copy of the game:
the game files are never distributed, only a binary patch + the Arabic text.

Usage (any one of):
  uv run install.py                                  # auto: finds the NSPs next to this script / in the current folder
  uv run install.py BASE.nsp UPDATE.nsp              # explicit NSPs (order does not matter)
  uv run install.py --romfs "path/to/dumped/romfs"   # a RomFS dump made with Eden (Dump RomFS -> Full)
Options:
  --keys prod.keys      default: the emulator's keys (%APPDATA%/eden/keys/prod.keys)
  --out DIR             default: %APPDATA%/eden/load/0100217023F6C000/Arabic
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import translations  # noqa: E402

TITLE_ID = '0100217023F6C000'
UPDATE_ID = '0100217023F6C800'
GAME_VERSION = '1.0.3'
# SHA-256 of the v1.0.3 game.win and of the patched result
GAME_WIN_SHA256 = '711dc2c9543eade97b77ac93cd50709f28f5568bbf54ea08244f8c476ba48604'
PATCHED_WIN_SHA256 = 'f72ddc32515d39782fe06a8d4da5b54f3f836986bfbd92b48671370525ef9b8e'


def find_data(rel):
    for base in (HERE, HERE.parent):
        p = base / rel
        if p.exists():
            return p
    sys.exit(f'ERROR: data file "{rel}" not found next to the installer.')


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def eden_dir():
    appdata = os.environ.get('APPDATA')
    if appdata:
        return Path(appdata) / 'eden'
    return Path.home() / '.local' / 'share' / 'eden'


def classify_nsps(paths):
    """Return (base, update) by looking at the ticket names inside each NSP."""
    from switchfs import Pfs0
    base = upd = None
    for p in paths:
        names = ' '.join(Pfs0(p).files).lower()
        if UPDATE_ID.lower() in names:
            upd = p
        elif TITLE_ID.lower() in names:
            base = p
    return base, upd


def extract_from_nsps(base, update, keys_path, workdir):
    from switchfs import load_keys, open_patched_romfs
    print(f'Keys:   {keys_path}')
    print(f'Base:   {base}')
    print(f'Update: {update}')
    keys = load_keys(keys_path)
    if 'header_key' not in keys:
        sys.exit('ERROR: prod.keys has no header_key - use the keys dumped from your console.')
    romfs = open_patched_romfs(str(base), str(update), keys)
    for name in ('game.win', 'translations.ini'):
        print(f'Extracting {name} ...')
        romfs.extract(name, workdir / name)
    return workdir


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description='Install the Well Dweller Arabic translation (Eden LayeredFS mod).')
    ap.add_argument('nsps', nargs='*', help='base game NSP and v1.0.3 update NSP')
    ap.add_argument('--romfs', help='folder with an already dumped RomFS (contains game.win and translations.ini)')
    ap.add_argument('--keys', help='prod.keys (default: Eden keys)')
    ap.add_argument('--out', help='mod output folder (default: Eden load/<title id>/Arabic)')
    args = ap.parse_args()

    out = Path(args.out) if args.out else eden_dir() / 'load' / TITLE_ID / 'Arabic'

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        if args.romfs:
            src = Path(args.romfs)
        else:
            nsps = [Path(p) for p in args.nsps] or sorted({*HERE.glob('*.nsp'), *Path.cwd().glob('*.nsp')})
            base, upd = classify_nsps(nsps)
            if not base or not upd:
                sys.exit('ERROR: need both the base game NSP and the v1.0.3 update NSP '
                         f'(title {TITLE_ID} and {UPDATE_ID}).\n'
                         'Pass them as arguments, put them next to install.py, or use --romfs.')
            keys = Path(args.keys) if args.keys else eden_dir() / 'keys' / 'prod.keys'
            if not keys.exists():
                sys.exit(f'ERROR: prod.keys not found at {keys} (use --keys).')
            src = extract_from_nsps(base, upd, keys, tmp)

        win, ini = src / 'game.win', src / 'translations.ini'
        for p in (win, ini):
            if not p.exists():
                sys.exit(f'ERROR: {p} not found.')

        print('Checking game version ...')
        if sha256_file(win) != GAME_WIN_SHA256:
            sys.exit(f'ERROR: game.win does not match Well Dweller v{GAME_VERSION}. '
                     'Make sure the v1.0.3 update is used.')

        import bsdiff4
        print('Patching game.win (Arabic fonts) ...')
        new_win = bsdiff4.patch(win.read_bytes(), find_data('patches/game.win.bsdiff').read_bytes())
        if hashlib.sha256(new_win).hexdigest() != PATCHED_WIN_SHA256:
            sys.exit('ERROR: patched game.win failed verification.')

        print('Writing Arabic text into translations.ini ...')
        arabic = json.loads(find_data('translation/arabic.json').read_text(encoding='utf-8'))
        new_ini = translations.apply_arabic(ini.read_bytes(), arabic)

        dst = out / 'romfs'
        dst.mkdir(parents=True, exist_ok=True)
        (dst / 'game.win').write_bytes(new_win)
        (dst / 'translations.ini').write_bytes(new_ini)

    print()
    print(f'Done! Mod installed to: {out}')
    print('In Eden: right-click Well Dweller > Properties > Add-Ons and make sure "Arabic" is checked')
    print('(the v1.0.3 update must also be installed). In game: Options > Language > العربية')


if __name__ == '__main__':
    main()
