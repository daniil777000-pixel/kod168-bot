import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from sqlalchemy import or_, func
from database import get_db
from models import Client, Visit, Master
from services.qr import generate_qr
from services.search import search_clients
from services.statistics import get_client_statistics
import io

logger = logging.getLogger(__name__)

# Состояния для добавления клиента
NAME, PHONE, BIRTHDAY, FAVORITE_CUT, COSMETIC, DISLIKES, NOTES = range(7)

# Состояния для добавления визита
VISIT_CLIENT, VISIT_SERVICE, VISIT_PRICE, VISIT_COMMENT, VISIT_PHOTO_BEFORE, VISIT_PHOTO_AFTER = range(6, 12)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    db = next(get_db())
    master = db.query(Master).filter(Master.telegram_id == user_id).first()
    db.close()
    
    if master:
        context.user_data["is_admin"] = master.is_admin
        context.user_data["master_id"] = master.id
        await update.message.reply_text(
            f"👋 Привет, {master.name}!\n\n"
            "🔥 **KOD 168 CRM**\n"
            "Полная система управления барбершопом\n\n"
            "📌 Используй /menu для доступа ко всем функциям",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "👋 Добро пожаловать в **KOD 168 CRM**!\n\n"
            "⚠️ Твой аккаунт не привязан к системе.\n"
            "Обратись к администратору для добавления.",
            parse_mode="Markdown"
        )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = context.user_data.get("is_admin", False)
    keyboard = [
        [InlineKeyboardButton("➕ Новый клиент", callback_data="add_client")],
        [InlineKeyboardButton("🔍 Найти клиента", callback_data="search_client")],
        [InlineKeyboardButton("👥 Мои клиенты", callback_data="my_clients")],
        [InlineKeyboardButton("📅 Добавить визит", callback_data="add_visit")],
        [InlineKeyboardButton("📊 Статистика", callback_data="statistics")],
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("👨‍🎨 Управление мастерами", callback_data="masters")])
        keyboard.append([InlineKeyboardButton("⚙️ Настройки", callback_data="settings")])
    
    await update.message.reply_text(
        "🔥 **KOD 168 CRM**\n\n"
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "add_client":
        await add_client_start(update, context)
    elif data == "search_client":
        await search_command(update, context)
    elif data == "my_clients":
        await clients_list(update, context)
    elif data == "add_visit":
        await add_visit_start(update, context)
    elif data == "statistics":
        await statistics_command(update, context)
    elif data == "masters" and context.user_data.get("is_admin"):
        await masters_menu(update, context)
    elif data.startswith("client_"):
        client_id = int(data.split("_")[1])
        await show_client_card(update, context, client_id)
    elif data.startswith("visit_history_"):
        client_id = int(data.split("_")[2])
        await visit_history(update, context, client_id)

async def add_client_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.message.reply_text(
            "📝 **Добавление нового клиента**\n\n"
            "Введите имя клиента:",
            parse_mode="Markdown"
        )
        return NAME
    else:
        await update.message.reply_text(
            "📝 **Добавление нового клиента**\n\n"
            "Введите имя клиента:",
            parse_mode="Markdown"
        )
        return NAME

async def add_client_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["client_name"] = update.message.text
    await update.message.reply_text(
        "📱 Введите номер телефона клиента:\n"
        "(или введите /skip)"
    )
    return PHONE

async def add_client_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/skip":
        context.user_data["client_phone"] = None
    else:
        context.user_data["client_phone"] = update.message.text
    await update.message.reply_text(
        "🎂 Введите дату рождения (ДД.ММ):\n"
        "(или /skip)"
    )
    return BIRTHDAY

async def add_client_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/skip":
        context.user_data["client_birthday"] = None
    else:
        context.user_data["client_birthday"] = update.message.text
    await update.message.reply_text(
        "✂️ Любимая стрижка:\n"
        "(или /skip)"
    )
    return FAVORITE_CUT

async def add_client_cut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/skip":
        context.user_data["client_cut"] = None
    else:
        context.user_data["client_cut"] = update.message.text
    await update.message.reply_text(
        "🧴 Любимая косметика:\n"
        "(или /skip)"
    )
    return COSMETIC

async def add_client_cosmetic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/skip":
        context.user_data["client_cosmetic"] = None
    else:
        context.user_data["client_cosmetic"] = update.message.text
    await update.message.reply_text(
        "❌ Что не любит клиент:\n"
        "(или /skip)"
    )
    return DISLIKES

async def add_client_dislikes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/skip":
        context.user_data["client_dislikes"] = None
    else:
        context.user_data["client_dislikes"] = update.message.text
    await update.message.reply_text(
        "📝 Заметки мастера:\n"
        "(или /skip)"
    )
    return NOTES

async def add_client_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/skip":
        context.user_data["client_notes"] = None
    else:
        context.user_data["client_notes"] = update.message.text
    
    db = next(get_db())
    client = Client()
    client.name = context.user_data.get("client_name")
    client.phone = context.user_data.get("client_phone")
    client.birthday = context.user_data.get("client_birthday")
    client.favorite_cut = context.user_data.get("client_cut")
    client.favorite_cosmetic = context.user_data.get("client_cosmetic")
    client.dislikes = context.user_data.get("client_dislikes")
    client.notes = context.user_data.get("client_notes")
    client.kod_id = client.generate_kod_id()
    client.master_id = context.user_data.get("master_id")
    client.status = "active"
    
    db.add(client)
    db.commit()
    db.refresh(client)
    db.close()
    
    await update.message.reply_text(
        f"✅ **Клиент добавлен!**\n\n"
        f"👤 Имя: {client.name}\n"
        f"🆔 KOD ID: `{client.kod_id}`\n\n"
        f"Используй /client {client.name} для просмотра карточки",
        parse_mode="Markdown"
    )
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Операция отменена")
    context.user_data.clear()
    return ConversationHandler.END

async def clients_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    master_id = context.user_data.get("master_id")
    db = next(get_db())
    
    query = db.query(Client)
    if master_id:
        query = query.filter(Client.master_id == master_id)
    
    clients = query.order_by(Client.created_at.desc()).limit(20).all()
    db.close()
    
    if not clients:
        await update.message.reply_text("📭 У вас пока нет клиентов.\nИспользуйте /add для добавления")
        return
    
    text = "👥 **Последние клиенты:**\n\n"
    for i, client in enumerate(clients, 1):
        text += f"{i}. {client.name} | `{client.kod_id}` | {client.phone or 'Нет телефона'}\n"
    
    keyboard = []
    for client in clients[:10]:
        keyboard.append([InlineKeyboardButton(client.name, callback_data=f"client_{client.id}")])
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_client_card(update: Update, context: ContextTypes.DEFAULT_TYPE, client_id: int = None):
    if client_id is None:
        # Если команда /client [имя]
        args = context.args
        if not args:
            await update.message.reply_text("❌ Укажите имя или KOD ID клиента.\nПример: `/client Александр`", parse_mode="Markdown")
            return
        query = " ".join(args)
        db = next(get_db())
        client = db.query(Client).filter(
            or_(
                Client.name.ilike(f"%{query}%"),
                Client.kod_id.ilike(f"%{query}%"),
                Client.phone.ilike(f"%{query}%")
            )
        ).first()
        db.close()
    else:
        db = next(get_db())
        client = db.query(Client).filter(Client.id == client_id).first()
        db.close()
    
    if not client:
        await update.message.reply_text("❌ Клиент не найден")
        return
    
    # Статистика
    stats = get_client_statistics(client.id)
    
    text = f"""
👤 **{client.name}**
🆔 KOD ID: `{client.kod_id}`
📱 Телефон: {client.phone or 'Не указан'}
🎂 День рождения: {client.birthday or 'Не указан'}

✂️ **Любимая стрижка:** {client.favorite_cut or 'Не указана'}
🧴 **Косметика:** {client.favorite_cosmetic or 'Не указана'}
❌ **Не любит:** {client.dislikes or 'Не указано'}

📊 **Статистика:**
💰 Всего потрачено: {client.total_spent or 0} ₽
📅 Визитов: {client.visits_count or 0}
⭐ Статус: {client.status or 'Обычный'}
📈 Средний чек: {stats['avg_check'] if stats else 0:.0f} ₽

📝 **Заметки:** {client.notes or 'Нет'}

📅 Дата регистрации: {client.created_at.strftime('%d.%m.%Y')}
    """
    
    keyboard = [
        [InlineKeyboardButton("➕ Добавить визит", callback_data=f"add_visit_for_{client.id}")],
        [InlineKeyboardButton("📷 QR-код", callback_data=f"qr_{client.kod_id}")],
        [InlineKeyboardButton("📋 История визитов", callback_data=f"visit_history_{client.id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")],
    ]
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def qr_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kod_id = query.data.split("_")[1]
    
    qr_data = generate_qr(kod_id)
    await query.message.reply_photo(photo=io.BytesIO(qr_data), caption=f"🆔 QR-код для {kod_id}")

async def visit_history(update: Update, context: ContextTypes.DEFAULT_TYPE, client_id: int = None):
    if client_id is None:
        args = context.args
        if not args:
            await update.message.reply_text("❌ Укажите имя клиента")
            return
        query = " ".join(args)
        db = next(get_db())
        client = db.query(Client).filter(Client.name.ilike(f"%{query}%")).first()
        db.close()
        if not client:
            await update.message.reply_text("❌ Клиент не найден")
            return
        client_id = client.id
    
    db = next(get_db())
    client = db.query(Client).filter(Client.id == client_id).first()
    visits = db.query(Visit).filter(Visit.client_id == client_id).order_by(Visit.date.desc()).all()
    db.close()
    
    if not visits:
        await update.message.reply_text(f"📭 У {client.name} пока нет визитов")
        return
    
    text = f"📋 **История визитов** - {client.name}\n\n"
    for i, visit in enumerate(visits[:10], 1):
        text += f"{i}. {visit.date.strftime('%d.%m.%Y')} - {visit.service} - {visit.price} ₽\n"
        if visit.comment:
            text += f"   📝 {visit.comment}\n"
    
    if len(visits) > 10:
        text += f"\n... и ещё {len(visits) - 10} визитов"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def add_visit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.message.reply_text(
            "📝 **Добавление визита**\n\n"
            "Введите KOD ID или имя клиента:"
        )
        return VISIT_CLIENT
    else:
        await update.message.reply_text(
            "📝 **Добавление визита**\n\n"
            "Введите KOD ID или имя клиента:"
        )
        return VISIT_CLIENT

async def add_visit_client(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    db = next(get_db())
    client = db.query(Client).filter(
        or_(
            Client.name.ilike(f"%{query}%"),
            Client.kod_id.ilike(f"%{query}%")
        )
    ).first()
    db.close()
    
    if not client:
        await update.message.reply_text("❌ Клиент не найден. Попробуйте снова:")
        return VISIT_CLIENT
    
    context.user_data["visit_client_id"] = client.id
    await update.message.reply_text(
        f"✅ Клиент: {client.name}\n\n"
        "✂️ Введите услугу (например: Мужская стрижка):"
    )
    return VISIT_SERVICE

async def add_visit_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["visit_service"] = update.message.text
    await update.message.reply_text("💰 Введите цену (в рублях):")
    return VISIT_PRICE

async def add_visit_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text.replace("₽", "").strip())
        context.user_data["visit_price"] = price
        await update.message.reply_text(
            "📝 Введите комментарий к визиту:\n"
            "(или /skip для пропуска)"
        )
        return VISIT_COMMENT
    except:
        await update.message.reply_text("❌ Введите корректную цену (число):")
        return VISIT_PRICE

async def add_visit_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/skip":
        context.user_data["visit_comment"] = None
    else:
        context.user_data["visit_comment"] = update.message.text
    
    # Сохраняем визит
    db = next(get_db())
    visit = Visit()
    visit.client_id = context.user_data["visit_client_id"]
    visit.service = context.user_data["visit_service"]
    visit.price = context.user_data["visit_price"]
    visit.comment = context.user_data.get("visit_comment")
    visit.master_id = context.user_data.get("master_id")
    
    db.add(visit)
    db.commit()
    
    # Обновляем клиента
    client = db.query(Client).filter(Client.id == visit.client_id).first()
    client.visits_count = (client.visits_count or 0) + 1
    client.total_spent = (client.total_spent or 0) + visit.price
    if client.total_spent > 5000:
        client.status = "vip"
    db.commit()
    db.close()
    
    await update.message.reply_text(
        f"✅ **Визит добавлен!**\n\n"
        f"👤 Клиент: {client.name}\n"
        f"✂️ Услуга: {visit.service}\n"
        f"💰 Цена: {visit.price} ₽\n"
        f"📝 Комментарий: {visit.comment or 'Нет'}\n\n"
        f"📊 Всего визитов: {client.visits_count}\n"
        f"💰 Всего потрачено: {client.total_spent} ₽"
    )
    context.user_data.clear()
    return ConversationHandler.END

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text(
            "🔍 **Поиск клиентов**\n\n"
            "Примеры:\n"
            "/search Александр\n"
            "/search 79991234567\n"
            "/search KOD168-123456",
            parse_mode="Markdown"
        )
        return
    
    query = " ".join(args)
    master_id = context.user_data.get("master_id")
    results = search_clients(query, master_id)
    
    if not results:
        await update.message.reply_text(f"❌ Клиенты не найдены: {query}")
        return
    
    text = f"🔍 **Найдено {len(results)} клиентов:**\n\n"
    keyboard = []
    for client in results[:10]:
        text += f"• {client.name} | `{client.kod_id}` | {client.phone or 'Нет телефона'}\n"
        keyboard.append([InlineKeyboardButton(client.name, callback_data=f"client_{client.id}")])
    
    if len(results) > 10:
        text += f"\n... и ещё {len(results) - 10} клиентов"
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def statistics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    master_id = context.user_data.get("master_id")
    
    # Общая статистика
    total_clients = db.query(Client).count()
    total_visits = db.query(Visit).count()
    total_revenue = db.query(func.sum(Visit.price)).scalar() or 0
    
    # Статистика мастера
    master_stats = db.query(
        Master.name,
        func.count(Client.id).label("clients"),
        func.count(Visit.id).label("visits"),
        func.sum(Visit.price).label("revenue")
    ).outerjoin(Client, Client.master_id == Master.id)\
     .outerjoin(Visit, Visit.client_id == Client.id)\
     .group_by(Master.id).all()
    
    db.close()
    
    text = f"""
📊 **СТАТИСТИКА KOD 168**

👥 **Общая:**
Всего клиентов: {total_clients}
Всего визитов: {total_visits}
Общая выручка: {total_revenue:.0f} ₽

👨‍🎨 **Мастера:**
"""
    for stat in master_stats:
        text += f"\n• {stat[0]}: {stat[1] or 0} клиентов, {stat[2] or 0} визитов, {stat[3] or 0:.0f} ₽"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def masters_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("is_admin"):
        await update.message.reply_text("⛔️ Недостаточно прав")
        return
    
    db = next(get_db())
    masters = db.query(Master).all()
    db.close()
    
    text = "👨‍🎨 **Управление мастерами**\n\n"
    for master in masters:
        text += f"• {master.name} | {'✅ Админ' if master.is_admin else '👤 Мастер'}\n"
    
    keyboard = [
        [InlineKeyboardButton("➕ Добавить мастера", callback_data="add_master")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
    ]
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

def get_handlers():
    add_client_conv = ConversationHandler(
        entry_points=[
            CommandHandler("add", add_client_start),
            CommandHandler("add_client", add_client_start),
            CallbackQueryHandler(add_client_start, pattern="^add_client$")
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_phone)],
            BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_birthday)],
            FAVORITE_CUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_cut)],
            COSMETIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_cosmetic)],
            DISLIKES: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_dislikes)],
            NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_notes)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="add_client"
    )
    
    add_visit_conv = ConversationHandler(
        entry_points=[
            CommandHandler("visit", add_visit_start),
            CallbackQueryHandler(add_visit_start, pattern="^add_visit$"),
            CallbackQueryHandler(add_visit_start, pattern="^add_visit_for_")
        ],
        states={
            VISIT_CLIENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_visit_client)],
            VISIT_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_visit_service)],
            VISIT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_visit_price)],
            VISIT_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_visit_comment)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="add_visit"
    )
    
    return [
        CommandHandler("start", start_command),
        CommandHandler("menu", menu_command),
        CommandHandler("clients", clients_list),
        CommandHandler("client", show_client_card),
        CommandHandler("search", search_command),
        CommandHandler("stats", statistics_command),
        CommandHandler("history", visit_history),
        add_client_conv,
        add_visit_conv,
        CallbackQueryHandler(menu_callback, pattern="^(add_client|search_client|my_clients|add_visit|statistics|masters|settings)$"),
        CallbackQueryHandler(qr_callback, pattern="^qr_"),
        CallbackQueryHandler(show_client_card, pattern="^client_"),
        CallbackQueryHandler(visit_history, pattern="^visit_history_"),
        CallbackQueryHandler(masters_menu, pattern="^masters$"),
        CallbackQueryHandler(menu_command, pattern="^back_to_menu$"),
    ]