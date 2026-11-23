// Inject Arabic glyph atlases into fonts: new texture page per font, new TPAG, extended glyph table.
using System.IO;
using System.Linq;
using System.Text.Json;
using UndertaleModLib.Util;

var dir = Path.Combine(Environment.GetEnvironmentVariable("WD_WORK") ?? throw new Exception("set WD_WORK to the work folder"), "fonts");
var log = new System.Text.StringBuilder();
var tg = Data.TextureGroupInfo.First(x => x.Name.Content == "default");

foreach (var name in new[] { "fnt_default", "fnt_default2", "fnt_default3", "fnt_title" })
{
    var font = Data.Fonts.ByName(name);
    var oldPage = font.Texture.TexturePage;
    using var doc = JsonDocument.Parse(File.ReadAllText(Path.Combine(dir, name + "_new.json")));
    var root = doc.RootElement;
    int pw = root.GetProperty("page")[0].GetInt32(), ph = root.GetProperty("page")[1].GetInt32();

    var tex = new UndertaleEmbeddedTexture();
    tex.Name = new UndertaleString("Texture " + Data.EmbeddedTextures.Count);
    tex.Scaled = oldPage.Scaled;
    tex.GeneratedMips = oldPage.GeneratedMips;
    tex.TextureData.Image = GMImage.FromPng(File.ReadAllBytes(Path.Combine(dir, name + "_new.png")));
    tex.TextureWidth = pw;
    tex.TextureHeight = ph;
    tex.IndexInGroup = tg.TexturePages.Count;
    Data.EmbeddedTextures.Add(tex);
    var res = new UndertaleResourceById<UndertaleEmbeddedTexture, UndertaleChunkTXTR>();
    res.Resource = tex;
    tg.TexturePages.Add(res);

    var tp = new UndertaleTexturePageItem();
    tp.Name = new UndertaleString("PageItem " + Data.TexturePageItems.Count);
    tp.SourceX = 0; tp.SourceY = 0; tp.SourceWidth = (ushort)pw; tp.SourceHeight = (ushort)ph;
    tp.TargetX = 0; tp.TargetY = 0; tp.TargetWidth = (ushort)pw; tp.TargetHeight = (ushort)ph;
    tp.BoundingWidth = (ushort)pw; tp.BoundingHeight = (ushort)ph;
    tp.TexturePage = tex;
    Data.TexturePageItems.Add(tp);

    var old = font.Glyphs.ToDictionary(g => (int)g.Character);
    var list = new List<UndertaleFont.Glyph>();
    foreach (var e in root.GetProperty("glyphs").EnumerateArray())
    {
        int cp = e[0].GetInt32();
        UndertaleFont.Glyph g;
        if (old.TryGetValue(cp, out var og)) g = og;   // original glyph: coordinates unchanged (atlas copied to 0,0)
        else g = new UndertaleFont.Glyph();
        g.Character = (ushort)cp;
        g.SourceX = (ushort)e[1].GetInt32(); g.SourceY = (ushort)e[2].GetInt32();
        g.SourceWidth = (ushort)e[3].GetInt32(); g.SourceHeight = (ushort)e[4].GetInt32();
        g.Shift = (short)e[5].GetInt32(); g.Offset = (short)e[6].GetInt32();
        list.Add(g);
    }
    font.Glyphs.Clear();
    foreach (var g in list.OrderBy(g => g.Character)) font.Glyphs.Add(g);
    font.Texture = tp;
    font.RangeEnd = Math.Max(font.RangeEnd, (uint)list.Max(g => g.Character));
    log.AppendLine($"{name}: page {pw}x{ph} tex#{Data.EmbeddedTextures.Count - 1} glyphs {font.Glyphs.Count} rangeEnd {font.RangeEnd} (old page scaled={oldPage.Scaled} mips={oldPage.GeneratedMips} idx={oldPage.IndexInGroup} w={oldPage.TextureWidth})");
}
File.WriteAllText(Path.Combine(dir, "inject_log.txt"), log.ToString());
