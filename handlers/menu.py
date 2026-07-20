from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

def get_main_menu_markup(is_admin: bool = False):
    """Создаёт клавиатуру главного меню"""
    keyboard = [
        [InlineKeyboardButton("➕ Новый клиент", callback_data="add_client")],
        [InlineKeyboardButton("🔍 Найти клиента", callback_data="search_client")],
        [InlineKeyboardButton("👥 Мои клиенты", callback_data="my_clients")],
        [InlineKeyboardButton("📅 Добавить визит", callback_data="add_visit")],
        [InlineKeyboardButton("📊 Статистика", callback_data="statistics")],
    ]
    
    if is_admin:
        keyboard.append([InlineKeyboardButton("👨‍🎨 Мастера", callback_data="masters")])
        keyboard.append([InlineKeyboardButton("⚙️ Настройки", callback_data="settings")])
    
    return InlineKeyboardMarkup(keyboard)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /menu — показать главное меню"""
    user_id = update.effective_user.id
    is_admin = context.user_data.get("is_admin", False)
    
    await update.message.reply_text(
        "🔥 **KOD 168 CRM**\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu_markup(is_admin),
        parse_mode="Markdown"
    )

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий кнопок главного меню"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    user_id = query.from_user.id
    
    # TODO: Реализовать логику для каждого пункта меню
    await query.edit_message_text(
        f"Вы выбрали: {callback_data}\n\nФункция в разработке...",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
        ])
    )

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    query = update.callback_query
    await query.answer()
    
    is_admin = context.user_data.get("is_admin", False)
    await query.edit_message_text(
        "🔥 **KOD 168 CRM**\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu_markup(is_admin),
        parse_mode="Markdown"
    )

def get_menu_handlers():
    """Возвращает обработчики для меню"""
    return [
        CommandHandler("menu", menu_command),
        CallbackQueryHandler(menu_callback, pattern="^(add_client|search_client|my_clients|add_visit|statistics|masters|settings)$"),
        CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"),
    ]