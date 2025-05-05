# 🚀 TELEDOWNLOAD  
**🔧 Create by WR JUNIOR**

TELEDOWNLOAD adalah alat berbasis Python yang memungkinkan kamu untuk **mengunduh media spesifik (seperti .mp4, .pdf, .doc, .jpeg, dll)** dari channel Telegram dengan mudah dan cepat.  
Dengan antarmuka terminal yang interaktif dan mendukung pemilihan folder penyimpanan, aplikasi ini sangat cocok digunakan untuk backup media pribadi dari channel Telegram.

---

## 🧰 Fitur Unggulan
- ✅ Login ke Telegram dengan aman
- 📜 Tampilkan daftar channel/obrolan (10 per halaman)
- 🎯 Pilih ekstensi file tertentu yang ingin diunduh (.mp4, .pdf, dll)
- 🗂 Tentukan folder tujuan penyimpanan file
- 🔢 Atur jumlah file & urutan unduhan
- 🔄 Resume otomatis jika file sudah ada
- 🔁 Fitur reset session (login akun lain)
- 💬 Dukungan antarmuka ASCII Art

---

## ⚙️ Instalasi

### 1. Clone Repositori

```bash
git clone https://github.com/USERNAME/teledownload.git
cd teledownload

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

API_ID=YOUR_API_ID
API_HASH=YOUR_API_HASH
SESSION_NAME=teledownload

python3 telegram_media_downloader.py/
