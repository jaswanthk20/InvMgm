import sqlite3
import random
from datetime import datetime, timedelta

DATABASE = 'database.db'

def seed_data():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # Clear existing data
    tables = [
        'stock_movements', 'stock_on_hand', 'return_audit_log', 
        'search_time_log', 'disruptions_log', 'receiving_records',
        'purchase_order_lines', 'purchase_orders', 'reorder_rules',
        'suppliers', 'item_home_locations', 'locations', 'items',
        'machine_assets', 'categories', 'users'
    ]
    for table in tables:
        cur.execute(f'DELETE FROM {table}')

    # 1. Users
    users = [('admin', 'admin'), ('danielle', 'staff'), ('ben', 'staff'), ('student1', 'user')]
    for user in users:
        cur.execute('INSERT INTO users (username, role) VALUES (?, ?)', user)
    
    # 2. Categories
    categories = ['Hand Tools', 'Power Tool Accessories', 'Adhesives & Tape', 'Electronics']
    for cat in categories:
        cur.execute('INSERT INTO categories (name) VALUES (?)', (cat,))

    # 3. Machine Assets
    machines = ['Band Saw', '3D Printer', 'Laser Cutter']
    for m in machines:
        cur.execute('INSERT INTO machine_assets (name) VALUES (?)', (m,))

    # 4. Locations
    locations = [
        ('Mechanical Room', 'Main Floor', 'A1', 'Bin 1', 1), # Labeled
        ('Mechanical Room', 'Main Floor', 'A1', 'Bin 2', 1), # Labeled
        ('Electronics Lab', '2nd Floor', 'B1', 'Drawer 1', 0), # Not Labeled
        ('General Storage', 'Basement', 'C1', 'Shelf 1', 0), # Not Labeled
    ]
    for loc in locations:
        cur.execute('INSERT INTO locations (zone, room, shelf, bin, is_labeled) VALUES (?, ?, ?, ?, ?)', loc)

    # 5. Items
    items = [
        # (sku, name, cat_id, unit, reorder_pt, min_stock, is_replacement, machine_id, freq)
        ('SKU-1001', 'Measuring Tape 25ft', 1, 'pcs', 2, 1, 0, None, 'yearly'),
        ('SKU-1002', 'Exacto Knife Set', 1, 'sets', 5, 2, 0, None, 'yearly'),
        ('SKU-2001', 'Wood Glue 8oz', 3, 'bottles', 10, 5, 0, None, 'quarterly'),
        ('SKU-2002', 'Masking Tape 1"', 3, 'rolls', 20, 10, 0, None, 'quarterly'),
        ('SKU-3001', 'Band Saw Blade 93.5"', 2, 'pcs', 3, 2, 1, 1, 'yearly'), # Replacement part
        ('SKU-4001', 'PLA Filament 1kg', 4, 'spools', 15, 5, 0, 2, 'monthly')
    ]
    for item in items:
        cur.execute('''
            INSERT INTO items (sku, name, category_id, unit, reorder_point, min_stock, is_replacement_part, machine_asset_id, replenishment_frequency) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', item)

    # 6. Initial Stock (stock_on_hand & stock_movements)
    # Give some items healthy stock, some low stock
    initial_stock = {
        1: 5,  # Measuring Tape (Healthy)
        2: 1,  # Exacto Knife (Low)
        3: 15, # Glue (Healthy)
        4: 8,  # Masking Tape (Low)
        5: 1,  # Band Saw Blade (Low/Below min)
        6: 20  # PLA (Healthy)
    }
    
    for item_id, qty in initial_stock.items():
        loc_id = random.randint(1, 4)
        # Add to stock
        cur.execute('INSERT INTO stock_on_hand (item_id, location_id, quantity) VALUES (?, ?, ?)', (item_id, loc_id, qty))
        # Log movement
        cur.execute('''
            INSERT INTO stock_movements (item_id, to_location_id, quantity, user_id, movement_type) 
            VALUES (?, ?, ?, 1, 'IN')
        ''', (item_id, loc_id, qty))

    # 7. Metrics Logs (Past 7 Days)
    now = datetime.now()
    
    # Disruptions (e.g., vent downtime, missing tools)
    for _ in range(12): # 12 disruptions this week
        days_ago = random.randint(0, 6)
        ts = now - timedelta(days=days_ago)
        cur.execute('''
            INSERT INTO disruptions_log (item_id, location_id, description, reported_by, timestamp) 
            VALUES (?, ?, ?, 1, ?)
        ''', (random.randint(1, 6), random.randint(1, 4), "Item missing or location messy", ts.strftime('%Y-%m-%d %H:%M:%S')))

    # Search Time (avg ~4.5 mins)
    for _ in range(20):
        days_ago = random.randint(0, 6)
        ts = now - timedelta(days=days_ago)
        duration = random.choice([2, 3, 4, 5, 6, 7])
        is_found = 1 if duration < 6 else 0
        cur.execute('''
            INSERT INTO search_time_log (item_id, user_id, search_duration_minutes, is_found, timestamp) 
            VALUES (?, 1, ?, ?, ?)
        ''', (random.randint(1, 6), duration, is_found, ts.strftime('%Y-%m-%d %H:%M:%S')))

    # Return Audit (Compliance ~20%)
    for _ in range(30):
        days_ago = random.randint(0, 6)
        ts = now - timedelta(days=days_ago)
        is_correct = 1 if random.random() < 0.25 else 0 # ~25% compliance
        cur.execute('''
            INSERT INTO return_audit_log (item_id, user_id, returned_to_correct_location, timestamp) 
            VALUES (?, 1, ?, ?)
        ''', (random.randint(1, 6), is_correct, ts.strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()
    print("Database seeded with realistic demo data successfully.")

if __name__ == '__main__':
    seed_data()
