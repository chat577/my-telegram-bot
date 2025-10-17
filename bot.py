import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Будем брать токен из настроек Railway
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🎉 Привет! Я работаю из облака Railway!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Я простой тестовый бот. Пока умею только отвечать на /start')

if __name__ == '__main__':
    # Создаем бота
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем команды
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    
    # Запускаем бота
    print("✅ Бот запущен и работает!")
    app.run_polling()