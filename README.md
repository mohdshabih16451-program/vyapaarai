# VyapAI Backend (Phase 1–2)

FastAPI + SQLAlchemy + SQLite.

## Run

```bash
cd vyapai-backend
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python seed.py                 # optional: sample customers + products
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs and test each endpoint in Swagger.

## File map (what each file is for)

| File | Role |
|------|------|
| `app/database.py` | Engine, session, `Base`, `get_db` dependency |
| `app/models.py` | Table definitions (the ER diagram in code) |
| `app/schemas.py` | Pydantic request/response shapes + validation |
| `app/services.py` | Business logic: stock + order transaction, payments, dashboard |
| `app/main.py` | Thin routes that call `services.py` |
| `seed.py` | Demo data |

## Test order (Swagger)

1. `POST /customers`, `POST /products` (or run `seed.py`)
2. `POST /orders` → `{"customer_id":1,"items":[{"product_id":1,"quantity":2}]}`; check `GET /products` – stock dropped
3. Try ordering more than stock → 400, and stock is unchanged (rollback)
4. `POST /payments` → partial amount; `GET /orders/1` shows `partial`
5. `GET /dashboard`

## Viva questions to prepare

- Why is `paid_amount` computed instead of stored? (can't get out of sync)
- Why copy `unit_price` into `order_items`? (old bills stay correct)
- What does `db.rollback()` do in `create_order`? (transaction atomicity)
- Why separate `models.py` and `schemas.py`? (DB shape vs API shape)
