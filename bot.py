import os
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ===== НАСТРОЙКИ =====
PUBLIC_BOT_TOKEN = os.getenv("8592438297:AAFrnyikG9JFXqNfp46K2W1EeIqZeEnv0BE")
PRIVATE_BOT_TOKEN = os.getenv("8102004931:AAFoCqyihvkC1JOdUQdWheBYwax8HZapXTk")

OWNER_ID = int(os.getenv("6576927659"))
CHANNEL_ID = int(os.getenv("-1003664705860"))
CHANNEL_LINK = os.getenv("https://t.me/DeepsyBio")

PORT = int(os.getenv("PORT", 8080))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
# ====================

notify_bot = Bot(token=PRIVATE_BOT_TOKEN)
user_message_count = {}


# 🔍 проверка подписки
async def is_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot = context.bot

    if not await is_subscribed(bot, user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Подписаться", url=CHANNEL_LINK)]
        ])

        await update.message.reply_text(
            "❗ Для использования бота нужно подписаться на канал.\n\n"
            "После подписки напиши /start ещё раз.",
            reply_markup=keyboard
        )
        return

    await update.message.reply_text(
        "👋 Привет!\n"
        "Напиши сообщение — оно будет передано Deepsy."
    )


# сообщения
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    bot = context.bot

    if not await is_subscribed(bot, user.id):
        await update.message.reply_text(
            f"❗ Сначала подпишись:\n{CHANNEL_LINK}"
        )
        return

    user_message_count[user.id] = user_message_count.get(user.id, 0) + 1

    username = f"@{user.username}" if user.username else "нет username"
    text = update.message.text

    msg = (
        "📩 Новое сообщение\n\n"
        f"👤 Пользователь: {username}\n"
        f"🆔 ID: {user.id}\n\n"
        f"💬 Текст:\n{text}"
    )

    await notify_bot.send_message(chat_id=OWNER_ID, text=msg)

    if user_message_count[user.id] % 3 == 0:
        await update.message.reply_text(
            "✅ Сообщение отправлено!\n\n"
            "📢 Вся актуальная инфа и ответы тут 👇\n"
            f"{CHANNEL_LINK}"
        )
    else:
        await update.message.reply_text("✅ Сообщение отправлено")


def main():
    app = ApplicationBuilder().token(PUBLIC_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    print("🚀 Бот запущен через Webhook")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
    )


if __name__ == "__main__":
    main()
