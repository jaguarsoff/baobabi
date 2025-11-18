from sqlalchemy import Table, Column, Integer, String, Float, Text, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import metadata

users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('tg_id', Integer, unique=True, nullable=False),
    Column('name', String(128)),
    Column('phone', String(64)),
    Column('created_at', DateTime, server_default=func.now())
)

carts = Table(
    'carts',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('items', JSON, default='[]')  # list of cart items
)

orders = Table(
    'orders',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('items', JSON),
    Column('total_rub', Float),
    Column('status', String(64), default='created'),
    Column('track', String(128)),
    Column('created_at', DateTime, server_default=func.now())
)
