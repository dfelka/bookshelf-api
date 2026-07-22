"""Tests for the auto-generated API documentation endpoints."""


def test_openapi_schema_available(client) -> None:
    resp = client.get("/openapi.json")

    assert resp.status_code == 200
    assert resp.json()["info"]["title"] == "Bookshelf API"


def test_swagger_docs_available(client) -> None:
    resp = client.get("/docs")

    assert resp.status_code == 200


def test_redoc_uses_pinned_bundle(client) -> None:
    resp = client.get("/redoc")

    assert resp.status_code == 200
    body = resp.text
    # Must load the pinned, stable bundle — not the broken `@next` tag that
    # FastAPI ships by default (it 404s on the CDN and renders a blank page).
    assert "redoc@2" in body
    assert "redoc@next" not in body
