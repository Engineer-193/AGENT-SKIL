import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import WORK_DIR

SKILL_NAME = "NVIDIA NIM Deploy"
SKILL_DESC = "Deploy and manage NVIDIA NIM (Inference Microservices) containers for self-hosted LLM inference"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "nim_pull",
            "description": "Pull a NVIDIA NIM container image from NGC registry",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "NIM model name, e.g. 'meta/llama-3.1-8b-instruct', 'mistralai/mistral-7b-instruct-v0.3'"
                    },
                    "tag": {
                        "type": "string",
                        "description": "Image tag, default 'latest'",
                        "default": "latest"
                    }
                },
                "required": ["model"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "nim_run",
            "description": "Run a NVIDIA NIM container and expose the OpenAI-compatible inference endpoint",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "NIM model name to run"
                    },
                    "port": {
                        "type": "integer",
                        "description": "Host port to expose, default 8000",
                        "default": 8000
                    },
                    "gpu": {
                        "type": "string",
                        "description": "GPU device(s) to use, e.g. 'all', '0', '0,1'",
                        "default": "all"
                    },
                    "extra_args": {
                        "type": "string",
                        "description": "Extra docker run arguments"
                    }
                },
                "required": ["model"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "nim_status",
            "description": "Check status of running NIM containers and their health endpoints",
            "parameters": {
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Specific container name, or omit to list all NIM containers"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "nim_stop",
            "description": "Stop and remove a running NIM container",
            "parameters": {
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Name of the NIM container to stop"
                    }
                },
                "required": ["container_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "nim_test",
            "description": "Test a running NIM endpoint with a sample inference request",
            "parameters": {
                "type": "object",
                "properties": {
                    "port": {
                        "type": "integer",
                        "description": "Port of the NIM endpoint, default 8000",
                        "default": 8000
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Test prompt to send",
                        "default": "Hello! Briefly introduce yourself."
                    },
                    "model": {
                        "type": "string",
                        "description": "Model name to use in the request"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "nim_list_models",
            "description": "List available NVIDIA NIM models from NGC catalog",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category: 'llm', 'vision', 'speech', 'embedding', or omit for all"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "nim_logs",
            "description": "Fetch logs from a running NIM container",
            "parameters": {
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Name of the NIM container"
                    },
                    "tail": {
                        "type": "integer",
                        "description": "Number of log lines to return, default 50",
                        "default": 50
                    }
                },
                "required": ["container_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "nim_scale",
            "description": "Scale NIM deployment using Docker Compose or Kubernetes",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "NIM model to scale"
                    },
                    "replicas": {
                        "type": "integer",
                        "description": "Number of replicas"
                    },
                    "platform": {
                        "type": "string",
                        "enum": ["docker-compose", "kubernetes"],
                        "description": "Deployment platform"
                    }
                },
                "required": ["model", "replicas", "platform"]
            }
        }
    }
]


def nim_pull(model: str, tag: str = "latest") -> str:
    img = f"nvcr.io/nim/{model}:{tag}"
    cmd = ["docker", "pull", img]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return f"✅ NIM image pulled: {img}\n{result.stdout[-500:] if result.stdout else ''}"
    return (
        f"🔧 nim_pull command:\n`docker pull {img}`\n\n"
        f"⚠️ Note: Ensure NGC_API_KEY is set and you have access to this NIM.\n"
        f"Steps:\n"
        f"1. Export NGC key: `export NGC_API_KEY=<your_key>`\n"
        f"2. Login: `docker login nvcr.io -u '$oauthtoken' -p $NGC_API_KEY`\n"
        f"3. Run: `docker pull {img}`\n"
        f"Error: {result.stderr[:300] if result.stderr else 'docker not available'}"
    )


def nim_run(model: str, port: int = 8000, gpu: str = "all", extra_args: str = "") -> str:
    safe_name = model.replace("/", "-").replace(".", "-")
    container_name = f"nim-{safe_name}"
    cmd = (
        f"docker run -d --name {container_name} "
        f"--gpus {gpu} "
        f"-e NGC_API_KEY=$NGC_API_KEY "
        f"-p {port}:8000 "
        f"-v ~/.cache/nim:/opt/nim/.cache "
        f"{extra_args} "
        f"nvcr.io/nim/{model}:latest"
    )
    return (
        f"🚀 NIM Run Command:\n```bash\n{cmd}\n```\n\n"
        f"Container name: `{container_name}`\n"
        f"Endpoint: `http://localhost:{port}/v1`\n\n"
        f"Health check: `curl http://localhost:{port}/v1/health/ready`\n"
        f"Test: `curl http://localhost:{port}/v1/models`"
    )


