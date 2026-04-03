# User Guide

Welcome to the Inventory Management System. This guide will help you manage your workshop inventory effectively.

## Getting Started

1.  **Open the App**: Navigate to [http://localhost:8000](http://localhost:8000) in your browser.
2.  **Dashboard**: The initial view shows a dashboard with:
    -   **Low Stock Alerts**: Items that are running low and need reordering.
    -   **Recent Activity**: The latest inventory changes.

## Managing Setup Data

Before adding items, you need to define your Workshops and Categories.

### Adding a Workshop
1.  Go to the **Workshops** tab (if available in UI layout) or ensure at least one workshop exists.
2.  (Implementation detail: currently managed via API or initial setup, UI controls to be confirmed).

### Adding a Category
1.  Define categories like "Power Tools", "Hand Tools", "Consumables" to organize your items.

## Managing Inventory

### Adding a New Item
1.  Click the **"Add Item"** button.
2.  Fill in the details:
    -   **Name**: e.g., "Drill Bit 5mm".
    -   **Description**: e.g., "Cobalt steel for metal".
    -   **Category**: Select from the list.
    -   **Workshop**: Select where it is stored.
    -   **Initial Quantity**: Current count.
    -   **Min Quantity**: When stock drops below this, you'll get an alert.
3.  Click **Save**.

### Updating Stock (Check-in / Check-out)
1.  Find the item in the inventory list.
2.  **To Remove Stock**: Click the **"-"** button. Enter the amount to remove and the reason (e.g., "Used for Project X").
3.  **To Add Stock**: Click the **"+"** button. Enter the amount to add and the reason (e.g., "Restock").
4.  The system automatically logs this transaction and updates the quantity.

### Deleting an Item
1.  Find the item.
2.  Click the **Delete** (Trash icon) button.
3.  Confirm the action. **Warning**: This action cannot be undone.

## Orders

### Placing an Order
1.  Identified a low-stock item?
2.  Go to the **Orders** section.
3.  Create a new order for the specific Item and Quantity.
4.  The order status will be "Pending".

### Completing an Order
1.  When the shipment arrives:
2.  Find the pending order.
3.  Mark it as **Complete**.
4.  **Note**: This does NOT automatically add stock to the item (depending on current implementation logic, manual stock update might be needed - check specific business rule). *Self-correction: API currently just marks complete. User should manually add stock via the "+" button when receiving items.*
