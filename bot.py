import os
import logging
import random
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv('BOT_TOKEN')

# БАЗЫ ДАННЫХ НА РУССКОМ
RUSSIAN_FACTS = [
    "🎲 Коты могут поворачивать уши на 180 градусов!",
    "🎲 Осьминоги имеют три сердца и голубую кровь!",
    "🎲 Мед никогда не портится - археологи находили съедобный мед возрастом 3000 лет!",
    "🎲 Земля - единственная планета, не названная в честь бога!",
    "🎲 Сердце кита бьется всего 9 раз в минуту!",
    "🎲 Змеи могут спать до 3 лет без еды!",
    "🎲 Страусы могут бегать быстрее лошадей!",
    "🎲 Бабочки пробуют еду лапками!"
]

RUSSIAN_JOKES = [
    "😂 Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 == Dec 25!",
    "😂 Как называется бабочка-программист? Мотылек!",
    "😂 Почему Python не нужна одежда? Потому что у него есть классы!",
    "😂 Что сказал один сервер другому? У меня RAM'а не хватает...",
    "😂 Почему математик не любит природу? Слишком много переменных!",
    "😂 Что программист сказал перед смертью? Hello world!",
    "😂 Почему компьютер никогда не болеет? У него хороший иммунитет!"
]

RUSSIAN_ADVICES = [
    "🌟 Начни свой день с улыбки!",
    "🌟 Не откладывай на завтра то, что можно сделать сегодня.",
    "🌟 Помни: каждый эксперт когда-то был новичком.",
    "🌟 Учись на ошибках - они лучшие учителя!",
    "🌟 Не сравнивай себя с другими - сравнивай с собой вчерашним.",
    "🌟 Маленькие шаги каждый день приводят к большим результатам.",
    "🌟 Отдых - это тоже часть продуктивности."
]

# БЕСПЛАТНЫЕ API
API_URLS = {
    "quote": "https://api.quotable.io/random",
}

