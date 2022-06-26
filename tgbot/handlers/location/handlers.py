import telegram
from telegram import Update
from telegram.ext import CallbackContext

from tgbot.handlers.location.static_text import share_location, thanks_for_location, welcome_to_ofice
from tgbot.handlers.location.keyboards import send_location_keyboard, back_keyboard
from tgbot.models import User, Location


def ask_for_location(update: Update, context: CallbackContext) -> None:
    """ Entered /ask_location command"""
    u = User.get_user(update, context)

    context.bot.send_message(
        chat_id=u.user_id,
        text=share_location,
        reply_markup=send_location_keyboard()
    )


def location_handler(update: Update, context: CallbackContext) -> None:
    # receiving user's location
    user = User.get_user_from_update(update)
    lat, lon = update.message.location.latitude, update.message.location.longitude
    Location.objects.create(user=user, latitude=lat, longitude=lon)

    update.message.reply_text(
        thanks_for_location,
        reply_markup=telegram.ReplyKeyboardRemove(),
    )


def address_handler(update: Update, _) -> int:
    user = User.get_user_from_update(update)
    update.message.reply_text(text=welcome_to_ofice[user.lng])
    update.message.reply_location(latitude=41.316905, longitude=69.279732, reply_markup=back_keyboard(user.language_code))
    return 40
