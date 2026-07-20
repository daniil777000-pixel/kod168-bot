import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from database import get_db
from models import Client, Visit

logging.basicConfig(level=logging.INFO)

# Состояния
NAME, PHONE, BIRTHDAY, FAVORITE_CUT, COSMETIC, DISLIKES, NOTES, PHOTO = range(8)
VISIT_SERVICE, VISIT_PRICE = range(8, 10)
SEARCH = 10

# ==================== ГЛАВНОЕ МЕНЮ ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Добавить клиента", callback_data="menu_add")],
        [InlineKeyboardButton("🔍 Найти клиента", callback_data="menu_find")],
        [InlineKeyboardButton("👥 Все клиенты", callback_data="menu_list")],
        [InlineKeyboardButton("📊 Статистика", callback_data="menu_stats")],
    ]
    await update.message.reply_text(
        "🔥 **KOD 168 CRM**\n\nВыберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "menu_add":
        await add_client_start(update, context)
    elif data == "menu_find":
        await find_client_start(update, context)
    elif data == "menu_list":
        await clients_list(update, context)
    elif data == "menu_stats":
        await stats(update, context)
    elif data.startswith("client_"):
        client_id = int(data.split("_")[1])
        await show_client_card(update, context, client_id)
    elif data == "back_to_menu":
        await start(update, context)

# ==================== ДОБАВЛЕНИЕ КЛИЕНТА ====================
async def add_client_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.message.reply_text(
            "📝 **Добавление клиента**\n\n✏️ Введите ИМЯ клиента:"
        )
        return NAME
    else:
        await update.message.reply_text(
            "📝 **Добавление клиента**\n\n✏️ Введите ИМЯ клиента:"
        )
        return NAME

async def add_client_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        f"✅ Имя: {update.message.text}\n\n📱 Введите ТЕЛЕФОН клиента:\n(например: +79991234567 или /skip)"
    )
    return PHONE

async def add_client_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/skip":
        context.user_data['phone'] = None
    else:
        context.user_data['phone'] = update.message.text
    await update.message.reply_text(
        "🎂 ДАТА РОЖДЕНИЯ (ДД.ММ):\n(или /skip)"
    )
    return BIRTHDAY

async def add_client_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/skip":
        context.user_data['birthday'] = None
    else:
        context.user_data['birthday'] = update.message.text
    await update.message.reply_text(
        "✂️ Любимая стрижка:\n(или /skip)"
    )
    return FAVORITE_CUT

async def add_client_cut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/skip":
        context.user_data['cut'] = None
    else:
        context.user_data['cut'] = update.message.text
    await update.message.reply_text(
        "🧴 Любимая косметика:\n(или /skip)"
    )
    return COSMETIC

async def add_client_cosmetic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/skip":
        context.user_data['cosmetic'] = None
    else:
        context.user_data['cosmetic'] = update.message.text
    await update.message.reply_text(
        "❌ Что НЕ ЛЮБИТ клиент:\n(или /skip)"
    )
    return DISLIKES

async def add_client_dislikes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/skip":
        context.user_data['dislikes'] = None
    else:
        context.user_data['dislikes'] = update.message.text
    await update.message.reply_text(
        "📝 Заметки мастера:\n(или /skip)"
    )
    return NOTES

async def add_client_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/skip":
        context.user_data['notes'] = None
    else:
        context.user_data['notes'] = update.message.text
    await update.message.reply_text(
        "📸 Отправьте ФОТО клиента\n(или /skip)"
    )
    return PHOTO

async def add_client_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text == "/skip":
        photo_id = None
    elif update.message.photo:
        photo_id = update.message.photo[-1].file_id
    else:
        await update.message.reply_text("❌ Отправьте фото или /skip")
        return PHOTO
    
    context.user_data['photo'] = photo_id
    
    db = get_db()
    client = Client()
    client.name = context.user_data.get('name', 'Без имени')
    client.phone = context.user_data.get('phone')
    client.birthday = context.user_data.get('birthday')
    client.favorite_cut = context.user_data.get('cut')
    client.favorite_cosmetic = context.user_data.get('cosmetic')
    client.dislikes = context.user_data.get('dislikes')
    client.notes = context.user_data.get('notes')
    client.photo = photo_id
    client.kod_id = f"KOD168-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    db.add(client)
    db.commit()
    db.refresh(client)
    db.close()
    
    await show_client_card(update, context, client.id)
    context.user_data.clear()
    return ConversationHandler.END

