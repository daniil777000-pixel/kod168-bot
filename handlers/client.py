async def search_client(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.message.text.strip()

    db = get_db()

    phone = normalize_phone(query)


    client = (
        db.query(Client)
        .filter(
            (Client.name.ilike(f"%{query}%"))
            |
            (Client.phone.ilike(f"%{phone}%"))
            |
            (Client.client_code.ilike(f"%{query}%"))
        )
        .first()
    )


    if not client:

        db.close()

        await update.message.reply_text(
            "❌ Клиент не найден"
        )

        return ConversationHandler.END


    text = f"""
🔥 KOD 168 CLIENT

👤 {client.name}

🆔 {client.client_code}

📞 {client.phone}

✂️ {client.haircut}

🧴 {client.cosmetics}

📝 {client.notes}

⭐ Статус: {client.status}

🔄 Визитов: {client.visits}

💰 Потрачено: {client.total_money} ₽
"""


    db.close()


    if client.photo_id:

        await update.message.reply_photo(
            photo=client.photo_id,
            caption=text
        )

    else:

        await update.message.reply_text(
            text
        )


    return ConversationHandler.END