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