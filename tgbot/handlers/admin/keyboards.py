from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.models import User


def keyboard_courier_list() -> InlineKeyboardMarkup:
    couriers = User.objects.filter(is_courier=True).all()
    buttons = [[
        InlineKeyboardButton(courier)
    ] for courier in couriers]

    return InlineKeyboardMarkup(buttons)