import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import WORK_DIR

SKILL_NAME = "NVIDIA Cosmos"
SKILL_DESC = "NVIDIA Cosmos World Foundation Models for physical AI, robotics simulation, and synthetic data generation"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "cosmos_generate_video",
            "description": "Generate a synthetic world simulation video using Cosmos WFM from text or image prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Text description of the world/scene to generate"},
                    "model": {
                        "type": "string",
                        "enum": ["Cosmos-1.0-Diffusion-7B-Video2World", "Cosmos-1.0-Diffusion-14B-Video2World", "Cosmos-1.0-Autoregressive-5B", "Cosmos-1.0-Autoregressive-13B"],
                        "description": "Cosmos model to use"
                    },
                    "duration_seconds": {"type": "integer", "description": "Video duration in seconds", "default": 5},
                    "input_image": {"type": "string", "description": "Optional path to input image for image-to-video"}
                },
                "required": ["prompt", "model"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cosmos_setup",
            "description": "Set up Cosmos environment, download model weights from NGC/HuggingFace",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {"type": "string", "description": "Cosmos model name to download"},
                    "install_dir": {"type": "string", "description": "Installation directory", "default": "~/cosmos"}
                },
                "required": ["model"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cosmos_list_models",
            "description": "List available NVIDIA Cosmos models and their capabilities",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cosmos_post_train",
            "description": "Post-train (fine-tune) a Cosmos model on custom world data",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_model": {"type": "string", "description": "Base Cosmos model to fine-tune"},
                    "dataset_path": {"type": "string", "description": "Path to training video dataset"},
                    "epochs": {"type": "integer", "description": "Number of training epochs", "default": 10},
                    "output_name": {"type": "string", "description": "Name for the fine-tuned model"}
                },
                "required": ["base_model", "dataset_path", "output_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cosmos_robotics_sim",
            "description": "Generate robotics simulation data using Cosmos for training robot policies",
            "parameters": {
                "type": "object",
                "properties": {
                    "robot_type": {"type": "string", "description": "Robot type, e.g. 'humanoid', 'arm', 'mobile_robot'"},
                    "task": {"type": "string", "description": "Task description, e.g. 'pick and place object', 'navigate corridor'"},
                    "num_samples": {"type": "integer", "description": "Number of simulation samples to generate", "default": 100},
                    "environment": {"type": "string", "description": "Environment description, e.g. 'warehouse', 'kitchen', 'outdoor'"}
                },
                "required": ["robot_type", "task"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cosmos_explain",
            "description": "Explain NVIDIA Cosmos capabilities and use cases",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": ["overview", "wfm", "video2world", "robotics", "autonomous_driving", "synthetic_data"],
                        "description": "Topic to explain"
                    }
                },
                "required": ["topic"]
            }
        }
    }
]


def cosmos_list_models() -> str:
    return (
        "🌌 **NVIDIA Cosmos Models:**\n\n"
        "**Diffusion (Video2World):**\n"
        "  • `Cosmos-1.0-Diffusion-7B-Video2World` — 7B params, fast\n"
        "  • `Cosmos-1.0-Diffusion-14B-Video2World` — 14B params, higher quality\n\n"
        "**Autoregressive:**\n"
        "  • `Cosmos-1.0-Autoregressive-5B` — 5B, streaming generation\n"
        "  • `Cosmos-1.0-Autoregressive-13B` — 13B, highest quality\n\n"
        "**Tokenizers:**\n"
        "  • `Cosmos-1.0-Tokenizer-CV8x8x8` — continuous video tokenizer\n"
        "  • `Cosmos-1.0-Tokenizer-DV8x16x16` — discrete video tokenizer\n\n"
        "HuggingFace: https://huggingface.co/nvidia/Cosmos-1.0-Diffusion-7B-Video2World\n"
        "NGC: nvcr.io/nvidia/cosmos"
    )


def cosmos_setup(model: str, install_dir: str = "~/cosmos") -> str:
    hf_map = {
        "Cosmos-1.0-Diffusion-7B-Video2World": "nvidia/Cosmos-1.0-Diffusion-7B-Video2World",
        "Cosmos-1.0-Diffusion-14B-Video2World": "nvidia/Cosmos-1.0-Diffusion-14B-Video2World",
        "Cosmos-1.0-Autoregressive-5B": "nvidia/Cosmos-1.0-Autoregressive-5B",
        "Cosmos-1.0-Autoregressive-13B": "nvidia/Cosmos-1.0-Autoregressive-13B",
    }
    hf_id = hf_map.get(model, f"nvidia/{model}")
    return (
        f"🚀 **Cosmos Setup: {model}**\n\n"
        f"```bash\n"
        f"# 1. Clone Cosmos repo\ngit clone https://github.com/NVIDIA/Cosmos.git {install_dir}\ncd {install_dir}\n\n"
        f"# 2. Install dependencies\npip install -e .[all]\n\n"
        f"# 3. Download model weights\npython scripts/download_diffusion_models.py \\\n"
        f"  --model_name {model} \\\n"
        f"  --hf_token $HF_TOKEN\n\n"
        f"# Or via HuggingFace Hub:\nhuggingface-cli download {hf_id} \\\n"
        f"  --token $HF_TOKEN \\\n"
        f"  --local-dir ./checkpoints/{model}\n"
        f"```\n\n"
        f"Requirements: NVIDIA GPU with 24GB+ VRAM (80GB recommended for 14B)"
    )


