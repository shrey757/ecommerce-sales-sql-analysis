"""
Generate a realistic e-commerce dataset as CSV files.

Output: data/customers.csv, data/products.csv, data/orders.csv, data/order_items.csv
"""

import csv
import os
import random
from datetime import date, timedelta

random.seed(42)  # reproducible output
os.makedirs("data", exist_ok=True)

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
FIRST_NAMES = [
    "Liam", "Olivia", "Noah", "Emma", "Oliver", "Ava", "Elijah", "Sophia",
    "William", "Isabella", "James", "Mia", "Benjamin", "Charlotte", "Lucas",
    "Amelia", "Henry", "Harper", "Alexander", "Evelyn", "Aarav", "Priya",
    "Wei", "Mei", "Diego", "Sofia", "Omar", "Layla", "Chen", "Yuki",
]
LAST_NAMES = [
    "Smith", "Brown", "Tremblay", "Wong", "Patel", "Singh", "Martin", "Roy",
    "Gagnon", "Lee", "Nguyen", "Garcia", "Kumar", "Wilson", "MacDonald",
    "Cote", "Khan", "Reid", "Bouchard", "Chan",
]

# (city, province) — province is used as the "region" for analysis
CITIES = [
    ("Toronto", "Ontario"), ("Ottawa", "Ontario"), ("Mississauga", "Ontario"),
    ("Montreal", "Quebec"), ("Quebec City", "Quebec"),
    ("Vancouver", "British Columbia"), ("Victoria", "British Columbia"),
    ("Calgary", "Alberta"), ("Edmonton", "Alberta"),
    ("Winnipeg", "Manitoba"), ("Halifax", "Nova Scotia"),
    ("Saskatoon", "Saskatchewan"),
]

# category -> (min_price, max_price)
CATEGORIES = {
    "Electronics": (50, 1200),
    "Home & Kitchen": (15, 400),
    "Clothing": (12, 150),
    "Books": (8, 45),
    "Sports & Outdoors": (20, 500),
    "Beauty": (8, 120),
    "Toys & Games": (10, 90),
}

# noun pools used to build plausible product names per category
CATEGORY_NOUNS = {
    "Electronics": ["Headphones", "Smartwatch", "Bluetooth Speaker", "Laptop",
                    "Tablet", "Webcam", "Power Bank", "Monitor"],
    "Home & Kitchen": ["Coffee Maker", "Blender", "Knife Set", "Cookware Set",
                       "Air Fryer", "Vacuum", "Toaster"],
    "Clothing": ["T-Shirt", "Hoodie", "Jeans", "Jacket", "Sneakers", "Cap"],
    "Books": ["Novel", "Cookbook", "Biography", "Guidebook", "Textbook"],
    "Sports & Outdoors": ["Yoga Mat", "Dumbbell Set", "Tent", "Bicycle",
                          "Running Shoes", "Backpack"],
    "Beauty": ["Face Serum", "Lipstick", "Shampoo", "Perfume", "Moisturizer"],
    "Toys & Games": ["Board Game", "Puzzle", "Building Blocks", "Action Figure",
                     "Card Game"],
}
ADJECTIVES = ["Pro", "Classic", "Premium", "Eco", "Ultra", "Compact", "Deluxe",
              "Everyday", "Smart", "Lite"]

# ---------------------------------------------------------------------------
# 1. Customers
# ---------------------------------------------------------------------------
N_CUSTOMERS = 600
customers = []
for cid in range(1, N_CUSTOMERS + 1):
    city, province = random.choice(CITIES)
    # signups spread across ~3 years, weighted slightly toward recent
    signup = date(2023, 1, 1) + timedelta(days=random.randint(0, 1000))
    customers.append({
        "customer_id": cid,
        "customer_name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "city": city,
        "province": province,
        "signup_date": signup.isoformat(),
    })

with open("data/customers.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["customer_id", "customer_name", "city",
                                      "province", "signup_date"])
    w.writeheader()
    w.writerows(customers)

# ---------------------------------------------------------------------------
# 2. Products
# ---------------------------------------------------------------------------
products = []
pid = 1
for category, (lo, hi) in CATEGORIES.items():
    for noun in CATEGORY_NOUNS[category]:
        name = f"{random.choice(ADJECTIVES)} {noun}"
        price = round(random.uniform(lo, hi), 2)
        products.append({
            "product_id": pid,
            "product_name": name,
            "category": category,
            "price": price,
        })
        pid += 1

with open("data/products.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["product_id", "product_name",
                                      "category", "price"])
    w.writeheader()
    w.writerows(products)

# ---------------------------------------------------------------------------
# 3. Orders + 4. Order items
# ---------------------------------------------------------------------------

customer_ids = [c["customer_id"] for c in customers]
weights = [random.choice([1, 1, 1, 2, 4, 8]) for _ in customer_ids]

# Monthly order volume: 24 months (2024-01 .. 2025-12), gentle upward trend
# plus seasonal lift in Nov/Dec and a smaller summer bump.
SEASONAL = {1: 0.85, 2: 0.85, 3: 0.95, 4: 1.0, 5: 1.05, 6: 1.1,
            7: 1.1, 8: 1.05, 9: 1.0, 10: 1.05, 11: 1.4, 12: 1.6}

orders = []
order_items = []
order_id = 1
order_item_id = 1
base = 110  # base orders per month

for year in (2024, 2025):
    trend = 1.0 if year == 2024 else 1.25  # 2025 grows vs 2024
    for month in range(1, 13):
        n_orders = int(base * trend * SEASONAL[month] * random.uniform(0.92, 1.08))
        for _ in range(n_orders):
            day = random.randint(1, 28)
            odate = date(year, month, day)
            customer = random.choices(customer_ids, weights=weights, k=1)[0]
            # most orders complete; some cancelled / returned
            status = random.choices(
                ["completed", "cancelled", "returned"],
                weights=[0.85, 0.08, 0.07], k=1)[0]
            orders.append({
                "order_id": order_id,
                "customer_id": customer,
                "order_date": odate.isoformat(),
                "status": status,
            })
            # 1-5 line items per order
            n_items = random.randint(1, 5)
            chosen = random.sample(products, n_items)
            for prod in chosen:
                qty = random.randint(1, 3)
                # occasional small discount on the line
                unit_price = prod["price"]
                if random.random() < 0.15:
                    unit_price = round(unit_price * random.uniform(0.85, 0.95), 2)
                order_items.append({
                    "order_item_id": order_item_id,
                    "order_id": order_id,
                    "product_id": prod["product_id"],
                    "quantity": qty,
                    "unit_price": unit_price,
                })
                order_item_id += 1
            order_id += 1

with open("data/orders.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["order_id", "customer_id",
                                      "order_date", "status"])
    w.writeheader()
    w.writerows(orders)

with open("data/order_items.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["order_item_id", "order_id", "product_id",
                                      "quantity", "unit_price"])
    w.writeheader()
    w.writerows(order_items)

print(f"Generated {len(customers)} customers, {len(products)} products, "
      f"{len(orders)} orders, {len(order_items)} order items.")
