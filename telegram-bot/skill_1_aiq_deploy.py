"""
Skill 1 — NVIDIA AI-Q Deploy (aiq-deploy)
==========================================
Gunakan saat diminta untuk:
  install | deploy | run | validate | troubleshoot | stop
infrastruktur NVIDIA AI-Q Blueprint / NeMo Agent Toolkit.

Referensi: https://github.com/NVIDIA/NeMo-Agent-Toolkit
"""

import subprocess
import shutil
import os
import json
import signal
import logging
from typing import Any
from config import COMMAND_TIMEOUT, MAX_OUTPUT_LENGTH, WORK_DIR

logger = logging.getLogger(__name__)

AIQ_PROCESS_REGISTRY: dict[str, Any] = {}


def _run(cmd: str, cwd: str | None = None, timeout: int | None = None) -> tuple[int, str]:
    timeout = timeout or COMMAND_TIMEOUT
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd or WORK_DIR,
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return -1, f"⏱️ Timeout setelah {timeout} detik"
    except Exception as e:
        return -1, str(e)


def _trunc(text: str) -> str:
    if len(text) > MAX_OUTPUT_LENGTH:
        return text[:MAX_OUTPUT_LENGTH] + f"\n...[dipotong, total {len(text)} karakter]"
    return text


def aiq_install(package: str = "nvidia-nat", extras: str = "") -> str:
    """
    Install NVIDIA NeMo Agent Toolkit (AIQ Toolkit) via pip.
    package: nama paket (default: nvidia-nat)
    extras: extras pip, misal: 'langchain' → nvidia-nat[langchain]
    """
    target = f"{package}[{extras}]" if extras else package
    logger.info(f"[aiq_install] pip install {target}")

    code, out = _run(f"pip install {target} --quiet", timeout=180)
    if code == 0:
        code2, ver = _run("python -c \"import importlib.metadata; print(importlib.metadata.version('nvidia-nat'))\"")
        version_info = f"\n📦 Versi terpasang: `{ver.strip()}`" if code2 == 0 else ""
        return _trunc(
            f"✅ *AIQ Toolkit berhasil diinstall*{version_info}\n\n"
            f"```\n{out or '(instalasi selesai tanpa output)'}\n```"
        )
    return _trunc(f"❌ *Install gagal* (exit {code})\n```\n{out}\n```")


def aiq_deploy(
    workflow_path: str,
    config_file: str = "",
    port: int = 8000,
    background: bool = True,
) -> str:
    """
    Deploy/launch sebuah AIQ workflow.
    workflow_path: path ke file workflow .py atau .yaml
    config_file: path ke file konfigurasi opsional
    port: port server (default 8000)
    background: jalankan di background (default True)
    """
    if not os.path.exists(workflow_path):
        return f"❌ File workflow tidak ditemukan: `{workflow_path}`"

    config_arg = f"--config {config_file}" if config_file else ""
    cmd = f"aiq run {workflow_path} {config_arg} --port {port}"

    if background:
        logger.info(f"[aiq_deploy] background: {cmd}")
        try:
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=WORK_DIR,
            )
            key = f"{workflow_path}:{port}"
            AIQ_PROCESS_REGISTRY[key] = proc
            return (
                f"🚀 *AIQ Blueprint di-deploy (background)*\n"
                f"• Workflow: `{workflow_path}`\n"
                f"• Port: `{port}`\n"
                f"• PID: `{proc.pid}`\n"
                f"• Key: `{key}`\n\n"
                f"Gunakan `aiq_status` untuk cek atau `aiq_stop` untuk hentikan."
            )
        except Exception as e:
            return f"❌ Gagal deploy background: {e}"
    else:
        code, out = _run(cmd, timeout=120)
        status = "✅" if code == 0 else f"❌ (exit {code})"
        return _trunc(f"🚀 *AIQ Deploy* {status}\n```\n{out}\n```")


