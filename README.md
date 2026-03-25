# 🛡 19 VPN — VPN для учеников гимназии ОдинДевять

<div align="center">

### Свободный интернет для Девятнадцатой.

Полноценный VPN на WireGuard: веб-панель, админка, macOS-клиент, все платформы.

**Ноль логов · Обфускация · Открытый код**

[Возможности](#возможности) · [Установка](#установка) · [Архитектура](#архитектура)

---

</div>

## Возможности

| Что | Описание |
|-----|----------|
| **WireGuard** | Самый быстрый VPN-протокол — встроен в ядро Linux, в 4x быстрее OpenVPN |
| **Обфускация трафика** | wstunnel оборачивает VPN в WebSocket — провайдер видит HTTPS, а не VPN |
| **DNS over TLS** | Unbound → Cloudflare DoT + Google DoT. Безопасный DNS. |
| **Ноль логов** | Не записываем трафик, DNS, IP, временные метки |
| **Веб-панель** | Регистрация, генерация ключей, QR-коды |
| **Админ-панель** | Управление пользователями, тарифами, статистика, доход |
| **macOS клиент** | Приложение в menu bar — подключение, kill switch, авто-connect |
| **Все платформы** | macOS, Windows, Android, iOS через WireGuard конфиги + QR |
| **Kill Switch** | Блокирует весь трафик при падении VPN (macOS) |
| **YouTube, TikTok, Telegram, Discord** | Всё работает без ограничений |
| **Instagram, Twitter/X, ChatGPT** | Полный доступ ко всем сервисам |
| **Spotify, Twitch, Netflix, Steam** | Стриминг и игры без блокировок |

## Технологии

| Компонент | Технология |
|-----------|-----------|
| VPN-сервер | WireGuard + wstunnel + Unbound DNS |
| Веб-панель | Python Flask, Jinja2, HTML5/CSS3/JS |
| macOS клиент | Python + rumps (menu bar) |
| База данных | JSON-файлы (без внешних БД) |
| Установка | `setup.sh` — одна команда |

## Установка

### 1. VPN-сервер

Купи VPS ($3-5/мес) — Hetzner, DigitalOcean, Vultr. Далее:

```bash
cd server
sudo bash setup.sh
```

Скрипт установит WireGuard, настроит DNS over TLS (Unbound), wstunnel для обфускации, firewall и создаст первый конфиг.

### 2. Веб-панель

```bash
cd web
pip install flask requests
python app.py
```

Открой `http://localhost:5000`

**Переменные окружения:**
```
VPN_API_URL=https://YOUR_VPS_IP:8443
VPN_API_KEY=your-api-token
ADMIN_USER=admin
ADMIN_PASS=19gym2025
SECRET_KEY=random-secret
```

### 3. macOS клиент

```bash
cd client
pip install rumps
python nexusvpn.py
```

### 4. Другие платформы

| Платформа | Как подключиться |
|-----------|-----------------|
| **Android** | Кабинет → Добавить устройство → Сканируй QR в WireGuard |
| **iOS** | Кабинет → Добавить устройство → Сканируй QR в WireGuard |
| **Windows** | Кабинет → Скачать .conf → Импортируй в WireGuard |
| **macOS** | Используй клиент 19 VPN или импортируй .conf |

## Архитектура

```
nexus_vpn/
├── server/                 # Серверная часть (VPS)
│   ├── setup.sh            # Установка одной командой
│   ├── manage.py           # CLI: добавить/удалить клиентов
│   ├── wg_manager.py       # Управление ключами WireGuard
│   └── api.py              # REST API для веб-панели
│
├── web/                    # Веб-панель (Flask)
│   ├── app.py              # Авторизация, кабинет, админка
│   ├── templates/          # Лендинг, Кабинет, Админка, Скачать
│   └── static/             # CSS + JS
│
├── client/                 # macOS клиент
│   ├── nexusvpn.py         # Точка входа
│   ├── vpn_engine.py       # WireGuard-движок
│   ├── tray.py             # Menu bar (rumps)
│   └── config.py           # Хранение конфигов
│
└── configs/                # Примеры конфигов
    ├── SETUP_GUIDE.md
    └── *.conf
```

## Сервер: требования

- Ubuntu 20.04+ или Debian 11+
- 512 MB RAM минимум
- Root-доступ
- VPS: $3-5/месяц

## Лицензия

MIT License — можно использовать, менять, распространять.

---

**19 VPN** — Сделано для гимназии №19 ОдинДевять, Казань.
