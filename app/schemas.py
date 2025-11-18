from pydantic import BaseModel, Field
from typing import List, Optional

class CartItem(BaseModel):
    product_name: str
    price_cny: float
    quantity: int = 1
    category: Optional[str] = None  # e.g. 'shoes', 'clothes', 'small'

class UserCreate(BaseModel):
    tg_id: int
    name: Optional[str]
    phone: Optional[str]

class OrderCreate(BaseModel):
    user_id: int
    items: List[CartItem]
    total_rub: float
