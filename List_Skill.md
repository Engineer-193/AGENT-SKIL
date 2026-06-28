# NVIDIA Agent Skills — Daftar Lengkap

Bot Telegram AI Agent dengan **10 NVIDIA Skills** terintegrasi.
**Total: 70 tools** aktif siap dipakai via AI tool calling.

---

## Skill 1 — NVIDIA AI-Q Deploy
**File:** `allskil/skill_1_aiq_deploy.py`
**Deskripsi:** Deploy dan manage NVIDIA AI-Q Blueprint Agents

| Tool | Fungsi |
|------|--------|
| `aiq_install` | Install AIQ CLI dan dependencies |
| `aiq_deploy` | Deploy AI-Q blueprint agent |
| `aiq_run` | Jalankan agent dengan prompt |
| `aiq_validate` | Validasi konfigurasi blueprint |
| `aiq_troubleshoot` | Diagnosa dan perbaiki error |
| `aiq_stop` | Stop agent yang berjalan |
| `aiq_status` | Cek status semua agent |

---

## Skill 2 — NeMo RL Session Memory
**File:** `allskil/skill_2_session_memory.py`
**Deskripsi:** Manajemen session dan memory persisten untuk AI agents

| Tool | Fungsi |
|------|--------|
| `session_start` | Mulai session baru |
| `session_checkpoint` | Simpan checkpoint session |
| `session_recover` | Pulihkan session dari checkpoint |
| `session_list` | Daftar semua session |
| `session_timeline_append` | Tambah event ke timeline |
| `session_files_update` | Update file dalam session |
| `session_handoff` | Transfer session ke agent lain |
| `session_read` | Baca isi session |

---

## Skill 3 — Physical AI Neural Reconstruction
**File:** `allskil/skill_3_physical_ai.py`
**Deskripsi:** NVIDIA Neural Reconstruction (NuRec) untuk Physical AI

| Tool | Fungsi |
|------|--------|
| `nurec_route` | Route ke workflow NuRec yang tepat |
| `nurec_check_prereqs` | Cek prerequisites sistem |
| `nurec_clone_upstream` | Clone repo upstream NuRec |
| `nurec_workflow` | Jalankan full NuRec workflow |
| `nurec_render_usdz` | Render USDZ dari model 3D |
| `nurec_convert_ncore` | Konversi ke format NCore |
| `nurec_grpc_sim` | Simulasi via gRPC |
| `nurec_dataset_hf` | Upload dataset ke HuggingFace |

---

## Skill 4 — NVIDIA NIM Deploy
**File:** `allskil/skill_4_nim_deploy.py`
**Deskripsi:** Deploy dan manage NVIDIA NIM Inference Microservices untuk self-hosted LLM

| Tool | Fungsi |
|------|--------|
| `nim_pull` | Pull NIM container dari NGC |
| `nim_run` | Jalankan NIM container |
| `nim_status` | Cek status NIM containers |
| `nim_stop` | Stop NIM container |
| `nim_test` | Test NIM inference endpoint |
| `nim_list_models` | Daftar NIM models tersedia |
| `nim_logs` | Lihat log container |
| `nim_scale` | Scale deployment (Docker Compose/K8s) |

---

## Skill 5 — NeMo Guardrails
**File:** `allskil/skill_5_nemo_guardrails.py`
**Deskripsi:** Safety rails untuk LLM — topic control, jailbreak prevention, policy enforcement

| Tool | Fungsi |
|------|--------|
| `guardrails_init` | Inisialisasi proyek guardrails |
| `guardrails_add_rule` | Tambah rule baru (input/output/topic) |
| `guardrails_test` | Test konfigurasi dengan prompt |
| `guardrails_list` | Daftar rules dalam proyek |
| `guardrails_generate_config` | Generate config otomatis dari use case |
| `guardrails_serve` | Jalankan guardrails server |
| `guardrails_explain` | Penjelasan konsep guardrails |

---

## Skill 6 — NVIDIA Cosmos
**File:** `allskil/skill_6_cosmos.py`
**Deskripsi:** World Foundation Models untuk Physical AI — simulasi dunia nyata & synthetic data

| Tool | Fungsi |
|------|--------|
| `cosmos_generate_video` | Generate video simulasi dunia dari prompt |
| `cosmos_setup` | Setup Cosmos + download model weights |
| `cosmos_list_models` | Daftar semua Cosmos models |
| `cosmos_post_train` | Fine-tune Cosmos pada data custom |
| `cosmos_robotics_sim` | Generate data simulasi robotika |
| `cosmos_explain` | Penjelasan Cosmos WFM |

---

## Skill 7 — NVIDIA Morpheus
**File:** `allskil/skill_7_morpheus.py`
**Deskripsi:** AI Cybersecurity — real-time threat detection, digital fingerprinting, Kafka streaming

