import os
import logging
import telebot

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не найден!")
    exit(1)

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        logger.info(f"👤 Пользователь {message.from_user.first_name} запустил бота")
        bot.reply_to(
            message,
            f"Привет, {message.from_user.first_name}! 👋\n"
            "Я работаю! Рад тебя видеть!"
        )
    except Exception as e:
        logger.error(f"❌ Ошибка в /start: {e}")

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    try:
        help_text = """
🤖 Доступные команды:
/start - Начать общение
/help - Показать справку

Просто напиши мне что-нибудь!
        """
        bot.reply_to(message, help_text)
        logger.info("📋 Отправлена справка")
    except Exception as e:
        logger.error(f"❌ Ошибка в /help: {e}")

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        user_text = message.text
        user = message.from_user
        
        logger.info(f"💬 Сообщение от {user.first_name}: {user_text}")
        
        # Простые ответы
        if 'привет' in user_text.lower():
            response = f"Привет, {user.first_name}! 😊"
        elif 'как дела' in user_text.lower():
            response = "Отлично! Спасибо! 👍"
        elif 'пока' in user_text.lower():
            response = "До свидания! 👋"
        else:
            response = f"Ты сказал: {user_text}\nЯ простой бот! 🤖"
        
        bot.reply_to(message, response)
        logger.info(f"📤 Ответ отправлен: {response}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке сообщения: {e}")

# Запуск бота
if __name__ == '__main__':
    logger.info("🚀 Бот запускается...")
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
