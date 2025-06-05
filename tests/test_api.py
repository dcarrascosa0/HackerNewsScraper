 # tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.main import app
from app.scraper import fetch_page

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_fetch_page(monkeypatch):
    """
    Monkeypatch `fetch_page` so that each page fetch returns
    a list of 30 identical dummy items. Tests can then verify
    the endpoint behavior without hitting Hacker News.
    """
    dummy_item = {
        "title": "dummy title",
        "url": "https://example.com",
        "points": 1,
        "sent_by": "dummyuser",
        "published": "1 hour ago",
        "comments": 0
    }
    async def _fake_fetch(page_number: int):
        return [dummy_item.copy() for _ in range(30)]

    spy = AsyncMock(side_effect=_fake_fetch)
    monkeypatch.setattr("app.main.fetch_page", spy)
    return spy

def test_get_root_returns_30_and_calls_fetch_once(mock_fetch_page):
    resp = client.get("/")
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 30

    # Should have been called exactly once with page_number=1
    mock_fetch_page.assert_awaited_once_with(1)

def test_get_2_pages_returns_60_and_calls_fetch_twice(mock_fetch_page):
    resp = client.get("/2")
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 60

    # fetch_page should be awaited for page 1 and page 2 (order may vary)
    called_args = sorted(call.args[0] for call in mock_fetch_page.await_args_list)
    assert called_args == [1, 2]

def test_get_multiple_times_calls_fetch_every_time(mock_fetch_page):
    # First call /1
    resp1 = client.get("/1")
    assert resp1.status_code == 200
    assert len(resp1.json()) == 30
    assert mock_fetch_page.call_count == 1

    # Second call /1 again (no cache yet) → should call fetch_page again
    resp2 = client.get("/1")
    assert resp2.status_code == 200
    assert len(resp2.json()) == 30
    assert mock_fetch_page.call_count == 2

def test_invalid_number_returns_400_or_422():
    for param in ["0", "-5", "abc"]:
        resp = client.get(f"/{param}")
        assert resp.status_code in (400, 422)

def test_each_item_shape():
    resp = client.get("/1")
    assert resp.status_code == 200

    for item in resp.json():
        assert set(item.keys()) == {
            "title",
            "url",
            "points",
            "sent_by",
            "published",
            "comments"
        }
        assert isinstance(item["title"], str)
        assert isinstance(item["url"], str)
        assert isinstance(item["points"], int)
        assert isinstance(item["sent_by"], str)
        assert isinstance(item["published"], str)
        assert isinstance(item["comments"], int)
