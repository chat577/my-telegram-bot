from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import get_main_menu_keyboard

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🇬🇧 *Добро пожаловать в English Helper Bot!* 🇺🇸

Это ваш личный блокнот для изучения английского языка!

✨ *Что умеет этот бот:*
• 📚 Объясняет английские времена
• 🔤 Учит неправильные и основные глаголы
• 💬 Дает полезные разговорные фразы
• 🎴 Помогает запоминать слова с карточками

Выберите раздел для начала обучения:
    """
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 *Как пользоваться ботом:*

1. Используйте кнопки меню для навигации
2. Выбирайте интересующие вас темы
3. Регулярно повторяйте материал
4. Используйте карточки для запоминания

📞 *Поддержка:* Если есть вопросы по использованию бота, напишите разработчику.

*Удачи в изучении английского!* 🚀
    """
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )
