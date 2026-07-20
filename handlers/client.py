from telegram import Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from sqlalchemy import or_
import random

from database import get_db
from models import Client


NAME, PHONE, PHOTO, HAIRCUT, COSMETICS, NOTES = range(6)


async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👤 Введите имя клиента:"
    )

    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "📞 Введите номер телефона:"
    )

    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["phone"] = update.message.text

    await update.message.reply_text(
        "📸 Отправьте фото клиента:"
    )

    return PHOTO


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.photo:
        await update.message.reply_text(
            "❗ Отправьте именно фото"
        )
        return PHOTO

    context.user_data["photo_id"] = update.message.photo[-1].file_id

    await update.message.reply_text(
        "✂️ Какая любимая стрижка?"
    )

    return HAIRCUT


async def get_haircut(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["haircut"] = update.message.text

    await update.message.reply_text(
        "🧴 Какая косметика используется?"
    )

    return COSMETICS


async def get_cosmetics(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["cosmetics"] = update.message.text

    await update.message.reply_text(
        "📝 Заметка мастера:"
    )

    return NOTES


async def get_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["notes"] = update.message.text

    db = get_db()

    code = f"KOD168-{random.randint(100000,999999)}"


    client = Client(
        name=context.user_data["name"],
        phone=context.user_data["phone"],
        photo_id=context.user_data.get("photo_id"),
        client_code=code,
        haircut=context.user_data["haircut"],
        cosmetics=context.user_data["cosmetics"],
        notes=context.user_data["notes"],
        visits=1
    )


    db.add(client)
    db.commit()
    db.refresh(client)


    text = f"""
🔥 НОВЫЙ КЛИЕНТ KOD 168

👤 {client.name}

🆔 {client.client_code}

📞 {client.phone}

✂️ {client.haircut}

🧴 {client.cosmetics}

📝 {client.notes}

📊 Визитов: {client.visits}
"""


    if client.photo_id:

        await update.message.reply_photo(
            photo=client.photo_id,
            caption=text
        )

    else:

        await update.message.reply_text(
            text
        )


    db.close()

    return ConversationHandler.END



async def find_client(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:

        await update.message.reply_text(
            "🔍 Использование:\n/find номер телефона или KOD ID"
        )

        return


    search = context.args[0]

    db = get_db()


    client = db.query(Client).filter(
        or_(
            Client.phone == search,
            Client.client_code == search
        )
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

📊 Визитов:
{client.visits}

💰 Потрачено:
{client.total_money}₽
"""


    if client.photo_id:

        await update.message.reply_photo(
            photo=client.photo_id,
            caption=text
        )

    else:

        await update.message.reply_text(
            text
        )


    db.close()



async def clients(update: Update, context: ContextTypes.DEFAULT_TYPE):

    db = get_db()

    users = db.query(Client).all()


    if not users:

        await update.message.reply_text(
            "👥 Клиентов пока нет"
        )

        db.close()
        return


    text = "👥 БАЗА KOD 168\n\n"


    for user in users:

        text += (
            f"👤 {user.name}\n"
            f"🆔 {user.client_code}\n"
            f"📞 {user.phone}\n\n"
        )


    db.close()


    await update.message.reply_text(
        text
    )



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

                PHOTO:[
                    MessageHandler(
                        filters.PHOTO,
                        get_photo
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
            "clients",
            clients
        ),


        CommandHandler(
            "find",
            find_client
        )

    ]