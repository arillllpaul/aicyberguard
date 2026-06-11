import streamlit as st
import time
from FSM import CyberGuardFSM

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="CyberGuard", page_icon="✺", layout="wide", initial_sidebar_state="expanded")

# --- 2. KUSTOMISASI CSS GAYA CLAUDE ---
st.markdown("""
    <style>
    /* Latar belakang bergradasi dan beranimasi halus (Ramai tapi elegan) */
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stApp { 
        background: linear-gradient(-45deg, #ffffff, #e0f2fe, #bae6fd, #7dd3fc);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #0f172a; 
    }
    
    /* Menyembunyikan elemen bawaan Streamlit */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display: none;}
    header {background-color: transparent !important;}
    
    /* GAYA SAMBUTAN BERANIMASI */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }
    .claude-greeting {
        text-align: center; 
        font-family: 'Inter', 'Segoe UI', sans-serif; 
        font-weight: 800; 
        font-size: 3.5rem; 
        margin-top: 10vh;
        margin-bottom: 0.5rem;
        background: -webkit-linear-gradient(45deg, #1e3a8a, #3b82f6, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: float 4s ease-in-out infinite;
        text-shadow: 0px 10px 20px rgba(0,0,0,0.05);
    }
    .claude-subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 3rem;
        font-weight: 500;
    }
    
    /* GAYA TOMBOL PIL MODERN (PILL BUTTONS) */
    .stButton>button {
        border-radius: 50px !important; 
        border: 1px solid rgba(255,255,255,0.6) !important;
        background: rgba(255, 255, 255, 0.8) !important;
        color: #334155 !important;
        padding: 12px 24px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05), inset 0 1px 0 rgba(255,255,255,1) !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .stButton>button:hover {
        transform: translateY(-4px) scale(1.03) !important;
        box-shadow: 0 12px 25px rgba(79, 70, 229, 0.2) !important;
        color: #4f46e5 !important;
        border-color: #c7d2fe !important;
    }
    .stButton>button:active {
        transform: translateY(1px) !important;
    }
    
    /* GAYA PANEL SAMPING (SIDEBAR) BERSIH & ELEGAN */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 2px 0 15px rgba(0,0,0,0.03) !important;
    }
    
    /* Kembalikan warna teks menjadi gelap */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div {
        color: #1e293b !important;
    }
    
    /* Gaya kotak alert/status di sidebar yang kalem */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: #f0fdfa !important; 
        border: 1px solid #ccfbf1 !important;
        border-radius: 12px !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] * {
        color: #0f766e !important;
    }
    
    /* Tombol elegan di sidebar */
    [data-testid="stSidebar"] button {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        color: #334155 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
    }
    [data-testid="stSidebar"] button:hover {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
        color: #4f46e5 !important;
    }/* --- Hapus styling lama --- */
    </style>
""", unsafe_allow_html=True)

# --- 3. INISIALISASI FSM & RIWAYAT ---
if 'bot' not in st.session_state:
    st.session_state.bot = CyberGuardFSM()

if "messages" not in st.session_state:
    st.session_state.messages = []

if 'show_detail' not in st.session_state:
    st.session_state.show_detail = False

if 'show_audit' not in st.session_state:
    st.session_state.show_audit = False

if 'audit_index' not in st.session_state:
    st.session_state.audit_index = 0

if 'audit_answers' not in st.session_state:
    st.session_state.audit_answers = []

