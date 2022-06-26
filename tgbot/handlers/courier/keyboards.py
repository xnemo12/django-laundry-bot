import datetime
import locale

from telegram import ReplyKeyboardMarkup, KeyboardButton

from tgbot.handlers.courier.static_text import location_button, contact_button, cancel_button
from tgbot.handlers.utils.lists import to_pair_list


def days_keyboard(lng) -> ReplyKeyboardMarkup:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    date_list = [datetime.datetime.today() + datetime.timedelta(days=x) for x in range(4)]
    date_pairs = to_pair_list(date_list, 2)
    buttons = [[KeyboardButton(text=d1.strftime('📆  %d %B').upper()),
                KeyboardButton(text=d2.strftime('📆  %d %B').upper())]
               for (d1, d2) in date_pairs]
    buttons.append([KeyboardButton(text=cancel_button[lng])])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)


def times_keyboard(lng) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text='🕘 09:00-12:00'), KeyboardButton(text='🕛 12:00-15:00')],
        [KeyboardButton(text='🕒 15:00-18:00'), KeyboardButton(text='🕕 18:00-21:00')],
        [KeyboardButton(text=cancel_button[lng])]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)


def location_keyboard(lng) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text=location_button[lng], request_location=True)], [KeyboardButton(text=cancel_button[lng])]],
        resize_keyboard=True
    )


def contact_keyboard(lng) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text=contact_button[lng], request_contact=True)], [KeyboardButton(text=cancel_button[lng])]],
        resize_keyboard=True
    )
