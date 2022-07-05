import datetime

from telegram import Update
from telegram.ext import CallbackContext
import re

from order.models import Order
from tgbot.handlers.courier.keyboards import days_keyboard, times_keyboard, location_keyboard, contact_keyboard, \
    keyboard_courier_list, order_accept_keyboard, order_pick_keyboard
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
    order.location = location
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
    address = order.location.arcgis.address if order.location.arcgis is not None else ""

    if admin:
        order_text = f"Новый заказ!\n" \
                     f"Номер заказа: {order.id} \n" \
                     f"ФИО: {order.user.first_name} {order.user.last_name} \n" \
                     f"Адрес: {address} \n" \
                     f"Номер телефона: {order.phone} \n" \
                     f"Комментарий: {order.comment}"

        context.bot.send_location(admin.user_id,
                                  latitude=order.location.latitude,
                                  longitude=order.location.longitude)
        context.bot.send_message(admin.user_id, f"{order_text}", reply_markup=keyboard_courier_list(order.id))

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


def set_courier(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data.split(":")
    order_id = data[2]
    order = Order.objects.get(id=order_id)
    order.state = Order.OrderState.CONFIRMED
    order.save()

    if order:
        address = order.location.arcgis.address if order.location.arcgis is not None else ""
        order_text = f"Новый заказ!\n" \
                     f"Номер заказа: {order.id} \n" \
                     f"ФИО: {order.user.first_name} {order.user.last_name} \n" \
                     f"Адрес: {address} \n" \
                     f"Номер телефона: {order.phone} \n" \
                     f"Комментарий: {order.comment}"
        context.bot.send_location(chat_id=data[1],
                                  latitude=order.location.latitude,
                                  longitude=order.location.longitude)
        context.bot.send_message(chat_id=data[1], text=order_text, reply_markup=order_accept_keyboard(order_id))


def courier_accept(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data.split(":")

    courier = User.get_user_from_update(update)

    order_id = data[1]
    order = Order.objects.get(id=order_id)
    order.state = Order.OrderState.EXECUTING
    order.courier = courier
    order.confirmed_time = datetime.datetime.now()
    order.save()

    query.edit_message_text(text='Заявка принята', reply_markup=order_pick_keyboard(order_id))


def courier_cancel(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data.split(":")
    order_id = data[1]
    order = Order.objects.get(id=order_id)
    order.state = Order.OrderState.CANCELLED
    order.save()
    query.edit_message_text(text='Заявка отменена')


def courier_picked(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data.split(":")
    order_id = data[1]
    order = Order.objects.get(id=order_id)
    order.state = Order.OrderState.PICKED
    order.picked_time = datetime.datetime.now()
    order.save()
    query.edit_message_text(text='Вещи получены')
