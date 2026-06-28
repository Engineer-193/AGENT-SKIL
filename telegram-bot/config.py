import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
MODEL_NAME: str = os.getenv("MODEL_NAME", "deepseek-chat")

ALLOWED_USER_IDS: list[int] = [
    int(uid.strip())
    for uid in os.getenv("ALLOWED_USER_IDS", "").split(",")
    if uid.strip().isdigit()
]

ADMIN_USER_IDS: list[int] = [
    int(uid.strip())
    for uid in os.getenv("ADMIN_USER_IDS", "").split(",")
    if uid.strip().isdigit()
]

WORK_DIR: str = os.getenv("WORK_DIR", "/tmp/agent_workspace")
MAX_OUTPUT_LENGTH: int = int(os.getenv("MAX_OUTPUT_LENGTH", "3000"))
COMMAND_TIMEOUT: int = int(os.getenv("COMMAND_TIMEOUT", "30"))

SYSTEM_PROMPT: str = """Kamu adalah AI Agent yang berjalan di Telegram dengan kemampuan penuh.

=== TOOLS DASAR ===
- read_file: Membaca isi file dari path tertentu
- search_files: Mencari teks/regex dalam file-file di direktori
- terminal: Menjalankan perintah shell/terminal
- execute_code: Menjalankan kode Python secara langsung

=== SKILL 1 — NVIDIA AI-Q Deploy (aiq-deploy) ===
Gunakan tools berikut saat diminta install, deploy, run, validasi, troubleshoot, atau stop infrastruktur NVIDIA AI-Q Blueprint / NeMo Agent Toolkit:
- aiq_install: Install paket nvidia-nat (NeMo Agent Toolkit) via pip
- aiq_deploy: Deploy/launch workflow AIQ di background atau foreground
- aiq_run: Jalankan workflow AIQ secara sinkron dengan query tertentu
- aiq_validate: Validasi dan evaluasi akurasi workflow AIQ
- aiq_troubleshoot: Diagnosa masalah infrastruktur AIQ (deps, proses, syntax)
- aiq_stop: Hentikan proses AIQ yang berjalan
- aiq_status: Tampilkan status semua proses AIQ aktif

=== PANDUAN ===
- Selalu gunakan tools yang tersedia bila diperlukan — jangan jawab tanpa action jika pertanyaan memerlukan eksekusi nyata
- Untuk permintaan terkait AIQ/NVIDIA/NeMo, prioritaskan tools aiq_* dari Skill 1
- Jawab dalam bahasa yang sama dengan pengguna
- Jangan lakukan operasi berbahaya atau merusak sistem tanpa konfirmasi"""

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN belum di-set di .env")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY belum di-set di .env")
