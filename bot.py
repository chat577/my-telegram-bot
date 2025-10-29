import os
import logging
import random
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

class EnglishDictionary:
    def __init__(self):
        self.verbs_db = {
            'be': {'phonetic': '/biː/', 'translation': 'быть', 'past': 'was/were', 'participle': 'been', 'examples': ['I am happy', 'They are students']},
            'have': {'phonetic': '/hæv/', 'translation': 'иметь', 'past': 'had', 'participle': 'had', 'examples': ['I have a car', 'She has a book']},
            'do': {'phonetic': '/duː/', 'translation': 'делать', 'past': 'did', 'participle': 'done', 'examples': ['I do homework', 'What do you do?']},
            'say': {'phonetic': '/seɪ/', 'translation': 'говорить', 'past': 'said', 'participle': 'said', 'examples': ['I say hello', 'She says goodbye']},
            'get': {'phonetic': '/ɡet/', 'translation': 'получать', 'past': 'got', 'participle': 'got/gotten', 'examples': ['I get up early', 'Get a job']},
            'make': {'phonetic': '/meɪk/', 'translation': 'делать', 'past': 'made', 'participle': 'made', 'examples': ['Make a cake', 'Make money']},
            'go': {'phonetic': '/ɡoʊ/', 'translation': 'идти', 'past': 'went', 'participle': 'gone', 'examples': ['Go to school', 'Go home']},
            'know': {'phonetic': '/noʊ/', 'translation': 'знать', 'past': 'knew', 'participle': 'known', 'examples': ['I know him', 'Do you know?']},
            'take': {'phonetic': '/teɪk/', 'translation': 'брать', 'past': 'took', 'participle': 'taken', 'examples': ['Take a book', 'Take a break']},
            'see': {'phonetic': '/siː/', 'translation': 'видеть', 'past': 'saw', 'participle': 'seen', 'examples': ['I see you', 'See a movie']},
            'come': {'phonetic': '/kʌm/', 'translation': 'приходить', 'past': 'came', 'participle': 'come', 'examples': ['Come here', 'Come tomorrow']},
            'think': {'phonetic': '/θɪŋk/', 'translation': 'думать', 'past': 'thought', 'participle': 'thought', 'examples': ['I think so', 'Think about it']},
            'look': {'phonetic': '/lʊk/', 'translation': 'смотреть', 'past': 'looked', 'participle': 'looked', 'examples': ['Look at me', 'Look for keys']},
            'want': {'phonetic': '/wɒnt/', 'translation': 'хотеть', 'past': 'wanted', 'participle': 'wanted', 'examples': ['I want water', 'Want to go?']},
            'give': {'phonetic': '/ɡɪv/', 'translation': 'давать', 'past': 'gave', 'participle': 'given', 'examples': ['Give me money', 'Give a present']},
            'find': {'phonetic': '/faɪnd/', 'translation': 'находить', 'past': 'found', 'participle': 'found', 'examples': ['Find a job', 'Find keys']},
            'tell': {'phonetic': '/tel/', 'translation': 'рассказывать', 'past': 'told', 'participle': 'told', 'examples': ['Tell a story', 'Tell me']},
            'work': {'phonetic': '/wɜːrk/', 'translation': 'работать', 'past': 'worked', 'participle': 'worked', 'examples': ['Work hard', 'Work from home']},
        }
        
        self.words_db = {
            'hello': {'phonetic': '/həˈloʊ/', 'translation': 'привет', 'examples': ['Hello! How are you?']},
            'time': {'phonetic': '/taɪm/', 'translation': 'время', 'examples': ['What time is it?']},
            'people': {'phonetic': '/ˈpiːpəl/', 'translation': 'люди', 'examples': ['Many people think...']},
            'water': {'phonetic': '/ˈwɔːtər/', 'translation': 'вода', 'examples': ['I drink water']},
            'food': {'phonetic': '/fuːd/', 'translation': 'еда', 'examples': ['I like Chinese food']},
            'house': {'phonetic': '/haʊs/', 'translation': 'дом', 'examples': ['My house is big']},
            'city': {'phonetic': '/ˈsɪti/', 'translation': 'город', 'examples': ['I live in a big city']},
            'book': {'phonetic': '/bʊk/', 'translation': 'книга', 'examples': ['Read a book']},
            'friend': {'phonetic': '/frend/', 'translation': 'друг', 'examples': ['My best friend']},
        }

    async def get_word_info(self, word):
        """Получает информацию о слове из локальной базы или API"""
        word = word.lower()
        
        # Сначала проверяем локальную базу
        if word in self.verbs_db:
            info = self.verbs_db[word].copy()
            info['type'] = 'verb'
            info['word'] = word
            return info
        elif word in self.words_db:
            info = self.words_db[word].copy()
            info['type'] = 'word'
            info['word'] = word
            return info
        
        # Если нет в локальной базе, пробуем API
        return await self._get_from_api(word)
    
    async def _get_from_api(self, word):
        """Пробует получить информацию из Free Dictionary API"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
                response = await client.get(url, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_api_response(word, data)
        except Exception as e:
            logger.error(f"API error for {word}: {e}")
        
        # Если API не сработал, возвращаем базовую информацию
        return self._get_basic_info(word)
    
    def _parse_api_response(self, word, data):
        """Парсит ответ от Dictionary API"""
        if not data:
            return None
        
        word_data = data[0]
        result = {
            'word': word,
            'phonetic': '',
            'translation': '',
            'examples': [],
            'type': 'word',
            'source': 'Dictionary API'
        }
        
        # Получаем транскрипцию
        if 'phonetic' in word_data:
            result['phonetic'] = word_data['phonetic']
        elif 'phonetics' in word_data and word_data['phonetics']:
            for phonetics in word_data['phonetics']:
                if 'text' in phonetics:
                    result['phonetic'] = phonetics['text']
                    break
        
        # Получаем первое значение
        if 'meanings' in word_data and word_data['meanings']:
            first_meaning = word_data['meanings'][0]
            if 'definitions' in first_meaning and first_meaning['definitions']:
                first_def = first_meaning['definitions'][0]
                result['translation'] = first_def.get('definition', '')[:100] + '...'
                if 'example' in first_def:
                    result['examples'].append(first_def['example'])
        
        return result
    
    def _get_basic_info(self, word):
        """Возвращает базовую информацию о слове"""
        return {
            'word': word,
            'phonetic': '/транскрипция/',
            'translation': 'перевод',
            'examples': [f'I {word} every day' if word in self.verbs_db else f'This is {word}'],
            'type': 'verb' if word in self.verbs_db else 'word',
            'source': 'Local database'
        }

# Создаем экземпляр словаря
dictionary = EnglishDictionary()

# --- КЛАВИАТУРЫ ---
def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔤 Поиск слова", callback_data="search_word")],
        [InlineKeyboardButton("📚 Популярные глаголы", callback_data="popular_verbs")],
        [InlineKeyboardButton("💬 Разговорные фразы", callback_data="common_phrases")],
        [InlineKeyboardButton("📖 Грамматика", callback_data="grammar")],
        [InlineKeyboardButton("🎯 Случайное слово", callback_data="random_word")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_verbs_keyboard():
    keyboard = [
        [InlineKeyboardButton("be", callback_data="verb_be"), InlineKeyboardButton("have", callback_data="verb_have")],
        [InlineKeyboardButton("do", callback_data="verb_do"), InlineKeyboardButton("go", callback_data="verb_go")],
        [InlineKeyboardButton("see", callback_data="verb_see"), InlineKeyboardButton("say", callback_data="verb_say")],
        [InlineKeyboardButton("get", callback_data="verb_get"), InlineKeyboardButton("make", callback_data="verb_make")],
        [InlineKeyboardButton("📚 Все глаголы", callback_data="all_verbs")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
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
        [InlineKeyboardButton("📝 Present Simple", callback_data="grammar_present")],
        [InlineKeyboardButton("⏳ Past Simple", callback_data="grammar_past")],
        [InlineKeyboardButton("🔮 Future Simple", callback_data="grammar_future")],
        [InlineKeyboardButton("🔄 Времена сравнение", callback_data="grammar_comparison")],
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

🎯 *Уровень:* Начальный (A1-A2)

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
    
    elif callback_data == "popular_verbs":
        await popular_verbs_handler(query)
    
    elif callback_data == "common_phrases":
        await common_phrases_handler(query)
    
    elif callback_data == "random_word":
        await random_word_handler(query)
    
    elif callback_data == "grammar":
        await grammar_handler(query)
    
    elif callback_data == "help":
        await help_handler(query)
    
    elif callback_data.startswith("verb_"):
        verb = callback_data.replace("verb_", "")
        await word_detail_handler(query, verb)
    
    elif callback_data == "all_verbs":
        await all_verbs_handler(query)
    
    elif callback_data.startswith("phrases_"):
        await phrases_handler(query, callback_data.replace("phrases_", ""))
    
    elif callback_data.startswith("grammar_"):
        await grammar_detail_handler(query, callback_data.replace("grammar_", ""))

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

*Или выберите из популярных:*
    """
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_verbs_keyboard()
    )

