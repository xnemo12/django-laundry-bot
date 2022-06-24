from telegram import ReplyKeyboardMarkup, KeyboardButton

from core.models import ProductCategory
from tgbot.handlers.price.static_text import back_button
from tgbot.handlers.utils.lists import to_pair_list


def product_categories_keyboard(lang) -> ReplyKeyboardMarkup:
    categories = ProductCategory.objects.all().order_by('order')
    cat_pairs = to_pair_list(categories, 2)
    buttons = [[KeyboardButton(text=c1.name), KeyboardButton(text=c2.name)] for (c1, c2) in cat_pairs]
    buttons.append([KeyboardButton(text=back_button[lang])])
    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True,
        # one_time_keyboard=True
    )
