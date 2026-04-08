/*
ASSUMPTIONS
===========================================================

1) Inventory is tracked per (warehouse_id, product_id).
2) Bundles are made up of multiple products with quantities.
3) SKU is unique per company (not globally).
4) Inventory quantity cannot go below 0.


QUESTIONS FOR PRODUCT TEAM
===========================================================
1) Should SKUs be globally unique or only within a company?
2) Can multiple comapanies have the same product?
3) Can bundles be nested [bundle inside bundle]?
4) Do we need warehouse constraints (capacity, location hierarchy)?
5) Should we track who made inventory changes (user_id)?
6) Are deletions soft deletes or hard deletes?


DESIGN DECISIONS
===========================================================
1) Separate INVENTORY and INVENTORY_LOG:
   - INVETORY will be accessed a lot so we should try to keep it to a minimal
   - INVENTORY_LOG will be used rarely compared to INVETORY


2) Composite PK for inventory: (warehouse_id, product_id) ensures uniqueness per warehouse

3) Bundle modeling:
   - Self-referencing many-to-many table (bundle_items)

4) Indexing:
   - SKU indexed for quick lookup
   - Foreign keys indexed for joins
   - Inventory log indexed by product + time for analytics

*/


CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL,
    name TEXT NOT NULL,
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);


CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL,
    name TEXT NOT NULL,
    sku TEXT NOT NULL,
    threshold INT DEFAULT 0,
    is_bundle BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (company_id, sku),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);


CREATE TABLE inventory (
    warehouse_id INT,
    product_id INT,
    quantity INT NOT NULL CHECK (quantity >= 0),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (warehouse_id, product_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);


CREATE TABLE inventory_log (
    id SERIAL PRIMARY KEY,
    warehouse_id INT NOT NULL,
    product_id INT NOT NULL,
    change INT NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);


CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    contact_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE bundle_items (
    bundle_id INT,
    product_id INT,
    quantity INT NOT NULL CHECK (quantity > 0),

    PRIMARY KEY (bundle_id, product_id),
    FOREIGN KEY (bundle_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);


-- INDEXES
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_inventory_product ON inventory(product_id);
CREATE INDEX idx_inventory_log_product_time ON inventory_log(product_id, created_at);