-- =====================================================================
-- analysis.sql  |  Business questions answered with SQL
-- ---------------------------------------------------------------------
-- Every query below counts revenue ONLY from completed orders
-- (cancelled and returned orders are excluded), because that is the
-- money the business actually kept. Revenue = quantity * unit_price.
--
-- You can run any of these in the SQLite shell:  sqlite3 ecommerce.db
-- or paste them into DB Browser for SQLite / any SQL tool.
-- =====================================================================


-- Q1. Headline KPIs: total revenue, completed orders, customers, AOV ----
-- (AOV = average order value = revenue per completed order)
SELECT
    ROUND(SUM(oi.quantity * oi.unit_price), 2)                AS total_revenue,
    COUNT(DISTINCT o.order_id)                                AS completed_orders,
    COUNT(DISTINCT o.customer_id)                             AS paying_customers,
    ROUND(SUM(oi.quantity * oi.unit_price)
          / COUNT(DISTINCT o.order_id), 2)                    AS avg_order_value
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status = 'completed';


-- Q2. Monthly revenue trend with month-over-month growth ----------------
-- Uses a CTE to total revenue per month, then a window function (LAG)
-- to compare each month to the previous one.
WITH monthly AS (
    SELECT
        strftime('%Y-%m', o.order_date)            AS month,
        SUM(oi.quantity * oi.unit_price)           AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY month
)
SELECT
    month,
    ROUND(revenue, 2)                              AS revenue,
    ROUND(revenue - LAG(revenue) OVER (ORDER BY month), 2)        AS change_vs_prev,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
          / LAG(revenue) OVER (ORDER BY month), 1)               AS pct_change
FROM monthly
ORDER BY month;


-- Q3. Revenue by product category --------------------------------------
SELECT
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)     AS revenue,
    SUM(oi.quantity)                               AS units_sold
FROM order_items oi
JOIN orders   o ON o.order_id   = oi.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.status = 'completed'
GROUP BY p.category
ORDER BY revenue DESC;


-- Q4. Top 10 products by revenue ---------------------------------------
SELECT
    p.product_name,
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)     AS revenue
FROM order_items oi
JOIN orders   o ON o.order_id   = oi.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.status = 'completed'
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 10;


-- Q5. Revenue by province (region) -------------------------------------
SELECT
    c.province,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)     AS revenue,
    COUNT(DISTINCT o.order_id)                     AS orders
FROM orders o
JOIN customers   c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id  = o.order_id
WHERE o.status = 'completed'
GROUP BY c.province
ORDER BY revenue DESC;


-- Q6. Top 10 customers by lifetime spend -------------------------------
SELECT
    c.customer_id,
    c.customer_name,
    c.province,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)     AS lifetime_spend,
    COUNT(DISTINCT o.order_id)                     AS orders
FROM customers c
JOIN orders      o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id  = o.order_id
WHERE o.status = 'completed'
GROUP BY c.customer_id
ORDER BY lifetime_spend DESC
LIMIT 10;


-- Q7. Repeat vs one-time customers -------------------------------------
-- A "repeat" customer has more than one completed order. Repeat-purchase
-- rate is one of the most-watched metrics in e-commerce.
WITH per_customer AS (
    SELECT customer_id, COUNT(*) AS orders
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
)
SELECT
    CASE WHEN orders > 1 THEN 'Repeat (2+ orders)'
         ELSE 'One-time' END                       AS customer_type,
    COUNT(*)                                       AS customers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_customers
FROM per_customer
GROUP BY customer_type
ORDER BY customers DESC;


-- Q8. Impact of cancelled / returned orders ----------------------------
-- Shows how much potential revenue is lost to each order status.
SELECT
    o.status,
    COUNT(DISTINCT o.order_id)                     AS orders,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)     AS gross_value
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.status
ORDER BY gross_value DESC;
