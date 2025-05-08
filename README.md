# 📺 TeleVid - Telegram Video Downloader

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20WSL-lightgrey)

> 🔥 **TeleVid** adalah alat downloader video dari channel Telegram, dengan fitur lanjutan seperti pemilihan durasi minimum video, resume download otomatis, urutan mulai, dan jeda otomatis. Semua dirancang untuk mendukung efisiensi dan stabilitas saat mengunduh ratusan video.

---

## 🚀 Fitur Unggulan

✅ Hanya mendownload **video & Gambar**, bukan dokumen lain  
✅ Filter berdasarkan **durasi minimum video** (misalnya hanya video di atas 5 menit)  
✅ Tentukan **jumlah video** yang ingin diunduh  
✅ Tentukan **urutan keberapa** video dimulai  
✅ Otomatis **melanjutkan unduhan** jika sebelumnya terputus  
✅ Terdapat sistem **file sementara (.part)** untuk mendeteksi file yang belum selesai  
✅ **Jeda otomatis** setiap 20 video selama 60 detik untuk menghindari pembatasan Telegram  
✅ Opsi **reset session** jika ingin login ulang  
✅ GUI untuk memilih folder download (dengan `Tkinter`)  
✅ Tampilan **progress bar** dengan kecepatan real-time

---

## 💻 Cara Installasi

1. **Clone repositori ini**:
   ```bash
   git clone https://github.com/kamu/televid.git
   cd televid

Buat virtual environment (opsional tapi disarankan):

python3 -m venv venv
source venv/bin/activate  # untuk Linux/macOS
venv\Scripts\activate     # untuk Windows
Install dependensi:
pip install -r requirements.txt

Buat file .env di direktori utama dan isi dengan API Telegram kamu:

API_ID=123456
API_HASH=abcdef1234567890abcdef1234567890
SESSION_NAME=televid
Jalankan script:

python televid.py



❓ FAQ
Q: Apakah hanya bisa digunakan untuk video?
✅ Ya, hanya file video Telegram (bukan gambar, dokumen, atau voice note).

Q: Apakah bisa resume download jika sebelumnya terputus?
✅ Ya, selama file .part masih ada, program akan melanjutkan unduhan sebelumnya.

Q: Apakah bisa digunakan di Windows, Linux, atau WSL?
✅ Bisa digunakan di semua OS yang mendukung Python dan Telegram API.

🛡️ License
MIT License — bebas digunakan untuk keperluan pribadi maupun komersial.

✨ Kontribusi
Pull Request dan saran sangat terbuka. Silakan fork dan submit perbaikan jika menemukan bug atau punya ide fitur baru!
