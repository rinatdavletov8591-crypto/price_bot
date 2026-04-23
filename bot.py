# bot.py
import os
import asyncio
import threading
from flask import Flask
# ... (весь ваш код парсинга и обработки команд) ...

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import logging

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

    # Запускаем парсеры в параллельных потоках
    loop = asyncio.get_event_loop()
    wb_price = await loop.run_in_executor(None, get_wb_price, f"https://www.wildberries.ru/catalog/0/search.aspx?search={query}")
    oz_price = await loop.run_in_executor(None, get_oz_price, query)

    # Формируем и отправляем ответ
    response = f"Результаты поиска для: *{query}*\n\n"
    response += f"🛒 Wildberries: {wb_price if wb_price else 'Не найдено'} ₽\n"
    response += f"🛍️ Ozon: {oz_price if oz_price else 'Не найдено'} ₽"

    await update.message.reply_text(response, parse_mode='Markdown')

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_product))

    logger.info("Бот запущен и готов к работе.")
    application.run_polling()

if __name__ == '__main__':
    main()

# Создаем Flask-приложение
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Бот работает!"

def run_flask():
    # Запускаем Flask-сервер на порту, который предоставит Render
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

def main():
    # ... (код создания и настройки вашего Application) ...
    
    # Запускаем Flask в отдельном потоке
    threading.Thread(target=run_flask).start()
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()