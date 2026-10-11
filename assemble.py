import os
import subprocess
import json

base = "C:/Users/DELL/geo_shorts_factory"
audio_dir = os.path.join(base, "audio")
frames_dir = os.path.join(base, "frames")
output_dir = os.path.join(base, "output")
os.makedirs(output_dir, exist_ok=True)

# 1. Create individual clips for each scene
clip_files = []
for i in range(1, 6):
    img = os.path.join(frames_dir, f"scene_{i}.png")
    aud = os.path.join(audio_dir, f"scene_{i}.mp3")
    out_clip = os.path.join(output_dir, f"clip_{i}.mp4")
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", img,
        "-i", aud,
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        out_clip
    ]
    subprocess.run(cmd, check=True)
    clip_files.append(out_clip)
    print(f"Rendered clip_{i}.mp4")

# 2. Concat all 5 clips
concat_list = os.path.join(output_dir, "concat.txt")
with open(concat_list, "w", encoding="utf-8") as f:
    for c in clip_files:
        clean_path = c.replace("\\", "/")
        f.write(f"file '{clean_path}'\n")

merged_voice = os.path.join(output_dir, "merged_voice.mp4")
subprocess.run([
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0", "-i", concat_list,
    "-c", "copy",
    merged_voice
], check=True)
print("Merged voice video created!")

# 3. Add BGM with balanced audio mixing (voice 1.0, bgm 0.15)
bgm_path = os.path.join(base, "bgm.mp3")
final_output = os.path.join(base, "Japan_vs_Germany_Shorts.mp4")

# Get duration of merged video
cmd_dur = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", merged_voice]
dur_out = subprocess.check_output(cmd_dur)
total_dur = float(json.loads(dur_out)["format"]["duration"])

cmd_final = [
    "ffmpeg", "-y",
    "-i", merged_voice,
    "-stream_loop", "-1", "-i", bgm_path,
    "-filter_complex",
    f"[0:a]volume=1.0[voice];[1:a]volume=0.15,afade=t=out:st={total_dur-1.5}:d=1.5[music];[voice][music]amix=inputs=2:duration=first[aout]",
    "-map", "0:v",
    "-map", "[aout]",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k",
    "-t", str(total_dur),
    final_output
]
subprocess.run(cmd_final, check=True)
print("========================================")
print("FINAL VIDEO READY AT:", final_output)
print("Duration:", f"{total_dur:.2f} seconds")
print("========================================")
