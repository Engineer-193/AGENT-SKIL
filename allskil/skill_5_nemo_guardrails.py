import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import WORK_DIR

SKILL_NAME = "NeMo Guardrails"
SKILL_DESC = "Configure and manage NVIDIA NeMo Guardrails for LLM safety, topic control, and policy enforcement"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "guardrails_init",
            "description": "Initialize a NeMo Guardrails configuration project",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "Name of the guardrails project"},
                    "template": {
                        "type": "string",
                        "enum": ["basic", "jailbreak", "topical", "custom"],
                        "description": "Guardrails template to start from"
                    }
                },
                "required": ["project_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "guardrails_add_rule",
            "description": "Add a guardrail rule (input/output/topic rail) to the configuration",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "Guardrails project name"},
                    "rail_type": {
                        "type": "string",
                        "enum": ["input", "output", "topic", "dialog"],
                        "description": "Type of guardrail"
                    },
                    "rule_name": {"type": "string", "description": "Name/identifier for this rule"},
                    "description": {"type": "string", "description": "What this rule blocks or allows"},
                    "action": {
                        "type": "string",
                        "enum": ["block", "allow", "redirect"],
                        "description": "Action to take when rule matches"
                    }
                },
                "required": ["project_name", "rail_type", "rule_name", "description", "action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "guardrails_test",
            "description": "Test a guardrails configuration with a sample prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "Guardrails project name"},
                    "prompt": {"type": "string", "description": "Test prompt to run through guardrails"},
                    "expected_behavior": {
                        "type": "string",
                        "enum": ["blocked", "allowed", "redirected"],
                        "description": "Expected outcome"
                    }
                },
                "required": ["project_name", "prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "guardrails_list",
            "description": "List all guardrail rules in a project",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "Guardrails project name"}
                },
                "required": ["project_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "guardrails_generate_config",
            "description": "Generate a complete NeMo Guardrails config.yml and .co files",
            "parameters": {
                "type": "object",
                "properties": {
                    "use_case": {"type": "string", "description": "Use case description, e.g. 'customer support bot', 'medical AI assistant'"},
                    "blocked_topics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Topics to block, e.g. ['politics', 'violence', 'competitor products']"
                    },
                    "allowed_topics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Topics explicitly allowed"
                    },
                    "output_dir": {"type": "string", "description": "Output directory for config files"}
                },
                "required": ["use_case"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "guardrails_serve",
            "description": "Start the NeMo Guardrails server for an existing config",
            "parameters": {
                "type": "object",
                "properties": {
                    "config_path": {"type": "string", "description": "Path to guardrails config directory"},
                    "port": {"type": "integer", "description": "Port to serve on, default 8111", "default": 8111}
                },
                "required": ["config_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "guardrails_explain",
            "description": "Explain how NeMo Guardrails works and available rail types",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": ["overview", "input_rails", "output_rails", "dialog_rails", "topical_rails", "integration"],
                        "description": "Topic to explain"
                    }
                },
                "required": ["topic"]
            }
        }
    }
]


def guardrails_init(project_name: str, template: str = "basic") -> str:
    templates = {
        "basic": "Basic input/output safety filtering",
        "jailbreak": "Anti-jailbreak and prompt injection protection",
        "topical": "Topic-focused rails (stay on-topic)",
        "custom": "Empty template for custom rules"
    }
    config_yml = f"""# NeMo Guardrails Config — {project_name}
models:
  - type: main
    engine: openai
    model: gpt-3.5-turbo

instructions:
  - type: general
    content: |
      You are a helpful AI assistant. You must follow all guardrail rules.

rails:
  input:
    flows:
      - self check input
  output:
    flows:
      - self check output
"""
    input_rail_co = f"""define user express greeting
  "hello"
  "hi"
  "hey"

define bot express greeting
  "Hello! How can I help you today?"

define flow greeting
  user express greeting
  bot express greeting
"""
    path = os.path.join(WORK_DIR, f"guardrails_{project_name}")
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "config.yml"), "w") as f:
        f.write(config_yml)
    with open(os.path.join(path, "rails.co"), "w") as f:
        f.write(input_rail_co)
    return (
        f"✅ Guardrails project '{project_name}' initialized!\n"
        f"Template: {template} — {templates.get(template, '')}\n"
        f"Location: {path}\n\n"
        f"Files created:\n"
        f"  📄 config.yml — main configuration\n"
        f"  📄 rails.co — Colang rules\n\n"
        f"Install: `pip install nemoguardrails`\n"
        f"Serve: `nemoguardrails server --config={path}`"
    )


