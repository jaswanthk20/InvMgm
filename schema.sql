-- DDL Statements

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL, -- 'admin', 'staff', 'user'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS machine_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku VARCHAR(50) UNIQUE,
    name VARCHAR(200) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    unit VARCHAR(20) NOT NULL, -- e.g., 'pcs', 'boxes', 'meters'
    reorder_point INTEGER DEFAULT 0,
    min_stock INTEGER DEFAULT 0,
    unit_cost DECIMAL(10, 2) DEFAULT 0.00,
    is_replacement_part BOOLEAN DEFAULT 0,
    machine_asset_id INTEGER REFERENCES machine_assets(id),
    replenishment_frequency VARCHAR(50), -- e.g., 'quarterly', 'yearly'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone VARCHAR(50),  -- e.g., 'Mechanical Room'
    room VARCHAR(50),  -- e.g., 'Main Floor'
    shelf VARCHAR(50), -- e.g., 'A1'
    bin VARCHAR(50),   -- e.g., 'Bin 3'
    is_labeled BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS item_home_locations (
    item_id INTEGER REFERENCES items(id),
    location_id INTEGER REFERENCES locations(id),
    PRIMARY KEY (item_id, location_id)
);

CREATE TABLE IF NOT EXISTS stock_on_hand (
    item_id INTEGER REFERENCES items(id),
    location_id INTEGER REFERENCES locations(id),
    quantity INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (item_id, location_id),
    CHECK (quantity >= 0) -- Constraint prevents negative logic
);

CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER REFERENCES items(id),
    from_location_id INTEGER REFERENCES locations(id), -- NULL if new stock
    to_location_id INTEGER REFERENCES locations(id),   -- NULL if consumed
    quantity INTEGER NOT NULL,
    user_id INTEGER REFERENCES users(id),
    movement_type VARCHAR(20) NOT NULL, -- 'IN', 'OUT', 'MOVE', 'ADJUST'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS reorder_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER REFERENCES items(id),
    supplier_id INTEGER REFERENCES suppliers(id),
    min_order_qty INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status VARCHAR(20) DEFAULT 'DRAFT', -- 'DRAFT', 'ORDERED', 'RECEIVED'
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    received_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS purchase_order_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_id INTEGER REFERENCES purchase_orders(id),
    item_id INTEGER REFERENCES items(id),
    ordered_qty INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING'
);

CREATE TABLE IF NOT EXISTS receiving_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_line_id INTEGER REFERENCES purchase_order_lines(id),
    received_qty INTEGER NOT NULL,
    received_by INTEGER REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Metrics Logging Tables
CREATE TABLE IF NOT EXISTS disruptions_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER REFERENCES items(id),
    location_id INTEGER REFERENCES locations(id),
    description TEXT NOT NULL,
    reported_by INTEGER REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS search_time_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER REFERENCES items(id),
    user_id INTEGER REFERENCES users(id),
    search_duration_minutes INTEGER NOT NULL,
    is_found BOOLEAN DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS return_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER REFERENCES items(id),
    user_id INTEGER REFERENCES users(id),
    returned_to_correct_location BOOLEAN NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category_id);
CREATE INDEX IF NOT EXISTS idx_stock_item ON stock_on_hand(item_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_item ON stock_movements(item_id);
CREATE INDEX IF NOT EXISTS idx_disruptions_timestamp ON disruptions_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_search_time_timestamp ON search_time_log(timestamp);

-- Insert dummy admin user if not exists
INSERT OR IGNORE INTO users (username, role) VALUES ('admin', 'admin');