# --- BANK SOAL AUDIT ---
audit_questions = [
    {
        "q": "1. Apakah Anda menggunakan kata sandi yang persis sama untuk lebih dari satu akun penting (misal: sandi Instagram sama dengan sandi Email)?",
        "btn_risk": "Ya, saya pakai sandi yang sama",
        "btn_safe": "Tidak, sandi saya berbeda-beda",
        "advice": "- ⚠️ Anda menggunakan **sandi yang sama** untuk banyak akun. Jika satu bocor, semua akun tamat. Saran: Gunakan aplikasi *Password Manager*."
    },
    {
        "q": "2. Apakah Anda sudah mengaktifkan fitur Autentikasi Dua Langkah (2FA/OTP) pada aplikasi penting Anda seperti WhatsApp dan Mobile Banking?",
        "btn_safe": "Sudah diaktifkan",
        "btn_risk": "Belum/Tidak tahu",
        "advice": "- ⚠️ Akun Anda **belum diproteksi 2FA**. Meskipun sandi Anda rumit, akun tetap mudah diretas jika password bocor. Saran: Segera aktifkan 2FA."
    },
    {
        "q": "3. Seberapa sering Anda menyambungkan HP/Laptop ke Wi-Fi publik gratis (di kafe/bandara) untuk membuka hal sensitif tanpa VPN?",
        "btn_risk": "Sering / Pernah",
        "btn_safe": "Tidak Pernah",
        "advice": "- ⚠️ Menggunakan **Wi-Fi Publik** sangat rentan disadap (*Man-in-the-Middle Attack*). Saran: Instal aplikasi VPN terpercaya sebelum memakai Wi-Fi publik."
    },
    {
        "q": "4. Pernahkah Anda mengeklik sebuah link dari SMS atau Email yang pengirimnya tidak Anda kenal (misal: link pelacakan paket kurir)?",
        "btn_risk": "Pernah",
        "btn_safe": "Tidak Pernah",
        "advice": "- ⚠️ **Mengeklik link sembarangan** adalah pintu masuk utama Malware pencuri OTP. Saran: Jangan pernah asal klik link tak dikenal."
    },
    {
        "q": "5. Ketika HP atau Laptop Anda meminta untuk melakukan pembaruan sistem operasi (Update OS), apakah Anda sering menundanya?",
        "btn_risk": "Ya, saya sering menunda",
        "btn_safe": "Tidak, saya langsung update",
        "advice": "- ⚠️ **Menunda update** sama dengan membiarkan pintu rumah Anda rusak karena update berisi tambalan anti-virus terbaru. Saran: Rutinlah melakukan Update OS."
    }
]

# Fungsi pembantu untuk tombol pintasan
def jalankan_perintah_tombol(teks_instruksi):
    st.session_state.messages.append({"role": "user", "content": teks_instruksi})
    st.session_state.bot.step(teks_instruksi)
    st.session_state.messages.append({"role": "assistant", "content": st.session_state.bot.get_response()})
    st.rerun()

# Fungsi pembuat PDF
def generate_pdf_bytes(report_text):
    import markdown
    from fpdf import FPDF
    import datetime
    
    clean_text = report_text.encode('latin-1', 'ignore').decode('latin-1')
    html_text = markdown.markdown(clean_text)
    
    class PDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 14)
            self.cell(0, 10, "CYBERGUARD - LAPORAN ANALISIS SISTEM", ln=True, align="C")
            self.set_font("Helvetica", "I", 10)
            self.set_text_color(100, 100, 100)
            now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cell(0, 10, f"Dicetak pada: {now_str}", ln=True, align="C")
            self.line(10, 30, 200, 30)
            self.ln(10)
            
        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, "Dokumen ini di-generate secara otomatis oleh CyberGuard AI Assistant.", align="C")

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(0, 0, 0)
    pdf.write_html(html_text)
    return bytes(pdf.output())

# --- 4. PANEL SAMPING (SIDEBAR CLAUDE) ---
with st.sidebar:
    # Tombol "Chat baru" diletakkan di paling atas seperti di Claude
    if st.button("➕ Chat baru", use_container_width=True):
        st.session_state.bot.__init__() # Reset logika FSM
        st.session_state.messages = []  # Kosongkan layar
        st.rerun()
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("Mode Saat Ini")
    
    # Pemetaan state FSM ke nama mode yang mudah dibaca
    state_map = {
        "IDLE": "🏠 Menu Utama",
        "PASSWORD_CHECK": "🔑🛡️ Cek Kekuatan Sandi",
        "WAIT_RETRY_PASSWORD": "🔑🛡️ Cek Kekuatan Sandi",
        "PHISHING_CHECK": "✉️🎣 Cek Email Phishing",
        "WAIT_RETRY_PHISHING": "✉️🎣 Cek Email Phishing",
        "LINK_CHECK": "🔗🌐 Deteksi Link Berbahaya",
        "WAIT_RETRY_LINK": "🔗🌐 Deteksi Link Berbahaya"
    }
    current_state_name = st.session_state.bot.state.name
    friendly_mode = state_map.get(current_state_name, current_state_name)
    
    st.info(f"**{friendly_mode}**")
    
    # Menampilkan hasil analisis terakhir di sidebar (jika ada)
    if hasattr(st.session_state.bot, 'latest_result_summary') and st.session_state.bot.latest_result_summary:
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("📋 Hasil Analisis Terakhir")
        # Menggunakan st.success atau container dengan border agar rapi
        with st.container(border=True):
            st.markdown(st.session_state.bot.latest_result_summary)
            
        if st.button("🔍 Lihat Layar Penuh", use_container_width=True):
            st.session_state.show_detail = True
            st.rerun()

