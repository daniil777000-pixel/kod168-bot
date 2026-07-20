from database import get_db
from models import Master

def add_master_if_not_exists():
    db = get_db()
    master = db.query(Master).filter(Master.telegram_id == 7161907994).first()
    if not master:
        new_master = Master(telegram_id=7161907994, name="Даня", is_admin=1)
        db.add(new_master)
        db.commit()
        print("✅ Мастер Даня добавлен!")
    else:
        print("✅ Мастер уже существует")
    db.close()

add_master_if_not_exists()

import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from config import BOT_TOKEN
from database import create_tables
from handlers import client

logging.basicConfig(level=logging.INFO)

def main():
    create_tables()
    print("✅ База данных готова")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    for handler in client.get_handlers():
        app.add_handler(handler)
    
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()