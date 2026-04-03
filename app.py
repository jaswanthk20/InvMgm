import os
from flask import Flask, jsonify, request, render_template
import sqlite3
from db import get_db, close_connection, init_db

app = Flask(__name__)
# Clean up DB connections after each request
app.teardown_appcontext(close_connection)

@app.cli.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db(app)
    print('Initialized the database.')

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/items')
def item_master():
    return render_template('items.html')

@app.route('/locations')
def locations_page():
    return render_template('locations.html')

@app.route('/orders')
def orders_page():
    return render_template('orders.html')

@app.route('/reports')
def reports_page():
    return render_template('reports.html')

# --- API Endpoints ---

@app.route('/api/items', methods=['GET', 'POST'])
def handle_items():
    db = get_db()
    if request.method == 'GET':
        items = db.execute('''
            SELECT i.*, c.name as category_name
            FROM items i
            LEFT JOIN categories c ON i.category_id = c.id
        ''').fetchall()
        return jsonify([dict(ix) for ix in items])
    else:
        # POST new item
        data = request.json
        cur = db.cursor()
        cur.execute('''
            INSERT INTO items (sku, name, category_id, unit, reorder_point, min_stock, replenishment_frequency)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('sku'), data.get('name'), data.get('category_id'),
            data.get('unit', 'pcs'), data.get('reorder_point', 0),
            data.get('min_stock', 0), data.get('replenishment_frequency')
        ))
        db.commit()
        return jsonify({"success": True, "id": cur.lastrowid})

@app.route('/api/locations', methods=['GET', 'POST'])
def handle_locations():
    db = get_db()
    if request.method == 'GET':
        locs = db.execute('SELECT * FROM locations').fetchall()
        return jsonify([dict(l) for l in locs])
    else:
        # POST new location
        data = request.json
        cur = db.cursor()
        cur.execute('''
            INSERT INTO locations (zone, room, shelf, bin, is_labeled)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get('zone'), data.get('room'), data.get('shelf'),
            data.get('bin'), data.get('is_labeled', False)
        ))
        db.commit()
        return jsonify({"success": True, "id": cur.lastrowid})

