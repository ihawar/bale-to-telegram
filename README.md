# Bale to Telegram Channel Bridge 🚀

A production-ready dual-bot bridge that forwards Bale channel posts into connected Telegram channels. Designed as a clean and maintainable Python project, it uses `aiogram` for both Bale and Telegram APIs, `tortoise-orm` for database management, and `APScheduler` for periodic backup tasks.

## Key Features ✨

- Dual-bot architecture:
  - Bale bot receives updates from Bale channels
  - Telegram bot publishes connected channel content on Telegram
- User-driven connection flow for linking Bale channels to Telegram channels
- Admin panel for managing bot settings and viewing database information
- Scheduled database backups with `APScheduler`
- Structured logging and issue reporting support
- Modular directory layout for handlers, middlewares, states, and tasks

## Installation 🔧

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration ⚙️

1. Copy the example configuration:

```bash
cp config.example.ini config.ini
```

2. Fill in the required values in `config.ini`:

- `[BALE]` section for the Bale bot token and owner IDs
- `[TELEGRAM]` section for the Telegram bot token and owner IDs
- `[PROXY]` section for optional Bale and Telegram proxies
- `[DB]` section for the SQLite database path

## Running the Bot ▶️

Start the application with:

```bash
python bot.py
```

The application will:

- initialize Bale and Telegram bot sessions
- register handlers and middlewares
- start polling both bots concurrently
- start the scheduled backup task

## Deploying on Linux with systemd 🛡️

If you want the bot to restart automatically after a reboot, use `systemd`.

1. Create a service file, for example `/etc/systemd/system/bale-to-telegram.service`:

```ini
[Unit]
Description=Bale to Telegram Channel Bridge
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/project/src
Environment="PATH=/path/to/project/src/venv/bin"
ExecStart=/path/to/project/src/venv/bin/python /path/to/project/src/bot.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

2. Reload `systemd` and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bale-to-telegram.service
sudo systemctl start bale-to-telegram.service
```

3. Check the service status:

```bash
sudo systemctl status bale-to-telegram.service
```

## Project Structure 📁

- `bot.py` — main entrypoint and runtime orchestration
- `config.py` — configuration loader
- `db/` — Tortoise ORM models and database initialization
- `handlers/` — Bale and Telegram command/event handlers
- `middlewares/` — middleware layers for user, bot, admin, and album processing
- `states/` — FSM states for connection flows and command handling
- `tasks/` — scheduled tasks such as database backups
- `utils/` — shared utility code

## Dependencies 📦

- `aiogram` — async Telegram/Bale bot framework
- `tortoise-orm` — async ORM for SQLite
- `APScheduler` — task scheduling for backups

## Notes 📝

- Use `config.example.ini` as the template for configuration.
- The bot is designed to run from the project root using `python bot.py`.
