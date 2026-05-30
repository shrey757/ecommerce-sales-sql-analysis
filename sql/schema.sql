-- =====================================================================
-- schema.sql  |  E-commerce sales database
-- ---------------------------------------------------------------------
-- Four related tables in a classic sales model:
--
--   customers ──< orders ──< order_items >── products
--
-- A customer places many orders; each order contains many line items;
-- each line item refers to one product. Revenue lives in order_items
-- (quantity * unit_price), so most analysis joins through that table.
-- =====================================================================

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id   INTEGER PRIMARY KEY,
    customer_name TEXT    NOT NULL,
    city          TEXT    NOT NULL,
    province      TEXT    NOT NULL,   -- used as "region" in analysis
    signup_date   TEXT    NOT NULL    -- ISO date (YYYY-MM-DD)
);

CREATE TABLE products (
    product_id   INTEGER PRIMARY KEY,
    product_name TEXT    NOT NULL,
    category     TEXT    NOT NULL,
    price        REAL    NOT NULL
);

CREATE TABLE orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date  TEXT    NOT NULL,     -- ISO date (YYYY-MM-DD)
    status      TEXT    NOT NULL,     -- completed | cancelled | returned
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id      INTEGER NOT NULL,
    product_id    INTEGER NOT NULL,
    quantity      INTEGER NOT NULL,
    unit_price    REAL    NOT NULL,   -- price actually charged (may include a discount)
    FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Indexes on the columns we join/filter on most often.
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date     ON orders(order_date);
CREATE INDEX idx_items_order     ON order_items(order_id);
CREATE INDEX idx_items_product   ON order_items(product_id);
