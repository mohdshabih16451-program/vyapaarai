"""API routes. Run with:  uvicorn app.main:app --reload   then open http://127.0.0.1:8000/docs"""
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas, services
from .database import Base, engine, get_db

# Creates the tables in vyapai.db if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(title="VyapAI API", version="0.1.0")

# Lets the React dev server (Vite runs on :5173) call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"status": "ok", "app": "VyapAI"}


# ---- Customers ----
@app.post("/customers", response_model=schemas.CustomerOut, status_code=201)
def add_customer(data: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return services.create_customer(db, data)


@app.get("/customers", response_model=list[schemas.CustomerOut])
def get_customers(db: Session = Depends(get_db)):
    return services.list_customers(db)


# ---- Products ----
@app.post("/products", response_model=schemas.ProductOut, status_code=201)
def add_product(data: schemas.ProductCreate, db: Session = Depends(get_db)):
    return services.create_product(db, data)


@app.get("/products", response_model=list[schemas.ProductOut])
def get_products(db: Session = Depends(get_db)):
    return services.list_products(db)


# ---- Orders ----
@app.post("/orders", response_model=schemas.OrderOut, status_code=201)
def add_order(data: schemas.OrderCreate, db: Session = Depends(get_db)):
    return services.create_order(db, data)


@app.get("/orders", response_model=list[schemas.OrderOut])
def get_orders(db: Session = Depends(get_db)):
    return services.list_orders(db)


@app.get("/orders/{order_id}", response_model=schemas.OrderOut)
def get_one_order(order_id: int, db: Session = Depends(get_db)):
    return services.get_order(db, order_id)


# ---- Payments ----
@app.post("/payments", response_model=schemas.PaymentOut, status_code=201)
def add_payment(data: schemas.PaymentCreate, db: Session = Depends(get_db)):
    return services.record_payment(db, data)


# ---- Dashboard ----
@app.get("/dashboard", response_model=schemas.DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    return services.get_dashboard(db)
