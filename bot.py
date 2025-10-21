import os
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv

# Загрузка обработчиков
from handlers.start import start_command, help_command
from handlers.menu import handle_main_menu
from handlers.tenses import handle_tenses
from handlers.verbs import handle_verbs, send_flashcard
from handlers.phrases import handle_phrases

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

def main():
    # Получение токена из переменных окружения
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в переменных окружения!")
    
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("flashcard", send_flashcard))
    
    # Обработчики callback запросов
    application.add_handler(CallbackQueryHandler(handle_main_menu, pattern="^(back_to_main|menu_)"))
    application.add_handler(CallbackQueryHandler(handle_tenses, pattern="^tense_"))
    application.add_handler(CallbackQueryHandler(handle_verbs, pattern="^verbs_"))
    application.add_handler(CallbackQueryHandler(handle_phrases, pattern="^phrases_"))
    application.add_handler(CallbackQueryHandler(send_flashcard, pattern="^menu_flashcards"))
    
    # Запуск бота
    if os.getenv('RAILWAY_ENVIRONMENT'):
        # На Railway используем вебхук
        PORT = int(os.getenv('PORT', 8443))
        WEBHOOK_URL = os.getenv('WEBHOOK_URL')
        
        if WEBHOOK_URL:
            application.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=BOT_TOKEN,
                webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
            )
        else:
            logger.warning("WEBHOOK_URL не установлен, используем поллинг")
            application.run_polling()
    else:
        # Локально используем поллинг
        logger.info("Запуск бота в режиме поллинга...")
        application.run_polling()

if __name__ == '__main__':
    main()
