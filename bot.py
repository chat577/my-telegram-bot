import os
import logging
import requests
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv('BOT_TOKEN')

# Словарь тематических изображений
THEMATIC_IMAGES = {
    "космос": [
        "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06",  # космос
        "https://images.unsplash.com/photo-1462331940025-496dfbfc7564",  # галактика
    ],
    "животные": [
        "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba",  # кот
        "https://images.unsplash.com/photo-1543852786-1cf6624b9987",  # собака
    ],
    "природа": [
        "https://images.unsplash.com/photo-1501854140801-50d01698950b",  # горы
        "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05",  # лес
    ],
    "город": [
        "https://images.unsplash.com/photo-1449824913935-59a10b8d2000",  # город
        "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b",  # небоскребы
    ],
    "технологии": [
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e",  # робот
        "https://images.unsplash.com/photo-1535223289827-42f1e9919769",  # будущее
    ]
}

# Клавиатуры
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎨 Сгенерировать картинку", callback_data="generate_image")],
        [InlineKeyboardButton("🎯 Популярные запросы", callback_data="popular_requests")],
        [InlineKeyboardButton("📖 Инструкция", callback_data="help_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_popular_requests_keyboard():
    keyboard = [
        [InlineKeyboardButton("🚀 Космос и планеты", callback_data="req_space")],
        [InlineKeyboardButton("🐱 Милые животные", callback_data="req_animals")],
        [InlineKeyboardButton("🏔️ Природа и пейзажи", callback_data="req_nature")],
        [InlineKeyboardButton("🏙️ Города будущего", callback_data="req_city")],
        [InlineKeyboardButton("🤖 Роботы и технологии", callback_data="req_tech")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_generate_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔄 Сгенерировать похожее", callback_data="generate_similar")],
        [InlineKeyboardButton("🎨 Новый запрос", callback_data="generate_image")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_cmd")]])

def analyze_request(text):
    """Анализирует запрос и определяет тему"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['космос', 'планет', 'звезд', 'галактик']):
        return "космос"
    elif any(word in text_lower for word in ['кот', 'собак', 'животн', 'панда', 'медвед']):
        return "животные"
    elif any(word in text_lower for word in ['природ', 'лес', 'гор', 'озер', 'пейзаж']):
        return "природа"
    elif any(word in text_lower for word in ['город', 'здани', 'небоскреб', 'улиц']):
        return "город"
    elif any(word in text_lower for word in ['робот', 'техник', 'будущ', 'искусс']):
        return "технологии"
    else:
        return "random"

def generate_smart_image(text):
    """Умная генерация на основе тематики"""
    try:
        theme = analyze_request(text)
        
        if theme in THEMATIC_IMAGES:
            # Выбираем случайное изображение из тематической коллекции
            image_url = random.choice(THEMATIC_IMAGES[theme])
            return {
                "success": True,
                "image_url": image_url,
                "theme": theme,
                "description": f"🎨 Тема: {theme}\n📝 Запрос: '{text}'"
            }
        else:
            # Случайное качественное изображение
            collections = {
                "космос": 444,
                "животные": 105,
                "природа": 106,
                "город": 116,
                "технологии": 109
            }
            collection_id = random.choice(list(collections.values()))
            image_url = f"https://source.unsplash.com/collection/{collection_id}/512x512"
            
            return {
                "success": True,
                "image_url": image_url,
                "theme": "random",
                "description": f"🎨 Случайная подборка\n📝 Запрос: '{text}'"
            }
            
    except Exception as e:
        logging.error(f"Error in smart generation: {e}")
        return {
            "success": False,
            "error": "Ошибка генерации"
        }

# Команды бота
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_main_keyboard()
    
    welcome_text = (
        "🎨 **Умный генератор изображений**\n\n"
        "Я подбираю релевантные изображения по вашему описанию!\n\n"
        "**Как это работает:**\n"
        "• Анализирую ваш запрос\n"
        "• Подбираю тематическое изображение\n"
        "• Нахожу качественные картинки\n\n"
        "Выберите действие:"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(welcome_text, reply_markup=keyboard, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 **Как получить лучшие результаты:**\n\n"
        "**Эффективные запросы:**\n"
        "• 'Космос и планеты' 🚀\n"
        "• 'Милые коты и собаки' 🐱\n" 
        "• 'Горные пейзажи' 🏔️\n"
        "• 'Города будущего' 🏙️\n"
        "• 'Роботы и технологии' 🤖\n\n"
        "**Советы:**\n"
        "• Используйте конкретные темы\n"
        "• Попробуйте 'Популярные запросы'\n"
        "• Экспериментируйте с разными темами!"
    )
    
    if update.message:
        await update.message.reply_text(help_text, reply_markup=get_back_keyboard(), parse_mode='Markdown')
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(help_text, reply_markup=get_back_keyboard(), parse_mode='Markdown')

# Обработка inline-кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "start_cmd":
        await start_command(update, context)
    
    elif data == "generate_image":
        instruction_text = (
            "🎨 **Опишите желаемое изображение:**\n\n"
            "**Примеры эффективных запросов:**\n"
            "• 'Космос с планетами'\n"
            "• 'Милые животные'\n" 
            "• 'Горный пейзаж'\n"
            "• 'Город будущего'\n"
            "• 'Робот технологии'\n\n"
            "Введите ваш запрос:"
        )
        
        context.user_data[user_id] = {'waiting_for_text': True}
        await query.edit_message_text(instruction_text, reply_markup=get_back_keyboard(), parse_mode='Markdown')
    
    elif data == "popular_requests":
        await query.edit_message_text(
            "🎯 **Популярные категории:**\n\n"
            "Выберите тему для генерации:",
            reply_markup=get_popular_requests_keyboard()
        )
    
    elif data.startswith("req_"):
        themes = {
            "req_space": "космос планеты звезды",
            "req_animals": "милые животные коты собаки", 
            "req_nature": "горный пейзаж природа",
            "req_city": "город будущего архитектура",
            "req_tech": "робот технологии будущее"
        }
        
        theme_text = themes[data]
        await process_image_generation(update, context, theme_text, user_id)
    
    elif data == "generate_similar":
        last_text = context.user_data.get(user_id, {}).get('last_text', '')
        if last_text:
            await process_image_generation(update, context, last_text, user_id)
        else:
            await query.answer("❌ Нет предыдущего запроса")
    
    elif data == "help_cmd":
        await help_command(update, context)
    
    elif data == "back_cmd":
        await start_command(update, context)

async def process_image_generation(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str, user_id: int):
    """Обрабатывает генерацию изображения"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            f"🔍 **Ищу подходящее изображение...**\n\n"
            f"Запрос: '{user_text}'\n\n"
            f"⏳ Подбираю лучший вариант...",
            parse_mode='Markdown'
        )
    
    result = generate_smart_image(user_text)
    
    if result["success"]:
        context.user_data[user_id] = {'last_text': user_text}
        
        success_text = (
            f"✅ **Изображение найдено!**\n\n"
            f"{result['description']}\n\n"
            f"💡 Попробуйте 'похожее' для другого варианта!"
        )
        
        try:
            if update.callback_query:
                await context.bot.send_photo(
                    chat_id=update.callback_query.message.chat_id,
                    photo=result["image_url"],
                    caption=success_text,
                    reply_markup=get_generate_keyboard(),
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_photo(
                    photo=result["image_url"],
                    caption=success_text,
                    reply_markup=get_generate_keyboard(),
                    parse_mode='Markdown'
                )
        except Exception as e:
            await handle_photo_error(update, context, result, user_text)
    
    else:
        error_text = f"❌ Не удалось найти изображение для: '{user_text}'"
        if update.callback_query:
            await update.callback_query.edit_message_text(error_text, reply_markup=get_main_keyboard())
        else:
            await update.message.reply_text(error_text, reply_markup=get_main_keyboard())

async def handle_photo_error(update: Update, context: ContextTypes.DEFAULT_TYPE, result: dict, user_text: str):
    """Обрабатывает ошибки отправки фото"""
    error_message = (
        f"✅ **Изображение готово!**\n\n"
        f"📝 Запрос: '{user_text}'\n\n"
        f"🔗 Ссылка: {result['image_url']}\n\n"
        f"💡 Скопируйте ссылку для просмотра!"
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(error_message, reply_markup=get_generate_keyboard())
    else:
        await update.message.reply_text(error_message, reply_markup=get_generate_keyboard())

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if context.user_data.get(user_id, {}).get('waiting_for_text'):
        context.user_data[user_id]['waiting_for_text'] = False
        await process_image_generation(update, context, text, user_id)
    else:
        await start_command(update, context)

def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Умный генератор изображений запускается...")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()
