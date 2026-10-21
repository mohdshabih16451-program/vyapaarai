"""Pydantic schemas: define what JSON the API ACCEPTS and RETURNS.

models.py = database tables.  schemas.py = API request/response shapes.
Keeping them separate means we never leak internal DB details by accident.
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # lets Pydantic read SQLAlchemy objects


# ---------- Customers ----------
class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone: str | None = None
    address: str | None = None


class CustomerOut(ORMModel):
    id: int
    name: str
    phone: str | None
    address: str | None


# ---------- Products ----------
class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=5, ge=0)


class ProductOut(ORMModel):
    id: int
    name: str
    price: float
    stock: int
    low_stock_threshold: int


# ---------- Orders ----------
class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_id: int
    items: list[OrderItemIn] = Field(min_length=1)


class OrderItemOut(ORMModel):
    product_id: int
    quantity: int
    unit_price: float


class OrderOut(ORMModel):
    id: int
    customer_id: int
    total_amount: float
    paid_amount: float
    pending_amount: float
    payment_status: str
    created_at: datetime
    items: list[OrderItemOut]


# ---------- Payments ----------
class PaymentCreate(BaseModel):
    order_id: int
    amount: float = Field(gt=0)
    method: str = "cash"


class PaymentOut(ORMModel):
    id: int
    order_id: int
    amount: float
    method: str
    paid_at: datetime


# ---------- Dashboard ----------
class LowStockItem(BaseModel):
    id: int
    name: str
    stock: int


class DashboardOut(BaseModel):
    todays_sales: float
    todays_order_count: int
    total_pending_payments: float
    low_stock_items: list[LowStockItem]
