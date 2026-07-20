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


NAME, PHONE, PHOTO, HAIRCUT, COSMETICS, NOTES = range(6)


async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 Введите имя клиента:"
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "📱 Введите номер телефона клиента:"
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text

    await update.message.reply_text(
        "📸 Отправьте фото клиента:"
    )
    return PHOTO


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.photo:
        context.user_data["photo_id"] = update.message.photo[-1].file_id

        await update.message.reply_text(
            "✂️ Какая любимая стрижка?"
        )

        return HAIRCUT

    await update.message.reply_text(
        "Нужно отправить именно фото 📸"
    )

    return PHOTO


async def get_haircut(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["haircut"] = update.message.text

    await update.message.reply_text(
        "🧴 Какая косметика или предпочтения клиента?"
    )

    return COSMETICS


async def get_cosmetics(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["cosmetics"] = update.message.text

    await update.message.reply_text(
        "📝 Заметки мастера:"
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
        notes=context.user_data["notes"]
    )

    db.add(client)
    db.commit()

    await update.message.reply_text(
        f"""
🔥 Клиент KOD 168 создан

👤 {client.name}

🆔 {client.client_code}

📞 {client.phone}

✂️ {client.haircut}

🧴 {client.cosmetics}

📝 {client.notes}
"""
    )

    db.close()

    return ConversationHandler.END


async def clients(update: Update, context: ContextTypes.DEFAULT_TYPE):

    db = get_db()

    users = db.query(Client).all()

    if not users:
        await update.message.reply_text(
            "👥 Клиентов пока нет."
        )
        db.close()
        return

    text = "👥 Клиенты KOD 168:\n\n"

    for number, user in enumerate(users, start=1):
        text += (
            f"{number}. {user.name}\n"
            f"🆔 {user.client_code}\n"
            f"✂️ {user.haircut}\n\n"
        )

    db.close()

    await update.message.reply_text(text)


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

                NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        get_name
                    )
                ],

                PHONE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        get_phone
                    )
                ],

                PHOTO: [
                    MessageHandler(
                        filters.PHOTO,
                        get_photo
                    )
                ],

                HAIRCUT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        get_haircut
                    )
                ],

                COSMETICS: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        get_cosmetics
                    )
                ],

                NOTES: [
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
        )

    ]