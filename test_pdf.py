import markdown
import re
from fpdf import FPDF

def remove_emojis(text):
    # Pola untuk menghapus sebagian besar emoji Unicode
    return re.sub(r'[^\w\s.,;:!?()\[\]{}""''\-+*/=<>@#&%`$|\\~^]', '', text)

def generate_pdf(markdown_text):
    clean_text = remove_emojis(markdown_text)
    html_text = markdown.markdown(clean_text)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    # Gunakan write_html
    pdf.write_html(html_text)
    pdf.output("test_report.pdf")
    print("PDF Generated!")

sample = """# Hasil Analisis Tautan
🔴 **Sangat Berbahaya (Malicious)** (Skor Risiko: 70/100)

**Laporan Analisis Taktik:**
- 🔓 **Koneksi Tidak Aman:** Tautan menggunakan HTTP, bukan HTTPS. Data Anda tidak dienkripsi dan rawan disadap.
- 🖥️ **Alamat IP Langsung:** Tautan mengarah langsung ke alamat IP. Website resmi menggunakan nama domain.

---
*Digenerate oleh CyberGuard AI Assistant*
"""

generate_pdf(sample)
