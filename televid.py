import os
import time
import asyncio
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.types import DocumentAttributeVideo
from tqdm import tqdm

# Load konfigurasi dari .env
load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = os.getenv("SESSION_NAME", "anon")

# Header
print("""
 $$$$$$$$\ $$$$$$$$\ $$\       $$$$$$$$\ $$$$$$$\   $$$$$$\  $$\      $$\ $$\   $$\ $$\       $$$$$$\   $$$$$$\  $$$$$$$\  
\__$$  __|$$  _____|$$ |      $$  _____|$$  __$$\ $$  __$$\ $$ | $\  $$ |$$$\  $$ |$$ |     $$  __$$\ $$  __$$\ $$  __$$\ 
   $$ |   $$ |      $$ |      $$ |      $$ |  $$ |$$ /  $$ |$$ |$$$\ $$ |$$$$\ $$ |$$ |     $$ /  $$ |$$ /  $$ |$$ |  $$ |
   $$ |   $$$$$\    $$ |      $$$$$\    $$ |  $$ |$$ |  $$ |$$ $$ $$\$$ |$$ $$\$$ |$$ |     $$ |  $$ |$$$$$$$$ |$$ |  $$ |
   $$ |   $$  __|   $$ |      $$  __|   $$ |  $$ |$$ |  $$ |$$$$  _$$$$ |$$ \$$$$ |$$ |     $$ |  $$ |$$  __$$ |$$ |  $$ |
   $$ |   $$ |      $$ |      $$ |      $$ |  $$ |$$ |  $$ |$$$  / \$$$ |$$ |\$$$ |$$ |     $$ |  $$ |$$ |  $$ |$$ |  $$ |
   $$ |   $$$$$$$$\ $$$$$$$$\ $$$$$$$$\ $$$$$$$  | $$$$$$  |$$  /   \$$ |$$ | \$$ |$$$$$$$$\ $$$$$$  |$$ |  $$ |$$$$$$$  |
   \__|   \________|\________|\________|\_______/  \______/ \__/     \__|\__|  \__|\________|\______/ \__|  \__|\_______/                                                                                             
""")

# Reset session jika diminta
if os.path.exists(f"{session_name}.session"):
    jawab = input("Ingin menghapus session lama? (y/n): ").strip().lower()
    if jawab == 'y':
        os.remove(f"{session_name}.session")
        print("✅ Session berhasil dihapus. Silakan login ulang nanti.\n")

# Fungsi pilih folder

def pilih_folder():
    folder = input("Masukkan path folder tujuan untuk menyimpan file: ").strip()
    if os.path.isdir(folder):
        return folder
    else:
        print("❌ Folder tidak valid.")
        return None

# Update progress bar seperti docker pull

def format_bar(filename, downloaded, total, speed):
    percent = (downloaded / total) * 100 if total else 0
    bar_length = 50
    filled_length = int(bar_length * percent / 100)
    bar = '▕' + '█' * filled_length + ' ' * (bar_length - filled_length) + '▏'
    human_downloaded = f"{downloaded / (1024 * 1024):.1f} MB"
    human_total = f"{total / (1024 * 1024):.1f} MB"
    speed_str = f"{speed:.1f} MB/s"
    return f"{filename}: {percent:>5.1f}% {bar} {human_downloaded}/{human_total} {speed_str}"

# Fungsi utama
async def download_video():
    async with TelegramClient(session_name, api_id, api_hash) as client:
        print("✅ Login berhasil.")

        dialogs = await client.get_dialogs()
        dialogs = sorted(dialogs, key=lambda d: d.name.lower())

        print("\nDaftar Channel:")
        for i, d in enumerate(dialogs, 1):
            print(f"{i}. {d.name}")

        try:
            pilihan = int(input("Pilih nomor channel: "))
            target = dialogs[pilihan - 1].entity
        except Exception as e:
            print(f"❌ Pilihan tidak valid: {e}")
            return

        durasi_input = input("Masukkan durasi minimum video (dalam detik) atau ketik 'all' untuk semua: ").strip().lower()
        min_duration = int(durasi_input) if durasi_input.isdigit() else 0

        start_index = input("Mulai dari urutan ke-berapa? (contoh: 1): ").strip()
        if not start_index.isdigit():
            print("❌ Input tidak valid.")
            return
        start_index = int(start_index)

        jumlah_input = input("Berapa video yang ingin diunduh? (contoh: 10 atau 'all'): ").strip().lower()
        jumlah = int(jumlah_input) if jumlah_input.isdigit() else None

        folder = pilih_folder()
        if not folder:
            print("❌ Tidak ada folder dipilih.")
            return

        print("\n🔍 Mendeteksi video...")
        messages = []
        deteksi = 0

        async for msg in client.iter_messages(target, reverse=True):
            deteksi += 1
            if deteksi % 50 == 0:
                print(f"  ↪ Memeriksa pesan ke-{deteksi}")

            doc = msg.document
            if doc:
                for attr in doc.attributes:
                    if isinstance(attr, DocumentAttributeVideo):
                        duration = getattr(attr, 'duration', 0)
                        if min_duration == 0 or duration >= min_duration:
                            messages.append(msg)
                        break

        total_video = len(messages)
        print(f"✅ Ditemukan {total_video} video.")
        if total_video == 0:
            print("❌ Tidak ada video ditemukan. Program berhenti.")
            return

        if jumlah is None:
            jumlah = total_video

        messages = messages[start_index - 1 : start_index - 1 + jumlah]
        print(f"▶️ Jumlah video yang akan diunduh: {len(messages)}")
        if len(messages) == 0:
            print("❌ Tidak ada video pada rentang urutan tersebut. Program berhenti.")
            return

        for i, msg in enumerate(messages, start=start_index):
            print(f"▶️ Memulai pengunduhan video ke-{i}")
            filename = f"Video - {str(i).zfill(3)}.mp4"
            path = os.path.join(folder, filename)
            temp_path = path + ".part"

            if os.path.exists(path) and os.path.getsize(path) > 0:
                print(f"✅ Lewati (sudah ada): {filename}")
                continue

            print(f"⬇️  Mengunduh {filename}...")
            try:
                start_time = time.time()
                last_print = 0

                def progress_callback(downloaded, total):
                    nonlocal last_print
                    now = time.time()
                    if now - last_print >= 0.5:
                        elapsed = now - start_time
                        speed = downloaded / 1024 / 1024 / elapsed if elapsed > 0 else 0
                        output = format_bar(filename, downloaded, total, speed)
                        print("\r" + output, end="", flush=True)
                        last_print = now

                await client.download_media(
                    msg,
                    file=temp_path,
                    progress_callback=progress_callback
                )
                os.rename(temp_path, path)
                print(f"\n✅ Selesai: {filename}\n")
            except Exception as e:
                print(f"❌ Gagal: {e}")

            if (i - start_index + 1) % 20 == 0:
                print("⏳ Istirahat 60 detik...")
                await asyncio.sleep(60)

# Eksekusi
if __name__ == "__main__":
    try:
        asyncio.run(download_video())
    except Exception as e:
        print(f"\n‼️ Program berhenti karena error tidak terduga: {e}")