# ==================== КАРТОЧКА КЛИЕНТА ====================
async def show_client_card(update: Update, context: ContextTypes.DEFAULT_TYPE, client_id: int):
    db = get_db()
    client = db.query(Client).filter(Client.id == client_id).first()
    visits = db.query(Visit).filter(Visit.client_id == client_id).order_by(Visit.date.desc()).limit(5).all()
    db.close()
    
    if not client:
        await update.message.reply_text("❌ Клиент не найден")
        return
    
    text = f"👤 **{client.name}**\n"
    text += f"🆔 KOD ID: `{client.kod_id}`\n"
    text += f"📱 Телефон: {client.phone or 'Не указан'}\n"
    text += f"🎂 ДР: {client.birthday or 'Не указан'}\n\n"
    text += f"✂️ Любимая стрижка: {client.favorite_cut or 'Не указана'}\n"
    text += f"🧴 Косметика: {client.favorite_cosmetic or 'Не указана'}\n"
    text += f"❌ Не любит: {client.dislikes or 'Не указано'}\n\n"
    text += f"📊 Визитов: {client.visits_count or 0}\n"
    text += f"💰 Потрачено: {client.total_spent or 0} ₽\n"
    text += f"📅 Создан: {client.created_at.strftime('%d.%m.%Y')}\n\n"
    
    if client.notes:
        text += f"📝 Заметки: {client.notes}\n"
    
    if visits:
        text += "\n📋 **Последние визиты:**\n"
        for v in visits[:3]:
            text += f"• {v.date.strftime('%d.%m')} — {v.service} ({v.price}₽)\n"
    
    keyboard = [
        [InlineKeyboardButton("📅 Добавить визит", callback_data=f"visit_{client.id}")],
        [InlineKeyboardButton("🔄 Обновить фото", callback_data=f"photo_{client.id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")],
    ]
    
    if update.callback_query:
        if client.photo:
            await update.callback_query.message.reply_photo(
                photo=client.photo,
                caption=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await update.callback_query.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
    else:
        if client.photo:
            await update.message.reply_photo(
                photo=client.photo,
                caption=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

# ==================== ДОБАВЛЕНИЕ ВИЗИТА ====================
async def add_visit_start(update: Update, context: ContextTypes.DEFAULT_TYPE, client_id: int):
    context.user_data['visit_client_id'] = client_id
    await update.callback_query.message.reply_text(
        "📅 **Добавление визита**\n\n✂️ Введите УСЛУГУ:"
    )
    return VISIT_SERVICE

async def add_visit_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['visit_service'] = update.message.text
    await update.message.reply_text("💰 Введите ЦЕНУ (в рублях):")
    return VISIT_PRICE

async def add_visit_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text.replace("₽", "").strip())
        context.user_data['visit_price'] = price
        
        db = get_db()
        visit = Visit()
        visit.client_id = context.user_data['visit_client_id']
        visit.service = context.user_data['visit_service']
        visit.price = price
        
        client = db.query(Client).filter(Client.id == visit.client_id).first()
        client.visits_count = (client.visits_count or 0) + 1
        client.total_spent = (client.total_spent or 0) + price
        
        db.add(visit)
        db.commit()
        db.close()
        
        await update.message.reply_text(
            f"✅ **Визит добавлен!**\n\n✂️ {visit.service}\n💰 {price} ₽\n📊 Всего визитов: {client.visits_count}\n💰 Всего потрачено: {client.total_spent} ₽"
        )
        
        await show_client_card(update, context, client.id)
        context.user_data.clear()
        return ConversationHandler.END
        
    except:
        await update.message.reply_text("❌ Введите корректную цену (число):")
        return VISIT_PRICE

# ==================== ПОИСК КЛИЕНТА ====================
async def find_client_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.message.reply_text(
            "🔍 **Поиск клиента**\n\n✏️ Введите имя или телефон:"
        )
        return SEARCH
    else:
        await update.message.reply_text(
            "🔍 **Поиск клиента**\n\n✏️ Введите имя или телефон:"
        )
        return SEARCH

async def find_client_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    db = get_db()
    clients = db.query(Client).filter(
        Client.name.ilike(f"%{query}%") | Client.phone.ilike(f"%{query}%")
    ).limit(10).all()
    db.close()
    
    if not clients:
        await update.message.reply_text(f"❌ Ничего не найдено: {query}")
        return ConversationHandler.END
    
    keyboard = []
    for c in clients:
        keyboard.append([InlineKeyboardButton(f"{c.name} 📱{c.phone or ''}", callback_data=f"client_{c.id}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")])
    
    await update.message.reply_text(
        f"🔍 **Найдено {len(clients)} клиентов:**",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data.clear()
    return ConversationHandler.END

# ==================== ВСЕ КЛИЕНТЫ ====================
async def clients_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    clients = db.query(Client).order_by(Client.created_at.desc()).limit(20).all()
    db.close()
    
    if not clients:
        text = "📭 **Нет клиентов**\n\nДобавьте первого через /add"
        keyboard = [[InlineKeyboardButton("➕ Добавить клиента", callback_data="menu_add")]]
        if update.callback_query:
            await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return
    
    keyboard = []
    for c in clients[:10]:
        keyboard.append([InlineKeyboardButton(f"{c.name} 📱{c.phone or ''}", callback_data=f"client_{c.id}")])
    keyboard.append([InlineKeyboardButton("➕ Добавить клиента", callback_data="menu_add")])
    
    text = f"👥 **Последние клиенты ({len(clients)})**\n\n"
    for i, c in enumerate(clients[:10], 1):
        text += f"{i}. {c.name} | 📱{c.phone or 'нет телефона'}\n"
    
    if update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ==================== СТАТИСТИКА ====================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    total_clients = db.query(Client).count()
    total_visits = db.query(Visit).count()
    total_revenue = db.query(db.func.sum(Visit.price)).scalar() or 0
    db.close()
    
    text = f"📊 **СТАТИСТИКА KOD 168**\n\n"
    text += f"👥 Всего клиентов: {total_clients}\n"
    text += f"📅 Всего визитов: {total_visits}\n"
    text += f"💰 Общая выручка: {total_revenue:.0f} ₽\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
    
    if update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ==================== ОТМЕНА ====================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено")
    context.user_data.clear()
    return ConversationHandler.END

# ==================== РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ ====================
def get_handlers():
    # ConversationHandler для добавления клиента
    add_conv = ConversationHandler(
        entry_points=[
            CommandHandler("add", add_client_start),
            CallbackQueryHandler(add_client_start, pattern="^menu_add$")
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_phone)],
            BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_birthday)],
            FAVORITE_CUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_cut)],
            COSMETIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_cosmetic)],
            DISLIKES: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_dislikes)],
            NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_notes)],
            PHOTO: [
                MessageHandler(filters.PHOTO, add_client_photo),
                CommandHandler("skip", add_client_photo),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="add_client"
    )
    
    # ConversationHandler для поиска
    find_conv = ConversationHandler(
        entry_points=[
            CommandHandler("find", find_client_start),
            CallbackQueryHandler(find_client_start, pattern="^menu_find$")
        ],
        states={
            SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, find_client_query)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="find_client"
    )
    
    # ConversationHandler для визита
    visit_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_visit_start, pattern="^visit_")],
        states={
            VISIT_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_visit_service)],
            VISIT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_visit_price)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="add_visit"
    )
    
    return [
        CommandHandler("start", start),
        CommandHandler("menu", start),
        add_conv,
        find_conv,
        visit_conv,
        CallbackQueryHandler(menu_callback, pattern="^menu_"),
        CallbackQueryHandler(menu_callback, pattern="^client_"),
        CallbackQueryHandler(menu_callback, pattern="^back_to_menu$"),
    ]