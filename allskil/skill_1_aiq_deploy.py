"""
Skill 1 — NVIDIA AI-Q Deploy (aiq-deploy)
==========================================
Gunakan saat diminta untuk:
  install | deploy | run | validate | troubleshoot | stop
infrastruktur NVIDIA AI-Q Blueprint / NeMo Agent Toolkit.

npx skills add NVIDIA/skills --skill aiq-deploy
Referensi: https://github.com/NVIDIA/NeMo-Agent-Toolkit
"""

import subprocess
import os
import logging
from typing import Any
from config import COMMAND_TIMEOUT, MAX_OUTPUT_LENGTH, WORK_DIR

logger = logging.getLogger(__name__)

AIQ_PROCESS_REGISTRY: dict[str, Any] = {}


def _run(cmd: str, cwd: str | None = None, timeout: int | None = None) -> tuple[int, str]:
    timeout = timeout or COMMAND_TIMEOUT
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=cwd or WORK_DIR,
        )
        return result.returncode, (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return -1, f"⏱️ Timeout setelah {timeout} detik"
    except Exception as e:
        return -1, str(e)


def _trunc(text: str) -> str:
    if len(text) > MAX_OUTPUT_LENGTH:
        return text[:MAX_OUTPUT_LENGTH] + f"\n...[dipotong, {len(text)} karakter]"
    return text


def aiq_install(package: str = "nvidia-nat", extras: str = "") -> str:
    target = f"{package}[{extras}]" if extras else package
    logger.info(f"[aiq_install] pip install {target}")
    code, out = _run(f"pip install {target} --quiet", timeout=180)
    if code == 0:
        code2, ver = _run("python -c \"import importlib.metadata; print(importlib.metadata.version('nvidia-nat'))\"")
        ver_info = f"\n📦 Versi: `{ver.strip()}`" if code2 == 0 else ""
        return _trunc(f"✅ *AIQ Toolkit terinstall*{ver_info}\n```\n{out or '(selesai)'}\n```")
    return _trunc(f"❌ *Install gagal* (exit {code})\n```\n{out}\n```")


def aiq_deploy(workflow_path: str, config_file: str = "", port: int = 8000, background: bool = True) -> str:
    if not os.path.exists(workflow_path):
        return f"❌ File tidak ditemukan: `{workflow_path}`"
    config_arg = f"--config {config_file}" if config_file else ""
    cmd = f"aiq run {workflow_path} {config_arg} --port {port}"
    if background:
        try:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, cwd=WORK_DIR)
            key = f"{workflow_path}:{port}"
            AIQ_PROCESS_REGISTRY[key] = proc
            return (f"🚀 *AIQ Deploy (background)*\n• Workflow: `{workflow_path}`\n"
                    f"• Port: `{port}` | PID: `{proc.pid}` | Key: `{key}`")
        except Exception as e:
            return f"❌ Gagal deploy: {e}"
    code, out = _run(cmd, timeout=120)
    return _trunc(f"🚀 *AIQ Deploy* {'✅' if code == 0 else f'❌ exit {code}'}\n```\n{out}\n```")


def aiq_run(workflow_path: str, query: str = "", config_file: str = "", extra_args: str = "") -> str:
    if not os.path.exists(workflow_path):
        return f"❌ File tidak ditemukan: `{workflow_path}`"
    config_arg = f"--config {config_file}" if config_file else ""
    query_arg = f"--query \"{query}\"" if query else ""
    cmd = f"aiq run {workflow_path} {config_arg} {query_arg} {extra_args}".strip()
    code, out = _run(cmd, timeout=300)
    return _trunc(f"▶️ *AIQ Run* — {'✅ Selesai' if code == 0 else f'❌ exit {code}'}\n```\n{out}\n```")


def aiq_validate(workflow_path: str, eval_config: str = "", dataset: str = "") -> str:
    if not os.path.exists(workflow_path):
        return f"❌ File tidak ditemukan: `{workflow_path}`"
    checks = []
    code, out = _run(f"python -m py_compile {workflow_path} && echo OK", timeout=15)
    checks.append(f"• Syntax: {'✅ OK' if code == 0 else f'❌ {out[:200]}'}")
    code2, ver = _run("aiq --version", timeout=15)
    checks.append(f"• AIQ CLI: {'✅ ' + ver.strip() if code2 == 0 else '❌ Tidak ditemukan'}")
    if eval_config or dataset:
        config_arg = f"--config {eval_config}" if eval_config else ""
        dataset_arg = f"--dataset {dataset}" if dataset else ""
        code3, out3 = _run(f"aiq eval {workflow_path} {config_arg} {dataset_arg}", timeout=300)
        checks.append(f"• Evaluasi: {'✅' if code3 == 0 else f'❌ exit {code3}'}\n```\n{out3[:800]}\n```")
    return f"🔬 *AIQ Validate* — `{workflow_path}`\n\n" + "\n".join(checks)


