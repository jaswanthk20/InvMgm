# 📦 EMERA ideaHUB & Makerspace — Inventory Management System

> A lightweight, full-stack inventory management prototype purpose-built for the operational needs of a makerspace environment. Designed for speed: most stock transactions complete in **≤ 2 clicks**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.3-lightgrey?logo=flask)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Prototype-orange)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Pages & UI](#pages--ui)
- [Import Format](#import-format)
- [Testing](#testing)
- [Contributing](#contributing)

---

## Overview

The **EMERA ideaHUB Inventory Management System (InvMgm)** is a Flask-based web application tailored for makerspaces to simplify tracking of tools, consumables, and hardware. It solves three core operational problems:

| Problem | Solution |
|---|---|
| Tools go missing and are hard to locate | Location-aware stock ledger with zone/shelf/bin granularity |
| Re-ordering is reactive and ad hoc | Low-stock alerts & purchase order workflow on the dashboard |
| Bulk item setup takes hours | CSV/Excel drag-and-drop bulk import with duplicate SKU detection |

> **Note:** There is a legacy FastAPI + SQLAlchemy implementation in the `backend/` folder (port 8000). The active prototype runs from `app.py` via Flask on **port 5000**.

---

## Features

### 🏠 Dashboard KPIs
Real-time operational metrics visible on first load — no page reloads needed:
- **Out of Stock** — count of items at zero quantity
- **Low Stock** — items below their configured `min_stock` threshold
- **Open Purchase Orders** — pending replenishment requests
- **Weekly Movements** — stock IN / OUT transactions in the last 7 days

### ⚡ Quick Transactions (≤ 2 Clicks)
Submit an `IN` or `OUT` stock adjustment from the main dashboard without navigating away. A modal captures item, location, quantity, and movement type.

### 📦 Item Master List
- Add, edit, or deactivate items with name, SKU, category, unit cost, and reorder thresholds
- Dual-layer filtering: combine free-text search with a **live-generated** category dropdown (no hardcoded lists — categories are derived from actual data)
- Inline **Edit** button saves changes to the database in real time via the Fetch API

### 📥 Bulk Import (CSV / Excel)
- Drag-and-drop upload on the Items page
- Detects and skips **duplicate SKUs** automatically
- Maps standard spreadsheet columns to the item master schema

### 🛒 Purchase Orders & Receiving
- Create order requests per item with required quantities
- Items enter `PENDING` state and surface on the dashboard as Open POs
- **Mark as Received** button closes the order and triggers a stock `IN` movement automatically

### 📊 Reports
Filterable management reports providing aggregate inventory valuation, movement summaries, and disruption logs.

### 🔒 Zero Negative Stock
A `CHECK (quantity >= 0)` constraint enforced at the SQLite database level prevents any logical error from creating impossible negative stock values.

### 📋 Append-Only Audit Ledger
Every stock movement is written to `stock_movements` — records are never deleted or updated, providing a full paper trail.

---

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| **Backend** | Python 3.10+ / Flask 3.0.3 | REST API + server-side template rendering |
| **Database** | SQLite (`database.db`) | DDL compatible with PostgreSQL for future migration |
| **Frontend** | HTML5, Vanilla CSS, Vanilla JavaScript | No build step; uses native `Fetch API` |
| **Extras** | pdfplumber, pytesseract, Pillow | PDF/image parsing utilities |

---

## Project Structure

```
InvMgm/
├── app.py                   # Core Flask app — routes, API endpoints, CSV import logic
├── db.py                    # DB connection lifecycle & CLI init-db command
├── schema.sql               # Full DDL — all tables, constraints, and indexes
├── seed_data.py             # Generates realistic sample data (locations, items, metrics)
├── migrate_db.py            # Schema migration helper
├── check_db.py              # Quick DB health check utility
├── requirements.txt         # Python dependency list
├── database.db              # Active SQLite database (git-ignored in production)
├── inventory.db             # Legacy DB file (older schema)
├── test_import_items.csv    # Sample CSV for bulk import testing
├── e2e_test_script.py       # End-to-end API smoke tests
├── test_workshop_update.py  # Focused integration test for item updates
│
├── templates/               # Jinja2 HTML templates
│   ├── base.html            # Shared layout: sidebar navigation + topbar
│   ├── dashboard.html       # KPI tiles, quick transaction modal, low-stock panel
│   ├── items.html           # Item master list, add/edit dialog, bulk import dropzone
│   ├── locations.html       # Location management (zone / room / shelf / bin)
│   ├── orders.html          # Purchase order creation and receiving workflow
│   └── reports.html         # Inventory reports and analytics
│
├── static/
│   └── css/
│       └── style.css        # Full design system: colors, typography (Inter), layout
│
├── backend/                 # Legacy FastAPI + SQLAlchemy implementation (inactive)
├── docs/                    # Additional documentation
│   ├── Project_Overview.md
│   └── User_Guide.md
└── .github/                 # GitHub Actions / workflows
```

---

## Database Schema

The database is organized into three logical groups:

### Core Inventory Tables

```
items ──────────────── categories
  │                        │
  ├─── stock_on_hand ◄─── locations
  ├─── stock_movements
  ├─── item_home_locations
  └─── reorder_rules ────── suppliers
```

### Purchase Order Tables

```
purchase_orders ──── purchase_order_lines ──── receiving_records
                              │
                           items
```

### Metrics & Audit Tables

```
disruptions_log     ←  items, locations, users
search_time_log     ←  items, users
return_audit_log    ←  items, users
stock_movements     ←  items, locations, users  (primary audit ledger)
```

### Key Design Decisions

| Decision | Rationale |
|---|---|
| `CHECK (quantity >= 0)` on `stock_on_hand` | Prevents negative stock at the DB level — not just application logic |
| Append-only `stock_movements` | Full audit trail; no UPDATE/DELETE on movement records |
| `SKU UNIQUE` constraint on `items` | Enables safe upsert logic during CSV bulk import |
| `item_home_locations` junction table | Allows one item to have multiple canonical home locations |

---

## Getting Started

### Prerequisites
- **Python 3.10+**
- `pip` (bundled with Python)

### 1. Clone the Repository
```powershell
git clone <repository-url>
cd InvMgm
```

### 2. Set Up the Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Initialize the Database
This creates `database.db` by running `schema.sql`.
```powershell
flask --app app init-db
```

### 5. (Optional) Seed with Sample Data
Populate the database with realistic locations, items, and metric logs.
```powershell
python seed_data.py
```

### 6. Start the Development Server
```powershell
flask --app app run --port 5000
```

Open your browser to **[http://localhost:5000](http://localhost:5000)**.

---

## API Reference

All endpoints return JSON. Base URL: `http://localhost:5000`

### Items

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/items` | List all items |
| `POST` | `/api/items` | Create a new item |
| `PUT` | `/api/items/<id>` | Update an existing item |
| `DELETE` | `/api/items/<id>` | Remove an item |

### Locations

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/locations` | List all locations |
| `POST` | `/api/locations` | Create a new location |

### Transactions / Stock Movements

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/transactions` | Log a stock IN / OUT / MOVE |
| `GET` | `/api/transactions` | Fetch recent movement log |

### Dashboard & Metrics

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard/metrics` | Returns KPI counts (low stock, open POs, weekly movements) |
| `GET` | `/api/dashboard/low-stock` | Returns items below their `min_stock` threshold |

### Purchase Orders

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/orders` | List all purchase orders |
| `POST` | `/api/orders` | Create a new purchase order |
| `PUT` | `/api/orders/<id>/receive` | Mark an order as received (triggers stock IN) |

### Bulk Import

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/import` | Upload CSV or Excel file for bulk item registration |

---

## Pages & UI

| Page | Route | Description |
|---|---|---|
| Dashboard | `/` | KPI tiles, quick transaction modal, low-stock alerts |
| Item Master | `/items` | Full item catalog with search, filter, add, edit, bulk import |
| Locations | `/locations` | Manage storage zones, rooms, shelves, and bins |
| Orders & Requests | `/orders` | Create and fulfill purchase order requests |
| Reports | `/reports` | Inventory analytics and movement summaries |

---

## Import Format

Bulk item uploads accept `.csv` or `.xlsx` files. The importer maps the following columns:

| Column | Required | Description |
|---|---|---|
| `sku` | ✅ | Unique identifier. Duplicates are skipped. |
| `name` | ✅ | Item display name |
| `category` | ✗ | Category label (auto-created if new) |
| `unit` | ✗ | Unit of measure (e.g., `pcs`, `boxes`) |
| `min_stock` | ✗ | Minimum stock threshold for low-stock alerts |
| `reorder_point` | ✗ | Quantity at which to trigger a reorder request |
| `unit_cost` | ✗ | Per-unit cost for inventory valuation |

See [`test_import_items.csv`](./test_import_items.csv) for a working example.

---

## Testing

### End-to-End Smoke Test
Runs a full API cycle: create item → log transaction → verify stock.
```powershell
python e2e_test_script.py
```

### Workshop Update Integration Test
Validates that item edits persist correctly.
```powershell
python test_workshop_update.py
```

### Database Health Check
Confirms the database file is accessible and tables exist.
```powershell
python check_db.py
```

---

## Contributing

1. **Fork** the repository and create a feature branch (`git checkout -b feature/your-feature`)
2. Follow the existing code style — no external frontend frameworks, keep Flask routes in `app.py`
3. Test your changes with `e2e_test_script.py` before submitting a PR
4. Open a **Pull Request** with a clear description of what changed and why

### Branching Convention

| Branch prefix | Purpose |
|---|---|
| `feature/` | New functionality |
| `fix/` | Bug fixes |
| `docs/` | Documentation changes only |
| `refactor/` | Internal code improvement, no behaviour change |

---

## Further Documentation

- 📄 [Project Overview](./docs/Project_Overview.md) — Architecture decisions and system design
- 📖 [User Guide](./docs/User_Guide.md) — Step-by-step instructions for end users

---

*Built for the EMERA ideaHUB & Makerspace — S2 Integrators LLC*
