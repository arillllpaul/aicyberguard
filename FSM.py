from enum import Enum, auto
from engine import NLPEngine

# Penambahan status perantara untuk menunggu konfirmasi pengguna
class State(Enum):
    IDLE = auto()
    PASSWORD_CHECK = auto()
    WAIT_RETRY_PASSWORD = auto() 
    ASK_PASSWORD_BASE = auto()
    WAIT_PASSWORD_BASE = auto()
    PHISHING_CHECK = auto()
    WAIT_RETRY_PHISHING = auto()
    LINK_CHECK = auto()
    WAIT_RETRY_LINK = auto()

class CyberGuardFSM:
    def __init__(self):
        self.state = State.IDLE
        self.nlp = NLPEngine()
        self.response = ""
        self.latest_result_summary = None
        self.latest_result_full = None

    def get_response(self):
        return self.response

    def step(self, user_input=""):
        user_input = user_input.strip()
        intent = self.nlp.detect_intent(user_input)

        # ========================================================
        # LOGIKA INTERUPSI GLOBAL (Pindah fitur kapan saja)
        # ========================================================
        if intent == "OTHER_OPTIONS" or intent == "MENU":
            self.state = State.IDLE
            self.response = "Sistem kembali ke menu utama. Fitur yang tersedia:\n1. ✉️ Cek Email Phishing\n2. 🔑 Cek Kekuatan Sandi\n3. 🔗 Deteksi Link Berbahaya\n\nSilakan pilih atau ketik fitur yang ingin digunakan."
            return
        
        # Transisi dari IDLE berdasarkan intent
        if self.state == State.IDLE:
            if intent == "CHECK_PHISHING":
                self.state = State.PHISHING_CHECK
                self.response = "✉️🎣 **Mode Cek Email Phishing** aktif!\n\n👀 Silakan tempel (paste) teks email, SMS, atau pesan WhatsApp yang mencurigakan di bawah ini. Saya akan membongkar trik penipuannya!"
            elif intent == "CHECK_PASSWORD":
                self.state = State.PASSWORD_CHECK
                self.response = "🔑🛡️ **Mode Cek Kekuatan Sandi** aktif!\n\n🔐 Silakan ketik kata sandi yang ingin Anda uji. Tenang, sandi Anda tidak disimpan dan diproses secara lokal."
            elif intent == "CHECK_LINK":
                self.state = State.LINK_CHECK
                self.response = "🔗🌐 **Mode Deteksi Link Berbahaya** aktif!\n\n🕵️‍♂️ Silakan masukkan tautan/URL yang mencurigakan. Saya akan membedah anatomi link tersebut."
            elif intent == "AUDIT":
                self.response = "TRIGGER_AUDIT"
            elif intent == "EDUCATION":
                self.response = self.nlp.get_education_response(user_input)
            elif intent == "GREETING":
                self.response = "Halo juga! Saya siap membantu mengamankan aktivitas digital Anda. Ada yang spesifik ingin Anda cek hari ini?"
            else:
                self.response = "Maaf, saya belum sepenuhnya mengerti maksud Anda. Anda bisa mencoba mengetik istilah keamanan (misal: 'apa itu phishing?') atau langsung memilih fitur keamanan yang tersedia."
                
            return

        # --- ALUR CEK SANDI ---
        if self.state == State.PASSWORD_CHECK:
            result = self.nlp.check_password_strength(user_input)
            score = result['score']
            pwned_count = result['pwned_count']
            crack_time = result['crack_time']
            feedback = result['feedback']
            
            if score <= 2: kategori = "🔴 **Lemah**"
            elif score == 3: kategori = "🟡 **Sedang**"
            else: kategori = "🟢 **Sangat Kuat**"

            reply = f"**Hasil Analisis Kata Sandi:** {kategori} (Skor: {score}/4)\n\n"
            reply += f"⏱️ **Estimasi Waktu Retas:** {crack_time}\n\n"
            
            if pwned_count > 0:
                reply += f"⚠️ **BAHAYA KEBOCORAN DATA:** Kata sandi ini telah ditemukan bocor sebanyak **{pwned_count:,} kali** di internet. Jangan gunakan kata sandi ini!\n\n"
            else:
                reply += "✅ **Status Kebocoran:** Tidak ditemukan dalam database kebocoran publik (Aman).\n\n"

            if feedback: 
                reply += "**Masukan / Kelemahan:**\n" + "\n".join(feedback) + "\n\n"
            elif score == 4:
                reply += "Luar biasa! Kata sandi Anda sudah memenuhi standar keamanan siber yang kokoh.\n\n"
                
            self.latest_result_summary = f"**Hasil Kata Sandi:** {kategori} ({score}/4)"
            self.latest_result_full = reply
            
            reply += "\n---\n*Silakan klik tombol pilihan di bawah layar untuk langkah selanjutnya.*"
            self.response = reply
            
            # Pindah ke status tunggu konfirmasi (BUKAN ke IDLE)
            self.state = State.WAIT_RETRY_PASSWORD 

        # Menangani jawaban konfirmasi "Ya", "Saran" atau "Pilihan Lainnya"
        elif self.state == State.WAIT_RETRY_PASSWORD:
            if intent == "SUGGEST_PASSWORD":
                self.state = State.WAIT_PASSWORD_BASE
                self.response = "Baik, saya bisa membuatkannya! \n\nKetik **'acak'** jika Anda ingin sandi acak sepenuhnya, atau ketikkan **sebuah kata dasar** (misal: nama Anda 'aril') jika Anda ingin sandi yang lebih personal namun kuat."
            elif intent == "YES":
                self.state = State.PASSWORD_CHECK
                self.response = "Baik, silakan masukkan kata sandi baru yang ingin dicek."
            else:
                self.response = "Silakan jawab dengan **'saran'** (buat sandi baru), **'ya'** (untuk cek sandi lagi) atau **'pilihan lainnya'** (untuk melihat menu)."

        # --- ALUR SARAN SANDI ---
        elif self.state == State.WAIT_PASSWORD_BASE:
            if user_input.lower() == "acak":
                new_pwd = self.nlp.generate_strong_password()
                base_info = "Kata sandi acak sepenuhnya."
            else:
                new_pwd = self.nlp.generate_fortified_password(user_input)
                base_info = f"Kata sandi berbasis kata '{user_input}' yang telah diperkuat."
                
            reply = f"💡 **Ini Saran Kata Sandi Anda:**\n`{new_pwd}`\n\n"
            reply += f"*{base_info} Kombinasi ini sudah memenuhi standar keamanan siber yang kokoh!*\n\n"
            reply += "---\n*Silakan klik tombol pilihan di bawah layar untuk langkah selanjutnya.*"
            
            self.response = reply
            self.latest_result_summary = "**Saran Sandi Dibuat**"
            self.latest_result_full = reply
            self.state = State.WAIT_RETRY_PASSWORD

        # --- ALUR CEK PHISHING ---
        elif self.state == State.PHISHING_CHECK:
            result = self.nlp.check_phishing(user_input)
            
            if not result['valid']:
                self.response = f"⚠️ **Analisis Dibatalkan:**\n{result['error_msg']}\n\nSilakan coba lagi dengan input yang benar."
                # Tetap di state PHISHING_CHECK
                return
                
            score = result['score']
            risk_level = result['risk_level']
            feedback = result['feedback']
            
            reply = f"**Hasil Analisis Teks Phishing:** {risk_level} (Skor Risiko: {score}/100)\n\n"
            if feedback: 
                reply += "**Laporan Analisis Taktik:**\n" + "\n".join([f"- {f}" for f in feedback])
            else: 
                reply += "Teks ini tidak menunjukkan indikasi phishing yang jelas berdasarkan pola heuristik umum."
            
            self.latest_result_summary = f"**Hasil Phishing:** {risk_level}"
            self.latest_result_full = reply
            
            reply += "\n\n---\n*Silakan klik tombol pilihan di bawah layar untuk langkah selanjutnya.*"
            self.response = reply
            self.state = State.WAIT_RETRY_PHISHING

        elif self.state == State.WAIT_RETRY_PHISHING:
            if intent == "YES":
                self.state = State.PHISHING_CHECK
                self.response = "Baik, silakan tempelkan teks email atau pesan phishing yang ingin dicek."
            elif user_input.lower() == "cara lapor":
                self.response = "🛡️ **Panduan Pelaporan Phishing:**\n\n1. **Aduan Kominfo:** Teruskan pesan SMS penipuan ke **159** atau laporkan melalui situs *aduanbrti.id*.\n2. **Pihak Bank:** Jika penipu mengatasnamakan bank, segera hubungi nomor *Call Center* resmi (yang tertera di belakang kartu ATM Anda, BUKAN di pesan).\n3. **Cek Rekening:** Periksa nomor rekening penipu melalui situs *cekrekening.id*.\n\n---\n*Silakan klik tombol di bawah untuk langkah selanjutnya.*"
            else:
                self.response = "Silakan klik tombol pilihan di layar atau jawab dengan **'ya'** (untuk cek teks lagi) atau **'pilihan lainnya'** (untuk melihat menu)."

        # --- ALUR CEK LINK ---
        elif self.state == State.LINK_CHECK:
            result = self.nlp.check_link(user_input)
            
            if not result['valid']:
                self.response = f"⚠️ **Analisis Dibatalkan:**\n{result['error_msg']}\n\nSilakan coba lagi."
                return
                
            score = result['score']
            risk_level = result['risk_level']
            feedback = result['feedback']
            
            reply = f"**Hasil Analisis Tautan:** {risk_level} (Skor Risiko: {score}/100)\n\n"
            if feedback: 
                reply += "**Laporan Analisis Taktik:**\n" + "\n".join([f"- {f}" for f in feedback])
            else: 
                reply += "Tautan ini terlihat normal dan tidak menunjukkan pola anomali yang mencurigakan."
            
            self.latest_result_summary = f"**Hasil Tautan:** {risk_level}"
            self.latest_result_full = reply
            
            reply += "\n\n---\n*Silakan klik tombol pilihan di bawah layar untuk langkah selanjutnya.*"
            self.response = reply
            self.state = State.WAIT_RETRY_LINK

        elif self.state == State.WAIT_RETRY_LINK:
            if intent == "YES":
                self.state = State.LINK_CHECK
                self.response = "Baik, silakan kirimkan tautan/URL lainnya."
            else:
                self.response = "Silakan jawab dengan **'ya'** atau **'pilihan lainnya'**."