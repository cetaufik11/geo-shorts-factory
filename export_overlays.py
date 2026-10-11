from playwright.sync_api import sync_playwright

def export_overlay(is_jp, out_path):
    cls = "hl-jp" if is_jp else "hl-de"
    feat_name = "jpFeature" if is_jp else "deFeature"
    html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; width: 3000px; height: 3000px; }}
  .hl-jp {{ fill: #ff4757; stroke: #ffffff; stroke-width: 5px; filter: drop-shadow(0 0 35px #ff4757) drop-shadow(0 0 15px #ff6b81); }}
  .hl-de {{ fill: #2ed573; stroke: #ffffff; stroke-width: 5px; filter: drop-shadow(0 0 35px #2ed573) drop-shadow(0 0 15px #7bed9f); }}
</style>
<script src="assets/d3.min.js"></script>
<script src="assets/jp_de_features.js"></script>
</head>
<body>
<svg width="3000" height="3000" viewBox="0 0 3000 3000">
  <path id="target" class="{cls}"></path>
</svg>
<script>
  const projection = d3.geoMercator().scale(475).translate([1500, 1500]);
  const pathGen = d3.geoPath().projection(projection);
  d3.select('#target').attr('d', pathGen({feat_name}));
</script>
</body>
</html>"""
    with open("C:/Users/DELL/geo_shorts_factory/temp_overlay.html", "w", encoding="utf-8") as f:
        f.write(html)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 3000, "height": 3000})
        pg.goto("file:///C:/Users/DELL/geo_shorts_factory/temp_overlay.html")
        pg.wait_for_timeout(500)
        pg.screenshot(path=out_path, omit_background=True)
        b.close()

export_overlay(True, "C:/Users/DELL/geo_shorts_factory/assets/overlay_jp.png")
export_overlay(False, "C:/Users/DELL/geo_shorts_factory/assets/overlay_de.png")
print("Overlays exported successfully!")
