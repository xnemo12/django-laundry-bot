from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

from tgbot.handlers.onboarding.manage_data import SET_LANG_UZB, SET_LANG_RU
from tgbot.handlers.onboarding.static_text import *


def make_keyboard_for_start_command() -> InlineKeyboardMarkup:
    buttons = [[
        InlineKeyboardButton(lang_ru_text, callback_data=f'{SET_LANG_RU}'),
        InlineKeyboardButton(lang_uz_text, callback_data=f'{SET_LANG_UZB}')
    ]]

    return InlineKeyboardMarkup(buttons)


def main_menu_keyboard(lng) -> ReplyKeyboardMarkup:
    # webAppTest = WebAppInfo("https://expented.github.io/tgdtp/?hide=time")  # создаем webappinfo - формат хранения url
    buttons = [[
        KeyboardButton(text=call_courier_button[lng]),
        KeyboardButton(text=prices_button[lng])
    ], [KeyboardButton(text=contact_button[lng])]]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)
