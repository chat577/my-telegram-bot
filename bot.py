import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не установлен в переменных окружения")
    exit(1)

# Команда /start
def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f"👤 Пользователь {user.first_name} запустил бота")
    
    update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n"
        "Я простой чат-бот. Просто напиши мне что-нибудь!\n"
        "Используй /help для списка команд."
    )

# Команда /help
def help_command(update: Update, context: CallbackContext):
    help_text = """
🤖 Доступные команды:
/start - Начать общение
/help - Показать эту справку

Просто напиши мне сообщение, и я отвечу!
    """
    update.message.reply_text(help_text)
    logger.info("📋 Отправлена справка")

# Обработка текстовых сообщений
def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    user = update.message.from_user
    
    logger.info(f"💬 Получено сообщение от {user.first_name}: {user_message}")
    
    user_message_lower = user_message.lower()
    
    if 'привет' in user_message_lower:
        response = f"Привет, {user.first_name}! Рад тебя видеть! 😊"
    elif 'как дела' in user_message_lower:
        response = "У меня всё отлично! Спасибо, что спросил! 👍"
    elif 'пока' in user_message_lower:
        response = "До свидания! Возвращайся скорее! 👋"
    elif 'спасибо' in user_message_lower:
        response = "Пожалуйста! Всегда рад помочь! 😄"
    else:
        response = f"Ты написал: '{user_message}'\n\nЯ простой бот, но я тебя услышал! 😊"
    
    update.message.reply_text(response)
    logger.info(f"📤 Отправлен ответ: {response}")

# Обработка ошибок
def error_handler(update: Update, context: CallbackContext):
    logger.error(f"❌ Ошибка: {context.error}")

def main():
    try:
        logger.info("🚀 Запуск бота...")
        
        # Создаем updater
        updater = Updater(BOT_TOKEN, use_context=True)
        
        # Получаем dispatcher
        dp = updater.dispatcher
        
        # Добавляем обработчики
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        
        # Обработчик ошибок
        dp.add_error_handler(error_handler)
        
        # Запускаем бота
        logger.info("✅ Бот запущен и ожидает сообщения...")
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        logger.error(f"💥 Критическая ошибка при запуске бота: {e}")

if __name__ == "__main__":
    main()
