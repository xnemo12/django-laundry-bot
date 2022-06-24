from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext

from tgbot.handlers.onboarding import static_text
from tgbot.models import User
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command, main_menu_keyboard


def command_start(update: Update, context: CallbackContext) -> int:
    u, created = User.get_user_and_created(update, context)
    lang = u.language_code if created else 'ru'
    if lang not in ('ru', 'uz'):
        lang = 'ru'

    if created:
        text = static_text.start_created[lang].format(first_name=u.first_name)
        update.message.reply_text(text=text,
                                  reply_markup=make_keyboard_for_start_command())
        return 1
    else:
        text = static_text.start_not_created[lang].format(first_name=u.first_name)
        update.message.reply_text(text=text, reply_markup=main_menu_keyboard(lang))
        return 10


def main_menu(update: Update, _) -> int:
    u = User.get_user_from_update(update)
    update.message.reply_text(text='Выберите действие', reply_markup=main_menu_keyboard(u.lng))
    return 10


def set_user_language_uz(update: Update, context: CallbackContext) -> int:
    user = User.get_user_from_update(update)
    user.language_code = 'uz'
    user.save()

    context.bot.send_message(
        text='Ismingizni kiriting',
        chat_id=user.user_id,
        parse_mode=ParseMode.HTML
    )
    return 2


def set_user_language_ru(update: Update, context: CallbackContext) -> int:
    user = User.get_user_from_update(update)
    user.language_code = 'ru'
    user.save()

    context.bot.send_message(
        text='Как Вас зовут?',
        chat_id=user.user_id,
        parse_mode=ParseMode.HTML
    )
    return 2


def ask_name(update: Update, _) -> int:
    user = User.get_user_from_update(update)
    lng = user.language_code
    update.message.reply_text(
        text=f'Tanishganimdan xursandman {update.message.text}, ?',
        reply_markup=main_menu_keyboard(lng))
    return 10


def command_cancel(update: Update, _):
    print("CANCEL")
    update.message.reply_text(
        'Выберите действие',
        reply_markup=ReplyKeyboardRemove()
    )
    return 3
