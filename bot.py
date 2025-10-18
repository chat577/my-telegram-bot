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
        [InlineKeyboardButton("📊 Статистика", callback_data="stats_cmd")],
        [InlineKeyboardButton("⭐ Избранное", callback_data="favorites_cmd")],
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
        [InlineKeyboardButton("❤️ В избранное", callback_data="fav_fact")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_joke_keyboard():
    keyboard = [
        [InlineKeyboardButton("😂 Еще шутку", callback_data="gen_joke")],
        [InlineKeyboardButton("❤️ В избранное", callback_data="fav_joke")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_idea_keyboard():
    keyboard = [
        [InlineKeyboardButton("💡 Еще идею", callback_data="gen_idea")],
        [InlineKeyboardButton("❤️ В избранное", callback_data="fav_idea")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_advice_keyboard():
    keyboard = [
        [InlineKeyboardButton("🌟 Еще совет", callback_data="gen_advice")],
        [InlineKeyboardButton("❤️ В избранное", callback_data="fav_advice")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_quote_keyboard():
    keyboard = [
        [InlineKeyboardButton("📜 Еще цитату", callback_data="gen_quote")],
        [InlineKeyboardButton("❤️ В избранное", callback_data="fav_quote")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_movie_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎬 Еще цитату из фильма", callback_data="movie_cmd")],
        [InlineKeyboardButton("❤️ В избранное", callback_data="fav_movie")],
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
def get_favorites_management_keyboard():
    keyboard = [
        [InlineKeyboardButton("📋 Посмотреть избранное", callback_data="view_favorites")],
        [InlineKeyboardButton("🗑️ Удалить избранное", callback_data="delete_favorites")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_favorites_list_keyboard(favorites, page=0, items_per_page=5):
    keyboard = []
    
    # Показываем избранное для текущей страницы
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    current_favorites = favorites[start_idx:end_idx]
    
    for i, (fav_id, content_type, content, timestamp) in enumerate(current_favorites):
        # Обрезаем длинный текст для кнопки
        short_content = content[:30] + "..." if len(content) > 30 else content
        emoji = {
            'fact': '🎲', 'joke': '😂', 'quote': '📜', 
            'advice': '🌟', 'idea': '💡', 'movie': '🎬'
        }.get(content_type, '⭐')
        
        keyboard.append([InlineKeyboardButton(
            f"{emoji} {short_content}", 
            callback_data=f"view_fav_{fav_id}"
        )])
    
    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"fav_page_{page-1}"))
    
    if end_idx < len(favorites):
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"fav_page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🔙 К управлению", callback_data="manage_favorites")])
    
    return InlineKeyboardMarkup(keyboard)

def get_favorite_item_keyboard(fav_id, content_type, content):
    keyboard = [
        [InlineKeyboardButton("🗑️ Удалить эту запись", callback_data=f"delete_fav_{fav_id}")],
        [InlineKeyboardButton("📋 К списку избранного", callback_data="view_favorites")],
        [InlineKeyboardButton("🔙 К управлению", callback_data="manage_favorites")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_delete_favorites_keyboard(favorites, page=0, items_per_page=5):
    keyboard = []
    
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    current_favorites = favorites[start_idx:end_idx]
    
    for i, (fav_id, content_type, content, timestamp) in enumerate(current_favorites):
        short_content = content[:30] + "..." if len(content) > 30 else content
        emoji = {
            'fact': '🎲', 'joke': '😂', 'quote': '📜', 
            'advice': '🌟', 'idea': '💡', 'movie': '🎬'
        }.get(content_type, '⭐')
        
        keyboard.append([InlineKeyboardButton(
            f"❌ {emoji} {short_content}", 
            callback_data=f"confirm_delete_{fav_id}"
        )])
    
    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"delete_page_{page-1}"))
    
    if end_idx < len(favorites):
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"delete_page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🔙 К управлению", callback_data="manage_favorites")])
    
    return InlineKeyboardMarkup(keyboard)

def get_delete_confirmation_keyboard(fav_id):
    keyboard = [
        [InlineKeyboardButton("✅ Да, удалить", callback_data=f"final_delete_{fav_id}")],
        [InlineKeyboardButton("❌ Нет, отмена", callback_data="view_favorites")]
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

# БАЗА ДАННЫХ - упрощенная версия без PostgreSQL
user_data = {}

def update_user(user_id, username=None, first_name=None, last_name=None):
    """Упрощенная функция для хранения данных пользователя"""
    if user_id not in user_data:
        user_data[user_id] = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'created_at': datetime.now(),
            'last_active': datetime.now(),
            'requests': [],
            'favorites': []
        }
    else:
        user_data[user_id].update({
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'last_active': datetime.now()
        })

def save_request(user_id, request_type, request_data, response_data):
    """Упрощенная функция для сохранения запроса"""
    if user_id not in user_data:
        update_user(user_id)
    
    user_data[user_id]['requests'].append({
        'type': request_type,
        'data': request_data,
        'response': response_data,
        'timestamp': datetime.now()
    })

def add_to_favorites(user_id, content_type, content):
    """Упрощенная функция для добавления в избранное"""
    if user_id not in user_data:
        update_user(user_id)
    
    user_data[user_id]['favorites'].append({
        'type': content_type,
        'content': content,
        'timestamp': datetime.now()
    })
    return True

def get_user_stats(user_id):
    """Упрощенная функция для получения статистики"""
    if user_id not in user_data:
        return None
    
    user = user_data[user_id]
    total_requests = len(user['requests'])
    
    # Считаем популярные типы запросов
    type_count = {}
    for req in user['requests']:
        req_type = req['type']
        type_count[req_type] = type_count.get(req_type, 0) + 1
    
    popular_types = sorted(type_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        'total_requests': total_requests,
        'popular_types': popular_types,
        'last_active': user['last_active'],
        'favorites_count': len(user['favorites'])
    }

def get_favorites(user_id):
    """Упрощенная функция для получения избранного"""
    if user_id not in user_data:
        return []
    
    return [(fav['type'], fav['content'], fav['timestamp']) for fav in user_data[user_id]['favorites']]

async def update_user_info(update: Update):
    """Обновление информации о пользователе"""
    user = update.effective_user
    if user:
        update_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

# Команды бота
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update_user_info(update)
    keyboard = get_main_inline_keyboard()
    await update.message.reply_text(
        '🎉 Добро пожаловать! Я генерирую свежий контент каждый день!\n\n'
        '• 🎲 Факты, шутки, цитаты\n'
        '• 📅 Ежедневные гороскопы\n'
        '• 🍽️ Случайные рецепты\n'
        '• 🎬 Цитаты из фильмов\n'
        '• 🔢 Нумерология по дате рождения\n'
        '• 📊 Статистика и избранное\n\n'
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
            '🔢 Нумерология - анализ по дате рождения\n'
            '📊 Статистика - ваша активность и предпочтения\n'
            '⭐ Избранное - сохраняйте понравившийся контент\n\n'
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
            '🔢 Нумерология - анализ по дате рождения\n'
            '📊 Статистика - ваша активность и предпочтения\n'
            '⭐ Избранное - сохраняйте понравившийся контент\n\n'
            '💫 Контент обновляется ежедневно!',
            reply_markup=keyboard
        )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update_user_info(update)
    user_id = update.effective_user.id
    
    stats = get_user_stats(user_id)
    if stats:
        message = f"📊 **Ваша статистика:**\n\n"
        message += f"• Всего запросов: {stats['total_requests']}\n"
        message += f"• Избранных записей: {stats['favorites_count']}\n"
        message += f"• Последняя активность: {stats['last_active'].strftime('%d.%m.%Y %H:%M')}\n\n"
        
        if stats['popular_types']:
            message += "🎯 **Популярные запросы:**\n"
            for req_type, count in stats['popular_types']:
                type_names = {
                    'fact': 'Факты',
                    'joke': 'Шутки', 
                    'quote': 'Цитаты',
                    'advice': 'Советы',
                    'idea': 'Идеи',
                    'horoscope': 'Гороскопы',
                    'recipe': 'Рецепты',
                    'movie': 'Фильмы',
                    'birthdate': 'Нумерология'
                }
                display_name = type_names.get(req_type, req_type)
                message += f"• {display_name}: {count}\n"
    else:
        message = "📊 У вас пока нет статистики. Начните использовать бота!"
    
    keyboard = get_back_keyboard()
    if update.message:
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode='Markdown')
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def favorites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update_user_info(update)
    
    keyboard = get_favorites_management_keyboard()
    if update.message:
        await update.message.reply_text(
            "⭐ **Управление избранным:**\n\n"
            "Выберите действие:",
            reply_markup=keyboard
        )
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "⭐ **Управление избранным:**\n\n"
            "Выберите действие:",
            reply_markup=keyboard
        )
    
    favorites = get_favorites(user_id)
    if favorites:
        message = "⭐ **Ваше избранное:**\n\n"
        for content_type, content, created_at in favorites[:10]:
            type_emoji = {
                'fact': '🎲',
                'joke': '😂',
                'quote': '📜',
                'advice': '🌟',
                'idea': '💡',
                'movie': '🎬'
            }
            emoji = type_emoji.get(content_type, '⭐')
            short_content = content[:100] + "..." if len(content) > 100 else content
            message += f"{emoji} {short_content}\n\n"
    else:
        message = "⭐ У вас пока нет избранного. Нажмите ❤️ на понравившемся контенте чтобы добавить!"
    
    keyboard = get_back_keyboard()
    if update.message:
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode='Markdown')
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

