"""
Skill 3 — Physical AI Neural Reconstruction (physical-ai-neural-reconstruction)
================================================================================
Router untuk NVIDIA NuRec/NRE:
  - Rendering USDZ
  - Konversi NCore V4
  - 3D Gaussian Splatting (3DGS / 3DGUT / 3DGRT)
  - Simulasi sensor gRPC (CARLA, Isaac Sim, AlpaSim)
  - Dataset PhysicalAI HuggingFace

JANGAN gunakan untuk: SimReady, infrastruktur AKS/OSMO/NIM Operator,
atau USD performance tuning umum yang tidak terkait NuRec.

npx skills add NVIDIA/skills --skill physical-ai-neural-reconstruction
Referensi: https://github.com/NVIDIA/skills/tree/main/skills/physical-ai-neural-reconstruction
Upstream sibling skills: https://github.com/NVIDIA/nurec-skills
"""

import subprocess
import os
import logging
from config import COMMAND_TIMEOUT, MAX_OUTPUT_LENGTH, WORK_DIR

logger = logging.getLogger(__name__)

NUREC_UPSTREAM = os.environ.get(
    "NUREC_SKILLS_UPSTREAM_ROOT",
    os.path.expanduser("~/.physical-ai-skill-hub/upstreams/nurec-skills"),
)

SIBLING_SKILLS = {
    "physical-ai-datasets": "Download/cari dataset NuRec dari HuggingFace NVIDIA",
    "ncore":                "Konversi recording (kamera/LiDAR/radar) ke format NCore V4",
    "nre":                  "Training rekonstruksi 3D & rendering USDZ dari NCore V4",
    "asset-harvester":      "Ekstrak/tambah/ganti objek 3D dalam scene NuRec",
    "nurec-fixer":          "Cleanup frame (ghosting, floater, flicker) — DiffusionHarmonizer",
}

WORKFLOW_MAP = {
    "A": "Buat scene NuRec dari recording sendiri: ncore → nre",
    "B": "Gunakan scene NuRec NVIDIA yang sudah ada: physical-ai-datasets → nre",
    "C": "Tambah/ganti objek 3D dalam scene: asset-harvester → nre",
    "D": "Bersihkan frame hasil render: nurec-fixer (atau --enable-difix di nre)",
    "E": "Benchmark kualitas rekonstruksi: physical-ai-datasets (PPISP) → nre (eval)",
    "F": "Hubungkan NuRec ke simulator: nre (serve-grpc → CARLA/Isaac Sim/AlpaSim)",
}

GOAL_ROUTING = {
    "download dataset": "physical-ai-datasets",
    "dataset": "physical-ai-datasets",
    "hf dataset": "physical-ai-datasets",
    "huggingface": "physical-ai-datasets",
    "konversi recording": "ncore",
    "ncore": "ncore",
    "convert": "ncore → nre",
    "ros bag": "ncore",
    "colmap": "ncore",
    "training": "ncore → nre",
    "train": "ncore → nre",
    "render usdz": "nre",
    "usdz": "nre",
    "render": "nre",
    "novel view": "nre",
    "grpc": "nre (serve-grpc)",
    "simulator": "nre (serve-grpc)",
    "carla": "nre (serve-grpc)",
    "isaac sim": "nre (serve-grpc)",
    "lidar": "nre (render-grpc --lidar)",
    "point cloud": "nre (render-grpc --lidar)",
    "extract objek": "asset-harvester",
    "harvest": "asset-harvester",
    "objek 3d": "asset-harvester",
    "cleanup frame": "nurec-fixer",
    "ghosting": "nurec-fixer",
    "floater": "nurec-fixer",
    "difix": "nurec-fixer",
    "harmonizer": "nurec-fixer",
}


