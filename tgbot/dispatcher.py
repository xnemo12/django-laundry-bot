"""
    Telegram event handlers
"""
import sys
import logging
from typing import Dict

import telegram.error
from telegram import Bot, Update, BotCommand
from telegram.ext import (
    Updater, Dispatcher, Filters,
    CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters,
)

from dtb.celery import app  # event processing in async mode
from dtb.settings import TELEGRAM_TOKEN, DEBUG

from tgbot.handlers.utils import files, error
from tgbot.handlers.admin import handlers as admin_handlers
from tgbot.handlers.location import handlers as location_handlers
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.price import handlers as price_handlers
from tgbot.handlers.courier import handlers as courier_handlers
from tgbot.handlers.broadcast_message import handlers as broadcast_handlers
from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON, SET_LANG_UZB, SET_LANG_RU
from tgbot.handlers.broadcast_message.manage_data import CONFIRM_DECLINE_BROADCAST
from tgbot.handlers.broadcast_message.static_text import broadcast_command

START = 0
GREETING_NEW_USER = 1
ASK_NAME = 2
MAIN_MENU = 3
HANDLE_MENU = 10
CALL_COURIER = 20
HANDLE_DATE = 21
HANDLE_TIME = 22
HANDLE_GEO = 23
HANDLE_CONTACT = 24
PRICE = 30
CONTACT = 40


def setup_dispatcher(dp):
    """
    Adding handlers for events from Telegram
    """

    dp.add_handler(CallbackQueryHandler(courier_handlers.set_courier, pattern=f"^courier*"))

    dp.add_handler(CallbackQueryHandler(courier_handlers.courier_accept, pattern=f"^action_accept*"))
    dp.add_handler(CallbackQueryHandler(courier_handlers.courier_cancel, pattern=f"^action_cancel*"))
    dp.add_handler(CallbackQueryHandler(courier_handlers.courier_picked, pattern=f"^action_picked*"))

    dp.add_handler(MessageHandler(Filters.text, onboarding_handlers.command_cancel))

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", onboarding_handlers.command_start)],
        states={
            START: [CommandHandler("start", onboarding_handlers.command_start)],
            GREETING_NEW_USER: [
                CallbackQueryHandler(onboarding_handlers.set_user_language_uz, pattern=f"^{SET_LANG_UZB}"),
                CallbackQueryHandler(onboarding_handlers.set_user_language_ru, pattern=f"^{SET_LANG_RU}")
            ],
            ASK_NAME: [MessageHandler(Filters.text, onboarding_handlers.ask_name)],
            MAIN_MENU: [MessageHandler(Filters.update, onboarding_handlers.main_menu)],
            HANDLE_MENU: [
                MessageHandler(Filters.regex(r'Посмотреть цены') | Filters.regex(r'Narxlarni ko`rish'), price_handlers.product_categories),
                MessageHandler(Filters.regex(r'Приехать к нам') | Filters.regex(r'Bizning manzil'), location_handlers.address_handler),
                MessageHandler(Filters.regex(r'Вызвать курьера') | Filters.regex(r'Kuryer chaqirish'),
                               courier_handlers.call_courier)
            ],
            CALL_COURIER: [],
            HANDLE_DATE: [
                MessageHandler(Filters.regex(r'Отменить') | Filters.regex(r'Bekor qilish'), courier_handlers.handle_cancel),
                MessageHandler(Filters.text, courier_handlers.handle_date),
            ],
            HANDLE_TIME: [
                MessageHandler(Filters.regex(r'Отменить') | Filters.regex(r'Bekor qilish'), courier_handlers.handle_cancel),
                MessageHandler(Filters.text, courier_handlers.handle_time),
            ],
            HANDLE_GEO: [
                MessageHandler(Filters.regex(r'Отменить') | Filters.regex(r'Bekor qilish'), courier_handlers.handle_cancel),
                MessageHandler(Filters.location, courier_handlers.handle_geo),
            ],
            HANDLE_CONTACT: [
                MessageHandler(Filters.regex(r'Отменить') | Filters.regex(r'Bekor qilish'), courier_handlers.handle_cancel),
                MessageHandler(Filters.contact, courier_handlers.handle_contacts)],
            PRICE: [
                MessageHandler(Filters.regex(r'Назад') | Filters.regex(r'Ortga'), onboarding_handlers.main_menu),
                MessageHandler(Filters.text, price_handlers.product_prices),
            ],
            CONTACT: [MessageHandler(Filters.regex(r'Назад') | Filters.regex(r'Ortga'), onboarding_handlers.main_menu)]
        },
        fallbacks=[CommandHandler("cancel", onboarding_handlers.command_cancel)]
    ))

    # files
    dp.add_handler(MessageHandler(
        Filters.animation, files.show_file_id,
    ))

    # handling errors
    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    return dp


def run_pooling():
    """ Run bot in pooling mode """
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f"https://t.me/" + bot_info["username"]

    print(f"Pooling of '{bot_link}' started")
    # it is really useful to send '👋' emoji to developer
    # when you run local test
    # bot.send_message(text='👋', chat_id=<YOUR TELEGRAM ID>)

    updater.start_polling()
    updater.idle()


# Global variable - best way I found to init Telegram bot
bot = Bot(TELEGRAM_TOKEN)
try:
    TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
except telegram.error.Unauthorized:
    logging.error(f"Invalid TELEGRAM_TOKEN.")
    sys.exit(1)


@app.task(ignore_result=True)
def process_telegram_event(update_json):
    update = Update.de_json(update_json, bot)
    dispatcher.process_update(update)


def set_up_commands(bot_instance: Bot) -> None:
    langs_with_commands: Dict[str, Dict[str, str]] = {
        'ru': {
            'start': 'Запустить бота 🚀',
            'cancel': 'Отмена'
        },
        'uz': {
            'start': 'Botni ishga tushirish 🚀',
            'cancel': 'Bekor qilish'
        }
    }

    bot_instance.delete_my_commands()
    for language_code in langs_with_commands:
        bot_instance.set_my_commands(
            language_code=language_code,
            commands=[
                BotCommand(command, description) for command, description in langs_with_commands[language_code].items()
            ]
        )


# WARNING: it's better to comment the line below in DEBUG mode.
# Likely, you'll get a flood limit control error, when restarting bot too often
set_up_commands(bot)

n_workers = 0 if DEBUG else 4
dispatcher = setup_dispatcher(Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True))
