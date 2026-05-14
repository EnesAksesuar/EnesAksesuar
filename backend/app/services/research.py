from __future__ import annotations

import csv
import io
from dataclasses import dataclass

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..models import CompetitorInsight, ProductOpportunity
from ..schemas import KeywordInsight, ResearchRequest

DISCLAIMER = (
    "Bu MVP örnek/seed veri ve deterministik analiz kurallarıyla çalışır. "
    "Canlı API/scraping bağlanana kadar satış adetleri tahmin olarak işaretlenir; "
    "uydurma satış rakamı verilmez ve her fırsatta kaynak/platform alanı gösterilir."
)

PLATFORM_ALIASES = {
    "Amazon": "Amazon Handmade",
    "Google": "Google Trends",
    "TikTok": "TikTok Shop",
}


@dataclass(frozen=True)
class PlatformConnector:
    name: str
    api_available: bool
    safe_collection_notes: str


CONNECTORS = [
    PlatformConnector("Etsy", True, "Official API ile listing/search verisi; robots.txt ve rate limit uyumlu fallback."),
    PlatformConnector("Amazon Handmade", False, "Affiliate/Product Advertising API uygunluğu veya manuel CSV; scraping sınırlı ve ToS uyumlu."),
    PlatformConnector("TikTok Shop", True, "TikTok Shop/Open API veya creator analytics export; video metrikleri için izinli entegrasyon."),
    PlatformConnector("eBay", True, "Browse API ve marketplace insights."),
    PlatformConnector("Pinterest", True, "Pinterest Trends/Ads keyword verisi ve izinli pin metrikleri."),
    PlatformConnector("Google Trends", True, "pytrends veya Trends export ile normalized trend indeksi."),
    PlatformConnector("Shopify", False, "Rakip mağazalarda herkese açık koleksiyon/sitemap analizi; ToS uyumlu, düşük frekanslı tarama."),
]


def normalize_platform(platform: str) -> str:
    return PLATFORM_ALIASES.get(platform, platform)


def search_opportunities(db: Session, request: ResearchRequest) -> list[ProductOpportunity]:
    query_terms = [term.strip().lower() for term in request.query.split() if term.strip()]
    platforms = {normalize_platform(platform) for platform in request.platforms}

    stmt = select(ProductOpportunity)
    if platforms:
        stmt = stmt.where(ProductOpportunity.platform.in_(platforms))
    if request.category and request.category != "All":
        stmt = stmt.where(or_(ProductOpportunity.category.ilike(f"%{request.category}%"), ProductOpportunity.primary_keywords.ilike(f"%{request.category}%")))

    results = list(db.scalars(stmt).all())
    if query_terms:
        ranked = []
        for item in results:
            haystack = " ".join(
                [
                    item.product_name,
                    item.category,
                    item.primary_keywords,
                    item.long_tail_keywords,
                    item.target_customer,
                    item.viral_reason,
                ]
            ).lower()
            match_count = sum(1 for term in query_terms if term in haystack)
            if match_count:
                ranked.append((match_count, item.sales_potential_score, item))
        results = [item for _, _, item in sorted(ranked, key=lambda row: (row[0], row[1]), reverse=True)] or results

    return sorted(results, key=lambda item: (item.sales_potential_score, item.trend_score), reverse=True)[: request.limit]


def get_competitors(db: Session, platforms: list[str] | None = None) -> list[CompetitorInsight]:
    stmt = select(CompetitorInsight)
    if platforms:
        stmt = stmt.where(CompetitorInsight.platform.in_({normalize_platform(platform) for platform in platforms}))
    return list(db.scalars(stmt).all())


def build_keyword_insights(opportunities: list[ProductOpportunity]) -> list[KeywordInsight]:
    seen: set[str] = set()
    insights: list[KeywordInsight] = []
    for opportunity in opportunities:
        for keyword in [*opportunity.primary_keywords.split(","), *opportunity.long_tail_keywords.split(",")]:
            cleaned = keyword.strip()
            if not cleaned or cleaned.lower() in seen:
                continue
            seen.add(cleaned.lower())
            is_long_tail = len(cleaned.split()) >= 4
            insights.append(
                KeywordInsight(
                    keyword=cleaned,
                    intent="Gift / purchase intent" if any(word in cleaned.lower() for word in ["gift", "mom", "girlfriend", "bridesmaid"]) else "Discovery / style intent",
                    suggested_use="Etsy title + first 160 chars" if is_long_tail else "Tag + attributes + image alt text",
                    competition_hint="Lower competition opportunity" if is_long_tail else "Validate competition before scaling",
                )
            )
    return insights[:20]


def opportunities_to_csv(opportunities: list[ProductOpportunity]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "product_name",
            "platform",
            "trend_status",
            "competition_level",
            "average_price",
            "primary_keywords",
            "sales_potential_score",
            "data_confidence",
            "source_url",
        ]
    )
    for item in opportunities:
        writer.writerow(
            [
                item.product_name,
                item.platform,
                item.trend_status,
                item.competition_level,
                item.average_price,
                item.primary_keywords,
                item.sales_potential_score,
                item.data_confidence,
                item.source_url,
            ]
        )
    return output.getvalue()
