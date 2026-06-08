# 🛡️ CyberGuard AI Assistant

CyberGuard adalah purwarupa Asisten Keamanan Siber berbasis AI (Natural Language Processing Heuristik) yang dirancang untuk mendeteksi ancaman keamanan siber secara lokal dan mandiri tanpa bergantung pada konektivitas API pihak ketiga. Aplikasi ini dikembangkan untuk tujuan edukasi dan perlindungan pengguna.

## ✨ Fitur Utama

1. **Pendeteksi Email Phishing (NLP Heuristik)**
   - Mendeteksi taktik *Spoofing*, urgensi, dan manipulasi *Social Engineering*.
   - Menganalisis elemen kredensial dan kata kunci yang mencurigakan.
2. **Pembedah Tautan (URL Anomaly Detector)**
   - Mampu memecah struktur *link* (`urllib.parse`) untuk menemukan taktik *Typosquatting* (pemalsuan sub-domain).
   - Mendeteksi *URL Shortener*, alamat IP langsung, dan ekstensi domain murah (TLD).
3. **Pengukur Kekuatan Sandi (Entropy & zxcvbn)**
   - Mengevaluasi kata sandi menggunakan metrik keamanan tingkat lanjut, bukan sekadar panjang karakter.
   - Peringatan instan jika kata sandi menggunakan pola umum atau kamus yang mudah ditebak.
4. **Asisten Edukasi Siber Interaktif**
   - *Chatbot* cerdas yang bertindak sebagai ensiklopedia siber berjalan (Mampu menjelaskan Malware, DDoS, Ransomware, MitM, dll).
5. **Ekspor Laporan Digital**
   - Mendukung pembuatan berkas PDF secara *real-time* (`fpdf2` & `markdown`) untuk menyimpan riwayat analisis keamanan sebagai bukti resmi.

## 🛠️ Teknologi yang Digunakan
- **Python 3.9+** (Bahasa Pemrograman Utama)
- **Streamlit** (Kerangka Antarmuka Pengguna/UI)
- **zxcvbn** (Algoritma Penilai Sandi Standar Industri)
- **FPDF2 & Markdown** (Pembuat Laporan PDF)
- **Regex (Regular Expression)** (Mesin Pencari Anomali NLP)

## 🚀 Cara Menjalankan Aplikasi Secara Lokal

1. Pastikan Anda telah menginstal pustaka yang dibutuhkan:
```bash
pip install -r requirements.txt
```

2. Jalankan aplikasi menggunakan Streamlit:
```bash
streamlit run app.py
```

---
*Proyek ini merupakan demonstrasi kemampuan analisis keamanan berskala lokal menggunakan mesin algoritma mandiri.*
