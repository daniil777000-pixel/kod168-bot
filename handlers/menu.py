from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
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
        "🔥 KOD 168 CRM\nВыберите действие:",
        reply_markup=main_menu()
    )


async def buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text


    if text == "➕ Новый клиент":

        await update.message.reply_text(
            "Для добавления клиента используйте:\n/add"
        )


    elif text == "🔍 Найти клиента":

        await update.message.reply_text(
            "Введите:\n/find номер телефона"
        )


    elif text == "👥 Клиенты":

        await update.message.reply_text(
            "Открываю базу клиентов..."
        )


    elif text == "📊 Статистика":

        await update.message.reply_text(
            "📊 Статистика пока в разработке"
        )


    elif text == "⚙️ Настройки":

        await update.message.reply_text(
            "⚙️ Настройки CRM"
        )


def get_menu_handlers():

    return [

        CommandHandler(
            "menu",
            menu
        ),

        MessageHandler(
            filters.TEXT,
            buttons
        )

    ]