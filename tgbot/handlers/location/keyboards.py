from telegram import ReplyKeyboardMarkup, KeyboardButton

from tgbot.handlers.location.static_text import SEND_LOCATION, back_button


def send_location_keyboard() -> ReplyKeyboardMarkup:
    # resize_keyboard=False will make this button appear on half screen (become very large).
    # Likely, it will increase click conversion but may decrease UX quality.
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text=SEND_LOCATION, request_location=True)]],
        resize_keyboard=True
    )


def back_keyboard(lang) -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=back_button[lang])]]
    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
