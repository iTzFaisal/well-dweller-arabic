# /// script
# requires-python = ">=3.10"
# dependencies = ["pycryptodome>=3.20", "cryptography>=42", "bsdiff4>=1.2", "pillow", "uharfbuzz", "freetype-py"]
# ///
"""Full maintainer build: game files -> modded game.win -> patches/game.win.bsdiff.

  uv run tools/build.py --utmt path/to/UndertaleModCli.exe BASE.nsp UPDATE.nsp [--keys prod.keys]
  uv run tools/build.py --utmt path/to/UndertaleModCli.exe --romfs path/to/romfs

Steps: extract game.win + translations.ini -> export font atlases (UTMT) -> render Arabic glyphs
-> inject into game.win (UTMT) -> bsdiff patch + SHA-256 values for installer/install.py.
Everything goes to ./work (git-ignored). Also writes work/mod/romfs/ ready to copy into Eden.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'installer'))
import install  # noqa: E402
import translations  # noqa: E402


def run(cmd, **kw):
    print('>', ' '.join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def utmt(cli, src, script, out=None, env=None):
    cmd = [cli, 'load', src, '-s', script]
    if out:
        cmd += ['-o', out, '-f']
    run(cmd, env=env)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('nsps', nargs='*')
    ap.add_argument('--romfs')
    ap.add_argument('--keys')
    ap.add_argument('--utmt', required=True, help='UndertaleModCli executable (UndertaleModTool CLI >= 0.9.2)')
    ap.add_argument('--work', default=str(REPO / 'work'))
    args = ap.parse_args()

    work = Path(args.work).resolve()
    src = work / 'source'
    src.mkdir(parents=True, exist_ok=True)
    if args.romfs:
        for n in ('game.win', 'translations.ini'):
            shutil.copy(Path(args.romfs) / n, src / n)
    else:
        base, upd = install.classify_nsps([Path(p) for p in args.nsps])
        keys = Path(args.keys) if args.keys else install.eden_dir() / 'keys' / 'prod.keys'
        install.extract_from_nsps(base, upd, keys, src)

    win = src / 'game.win'
    if install.sha256_file(win) != install.GAME_WIN_SHA256:
        print('WARNING: source game.win differs from the expected v1.0.3 - update GAME_WIN_SHA256 if intended')

    env = dict(os.environ, WD_WORK=str(work))
    utmt(args.utmt, win, REPO / 'tools/utmt/exportfonts.csx', env=env)
    run([sys.executable, REPO / 'tools/build_glyphs.py', work])
    modded = work / 'game_ar.win'
    utmt(args.utmt, win, REPO / 'tools/utmt/inject.csx', out=modded, env=env)

    import bsdiff4
    print('Creating patch ...')
    patch = bsdiff4.diff(win.read_bytes(), modded.read_bytes())
    (REPO / 'patches').mkdir(exist_ok=True)
    (REPO / 'patches/game.win.bsdiff').write_bytes(patch)

    arabic = json.loads((REPO / 'translation/arabic.json').read_text(encoding='utf-8'))
    mod = work / 'mod/romfs'
    mod.mkdir(parents=True, exist_ok=True)
    shutil.copy(modded, mod / 'game.win')
    (mod / 'translations.ini').write_bytes(translations.apply_arabic((src / 'translations.ini').read_bytes(), arabic))

    h_src, h_out = install.sha256_file(win), install.sha256_file(modded)
    print(f'\npatch: {len(patch)} bytes')
    print(f"GAME_WIN_SHA256 = '{h_src}'")
    print(f"PATCHED_WIN_SHA256 = '{h_out}'")
    if (h_src, h_out) != (install.GAME_WIN_SHA256, install.PATCHED_WIN_SHA256):
        print('NOTE: hashes differ from installer/install.py - update them there before releasing.')
    print(f'Mod folder for testing: {mod.parent}')


if __name__ == '__main__':
    main()
