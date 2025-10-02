import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.scrolledtext as scrolledtext
import os, threading, asyncio, time
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeVideo

# ---------- Load .env ----------
load_dotenv()
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_NAME = os.getenv("SESSION_NAME", "televid_session")

if not API_ID or not API_HASH:
    raise RuntimeError("❌ API_ID/API_HASH belum di-set di .env")

# ---------- Konstanta ----------
BATCH_SIZE = 20
BATCH_PAUSE_SEC = 60


class TeleVidApp:
    def __init__(self, master):
        self.master = master
        master.title("✨ TeleVid Downloader ✨")
        master.geometry("950x700")
        master.configure(bg="#f0f4f8")

        tk.Label(master, text="📥 TeleVid Downloader",
                 font=("Helvetica", 18, "bold"), bg="#f0f4f8").pack(pady=10)

        frm = tk.Frame(master, bg="white", bd=2, relief=tk.RIDGE)
        frm.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # List chat
        tk.Label(frm, text="Pilih Group / Channel / Chat:", bg="white").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.listbox = tk.Listbox(frm, height=12, bg="#fafafa",
                                  selectbackground="#4CAF50", font=("Consolas", 10))
        self.listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        sb = tk.Scrollbar(frm, orient="vertical", command=self.listbox.yview)
        sb.grid(row=1, column=2, sticky="ns", padx=(0, 10), pady=5)
        self.listbox.config(yscrollcommand=sb.set)

        # Filter durasi
        tk.Label(frm, text="Filter durasi video (detik) ≤", bg="white").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.ent_durasi = tk.Entry(frm, width=10)
        self.ent_durasi.insert(0, "60")
        self.ent_durasi.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        # Start index
        tk.Label(frm, text="Mulai dari urutan ke-", bg="white").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.ent_start = tk.Entry(frm, width=10)
        self.ent_start.insert(0, "1")
        self.ent_start.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        # Folder
        tk.Label(frm, text="Lokasi download:", bg="white").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.folder_var = tk.StringVar()
        self.ent_folder = tk.Entry(frm, textvariable=self.folder_var, width=40)
        self.ent_folder.grid(row=4, column=1, sticky="w", padx=10, pady=5)
        tk.Button(frm, text="📂 Browse", command=self.choose_folder,
                  bg="#2196F3", fg="white", relief=tk.FLAT).grid(row=4, column=2, padx=5)

        # Tombol
        tk.Button(frm, text="🚀 Mulai Download", bg="#4CAF50", fg="white",
                  relief=tk.FLAT, command=self.start_download)\
            .grid(row=5, column=0, columnspan=3, pady=15)

        # Status singkat
        self.lbl_status = tk.Label(frm, text="Status: Idle", bg="white", fg="#555")
        self.lbl_status.grid(row=6, column=0, columnspan=3, pady=5)

        # Area log dengan Scroll
        self.txt_log = scrolledtext.ScrolledText(frm, height=20, bg="#111", fg="#0f0", font=("Consolas", 10))
        self.txt_log.grid(row=7, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Progress bar indeterminate
        self.progress = ttk.Progressbar(frm, orient="horizontal", mode="indeterminate", length=600)
        self.progress.grid(row=8, column=0, columnspan=3, pady=10)

        # Data dialog
        self.dialog_entities = []

        # Loop khusus Telethon
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.loop_thread.start()
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH, loop=self.loop)

        # Load chat
        self.run_async(self._load_dialogs())

        master.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- Utility ----------
    def ui_call(self, fn, *args, **kwargs):
        self.master.after(0, lambda: fn(*args, **kwargs))

    def log_message(self, msg, newline=True):
        self.ui_call(self._append_log, msg + ("\n" if newline else ""))

    def _append_log(self, text):
        self.txt_log.insert(tk.END, text)
        self.txt_log.see(tk.END)  # auto scroll ke bawah

    def set_status(self, text):
        self.ui_call(self.lbl_status.config, text=text)

    def progress_start(self):
        self.ui_call(self.progress.start, 10)

    def progress_stop(self):
        self.ui_call(self.progress.stop)

    def run_async(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    # ---------- Load dialogs ----------
    async def _load_dialogs(self):
        await self.client.start()
        dialogs = await self.client.get_dialogs()
        items = [(d.name or "Tanpa Nama", d.entity) for d in dialogs]
        items.sort(key=lambda x: x[0].lower())
        self.dialog_entities.clear()
        for name, entity in items:
            self.dialog_entities.append(entity)
            self.ui_call(self.listbox.insert, tk.END, name)
        self.set_status("✅ Dialog berhasil dimuat")

    # ---------- UI Action ----------
    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def start_download(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Pilih chat dulu")
            return
        try:
            max_dur = int(self.ent_durasi.get())
            start_from = int(self.ent_start.get())
        except ValueError:
            messagebox.showwarning("Warning", "Durasi dan urutan harus angka")
            return
        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showwarning("Warning", "Pilih folder download dulu")
            return
        os.makedirs(folder, exist_ok=True)
        entity = self.dialog_entities[sel[0]]
        self.set_status("Status: Mulai download…")
        self.progress_start()
        self.run_async(self._download_videos(entity, max_dur, start_from, folder))

    def _get_video_duration(self, msg):
        if not msg.video:
            return None
        for attr in getattr(msg.video, "attributes", []):
            if isinstance(attr, DocumentAttributeVideo):
                return getattr(attr, "duration", None)
        return None

    # ---------- Download ----------
    async def _download_videos(self, entity, max_duration_sec, start_from_index, folder):
        await self.client.start()
        matched_index = 0
        downloaded = 0
        last_time = {}

        async for msg in self.client.iter_messages(entity, reverse=True):
            if not msg.video:
                continue
            dur = self._get_video_duration(msg)
            if dur is None or dur > max_duration_sec:
                continue
            matched_index += 1
            if matched_index < start_from_index:
                continue

            filename = msg.file.name or f"video_{msg.id}.mp4"
            path = os.path.join(folder, filename)

            # Log awal
            self.log_message(f"\n▶️ Memulai pengunduhan video ke-{matched_index}")
            self.log_message(f"   Mengunduh {filename}...")

            # Progress callback
            def progress_callback(received, total):
                if total == 0:
                    return
                percent = received / total * 100
                now = time.time()
                speed = 0
                if filename in last_time:
                    elapsed = now - last_time[filename][0]
                    if elapsed > 0:
                        speed = (received - last_time[filename][1]) / elapsed
                last_time[filename] = (now, received)
                bar_len = 20
                filled = int(bar_len * percent // 100)
                bar = "█" * filled + "-" * (bar_len - filled)
                mb_done = received / (1024*1024)
                mb_total = total / (1024*1024)
                spd = f"{speed/1024:.1f} KB/s" if speed < 1024*1024 else f"{speed/1024/1024:.1f} MB/s"
                self.log_message(f"   [{bar}] {percent:3.0f}% {mb_done:.1f}MB/{mb_total:.1f}MB {spd}")

            # Download
            await msg.download_media(file=path, progress_callback=progress_callback)
            self.log_message(f"✅ Selesai: {filename}")

            downloaded += 1
            if downloaded % BATCH_SIZE == 0:
                self.log_message(f"⏸️ Istirahat {BATCH_PAUSE_SEC} detik...")
                await asyncio.sleep(BATCH_PAUSE_SEC)

        self.progress_stop()
        self.set_status("🎉 Semua video selesai diunduh!")

    # ---------- Exit ----------
    def on_close(self):
        async def _shutdown():
            try:
                await self.client.disconnect()
            except Exception:
                pass
        try:
            self.run_async(_shutdown()).result(timeout=5)
        except Exception:
            pass
        finally:
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.master.destroy()


def main():
    root = tk.Tk()
    TeleVidApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
