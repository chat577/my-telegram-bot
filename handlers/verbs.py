from telegram import Update
from telegram.ext import ContextTypes
import random
from data.verbs import IRREGULAR_VERBS, BASIC_VERBS
from utils.keyboards import get_verbs_menu_keyboard, get_back_to_main_keyboard

async def handle_verbs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "verbs_irregular":
        # Показываем первые 10 неправильных глаголов
        verbs_text = "📖 *Неправильные глаголы (топ-10):*\n\n"
        verbs_text += "`Инфинитив    | Прошедшее   | Причастие  | Перевод`\n"
        verbs_text += "`-------------|-------------|------------|---------`\n"
        
        for verb in IRREGULAR_VERBS[:10]:
            verbs_text += f"`{verb['infinitive']:<12} | {verb['past']:<11} | {verb['participle']:<10} | {verb['translation']}`\n"
        
        verbs_text += "\n💡 *Совет:* Учите по 5-10 глаголов в день!"
        
        await query.edit_message_text(
            text=verbs_text,
            parse_mode='Markdown',
            reply_markup=get_verbs_menu_keyboard()
        )
    
    elif query.data == "verbs_basic":
        # Показываем основные глаголы
        verbs_text = "🔠 *Основные глаголы для начинающих:*\n\n"
        
        for i, verb in enumerate(BASIC_VERBS[:15], 1):
            verbs_text += f"*{verb['english']}* - {verb['russian']}\n"
            verbs_text += f"   _Пример: {verb['example']}_\n\n"
        
        await query.edit_message_text(
            text=verbs_text,
            parse_mode='Markdown',
            reply_markup=get_verbs_menu_keyboard()
        )

async def send_flashcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # Случайно выбираем тип карточки
    card_type = random.choice(['irregular_verb', 'basic_verb', 'phrase'])
    
    if card_type == 'irregular_verb':
        verb = random.choice(IRREGULAR_VERBS)
        text = f"""
🎴 *Карточка: Неправильный глагол*

💬 *Инфинитив:* {verb['infinitive']}
⏳ *Прошедшее время:* {verb['past']}
📝 *Причастие II:* {verb['participle']}
🇷🇺 *Перевод:* {verb['translation']}
🎯 *Уровень:* {verb['level']}

*Пример предложения:*
_I {verb['infinitive']} here every day._ → Я {verb['translation']} здесь каждый день.
        """
    
    elif card_type == 'basic_verb':
        verb = random.choice(BASIC_VERBS)
        text = f"""
🎴 *Карточка: Основной глагол*

💬 *Английский:* {verb['english']}
🇷🇺 *Русский:* {verb['russian']}
📚 *Пример:* {verb['example']}

*Попробуйте составить свое предложение!*
        """
    
    else:  # phrase
        from data.phrases import PHRASES
        category = random.choice(list(PHRASES.values()))
        phrase = random.choice(category['phrases'])
        text = f"""
🎴 *Карточка: Разговорная фраза*

💬 *Английский:* {phrase['english']}
🇷🇺 *Русский:* {phrase['russian']}
📝 *Контекст:* {phrase['context']}

*Попрактикуйтесь в произношении!*
        """
    
    keyboard = [
        [InlineKeyboardButton("🔄 Еще карточку", callback_data="menu_flashcards")],
        [InlineKeyboardButton("◀️ В главное меню", callback_data="back_to_main")]
    ]
    
    if query:
        await query.edit_message_text(
            text=text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text=text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