def aiq_run(
    workflow_path: str,
    query: str = "",
    config_file: str = "",
    extra_args: str = "",
) -> str:
    """
    Jalankan workflow AIQ secara sinkron (foreground) dengan query opsional.
    workflow_path: path ke workflow
    query: input/query untuk agent
    config_file: file konfigurasi opsional
    extra_args: argumen tambahan untuk CLI aiq
    """
    if not os.path.exists(workflow_path):
        return f"❌ File workflow tidak ditemukan: `{workflow_path}`"

    config_arg = f"--config {config_file}" if config_file else ""
    query_arg = f"--query \"{query}\"" if query else ""
    cmd = f"aiq run {workflow_path} {config_arg} {query_arg} {extra_args}".strip()

    logger.info(f"[aiq_run] {cmd}")
    code, out = _run(cmd, timeout=300)
    status = "✅ Selesai" if code == 0 else f"❌ exit {code}"
    return _trunc(f"▶️ *AIQ Run* — {status}\n\n```\n{out or '(tidak ada output)'}\n```")


def aiq_validate(
    workflow_path: str,
    eval_config: str = "",
    dataset: str = "",
) -> str:
    """
    Validasi/evaluasi workflow AIQ menggunakan evaluation system bawaan.
    workflow_path: path ke workflow
    eval_config: file konfigurasi evaluasi opsional
    dataset: path ke dataset evaluasi opsional
    """
    if not os.path.exists(workflow_path):
        return f"❌ File workflow tidak ditemukan: `{workflow_path}`"

    config_arg = f"--config {eval_config}" if eval_config else ""
    dataset_arg = f"--dataset {dataset}" if dataset else ""
    cmd = f"aiq eval {workflow_path} {config_arg} {dataset_arg}".strip()

    logger.info(f"[aiq_validate] {cmd}")

    checks: list[str] = []

    code_import, out_import = _run(
        f"python -c \"import importlib.util; spec=importlib.util.spec_from_file_location('w','{workflow_path}'); "
        f"m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print('OK')\"",
        timeout=30,
    )
    checks.append(
        f"• Import check: {'✅ OK' if code_import == 0 else f'❌ {out_import[:200]}'}"
    )

    code_aiq, out_aiq = _run("aiq --version", timeout=15)
    checks.append(
        f"• AIQ CLI: {'✅ ' + out_aiq.strip() if code_aiq == 0 else '❌ Tidak ditemukan'}"
    )

    if code_aiq == 0 and (eval_config or dataset):
        code_eval, out_eval = _run(cmd, timeout=300)
        checks.append(
            f"• Evaluasi: {'✅' if code_eval == 0 else f'❌ exit {code_eval}'}\n```\n{out_eval[:1000]}\n```"
        )

    summary = "\n".join(checks)
    return f"🔬 *AIQ Validate* — `{workflow_path}`\n\n{summary}"


