from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import (
    get_main_menu_keyboard,
    get_tenses_menu_keyboard,
    get_verbs_menu_keyboard,
    get_phrases_menu_keyboard
)

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == "back_to_main":
        text = "🏠 *Главное меню*\n\nВыберите раздел для изучения:"
        keyboard = get_main_menu_keyboard()
    
    elif callback_data == "menu_tenses":
        text = "📚 *Английские времена*\n\nВыберите время для изучения:"
        keyboard = get_tenses_menu_keyboard()
    
    elif callback_data == "menu_verbs":
        text = "🔤 *Глаголы английского языка*\n\nВыберите тип глаголов:"
        keyboard = get_verbs_menu_keyboard()
    
    elif callback_data == "menu_phrases":
        text = "💬 *Разговорные фразы*\n\nВыберите категорию фраз:"
        keyboard = get_phrases_menu_keyboard()
    
    elif callback_data == "menu_flashcards":
        from handlers.verbs import send_flashcard
        return await send_flashcard(update, context)
    
    elif callback_data == "menu_about":
        text = """
ℹ️ *О боте English Helper*

Этот бот создан чтобы помочь вам в изучении английского языка с нуля!

📊 *Доступные материалы:*
• 4 основных времени английского
• 50+ неправильных глаголов
• 40+ основных глаголов
• 25+ разговорных фраз

🎯 *Уровень:* Начальный (A1-A2)

*Учите английский с удовольствием!* 🌟
        """
        keyboard = get_main_menu_keyboard()
    
    else:
        return
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
