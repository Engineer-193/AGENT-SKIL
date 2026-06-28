"""
Skill 2 — NeMo RL Session Memory (nemo-rl-session-memory)
==========================================================
Kelola memori sesi kerja yang tahan lama untuk agen pengkodean.

Gunakan saat pengguna meminta untuk:
  - menyimpan / memulihkan konteks agen
  - checkpoint pekerjaan panjang
  - serah terima (handoff) ke agen lain
  - restart VS Code / disconnect / branch switch
  - sesi di mana status penting harus ditulis berkala

Jangan gunakan untuk: pertanyaan singkat, satu perintah, linting, code review.

Referensi: https://github.com/NVIDIA/skills/tree/main/skills/nemo-rl-session-memory
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from config import WORK_DIR, MAX_OUTPUT_LENGTH

logger = logging.getLogger(__name__)

SESSION_BASE = os.path.join(WORK_DIR, "session")
_ACTIVE_SESSION: dict = {}


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _session_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _active_dir() -> str | None:
    return _ACTIVE_SESSION.get("dir")


def _trunc(text: str) -> str:
    if len(text) > MAX_OUTPUT_LENGTH:
        return text[:MAX_OUTPUT_LENGTH] + f"\n...[dipotong, {len(text)} karakter total]"
    return text


def _write_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _read_file(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _append_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)


def session_start(
    goal: str,
    subtask: str = "",
    repo_path: str = "",
    branch: str = "",
    loaded_skills: str = "Skill 1: aiq-deploy, Skill 2: nemo-rl-session-memory",
    resume: bool = False,
) -> str:
    """
    Mulai sesi baru atau lanjutkan sesi yang paling terbaru.
    goal: Tujuan utama sesi ini
    subtask: Tugas yang sedang dikerjakan sekarang
    repo_path: Path repo (opsional)
    branch: Nama branch git (opsional)
    loaded_skills: Skill yang dimuat
    resume: True untuk melanjutkan sesi terakhir, False untuk membuat baru
    """
    global _ACTIVE_SESSION
    os.makedirs(SESSION_BASE, exist_ok=True)

    if resume:
        existing = sorted(
            [d for d in os.listdir(SESSION_BASE) if os.path.isdir(os.path.join(SESSION_BASE, d))],
            reverse=True,
        )
        if existing:
            session_dir = os.path.join(SESSION_BASE, existing[0])
            _ACTIVE_SESSION = {"id": existing[0], "dir": session_dir}
            handoff = _read_file(os.path.join(session_dir, "handoff.md"))
            state = _read_file(os.path.join(session_dir, "session_state.md"))
            _append_file(
                os.path.join(session_dir, "timeline.md"),
                f"\n## {_now()}\n- Recovery: Sesi dilanjutkan oleh agen baru\n- Goal tetap: {goal}\n",
            )
            return _trunc(
                f"🔄 *Sesi dilanjutkan*: `{existing[0]}`\n\n"
                f"**📋 Handoff:**\n{handoff or '(kosong)'}\n\n"
                f"**📊 State terakhir:**\n{state[:800] if state else '(kosong)'}"
            )

    sid = _session_id()
    session_dir = os.path.join(SESSION_BASE, sid)
    os.makedirs(session_dir, exist_ok=True)
    _ACTIVE_SESSION = {"id": sid, "dir": session_dir}

    state_content = f"""# Session State

- Session: {sid}
- Repo: {repo_path or WORK_DIR}
- Branch: {branch or '(tidak diketahui)'}
- Started: {_now()}
- Updated: {_now()}

## Goal
{goal}

## Current Subtask
{subtask or '(belum ditentukan)'}

## Loaded Skills
- `aiq-deploy` — deploy, run, validate, troubleshoot, stop NVIDIA AIQ Blueprint
- `nemo-rl-session-memory` — kelola memori sesi tahan lama
{loaded_skills}

## Current Status
Sesi baru dimulai. Konteks awal sedang dikumpulkan.

## Plan
- [ ] Kumpulkan konteks awal
- [ ] Tentukan subtask pertama
- [ ] Mulai eksekusi

## Assumptions
- (belum ada asumsi tercatat)

## Blockers
- None known
"""

    timeline_content = f"""# Timeline

