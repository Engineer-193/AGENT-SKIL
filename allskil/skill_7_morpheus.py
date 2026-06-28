import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import WORK_DIR

SKILL_NAME = "NVIDIA Morpheus"
SKILL_DESC = "NVIDIA Morpheus AI cybersecurity framework for real-time threat detection, network analysis, and security workflows"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "morpheus_setup",
            "description": "Set up NVIDIA Morpheus cybersecurity AI framework",
            "parameters": {
                "type": "object",
                "properties": {
                    "install_method": {
                        "type": "string",
                        "enum": ["conda", "docker", "source"],
                        "description": "Installation method"
                    },
                    "version": {"type": "string", "description": "Morpheus version, default 'latest'", "default": "latest"}
                },
                "required": ["install_method"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "morpheus_run_pipeline",
            "description": "Run a Morpheus cybersecurity pipeline on log/network data",
            "parameters": {
                "type": "object",
                "properties": {
                    "pipeline_type": {
                        "type": "string",
                        "enum": ["ransomware_detection", "phishing_detection", "digital_fingerprinting", "network_anomaly", "log_parsing", "sid_classification"],
                        "description": "Type of security pipeline to run"
                    },
                    "input_source": {"type": "string", "description": "Input data source: file path, Kafka topic, or 'stdin'"},
                    "output_sink": {"type": "string", "description": "Output sink: file path, Kafka topic, or 'stdout'"},
                    "model_path": {"type": "string", "description": "Path to custom trained model (optional)"}
                },
                "required": ["pipeline_type", "input_source"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "morpheus_digital_fingerprinting",
            "description": "Run NVIDIA AI Digital Fingerprinting (ADF) to detect anomalous user behavior",
            "parameters": {
                "type": "object",
                "properties": {
                    "log_source": {
                        "type": "string",
                        "enum": ["azure_ad", "duo", "gcp_audit", "github", "okta", "slack", "ssh", "vpn"],
                        "description": "Log source type for user behavior analysis"
                    },
                    "data_path": {"type": "string", "description": "Path to log data files"},
                    "training_mode": {"type": "boolean", "description": "Run in training mode to build baseline", "default": False},
                    "anomaly_threshold": {"type": "number", "description": "Anomaly score threshold (0-1)", "default": 0.5}
                },
                "required": ["log_source", "data_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "morpheus_train_model",
            "description": "Train a custom Morpheus security model on your data",
            "parameters": {
                "type": "object",
                "properties": {
                    "model_type": {
                        "type": "string",
                        "enum": ["phishing-bert", "ransomware-rf", "network-anomaly-ae", "log-parsing-bert"],
                        "description": "Model architecture to train"
                    },
                    "training_data": {"type": "string", "description": "Path to training dataset"},
                    "epochs": {"type": "integer", "description": "Training epochs", "default": 5},
                    "output_model": {"type": "string", "description": "Output model name/path"}
                },
                "required": ["model_type", "training_data", "output_model"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "morpheus_analyze_logs",
            "description": "Analyze security log files for threats using Morpheus",
            "parameters": {
                "type": "object",
                "properties": {
                    "log_file": {"type": "string", "description": "Path to log file to analyze"},
                    "log_type": {
                        "type": "string",
                        "enum": ["syslog", "apache", "nginx", "windows_event", "aws_cloudtrail", "network_pcap"],
                        "description": "Type of log file"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["json", "csv", "summary"],
                        "description": "Output format for results",
                        "default": "summary"
                    }
                },
                "required": ["log_file", "log_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "morpheus_kafka_stream",
            "description": "Set up real-time Morpheus pipeline with Kafka streaming",
            "parameters": {
                "type": "object",
                "properties": {
                    "kafka_broker": {"type": "string", "description": "Kafka broker address, e.g. 'localhost:9092'"},
                    "input_topic": {"type": "string", "description": "Kafka input topic name"},
                    "output_topic": {"type": "string", "description": "Kafka output topic name"},
                    "pipeline_type": {"type": "string", "description": "Pipeline type to run on stream"}
                },
                "required": ["kafka_broker", "input_topic", "output_topic", "pipeline_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "morpheus_explain",
            "description": "Explain NVIDIA Morpheus capabilities and pipelines",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": ["overview", "pipelines", "digital_fingerprinting", "models", "kafka_integration"],
                        "description": "Topic to explain"
                    }
                },
                "required": ["topic"]
            }
        }
    }
]


def morpheus_setup(install_method: str, version: str = "latest") -> str:
    if install_method == "docker":
        return (
            f"🐳 **Morpheus Docker Setup:**\n```bash\n"
            f"docker pull nvcr.io/nvidia/morpheus/morpheus:{version}-runtime\n\n"
            f"docker run --rm -it --gpus all \\\n"
            f"  --net=host \\\n"
            f"  -v /path/to/data:/data \\\n"
            f"  nvcr.io/nvidia/morpheus/morpheus:{version}-runtime\n```"
        )
    elif install_method == "conda":
        return (
            f"🐍 **Morpheus Conda Setup:**\n```bash\n"
            f"conda create -n morpheus python=3.10\nconda activate morpheus\n\n"
            f"conda install -c rapidsai -c nvidia -c conda-forge morpheus\n\n"
            f"# Verify install\nmorpheus --version\n```"
        )
    else:
        return (
            f"🔧 **Morpheus Source Build:**\n```bash\n"
            f"git clone https://github.com/nv-morpheus/Morpheus.git\ncd Morpheus\n\n"
            f"git submodule update --init --recursive\n"
            f"./scripts/compile.sh\n```\n"
            f"Docs: https://docs.nvidia.com/morpheus-ai-framework/"
        )


def morpheus_run_pipeline(pipeline_type: str, input_source: str, output_sink: str = "stdout", model_path: str = None) -> str:
    cmds = {
        "ransomware_detection": f"python examples/ransomware_detection/run.py --input_glob '{input_source}/**/*.csv'",
        "phishing_detection": f"morpheus run pipeline-nlp --model_name phishing-bert-v1 from-file --filename {input_source}",
        "digital_fingerprinting": f"python examples/digital_fingerprinting/run.py --input_file {input_source}",
        "network_anomaly": f"morpheus run pipeline-ae from-kafka --input_topic {input_source}",
        "log_parsing": f"morpheus run pipeline-nlp from-file --filename {input_source} log-parse-nlp",
        "sid_classification": f"morpheus run pipeline-nlp from-file --filename {input_source} sid-filter"
    }
    cmd = cmds.get(pipeline_type, f"morpheus run {pipeline_type} from-file --filename {input_source}")
    if output_sink != "stdout":
        cmd += f" to-file --filename {output_sink}"
    if model_path:
        cmd += f" --model_path {model_path}"
    return (
        f"🛡️ **Morpheus Pipeline: {pipeline_type}**\n"
        f"Input: `{input_source}` → Output: `{output_sink}`\n\n"
        f"```bash\n{cmd}\n```\n\n"
        f"Monitor: `morpheus run --help` for all pipeline options."
    )


def morpheus_digital_fingerprinting(log_source: str, data_path: str, training_mode: bool = False, anomaly_threshold: float = 0.5) -> str:
    mode = "training" if training_mode else "inference"
    return (
        f"🔍 **Morpheus Digital Fingerprinting (ADF)**\n"
        f"Log source: `{log_source}` | Mode: `{mode}` | Threshold: {anomaly_threshold}\n\n"
        f"```bash\npython examples/digital_fingerprinting/run.py \\\n"
        f"  --log_source {log_source} \\\n"
        f"  --input_file {data_path} \\\n"
        f"  --{'train' if training_mode else 'infer'} \\\n"
        f"  --anomaly_threshold {anomaly_threshold} \\\n"
        f"  --output_dir ./adf_results\n```\n\n"
        f"ADF builds per-user behavioral baselines and flags deviations in:\n"
        f"• Login times/locations • Access patterns • Data volume • Command sequences"
    )


def morpheus_train_model(model_type: str, training_data: str, output_model: str, epochs: int = 5) -> str:
    return (
        f"🏋️ **Morpheus Model Training: {model_type}**\n"
        f"Data: `{training_data}` | Epochs: {epochs} | Output: `{output_model}`\n\n"
        f"```bash\npython training-tuning-examples/{model_type}/train.py \\\n"
        f"  --data_path {training_data} \\\n"
        f"  --epochs {epochs} \\\n"
        f"  --output_model {output_model}\n```\n\n"
        f"After training, deploy via Triton Inference Server:\n"
        f"```bash\ntritonserver --model-repository={output_model}\n```"
    )


def morpheus_analyze_logs(log_file: str, log_type: str, output_format: str = "summary") -> str:
    return (
        f"🔎 **Morpheus Log Analysis**\n"
        f"File: `{log_file}` | Type: `{log_type}` | Output: `{output_format}`\n\n"
        f"```bash\nmorpheus run pipeline-nlp \\\n"
        f"  from-file --filename {log_file} \\\n"
        f"  log-parse-nlp \\\n"
        f"  to-file --filename results.{output_format}\n```\n\n"
        f"Results include:\n"
        f"• Threat severity scores\n• Anomaly indicators\n• Timeline of suspicious events\n• Recommended actions"
    )


def morpheus_kafka_stream(kafka_broker: str, input_topic: str, output_topic: str, pipeline_type: str) -> str:
    return (
        f"📡 **Morpheus Real-time Kafka Pipeline**\n"
        f"Broker: `{kafka_broker}` | `{input_topic}` → `{output_topic}`\n\n"
        f"```bash\nmorpheus run pipeline-nlp \\\n"
        f"  from-kafka \\\n"
        f"    --input_topic {input_topic} \\\n"
        f"    --bootstrap_servers {kafka_broker} \\\n"
        f"  {pipeline_type} \\\n"
        f"  to-kafka \\\n"
        f"    --output_topic {output_topic} \\\n"
        f"    --bootstrap_servers {kafka_broker}\n```\n\n"
        f"Start Kafka: `docker compose -f docker/docker-compose.yml up kafka`"
    )


def morpheus_explain(topic: str) -> str:
    explanations = {
        "overview": (
            "🛡️ **NVIDIA Morpheus Overview**\n\n"
            "End-to-end AI cybersecurity framework for real-time threat detection:\n"
            "• Processes millions of events/second via GPU acceleration\n"
            "• Built on RAPIDS cuDF, cuML for GPU-accelerated data processing\n"
            "• Integrates with Kafka, Splunk, and SIEM platforms\n"
            "• Pre-built pipelines: ransomware, phishing, network anomaly, DFP\n"
            "Docs: https://docs.nvidia.com/morpheus-ai-framework/"
        ),
        "pipelines": "🔧 Pipelines: ransomware_detection, phishing_detection, digital_fingerprinting, network_anomaly, log_parsing, sid_classification",
        "digital_fingerprinting": "🔍 ADF (AI Digital Fingerprinting) builds per-entity behavioral baselines and detects insider threats, compromised accounts, and lateral movement.",
        "models": "🧠 Built-in models: phishing-bert, ransomware-rf, network-anomaly-ae, log-parsing-bert. All deployable via NVIDIA Triton Inference Server.",
        "kafka_integration": "📡 Morpheus natively integrates with Apache Kafka for real-time streaming security analytics at scale."
    }
    return explanations.get(topic, f"Unknown topic: {topic}")


TOOL_HANDLERS = {
    "morpheus_setup": morpheus_setup,
    "morpheus_run_pipeline": morpheus_run_pipeline,
    "morpheus_digital_fingerprinting": morpheus_digital_fingerprinting,
    "morpheus_train_model": morpheus_train_model,
    "morpheus_analyze_logs": morpheus_analyze_logs,
    "morpheus_kafka_stream": morpheus_kafka_stream,
    "morpheus_explain": morpheus_explain,
}
