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
    
    # Регистрируем все обработчики из client.py
    for handler in client.get_handlers():
        app.add_handler(handler)
    
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()