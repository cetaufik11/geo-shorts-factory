import os
import subprocess
import glob
import time
from playwright.sync_api import sync_playwright

base = "C:/Users/DELL/geo_shorts_factory"
rec_dir = os.path.join(base, "rec_temp")
os.makedirs(rec_dir, exist_ok=True)

# Clean existing webm files in rec_temp
for f in glob.glob(os.path.join(rec_dir, "*.webm")):
    try:
        os.remove(f)
    except:
        pass

html_path = os.path.join(base, "motion_shorts.html").replace("\\", "/")
file_url = f"file:///{html_path}"

print("Launching Playwright Chromium for 60fps Motion Capture...")
with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(
        viewport={"width": 1080, "height": 1920},
        record_video_dir=rec_dir,
        record_video_size={"width": 1080, "height": 1920}
    )
    page = context.new_page()
    page.goto(file_url)
    
    # Wait for the exact total duration (35.5 seconds)
    print("Recording real-time motion graphics, spring physics, and particle canvas (35.5s)...")
    page.wait_for_timeout(35500)
    
    context.close()
    browser.close()

# Find the recorded webm file
webm_files = glob.glob(os.path.join(rec_dir, "*.webm"))
if not webm_files:
    raise Exception("No webm recording found!")

raw_webm = webm_files[0]
print(f"Captured video: {raw_webm}")

# Build audio mix with voice + SFX + BGM
# SFX Timestamps:
# Whooshes: 0s, 4.63s, 12.77s, 22.06s, 29.91s
# Dings: 7.43s, 15.77s, 24.66s
whoosh = os.path.join(base, "sfx/whoosh.wav")
ding = os.path.join(base, "sfx/ding.wav")
bgm = os.path.join(base, "bgm.mp3")
voice = os.path.join(base, "output/merged_voice.mp4")
final_out = os.path.join(base, "Japan_vs_Germany_MOTION_GRAPHICS.mp4")

# Complex audio filter for voice + 5 whooshes + 3 dings + bgm
filter_complex = (
    "[0:a]volume=1.0[voice];"
    "[1:a]volume=0.35,adelay=0|0[w1];"
    "[1:a]volume=0.35,adelay=4630|4630[w2];"
    "[1:a]volume=0.35,adelay=12770|12770[w3];"
    "[1:a]volume=0.35,adelay=22060|22060[w4];"
    "[1:a]volume=0.35,adelay=29910|29910[w5];"
    "[2:a]volume=0.6,adelay=7430|7430[d1];"
    "[2:a]volume=0.6,adelay=15770|15770[d2];"
    "[2:a]volume=0.6,adelay=24660|24660[d3];"
    "[3:a]volume=0.15,afade=t=out:st=34:d=1.5[music];"
    "[voice][w1][w2][w3][w4][w5][d1][d2][d3][music]amix=inputs=10:duration=first[aout]"
)

cmd = [
    "ffmpeg", "-y",
    "-i", voice,
    "-i", whoosh,
    "-i", ding,
    "-stream_loop", "-1", "-i", bgm,
    "-i", raw_webm,
    "-filter_complex", filter_complex,
    "-map", "4:v",
    "-map", "[aout]",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    "-t", "35.25",
    final_out
]

print("Rendering final MP4 with synchronized audio & motion...")
subprocess.run(cmd, check=True)
print("==================================================")
print("PRO MOTION GRAPHICS VIDEO READY AT:", final_out)
print("==================================================")
