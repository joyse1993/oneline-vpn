"""
19 VPN Telegram Bot — для учеников гимназии ОдинДевять

Функции:
- /start — приветствие + главное меню
- /connect — как подключиться (инструкция)
- /services — список сервисов (YouTube, TikTok и т.д.)
- /download — ссылки на клиенты
- /status — статус VPN-сервера
- /help — помощь и контакты
- /faq — частые вопросы
- Inline-кнопки для навигации
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHANNEL = "@vpngym19"
MANAGER = "@ForwardElite"
SITE_URL = os.environ.get("SITE_URL", "http://localhost:5050")


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Как подключиться", callback_data="connect"),
         InlineKeyboardButton("📱 Скачать клиент", callback_data="download")],
        [InlineKeyboardButton("🎬 Что работает", callback_data="services"),
         InlineKeyboardButton("❓ FAQ", callback_data="faq")],
        [InlineKeyboardButton("📊 Статус сервера", callback_data="status"),
         InlineKeyboardButton("💬 Менеджер", url=f"https://t.me/{MANAGER.replace('@', '')}")],
        [InlineKeyboardButton("📢 Канал", url=f"https://t.me/{CHANNEL.replace('@', '')}"),
         InlineKeyboardButton("🌐 Сайт", url=SITE_URL)],
    ])


def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Главное меню", callback_data="menu")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🛡 *19 VPN — Гимназия ОдинДевять*\n\n"
        "Свободный интернет для учеников 19-й\\.\n"
        "YouTube, TikTok, Telegram, Discord, Instagram — без блокировок\\.\n\n"
        "🔒 WireGuard \\| Ноль логов \\| Обфускация\n"
        "📱 macOS, Windows, Android, iOS\n"
        "💰 Бесплатно для учеников\n\n"
        "Выбери что тебе нужно:"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="MarkdownV2")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode="MarkdownV2")


async def connect_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "🚀 *Подключение за 60 секунд*\n\n"
        "*Шаг 1:* Зайди на сайт и зарегистрируйся\n"
        f"🔗 {SITE_URL}\n\n"
        "*Шаг 2:* В Кабинете нажми «Добавить устройство»\n"
        "Выбери платформу \\(macOS/Windows/Android/iOS\\)\n\n"
        "*Шаг 3:*\n"
        "📱 *Телефон:* Установи WireGuard → Сканируй QR из Кабинета\n"
        "💻 *Компьютер:* Скачай \\.conf → Импортируй в WireGuard\n\n"
        "✅ Готово\\! Весь трафик зашифрован\\."
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Открыть сайт", url=SITE_URL)],
        [InlineKeyboardButton("📱 Скачать клиент", callback_data="download")],
        [InlineKeyboardButton("⬅️ Главное меню", callback_data="menu")]
    ])
    await query.edit_message_text(text, reply_markup=kb, parse_mode="MarkdownV2")


async def services_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "🎬 *Что работает с 19 VPN*\n\n"
        "▶️ *YouTube* — 4K без тормозов\n"
        "🎵 *TikTok* — видео \\+ прямые эфиры\n"
        "✈️ *Telegram* — чаты \\+ каналы \\+ боты\n"
        "🎮 *Discord* — голос \\+ стрим \\+ видео\n"
        "📷 *Instagram* — Reels \\+ Stories \\+ посты\n"
        "🐦 *Twitter/X* — лента \\+ Spaces\n"
        "🤖 *ChatGPT* — GPT\\-4 \\+ DALL\\-E\n"
        "🎧 *Spotify* — музыка \\+ подкасты\n"
        "🎬 *Twitch* — стримы \\+ VOD\n"
        "🎮 *Steam* — игры \\+ магазин\n"
        "📺 *Netflix* — фильмы \\+ сериалы\n"
        "🔗 *И ещё 1000\\+* — любой сайт\n\n"
        "Всё работает через WireGuard \\+ обфускацию\\.\n"
        "Провайдер не видит что ты используешь VPN\\."
    )
    await query.edit_message_text(text, reply_markup=back_button(), parse_mode="MarkdownV2")


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📱 *Скачать 19 VPN*\n\n"
        "🍎 *macOS* — свой клиент 19 VPN\n"
        "Меню\\-бар, kill switch, авто\\-подключение\n\n"
        "🪟 *Windows* — WireGuard клиент\n"
        "Скачай → Импортируй \\.conf из Кабинета\n\n"
        "🤖 *Android* — WireGuard из Google Play\n"
        "Сканируй QR из Кабинета → Готово\n\n"
        "🍏 *iOS* — WireGuard из App Store\n"
        "Сканируй QR из Кабинета → Готово\n\n"
        "💡 Конфиг генерируется в Кабинете на сайте"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Открыть Кабинет", url=f"{SITE_URL}/dashboard")],
        [InlineKeyboardButton("🪟 WireGuard Windows", url="https://www.wireguard.com/install/")],
        [InlineKeyboardButton("🤖 WireGuard Android", url="https://play.google.com/store/apps/details?id=com.wireguard.android")],
        [InlineKeyboardButton("🍏 WireGuard iOS", url="https://apps.apple.com/app/wireguard/id1441195209")],
        [InlineKeyboardButton("⬅️ Главное меню", callback_data="menu")]
    ])
    await query.edit_message_text(text, reply_markup=kb, parse_mode="MarkdownV2")


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📊 *Статус 19 VPN*\n\n"
        "🟢 Веб\\-панель: *Работает*\n"
        "🔒 Протокол: *WireGuard*\n"
        "🛡 Обфускация: *wstunnel \\(WebSocket\\)*\n"
        "🌐 DNS: *DNS over TLS \\(Cloudflare \\+ Google\\)*\n"
        "🔑 Шифрование: *ChaCha20 256\\-bit*\n\n"
        "⚡ Серверная часть запускается на VPS\\.\n"
        f"Вопросы по серверу → {MANAGER}"
    )
    await query.edit_message_text(text, reply_markup=back_button(), parse_mode="MarkdownV2")


async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "❓ *Частые вопросы*\n\n"
        "*Это бесплатно?*\n"
        "Да\\. Базовый тариф — 1 устройство, 50 Mbps\\. Бесплатно\\.\n\n"
        "*TikTok и Instagram работают?*\n"
        "Да\\. YouTube, TikTok, Instagram, Discord, Telegram, ChatGPT, Spotify, Twitch, Netflix, Steam — всё\\.\n\n"
        "*Провайдер увидит VPN?*\n"
        "Нет\\. Обфускация через WebSocket\\. Для провайдера это обычный HTTPS\\.\n\n"
        "*Какие устройства?*\n"
        "macOS, Windows, Android, iOS\\.\n\n"
        "*Это безопасно?*\n"
        "Свой сервер, открытый код, 256\\-bit шифрование, DNS через TLS\\. Ноль логов\\.\n\n"
        f"Ещё вопросы → {MANAGER}"
    )
    await query.edit_message_text(text, reply_markup=back_button(), parse_mode="MarkdownV2")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💬 *Помощь*\n\n"
        "Команды бота:\n"
        "/start — Главное меню\n"
        "/connect — Как подключиться\n"
        "/services — Что работает\n"
        "/download — Скачать клиент\n"
        "/status — Статус сервера\n"
        "/faq — Частые вопросы\n\n"
        f"Менеджер: {MANAGER}\n"
        f"Канал: {CHANNEL}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    handlers = {
        "menu": start,
        "connect": connect_handler,
        "services": services_handler,
        "download": download_handler,
        "status": status_handler,
        "faq": faq_handler,
    }

    handler = handlers.get(data)
    if handler:
        await handler(update, context)


async def cmd_connect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.callback_query = type('obj', (object,), {'answer': lambda: None, 'edit_message_text': update.message.reply_text, 'data': 'connect'})()
    text = (
        "🚀 *Подключение за 60 секунд*\n\n"
        f"1. Зарегистрируйся: {SITE_URL}\n"
        "2. Кабинет → «Добавить устройство»\n"
        "3. 📱 Телефон: WireGuard → QR\n"
        "   💻 Комп: Скачай .conf → Импортируй\n\n"
        f"Вопросы → {MANAGER}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎬 *Что работает с 19 VPN*\n\n"
        "▶️ YouTube • 🎵 TikTok • ✈️ Telegram\n"
        "🎮 Discord • 📷 Instagram • 🐦 Twitter/X\n"
        "🤖 ChatGPT • 🎧 Spotify • 🎬 Twitch\n"
        "🎮 Steam • 📺 Netflix • 🔗 +1000 сайтов"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📱 *Скачать клиенты*\n\n"
        f"🌐 Сайт: {SITE_URL}/download\n"
        "🪟 WireGuard Windows: wireguard.com/install\n"
        "🤖 Android: Google Play → WireGuard\n"
        "🍏 iOS: App Store → WireGuard\n\n"
        "Конфиг генерируется в Кабинете на сайте."
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📊 *Статус 19 VPN*\n\n"
        "🟢 Веб-панель: Работает\n"
        "🔒 WireGuard + wstunnel\n"
        "🌐 DNS over TLS\n"
        "🔑 256-bit шифрование\n\n"
        f"Вопросы → {MANAGER}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❓ *FAQ*\n\n"
        "• *Бесплатно?* Да, базовый тариф.\n"
        "• *TikTok работает?* Да, и ещё 12+ сервисов.\n"
        "• *Провайдер видит?* Нет, обфускация.\n"
        "• *Устройства?* macOS, Windows, Android, iOS.\n"
        "• *Безопасно?* Свой сервер, 0 логов.\n\n"
        f"Ещё вопросы → {MANAGER}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("=" * 50)
        print("⚠️  Установи BOT_TOKEN!")
        print()
        print("1. Открой @BotFather в Telegram")
        print("2. /newbot → Назови '19 VPN Bot'")
        print("3. Скопируй токен")
        print("4. Запусти: BOT_TOKEN=xxx python3 bot.py")
        print("=" * 50)
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("connect", cmd_connect))
    app.add_handler(CommandHandler("services", cmd_services))
    app.add_handler(CommandHandler("download", cmd_download))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("faq", cmd_faq))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("🛡 19 VPN Bot запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
