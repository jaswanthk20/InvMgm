# Project Overview

The **Inventory Management System (InvMgm)** is a full-stack web application designed to help engineering workshops track their inventory of tools, consumables, and spare parts.

## Architecture

The application is built using a lightweight and efficient stack:

*   **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
    *   Provides a high-performance RESTful API.
    *   Handles database operations via SQLAlchemy.
    *   Validates data using Pydantic schemas.
*   **Database**: SQLite
    *   Simple, serverless, file-based database for easy deployment.
*   **Frontend**: Vanilla JavaScript + HTML + CSS
    *   No complex build steps or heavy frameworks.
    *   Uses **Tailwind CSS** (via CDN) for modern, responsive styling.
    *   Communicates with the backend via the native `fetch` API.

## Directory Structure

```text
InvMgm/
├── backend/
│   ├── main.py          # App entry point (FastAPI app instance)
│   ├── models.py        # Database table definitions (SQLAlchemy)
│   ├── schemas.py       # Data validation schemas (Pydantic)
│   ├── routes.py        # API endpoint definitions
│   ├── crud.py          # Database lookup/create/update/delete logic
│   ├── database.py      # Database connection & session handling
│   └── static/          # Serving frontend files
│       ├── index.html
│       ├── app.js
│       └── style.css
├── docs/                # Project Documentation
├── e2e_test_script.py   # End-to-End backend test script
└── inventory.db         # SQLite database file (created on runtime)
```

## Key Features

1.  **Workshops & Locations**: Manage multiple workshop locations.
2.  **Categories**: Organize items into logical groups (e.g., "Power Tools", "Safety Gear").
3.  **Item Management**: comprehensive CRUD operations for inventory items.
4.  **Stock Tracking**: Real-time quantity updates with low-stock indicators.
5.  **Logging**: Audit trail for every stock change (additions, removals, shrinkage).
6.  **Orders**: Simple ordering system to track replenished items.