async def popular_verbs_handler(query):
    text = """
📚 *Популярные английские глаголы*

Выберите глагол для подробной информации:

*Топ-10 самых используемых глаголов:*
1. *be* - быть
2. *have* - иметь  
3. *do* - делать
4. *say* - говорить
5. *get* - получать
6. *make* - делать
7. *go* - идти
8. *know* - знать
9. *take* - брать
10. *see* - видеть

💡 *Совет:* Эти глаголы покрывают 50% всей английской речи!
    """
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_verbs_keyboard()
    )

async def all_verbs_handler(query):
    verbs = dictionary.verbs_db
    text = "📚 *Все глаголы в базе:*\n\n"
    
    for i, (verb, info) in enumerate(verbs.items(), 1):
        text += f"{i}. *{verb}* - {info['translation']}\n"
        text += f"   Формы: {info['past']} - {info['participle']}\n\n"
    
    text += "💡 Нажмите на глагол для подробной информации"
    
    # Создаем кнопки для всех глаголов
    keyboard = []
    verbs_list = list(verbs.keys())
    
    # Группируем по 2 глагола в строке
    for i in range(0, len(verbs_list), 2):
        row = []
        if i < len(verbs_list):
            row.append(InlineKeyboardButton(verbs_list[i], callback_data=f"verb_{verbs_list[i]}"))
        if i + 1 < len(verbs_list):
            row.append(InlineKeyboardButton(verbs_list[i + 1], callback_data=f"verb_{verbs_list[i + 1]}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="popular_verbs")])
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def common_phrases_handler(query):
    text = """
💬 *Разговорные фразы*

Выберите категорию полезных фраз для повседневного общения:

*Доступные категории:*
• 👋 Приветствия и прощания
• 🤝 Знакомство
• ☕ В кафе и ресторане  
• ❓ Основные вопросы

💡 *Практикуйте фразы вслух!*
    """
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_phrases_keyboard()
    )

async def random_word_handler(query):
    # Объединяем слова и глаголы
    all_words = {**dictionary.words_db, **dictionary.verbs_db}
    word = random.choice(list(all_words.keys()))
    
    word_info = all_words[word]
    
    text = f"""
🎯 *Случайное слово для изучения!*

📖 *Слово:* {word}
📝 *Транскрипция:* {word_info['phonetic']}
🇷🇺 *Перевод:* {word_info['translation']}

"""
    
    if 'past' in word_info:
        text += f"📊 *Формы глагола:*\n"
        text += f"• Past Simple: {word_info['past']}\n"
        text += f"• Past Participle: {word_info['participle']}\n\n"
    
    text += f"💡 *Пример:* {word_info['examples'][0]}\n\n"
    text += "*Практика:* Составьте своё предложение с этим словом!"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Новое слово", callback_data="random_word")],
        [InlineKeyboardButton("🔍 Подробнее", callback_data=f"verb_{word}" if word in dictionary.verbs_db else f"word_{word}")],
        [InlineKeyboardButton("◀️ В меню", callback_data="back_to_main")],
    ]
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def grammar_handler(query):
    text = """
📖 *Грамматика английского языка*

Выберите раздел для изучения:

*Доступные темы:*
• 📝 Present Simple - настоящее время
• ⏳ Past Simple - прошедшее время  
• 🔮 Future Simple - будущее время
• 🔄 Сравнение времен

💡 *Каждая тема включает:*
- Правила образования
- Примеры предложений
- Слова-маркеры
- Упражнения для практики
    """
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_grammar_keyboard()
    )

