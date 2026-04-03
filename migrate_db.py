import sqlite3

def add_col(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE items ADD COLUMN unit_cost DECIMAL(10, 2) DEFAULT 0.00")
        conn.commit()
        print(f"Successfully added unit_cost to {db_path}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"Column already exists in {db_path}")
        else:
            print(f"Error acting on {db_path}: {e}")
    conn.close()

if __name__ == "__main__":
    add_col('database.db')
    add_col('inventory.db') # Just in case the fastapi backup uses it too
