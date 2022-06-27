import datetime

from telegram import Update
from telegram.ext import CallbackContext
import re

from order.models import Order
from tgbot.handlers.courier.keyboards import days_keyboard, times_keyboard, location_keyboard, contact_keyboard, \
    keyboard_courier_list
from tgbot.handlers.courier.static_text import choose_date_text, choose_time_text, send_location_text, \
    send_contact_text, order_received_text, order_cancel_text
from tgbot.handlers.onboarding.keyboards import main_menu_keyboard
from tgbot.models import Location, User


def call_courier(update: Update, _) -> int:
    user = User.get_user_from_update(update)
    update.message.reply_text(text=choose_date_text[user.lng], reply_markup=days_keyboard(user.lng))
    return 21


def handle_date(update: Update, context: CallbackContext) -> int:
    user = User.get_user_from_update(update)
    info = f'Дата: {update.message.text}'
    order = Order(user=user, state=Order.OrderState.NEW.value, description=info)
    order.save()

    context.user_data["order_id"] = order.id
    update.message.reply_text(text=choose_time_text[user.lng], reply_markup=times_keyboard(user.lng))
    return 22


def handle_time(update: Update, context: CallbackContext) -> int:
    user = User.get_user_from_update(update)
    order_id = context.user_data["order_id"]
    order = Order.objects.get(id=order_id)
    order.description = f'{order.description} \nВремя: {update.message.text}'
    order.save()
    update.message.reply_text(text=send_location_text[user.lng], reply_markup=location_keyboard(user.lng))
    return 23


def handle_geo(update: Update, context: CallbackContext) -> int:
    user = User.get_user_from_update(update)
    lat, lon = update.message.location.latitude, update.message.location.longitude
    location = Location.objects.create(user=user, latitude=lat, longitude=lon)

    order_id = context.user_data["order_id"]
    order = Order.objects.get(id=order_id)
    order.location = location.arcgis
    order.save()

    update.message.reply_text(text=send_contact_text[user.lng], reply_markup=contact_keyboard(user.lng))
    return 24


def handle_contacts(update: Update, context: CallbackContext) -> int:
    user = User.get_user_from_update(update)
    contact = update.message.contact.phone_number

    order_id = context.user_data["order_id"]
    order = Order.objects.get(id=order_id)
    order.phone = contact
    order.order_time = datetime.datetime.now()
    order.save()

    context.user_data["order_id"] = None

    update.message.reply_text(text=order_received_text[user.lng], reply_markup=main_menu_keyboard(user.lng))

    admin = User.objects.filter(is_admin=True).first()
    context.bot.send_message(admin.user_id, "Новый заказ!", reply_markup=keyboard_courier_list())

    return 10


def handle_cancel(update: Update, context: CallbackContext) -> int:
    user = User.get_user_from_update(update)

    order_id = context.user_data.get("order_id", None)
    if order_id is not None:
        order = Order.objects.get(id=order_id)
        order.state = Order.OrderState.CANCELLED
        order.save()
        context.user_data["order_id"] = None

    update.message.reply_text(text=order_cancel_text[user.lng], reply_markup=main_menu_keyboard(user.lng))
    return 10