async def help_handler(query):
    text = """
ℹ️ *Помощь по использованию бота*

*Основные функции:*
🔤 *Поиск слов* - транскрипция, перевод, примеры
📚 *Глаголы* - формы, использование, примеры
💬 *Фразы* - разговорные выражения по темам
📖 *Грамматика* - правила и упражнения

*Команды:*
/start - главное меню
/help - помощь
/word <слово> - найти слово
/verb <глагол> - найти глагол
/random - случайное слово

💡 *Для лучшего результата:*
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

async def word_detail_handler(query, word):
    # Показываем загрузку
    await query.edit_message_text(
        text=f"🔍 Ищу информацию о слове *{word}*...",
        parse_mode='Markdown'
    )
    
    # Получаем информацию о слове
    word_info = await dictionary.get_word_info(word)
    
    if word_info:
        text = f"""
🔤 *Слово:* {word_info['word']}

📝 *Транскрипция:* {word_info.get('phonetic', '/транскрипция/')}
🇷🇺 *Перевод:* {word_info.get('translation', 'перевод')}
"""
        
        # Добавляем формы для глаголов
        if word_info.get('type') == 'verb' and 'past' in word_info:
            text += f"\n📊 *Формы глагола:*\n"
            text += f"• Past Simple: {word_info['past']}\n"
            text += f"• Past Participle: {word_info['participle']}\n"
        
        # Добавляем примеры
        text += f"\n💡 *Примеры использования:*\n"
        for example in word_info.get('examples', []):
            text += f"• {example}\n"
        
        text += f"\n📚 *Источник:* {word_info.get('source', 'База данных')}\n\n"
        text += "🎯 *Практика:* Составьте 2-3 предложения с этим словом!"
    
    else:
        text = f"""
