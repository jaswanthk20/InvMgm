# EMERA ideaHUB & Makerspace Inventory Prototype

This repository contains the prototype inventory management system tailored for the unique constraints and operational needs of the EMERA ideaHUB & Makerspace. It focuses on problem-fit, high visibility, and reducing friction (transactions in ≤2 clicks).

## Tech Stack
* **Backend:** Python + Flask
* **Database:** SQLite (built with standard SQL DDL for straightforward PostgreSQL migration if needed)
* **Frontend:** HTML, Vanilla CSS (`style.css`), Vanilla JavaScript (Fetch API)

---

## File Structure

* **`app.py`**: The core Flask application backbone. It houses:
  * Application initialization and generic template mapping endpoints.
  * API Routes: Core item creation (`/api/items`), location management (`/api/locations`), transaction logging (`/api/transactions`), and specific workflow triggers (low stock fetching, Dashboard metrics calculations).
  * The `import_amazon_csv()` method that maps standard Amazon CSV layouts to our item master list or creates new records.
* **`db.py`**: A helper handling database connection lifecycles and loading the initialization script via `app.cli.command`.
* **`schema.sql`**: The DDL structure declaring relationships between Items, Locations, Logs, Stock Movements, Orders, and System users. Includes SQLite constraints to prevent negative stock values.
* **`seed_data.py`**: An executable Python script creating 4 realistic locations, user roles, 6 items with metrics profiles, and over 60 simulated metric log traces (Search times, Return compliance checks, Disruptions).
* **`requirements.txt`**: The `pip` list of backend dependencies (just Flask).
* **`templates/base.html`**: The unified layout structure mapping the Sidebar and Topbar Search wrapper.
* **`templates/dashboard.html`**: The main operational hub highlighting the 6 core metrics tiles (Visibility score, Return %, Search Average, Disruptions, etc.), the quick transaction modal, low stock warnings, and CSV Dropzone logic.
* **`templates/items.html`**: The Item Master List demonstrating table grids and the "Add Item" flow dialog.
* **`static/css/style.css`**: The design system styling colors, fonts (Inter), button behaviors, hover states, input formatting, and layout behaviors without relying on heavy frameworks like Tailwind or Bootstrap. 

---

## Getting Started

### 1. Prerequisites
Ensure you are running **Python 3.10+**.

### 2. Setup the Virtual Environment
Create a clean environment and install Flask.
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Initialize the Database
This will create `database.db` locally by consuming `schema.sql`.
```powershell
flask --app app init-db
```

### 4. (Optional) Seed the Database with Dummy Data
If you want to view the prototype with rich sample metrics, run this snippet to populate logs and existing inventory quantities.
```powershell
python seed_data.py
```

### 5. Start the Server
Run the Flask development server on port 5000.
```powershell
flask --app app run --port 5000
```
Then, point a browser to `http://localhost:5000`.

---

## Features
* **Inventory Visibility Score**: An autonomous equation `( (Labeling % * 0.3) + (Returns % * 0.3) + (100 - Avg Search Delay % * 0.4) ) / 10`.
* **Zero Negative Stock**: Protected strictly at the SQLite DB level, we only utilize append-only movement ledgers.
* **Frictionless UI Interface**: Users can submit an `IN` or `OUT` stock switch from the central dashboard without changing URLs within 2 clicks.
* **Amazon Replenishment**: Native CSV mapping capabilities.
