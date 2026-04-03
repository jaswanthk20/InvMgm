# User Guide

Welcome to the EMERA ideaHUB Inventory Management System. This guide will clarify how to utilize the prototype functionality.

## Getting Started

1.  **Open the App**: Once the app is running in the background via `python app.py` or the `flask` command, point your browser to [http://localhost:5000](http://localhost:5000).
2.  **Dashboard Hub**: The initial view shows a quick-glimpse operational dashboard presenting:
    -   **Out of Stock & Low Stock**: Actionable flags ensuring critical shop tools are resupplied.
    -   **Weekly Movements**: An indicator of how aggressively the space was engaged in the last 7 days.
    -   **Quick Transactions**: Add or remove stock directly from any listed Location immediately upon log in.

## Managing the Item Catalog

Instead of defining categories individually by hand manually, categories are organically populated from your tool listings.

### Bulk Import Items via Spreadsheets
1. Navigated to **Items Master** via the sidebar.
2. Click the **Import CSV/Excel** button.
3. Your provided file will be heavily scrubbed for duplicate SKUs saving hours of data entry and syncing directly to the SQLite databases.

### Updating or Adding an Individual Item
1. Click the **+ Add New Item** component.
2. Fill out thresholds like `Min Stock` limitations. 
3. If an item needs to be updated with a new name, simply click the **Edit** button generated inside the data grid to launch the edit experience. The UI maps changes synchronously to the database in real-time.

### Multi-Filter Finding
If the database climbs to hundreds of tools:
1. Utilize the text search bar to type tool specifics (e.g., `Drill`).
2. Utilize the adjacent dropdown category menu (which crawls all live available items) to filter to specific tool groups (e.g., `Power Tools`). Both elements synergize to lock onto tools instantly.

## Purchase Order Workflows

### Making a Request
1. Transition to the **Orders & Requests** page.
2. Form a new Order Request noting the target item id and volume requirement.
3. When requested, the item drops into a `PENDING` transaction block on the dashboard.

### Fulfilling Orders
1. Once shipped supplies physically arrive, transition back to the Orders page.
2. Simply click the **Mark as Received** UI component. This triggers an instant background API transaction confirming it internally, flipping the metric on the Dashboard off.
