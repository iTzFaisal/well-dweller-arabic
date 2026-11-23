"""Write the Arabic text into the game's translations.ini (it replaces the [spanish] section)."""
import re

TARGET_SECTION = 'spanish'


def parse_sections(text):
    secs, cur = {}, None
    for ln in text.splitlines():
        m = re.match(r'^\[(\w+)\]\s*$', ln)
        if m:
            cur = m.group(1)
            secs[cur] = {}
        elif cur and '=' in ln:
            k, v = ln.split('=', 1)
            if k.strip():
                secs[cur][k.strip()] = v
    return secs


def apply_arabic(src_bytes, arabic):
    """Return new translations.ini bytes, with the [spanish] values replaced by `arabic` (key -> text)."""
    bom = src_bytes.startswith(b'\xef\xbb\xbf')
    text = src_bytes.decode('utf-8-sig')
    nl = '\r\n' if '\r\n' in text else '\n'
    out, sec, seen = [], None, set()

    def close_target():
        trail = []
        while out and out[-1].strip() == '':
            trail.append(out.pop())
        out.extend(f'{k}={v}' for k, v in arabic.items() if k and k not in seen)
        out.extend(trail)

    for ln in text.split(nl):
        m = re.match(r'^\[(\w+)\]\s*$', ln)
        if m:
            if sec == TARGET_SECTION:
                close_target()
            sec = m.group(1)
            out.append(ln)
            continue
        if sec == TARGET_SECTION and '=' in ln:
            k, _ = ln.split('=', 1)
            if k.strip() in arabic:
                seen.add(k.strip())
                out.append(f'{k}={arabic[k.strip()]}')
                continue
        out.append(ln)
    if sec == TARGET_SECTION:
        close_target()
    if not seen:
        raise ValueError(f'[{TARGET_SECTION}] section not found in translations.ini')
    data = nl.join(out).encode('utf-8')
    return (b'\xef\xbb\xbf' if bom else b'') + data
