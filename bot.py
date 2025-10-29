import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Импортируем данные
from data import verbs, words, phrases, grammar

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

class EnglishBot:
    def __init__(self):
        self.verbs = verbs
        self.words = words
        self.phrases = phrases
        self.grammar = grammar

    def get_random_word(self):
        """Возвращает случайное слово или глагол"""
        all_items = {**self.verbs, **self.words}
        if not all_items:
            return None
        word = random.choice(list(all_items.keys()))
        return word, all_items[word]

    def search_word(self, word):
        """Ищет слово в базах данных"""
        word = word.lower()
        if word in self.verbs:
            return self.verbs[word], 'verb'
        elif word in self.words:
            return self.words[word], 'word'
        return None, None

# Создаем экземпляр бота
bot_data = EnglishBot()

# --- КЛАВИАТУРЫ ---
def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔤 Поиск слова", callback_data="search_word")],
        [InlineKeyboardButton("📚 Глаголы", callback_data="verbs_menu")],
        [InlineKeyboardButton("💬 Разговорные фразы", callback_data="phrases_menu")],
        [InlineKeyboardButton("📖 Грамматика", callback_data="grammar_menu")],
        [InlineKeyboardButton("🎯 Случайное слово", callback_data="random_word")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_verbs_keyboard():
    keyboard = []
    verbs_list = list(bot_data.verbs.keys())
    
    # Группируем по 2 глагола в строке
    for i in range(0, len(verbs_list), 2):
        row = []
        if i < len(verbs_list):
            row.append(InlineKeyboardButton(verbs_list[i], callback_data=f"verb_{verbs_list[i]}"))
        if i + 1 < len(verbs_list):
            row.append(InlineKeyboardButton(verbs_list[i + 1], callback_data=f"verb_{verbs_list[i + 1]}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def get_phrases_keyboard():
    keyboard = [
        [InlineKeyboardButton("👋 Приветствия", callback_data="phrases_greetings")],
        [InlineKeyboardButton("🤝 Знакомство", callback_data="phrases_introduction")],
        [InlineKeyboardButton("☕ В кафе", callback_data="phrases_cafe")],
        [InlineKeyboardButton("❓ Вопросы", callback_data="phrases_questions")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_grammar_keyboard():
    keyboard = [
        [InlineKeyboardButton("📝 Present Simple", callback_data="grammar_present_simple")],
        [InlineKeyboardButton("⏳ Past Simple", callback_data="grammar_past_simple")],
        [InlineKeyboardButton("🔮 Future Simple", callback_data="grammar_future_simple")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# --- ОБРАБОТЧИКИ КОМАНД ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🇬🇧 *English Learning Bot* 🇺🇸

*Ваш умный помощник для изучения английского!*

✨ *Что умеет бот:*
• 🔤 Поиск слов с транскрипцией
• 📚 Глаголы с формами и примерами  
• 💬 Полезные разговорные фразы
• 📖 Объяснения грамматики
• 🎯 Интерактивные упражнения

🎯 *Уровень:* Начальный (A1)

*Выберите действие:*
    """
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 *Как использовать бота:*

*Основные команды:*
/start - Главное меню
/help - Эта справка
/word <слово> - Найти слово
/verb <глагол> - Найти глагол
/random - Случайное слово

*Интерактивное меню:*
• Используйте кнопки для навигации
• Нажимайте на слова для подробностей
• Практикуйтесь ежедневно!

💡 *Советы для изучения:*
1. Учите по 5-10 слов в день
2. Составляйте свои предложения
3. Повторяйте пройденное
4. Практикуйте произношение

*Удачи в изучении английского!* 🚀
    """
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )

# --- ОБРАБОТЧИКИ CALLBACK ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == "back_to_main":
        await show_main_menu(query)
    
    elif callback_data == "search_word":
        await search_word_handler(query)
    
    elif callback_data == "verbs_menu":
        await verbs_menu_handler(query)
    
    elif callback_data == "phrases_menu":
        await phrases_menu_handler(query)
    
    elif callback_data == "grammar_menu":
        await grammar_menu_handler(query)
    
    elif callback_data == "random_word":
        await random_word_handler(query)
    
    elif callback_data == "help":
        await help_handler(query)
    
    elif callback_data.startswith("verb_"):
        verb = callback_data.replace("verb_", "")
        await word_detail_handler(query, verb, 'verb')
    
    elif callback_data.startswith("phrases_"):
        category = callback_data.replace("phrases_", "")
        await phrases_handler(query, category)
    
    elif callback_data.startswith("grammar_"):
        tense = callback_data.replace("grammar_", "")
        await grammar_handler(query, tense)

async def show_main_menu(query):
    text = "🏠 *Главное меню*\n\nВыберите раздел:"
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )

async def search_word_handler(query):
    text = """
🔍 *Поиск слова или глагола*

Введите слово на английском, и я найду:
• 📝 Транскрипцию (произношение)
• 🇷🇺 Перевод на русский
• 💡 Примеры использования

*Используйте команды:*
`/word hello` - найти слово
`/verb go` - найти глагол

*Или выберите из доступных глаголов:*
    """
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_verbs_keyboard()
    )

async def verbs_menu_handler(query):
    text = f"""
📚 *Английские глаголы*

Доступно *{len(bot_data.verbs)}* глаголов с транскрипцией, переводами и примерами.

Выберите глагол для изучения:
    """
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_verbs_keyboard()
    )

async def phrases_menu_handler(query):
    text = """
💬 *Разговорные фразы*

Полезные выражения для повседневного общения на английском.

Выберите категорию:
    """
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_phrases_keyboard()
    )

async def grammar_menu_handler(query):
    text = """
📖 *Грамматика английского языка*

Изучайте основные времена английского языка с примерами и упражнениями.

Выберите время:
    """
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_grammar_keyboard()
    )

async def random_word_handler(query):
    result = bot_data.get_random_word()
    if not result:
        await query.edit_message_text(
            text="❌ База данных временно недоступна",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    word, info = result
    word_type = 'verb' if word in bot_data.verbs else 'word'
    
    text = f"""
🎯 *Случайное слово для изучения!*

📖 *Слово:* {word}
📝 *Транскрипция:* {info['phonetic']}
🇷🇺 *Перевод:* {info['translation']}
🎯 *Уровень:* {info.get('level', 'A1')}

"""
    
    if word_type == 'verb':
        text += f"📊 *Формы глагола:*\n"
        text += f"• Past Simple: {info['past']}\n"
        text += f"• Past Participle: {info['participle']}\n\n"
    
    text += f"💡 *Пример:* {info['examples'][0]}\n\n"
    text += "*Практика:* Составьте своё предложение с этим словом!"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Новое слово", callback_data="random_word")],
        [InlineKeyboardButton("🔍 Подробнее", callback_data=f"verb_{word}" if word_type == 'verb' else f"word_{word}")],
        [InlineKeyboardButton("◀️ В меню", callback_data="back_to_main")],
    ]
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_handler(query):
    text = """
ℹ️ *Помощь по использованию бота*

*Основные функции:*
🔤 *Поиск слов* - транскрипция, перевод, примеры
📚 *Глаголы* - формы, использование, примеры
💬 *Фразы* - разговорные выражения по темам
📖 *Грамматика* - правила и упражнения

*Для лучшего результата:*
• Занимайтесь регулярно
• Составляйте свои предложения
• Повторяйте пройденное
• Практикуйте произношение

*Удачи в изучении!* 🌟
    """
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")]]
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def word_detail_handler(query, word, word_type):
    info, found_type = bot_data.search_word(word)
    
    if not info:
        await query.edit_message_text(
            text=f"❌ Слово *{word}* не найдено в базе данных",
            parse_mode='Markdown',
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    text = f"""
🔤 *{'Глагол' if found_type == 'verb' else 'Слово'}:* {word}

📝 *Транскрипция:* {info['phonetic']}
🇷🇺 *Перевод:* {info['translation']}
🎯 *Уровень:* {info.get('level', 'A1')}
"""
    
    if found_type == 'verb':
        text += f"\n📊 *Формы глагола:*\n"
        text += f"• Past Simple: {info['past']}\n"
        text += f"• Past Participle: {info['participle']}\n"
    
    text += f"\n💡 *Примеры использования:*\n"
    for example in info['examples']:
        text += f"• {example}\n"
    
    text += f"\n🎯 *Задание:* Составьте 2-3 предложения с этим {'глаголом' if found_type == 'verb' else 'словом'}!"
    
    keyboard = [
        [InlineKeyboardButton("🔍 Другое слово", callback_data="search_word")],
        [InlineKeyboardButton("🎯 Случайное слово", callback_data="random_word")],
        [InlineKeyboardButton("📚 Все глаголы", callback_data="verbs_menu")],
        [InlineKeyboardButton("◀️ В меню", callback_data="back_to_main")],
    ]
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def phrases_handler(query, category):
    if category not in bot_data.phrases:
        await query.edit_message_text(
            text="❌ Категория не найдена",
            reply_markup=get_phrases_keyboard()
        )
        return
    
    category_data = bot_data.phrases[category]
    text = f"💬 *{category_data['name']}*\n\n"
    
    for phrase in category_data['phrases']:
        text += f"• *{phrase['english']}*\n"
        text += f"  🇷🇺 {phrase['russian']}\n"
        text += f"  _💡 {phrase['context']}_\n"
        
        if 'examples' in phrase and phrase['examples']:
            text += f"  📝 {phrase['examples'][0]}\n"
        
        text += "\n"
    
    text += "💡 *Совет:* Произносите фразы вслух для лучшего запоминания!"
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_phrases_keyboard()
    )

async def grammar_handler(query, tense):
    if tense not in bot_data.grammar:
        await query.edit_message_text(
            text="❌ Раздел грамматики не найден",
            reply_markup=get_grammar_keyboard()
        )
        return
    
    grammar_data = bot_data.grammar[tense]
    text = f"""
📖 *{grammar_data['name']}* ({grammar_data['russian_name']})

🎯 *Использование:* {grammar_data['usage']}

🏗️ *Формула:* `{grammar_data['structure']}`

📝 *Примеры:*
"""
    for example in grammar_data['examples']:
        text += f"• {example}\n"
    
    text += f"\n🔍 *Слова-маркеры:* {', '.join(grammar_data['signal_words'])}"
    
    if 'exercises' in grammar_data:
        text += f"\n\n💪 *Упражнения:*\n"
        for i, exercise in enumerate(grammar_data['exercises'], 1):
            text += f"{i}. {exercise['question']}\n"
            text += f"   Ответ: ||{exercise['answer']}||\n\n"
    
    text += "\n💡 *Практика:* Составьте свои предложения в этом времени!"
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_grammar_keyboard()
    )

