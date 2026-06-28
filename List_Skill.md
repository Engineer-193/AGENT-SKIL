# List Skill — Telegram AI Agent Bot

Daftar semua skill yang terpasang di bot ini. Skill disimpan di folder `allskil/`.

---

## Skill 1 — NVIDIA AI-Q Deploy (`aiq-deploy`)

**File:** `allskil/skill_1_aiq_deploy.py`
**Sumber:** `npx skills add NVIDIA/skills --skill aiq-deploy`
**Referensi:** https://github.com/NVIDIA/NeMo-Agent-Toolkit

**Gunakan saat:** install, deploy, run, validasi, troubleshoot, atau stop infrastruktur NVIDIA AI-Q Blueprint / NeMo Agent Toolkit.

| Tool | Fungsi |
|------|--------|
| `aiq_install` | Install paket `nvidia-nat` via pip |
| `aiq_deploy` | Deploy/launch workflow AIQ (background/foreground) |
| `aiq_run` | Jalankan workflow AIQ secara sinkron |
| `aiq_validate` | Validasi dan evaluasi workflow AIQ |
| `aiq_troubleshoot` | Diagnosa masalah infrastruktur AIQ |
| `aiq_stop` | Hentikan proses AIQ yang berjalan |
| `aiq_status` | Status semua proses AIQ aktif |

---

## Skill 2 — NeMo RL Session Memory (`nemo-rl-session-memory`)

**File:** `allskil/skill_2_session_memory.py`
**Sumber:** `npx skills add NVIDIA/skills --skill nemo-rl-session-memory`
**Referensi:** https://github.com/NVIDIA/skills/tree/main/skills/nemo-rl-session-memory

**Gunakan saat:** simpan/pulihkan konteks agen, pekerjaan panjang, handoff, disconnect, restart VS Code, branch switch.
**JANGAN gunakan untuk:** pertanyaan singkat, satu perintah, linting, code review.

| Tool | Fungsi |
|------|--------|
| `session_start` | Mulai sesi baru atau lanjutkan sesi terakhir |
| `session_checkpoint` | Tulis checkpoint berkala (sebelum/sesudah edit penting) |
| `session_recover` | Pulihkan sesi setelah disconnect/restart |
| `session_list` | Tampilkan semua sesi tersimpan |
| `session_timeline_append` | Catat aksi/keputusan ke timeline |
| `session_files_update` | Catat file yang diperiksa/diubah/dibuat |
| `session_handoff` | Tulis instruksi serah terima untuk agen berikutnya |
| `session_read` | Baca file sesi: handoff/state/timeline/files |

**Struktur sesi (per session):**
```
session/<timestamp>/
├── session_state.md  — goal, subtask, plan, blockers
├── timeline.md       — log append-only semua aksi
├── files.md          — file yang diperiksa/diubah
└── handoff.md        — instruksi untuk agen berikutnya
```

---

## Skill 3 — Physical AI Neural Reconstruction (`physical-ai-neural-reconstruction`)

**File:** `allskil/skill_3_physical_ai.py`
**Sumber:** `npx skills add NVIDIA/skills --skill physical-ai-neural-reconstruction`
**Referensi:** https://github.com/NVIDIA/skills/tree/main/skills/physical-ai-neural-reconstruction
**Upstream sibling skills:** https://github.com/NVIDIA/nurec-skills

**Router untuk NVIDIA NuRec/NRE:** Rendering USDZ, konversi NCore V4, 3DGS/3DGUT/3DGRT, simulasi sensor gRPC, dataset PhysicalAI HuggingFace.
**JANGAN gunakan untuk:** SimReady/CAD packaging, USD performance tuning umum, AKS/OSMO/NIM Operator infra setup.

| Tool | Fungsi |
|------|--------|
| `nurec_route` | Router utama: pilih sibling skill yang tepat untuk kebutuhan NuRec |
| `nurec_check_prereqs` | Cek prasyarat (Docker, GPU, NGC_API_KEY, HF_TOKEN, Python) |
| `nurec_clone_upstream` | Clone/refresh repo `nurec-skills` dari GitHub |
| `nurec_workflow` | Panduan workflow A-F (buat scene, pakai scene NVIDIA, edit objek, cleanup, benchmark, simulator) |
| `nurec_render_usdz` | Panduan render USDZ: rgb, lidar, serve-grpc, eval |
| `nurec_convert_ncore` | Panduan konversi recording sensor ke NCore V4 |
| `nurec_grpc_sim` | Panduan integrasi NuRec dengan CARLA/Isaac Sim/AlpaSim via gRPC |
| `nurec_dataset_hf` | Download dataset NuRec dari HuggingFace NVIDIA |

**Sibling Skills (upstream):**
| Skill | Fungsi |
|-------|--------|
| `physical-ai-datasets` | Download dataset NuRec dari HF |
| `ncore` | Konversi recording ke NCore V4 |
| `nre` | Training rekonstruksi 3D & render USDZ |
| `asset-harvester` | Ekstrak/tambah/ganti objek 3D |
| `nurec-fixer` | Cleanup frame (DiffusionHarmonizer) |

**Prerequisites:**
- Docker + NVIDIA Container Toolkit + GPU
- `NGC_API_KEY` — untuk pull NGC containers
- `HF_TOKEN` — untuk download PhysicalAI gated datasets
- Python 3.10+ + `huggingface_hub`
- (Opsional) CARLA / Isaac Sim 5.1 / AlpaSim untuk simulator integration

---

## Cara Menambah Skill Baru

1. Buat file `allskil/skill_N_nama_skill.py`
2. Definisikan fungsi tool dan dua variabel:
   - `SKILL_TOOL_DEFINITIONS` — list definisi tool untuk LLM
   - `SKILL_TOOL_FUNCTIONS` — dict nama → fungsi Python
3. Import di `tools.py`:
   ```python
   from allskil.skill_N_nama_skill import SKILL_TOOL_DEFINITIONS, SKILL_TOOL_FUNCTIONS
   ```
4. Tambahkan ke merge di `tools.py`:
   ```python
   TOOL_DEFINITIONS = [..., *SKILL_TOOL_DEFINITIONS]
   TOOL_FUNCTIONS = {..., **SKILL_TOOL_FUNCTIONS}
   ```
5. Update `SYSTEM_PROMPT` di `config.py`
6. Update file ini (`List_Skill.md`)
