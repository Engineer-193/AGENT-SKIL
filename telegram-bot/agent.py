import json
import logging
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME, SYSTEM_PROMPT
from tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

MAX_ITERATIONS = 10


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

    for iteration in range(MAX_ITERATIONS):
        logger.info(f"[Agent] Iterasi {iteration + 1} — chat_id={chat_id}")

        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            max_tokens=4096,
            temperature=0.7,
        )

        choice = response.choices[0]
        msg = choice.message
        messages.append(msg.model_dump(exclude_unset=False))

        if choice.finish_reason == "stop" or not msg.tool_calls:
            return msg.content or "✅ Selesai."

        if choice.finish_reason == "tool_calls" or msg.tool_calls:
            tool_results: list[dict] = []

            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                try:
                    fn_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    fn_args = {}

                logger.info(f"[Tool] {fn_name}({fn_args})")

                if status_callback:
                    await status_callback(f"🔧 `{fn_name}`: `{json.dumps(fn_args, ensure_ascii=False)[:80]}`...")

                if fn_name in TOOL_FUNCTIONS:
                    try:
                        result = TOOL_FUNCTIONS[fn_name](**fn_args)
                    except Exception as e:
                        result = f"❌ Error saat memanggil {fn_name}: {e}"
                else:
                    result = f"❌ Tool tidak dikenal: {fn_name}"

                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })

            messages.extend(tool_results)

    return "⚠️ Melebihi batas iterasi maksimum. Coba sederhanakan permintaan."


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
