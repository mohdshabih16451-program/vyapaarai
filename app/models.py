"""Table definitions (Phase 1).

ER relationships (explain these in the viva):

    Customer 1 ───< Order 1 ───< OrderItem >─── 1 Product
                      │
                      └───< Payment

  - One customer has many orders.
  - One order has many order_items (the line items / the bill rows).
  - Each order_item points to ONE product (many items can refer to the same product).
  - One order can have many payments (partial payments over time).
"""
from datetime import datetime
from sqlalchemy import ForeignKey, String, Float, Integer, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(15), unique=True)
    address: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    orders: Mapped[list["Order"]] = relationship(back_populates="customer")


class Product(Base):
    __tablename__ = "products"
    # DB-level safety net: stock can never go negative even if our Python code has a bug
    __table_args__ = (CheckConstraint("stock >= 0", name="ck_stock_non_negative"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=5)

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship(back_populates="order", cascade="all, delete-orphan")

    # Derived values: we do NOT store them, so they can never go out of sync.
    @property
    def paid_amount(self) -> float:
        return sum(p.amount for p in self.payments)

    @property
    def pending_amount(self) -> float:
        return round(self.total_amount - self.paid_amount, 2)

    @property
    def payment_status(self) -> str:
        if self.paid_amount <= 0:
            return "pending"
        if self.paid_amount < self.total_amount:
            return "partial"
        return "paid"


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    # Price is copied at sale time: if the product price changes later, old bills stay correct.
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[str] = mapped_column(String(20), default="cash")  # cash / upi / card
    paid_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    order: Mapped["Order"] = relationship(back_populates="payments")
