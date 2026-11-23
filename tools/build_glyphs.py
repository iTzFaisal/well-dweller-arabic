# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "uharfbuzz", "freetype-py"]
# ///
"""Render Arabic presentation-form glyphs into new GameMaker font atlases.

usage: build_glyphs.py <workdir> [font ...]
  input : <workdir>/fonts/<font>.json + <font>_page.png   (exported with tools/utmt/exportfonts.csx)
  output: <workdir>/fonts/<font>_new.png + <font>_new.json (full glyph list incl. originals)
"""
import json, re, sys, os, math
import uharfbuzz as hb
import freetype
from PIL import Image, ImageChops

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(sys.argv[1], 'fonts')
EXT = os.path.join(REPO, 'fonts')

# ---- 1. presentation forms used by Scribble 9.3.1 -------------------------------------
gml = open(os.path.join(REPO, 'tools', 'third_party', 'scribble_glyphdata.gml'), encoding='utf-8').read()
FORM = {'i': 'iso', 'c': 'fin', 'b': 'med', 'a': 'ini'}
targets = {}  # codepoint -> (base_text, form)
for m in re.finditer(r'_map_([icba])\[\?\s*0x([0-9A-Fa-f]+)\]\s*=\s*0x([0-9A-Fa-f]+)', gml):
    form, base, pf = FORM[m.group(1)], int(m.group(2), 16), int(m.group(3), 16)
    if pf not in targets or targets[pf][1] == 'iso':
        targets.setdefault(pf, (chr(base), form))
# lam-alef ligatures (Scribble replaces lam+alef with these, then joins final/isolated)
LAMALEF = {0xFEF5: 'آ', 0xFEF7: 'أ', 0xFEF9: 'إ', 0xFEFB: 'ا'}
for iso, alef in LAMALEF.items():
    targets[iso] = ('ل' + alef, 'iso')
    targets[iso + 1] = ('ل' + alef, 'fin')
# punctuation + plain letters as fallback (isolated)
for cp in [0x060C, 0x061B, 0x061F] + list(range(0x0621, 0x063B)) + list(range(0x0641, 0x064B)):
    targets.setdefault(cp, (chr(cp), 'iso'))
print('glyphs to render:', len(targets))

ZWJ = '‍'
GROW = 1.2  # Arabic glyph cells may be up to 20% taller than the Latin line height
def ctx(text, form):
    return {'iso': text, 'ini': text + ZWJ, 'med': ZWJ + text + ZWJ, 'fin': ZWJ + text}[form]

# ---- 2. per-font config -----------------------------------------------------------------
CFG = {
    'fnt_default':  dict(ttf='NotoNaskhArabic.ttf', wght=500),
    'fnt_default3': dict(ttf='NotoNaskhArabic.ttf', wght=700),
    'fnt_default2': dict(ttf='NotoNaskhArabic.ttf', wght=700),
    'fnt_title':    dict(ttf='Lalezar-Regular.ttf', wght=None, pagew=4096),
}
if os.environ.get('TITLE_TTF'):
    CFG['fnt_title'] = dict(ttf=os.environ['TITLE_TTF'], wght=int(os.environ.get('TITLE_WGHT', 0)) or None)

class Renderer:
    def __init__(self, path, wght, px):
        self.px = px
        blob = hb.Blob.from_file_path(path)
        self.face = hb.Face(blob)
        self.font = hb.Font(self.face)
        upem = self.face.upem
        self.font.scale = (int(px * 64), int(px * 64))
        self.ft = freetype.Face(path)
        self.ft.set_char_size(int(px * 64))
        if wght:
            self.font.set_variations({'wght': wght})
            axes = self.ft.get_variation_info().axes
            self.ft.set_var_design_coords([wght if a.tag == 'wght' else a.default for a in axes])

    def shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {'kern': True, 'liga': True})
        glyphs = []
        x = 0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            ch = text[info.cluster] if info.cluster < len(text) else ''
            if ch == ZWJ:
                continue
            glyphs.append((info.codepoint, x + pos.x_offset, pos.y_offset))
            x += pos.x_advance
        return glyphs, x  # positions in 26.6, RTL buffer => visual order left->right

    def render(self, text):
        glyphs, adv = self.shape(text)
        layers = []
        for gid, x, y in glyphs:
            self.ft.load_glyph(gid, freetype.FT_LOAD_DEFAULT | freetype.FT_LOAD_NO_HINTING | freetype.FT_LOAD_TARGET_LIGHT)
            # sub-pixel x placement
            self.ft.glyph.render(freetype.FT_RENDER_MODE_NORMAL)
            bm = self.ft.glyph.bitmap
            if bm.width == 0 or bm.rows == 0:
                continue
            img = Image.frombytes('L', (bm.width, bm.rows), bytes(bm.buffer)) if bm.pitch == bm.width else \
                Image.frombytes('L', (bm.width, bm.rows), bytes(b for r in range(bm.rows) for b in bm.buffer[r * bm.pitch: r * bm.pitch + bm.width]))
            left = round(x / 64) + self.ft.glyph.bitmap_left
            top = self.ft.glyph.bitmap_top + round(y / 64)  # above baseline
            layers.append((img, left, top))
        return layers, adv / 64