def aiq_troubleshoot(workflow_path: str = "", process_key: str = "", check_deps: bool = True) -> str:
    report = ["🩺 *AIQ Troubleshoot*\n"]
    if check_deps:
        lines = []
        for pkg in ["nvidia-nat", "aiq", "pydantic", "fastapi", "uvicorn"]:
            code, out = _run(f"python -c \"import importlib.metadata; print(importlib.metadata.version('{pkg}'))\"", timeout=10)
            lines.append(f"  • `{pkg}`: {'✅ ' + out.strip() if code == 0 else '❌'}")
        report.append("*Deps:*\n" + "\n".join(lines))
    code_py, out_py = _run("python --version", timeout=5)
    report.append(f"\n*Python:* `{out_py.strip()}`")
    if process_key and process_key in AIQ_PROCESS_REGISTRY:
        proc = AIQ_PROCESS_REGISTRY[process_key]
        alive = proc.poll() is None
        report.append(f"\n*Proses `{process_key}`:* PID `{proc.pid}` — {'🟢 berjalan' if alive else '🔴 berhenti'}")
    if workflow_path and os.path.exists(workflow_path):
        code_s, out_s = _run(f"python -m py_compile {workflow_path} && echo OK", timeout=15)
        report.append(f"\n*Syntax `{workflow_path}`:* {'✅ OK' if code_s == 0 else f'❌ {out_s[:200]}'}")
    code_env, out_env = _run("env | grep -E 'NVIDIA|OPENAI|AIQ|NEMO' | sort", timeout=5)
    if out_env.strip():
        report.append(f"\n*Env:*\n```\n{out_env[:400]}\n```")
    return _trunc("\n".join(report))


def aiq_stop(process_key: str = "", port: int = 0) -> str:
    results = []
    if process_key and process_key in AIQ_PROCESS_REGISTRY:
        proc = AIQ_PROCESS_REGISTRY.pop(process_key)
        try:
            proc.terminate(); proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        results.append(f"✅ `{process_key}` (PID {proc.pid}) dihentikan.")
    if port:
        code, out = _run(f"lsof -ti :{port} | xargs kill -9 2>/dev/null && echo killed || echo not_found", timeout=10)
        results.append(f"✅ Port `{port}` dihentikan." if "killed" in out else f"ℹ️ Tidak ada proses di port `{port}`.")
    if not process_key and not port:
        if AIQ_PROCESS_REGISTRY:
            for key, proc in list(AIQ_PROCESS_REGISTRY.items()):
                try: proc.terminate(); proc.wait(timeout=3)
                except Exception: proc.kill()
                results.append(f"✅ `{key}` (PID {proc.pid}) dihentikan.")
            AIQ_PROCESS_REGISTRY.clear()
        else:
            results.append("ℹ️ Tidak ada proses AIQ aktif.")
    return "🛑 *AIQ Stop*\n\n" + "\n".join(results)


def aiq_status() -> str:
    if not AIQ_PROCESS_REGISTRY:
        return "ℹ️ *AIQ Status*: Tidak ada proses terdaftar."
    lines = ["📊 *AIQ Status:*\n"]
    for key, proc in AIQ_PROCESS_REGISTRY.items():
        alive = proc.poll() is None
        lines.append(f"• `{key}` | PID `{proc.pid}` | {'🟢 berjalan' if alive else '🔴 berhenti'}")
    return "\n".join(lines)


AIQ_TOOL_DEFINITIONS = [
    {"type": "function", "function": {"name": "aiq_install", "description": "Install NVIDIA AI-Q Blueprint / NeMo Agent Toolkit via pip.", "parameters": {"type": "object", "properties": {"package": {"type": "string", "default": "nvidia-nat"}, "extras": {"type": "string", "default": ""}}, "required": []}}},
    {"type": "function", "function": {"name": "aiq_deploy", "description": "Deploy/launch workflow NVIDIA AI-Q Blueprint (background/foreground).", "parameters": {"type": "object", "properties": {"workflow_path": {"type": "string"}, "config_file": {"type": "string", "default": ""}, "port": {"type": "integer", "default": 8000}, "background": {"type": "boolean", "default": True}}, "required": ["workflow_path"]}}},
    {"type": "function", "function": {"name": "aiq_run", "description": "Jalankan workflow AIQ secara sinkron dengan query opsional.", "parameters": {"type": "object", "properties": {"workflow_path": {"type": "string"}, "query": {"type": "string", "default": ""}, "config_file": {"type": "string", "default": ""}, "extra_args": {"type": "string", "default": ""}}, "required": ["workflow_path"]}}},
    {"type": "function", "function": {"name": "aiq_validate", "description": "Validasi dan evaluasi workflow AIQ.", "parameters": {"type": "object", "properties": {"workflow_path": {"type": "string"}, "eval_config": {"type": "string", "default": ""}, "dataset": {"type": "string", "default": ""}}, "required": ["workflow_path"]}}},
    {"type": "function", "function": {"name": "aiq_troubleshoot", "description": "Diagnosa masalah infrastruktur NVIDIA AI-Q.", "parameters": {"type": "object", "properties": {"workflow_path": {"type": "string", "default": ""}, "process_key": {"type": "string", "default": ""}, "check_deps": {"type": "boolean", "default": True}}, "required": []}}},
    {"type": "function", "function": {"name": "aiq_stop", "description": "Hentikan infrastruktur NVIDIA AI-Q yang berjalan.", "parameters": {"type": "object", "properties": {"process_key": {"type": "string", "default": ""}, "port": {"type": "integer", "default": 0}}, "required": []}}},
    {"type": "function", "function": {"name": "aiq_status", "description": "Status semua proses AIQ aktif.", "parameters": {"type": "object", "properties": {}, "required": []}}},
]

AIQ_TOOL_FUNCTIONS = {
    "aiq_install": aiq_install, "aiq_deploy": aiq_deploy, "aiq_run": aiq_run,
    "aiq_validate": aiq_validate, "aiq_troubleshoot": aiq_troubleshoot,
    "aiq_stop": aiq_stop, "aiq_status": aiq_status,
}
