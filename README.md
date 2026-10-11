# 🌍 Automated Geo Country Comparison Shorts Factory

Pipeline otomatis untuk memproduksi video **YouTube Shorts / TikTok / Reels** berniche *Country Comparison / Geo-Facts* (seperti style Vox, Johnny Harris, RealLifeLore) dengan **30.00 CFR constant frame rate**, zoom kamera antar benua, efek neon border, dan hook pembuka dinamis.

---

## 🚀 Fitur Utama
1. **30 Matchup Unik (Anti-Template):** Meliputi seluruh benua dengan metrik beragam (Gaji, Kereta Cepat, Dana Minyak, Hari Cerah, Paspor, dll.).
2. **Deterministic Motion Engine:** OpenCV subpixel transform langsung dipipakan ke FFmpeg tanpa dropped frame (`dup=0`, `drop=0`).
3. **Multi-Voice AI:** Rotasi otomatis 4 narator neural Edge-TTS (Christopher, Guy, Eric, Ryan).
4. **Cinematic Sound Design:** Bass impact, whoosh transisi, dan victory ding terintegrasi.
5. **Dukungan Cloud & Lokal:** Berjalan di komputer lokal (auto-sync ke `G:\My Drive\YouTube_Shorts_Output`) atau di **GitHub Actions** (otomatis via Cron / Schedule).

---

## 💻 Menjalankan di Komputer Lokal

```bash
# Render video tertentu (misal: topik 1 sampai 5)
python batch_shorts_factory.py 1 5

# Render seluruh 30 video
python batch_shorts_factory.py 1 30
```

Hasil render akan otomatis tersimpan di folder lokal `output_batch/` dan dicopy ke `G:\My Drive\YouTube_Shorts_Output\`.

---

## ☁️ Menjalankan di GitHub Actions (Cloud Automation)

### 1. Hubungkan ke GitHub Repository
Buka terminal di folder ini:
```bash
git init
git add .
git commit -m "feat: automated geo shorts factory pipeline"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO_NAME.git
git push -u origin main
```

### 2. Jadwal Otomatis (Cron)
Workflow [generate_shorts.yml](.github/workflows/generate_shorts.yml) sudah dikonfigurasi untuk berjalan otomatis:
- **Jadwal:** Setiap hari jam 07:00 WIB (`cron: '0 0 * * *'`).
- **Manual Trigger:** Masuk ke tab **Actions** di GitHub ➔ Pilih **Automated Geo Shorts Generator** ➔ Klik **Run workflow** (masukkan Topic ID yang ingin dirender).

### 3. Setup Upload Otomatis ke Google Drive (Opsional)
Jika ingin video hasil render dari GitHub Actions langsung terkirim ke Google Drive:
1. Buat **Service Account** di Google Cloud Console dan unduh file kuncinya (`credentials.json`).
2. Bagikan (Share) folder Google Drive tujuan Anda ke email Service Account tersebut (Editor).
3. Di GitHub Repository, buka **Settings** ➔ **Secrets and variables** ➔ **Actions**, tambahkan:
   - `GDRIVE_CREDENTIALS_JSON`: Isi seluruh teks JSON dari file Service Account.
   - `GDRIVE_FOLDER_ID`: ID folder Google Drive tujuan (tertera di URL folder).
4. Jika Secrets tidak diisi, video tetap dapat diunduh langsung lewat menu **Artifacts** di setiap eksekusi GitHub Actions.
