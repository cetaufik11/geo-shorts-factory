with open('C:/Users/DELL/geo_shorts_factory/assets/map_jp.svg', 'r', encoding='utf-8') as f:
    jp = f.read().replace('fill="#000000"', 'fill="#ff4757"')
with open('C:/Users/DELL/geo_shorts_factory/assets/map_jp_neon.svg', 'w', encoding='utf-8') as f:
    f.write(jp)

with open('C:/Users/DELL/geo_shorts_factory/assets/map_de.svg', 'r', encoding='utf-8') as f:
    de = f.read().replace('fill="#000000"', 'fill="#ffa502"')
with open('C:/Users/DELL/geo_shorts_factory/assets/map_de_neon.svg', 'w', encoding='utf-8') as f:
    f.write(de)

print("Neon maps created successfully!")
