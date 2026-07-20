import logging
from telegram.ext import Application
from config import BOT_TOKEN
from database import create_tables, get_db
from models import Client, Visit, Master
from handlers import client

# Настройка логирования
logging.basicConfig(level=logging.INFO)

def initialize_master():
    """Безопасно добавляет мастера только после создания таблиц."""
    db = get_db()
    try:
        # Проверяем, есть ли уже мастер
        master = db.query(Master).filter(Master.telegram_id == 7161907994).first()
        if not master:
            new_master = Master(telegram_id=7161907994, name="Даня", is_admin=1)
            db.add(new_master)
            db.commit()
            logging.info("✅ Мастер Даня успешно добавлен в базу!")
        else:
            logging.info("✅ Мастер уже существует в базе.")
    except Exception as e:
        logging.error(f"❌ Ошибка при добавлении мастера: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    # ШАГ 1: ВСЕГДА ПЕРВЫМ СОЗДАЕМ ТАБЛИЦЫ
    create_tables()
    logging.info("✅ База данных и все таблицы созданы/проверены.")

    # ШАГ 2: ТОЛЬКО ПОСЛЕ ЭТОГО РАБОТАЕМ С ТАБЛИЦАМИ
    initialize_master()

    # ШАГ 3: ЗАПУСКАЕМ БОТА
    logging.info("🚀 Запуск Telegram-бота...")
    app = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем все обработчики
    for handler in client.get_handlers():
        app.add_handler(handler)

    logging.info("✅ Бот успешно запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()