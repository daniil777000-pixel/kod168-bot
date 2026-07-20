from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    ContextTypes
)


def main_menu():

    keyboard = [
        [
            "➕ Новый клиент",
            "🔍 Найти клиента"
        ],
        [
            "👥 Клиенты",
            "📊 Статистика"
        ],
        [
            "⚙️ Настройки"
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


async def menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🔥 KOD 168 CRM\n\nВыберите действие:",
        reply_markup=main_menu()
    )


def get_menu_handlers():

    return [
        CommandHandler(
            "menu",
            menu
        )
    ]
