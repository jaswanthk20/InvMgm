# API Reference

The backend API is built with **FastAPI**. All responses are in JSON format.

## Base URL
http://localhost:8000

## Endpoints

### Workshops

#### Get All Workshops
Get a list of all workshops.
- **URL**: `/workshops/`
- **Method**: `GET`
- **Query Params**:
  - `skip` (int, default=0): Number of records to skip.
  - `limit` (int, default=100): Max number of records to return.
- **Response**: List of Workshop objects.

#### Create Workshop
Add a new workshop.
- **URL**: `/workshops/`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "name": "string",
    "location": "string (optional)"
  }
  ```
- **Response**: Created Workshop object.

#### Update Workshop
Update an existing workshop's details.
- **URL**: `/workshops/{workshop_id}`
- **Method**: `PUT`
- **Body**:
  ```json
  {
    "name": "string (optional)",
    "location": "string (optional)"
  }
  ```

#### Delete Workshop
- **URL**: `/workshops/{workshop_id}`
- **Method**: `DELETE`
- **Response**: Deleted Workshop object.
- **Note**: Will fail if workshop contains items.

---

### Categories

#### Get All Categories
- **URL**: `/categories/`
- **Method**: `GET`

#### Create Category
- **URL**: `/categories/`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "name": "string"
  }
  ```

#### Delete Category
- **URL**: `/categories/{category_id}`
- **Method**: `DELETE`

---

### Items

#### Get All Items
- **URL**: `/items/`
- **Method**: `GET`

#### Create Item
- **URL**: `/items/`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "name": "string",
    "description": "string (optional)",
    "category_id": int,
    "workshop_id": int,
    "quantity": int,
    "min_quantity": int,
    "sku": "string (optional)"
  }
  ```

#### Update Item Quantity (Log Transaction)
Adjust stock levels.
- **URL**: `/items/{item_id}/quantity`
- **Method**: `PUT`
- **Query Params**:
  - `change` (int): Amount to add (positive) or remove (negative).
  - `reason` (str): Reason for the change.
- **Response**: Updated Item object.

#### Delete Item
- **URL**: `/items/{item_id}`
- **Method**: `DELETE`

---

### Orders

#### Get All Orders
- **URL**: `/orders/`
- **Method**: `GET`

#### Create Order
- **URL**: `/orders/`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "item_id": int,
    "quantity": int
  }
  ```

#### Complete Order
Mark an order as completed.
- **URL**: `/orders/{order_id}/complete`
- **Method**: `PUT`

---

### Logs

#### Get Inventory Logs
Get history of stock changes.
- **URL**: `/logs/`
- **Method**: `GET`