# --- КОМАНДЫ ДЛЯ ВВОДА ТЕКСТА ---
async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Введите слово после команды: `/word hello`",
            parse_mode='Markdown',
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    word = context.args[0].lower()
    await send_word_info(update, word)

async def verb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Введите глагол после команды: `/verb go`",
            parse_mode='Markdown',
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    verb = context.args[0].lower()
    await send_word_info(update, verb)

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await random_word_handler(update)

async def send_word_info(update, word):
    info, word_type = bot_data.search_word(word)
    
    if not info:
        await update.message.reply_text(
            f"❌ Слово *{word}* не найдено в базе данных\n\nПопробуйте:\n• Проверить написание\n• Использовать другое слово\n• Посмотреть доступные глаголы через меню",
            parse_mode='Markdown',
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    text = f"""
🔍 *Результат поиска:*

📖 *{'Глагол' if word_type == 'verb' else 'Слово'}:* {word}
📝 *Транскрипция:* {info['phonetic']}
🇷🇺 *Перевод:* {info['translation']}
🎯 *Уровень:* {info.get('level', 'A1')}
"""
    
    if word_type == 'verb':
        text += f"📊 *Формы глагола:*\n"
        text += f"• Past Simple: {info['past']}\n"
        text += f"• Past Participle: {info['participle']}\n\n"
    
    text += f"💡 *Пример:* {info['examples'][0]}\n\n"
    text += "💪 *Практика:* Составьте своё предложение!"
    
    await update.message.reply_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )

# --- ОСНОВНАЯ ФУНКЦИЯ ---
def main():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден! Установите в переменных окружения Railway.")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("word", word_command))
    application.add_handler(CommandHandler("verb", verb_command))
    application.add_handler(CommandHandler("random", random_command))
    
    # Обработчики callback
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Запуск
    if os.getenv('RAILWAY_ENVIRONMENT'):
        # На Railway
        PORT = int(os.getenv('PORT', 8443))
        logger.info(f"Starting bot on Railway, port: {PORT}")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"https://{os.getenv('RAILWAY_STATIC_URL', '')}/{BOT_TOKEN}"
        )
    else:
        # Локально
        logger.info("Starting bot in polling mode locally...")
        application.run_polling()

if __name__ == '__main__':
    main()
