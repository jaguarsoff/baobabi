from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton('📦 Заказать вещи', callback_data='order'),
        InlineKeyboardButton('🔎 Мои заказы', callback_data='my_orders'),
    )
    kb.add(
        InlineKeyboardButton('🧾 Расчёт', callback_data='calc'),
        InlineKeyboardButton('🛒 Корзина', callback_data='cart')
    )
    kb.add(InlineKeyboardButton('❓ Помощь', callback_data='help'))
    return kb

def cart_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton('Оформить заказ', callback_data='checkout'))
    kb.add(InlineKeyboardButton('Очистить корзину', callback_data='clear_cart'))
    kb.add(InlineKeyboardButton('Назад', callback_data='back'))
    return kb

def item_edit_kb(item_index: int):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton('Удалить', callback_data=f'del_{item_index}'))
    kb.add(InlineKeyboardButton('Изменить кол-во', callback_data=f'editq_{item_index}'))
    kb.add(InlineKeyboardButton('Назад', callback_data='cart'))
    return kb
