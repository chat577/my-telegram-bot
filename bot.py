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

# Клавиатуры
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎨 Сгенерировать картинку", callback_data="generate_image")],
        [InlineKeyboardButton("📖 Инструкция", callback_data="help_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_generate_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔄 Сгенерировать еще", callback_data="generate_another")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Хранение данных пользователей
user_requests = {}

def generate_image_from_text(text):
    """
    Генерирует изображение на основе текста
    Используем разные стратегии для демо
    """
    try:
        # Стратегия 1: Unsplash Source (бесплатные случайные изображения)
        unsplash_url = f"https://source.unsplash.com/512x512/?{requests.utils.quote(text)}"
        
        # Стратегия 2: Lorem Picsum (просто случайные изображения)
        random_id = random.randint(1, 1000)
        picsum_url = f"https://picsum.photos/512/512?random={random_id}"
        
        # Стратегия 3: Placeholder с цветом на основе текста
        text_hash = abs(hash(text)) % 16777215  # RGB цвет
        placeholder_url = f"https://via.placeholder.com/512/{(text_hash >> 16) & 255:02x}{(text_hash >> 8) & 255:02x}{text_hash & 255:02x}/ffffff?text={requests.utils.quote(text[:30])}"
        
        # Выбираем случайную стратегию
        strategies = [unsplash_url, picsum_url, placeholder_url]
        image_url = random.choice(strategies)
        
        return {
            "success": True,
            "image_url": image_url,
            "description": f"🖼️ Сгенерировано по запросу: '{text}'"
        }
    except Exception as e:
        logging.error(f"Error generating image: {e}")
        return {
            "success": False,
            "error": "Ошибка генерации изображения"
        }

# Команды бота
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_main_keyboard()
    
    welcome_text = (
        "🎨 **Добро пожаловать в генератор изображений!**\n\n"
        "Я помогу вам создать уникальные изображения по вашему текстовому описанию.\n\n"
        "**Что я умею:**\n"
        "• 🎨 Генерировать картинки по тексту\n"
        "• ⚡ Быстро обрабатывать запросы\n"
        "• 🖼️ Создавать уникальные изображения\n\n"
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
        "📖 **Инструкция по использованию:**\n\n"
        "**Как генерировать изображения:**\n"
        "1. Нажмите '🎨 Сгенерировать картинку'\n"
        "2. Введите текстовое описание\n"
        "3. Получите ваше изображение!\n\n"
        "**Примеры запросов:**\n"
        "• 'кот космос'\n"
        "• 'закат горы'\n"
        "• 'город будущее'\n"
        "• 'панда бамбук'\n\n"
        "**Советы:**\n"
        "• Используйте английские слова для лучших результатов\n"
        "• Будьте конкретны в описаниях\n"
        "• Экспериментируйте с разными запросами!"
    )
    
    keyboard = get_back_keyboard()
    
    if update.message:
        await update.message.reply_text(help_text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(help_text, reply_markup=keyboard, parse_mode='Markdown')

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
            "🎨 **Какую картинку вам сгенерировать сегодня?**\n\n"
            "Опишите словами то, что хотите увидеть на изображении.\n\n"
            "**Примеры:**\n"
            "• 'cat space' (кот в космосе)\n"
            "• 'sunset mountains' (закат в горах)\n"
            "• 'robot future' (робот будущее)\n\n"
            "💡 **Совет:** Используйте английские слова для лучших результатов!\n\n"
            "Введите ваш текст:"
        )
        
        # Сохраняем состояние для этого пользователя
        context.user_data[user_id] = {'waiting_for_text': True}
        
        await query.edit_message_text(instruction_text, reply_markup=get_back_keyboard(), parse_mode='Markdown')
    
    elif data == "generate_another":
        # Генерируем еще одно изображение с тем же текстом
        user_text = context.user_data.get(user_id, {}).get('last_text', '')
        
        if user_text:
            await process_image_generation(update, context, user_text, user_id)
        else:
            await query.edit_message_text(
                "❌ Не найден предыдущий текст. Начните заново.",
                reply_markup=get_main_keyboard()
            )
    
    elif data == "help_cmd":
        await help_command(update, context)
    
    elif data == "back_cmd":
        await start_command(update, context)

async def process_image_generation(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str, user_id: int):
    """Обрабатывает генерацию изображения"""
    
    # Показываем сообщение о начале генерации
    if update.callback_query:
        await update.callback_query.edit_message_text(
            f"⚡ **Генерирую изображение...**\n\n"
            f"Запрос: '{user_text}'\n\n"
            f"Это займет несколько секунд ⏳",
            parse_mode='Markdown'
        )
    elif update.message:
        await update.message.reply_text(
            f"⚡ **Генерирую изображение...**\n\n"
            f"Запрос: '{user_text}'\n\n"
            f"Это займет несколько секунд ⏳",
            parse_mode='Markdown'
        )
    
    # Генерируем изображение
    result = generate_image_from_text(user_text)
    
    if result["success"]:
        # Сохраняем в историю пользователя
        if user_id not in user_requests:
            user_requests[user_id] = []
        
        user_requests[user_id].append({
            "text": user_text,
            "timestamp": datetime.now().isoformat(),
            "image_url": result["image_url"]
        })
        
        # Сохраняем текст для повторной генерации
        if user_id not in context.user_data:
            context.user_data[user_id] = {}
        context.user_data[user_id]['last_text'] = user_text
        
        # Отправляем изображение
        success_text = (
            f"✅ **Изображение готово!**\n\n"
            f"📝 Запрос: '{user_text}'\n\n"
            f"Что дальше?"
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
            logging.error(f"Error sending photo: {e}")
            # Если не удалось отправить фото, отправляем ссылку
            error_message = (
                f"✅ **Изображение готово!**\n\n"
                f"📝 Запрос: '{user_text}'\n\n"
                f"🔗 Ссылка на изображение: {result['image_url']}\n\n"
                f"Что дальше?"
            )
            if update.callback_query:
                await update.callback_query.edit_message_text(error_message, reply_markup=get_generate_keyboard(), parse_mode='Markdown')
            else:
                await update.message.reply_text(error_message, reply_markup=get_generate_keyboard(), parse_mode='Markdown')
    
    else:
        error_text = (
            f"❌ **Ошибка генерации**\n\n"
            f"Не удалось создать изображение по запросу: '{user_text}'\n\n"
            f"Попробуйте другой текст или повторите позже."
        )
        if update.callback_query:
            await update.callback_query.edit_message_text(error_text, reply_markup=get_generate_keyboard(), parse_mode='Markdown')
        else:
            await update.message.reply_text(error_text, reply_markup=get_generate_keyboard(), parse_mode='Markdown')

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Проверяем, ждем ли мы текст для генерации
    if context.user_data.get(user_id, {}).get('waiting_for_text'):
        # Обрабатываем генерацию
        context.user_data[user_id]['waiting_for_text'] = False
        await process_image_generation(update, context, text, user_id)
    
    else:
        # Обычное сообщение - показываем меню
        await start_command(update, context)

def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Команды
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        
        # Обработчики
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Бот-генератор изображений запускается...")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()
