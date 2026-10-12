# 🤖 MASTER PROMPT CLAUDE - KONTEN GENERATOR YOUTUBE SHORTS
Dokumen ini berisi panduan dan master prompt siap pakai untuk diberikan ke Claude agar menghasilkan ide, naskah, dan dataset yang **100% kompatibel dengan pipeline automasi YouTube Shorts**.

---

## 🎯 PROMPT 1: Country Showdown & Superpower Rivalry (Format USA vs China - 1K+ Views)
> **Gunakan prompt ini jika ingin menambah stok video perbandingan negara di `geo_shorts_factory`. Format ini terbukti viral dan memancing perdebatan di kolom komentar.**

### 📋 Salin Teks Prompt Berikut ke Claude:
```text
Halo Claude, saya mengelola channel YouTube Shorts bertema Geopolitik & Perbandingan Negara bergaya modern neon HUD (seperti akun perbandingan data & geografi viral). Target audiens saya adalah penonton US & Global (High RPM). 

Video saya sebelumnya yang berjudul "USA vs China: Superpower Showdown" sangat sukses (tembus 1.000+ views dengan engagement tinggi) karena membandingkan metrik tajam dan memancing debat penonton.

Tolong buatkan 5 data topik pertarungan negara baru yang sangat kontroversial, seru, dan menarik untuk audiens global/US. Contoh tema:
- USA vs Russia (Military Power / Resources / Wealth)
- China vs India (Demographic & Tech Titan Battle)
- Japan vs Germany (Economic & Engineering Giants)
- Texas vs California (US Internal Showdown)
- Saudi Arabia vs UAE (Gulf Wealth & Mega Projects)

PENTING: Output HARUS dalam format struktur list Python dictionary berikut agar bisa langsung saya paste ke sistem automasi tanpa modifikasi:

[
    {
        "id": <nomor_id_lanjutan>,
        "filename": "<ID_NEGARA1_vs_NEGARA2>",
        "voice": "en-US-ChristopherNeural",  # Pilih: en-US-ChristopherNeural, en-US-GuyNeural, en-US-EricNeural, atau en-GB-RyanNeural
        "c1": {
            "name": "<NAMA NEGARA 1 + FLAG EMOJI>",
            "iso": "<ISO_2_LETTER_CODE>",
            "city": "<CAPITAL_CITY>",
            "coords": (<PIXEL_X>, <PIXEL_Y>), # atau sebutkan Longitude & Latitude kotanya
            "color_bgr": (<B>, <G>, <R>) # Warna neon kontras (misal Neon Blue: 255, 140, 30)
        },
        "c2": {
            "name": "<NAMA NEGARA 2 + FLAG EMOJI>",
            "iso": "<ISO_2_LETTER_CODE>",
            "city": "<CAPITAL_CITY>",
            "coords": (<PIXEL_X>, <PIXEL_Y>),
            "color_bgr": (<B>, <G>, <R>) # Warna neon kontras kedua (misal Crimson Red: 40, 50, 255)
        },
        "hook_badge": "🔥 <HOOK_BADGE_TEXT> 🔥",
        "hook_text": "<Pertanyaan provokatif pembuka di detik 1-3>",
        "r1": {
            "badge": "💰 <NAMA_ROUND_1> 💰",
            "lbl": "<Label Metrik>",
            "c1_val": "<Nilai Negara 1, misal $5,000>",
            "c1_num": <Angka integer>,
            "c2_val": "<Nilai Negara 2, misal $1,200>",
            "c2_num": <Angka integer>,
            "winner": "c1", # atau "c2"
            "s1": "<Kalimat voiceover untuk Negara 1>",
            "s2": "<Kalimat voiceover untuk Negara 2 yang mengumumkan pemenang>"
        },
        "r2": {
            "badge": "⚔️ <NAMA_ROUND_2> ⚔️",
            "lbl": "<Label Metrik>",
            "c1_val": "<Nilai Negara 1>",
            "c1_num": <Angka integer>,
            "c2_val": "<Nilai Negara 2>",
            "c2_num": <Angka integer>,
            "winner": "c2",
            "s1": "<Kalimat voiceover Negara 1>",
            "s2": "<Kalimat voiceover Negara 2>"
        },
        "r3": {
            "badge": "🚀 <NAMA_ROUND_3> 🚀",
            "lbl": "<Label Metrik>",
            "c1_val": "<Nilai Negara 1>",
            "c1_num": <Angka integer>,
            "c2_val": "<Nilai Negara 2>",
            "c2_num": <Angka integer>,
            "winner": "c1",
            "s1": "<Kalimat voiceover Negara 1>",
            "s2": "<Kalimat voiceover Negara 2>"
        },
        "outro": "<Pertanyaan penutup memancing komentar: Siapa pemenang sejati? Komen Negara 1 atau Negara 2 di bawah!>"
    }
]

Pastikan datanya akurat, kalimat naskah bahasa Inggris tajam dan punchy, serta skor akhir berimbang (misal 2-1) agar penonton berdebat di kolom komentar.
```

