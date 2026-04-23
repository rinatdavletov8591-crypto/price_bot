# bot.py
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import logging
import traceback

from wb_parser import get_wb_price
from oz_parser import get_oz_price

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Отправь мне название товара для поиска на Wildberries и Ozon.')

async def search_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text(f'Ищу "{query}" на маркетплейсах...')

    try:
        # Запускаем парсеры в отдельных потоках с тайм-аутом в 60 секунд
        wb_task = asyncio.to_thread(get_wb_price, f"https://www.wildberries.ru/catalog/0/search.aspx?search={query}")
        oz_task = asyncio.to_thread(get_oz_price, query)
        
        wb_price, oz_price = await asyncio.wait_for(asyncio.gather(wb_task, oz_task), timeout=60)
        
    except asyncio.TimeoutError:
        await update.message.reply_text("Извините, поиск занял слишком много времени. Попробуйте чуть позже.")
        return
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {traceback.format_exc()}")
        await update.message.reply_text(f"Произошла ошибка при поиске: {type(e).__name__}")
        return

    # Формируем ответ
    response = f"Результаты поиска для: *{query}*\n\n"
    response += f"🛒 Wildberries: {wb_price if wb_price else 'Не найдено'} ₽\n"
    response += f"🛍️ Ozon: {oz_price if oz_price else 'Не найдено'} ₽"

    await update.message.reply_text(response, parse_mode='Markdown')

def main():
    # Добавляем настройки тайм-аута для библиотеки python-telegram-bot
    application = Application.builder().token(TOKEN)\
        .read_timeout(60)\
        .write_timeout(60)\
        .connect_timeout(60)\
        .pool_timeout(60)\
        .build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_product))
    
    logger.info("Бот запущен и готов к работе.")
    application.run_polling()

if __name__ == '__main__':
    main()