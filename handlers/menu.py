from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

def get_main_menu_markup(is_admin: bool = False):
    """Создаёт клавиатуру главного меню"""
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
    """Команда /menu — показать главное меню"""
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
    
    # Обрабатываем каждую кнопку
    if callback_data == "menu_add_client":
        await query.edit_message_text(
            "➕ **Добавление клиента**\n\n"
            "Используй команду /add или нажми кнопку ниже:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Добавить клиента", callback_data="add_client")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
            ]),
            parse_mode="Markdown"
        )
    
    elif callback_data == "menu_search_client":
        await query.edit_message_text(
            "🔍 **Поиск клиента**\n\n"
            "Используй команду /search [имя/телефон/KOD ID]\n"
            "Пример: `/search Александр`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
            ]),
            parse_mode="Markdown"
        )
    
    elif callback_data == "menu_my_clients":
        await query.edit_message_text(
            "👥 **Мои клиенты**\n\n"
            "Используй команду /clients для просмотра списка",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
            ]),
            parse_mode="Markdown"
        )
    
    elif callback_data == "menu_add_visit":
        await query.edit_message_text(
            "📅 **Добавление визита**\n\n"
            "Используй команду /visit",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
            ]),
            parse_mode="Markdown"
        )
    
    elif callback_data == "menu_statistics":
        await query.edit_message_text(
            "📊 **Статистика**\n\n"
            "Используй команду /stats",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
            ]),
            parse_mode="Markdown"
        )
    
    elif callback_data == "menu_masters":
        await query.edit_message_text(
            "👨‍🎨 **Управление мастерами**\n\n"
            "Только для администратора",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
            ]),
            parse_mode="Markdown"
        )
    
    elif callback_data == "menu_settings":
        await query.edit_message_text(
            "⚙️ **Настройки**\n\n"
            "Только для администратора",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
            ]),
            parse_mode="Markdown"
        )
    
    else:
        await query.edit_message_text(
            "❌ Неизвестная команда",
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
        # Обработчик для всех кнопок меню с префиксом "menu_"
        CallbackQueryHandler(menu_callback, pattern="^menu_"),
        # Обработчик для кнопки "Назад"
        CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"),
    