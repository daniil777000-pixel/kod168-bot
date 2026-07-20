from telegram import Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from database import get_db
from models import Client

import random
import logging


logger = logging.getLogger(__name__)


(
    NAME,
    PHONE,
    HAIRCUT,
    COSMETICS,
    NOTES,
    PHOTO
) = range(6)


SEARCH = 10


def normalize_phone(phone: str) -> str:
    """
    Очистка номера телефона
    """

    return (
        phone
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
    )


def generate_code() -> str:
    """
    Генерация KOD ID
    """

    return f"KOD168-{random.randint(100000,999999)}"


# =========================
# ДОБАВЛЕНИЕ КЛИЕНТА
# =========================


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
        "📞 Введите телефон:"
    )

    return PHONE



async def get_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    phone = normalize_phone(
        update.message.text
    )

    db = get_db()

    exists = (
        db.query(Client)
        .filter(Client.phone == phone)
        .first()
    )

    db.close()


    if exists:

        await update.message.reply_text(
            "⚠️ Такой номер уже есть в базе"
        )

        return ConversationHandler.END


    context.user_data["phone"] = phone


    await update.message.reply_text(
        "✂️ Какая любимая стрижка?"
    )


    return HAIRCUT



async def get_haircut(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["haircut"] = update.message.text


    await update.message.reply_text(
        "🧴 Любимая косметика:"
    )


    return COSMETICS



async def get_cosmetics(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["cosmetics"] = update.message.text


    await update.message.reply_text(
        "📝 Заметки:"
    )


    return NOTES



async def get_notes(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["notes"] = update.message.text


    await update.message.reply_text(
        "📸 Отправьте фото клиента\n"
        "или напишите: пропустить"
    )


    return PHOTO



async def get_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    photo_id = None


    if update.message.photo:

        photo_id = update.message.photo[-1].file_id


    db = get_db()


    client = Client(

        client_code=generate_code(),

        name=context.user_data["name"],

        phone=context.user_data["phone"],

        haircut=context.user_data["haircut"],

        cosmetics=context.user_data["cosmetics"],

        notes=context.user_data["notes"],

        photo_id=photo_id

    )


    db.add(client)
    db.commit()
    db.refresh(client)

    db.close()


    await update.message.reply_text(

        f"""
🔥 Клиент создан

👤 {client.name}

🆔 {client.client_code}

📞 {client.phone}

✂️ {client.haircut}

🧴 {client.cosmetics}
"""

    )


    context.user_data.clear()


    return ConversationHandler.END



async def skip_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    update.message.photo = None

    return await get_photo(
        update,
        context
    )



# =========================
# ПОИСК
# =========================


async def find_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🔍 Введите имя, телефон или KOD ID:"
    )


    return SEARCH



async def search_client(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.message.text.strip()


    db = get_db()


    client = (
        db.query(Client)
        .filter(
            (Client.name.ilike(f"%{query}%"))
            |
            (Client.phone == normalize_phone(query))
            |
            (Client.client_code == query)
        )
        .first()
    )


    db.close()


    if not client:

        await update.message.reply_text(
            "❌ Клиент не найден"
        )

        return ConversationHandler.END



    await update.message.reply_text(

        f"""
🔥 KOD 168 CLIENT

👤 {client.name}

🆔 {client.client_code}

📞 {client.phone}

✂️ {client.haircut}

⭐ {client.status}
"""

    )


    return ConversationHandler.END



# =========================
# HANDLERS
# =========================


def get_handlers():

    add_client = ConversationHandler(

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
            ],

            PHOTO:[

                MessageHandler(
                    filters.PHOTO,
                    get_photo
                ),

                MessageHandler(
                    filters.Regex("^пропустить$"),
                    get_photo
                )

            ]

        },

        fallbacks=[]

    )


    search = ConversationHandler(

        entry_points=[

            CommandHandler(
                "find",
                find_start
            )

        ],

        states={

            SEARCH:[

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    search_client
                )

            ]

        },

        fallbacks=[]

    )


    return [
        add_client,
        search
    ]