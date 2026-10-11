import os
import subprocess
import numpy as np
import scipy.io.wavfile as wavfile

base = "C:/Users/DELL/geo_shorts_factory"
sr = 44100

# 1. Convert inputs to clean 44.1kHz mono WAV
def convert_to_wav(in_path, out_path):
    cmd = ["ffmpeg", "-y", "-i", in_path, "-ar", str(sr), "-ac", "1", out_path]
    subprocess.run(cmd, check=True)

wav_voice = os.path.join(base, "audio/voice_mono.wav")
wav_bgm = os.path.join(base, "audio/bgm_mono.wav")
convert_to_wav(os.path.join(base, "output/merged_voice.mp4"), wav_voice)
convert_to_wav(os.path.join(base, "bgm.mp3"), wav_bgm)

# 2. Read all WAVs
_, voice_data = wavfile.read(wav_voice)
_, bgm_data = wavfile.read(wav_bgm)
_, whoosh_data = wavfile.read(os.path.join(base, "sfx/whoosh.wav"))
_, ding_data = wavfile.read(os.path.join(base, "sfx/ding.wav"))
_, impact_data = wavfile.read(os.path.join(base, "sfx/impact.wav"))

# Total length ~35.5s
total_samples = int(35.5 * sr)
master = np.zeros(total_samples, dtype=np.float32)

# Add voice
v_len = min(len(voice_data), total_samples)
master[:v_len] += voice_data[:v_len].astype(np.float32) * 1.0

# Add BGM with fadeout
b_len = min(len(bgm_data), total_samples)
bgm_track = bgm_data[:b_len].astype(np.float32) * 0.14
# Fade out in last 1.5s
fade_len = int(1.5 * sr)
fade_env = np.linspace(1.0, 0.0, fade_len)
bgm_track[-fade_len:] *= fade_env
master[:b_len] += bgm_track

# Helper to overlay SFX
def overlay_sfx(sfx_arr, start_sec, volume):
    start_idx = int(start_sec * sr)
    end_idx = min(start_idx + len(sfx_arr), total_samples)
    sfx_cut = sfx_arr[:end_idx - start_idx].astype(np.float32) * volume
    master[start_idx:end_idx] += sfx_cut

# Overlay Impacts (Cinematic Booms)
impact_times = [0.0, 1.8, 3.2]
for t in impact_times:
    overlay_sfx(impact_data, t, 0.65)

# Overlay Whooshes
whoosh_times = [1.2, 2.6, 4.63, 7.43, 12.77, 15.77, 22.06, 24.66, 29.91]
for t in whoosh_times:
    overlay_sfx(whoosh_data, t, 0.45)

# Overlay Dings
ding_times = [3.2, 7.43, 15.77, 24.66]
for t in ding_times:
    overlay_sfx(ding_data, t, 0.6)

# Normalize and export 16-bit PCM WAV
max_val = np.max(np.abs(master))
if max_val > 0:
    master = master / max_val * 32000
master_int16 = master.astype(np.int16)

master_wav_path = os.path.join(base, "audio/master_soundtrack.wav")
wavfile.write(master_wav_path, sr, master_int16)
print("MASTER SOUNDTRACK GENERATED AT:", master_wav_path)