def _run(cmd: str, timeout: int | None = None) -> tuple[int, str]:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout or COMMAND_TIMEOUT, cwd=WORK_DIR,
        )
        return result.returncode, (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return -1, f"⏱️ Timeout setelah {timeout or COMMAND_TIMEOUT} detik"
    except Exception as e:
        return -1, str(e)


def _trunc(text: str) -> str:
    if len(text) > MAX_OUTPUT_LENGTH:
        return text[:MAX_OUTPUT_LENGTH] + f"\n...[dipotong, {len(text)} karakter]"
    return text


def nurec_route(goal: str) -> str:
    """
    Router utama: tentukan sibling skill mana yang menjawab kebutuhan NuRec user.
    goal: Deskripsi apa yang ingin user lakukan (bebas bahasa)
    """
    goal_lower = goal.lower()

    matched: list[tuple[str, str]] = []
    for keyword, skill in GOAL_ROUTING.items():
        if keyword in goal_lower:
            matched.append((keyword, skill))

    if not matched:
        table = "\n".join(f"• `{k}` — `{v}`" for k, v in list(GOAL_ROUTING.items())[:10])
        return (
            f"🗺️ *NuRec Router*\n\nTidak ada keyword cocok untuk: _{goal}_\n\n"
            f"Coba jelaskan dengan keyword ini:\n{table}\n\n"
            f"Atau pilih workflow:\n" +
            "\n".join(f"• **{k}**: {v}" for k, v in WORKFLOW_MAP.items())
        )

    skill_name = matched[0][1]
    lines = [
        f"🗺️ *NuRec Router* — Goal: _{goal}_\n",
        f"✅ **Sibling skill yang tepat: `{skill_name}`**\n",
    ]

    if "→" in skill_name:
        steps = [s.strip() for s in skill_name.split("→")]
        lines.append("*Urutan langkah:*")
        for i, step in enumerate(steps, 1):
            desc = SIBLING_SKILLS.get(step.split("(")[0].strip(), "")
            lines.append(f"  {i}. `{step}` — {desc}")
    else:
        base = skill_name.split("(")[0].strip()
        desc = SIBLING_SKILLS.get(base, "")
        lines.append(f"*Fungsi:* {desc}")

    lines.append(
        f"\n*Upstream:* `https://github.com/NVIDIA/nurec-skills`\n"
        f"Gunakan `nurec_clone_upstream` untuk fetch skill lengkapnya."
    )
    return "\n".join(lines)


def nurec_check_prereqs() -> str:
    """
    Cek semua prasyarat NVIDIA NuRec: Docker, GPU, NGC API key, HF token, Python, huggingface_hub.
    """
    checks: list[str] = ["🔍 *NuRec Prerequisites Check*\n"]

    code, out = _run("docker --version 2>/dev/null || echo NOT_FOUND", timeout=10)
    docker_ver = out.split('\n')[0][:60]
    checks.append(f"• Docker: {'✅ ' + docker_ver if 'NOT_FOUND' not in out else '❌ Tidak ditemukan'}")

    code, out = _run("nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -2 || echo NOT_FOUND", timeout=10)
    if "NOT_FOUND" in out or not out.strip():
        checks.append("• GPU: ❌ Tidak ditemukan (nvidia-smi gagal)")
    else:
        gpus = out.strip().splitlines()
        checks.append(f"• GPU: ✅ {len(gpus)} GPU — {', '.join(gpus)}")

    code, out = _run("python --version 2>&1", timeout=5)
    checks.append(f"• Python: {'✅ ' + out.strip() if code == 0 else '❌ Tidak ditemukan'}")

    code, out = _run("python -c \"import huggingface_hub; print(huggingface_hub.__version__)\" 2>&1", timeout=10)
    checks.append(f"• huggingface_hub: {'✅ v' + out.strip() if code == 0 else '❌ Tidak terinstall (pip install huggingface_hub)'}")

    hf_token = os.environ.get("HF_TOKEN", "")
    ngc_key = os.environ.get("NGC_API_KEY", "")
    checks.append(f"• HF_TOKEN: {'✅ Set (len=' + str(len(hf_token)) + ')' if hf_token else '❌ Belum di-set'}")
    checks.append(f"• NGC_API_KEY: {'✅ Set (len=' + str(len(ngc_key)) + ')' if ngc_key else '❌ Belum di-set'}")

    code, out = _run("git --version 2>&1", timeout=5)
    checks.append(f"• git: {'✅ ' + out.strip() if code == 0 else '❌ Tidak ditemukan'}")

    code, out = _run("pip show huggingface_hub 2>/dev/null | grep Version || echo NOT_FOUND", timeout=10)
    checks.append(f"• hf_hub pip: {'✅ Terinstall' if 'NOT_FOUND' not in out else '⚠️ Tidak ditemukan'}")

    return "\n".join(checks)


def nurec_clone_upstream(force_refresh: bool = False) -> str:
    """
    Clone atau refresh repo upstream nurec-skills dari GitHub.
    force_refresh: True untuk hapus dan clone ulang
    """
    os.makedirs(os.path.dirname(NUREC_UPSTREAM), exist_ok=True)

    if os.path.exists(NUREC_UPSTREAM) and not force_refresh:
        code, out = _run(f"git -C {NUREC_UPSTREAM} pull --ff-only 2>&1", timeout=60)
        if code == 0:
            return f"✅ *nurec-skills diperbarui*\n```\n{out[:500]}\n```\n📁 Path: `{NUREC_UPSTREAM}`"
        return f"⚠️ *Pull gagal* (gunakan force_refresh=true untuk clone ulang)\n```\n{out[:300]}\n```"

    if os.path.exists(NUREC_UPSTREAM) and force_refresh:
        import shutil
        shutil.rmtree(NUREC_UPSTREAM, ignore_errors=True)

    code, out = _run(
        f"git clone --depth=1 https://github.com/NVIDIA/nurec-skills.git {NUREC_UPSTREAM} 2>&1",
        timeout=120,
    )
    if code == 0:
        code2, skills_list = _run(f"ls {NUREC_UPSTREAM}/.agents/skills/ 2>/dev/null || ls {NUREC_UPSTREAM}/ 2>/dev/null", timeout=10)
        return (
            f"✅ *nurec-skills di-clone*\n"
            f"📁 Path: `{NUREC_UPSTREAM}`\n"
            f"📂 Skills:\n```\n{skills_list[:400]}\n```"
        )
    return _trunc(f"❌ *Clone gagal* (exit {code})\n```\n{out}\n```")


def nurec_workflow(workflow: str, extra_context: str = "") -> str:
    """
    Panduan workflow end-to-end NuRec berdasarkan huruf workflow (A-F).
    workflow: 'A' | 'B' | 'C' | 'D' | 'E' | 'F'
    extra_context: Detail tambahan dari user (opsional)
    """
    wf = workflow.upper().strip()
    if wf not in WORKFLOW_MAP:
        options = "\n".join(f"• **{k}**: {v}" for k, v in WORKFLOW_MAP.items())
        return f"❓ Workflow `{workflow}` tidak dikenal.\n\nPilih dari:\n{options}"

    desc = WORKFLOW_MAP[wf]
    steps_detail = {
        "A": [
            "1. `ncore` — Konversi recording kamera/LiDAR/radar ke format NCore V4",
            "   → Jalankan `nurec_clone_upstream` → buka skill `ncore` dari upstream",
            "2. `nre` — Training 3D reconstruction dari NCore V4, output: USDZ",
            "   → Buka skill `nre` dari upstream untuk recipe training",
            "3. `nre` — Render USDZ dari trajectory baru atau view shifts",
        ],
        "B": [
            "1. `physical-ai-datasets` — Download scene NuRec yang sudah di-train NVIDIA",
            "   → Dataset tersedia di: https://huggingface.co/nvidia (butuh HF_TOKEN + gated license)",
            "2. `nre` — Langsung render USDZ yang sudah didownload tanpa training ulang",
        ],
        "C": [
            "1. `asset-harvester` — Ekstrak objek 3D (mobil, pejalan kaki) dari clip driving",
            "2. `asset-harvester` → `nre` — Tambah/ganti objek di scene NuRec",
        ],
        "D": [
            "1. `nurec-fixer` — Bersihkan ghosting, floater, flicker dengan DiffusionHarmonizer",
            "   ATAU gunakan flag `--enable-difix` saat render di `nre` (inline fix)",
        ],
        "E": [
            "1. `physical-ai-datasets` — Download benchmark dataset PhysicalAI-NuRec-PPISP",
            "2. `nre` — Jalankan `eval-rendering-metrics` (PSNR, SSIM, LPIPS)",
        ],
        "F": [
            "1. `nre` — Jalankan `serve-grpc` untuk expose USDZ sebagai gRPC server",
            "2. Koneksikan CARLA / Isaac Sim 5.1 / AlpaSim ke endpoint gRPC",
            "3. (Opsional) Gunakan `render-grpc --lidar` untuk LiDAR simulation",
            "4. (Opsional) Warm serve-grpc untuk minimal latency per-call via `batch_render_rgb`",
        ],
    }

    detail = "\n".join(steps_detail.get(wf, ["(detail tidak tersedia)"]))
    context_note = f"\n\n📝 *Konteks tambahan:* {extra_context}" if extra_context else ""

    return (
        f"🔄 *NuRec Workflow {wf}*\n\n"
        f"**Tujuan:** {desc}\n\n"
        f"**Langkah:**\n{detail}\n\n"
        f"*Upstream recipe lengkap:* `nurec_clone_upstream` → buka file skill di `{NUREC_UPSTREAM}`"
        f"{context_note}"
    )


def nurec_render_usdz(usdz_path: str, mode: str = "rgb", port: int = 0,
                       quality: str = "default", trajectory_shift: str = "") -> str:
    """
    Panduan / eksekusi render USDZ menggunakan NRE.
    usdz_path: Path ke file USDZ
    mode: 'rgb' | 'lidar' | 'serve-grpc' | 'eval'
    port: Port untuk serve-grpc (0 = tidak serve)
    quality: 'default' | 'full-res' | 'fast'
    trajectory_shift: Shift trajectory, misal '3m-left' (opsional)
    """
    if not os.path.exists(usdz_path) and not usdz_path.startswith("http"):
        return (
            f"⚠️ USDZ tidak ditemukan: `{usdz_path}`\n\n"
            f"*Untuk mendapatkan USDZ:*\n"
            f"• Download dari HF: `nurec_dataset_hf()`\n"
            f"• Train dari NCore: `nurec_workflow('A')`\n"
            f"• Gunakan scene yang sudah ada: `nurec_workflow('B')`"
        )

    quality_flags = {"full-res": "--quality full", "fast": "--quality fast", "default": ""}
    mode_info = {
        "rgb": f"nre render {usdz_path} {quality_flags.get(quality, '')}",
        "lidar": f"nre render-grpc --lidar {usdz_path}",
        "serve-grpc": f"nre serve-grpc {usdz_path} --port {port or 8080}",
        "eval": f"nre eval-rendering-metrics {usdz_path}",
    }

    cmd_template = mode_info.get(mode, mode_info["rgb"])
    if trajectory_shift:
        cmd_template += f" --trajectory-shift {trajectory_shift}"

    return (
        f"🎬 *NuRec Render USDZ*\n\n"
        f"• File: `{usdz_path}`\n"
        f"• Mode: `{mode}` | Quality: `{quality}`"
        + (f" | Trajectory: `{trajectory_shift}`" if trajectory_shift else "")
        + (f" | Port: `{port}`" if port else "")
        + f"\n\n*Perintah NRE (dari upstream skill):*\n```bash\n{cmd_template}\n```\n\n"
        f"*Pastikan:* NRE container sudah running (`nvcr.io/nvidia/nre/nre`)\n"
        f"*Fetch upstream:* `nurec_clone_upstream()` → buka skill `nre` untuk recipe lengkap"
    )


def nurec_convert_ncore(input_path: str, sensor_type: str = "camera",
                         output_dir: str = "", extra_args: str = "") -> str:
    """
    Panduan konversi recording ke format NCore V4 menggunakan skill ncore.
    input_path: Path ke file/direktori recording
    sensor_type: 'camera' | 'lidar' | 'radar' | 'stereo' | 'depth' | 'ros2-bag' | 'colmap'
    output_dir: Direktori output NCore V4
    extra_args: Argumen tambahan untuk converter
    """
    out_dir = output_dir or os.path.join(WORK_DIR, "ncore_output")
    sensor_notes = {
        "camera": "Standard camera recording (MP4, image sequence, atau multi-cam rig)",
        "lidar": "LiDAR point cloud sweep — format KITTI, nuScenes, atau custom",
        "radar": "Radar recording — 4D radar supported via custom converter",
        "stereo": "Stereo camera — depth dari disparity map",
        "depth": "RGB-D sensor (Intel RealSense, Azure Kinect, dll.)",
        "ros2-bag": "ROS 2 bag file — butuh ROS 2 environment",
        "colmap": "COLMAP reconstruction output sebagai input NCore",
    }
    note = sensor_notes.get(sensor_type, "Sensor type tidak dikenal")
    return (
        f"🔄 *NuRec: Konversi ke NCore V4*\n\n"
        f"• Input: `{input_path}`\n"
        f"• Sensor: `{sensor_type}` — {note}\n"
        f"• Output: `{out_dir}`\n\n"
        f"*Dari upstream skill `ncore`:*\n"
        f"```bash\n# Fetch upstream dulu:\nnurec_clone_upstream()\n\n"
        f"# Buka skill ncore di:\n{NUREC_UPSTREAM}/ncore/SKILL.md\n```\n\n"
        f"*Urutan workflow:* `ncore` (konversi) → `nre` (training) → `nre` (render)\n"
        f"Gunakan `nurec_workflow('A')` untuk panduan lengkap."
    )


def nurec_grpc_sim(usdz_path: str, simulator: str = "carla",
                    port: int = 8080, warm: bool = False) -> str:
    """
    Panduan integrasi NuRec dengan simulator via gRPC.
    usdz_path: Path ke USDZ yang sudah di-train
    simulator: 'carla' | 'isaac-sim' | 'alpasim' | 'custom'
    port: Port gRPC server (default 8080)
    warm: True untuk warm serve-grpc (minimal latency)
    """
    sim_notes = {
        "carla": "CARLA Simulator — koneksikan lewat NRE gRPC client library",
        "isaac-sim": "NVIDIA Isaac Sim 5.1 — native NRE gRPC plugin tersedia",
        "alpasim": "AlpaSim — koneksi via thin Python client",
        "custom": "Custom simulator — gunakan NRE thin Python client (`batch_render_rgb`)",
    }
    note = sim_notes.get(simulator, sim_notes["custom"])
    warm_cmd = f"nre warm serve-grpc {usdz_path} --port {port}" if warm else f"nre serve-grpc {usdz_path} --port {port}"
    return (
        f"🤖 *NuRec gRPC Sensor Simulation*\n\n"
        f"• USDZ: `{usdz_path}`\n"
        f"• Simulator: `{simulator}` — {note}\n"
        f"• Port: `{port}` | Warm: `{'✅' if warm else '❌'}`\n\n"
        f"*Perintah NRE:*\n```bash\n{warm_cmd}\n```\n\n"
        f"*Untuk LiDAR sweep:*\n```bash\nnre render-grpc --lidar {usdz_path} --port {port}\n```\n\n"
        f"Gunakan `nurec_workflow('F')` untuk panduan koneksi simulator lengkap."
    )


def nurec_dataset_hf(dataset_name: str = "", list_available: bool = False) -> str:
    """
    Panduan download/cari dataset NuRec dari HuggingFace NVIDIA.
    dataset_name: Nama dataset spesifik (kosong = tampilkan daftar)
    list_available: True untuk tampilkan semua dataset yang tersedia
    """
    known_datasets = {
        "PhysicalAI-Autonomous-Vehicles-NuRec": "Dataset driving multi-sensor untuk training NuRec (kamera + LiDAR)",
        "PhysicalAI-NuRec-PPISP": "Benchmark dataset untuk evaluasi kualitas rekonstruksi (PSNR/SSIM/LPIPS)",
        "Cosmos-Drive-Dreams": "Dataset generatif driving untuk NuRec dan simulasi",
        "DiffusionHarmonizer": "Model untuk nurec-fixer (difix / difix3d cleanup)",
    }

    if list_available or not dataset_name:
        lines = ["📦 *Dataset NuRec di HuggingFace NVIDIA:*\n",
                 "Base URL: `https://huggingface.co/nvidia`\n",
                 "*Dataset Utama:*"]
        for name, desc in known_datasets.items():
            lines.append(f"• `nvidia/{name}`\n  _{desc}_")
        lines.append("\n*Prerequisites:*\n• `HF_TOKEN` di-set dengan license gated diterima\n• `pip install huggingface_hub`")
        lines.append("\n*Download:*\n```python\nfrom huggingface_hub import snapshot_download\nsnapshot_download('nvidia/<dataset_name>', local_dir='./data')\n```")
        return "\n".join(lines)

    desc = known_datasets.get(dataset_name, "(dataset baru atau tidak dikenal — cek langsung di huggingface.co/nvidia)")
    hf_token = os.environ.get("HF_TOKEN", "")
    token_status = f"✅ Set (len={len(hf_token)})" if hf_token else "❌ Belum di-set — set HF_TOKEN dulu"
    return (
        f"📦 *NuRec Dataset: `nvidia/{dataset_name}`*\n\n"
        f"_{desc}_\n\n"
        f"• HF_TOKEN: {token_status}\n\n"
        f"*Download:*\n```python\nfrom huggingface_hub import snapshot_download\nsnapshot_download(\n    'nvidia/{dataset_name}',\n    local_dir='./nurec_data/{dataset_name}',\n    token='{'{HF_TOKEN}'}'  # dari env\n)\n```\n\n"
        f"*Setelah download:* gunakan `nurec_workflow('B')` untuk render langsung."
    )


NUREC_TOOL_DEFINITIONS = [
    {"type": "function", "function": {"name": "nurec_route", "description": "Router utama NuRec: tentukan sibling skill yang tepat berdasarkan tujuan user. Gunakan saat user menyebut nurec, NRE, USDZ, NCore, 3DGS, 3DGUT, sensor sim, asset harvester, atau neural reconstruction.", "parameters": {"type": "object", "properties": {"goal": {"type": "string", "description": "Deskripsi apa yang ingin user lakukan"}}, "required": ["goal"]}}},
    {"type": "function", "function": {"name": "nurec_check_prereqs", "description": "Cek semua prasyarat NVIDIA NuRec (Docker, GPU, NGC_API_KEY, HF_TOKEN, Python, huggingface_hub).", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "nurec_clone_upstream", "description": "Clone atau refresh repo nurec-skills dari GitHub untuk mengakses recipe lengkap sibling skills.", "parameters": {"type": "object", "properties": {"force_refresh": {"type": "boolean", "default": False}}, "required": []}}},
    {"type": "function", "function": {"name": "nurec_workflow", "description": "Panduan workflow end-to-end NuRec: A=buat scene, B=pakai scene NVIDIA, C=edit objek, D=cleanup, E=benchmark, F=simulator.", "parameters": {"type": "object", "properties": {"workflow": {"type": "string", "description": "Huruf workflow: A | B | C | D | E | F"}, "extra_context": {"type": "string", "default": ""}}, "required": ["workflow"]}}},
    {"type": "function", "function": {"name": "nurec_render_usdz", "description": "Panduan render USDZ menggunakan NRE. Gunakan saat user ingin render scene NuRec.", "parameters": {"type": "object", "properties": {"usdz_path": {"type": "string"}, "mode": {"type": "string", "default": "rgb", "description": "rgb | lidar | serve-grpc | eval"}, "port": {"type": "integer", "default": 0}, "quality": {"type": "string", "default": "default"}, "trajectory_shift": {"type": "string", "default": ""}}, "required": ["usdz_path"]}}},
    {"type": "function", "function": {"name": "nurec_convert_ncore", "description": "Panduan konversi recording ke NCore V4. Gunakan saat user ingin konversi data sensor ke format NuRec.", "parameters": {"type": "object", "properties": {"input_path": {"type": "string"}, "sensor_type": {"type": "string", "default": "camera", "description": "camera | lidar | radar | stereo | depth | ros2-bag | colmap"}, "output_dir": {"type": "string", "default": ""}, "extra_args": {"type": "string", "default": ""}}, "required": ["input_path"]}}},
    {"type": "function", "function": {"name": "nurec_grpc_sim", "description": "Panduan koneksi NuRec ke simulator via gRPC (CARLA, Isaac Sim, AlpaSim). Gunakan saat user sebut serve-grpc, render-grpc, atau simulator integration.", "parameters": {"type": "object", "properties": {"usdz_path": {"type": "string"}, "simulator": {"type": "string", "default": "carla", "description": "carla | isaac-sim | alpasim | custom"}, "port": {"type": "integer", "default": 8080}, "warm": {"type": "boolean", "default": False}}, "required": ["usdz_path"]}}},
    {"type": "function", "function": {"name": "nurec_dataset_hf", "description": "Panduan download dataset NuRec dari HuggingFace NVIDIA (PhysicalAI-*, Cosmos-Drive-Dreams, dll.).", "parameters": {"type": "object", "properties": {"dataset_name": {"type": "string", "default": ""}, "list_available": {"type": "boolean", "default": False}}, "required": []}}},
]

NUREC_TOOL_FUNCTIONS = {
    "nurec_route": nurec_route,
    "nurec_check_prereqs": nurec_check_prereqs,
    "nurec_clone_upstream": nurec_clone_upstream,
    "nurec_workflow": nurec_workflow,
    "nurec_render_usdz": nurec_render_usdz,
    "nurec_convert_ncore": nurec_convert_ncore,
    "nurec_grpc_sim": nurec_grpc_sim,
    "nurec_dataset_hf": nurec_dataset_hf,
}
