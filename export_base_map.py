from playwright.sync_api import sync_playwright

# Render the world map at 3000x3000 and save as a high-res image
html_content = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 0; background: #08101e; overflow: hidden; width: 3000px; height: 3000px; }
  .country { fill: #22334a; stroke: #4d6685; stroke-width: 2.2px; stroke-linejoin: round; }
  .map-label { font-size: 32px; font-weight: 800; fill: #8ca3be; font-family: sans-serif; text-anchor: middle; }
</style>
<script src="assets/d3.min.js"></script>
<script src="assets/countries_data.js"></script>
</head>
<body>
<svg id="svg" width="3000" height="3000" viewBox="0 0 3000 3000">
  <g id="countries"></g>
  <g id="labels"></g>
</svg>
<script>
  const projection = d3.geoMercator().scale(475).translate([1500, 1500]);
  const pathGen = d3.geoPath().projection(projection);
  d3.select('#countries').selectAll('path')
    .data(geoData.features)
    .enter()
    .append('path')
    .attr('class', 'country')
    .attr('d', pathGen);

  const labelData = [
    { name: "CHINA", coords: [104, 35] },
    { name: "KOREA", coords: [127.7, 36.5] },
    { name: "RUSSIA", coords: [95, 60] },
    { name: "FRANCE", coords: [2.2, 46.2] },
    { name: "POLAND", coords: [19.1, 51.9] },
    { name: "UNITED KINGDOM", coords: [-3.4, 55.3] },
    { name: "ITALY", coords: [12.5, 41.8] },
    { name: "INDIA", coords: [78.9, 20.5] }
  ];
  labelData.forEach(l => {
    const pt = projection(l.coords);
    if(pt) {
      d3.select('#labels').append('text')
        .attr('class', 'map-label')
        .attr('x', pt[0])
        .attr('y', pt[1])
        .text(l.name);
    }
  });
</script>
</body>
</html>
"""

with open("C:/Users/DELL/geo_shorts_factory/render_base_map.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Taking high-res 3000x3000 snapshot of world map...")
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 3000, "height": 3000})
    page.goto("file:///C:/Users/DELL/geo_shorts_factory/render_base_map.html")
    page.wait_for_timeout(1000)
    page.screenshot(path="C:/Users/DELL/geo_shorts_factory/assets/world_base_3000.png")
    browser.close()

print("High-res world map snapshot saved to assets/world_base_3000.png!")
