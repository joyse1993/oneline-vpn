# 19 VPN Telegram Bot

Бот для поддержки и информации о 19 VPN.

## Создание бота

1. Открой [@BotFather](https://t.me/BotFather) в Telegram
2. Отправь `/newbot`
3. Имя: `19 VPN Bot`
4. Username: `vpn19gym_bot` (или любой свободный)
5. Скопируй токен

## Запуск

```bash
cd bot
pip install -r requirements.txt
BOT_TOKEN=твой_токен python3 bot.py
```

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Главное меню с кнопками |
| `/connect` | Как подключиться |
| `/services` | Список сервисов (YouTube, TikTok...) |
| `/download` | Ссылки на клиенты |
| `/status` | Статус VPN-сервера |
| `/faq` | Частые вопросы |
| `/help` | Все команды + контакты |

## Настройка команд в BotFather

Отправь `/setcommands` в @BotFather, затем:

```
start - Главное меню
connect - Как подключиться
services - Что работает (YouTube, TikTok...)
download - Скачать клиент
status - Статус сервера
faq - Частые вопросы
help - Помощь
```
