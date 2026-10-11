svg_eagle = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 240" width="200" height="240">
  <defs>
    <radialGradient id="shieldGrad" cx="50%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#ffeaa7"/>
      <stop offset="70%" stop-color="#fdcb6e"/>
      <stop offset="100%" stop-color="#e17055"/>
    </radialGradient>
    <filter id="goldGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#fdcb6e" flood-opacity="0.6"/>
    </filter>
  </defs>
  <!-- Gold Shield -->
  <path d="M 20 20 L 180 20 C 180 140 140 210 100 230 C 60 210 20 140 20 20 Z" 
        fill="url(#shieldGrad)" stroke="#ffeaa7" stroke-width="6" filter="url(#goldGlow)"/>
  <!-- German Federal Eagle Silhouette -->
  <g fill="#2d3436" transform="translate(100, 110) scale(0.68)">
    <!-- Head & Beak -->
    <path d="M 0 -85 C -15 -85 -25 -70 -25 -55 C -25 -45 -18 -38 -15 -35 L -35 -40 L -18 -25 C -15 -15 0 -10 0 -10 C 0 -10 15 -15 18 -25 L 35 -40 L 15 -35 C 18 -38 25 -45 25 -55 C 25 -70 15 -85 0 -85 Z"/>
    <circle cx="-10" cy="-62" r="4" fill="#d63031"/>
    <!-- Wings Left -->
    <path d="M -15 -25 C -55 -45 -100 -20 -115 45 C -105 25 -80 15 -75 35 C -65 15 -45 15 -35 45 C -25 25 -10 15 -5 35 Z"/>
    <!-- Wings Right -->
    <path d="M 15 -25 C 55 -45 100 -20 115 45 C 105 25 80 15 75 35 C 65 15 45 15 35 45 C 25 25 10 15 5 35 Z"/>
    <!-- Body & Feathers -->
    <path d="M -18 -15 C -25 20 -20 50 -10 75 L 0 85 L 10 75 C 20 50 25 20 18 -15 Z"/>
    <!-- Tail -->
    <path d="M -25 80 L -35 110 L -15 100 L 0 120 L 15 100 L 35 110 L 25 80 Z"/>
    <!-- Talons (Claws) Red -->
    <path d="M -30 65 L -45 80 L -30 75 L -40 90 L -20 80 Z" fill="#d63031"/>
    <path d="M 30 65 L 45 80 L 30 75 L 40 90 L 20 80 Z" fill="#d63031"/>
  </g>
</svg>'''

with open('C:/Users/DELL/geo_shorts_factory/assets/emblem_de.svg', 'w', encoding='utf-8') as f:
    f.write(svg_eagle)

print("emblem_de.svg created successfully!")
