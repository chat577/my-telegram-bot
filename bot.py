import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Будем брать токен из настроек Railway
BOT_TOKEN = os.getenv('BOT_TOKEN')

def start_command(update: Update, context: CallbackContext):
    update.message.reply_text('🎉 Привет! Я работаю из облака Railway! Старая версия кода!')

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('Я простой тестовый бот. Пока умею только отвечать на /start и /help')

def main():
    try:
        # Создаем Updater (старый способ)
        updater = Updater(BOT_TOKEN, use_context=True)
        
        # Получаем диспетчер для регистрации обработчиков
        dispatcher = updater.dispatcher
        
        # Добавляем обработчики команд
        dispatcher.add_handler(CommandHandler("start", start_command))
        dispatcher.add_handler(CommandHandler("help", help_command))
        
        print("✅ Бот запускается...")
        
        # Запускаем бота
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()
