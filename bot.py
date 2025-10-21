import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# --- ДАННЫЕ ---

# Неправильные глаголы
IRREGULAR_VERBS = [
    {"infinitive": "be", "past": "was/were", "participle": "been", "translation": "быть", "level": "A1"},
    {"infinitive": "have", "past": "had", "participle": "had", "translation": "иметь", "level": "A1"},
    {"infinitive": "do", "past": "did", "participle": "done", "translation": "делать", "level": "A1"},
    {"infinitive": "go", "past": "went", "participle": "gone", "translation": "идти", "level": "A1"},
    {"infinitive": "see", "past": "saw", "participle": "seen", "translation": "видеть", "level": "A1"},
    {"infinitive": "come", "past": "came", "participle": "come", "translation": "приходить", "level": "A1"},
    {"infinitive": "get", "past": "got", "participle": "got/gotten", "translation": "получать", "level": "A1"},
    {"infinitive": "give", "past": "gave", "participle": "given", "translation": "давать", "level": "A1"},
    {"infinitive": "take", "past": "took", "participle": "taken", "translation": "брать", "level": "A1"},
    {"infinitive": "make", "past": "made", "participle": "made", "translation": "делать", "level": "A1"},
]

# Основные глаголы
BASIC_VERBS = [
    {"english": "like", "russian": "нравиться", "example": "I like coffee"},
    {"english": "want", "russian": "хотеть", "example": "I want water"},
    {"english": "need", "russian": "нуждаться", "example": "I need help"},
    {"english": "can", "russian": "мочь", "example": "I can swim"},
    {"english": "know", "russian": "знать", "example": "I know this"},
    {"english": "think", "russian": "думать", "example": "I think so"},
    {"english": "say", "russian": "говорить", "example": "I say hello"},
    {"english": "see", "russian": "видеть", "example": "I see you"},
    {"english": "come", "russian": "приходить", "example": "I come home"},
    {"english": "look", "russian": "смотреть", "example": "Look at me"},
]

# Времена
TENSES = {
    "present_simple": {
        "name": "Present Simple",
        "russian_name": "Настоящее Простое",
        "usage": "Постоянные действия, привычки, факты",
        "structure": "Subject + V1/V1+s",
        "examples": [
            "I work every day - Я работаю каждый день",
            "He works in an office - Он работает в офисе",
            "We like music - Нам нравится музыка"
        ],
        "signal_words": ["always", "usually", "often", "every day", "sometimes"]
    },
    "present_continuous": {
        "name": "Present Continuous",
        "russian_name": "Настоящее Длительное",
        "usage": "Действия в момент речи, временные ситуации",
        "structure": "Subject + am/is/are + V-ing",
        "examples": [
            "I am reading now - Я сейчас читаю",
            "She is watching TV - Она смотрит телевизор",
            "They are playing football - Они играют в футбол"
        ],
        "signal_words": ["now", "at the moment", "currently", "today"]
    },
    "past_simple": {
        "name": "Past Simple",
        "russian_name": "Прошедшее Простое",
        "usage": "Завершенные действия в прошлом",
        "structure": "Subject + V2",
        "examples": [
            "I worked yesterday - Я работал вчера",
            "She went to school - Она ходила в школу",
            "We saw a movie - Мы смотрели фильм"
        ],
        "signal_words": ["yesterday", "last week", "ago", "in 2020"]
    },
    "future_simple": {
        "name": "Future Simple",
        "russian_name": "Будущее Простое",
        "usage": "Спонтанные решения, предсказания, обещания",
        "structure": "Subject + will + V1",
        "examples": [
            "I will help you - Я помогу тебе",
            "It will rain tomorrow - Завтра будет дождь",
            "We will travel - Мы будем путешествовать"
        ],
        "signal_words": ["tomorrow", "next week", "soon", "in the future"]
    }
}

# Фразы
PHRASES = {
    "greetings": {
        "name": "👋 Приветствия",
        "phrases": [
            {"english": "Hello! / Hi!", "russian": "Привет!", "context": "Неформальное приветствие"},
            {"english": "Good morning!", "russian": "Доброе утро!", "context": "До 12:00"},
            {"english": "How are you?", "russian": "Как дела?", "context": "Стандартный вопрос"},
            {"english": "I'm fine, thank you!", "russian": "Хорошо, спасибо!", "context": "Позитивный ответ"},
        ]
    },
    "introduction": {
        "name": "🤝 Знакомство",
        "phrases": [
            {"english": "What is your name?", "russian": "Как тебя зовут?", "context": "Спросить имя"},
            {"english": "My name is...", "russian": "Меня зовут...", "context": "Назвать свое имя"},
            {"english": "Where are you from?", "russian": "Откуда ты?", "context": "Спросить откуда"},
            {"english": "I'm from Russia", "russian": "Я из России", "context": "Ответить откуда"},
        ]
    },
    "cafe": {
        "name": "☕ В кафе",
        "phrases": [
            {"english": "Can I have a coffee?", "russian": "Можно мне кофе?", "context": "Заказ напитка"},
            {"english": "How much is it?", "russian": "Сколько это стоит?", "context": "Узнать цену"},
            {"english": "Thank you!", "russian": "Спасибо!", "context": "Поблагодарить"},
        ]
    }
}

# --- КЛАВИАТУРЫ ---

