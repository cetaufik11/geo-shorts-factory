import os
import sys
import json
import math
import time
import shutil
import asyncio
import subprocess
import urllib.request
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import scipy.io.wavfile as wavfile
import edge_tts

from topics_data import TOPICS

base = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(base, "assets")
flags_dir = os.path.join(assets_dir, "flags")
overlays_dir = os.path.join(assets_dir, "overlays")
output_dir = os.path.join(base, "output_batch")
drive_dest_dir = "G:/My Drive/YouTube_Shorts_Output"

os.makedirs(flags_dir, exist_ok=True)
os.makedirs(overlays_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# 1. Load Base Map and GeoJSON
print("Loading base map and geojson data...")
base_map = cv2.imread(os.path.join(assets_dir, "world_base_3000.png"))
geo_data = json.load(open(os.path.join(assets_dir, "countries.geojson"), encoding="utf-8"))

# Load Fonts (Cross-platform)
fonts_dir = os.path.join(assets_dir, "fonts")
font_title_path = os.path.join(fonts_dir, "segoeuib.ttf") if os.path.exists(os.path.join(fonts_dir, "segoeuib.ttf")) else "C:/Windows/Fonts/segoeuib.ttf"
font_impact_path = os.path.join(fonts_dir, "impact.ttf") if os.path.exists(os.path.join(fonts_dir, "impact.ttf")) else "C:/Windows/Fonts/impact.ttf"

font_title = ImageFont.truetype(font_title_path, 52)
font_badge = ImageFont.truetype(font_title_path, 28)
font_stat_lbl = ImageFont.truetype(font_title_path, 32)
font_stat_val = ImageFont.truetype(font_impact_path, 76)
font_sub = ImageFont.truetype(font_impact_path, 46)
font_top = ImageFont.truetype(font_title_path, 36)
font_pin = ImageFont.truetype(font_title_path, 24)

# Load SFX & BGM
sr = 44100
_, whoosh_data = wavfile.read(os.path.join(base, "sfx/whoosh.wav"))
_, ding_data = wavfile.read(os.path.join(base, "sfx/ding.wav"))
_, impact_data = wavfile.read(os.path.join(base, "sfx/impact.wav"))

bgm_wav = os.path.join(base, "audio/bgm_mono.wav")
if not os.path.exists(bgm_wav):
    os.makedirs(os.path.join(base, "audio"), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-i", os.path.join(base, "bgm.mp3"), "-ar", "44100", "-ac", "1", bgm_wav], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
_, bgm_data = wavfile.read(bgm_wav)

# Coordinate Projection
def proj(lon, lat):
    x = 1500 + 475 * math.radians(lon)
    lat_clamped = max(-85.0, min(85.0, lat))
    y = 1500 - 475 * math.log(math.tan(math.pi/4 + math.radians(lat_clamped)/2))
    return [int(round(x)), int(round(y))]

def get_country_polys(iso2):
    if iso2 == "SG":
        # Singapore special island polygon
        angles = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        cx, cy = 2380, 1500
        return [np.array([[int(cx + 18 * np.cos(a)), int(cy + 18 * np.sin(a))] for a in angles], dtype=np.int32)]
    
    feat = next((f for f in geo_data['features'] if f['properties'].get('iso_a2') == iso2), None)
    if not feat:
        return []
    geom = feat['geometry']
    polys = []
    if geom['type'] == 'Polygon':
        for ring in geom['coordinates']:
            polys.append(np.array([proj(pt[0], pt[1]) for pt in ring], dtype=np.int32))
    elif geom['type'] == 'MultiPolygon':
        for poly in geom['coordinates']:
            for ring in poly:
                polys.append(np.array([proj(pt[0], pt[1]) for pt in ring], dtype=np.int32))
    return polys

# 2. Flag Downloader
def get_flag(iso2):
    flag_path = os.path.join(flags_dir, f"flag_{iso2.lower()}.png")
    if not os.path.exists(flag_path):
        url = f"https://flagcdn.com/w160/{iso2.lower()}.png"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp, open(flag_path, 'wb') as f:
                f.write(resp.read())
        except Exception as e:
            print(f"Error downloading flag for {iso2}: {e}")
            # create blank placeholder
            im = Image.new("RGB", (140, 92), (80, 80, 80))
            im.save(flag_path)
            return im
    return Image.open(flag_path).resize((140, 92))

# 3. Glowing Neon Overlay Synthesizer
def get_or_create_overlay(iso2, color_bgr):
    fname = f"overlay_{iso2}_{color_bgr[0]}_{color_bgr[1]}_{color_bgr[2]}.png"
    fpath = os.path.join(overlays_dir, fname)
    if os.path.exists(fpath):
        return cv2.imread(fpath, cv2.IMREAD_UNCHANGED)
    
    polys = get_country_polys(iso2)
    if not polys:
        return None
    
    overlay = np.zeros((3000, 3000, 4), dtype=np.uint8)
    # Bloom glow
    glow_mask = np.zeros((3000, 3000), dtype=np.uint8)
    cv2.fillPoly(glow_mask, polys, 255)
    cv2.polylines(glow_mask, polys, isClosed=True, color=255, thickness=12)
    small_mask = cv2.resize(glow_mask, (750, 750))
    small_blur = cv2.GaussianBlur(small_mask, (31, 31), 0)
    glow_blurred = cv2.resize(small_blur, (3000, 3000))
    
    for c in range(3):
        overlay[:, :, c] = color_bgr[c]
    overlay[:, :, 3] = (glow_blurred.astype(np.float32) * 0.72).astype(np.uint8)
    
    # Fill + Crisp Outline
    fill_img = np.zeros((3000, 3000, 4), dtype=np.uint8)
    cv2.fillPoly(fill_img, polys, (*color_bgr, 215))
    cv2.polylines(fill_img, polys, isClosed=True, color=(255, 255, 255, 255), thickness=4)
    
    alpha = fill_img[:, :, 3] / 255.0
    for c in range(3):
        overlay[:, :, c] = (overlay[:, :, c] * (1 - alpha) + fill_img[:, :, c] * alpha).astype(np.uint8)
    overlay[:, :, 3] = np.maximum(overlay[:, :, 3], fill_img[:, :, 3])
    
    cv2.imwrite(fpath, overlay)
    return overlay

# 4. Audio Generator with Edge-TTS & Dynamic Sound Design
async def generate_voice_scenes(topic, t_dir):
    os.makedirs(t_dir, exist_ok=True)
    voice = topic["voice"]
    
    scenes = [
        # Scene 1: Hook
        f"{topic['hook_text']} Which country actually gives you a better life?",
        # Scene 2: Round 1
        f"{topic['r1']['s1']} {topic['r1']['s2']}",
        # Scene 3: Round 2
        f"{topic['r2']['s1']} {topic['r2']['s2']}",
        # Scene 4: Round 3
        f"{topic['r3']['s1']} {topic['r3']['s2']}",
        # Scene 5: Outro
        topic["outro"]
    ]
    
    durations = []
    clip_paths = []
    for idx, text in enumerate(scenes):
        mp3_path = os.path.join(t_dir, f"scene_{idx+1}.mp3")
        comm = edge_tts.Communicate(text, voice, rate="+4%")
        await comm.save(mp3_path)
        
        # Get duration
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", mp3_path]
        dur_json = json.loads(subprocess.check_output(cmd))
        d = float(dur_json["format"]["duration"])
        durations.append(d)
        clip_paths.append(mp3_path)
    
    # Concat voice
    concat_txt = os.path.join(t_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in clip_paths:
            f.write(f"file '{p.replace(chr(92), '/')}'\n")
    
    merged_voice = os.path.join(t_dir, "voice_merged.wav")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-ar", "44100", "-ac", "1", merged_voice], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return merged_voice, durations

def build_soundtrack(voice_wav, durations, out_soundtrack):
    _, v_data = wavfile.read(voice_wav)
    total_samples = len(v_data) + int(0.5 * sr)
    master = np.zeros(total_samples, dtype=np.float32)
    
    # 1. Voice
    master[:len(v_data)] += v_data.astype(np.float32) * 1.0
    
    # 2. BGM
    bgm_len = min(len(bgm_data), total_samples)
    bgm_track = bgm_data[:bgm_len].astype(np.float32) * 0.13
    fade_len = int(1.5 * sr)
    if bgm_len > fade_len:
        bgm_track[-fade_len:] *= np.linspace(1.0, 0.0, fade_len)
    master[:bgm_len] += bgm_track
    
    def add_sfx(sfx_arr, start_sec, vol):
        s_idx = int(start_sec * sr)
        e_idx = min(s_idx + len(sfx_arr), total_samples)
        if s_idx < total_samples:
            cut = sfx_arr[:e_idx - s_idx].astype(np.float32) * vol
            master[s_idx:e_idx] += cut
    
    # Cumulative scene timestamps
    t0 = 0.0
    t1 = durations[0]
    t2 = t1 + durations[1]
    t3 = t2 + durations[2]
    t4 = t3 + durations[3]
    
    # Impacts & Whooshes for Hook (Scene 1)
    add_sfx(impact_data, 0.0, 0.65)
    add_sfx(whoosh_data, 1.3, 0.45)
    add_sfx(impact_data, 1.8, 0.65)
    add_sfx(whoosh_data, 2.7, 0.45)
    add_sfx(ding_data, 3.2, 0.60)
    
    # Round 1 (Scene 2)
    add_sfx(whoosh_data, t1, 0.40)
    add_sfx(whoosh_data, t1 + durations[1]*0.5, 0.40)
    add_sfx(ding_data, t1 + durations[1]*0.65, 0.60)
    
    # Round 2 (Scene 3)
    add_sfx(whoosh_data, t2, 0.40)
    add_sfx(whoosh_data, t2 + durations[2]*0.5, 0.40)
    add_sfx(ding_data, t2 + durations[2]*0.65, 0.60)
    
    # Round 3 (Scene 4)
    add_sfx(whoosh_data, t3, 0.40)
    add_sfx(whoosh_data, t3 + durations[3]*0.5, 0.40)
    add_sfx(ding_data, t3 + durations[3]*0.65, 0.60)
    
    # Outro (Scene 5)
    add_sfx(whoosh_data, t4, 0.45)
    add_sfx(impact_data, t4 + 0.3, 0.55)
    
    # Normalize
    m_max = np.max(np.abs(master))
    if m_max > 0:
        master = master / m_max * 32000
    wavfile.write(out_soundtrack, sr, master.astype(np.int16))

# 5. Smooth Interpolation Easing
def smooth_ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * t * (t * (t * 6 - 15) + 10)

def interp_cam(c1, c2, t, arc_lift=0.0):
    e = smooth_ease(t)
    x = c1[0] + (c2[0] - c1[0]) * e
    y = c1[1] + (c2[1] - c1[1]) * e
    s = c1[2] + (c2[2] - c1[2]) * e
    if arc_lift > 0.0:
        s -= arc_lift * np.sin(e * np.pi)
    return x, y, max(0.4, s)

# 6. Full Deterministic Motion Renderer
def render_shorts_video(topic, audio_path, durations, out_mp4):
    c1 = topic["c1"]
    c2 = topic["c2"]
    
    # Overlays
    ov_c1 = get_or_create_overlay(c1["iso"], c1["color_bgr"])
    ov_c2 = get_or_create_overlay(c2["iso"], c2["color_bgr"])
    
    # Pre-composite maps
    map_c1 = base_map.copy()
    if ov_c1 is not None:
        a = ov_c1[:, :, 3] / 255.0
        for i in range(3):
            map_c1[:, :, i] = (1 - a) * map_c1[:, :, i] + a * ov_c1[:, :, i]
            
    map_c2 = base_map.copy()
    if ov_c2 is not None:
        a = ov_c2[:, :, 3] / 255.0
        for i in range(3):
            map_c2[:, :, i] = (1 - a) * map_c2[:, :, i] + a * ov_c2[:, :, i]
            
    map_both = base_map.copy()
    if ov_c1 is not None:
        a = ov_c1[:, :, 3] / 255.0
        for i in range(3):
            map_both[:, :, i] = (1 - a) * map_both[:, :, i] + a * ov_c1[:, :, i]
    if ov_c2 is not None:
        a = ov_c2[:, :, 3] / 255.0
        for i in range(3):
            map_both[:, :, i] = (1 - a) * map_both[:, :, i] + a * ov_c2[:, :, i]

    # Preload flags
    flag1 = get_flag(c1["iso"])
    flag2 = get_flag(c2["iso"])
    
    # Dynamic camera overview calculation
    mid_x = (c1["coords"][0] + c2["coords"][0]) / 2
    mid_y = (c1["coords"][1] + c2["coords"][1]) / 2
    dist = math.hypot(c1["coords"][0] - c2["coords"][0], c1["coords"][1] - c2["coords"][1])
    ov_scale = min(0.95, max(0.48, 850.0 / (dist + 300)))
    
    pos_overview = (mid_x, mid_y, ov_scale)
    pos_c1 = (c1["coords"][0], c1["coords"][1], 1.95)
    pos_c2 = (c2["coords"][0], c2["coords"][1], 1.95)
    
    # Timeline durations
    d_hook = durations[0]
    d_r1 = durations[1]
    d_r2 = durations[2]
    d_r3 = durations[3]
    d_outro = durations[4]
    
    t_h_end = d_hook
    t_r1_end = t_h_end + d_r1
    t_r2_end = t_r1_end + d_r2
    t_r3_end = t_r2_end + d_r3
    total_time = t_r3_end + d_outro
    
    FPS = 30
    total_frames = int(total_time * FPS)
    
    def get_state(sec):
        # 1. Opening Hook (0 to t_h_end)
        if sec < t_h_end:
            p1_end = 1.35
            p2_end = 2.75
            if sec < p1_end:
                t_d = min(1.0, sec / 0.8)
                cam_start = (c1["coords"][0] - 100, c1["coords"][1] - 50, 1.1)
                cam = interp_cam(cam_start, pos_c1, t_d)
                return cam, "C1", (flag1, c1["name"], "CONTENDER #1", "Powerhouse", "READY", 0.85, False, "Which country gives you...", topic["hook_badge"])
            elif sec < p2_end:
                t_f = min(1.0, (sec - p1_end) / 1.3)
                cam = interp_cam(pos_c1, pos_c2, t_f, arc_lift=0.35)
                act = "C2" if t_f > 0.35 else "C1"
                return cam, act, (flag2, c2["name"], "CONTENDER #2", "Powerhouse", "CHALLENGER", 0.90, False, "...a BETTER life?", topic["hook_badge"])
            else:
                t_o = min(1.0, (sec - p2_end) / 1.4)
                cam = interp_cam(pos_c2, pos_overview, t_o)
                return cam, "BOTH", (flag1, f"{c1['iso']} vs {c2['iso']}", "THE DUEL", "Quality of Life Faceoff", "⚔️ VS ⚔️", 1.0, False, "Let's compare the real data!", "⚔️ THE ULTIMATE DUEL ⚔️")
        
        # 2. Round 1
        elif sec < t_r1_end:
            r = topic["r1"]
            local_t = sec - t_h_end
            split = d_r1 * 0.45
            if local_t < split:
                t_f = min(1.0, local_t / 1.4)
                cam = interp_cam(pos_overview, pos_c1, t_f, arc_lift=0.25)
                c_p = min(1.0, local_t / (split * 0.8))
                is_win = r["winner"] == "c1" and local_t > split * 0.6
                return cam, "C1", (flag1, c1["name"], "🏆 WINNER" if is_win else "ROUND 1", r["lbl"], r["c1_val"], c_p * 0.85, is_win, r["s1"], r["badge"])
            else:
                t_f = min(1.0, (local_t - split) / 1.4)
                cam = interp_cam(pos_c1, pos_c2, t_f, arc_lift=0.35)
                c_p = min(1.0, (local_t - split) / ((d_r1 - split) * 0.8))
                is_win = r["winner"] == "c2" and (local_t - split) > (d_r1 - split) * 0.5
                return cam, "C2", (flag2, c2["name"], "🏆 WINNER" if is_win else "ROUND 1", r["lbl"], r["c2_val"], c_p * 0.95, is_win, r["s2"], r["badge"])

        # 3. Round 2
        elif sec < t_r2_end:
            r = topic["r2"]
            local_t = sec - t_r1_end
            split = d_r2 * 0.45
            if local_t < split:
                t_f = min(1.0, local_t / 1.4)
                cam = interp_cam(pos_c2, pos_c1, t_f, arc_lift=0.35)
                c_p = min(1.0, local_t / (split * 0.8))
                is_win = r["winner"] == "c1" and local_t > split * 0.6
                return cam, "C1", (flag1, c1["name"], "🏆 WINNER" if is_win else "ROUND 2", r["lbl"], r["c1_val"], c_p * 0.85, is_win, r["s1"], r["badge"])
            else:
                t_f = min(1.0, (local_t - split) / 1.4)
                cam = interp_cam(pos_c1, pos_c2, t_f, arc_lift=0.35)
                c_p = min(1.0, (local_t - split) / ((d_r2 - split) * 0.8))
                is_win = r["winner"] == "c2" and (local_t - split) > (d_r2 - split) * 0.5
                return cam, "C2", (flag2, c2["name"], "🏆 WINNER" if is_win else "ROUND 2", r["lbl"], r["c2_val"], c_p * 0.95, is_win, r["s2"], r["badge"])

        # 4. Round 3
        elif sec < t_r3_end:
            r = topic["r3"]
            local_t = sec - t_r2_end
            split = d_r3 * 0.45
            if local_t < split:
                t_f = min(1.0, local_t / 1.4)
                cam = interp_cam(pos_c2, pos_c1, t_f, arc_lift=0.35)
                c_p = min(1.0, local_t / (split * 0.8))
                is_win = r["winner"] == "c1" and local_t > split * 0.6
                return cam, "C1", (flag1, c1["name"], "🏆 WINNER" if is_win else "ROUND 3", r["lbl"], r["c1_val"], c_p * 0.85, is_win, r["s1"], r["badge"])
            else:
                t_f = min(1.0, (local_t - split) / 1.4)
                cam = interp_cam(pos_c1, pos_c2, t_f, arc_lift=0.35)
                c_p = min(1.0, (local_t - split) / ((d_r3 - split) * 0.8))
                is_win = r["winner"] == "c2" and (local_t - split) > (d_r3 - split) * 0.5
                return cam, "C2", (flag2, c2["name"], "🏆 WINNER" if is_win else "ROUND 3", r["lbl"], r["c2_val"], c_p * 0.95, is_win, r["s2"], r["badge"])

        # 5. Outro
        else:
            local_t = sec - t_r3_end
            t_f = min(1.0, local_t / 1.6)
            cam = interp_cam(pos_c2, pos_overview, t_f, arc_lift=0.25)
            return cam, "BOTH", (flag1, "WHICH ONE?", "VOTE BELOW", f"A: {c1['name']} vs B: {c2['name']}", "YOUR VOTE", 0.5, False, topic["outro"], "🔥 FINAL VERDICT 🔥")

    # Launch FFmpeg Pipe
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1080x1920",
        "-pix_fmt", "bgr24",
        "-r", "30",
        "-i", "-",
        "-i", audio_path,
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{total_time:.2f}",
        out_mp4
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    
    pt1 = (int(c1["coords"][0]), int(c1["coords"][1]))
    pt2 = (int(c2["coords"][0]), int(c2["coords"][1]))
    
    for frame_idx in range(total_frames):
        sec = frame_idx / FPS
        cam, act_country, (flag, name, badge, stat_lbl, stat_val, bar_ratio, is_winner, sub_text, top_badge) = get_state(sec)
        
        # Texture
        if act_country == "C1":
            cur_map = map_c1
        elif act_country == "C2":
            cur_map = map_c2
        elif act_country == "BOTH":
            cur_map = map_both
        else:
            cur_map = base_map
            
        cx, cy, scale = cam
        M = np.float32([
            [scale, 0, 540 - cx * scale],
            [0, scale, 750 - cy * scale]
        ])
        frame_bgr = cv2.warpAffine(cur_map, M, (1080, 1920), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(8, 16, 30))
        
        # Flight Arc
        s1_pt = (int(pt1[0] * scale + (540 - cx * scale)), int(pt1[1] * scale + (750 - cy * scale)))
        s2_pt = (int(pt2[0] * scale + (540 - cx * scale)), int(pt2[1] * scale + (750 - cy * scale)))
        
        mid_ctrl = ((s1_pt[0] + s2_pt[0]) // 2, min(s1_pt[1], s2_pt[1]) - int(150 * scale))
        curve_pts = []
        for t_step in np.linspace(0, 1, 20):
            px = (1 - t_step)**2 * s1_pt[0] + 2 * (1 - t_step) * t_step * mid_ctrl[0] + t_step**2 * s2_pt[0]
            py = (1 - t_step)**2 * s1_pt[1] + 2 * (1 - t_step) * t_step * mid_ctrl[1] + t_step**2 * s2_pt[1]
            curve_pts.append([int(px), int(py)])
        cv2.polylines(frame_bgr, [np.array(curve_pts, dtype=np.int32)], isClosed=False, color=(42, 211, 255), thickness=3, lineType=cv2.LINE_AA)
        
        # Traveling pulse
        t_pulse = (sec * 0.7) % 1.0
        px = (1 - t_pulse)**2 * s1_pt[0] + 2 * (1 - t_pulse) * t_pulse * mid_ctrl[0] + t_pulse**2 * s2_pt[0]
        py = (1 - t_pulse)**2 * s1_pt[1] + 2 * (1 - t_pulse) * t_pulse * mid_ctrl[1] + t_pulse**2 * s2_pt[1]
        cv2.circle(frame_bgr, (int(px), int(py)), 7, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(frame_bgr, (int(px), int(py)), 14, (42, 211, 255), 2, cv2.LINE_AA)
        
        # Beacons
        r1_pulse = int(3 * np.sin(sec * 10))
        cv2.circle(frame_bgr, s1_pt, int(11 * min(2.0, scale)), (87, 71, 255), -1, cv2.LINE_AA)
        cv2.circle(frame_bgr, s1_pt, int(18 * min(2.0, scale)) + r1_pulse, (87, 71, 255), 2, cv2.LINE_AA)
        
        r2_pulse = int(3 * np.cos(sec * 10))
        cv2.circle(frame_bgr, s2_pt, int(11 * min(2.0, scale)), (2, 165, 255), -1, cv2.LINE_AA)
        cv2.circle(frame_bgr, s2_pt, int(18 * min(2.0, scale)) + r2_pulse, (2, 165, 255), 2, cv2.LINE_AA)
        
        # PIL Draw
        img_pil = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        # Top pill
        top_w, top_h = 680, 76
        top_x = (1080 - top_w) // 2
        draw.rounded_rectangle([top_x, 90, top_x + top_w, 90 + top_h], radius=38, fill=(255, 71, 87), outline=(255, 255, 255), width=3)
        draw.text((540, 128), top_badge, font=font_top, fill=(255, 255, 255), anchor="mm")
        
        # HUD Panel
        hud_bg = (18, 38, 28) if is_winner else (10, 18, 32)
        hud_border = (46, 213, 115) if is_winner else (80, 110, 150)
        if is_winner:
            draw.rounded_rectangle([54, 1154, 1026, 1646], radius=44, fill=(25, 60, 40))
        draw.rounded_rectangle([60, 1160, 1020, 1640], radius=40, fill=hud_bg, outline=hud_border, width=4)
        
        if act_country == "BOTH":
            img_pil.paste(flag1, (110, 1205))
            img_pil.paste(flag2, (830, 1205))
            draw.text((540, 1220), name, font=font_title, fill=(255, 255, 255), anchor="mt")
            draw.rounded_rectangle([430, 1285, 650, 1330], radius=14, fill=(60, 85, 115))
            draw.text((540, 1307), badge, font=font_badge, fill=(220, 230, 245), anchor="mm")
            
            draw.text((110, 1380), stat_lbl, font=font_stat_lbl, fill=(150, 170, 195))
            draw.text((960, 1400), stat_val, font=font_stat_val, fill=(255, 211, 42), anchor="rm")
            
            bar_w = 850
            bar_x, bar_y = 110, 1520
            draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 22], radius=11, fill=(35, 50, 70))
            draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w // 2, bar_y + 22], radius=11, fill=(255, 71, 87))
            draw.rounded_rectangle([bar_x + bar_w // 2, bar_y, bar_x + bar_w, bar_y + 22], radius=11, fill=(46, 213, 115))
        else:
            if isinstance(flag, Image.Image):
                img_pil.paste(flag, (110, 1205))
            draw.text((280, 1220), name, font=font_title, fill=(255, 255, 255))
            badge_bg = (46, 213, 115) if is_winner else (60, 85, 115)
            badge_fg = (5, 15, 10) if is_winner else (220, 230, 245)
            draw.rounded_rectangle([720, 1220, 960, 1270], radius=16, fill=badge_bg)
            draw.text((840, 1245), badge, font=font_badge, fill=badge_fg, anchor="mm")
            
            draw.text((110, 1370), stat_lbl, font=font_stat_lbl, fill=(150, 170, 195))
            val_fg = (46, 213, 115) if is_winner else (255, 255, 255)
            draw.text((960, 1400), stat_val, font=font_stat_val, fill=val_fg, anchor="rm")
            
            bar_w = 850
            bar_x, bar_y = 110, 1520
            draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 22], radius=11, fill=(35, 50, 70))
            fill_w = max(0, min(bar_w, int(bar_w * bar_ratio)))
            bar_fill_color = (46, 213, 115) if is_winner else (30, 144, 255)
            if fill_w > 10:
                draw.rounded_rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + 22], radius=11, fill=bar_fill_color)
                
        # City Badges
        if -50 < s1_pt[0] < 1130 and 150 < s1_pt[1] < 1120:
            bx, by = s1_pt[0] - 80, s1_pt[1] - 65
            draw.rounded_rectangle([bx, by, bx + 160, by + 40], radius=12, fill=(12, 18, 30), outline=(255, 71, 87), width=2)
            draw.text((bx + 80, by + 20), f"{c1['city']}", font=font_pin, fill=(255, 255, 255), anchor="mm")
            
        if -50 < s2_pt[0] < 1130 and 150 < s2_pt[1] < 1120:
            bx, by = s2_pt[0] - 80, s2_pt[1] - 65
            draw.rounded_rectangle([bx, by, bx + 160, by + 40], radius=12, fill=(12, 18, 30), outline=(2, 165, 255), width=2)
            draw.text((bx + 80, by + 20), f"{c2['city']}", font=font_pin, fill=(255, 255, 255), anchor="mm")
            
        # Bottom Subtitle
        draw.rounded_rectangle([60, 1710, 1020, 1830], radius=32, fill=(6, 12, 22), outline=(255, 211, 42), width=3)
        draw.text((540, 1770), sub_text, font=font_sub, fill=(255, 211, 42), anchor="mm")
        
        final_frame_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        proc.stdin.write(final_frame_bgr.tobytes())
        
    proc.stdin.close()
    proc.wait()

# 7. Worker Loop
def process_single_video(topic):
    idx = topic["id"]
    fname = topic["filename"]
    print(f"\n=======================================================")
    print(f"[{idx}/30] GENERATING: {fname}")
    print(f"=======================================================")
    
    t_dir = os.path.join(output_dir, f"temp_{idx}")
    
    # Audio
    print(f"-> Generating neural voiceover ({topic['voice']})...")
    merged_voice, durations = asyncio.run(generate_voice_scenes(topic, t_dir))
    
    soundtrack_wav = os.path.join(t_dir, "soundtrack.wav")
    print(f"-> Mixing audio with BGM and SFX...")
    build_soundtrack(merged_voice, durations, soundtrack_wav)
    
    # Render
    local_mp4 = os.path.join(output_dir, f"{fname}.mp4")
    print(f"-> Rendering 30.00 CFR constant frame rate video...")
    render_shorts_video(topic, soundtrack_wav, durations, local_mp4)
    print(f"-> Video rendered successfully: {local_mp4}")
    
    # 1. Local Google Drive sync (if running on user's machine)
    if os.path.exists(drive_dest_dir):
        drive_file = os.path.join(drive_dest_dir, f"{fname}.mp4")
        try:
            shutil.copy2(local_mp4, drive_file)
            print(f"-> SYNCED TO LOCAL GOOGLE DRIVE: {drive_file}")
        except Exception as e:
            print(f"-> Local Google Drive sync warning: {e}")

    # 2. Cloud Google Drive API upload (if running in GitHub Actions with Secrets)
    gdrive_json = os.environ.get("GDRIVE_CREDENTIALS_JSON")
    gdrive_fid = os.environ.get("GDRIVE_FOLDER_ID")
    if gdrive_json and gdrive_fid:
        try:
            from upload_to_gdrive import upload_file_to_gdrive
            upload_file_to_gdrive(local_mp4, f"{fname}.mp4", gdrive_fid, gdrive_json)
        except Exception as e:
            print(f"-> Cloud Google Drive upload warning: {e}")
        
    # Clean temp dir
    try:
        shutil.rmtree(t_dir)
    except:
        pass
        
    print(f"[{idx}/30] COMPLETE: {fname}.mp4")

if __name__ == "__main__":
    start_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end_id = int(sys.argv[2]) if len(sys.argv) > 2 else len(TOPICS)
    
    print(f"Starting Batch Shorts Factory for topics {start_id} to {end_id}...")
    for topic in TOPICS:
        if start_id <= topic["id"] <= end_id:
            process_single_video(topic)
    print("\nALL REQUESTED VIDEOS GENERATED AND SYNCED TO GOOGLE DRIVE!")
