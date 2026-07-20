from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from database import get_db
from models import Client


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


async def clients_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    db = get_db()

    clients = (
        db.query(Client)
        .order_by(Client.id.desc())
        .limit(20)
        .all()
    )

    db.close()


    if not clients:

        await update.message.reply_text(
            "📭 Клиентов пока нет"
        )

        return


    buttons = []


    for client in clients:

        buttons.append(

            [
                InlineKeyboardButton(
                    f"👤 {client.name}",
                    callback_data=f"client_{client.id}"
                )
            ]

        )


    await update.message.reply_text(

        "👥 База клиентов KOD 168:",

        reply_markup=InlineKeyboardMarkup(buttons)

    )


async def open_client(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    client_id = int(
        query.data.split("_")[1]
    )


    db = get_db()


    client = (
        db.query(Client)
        .filter(Client.id == client_id)
        .first()
    )


    db.close()


    if not client:

        await query.message.reply_text(
            "❌ Клиент не найден"
        )

        return


    text = f"""
🔥 KOD 168 CLIENT

👤 {client.name}

🆔 {client.client_code}

📞 {client.phone}

✂️ {client.haircut}

🧴 {client.cosmetics}

📝 {client.notes}

⭐ {client.status}

🔄 Визитов: {client.visits}

💰 {client.total_money} ₽
"""


    if client.photo_id:

        await query.message.reply_photo(
            photo=client.photo_id,
            caption=text
        )

    else:

        await query.message.reply_text(
            text
        )



async def buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text


    if text == "➕ Новый клиент":

        await update.message.reply_text(
            "Введите /add для создания клиента"
        )


    elif text == "🔍 Найти клиента":

        await update.message.reply_text(
            "Введите /find и данные клиента"
        )


    elif text == "👥 Клиенты":

        await clients_list(
            update,
            context
        )


    elif text == "📊 Статистика":

        await update.message.reply_text(
            "📊 Скоро будет"
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
            filters.TEXT & ~filters.COMMAND,
            buttons
        ),

        CallbackQueryHandler(
            open_client,
            pattern="^client_"
        )

    ]