def aiq_troubleshoot(
    workflow_path: str = "",
    process_key: str = "",
    check_deps: bool = True,
) -> str:
    """
    Diagnosa masalah pada infrastruktur AIQ.
    workflow_path: path ke workflow (opsional)
    process_key: key dari proses yang di-deploy background
    check_deps: periksa dependensi (default True)
    """
    report: list[str] = ["🩺 *AIQ Troubleshoot Report*\n"]

    if check_deps:
        packages = ["nvidia-nat", "aiq", "pydantic", "fastapi", "uvicorn"]
        dep_lines: list[str] = []
        for pkg in packages:
            code, out = _run(
                f"python -c \"import importlib.metadata; print(importlib.metadata.version('{pkg}'))\"",
                timeout=10,
            )
            dep_lines.append(f"  • `{pkg}`: {'✅ ' + out.strip() if code == 0 else '❌ tidak ada'}")
        report.append("*Dependensi:*\n" + "\n".join(dep_lines))

    code_py, out_py = _run("python --version", timeout=5)
    report.append(f"\n*Python:* `{out_py.strip() if code_py == 0 else 'tidak ditemukan'}`")

    code_aiq_path, out_aiq_path = _run("which aiq || echo 'not found'", timeout=5)
    report.append(f"*AIQ CLI path:* `{out_aiq_path.strip()}`")

    if process_key and process_key in AIQ_PROCESS_REGISTRY:
        proc = AIQ_PROCESS_REGISTRY[process_key]
        alive = proc.poll() is None
        report.append(
            f"\n*Proses `{process_key}`:*\n"
            f"  • PID: `{proc.pid}`\n"
            f"  • Status: {'🟢 berjalan' if alive else '🔴 berhenti'}"
        )
        if not alive:
            try:
                stdout, _ = proc.communicate(timeout=2)
                if stdout:
                    report.append(f"  • Output terakhir:\n```\n{stdout[:500]}\n```")
            except Exception:
                pass

    if workflow_path and os.path.exists(workflow_path):
        code_s, out_s = _run(f"python -m py_compile {workflow_path} && echo OK", timeout=15)
        report.append(
            f"\n*Syntax check `{workflow_path}`:* {'✅ OK' if code_s == 0 else f'❌ {out_s[:300]}'}"
        )

    code_env, out_env = _run("env | grep -E 'NVIDIA|OPENAI|AIQ|NEMO' | sort", timeout=5)
    if out_env.strip():
        report.append(f"\n*Env vars relevan:*\n```\n{out_env[:500]}\n```")
    else:
        report.append("\n*Env vars relevan:* tidak ada (NVIDIA_*, OPENAI_*, AIQ_*, NEMO_*)")

    return _trunc("\n".join(report))


def aiq_stop(process_key: str = "", port: int = 0) -> str:
    """
    Hentikan infrastruktur AIQ yang sedang berjalan.
    process_key: key proses dari aiq_deploy (format 'workflow:port')
    port: port yang ingin di-kill prosesnya (alternatif)
    """
    results: list[str] = []

    if process_key and process_key in AIQ_PROCESS_REGISTRY:
        proc = AIQ_PROCESS_REGISTRY[process_key]
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        del AIQ_PROCESS_REGISTRY[process_key]
        results.append(f"✅ Proses `{process_key}` (PID {proc.pid}) dihentikan.")

    if port:
        code, out = _run(f"lsof -ti :{port} | xargs kill -9 2>/dev/null && echo killed || echo not_found", timeout=10)
        if "killed" in out:
            results.append(f"✅ Proses di port `{port}` dihentikan.")
        else:
            results.append(f"ℹ️ Tidak ada proses aktif di port `{port}`.")

    if not process_key and not port:
        active_keys = list(AIQ_PROCESS_REGISTRY.keys())
        if active_keys:
            for key in active_keys:
                proc = AIQ_PROCESS_REGISTRY[key]
                try:
                    proc.terminate()
                    proc.wait(timeout=3)
                except Exception:
                    proc.kill()
                results.append(f"✅ Dihentikan: `{key}` (PID {proc.pid})")
            AIQ_PROCESS_REGISTRY.clear()
        else:
            results.append("ℹ️ Tidak ada proses AIQ aktif yang terdaftar.")

    return "🛑 *AIQ Stop*\n\n" + "\n".join(results) if results else "ℹ️ Tidak ada aksi yang dilakukan."


def aiq_status() -> str:
    """
    Tampilkan status semua proses AIQ yang aktif.
    """
    if not AIQ_PROCESS_REGISTRY:
        return "ℹ️ *AIQ Status*: Tidak ada proses yang terdaftar."

    lines = ["📊 *AIQ Status — Proses Aktif:*\n"]
    for key, proc in AIQ_PROCESS_REGISTRY.items():
        alive = proc.poll() is None
        lines.append(
            f"• `{key}`\n"
            f"  PID: `{proc.pid}` | Status: {'🟢 berjalan' if alive else '🔴 berhenti'}"
        )
    return "\n".join(lines)


