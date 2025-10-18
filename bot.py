import os
import logging
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv('BOT_TOKEN')

# Бесплатные API для генерации изображений
IMAGE_APIS = {
    "dalle": "https://api.openai.com/v1/images/generations",  # Платный, но для структуры
    "placeholder": "https://picsum.photos/512/512",  # Бесплатные случайные изображения
    "placeholder_custom": "https://picsum.photos/512/512?random="  # С параметром
}

# Клавиатуры
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎨 Сгенерировать картинку", callback_data="generate_image")],
        [InlineKeyboardButton("🖼️ Мои генерации", callback_data="my_generations")],
        [InlineKeyboardButton("📖 Инструкция", callback_data="help_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_generate_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔄 Сгенерировать еще", callback_data="generate_image")],
        [InlineKeyboardButton("📋 Ввести новый текст", callback_data="new_text")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_keyboard():
    keyboard = [
        [InlineKeyboardButton("✅ Да, генерировать!", callback_data="confirm_generate")],
        [InlineKeyboardButton("✏️ Изменить текст", callback_data="change_text")],
        [InlineKeyboardButton("🔙 Отмена", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Хранение данных пользователей
user_requests = {}

# Функции для генерации изображений
def generate_placeholder_image(text):
    """
    Генерирует псевдо-изображение на основе текста
    В реальном боте здесь будет вызов AI API
    """
    # Создаем "уникальный" URL на основе текста
    text_hash = abs(hash(text)) % 1000
    image_url = f"https://picsum.photos/512/512?random={text_hash}"
    
    return {
        "success": True,
        "image_url": image_url,
        "description": f"🖼️ Сгенерировано по запросу: '{text}'"
    }

def generate_ai_image(text):
    """
    Заглушка для реальной AI генерации
    В продакшене здесь будет вызов DALL-E, Stable Diffusion и т.д.
    """
    try:
        # Здесь будет реальный вызов AI API
        # Например: 
        # response = requests.post(IMAGE_APIS["dalle"], 
        #                         headers={"Authorization": f"Bearer {API_KEY}"},
        #                         json={"prompt": text, "n": 1, "size": "512x512"})
        
        # Для демо используем placeholder
        return generate_placeholder_image(text)
        
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
        "• 🖼️ Показывать историю ваших генераций\n"
        "• ⚡ Быстро обрабатывать запросы\n\n"
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
        "2. Введите текстовое описание того, что хотите увидеть\n"
        "3. Подтвердите генерацию\n"
        "4. Получите ваше изображение!\n\n"
        "**Примеры запросов:**\n"
        "• 'Кот в космосе в скафандре'\n"
        "• 'Закат над горным озером'\n"
        "• 'Фантастический город будущего'\n"
        "• 'Милая панда ест бамбук'\n\n"
        "**Советы:**\n"
        "• Будьте конкретны в описаниях\n"
        "• Добавляйте детали для лучшего результата\n"
        "• Используйте прилагательные\n"
        "• Экспериментируйте с разными стилями!"
    )
    
    keyboard = get_back_keyboard()
    
    if update.message:
        await update.message.reply_text(help_text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(help_text, reply_markup=keyboard, parse_mode='Markdown')

async def my_generations_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_history = user_requests.get(user_id, [])
    
    if user_history:
        history_text = "🖼️ **Ваши последние генерации:**\n\n"
        for i, request in enumerate(user_history[-5:], 1):  # Последние 5 запросов
            history_text += f"{i}. '{request['text']}'\n"
        
        history_text += "\nПродолжайте творить! 🎨"
    else:
        history_text = "🖼️ У вас пока нет созданных изображений.\n\nНажмите '🎨 Сгенерировать картинку' чтобы начать!"
    
    keyboard = get_back_keyboard()
    
    if update.message:
        await update.message.reply_text(history_text, reply_markup=keyboard)
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(history_text, reply_markup=keyboard)

# Обработка inline-кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "start_cmd":
        await start_command(update, context)
    
    elif data == "generate_image":
        # Сохраняем состояние для этого пользователя
        if user_id not in context.user_data:
            context.user_data[user_id] = {}
        context.user_data[user_id]['waiting_for_text'] = True
        
        instruction_text = (
            "🎨 **Какую картинку вам сгенерировать сегодня?**\n\n"
            "Опишите словами то, что хотите увидеть на изображении.\n\n"
            "**Примеры:**\n"
            "• 'Космонавт катается на скейте'\n"
            "• 'Замок на облаке'\n"
            "• 'Робот читает книгу'\n\n"
            "💡 **Совет:** Чем детальнее описание, тем лучше результат!\n\n"
            "Введите ваш текст:"
        )
        
        keyboard = get_back_keyboard()
        await query.edit_message_text(instruction_text, reply_markup=keyboard, parse_mode='Markdown')
    
    elif data == "new_text":
        # Снова запрашиваем текст
        context.user_data[user_id]['waiting_for_text'] = True
        
        instruction_text = "✏️ **Введите новый текст для генерации картинки:**"
        await query.edit_message_text(instruction_text, reply_markup=get_back_keyboard())
    
    elif data == "confirm_generate":
        # Генерируем изображение с сохраненным текстом
        user_text = context.user_data[user_id].get('pending_text', '')
        
        if not user_text:
            await query.edit_message_text(
                "❌ Текст не найден. Попробуйте снова.",
                reply_markup=get_main_keyboard()
            )
            return
        
        # Показываем сообщение о начале генерации
        await query.edit_message_text(
            f"⚡ **Генерирую изображение...**\n\n"
            f"Запрос: '{user_text}'\n\n"
            f"Это займет несколько секунд ⏳",
            parse_mode='Markdown'
        )
        
        # Генерируем изображение
        result = generate_ai_image(user_text)
        
        if result["success"]:
            # Сохраняем в историю пользователя
            if user_id not in user_requests:
                user_requests[user_id] = []
            
            user_requests[user_id].append({
                "text": user_text,
                "timestamp": datetime.now().isoformat(),
                "image_url": result["image_url"]
            })
            
            # Отправляем изображение
            success_text = (
                f"✅ **Изображение готово!**\n\n"
                f"📝 Запрос: '{user_text}'\n\n"
                f"Что дальше?"
            )
            
            try:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=result["image_url"],
                    caption=success_text,
                    reply_markup=get_generate_keyboard(),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logging.error(f"Error sending photo: {e}")
                await query.edit_message_text(
                    f"✅ **Изображение готово!**\n\n"
                    f"📝 Запрос: '{user_text}'\n\n"
                    f"🔗 Ссылка: {result['image_url']}\n\n"
                    f"Что дальше?",
                    reply_markup=get_generate_keyboard(),
                    parse_mode='Markdown'
                )
        
        else:
            error_text = (
                f"❌ **Ошибка генерации**\n\n"
                f"Не удалось создать изображение по запросу: '{user_text}'\n\n"
                f"Попробуйте другой текст или повторите позже."
            )
            await query.edit_message_text(error_text, reply_markup=get_generate_keyboard(), parse_mode='Markdown')
    
    elif data == "change_text":
        # Возвращаем к вводу текста
        context.user_data[user_id]['waiting_for_text'] = True
        old_text = context.user_data[user_id].get('pending_text', '')
        
        change_text = (
            f"✏️ **Измените текст для генерации:**\n\n"
            f"Текущий текст: '{old_text}'\n\n"
            f"Введите новый текст:"
        )
        await query.edit_message_text(change_text, reply_markup=get_back_keyboard())
    
    elif data == "my_generations":
        await my_generations_command(update, context)
    
    elif data == "help_cmd":
        await help_command(update, context)
    
    elif data == "back_cmd":
        await start_command(update, context)

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Проверяем, ждем ли мы текст для генерации
    if context.user_data.get(user_id, {}).get('waiting_for_text'):
        # Сохраняем текст и показываем подтверждение
        if user_id not in context.user_data:
            context.user_data[user_id] = {}
        
        context.user_data[user_id]['pending_text'] = text
        context.user_data[user_id]['waiting_for_text'] = False
        
        confirm_text = (
            f"✅ **Текст принят!**\n\n"
            f"📝 Ваш запрос: '{text}'\n\n"
            f"Готовы сгенерировать изображение?"
        )
        
        await update.message.reply_text(
            confirm_text,
            reply_markup=get_confirm_keyboard(),
            parse_mode='Markdown'
        )
    
    else:
        # Обычное сообщение - показываем меню
        await start_command(update, context)

def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Команды
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("mygens", my_generations_command))
        
        # Обработчики
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Бот-генератор изображений запускается...")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()
