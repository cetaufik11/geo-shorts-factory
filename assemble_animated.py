import os
import subprocess
import json

base = "C:/Users/DELL/geo_shorts_factory"
frames_dir = os.path.join(base, "frames")
audio_dir = os.path.join(base, "audio")
sfx_dir = os.path.join(base, "sfx")
output_dir = os.path.join(base, "output_animated")
os.makedirs(output_dir, exist_ok=True)

whoosh_sfx = os.path.join(sfx_dir, "whoosh.wav")
ding_sfx = os.path.join(sfx_dir, "ding.wav")

def get_duration(audio_file):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", audio_file]
    out = subprocess.check_output(cmd)
    return float(json.loads(out)["format"]["duration"])

def render_zoom_video(img_path, duration, out_path, fps=30):
    total_frames = int(duration * fps) + 2
    # Smooth continuous zoom
    vf = f"scale=1080:1920,zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", img_path,
        "-vf", vf,
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        out_path
    ]
    subprocess.run(cmd, check=True)

# 1. SCENE 1 (Hook)
dur_1 = get_duration(os.path.join(audio_dir, "scene_1.mp3"))
v_s1 = os.path.join(output_dir, "v_s1.mp4")
a_s1 = os.path.join(output_dir, "a_s1.wav")
render_zoom_video(os.path.join(frames_dir, "scene_1.png"), dur_1, v_s1)
# Mix voice + whoosh at 0s
subprocess.run([
    "ffmpeg", "-y",
    "-i", os.path.join(audio_dir, "scene_1.mp3"),
    "-i", whoosh_sfx,
    "-filter_complex", "[0:a]volume=1.0[v];[1:a]volume=0.4[w];[v][w]amix=inputs=2:duration=first",
    a_s1
], check=True)

# Helper to render progressive round
def render_progressive_round(scene_num, split_time, img_a, img_b):
    aud_path = os.path.join(audio_dir, f"scene_{scene_num}.mp3")
    total_dur = get_duration(aud_path)
    dur_a = split_time
    dur_b = total_dur - split_time
    
    # Video A
    va = os.path.join(output_dir, f"v_s{scene_num}_a.mp4")
    render_zoom_video(img_a, dur_a, va)
    
    # Video B
    vb = os.path.join(output_dir, f"v_s{scene_num}_b.mp4")
    render_zoom_video(img_b, dur_b, vb)
    
    # Concat Video
    list_txt = os.path.join(output_dir, f"list_{scene_num}.txt")
    with open(list_txt, "w") as f:
        f.write(f"file '{va.replace(os.sep, '/')}'\n")
        f.write(f"file '{vb.replace(os.sep, '/')}'\n")
    
    v_merged = os.path.join(output_dir, f"v_s{scene_num}.mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_txt, "-c", "copy", v_merged], check=True)
    
    # Audio with Whoosh at 0s and Ding at split_time
    a_merged = os.path.join(output_dir, f"a_s{scene_num}.wav")
    filter_sfx = f"[0:a]volume=1.0[voice];[1:a]volume=0.4[w];[2:a]adelay={int(split_time*1000)}|{int(split_time*1000)},volume=0.6[d];[voice][w][d]amix=inputs=3:duration=first[aout]"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", aud_path,
        "-i", whoosh_sfx,
        "-i", ding_sfx,
        "-filter_complex", filter_sfx,
        "-map", "[aout]",
        a_merged
    ], check=True)
    
    return v_merged, a_merged

# 2. SCENE 2 (Salary)
v_s2, a_s2 = render_progressive_round(2, 3.0, 
    os.path.join(frames_dir, "scene_2_a.png"), 
    os.path.join(frames_dir, "scene_2.png"))

# 3. SCENE 3 (Work-life)
v_s3, a_s3 = render_progressive_round(3, 3.2, 
    os.path.join(frames_dir, "scene_3_a.png"), 
    os.path.join(frames_dir, "scene_3.png"))

# 4. SCENE 4 (Safety)
v_s4, a_s4 = render_progressive_round(4, 2.8, 
    os.path.join(frames_dir, "scene_4_a.png"), 
    os.path.join(frames_dir, "scene_4.png"))

# 5. SCENE 5 (Call to action)
dur_5 = get_duration(os.path.join(audio_dir, "scene_5.mp3"))
v_s5 = os.path.join(output_dir, "v_s5.mp4")
a_s5 = os.path.join(output_dir, "a_s5.wav")
render_zoom_video(os.path.join(frames_dir, "scene_5.png"), dur_5, v_s5)
subprocess.run([
    "ffmpeg", "-y",
    "-i", os.path.join(audio_dir, "scene_5.mp3"),
    "-i", whoosh_sfx,
    "-filter_complex", "[0:a]volume=1.0[v];[1:a]volume=0.4[w];[v][w]amix=inputs=2:duration=first",
    a_s5
], check=True)

# Combine each video with its audio
final_scenes = []
for i, (v, a) in enumerate([(v_s1, a_s1), (v_s2, a_s2), (v_s3, a_s3), (v_s4, a_s4), (v_s5, a_s5)], start=1):
    scene_out = os.path.join(output_dir, f"final_scene_{i}.mp4")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", v,
        "-i", a,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        scene_out
    ], check=True)
    final_scenes.append(scene_out)

# Concat all scenes
full_list = os.path.join(output_dir, "full_list.txt")
with open(full_list, "w") as f:
    for sc in final_scenes:
        f.write(f"file '{sc.replace(os.sep, '/')}'\n")

full_video = os.path.join(output_dir, "full_animated_voice.mp4")
subprocess.run([
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0", "-i", full_list,
    "-c", "copy",
    full_video
], check=True)

# Add BGM
bgm_path = os.path.join(base, "bgm.mp3")
final_animated = os.path.join(base, "Japan_vs_Germany_Shorts_ANIMATED.mp4")
total_dur = get_duration(full_video)

cmd_final = [
    "ffmpeg", "-y",
    "-i", full_video,
    "-stream_loop", "-1", "-i", bgm_path,
    "-filter_complex",
    f"[0:a]volume=1.0[voice];[1:a]volume=0.15,afade=t=out:st={total_dur-1.5}:d=1.5[music];[voice][music]amix=inputs=2:duration=first[aout]",
    "-map", "0:v",
    "-map", "[aout]",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k",
    "-t", str(total_dur),
    final_animated
]
subprocess.run(cmd_final, check=True)
print("ANIMATED VIDEO CREATED AT:", final_animated)
