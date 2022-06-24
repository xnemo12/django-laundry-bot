import telegram
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from core.models import Product
from tgbot.handlers.price.keyboards import product_categories_keyboard
from tgbot.handlers.price.static_text import price_text
from tgbot.models import User


def product_categories(update: Update, context: CallbackContext) -> int:
    user = User.get_user_from_update(update)
    lng = user.language_code

    context.bot.send_message(
        chat_id=user.user_id,
        text=price_text[lng],
        reply_markup=product_categories_keyboard(lng)
    )
    return 30


def product_prices(update: Update, context: CallbackContext) -> int:
    user = User.get_user_from_update(update)
    try:
        prices = Product.objects.filter(category__name__contains=update.message.text)
        message = update.message.text + '\n'
        i = 1
        for price in prices:
            x = round(price.price)
            price_str = '{0:,}'.format(x).replace(',', ' ')
            message = message + f'{i}. {price.name} - {price_str} сум \n'
            i = i + 1

        context.bot.send_message(
            chat_id=user.user_id,
            text=message
        )
    except:
        context.bot.send_message(
            chat_id=user.user_id,
            text='Oops, something is wrong! Please try again!'
        )

    return 30
