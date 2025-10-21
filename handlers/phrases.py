from telegram import Update
from telegram.ext import ContextTypes
from data.phrases import PHRASES
from utils.keyboards import get_phrases_menu_keyboard

async def handle_phrases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    category_key = query.data.replace("phrases_", "")
    
    if category_key in PHRASES:
        category = PHRASES[category_key]
        
        text = f"{category['name']}\n\n"
        
        for i, phrase in enumerate(category['phrases'], 1):
            text += f"*{phrase['english']}*\n"
            text += f"🇷🇺 {phrase['russian']}\n"
            text += f"_💡 {phrase['context']}_\n\n"
        
        text += "💡 *Совет:* Произносите фразы вслух для лучшего запоминания!"
        
        await query.edit_message_text(
            text=text,
            parse_mode='Markdown',
            reply_markup=get_phrases_menu_keyboard()
        )
