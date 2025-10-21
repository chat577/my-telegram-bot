from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Главное меню
def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📚 Времена", callback_data="menu_tenses")],
        [InlineKeyboardButton("🔤 Глаголы", callback_data="menu_verbs")],
        [InlineKeyboardButton("💬 Разговорные фразы", callback_data="menu_phrases")],
        [InlineKeyboardButton("🎴 Карточки для запоминания", callback_data="menu_flashcards")],
        [InlineKeyboardButton("ℹ️ О боте", callback_data="menu_about")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Меню времен
def get_tenses_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Present Simple", callback_data="tense_present_simple")],
        [InlineKeyboardButton("Present Continuous", callback_data="tense_present_continuous")],
        [InlineKeyboardButton("Past Simple", callback_data="tense_past_simple")],
        [InlineKeyboardButton("Future Simple", callback_data="tense_future_simple")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Меню глаголов
def get_verbs_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📖 Неправильные глаголы", callback_data="verbs_irregular")],
        [InlineKeyboardButton("🔠 Основные глаголы", callback_data="verbs_basic")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Меню фраз
def get_phrases_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("👋 Приветствия", callback_data="phrases_greetings")],
        [InlineKeyboardButton("🤝 Знакомство", callback_data="phrases_introduction")],
        [InlineKeyboardButton("☕ В кафе", callback_data="phrases_cafe")],
        [InlineKeyboardButton("❓ Вопросы", callback_data="phrases_questions")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Кнопка назад в главное меню
def get_back_to_main_keyboard():
    keyboard = [[InlineKeyboardButton("◀️ В главное меню", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(keyboard)
