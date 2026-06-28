"""
Skill 2 — NeMo RL Session Memory (nemo-rl-session-memory)
==========================================================
Kelola memori sesi kerja yang tahan lama untuk agen pengkodean.

npx skills add NVIDIA/skills --skill nemo-rl-session-memory
Referensi: https://github.com/NVIDIA/skills/tree/main/skills/nemo-rl-session-memory

Gunakan saat: simpan/pulihkan konteks, pekerjaan panjang, handoff, disconnect, restart.
JANGAN gunakan untuk: pertanyaan singkat, satu perintah, linting, code review.
"""

import os
import logging
from datetime import datetime
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
        return text[:MAX_OUTPUT_LENGTH] + f"\n...[dipotong, {len(text)} karakter]"
    return text

def _write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def _read(path: str) -> str:
    if not os.path.exists(path): return ""
    with open(path, "r", encoding="utf-8") as f: return f.read()

def _append(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)


def session_start(goal: str, subtask: str = "", repo_path: str = "", branch: str = "",
                  loaded_skills: str = "Skill 1: aiq-deploy, Skill 2: nemo-rl-session-memory, Skill 3: physical-ai-neural-reconstruction",
                  resume: bool = False) -> str:
    global _ACTIVE_SESSION
    os.makedirs(SESSION_BASE, exist_ok=True)
    if resume:
        existing = sorted([d for d in os.listdir(SESSION_BASE) if os.path.isdir(os.path.join(SESSION_BASE, d))], reverse=True)
        if existing:
            sdir = os.path.join(SESSION_BASE, existing[0])
            _ACTIVE_SESSION = {"id": existing[0], "dir": sdir}
            handoff = _read(os.path.join(sdir, "handoff.md"))
            state = _read(os.path.join(sdir, "session_state.md"))
            _append(os.path.join(sdir, "timeline.md"), f"\n## {_now()}\n- Recovery: Sesi dilanjutkan\n- Goal: {goal}\n")
            return _trunc(f"🔄 *Sesi dilanjutkan*: `{existing[0]}`\n\n**📋 Handoff:**\n{handoff or '(kosong)'}\n\n**📊 State:**\n{state[:600] if state else '(kosong)'}")
    sid = _session_id()
    sdir = os.path.join(SESSION_BASE, sid)
    os.makedirs(sdir, exist_ok=True)
    _ACTIVE_SESSION = {"id": sid, "dir": sdir}
    _write(os.path.join(sdir, "session_state.md"), f"# Session State\n\n- Session: {sid}\n- Repo: {repo_path or WORK_DIR}\n- Branch: {branch or '(tidak diketahui)'}\n- Started: {_now()}\n- Updated: {_now()}\n\n## Goal\n{goal}\n\n## Current Subtask\n{subtask or '(belum ditentukan)'}\n\n## Loaded Skills\n{loaded_skills}\n\n## Current Status\nSesi baru dimulai.\n\n## Plan\n- [ ] Kumpulkan konteks\n- [ ] Tentukan subtask\n- [ ] Eksekusi\n\n## Blockers\n- None known\n")
    _write(os.path.join(sdir, "timeline.md"), f"# Timeline\n\n## {_now()}\n- Sesi dimulai | Goal: {goal}\n")
    _write(os.path.join(sdir, "files.md"), f"# Files\n\n## Inspected\n- (belum ada)\n\n## Changed\n- (belum ada)\n\n## Generated\n- `session/{sid}/` — file sesi\n")
    _write(os.path.join(sdir, "handoff.md"), f"# Handoff\n\n## Resume From Here\nSesi baru: {goal}\n\n## Next Actions\n- Tentukan subtask pertama\n\n## Watch Outs\n- (belum ada)\n")
    return f"✅ *Sesi dimulai*: `{sid}`\n🎯 Goal: {goal}\n📌 Subtask: {subtask or '(belum ditentukan)'}\n\nFile: session_state.md | timeline.md | files.md | handoff.md"


