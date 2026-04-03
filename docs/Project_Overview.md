# Project Overview

The **EMERA ideaHUB & Makerspace Inventory Management System (InvMgm)** is a full-stack web application tailored for makerspaces to heavily simplify tracking tools, consumables, and hardware flows.

## Architecture

The operational prototype is built using a lightweight and rapidly iterating stack:

*   **Backend**: Python + [Flask](https://flask.palletsprojects.com/)
    *   Provides high-performance rendering and a centralized REST API router.
    *   Zero excessive class-layer dependencies; queries execute directly against database states.
*   **Database**: SQLite (`database.db`)
    *   Robust architecture embedded with `CHECK` constraints mapping to positive inventory logic, making data highly secure from logical bugs.
*   **Frontend**: Vanilla JavaScript + HTML + CSS
    *   No complex build steps, TS compilation, or heavy CSS frameworks. Relies on custom variables inside `style.css`.
    *   Communicates asynchronously via native `Fetch API` for smooth page-in-page mutations (like the multi-layer item searching and editing).

*(Note: There is an older, legacy implementation utilizing FastAPI and SQLAlchemy located in the `backend/` folder setup on port 8000, but the live prototype is mapping explicitly to `app.py` via Flask on port 5000.)*

## Key Features

1.  **Dashboard KPIs**: View active pulse metrics including Weekly Shop Movements, Out of Stock totals, Low Stock alerts, and Open Purchase requests asynchronously.
2.  **Frictionless Processing**: Allow users to perform "Quick Transactions" (`IN`/`OUT`) covering specific locations in less than three clicks right from the main dashboard.
3.  **Bulk Excel / CSV Loading**: Easily provision large catalogs of tools by dumping spreadsheet ledgers natively inside the web app portal without hitting the CLI.
4.  **Auto-Populating Categorization**: The prototype abandons static Category lists to analyze available stock elements inside the database natively to generate Smart dropdown filter tools live.
5.  **Audit Logs**: Append-only ledgers ensuring stock additions and subtractions maintain a perfect paper trail.
