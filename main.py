# ВРЕМЕННОЕ ДОБАВЛЕНИЕ МАСТЕРА
from database import get_db
from models import Master
import logging
logging.basicConfig(level=logging.INFO)

def add_master_if_not_exists():
    db = get_db()
    master = db.query(Master).filter(Master.telegram_id == 7161907994).first()
    if not master:
        new_master = Master(telegram_id=7161907994, name="Даня", is_admin=True)
        db.add(new_master)
        db.commit()
        logging.info("✅ Мастер Даня добавлен в базу!")
    else:
        logging.info("✅ Мастер уже существует")
    db.close()

add_master_if_not_exists()
# КОНЕЦ ВРЕМЕННОГО КОДА
import logging
from telegram.ext import Application
from config import BOT_TOKEN
from database import create_tables, Base, engine
from handlers import client

logging.basicConfig(level=logging.INFO)

def main():
    # Создаём таблицы
    Base.metadata.create_all(bind=engine)
    print("✅ База данных готова")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    for handler in client.get_handlers():
        app.add_handler(handler)
    
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()