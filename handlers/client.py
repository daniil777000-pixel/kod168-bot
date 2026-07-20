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


    text = f"""
🔥 Клиент создан

👤 {client.name}

🆔 {client.client_code}

📞 {client.phone}

✂️ {client.haircut}

🧴 {client.cosmetics}
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


    context.user_data.clear()

    return ConversationHandler.END