from telegram import Update
from telegram.ext import ContextTypes
from data.tenses import TENSES
from utils.keyboards import get_tenses_menu_keyboard, get_back_to_main_keyboard

async def handle_tenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tense_key = query.data.replace("tense_", "")
    
    if tense_key in TENSES:
        tense = TENSES[tense_key]
        
        text = f"""
📚 *{tense['name']}* ({tense['russian_name']})

🎯 *Использование:* {tense['usage']}

🏗️ *Формула:* `{tense['structure']}`

📝 *Примеры:*
"""
        for example in tense['examples']:
            text += f"• {example}\n"
        
        text += f"\n🔍 *Слова-маркеры:* {', '.join(tense['signal_words'])}"
        
        await query.edit_message_text(
            text=text,
            parse_mode='Markdown',
            reply_markup=get_tenses_menu_keyboard()
        )