def cosmos_generate_video(prompt: str, model: str, duration_seconds: int = 5, input_image: str = None) -> str:
    img_arg = f"--input_image {input_image} \\\n  " if input_image else ""
    return (
        f"🎬 **Cosmos Video Generation**\n"
        f"Model: `{model}`\n"
        f"Prompt: `{prompt}`\n"
        f"Duration: {duration_seconds}s\n\n"
        f"```bash\npython inference/generate_video.py \\\n"
        f"  --model {model} \\\n"
        f"  --prompt \"{prompt}\" \\\n"
        f"  {img_arg}--duration {duration_seconds} \\\n"
        f"  --output ./output_video.mp4 \\\n"
        f"  --checkpoint_dir ./checkpoints/{model}\n```\n\n"
        f"Or via Python API:\n"
        f"```python\nfrom cosmos.inference import CosmosInference\n"
        f"model = CosmosInference.from_pretrained('{model}')\n"
        f"video = model.generate(prompt='{prompt}', duration={duration_seconds})\n"
        f"video.save('output.mp4')\n```"
    )


def cosmos_post_train(base_model: str, dataset_path: str, output_name: str, epochs: int = 10) -> str:
    return (
        f"🏋️ **Cosmos Post-Training: {output_name}**\n"
        f"Base: `{base_model}` | Dataset: `{dataset_path}` | Epochs: {epochs}\n\n"
        f"```bash\npython training/post_train.py \\\n"
        f"  --base_model {base_model} \\\n"
        f"  --dataset_path {dataset_path} \\\n"
        f"  --output_name {output_name} \\\n"
        f"  --epochs {epochs} \\\n"
        f"  --checkpoint_dir ./checkpoints/{base_model} \\\n"
        f"  --save_dir ./finetuned/{output_name}\n```\n\n"
        f"Multi-GPU training:\n"
        f"```bash\ntorchrun --nproc_per_node=8 training/post_train.py \\\n"
        f"  --base_model {base_model} --dataset_path {dataset_path}\n```"
    )


def cosmos_robotics_sim(robot_type: str, task: str, num_samples: int = 100, environment: str = "general") -> str:
    return (
        f"🤖 **Cosmos Robotics Simulation**\n"
        f"Robot: `{robot_type}` | Task: `{task}`\n"
        f"Environment: `{environment}` | Samples: {num_samples}\n\n"
        f"```python\nfrom cosmos.robotics import RoboticsSynthesizer\n\n"
        f"synth = RoboticsSynthesizer(\n"
        f"    robot_type='{robot_type}',\n"
        f"    world_model='Cosmos-1.0-Diffusion-7B-Video2World'\n"
        f")\n\n"
        f"dataset = synth.generate(\n"
        f"    task='{task}',\n"
        f"    environment='{environment}',\n"
        f"    num_samples={num_samples},\n"
        f"    output_dir='./robot_data/{robot_type}'\n"
        f")\n"
        f"print(f'Generated {{len(dataset)}} samples')\n```\n\n"
        f"Use generated data to train robot policies with Isaac Lab or Lerobot."
    )


def cosmos_explain(topic: str) -> str:
    explanations = {
        "overview": (
            "🌌 **NVIDIA Cosmos — World Foundation Models**\n\n"
            "Cosmos generates photorealistic, physically accurate video simulations of the real world.\n"
            "Key use cases:\n"
            "• **Robotics** — generate training data for robot policies\n"
            "• **Autonomous driving** — simulate rare/dangerous scenarios\n"
            "• **Synthetic data** — replace expensive real-world data collection\n"
            "• **World modeling** — understand and predict physical environments"
        ),
        "wfm": "🌐 World Foundation Models (WFM) are large generative models trained on massive video datasets to understand and simulate physical world dynamics.",
        "video2world": "🎬 Video2World: Given an input image or short video clip, Cosmos generates what happens next — physically plausible future frames.",
        "robotics": "🤖 Cosmos generates robot training environments at scale — warehouses, kitchens, factories — without real-world data collection.",
        "autonomous_driving": "🚗 Cosmos simulates rare driving scenarios (accidents, bad weather, edge cases) to train safer autonomous vehicles.",
        "synthetic_data": "📊 Replace expensive real-world data collection with Cosmos-generated synthetic datasets for computer vision and robotics training."
    }
    return explanations.get(topic, f"Unknown topic: {topic}")


TOOL_HANDLERS = {
    "cosmos_generate_video": cosmos_generate_video,
    "cosmos_setup": cosmos_setup,
    "cosmos_list_models": cosmos_list_models,
    "cosmos_post_train": cosmos_post_train,
    "cosmos_robotics_sim": cosmos_robotics_sim,
    "cosmos_explain": cosmos_explain,
}
