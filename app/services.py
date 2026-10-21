"""Business logic (the "service layer").

Routes in main.py stay thin and just call these functions.
IMPORTANT for Phase 4: the AI command endpoint will call these SAME functions
(create_order, record_payment, ...). The AI never writes SQL.
"""
from datetime import datetime, time
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from . import models, schemas


# ---------- Customers ----------
def create_customer(db: Session, data: schemas.CustomerCreate) -> models.Customer:
    if data.phone and db.scalar(select(models.Customer).where(models.Customer.phone == data.phone)):
        raise HTTPException(409, "A customer with this phone already exists")
    customer = models.Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def list_customers(db: Session) -> list[models.Customer]:
    return list(db.scalars(select(models.Customer).order_by(models.Customer.name)))


# ---------- Products ----------
def create_product(db: Session, data: schemas.ProductCreate) -> models.Product:
    if db.scalar(select(models.Product).where(models.Product.name == data.name)):
        raise HTTPException(409, "A product with this name already exists")
    product = models.Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def list_products(db: Session) -> list[models.Product]:
    return list(db.scalars(select(models.Product).order_by(models.Product.name)))


# ---------- Orders ----------
def create_order(db: Session, data: schemas.OrderCreate) -> models.Order:
    """Insert order + items AND reduce stock as ONE transaction.

    Transaction = all-or-nothing. If any item has insufficient stock we raise an
    error BEFORE commit, db.rollback() undoes everything, and no half-saved order exists.
    """
    if not db.get(models.Customer, data.customer_id):
        raise HTTPException(404, "Customer not found")

    try:
        order = models.Order(customer_id=data.customer_id)
        total = 0.0

        for line in data.items:
            product = db.get(models.Product, line.product_id)
            if not product:
                raise HTTPException(404, f"Product {line.product_id} not found")
            if product.stock < line.quantity:
                raise HTTPException(
                    400, f"Not enough stock for '{product.name}': have {product.stock}, need {line.quantity}"
                )

            product.stock -= line.quantity  # decrease stock
            order.items.append(
                models.OrderItem(product_id=product.id, quantity=line.quantity, unit_price=product.price)
            )
            total += product.price * line.quantity

        order.total_amount = round(total, 2)
        db.add(order)
        db.commit()  # <- everything is saved together here
    except Exception:
        db.rollback()  # <- or everything is undone here
        raise

    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> models.Order:
    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order


def list_orders(db: Session) -> list[models.Order]:
    return list(db.scalars(select(models.Order).order_by(models.Order.id.desc())))


# ---------- Payments ----------
def record_payment(db: Session, data: schemas.PaymentCreate) -> models.Payment:
    order = get_order(db, data.order_id)
    if data.amount > order.pending_amount + 0.001:
        raise HTTPException(400, f"Amount exceeds pending balance of {order.pending_amount}")

    payment = models.Payment(order_id=order.id, amount=data.amount, method=data.method)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


# ---------- Dashboard ----------
def get_dashboard(db: Session) -> schemas.DashboardOut:
    start_of_today = datetime.combine(datetime.now().date(), time.min)

    # SQL equivalent: SELECT COALESCE(SUM(total_amount),0), COUNT(id) FROM orders WHERE created_at >= :today
    sales, count = db.execute(
        select(func.coalesce(func.sum(models.Order.total_amount), 0.0), func.count(models.Order.id))
        .where(models.Order.created_at >= start_of_today)
    ).one()

    pending = sum(o.pending_amount for o in db.scalars(select(models.Order)))

    low = db.scalars(select(models.Product).where(models.Product.stock <= models.Product.low_stock_threshold))
    return schemas.DashboardOut(
        todays_sales=round(sales, 2),
        todays_order_count=count,
        total_pending_payments=round(pending, 2),
        low_stock_items=[schemas.LowStockItem(id=p.id, name=p.name, stock=p.stock) for p in low],
    )
