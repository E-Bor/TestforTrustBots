from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardMarkup,KeyboardButton,ReplyKeyboardRemove

def create_markup(titles: list):
    button = [KeyboardButton(text=f"{i}") for i in titles]
    mk = ReplyKeyboardMarkup(resize_keyboard=True)
    mk.add(*button)
    if "🔙 Оставить номер телефона" not in titles:
        mk.row(KeyboardButton(text="🔙Назад"))
    return mk

markup_start = ReplyKeyboardMarkup(resize_keyboard=True).\
    add(KeyboardButton("⛔ Оставить заявку"),KeyboardButton("📞 Связаться")).\
    row(KeyboardButton("⚙️ Настройки")).row(KeyboardButton("☎ Полезные контакты"))


def create_inline_markup(titles: list, back=None):
    if not isinstance(titles, list):
        titles = [titles]
    buttons = [InlineKeyboardButton(text=f"{i}", callback_data=f"{i}") for i in titles]
    main_markup = InlineKeyboardMarkup(row_width=2)
    main_markup.add(*buttons)
    if "🔙 Оставить номер телефона" not in titles:
        main_markup.row(InlineKeyboardButton(text="🔙Назад", callback_data="🔙Назад"))
    return main_markup

