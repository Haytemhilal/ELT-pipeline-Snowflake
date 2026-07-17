"""
Generate realistic retail sample data (customers, products, orders).
Run once to create CSVs in ../data/. Swap these for a real Kaggle
dataset later if you want (e.g. 'Superstore Sales') - the pipeline
doesn't care where the CSVs come from.

Usage:  python generate_data.py
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# ---------- customers ----------
FIRST = ["Alex", "Maria", "Omar", "Julie", "Sam", "Nadia", "Louis", "Sara", "Karim", "Eve"]
LAST = ["Tremblay", "Gagnon", "Roy", "Belanger", "Nguyen", "Smith", "Haddad", "Cote"]
CITIES = ["Montreal", "Sherbrooke", "Quebec City", "Ottawa", "Toronto", "Laval"]

customers = []
for cid in range(1, 201):
    customers.append({
        "customer_id": cid,
        "first_name": random.choice(FIRST),
        "last_name": random.choice(LAST),
        "email": f"user{cid}@example.com",
        "city": random.choice(CITIES),
        "signup_date": (date(2024, 1, 1) + timedelta(days=random.randint(0, 500))).isoformat(),
    })

# ---------- products ----------
CATEGORIES = {
    "Electronics": ["USB-C Cable", "Wireless Mouse", "Mechanical Keyboard", "Webcam", "Monitor 27in"],
    "Home": ["Coffee Maker", "Desk Lamp", "Air Purifier", "Blender"],
    "Office": ["Notebook", "Standing Desk", "Office Chair", "Whiteboard"],
}
products, pid = [], 1
for cat, names in CATEGORIES.items():
    for name in names:
        products.append({
            "product_id": pid,
            "product_name": name,
            "category": cat,
            "unit_price": round(random.uniform(9.99, 499.99), 2),
        })
        pid += 1

# ---------- orders (intentionally a bit messy: mixed-case status, some nulls) ----------
STATUSES = ["completed", "COMPLETED", "shipped", "returned", "cancelled", "Completed"]
orders = []
for oid in range(1, 5001):
    prod = random.choice(products)
    qty = random.randint(1, 5)
    orders.append({
        "order_id": oid,
        "customer_id": random.choice(customers)["customer_id"],
        "product_id": prod["product_id"],
        "order_date": (date(2025, 1, 1) + timedelta(days=random.randint(0, 540))).isoformat(),
        "quantity": qty,
        "unit_price": prod["unit_price"],
        "status": random.choice(STATUSES),
        "discount_pct": random.choice([0, 0, 0, 5, 10, ""]),  # "" = messy null to clean in staging
    })

def write(name, rows):
    with open(DATA_DIR / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows):>5} rows -> data/{name}")

write("customers.csv", customers)
write("products.csv", products)
write("orders.csv", orders)
