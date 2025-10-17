import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Будем брать токен из настроек Railway
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🎉 Привет! Я работаю из облака Railway! Версия 20.8!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Я простой тестовый бот. Пока умею только отвечать на /start и /help')

if __name__ == '__main__':
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        
        print("✅ Бот запускается...")
        
        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