def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📚 Времена", callback_data="menu_tenses")],
        [InlineKeyboardButton("🔤 Глаголы", callback_data="menu_verbs")],
        [InlineKeyboardButton("💬 Разговорные фразы", callback_data="menu_phrases")],
        [InlineKeyboardButton("🎴 Карточки для запоминания", callback_data="menu_flashcards")],
        [InlineKeyboardButton("ℹ️ О боте", callback_data="menu_about")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_tenses_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Present Simple", callback_data="tense_present_simple")],
        [InlineKeyboardButton("Present Continuous", callback_data="tense_present_continuous")],
        [InlineKeyboardButton("Past Simple", callback_data="tense_past_simple")],
        [InlineKeyboardButton("Future Simple", callback_data="tense_future_simple")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_verbs_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📖 Неправильные глаголы", callback_data="verbs_irregular")],
        [InlineKeyboardButton("🔠 Основные глаголы", callback_data="verbs_basic")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_phrases_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("👋 Приветствия", callback_data="phrases_greetings")],
        [InlineKeyboardButton("🤝 Знакомство", callback_data="phrases_introduction")],
        [InlineKeyboardButton("☕ В кафе", callback_data="phrases_cafe")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# --- ОБРАБОТЧИКИ КОМАНД ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🇬🇧 *Добро пожаловать в English Helper Bot!* 🇺🇸

Это ваш личный блокнот для изучения английского языка!

✨ *Что умеет этот бот:*
• 📚 Объясняет английские времена
• 🔤 Учит неправильные и основные глаголы
• 💬 Дает полезные разговорные фразы
• 🎴 Помогает запоминать слова с карточками

Выберите раздел для начала обучения:
    """
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 *Как пользоваться ботом:*

1. Используйте кнопки меню для навигации
2. Выбирайте интересующие вас темы
3. Регулярно повторяйте материал
4. Используйте карточки для запоминания

*Удачи в изучении английского!* 🚀
    """
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )

# --- ОБРАБОТЧИКИ CALLBACK ---

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
        return await send_flashcard(update, context)
    
    elif callback_data == "menu_about":
        text = """
ℹ️ *О боте English Helper*

Этот бот создан чтобы помочь вам в изучении английского языка с нуля!

📊 *Доступные материалы:*
• 4 основных времени английского
• 10+ неправильных глаголов
• 10+ основных глаголов
• 10+ разговорных фраз

🎯 *Уровень:* Начальный (A1)

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

async def handle_verbs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "verbs_irregular":
        verbs_text = "📖 *Неправильные глаголы:*\n\n"
        
        for verb in IRREGULAR_VERBS:
            verbs_text += f"*{verb['infinitive']}* - {verb['past']} - {verb['participle']}\n"
            verbs_text += f"🇷🇺 {verb['translation']} | 🎯 {verb['level']}\n\n"
        
        verbs_text += "💡 *Совет:* Учите по 5 глаголов в день!"
        
        await query.edit_message_text(
            text=verbs_text,
            parse_mode='Markdown',
            reply_markup=get_verbs_menu_keyboard()
        )
    
    elif query.data == "verbs_basic":
        verbs_text = "🔠 *Основные глаголы для начинающих:*\n\n"
        
        for verb in BASIC_VERBS:
            verbs_text += f"*{verb['english']}* - {verb['russian']}\n"
            verbs_text += f"   _Пример: {verb['example']}_\n\n"
        
        await query.edit_message_text(
            text=verbs_text,
            parse_mode='Markdown',
            reply_markup=get_verbs_menu_keyboard()
        )

async def handle_phrases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    category_key = query.data.replace("phrases_", "")
    
    if category_key in PHRASES:
        category = PHRASES[category_key]
        
        text = f"*{category['name']}*\n\n"
        
        for phrase in category['phrases']:
            text += f"💬 *{phrase['english']}*\n"
            text += f"🇷🇺 {phrase['russian']}\n"
            text += f"_💡 {phrase['context']}_\n\n"
        
        text += "💡 *Совет:* Произносите фразы вслух для лучшего запоминания!"
        
        await query.edit_message_text(
            text=text,
            parse_mode='Markdown',
            reply_markup=get_phrases_menu_keyboard()
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

*Пример:*
_I {verb['infinitive']} here every day._
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

# --- ОСНОВНАЯ ФУНКЦИЯ ---

def main():
    # Получение токена
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден! Убедитесь, что он установлен в переменных окружения Railway.")
    
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("flashcard", send_flashcard))
    
    # Обработчики callback
    application.add_handler(CallbackQueryHandler(handle_main_menu, pattern="^(back_to_main|menu_)"))
    application.add_handler(CallbackQueryHandler(handle_tenses, pattern="^tense_"))
    application.add_handler(CallbackQueryHandler(handle_verbs, pattern="^verbs_"))
    application.add_handler(CallbackQueryHandler(handle_phrases, pattern="^phrases_"))
    application.add_handler(CallbackQueryHandler(send_flashcard, pattern="^menu_flashcards"))
    
    # Запуск бота
    if os.getenv('RAILWAY_ENVIRONMENT'):
        # На Railway
        PORT = int(os.getenv('PORT', 8443))
        WEBHOOK_URL = os.getenv('WEBHOOK_URL')
        
        if WEBHOOK_URL:
            # Используем вебхук если есть URL
            application.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=BOT_TOKEN,
                webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
            )
        else:
            # Иначе поллинг (для Railway тоже работает)
            logger.info("Запуск бота в режиме поллинга на Railway...")
            application.run_polling()
    else:
        # Локально
        logger.info("Запуск бота в режиме поллинга локально...")
        application.run_polling()

if __name__ == '__main__':
    main()
