from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_research_returns_ranked_opportunities() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/research",
            json={"query": "personalized necklace gift", "platforms": ["Etsy", "Amazon Handmade"], "category": "All", "limit": 5},
        )
    assert response.status_code == 200
    payload = response.json()
    assert "tahmin" in payload["disclaimer"]
    assert payload["opportunities"]
    assert payload["opportunities"][0]["sales_potential_score"] >= 80
    assert payload["keywords"]


def test_export_csv() -> None:
    with TestClient(app) as client:
        response = client.post("/api/export.csv", json={"query": "bracelet", "platforms": ["TikTok Shop"], "category": "All", "limit": 3})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "product_name,platform" in response.text
