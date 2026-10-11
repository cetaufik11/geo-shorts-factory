import os
import sys
import subprocess
import shutil
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

base = "C:/Users/DELL/geo_shorts_factory"
assets_dir = os.path.join(base, "assets")

print("Loading base map and overlay assets...")
# Load 3000x3000 textures
base_map = cv2.imread(os.path.join(assets_dir, "world_base_3000.png"))
overlay_jp_raw = cv2.imread(os.path.join(assets_dir, "overlay_jp.png"), cv2.IMREAD_UNCHANGED)
overlay_de_raw = cv2.imread(os.path.join(assets_dir, "overlay_de.png"), cv2.IMREAD_UNCHANGED)

# Pre-composite highlight maps for ultra-fast rendering
map_with_jp = base_map.copy()
if overlay_jp_raw is not None:
    alpha_jp = overlay_jp_raw[:, :, 3] / 255.0
    for c in range(3):
        map_with_jp[:, :, c] = (1 - alpha_jp) * map_with_jp[:, :, c] + alpha_jp * overlay_jp_raw[:, :, c]

map_with_de = base_map.copy()
if overlay_de_raw is not None:
    alpha_de = overlay_de_raw[:, :, 3] / 255.0
    for c in range(3):
        map_with_de[:, :, c] = (1 - alpha_de) * map_with_de[:, :, c] + alpha_de * overlay_de_raw[:, :, c]

map_with_both = base_map.copy()
if overlay_jp_raw is not None:
    alpha_jp = overlay_jp_raw[:, :, 3] / 255.0
    for c in range(3):
        map_with_both[:, :, c] = (1 - alpha_jp) * map_with_both[:, :, c] + alpha_jp * overlay_jp_raw[:, :, c]
if overlay_de_raw is not None:
    alpha_de = overlay_de_raw[:, :, 3] / 255.0
    for c in range(3):
        map_with_both[:, :, c] = (1 - alpha_de) * map_with_both[:, :, c] + alpha_de * overlay_de_raw[:, :, c]

# Preload flags
flag_jp = Image.open(os.path.join(assets_dir, "flag_japan.png")).resize((140, 92))
flag_de = Image.open(os.path.join(assets_dir, "flag_germany.png")).resize((140, 92))

# Load Windows Fonts
font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 52)
font_badge = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 28)
font_stat_lbl = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 32)
font_stat_val = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 76)
font_sub = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 46)
font_top = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 36)
font_pin = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 24)

# Coordinates on 3000x3000 map:
# Tokyo (Japan): (2658.2, 1182.8)
# Berlin (Germany): (1611.1, 986.8)
# Eurasia Overview: (2134.2, 1091.8)
pos_overview = (2134.2, 1091.8, 0.72)
pos_jp = (2658.2, 1182.8, 1.95)
pos_de = (1611.1, 986.8, 2.05)

# Smooth easing function (Quintic smoothstep: zero jerk, silky smooth)
def smooth_ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * t * (t * (t * 6 - 15) + 10)

def interpolate_camera(c1, c2, t, arc_lift=0.0):
    e = smooth_ease(t)
    x = c1[0] + (c2[0] - c1[0]) * e
    y = c1[1] + (c2[1] - c1[1]) * e
    s = c1[2] + (c2[2] - c1[2]) * e
    if arc_lift > 0.0:
        s -= arc_lift * np.sin(e * np.pi)
    return x, y, max(0.4, s)

