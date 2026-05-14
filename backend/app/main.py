from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, get_db
from .models import ProductOpportunity
from .schemas import ProductOpportunityOut, ResearchRequest, ResearchResponse
from .seed_data import seed_database
from .services.research import (
    CONNECTORS,
    DISCLAIMER,
    build_keyword_insights,
    get_competitors,
    opportunities_to_csv,
    search_opportunities,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Edel Luxe Viral Product Research Agent",
    description="Marketplace research, competitor analysis, Etsy SEO listing generation, and scoring for Edel Luxe.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "agent": "Edel Luxe Viral Product Research Agent"}


@app.get("/api/connectors")
def connectors() -> list[dict[str, str | bool]]:
    return [connector.__dict__ for connector in CONNECTORS]


@app.post("/api/research", response_model=ResearchResponse)
def research(request: ResearchRequest, db: Session = Depends(get_db)) -> ResearchResponse:
    opportunities = search_opportunities(db, request)
    competitors = get_competitors(db, request.platforms)
    return ResearchResponse(
        query=request.query,
        disclaimer=DISCLAIMER,
        opportunities=opportunities,
        competitors=competitors,
        keywords=build_keyword_insights(opportunities),
    )


@app.get("/api/opportunities", response_model=list[ProductOpportunityOut])
def opportunities(db: Session = Depends(get_db), limit: int = 20) -> list[ProductOpportunity]:
    request = ResearchRequest(query="jewelry", platforms=[], category="All", limit=limit)
    return search_opportunities(db, request)


@app.get("/api/opportunities/{opportunity_id}", response_model=ProductOpportunityOut)
def opportunity_detail(opportunity_id: int, db: Session = Depends(get_db)) -> ProductOpportunity:
    item = db.get(ProductOpportunity, opportunity_id)
    if not item:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return item


@app.post("/api/export.csv")
def export_csv(request: ResearchRequest, db: Session = Depends(get_db)) -> Response:
    opportunities = search_opportunities(db, request)
    csv_payload = opportunities_to_csv(opportunities)
    return Response(
        content=csv_payload,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=edel-luxe-product-research.csv"},
    )
