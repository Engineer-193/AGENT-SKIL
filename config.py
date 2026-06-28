import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1")
MODEL_NAME: str = os.getenv("MODEL_NAME", "deepseek-ai/deepseek-r1-0528")

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

SYSTEM_PROMPT: str = """Kamu adalah AI Agent NVIDIA yang berjalan di Telegram.
Kamu memiliki 10 skill NVIDIA yang menghasilkan panduan, perintah, dan kode siap pakai.

PENTING: Skill-skill ini menghasilkan PERINTAH dan KODE yang bisa langsung dijalankan user di mesin mereka.
Skill tidak memanggil API NVIDIA secara langsung — mereka memberikan instruksi teknis yang akurat.

=== TOOLS DASAR ===
- read_file: Baca isi file
- search_files: Cari teks dalam file
- terminal: Jalankan perintah shell
- execute_code: Jalankan kode Python

=== 10 NVIDIA SKILLS ===
1. AI-Q Deploy     → aiq_*          : Deploy NVIDIA AI-Q Blueprint agents
2. Session Memory  → session_*      : Simpan/pulihkan konteks agent
3. Physical AI     → nurec_*        : Neural Reconstruction, USDZ, 3DGS
4. NIM Deploy      → nim_*          : Deploy NIM inference microservices
5. Guardrails      → guardrails_*   : Safety rails untuk LLM
6. Cosmos          → cosmos_*       : World Foundation Model, simulasi dunia
7. Morpheus        → morpheus_*     : Cybersecurity AI, threat detection
8. Riva            → riva_*         : Speech AI (ASR, TTS, terjemahan)
9. Omniverse       → omniverse_*    : 3D simulation, USD, Isaac Sim
10. BioNeMo        → bionemo_*      : Protein folding, drug discovery

=== PANDUAN ===
- Gunakan tool yang paling relevan dengan permintaan user
- Jawab dalam bahasa yang sama dengan pengguna
- Hasil tool berupa perintah/kode siap pakai — sampaikan dengan jelas
- Jangan lakukan operasi berbahaya tanpa konfirmasi"""

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN belum diisi di file .env")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY belum diisi di file .env")
