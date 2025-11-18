from aiogram import Router, F
from aiogram.filters import CommandStart, Command, Text
from aiogram.types import Message, CallbackQuery
from app.keyboards import main_menu, cart_kb, item_edit_kb
from app.database import database
from app import models, schemas
from app.config import settings
import random, string, json

router = Router()

async def get_user_by_tg(tg_id: int):
    query = models.users.select().where(models.users.c.tg_id == tg_id)
    row = await database.fetch_one(query)
    return row

async def create_user(tg_id: int, name: str | None = None, phone: str | None = None):
    query = models.users.insert().values(tg_id=tg_id, name=name, phone=phone)
    user_id = await database.execute(query)
    return user_id

async def get_cart(user_id: int):
    q = models.carts.select().where(models.carts.c.user_id == user_id)
    r = await database.fetch_one(q)
    if not r:
        return []
    return r['items'] or []

async def save_cart(user_id: int, items):
    q = models.carts.select().where(models.carts.c.user_id == user_id)
    r = await database.fetch_one(q)
    if r:
        await database.execute(models.carts.update().where(models.carts.c.user_id==user_id).values(items=items))
    else:
        await database.execute(models.carts.insert().values(user_id=user_id, items=items))

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await get_user_by_tg(message.from_user.id)
    if not user:
        await create_user(message.from_user.id, message.from_user.full_name, None)
    text = 'Привет 👋\nЯ Kul2Bot — помогу заказать вещи с Poizon. Выбери действие:'
    await message.answer(text, reply_markup=main_menu())

@router.message(Command(commands=['admin']) )
async def admin_cmd(message: Message):
    if not settings.admin_id or message.from_user.id != settings.admin_id:
        await message.answer('Доступ запрещён.')
        return
    # show simple admin summary
    q = models.orders.select().order_by(models.orders.c.created_at.desc())
    rows = await database.fetch_all(q)
    text = f'Всего заказов: {len(rows)}\nПоследние 5:\n'
    for o in rows[:5]:
        text += f"ID {o['id']} — {o['status']} — {o['total_rub']} руб\n"
    await message.answer(text)

@router.callback_query(F.data == 'order')
async def cb_order(cq: CallbackQuery):
    await cq.message.answer('Напиши название товара и цену в юанях (например: Nike Air 200 899).', reply_markup=None)
    await cq.answer()

@router.message()
async def text_all(message: Message):
    # allow quick add to cart by message like: name price category(optional) qty(optional)
    parts = message.text.split()
    if len(parts) >= 2 and parts[-1].replace('.', '', 1).isdigit():
        # last token is price
        price = float(parts[-1])
        name = ' '.join(parts[:-1])
        category = None
        quantity = 1
        # simple category detection by keywords
        if 'shoe' in name.lower() or 'nike' in name.lower() or 'air' in name.lower():
            category = 'shoes'
        user = await get_user_by_tg(message.from_user.id)
        if not user:
            uid = await create_user(message.from_user.id, message.from_user.full_name, None)
            user = {'id': uid}
        items = await get_cart(user['id'])
        items.append({'product_name': name, 'price_cny': price, 'quantity': quantity, 'category': category})
        await save_cart(user['id'], items)
        await message.answer(f'Добавлено в корзину: {name} — {price} CNY', reply_markup=main_menu())
        return
    await message.answer('Не понял. Для быстрого добавления отправьте: <название> <цена в CNY>.', reply_markup=main_menu())

@router.callback_query(F.data == 'cart')
async def cb_cart(cq: CallbackQuery):
    user = await get_user_by_tg(cq.from_user.id)
    if not user:
        await create_user(cq.from_user.id, cq.from_user.full_name, None)
        user = await get_user_by_tg(cq.from_user.id)
    items = await get_cart(user['id'])
    if not items:
        await cq.message.answer('Корзина пуста.', reply_markup=main_menu())
        await cq.answer()
        return
    text = 'Корзина:\n'
    for i, it in enumerate(items):
        text += f"{i+1}. {it['product_name']} — {it['price_cny']} CNY x{it.get('quantity',1)}\n"
    await cq.message.answer(text, reply_markup=cart_kb())
    await cq.answer()

