-- schema.sql

CREATE TABLE IF NOT EXISTS workshops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    location TEXT
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE -- e.g., 'Handy Tool', 'Consumable', 'Spare Part'
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL,
    workshop_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    min_quantity INTEGER DEFAULT 5, -- Alert threshold
    sku TEXT, -- Stock Keeping Unit or Barcode
    FOREIGN KEY (category_id) REFERENCES categories (id),
    FOREIGN KEY (workshop_id) REFERENCES workshops (id)
);

CREATE TABLE IF NOT EXISTS inventory_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    change_amount INTEGER NOT NULL, -- positive for addition, negative for removal
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    reason TEXT, -- e.g., 'Restock', 'Used', 'Missing', 'Damaged'
    FOREIGN KEY (item_id) REFERENCES items (id)
);

-- Pre-populate some data
INSERT OR IGNORE INTO workshops (name, location) VALUES 
('Workshop A', 'Main Building'),
('Workshop B', 'Annex'),
('Workshop C', 'Off-site');

INSERT OR IGNORE INTO categories (name) VALUES 
('Handy Tool'),
('Consumable'),
('Spare Part');
