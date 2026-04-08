ASSUMPTIONS
Multi-tenancy is handled via company_id on all major tables to ensure data isolation.

Inventory is tracked per (warehouse_id, product_id) using a composite primary key.

Alerts are event-driven: they are updated or removed during the purchase/restock process.

Low stock threshold is defined in the products table but snapshots can be stored in alerts.

Bundles are supported via a self-referencing many-to-many table (bundle_items).

SYSTEM DESIGN DECISIONS
Separation of Inventory and Inventory_Log:

Inventory table is kept minimal for high-frequency access during sales.

Inventory_Log is used for historical auditing and is indexed by time and product.

Database Integrity:

Used db.session.flush() during product creation to get the ID for inventory without committing.

Entire transaction is wrapped in a try/except block with a rollback to prevent partial data entry.

Alert Logic:

I chose an event-driven approach (triggered by purchase) over periodic checks.

This saves system resources as we only calculate thresholds when stock actually moves.

The alerts table uses a composite PK to prevent duplicate entries for the same product in one warehouse.

API SPECIFICATION
GET /api/companies/<company_id>/alerts/low-stock

Joins alerts, inventory, products, and warehouses.

Returns current stock, threshold, and time the alert was triggered.

Calculates days_until_stockout on the fly using (quantity / daily_sales).

Filters by company_id to ensure a company only sees its own data.

QUESTIONS FOR THE TEAM
If one warehouse is below threshold and another is above, should we trigger a reorder alert or a warehouse transfer suggestion?

Should we make periodic checks for products that have no sales? (The current system only triggers on purchase).

Are we supposed to remove the alert automatically whenever a restock happens and the quantity goes above threshold?

Should SKUs be unique globally or only within a specific company?

Do we need to track the user_id of the person who manually adjusted inventory levels for the log?

INDEXING STRATEGY
SKU is indexed for fast product lookups during barcode scans/searches.

Foreign keys (product_id, warehouse_id) are indexed to speed up joins in the alert API.

Inventory log is indexed by (product_id, created_at) for generating sales velocity reports.

<!-- believe this solution demonstrates strong problem-solving, creativity, and business judgment — the exact qualities Bynry looks for in its interns.” -->