# Timeline Waypoints:
# (time_sec, camera_target, active_country, hud_data)
# hud_data: (flag, name, badge, stat_lbl, stat_val, bar_ratio, is_winner, sub_text, top_badge)
def get_state(sec):
    # 0.0s - 4.63s: EXPLOSIVE OPENING HOOK (Hook Choreography)
    if sec < 1.40:
        # Phase 1 (0.0 - 1.4s): Instant crash-dive into Japan!
        t_dive = min(1.0, sec / 0.85)
        cam_start = (2520.0, 1140.0, 1.15)
        cam = interpolate_camera(cam_start, pos_jp, t_dive)
        return cam, "JP", (flag_jp, "JAPAN 🇯🇵", "CONTENDER #1", "East Asia Powerhouse", "GDP $4.2T", 0.85, False, "Which country gives you...", "🔥 WHO HAS A BETTER LIFE? 🔥")

    elif sec < 2.80:
        # Phase 2 (1.4 - 2.8s): High-speed transcontinental swoop across Eurasia to Germany!
        t_flight = min(1.0, (sec - 1.40) / 1.30)
        cam = interpolate_camera(pos_jp, pos_de, t_flight, arc_lift=0.35)
        act = "DE" if t_flight > 0.35 else "JP"
        return cam, act, (flag_de, "GERMANY 🇩🇪", "CONTENDER #2", "European Giant", "GDP $4.5T", 0.90, False, "...a BETTER life?", "🔥 WHO HAS A BETTER LIFE? 🔥")

    elif sec < 4.63:
        # Phase 3 (2.8 - 4.63s): Smooth zoom-out to Eurasian Duel Arena (Both countries glowing!)
        t_out = min(1.0, (sec - 2.80) / 1.40)
        cam = interpolate_camera(pos_de, pos_overview, t_out)
        return cam, "BOTH", (flag_jp, "JAPAN vs GERMANY", "THE DUEL", "Quality of Life Faceoff", "⚔️ VS ⚔️", 1.0, False, "Let's compare the real data!", "⚔️ BATTLE OF THE TITANS ⚔️")

    # 4.63 - 7.43s: Fly to Japan (Salary)
    elif sec < 7.43:
        t_flight = min(1.0, (sec - 4.63) / 1.5)
        cam = interpolate_camera(pos_overview, pos_jp, t_flight, arc_lift=0.25)
        c_prog = min(1.0, (sec - 4.63) / 1.8)
        val = int(c_prog * 3200)
        return cam, "JP", (flag_jp, "JAPAN 🇯🇵", "MONTHLY NET", "Average Income", f"${val:,}", c_prog * 0.71, False, "Japan averages thirty-two hundred dollars!", "💰 ROUND 1: SALARY 💰")

    # 7.43 - 12.77s: Fly to Germany (Salary Winner)
    elif sec < 12.77:
        t_flight = min(1.0, (sec - 7.43) / 1.6)
        cam = interpolate_camera(pos_jp, pos_de, t_flight, arc_lift=0.35)
        c_prog = min(1.0, (sec - 7.43) / 1.8)
        val = int(c_prog * 4500)
        is_win = (sec - 7.43) > 1.0
        return cam, "DE", (flag_de, "GERMANY 🇩🇪", "🏆 WINNER" if is_win else "MONTHLY NET", "Average Income", f"${val:,}", c_prog * 1.0, is_win, "Germany takes the lead with $4,500!", "💰 ROUND 1: SALARY 💰")

    # 12.77 - 15.77s: Fly to Japan (Work-Life)
    elif sec < 15.77:
        t_flight = min(1.0, (sec - 12.77) / 1.6)
        cam = interpolate_camera(pos_de, pos_jp, t_flight, arc_lift=0.35)
        c_prog = min(1.0, (sec - 12.77) / 1.8)
        val = int(c_prog * 1607)
        return cam, "JP", (flag_jp, "JAPAN 🇯🇵", "ANNUAL WORKLOAD", "Working Hours", f"{val:,} hrs", c_prog * 1.0, False, "Japan clocks in over 1,600 hours a year!", "⏰ ROUND 2: WORK-LIFE ⏰")

    # 15.77 - 22.06s: Fly to Germany (Work-Life Winner)
    elif sec < 22.06:
        t_flight = min(1.0, (sec - 15.77) / 1.6)
        cam = interpolate_camera(pos_jp, pos_de, t_flight, arc_lift=0.35)
        c_prog = min(1.0, (sec - 15.77) / 1.8)
        val = int(c_prog * 1341)
        is_win = (sec - 15.77) > 1.0
        return cam, "DE", (flag_de, "GERMANY 🇩🇪", "🏆 WINNER" if is_win else "ANNUAL WORKLOAD", "Working Hours", f"{val:,} hrs", c_prog * 0.83, is_win, "Germans work 260 fewer hours per year!", "⏰ ROUND 2: WORK-LIFE ⏰")

    # 22.06 - 24.66s: Stay Germany (Safety)
    elif sec < 24.66:
        cam = pos_de
        c_prog = min(1.0, (sec - 22.06) / 1.5)
        val = int(c_prog * 20)
        return cam, "DE", (flag_de, "GERMANY 🇩🇪", "GLOBAL RANK", "Safety Index", f"#{val}", c_prog * 0.65, False, "Germany ranks #20 in global safety!", "🛡️ ROUND 3: SAFETY 🛡️")

    # 24.66 - 29.91s: Fly to Japan (Safety Winner)
    elif sec < 29.91:
        t_flight = min(1.0, (sec - 24.66) / 1.6)
        cam = interpolate_camera(pos_de, pos_jp, t_flight, arc_lift=0.35)
        c_prog = min(1.0, (sec - 24.66) / 1.8)
        val = int(c_prog * 9)
        is_win = (sec - 24.66) > 1.0
        return cam, "JP", (flag_jp, "JAPAN 🇯🇵", "🏆 WINNER" if is_win else "GLOBAL RANK", "Safety Index", f"#{val}", c_prog * 0.95, is_win, "Japan destroys Germany with ultra-low crime rate!", "🛡️ ROUND 3: SAFETY 🛡️")

    # 29.91s+: Final Overview & Call to Action
    else:
        t_flight = min(1.0, (sec - 29.91) / 1.8)
        cam = interpolate_camera(pos_jp, pos_overview, t_flight, arc_lift=0.25)
        return cam, "BOTH", (flag_jp, "WHICH ONE?", "VOTE BELOW", "A: Japan vs B: Germany", "YOUR CHOICE", 0.5, False, "Which country are you picking? Comment below!", "🔥 FINAL VERDICT 🔥")

