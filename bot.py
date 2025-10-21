import os
import logging
import random
import aiohttp
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

class EnglishParser:
    def __init__(self):
        self.session = None
        
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None
    
    async def parse_verb(self, verb):
        """Парсит информацию о глаголе с lingvolive"""
        try:
            session = await self.get_session()
            url = f"https://www.lingvolive.com/ru-ru/translate/en-ru/{verb}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Ищем транскрипцию и перевод
                    transcription = ""
                    translation = ""
                    
                    # Пример парсинга (нужно адаптировать под конкретную структуру сайта)
                    trans_elem = soup.find('span', class_='transcription')
                    if trans_elem:
                        transcription = trans_elem.text
                    
                    trans_elem = soup.find('span', class_='translation')
                    if trans_elem:
                        translation = trans_elem.text
                    
                    return {
                        'verb': verb,
                        'transcription': transcription or "[транскрипция]",
                        'translation': translation or "[перевод]",
                        'source': 'lingvolive'
                    }
        except Exception as e:
            logger.error(f"Error parsing verb {verb}: {e}")
        
        return None
    
    async def parse_phrase(self, phrase_type):
        """Парсит разговорные фразы"""
        phrases_db = {
            "greetings": [
                "Hello", "Hi", "Good morning", "Good afternoon", "Good evening"
            ],
            "introduction": [
                "My name is", "I am from", "Nice to meet you", "How are you"
            ],
            "questions": [
                "What is this", "Where is", "How much", "Can you help me"
            ]
        }
        
        phrases = phrases_db.get(phrase_type, [])
        results = []
        
        for phrase in phrases:
            try:
                session = await self.get_session()
                url = f"https://www.lingvolive.com/ru-ru/translate/en-ru/{phrase.replace(' ', '+')}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'lxml')
                        
                        translation_elem = soup.find('span', class_='translation')
                        translation = translation_elem.text if translation_elem else "[перевод]"
                        
                        results.append({
                            'english': phrase,
                            'russian': translation,
                            'context': "Разговорная фраза"
                        })
            except Exception as e:
                logger.error(f"Error parsing phrase {phrase}: {e}")
                results.append({
                    'english': phrase,
                    'russian': "[автоматический перевод]",
                    'context': "Разговорная фраза"
                })
        
        return results

# Глобальный парсер
parser = EnglishParser()

