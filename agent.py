import logging
import httpx
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
    max_retries=0,
    http_client=httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=15.0)),
)


async def run_agent(
    user_message: str,
    chat_id: int,
    history: list[dict],
    status_callback=None,
) -> str:
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": user_message},
    ]

    logger.info(f"[Agent] Memanggil AI — chat_id={chat_id}")

    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=4096,
            temperature=0.7,
            extra_body={"chat_template_kwargs": {"thinking": False}},
        )
        return response.choices[0].message.content or ""
    except httpx.TimeoutException:
        logger.warning("[Agent] Timeout saat memanggil AI")
        return "Maaf, AI lambat merespons. Coba lagi."
    except Exception as e:
        logger.error(f"[Agent] Error: {e}")
        return "Maaf, terjadi error. Coba lagi."


class ConversationManager:
    def __init__(self, max_history: int = 20):
        self._histories: dict[int, list[dict]] = {}
        self.max_history = max_history

    def get(self, chat_id: int) -> list[dict]:
        return self._histories.get(chat_id, [])

    def append(self, chat_id: int, role: str, content: str) -> None:
        if chat_id not in self._histories:
            self._histories[chat_id] = []
        self._histories[chat_id].append({"role": role, "content": content})
        if len(self._histories[chat_id]) > self.max_history * 2:
            self._histories[chat_id] = self._histories[chat_id][-self.max_history * 2:]

    def clear(self, chat_id: int) -> None:
        self._histories[chat_id] = []

    def size(self, chat_id: int) -> int:
        return len(self._histories.get(chat_id, []))


conversation_manager = ConversationManager()
