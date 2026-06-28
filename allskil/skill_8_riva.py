import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import WORK_DIR

SKILL_NAME = "NVIDIA Riva"
SKILL_DESC = "NVIDIA Riva Speech AI — ASR, TTS, NLP, and conversational AI with GPU-accelerated inference"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "riva_setup",
            "description": "Set up NVIDIA Riva Speech AI server",
            "parameters": {
                "type": "object",
                "properties": {
                    "models": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Models to deploy, e.g. ['asr-en', 'tts-en', 'nmt-en-de']"
                    },
                    "port": {"type": "integer", "description": "gRPC port for Riva server", "default": 50051},
                    "gpu": {"type": "string", "description": "GPU device(s) to use", "default": "all"}
                },
                "required": ["models"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "riva_asr",
            "description": "Transcribe speech audio file to text using Riva ASR",
            "parameters": {
                "type": "object",
                "properties": {
                    "audio_file": {"type": "string", "description": "Path to audio file (.wav, .mp3, .flac)"},
                    "language": {"type": "string", "description": "Language code, e.g. 'en-US', 'es-ES', 'zh-CN'", "default": "en-US"},
                    "model": {"type": "string", "description": "ASR model: 'parakeet-ctc', 'conformer', 'citrinet'", "default": "parakeet-ctc"},
                    "streaming": {"type": "boolean", "description": "Use streaming ASR mode", "default": False}
                },
                "required": ["audio_file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "riva_tts",
            "description": "Convert text to speech using Riva TTS",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to convert to speech"},
                    "voice": {"type": "string", "description": "Voice name, e.g. 'English-US-Female-1', 'English-US-Male-1'", "default": "English-US-Female-1"},
                    "output_file": {"type": "string", "description": "Output audio file path", "default": "output.wav"},
                    "sample_rate": {"type": "integer", "description": "Audio sample rate in Hz", "default": 22050}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "riva_translate",
            "description": "Translate text between languages using Riva NMT (Neural Machine Translation)",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to translate"},
                    "source_lang": {"type": "string", "description": "Source language code, e.g. 'en'"},
                    "target_lang": {"type": "string", "description": "Target language code, e.g. 'es', 'de', 'zh'"}
                },
                "required": ["text", "source_lang", "target_lang"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "riva_list_models",
            "description": "List available NVIDIA Riva models for ASR, TTS, NLP, and NMT",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "enum": ["asr", "tts", "nmt", "nlp", "all"],
                        "description": "Filter by task type"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "riva_streaming_demo",
            "description": "Set up a real-time streaming ASR demo with Riva",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_url": {"type": "string", "description": "Riva server URL", "default": "localhost:50051"},
                    "language": {"type": "string", "description": "Language code", "default": "en-US"},
                    "chunk_duration_ms": {"type": "integer", "description": "Audio chunk duration in milliseconds", "default": 100}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "riva_custom_vocab",
            "description": "Add custom vocabulary (domain-specific terms) to Riva ASR model",
            "parameters": {
                "type": "object",
                "properties": {
                    "vocab_words": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of custom words/phrases to add"
                    },
                    "boost_score": {"type": "number", "description": "Boosting score for custom words (0-20)", "default": 10.0}
                },
                "required": ["vocab_words"]
            }
        }
    }
]


def riva_setup(models: list, port: int = 50051, gpu: str = "all") -> str:
    model_list = " ".join(models)
    return (
        f"🎙️ **Riva Setup: {', '.join(models)}**\n\n"
        f"```bash\n"
        f"# 1. Download Riva Quick Start\ncurl -s https://api.ngc.nvidia.com/v2/resources/nvidia/riva/riva_quickstart/versions/latest/zip \\\n"
        f"  -o riva_quickstart.zip && unzip riva_quickstart.zip && cd riva_quickstart\n\n"
        f"# 2. Configure models in config.sh\nexport service_enabled_asr={'asr' in model_list or True}\nexport service_enabled_tts={'tts' in model_list or True}\n\n"
        f"# 3. Initialize (downloads models)\nbash riva_init.sh\n\n"
        f"# 4. Start Riva server\nbash riva_start.sh\n```\n\n"
        f"Server will be available at: `localhost:{port}` (gRPC)\n"
        f"Docker: `nvcr.io/nvidia/riva/riva-speech:latest`"
    )


def riva_asr(audio_file: str, language: str = "en-US", model: str = "parakeet-ctc", streaming: bool = False) -> str:
    mode = "streaming" if streaming else "offline"
    return (
        f"🎤 **Riva ASR: {audio_file}**\n"
        f"Language: `{language}` | Model: `{model}` | Mode: `{mode}`\n\n"
        f"```python\nimport riva.client\n\n"
        f"auth = riva.client.Auth(uri='localhost:50051')\nasr_client = riva.client.ASRService(auth)\n\n"
        f"config = riva.client.RecognitionConfig(\n"
        f"    language_code='{language}',\n"
        f"    max_alternatives=1,\n"
        f"    enable_automatic_punctuation=True,\n"
        f")\n\n"
        f"with open('{audio_file}', 'rb') as f:\n"
        f"    audio_data = f.read()\n\n"
        f"response = asr_client.offline_recognize(audio_data, config)\n"
        f"for result in response.results:\n"
        f"    print(result.alternatives[0].transcript)\n```\n\n"
        f"CLI: `python -m riva.client.cli asr --audio {audio_file} --language-code {language}`"
    )


