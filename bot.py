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

# Создаем клавиатуру с кнопками
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🚀 Старт"), KeyboardButton("ℹ️ Информация")],
        [KeyboardButton("📞 Помощь"), KeyboardButton("🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_main_keyboard()
    await update.message.reply_text(
        '🎉 Добро пожаловать! Выберите действие:',
        reply_markup=keyboard
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '📞 Помощь:\n'
        '• Нажмите "Старт" для начала работы\n'
        '• "Информация" - о боте\n'
        '• "Помощь" - это сообщение\n'
        '• "Назад" - вернуться в главное меню',
        reply_markup=get_main_keyboard()
    )

# Обработка нажатий на кнопки
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🚀 Старт":
        await update.message.reply_text(
            '🚀 Бот запущен и готов к работе!\n'
            'Это ваше первое меню с кнопками.\n'
            'Выберите следующий шаг:',
            reply_markup=get_main_keyboard()
        )
    
    elif text == "ℹ️ Информация":
        await update.message.reply_text(
            '🤖 **Информация о боте:**\n'
            '• Создан на Python\n'
            '• Хостится на Railway\n'
            '• Использует python-telegram-bot\n'
            '• Имеет кнопочное меню\n\n'
            'Это демо-версия бота с кнопками!',
            reply_markup=get_main_keyboard()
        )
    
    elif text == "📞 Помощь":
        await help_command(update, context)
    
    elif text == "🔙 Назад":
        await update.message.reply_text(
            '🔙 Возвращаемся в главное меню:',
            reply_markup=get_main_keyboard()
        )
    
    else:
        # Если получен неизвестный текст
        await update.message.reply_text(
            'Я не понимаю эту команду. Используйте кнопки меню:',
            reply_markup=get_main_keyboard()
        )

# Обработка обычных текстовых сообщений (если пользователь пишет текст вместо кнопок)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if text in ['привет', 'hello', 'hi']:
        await update.message.reply_text(
            'Привет! Используйте кнопки для навигации:',
            reply_markup=get_main_keyboard()
        )
    elif text in ['спасибо', 'благодарю']:
        await update.message.reply_text('Пожалуйста! 😊')
    else:
        await update.message.reply_text(
            'Используйте кнопки меню для взаимодействия:',
            reply_markup=get_main_keyboard()
        )

def main():
    try:
        # Создаем Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        
        # Обработчик кнопок
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
        
        # Обработчик обычных сообщений (опционально)
        application.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, handle_message))
        
        print("✅ Бот с кнопками запускается...")
        
        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()