# Launch FFmpeg output process directly
final_out = os.path.join(base, "Japan_vs_Germany_MAP_FLIGHT.mp4")
master_audio = os.path.join(base, "audio/master_soundtrack.wav")

cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", "1080x1920",
    "-pix_fmt", "bgr24",
    "-r", "30",
    "-i", "-",
    "-i", master_audio,
    "-map", "0:v",
    "-map", "1:a",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-t", "35.25",
    final_out
]

print("Launching FFmpeg direct pipe process (30.00 CFR constant frame rate)...")
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

FPS = 30
TOTAL_FRAMES = int(35.25 * FPS)
print(f"Rendering {TOTAL_FRAMES} mathematically perfect frames with dynamic intro hook...")

tokyo_pt = (int(2658.2), int(1182.8))
berlin_pt = (int(1611.1), int(986.8))

for frame_idx in range(TOTAL_FRAMES):
    sec = frame_idx / FPS
    cam, active_country, (flag, name, badge, stat_lbl, stat_val, bar_ratio, is_winner, sub_text, top_badge) = get_state(sec)
    
    # Select texture
    if active_country == "JP":
        current_map = map_with_jp
    elif active_country == "DE":
        current_map = map_with_de
    elif active_country == "BOTH":
        current_map = map_with_both
    else:
        current_map = base_map

    # Camera affine transform
    cx, cy, scale = cam
    M = np.float32([
        [scale, 0, 540 - cx * scale],
        [0, scale, 750 - cy * scale]
    ])
    
    # Bilinear subpixel transform (100% smooth, 0 dropped frames)
    frame_bgr = cv2.warpAffine(current_map, M, (1080, 1920), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(8, 16, 30))
    
    # Transform Tokyo & Berlin to screen
    t_screen = (int(tokyo_pt[0] * scale + (540 - cx * scale)), int(tokyo_pt[1] * scale + (750 - cy * scale)))
    b_screen = (int(berlin_pt[0] * scale + (540 - cx * scale)), int(berlin_pt[1] * scale + (750 - cy * scale)))
    
    # Draw Flight Arc between Tokyo and Berlin
    mid_ctrl = ((t_screen[0] + b_screen[0]) // 2, min(t_screen[1], b_screen[1]) - int(150 * scale))
    curve_pts = []
    for t_step in np.linspace(0, 1, 20):
        px = (1 - t_step)**2 * t_screen[0] + 2 * (1 - t_step) * t_step * mid_ctrl[0] + t_step**2 * b_screen[0]
        py = (1 - t_step)**2 * t_screen[1] + 2 * (1 - t_step) * t_step * mid_ctrl[1] + t_step**2 * b_screen[1]
        curve_pts.append([int(px), int(py)])
    cv2.polylines(frame_bgr, [np.array(curve_pts, dtype=np.int32)], isClosed=False, color=(42, 211, 255), thickness=3, lineType=cv2.LINE_AA)
    
    # Dynamic traveling laser pulse along flight arc
    t_pulse = (sec * 0.7) % 1.0
    px = (1 - t_pulse)**2 * t_screen[0] + 2 * (1 - t_pulse) * t_pulse * mid_ctrl[0] + t_pulse**2 * b_screen[0]
    py = (1 - t_pulse)**2 * t_screen[1] + 2 * (1 - t_pulse) * t_pulse * mid_ctrl[1] + t_pulse**2 * b_screen[1]
    cv2.circle(frame_bgr, (int(px), int(py)), 7, (255, 255, 255), -1, cv2.LINE_AA)
    cv2.circle(frame_bgr, (int(px), int(py)), 14, (42, 211, 255), 2, cv2.LINE_AA)

    # Beacons with pulse animation
    t_ring = int(3 * np.sin(sec * 10))
    cv2.circle(frame_bgr, t_screen, int(11 * min(2.0, scale)), (87, 71, 255), -1, cv2.LINE_AA) # Tokyo Red
    cv2.circle(frame_bgr, t_screen, int(18 * min(2.0, scale)) + t_ring, (87, 71, 255), 2, cv2.LINE_AA)
    
    b_ring = int(3 * np.cos(sec * 10))
    cv2.circle(frame_bgr, b_screen, int(11 * min(2.0, scale)), (2, 165, 255), -1, cv2.LINE_AA) # Berlin Yellow
    cv2.circle(frame_bgr, b_screen, int(18 * min(2.0, scale)) + b_ring, (2, 165, 255), 2, cv2.LINE_AA)

    # Convert to PIL for crisp typography & HUD overlays
    img_pil = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    # 1. Top Category Pill
    top_w, top_h = 660, 76
    top_x = (1080 - top_w) // 2
    draw.rounded_rectangle([top_x, 90, top_x + top_w, 90 + top_h], radius=38, fill=(255, 71, 87), outline=(255, 255, 255), width=3)
    draw.text((540, 128), top_badge, font=font_top, fill=(255, 255, 255), anchor="mm")

    # 2. Floating HUD Panel (y=1160 to 1640)
    hud_bg = (18, 38, 28) if is_winner else (10, 18, 32)
    hud_border = (46, 213, 115) if is_winner else (80, 110, 150)
    
    if is_winner:
        draw.rounded_rectangle([54, 1154, 1026, 1646], radius=44, fill=(25, 60, 40))
    draw.rounded_rectangle([60, 1160, 1020, 1640], radius=40, fill=hud_bg, outline=hud_border, width=4)

    if active_country == "BOTH":
        # Duel Layout with Both Flags
        img_pil.paste(flag_jp, (110, 1205))
        img_pil.paste(flag_de, (830, 1205))
        draw.text((540, 1220), name, font=font_title, fill=(255, 255, 255), anchor="mt")
        draw.rounded_rectangle([440, 1285, 640, 1330], radius=14, fill=(60, 85, 115))
        draw.text((540, 1307), badge, font=font_badge, fill=(220, 230, 245), anchor="mm")
        
        # Stat Label & Value
        draw.text((110, 1380), stat_lbl, font=font_stat_lbl, fill=(150, 170, 195))
        draw.text((960, 1400), stat_val, font=font_stat_val, fill=(255, 211, 42), anchor="rm")

        # Progress Bar: Split Duel Color
        bar_w = 850
        bar_x, bar_y = 110, 1520
        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 22], radius=11, fill=(35, 50, 70))
        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w // 2, bar_y + 22], radius=11, fill=(255, 71, 87))
        draw.rounded_rectangle([bar_x + bar_w // 2, bar_y, bar_x + bar_w, bar_y + 22], radius=11, fill=(46, 213, 115))
    else:
        # Single Country Layout
        if isinstance(flag, Image.Image):
            img_pil.paste(flag, (110, 1205))
        
        # Title & Badge
        draw.text((280, 1220), name, font=font_title, fill=(255, 255, 255))
        badge_bg = (46, 213, 115) if is_winner else (60, 85, 115)
        badge_fg = (5, 15, 10) if is_winner else (220, 230, 245)
        draw.rounded_rectangle([720, 1220, 960, 1270], radius=16, fill=badge_bg)
        draw.text((840, 1245), badge, font=font_badge, fill=badge_fg, anchor="mm")

        # Stat Label & Value
        draw.text((110, 1370), stat_lbl, font=font_stat_lbl, fill=(150, 170, 195))
        val_fg = (46, 213, 115) if is_winner else (255, 255, 255)
        draw.text((960, 1400), stat_val, font=font_stat_val, fill=val_fg, anchor="rm")

        # Progress Bar
        bar_w = 850
        bar_x, bar_y = 110, 1520
        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 22], radius=11, fill=(35, 50, 70))
        fill_w = max(0, min(bar_w, int(bar_w * bar_ratio)))
        bar_fill_color = (46, 213, 115) if is_winner else (30, 144, 255)
        if fill_w > 10:
            draw.rounded_rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + 22], radius=11, fill=bar_fill_color)

    # 3. Floating City Badges on Map (if in view)
    if -50 < t_screen[0] < 1130 and 150 < t_screen[1] < 1120:
        bx, by = t_screen[0] - 80, t_screen[1] - 65
        draw.rounded_rectangle([bx, by, bx + 160, by + 40], radius=12, fill=(12, 18, 30), outline=(255, 71, 87), width=2)
        draw.text((bx + 80, by + 20), "🇯🇵 TOKYO", font=font_pin, fill=(255, 255, 255), anchor="mm")

    if -50 < b_screen[0] < 1130 and 150 < b_screen[1] < 1120:
        bx, by = b_screen[0] - 80, b_screen[1] - 65
        draw.rounded_rectangle([bx, by, bx + 160, by + 40], radius=12, fill=(12, 18, 30), outline=(2, 165, 255), width=2)
        draw.text((bx + 80, by + 20), "🇩🇪 BERLIN", font=font_pin, fill=(255, 255, 255), anchor="mm")

    # 4. Bottom Subtitle Bar (y=1710 to 1830)
    draw.rounded_rectangle([60, 1710, 1020, 1830], radius=32, fill=(6, 12, 22), outline=(255, 211, 42), width=3)
    draw.text((540, 1770), sub_text, font=font_sub, fill=(255, 211, 42), anchor="mm")

    # Convert back to BGR and pipe to FFmpeg
    final_frame_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    proc.stdin.write(final_frame_bgr.tobytes())

    if frame_idx % 150 == 0:
        print(f"Rendered frame {frame_idx}/{TOTAL_FRAMES} ({(frame_idx/TOTAL_FRAMES)*100:.1f}%)")

proc.stdin.close()
proc.wait()
print("Direct FFmpeg Pipe Complete!")

# Copy to Google Drive
drive_dest = "G:/My Drive/YouTube_Shorts_Output/Japan_vs_Germany_MAP_FLIGHT.mp4"
try:
    shutil.copy2(final_out, drive_dest)
    print("==================================================")
    print("UPDATED ON GOOGLE DRIVE AT:", drive_dest)
    print("==================================================")
except Exception as e:
    print("Google Drive copy error:", e)

print("PURE MOTION MAP FLIGHT READY AT:", final_out)
