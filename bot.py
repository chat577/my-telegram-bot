import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Будем брать токен из настроек Railway
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Создаем основную клавиатуру
def get_main_keyboard():
    keyboard = [
       [KeyboardButton("🎯 Старт"), KeyboardButton("📚 Инфо")],
        [KeyboardButton("💡 Помощь"), KeyboardButton("⬅️ Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="Выберите команду...")

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_main_keyboard()
    await update.message.reply_text(
        '🎉 Добро пожаловать! Выберите команду из меню ниже:',
        reply_markup=keyboard
    )

# Команда /info
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_main_keyboard()
    await update.message.reply_text(
        '🤖 **Информация о боте:**\n\n'
        '• Создан на Python\n'
        '• Хостится на Railway\n'
        '• Использует python-telegram-bot\n'
        '• Имеет кнопочное меню\n\n'
        'Это демо-версия бота с кнопками!',
        reply_markup=keyboard
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_main_keyboard()
    await update.message.reply_text(
        '📞 **Помощь по командам:**\n\n'
        '/start - Начало работы\n'
        '/info - Информация о боте\n'
        '/help - Эта справка\n'
        '/back - Вернуться в главное меню\n\n'
        'Или используйте кнопки ниже ↓',
        reply_markup=keyboard
    )

# Команда /back
async def back_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_main_keyboard()
    await update.message.reply_text(
        '🔙 Возвращаемся в главное меню:',
        reply_markup=keyboard
    )

# Обработка обычных текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Если пользователь нажал на текстовую кнопку (без слеша)
    if text == "Старт" or text == "start":
        await start_command(update, context)
    elif text == "Информация" or text == "info":
        await info_command(update, context)
    elif text == "Помощь" or text == "help":
        await help_command(update, context)
    elif text == "Назад" or text == "back":
        await back_command(update, context)
    else:
        # Для любого другого текста показываем меню
        keyboard = get_main_keyboard()
        await update.message.reply_text(
            'Используйте кнопки меню или команды:\n'
            '/start, /info, /help, /back',
            reply_markup=keyboard
        )

def main():
    try:
        # Создаем Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("info", info_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("back", back_command))
        
        # Обработчик всех текстовых сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Бот с кнопками запускается...")
        
        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()

