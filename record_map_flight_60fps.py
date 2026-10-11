import os
import subprocess
import glob
import shutil
from playwright.sync_api import sync_playwright

base = "C:/Users/DELL/geo_shorts_factory"
rec_dir = os.path.join(base, "rec_map_60fps")
os.makedirs(rec_dir, exist_ok=True)

# Clean previous webm
for f in glob.glob(os.path.join(rec_dir, "*.webm")):
    try:
        os.remove(f)
    except:
        pass

html_path = os.path.join(base, "map_flight_60fps.html").replace("\\", "/")
file_url = f"file:///{html_path}"

print("==================================================")
print("RECORDING 60FPS SMOOTH CONTINENTAL MAP FLIGHT...")
print("==================================================")

launch_args = [
    "--enable-gpu",
    "--use-gl=angle",
    "--enable-webgl",
    "--ignore-gpu-blocklist",
    "--disable-features=UseChromeOSDirectVideoDecoder"
]

with sync_playwright() as p:
    browser = p.chromium.launch(args=launch_args)
    context = browser.new_context(
        viewport={"width": 1080, "height": 1920},
        record_video_dir=rec_dir,
        record_video_size={"width": 1080, "height": 1920}
    )
    page = context.new_page()
    page.goto(file_url)
    
    print("Capturing 60fps buttery smooth continental flights (35.5s)...")
    page.wait_for_timeout(35500)
    
    context.close()
    browser.close()

webm_files = glob.glob(os.path.join(rec_dir, "*.webm"))
if not webm_files:
    raise Exception("No webm recording found!")

raw_webm = webm_files[0]
print(f"Captured 60fps video: {raw_webm} ({os.path.getsize(raw_webm)} bytes)")

master_audio = os.path.join(base, "audio/master_soundtrack.wav")
final_out = os.path.join(base, "Japan_vs_Germany_MAP_FLIGHT.mp4")

cmd = [
    "ffmpeg", "-y",
    "-i", raw_webm,
    "-i", master_audio,
    "-map", "0:v",
    "-map", "1:a",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
    "-r", "60",
    "-c:a", "aac", "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    "-t", "35.25",
    final_out
]

print("Rendering final 60fps MP4 with master audio...")
subprocess.run(cmd, check=True)

# Copy to Google Drive automatically
drive_dest = "G:/My Drive/YouTube_Shorts_Output/Japan_vs_Germany_MAP_FLIGHT.mp4"
try:
    shutil.copy2(final_out, drive_dest)
    print("==================================================")
    print("UPDATED ON GOOGLE DRIVE AT:", drive_dest)
    print("==================================================")
except Exception as e:
    print("Failed to copy to Google Drive:", e)

print("60FPS SMOOTH MAP FLIGHT VIDEO READY AT:", final_out)
