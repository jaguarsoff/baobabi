# Simple admin utilities - can be extended into web admin or CLI
from app.database import database
from app import models
from app.config import settings

async def set_order_status(order_id: int, status: str, bot=None):
    q = models.orders.update().where(models.orders.c.id==order_id).values(status=status)
    await database.execute(q)
    # fetch order and notify user
    ord_q = models.orders.select().where(models.orders.c.id==order_id)
    o = await database.fetch_one(ord_q)
    if o and bot:
        user_q = models.users.select().where(models.users.c.id==o['user_id'])
        u = await database.fetch_one(user_q)
        if u:
            await bot.send_message(chat_id=u['tg_id'], text=f'Статус заказа {order_id} изменён на: {status}')
