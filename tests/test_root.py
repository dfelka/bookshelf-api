"""Integration test for the root metadata endpoint."""


def test_root_returns_metadata(client) -> None:
    resp = client.get("/")

    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Bookshelf API"
    assert body["docs"] == "/docs"
    assert body["health"] == "/health"
    assert "version" in body
