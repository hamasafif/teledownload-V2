import os
import time
import asyncio
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from tkinter import Tk, filedialog
from tqdm import tqdm

# Load konfigurasi dari .env
load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = os.getenv("SESSION_NAME", "anon")

# Header ASCII
def tampilkan_header():
    print(r"""
████████╗███████╗██╗     ███████╗██████╗  ██████╗ ██╗    ██╗███╗   ██╗██╗      ██████╗  █████╗ ██████╗ 
╚══██╔══╝██╔════╝██║     ██╔════╝██╔══██╗██╔═══██╗██║    ██║████╗  ██║██║     ██╔═══██╗██╔══██╗██╔══██╗
   ██║   █████╗  ██║     █████╗  ██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║██║     ██║   ██║███████║██║  ██║
   ██║   ██╔══╝  ██║     ██╔══╝  ██║  ██║██║   ██║██║███╗██║██║╚██╗██║██║     ██║   ██║██╔══██║██║  ██║
   ██║   ███████╗███████╗███████╗██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║███████╗╚██████╔╝██║  ██║██████╔╝
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝                                                                            
    """)
    print("Created by WR JUNIOR\n")

# Reset session jika diminta
if os.path.exists(f"{session_name}.session"):
    jawab = input("Ingin menghapus session lama? (y/n): ").strip().lower()
    if jawab == 'y':
        os.remove(f"{session_name}.session")
        print("✅ Session berhasil dihapus. Silakan login ulang nanti.\n")

# Pilih folder
def pilih_folder():
    folder = input("Masukkan path folder tujuan untuk menyimpan file: ").strip()
    if os.path.isdir(folder):
        return folder
    else:
        print("❌ Folder tidak valid.")
        return None

# Update progress bar
def update_progress(downloaded, total, pbar, start_time):
    elapsed_time = time.time() - start_time
    percent = (downloaded / total) * 100 if total else 0
    pbar.update(percent - pbar.n)
    if elapsed_time > 0:
        speed = downloaded / 1024 / 1024 / elapsed_time
        pbar.set_postfix_str(f"Kecepatan: {speed:.2f} MB/s")

# Fungsi utama
async def download_gambar():
    async with TelegramClient(session_name, api_id, api_hash) as client:
        tampilkan_header()
        print("✅ Login berhasil.\n")

        dialogs = await client.get_dialogs()
        dialogs = sorted(dialogs, key=lambda d: d.name.lower())

        print("Daftar Channel:")
        for i, d in enumerate(dialogs, start=1):
            print(f"{i}. {d.name}")

        try:
            pilihan = int(input("\nPilih nomor channel: ").strip())
            target = dialogs[pilihan - 1].entity
        except:
            print("❌ Pilihan tidak valid.")
            return

        folder = pilih_folder()
        if not folder:
            return

        print("\n🔍 Mendeteksi gambar (.jpg/.jpeg)...")
        messages = []

        async for msg in client.iter_messages(target, reverse=True):  # reverse=True: dari lama ke baru
            if isinstance(msg.media, MessageMediaPhoto):
                messages.append(msg)
            elif isinstance(msg.media, MessageMediaDocument):
                if msg.media.document.mime_type in ["image/jpeg", "image/jpg"]:
                    messages.append(msg)

        print(f"✅ Ditemukan {len(messages)} gambar.\n")

        for i, msg in enumerate(messages, start=1):  # TIDAK dibalik di sini, jadi urutannya benar
            filename = f"Gambar - {str(i).zfill(3)}.jpg"
            path = os.path.join(folder, filename)

            if os.path.exists(path) and os.path.getsize(path) > 0:
                print(f"✅ Lewati (sudah ada): {filename}")
                continue

            print(f"⬇️  Mengunduh {filename}...")
            start_time = time.time()
            try:
                with tqdm(total=100, desc=filename, unit='%', ncols=100) as pbar:
                    await client.download_media(
                        msg,
                        file=path,
                        progress_callback=lambda d, t: update_progress(d, t, pbar, start_time)
                    )
                print(f"✅ Selesai: {filename}\n")
            except Exception as e:
                print(f"❌ Gagal: {e}\n")

if __name__ == "__main__":
    asyncio.run(download_gambar())
