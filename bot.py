import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Будем брать токен из настроек Railway
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Создаем inline-клавиатуру для главного меню
def get_main_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("🚀 Старт", callback_data="start_cmd")],
        [InlineKeyboardButton("ℹ️ Информация", callback_data="info_cmd")],
        [InlineKeyboardButton("📞 Помощь", callback_data="help_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Создаем inline-клавиатуру для возврата
def get_back_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔙 Назад в меню", callback_data="back_cmd")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_main_inline_keyboard()
    await update.message.reply_text(
        '🎉 Добро пожаловать! Выберите действие:',
        reply_markup=keyboard
    )

# Команда /info
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_back_keyboard()
    await update.message.reply_text(
        '🤖 **Информация о боте:**\n\n'
        '• Создан на Python\n'
        '• Хостится на Railway\n'
        '• Использует python-telegram-bot\n'
        '• Имеет inline-кнопки\n\n'
        '✅ Кнопки работают в веб и мобильной версиях!',
        reply_markup=keyboard
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_back_keyboard()
    await update.message.reply_text(
        '📞 **Помощь по командам:**\n\n'
        '/start - Начало работы\n'
        '/info - Информация о боте\n'
        '/help - Эта справка\n\n'
        'Или используйте кнопки под сообщениями ↓',
        reply_markup=keyboard
    )

# Обработка нажатий на inline-кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Ответим на callback чтобы убрать "часики"
    
    data = query.data
    
    if data == "start_cmd":
        keyboard = get_main_inline_keyboard()
        await query.edit_message_text(
            '🚀 Бот запущен и готов к работе!\n'
            'Это ваше меню с inline-кнопками.\n'
            'Выберите следующий шаг:',
            reply_markup=keyboard
        )
    
    elif data == "info_cmd":
        keyboard = get_back_keyboard()
        await query.edit_message_text(
            '🤖 **Информация о боте:**\n\n'
            '• Создан на Python\n'
            '• Хостится на Railway\n'
            '• Использует python-telegram-bot\n'
            '• Имеет inline-кнопки\n\n'
            '✅ Кнопки работают в веб и мобильной версиях!',
            reply_markup=keyboard
        )
    
    elif data == "help_cmd":
        keyboard = get_back_keyboard()
        await query.edit_message_text(
            '📞 **Помощь по командам:**\n\n'
            '/start - Начало работы\n'
            '/info - Информация о боте\n'
            '/help - Эта справка\n\n'
            'Или используйте кнопки под сообщениями ↓',
            reply_markup=keyboard
        )
    
    elif data == "back_cmd":
        keyboard = get_main_inline_keyboard()
        await query.edit_message_text(
            '🔙 Возвращаемся в главное меню:',
            reply_markup=keyboard
        )

# Обработка обычных текстовых сообщений - БЕЗ КНОПОК ПОД ПОЛЕМ ВВОДА
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Просто отправляем сообщение БЕЗ reply_markup
    await update.message.reply_text(
        'Используйте команды:\n'
        '/start - показать меню с кнопками\n'
        '/info - информация о боте\n'
        '/help - справка\n\n'
        'Или напишите /start чтобы увидеть кнопки меню.'
    )

def main():
    try:
        # Создаем Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("info", info_command))
        application.add_handler(CommandHandler("help", help_command))
        
        # Обработчик нажатий на inline-кнопки
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Обработчик обычных сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Бот с inline-кнопками запускается...")
        
        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()