# --- 5. TAMPILAN UTAMA (KONDISIONAL DETAIL ATAU CHAT ATAU AUDIT) ---
if st.session_state.get('show_audit', False):
    st.markdown("## 📊 Audit Keamanan Pribadi")
    st.info("Mari periksa seberapa tangguh kebiasaan keamanan digital Anda. Jawab dengan jujur!")
    
    if st.session_state.audit_index < len(audit_questions):
        q_data = audit_questions[st.session_state.audit_index]
        
        with st.container(border=True):
            st.markdown(f"#### {q_data['q']}")
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button(q_data['btn_risk'], use_container_width=True, key=f"risk_{st.session_state.audit_index}"):
                    st.session_state.audit_answers.append(False) # False = berisiko
                    st.session_state.audit_index += 1
                    st.rerun()
            with col_b:
                if st.button(q_data['btn_safe'], use_container_width=True, key=f"safe_{st.session_state.audit_index}"):
                    st.session_state.audit_answers.append(True) # True = aman
                    st.session_state.audit_index += 1
                    st.rerun()
    else:
        # Layar Rapor Akhir
        safe_count = sum(st.session_state.audit_answers)
        score = int((safe_count / len(audit_questions)) * 100)
        
        status_text = ""
        if score >= 80:
            status_text = "AMAN"
            st.success(f"### 🩺 Skor Kesehatan Siber Anda: {score}/100 (AMAN 🟢)")
        elif score >= 60:
            status_text = "WASPADA"
            st.warning(f"### 🩺 Skor Kesehatan Siber Anda: {score}/100 (WASPADA 🟡)")
        else:
            status_text = "BAHAYA"
            st.error(f"### 🩺 Skor Kesehatan Siber Anda: {score}/100 (BAHAYA 🔴)")
            
        st.markdown("---")
        st.markdown("#### 💡 Rekomendasi Khusus Untuk Anda:")
        
        perfect = True
        recommendations = []
        for i, is_safe in enumerate(st.session_state.audit_answers):
            if not is_safe:
                perfect = False
                advice = audit_questions[i]['advice']
                st.markdown(advice)
                recommendations.append(advice)
                
        if perfect:
            msg = "Luar biasa! Pertahankan kebiasaan digital sehat Anda. Tidak ada celah keamanan yang fatal ditemukan."
            st.info(msg)
            recommendations.append(f"- {msg}")
            
        # Simpan ke Sidebar dan Memori Utama
        report_full = f"### SKOR KESEHATAN SIBER: {score}/100 ({status_text})\n\n#### REKOMENDASI AUDIT:\n"
        for rec in recommendations:
            report_full += f"{rec}\n\n"
            
        st.session_state.bot.latest_result_summary = f"📋 Audit Keamanan Selesai (Skor: {score}/100)"
        st.session_state.bot.latest_result_full = report_full
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Kembali ke Menu Utama", use_container_width=True):
                st.session_state.show_audit = False
                st.rerun()
        with col2:
            try:
                pdf_bytes = generate_pdf_bytes(report_full)
                st.download_button(
                    label="📥 Unduh Rapor (.pdf)",
                    data=pdf_bytes,
                    file_name="Rapor_Audit_CyberGuard.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Gagal memproses PDF: {str(e)}")

elif st.session_state.show_detail:
    st.markdown("## 📋 Detail Hasil Analisis")
    st.info(st.session_state.bot.latest_result_full)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1.5])
    with col1:
        if st.button("⬅️ Kembali ke Chat", use_container_width=True):
            st.session_state.show_detail = False
            st.rerun()
    with col2:
        if st.button("🔄 Reset Chat Baru", use_container_width=True):
            st.session_state.show_detail = False
            st.session_state.bot.__init__()
            st.session_state.messages = []
            st.rerun()
    with col3:
        report_text = f"# LAPORAN ANALISIS CYBERGUARD\n\n{st.session_state.bot.latest_result_full}\n\n---\n*Digenerate oleh CyberGuard AI Assistant*"
        try:
            pdf_bytes = generate_pdf_bytes(report_text)
            st.download_button(
                label="📥 Unduh Laporan (.pdf)",
                data=pdf_bytes,
                file_name="Laporan_CyberGuard.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Gagal memproses PDF: {str(e)}")