@app.route('/api/locations/<int:loc_id>', methods=['DELETE'])
def delete_location(loc_id):
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute('DELETE FROM locations WHERE id = ?', (loc_id,))
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/transactions', methods=['POST'])
def handle_transactions():
    data = request.json
    db = get_db()
    try:
        cur = db.cursor()
        # Insert movement
        cur.execute('''
            INSERT INTO stock_movements (item_id, from_location_id, to_location_id, quantity, user_id, movement_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('item_id'), data.get('from_location_id'), data.get('to_location_id'),
            data.get('quantity'), 1, data.get('movement_type') # hardcoding user_id=1 for prototype
        ))
        
        # Update stock on hand
        if data.get('movement_type') == 'IN':
            cur.execute('''
                INSERT INTO stock_on_hand (item_id, location_id, quantity)
                VALUES (?, ?, ?)
                ON CONFLICT(item_id, location_id) DO UPDATE SET quantity = quantity + ?
            ''', (data.get('item_id'), data.get('to_location_id'), data.get('quantity'), data.get('quantity')))
        elif data.get('movement_type') == 'OUT':
            # Decrement logic (sqlite CHECK ensures no negatives)
            cur.execute('''
                UPDATE stock_on_hand SET quantity = quantity - ? 
                WHERE item_id = ? AND location_id = ?
            ''', (data.get('quantity'), data.get('item_id'), data.get('from_location_id')))
        # TODO: Implement MOVE and ADJUST
            
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/logs/disruption', methods=['POST'])
def log_disruption():
    data = request.json
    db = get_db()
    cur = db.cursor()
    cur.execute('''
        INSERT INTO disruptions_log (item_id, location_id, description, reported_by)
        VALUES (?, ?, ?, ?)
    ''', (data.get('item_id'), data.get('location_id'), data.get('description'), 1))
    db.commit()
    return jsonify({"success": True, "id": cur.lastrowid})

@app.route('/api/logs/search-time', methods=['POST'])
def log_search_time():
    data = request.json
    db = get_db()
    cur = db.cursor()
    cur.execute('''
        INSERT INTO search_time_log (item_id, user_id, search_duration_minutes, is_found)
        VALUES (?, ?, ?, ?)
    ''', (data.get('item_id'), 1, data.get('duration_minutes'), data.get('is_found', True)))
    db.commit()
    return jsonify({"success": True, "id": cur.lastrowid})

@app.route('/api/logs/return-audit', methods=['POST'])
def log_return_audit():
    data = request.json
    db = get_db()
    cur = db.cursor()
    cur.execute('''
        INSERT INTO return_audit_log (item_id, user_id, returned_to_correct_location)
        VALUES (?, ?, ?)
    ''', (data.get('item_id'), 1, data.get('is_correct')))
    db.commit()
    return jsonify({"success": True, "id": cur.lastrowid})

@app.route('/api/replenishment/low-stock', methods=['GET'])
def get_low_stock():
    db = get_db()
    items = db.execute('''
        SELECT i.id, i.sku, i.name, i.min_stock, COALESCE(SUM(s.quantity), 0) as total_qty
        FROM items i
        LEFT JOIN stock_on_hand s ON i.id = s.item_id
        GROUP BY i.id
        HAVING total_qty <= i.min_stock
    ''').fetchall()
    return jsonify([dict(ix) for ix in items])

@app.route('/api/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    db = get_db()
    # Disruptions past 7 days
    disruptions = db.execute("SELECT COUNT(*) as c FROM disruptions_log WHERE timestamp >= datetime('now', '-7 days')").fetchone()['c']
    
    # Avg search time past 7 days
    avg_search = db.execute("SELECT AVG(search_duration_minutes) as m FROM search_time_log WHERE timestamp >= datetime('now', '-7 days')").fetchone()['m'] or 0
    
    # Return compliance %
    total_returns = db.execute("SELECT COUNT(*) as c FROM return_audit_log").fetchone()['c']
    returns_pct = 100
    if total_returns > 0:
        correct_returns = db.execute("SELECT COUNT(*) as c FROM return_audit_log WHERE returned_to_correct_location = 1").fetchone()['c']
        returns_pct = (correct_returns / total_returns) * 100

    # Labeling coverage %
    total_locs = db.execute("SELECT COUNT(*) as c FROM locations").fetchone()['c']
    label_pct = 0
    if total_locs > 0:
        labeled_locs = db.execute("SELECT COUNT(*) as c FROM locations WHERE is_labeled = 1").fetchone()['c']
        label_pct = (labeled_locs / total_locs) * 100

    # Visibility score (Removed search penalty)
    visibility_score = ((label_pct * 0.5) + (returns_pct * 0.5)) / 10

    # Pending Orders Count
    pending_orders = db.execute("SELECT COUNT(*) as c FROM purchase_orders WHERE status = 'ORDERED'").fetchone()['c']
    pending_items = db.execute("SELECT COALESCE(SUM(ordered_qty), 0) as total FROM purchase_order_lines jl JOIN purchase_orders p ON jl.po_id = p.id WHERE p.status = 'ORDERED'").fetchone()['total']

    # Replacement Readiness
    replacement_items = db.execute("SELECT id, min_stock FROM items WHERE is_replacement_part = 1").fetchall()
    readiness_pct = 100
    if replacement_items:
        ready_count = 0
        for r_item in replacement_items:
            stock = db.execute("SELECT SUM(quantity) as q FROM stock_on_hand WHERE item_id = ?", (r_item['id'],)).fetchone()['q'] or 0
            if stock >= r_item['min_stock']:
                ready_count += 1
        readiness_pct = (ready_count / len(replacement_items)) * 100

    return jsonify({
        "disruptions": disruptions,
        "avg_search_time": round(avg_search, 1),
        "return_compliance": round(returns_pct, 1),
        "labeling_coverage": round(label_pct, 1),
        "visibility_score": round(visibility_score, 1),
        "replacement_readiness": round(readiness_pct, 1),
        "pending_orders": pending_orders,
        "pending_items": pending_items
    })

@app.route('/api/orders', methods=['GET', 'POST'])
def handle_orders():
    db = get_db()
    if request.method == 'GET':
        orders = db.execute('''
            SELECT po.*, u.username as creator
            FROM purchase_orders po
            LEFT JOIN users u ON po.created_by = u.id
        ''').fetchall()
        
        result = []
        for o in orders:
            d_o = dict(o)
            lines = db.execute('''
                SELECT l.*, i.name as item_name, i.sku
                FROM purchase_order_lines l
                JOIN items i ON l.item_id = i.id
                WHERE l.po_id = ?
            ''', (d_o['id'],)).fetchall()
            d_o['lines'] = [dict(l) for l in lines]
            result.append(d_o)
        return jsonify(result)
        
    else: # POST
        data = request.json
        cur = db.cursor()
        cur.execute('''
            INSERT INTO purchase_orders (status, created_by)
            VALUES (?, ?)
        ''', ('ORDERED', 1))
        po_id = cur.lastrowid
        
        for item_entry in data.get('lines', []):
            cur.execute('''
                INSERT INTO purchase_order_lines (po_id, item_id, ordered_qty)
                VALUES (?, ?, ?)
            ''', (po_id, item_entry['item_id'], item_entry['qty']))
        
        db.commit()
        return jsonify({"success": True, "id": po_id})

@app.route('/api/orders/<int:po_id>/receive', methods=['POST'])
def receive_order(po_id):
    db = get_db()
    try:
        cur = db.cursor()
        po = cur.execute('SELECT * FROM purchase_orders WHERE id = ?', (po_id,)).fetchone()
        if not po:
            return jsonify({"success": False, "message": "PO not found"}), 404
        if po['status'] == 'RECEIVED':
            return jsonify({"success": False, "message": "Already received"}), 400
            
        lines = cur.execute('SELECT id, item_id, ordered_qty FROM purchase_order_lines WHERE po_id = ?', (po_id,)).fetchall()
        
        # Determine the default receiving location (e.g. ID 1, or skip and just add to stock without a specific location for simple prototype)
        # For prototype rigor, let's insert into `stock_movements` as from_location NULL (supplier), to_location 1.
        # Ensure a default location exists first? We'll rely on the user passing 'receive_location_id' in body.
        data = request.json or {}
        recv_loc = data.get('receive_location_id', 1) 
        
        for line in lines:
            # mark received
            cur.execute('''
                INSERT INTO receiving_records (po_line_id, received_qty, received_by)
                VALUES (?, ?, ?)
            ''', (line['id'], line['ordered_qty'], 1))
            
            cur.execute('''
                UPDATE purchase_order_lines SET status = 'RECEIVED' WHERE id = ?
            ''', (line['id'],))
            
            # Stock movement logic
            cur.execute('''
                INSERT INTO stock_movements (item_id, from_location_id, to_location_id, quantity, user_id, movement_type)
                VALUES (?, NULL, ?, ?, ?, 'IN')
            ''', (line['item_id'], recv_loc, line['ordered_qty'], 1))
            
            # Update stock on hand
            cur.execute('''
                INSERT INTO stock_on_hand (item_id, location_id, quantity)
                VALUES (?, ?, ?)
                ON CONFLICT(item_id, location_id) DO UPDATE SET quantity = quantity + ?
            ''', (line['item_id'], recv_loc, line['ordered_qty'], line['ordered_qty']))
            
        cur.execute("UPDATE purchase_orders SET status = 'RECEIVED', received_at = CURRENT_TIMESTAMP WHERE id = ?", (po_id,))
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)}), 400

import re
import pdfplumber
import pytesseract
from PIL import Image

@app.route('/api/import/receipt', methods=['POST'])
def import_receipt():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400
        
    ext = file.filename.lower().split('.')[-1]
    if ext not in ['pdf', 'png', 'jpg', 'jpeg']:
        return jsonify({"success": False, "message": "Must be a PDF or Image file"}), 400
        
    extracted_text = ""
    try:
        if ext == 'pdf':
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    extracted_text += page.extract_text() + "\n"
        else:
            img = Image.open(file)
            extracted_text = pytesseract.image_to_string(img)
    except pytesseract.TesseractNotFoundError:
        return jsonify({"success": False, "message": "Tesseract OCR engine is not installed on this server. Please install it to scan images, or upload a digital PDF instead."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error parsing file: {str(e)}"}), 400

    db = get_db()
    try:
        cur = db.cursor()
        items = cur.execute('SELECT * FROM items').fetchall()
        
        added_count = 0
        text_lines = extracted_text.split('\n')
        
        # Look for known inventory items in the receipt text
        for item in items:
            item_name = item['name'].lower()
            item_sku = (item['sku'] or '').lower()
            
            # Check if this item exists in the receipt text
            item_found = False
            qty = 1
            
            for line in text_lines:
                line_lower = line.lower()
                if (item_name and item_name in line_lower) or (item_sku and item_sku in line_lower):
                    item_found = True
                    # Heuristic: Find digits in the line to guess the quantity
                    nums = re.findall(r'\b\d+\b', line_lower)
                    if nums:
                        # Simple rule: if we find numbers, take the first reasonable one
                        try:
                            # Avoid taking huge numbers (like SKUs or prices without decimal) as quantity
                            possible_qtys = [int(n) for n in nums if 0 < int(n) < 1000]
                            if possible_qtys:
                                qty = possible_qtys[0]
                        except:
                            pass
                    break # Found the item, stop checking lines
                    
            if item_found:
                # Log receiving record directly to stock
                cur.execute('''
                    INSERT INTO stock_movements (item_id, from_location_id, to_location_id, quantity, user_id, movement_type)
                    VALUES (?, NULL, 1, ?, 1, 'IN')
                ''', (item['id'], qty))
                
                cur.execute('''
                    INSERT INTO stock_on_hand (item_id, location_id, quantity)
                    VALUES (?, 1, ?)
                    ON CONFLICT(item_id, location_id) DO UPDATE SET quantity = quantity + ?
                ''', (item['id'], qty, qty))
                
                added_count += 1
                
        db.commit()
        
        if added_count == 0:
             return jsonify({"success": False, "message": "OCR succeeded, but no matching inventory items were found in the receipt text.", "text": extracted_text[:200]}), 400
             
        return jsonify({"success": True, "items_processed": added_count})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
