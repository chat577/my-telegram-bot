import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    logger.error("BOT_TOKEN не установлен в переменных окружения")
    exit(1)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        logger.info(f"Пользователь {user.first_name} запустил бота")
        
        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋\n"
            "Я простой чат-бот. Просто напиши мне что-нибудь!\n"
            "Используй /help для списка команд."
        )
    except Exception as e:
        logger.error(f"Ошибка в команде start: {e}")

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        help_text = """
🤖 Доступные команды:
/start - Начать общение
/help - Показать эту справку

Просто напиши мне сообщение, и я отвечу!
        """
        await update.message.reply_text(help_text)
        logger.info("Отправлена справка")
    except Exception as e:
        logger.error(f"Ошибка в команде help: {e}")

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text
        user = update.message.from_user
        
        logger.info(f"Получено сообщение от {user.first_name}: {user_message}")
        
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
        
        await update.message.reply_text(response)
        logger.info(f"Отправлен ответ: {response}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")

# Обработка ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка в обработчике: {context.error}")

def main():
    try:
        logger.info("Запуск бота...")
        
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        application.add_error_handler(error_handler)
        
        # Запускаем бота
        logger.info("Бот запущен и ожидает сообщения...")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    main()
