import os
import logging
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv('BOT_TOKEN')

# БАЗА ДАННЫХ СЛУЧАЙНЫХ ФАКТОВ
FACTS = [
    "🐙 Осьминоги имеют три сердца и голубую кровь!",
    "🌍 Земля - единственная планета, не названная в честь бога",
    "🍯 Мед никогда не портится - археологи находили съедобный мед возрастом 3000 лет",
    "🐧 Пингвины могут прыгать до 2 метров в высоту",
    "📚 В Японии более 50 видов пончиков с вкусом пиццы"
]

JOKES = [
    "Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 == Dec 25!",
    "Разговор двух серверов: - Ты почему такой медленный? - Да RAM'а не хватает...",
    "Почему Python не нужна одежда? Потому что у него есть классы!",
    "Какой кофе пьют программисты? Java!",
]

IDEAS = [
    "💡 Создай приложение для учета личных финансов",
    "🚀 Разработай бота для изучения английского языка",
    "🎨 Сделай генератор мемов на основе текущих новостей",
    "📊 Создай дашборд для отслеживания привычек",
    "🤖 Напиши AI-помощника для планирования дня"
]

# Клавиатуры
def get_main_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("🚀 Старт", callback_data="start_cmd")],
        [InlineKeyboardButton("ℹ️ Информация", callback_data="info_cmd")],
        [InlineKeyboardButton("🎲 Генератор", callback_data="generator_cmd")],
        [InlineKeyboardButton("📞 Помощь", callback_data="help_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_generator_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎲 Случайный факт", callback_data="gen_fact")],
        [InlineKeyboardButton("😂 Случайная шутка", callback_data="gen_joke")],
        [InlineKeyboardButton("💡 Идея для проекта", callback_data="gen_idea")],
        [InlineKeyboardButton("🎯 Случайное число", callback_data="gen_number")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔙 Назад в меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Генераторы контента
def generate_fact():
    return random.choice(FACTS)

def generate_joke():
    return random.choice(JOKES)

def generate_idea():
    return random.choice(IDEAS)

def generate_number():
    return f"🎲 Ваше случайное число: **{random.randint(1, 100)}**"

def generate_advice():
    advices = [
        "🌟 Начни с малого - большие цели достигаются маленькими шагами",
        "💪 Сегодня лучше, чем вчера - это уже прогресс!",
        "🎯 Сфокусируйся на одном деле и доведи его до конца",
        "📚 Учись каждый день чему-то новому",
        "🚀 Не бойся ошибок - они ведут к росту"
    ]
    return random.choice(advices)

# Команды бота
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_main_inline_keyboard()
    await update.message.reply_text(
        '🎉 Добро пожаловать! Я умею генерировать разный контент!\n\n'
        'Выберите действие:',
        reply_markup=keyboard
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_back_keyboard()
    await update.message.reply_text(
        '🤖 **Информация о боте:**\n\n'
        '• Создан на Python\n• Хостится на Railway\n• Умеет генерировать:\n'
        '  🎲 Случайные факты\n  😂 Шутки\n  💡 Идеи для проектов\n  🎯 Числа\n  🌟 Советы\n\n'
        '✅ Все генераторы работают бесплатно!',
        reply_markup=keyboard
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_back_keyboard()
    await update.message.reply_text(
        '📞 **Доступные команды:**\n\n'
        '/start - начать работу\n'
        '/fact - случайный факт\n'
        '/joke - случайная шутка\n'
        '/idea - идея для проекта\n'
        '/number - случайное число\n'
        '/advice - случайный совет\n'
        '/help - эта справка\n\n'
        'Или используйте кнопки меню ↓',
        reply_markup=keyboard
    )

# Генераторы через команды
async def fact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_fact())

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_joke())

async def idea_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_idea())

async def number_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_number(), parse_mode='Markdown')

async def advice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_advice())

# Обработка inline-кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "start_cmd":
        keyboard = get_main_inline_keyboard()
        await query.edit_message_text(
            '🎉 Добро пожаловать! Что хотите сгенерировать?',
            reply_markup=keyboard
        )
    
    elif data == "info_cmd":
        keyboard = get_back_keyboard()
        await query.edit_message_text(
            '🤖 **Информация о боте:**\n\n'
            '• Создан на Python\n• Хостится на Railway\n• Умеет генерировать:\n'
            '  🎲 Случайные факты\n  😂 Шутки\n  💡 Идеи для проектов\n  🎯 Числа\n  🌟 Советы\n\n'
            '✅ Все генераторы работают бесплатно!',
            reply_markup=keyboard
        )
    
    elif data == "generator_cmd":
        keyboard = get_generator_keyboard()
        await query.edit_message_text(
            '🎲 **Генератор контента:**\n\n'
            'Выберите что хотите сгенерировать:',
            reply_markup=keyboard
        )
    
    elif data == "help_cmd":
        keyboard = get_back_keyboard()
        await query.edit_message_text(
            '📞 **Доступные команды:**\n\n'
            '/start - начать работу\n'
            '/fact - случайный факт\n'
            '/joke - случайная шутка\n'
            '/idea - идея для проекта\n'
            '/number - случайное число\n'
            '/advice - случайный совет\n'
            '/help - эта справка\n\n'
            'Или используйте кнопки меню ↓',
            reply_markup=keyboard
        )
    
    elif data == "gen_fact":
        keyboard = get_generator_keyboard()
        await query.edit_message_text(
            f'{generate_fact()}\n\n'
            'Хотите еще что-то сгенерировать?',
            reply_markup=keyboard
        )
    
    elif data == "gen_joke":
        keyboard = get_generator_keyboard()
        await query.edit_message_text(
            f'{generate_joke()}\n\n'
            'Хотите еще что-то сгенерировать?',
            reply_markup=keyboard
        )
    
    elif data == "gen_idea":
        keyboard = get_generator_keyboard()
        await query.edit_message_text(
            f'{generate_idea()}\n\n'
            'Хотите еще что-то сгенерировать?',
            reply_markup=keyboard
        )
    
    elif data == "gen_number":
        keyboard = get_generator_keyboard()
        await query.edit_message_text(
            f'{generate_number()}\n\n'
            'Хотите еще что-то сгенерировать?',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    elif data == "back_cmd":
        keyboard = get_main_inline_keyboard()
        await query.edit_message_text(
            '🔙 Возвращаемся в главное меню:',
            reply_markup=keyboard
        )

# Обработка обычных сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if any(word in text for word in ['факт', 'fact']):
        await update.message.reply_text(generate_fact())
    elif any(word in text for word in ['шутка', 'анекдот', 'joke']):
        await update.message.reply_text(generate_joke())
    elif any(word in text for word in ['идея', 'проект', 'idea']):
        await update.message.reply_text(generate_idea())
    elif any(word in text for word in ['число', 'номер', 'number']):
        await update.message.reply_text(generate_number(), parse_mode='Markdown')
    elif any(word in text for word in ['совет', 'advice']):
        await update.message.reply_text(generate_advice())
    else:
        keyboard = get_main_inline_keyboard()
        await update.message.reply_text(
            'Не понял запрос 😊 Используйте команды или кнопки меню:',
            reply_markup=keyboard
        )

def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Команды
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("info", info_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("fact", fact_command))
        application.add_handler(CommandHandler("joke", joke_command))
        application.add_handler(CommandHandler("idea", idea_command))
        application.add_handler(CommandHandler("number", number_command))
        application.add_handler(CommandHandler("advice", advice_command))
        
        # Обработчики
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Бот-генератор запускается...")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()
