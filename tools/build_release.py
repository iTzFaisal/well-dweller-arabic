"""Build the user-facing release: dist/Arabic-iTzFaisal.zip

  uv run tools/build_release.py

Creates a single-file Windows program (PyInstaller) that contains the installer, the Arabic text and
the font patch, then zips it with the readme and licenses. No game data is included - the program
builds the mod from the user's own copy of the game.
"""
import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NAME = 'Arabic-iTzFaisal'
EXTRAS = [
    ('docs/INSTALL.md', 'README.md'),
    ('LICENSE', 'LICENSE.txt'),
    ('fonts/OFL-naskh.txt', 'licenses/NotoNaskhArabic-OFL.txt'),
    ('fonts/OFL-lalezar.txt', 'licenses/Lalezar-OFL.txt'),
    ('tools/third_party/LICENSE-Scribble.txt', 'licenses/Scribble-MIT.txt'),
]


def main():
    work = REPO / 'work' / 'pyinstaller'
    sep = ';' if sys.platform == 'win32' else ':'
    cmd = [
        'uv', 'run', '--with', 'pyinstaller', '--with', 'pycryptodome', '--with', 'cryptography',
        '--with', 'bsdiff4', '--', 'pyinstaller', '--noconfirm', '--onefile', '--console',
        '--name', NAME,
        '--paths', str(REPO / 'installer'),
        '--add-data', f'{REPO / "patches/game.win.bsdiff"}{sep}patches',
        '--add-data', f'{REPO / "translation/arabic.json"}{sep}translation',
        '--distpath', str(work / 'dist'), '--workpath', str(work / 'build'), '--specpath', str(work),
        str(REPO / 'installer/install.py'),
    ]
    print('>', ' '.join(cmd))
    subprocess.run(cmd, check=True, cwd=REPO)
    exe = work / 'dist' / (NAME + ('.exe' if sys.platform == 'win32' else ''))

    dist = REPO / 'dist'
    dist.mkdir(exist_ok=True)
    out = dist / f'{NAME}.zip'
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(exe, f'{NAME}/{exe.name}')
        for src, dst in EXTRAS:
            z.write(REPO / src, f'{NAME}/{dst}')
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    (dist / f'{out.name}.sha256').write_text(f'{digest}  {out.name}\n')
    shutil.copy(exe, dist / exe.name)
    print(f'\n{out} ({out.stat().st_size // 1024} KB)\nsha256 {digest}')


if __name__ == '__main__':
    main()