🔤 *Слово:* {word}

⚠️ *Информация не найдена*

💡 *Попробуйте:*
• Проверить написание слова
• Использовать базовую форму (для глаголов)
• Воспользоваться другим словом

*Пример использования:* I {word} every day.
        """
    
    keyboard = [
        [InlineKeyboardButton("🔍 Другое слово", callback_data="search_word")],
        [InlineKeyboardButton("🎯 Случайное слово", callback_data="random_word")],
        [InlineKeyboardButton("📚 Все глаголы", callback_data="all_verbs")],
        [InlineKeyboardButton("◀️ В меню", callback_data="back_to_main")],
    ]
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def phrases_handler(query, category):
    phrases_db = {
        "greetings": [
            {"english": "Hello! / Hi!", "russian": "Привет!", "context": "Неформальное приветствие"},
            {"english": "Good morning!", "russian": "Доброе утро!", "context": "До 12:00"},
            {"english": "Good afternoon!", "russian": "Добрый день!", "context": "12:00-18:00"},
            {"english": "Good evening!", "russian": "Добрый вечер!", "context": "После 18:00"},
            {"english": "How are you?", "russian": "Как дела?", "context": "Стандартный вопрос"},
            {"english": "I'm fine, thanks!", "russian": "Хорошо, спасибо!", "context": "Позитивный ответ"},
            {"english": "What's up?", "russian": "Как дела? (неформ.)", "context": "Неформальный вопрос"},
        ],
        "introduction": [
            {"english": "What's your name?", "russian": "Как тебя зовут?", "context": "Спросить имя"},
            {"english": "My name is...", "russian": "Меня зовут...", "context": "Представиться"},
            {"english": "Where are you from?", "russian": "Откуда ты?", "context": "Спросить откуда"},
            {"english": "I'm from Russia", "russian": "Я из России", "context": "Ответить откуда"},
            {"english": "Nice to meet you!", "russian": "Приятно познакомиться!", "context": "После знакомства"},
            {"english": "How old are you?", "russian": "Сколько тебе лет?", "context": "Спросить возраст"},
        ],
        "cafe": [
            {"english": "Can I have a coffee?", "russian": "Можно мне кофе?", "context": "Заказ напитка"},
            {"english": "I would like tea", "russian": "Я бы хотел(а) чай", "context": "Вежливый заказ"},
            {"english": "What do you recommend?", "russian": "Что вы посоветуете?", "context": "Спросить рекомендацию"},
            {"english": "How much is it?", "russian": "Сколько это стоит?", "context": "Узнать цену"},
            {"english": "The bill, please", "russian": "Счет, пожалуйста", "context": "Попросить счет"},
            {"english": "It's delicious!", "russian": "Это очень вкусно!", "context": "Похвалить еду"},
        ],
        "questions": [
            {"english": "What is this?", "russian": "Что это?", "context": "Спросить о предмете"},
            {"english": "Where is...?", "russian": "Где...?", "context": "Спросить о месте"},
            {"english": "When...?", "russian": "Когда...?", "context": "Спросить о времени"},
            {"english": "Why...?", "russian": "Почему...?", "context": "Спросить причину"},
            {"english": "How...?", "russian": "Как...?", "context": "Спросить способ"},
            {"english": "Can you help me?", "russian": "Можете помочь мне?", "context": "Попросить помощи"},
        ]
    }
    
    category_names = {
        "greetings": "👋 Приветствия и прощания",
        "introduction": "🤝 Знакомство", 
        "cafe": "☕ В кафе и ресторане",
        "questions": "❓ Основные вопросы"
    }
    
    phrases = phrases_db.get(category, [])
    category_name = category_names.get(category, category)
    
    text = f"💬 *{category_name}*\n\n"
    
    for phrase in phrases:
        text += f"• *{phrase['english']}*\n"
        text += f"  🇷🇺 {phrase['russian']}\n"
        text += f"  _💡 {phrase['context']}_\n\n"
    
    text += "💡 *Совет:* Произносите фразы вслух для лучшего запоминания!"
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_phrases_keyboard()
    )

async def grammar_detail_handler(query, topic):
    grammar_db = {
        "present": {
            "title": "📝 Present Simple",
            "content": """
