# Poizon Ordering Telegram Bot (Aiogram 3.x + Pydantic v2)

This is a minimal example bot implementing the features you requested:
- Menu driven navigation with buttons (main menu, order, cart, calculation, help, my orders)
- Cart stored per-user (in DB) and editable
- Order creation with saved contacts (first order requests phone and name)
- Calculation tool for approximate cost
- Admin "panel" accessible via admin commands (admin chat id configured in .env)
- Order status change notifications sent to user

**Important**: This is an example starter project. You need to configure a Telegram bot token and ADMIN_ID in `.env` before running.

## Setup
1. Create `.env` in the project root with:

```env
BOT_TOKEN=123456:ABC-DEF...
ADMIN_ID=123456789
DATABASE_URL=sqlite+aiosqlite:///./poizon.db
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Run the bot:
```bash
python -m app.main
```

## Notes
- This uses SQLite for simplicity. For production, use PostgreSQL and secure the admin commands.
- Aiogram 3.x API is in beta; adjust imports/versions if your environment differs.
