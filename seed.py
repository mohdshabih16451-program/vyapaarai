"""Sample data for demo. Run once:  python seed.py   (safe to re-run; it skips if data exists)"""
from app.database import Base, SessionLocal, engine
from app import models

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(models.Customer).count():
    print("Database already has data - skipping seed.")
else:
    customers = [
        ("Ramesh Kumar", "9876500001"), ("Sunita Devi", "9876500002"), ("Amit Sharma", "9876500003"),
        ("Priya Verma", "9876500004"), ("Mohd. Arif", "9876500005"), ("Neha Gupta", "9876500006"),
        ("Vikas Yadav", "9876500007"), ("Sita Traders", "9876500008"), ("Rajesh Stores", "9876500009"),
        ("Anil Mishra", "9876500010"),
    ]
    products = [
        ("Rice 5kg", 320, 40), ("Wheat Flour 10kg", 410, 25), ("Sugar 1kg", 46, 60), ("Toor Dal 1kg", 140, 30),
        ("Mustard Oil 1L", 165, 4), ("Tea 500g", 240, 18), ("Salt 1kg", 22, 3), ("Biscuits Pack", 10, 120),
    ]
    db.add_all([models.Customer(name=n, phone=p) for n, p in customers])
    db.add_all([models.Product(name=n, price=pr, stock=s) for n, pr, s in products])
    db.commit()
    print(f"Seeded {len(customers)} customers and {len(products)} products.")

db.close()