def session_checkpoint(status: str, subtask: str = "", plan_done: str = "", plan_next: str = "", decisions: str = "", blockers: str = "None known") -> str:
    sdir = _active_dir()
    if not sdir: return "⚠️ Belum ada sesi aktif. Jalankan `session_start`."
    state_path = os.path.join(sdir, "session_state.md")
    state = _read(state_path)
    updated = []
    for line in state.splitlines():
        if line.startswith("- Updated:"): updated.append(f"- Updated: {_now()}")
        elif line.startswith("## Current Subtask"): updated.append(line); updated.append(subtask or "(tidak berubah)")
        elif line.startswith("## Current Status"): updated.append(line); updated.append(status)
        elif line.startswith("## Plan"):
            updated.append(line)
            for s in plan_done.split(";"): 
                if s.strip(): updated.append(f"- [x] {s.strip()}")
            for s in plan_next.split(";"):
                if s.strip(): updated.append(f"- [ ] {s.strip()}")
        elif line.startswith("## Blockers"): updated.append(line); updated.append(f"- {blockers}")
        else: updated.append(line)
    _write(state_path, "\n".join(updated))
    _append(os.path.join(sdir, "timeline.md"), f"\n## {_now()}\n- Checkpoint | Status: {status}" + (f" | Decision: {decisions}" if decisions else "") + "\n")
    _write(os.path.join(sdir, "handoff.md"), f"# Handoff\n\n## Resume From Here\n{status}\n\n## Next Actions\n" + ("\n".join(f"- {s.strip()}" for s in plan_next.split(";") if s.strip()) or "- (lihat session_state.md)") + f"\n\n## Watch Outs\n- {blockers}\n")
    return f"💾 *Checkpoint disimpan* — `{_ACTIVE_SESSION.get('id')}`\n📊 {status[:200]}\n⏱️ {_now()}"


def session_recover(session_id: str = "") -> str:
    global _ACTIVE_SESSION
    os.makedirs(SESSION_BASE, exist_ok=True)
    sessions = sorted([d for d in os.listdir(SESSION_BASE) if os.path.isdir(os.path.join(SESSION_BASE, d))], reverse=True)
    if not sessions: return "ℹ️ Tidak ada sesi tersimpan."
    target = session_id if session_id and session_id in sessions else sessions[0]
    sdir = os.path.join(SESSION_BASE, target)
    _ACTIVE_SESSION = {"id": target, "dir": sdir}
    handoff = _read(os.path.join(sdir, "handoff.md"))
    state = _read(os.path.join(sdir, "session_state.md"))
    tl = _read(os.path.join(sdir, "timeline.md")).splitlines()
    recent = "\n".join(tl[-25:])
    _append(os.path.join(sdir, "timeline.md"), f"\n## {_now()}\n- Recovery: Agen baru terhubung\n")
    return _trunc(f"🔄 *Dipulihkan*: `{target}`\n\n**Handoff:**\n```\n{handoff or '(kosong)'}\n```\n\n**State:**\n```\n{state[:500]}\n```\n\n**Timeline Terakhir:**\n```\n{recent}\n```")


def session_list() -> str:
    os.makedirs(SESSION_BASE, exist_ok=True)
    sessions = sorted([d for d in os.listdir(SESSION_BASE) if os.path.isdir(os.path.join(SESSION_BASE, d))], reverse=True)
    if not sessions: return "ℹ️ Tidak ada sesi tersimpan."
    lines = [f"📚 *Sesi ({len(sessions)} total):*\n"]
    for i, sid in enumerate(sessions[:20]):
        sdir = os.path.join(SESSION_BASE, sid)
        marker = " ← *aktif*" if sid == _ACTIVE_SESSION.get("id") else ""
        preview = ""
        hp = os.path.join(sdir, "handoff.md")
        if os.path.exists(hp):
            with open(hp) as f:
                for line in f:
                    l = line.strip()
                    if l and not l.startswith("#"):
                        preview = l[:80]; break
        lines.append(f"`{i+1}.` `{sid}`{marker}\n    _{preview}_")
    return "\n".join(lines)


def session_timeline_append(entry: str, action_type: str = "Update") -> str:
    sdir = _active_dir()
    if not sdir: return "⚠️ Belum ada sesi aktif."
    _append(os.path.join(sdir, "timeline.md"), f"\n## {_now()}\n- [{action_type}] {entry}\n")
    return f"📝 Timeline — `[{action_type}]` {entry[:100]}"


def session_files_update(inspected: str = "", changed: str = "", generated: str = "") -> str:
    sdir = _active_dir()
    if not sdir: return "⚠️ Belum ada sesi aktif."
    sections = [f"\n---\n_Updated: {_now()}_"]
    for items, label in [(inspected, "Inspected"), (changed, "Changed"), (generated, "Generated")]:
        if items:
            sections.append(f"\n## {label}")
            for item in items.split(";"):
                item = item.strip()
                if ":" in item:
                    p, r = item.split(":", 1)
                    sections.append(f"- `{p.strip()}` — {r.strip()}")
                elif item:
                    sections.append(f"- `{item}`")
    _append(os.path.join(sdir, "files.md"), "\n".join(sections) + "\n")
    _append(os.path.join(sdir, "timeline.md"), f"\n## {_now()}\n- [Files] Changed: {changed[:100]}\n")
    return f"📁 *files.md diupdate* — `{_ACTIVE_SESSION.get('id')}`"


