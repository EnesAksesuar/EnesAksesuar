# Edel Luxe Viral Product Research Agent

Full-stack MVP for researching premium handmade jewelry and gift product opportunities for Edel Luxe.

## What it does

- Scores viral/product opportunities across Etsy, Amazon Handmade, TikTok Shop, eBay, Pinterest, Google Trends, and Shopify-oriented research flows.
- Stores sample opportunities and competitor insights in SQLite.
- Generates an `ÜRÜN FIRSATI RAPORU` with Etsy SEO title, SEO description, 13 tags, photo advice, product development ideas, and first action plan.
- Provides a React + Vite dashboard with search, platform/category filters, trend product table, competitor analysis, keyword analysis, CSV export, and an Edel Luxe listing action button.

> Data note: this MVP ships with sample/estimated seed data. Live marketplace APIs or legally permitted exports/scrapers should be connected before making inventory decisions. The app deliberately avoids fabricated sales counts.

## Architecture

```text
backend/
  app/
    main.py                 FastAPI routes and app lifecycle
    database.py             SQLAlchemy engine/session setup
    models.py               SQLite-ready ORM models
    schemas.py              Pydantic request/response schemas
    seed_data.py            Sample research and competitor data
    services/research.py    Scoring/search/keyword/export logic
  tests/test_api.py         API smoke tests
frontend/
  src/main.jsx              Dashboard UI
  src/styles.css            Professional Edel Luxe styling
```

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: <http://localhost:8000/docs>

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard: <http://localhost:5173>

## Tests

```bash
cd backend
pytest
```
