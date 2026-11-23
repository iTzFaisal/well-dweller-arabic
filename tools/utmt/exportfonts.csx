// Export each target font's atlas region + glyph table as JSON for the Python builder
using System.IO;
using System.Linq;
using System.Text.Json;
var outDir = Path.Combine(Environment.GetEnvironmentVariable("WD_WORK") ?? throw new Exception("set WD_WORK to the work folder"), "fonts");
Directory.CreateDirectory(outDir);
foreach (var name in new[] { "fnt_default", "fnt_default2", "fnt_default3", "fnt_title" })
{
    var f = Data.Fonts.ByName(name);
    var t = f.Texture;
    using (var fs = File.Create(Path.Combine(outDir, name + "_page.png")))
        t.TexturePage.TextureData.Image.SavePng(fs);
    var meta = new Dictionary<string, object> {
        ["name"] = name, ["emSize"] = f.EmSize, ["ascender"] = f.Ascender, ["ascenderOffset"] = f.AscenderOffset,
        ["lineHeight"] = f.LineHeight, ["rangeStart"] = f.RangeStart, ["rangeEnd"] = f.RangeEnd,
        ["src"] = new[] { (int)t.SourceX, (int)t.SourceY, (int)t.SourceWidth, (int)t.SourceHeight },
        ["glyphs"] = f.Glyphs.Select(g => new[] { (int)g.Character, (int)g.SourceX, (int)g.SourceY, (int)g.SourceWidth, (int)g.SourceHeight, (int)g.Shift, (int)g.Offset, g.Kerning.Count }).ToList()
    };
    File.WriteAllText(Path.Combine(outDir, name + ".json"), JsonSerializer.Serialize(meta));
}
