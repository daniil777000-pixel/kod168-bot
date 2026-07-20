from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

def get_main_menu_markup(is_admin: bool = False):
    keyboard = [
        [InlineKeyboardButton("➕ Новый клиент", callback_data="menu_add_client")],
        [InlineKeyboardButton("🔍 Найти клиента", callback_data="menu_search_client")],
        [InlineKeyboardButton("👥 Мои клиенты", callback_data="menu_my_clients")],
        [InlineKeyboardButton("📅 Добавить визит", callback_data="menu_add_visit")],
        [InlineKeyboardButton("📊 Статистика", callback_data="menu_statistics")],
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("👨‍🎨 Мастера", callback_data="menu_masters")])
        keyboard.append([InlineKeyboardButton("⚙️ Настройки", callback_data="menu_settings")])
    return InlineKeyboardMarkup(keyboard)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = context.user_data.get("is_admin", False)
    await update.message.reply_text(
        "🔥 **KOD 168 CRM**\n\nВыберите действие:",
        reply_markup=get_main_menu_markup(is_admin),
        parse_mode="Markdown"
    )

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "menu_add_client":
        await query.edit_message_text("➕ Используй команду /add", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]))
    elif data == "menu_search_client":
        await query.edit_message_text("🔍 Используй команду /search", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]))
    elif data == "menu_my_clients":
        await query.edit_message_text("👥 Используй команду /clients", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]))
    elif data == "menu_add_visit":
        await query.edit_message_text("📅 Используй команду /visit", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]))
    elif data == "menu_statistics":
        await query.edit_message_text("📊 Используй команду /stats", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]))
    elif data == "back_to_menu":
        is_admin = context.user_data.get("is_admin", False)
        await query.edit_message_text(
            "🔥 **KOD 168 CRM**\n\nВыберите действие:",
            reply_markup=get_main_menu_markup(is_admin),
            parse_mode="Markdown"
        )

def get_menu_handlers():
    return [
        CommandHandler("menu", menu_command),
        CallbackQueryHandler(menu_callback, pattern="^menu_"),
        CallbackQueryHandler(menu_callback, pattern="^back_to_menu$"),
    ]