def nim_status(container_name: str = None) -> str:
    if container_name:
        cmd = ["docker", "inspect", "--format",
               "{{.State.Status}} | {{.State.StartedAt}}", container_name]
    else:
        cmd = ["docker", "ps", "--filter", "name=nim-", "--format",
               "table {{.Names}}\t{{.Status}}\t{{.Ports}}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return f"📊 NIM Status:\n```\n{result.stdout.strip()}\n```"
    return (
        f"📊 NIM Status Check:\n"
        f"Command: `docker ps --filter name=nim-`\n"
        f"No NIM containers running or docker unavailable.\n"
        f"Start with: `nim_run(model='meta/llama-3.1-8b-instruct')`"
    )


def nim_stop(container_name: str) -> str:
    cmd = f"docker stop {container_name} && docker rm {container_name}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        return f"✅ NIM container stopped and removed: {container_name}"
    return (
        f"🛑 Stop NIM Container:\n"
        f"```bash\ndocker stop {container_name} && docker rm {container_name}\n```\n"
        f"Result: {result.stderr[:200] if result.stderr else 'Run command above manually'}"
    )


def nim_test(port: int = 8000, prompt: str = "Hello! Briefly introduce yourself.", model: str = None) -> str:
    import json
    payload = {
        "model": model or "auto",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100
    }
    curl_cmd = (
        f"curl -s http://localhost:{port}/v1/chat/completions \\\n"
        f"  -H 'Content-Type: application/json' \\\n"
        f"  -d '{json.dumps(payload)}'"
    )
    try:
        import urllib.request
        req_data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"http://localhost:{port}/v1/chat/completions",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            content = result["choices"][0]["message"]["content"]
            return f"✅ NIM Test Success!\nResponse: {content}"
    except Exception as e:
        return (
            f"🧪 NIM Test Command:\n```bash\n{curl_cmd}\n```\n"
            f"Error connecting to localhost:{port} — ensure NIM container is running.\n"
            f"Health check: `curl http://localhost:{port}/v1/health/ready`"
        )


def nim_list_models(category: str = None) -> str:
    models = {
        "llm": [
            "meta/llama-3.1-8b-instruct",
            "meta/llama-3.1-70b-instruct",
            "meta/llama-3.1-405b-instruct",
            "mistralai/mistral-7b-instruct-v0.3",
            "mistralai/mixtral-8x7b-instruct-v0.1",
            "microsoft/phi-3-mini-4k-instruct",
            "google/gemma-2-9b-it",
            "nvidia/nemotron-4-340b-instruct",
        ],
        "embedding": [
            "nvidia/nv-embedqa-e5-v5",
            "nvidia/nv-embedqa-mistral-7b-v2",
            "snowflake/arctic-embed-l",
        ],
        "vision": [
            "microsoft/phi-3-vision-128k-instruct",
            "meta/llama-3.2-11b-vision-instruct",
            "nvidia/neva-22b",
        ],
        "speech": [
            "nvidia/parakeet-ctc-1.1b-asr",
            "nvidia/conformer-ctc-large",
        ],
        "reranking": [
            "nvidia/nv-rerankqa-mistral-4b-v3",
        ]
    }
    if category and category in models:
        items = "\n".join(f"  • `{m}`" for m in models[category])
        return f"📋 NIM Models [{category}]:\n{items}"
    result = []
    for cat, items in models.items():
        result.append(f"**{cat.upper()}**")
        for m in items:
            result.append(f"  • `{m}`")
    return "📋 Available NVIDIA NIM Models:\n" + "\n".join(result)


def nim_logs(container_name: str, tail: int = 50) -> str:
    cmd = ["docker", "logs", "--tail", str(tail), container_name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        output = result.stdout or result.stderr
        return f"📜 NIM Logs [{container_name}] (last {tail} lines):\n```\n{output[-1500:]}\n```"
    return (
        f"📜 View NIM Logs:\n"
        f"```bash\ndocker logs --tail {tail} {container_name}\n```"
    )


def nim_scale(model: str, replicas: int, platform: str) -> str:
    safe_name = model.replace("/", "-").replace(".", "-")
    if platform == "docker-compose":
        compose = f"""version: '3.8'
services:
  nim-{safe_name}:
    image: nvcr.io/nim/{model}:latest
    deploy:
      replicas: {replicas}
    environment:
      - NGC_API_KEY=${{NGC_API_KEY}}
    volumes:
      - ~/.cache/nim:/opt/nim/.cache
    ports:
      - "8000-{8000+replicas-1}:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              capabilities: [gpu]
"""
        return (
            f"📦 Docker Compose Scale ({replicas}x {model}):\n"
            f"```yaml\n{compose}\n```\n"
            f"Run: `docker compose up -d --scale nim-{safe_name}={replicas}`"
        )
    else:
        return (
            f"☸️ Kubernetes Scale ({replicas}x {model}):\n"
            f"```bash\nkubectl scale deployment nim-{safe_name} --replicas={replicas}\n```\n"
            f"Or use NVIDIA GPU Operator + NIM Operator for full K8s deployment."
        )


TOOL_HANDLERS = {
    "nim_pull": nim_pull,
    "nim_run": nim_run,
    "nim_status": nim_status,
    "nim_stop": nim_stop,
    "nim_test": nim_test,
    "nim_list_models": nim_list_models,
    "nim_logs": nim_logs,
    "nim_scale": nim_scale,
}
