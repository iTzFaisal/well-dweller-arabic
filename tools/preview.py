# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""Simulate Scribble 9.3.1 Arabic shaping + render with the generated GM font atlas.
usage: preview.py <workdir> <font> <out.png> <line> [<line> ...]
"""
import json, re, sys, os
from PIL import Image

WORK, FONT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lines = sys.argv[4:]
gml = open(os.path.join(REPO, 'tools', 'third_party', 'scribble_glyphdata.gml'), encoding='utf-8').read()
maps = {k: {} for k in 'icba'}
for m in re.finditer(r'_map_([icba])\[\?\s*0x([0-9A-Fa-f]+)\]\s*=\s*0x([0-9A-Fa-f]+)', gml):
    maps[m.group(1)][int(m.group(2), 16)] = int(m.group(3), 16)
iso, fin, med, ini = maps['i'], maps['c'], maps['b'], maps['a']
join_prev = {g: ini.get(g) != med.get(g) for g in iso}
join_next = {g: ini.get(g) != iso.get(g) for g in iso}
LA = {0x0622: 0xFEF5, 0x0623: 0xFEF7, 0x0625: 0xFEF9, 0x0627: 0xFEFB}

def shape(s):
    cps = [ord(c) for c in s]
    out = []; prev_join = False; i = 0
    while i < len(cps):
        g = cps[i]; joiner = g
        if 0x0600 <= g <= 0x06FF:
            nxt = cps[i + 1] if i + 1 < len(cps) else 0
            if g == 0x0644 and nxt in LA:
                g = joiner = LA[nxt]; i += 1
                nxt = cps[i + 1] if i + 1 < len(cps) else 0
            if prev_join:
                ng = med.get(g) if join_prev.get(nxt) else fin.get(g)
            else:
                ng = ini.get(g) if join_prev.get(nxt) else iso.get(g)
            if ng is not None: g = ng
            prev_join = join_next.get(joiner, False)
        else:
            prev_join = False
        out.append(g); i += 1
    return out

meta = json.load(open(os.path.join(WORK, 'fonts', FONT + '_new.json')))
G = {g[0]: g for g in meta['glyphs']}
page = Image.open(os.path.join(WORK, 'fonts', FONT + '_new.png'))
lh = max(g[4] for g in meta['glyphs'])
W = 1400
img = Image.new('RGBA', (W, lh * len(lines) + 20), (40, 30, 50, 255))
for li, s in enumerate(lines):
    vis = list(reversed(shape(s)))  # pure RTL line
    vis = [{0x28: 0x29, 0x29: 0x28}.get(c, c) for c in vis]
    # width
    total = sum(G.get(c, G[32])[5] for c in vis)
    x = W - 10 - total; y = 10 + li * lh
    for c in vis:
        g = G.get(c)
        if g is None:
            print('MISSING', hex(c)); g = G[ord('?')]
        cp, gx, gy, w, h, shift, off = g
        if w and h:
            gl = page.crop((gx, gy, gx + w, gy + h))
            img.alpha_composite(gl, (x + off, y))
        x += shift
img.save(OUT)
