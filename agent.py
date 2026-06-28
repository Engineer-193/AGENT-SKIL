import json
import logging
import httpx
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME, SYSTEM_PROMPT
from tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
    http_client=httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=15.0)),
)

MAX_ITERATIONS = 10


async def _call_api(messages: list[dict], use_tools: bool) -> object:
    kwargs: dict = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.7,
    }
    if use_tools and TOOL_DEFINITIONS:
        kwargs["tools"] = TOOL_DEFINITIONS
        kwargs["tool_choice"] = "auto"
    return await client.chat.completions.create(**kwargs)


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

    use_tools = True

    for iteration in range(MAX_ITERATIONS):
        logger.info(f"[Agent] Iterasi {iteration + 1} — chat_id={chat_id}")

        try:
            response = await _call_api(messages, use_tools=use_tools)
        except httpx.TimeoutException:
            logger.warning("[Agent] API timeout, retry tanpa tools")
            if use_tools:
                use_tools = False
                try:
                    response = await _call_api(messages, use_tools=False)
                except httpx.TimeoutException:
                    return "Maaf, AI tidak merespons saat ini. Coba lagi nanti."
            else:
                return "Maaf, AI tidak merespons saat ini. Coba lagi nanti."
        except Exception as e:
            logger.error(f"[Agent] API error: {e}")
            if use_tools:
                logger.info("[Agent] Retry tanpa tools setelah error")
                use_tools = False
                try:
                    response = await _call_api(messages, use_tools=False)
                except Exception as e2:
                    logger.error(f"[Agent] API error (no tools): {e2}")
                    return "Terjadi error saat menghubungi AI."
            else:
                return "Terjadi error saat menghubungi AI."

        choice = response.choices[0]
        msg = choice.message
        messages.append(msg.model_dump(exclude_unset=False))

        if choice.finish_reason == "stop" or not msg.tool_calls:
            return msg.content or ""

        if choice.finish_reason == "tool_calls" or msg.tool_calls:
            tool_results: list[dict] = []

            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                try:
                    fn_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    fn_args = {}

                logger.info(f"[Tool] {fn_name}({fn_args})")

                if fn_name in TOOL_FUNCTIONS:
                    try:
                        result = TOOL_FUNCTIONS[fn_name](**fn_args)
                    except Exception as e:
                        result = f"Error: {e}"
                else:
                    result = f"Tool tidak dikenal: {fn_name}"

                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })

            messages.extend(tool_results)

    return "Coba sederhanakan permintaan."


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
