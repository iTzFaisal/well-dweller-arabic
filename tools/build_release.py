"""Package the user-facing release zip into dist/.

  python tools/build_release.py [version]

The zip contains only original work: installer, Arabic text, binary patch, font licenses, docs.
No game data is included - users build the mod from their own copy of the game.
"""
import hashlib
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FILES = [
    ('installer/install.py', 'install.py'),
    ('installer/install.bat', 'install.bat'),
    ('installer/switchfs.py', 'switchfs.py'),
    ('installer/translations.py', 'translations.py'),
    ('patches/game.win.bsdiff', 'patches/game.win.bsdiff'),
    ('translation/arabic.json', 'translation/arabic.json'),
    ('docs/INSTALL.md', 'README.md'),
    ('LICENSE', 'LICENSE.txt'),
    ('fonts/OFL-naskh.txt', 'licenses/NotoNaskhArabic-OFL.txt'),
    ('fonts/OFL-lalezar.txt', 'licenses/Lalezar-OFL.txt'),
    ('tools/third_party/LICENSE-Scribble.txt', 'licenses/Scribble-MIT.txt'),
]


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else 'dev'
    dist = REPO / 'dist'
    dist.mkdir(exist_ok=True)
    out = dist / f'WellDweller-Arabic-{version}.zip'
    root = f'WellDweller-Arabic-{version}/'
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for src, dst in FILES:
            z.write(REPO / src, root + dst)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    (dist / (out.name + '.sha256')).write_text(f'{digest}  {out.name}\n')
    print(f'{out}  ({out.stat().st_size} bytes)\nsha256 {digest}')


if __name__ == '__main__':
    main()