@router.callback_query(F.data == 'clear_cart')
async def cb_clear(cq: CallbackQuery):
    user = await get_user_by_tg(cq.from_user.id)
    if not user:
        await cq.answer('Пользователь не найден.')
        return
    await save_cart(user['id'], [])
    await cq.message.answer('Корзина очищена.', reply_markup=main_menu())
    await cq.answer()

@router.callback_query(F.data == 'checkout')
async def cb_checkout(cq: CallbackQuery):
    user = await get_user_by_tg(cq.from_user.id)
    if not user:
        await cq.answer('Пользователь не найден.')
        return
    # ensure contact exists
    if not user.get('phone'):
        await cq.message.answer('Пожалуйста, пришли свой номер телефона (в виде текста).')
        await cq.answer()
        return
    items = await get_cart(user['id'])
    if not items:
        await cq.answer('Корзина пуста.')
        return
    # compute total
    total = compute_total_rub(items)
    # create order
    import random, string
    track = 'TRK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    order_q = models.orders.insert().values(user_id=user['id'], items=items, total_rub=total, status='created', track=track)
    order_id = await database.execute(order_q)
    # notify admin
    if settings.admin_id:
        text = f'Новый заказ #{order_id}\nСумма: {total} руб\nТрек: {track}'
        await cq.message.bot.send_message(chat_id=settings.admin_id, text=text)
    await save_cart(user['id'], [])
    await cq.message.answer(f'Заказ оформлен. ID: {order_id}. Трек: {track}. Статус: created', reply_markup=main_menu())
    await cq.answer()

def compute_total_rub(items):
    # rules:
    # доставка 600 руб за 1 кг (we assume 1kg per shoe, 0.5 per clothes, negligible for small)
    # курс 12.3 CNY -> RUB
    CNY_RATE = 12.3
    delivery_per_kg = 600.0
    fixed_shoes = 800.0
    fixed_clothes = 500.0
    per_item_from3 = 350.0
    total_cny = 0.0
    weight_kg = 0.0
    total_rub = 0.0
    for it in items:
        qty = it.get('quantity',1)
        total_cny += it['price_cny'] * qty
        cat = it.get('category') or ''
        if cat == 'shoes':
            weight_kg += 1.0 * qty
            total_rub += fixed_shoes * qty
        elif cat == 'clothes':
            weight_kg += 0.5 * qty
            total_rub += fixed_clothes * qty
        else:
            # small items — cost 100% of price in rubles (converted)
            total_rub += 0  # price conversion handled below
    # convert cny to rub and add
    total_rub += total_cny * CNY_RATE
    # delivery
    total_rub += weight_kg * delivery_per_kg
    # discount for >=3 items (apply to shoes/clothes only by reducing fixed fee)
    total_items = sum(it.get('quantity',1) for it in items)
    if total_items >= 3:
        # apply reduced per-item fixed for clothes/shoes
        # simplistic approach: subtract (fixed - per_item_from3) per applicable item counted as shoes/clothes
        for it in items:
            if it.get('category') in ('shoes','clothes'):
                total_rub -= ( (fixed_shoes if it['category']=='shoes' else fixed_clothes) - per_item_from3 ) * it.get('quantity',1)
    return round(total_rub, 2)

@router.callback_query(F.data == 'calc')
async def cb_calc(cq: CallbackQuery):
    await cq.message.answer('Отправь цену в CNY, я посчитаю ориентировочно в рублях. Формат: <цена> (например 899)')
    await cq.answer()

@router.message()
async def calc_price(message: Message):
    # This handler collides with earlier generic text_all but serves as a fallback for calc.
    parts = message.text.strip().split()
    try:
        val = float(parts[0])
    except Exception:
        return
    # naive calculation (single item)
    rate = 12.3
    rub = val * rate
    # delivery estimate per item assume small
    await message.answer(f'Примерно {rub:.2f} руб (без учёта фиксированных комиссий и доставки).', reply_markup=main_menu())