# Клавиатуры
def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📚 Времена с примерами", callback_data="menu_tenses")],
        [InlineKeyboardButton("🔤 Глаголы с переводом", callback_data="menu_verbs")],
        [InlineKeyboardButton("💬 Фразы с контекстом", callback_data="menu_phrases")],
        [InlineKeyboardButton("🎯 Случайное слово", callback_data="random_word")],
        [InlineKeyboardButton("📖 Упражнение", callback_data="exercise")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_verbs_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎯 Топ-глаголы", callback_data="verbs_top")],
        [InlineKeyboardButton("🔍 Найти глагол", callback_data="verbs_search")],
        [InlineKeyboardButton("📊 По темам", callback_data="verbs_themes")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_phrases_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("👋 Приветствия", callback_data="phrases_greetings")],
        [InlineKeyboardButton("🤝 Знакомство", callback_data="phrases_introduction")],
        [InlineKeyboardButton❓ Вопросы", callback_data="phrases_questions")],
        [InlineKeyboardButton("☕ Кафе/Ресторан", callback_data="phrases_cafe")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Обработчики
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🇬🇧 *English Helper - Умный бот для изучения английского!* 🇺🇸

✨ *Особенности:*
• 📚 Актуальные материалы с образовательных сайтов
• 🔤 Реальные примеры использования
• 🎯 Транскрипции и переводы
• 💬 Разговорные фразы с контекстом

*Бот использует свежие данные для вашего обучения!*

Выберите раздел:
    """
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )

async def handle_verbs_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
🔍 *Поиск глагола*

Введите глагол на английском, и я найду:
• Транскрипцию
• Перевод
• Формы (для неправильных)

*Пример:* `/verb go` или `/verb be`

Или выберите из популярных:
"""
    
    keyboard = [
        [InlineKeyboardButton("be", callback_data="verb_be"),
        [InlineKeyboardButton("have", callback_data="verb_have")],
        [InlineKeyboardButton("do", callback_data="verb_do")],
        [InlineKeyboardButton("go", callback_data="verb_go")],
        [InlineKeyboardButton("see", callback_data="verb_see")],
        [InlineKeyboardButton("◀️ Назад", callback_data="menu_verbs")],
    ]
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_verb_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    verb = query.data.replace("verb_", "")
    
    # Показываем загрузку
    await query.edit_message_text(
        text=f"🔍 Ищу информацию о глаголе *{verb}*...",
        parse_mode='Markdown'
    )
    
    # Парсим информацию
    verb_info = await parser.parse_verb(verb)
    
    if verb_info:
        text = f"""
🔤 *Глагол: {verb_info['verb']}*

📝 *Транскрипция:* {verb_info['transcription']}
🇷🇺 *Перевод:* {verb_info['translation']}
📚 *Источник:* {verb_info['source']}

💡 *Примеры использования:*
• I {verb} every day
• She {verb}s to school
• They {verb}ed yesterday

🎯 *Совет:* Составьте 3 своих предложения с этим глаголом!
        """
    else:
        text = f"""
🔤 *Глагол: {verb}*

⚠️ *Информация временно недоступна*

*Базовые формы:*
• Infinitive: {verb}
• Past Simple: [{verb}ed или неправильная форма]
• Past Participle: [{verb}ed или неправильная форма]

💡 *Попробуйте:* Используйте этот глагол в предложении!
        """
    
    keyboard = [
        [InlineKeyboardButton("🔍 Другой глагол", callback_data="verbs_search")],
        [InlineKeyboardButton("◀️ В меню", callback_data="back_to_main")],
    ]
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_phrases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    phrase_type = query.data.replace("phrases_", "")
    
    # Показываем загрузку
    await query.edit_message_text(
        text=f"🔍 Загружаю {phrase_type}...",
        parse_mode='Markdown'
    )
    
    # Парсим фразы
    phrases = await parser.parse_phrase(phrase_type)
    
    if phrases:
        text = f"💬 *{phrase_type.upper()}*\n\n"
        for phrase in phrases[:8]:  # Ограничиваем количество
            text += f"• *{phrase['english']}* - {phrase['russian']}\n"
            text += f"  _{phrase['context']}_\n\n"
    else:
        # Резервные фразы
        backup_phrases = {
            "greetings": [
                {"english": "Hello", "russian": "Привет", "context": "Неформальное приветствие"},
                {"english": "Good morning", "russian": "Доброе утро", "context": "Утреннее приветствие"},
            ],
            "introduction": [
                {"english": "My name is", "russian": "Меня зовут", "context": "Представление"},
                {"english": "I am from", "russian": "Я из", "context": "Указание происхождения"},
            ]
        }
        
        phrases = backup_phrases.get(phrase_type, [])
        text = f"💬 *{phrase_type.upper()}*\n\n"
        for phrase in phrases:
            text += f"• *{phrase['english']}* - {phrase['russian']}\n"
            text += f"  _{phrase['context']}_\n\n"
    
    text += "💡 *Произносите вслух для практики!*"
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_phrases_menu_keyboard()
    )

async def random_word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Случайное слово с переводом"""
    popular_words = ["hello", "time", "people", "water", "food", "house", "city", "car", "book", "friend"]
    word = random.choice(popular_words)
    
    word_info = await parser.parse_verb(word)
    
    if word_info:
        text = f"""
🎯 *Случайное слово дня!*

📖 *Слово:* {word_info['verb']}
📝 *Транскрипция:* {word_info['transcription']}
🇷🇺 *Перевод:* {word_info['translation']}

*Составьте предложение с этим словом!*
        """
    else:
        text = f"""
🎯 *Случайное слово дня!*

📖 *Слово:* {word}
🇷🇺 *Перевод:* [популярное слово]

*Пример:* I like this {word}!
        """
    
    keyboard = [
        [InlineKeyboardButton("🔄 Другое слово", callback_data="random_word")],
        [InlineKeyboardButton("📚 Все разделы", callback_data="back_to_main")],
    ]
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
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

# Команда для ручного ввода глагола
async def verb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Введите глагол после команды: `/verb go`")
        return
    
    verb = context.args[0].lower()
    
    # Парсим информацию о глаголе
    verb_info = await parser.parse_verb(verb)
    
    if verb_info:
        text = f"""
🔍 *Результат поиска:*

📖 *Глагол:* {verb_info['verb']}
📝 *Транскрипция:* {verb_info['transcription']}
🇷🇺 *Перевод:* {verb_info['translation']}
🔗 *Источник:* {verb_info['source']}

💡 *Используйте в предложениях!*
        """
    else:
        text = f"""
🔍 *Глагол:* {verb}

⚠️ *Не удалось найти подробную информацию*

*Попробуйте:*
• Проверить написание
• Использовать базовую форму
• Попробовать другой глагол

💡 *Пример использования:* I want to {verb}
        """
    
    await update.message.reply_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )

# Главный обработчик меню
async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == "back_to_main":
        text = "🏠 *Главное меню*\n\nВыберите раздел:"
        keyboard = get_main_menu_keyboard()
    
    elif callback_data == "menu_verbs":
        text = "🔤 *Изучение глаголов*\n\nВыберите опцию:"
        keyboard = get_verbs_menu_keyboard()
    
    elif callback_data == "menu_phrases":
        text = "💬 *Разговорные фразы*\n\nВыберите категорию:"
        keyboard = get_phrases_menu_keyboard()
    
    elif callback_data == "verbs_search":
        return await handle_verbs_search(update, context)
    
    elif callback_data.startswith("verb_"):
        return await handle_verb_detail(update, context)
    
    elif callback_data.startswith("phrases_"):
        return await handle_phrases(update, context)
    
    elif callback_data == "random_word":
        return await random_word_command(update, context)
    
    elif callback_data == "menu_tenses":
        text = """
📚 *Английские времена*

*Доступные времена с примерами:*

🟢 *Present Simple*
`I work every day` - Я работаю каждый день

🔵 *Present Continuous*  
`I am working now` - Я работаю сейчас

🟠 *Past Simple*
`I worked yesterday` - Я работал вчера

🟣 *Future Simple*
`I will work tomorrow` - Я буду работать завтра

💡 *Для подробного изучения используйте:* `/tense present_simple`
        """
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")]]
    
    else:
        return
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

def main():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден!")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("verb", verb_command))
    application.add_handler(CommandHandler("word", random_word_command))
    
    # Обработчики callback
    application.add_handler(CallbackQueryHandler(handle_main_menu))
    
    # Запуск
    if os.getenv('RAILWAY_ENVIRONMENT'):
        PORT = int(os.getenv('PORT', 8443))
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"https://{os.getenv('RAILWAY_STATIC_URL', '')}/{BOT_TOKEN}"
        )
    else:
        application.run_polling()

if __name__ == '__main__':
    main()
