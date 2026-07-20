import logging
from telegram.ext import Application
from config import BOT_TOKEN
from database import create_tables, get_db
from models import Client, Visit, Master
from handlers import client

logging.basicConfig(level=logging.INFO)

def main():
    # 1. СОЗДАЁМ ТАБЛИЦЫ
    create_tables()
    logging.info("✅ База данных готова")

    # 2. ДОБАВЛЯЕМ МАСТЕРА (ЕСЛИ ЕГО НЕТ)
    db = get_db()
    master = db.query(Master).filter(Master.telegram_id == 7161907994).first()
    if not master:
        new_master = Master(telegram_id=7161907994, name="Даня", is_admin=1)
        db.add(new_master)
        db.commit()
        logging.info("✅ Мастер Даня добавлен!")
    else:
        logging.info("✅ Мастер уже существует")
    db.close()

    # 3. ЗАПУСКАЕМ БОТА
    app = Application.builder().token(BOT_TOKEN).build()
    for handler in client.get_handlers():
        app.add_handler(handler)

    logging.info("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()