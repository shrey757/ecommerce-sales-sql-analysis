"""
analysis.py  |  Run the key queries and produce charts.

Prints a short report to the screen and saves charts to charts/.
Run:  python analysis.py   (after build_database.py)
"""

import sqlite3
import os
import matplotlib
matplotlib.use("Agg")  # save files without a display
import matplotlib.pyplot as plt

DB_FILE = "ecommerce.db"
os.makedirs("charts", exist_ok=True)

conn = sqlite3.connect(DB_FILE)
conn.row_factory = sqlite3.Row

# Brand colors for charts
BLUE = "#2E5C8A"
ACCENT = "#C0504D"


def q(sql):
    return conn.execute(sql).fetchall()


# ---- Q1: headline KPIs ------------------------------------------------
kpi = q("""
    SELECT ROUND(SUM(oi.quantity*oi.unit_price),2) AS revenue,
           COUNT(DISTINCT o.order_id)              AS orders,
           COUNT(DISTINCT o.customer_id)           AS customers,
           ROUND(SUM(oi.quantity*oi.unit_price)/COUNT(DISTINCT o.order_id),2) AS aov
    FROM orders o JOIN order_items oi ON oi.order_id=o.order_id
    WHERE o.status='completed';
""")[0]
print("\n=== HEADLINE KPIs (completed orders) ===")
print(f"Total revenue : ${kpi['revenue']:,.2f}")
print(f"Orders        : {kpi['orders']:,}")
print(f"Customers     : {kpi['customers']:,}")
print(f"Avg order val : ${kpi['aov']:,.2f}")

# ---- Q2: monthly revenue trend ---------------------------------------
monthly = q("""
    SELECT strftime('%Y-%m', o.order_date) AS month,
           SUM(oi.quantity*oi.unit_price)  AS revenue
    FROM orders o JOIN order_items oi ON oi.order_id=o.order_id
    WHERE o.status='completed'
    GROUP BY month ORDER BY month;
""")
months = [r["month"] for r in monthly]
revenue = [r["revenue"] for r in monthly]

plt.figure(figsize=(11, 4.5))
plt.plot(months, revenue, marker="o", color=BLUE, linewidth=2)
plt.title("Monthly Revenue (completed orders)", fontsize=13, weight="bold")
plt.ylabel("Revenue ($)")
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("charts/monthly_revenue.png", dpi=120)
plt.close()

# ---- Q3: revenue by category -----------------------------------------
cats = q("""
    SELECT p.category, SUM(oi.quantity*oi.unit_price) AS revenue
    FROM order_items oi
    JOIN orders o   ON o.order_id=oi.order_id
    JOIN products p ON p.product_id=oi.product_id
    WHERE o.status='completed'
    GROUP BY p.category ORDER BY revenue DESC;
""")
print("\n=== REVENUE BY CATEGORY ===")
for r in cats:
    print(f"{r['category']:<20} ${r['revenue']:>12,.2f}")

plt.figure(figsize=(9, 4.5))
plt.barh([r["category"] for r in cats][::-1],
         [r["revenue"] for r in cats][::-1], color=BLUE)
plt.title("Revenue by Category", fontsize=13, weight="bold")
plt.xlabel("Revenue ($)")
plt.tight_layout()
plt.savefig("charts/revenue_by_category.png", dpi=120)
plt.close()

# ---- Q5: revenue by province -----------------------------------------
prov = q("""
    SELECT c.province, SUM(oi.quantity*oi.unit_price) AS revenue
    FROM orders o
    JOIN customers c    ON c.customer_id=o.customer_id
    JOIN order_items oi ON oi.order_id=o.order_id
    WHERE o.status='completed'
    GROUP BY c.province ORDER BY revenue DESC;
""")
plt.figure(figsize=(9, 4.5))
plt.bar([r["province"] for r in prov], [r["revenue"] for r in prov], color=ACCENT)
plt.title("Revenue by Province", fontsize=13, weight="bold")
plt.ylabel("Revenue ($)")
plt.xticks(rotation=40, ha="right", fontsize=8)
plt.tight_layout()
plt.savefig("charts/revenue_by_province.png", dpi=120)
plt.close()

# ---- Q7: repeat vs one-time ------------------------------------------
repeat = q("""
    WITH per_customer AS (
        SELECT customer_id, COUNT(*) AS orders
        FROM orders WHERE status='completed' GROUP BY customer_id)
    SELECT CASE WHEN orders>1 THEN 'Repeat (2+ orders)' ELSE 'One-time' END AS type,
           COUNT(*) AS customers
    FROM per_customer GROUP BY type ORDER BY customers DESC;
""")
print("\n=== REPEAT vs ONE-TIME CUSTOMERS ===")
total_cust = sum(r["customers"] for r in repeat)
for r in repeat:
    print(f"{r['type']:<20} {r['customers']:>4}  ({100*r['customers']/total_cust:.1f}%)")

# ---- Q4: top products (printed only) ---------------------------------
top = q("""
    SELECT p.product_name, p.category,
           ROUND(SUM(oi.quantity*oi.unit_price),2) AS revenue
    FROM order_items oi
    JOIN orders o   ON o.order_id=oi.order_id
    JOIN products p ON p.product_id=oi.product_id
    WHERE o.status='completed'
    GROUP BY p.product_id ORDER BY revenue DESC LIMIT 10;
""")
print("\n=== TOP 10 PRODUCTS BY REVENUE ===")
for r in top:
    print(f"{r['product_name']:<22} {r['category']:<18} ${r['revenue']:>11,.2f}")

conn.close()
print("\nCharts saved to charts/")
