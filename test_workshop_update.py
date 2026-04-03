import requests
import sys

BASE_URL = "http://localhost:8000/api"

def run_test():
    print("1. Creating Workshop 'Update Test Shop'...")
    res = requests.post(f"{BASE_URL}/workshops/", json={"name": "Update Test Shop", "location": "Old Loc"})
    if res.status_code != 200:
        print(f"FAILED to create: {res.text}")
        return
    shop_id = res.json()["id"]
    print(f"   Success. ID: {shop_id}")

    print("2. Updating Workshop...")
    res = requests.put(f"{BASE_URL}/workshops/{shop_id}", json={"name": "Updated Shop Name", "location": "New Loc"})
    if res.status_code != 200:
        print(f"FAILED to update: {res.text}")
        return
    
    data = res.json()
    if data["name"] == "Updated Shop Name" and data["location"] == "New Loc":
        print("   Success. Workshop updated.")
    else:
        print(f"FAILED verifying update: {data}")

    print("\nALL TESTS PASSED")

if __name__ == "__main__":
    run_test()
