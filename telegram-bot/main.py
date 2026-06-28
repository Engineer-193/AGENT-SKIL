import logging
import json
from telegram import Update, Chat
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode, ChatAction

from config import (
    TELEGRAM_BOT_TOKEN,
    ALLOWED_USER_IDS,
    ADMIN_USER_IDS,
)
from agent import run_agent, conversation_manager

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def is_allowed(user_id: int) -> bool:
    if not ALLOWED_USER_IDS:
        return True
    return user_id in ALLOWED_USER_IDS or user_id in ADMIN_USER_IDS


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_USER_IDS


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Halo *{user.first_name}*!\n\n"
        "Saya adalah *Telegram AI Agent* 🤖\n\n"
        "Saya bisa:\n"
        "• 📄 `read_file` — membaca isi file\n"
        "• 🔍 `search_files` — mencari kode/teks dalam file\n"
        "• 🖥️ `terminal` — menjalankan perintah shell\n"
        "• 🐍 `execute_code` — mengeksekusi kode Python\n"
        "• 👥 `/tagall` — mention semua member grup\n\n"
        "Perintah:\n"
        "/clear — hapus riwayat percakapan\n"
        "/history — lihat jumlah riwayat\n"
        "/tagall — tag semua member (admin only)\n"
        "/start — tampilkan pesan ini",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        await update.message.reply_text("🚫 Kamu tidak punya akses.")
        return
    conversation_manager.clear(update.effective_chat.id)
    await update.message.reply_text("🗑️ Riwayat percakapan dihapus.")


async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        await update.message.reply_text("🚫 Kamu tidak punya akses.")
        return
    count = conversation_manager.size(update.effective_chat.id)
    await update.message.reply_text(f"📜 Riwayat chat: *{count}* pesan.", parse_mode=ParseMode.MARKDOWN)


async def cmd_tagall(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat = update.effective_chat

    if chat.type == Chat.PRIVATE:
        await update.message.reply_text("⚠️ Perintah ini hanya bisa digunakan di grup.")
        return

    if not is_admin(user_id):
        await update.message.reply_text("🚫 Hanya admin yang bisa menggunakan /tagall.")
        return

    custom_message = " ".join(context.args) if context.args else "📢 Perhatian semua!"

    await update.message.reply_text("⏳ Mengambil daftar member...")

    try:
        members: list[str] = []
        async for member in context.bot.get_chat_members(chat.id):
            if not member.user.is_bot:
                if member.user.username:
                    members.append(f"@{member.user.username}")
                else:
                    members.append(
                        f"[{member.user.first_name}](tg://user?id={member.user.id})"
                    )

        if not members:
            await update.message.reply_text("⚠️ Tidak ada member yang ditemukan.")
            return

        chunk_size = 30
        chunks = [members[i : i + chunk_size] for i in range(0, len(members), chunk_size)]

        await update.message.reply_text(
            f"📢 *{custom_message}*\n\n👥 Total: {len(members)} member",
            parse_mode=ParseMode.MARKDOWN,
        )

        for i, chunk in enumerate(chunks):
            await update.message.reply_text(
                " ".join(chunk),
                parse_mode=ParseMode.MARKDOWN,
            )

    except Exception as e:
        logger.error(f"Error tagall: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    user_text = update.message.text.strip()

    if not is_allowed(user_id):
        await update.message.reply_text("🚫 Kamu tidak punya akses ke bot ini.")
        return

    if not user_text:
        return

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    status_msg = await update.message.reply_text("⏳ Sedang berpikir...")

    async def status_callback(text: str) -> None:
        try:
            await status_msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            pass

    history = conversation_manager.get(chat_id)

    try:
        result = await run_agent(
            user_message=user_text,
            chat_id=chat_id,
            history=history,
            status_callback=status_callback,
        )

        conversation_manager.append(chat_id, "user", user_text)
        conversation_manager.append(chat_id, "assistant", result)

        await status_msg.delete()

        chunks = _split_message(result)
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Error handle_message: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Terjadi error: {e}")


def _split_message(text: str, max_len: int = 4000) -> list[str]:
    if len(text) <= max_len:
        return [text]
    chunks: list[str] = []
    while text:
        chunks.append(text[:max_len])
        text = text[max_len:]
    return chunks


def main() -> None:
    logger.info("🤖 Bot Agent Telegram sedang dijalankan...")

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("history", cmd_history))
    app.add_handler(CommandHandler("tagall", cmd_tagall))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    logger.info("✅ Bot siap! Menunggu pesan...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
