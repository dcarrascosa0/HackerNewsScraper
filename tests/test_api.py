# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.main import app
from app import cache

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_cache_before_test():
    """Clear the cache before each test to ensure test isolation."""
    cache.clear_cache()


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
    # Patch fetch_page in app.main (where it’s used)
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

    # After first request, cache has pages 1 and 2.
    # If we call /1 again, fetch_page should NOT be called again.
    mock_fetch_page.reset_mock()
    resp2 = client.get("/1")
    assert resp2.status_code == 200
    assert len(resp2.json()) == 30
    mock_fetch_page.assert_not_awaited()

    # Now if we call /3, only page 3 is missing; fetch_page should be called once with 3.
    mock_fetch_page.reset_mock()
    resp3 = client.get("/3")
    assert resp3.status_code == 200
    assert len(resp3.json()) == 90  # pages 1, 2 (from cache) + page 3
    mock_fetch_page.assert_awaited_once_with(3)
    # Cache should now be [1, 2, 3]
    assert cache.get_cached_pages() == [1, 2, 3]


def test_get_multiple_times_uses_cache(mock_fetch_page):
    # First call /1
    resp1 = client.get("/1")
    assert resp1.status_code == 200
    assert len(resp1.json()) == 30
    assert mock_fetch_page.call_count == 1

    # Second call /1 should use cache; fetch_page not called again
    mock_fetch_page.reset_mock()
    resp2 = client.get("/1")
    assert resp2.status_code == 200
    assert len(resp2.json()) == 30
    mock_fetch_page.assert_not_awaited()


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


def test_cache_mixed_requests(mock_fetch_page):
    """Test that cache works correctly with overlapping page ranges."""
    # First request /2 (fetches pages 1, 2)
    resp1 = client.get("/2")
    assert resp1.status_code == 200
    assert len(resp1.json()) == 60
    assert mock_fetch_page.call_count == 2
    
    # Second request /4 (should fetch only pages 3, 4 since 1, 2 are cached)
    mock_fetch_page.reset_mock()
    resp2 = client.get("/4")
    assert resp2.status_code == 200
    assert len(resp2.json()) == 120  # pages 1,2,3,4
    assert mock_fetch_page.call_count == 2  # only pages 3, 4 fetched
    called_args = sorted(call.args[0] for call in mock_fetch_page.await_args_list)
    assert called_args == [3, 4]


def test_large_page_number(mock_fetch_page):
    """Test that large page numbers work correctly."""
    resp = client.get("/10")
    assert resp.status_code == 200
    assert len(resp.json()) == 300  # 10 pages * 30 items each
    assert mock_fetch_page.call_count == 10


def test_zero_and_negative_numbers():
    """Test edge cases with invalid page numbers."""
    test_cases = [
        ("/0", [400, 422]),
        ("/-1", [400, 422]),
        ("/-5", [400, 422]),
    ]
    
    for endpoint, expected_codes in test_cases:
        resp = client.get(endpoint)
        assert resp.status_code in expected_codes
