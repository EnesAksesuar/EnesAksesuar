from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class ProductOpportunity(Base):
    __tablename__ = "product_opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_name: Mapped[str] = mapped_column(String(180), index=True)
    platform: Mapped[str] = mapped_column(String(60), index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    trend_status: Mapped[str] = mapped_column(String(40), index=True)
    competition_level: Mapped[str] = mapped_column(String(40), index=True)
    average_price: Mapped[str] = mapped_column(String(80))
    target_customer: Mapped[str] = mapped_column(String(240))
    primary_keywords: Mapped[str] = mapped_column(Text)
    long_tail_keywords: Mapped[str] = mapped_column(Text)
    title_structure: Mapped[str] = mapped_column(String(240))
    description_style: Mapped[str] = mapped_column(Text)
    visual_style: Mapped[str] = mapped_column(Text)
    competitor_learnings: Mapped[str] = mapped_column(Text)
    viral_reason: Mapped[str] = mapped_column(Text)
    edel_luxe_fit: Mapped[str] = mapped_column(Text)
    suggested_etsy_title: Mapped[str] = mapped_column(String(140))
    seo_description: Mapped[str] = mapped_column(Text)
    etsy_tags: Mapped[str] = mapped_column(Text)
    photo_advice: Mapped[str] = mapped_column(Text)
    product_development_idea: Mapped[str] = mapped_column(Text)
    sales_potential_score: Mapped[int] = mapped_column(Integer, index=True)
    estimated_sales_potential: Mapped[str] = mapped_column(String(80))
    trend_score: Mapped[float] = mapped_column(Float, default=0)
    source_url: Mapped[str] = mapped_column(String(500), default="")
    data_confidence: Mapped[str] = mapped_column(String(80), default="Sample / estimated")
    first_action_plan: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CompetitorInsight(Base):
    __tablename__ = "competitor_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    shop_name: Mapped[str] = mapped_column(String(160), index=True)
    platform: Mapped[str] = mapped_column(String(60), index=True)
    niche: Mapped[str] = mapped_column(String(120), index=True)
    best_selling_products: Mapped[str] = mapped_column(Text)
    pricing_strategy: Mapped[str] = mapped_column(Text)
    seo_patterns: Mapped[str] = mapped_column(Text)
    visual_style: Mapped[str] = mapped_column(Text)
    trust_signals: Mapped[str] = mapped_column(Text)
    shipping_promotions: Mapped[str] = mapped_column(Text)
    opportunity_gap: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(String(500), default="")
    data_confidence: Mapped[str] = mapped_column(String(80), default="Sample / estimated")
