from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ResearchRequest(BaseModel):
    query: str = Field(default="handmade jewelry", min_length=1, max_length=120)
    platforms: list[str] = Field(default_factory=lambda: ["Etsy", "Amazon Handmade", "TikTok Shop", "eBay", "Pinterest", "Google Trends", "Shopify"])
    category: str = Field(default="Handmade jewelry", max_length=80)
    limit: int = Field(default=10, ge=1, le=50)


class ProductOpportunityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_name: str
    platform: str
    category: str
    trend_status: str
    competition_level: str
    average_price: str
    target_customer: str
    primary_keywords: str
    long_tail_keywords: str
    title_structure: str
    description_style: str
    visual_style: str
    competitor_learnings: str
    viral_reason: str
    edel_luxe_fit: str
    suggested_etsy_title: str
    seo_description: str
    etsy_tags: str
    photo_advice: str
    product_development_idea: str
    sales_potential_score: int
    estimated_sales_potential: str
    trend_score: float
    source_url: str
    data_confidence: str
    first_action_plan: str


class CompetitorInsightOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shop_name: str
    platform: str
    niche: str
    best_selling_products: str
    pricing_strategy: str
    seo_patterns: str
    visual_style: str
    trust_signals: str
    shipping_promotions: str
    opportunity_gap: str
    source_url: str
    data_confidence: str


class KeywordInsight(BaseModel):
    keyword: str
    intent: str
    suggested_use: str
    competition_hint: str


class ResearchResponse(BaseModel):
    query: str
    disclaimer: str
    opportunities: list[ProductOpportunityOut]
    competitors: list[CompetitorInsightOut]
    keywords: list[KeywordInsight]