def ink_extents(r):
    asc = desc = 0
    for t in targets.values():
        layers, _ = r.render(ctx(*t))
        for img, left, top in layers:
            asc = max(asc, top); desc = max(desc, img.height - top)
    return asc, desc

def build(name):
    meta = json.load(open(os.path.join(FD, name + '.json')))
    page = Image.open(os.path.join(FD, name + '_page.png')).convert('RGBA')
    sx, sy, sw, sh = meta['src']
    orig = page.crop((sx, sy, sx + sw, sy + sh))
    used_h = orig.getchannel('A').getbbox()[3]
    glyphs = meta['glyphs']
    G = {g[0]: g for g in glyphs}
    cellh = G[ord('H')][4]
    # baseline & cap height from 'H'
    H = G[ord('H')]
    hb_ = orig.crop((H[1], H[2], H[1] + H[3], H[2] + H[4])).getchannel('A').getbbox()
    base = hb_[3]; cap = hb_[3] - hb_[1]
    cfg = CFG[name]
    path = os.path.join(EXT, cfg['ttf'])
    # size: alef height ~= 1.08 * cap height, clamped so ink fits the cell
    probe = Renderer(path, cfg['wght'], 100)
    alef = probe.render('ا')[0][0]
    alef_h = alef[2] / 100.0  # top above baseline per px
    px = 1.08 * cap / alef_h
    a, d = ink_extents(Renderer(path, cfg['wght'], px))
    fit = min(1.0, (base - 1) / a, (GROW * cellh - base - 1) / d)
    px *= fit
    r = Renderer(path, cfg['wght'], px)
    a, d = ink_extents(r)
    latin_cellh = cellh
    cellh = max(cellh, base + d + 1)
    print(f'{name}: cell={latin_cellh}->{cellh} baseline={base} cap={cap} -> arabic px={px:.1f} (fit {fit:.2f}) asc/desc={a}/{d}')

    # render all glyph cells
    cells = []
    for cp, t in sorted(targets.items()):
        layers, adv = r.render(ctx(*t))
        if not layers:
            continue
        minx = min(l for _, l, _ in layers); maxx = max(l + i.width for i, l, _ in layers)
        w = maxx - minx
        cell = Image.new('L', (w, cellh), 0)
        for img, left, top in layers:
            y = base - top
            # clip into cell
            layer = Image.new('L', cell.size, 0)
            layer.paste(img, (left - minx, y))
            cell = ImageChops.lighter(cell, layer)
        joining = t[1] in ('ini', 'med')
        shift = math.floor(adv + 0.5)
        offset = minx
        cells.append((cp, cell, shift, offset))

    # pack below the original atlas
    W = CFG[name].get('pagew', sw)
    pad = 2
    x, y = pad, used_h + pad
    placed = []
    for cp, cell, shift, offset in cells:
        if x + cell.width + pad > W:
            x = pad; y += cellh + pad
        placed.append((cp, x, y, cell, shift, offset))
        x += cell.width + pad
    total_h = y + cellh + pad
    PH = 1 << math.ceil(math.log2(max(total_h, sh)))
    PW = 1 << math.ceil(math.log2(W))
    new = Image.new('RGBA', (PW, PH), (255, 255, 255, 0))
    new.paste(orig, (0, 0))
    white = Image.new('RGBA', (1, 1), (255, 255, 255, 255))
    for cp, gx, gy, cell, shift, offset in placed:
        rgba = Image.new('RGBA', cell.size, (255, 255, 255, 0))
        rgba.putalpha(cell)
        new.paste(rgba, (gx, gy))
    new.save(os.path.join(FD, name + '_new.png'))
    newglyphs = [g[:7] for g in glyphs] + [[cp, gx, gy, cell.width, cellh, shift, offset] for cp, gx, gy, cell, shift, offset in placed]
    newglyphs.sort(key=lambda g: g[0])
    json.dump({'name': name, 'page': [PW, PH], 'glyphs': newglyphs}, open(os.path.join(FD, name + '_new.json'), 'w'))
    print(f'   page {PW}x{PH}, added {len(placed)} glyphs, total {len(newglyphs)}')
    return r, placed, base, cellh

def preview(name, r, text, base, cellh):
    """Simulate Scribble: logical text -> presentation forms -> reversed visual order."""
    meta = json.load(open(os.path.join(FD, name + '_new.json')))
    G = {g[0]: g for g in meta['glyphs']}
    page = Image.open(os.path.join(FD, name + '_new.png'))
    return G, page

if __name__ == '__main__':
    for n in (sys.argv[2:] or CFG):
        build(n)