# Клавиатуры
def get_main_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("🚀 Старт", callback_data="start_cmd")],
        [InlineKeyboardButton("🎲 Генератор", callback_data="generator_cmd")],
        [InlineKeyboardButton("📅 Ежедневный гороскоп", callback_data="horoscope_cmd")],
        [InlineKeyboardButton("🍽️ Случайный рецепт", callback_data="recipe_cmd")],
        [InlineKeyboardButton("🎬 Цитаты из фильмов", callback_data="movie_cmd")],
        [InlineKeyboardButton("🔢 Тест по дате рождения", callback_data="birthdate_cmd")],
        [InlineKeyboardButton("📞 Помощь", callback_data="help_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_generator_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎲 Случайный факт", callback_data="gen_fact")],
        [InlineKeyboardButton("😂 Случайная шутка", callback_data="gen_joke")],
        [InlineKeyboardButton("💡 Случайная идея", callback_data="gen_idea")],
        [InlineKeyboardButton("🌟 Случайный совет", callback_data="gen_advice")],
        [InlineKeyboardButton("📜 Случайная цитата", callback_data="gen_quote")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_fact_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎲 Еще факт", callback_data="gen_fact")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_joke_keyboard():
    keyboard = [
        [InlineKeyboardButton("😂 Еще шутку", callback_data="gen_joke")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_idea_keyboard():
    keyboard = [
        [InlineKeyboardButton("💡 Еще идею", callback_data="gen_idea")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_advice_keyboard():
    keyboard = [
        [InlineKeyboardButton("🌟 Еще совет", callback_data="gen_advice")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_quote_keyboard():
    keyboard = [
        [InlineKeyboardButton("📜 Еще цитату", callback_data="gen_quote")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_movie_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎬 Еще цитату из фильма", callback_data="movie_cmd")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_zodiac_keyboard():
    keyboard = [
        [InlineKeyboardButton("♈ Овен", callback_data="zodiac_aries")],
        [InlineKeyboardButton("♉ Телец", callback_data="zodiac_taurus")],
        [InlineKeyboardButton("♊ Близнецы", callback_data="zodiac_gemini")],
        [InlineKeyboardButton("♋ Рак", callback_data="zodiac_cancer")],
        [InlineKeyboardButton("♌ Лев", callback_data="zodiac_leo")],
        [InlineKeyboardButton("♍ Дева", callback_data="zodiac_virgo")],
        [InlineKeyboardButton("♎ Весы", callback_data="zodiac_libra")],
        [InlineKeyboardButton("♏ Скорпион", callback_data="zodiac_scorpio")],
        [InlineKeyboardButton("♐ Стрелец", callback_data="zodiac_sagittarius")],
        [InlineKeyboardButton("♑ Козерог", callback_data="zodiac_capricorn")],
        [InlineKeyboardButton("♒ Водолей", callback_data="zodiac_aquarius")],
        [InlineKeyboardButton("♓ Рыбы", callback_data="zodiac_pisces")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔙 Назад в меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Функции для получения данных
def get_daily_fact():
    return random.choice(RUSSIAN_FACTS)

def get_daily_joke():
    return random.choice(RUSSIAN_JOKES)

def get_daily_advice():
    return random.choice(RUSSIAN_ADVICES)

def get_daily_quote():
    try:
        response = requests.get(API_URLS["quote"])
        if response.status_code == 200:
            data = response.json()
            author_translations = {
                "Albert Einstein": "Альберт Эйнштейн",
                "Mahatma Gandhi": "Махатма Ганди", 
                "Confucius": "Конфуций",
                "Aristotle": "Аристотель",
                "Plato": "Платон",
                "Socrates": "Сократ",
                "Bruce Lee": "Брюс Ли",
                "Steve Jobs": "Стив Джобс",
                "Bill Gates": "Билл Гейтс",
                "Walt Disney": "Уолт Дисней"
            }
            author = author_translations.get(data['author'], data['author'])
            return f"📜 Цитата дня:\n\"{data['content']}\"\n— {author}"
    except:
        pass
    
    quotes = [
        "📜 Успех — это идти от неудачи к неудаче, не теряя энтузиазма. — Уинстон Черчилль",
        "📜 Лучший способ начать делать — перестать говорить и начать делать. — Уолт Дисней",
        "📜 Единственный способ делать великие дела — любить то, что ты делаешь. — Стив Джобс",
        "📜 Не ошибается тот, кто ничего не делает. Не бойтесь ошибаться. — Теодор Рузвельт",
        "📜 Будущее принадлежит тем, кто верит в красоту своей мечты. — Элеонора Рузвельт"
    ]
    return random.choice(quotes)

def get_daily_idea():
    ideas = [
        "💡 Сегодня отличный день чтобы начать изучать новый язык программирования!",
        "🚀 Попробуй создать свой первый Telegram бот - это проще чем кажется!",
        "🎨 Нарисуй что-то простое - даже если ты не художник, творчество полезно!",
        "📚 Прочитай главу из книги которую давно откладывал",
        "🏃 Сделай небольшую зарядку - тело скажет спасибо!",
        "✍️ Напиши 5 идей для проектов - одна из них может изменить всё!",
        "🌍 Изучи что-то новое о другой культуре или стране",
        "🎵 Создай плейлист для продуктивной работы"
    ]
    return random.choice(ideas)

def get_daily_horoscope(sign):
    today = datetime.now().strftime("%d%m")
    seed = hash(sign + today) % 100
    
    zodiac_names = {
        "aries": "Овна", "taurus": "Тельца", "gemini": "Близнецов",
        "cancer": "Рака", "leo": "Льва", "virgo": "Деву",
        "libra": "Весов", "scorpio": "Скорпиона", "sagittarius": "Стрельца",
        "capricorn": "Козерога", "aquarius": "Водолея", "pisces": "Рыб"
    }
    
    horoscope_templates = [
        f"♉ Для {zodiac_names[sign]} сегодня звезды благоволят вам! Идеальный день для новых начинаний и смелых решений.",
        f"♉ {zodiac_names[sign].capitalize()} сегодня: остерегайтесь необдуманных решений. Лучше отложить важные вопросы на завтра.",
        f"♉ Гороскоп для {zodiac_names[sign]}: день гармонии и баланса. Проведите время с близкими - это принесет душевный покой.",
        f"♉ {zodiac_names[sign].capitalize()} сегодня: энергия бьет ключом! Используйте этот день для активных действий и проектов.",
        f"♉ Для {zodiac_names[sign]} сегодня: время для самоанализа. Займитесь планированием и поставьте новые цели.",
        f"♉ {zodiac_names[sign].capitalize()} сегодня: удача на вашей стороне! Смело беритесь за то, что давно откладывали."
    ]
    
    return horoscope_templates[seed % len(horoscope_templates)]

def get_daily_recipe():
    recipes = [
        "🍳 **Простая яичница с помидорами:**\n2 яйца, 1 помидор, соль, перец. Помидор нарезать, обжарить 2 мин, добавить яйца, жарить до готовности. Вкусно и полезно!",
        "🥗 **Свежий салат:**\nОгурец, помидор, болгарский перец, лук. Нарезать кубиками, заправить оливковым маслом и лимонным соком.",
        "🍝 **Паста с чесноком:**\nСпагетти, 3 зубчика чеснока, оливковое масло, петрушка. Пасту отварить, чеснок обжарить, смешать с пастой.",
        "🍌 **Фруктовый смузи:**\nБанан, яблоко, йогурт, мед. Взбить в блендере - готово за 2 минуты!"
    ]
    return random.choice(recipes)

def get_movie_quote():
    quotes = [
        "🎬 **Властелин Колец:** 'Даже самый малый человек может изменить ход будущего.'",
        "🎬 **Форрест Гамп:** 'Жизнь как коробка шоколадных конфет: никогда не знаешь, какая начинка тебе попадётся.'",
        "🎬 **Звездные Войны:** 'Да пребудет с тобой Сила.'",
        "🎬 **Крестный отец:** 'Я сделаю ему предложение, от которого он не сможет отказаться.'",
        "🎬 **Титаник:** 'Я король мира!'",
        "🎬 **Матрица:** 'Знаешь, в чем разница между знанием и верой? Не знаешь? А я знаю.'"
    ]
    return random.choice(quotes)

def calculate_birth_number(day, month, year):
    total = sum(int(d) for d in str(day)) + sum(int(d) for d in str(month)) + sum(int(d) for d in str(year))
    
    while total > 9:
        total = sum(int(d) for d in str(total))
    
    meanings = {
        1: "**Лидер** - амбициозный, новатор, независимый",
        2: "**Дипломат** - чувствительный, интуитивный, гармоничный", 
        3: "**Творец** - оптимист, общительный, творческий",
        4: "**Практик** - надежный, организованный, трудолюбивый",
        5: "**Авантюрист** - свободолюбивый, любопытный, энергичный",
        6: "**Заботливый** - ответственный, семейный, гармоничный",
        7: "**Аналитик** - мудрый, духовный, интуитивный",
        8: "**Бизнесмен** - властный, успешный, материалистичный",
        9: "**Гуманист** - сострадательный, идеалистичный, мудрый"
    }
    
    return total, meanings.get(total, "**Особенная личность** - уникальный и многогранный характер")

# Команды бота
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_main_inline_keyboard()
    await update.message.reply_text(
        '🎉 Добро пожаловать! Я генерирую свежий контент каждый день!\n\n'
        '• 🎲 Факты, шутки, цитаты\n'
        '• 📅 Ежедневные гороскопы\n'
        '• 🍽️ Случайные рецепты\n'
        '• 🎬 Цитаты из фильмов\n'
        '• 🔢 Нумерология по дате рождения\n\n'
        'Выберите что вас интересует:',
        reply_markup=keyboard
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_back_keyboard()
    
    if update.message:
        await update.message.reply_text(
            '📞 **Доступные функции:**\n\n'
            '🎲 Генератор - случайные факты, шутки, цитаты\n'
            '📅 Гороскоп - ежедневный прогноз для вашего знака\n'
            '🍽️ Рецепты - простые идеи для готовки\n'
            '🎬 Фильмы - знаменитые цитаты из кино\n'
            '🔢 Нумерология - анализ по дате рождения\n\n'
            '💫 Контент обновляется ежедневно!',
            reply_markup=keyboard
        )
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            '📞 **Доступные функции:**\n\n'
            '🎲 Генератор - случайные факты, шутки, цитаты\n'
            '📅 Гороскоп - ежедневный прогноз для вашего знака\n'
            '🍽️ Рецепты - простые идеи для готовки\n'
            '🎬 Фильмы - знаменитые цитаты из кино\n'
            '🔢 Нумерология - анализ по дате рождения\n\n'
            '💫 Контент обновляется ежедневно!',
            reply_markup=keyboard
        )

# Обработка inline-кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "start_cmd":
        keyboard = get_main_inline_keyboard()
        await query.edit_message_text(
            '🎉 Добро пожаловать! Что хотите сгенерировать сегодня?',
            reply_markup=keyboard
        )
    
    elif data == "generator_cmd":
        keyboard = get_generator_keyboard()
        await query.edit_message_text(
            '🎲 **Генератор контента:**\n\n'
            'Выберите что хотите сгенерировать:',
            reply_markup=keyboard
        )
    
    elif data == "horoscope_cmd":
        keyboard = get_zodiac_keyboard()
        await query.edit_message_text(
            '♈ **Ежедневный гороскоп:**\n\n'
            'Выберите ваш знак зодиака:',
            reply_markup=keyboard
        )
    
    elif data == "recipe_cmd":
        recipe = get_daily_recipe()
        keyboard = get_back_keyboard()
        await query.edit_message_text(
            f'🍽️ {recipe}\n\n'
            'Приятного аппетита! 🎉',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    elif data == "movie_cmd":
        quote = get_movie_quote()
        keyboard = get_movie_keyboard()
        await query.edit_message_text(
            f'🎬 {quote}\n\n'
            'Хотите еще цитату из фильма?',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    elif data == "birthdate_cmd":
        keyboard = get_back_keyboard()
        await query.edit_message_text(
            '🔢 **Нумерология по дате рождения:**\n\n'
            'Отправьте мне дату рождения в формате:\n'
            '`ДД.ММ.ГГГГ`\n\n'
            'Например: 15.05.1990\n'
            'Я рассчитаю ваше число судьбы! ✨',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    elif data == "help_cmd":
        await help_command(update, context)
        return
    
    elif data.startswith("zodiac_"):
        sign = data.replace("zodiac_", "")
        horoscope = get_daily_horoscope(sign)
        keyboard = get_back_keyboard()
        await query.edit_message_text(
            horoscope,
            reply_markup=keyboard
        )
    
    elif data == "gen_fact":
        fact = get_daily_fact()
        keyboard = get_fact_keyboard()
        await query.edit_message_text(
            f'{fact}\n\n'
            'Хотите еще один факт?',
            reply_markup=keyboard
        )
    
    elif data == "gen_joke":
        joke = get_daily_joke()
        keyboard = get_joke_keyboard()
        await query.edit_message_text(
            f'{joke}\n\n'
            'Хотите еще одну шутку?',
            reply_markup=keyboard
        )
    
    elif data == "gen_idea":
        idea = get_daily_idea()
        keyboard = get_idea_keyboard()
        await query.edit_message_text(
            f'{idea}\n\n'
            'Хотите еще одну идею?',
            reply_markup=keyboard
        )
    
    elif data == "gen_advice":
        advice = get_daily_advice()
        keyboard = get_advice_keyboard()
        await query.edit_message_text(
            f'{advice}\n\n'
            'Хотите еще один совет?',
            reply_markup=keyboard
        )
    
    elif data == "gen_quote":
        quote = get_daily_quote()
        keyboard = get_quote_keyboard()
        await query.edit_message_text(
            f'{quote}\n\n'
            'Хотите еще одну цитату?',
            reply_markup=keyboard
        )
    
    elif data == "back_cmd":
        keyboard = get_main_inline_keyboard()
        await query.edit_message_text(
            '🔙 Возвращаемся в главное меню:',
            reply_markup=keyboard
        )

# Обработка даты рождения
async def handle_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        if '.' in text:
            day, month, year = map(int, text.split('.'))
        elif '-' in text:
            day, month, year = map(int, text.split('-'))
        elif '/' in text:
            day, month, year = map(int, text.split('/'))
        else:
            raise ValueError
        
        if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2023:
            number, meaning = calculate_birth_number(day, month, year)
            keyboard = get_back_keyboard()
            await update.message.reply_text(
                f'🔢 **Результат нумерологии:**\n\n'
                f'📅 Дата рождения: {text}\n'
                f'✨ Число судьбы: **{number}**\n\n'
                f'📖 **Характеристика:** {meaning}\n\n'
                f'💫 Это число отражает ваши врожденные таланты и потенциал!',
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                '❌ Неверная дата. Проверьте формат: ДД.ММ.ГГГГ\n'
                'Например: 15.05.1990'
            )
    except:
        await update.message.reply_text(
            '❌ Неверный формат. Используйте: ДД.ММ.ГГГГ\n'
            'Например: 15.05.1990'
        )

# Обработка обычных сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if any(c.isdigit() for c in text) and ('.' in text or '-' in text or '/' in text):
        await handle_birthdate(update, context)
        return
    
    if any(word in text for word in ['факт', 'fact']):
        await update.message.reply_text(get_daily_fact())
    elif any(word in text for word in ['шутка', 'анекдот', 'joke']):
        await update.message.reply_text(get_daily_joke())
    elif any(word in text for word in ['цитата', 'quote']):
        await update.message.reply_text(get_daily_quote())
    elif any(word in text for word in ['совет', 'advice']):
        await update.message.reply_text(get_daily_advice())
    elif any(word in text for word in ['идея', 'idea']):
        await update.message.reply_text(get_daily_idea())
    elif any(word in text for word in ['гороскоп', 'horoscope']):
        keyboard = get_zodiac_keyboard()
        await update.message.reply_text('Выберите ваш знак зодиака:', reply_markup=keyboard)
    elif any(word in text for word in ['рецепт', 'recipe']):
        await update.message.reply_text(get_daily_recipe(), parse_mode='Markdown')
    elif any(word in text for word in ['фильм', 'movie']):
        await update.message.reply_text(get_movie_quote(), parse_mode='Markdown')
    elif any(word in text for word in ['число', 'нумеролог']):
        await update.message.reply_text(
            '🔢 Отправьте дату рождения в формате: ДД.ММ.ГГГГ\nНапример: 15.05.1990'
        )
    else:
        keyboard = get_main_inline_keyboard()
        await update.message.reply_text(
            'Не понял запрос 😊 Используйте кнопки меню или напишите:\n'
            '• "факт" - случайный факт\n'
            '• "шутка" - случайная шутка\n'
            '• "гороскоп" - ежедневный гороскоп\n'
            '• "рецепт" - идея для готовки\n'
            '• "15.05.1990" - нумерология по дате',
            reply_markup=keyboard
        )

def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Бот запускается...")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()