def guardrails_add_rule(project_name: str, rail_type: str, rule_name: str, description: str, action: str) -> str:
    colang = f"""
# Rule: {rule_name}
# Type: {rail_type} | Action: {action}
define user {rule_name.lower().replace(' ', '_')}
  "{description}"

define bot respond_{rule_name.lower().replace(' ', '_')}
  "I'm not able to help with that topic."

define flow {rail_type}_{rule_name.lower().replace(' ', '_')}
  user {rule_name.lower().replace(' ', '_')}
  bot respond_{rule_name.lower().replace(' ', '_')}
"""
    path = os.path.join(WORK_DIR, f"guardrails_{project_name}", f"{rule_name}.co")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(colang)
    icons = {"block": "🚫", "allow": "✅", "redirect": "↪️"}
    return (
        f"{icons.get(action, '📌')} Rule added: **{rule_name}**\n"
        f"Type: `{rail_type}` | Action: `{action}`\n"
        f"Description: {description}\n"
        f"File: `{path}`\n\n"
        f"Colang rule:\n```\n{colang.strip()}\n```"
    )


def guardrails_test(project_name: str, prompt: str, expected_behavior: str = None) -> str:
    path = os.path.join(WORK_DIR, f"guardrails_{project_name}")
    cmd = f"nemoguardrails chat --config={path}"
    return (
        f"🧪 Test Guardrails — '{project_name}'\n"
        f"Prompt: `{prompt}`\n"
        f"Expected: {expected_behavior or 'auto-detect'}\n\n"
        f"Test via CLI:\n```bash\n{cmd}\n```\n"
        f"Or via Python:\n"
        f"```python\nfrom nemoguardrails import RailsConfig, LLMRails\n"
        f"config = RailsConfig.from_path('{path}')\n"
        f"rails = LLMRails(config)\n"
        f"response = rails.generate(messages=[{{'role': 'user', 'content': '{prompt}'}}])\n"
        f"print(response)\n```"
    )


def guardrails_list(project_name: str) -> str:
    path = os.path.join(WORK_DIR, f"guardrails_{project_name}")
    if not os.path.exists(path):
        return f"❌ Project '{project_name}' not found. Use `guardrails_init` first."
    files = [f for f in os.listdir(path) if f.endswith(".co")]
    if not files:
        return f"📋 No rules in '{project_name}' yet. Use `guardrails_add_rule` to add rules."
    return f"📋 Guardrail Rules in '{project_name}':\n" + "\n".join(f"  • {f}" for f in files)


def guardrails_generate_config(use_case: str, blocked_topics: list = None, allowed_topics: list = None, output_dir: str = None) -> str:
    blocked = blocked_topics or []
    allowed = allowed_topics or []
    out = output_dir or os.path.join(WORK_DIR, "guardrails_generated")
    os.makedirs(out, exist_ok=True)

    blocked_rules = "\n".join([
        f"define user ask about {t}\n  \"tell me about {t}\"\n\n"
        f"define bot refuse {t}\n  \"I'm not able to discuss {t}.\"\n\n"
        f"define flow block {t}\n  user ask about {t}\n  bot refuse {t}\n"
        for t in blocked
    ])

    config = f"""# Auto-generated NeMo Guardrails Config
# Use case: {use_case}

models:
  - type: main
    engine: openai
    model: gpt-4

instructions:
  - type: general
    content: |
      You are an AI assistant for: {use_case}.
      {"Blocked topics: " + ", ".join(blocked) if blocked else ""}
      {"Allowed topics: " + ", ".join(allowed) if allowed else ""}

rails:
  input:
    flows:
      - self check input
      - check blocked topics
  output:
    flows:
      - self check output
      - check output facts
"""
    with open(os.path.join(out, "config.yml"), "w") as f:
        f.write(config)
    with open(os.path.join(out, "rails.co"), "w") as f:
        f.write(blocked_rules or "# No blocked topics configured\n")

    return (
        f"✅ Guardrails config generated for: **{use_case}**\n"
        f"Blocked topics ({len(blocked)}): {', '.join(blocked) or 'none'}\n"
        f"Allowed topics ({len(allowed)}): {', '.join(allowed) or 'all'}\n"
        f"Output: `{out}`\n\n"
        f"Install & run:\n```bash\npip install nemoguardrails\nnemoguardrails server --config={out} --port=8111\n```"
    )


