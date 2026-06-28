import os
import subprocess
import io
import contextlib
import glob
import re
from typing import Any
from config import WORK_DIR, MAX_OUTPUT_LENGTH, COMMAND_TIMEOUT
from allskil.skill_1_aiq_deploy import AIQ_TOOL_DEFINITIONS, AIQ_TOOL_FUNCTIONS
from allskil.skill_2_session_memory import SESSION_TOOL_DEFINITIONS, SESSION_TOOL_FUNCTIONS
from allskil.skill_3_physical_ai import NUREC_TOOL_DEFINITIONS, NUREC_TOOL_FUNCTIONS

os.makedirs(WORK_DIR, exist_ok=True)


def _truncate(text: str) -> str:
    if len(text) > MAX_OUTPUT_LENGTH:
        return text[:MAX_OUTPUT_LENGTH] + f"\n... [terpotong, total {len(text)} karakter]"
    return text


def read_file(path: str) -> str:
    try:
        full_path = path if os.path.isabs(path) else os.path.join(WORK_DIR, path)
        if not os.path.exists(full_path):
            return f"❌ File tidak ditemukan: {full_path}"
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        lines = content.splitlines()
        return _truncate(f"📄 `{full_path}` ({len(lines)} baris):\n```\n{content}\n```")
    except Exception as e:
        return f"❌ Error membaca file: {e}"


def search_files(pattern: str, path: str = ".", file_glob: str = "*") -> str:
    try:
        search_dir = path if os.path.isabs(path) else os.path.join(WORK_DIR, path)
        results: list[str] = []
        regex = re.compile(pattern, re.IGNORECASE)
        matched_files = glob.glob(os.path.join(search_dir, "**", file_glob), recursive=True)
        for filepath in matched_files[:50]:
            if not os.path.isfile(filepath):
                continue
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    for lineno, line in enumerate(f, 1):
                        if regex.search(line):
                            results.append(f"`{filepath}:{lineno}`: {line.rstrip()}")
                            if len(results) >= 30:
                                break
            except Exception:
                continue
            if len(results) >= 30:
                break
        if not results:
            return f"🔍 Tidak ada hasil untuk `{pattern}` di `{search_dir}`"
        return _truncate(f"🔍 Hasil pencarian `{pattern}`:\n" + "\n".join(results))
    except Exception as e:
        return f"❌ Error search: {e}"


def terminal(command: str) -> str:
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=COMMAND_TIMEOUT, cwd=WORK_DIR,
        )
        output = result.stdout + result.stderr
        if not output.strip():
            output = "(tidak ada output)"
        status = "✅" if result.returncode == 0 else f"❌ (exit {result.returncode})"
        return _truncate(f"🖥️ `{command}` {status}\n```\n{output}\n```")
    except subprocess.TimeoutExpired:
        return f"⏱️ Timeout setelah {COMMAND_TIMEOUT} detik: `{command}`"
    except Exception as e:
        return f"❌ Error terminal: {e}"


def execute_code(code: str) -> str:
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            exec_globals: dict[str, Any] = {"__name__": "__main__"}
            exec(code, exec_globals)
        stdout_val = stdout_capture.getvalue()
        stderr_val = stderr_capture.getvalue()
        result_output = stdout_val + (f"\nSTDERR:\n{stderr_val}" if stderr_val else "")
        if not result_output.strip():
            result_output = "(tidak ada output)"
        return _truncate(f"🐍 Kode dieksekusi ✅\n```\n{result_output}\n```")
    except Exception as e:
        stdout_val = stdout_capture.getvalue()
        return _truncate(
            f"🐍 Kode error ❌: {type(e).__name__}: {e}"
            + (f"\nOutput:\n```\n{stdout_val}\n```" if stdout_val else "")
        )


BASE_TOOL_DEFINITIONS = [
    {"type": "function", "function": {"name": "read_file", "description": "Membaca isi file dari path yang diberikan.", "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "Path file (absolut atau relatif terhadap WORK_DIR)"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "search_files", "description": "Mencari pola teks/regex dalam file-file di direktori.", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string", "default": "."}, "file_glob": {"type": "string", "default": "*"}}, "required": ["pattern"]}}},
    {"type": "function", "function": {"name": "terminal", "description": "Menjalankan perintah shell/terminal.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "execute_code", "description": "Menjalankan kode Python secara langsung.", "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}}},
]

BASE_TOOL_FUNCTIONS: dict[str, Any] = {
    "read_file": read_file,
    "search_files": search_files,
    "terminal": terminal,
    "execute_code": execute_code,
}

TOOL_DEFINITIONS = [
    *BASE_TOOL_DEFINITIONS,
    *AIQ_TOOL_DEFINITIONS,
    *SESSION_TOOL_DEFINITIONS,
    *NUREC_TOOL_DEFINITIONS,
]

TOOL_FUNCTIONS: dict[str, Any] = {
    **BASE_TOOL_FUNCTIONS,
    **AIQ_TOOL_FUNCTIONS,
    **SESSION_TOOL_FUNCTIONS,
    **NUREC_TOOL_FUNCTIONS,
}
