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
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n"
        "Я простой чат-бот. Просто напиши мне что-нибудь!"
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🤖 Доступные команды:
/start - Начать общение
/help - Показать эту справку

Просто напиши мне сообщение, и я отвечу!
    """
    await update.message.reply_text(help_text)

# Обработка текстовых сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # Простые ответы на основе ключевых слов
    user_message_lower = user_message.lower()
    
    if 'привет' in user_message_lower:
        response = f"Привет, {update.message.from_user.first_name}! Рад тебя видеть! 😊"
    elif 'как дела' in user_message_lower:
        response = "У меня всё отлично! Спасибо, что спросил! 👍"
    elif 'пока' in user_message_lower or 'до свидания' in user_message_lower:
        response = "До свидания! Возвращайся скорее! 👋"
    elif 'спасибо' in user_message_lower:
        response = "Пожалуйста! Всегда рад помочь! 😄"
    else:
        response = f"Ты написал: '{user_message}'\n\nЯ простой бот, но я тебя услышал! 😊"
    
    await update.message.reply_text(response)

# Обработка ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")

def main():
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        
        # Запускаем бота
        logger.info("Бот запускается...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    main()
