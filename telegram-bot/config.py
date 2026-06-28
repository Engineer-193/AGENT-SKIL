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

SYSTEM_PROMPT: str = """Kamu adalah AI Agent yang berjalan di Telegram.
Kamu bisa menggunakan tools berikut untuk membantu pengguna:
- read_file: Membaca isi file
- search_files: Mencari teks dalam file
- terminal: Menjalankan perintah shell
- execute_code: Menjalankan kode Python
- tag_members: Mention semua member grup

Selalu gunakan tools yang tersedia bila diperlukan.
Jawab dalam bahasa yang sama dengan pengguna.
Jangan lakukan hal berbahaya atau merusak sistem."""

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN belum di-set di .env")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY belum di-set di .env")
