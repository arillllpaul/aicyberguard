import re
import hashlib
import requests
import secrets
import string
from zxcvbn import zxcvbn

class NLPEngine:
    def __init__(self):
        # Pola regex fitur utama
        self.intent_phishing = r"\b(phishing|email|surel|tipuan|palsu)\b|^1$"
        self.intent_password = r"\b(sandi|password|kekuatan|cek password|cek sandi)\b|^2$"
        self.intent_link = r"\b(link|tautan|url|situs|web)\b|^3$"
        self.intent_audit = r"\b(audit|kesehatan|cek akun|keamanan akun|kuesioner|tes aman)\b"
        
        self.intent_menu = r"\b(menu|kembali|batal|keluar|awal)\b"
        
        # Pola regex untuk jawaban konfirmasi pengguna
        self.intent_yes = r"\b(ya|iya|mau|boleh|lanjut|y|cek lagi)\b"
        self.intent_other = r"\b(pilihan lainnya|fitur lainnya|lainnya|lain|tidak|enggak)\b"

        # Pola regex untuk sapaan santai
        self.intent_greeting = r"\b(halo|hai|hey|hi|helo|pagi|siang|malam|bot|p)\b"

        # Pola regex untuk minta saran sandi
        self.intent_suggest = r"\b(saran|buatkan|rekomendasi|kasih saran|minta saran)\b"
        
        # Kamus Edukasi Keamanan Siber (Versi Diperluas)
        # Kamus Edukasi Keamanan Siber (Versi Ekstra Lengkap)
        self.cyber_dictionary = {
            "phishing": "🎣 **Phishing (Pengelabuan)**\n\nPhishing adalah teknik penipuan siber yang paling umum terjadi. Pelaku akan menyamar sebagai pihak yang dapat dipercaya (seperti bank, perusahaan e-commerce, atau instansi pemerintah) melalui email, SMS (Smishing), atau telepon (Vishing).\n\n**Tujuan Utama:** Memancing Anda untuk menyerahkan data sensitif seperti *password*, nomor kartu kredit, atau kode OTP.\n\n**Ciri-ciri Khas:**\n- Menciptakan rasa panik (contoh: \"Rekening Anda akan diblokir dalam 24 jam!\").\n- Menawarkan hadiah yang terlalu bagus untuk menjadi kenyataan.\n- Meminta Anda mengeklik tautan yang mengarah ke situs palsu.",
            
            "spoofing": "🎭 **Spoofing (Pemalsuan Identitas)**\n\nSpoofing adalah taktik tingkat lanjut di mana *hacker* memalsukan identitas digital agar terlihat seperti sumber yang sah. Berbeda dengan phishing biasa, spoofing lebih fokus pada manipulasi sistem.\n\n**Contoh Kasus:**\n- **Email Spoofing:** Anda menerima email dari `admin@bca.com`, namun jika dilacak IP pengirimnya, email tersebut sebenarnya dikirim dari server peretas di luar negeri.\n- **Caller ID Spoofing:** Layar HP Anda menampilkan panggilan masuk dari nomor resmi bank, padahal yang menelpon adalah sindikat penipu.",
            
            "typosquatting": "🔤 **Typosquatting (Pembajakan URL)**\n\nTyposquatting adalah jenis *social engineering* di mana penipu mendaftarkan nama domain yang memiliki kesalahan ejaan (typo) dari situs web populer.\n\n**Bagaimana Taktik Ini Bekerja?**\nPenipu bertaruh bahwa pengguna akan salah mengetik nama URL di *browser* atau tidak teliti saat mengeklik tautan. \n\n**Contoh Nyata:**\n- Bukannya `www.klikbca.com`, penipu menggunakan `www.kllikbca.com` (double L).\n- Bukannya `www.netflix.com`, penipu menggunakan `www.netfIix.com` (menggunakan huruf 'i' besar alih-alih 'L' kecil).",
            
            "brute force": "🔨 **Brute Force Attack (Serangan Membabi Buta)**\n\nBrute Force adalah metode peretasan yang paling kuno namun mematikan. Peretas menggunakan program komputer khusus (bot) untuk mencoba menebak *username* dan *password* Anda dengan mencoba jutaan kombinasi secara otomatis.\n\n**Bagaimana Menghindarinya?**\n1. **Gunakan sandi yang panjang:** Sandi 8 karakter bisa diretas dalam hitungan menit, tapi sandi 16 karakter butuh waktu ribuan tahun.\n2. **Gunakan 2FA:** Meskipun peretas berhasil menebak sandi Anda, mereka tetap tidak bisa masuk tanpa kode OTP dari HP Anda.",
            
            "malware": "🦠 **Malware (Malicious Software)**\n\nMalware adalah perangkat lunak atau kode yang sengaja dirancang untuk merusak, mengganggu, atau mencuri data dari komputer, server, atau jaringan komputer.\n\n**Jenis Malware Paling Berbahaya:**\n- **Ransomware:** Mengunci (men-enkripsi) file penting Anda dan meminta uang tebusan.\n- **Spyware:** Merekam aktivitas layar dan ketikan keyboard Anda (Keylogger) untuk mencuri kata sandi.\n- **Trojan:** Bersembunyi di dalam aplikasi bajakan yang seolah-olah terlihat berguna/aman.",
            
            "social engineering": "🧠 **Social Engineering (Rekayasa Sosial)**\n\nDalam dunia siber, tidak semua serangan melibatkan *coding* atau peretasan server. *Social Engineering* adalah seni memanipulasi kelemahan psikologis manusia agar korban secara sukarela menyerahkan data rahasia mereka.\n\n**Taktik Psikologis yang Dipakai:**\n- **Ketakutan:** \"Keluarga Anda kecelakaan, segera transfer uang!\"\n- **Keserakahan:** \"Anda menang undian 100 Juta, berikan PIN Anda untuk pencairan!\"\n- **Kepatuhan:** Menyamar sebagai atasan atau polisi untuk meminta data akses perusahaan.",
            
            "ransomware": "💀 **Ransomware (Malware Sandera)**\n\nRansomware adalah jenis *malware* yang akan mengenkripsi (mengunci) seluruh foto, dokumen, dan file di komputer Anda. Peretas kemudian akan meninggalkan pesan yang menuntut pembayaran (biasanya dalam Bitcoin) jika Anda ingin kunci pembukanya.\n\n**Fakta Penting:** Membayar tebusan tidak pernah menjamin file Anda akan dikembalikan. Cara terbaik menghadapinya adalah dengan rutin melakukan *backup* data ke *hard drive* eksternal.",
            
            "ddos": "💥 **DDoS (Distributed Denial of Service)**\n\nSerangan DDoS terjadi ketika peretas menggunakan ribuan komputer yang telah diretas (Botnet) untuk membanjiri sebuah situs web dengan *traffic* palsu secara bersamaan.\n\n**Analogi:** Bayangkan ada 10.000 orang palsu berdesakan masuk ke toko kecil pada saat bersamaan. Pembeli asli tidak akan bisa masuk, dan toko tersebut akhirnya lumpuh/tutup.",
            
            "mitm": "🕵️ **Man in the Middle (MitM) Attack**\n\nSerangan ini terjadi ketika *hacker* diam-diam menyusup di antara komunikasi Anda dan *website* yang Anda tuju (biasanya terjadi di jaringan Wi-Fi publik/kafe yang tidak dikunci).\n\n**Bahayanya:** Peretas bisa menguping dan mencuri segala sesuatu yang Anda ketik (termasuk *password* dan pesan pribadi) sebelum data itu sampai ke *server* tujuan. **Solusi:** Gunakan VPN jika memakai Wi-Fi publik.",
            
            "vpn": "🛡️ **VPN (Virtual Private Network)**\n\nVPN adalah layanan yang mengenkripsi jalur koneksi internet Anda dan menyembunyikan alamat IP asli Anda. \n\n**Fungsi Utama:** Melindungi Anda dari mata-mata (seperti serangan MitM) saat menggunakan jaringan publik, serta menjaga privasi dari penyedia layanan internet (ISP) Anda.",
            
            "enkripsi": "🔐 **Enkripsi (Encryption)**\n\nEnkripsi adalah proses mengacak data yang dapat dibaca (teks biasa) menjadi kode rahasia yang tidak dapat dibaca oleh siapa pun tanpa kunci pembukanya (dekripsi).\n\n**Contoh:** Pesan WhatsApp Anda dienkripsi secara *end-to-end*, artinya jika pesan tersebut disadap di tengah jalan, peretas hanya akan melihat rentetan huruf dan angka acak yang tidak masuk akal.",
            
            "2fa": "🔑 **2FA (Two-Factor Authentication)**\n\nAutentikasi Dua Langkah adalah gembok kedua untuk akun Anda. Selain membutuhkan kata sandi, Anda juga harus memasukkan bukti identitas kedua (seperti kode OTP dari SMS, aplikasi Google Authenticator, atau sidik jari).\n\nIni adalah pelindung paling ampuh: Bahkan jika *password* Anda bocor ke publik, *hacker* tetap tidak bisa *login* tanpa HP fisik Anda.",
            
            "keylogger": "⌨️ **Keylogger**\n\nKeylogger adalah *software* atau alat fisik yang diam-diam merekam setiap tombol yang Anda tekan di *keyboard* Anda. Ini sangat sering dipakai di warnet atau komputer publik untuk mencuri *username* dan *password* korban.",
            
            "doxing": "👁️ **Doxing (Document Dropping)**\n\nDoxing adalah tindakan menyebarkan informasi pribadi seseorang (nama asli, alamat rumah, KTP, nomor telepon, atau data keluarga) ke internet tanpa izin, biasanya dengan niat untuk mempermalukan, mengintimidasi, atau memeras korban.",
            
            "tips": "🛡️ **Panduan Komprehensif Keamanan Siber Pribadi:**\n\nBerikut adalah 5 langkah krusial untuk melindungi diri Anda di era digital:\n1. **Zero Trust (Jangan Mudah Percaya):** Jangan pernah memberikan kode OTP, PIN, atau *password* kepada siapa pun, bahkan kepada pihak yang mengaku sebagai pegawai bank atau keluarga.\n2. **Kewaspadaan Tautan (Link):** Biasakan mengecek ulang alamat situs (*URL*). Jangan langsung mengeklik *link* dari SMS/Email yang tidak diminta.\n3. **Kekuatan Kata Sandi:** Jangan gunakan tanggal lahir, nama hewan peliharaan, atau kata-kata umum di kamus. Gunakan *passphrase* (kombinasi beberapa kata acak).\n4. **Lapisan Keamanan Ganda (2FA/MFA):** Selalu aktifkan fitur Autentikasi Dua Langkah di WhatsApp, Instagram, dan aplikasi perbankan Anda.\n5. **Perbarui Perangkat:** Selalu lakukan *update* OS (*Operating System*) HP dan laptop Anda untuk menambal celah keamanan terbaru."
        }

    def detect_intent(self, text):
        """Mendeteksi fitur atau maksud pengguna."""
        # Jika teks panjang (lebih dari 10 kata), kemungkinan besar ini adalah teks phishing yang dipaste,
        # BUKAN perintah navigasi menu. Hindari false positive.
        if len(text.split()) > 10:
            return "UNKNOWN"
            
        text = text.lower()
        
        # Deteksi sapaan
        if re.search(self.intent_greeting, text):
            return "GREETING"
            
        # Deteksi pertanyaan edukasi (Jika ada kata tanya, prioritaskan sebagai pertanyaan)
        question_words = r"\b(apa|jelaskan|arti|maksud|bagaimana|gimana|tips|contoh|itu apa|adalah)\b"
        if re.search(question_words, text):
            return "EDUCATION"
            
        # Deteksi jawaban konfirmasi
        if re.search(self.intent_menu, text) or re.search(self.intent_other, text):
            return "OTHER_OPTIONS"
        if re.search(self.intent_yes, text):
            return "YES"
        if re.search(self.intent_suggest, text):
            return "SUGGEST_PASSWORD"
            
        # Deteksi fitur utama
        if re.search(self.intent_password, text):
            return "CHECK_PASSWORD"
        if re.search(self.intent_phishing, text):
            return "CHECK_PHISHING"
        if re.search(self.intent_link, text):
            return "CHECK_LINK"
        if re.search(self.intent_audit, text):
            return "AUDIT"
            
        return "UNKNOWN"

    def get_education_response(self, text):
        """Mencari penjelasan edukasi berdasarkan kata kunci."""
        text_lower = text.lower()
        responses = []
        
        # Khusus untuk "tips", kita periksa tanpa substring murni agar tidak terpicu sembarangan
        if "tips" in text_lower or "cara aman" in text_lower:
            responses.append(self.cyber_dictionary["tips"])
            
        for key, explanation in self.cyber_dictionary.items():
            if key != "tips" and key in text_lower:
                responses.append(explanation)
                
        if responses:
            return "💡 **Kamus Keamanan Siber:**\n\n" + "\n\n".join(responses)
        else:
            return "Maaf, saya tidak menemukan istilah siber tersebut di basis data saya. Coba tanyakan istilah populer lain seperti **Phishing**, **Spoofing**, **Typosquatting**, atau **Malware**."

    def generate_strong_password(self):
        """Menghasilkan kata sandi acak yang kuat."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        while True:
            password = ''.join(secrets.choice(alphabet) for i in range(16))
            if (any(c.islower() for c in password)
                    and any(c.isupper() for c in password)
                    and sum(c.isdigit() for c in password) >= 2
                    and any(c in "!@#$%^&*" for c in password)):
                return password

    def generate_fortified_password(self, base_word):
        """Membuat sandi kuat berdasarkan kata dasar dari pengguna."""
        base = base_word.strip().capitalize()
        if not base:
            return self.generate_strong_password()
            
        separator = secrets.choice(["-", "_", ".", "$", "@"])
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        
        # Cari suffix yang kuat
        while True:
            suffix = ''.join(secrets.choice(alphabet) for i in range(8))
            password = f"{base}{separator}{suffix}"
            if (any(c.islower() for c in password)
                    and any(c.isupper() for c in password)
                    and sum(c.isdigit() for c in password) >= 2
                    and any(c in "!@#$%^&*" for c in password)):
                return password

    def check_pwned_password(self, password):
        """Mengecek apakah password pernah bocor via HIBP API (k-Anonymity)."""
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1_hash[:5], sha1_hash[5:]
        try:
            url = f"https://api.pwnedpasswords.com/range/{prefix}"
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return 0
            hashes = (line.split(':') for line in response.text.splitlines())
            for h, count in hashes:
                if h == suffix:
                    return int(count)
            return 0
        except Exception:
            return 0

    def check_password_strength(self, password):
        """Mengevaluasi kata sandi dengan zxcvbn dan HIBP."""
        # 1. Cek Pwned
        pwned_count = self.check_pwned_password(password)
        
        # 2. Analisis zxcvbn
        result = zxcvbn(password)
        score = result['score']  # 0-4
        crack_time = result['crack_times_display']['offline_slow_hashing_1e4_per_second']
        
        feedback_list = []
        if result['feedback']['warning']:
            feedback_list.append(f"- **Peringatan:** {result['feedback']['warning']}")
        for sug in result['feedback']['suggestions']:
            feedback_list.append(f"- {sug}")

        return {
            'score': score,
            'pwned_count': pwned_count,
            'crack_time': crack_time,
            'feedback': feedback_list
        }

    def check_phishing(self, text):
        """Mengevaluasi teks untuk mendeteksi indikasi phishing."""
        text_raw = text.strip()
        text_lower = text_raw.lower()
        score = 0
        feedback = []

        # 1. Validasi Input Pendek / Ngasal
        words = text_raw.split()
        if len(words) < 3:
            return {
                'valid': False,
                'error_msg': "Teks terlalu pendek atau tidak mengandung struktur kalimat. Mohon salin seluruh isi pesan yang Anda curigai."
            }

        # 2. Validasi Hanya Email
        # Menggunakan regex email dasar
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if re.match(email_pattern, text_raw):
            return {
                'valid': False,
                'error_msg': "Anda hanya memberikan alamat email. Untuk analisis taktik penipuan, mohon lampirkan juga isi pesan email tersebut."
            }

        # 3. Analisis Pengirim (Spoofing)
        # Jika mengandung nama institusi besar tapi juga mengandung email gratisan
        institutions = r"\b(bca|mandiri|bri|bni|netflix|shopee|tokopedia|gojek|grab|dana|ovo)\b"
        free_emails = r"\b(gmail\.com|yahoo\.com|hotmail\.com|outlook\.com)\b"
        
        has_institution = re.search(institutions, text_lower)
        has_free_email = re.search(free_emails, text_lower)
        
        if has_institution and has_free_email:
            score += 50
            feedback.append("🎭 **Pemalsuan Identitas (Spoofing):** Pesan menyebut institusi resmi tetapi menggunakan domain email gratisan (@gmail/@yahoo). Institusi resmi TIDAK PERNAH menggunakan email gratisan.")

        # 4. Deteksi urgensi / ancaman
        urgency_keywords = r"\b(segera|blokir|penting|dibekukan|batas waktu|ditutup|ancaman|peringatan|hangus|ditangguhkan)\b"
        if re.search(urgency_keywords, text_lower):
            score += 30
            feedback.append("⚠️ **Taktik Tekanan Psikologis:** Terdapat unsur urgensi/ancaman untuk membuat Anda panik dan bertindak tanpa berpikir panjang.")

        # 5. Deteksi iming-iming hadiah
        reward_keywords = r"\b(menang|hadiah|selamat|gratis|bonus|undian|klaim|cair|pemenang)\b"
        if re.search(reward_keywords, text_lower):
            score += 30
            feedback.append("🎣 **Taktik Iming-iming:** Penipuan sering memancing korban menggunakan iming-iming hadiah uang atau barang gratis.")

        # 6. Permintaan informasi sensitif / link berbahaya
        sensitive_keywords = r"\b(password|kata sandi|sandi|otp|pin|klik tautan|klik link|login|verifikasi|perbarui data|update|konfirmasi)\b"
        if re.search(sensitive_keywords, text_lower):
            score += 40
            feedback.append("🔐 **Pencurian Kredensial:** Pesan mengarahkan Anda untuk mengeklik tautan verifikasi atau meminta data sensitif. Bank resmi tidak meminta OTP/PIN via link SMS/Email.")
            
        # 7. Gaya Penulisan (Penggunaan Kapital Berlebihan)
        # Menghitung persentase huruf kapital
        if len(text_raw) > 20:
            caps_count = sum(1 for c in text_raw if c.isupper())
            if caps_count / len(text_raw) > 0.4:
                score += 20
                feedback.append("✍️ **Anomali Gaya Teks:** Penggunaan HURUF KAPITAL yang berlebihan sering dipakai oleh penipu untuk menekankan kepanikan.")

        # 8. Deteksi Link Tersembunyi (Ekstraksi URL/Domain)
        # Mencari pola yang mirip URL atau domain
        url_pattern = r"(https?://[^\s]+|www\.[^\s]+)"
        urls_found = re.findall(url_pattern, text_lower)
        if urls_found:
            for url in urls_found:
                # Cek jika link menggunakan nama institusi tapi ekstensinya aneh (typosquatting)
                if re.search(institutions, url) and not re.search(r"\.(co\.id|com|id)\b", url):
                    score += 50
                    feedback.append(f"🔗 **Tautan Palsu (Typosquatting):** Ditemukan tautan yang menyamar sebagai institusi resmi (`{url}`). Bank resmi selalu menggunakan `.com` atau `.co.id`.")
                # Cek jika ada ekstensi yang sering dipakai untuk penipuan
                elif re.search(r"\.(cum|xyz|top|online|site|club|tk|ml)\b", url):
                    score += 40
                    feedback.append(f"🔗 **Domain Berbahaya:** Teks ini menyembunyikan tautan dengan akhiran domain yang tidak wajar dan murah (`{url}`).")

        # Normalisasi skor maksimal 100
        score = min(score, 100)

        risk_level = "Aman"
        if score >= 70:
            risk_level = "🔴 **Sangat Berbahaya (Phishing)**"
        elif score >= 30:
            risk_level = "🟡 **Mencurigakan**"
        else:
            risk_level = "🟢 **Cenderung Aman**"

        return {
            'valid': True,
            'score': score,
            'risk_level': risk_level,
            'feedback': feedback
        }

    def check_link(self, url):
        """Mengevaluasi tautan untuk mendeteksi potensi bahaya menggunakan analisis heuristik."""
        import urllib.parse
        
        url_raw = url.strip()
        url_lower = url_raw.lower()
        score = 0
        feedback = []

        # Validasi input sederhana
        if "." not in url_lower and "localhost" not in url_lower:
            return {
                'valid': False,
                'error_msg': "Input tidak terlihat seperti tautan (URL). Mohon masukkan tautan yang valid."
            }

        # Pastikan ada skema untuk parsing
        if not url_lower.startswith("http://") and not url_lower.startswith("https://"):
            parsed_url = urllib.parse.urlparse("http://" + url_raw)
        else:
            parsed_url = urllib.parse.urlparse(url_raw)

        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()

        # 1. Cek protokol HTTP
        if url_lower.startswith("http://"):
            score += 30
            feedback.append("🔓 **Koneksi Tidak Aman:** Tautan menggunakan HTTP, bukan HTTPS. Data Anda tidak dienkripsi dan rawan disadap.")

        # 2. Cek URL Shortener
        shorteners = r"^(bit\.ly|tinyurl\.com|s\.id|goo\.gl|t\.co|ow\.ly|is\.gd|buff\.ly|cutt\.ly)$"
        if re.match(shorteners, domain):
            score += 40
            feedback.append("🔗 **Tautan Tersembunyi (URL Shortener):** Ini adalah pemendek tautan yang sering dipakai untuk menyembunyikan alamat asli situs berbahaya.")

        # 3. Cek Typosquatting / Sub-domain abuse
        institutions = r"(bca|mandiri|bri|bni|netflix|shopee|tokopedia|gojek|grab|dana|ovo)"
        # Misal: bca.co.id.login-update.com (root domainnya login-update.com)
        parts = domain.split('.')
        if len(parts) >= 3:
            subdomain = ".".join(parts[:-2])
            root_domain = ".".join(parts[-2:])
            if re.search(institutions, subdomain) and not re.search(r"(co\.id|com|id|go\.id)$", root_domain):
                score += 50
                feedback.append(f"🎭 **Pemalsuan Sub-Domain:** Tautan ini mencoba mengecoh Anda. Nama aslinya adalah `{root_domain}`, BUKAN `{subdomain}`.")

        # 4. Deteksi ekstensi domain aneh (Suspicious TLD)
        suspicious_tlds = r"\.(xyz|top|online|site|club|tk|ml|cum|vip|buzz)$"
        if re.search(suspicious_tlds, domain):
            score += 40
            feedback.append("🚩 **Domain Mencurigakan:** Menggunakan ekstensi domain murah/gratisan yang sangat sering dipakai untuk penipuan.")

        # 5. Cek format IP Address
        ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$"
        if re.match(ip_pattern, domain):
            score += 40
            feedback.append("🖥️ **Alamat IP Langsung:** Tautan mengarah langsung ke alamat IP. Website resmi menggunakan nama domain.")

        # 6. Panjang URL Tidak Wajar
        if len(url_raw) > 75:
            score += 20
            feedback.append("📏 **Tautan Terlalu Panjang:** Panjang tautan ini tidak wajar. Seringkali dipakai agar domain asli tersembunyi/terpotong di layar HP.")

        # 7. Cek kata kunci mencurigakan di path atau domain
        suspicious_keywords = r"(login|update|verify|secure|free|account|banking|admin|support|recover|password)"
        if re.search(suspicious_keywords, url_lower):
            score += 20
            feedback.append("🎣 **Kata Kunci Pancingan:** Terdapat kata seperti 'login' atau 'verify' yang sering dipakai penipu untuk membuat tautan seolah-olah halaman resmi.")

        # Normalisasi skor
        score = min(score, 100)

        risk_level = "Aman"
        if score >= 70:
            risk_level = "🔴 **Sangat Berbahaya (Malicious)**"
        elif score >= 30:
            risk_level = "🟡 **Mencurigakan**"
        else:
            risk_level = "🟢 **Cenderung Aman**"

        return {
            'valid': True,
            'score': score,
            'risk_level': risk_level,
            'feedback': feedback
        }