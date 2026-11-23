"""Check translation/arabic.json against the English text of your own translations.ini.

  python tools/validate.py path/to/original/translations.ini [translation/arabic.json]

Checks: every English key is translated, [tags] / $ / @ / ~ counts match the English,
no tashkeel / tatweel / Arabic-Indic digits, only characters the mod's fonts contain.
"""
import collections
import io
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'installer'))
from translations import parse_sections  # noqa: E402

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ALLOWED = set(' .,!?:;-+/()"\'%$@~[]،؛؟0123456789')
BAD = re.compile('[ً-ْـ٠-٩]')
TAG = re.compile(r'\[[^\]]*\]')


def main():
    ini = Path(sys.argv[1])
    ar_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent / 'translation/arabic.json'
    en = parse_sections(ini.read_bytes().decode('utf-8-sig'))['english']
    ar = json.loads(ar_path.read_text(encoding='utf-8'))
    probs = []
    for k, e in en.items():
        if k not in ar:
            probs.append(f'{k}: missing')
            continue
        a = ar[k]
        if collections.Counter(TAG.findall(e)) != collections.Counter(TAG.findall(a)):
            probs.append(f'{k}: tags differ')
        for ch in '$@~':
            if e.count(ch) != a.count(ch):
                probs.append(f'{k}: count of {ch!r} differs (en={e.count(ch)} ar={a.count(ch)})')
        plain = TAG.sub('', a)
        if BAD.search(plain):
            probs.append(f'{k}: tashkeel / tatweel / Arabic-Indic digits')
        bad = {c for c in plain if not ('ء' <= c <= 'ي') and c not in ALLOWED}
        if bad:
            probs.append(f'{k}: unsupported characters {sorted(bad)}')
        if e.strip() and not a.strip():
            probs.append(f'{k}: empty')
    extra = set(ar) - set(en)
    if extra:
        probs.append(f'keys not in the game: {sorted(extra)}')
    print('\n'.join(probs) if probs else f'OK: {len(en)} entries')
    sys.exit(1 if probs else 0)


if __name__ == '__main__':
    main()
