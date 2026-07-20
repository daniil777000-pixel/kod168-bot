import logging
from telegram.ext import Application
from config import BOT_TOKEN
from database import create_tables
from handlers import client

logging.basicConfig(level=logging.INFO)

def main():
    # Просто создаём таблицы — и всё
    create_tables()
    logging.info("✅ База данных готова")
    
    # Запускаем бота
    app = Application.builder().token(BOT_TOKEN).build()
    
    for handler in client.get_handlers():
        app.add_handler(handler)
    
    logging.info("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()