---

## 🗺️ PROMPT 2: True-Scale Map Flying Comparison (Format Video Telegram / Peta Terbang)
> **Gunakan prompt ini untuk membuat ide komparasi skala peta nyata (True Scale vs Mercator distortion), persis seperti video `IMG_7126.MP4` di Telegram.**

### 📋 Salin Teks Prompt Berikut ke Claude:
```text
Halo Claude, saya sedang memproduksi video YouTube Shorts bertema Geografi Animasi Vektor Bersih (Clean Minimalist Vector Map Comparison). 

Format videonya adalah menganimasikan satu pulau/negara/wilayah besar diterbangkan ke benua lain (misalnya Eropa atau Amerika Serikat) untuk membuktikan skala aslinya jika tidak terdistorsi proyeksi Mercator (True-Scale Projection).

Tolong buatkan 5 konsep video baru yang paling mengejutkan (mind-blowing) bagi penonton global/US. Contoh:
1. Seberapa besar Pulau Kalimantan/Sumatra jika ditaruh di atas Benua Eropa?
2. Berapa banyak negara Eropa yang bisa muat di dalam Texas atau Alaska?
3. Seberapa luas daratan Amerika Serikat jika ditaruh di atas gurun Sahara/Afrika?
4. Perbandingan luas Jepang vs Pantai Timur Amerika Serikat.

Untuk setiap konsep, berikan detail data berikut:
1. Subjek Wilayah yang Diterbangkan (Subject Territory) & ISO Code.
2. Wilayah Tujuan (Destination Region, misal Western Europe / North America).
3. Hook Teks di Detik Pertama (contoh: "COVERING HOW MANY COUNTRIES? (min. 100 km² per country)").
4. Faktor Skala Mercator (Mercator Scale Factor & Latitude, contoh: "DRAWN AT x1.41 at 47°N").
5. Daftar Negara yang Tertutup/Tersentuh oleh wilayah tersebut (Countries Covered) beserta total luas wilayahnya.
6. Pertanyaan Provokatif Penutup (Outro) untuk memancing penonton menulis komentar perbandingan berikutnya.
```

---

## 📊 PROMPT 3: DataFlux Cyberpunk Bar Chart Race (Format Statistik Bergerak)
> **Gunakan prompt ini jika ingin menambah dataset statistik waktu-ke-waktu untuk repo `dataflux-automation`.**

### 📋 Salin Teks Prompt Berikut ke Claude:
```text
Halo Claude, saya mengelola channel YouTube Shorts "DataFlux" yang menyajikan animasi vertikal (9:16) Bar Chart Race bertema dark cyberpunk neon HUD untuk audiens US/High RPM.

Tolong buatkan 3 dataset time-series lengkap untuk topik berikut (pilih topik yang sangat kompetitif dan memicu rasa penasaran penonton US):
1. Market Cap 10 Perusahaan Paling Bernilai di Dunia (Tahun 2000 - 2025).
2. 10 Mata Uang Kripto Terbesar (Tahun 2015 - 2025).
3. Pendapatan Box Office Franchise Film Terbesar Sepanjang Masa (Tahun 1990 - 2024).

Format data untuk setiap video:
- Judul Video & Deskripsi Singkat untuk SEO YouTube US.
- Format CSV dengan header: Year,Entity,Value,Category
- Rentang tahun lengkap dengan interval tahunan/kuartalan agar animasinya mengalir mulus.
```

---

## 🚀 CARA MEMASUKKAN HASIL DARI CLAUDE KE AUTOMASI LAPTOP

1. **Buka Claude**, lalu *paste* salah satu prompt di atas.
2. Setelah Claude memberikan jawaban:
   - **Jika memilih Prompt 1 (Country Showdown)**:
     - Buka file `topics_data.py` di folder `geo_shorts_factory`.
     - Tempelkan (*paste*) list topik baru dari Claude ke dalam array `TOPICS`.
     - Jalankan script rendering di PowerShell:
       ```powershell
       python batch_shorts_factory.py
       ```
     - Video MP4 baru akan otomatis ter-generate di folder `output_batch/` dan siap tayang!
   - **Atau cukup kirim hasil Claude ke chat ini**:
     - Anda tinggal *paste* teks hasil dari Claude ke chat kita, nanti saya yang akan langsung merapikan kodenya dan mengeksekusi automasi renderingnya untuk Anda!