AIQ_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "aiq_install",
            "description": (
                "Install NVIDIA AI-Q Blueprint / NeMo Agent Toolkit via pip. "
                "Gunakan saat pengguna meminta instalasi AIQ atau nvidia-nat."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "package": {
                        "type": "string",
                        "description": "Nama paket pip (default: nvidia-nat)",
                        "default": "nvidia-nat",
                    },
                    "extras": {
                        "type": "string",
                        "description": "Extras pip: 'langchain', 'llamaindex', 'crewai', dll. (opsional)",
                        "default": "",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "aiq_deploy",
            "description": (
                "Deploy/launch workflow NVIDIA AI-Q Blueprint. "
                "Gunakan saat diminta menerapkan atau menjalankan infrastruktur AIQ."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_path": {
                        "type": "string",
                        "description": "Path ke file workflow .py atau .yaml",
                    },
                    "config_file": {
                        "type": "string",
                        "description": "Path ke file konfigurasi (opsional)",
                        "default": "",
                    },
                    "port": {
                        "type": "integer",
                        "description": "Port server (default 8000)",
                        "default": 8000,
                    },
                    "background": {
                        "type": "boolean",
                        "description": "Jalankan di background (default true)",
                        "default": True,
                    },
                },
                "required": ["workflow_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "aiq_run",
            "description": (
                "Jalankan workflow AIQ secara sinkron dengan query opsional. "
                "Gunakan saat diminta menjalankan atau mengeksekusi agent AIQ."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_path": {
                        "type": "string",
                        "description": "Path ke file workflow",
                    },
                    "query": {
                        "type": "string",
                        "description": "Input query untuk agent (opsional)",
                        "default": "",
                    },
                    "config_file": {
                        "type": "string",
                        "description": "Path ke file konfigurasi (opsional)",
                        "default": "",
                    },
                    "extra_args": {
                        "type": "string",
                        "description": "Argumen CLI tambahan (opsional)",
                        "default": "",
                    },
                },
                "required": ["workflow_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "aiq_validate",
            "description": (
                "Validasi dan evaluasi workflow AIQ. "
                "Gunakan saat diminta memvalidasi, mengevaluasi, atau mengecek akurasi blueprint AIQ."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_path": {
                        "type": "string",
                        "description": "Path ke file workflow",
                    },
                    "eval_config": {
                        "type": "string",
                        "description": "Path ke file konfigurasi evaluasi (opsional)",
                        "default": "",
                    },
                    "dataset": {
                        "type": "string",
                        "description": "Path ke dataset evaluasi (opsional)",
                        "default": "",
                    },
                },
                "required": ["workflow_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "aiq_troubleshoot",
            "description": (
                "Diagnosa dan troubleshoot masalah infrastruktur NVIDIA AI-Q. "
                "Gunakan saat ada error, crash, atau diminta memecahkan masalah AIQ."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_path": {
                        "type": "string",
                        "description": "Path ke workflow yang bermasalah (opsional)",
                        "default": "",
                    },
                    "process_key": {
                        "type": "string",
                        "description": "Key proses background dari aiq_deploy (opsional)",
                        "default": "",
                    },
                    "check_deps": {
                        "type": "boolean",
                        "description": "Periksa dependensi (default true)",
                        "default": True,
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "aiq_stop",
            "description": (
                "Hentikan infrastruktur NVIDIA AI-Q yang sedang berjalan. "
                "Gunakan saat diminta menghentikan, mematikan, atau stop blueprint AIQ."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "process_key": {
                        "type": "string",
                        "description": "Key proses dari aiq_deploy (format 'workflow:port'), kosong = stop semua",
                        "default": "",
                    },
                    "port": {
                        "type": "integer",
                        "description": "Port yang proses-nya ingin di-kill (opsional)",
                        "default": 0,
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "aiq_status",
            "description": "Tampilkan status semua proses AIQ yang aktif.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

AIQ_TOOL_FUNCTIONS = {
    "aiq_install": aiq_install,
    "aiq_deploy": aiq_deploy,
    "aiq_run": aiq_run,
    "aiq_validate": aiq_validate,
    "aiq_troubleshoot": aiq_troubleshoot,
    "aiq_stop": aiq_stop,
    "aiq_status": aiq_status,
}