def session_handoff(summary: str, next_actions: str, watch_outs: str = "") -> str:
    sdir = _active_dir()
    if not sdir: return "⚠️ Belum ada sesi aktif."
    actions = "\n".join(f"- {a.strip()}" for a in next_actions.split(";") if a.strip())
    watches = "\n".join(f"- {w.strip()}" for w in watch_outs.split(";") if w.strip()) if watch_outs else "- (tidak ada)"
    _write(os.path.join(sdir, "handoff.md"), f"# Handoff\n\n_Updated: {_now()}_\n\n## Resume From Here\n{summary}\n\n## Next Actions\n{actions}\n\n## Watch Outs\n{watches}\n")
    _append(os.path.join(sdir, "timeline.md"), f"\n## {_now()}\n- [Handoff] Ditulis | Next: {next_actions[:150]}\n")
    return f"🤝 *Handoff ditulis* — `{_ACTIVE_SESSION.get('id')}`\n📋 {summary[:200]}\n➡️\n{actions}"


def session_read(file: str = "handoff") -> str:
    sdir = _active_dir()
    if not sdir: return "⚠️ Belum ada sesi aktif."
    mapping = {"handoff": "handoff.md", "session_state": "session_state.md", "state": "session_state.md", "timeline": "timeline.md", "files": "files.md"}
    filename = mapping.get(file.lower().replace(".md", ""), f"{file}.md")
    content = _read(os.path.join(sdir, filename))
    if not content: return f"ℹ️ `{filename}` kosong atau tidak ada."
    return _trunc(f"📖 *`{filename}`* — `{_ACTIVE_SESSION.get('id')}`\n```\n{content}\n```")


SESSION_TOOL_DEFINITIONS = [
    {"type": "function", "function": {"name": "session_start", "description": "Mulai sesi memori baru atau lanjutkan terakhir. Gunakan untuk pekerjaan panjang atau saat user minta simpan konteks.", "parameters": {"type": "object", "properties": {"goal": {"type": "string"}, "subtask": {"type": "string", "default": ""}, "repo_path": {"type": "string", "default": ""}, "branch": {"type": "string", "default": ""}, "loaded_skills": {"type": "string", "default": ""}, "resume": {"type": "boolean", "default": False}}, "required": ["goal"]}}},
    {"type": "function", "function": {"name": "session_checkpoint", "description": "Tulis checkpoint sesi aktif. Gunakan sebelum/sesudah edit penting atau tiap 30 menit.", "parameters": {"type": "object", "properties": {"status": {"type": "string"}, "subtask": {"type": "string", "default": ""}, "plan_done": {"type": "string", "default": ""}, "plan_next": {"type": "string", "default": ""}, "decisions": {"type": "string", "default": ""}, "blockers": {"type": "string", "default": "None known"}}, "required": ["status"]}}},
    {"type": "function", "function": {"name": "session_recover", "description": "Pulihkan sesi setelah disconnect/restart/handoff.", "parameters": {"type": "object", "properties": {"session_id": {"type": "string", "default": ""}}, "required": []}}},
    {"type": "function", "function": {"name": "session_list", "description": "Tampilkan semua sesi tersimpan.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "session_timeline_append", "description": "Catat aksi/keputusan/hasil ke timeline sesi.", "parameters": {"type": "object", "properties": {"entry": {"type": "string"}, "action_type": {"type": "string", "default": "Update"}}, "required": ["entry"]}}},
    {"type": "function", "function": {"name": "session_files_update", "description": "Catat file yang diperiksa, diubah, atau dibuat.", "parameters": {"type": "object", "properties": {"inspected": {"type": "string", "default": ""}, "changed": {"type": "string", "default": ""}, "generated": {"type": "string", "default": ""}}, "required": []}}},
    {"type": "function", "function": {"name": "session_handoff", "description": "Tulis instruksi serah terima untuk agen berikutnya.", "parameters": {"type": "object", "properties": {"summary": {"type": "string"}, "next_actions": {"type": "string"}, "watch_outs": {"type": "string", "default": ""}}, "required": ["summary", "next_actions"]}}},
    {"type": "function", "function": {"name": "session_read", "description": "Baca file sesi: handoff | session_state | timeline | files.", "parameters": {"type": "object", "properties": {"file": {"type": "string", "default": "handoff"}}, "required": []}}},
]

SESSION_TOOL_FUNCTIONS = {
    "session_start": session_start, "session_checkpoint": session_checkpoint,
    "session_recover": session_recover, "session_list": session_list,
    "session_timeline_append": session_timeline_append, "session_files_update": session_files_update,
    "session_handoff": session_handoff, "session_read": session_read,
}
