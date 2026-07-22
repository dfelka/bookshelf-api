"""Integration tests for the /books endpoints.

These drive the full stack: router -> service -> ORM -> (in-memory) DB,
including Pydantic validation and the standard response envelopes.
"""


def _create(client, **fields):
    body = {"title": "Default Title", **fields}
    return client.post("/books", json=body)


# --------------------------------------------------------------------------- #
# Create                                                                      #
# --------------------------------------------------------------------------- #


def test_create_book_returns_201_and_envelope(client) -> None:
    resp = client.post(
        "/books",
        json={"title": "Dune", "author": "Frank Herbert", "description": "Spice"},
    )

    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["id"] == 1
    assert data["title"] == "Dune"
    assert data["author"] == "Frank Herbert"
    assert data["is_done"] is False
    assert "created_at" in data and "updated_at" in data


def test_create_book_missing_title_returns_422(client) -> None:
    resp = client.post("/books", json={"author": "Nobody"})

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "UNPROCESSABLE_ENTITY"


def test_create_book_blank_title_returns_422(client) -> None:
    resp = client.post("/books", json={"title": ""})

    assert resp.status_code == 422


# --------------------------------------------------------------------------- #
# List                                                                        #
# --------------------------------------------------------------------------- #


def test_list_books_returns_paginated_envelope(client) -> None:
    for i in range(3):
        _create(client, title=f"Book {i}")

    resp = client.get("/books", params={"page": 1, "per_page": 2})

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) == 2
    assert body["meta"] == {"page": 1, "per_page": 2, "total": 3}


def test_list_books_empty(client) -> None:
    resp = client.get("/books")

    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] == []
    assert body["meta"]["total"] == 0


def test_list_books_filters_by_is_done(client) -> None:
    _create(client, title="Read", is_done=True)
    _create(client, title="Unread", is_done=False)

    resp = client.get("/books", params={"is_done": True})

    body = resp.json()
    assert body["meta"]["total"] == 1
    assert body["data"][0]["title"] == "Read"


def test_list_books_rejects_bad_pagination(client) -> None:
    resp = client.get("/books", params={"per_page": 0})

    assert resp.status_code == 422


# --------------------------------------------------------------------------- #
# Retrieve                                                                    #
# --------------------------------------------------------------------------- #


def test_get_book_returns_single_envelope(client) -> None:
    created = _create(client, title="Solo").json()["data"]

    resp = client.get(f"/books/{created['id']}")

    assert resp.status_code == 200
    assert resp.json()["data"]["title"] == "Solo"


def test_get_book_unknown_id_returns_404(client) -> None:
    resp = client.get("/books/999")

    assert resp.status_code == 404
    error = resp.json()["error"]
    assert error["code"] == "NOT_FOUND"
    assert "999" in error["message"]


# --------------------------------------------------------------------------- #
# Update                                                                      #
# --------------------------------------------------------------------------- #


def test_patch_book_updates_only_sent_fields(client) -> None:
    created = _create(client, title="Before", author="Keep Me").json()["data"]

    resp = client.patch(f"/books/{created['id']}", json={"is_done": True})

    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["is_done"] is True
    assert data["title"] == "Before"
    assert data["author"] == "Keep Me"


def test_patch_unknown_id_returns_404(client) -> None:
    resp = client.patch("/books/999", json={"title": "Nope"})

    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


def test_patch_blank_title_returns_422(client) -> None:
    created = _create(client, title="Valid").json()["data"]

    resp = client.patch(f"/books/{created['id']}", json={"title": ""})

    assert resp.status_code == 422


# --------------------------------------------------------------------------- #
# Delete                                                                      #
# --------------------------------------------------------------------------- #


def test_delete_book_returns_204_and_removes(client) -> None:
    created = _create(client, title="Doomed").json()["data"]

    resp = client.delete(f"/books/{created['id']}")

    assert resp.status_code == 204
    assert resp.content == b""
    assert client.get(f"/books/{created['id']}").status_code == 404


def test_delete_unknown_id_returns_404(client) -> None:
    resp = client.delete("/books/999")

    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"