*Present Simple* (Настоящее Простое)

🎯 *Использование:*
• Регулярные действия и привычки
• Факты и общие истины
• Расписания и программы

🏗️ *Формула:*
• I/you/we/they + V1
• he/she/it + V1 + s

📝 *Примеры:*
• I work every day - Я работаю каждый день
• He works in an office - Он работает в офисе
• The sun rises in the east - Солнце встает на востоке

🔍 *Слова-маркеры:*
always, usually, often, every day, sometimes, never
            """
        },
        "past": {
            "title": "⏳ Past Simple", 
            "content": """
*Past Simple* (Прошедшее Простое)

🎯 *Использование:*
• Завершенные действия в прошлом
• Последовательные события
• Факты из прошлого

🏗️ *Формула:*
• Subject + V2 (правильные: V+ed)

📝 *Примеры:*
• I worked yesterday - Я работал вчера
• She went to school - Она ходила в школу
• We saw a movie - Мы смотрели фильм

🔍 *Слова-маркеры:*
yesterday, last week, ago, in 2020, then
            """
        },
        "future": {
            "title": "🔮 Future Simple",
            "content": """
*Future Simple* (Будущее Простое)

🎯 *Использование:*
• Спонтанные решения
• Предсказания и обещания
• Будущие факты

🏗️ *Формула:*
• Subject + will + V1

📝 *Примеры:*
• I will help you - Я помогу тебе
• It will rain tomorrow - Завтра будет дождь
• She will be 25 - Ей будет 25 лет

🔍 *Слова-маркеры:*
tomorrow, next week, soon, in the future
            """
        },
        "comparison": {
            "title": "🔄 Сравнение времен",
            "content": """
*Сравнение основных времен:*

🟢 *Present Simple*
I work every day - Постоянное действие

🔵 *Past Simple*  
I worked yesterday - Завершенное действие в прошлом

🟣 *Future Simple*
I will work tomorrow - Действие в будущем

💡 *Упражнение:*
Переведите на английский:
1. Я читаю книгу каждый день
2. Вчера я смотрел фильм
3. Завтра я пойду в парк

*Ответы:*
1. I read a book every day
2. Yesterday I watched a movie  
3. Tomorrow I will go to the park
            """
        }
    }
    
    topic_info = grammar_db.get(topic, {})
    
    if topic_info:
        text = topic_info['content']
    else:
        text = "Информация по данной теме временно недоступна."
    
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
    # Показываем что ищем
    message = await update.message.reply_text(f"🔍 Ищу информацию о слове *{word}*...", parse_mode='Markdown')
    
    # Получаем информацию
    word_info = await dictionary.get_word_info(word)
    
    if word_info:
        text = f"""
🔍 *Результат поиска:*

📖 *Слово:* {word_info['word']}
📝 *Транскрипция:* {word_info.get('phonetic', '/транскрипция/')}
🇷🇺 *Перевод:* {word_info.get('translation', 'перевод')}
"""
        
        if word_info.get('type') == 'verb' and 'past' in word_info:
            text += f"📊 *Формы глагола:*\n"
            text += f"• Past Simple: {word_info['past']}\n"
            text += f"• Past Participle: {word_info['participle']}\n\n"
        
        text += f"💡 *Пример:* {word_info.get('examples', [''])[0]}\n\n"
        text += f"📚 *Источник:* {word_info.get('source', 'База данных')}"
    
    else:
        text = f"""
🔍 *Слово:* {word}

⚠️ *Информация не найдена*

💡 *Попробуйте:*
• Проверить написание
• Использовать другое слово
• Обратиться к меню глаголов

*Пример использования:* I {word} every day.
        """
    
    await message.edit_text(text, parse_mode='Markdown', reply_markup=get_main_menu_keyboard())

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
