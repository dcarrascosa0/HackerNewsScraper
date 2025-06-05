import pytest
import asyncio

from app.scraper import fetch_page

pytestmark = pytest.mark.asyncio

async def test_fetch_page_returns_30_items_and_correct_shape():
    items = await fetch_page(1)
    assert isinstance(items, list)
    assert len(items) == 30

    first = items[0]
    assert "title" in first and isinstance(first["title"], str)
    assert "url" in first and isinstance(first["url"], str)
    assert "points" in first and isinstance(first["points"], int)
    assert "sent_by" in first and isinstance(first["sent_by"], str)
    assert "published" in first and isinstance(first["published"], str)
    assert "comments" in first and isinstance(first["comments"], int)

@pytest.mark.parametrize("invalid_page", [0, -1, None, "abc"])
async def test_fetch_page_invalid_param_raises(invalid_page):
    with pytest.raises(ValueError):
        # type: ignore
        await fetch_page(invalid_page)