| Tool | Fungsi |
|------|--------|
| `morpheus_setup` | Setup Morpheus (conda/docker/source) |
| `morpheus_run_pipeline` | Jalankan security pipeline |
| `morpheus_digital_fingerprinting` | Deteksi anomali perilaku user (ADF) |
| `morpheus_train_model` | Train custom security model |
| `morpheus_analyze_logs` | Analisis log keamanan |
| `morpheus_kafka_stream` | Setup real-time Kafka streaming pipeline |
| `morpheus_explain` | Penjelasan Morpheus |

---

## Skill 8 — NVIDIA Riva
**File:** `allskil/skill_8_riva.py`
**Deskripsi:** GPU-accelerated Speech AI — ASR, TTS, NMT multilingual

| Tool | Fungsi |
|------|--------|
| `riva_setup` | Setup Riva Speech AI server |
| `riva_asr` | Transkripsi audio ke teks |
| `riva_tts` | Teks ke suara (TTS) |
| `riva_translate` | Terjemahan bahasa Neural MT |
| `riva_list_models` | Daftar model ASR/TTS/NMT |
| `riva_streaming_demo` | Demo ASR streaming real-time |
| `riva_custom_vocab` | Tambah kosakata custom ke ASR |

---

## Skill 9 — NVIDIA Omniverse
**File:** `allskil/skill_9_omniverse.py`
**Deskripsi:** 3D simulation, USD workflows, digital twins, Isaac Sim, RTX rendering

| Tool | Fungsi |
|------|--------|
| `omniverse_setup` | Setup Kit SDK / Replicator / Isaac Sim |
| `omniverse_replicator_generate` | Generate synthetic computer vision data |
| `omniverse_usd_create` | Buat/modifikasi USD scene |
| `omniverse_digital_twin` | Setup digital twin workflow |
| `omniverse_rtx_render` | RTX path-tracing render job |
| `omniverse_isaac_sim` | Simulasi robot dengan Isaac Sim |
| `omniverse_explain` | Penjelasan Omniverse |

---

## Skill 10 — NVIDIA BioNeMo
**File:** `allskil/skill_10_bionemo.py`
**Deskripsi:** Biological AI — protein folding, drug discovery, molecular generation, genomics

| Tool | Fungsi |
|------|--------|
| `bionemo_protein_folding` | Prediksi struktur 3D protein (ESMFold/AlphaFold2) |
| `bionemo_molecule_generate` | Generate molekul obat baru (MolMIM) |
| `bionemo_docking` | Prediksi binding protein-ligan (DiffDock) |
| `bionemo_embeddings` | Generate embeddings biologis (ESM-2) |
| `bionemo_setup` | Setup BioNeMo framework/NIM |
| `bionemo_finetune` | Fine-tune model pada data biologis |
| `bionemo_explain` | Penjelasan BioNeMo |

---

## Ringkasan

| # | Skill | File | Tools |
|---|-------|------|-------|
| 1 | NVIDIA AI-Q Deploy | skill_1_aiq_deploy.py | 7 |
| 2 | NeMo Session Memory | skill_2_session_memory.py | 8 |
| 3 | Physical AI NuRec | skill_3_physical_ai.py | 8 |
| 4 | NVIDIA NIM Deploy | skill_4_nim_deploy.py | 8 |
| 5 | NeMo Guardrails | skill_5_nemo_guardrails.py | 7 |
| 6 | NVIDIA Cosmos | skill_6_cosmos.py | 6 |
| 7 | NVIDIA Morpheus | skill_7_morpheus.py | 7 |
| 8 | NVIDIA Riva | skill_8_riva.py | 7 |
| 9 | NVIDIA Omniverse | skill_9_omniverse.py | 7 |
| 10 | NVIDIA BioNeMo | skill_10_bionemo.py | 7 |
| — | Base Tools | tools.py | 4 |
| **Total** | | | **70 tools** |

---

## Contoh Penggunaan

```
"Deploy NIM untuk llama-3.1-8b"
→ nim_run(model='meta/llama-3.1-8b-instruct')

"Prediksi struktur protein MKTLLLT..."
→ bionemo_protein_folding(sequence='MKTLLLT...')

"Setup guardrails untuk customer support bot, block topik politik"
→ guardrails_generate_config(use_case='customer support', blocked_topics=['politics'])

"Generate 1000 gambar training data untuk deteksi objek di gudang"
→ omniverse_replicator_generate(scene_description='warehouse', num_frames=1000)

"Scan log syslog untuk ransomware"
→ morpheus_run_pipeline(pipeline_type='ransomware_detection', input_source='/var/log/syslog')

"Transkripsi file audio meeting.wav"
→ riva_asr(audio_file='meeting.wav', language='en-US')

"Generate video simulasi robot di pabrik"
→ cosmos_generate_video(prompt='robot arm assembling parts in factory', model='Cosmos-1.0-Diffusion-7B-Video2World')
```