elif not st.session_state.messages:
    # Teks Sambutan Gaya Baru (Gradien, Elegan, dan Ramai)
    st.markdown("""
        <div class='claude-greeting'>🛡️ CyberGuard</div>
        <div class='claude-subtitle'>Asisten Keamanan Siber Pribadi Anda. Apa yang ingin Anda periksa hari ini?</div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Tombol Pil (Pill Buttons) di tengah layar
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("✉️🎣 Cek Email Phishing", use_container_width=True):
            jalankan_perintah_tombol("cek phishing")
    with col2:
        if st.button("🔑🛡️ Cek Kekuatan Sandi", use_container_width=True):
            jalankan_perintah_tombol("cek kekuatan password")
    with col3:
        if st.button("🔗🌐 Deteksi Tautan/Link", use_container_width=True):
            jalankan_perintah_tombol("cek link")
    with col4:
        if st.button("📊🩺 Audit Keamanan", use_container_width=True):
            st.session_state.show_audit = True
            st.session_state.audit_index = 0
            st.session_state.audit_answers = []
            st.rerun()

# --- 6. RENDER RIWAYAT OBROLAN (HTML KUSTOM KANAN-KIRI) ---
else:
    import markdown
    for message in st.session_state.messages:
        if message["role"] == "user":
            safe_content = str(message["content"]).replace('<', '&lt;').replace('>', '&gt;')
            html_user = f"""<div style="display: flex; justify-content: flex-end; margin-bottom: 20px; align-items: flex-end;">
<div style="background: linear-gradient(135deg, #6C63FF, #4834d4); color: white; padding: 15px 20px; border-radius: 20px 20px 0px 20px; max-width: 80%; box-shadow: 0px 4px 15px rgba(108, 99, 255, 0.2); font-family: 'Inter', sans-serif; font-size: 1rem; word-break: break-word;">
{safe_content}
</div>
<div style="margin-left: 15px; font-size: 28px; line-height: 1;">👤</div>
</div>"""
            st.markdown(html_user, unsafe_allow_html=True)
        else:
            bot_html = markdown.markdown(message["content"])
            html_bot = f"""
            <div style="display: flex; justify-content: flex-start; margin-bottom: 20px; align-items: flex-end;">
                <div style="margin-right: 15px; font-size: 28px; line-height: 1;">🛡️</div>
                <div style="background: white; color: #2d3436; padding: 15px 20px; border-radius: 20px 20px 20px 0px; max-width: 80%; box-shadow: 0px 4px 15px rgba(0,0,0,0.05); border: 1px solid #f1f3f5; font-family: 'Inter', sans-serif; font-size: 1rem;">
                    {bot_html}
                </div>
            </div>
            """
            st.markdown(html_bot, unsafe_allow_html=True)

# --- 7. KOTAK INPUT BAWAH (HANYA MUNCUL JIKA TIDAK DI LAYAR DETAIL/AUDIT) ---
if not st.session_state.show_detail and not st.session_state.get('show_audit', False):
    # --- TOMBOL PILIHAN CEPAT (SHORTCUT) ---
    current_state = st.session_state.bot.state.name
    if current_state == "WAIT_RETRY_PASSWORD":
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            if st.button("💡✨ Saran Sandi Baru", use_container_width=True):
                jalankan_perintah_tombol("saran")
        with col2:
            if st.button("🔑🔄 Cek Password Lagi", use_container_width=True):
                jalankan_perintah_tombol("ya")
        with col3:
            if st.button("🏠🔙 Pilihan Lainnya", use_container_width=True):
                jalankan_perintah_tombol("pilihan lainnya")
    elif current_state in ["WAIT_RETRY_PHISHING", "WAIT_RETRY_LINK"]:
        st.markdown("<br>", unsafe_allow_html=True)
        if current_state == "WAIT_RETRY_PHISHING":
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("🔄🔍 Cek Lagi", use_container_width=True):
                    jalankan_perintah_tombol("ya")
            with col2:
                if st.button("🛡️🚨 Cara Melapor", use_container_width=True):
                    jalankan_perintah_tombol("cara lapor")
            with col3:
                if st.button("🏠🔙 Pilihan Lainnya", use_container_width=True):
                    jalankan_perintah_tombol("pilihan lainnya")
        else:
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("🔄🔍 Cek Lagi", use_container_width=True):
                    jalankan_perintah_tombol("ya")
            with col2:
                if st.button("🏠🔙 Pilihan Lainnya", use_container_width=True):
                    jalankan_perintah_tombol("pilihan lainnya")

    if prompt := st.chat_input("Ketik di sini... (Contoh: 'mau cek password' atau 'mulai audit')"):
        # Tambahkan ke riwayat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Proses di latar belakang
        st.session_state.bot.step(prompt)
        bot_reply = st.session_state.bot.get_response()
        
        if bot_reply == "TRIGGER_AUDIT":
            st.session_state.show_audit = True
            st.session_state.audit_index = 0
            st.session_state.audit_answers = []
            bot_reply = "✅ Membuka halaman Audit Keamanan Pribadi..."
            
        # Simpan balasan bot dan rerun (HTML renderer di atas akan otomatis me-render)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        st.rerun()