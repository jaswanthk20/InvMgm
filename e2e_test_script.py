import requests
import sys

BASE_URL = "http://localhost:8000/api"

def run_test():
    session = requests.Session()
    
    print("1. Creating Category 'E2E API Cat'...")
    res = session.post(f"{BASE_URL}/categories/", json={"name": "E2E API Cat"})
    if res.status_code != 200:
        print(f"FAILED: {res.text}")
        return
    cat_id = res.json()["id"]
    print(f"   Success. ID: {cat_id}")

    print("2. Creating Workshop 'E2E API Shop'...")
    res = session.post(f"{BASE_URL}/workshops/", json={"name": "E2E API Shop", "location": "Test Zone"})
    if res.status_code != 200:
        print(f"FAILED: {res.text}")
        return
    shop_id = res.json()["id"]
    print(f"   Success. ID: {shop_id}")

    print("3. Creating Item 'E2E API Widget'...")
    item_data = {
        "name": "E2E API Widget",
        "category_id": cat_id,
        "workshop_id": shop_id,
        "quantity": 100,
        "min_quantity": 10
    }
    res = session.post(f"{BASE_URL}/items/", json=item_data)
    if res.status_code != 200:
        print(f"FAILED: {res.text}")
        return
    item_id = res.json()["id"]
    print(f"   Success. ID: {item_id}. Initial Qty: {res.json()['quantity']}")

    print("4. Reporting Incident (Damaged: 10)...")
    # Using the same logic as frontend: PUT /items/{id}/quantity with negative change
    reason = "Damaged - E2E Test"
    res = session.put(f"{BASE_URL}/items/{item_id}/quantity", params={"change": -10, "reason": reason})
    if res.status_code != 200:
        print(f"FAILED: {res.text}")
        return
    # Verify Qty
    new_qty = res.json()['quantity']
    if new_qty != 90:
         print(f"FAILED: Expected 90, got {new_qty}")
         return
    print(f"   Success. New Qty: {new_qty}")

    print("5. Placing Order (Qty: 50)...")
    order_data = {
        "item_id": item_id,
        "quantity": 50
    }
    res = session.post(f"{BASE_URL}/orders/", json=order_data)
    if res.status_code != 200:
        print(f"FAILED: {res.text}")
        return
    order_id = res.json()["id"]
    status = res.json()["status"]
    print(f"   Success. Order ID: {order_id}, Status: {status}")

    print("6. Completing Order...")
    res = session.put(f"{BASE_URL}/orders/{order_id}/complete")
    if res.status_code != 200:
        print(f"FAILED: {res.text}")
        return
    print(f"   Success. Order Status: {res.json()['status']}")

    print("7. Verifying Final Quantity...")
    res = session.get(f"{BASE_URL}/items/")
    items = res.json()
    my_item = next((i for i in items if i["id"] == item_id), None)
    if my_item and my_item["quantity"] == 140:
        print(f"   Success. Final Qty is 140.")
    else:
        print(f"FAILED: Expected 140, got {my_item['quantity'] if my_item else 'None'}")
        return
        
    print("\nALL TESTS PASSED")

if __name__ == "__main__":
    run_test()