def riva_tts(text: str, voice: str = "English-US-Female-1", output_file: str = "output.wav", sample_rate: int = 22050) -> str:
    return (
        f"🔊 **Riva TTS**\n"
        f"Voice: `{voice}` | Output: `{output_file}`\n"
        f"Text: `{text[:80]}{'...' if len(text) > 80 else ''}`\n\n"
        f"```python\nimport riva.client\nimport soundfile as sf\n\n"
        f"auth = riva.client.Auth(uri='localhost:50051')\ntts_client = riva.client.SpeechSynthesisService(auth)\n\n"
        f"resp = tts_client.synthesize(\n"
        f"    '{text}',\n"
        f"    voice_name='{voice}',\n"
        f"    language_code='en-US',\n"
        f"    sample_rate_hz={sample_rate},\n"
        f")\n\n"
        f"import numpy as np\naudio = np.frombuffer(resp.audio, dtype=np.int16)\n"
        f"sf.write('{output_file}', audio, {sample_rate})\nprint(f'Saved to {output_file}')\n```"
    )


def riva_translate(text: str, source_lang: str, target_lang: str) -> str:
    return (
        f"🌍 **Riva NMT Translation**\n"
        f"`{source_lang}` → `{target_lang}`\n"
        f"Text: `{text[:100]}`\n\n"
        f"```python\nimport riva.client\n\n"
        f"auth = riva.client.Auth(uri='localhost:50051')\nnmt_client = riva.client.NeuralMachineTranslationClient(auth)\n\n"
        f"response = nmt_client.translate(\n"
        f"    ['{text}'],\n"
        f"    model='',  # auto-select\n"
        f"    source_language='{source_lang}',\n"
        f"    target_language='{target_lang}',\n"
        f")\nprint(response.translations[0].text)\n```"
    )


def riva_list_models(task: str = "all") -> str:
    models = {
        "asr": ["parakeet-ctc-1.1b (en)", "conformer-ctc-large (multilingual)", "citrinet-1024 (en)", "quartznet-15x5 (en)"],
        "tts": ["fastpitch+hifigan (en-US)", "fastpitch+hifigan (es-ES)", "radtts (en-US)", "riva-tts-multilingual"],
        "nmt": ["en↔es", "en↔de", "en↔fr", "en↔zh", "en↔ru", "en↔ko", "en↔ja"],
        "nlp": ["bert-ner", "bert-punct", "megatron-gpt2-qa", "text-classification-bert"]
    }
    if task != "all" and task in models:
        items = "\n".join(f"  • {m}" for m in models[task])
        return f"📋 Riva {task.upper()} Models:\n{items}"
    result = []
    for t, items in models.items():
        result.append(f"**{t.upper()}:**")
        for m in items:
            result.append(f"  • {m}")
    return "📋 **NVIDIA Riva Models:**\n" + "\n".join(result)


def riva_streaming_demo(server_url: str = "localhost:50051", language: str = "en-US", chunk_duration_ms: int = 100) -> str:
    return (
        f"🌊 **Riva Streaming ASR Demo**\n"
        f"Server: `{server_url}` | Language: `{language}` | Chunk: {chunk_duration_ms}ms\n\n"
        f"```python\nimport riva.client\nimport pyaudio\n\n"
        f"auth = riva.client.Auth(uri='{server_url}')\nasr = riva.client.ASRService(auth)\n\n"
        f"config = riva.client.StreamingRecognitionConfig(\n"
        f"    config=riva.client.RecognitionConfig(\n"
        f"        language_code='{language}',\n"
        f"        enable_automatic_punctuation=True,\n"
        f"    ),\n"
        f"    interim_results=True,\n"
        f")\n\n"
        f"# Stream from microphone\npa = pyaudio.PyAudio()\nstream = pa.open(rate=16000, channels=1, format=pyaudio.paInt16, input=True)\n"
        f"print('Listening... (Ctrl+C to stop)')\n"
        f"for response in asr.streaming_recognize(config, generate_audio_chunks(stream)):\n"
        f"    for result in response.results:\n"
        f"        if result.is_final:\n"
        f"            print(result.alternatives[0].transcript)\n```\n\n"
        f"Install: `pip install nvidia-riva-client pyaudio`"
    )


def riva_custom_vocab(vocab_words: list, boost_score: float = 10.0) -> str:
    phrases = [{"value": w, "boost": boost_score} for w in vocab_words]
    import json
    return (
        f"📝 **Riva Custom Vocabulary ({len(vocab_words)} words)**\n"
        f"Boost score: {boost_score}\n"
        f"Words: {', '.join(vocab_words[:10])}{'...' if len(vocab_words) > 10 else ''}\n\n"
        f"```python\nimport riva.client\n\nconfig = riva.client.RecognitionConfig(\n"
        f"    language_code='en-US',\n"
        f"    custom_configuration={{\n"
        f"        'custom_vocabulary': {json.dumps(vocab_words)}\n"
        f"    }},\n"
        f"    speech_contexts=[riva.client.SpeechContext(\n"
        f"        phrases={json.dumps(vocab_words)},\n"
        f"        boost={boost_score}\n"
        f"    )]\n"
        f")\n```"
    )


TOOL_HANDLERS = {
    "riva_setup": riva_setup,
    "riva_asr": riva_asr,
    "riva_tts": riva_tts,
    "riva_translate": riva_translate,
    "riva_list_models": riva_list_models,
    "riva_streaming_demo": riva_streaming_demo,
    "riva_custom_vocab": riva_custom_vocab,
}