## {_now()}
- User memulai sesi baru
- Goal: {goal}
- Subtask: {subtask or '(belum ditentukan)'}
- Status: Inisialisasi selesai
"""

    files_content = f"""# Files

## Inspected
- (belum ada)

## Changed
- (belum ada)

## Generated
- `session/{sid}/session_state.md` — State awal sesi
- `session/{sid}/timeline.md` — Log timeline sesi
- `session/{sid}/files.md` — Daftar file yang dilihat/diubah
- `session/{sid}/handoff.md` — Instruksi serah terima
"""

    handoff_content = f"""# Handoff

## Resume From Here
Sesi baru dimulai dengan goal: {goal}. Belum ada pekerjaan yang diselesaikan.

## Next Actions
- Tentukan subtask pertama yang konkret
- Kumpulkan konteks yang diperlukan

## Watch Outs
- (belum ada catatan khusus)
"""

    _write_file(os.path.join(session_dir, "session_state.md"), state_content)
    _write_file(os.path.join(session_dir, "timeline.md"), timeline_content)
    _write_file(os.path.join(session_dir, "files.md"), files_content)
    _write_file(os.path.join(session_dir, "handoff.md"), handoff_content)

    return (
        f"✅ *Sesi dimulai*: `{sid}`\n\n"
        f"📁 Direktori: `{session_dir}`\n"
        f"🎯 Goal: {goal}\n"
        f"📌 Subtask: {subtask or '(belum ditentukan)'}\n\n"
        f"File dibuat:\n"
        f"• `session_state.md` — status & rencana\n"
        f"• `timeline.md` — log aksi\n"
        f"• `files.md` — daftar file\n"
        f"• `handoff.md` — instruksi resume"
    )


def session_checkpoint(
    status: str,
    subtask: str = "",
    plan_done: str = "",
    plan_next: str = "",
    decisions: str = "",
    blockers: str = "None known",
) -> str:
    """
    Tulis checkpoint ke sesi aktif.
    status: Status pekerjaan saat ini
    subtask: Subtask yang sedang dikerjakan
    plan_done: Langkah yang sudah selesai (pisahkan dengan ';')
    plan_next: Langkah berikutnya (pisahkan dengan ';')
    decisions: Keputusan penting yang dibuat
    blockers: Blocker yang ada
    """
    sdir = _active_dir()
    if not sdir:
        return "⚠️ Belum ada sesi aktif. Jalankan `session_start` terlebih dahulu."

    state_path = os.path.join(sdir, "session_state.md")
    state = _read_file(state_path)

    updated_state = []
    for line in state.splitlines():
        if line.startswith("- Updated:"):
            updated_state.append(f"- Updated: {_now()}")
        elif line.startswith("## Current Subtask"):
            updated_state.append(line)
            updated_state.append(subtask or "(tidak berubah)")
        elif line.startswith("## Current Status"):
            updated_state.append(line)
            updated_state.append(status)
        elif line.startswith("## Plan"):
            updated_state.append(line)
            if plan_done:
                for step in plan_done.split(";"):
                    updated_state.append(f"- [x] {step.strip()}")
            if plan_next:
                for step in plan_next.split(";"):
                    updated_state.append(f"- [ ] {step.strip()}")
        elif line.startswith("## Blockers"):
            updated_state.append(line)
            updated_state.append(f"- {blockers}")
        else:
            updated_state.append(line)

    _write_file(state_path, "\n".join(updated_state))

    timeline_entry = f"\n## {_now()}\n- Checkpoint\n- Status: {status}\n"
    if subtask:
        timeline_entry += f"- Subtask: {subtask}\n"
    if decisions:
        timeline_entry += f"- Decision: {decisions}\n"
    if plan_next:
        timeline_entry += f"- Next: {plan_next[:200]}\n"

    _append_file(os.path.join(sdir, "timeline.md"), timeline_entry)

    handoff = (
        f"# Handoff\n\n"
        f"## Resume From Here\n"
        f"{status}\n\n"
        f"## Next Actions\n"
        + ("\n".join(f"- {s.strip()}" for s in plan_next.split(";")) if plan_next else "- (lihat session_state.md)")
        + f"\n\n## Watch Outs\n- {blockers}\n"
    )
    _write_file(os.path.join(sdir, "handoff.md"), handoff)

    return (
        f"💾 *Checkpoint disimpan* — `{_ACTIVE_SESSION.get('id')}`\n\n"
        f"📊 Status: {status[:200]}\n"
        f"⏱️ Waktu: {_now()}"
    )


def session_recover(session_id: str = "") -> str:
    """
    Pulihkan sesi dari disk. Baca handoff, state, dan timeline terakhir.
    session_id: ID sesi spesifik (kosong = sesi terbaru)
    """
    global _ACTIVE_SESSION
    os.makedirs(SESSION_BASE, exist_ok=True)

    sessions = sorted(
        [d for d in os.listdir(SESSION_BASE) if os.path.isdir(os.path.join(SESSION_BASE, d))],
        reverse=True,
    )

    if not sessions:
        return "ℹ️ Tidak ada sesi tersimpan. Gunakan `session_start` untuk membuat sesi baru."

    target = session_id if session_id and session_id in sessions else sessions[0]
    sdir = os.path.join(SESSION_BASE, target)
    _ACTIVE_SESSION = {"id": target, "dir": sdir}

    handoff = _read_file(os.path.join(sdir, "handoff.md"))
    state = _read_file(os.path.join(sdir, "session_state.md"))
    timeline_lines = _read_file(os.path.join(sdir, "timeline.md")).splitlines()
    recent_timeline = "\n".join(timeline_lines[-30:]) if len(timeline_lines) > 30 else "\n".join(timeline_lines)

    _append_file(
        os.path.join(sdir, "timeline.md"),
        f"\n## {_now()}\n- Recovery: Agen baru terhubung ke sesi ini\n",
    )

    return _trunc(
        f"🔄 *Sesi dipulihkan*: `{target}`\n\n"
        f"**📋 Handoff (baca ini dulu):**\n```\n{handoff or '(kosong)'}\n```\n\n"
        f"**📊 State:**\n```\n{state[:600] if state else '(kosong)'}\n```\n\n"
        f"**📅 Timeline Terbaru:**\n```\n{recent_timeline}\n```"
    )


def session_list() -> str:
    """
    Tampilkan daftar semua sesi yang tersimpan.
    """
    os.makedirs(SESSION_BASE, exist_ok=True)
    sessions = sorted(
        [d for d in os.listdir(SESSION_BASE) if os.path.isdir(os.path.join(SESSION_BASE, d))],
        reverse=True,
    )

    if not sessions:
        return "ℹ️ Tidak ada sesi tersimpan."

    lines = [f"📚 *Daftar Sesi ({len(sessions)} total):*\n"]
    for i, sid in enumerate(sessions[:20]):
        sdir = os.path.join(SESSION_BASE, sid)
        marker = " ← *aktif*" if sid == _ACTIVE_SESSION.get("id") else ""
        handoff_path = os.path.join(sdir, "handoff.md")
        preview = ""
        if os.path.exists(handoff_path):
            with open(handoff_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("##"):
                        preview = line[:80]
                        break
        lines.append(f"`{i+1}.` `{sid}`{marker}\n    _{preview}_")

    if _ACTIVE_SESSION.get("id"):
        lines.append(f"\n🟢 Sesi aktif: `{_ACTIVE_SESSION['id']}`")

    return "\n".join(lines)


def session_timeline_append(entry: str, action_type: str = "Update") -> str:
    """
    Tambahkan entri ke timeline sesi aktif.
    entry: Isi entri yang ingin dicatat
    action_type: Tipe aksi (misal: Edit, Test, Decision, Error, Command)
    """
    sdir = _active_dir()
    if not sdir:
        return "⚠️ Belum ada sesi aktif."

    timeline_entry = f"\n## {_now()}\n- [{action_type}] {entry}\n"
    _append_file(os.path.join(sdir, "timeline.md"), timeline_entry)

    return f"📝 Timeline diupdate — `[{action_type}]` {entry[:100]}"


def session_files_update(
    inspected: str = "",
    changed: str = "",
    generated: str = "",
) -> str:
    """
    Update catatan file pada sesi aktif.
    inspected: File yang diperiksa dan alasannya (format: 'path: alasan; path2: alasan2')
    changed: File yang diubah (format: 'path: perubahan; path2: perubahan2')
    generated: File yang dibuat baru (format: 'path: tujuan')
    """
    sdir = _active_dir()
    if not sdir:
        return "⚠️ Belum ada sesi aktif."

    files_path = os.path.join(sdir, "files.md")
    existing = _read_file(files_path)

    def _format_entries(raw: str, section: str) -> list[str]:
        lines = [f"\n## {section}"]
        if not raw:
            lines.append("- (tidak ada perubahan)")
            return lines
        for item in raw.split(";"):
            item = item.strip()
            if ":" in item:
                path, reason = item.split(":", 1)
                lines.append(f"- `{path.strip()}` — {reason.strip()}")
            elif item:
                lines.append(f"- `{item}`")
        return lines

    new_sections: list[str] = [f"\n---\n_Updated: {_now()}_"]
    if inspected:
        new_sections.extend(_format_entries(inspected, "Inspected"))
    if changed:
        new_sections.extend(_format_entries(changed, "Changed"))
    if generated:
        new_sections.extend(_format_entries(generated, "Generated"))

    _append_file(files_path, "\n".join(new_sections) + "\n")

    timeline_entry = f"\n## {_now()}\n- [Files Update]"
    if changed:
        timeline_entry += f" Changed: {changed[:150]}"
    if generated:
        timeline_entry += f" Generated: {generated[:100]}"
    _append_file(os.path.join(sdir, "timeline.md"), timeline_entry + "\n")

    return f"📁 *Files.md diupdate* — sesi `{_ACTIVE_SESSION.get('id')}`"


def session_handoff(
    summary: str,
    next_actions: str,
    watch_outs: str = "",
) -> str:
    """
    Tulis instruksi serah terima (handoff) untuk agen berikutnya.
    summary: Ringkasan kondisi saat ini (1 paragraf)
    next_actions: Aksi berikutnya (pisahkan dengan ';')
    watch_outs: Risiko atau catatan penting (pisahkan dengan ';')
    """
    sdir = _active_dir()
    if not sdir:
        return "⚠️ Belum ada sesi aktif."

    actions_md = "\n".join(
        f"- {a.strip()}" for a in next_actions.split(";") if a.strip()
    )
    watches_md = "\n".join(
        f"- {w.strip()}" for w in watch_outs.split(";") if w.strip()
    ) if watch_outs else "- (tidak ada)"

    handoff_content = (
        f"# Handoff\n\n"
        f"_Updated: {_now()}_\n\n"
        f"## Resume From Here\n{summary}\n\n"
        f"## Next Actions\n{actions_md}\n\n"
        f"## Watch Outs\n{watches_md}\n"
    )

    _write_file(os.path.join(sdir, "handoff.md"), handoff_content)
    _append_file(
        os.path.join(sdir, "timeline.md"),
        f"\n## {_now()}\n- [Handoff] Instruksi serah terima ditulis\n- Next: {next_actions[:200]}\n",
    )

    return (
        f"🤝 *Handoff ditulis* — `{_ACTIVE_SESSION.get('id')}`\n\n"
        f"📋 Ringkasan: {summary[:200]}\n"
        f"➡️ Aksi selanjutnya:\n{actions_md}"
    )


def session_read(file: str = "handoff") -> str:
    """
    Baca file tertentu dari sesi aktif.
    file: Nama file tanpa ekstensi — handoff | session_state | timeline | files
    """
    sdir = _active_dir()
    if not sdir:
        return "⚠️ Belum ada sesi aktif. Gunakan `session_recover` atau `session_start`."

    valid_files = {
        "handoff": "handoff.md",
        "session_state": "session_state.md",
        "state": "session_state.md",
        "timeline": "timeline.md",
        "files": "files.md",
    }
    filename = valid_files.get(file.lower().replace(".md", ""), f"{file}.md")
    path = os.path.join(sdir, filename)
    content = _read_file(path)

    if not content:
        return f"ℹ️ File `{filename}` kosong atau tidak ditemukan di sesi `{_ACTIVE_SESSION.get('id')}`."

    return _trunc(
        f"📖 *`{filename}`* — sesi `{_ACTIVE_SESSION.get('id')}`\n\n```\n{content}\n```"
    )


SESSION_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "session_start",
            "description": (
                "Mulai sesi memori baru atau lanjutkan sesi terakhir. "
                "Gunakan saat memulai pekerjaan panjang, sebelum nontrivial edits, atau saat user minta simpan konteks."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "goal": {"type": "string", "description": "Tujuan utama sesi ini (1-2 kalimat)"},
                    "subtask": {"type": "string", "description": "Tugas yang sedang dikerjakan sekarang", "default": ""},
                    "repo_path": {"type": "string", "description": "Path absolut repo (opsional)", "default": ""},
                    "branch": {"type": "string", "description": "Nama branch git (opsional)", "default": ""},
                    "loaded_skills": {"type": "string", "description": "Skill yang aktif", "default": "Skill 1: aiq-deploy, Skill 2: nemo-rl-session-memory"},
                    "resume": {"type": "boolean", "description": "True untuk lanjutkan sesi terakhir", "default": False},
                },
                "required": ["goal"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "session_checkpoint",
            "description": (
                "Tulis checkpoint sesi aktif. Gunakan sebelum/sesudah edit penting, "
                "sebelum perintah panjang, saat arah berubah, atau tiap 30 menit pekerjaan aktif."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Status pekerjaan saat ini"},
                    "subtask": {"type": "string", "description": "Subtask yang dikerjakan", "default": ""},
                    "plan_done": {"type": "string", "description": "Langkah selesai, pisah dengan ';'", "default": ""},
                    "plan_next": {"type": "string", "description": "Langkah berikutnya, pisah dengan ';'", "default": ""},
                    "decisions": {"type": "string", "description": "Keputusan penting yang diambil", "default": ""},
                    "blockers": {"type": "string", "description": "Blocker aktif", "default": "None known"},
                },
                "required": ["status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "session_recover",
            "description": (
                "Pulihkan sesi dari disk setelah disconnect, restart, atau handoff. "
                "Gunakan di awal sesi jika ada kemungkinan pekerjaan sebelumnya."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "ID sesi spesifik (kosong = terbaru)", "default": ""},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "session_list",
            "description": "Tampilkan semua sesi tersimpan beserta preview singkatnya.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "session_timeline_append",
            "description": "Tambahkan entri ke timeline sesi aktif untuk merekam aksi, keputusan, atau hasil.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entry": {"type": "string", "description": "Isi entri yang dicatat"},
                    "action_type": {
                        "type": "string",
                        "description": "Tipe: Edit | Test | Decision | Error | Command | Update | Result",
                        "default": "Update",
                    },
                },
                "required": ["entry"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "session_files_update",
            "description": "Catat file yang diperiksa, diubah, atau dibuat pada sesi aktif.",
            "parameters": {
                "type": "object",
                "properties": {
                    "inspected": {"type": "string", "description": "File diperiksa: 'path: alasan; path2: alasan2'", "default": ""},
                    "changed": {"type": "string", "description": "File diubah: 'path: perubahan; path2: perubahan2'", "default": ""},
                    "generated": {"type": "string", "description": "File baru dibuat: 'path: tujuan'", "default": ""},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "session_handoff",
            "description": (
                "Tulis instruksi serah terima untuk agen berikutnya. "
                "Gunakan sebelum mengakhiri sesi, sebelum handoff, atau saat pengguna disconnect."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Ringkasan kondisi saat ini (1 paragraf)"},
                    "next_actions": {"type": "string", "description": "Aksi berikutnya, pisah dengan ';'"},
                    "watch_outs": {"type": "string", "description": "Risiko/catatan penting, pisah dengan ';'", "default": ""},
                },
                "required": ["summary", "next_actions"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "session_read",
            "description": "Baca file sesi aktif: handoff, session_state, timeline, atau files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Nama file: handoff | session_state | timeline | files",
                        "default": "handoff",
                    },
                },
                "required": [],
            },
        },
    },
]

SESSION_TOOL_FUNCTIONS = {
    "session_start": session_start,
    "session_checkpoint": session_checkpoint,
    "session_recover": session_recover,
    "session_list": session_list,
    "session_timeline_append": session_timeline_append,
    "session_files_update": session_files_update,
    "session_handoff": session_handoff,
    "session_read": session_read,
}