# Обработка inline-кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
 # ДОБАВЬ эти обработчики в функцию button_handler:

elif data == "manage_favorites":
    keyboard = get_favorites_management_keyboard()
    await query.edit_message_text(
        "⭐ **Управление избранным:**\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )

elif data == "view_favorites":
    user_id = query.from_user.id
    favorites = get_favorites_with_ids(user_id)
    
    if favorites:
        keyboard = get_favorites_list_keyboard(favorites)
        await query.edit_message_text(
            "⭐ **Ваше избранное:**\n\n"
            "Выберите запись для просмотра:",
            reply_markup=keyboard
        )
    else:
        await query.answer("У вас пока нет избранного")

elif data.startswith("view_fav_"):
    fav_id = int(data.replace("view_fav_", ""))
    favorite = get_favorite_by_id(fav_id)
    
    if favorite:
        type_emoji = {
            'fact': '🎲', 'joke': '😂', 'quote': '📜',
            'advice': '🌟', 'idea': '💡', 'movie': '🎬'
        }
        emoji = type_emoji.get(favorite['type'], '⭐')
        
        keyboard = get_favorite_item_keyboard(fav_id, favorite['type'], favorite['content'])
        await query.edit_message_text(
            f"{emoji} **Запись из избранного:**\n\n"
            f"{favorite['content']}",
            reply_markup=keyboard,
            parse_mode='Markdown' if favorite['type'] in ['recipe', 'movie'] else None
        )
    else:
        await query.answer("Запись не найдена")

elif data.startswith("fav_page_"):
    page = int(data.replace("fav_page_", ""))
    user_id = query.from_user.id
    favorites = get_favorites_with_ids(user_id)
    
    keyboard = get_favorites_list_keyboard(favorites, page)
    await query.edit_message_text(
        f"⭐ **Ваше избранное (страница {page + 1}):**\n\n"
        "Выберите запись для просмотра:",
        reply_markup=keyboard
    )

elif data == "delete_favorites":
    user_id = query.from_user.id
    favorites = get_favorites_with_ids(user_id)
    
    if favorites:
        keyboard = get_delete_favorites_keyboard(favorites)
        await query.edit_message_text(
            "🗑️ **Удаление избранного:**\n\n"
            "Выберите запись для удаления:",
            reply_markup=keyboard
        )
    else:
        await query.answer("У вас пока нет избранного для удаления")

elif data.startswith("delete_page_"):
    page = int(data.replace("delete_page_", ""))
    user_id = query.from_user.id
    favorites = get_favorites_with_ids(user_id)
    
    keyboard = get_delete_favorites_keyboard(favorites, page)
    await query.edit_message_text(
        f"🗑️ **Удаление избранного (страница {page + 1}):**\n\n"
        "Выберите запись для удаления:",
        reply_markup=keyboard
    )

elif data.startswith("confirm_delete_"):
    fav_id = int(data.replace("confirm_delete_", ""))
    favorite = get_favorite_by_id(fav_id)
    
    if favorite:
        short_content = favorite['content'][:50] + "..." if len(favorite['content']) > 50 else favorite['content']
        keyboard = get_delete_confirmation_keyboard(fav_id)
        await query.edit_message_text(
            f"❓ **Подтверждение удаления:**\n\n"
            f"Вы уверены, что хотите удалить эту запись?\n\n"
            f"`{short_content}`",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        await query.answer("Запись не найдена")

elif data.startswith("final_delete_"):
    fav_id = int(data.replace("final_delete_", ""))
    user_id = query.from_user.id
    
    if delete_favorite(user_id, fav_id):
        await query.edit_message_text(
            "✅ **Запись успешно удалена из избранного!**",
            reply_markup=get_back_keyboard()
        )
    else:
        await query.answer("Ошибка при удалении записи")

# ОБНОВИ существующий обработчик favorites_cmd:
elif data == "favorites_cmd":
    keyboard = get_favorites_management_keyboard()
    await query.edit_message_text(
        "⭐ **Управление избранным:**\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )   
    # Обновляем информацию о пользователе
    await update_user_info(update)
    user_id = query.from_user.id
    
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
        save_request(user_id, 'recipe', '', recipe)
    
    elif data == "movie_cmd":
        quote = get_movie_quote()
        keyboard = get_movie_keyboard()
        await query.edit_message_text(
            f'🎬 {quote}\n\n'
            'Хотите еще цитату из фильма?',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        save_request(user_id, 'movie', '', quote)
    
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
    
    elif data == "stats_cmd":
        await stats_command(update, context)
        return
    
    elif data == "favorites_cmd":
        await favorites_command(update, context)
        return
    
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
        save_request(user_id, 'horoscope', sign, horoscope)
    
    elif data == "gen_fact":
        fact = get_daily_fact()
        keyboard = get_fact_keyboard()
        await query.edit_message_text(
            f'{fact}',
            reply_markup=keyboard
        )
        save_request(user_id, 'fact', '', fact)
    
    elif data == "gen_joke":
        joke = get_daily_joke()
        keyboard = get_joke_keyboard()
        await query.edit_message_text(
            f'{joke}',
            reply_markup=keyboard
        )
        save_request(user_id, 'joke', '', joke)
    
    elif data == "gen_idea":
        idea = get_daily_idea()
        keyboard = get_idea_keyboard()
        await query.edit_message_text(
            f'{idea}',
            reply_markup=keyboard
        )
        save_request(user_id, 'idea', '', idea)
    
    elif data == "gen_advice":
        advice = get_daily_advice()
        keyboard = get_advice_keyboard()
        await query.edit_message_text(
            f'{advice}',
            reply_markup=keyboard
        )
        save_request(user_id, 'advice', '', advice)
    
    elif data == "gen_quote":
        quote = get_daily_quote()
        keyboard = get_quote_keyboard()
        await query.edit_message_text(
            f'{quote}',
            reply_markup=keyboard
        )
        save_request(user_id, 'quote', '', quote)
    
    elif data.startswith("fav_"):
        content_type = data.replace("fav_", "")
        message_text = query.message.text
        
        if add_to_favorites(user_id, content_type, message_text):
            await query.answer("✅ Добавлено в избранное!")
        else:
            await query.answer("❌ Ошибка при добавлении в избранное")
    
    elif data == "back_cmd":
        keyboard = get_main_inline_keyboard()
        await query.edit_message_text(
            '🔙 Возвращаемся в главное меню:',
            reply_markup=keyboard
        )

# Обработка даты рождения
async def handle_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update_user_info(update)
    text = update.message.text
    user_id = update.effective_user.id
    
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
            result_text = (
                f'🔢 **Результат нумерологии:**\n\n'
                f'📅 Дата рождения: {text}\n'
                f'✨ Число судьбы: **{number}**\n\n'
                f'📖 **Характеристика:** {meaning}\n\n'
                f'💫 Это число отражает ваши врожденные таланты и потенциал!'
            )
            await update.message.reply_text(
                result_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            save_request(user_id, 'birthdate', text, result_text)
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
    await update_user_info(update)
    text = update.message.text.lower()
    user_id = update.effective_user.id
    
    if any(c.isdigit() for c in text) and ('.' in text or '-' in text or '/' in text):
        await handle_birthdate(update, context)
        return
    
    if any(word in text for word in ['факт', 'fact']):
        response = get_daily_fact()
        await update.message.reply_text(response)
        save_request(user_id, 'fact', text, response)
    elif any(word in text for word in ['шутка', 'анекдот', 'joke']):
        response = get_daily_joke()
        await update.message.reply_text(response)
        save_request(user_id, 'joke', text, response)
    elif any(word in text for word in ['цитата', 'quote']):
        response = get_daily_quote()
        await update.message.reply_text(response)
        save_request(user_id, 'quote', text, response)
    elif any(word in text for word in ['совет', 'advice']):
        response = get_daily_advice()
        await update.message.reply_text(response)
        save_request(user_id, 'advice', text, response)
    elif any(word in text for word in ['идея', 'idea']):
        response = get_daily_idea()
        await update.message.reply_text(response)
        save_request(user_id, 'idea', text, response)
    elif any(word in text for word in ['гороскоп', 'horoscope']):
        keyboard = get_zodiac_keyboard()
        await update.message.reply_text('Выберите ваш знак зодиака:', reply_markup=keyboard)
    elif any(word in text for word in ['рецепт', 'recipe']):
        response = get_daily_recipe()
        await update.message.reply_text(response, parse_mode='Markdown')
        save_request(user_id, 'recipe', text, response)
    elif any(word in text for word in ['фильм', 'movie']):
        response = get_movie_quote()
        await update.message.reply_text(response, parse_mode='Markdown')
        save_request(user_id, 'movie', text, response)
    elif any(word in text for word in ['статистика', 'stats']):
        await stats_command(update, context)
    elif any(word in text for word in ['избранное', 'favorites']):
        await favorites_command(update, context)
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
            '• "статистика" - ваша активность\n'
            '• "избранное" - сохраненные записи\n'
            '• "15.05.1990" - нумерология по дате',
            reply_markup=keyboard
        )

def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("favorites", favorites_command))
        
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Бот с улучшениями запускается...")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()

