from telegram import Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from database import get_db
from models import Client

import random


NAME, PHONE, HAIRCUT, COSMETICS, NOTES = range(5)


def normalize_phone(phone):

    return (
        phone
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )


def generate_code():

    return f"KOD168-{random.randint(100000,999999)}"


async def add_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "👤 Введите имя клиента:"
    )

    return NAME



async def get_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "📞 Введите номер телефона:"
    )

    return PHONE



async def get_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["phone"] = normalize_phone(
        update.message.text
    )

    await update.message.reply_text(
        "✂️ Любимая стрижка:"
    )

    return HAIRCUT



async def get_haircut(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["haircut"] = update.message.text

    await update.message.reply_text(
        "🧴 Какая косметика?"
    )

    return COSMETICS



async def get_cosmetics(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["cosmetics"] = update.message.text

    await update.message.reply_text(
        "📝 Заметки мастера:"
    )

    return NOTES



async def get_notes(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["notes"] = update.message.text

    db = get_db()


    client = Client(

        name=context.user_data["name"],

        phone=context.user_data["phone"],

        haircut=context.user_data["haircut"],

        cosmetics=context.user_data["cosmetics"],

        notes=context.user_data["notes"],

        client_code=generate_code()

    )


    db.add(client)

    db.commit()

    db.refresh(client)


    text = f"""
🔥 Клиент KOD 168 создан

👤 {client.name}

🆔 {client.client_code}

📞 {client.phone}

✂️ {client.haircut}

🧴 {client.cosmetics}

📝 {client.notes}
"""


    await update.message.reply_text(
        text
    )


    db.close()


    return ConversationHandler.END



async def find_client(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.message.text.replace(
        "/find",
        ""
    ).strip()


    db = get_db()


    q = normalize_phone(query)


    client = db.query(Client).filter(
        (Client.phone == q) |
        (Client.name.ilike(f"%{query}%")) |
        (Client.client_code == query)
    ).first()


    if not client:

        await update.message.reply_text(
            "❌ Клиент не найден"
        )

        db.close()

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

🔄 Визитов:
{client.visits}

💰 Потрачено:
{client.total_money} ₽
"""


    await update.message.reply_text(
        text
    )


    db.close()



def get_handlers():

    return [

        ConversationHandler(

            entry_points=[

                CommandHandler(
                    "add",
                    add_start
                )

            ],

            states={

                NAME:[
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        get_name
                    )
                ],

                PHONE:[
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        get_phone
                    )
                ],

                HAIRCUT:[
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        get_haircut
                    )
                ],

                COSMETICS:[
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        get_cosmetics
                    )
                ],

                NOTES:[
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        get_notes
                    )
                ]

            },

            fallbacks=[]

        ),


        CommandHandler(
            "find",
            find_client
        )

    ]