def guardrails_serve(config_path: str, port: int = 8111) -> str:
    return (
        f"🚀 Start NeMo Guardrails Server:\n"
        f"```bash\npip install nemoguardrails\nnemoguardrails server --config={config_path} --port={port}\n```\n\n"
        f"API will be available at: `http://localhost:{port}`\n"
        f"OpenAI-compatible endpoint: `http://localhost:{port}/v1/chat/completions`\n\n"
        f"Docker option:\n"
        f"```bash\ndocker run -p {port}:8111 \\\n"
        f"  -v {config_path}:/config \\\n"
        f"  nvcr.io/nvidia/nemo-guardrails:latest\n```"
    )


def guardrails_explain(topic: str) -> str:
    explanations = {
        "overview": (
            "📚 **NeMo Guardrails Overview**\n\n"
            "NeMo Guardrails adds programmable safety layers to LLM apps:\n"
            "• **Input Rails** — filter/validate user inputs before reaching LLM\n"
            "• **Output Rails** — validate/filter LLM responses before showing to user\n"
            "• **Dialog Rails** — control conversation flow using Colang language\n"
            "• **Topical Rails** — keep conversation on allowed topics\n\n"
            "Install: `pip install nemoguardrails`\n"
            "Docs: https://docs.nvidia.com/nemo/guardrails/"
        ),
        "input_rails": (
            "🔒 **Input Rails**\n\n"
            "Check and filter user messages before they reach the LLM:\n"
            "• Jailbreak detection\n• Prompt injection prevention\n"
            "• Profanity/PII filtering\n• Topic restriction\n\n"
            "Example Colang:\n```\ndefine flow self check input\n"
            "  $allowed = execute self_check_input\n"
            "  if not $allowed\n    bot refuse to respond\n    stop\n```"
        ),
        "output_rails": (
            "🔐 **Output Rails**\n\n"
            "Check LLM responses before delivering to user:\n"
            "• Fact checking\n• Sensitive info detection\n"
            "• Hallucination filtering\n• Policy compliance\n\n"
            "Example Colang:\n```\ndefine flow self check output\n"
            "  $allowed = execute self_check_output\n"
            "  if not $allowed\n    bot refuse to respond\n```"
        ),
        "dialog_rails": (
            "💬 **Dialog Rails (Colang)**\n\n"
            "Control conversation flow with Colang language:\n"
            "```colang\ndefine user ask weather\n  \"what's the weather?\"\n  \"is it raining?\"\n\n"
            "define bot answer weather\n  \"I can check the weather for you!\"\n\n"
            "define flow weather\n  user ask weather\n  bot answer weather\n```"
        ),
        "topical_rails": (
            "📌 **Topical Rails**\n\n"
            "Keep the bot on specific topics:\n"
            "```colang\ndefine user ask off topic\n  \"tell me a joke\"\n  \"what's in the news?\"\n\n"
            "define bot redirect to topic\n  \"I can only help with [your topic]. Let's stay focused!\"\n\n"
            "define flow off topic\n  user ask off topic\n  bot redirect to topic\n```"
        ),
        "integration": (
            "🔗 **Integration Options**\n\n"
            "• **LangChain**: `from nemoguardrails.integrations.langchain import RunnableRails`\n"
            "• **FastAPI**: Mount as middleware on existing API\n"
            "• **OpenAI drop-in**: Compatible with OpenAI SDK\n"
            "• **NIM**: Attach guardrails to any NIM endpoint\n\n"
            "Python quick start:\n```python\nfrom nemoguardrails import RailsConfig, LLMRails\n"
            "config = RailsConfig.from_path('./config')\nrails = LLMRails(config)\n```"
        )
    }
    return explanations.get(topic, f"Unknown topic: {topic}")


TOOL_HANDLERS = {
    "guardrails_init": guardrails_init,
    "guardrails_add_rule": guardrails_add_rule,
    "guardrails_test": guardrails_test,
    "guardrails_list": guardrails_list,
    "guardrails_generate_config": guardrails_generate_config,
    "guardrails_serve": guardrails_serve,
    "guardrails_explain": guardrails_explain,
}
