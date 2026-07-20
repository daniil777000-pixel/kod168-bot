import logging
import threading
import os
from telegram.ext import Application
from config import BOT_TOKEN
from app import app
from database import create_tables
from handlers import client, menu
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def run_flask():
    """Запуск Flask сервера для Render"""
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def main():
    """Запуск бота"""
    # Создаём таблицы при первом запуске
    create_tables()
    logger.info("✅ База данных инициализирована")
    
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info(f"✅ Flask сервер запущен на порту {os.environ.get('PORT', 10000)}")
    
    # Настраиваем бота
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем все обработчики
    all_handlers = []
    all_handlers.extend(client.get_handlers())
    all_handlers.extend(menu.get_menu_handlers())  # Исправлено!
    
    for handler in all_handlers:
        application.add_handler(handler)
    
    logger.info("✅ Все обработчики загружены")
    logger.info("🤖 Бот запущен и готов к работе!")
    
    # Запускаем бота
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()